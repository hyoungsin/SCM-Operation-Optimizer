from fastapi import APIRouter, HTTPException

from app.schemas.common import ValidationResponse
from app.services.validation_service import run_validation

router = APIRouter(tags=["validation"])


@router.post("/runs/{run_id}/validate", response_model=ValidationResponse)
def validate_run(run_id: str) -> ValidationResponse:
    result = run_validation(run_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    return result
