import json

from app.core.config import REPORT_DIR
from app.parsers.excel_parser import parse_workbook
from app.repository.run_repository import get_run, update_run
from app.schemas.common import ValidationResponse, ValidationSummary
from app.validators.input_validator import validate_parsed_input


def run_validation(run_id: str) -> ValidationResponse | None:
    run = get_run(run_id)
    if run is None:
        return None

    pull_input_path = run.get("pull_input_path")
    item_delivery_path = run.get("item_delivery_path")

    if not pull_input_path or not item_delivery_path:
        validation = {
            "validation_status": "failed",
            "errors": [
                {
                    "sheet": "upload",
                    "message": "Both pull-input-data and item-delivery update uploads must be completed before validation.",
                }
            ],
            "warnings": [],
            "summary": {"errors": 1, "warnings": 0, "infos": 0},
            "solve_allowed": False,
        }
    else:
        try:
            parsed_pull_input = parse_workbook(pull_input_path)
            parsed_item_delivery = parse_workbook(item_delivery_path)
            merged_sheets = dict(parsed_pull_input.get("sheets", {}))
            merged_sheets.update(parsed_item_delivery.get("sheets", {}))
            merged_workbook = {
                "file_path": f"{pull_input_path};{item_delivery_path}",
                "sheet_names": list(merged_sheets.keys()),
                "sheet_count": len(merged_sheets),
                "sheets": merged_sheets,
            }
            validation = validate_parsed_input(merged_workbook)
        except Exception as exc:
            validation = {
                "validation_status": "failed",
                "errors": [{"sheet": "workbook", "message": f"Failed to read workbook: {exc}"}],
                "warnings": [],
                "summary": {"errors": 1, "warnings": 0, "infos": 0},
                "solve_allowed": False,
            }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"{run_id}_validation_report.json"

    report_payload = {
        "run_id": run_id,
        "filename": run["filename"],
        "validation_status": validation["validation_status"],
        "errors": validation["errors"],
        "warnings": validation["warnings"],
        "summary": validation["summary"],
        "solve_allowed": validation["solve_allowed"],
    }
    report_path.write_text(json.dumps(report_payload, indent=2), encoding="utf-8")

    update_run(
        run_id,
        validation=report_payload,
        normalized_sheets=validation.get("normalized_sheets", {}),
        validation_report_path=report_path,
        status="validated" if validation["solve_allowed"] else "validation_error",
        next_step="solve" if validation["solve_allowed"] else "validation",
    )

    return ValidationResponse(
        run_id=run_id,
        validation_status=validation["validation_status"],
        errors=validation["errors"],
        warnings=validation["warnings"],
        summary=ValidationSummary(**validation["summary"]),
        solve_allowed=validation["solve_allowed"],
    )
