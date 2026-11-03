import networkx as nx
from typing import Dict, Any, List, Optional, Set
from backend.app.database.connection import get_connection, validate_identifier

class DependencyAnalyzer:
    def __init__(self):
        pass

    def build_graph(self) -> Dict[str, Any]:
        """
        Builds a directed dependency graph of the database schema using NetworkX.
        Nodes represent tables.
        Directed edges represent foreign key relationships: Parent Table -> Child Table.
        (Edge direction: Data in Parent must exist before Child can reference it).
        """
        conn = get_connection()
        G = nx.DiGraph()

        try:
            CORE_TABLES = {"departments", "instructors", "courses", "students", "enrollments", "classrooms"}
            with conn.cursor() as cur:
                # 1. Fetch only core business tables
                cur.execute("""
                    SELECT TABLE_NAME, ENGINE, TABLE_ROWS
                    FROM information_schema.TABLES
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME IN ('departments', 'instructors', 'courses', 'students', 'enrollments', 'classrooms')
                """)
                tables = {r["TABLE_NAME"]: r for r in cur.fetchall()}

                # Fetch issue counts per table for active issues
                cur.execute("""
                    SELECT table_name, COUNT(*) AS issue_count
                    FROM integrity_issues
                    WHERE status IN ('OPEN', 'REVIEWED', 'APPROVED')
                      AND table_name IN ('departments', 'instructors', 'courses', 'students', 'enrollments', 'classrooms')
                    GROUP BY table_name
                """)
                issue_counts = {r["table_name"]: r["issue_count"] for r in cur.fetchall()}

                for t_name in ["departments", "instructors", "courses", "students", "enrollments", "classrooms"]:
                    t_info = tables.get(t_name, {})
                    G.add_node(
                        t_name,
                        id=t_name,
                        label=t_name,
                        table_type="BUSINESS",
                        row_count=t_info.get("TABLE_ROWS") or 0,
                        issue_count=issue_counts.get(t_name, 0)
                    )

                # 2. Fetch declared foreign keys between the 6 core business tables
                cur.execute("""
                    SELECT 
                        TABLE_NAME AS child_table,
                        COLUMN_NAME AS child_column,
                        REFERENCED_TABLE_NAME AS parent_table,
                        REFERENCED_COLUMN_NAME AS parent_column,
                        CONSTRAINT_NAME AS constraint_name
                    FROM information_schema.KEY_COLUMN_USAGE
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND REFERENCED_TABLE_NAME IS NOT NULL
                      AND TABLE_NAME IN ('departments', 'instructors', 'courses', 'students', 'enrollments', 'classrooms')
                      AND REFERENCED_TABLE_NAME IN ('departments', 'instructors', 'courses', 'students', 'enrollments', 'classrooms')
                """)
                fk_rows = cur.fetchall()

                for fk in fk_rows:
                    p = fk["parent_table"]
                    c = fk["child_table"]
                    if p in CORE_TABLES and c in CORE_TABLES:
                        # Edge direction: Parent -> Child
                        G.add_edge(
                            p, c,
                            from_node=p,
                            to_node=c,
                            label=f"{c}.{fk['child_column']} -> {p}.{fk['parent_column']}",
                            relationship_type="PHYSICAL_FK",
                            constraint_name=fk["constraint_name"]
                        )

            # Analyze graph properties
            has_cycles = not nx.is_directed_acyclic_graph(G)
            cycle_nodes = []
            if has_cycles:
                try:
                    cycles = list(nx.simple_cycles(G))
                    cycle_nodes = list(set([node for cycle in cycles for node in cycle]))
                except Exception:
                    cycle_nodes = []

            topological_order = []
            if not has_cycles:
                try:
                    topological_order = list(nx.topological_sort(G))
                except Exception:
                    topological_order = []

            nodes = [
                {
                    "id": n,
                    "label": n,
                    "table_type": G.nodes[n].get("table_type", "BUSINESS"),
                    "row_count": G.nodes[n].get("row_count", 0),
                    "issue_count": G.nodes[n].get("issue_count", 0)
                }
                for n in G.nodes()
            ]

            edges = [
                {
                    "from_node": u,
                    "to_node": v,
                    "label": data.get("label", ""),
                    "relationship_type": data.get("relationship_type", "PHYSICAL_FK")
                }
                for u, v, data in G.edges(data=True)
            ]

            return {
                "nodes": nodes,
                "edges": edges,
                "has_cycles": has_cycles,
                "cycle_nodes": cycle_nodes,
                "topological_order": topological_order
            }

        finally:
            conn.close()

    def get_table_neighborhood(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Returns direct parents, children, and dependency chain for a specific table."""
        full_graph = self.build_graph()
        known_tables = {n["id"] for n in full_graph.get("nodes", [])}
        if table_name not in known_tables:
            return None

        G = nx.DiGraph()
        for n in full_graph.get("nodes", []):
            G.add_node(n["id"])
        for e in full_graph["edges"]:
            G.add_edge(e["from_node"], e["to_node"], label=e["label"])

        parents = list(G.predecessors(table_name))
        children = list(G.successors(table_name))

        # Descendant blast radius (all tables that depend on this table)
        descendants = list(nx.descendants(G, table_name))
        ancestors = list(nx.ancestors(G, table_name))

        return {
            "table_name": table_name,
            "direct_parents": parents,
            "direct_children": children,
            "ancestors": ancestors,
            "descendants": descendants,
            "blast_radius_tables": descendants
        }

    def assess_repair_impact(
        self,
        table_name: str,
        record_id: str,
        action: str,
        issue_severity: str = "MEDIUM"
    ) -> Dict[str, Any]:
        """
        Assesses the cascading impact of modifying or deleting a record in table_name.
        Inspects schema-level direct children, indirect descendants, and instance-level child rows.
        Computes accurate risk level combining issue severity, strategy destructiveness, and dependency scope.
        """
        table_name = validate_identifier(table_name)
        conn = get_connection()
        dependent_records: List[Dict[str, Any]] = []

        try:
            # 1. Schema-level neighborhood analysis
            neighborhood = self.get_table_neighborhood(table_name)
            direct_children = sorted(neighborhood.get("direct_children", []))
            all_descendants = sorted(neighborhood.get("descendants", []))
            downstream_tables = sorted([t for t in all_descendants if t not in direct_children])

            # 2. Instance-level matching records for this specific record_id
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        TABLE_NAME AS child_table,
                        COLUMN_NAME AS child_column,
                        CONSTRAINT_NAME AS fk_name
                    FROM information_schema.KEY_COLUMN_USAGE
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND REFERENCED_TABLE_NAME = %s
                """, (table_name,))
                fk_refs = cur.fetchall()

                for ref in fk_refs:
                    c_tbl = validate_identifier(ref["child_table"])
                    c_col = validate_identifier(ref["child_column"])
                    
                    cur.execute(f"SELECT COUNT(*) AS c FROM `{c_tbl}` WHERE `{c_col}` = %s", (record_id,))
                    res = cur.fetchone()
                    count = res["c"] if res else 0

                    if count > 0:
                        dependent_records.append({
                            "child_table": c_tbl,
                            "child_column": c_col,
                            "matching_records_count": count,
                            "constraint_name": ref["fk_name"]
                        })

            total_matching_records = sum(r["matching_records_count"] for r in dependent_records)
            has_dependents = len(dependent_records) > 0
            is_destructive = action in ["DELETE_RECORD", "QUARANTINE"]
            has_schema_children = len(direct_children) > 0 or len(downstream_tables) > 0

            # 3. Risk Level Calculation
            # Rules:
            # - Never downgrade a CRITICAL issue to LOW.
            # - Destructive repairs with child records or downstream tables are CRITICAL.
            # - Modifying key entity records with downstream tables maintains CRITICAL/HIGH risk.
            sev_upper = (issue_severity or "MEDIUM").upper()
            if sev_upper == "CRITICAL":
                if is_destructive or has_dependents or has_schema_children:
                    risk_level = "CRITICAL"
                else:
                    risk_level = "HIGH"
            elif sev_upper == "HIGH":
                if is_destructive or has_dependents:
                    risk_level = "CRITICAL"
                else:
                    risk_level = "HIGH"
            elif sev_upper == "MEDIUM":
                if is_destructive and has_dependents:
                    risk_level = "CRITICAL"
                elif is_destructive or has_dependents:
                    risk_level = "HIGH"
                elif has_schema_children:
                    risk_level = "MEDIUM"
                else:
                    risk_level = "LOW"
            else:  # LOW
                if is_destructive and has_dependents:
                    risk_level = "HIGH"
                elif is_destructive or has_dependents:
                    risk_level = "MEDIUM"
                else:
                    risk_level = "LOW"

            # 4. Warnings and Consequences formulation
            warning = None
            if has_dependents and is_destructive:
                warning = f"DESTRUCTIVE ACTION: Deleting this record will violate foreign key constraints in {len(dependent_records)} child table(s) ({total_matching_records} dependent rows) or require cascading actions."
            elif has_dependents:
                warning = f"This record has {total_matching_records} active dependent child row(s) in: {', '.join([r['child_table'] for r in dependent_records])}."

            if has_dependents:
                consequences_text = f"Modifying or deleting this record directly affects {total_matching_records} dependent record(s) across child table(s): {', '.join([r['child_table'] for r in dependent_records])}."
            elif has_schema_children:
                children_str = ", ".join(direct_children) if direct_children else "None"
                downstream_str = ", ".join(downstream_tables) if downstream_tables else "None"
                consequences_text = f"Schema dependencies detected: Direct children: [{children_str}], Downstream: [{downstream_str}]. Currently 0 active child records reference record ID {record_id}."
            else:
                consequences_text = "This table has no foreign key dependencies in the active database schema (Isolated entity)."

            # Combine direct and downstream tables for full dependent tables list
            all_dependent_tables = []
            for t in direct_children + downstream_tables:
                if t not in all_dependent_tables:
                    all_dependent_tables.append(t)

            return {
                "table_name": table_name,
                "record_id": record_id,
                "action": action,
                "issue_severity": sev_upper,
                "has_dependent_records": has_dependents,
                "matching_child_records_count": total_matching_records,
                "direct_children": direct_children,
                "downstream_tables": downstream_tables,
                "descendants": all_descendants,
                "dependent_tables": all_dependent_tables,
                "dependent_records": dependent_records,
                "foreign_key_consequences": consequences_text,
                "risk_level": risk_level,
                "is_safe_to_execute": not (has_dependents and is_destructive),
                "warning": warning
            }

        finally:
            conn.close()
