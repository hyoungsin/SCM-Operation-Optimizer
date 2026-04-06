from pyomo.environ import Binary, Constraint, Expression, NonNegativeReals, Objective, Param, Set, Var, maximize

BUCKETS = ("score_100", "score_80", "score_60", "score_40", "score_0")
BUCKET_SCORES = {
    "score_100": 100,
    "score_80": 80,
    "score_60": 60,
    "score_40": 40,
    "score_0": 0,
}
BUCKET_WEIGHTS = {
    "score_100": 1.0,
    "score_80": 0.8,
    "score_60": 0.6,
    "score_40": 0.4,
    "score_0": 0.0,
}
BUCKET_LOWER = {
    "score_100": 0.0,
    "score_80": 0.100001,
    "score_60": 0.200001,
    "score_40": 0.300001,
    "score_0": 0.400001,
}
BUCKET_UPPER = {
    "score_100": 0.10,
    "score_80": 0.20,
    "score_60": 0.30,
    "score_40": 0.40,
    "score_0": 1.0,
}
BIG_M = 1.0


def add_option2_objective(model) -> None:
    model.BUCKETS = Set(initialize=BUCKETS, ordered=True)
    model.bucket_score = Param(model.BUCKETS, initialize=BUCKET_SCORES)
    model.bucket_weight = Param(model.BUCKETS, initialize=BUCKET_WEIGHTS)
    model.bucket_select = Var(model.PRODUCTS, model.BUCKETS, within=Binary)
    model.abs_gap = Var(model.PRODUCTS, within=NonNegativeReals)
    model.weighted_revenue = Var(model.PRODUCTS, model.BUCKETS, within=NonNegativeReals)

    def fulfilled_total_by_model_rule(m, product):
        return sum(m.fulfill[product, week] for week in m.WEEKS)

    model.fulfilled_total_by_model = Expression(model.PRODUCTS, rule=fulfilled_total_by_model_rule)
    model.fulfilled_total = Expression(expr=sum(model.fulfill[product, week] for product in model.PRODUCTS for week in model.WEEKS))

    def alloc_total_rule(m):
        total_demand = float(m.total_demand.value)
        if total_demand <= 0:
            return 0.0
        return m.fulfilled_total / total_demand

    model.alloc_total = Expression(rule=alloc_total_rule)

    def alloc_by_model_rule(m, product):
        demand_total = float(m.demand_total_by_product[product])
        if demand_total <= 0:
            return m.alloc_total
        return m.fulfilled_total_by_model[product] / demand_total

    model.alloc_by_model = Expression(model.PRODUCTS, rule=alloc_by_model_rule)
    model.gap_by_model = Expression(model.PRODUCTS, rule=lambda m, product: m.alloc_by_model[product] - m.alloc_total)

    def revenue_by_model_rule(m, product):
        return sum(m.price[product] * m.demand_priority[week] * m.fulfill[product, week] for week in m.WEEKS)

    model.revenue_by_model = Expression(model.PRODUCTS, rule=revenue_by_model_rule)

    model.bucket_assignment = Constraint(
        model.PRODUCTS,
        rule=lambda m, product: sum(m.bucket_select[product, bucket] for bucket in m.BUCKETS) == 1,
    )
    model.abs_gap_upper = Constraint(
        model.PRODUCTS,
        rule=lambda m, product: m.abs_gap[product] >= m.gap_by_model[product],
    )
    model.abs_gap_lower = Constraint(
        model.PRODUCTS,
        rule=lambda m, product: m.abs_gap[product] >= -m.gap_by_model[product],
    )

    def bucket_upper_rule(m, product, bucket):
        return m.abs_gap[product] <= BUCKET_UPPER[bucket] + BIG_M * (1 - m.bucket_select[product, bucket])

    def bucket_lower_rule(m, product, bucket):
        return m.abs_gap[product] >= BUCKET_LOWER[bucket] - BIG_M * (1 - m.bucket_select[product, bucket])

    model.bucket_upper_bound = Constraint(model.PRODUCTS, model.BUCKETS, rule=bucket_upper_rule)
    model.bucket_lower_bound = Constraint(model.PRODUCTS, model.BUCKETS, rule=bucket_lower_rule)

    def weighted_revenue_upper_select_rule(m, product, bucket):
        return m.weighted_revenue[product, bucket] <= m.revenue_upper_bound[product] * m.bucket_select[product, bucket]

    def weighted_revenue_upper_revenue_rule(m, product, bucket):
        return m.weighted_revenue[product, bucket] <= m.revenue_by_model[product]

    def weighted_revenue_lower_rule(m, product, bucket):
        return (
            m.weighted_revenue[product, bucket]
            >= m.revenue_by_model[product] - m.revenue_upper_bound[product] * (1 - m.bucket_select[product, bucket])
        )

    model.weighted_revenue_upper_select = Constraint(
        model.PRODUCTS, model.BUCKETS, rule=weighted_revenue_upper_select_rule
    )
    model.weighted_revenue_upper_revenue = Constraint(
        model.PRODUCTS, model.BUCKETS, rule=weighted_revenue_upper_revenue_rule
    )
    model.weighted_revenue_lower = Constraint(model.PRODUCTS, model.BUCKETS, rule=weighted_revenue_lower_rule)

    def objective_rule(m):
        weighted_revenue_term = sum(
            m.bucket_weight[bucket] * m.weighted_revenue[product, bucket]
            for product in m.PRODUCTS
            for bucket in m.BUCKETS
        )
        air_penalty_term = sum(m.air_cost[product] * m.air_ship[product, week] for product in m.PRODUCTS for week in m.WEEKS)
        return weighted_revenue_term - air_penalty_term

    model.objective = Objective(rule=objective_rule, sense=maximize)
