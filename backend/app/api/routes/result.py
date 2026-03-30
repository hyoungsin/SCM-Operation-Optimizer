from fastapi import APIRouter, HTTPException

from app.schemas.common import ResultResponse
from app.services.result_service import ResultRetrievalError, get_result

router = APIRouter(tags=["result"])


@router.get("/runs/{run_id}/result", response_model=ResultResponse)
def get_run_result(run_id: str) -> ResultResponse:
    try:
        result = get_result(run_id)
    except ResultRetrievalError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if result is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    return result
