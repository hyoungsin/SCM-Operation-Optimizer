from time import perf_counter

from pyomo.environ import SolverFactory, value


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

    objective_value = float(value(model.objective))
    total_shortage = float(
        sum(value(model.shortage[product, week]) for product in model.PRODUCTS for week in model.WEEKS)
    )
    total_air_shipment = float(
        sum(value(model.air_ship[product, week]) for product in model.PRODUCTS for week in model.WEEKS)
    )
    total_air_cost = float(
        sum(
            value(model.air_ship[product, week]) * value(model.air_cost[product])
            for product in model.PRODUCTS
            for week in model.WEEKS
        )
    )
    weeks = list(model.WEEKS)

    shipment_air_rows = []
    shipment_sea_rows = []
    shortage_rows = []
    for product in model.PRODUCTS:
        air_row = {"model-site": product}
        sea_row = {"model-site": product}
        shortage_row = {"model-site": product}
        for week in weeks:
            air_qty = int(round(value(model.air_ship[product, week])))
            shortage_qty = int(round(value(model.shortage[product, week])))
            regular_qty = int(round(value(model.regular_ship[product, week]) + value(model.fixed_shipment_launch[product, week])))

            air_row[week] = air_qty
            sea_row[week] = regular_qty
            shortage_row[week] = shortage_qty

        shipment_air_rows.append(air_row)
        shipment_sea_rows.append(sea_row)
        shortage_rows.append(shortage_row)

    return {
        "solve_executed": True,
        "solve_status": str(result.solver.status),
        "termination_condition": str(result.solver.termination_condition),
        "objective_value": objective_value,
        "solving_time": round(solving_time, 4),
        "kpi_summary": {
            "total_shortage": round(total_shortage, 4),
            "total_air_shipment": round(total_air_shipment, 4),
            "total_air_cost": round(total_air_cost, 4),
        },
        "tables": {
            "shipment_sea": shipment_sea_rows,
            "shipment_air": shipment_air_rows,
            "shortage": shortage_rows,
        },
    }
