from app.repository.run_repository import get_run
from app.schemas.common import ResultResponse


class ResultRetrievalError(Exception):
    pass


def get_result(run_id: str) -> ResultResponse | None:
    run = get_run(run_id)
    if run is None:
        return None

    solve_summary = run.get("solve_summary")
    result_tables = run.get("result_tables")
    if not solve_summary or not result_tables:
        raise ResultRetrievalError("Solve must be completed before result retrieval.")

    return ResultResponse(
        run_id=run_id,
        solve_status=solve_summary["solve_status"],
        termination_condition=solve_summary["termination_condition"],
        objective_value=solve_summary["objective_value"],
        solving_time=solve_summary["solving_time"],
        kpi_summary=solve_summary["kpi_summary"],
        allocation_metrics=solve_summary["allocation_metrics"],
        tables=result_tables,
    )
