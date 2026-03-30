from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.services.download_service import (
    get_corrected_preview_file_path,
    get_output_file_path,
    get_validation_report_file_path,
)

router = APIRouter(tags=["download"])


@router.get("/runs/{run_id}/validation-report")
def download_validation_report(run_id: str) -> FileResponse:
    report_path = get_validation_report_file_path(run_id)
    if report_path is None or not report_path.exists():
        raise HTTPException(status_code=404, detail="Validation report file not found.")
    return FileResponse(
        path=report_path,
        filename=report_path.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.get("/runs/{run_id}/output-file")
def download_output_file(run_id: str) -> FileResponse:
    output_path = get_output_file_path(run_id)
    if output_path is None or not output_path.exists():
        raise HTTPException(status_code=404, detail="Output file not found.")
    return FileResponse(
        path=output_path,
        filename=output_path.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.get("/runs/{run_id}/corrected-preview-file")
def download_corrected_preview_file(run_id: str) -> FileResponse:
    preview_path = get_corrected_preview_file_path(run_id)
    if preview_path is None or not preview_path.exists():
        raise HTTPException(status_code=404, detail="Corrected preview file not found.")
    return FileResponse(
        path=preview_path,
        filename=preview_path.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
