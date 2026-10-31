import pytest
from backend.app.services.dependency_analyzer import DependencyAnalyzer

def test_dependency_graph_structure(mysql_available):
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")
    
    analyzer = DependencyAnalyzer()
    graph = analyzer.build_graph()
    
    assert "nodes" in graph
    assert "edges" in graph
    assert len(graph["nodes"]) >= 10
    
    # Check node labels
    node_ids = {n["id"] for n in graph["nodes"]}
    assert "customers" in node_ids
    assert "products" in node_ids
    assert "orders" in node_ids
    assert "categories" in node_ids

def test_table_neighborhood(mysql_available):
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")
    
    analyzer = DependencyAnalyzer()
    neighborhood = analyzer.get_table_neighborhood("products")
    
    assert neighborhood["table_name"] == "products"
    assert isinstance(neighborhood["direct_parents"], list)
    assert isinstance(neighborhood["direct_children"], list)

def test_repair_impact_assessment(mysql_available):
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")
    
    analyzer = DependencyAnalyzer()
    impact = analyzer.assess_repair_impact("customers", "1", "DELETE_RECORD")
    
    assert impact["table_name"] == "customers"
    assert impact["has_dependent_records"] is True
    assert impact["risk_level"] == "CRITICAL"
    assert impact["is_safe_to_execute"] is False
