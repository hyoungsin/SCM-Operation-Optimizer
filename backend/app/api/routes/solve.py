from fastapi import APIRouter, HTTPException

from app.schemas.common import SolveResponse
from app.services.solve_service import SolveExecutionError, run_solve

router = APIRouter(tags=["solve"])


@router.post("/runs/{run_id}/solve", response_model=SolveResponse)
def solve_run(run_id: str) -> SolveResponse:
    try:
        result = run_solve(run_id)
    except SolveExecutionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if result is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    return result
