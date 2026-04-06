from time import perf_counter

from pyomo.environ import SolverFactory

from app.optimization.solution_extractor import extract_solution


def _get_solver():
    for solver_name in ("appsi_highs", "highs"):
        solver = SolverFactory(solver_name)
        if solver is not None and solver.available(exception_flag=False):
            return solver
    raise RuntimeError("HiGHS solver is not available in the current environment.")


def solve_model(model) -> dict[str, object]:
    solver = _get_solver()

    started_at = perf_counter()
    result = solver.solve(model, tee=False)
    solving_time = perf_counter() - started_at

    return extract_solution(model, result, solving_time)
