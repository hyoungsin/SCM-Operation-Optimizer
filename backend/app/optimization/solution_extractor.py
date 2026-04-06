from pyomo.environ import value

from app.optimization.objective import BUCKETS, BUCKET_SCORES, BUCKET_WEIGHTS


def _select_bucket(model, product: str) -> str:
    for bucket in BUCKETS:
        if value(model.bucket_select[product, bucket]) >= 0.5:
            return bucket
    abs_gap = abs(float(value(model.abs_gap[product])))
    if abs_gap <= 0.10:
        return "score_100"
    if abs_gap <= 0.20:
        return "score_80"
    if abs_gap <= 0.30:
        return "score_60"
    if abs_gap <= 0.40:
        return "score_40"
    return "score_0"


def extract_solution(model, result, solving_time: float) -> dict[str, object]:
    objective_value = float(value(model.objective))
    total_shortage = float(sum(value(model.shortage[product, week]) for product in model.PRODUCTS for week in model.WEEKS))
    total_air_shipment = float(sum(value(model.air_ship[product, week]) for product in model.PRODUCTS for week in model.WEEKS))
    total_air_cost = float(
        sum(
            value(model.air_ship[product, week]) * value(model.air_cost[product])
            for product in model.PRODUCTS
            for week in model.WEEKS
        )
    )

    alloc_total = float(value(model.alloc_total))
    total_demand = float(value(model.total_demand))
    weeks = list(model.WEEKS)
    shipment_air_rows = []
    shipment_sea_rows = []
    shortage_rows = []
    alloc_by_model: dict[str, float] = {}
    gap_by_model: dict[str, float] = {}
    score_by_model: dict[str, int] = {}
    weight_by_model: dict[str, float] = {}
    weighted_total_score = 0.0

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

        bucket = _select_bucket(model, product)
        alloc_product = float(value(model.alloc_by_model[product]))
        gap_product = float(value(model.gap_by_model[product]))
        demand_total_product = float(value(model.demand_total_by_product[product]))
        demand_share = (demand_total_product / total_demand) if total_demand > 0 else 0.0
        score = BUCKET_SCORES[bucket]
        weight = BUCKET_WEIGHTS[bucket]

        alloc_by_model[product] = round(alloc_product, 6)
        gap_by_model[product] = round(gap_product, 6)
        score_by_model[product] = score
        weight_by_model[product] = round(weight, 4)
        weighted_total_score += score * demand_share

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
        "allocation_metrics": {
            "alloc_total": round(alloc_total, 6),
            "alloc_by_model": alloc_by_model,
            "gap_by_model": gap_by_model,
            "score_by_model": score_by_model,
            "weight_by_model": weight_by_model,
            "weighted_total_score": round(weighted_total_score, 4),
        },
        "tables": {
            "shipment_sea": shipment_sea_rows,
            "shipment_air": shipment_air_rows,
            "shortage": shortage_rows,
        },
    }
