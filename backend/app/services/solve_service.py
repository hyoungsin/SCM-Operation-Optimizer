from app.optimization.model_builder import build_model
from app.optimization.output_writer import write_output_workbook
from app.optimization.solver_runner import solve_model
from app.repository.run_repository import get_run, update_run
from app.schemas.common import SolveResponse


class SolveExecutionError(Exception):
    pass


def _sort_weeks(weeks: set[str]) -> list[str]:
    return sorted(weeks, key=lambda week: int(week[1:]))


def _build_row_map(rows: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    mapped: dict[str, dict[str, object]] = {}
    for row in rows:
        if not row:
            continue
        row_id = str(next(iter(row.values()), "")).strip()
        if row_id:
            mapped[row_id] = row
    return mapped


def _safe_float(value: object, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _extract_first_non_week_value(row: dict[str, object]) -> object:
    for key, value in row.items():
        if not (key.lower().startswith("w") and key[1:].isdigit()):
            return value
    return ""


def _build_sheet_key_map(rows: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    mapped: dict[str, dict[str, object]] = {}
    for row in rows:
        row_id = str(_extract_first_non_week_value(row)).strip()
        if row_id:
            mapped[row_id] = row
    return mapped


def _build_priority_map(rows: list[dict[str, object]], weeks: list[str]) -> dict[str, float]:
    if not rows:
        return {week: 1.0 for week in weeks}

    if len(rows) == 1 and all(week in rows[0] for week in weeks):
        return {week: _safe_float(rows[0].get(week), 1.0) for week in weeks}

    priority_map: dict[str, float] = {}
    for row in rows:
        week = str(row.get("week", "")).strip()
        if week:
            priority_map[week] = _safe_float(row.get("priority"), 1.0)

    return {week: priority_map.get(week, 1.0) for week in weeks}


def _prepare_model_input(normalized_sheets: dict[str, dict[str, object]]) -> dict[str, object]:
    demand_sheet = normalized_sheets.get("set-demand", {})
    price_sheet = normalized_sheets.get("set-price", {})
    inventory_sheet = normalized_sheets.get("set-inventory", {})
    delivery_sheet = normalized_sheets.get("delivery", {})
    air_mode_sheet = normalized_sheets.get("air-mode", {})
    resource_sheet = normalized_sheets.get("resource", {})
    capacity_sheet = normalized_sheets.get("capacity", {})
    priority_sheet = normalized_sheets.get("demand-priority", {})
    shipment_sheet = normalized_sheets.get("set-shipment", {})
    bod_sheet = normalized_sheets.get("bod", {})

    demand_rows = demand_sheet.get("rows", [])
    price_rows = price_sheet.get("rows", [])
    inventory_rows = inventory_sheet.get("rows", [])
    delivery_rows = delivery_sheet.get("rows", [])
    air_mode_rows = air_mode_sheet.get("rows", [])
    resource_rows = resource_sheet.get("rows", [])
    capacity_rows = capacity_sheet.get("rows", [])
    priority_rows = priority_sheet.get("rows", [])
    shipment_rows = shipment_sheet.get("rows", [])
    bod_rows = bod_sheet.get("rows", [])

    if not demand_rows:
        raise SolveExecutionError("Normalized demand data is not available for solve.")

    week_columns = {
        key
        for row in demand_rows
        for key in row.keys()
        if key.lower().startswith("w") and key[1:].isdigit()
    }
    if not week_columns:
        raise SolveExecutionError("No weekly demand buckets were found in normalized input.")

    weeks = _sort_weeks(week_columns)
    demand_by_product = _build_row_map(demand_rows)
    price_by_product = _build_row_map(price_rows)
    inventory_by_product = _build_row_map(inventory_rows)
    delivery_by_product = _build_row_map(delivery_rows)
    air_mode_by_product = _build_row_map(air_mode_rows)
    resource_by_product = _build_sheet_key_map(resource_rows)
    capacity_by_resource = _build_sheet_key_map(capacity_rows)
    demand_priority = _build_priority_map(priority_rows, weeks)
    products = sorted(demand_by_product.keys())

    demand: dict[tuple[str, str], float] = {}
    init_inventory: dict[str, float] = {}
    delivery: dict[tuple[str, str], float] = {}
    price: dict[str, float] = {}
    air_cost: dict[str, float] = {}
    air_enabled: dict[str, int] = {}
    air_leadtime: dict[str, int] = {}
    regular_enabled: dict[str, int] = {}
    regular_leadtime: dict[str, int] = {}
    fixed_horizon_index: dict[str, int] = {}
    fixed_shipment_launch: dict[tuple[str, str], float] = {}
    resource_map: dict[str, str] = {}
    resources: set[str] = set()
    capacity: dict[tuple[str, str], float] = {}
    bod_leadtime_map = {
        str(row.get("model-bod", "")).strip(): int(_safe_float(row.get("leadtime"), 0))
        for row in bod_rows
        if str(row.get("model-bod", "")).strip()
    }
    shipment_routes_by_product: dict[str, set[str]] = {}

    for row in shipment_rows:
        product = str(row.get("model-site", "")).strip()
        route = str(row.get("from-to", "")).strip()
        if product and route:
            shipment_routes_by_product.setdefault(product, set()).add(route)
            for week in weeks:
                qty = _safe_float(row.get(week), 0.0)
                fixed_shipment_launch[(product, week)] = fixed_shipment_launch.get((product, week), 0.0) + qty
                if qty > 0:
                    fixed_horizon_index[product] = max(
                        fixed_horizon_index.get(product, -1),
                        int(week[1:]),
                    )

    for product in products:
        demand_row = demand_by_product[product]
        price_row = price_by_product.get(product, {})
        inventory_row = inventory_by_product.get(product, {})
        delivery_row = delivery_by_product.get(product, {})
        air_mode_row = air_mode_by_product.get(product, {})
        resource_row = resource_by_product.get(product, {})

        price[product] = _safe_float(price_row.get("price"), 0.0)
        init_inventory[product] = float(inventory_row.get("w0", 0) or 0)
        air_cost[product] = float(air_mode_row.get("air-cost", 0) or 0)
        air_enabled[product] = 1 if float(air_mode_row.get("enabled", 0) or 0) > 0 else 0
        air_leadtime[product] = int(_safe_float(air_mode_row.get("air-leadtime"), 0))
        resource_name = str(resource_row.get("set-resource", "")).strip()
        resource_map[product] = resource_name
        if resource_name:
            resources.add(resource_name)

        regular_route_leadtimes = [
            leadtime
            for route, leadtime in bod_leadtime_map.items()
            if route in shipment_routes_by_product.get(product, set()) and "(Air)" not in route
        ]
        regular_enabled[product] = 1 if regular_route_leadtimes else 0
        regular_leadtime[product] = min(regular_route_leadtimes) if regular_route_leadtimes else 0

        for week in weeks:
            demand[(product, week)] = float(demand_row.get(week, 0) or 0)
            delivery[(product, week)] = float(delivery_row.get(week, 0) or 0)

    for resource_name in resources:
        capacity_row = capacity_by_resource.get(resource_name, {})
        for week in weeks:
            capacity[(resource_name, week)] = _safe_float(capacity_row.get(week), float("inf"))

    return {
        "products": products,
        "weeks": weeks,
        "resources": sorted(resources),
        "demand": demand,
        "delivery": delivery,
        "init_inventory": init_inventory,
        "price": price,
        "demand_priority": demand_priority,
        "air_cost": air_cost,
        "air_enabled": air_enabled,
        "air_leadtime": air_leadtime,
        "regular_enabled": regular_enabled,
        "regular_leadtime": regular_leadtime,
        "fixed_horizon_index": fixed_horizon_index,
        "fixed_shipment_launch": fixed_shipment_launch,
        "resource_map": resource_map,
        "capacity": capacity,
    }


def run_solve(run_id: str) -> SolveResponse | None:
    run = get_run(run_id)
    if run is None:
        return None

    validation = run.get("validation")
    if not validation:
        raise SolveExecutionError("Validation must be completed before solve.")

    if validation.get("solve_allowed") is not True:
        raise SolveExecutionError("Solve is blocked because validation did not pass.")

    normalized_sheets = run.get("normalized_sheets")
    if not normalized_sheets:
        raise SolveExecutionError("Normalized input could not be prepared for this run.")

    try:
        model_input = _prepare_model_input(normalized_sheets)
        model = build_model(model_input)
        solve_result = solve_model(model)
        output_path = write_output_workbook(run_id, solve_result)
    except SolveExecutionError:
        raise
    except Exception as exc:
        raise SolveExecutionError(f"Solve execution failed: {exc}") from exc

    update_run(
        run_id,
        solve_summary=solve_result,
        result_tables=solve_result.get("tables", {}),
        output_file_path=output_path,
        status="solved" if solve_result["solve_executed"] else "solve_failed",
        next_step="result",
    )

    return SolveResponse(
        run_id=run_id,
        solve_executed=solve_result["solve_executed"],
        solve_status=solve_result["solve_status"],
        termination_condition=solve_result["termination_condition"],
        objective_value=solve_result["objective_value"],
        solving_time=solve_result["solving_time"],
        kpi_summary=solve_result["kpi_summary"],
    )
