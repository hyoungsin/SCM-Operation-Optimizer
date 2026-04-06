from pathlib import Path

RUNS: dict[str, dict[str, object]] = {}


def _build_display_run_id(uploaded_at: str) -> str:
    date_part = uploaded_at.split("T", 1)[0].replace("-", "")
    sequence = 1
    for run in RUNS.values():
        if str(run.get("display_run_id", "")).startswith(f"{date_part[:4]}-{date_part[4:]}"):
            sequence += 1
    return f"{date_part[:4]}-{date_part[4:]}-{sequence:04d}"


def create_run(run_id: str, filename: str, input_path: Path, uploaded_at: str) -> None:
    RUNS[run_id] = {
        "run_id": run_id,
        "display_run_id": _build_display_run_id(uploaded_at),
        "filename": filename,
        "input_path": input_path,
        "pull_input_filename": filename,
        "pull_input_path": input_path,
        "item_delivery_filename": "",
        "item_delivery_path": None,
        "upload_status": {
            "pull_input_data_uploaded": True,
            "item_delivery_uploaded": False,
        },
        "uploaded_at": uploaded_at,
        "status": "pull_input_uploaded",
        "next_step": "item-delivery-upload",
        "validation": None,
        "normalized_sheets": None,
        "validation_report_path": None,
        "validation_report_xlsx_path": None,
        "solve_summary": None,
        "result_tables": None,
        "output_file_path": None,
        "preview": None,
        "preview_file_path": None,
    }


def get_run(run_id: str) -> dict[str, object] | None:
    return RUNS.get(run_id)


def update_run(run_id: str, **updates: object) -> None:
    if run_id in RUNS:
        RUNS[run_id].update(updates)
