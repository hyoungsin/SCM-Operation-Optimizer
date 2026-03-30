from pathlib import Path

RUNS: dict[str, dict[str, object]] = {}


def create_run(run_id: str, filename: str, input_path: Path, uploaded_at: str) -> None:
    RUNS[run_id] = {
        "run_id": run_id,
        "filename": filename,
        "input_path": input_path,
        "uploaded_at": uploaded_at,
        "status": "uploaded",
        "next_step": "validation",
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
