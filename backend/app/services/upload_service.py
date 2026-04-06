import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.core.config import UPLOAD_DIR
from app.parsers.excel_parser import get_workbook_sheet_names
from app.repository.run_repository import create_run, get_run, update_run
from app.schemas.common import UploadResponse
from app.validators.input_validator import ITEM_DELIVERY_REQUIRED_SHEETS, PULL_INPUT_REQUIRED_SHEETS


def _save_file(file: UploadFile, destination: Path) -> None:
    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)


def _validate_sheet_layout(file_path: Path, expected_sheets: list[str], label: str) -> None:
    sheet_names = get_workbook_sheet_names(file_path)
    existing = set(sheet_names)
    expected = set(expected_sheets)
    missing = [sheet for sheet in expected_sheets if sheet not in existing]
    unexpected = [sheet for sheet in sheet_names if sheet not in expected]

    if missing or unexpected:
        details: list[str] = [f"{label} workbook sheet layout is invalid."]
        if missing:
            details.append(f"Missing sheets: {', '.join(missing)}.")
        if unexpected:
            details.append(f"Unexpected sheets: {', '.join(unexpected)}.")
        raise HTTPException(status_code=400, detail=" ".join(details))


def _build_filename(run: dict[str, object]) -> str:
    pull_input_filename = str(run.get("pull_input_filename") or "").strip()
    item_delivery_filename = str(run.get("item_delivery_filename") or "").strip()
    if pull_input_filename and item_delivery_filename:
        return f"{pull_input_filename} + {item_delivery_filename}"
    return pull_input_filename or item_delivery_filename or ""


async def save_pull_input_upload(file: UploadFile) -> UploadResponse:
    run_id = str(uuid.uuid4())
    upload_time = datetime.now(timezone.utc).isoformat()
    filename = Path(file.filename).name
    destination = UPLOAD_DIR / f"{run_id}_pull_{filename}"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    _save_file(file, destination)
    _validate_sheet_layout(destination, PULL_INPUT_REQUIRED_SHEETS, "pull-input-data")

    create_run(
        run_id=run_id,
        filename=filename,
        input_path=destination,
        uploaded_at=upload_time,
    )
    return UploadResponse(
        run_id=run_id,
        display_run_id=str(get_run(run_id).get("display_run_id", run_id)),
        filename=filename,
        upload_time=upload_time,
        next_step="item-delivery-upload",
        upload_type="pull-input-data",
        upload_status={
            "pull_input_data_uploaded": True,
            "item_delivery_uploaded": False,
        },
    )


async def save_item_delivery_upload(run_id: str, file: UploadFile) -> UploadResponse:
    run = get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found.")

    upload_time = datetime.now(timezone.utc).isoformat()
    filename = Path(file.filename).name
    destination = UPLOAD_DIR / f"{run_id}_item_delivery_{filename}"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    _save_file(file, destination)
    _validate_sheet_layout(destination, ITEM_DELIVERY_REQUIRED_SHEETS, "item-delivery update")

    update_run(
        run_id,
        item_delivery_filename=filename,
        item_delivery_path=destination,
        filename=f"{run.get('pull_input_filename', '')} + {filename}",
        uploaded_at=upload_time,
        upload_status={
            "pull_input_data_uploaded": True,
            "item_delivery_uploaded": True,
        },
        status="uploaded",
        next_step="validation",
        validation=None,
        normalized_sheets=None,
        validation_report_path=None,
        validation_report_xlsx_path=None,
        solve_summary=None,
        result_tables=None,
        output_file_path=None,
        preview=None,
        preview_file_path=None,
    )
    updated_run = get_run(run_id) or run

    return UploadResponse(
        run_id=run_id,
        display_run_id=str(updated_run.get("display_run_id", run_id)),
        filename=_build_filename(updated_run),
        upload_time=upload_time,
        next_step="validation",
        upload_type="item-delivery-update",
        upload_status=updated_run["upload_status"],
    )
