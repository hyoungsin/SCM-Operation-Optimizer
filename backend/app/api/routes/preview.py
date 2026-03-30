from fastapi import APIRouter, HTTPException

from app.schemas.common import CorrectedPreviewResponse
from app.services.preview_service import get_corrected_preview

router = APIRouter(tags=["preview"])


@router.get("/runs/{run_id}/corrected-preview", response_model=CorrectedPreviewResponse)
def corrected_preview(run_id: str) -> CorrectedPreviewResponse:
    result = get_corrected_preview(run_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    if result.preview_generated is False:
        raise HTTPException(status_code=400, detail="Validation must be completed before preview.")
    return result
