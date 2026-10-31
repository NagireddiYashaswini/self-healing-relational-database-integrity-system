from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Generic, TypeVar
from datetime import datetime
from enum import Enum

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    error: Optional[str] = None

# --- Database Explorer Models ---
class ColumnInfo(BaseModel):
    name: str
    data_type: str
    is_nullable: bool
    default_value: Optional[str] = None
    is_primary_key: bool = False
    is_foreign_key: bool = False
    comment: Optional[str] = None

class ForeignKeyInfo(BaseModel):
    constraint_name: str
    column_name: str
    referenced_table: str
    referenced_column: str
    on_update: Optional[str] = None
    on_delete: Optional[str] = None

class IndexInfo(BaseModel):
    index_name: str
    column_name: str
    is_unique: bool
    is_primary: bool

class TableSummary(BaseModel):
    table_name: str
    row_count: int
    column_count: int
    engine: str
    table_type: str # 'BUSINESS', 'STAGING', 'SYSTEM', 'QUARANTINE'
    has_primary_key: bool
    foreign_key_count: int

class TableDetail(BaseModel):
    table_name: str
    row_count: int
    columns: List[ColumnInfo]
    foreign_keys: List[ForeignKeyInfo]
    indexes: List[IndexInfo]
    table_type: str
    sample_rows: List[Dict[str, Any]] = []

class RelationshipEdge(BaseModel):
    from_table: str # Parent
    to_table: str   # Child
    parent_column: str
    child_column: str
    constraint_name: str
    relationship_type: str # 'PHYSICAL_FK' or 'LOGICAL_RULE'
    on_delete: Optional[str] = None
    on_update: Optional[str] = None

# --- Rules Models ---
class RuleTypeEnum(str, Enum):
    ORPHAN = "ORPHAN"
    DUPLICATE = "DUPLICATE"
    NULL_CHECK = "NULL_CHECK"
    DOMAIN_CHECK = "DOMAIN_CHECK"
    RELATIONAL_CONSISTENCY = "RELATIONAL_CONSISTENCY"

class SeverityEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class IssueStatusEnum(str, Enum):
    OPEN = "OPEN"
    REVIEWED = "REVIEWED"
    APPROVED = "APPROVED"
    REPAIRED = "REPAIRED"
    IGNORED = "IGNORED"
    FAILED = "FAILED"

class RuleModel(BaseModel):
    rule_id: int
    rule_code: str
    name: str
    description: str
    rule_type: RuleTypeEnum
    target_table: str
    target_column: str
    parent_table: Optional[str] = None
    parent_column: Optional[str] = None
    parameters_json: Optional[Dict[str, Any]] = None
    severity: SeverityEnum
    is_enabled: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class RuleCreate(BaseModel):
    rule_code: str
    name: str
    description: str
    rule_type: RuleTypeEnum
    target_table: str
    target_column: str
    parent_table: Optional[str] = None
    parent_column: Optional[str] = None
    parameters_json: Optional[Dict[str, Any]] = None
    severity: SeverityEnum = SeverityEnum.MEDIUM
    is_enabled: bool = True

class RuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parameters_json: Optional[Dict[str, Any]] = None
    severity: Optional[SeverityEnum] = None
    is_enabled: Optional[bool] = None

# --- Scan Models ---
class ScanTriggerRequest(BaseModel):
    scan_type: str = "FULL" # 'FULL' or 'TABLE'
    target_tables: Optional[List[str]] = None
    rule_codes: Optional[List[str]] = None

class ScanSummary(BaseModel):
    scan_id: str
    scan_type: str
    target_tables: List[str]
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str
    total_rows_inspected: int
    issues_found: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    duration_ms: Optional[float] = None
    error_message: Optional[str] = None

class IntegrityIssueModel(BaseModel):
    issue_id: str
    scan_id: str
    rule_id: Optional[int] = None
    rule_code: str
    category: str
    severity: SeverityEnum
    table_name: str
    record_id: str
    column_name: Optional[str] = None
    invalid_value: Optional[str] = None
    description: str
    status: IssueStatusEnum
    ignored_reason: Optional[str] = None
    detected_at: datetime
    repaired_at: Optional[datetime] = None
    recommended_strategy: Optional[str] = None

class IssueStatusUpdateRequest(BaseModel):
    status: IssueStatusEnum
    reason: Optional[str] = None

# --- Repair Models ---
class RepairStrategyEnum(str, Enum):
    RESTORE_PARENT = "RESTORE_PARENT"
    MAP_PARENT = "MAP_PARENT"
    QUARANTINE = "QUARANTINE"
    DELETE_RECORD = "DELETE_RECORD"
    MERGE_DUPLICATE = "MERGE_DUPLICATE"
    SET_DEFAULT = "SET_DEFAULT"
    MANUAL_INTERVENTION = "MANUAL_INTERVENTION"

class RepairRecommendationModel(BaseModel):
    recommendation_id: int
    issue_id: str
    strategy: RepairStrategyEnum
    problem_description: str
    proposed_action: str
    reason: str
    expected_impact: str
    risk_level: SeverityEnum
    is_reversible: bool
    requires_approval: bool
    approval_status: str
    created_at: datetime

class RepairPreviewRequest(BaseModel):
    issue_id: str
    strategy: Optional[RepairStrategyEnum] = None
    repair_parameters: Optional[Dict[str, Any]] = None

class RepairPreviewResponse(BaseModel):
    issue_id: str
    table_name: str
    record_id: str
    strategy: str
    risk_level: str
    affected_rows_count: int
    before_state: Dict[str, Any]
    after_state: Dict[str, Any]
    dependent_tables: List[str]
    sql_preview: List[str]
    is_destructive: bool
    requires_confirmation: bool
    warning: Optional[str] = None

class RepairExecuteRequest(BaseModel):
    issue_id: str
    strategy: RepairStrategyEnum
    repair_parameters: Optional[Dict[str, Any]] = None
    confirmed: bool = False
    operator: str = "ADMIN_USER"

class RepairExecutionModel(BaseModel):
    execution_id: str
    issue_id: str
    transaction_id: str
    status: str
    executed_by: str
    executed_at: datetime
    sql_executed: str
    execution_time_ms: int
    verified: bool
    error_message: Optional[str] = None

# --- Dependency Models ---
class GraphNode(BaseModel):
    id: str
    label: str
    table_type: str
    row_count: int
    issue_count: int

class GraphEdge(BaseModel):
    from_node: str
    to_node: str
    label: str
    relationship_type: str

class DependencyGraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    has_cycles: bool
    cycle_nodes: List[str]
    topological_order: Optional[List[str]] = None

# --- Transaction Simulator Models ---
class TransactionDemoType(str, Enum):
    COMMIT_SUCCESS = "COMMIT_SUCCESS"
    SIMULATED_FAILURE_ROLLBACK = "SIMULATED_FAILURE_ROLLBACK"
    SAVEPOINT_PARTIAL_ROLLBACK = "SAVEPOINT_PARTIAL_ROLLBACK"

class TransactionStepResult(BaseModel):
    step_number: int
    operation_name: str
    sql: str
    status: str # 'EXECUTED', 'COMMITTED', 'ROLLED_BACK', 'FAILED', 'SAVEPOINT_SET'
    details: str
    database_state_snapshot: Optional[Dict[str, Any]] = None

class TransactionDemoResponse(BaseModel):
    transaction_id: str
    scenario: str
    overall_status: str # 'COMMITTED' or 'ROLLED_BACK'
    start_time: datetime
    end_time: datetime
    duration_ms: float
    steps: List[TransactionStepResult]
    initial_state_count: int
    final_state_count: int
    state_preserved: bool
    explanation: str

# --- Recovery Models ---
class RecoveryCheckpointModel(BaseModel):
    checkpoint_id: str
    checkpoint_name: str
    created_at: datetime
    checkpoint_type: str
    target_table: str
    rows_captured: int
    status: str

class CreateCheckpointRequest(BaseModel):
    target_table: str
    checkpoint_name: str

class RollbackCheckpointRequest(BaseModel):
    checkpoint_id: str
    confirmed: bool = False

# --- Audit Models ---
class AuditLogModel(BaseModel):
    event_id: int
    event_type: str
    actor: str
    timestamp: datetime
    related_scan_id: Optional[str] = None
    related_issue_id: Optional[str] = None
    related_transaction_id: Optional[str] = None
    action_description: str
    target_table: Optional[str] = None
    record_identifier: Optional[str] = None
    result: str
    before_values_json: Optional[str] = None
    after_values_json: Optional[str] = None
    error_message: Optional[str] = None
