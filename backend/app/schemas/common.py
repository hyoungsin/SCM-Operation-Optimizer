from pydantic import BaseModel


class UploadStatus(BaseModel):
    pull_input_data_uploaded: bool
    item_delivery_uploaded: bool


class UploadResponse(BaseModel):
    run_id: str
    display_run_id: str
    filename: str
    upload_time: str
    next_step: str
    upload_type: str
    upload_status: UploadStatus


class ValidationSummary(BaseModel):
    errors: int
    warnings: int
    infos: int


class ValidationResponse(BaseModel):
    run_id: str
    validation_status: str
    errors: list[dict[str, str]]
    warnings: list[dict[str, str]]
    summary: ValidationSummary
    solve_allowed: bool


class PreviewSheet(BaseModel):
    sheet_name: str
    row_count: int
    sample_rows: list[dict[str, object]]


class CorrectedPreviewResponse(BaseModel):
    run_id: str
    preview_generated: bool
    sheets: list[PreviewSheet]


class KpiSummary(BaseModel):
    total_shortage: float
    total_air_shipment: float
    total_air_cost: float


class AllocationMetrics(BaseModel):
    alloc_total: float
    alloc_by_model: dict[str, float]
    gap_by_model: dict[str, float]
    score_by_model: dict[str, int]
    weight_by_model: dict[str, float]
    weighted_total_score: float


class SolveResponse(BaseModel):
    run_id: str
    solve_executed: bool
    solve_status: str
    termination_condition: str
    objective_value: float
    solving_time: float
    kpi_summary: KpiSummary
    allocation_metrics: AllocationMetrics


class ResultTableRow(BaseModel):
    model_site: str
    values: dict[str, int]


class ResultTables(BaseModel):
    shipment_sea: list[dict[str, object]]
    shipment_air: list[dict[str, object]]
    shortage: list[dict[str, object]]


class ResultResponse(BaseModel):
    run_id: str
    solve_status: str
    termination_condition: str
    objective_value: float
    solving_time: float
    kpi_summary: KpiSummary
    allocation_metrics: AllocationMetrics
    tables: ResultTables
