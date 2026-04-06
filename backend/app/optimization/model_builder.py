from pyomo.environ import ConcreteModel, Constraint, NonNegativeReals, Param, Set, Var

from app.optimization.objective import add_option2_objective


def build_model(model_input: dict[str, object]) -> ConcreteModel:
    model = ConcreteModel()

    products = model_input["products"]
    weeks = model_input["weeks"]
    resources = model_input["resources"]
    week_index = {week: index for index, week in enumerate(weeks)}
    previous_week = {week: weeks[index - 1] if index > 0 else None for index, week in enumerate(weeks)}

    model.PRODUCTS = Set(initialize=products, ordered=True)
    model.WEEKS = Set(initialize=weeks, ordered=True)
    model.RESOURCES = Set(initialize=resources, ordered=True)

    model.demand = Param(model.PRODUCTS, model.WEEKS, initialize=model_input["demand"], default=0)
    model.delivery = Param(model.PRODUCTS, model.WEEKS, initialize=model_input["delivery"], default=0)
    model.init_inventory = Param(model.PRODUCTS, initialize=model_input["init_inventory"], default=0)
    model.price = Param(model.PRODUCTS, initialize=model_input["price"], default=0)
    model.demand_priority = Param(model.WEEKS, initialize=model_input["demand_priority"], default=1)
    model.air_cost = Param(model.PRODUCTS, initialize=model_input["air_cost"], default=0)
    model.air_enabled = Param(model.PRODUCTS, initialize=model_input["air_enabled"], default=0)
    model.air_leadtime = Param(model.PRODUCTS, initialize=model_input["air_leadtime"], default=0)
    model.regular_enabled = Param(model.PRODUCTS, initialize=model_input["regular_enabled"], default=0)
    model.regular_leadtime = Param(model.PRODUCTS, initialize=model_input["regular_leadtime"], default=0)
    model.fixed_horizon_index = Param(model.PRODUCTS, initialize=model_input["fixed_horizon_index"], default=-1)
    model.fixed_shipment_launch = Param(model.PRODUCTS, model.WEEKS, initialize=model_input["fixed_shipment_launch"], default=0)
    model.resource_of = Param(model.PRODUCTS, initialize=model_input["resource_map"], default="")
    model.capacity = Param(model.RESOURCES, model.WEEKS, initialize=model_input["capacity"], default=0)
    model.demand_total_by_product = Param(
        model.PRODUCTS, initialize=model_input["demand_total_by_product"], default=0
    )
    model.revenue_upper_bound = Param(
        model.PRODUCTS, initialize=model_input["revenue_upper_bound_by_product"], default=0
    )
    model.total_demand = Param(initialize=model_input["total_demand"], default=0)

    model.fulfill = Var(model.PRODUCTS, model.WEEKS, within=NonNegativeReals)
    model.shortage = Var(model.PRODUCTS, model.WEEKS, within=NonNegativeReals)
    model.regular_ship = Var(model.PRODUCTS, model.WEEKS, within=NonNegativeReals)
    model.air_ship = Var(model.PRODUCTS, model.WEEKS, within=NonNegativeReals)
    model.inventory = Var(model.PRODUCTS, model.WEEKS, within=NonNegativeReals)

    regular_arrivals: dict[tuple[str, str], list[str]] = {}
    air_arrivals: dict[tuple[str, str], list[str]] = {}
    for product in products:
        regular_lt = int(model_input["regular_leadtime"].get(product, 0))
        air_lt = int(model_input["air_leadtime"].get(product, 0))
        for week in weeks:
            current_index = week_index[week]
            regular_launches = []
            air_launches = []
            regular_source_index = current_index - regular_lt
            air_source_index = current_index - air_lt
            if regular_source_index >= 0:
                regular_launches.append(weeks[regular_source_index])
            if air_source_index >= 0:
                air_launches.append(weeks[air_source_index])
            regular_arrivals[(product, week)] = regular_launches
            air_arrivals[(product, week)] = air_launches

    def demand_balance_rule(m: ConcreteModel, product: str, week: str) -> Constraint:
        return m.fulfill[product, week] + m.shortage[product, week] == m.demand[product, week]

    def inventory_balance_rule(m: ConcreteModel, product: str, week: str) -> Constraint:
        regular_arrival = sum(m.regular_ship[product, launch_week] for launch_week in regular_arrivals[(product, week)])
        air_arrival = sum(m.air_ship[product, launch_week] for launch_week in air_arrivals[(product, week)])
        prev_week = previous_week[week]
        if prev_week is None:
            return (
                m.inventory[product, week]
                == m.init_inventory[product]
                + m.delivery[product, week]
                + regular_arrival
                + air_arrival
                - m.fulfill[product, week]
            )
        return (
            m.inventory[product, week]
            == m.inventory[product, prev_week]
            + m.delivery[product, week]
            + regular_arrival
            + air_arrival
            - m.fulfill[product, week]
        )

    def air_enable_rule(m: ConcreteModel, product: str, week: str) -> Constraint:
        return m.air_ship[product, week] <= m.demand[product, week] * m.air_enabled[product]

    def regular_enable_rule(m: ConcreteModel, product: str, week: str) -> Constraint:
        planning_open = 1 if week_index[week] > int(m.fixed_horizon_index[product]) else 0
        return m.regular_ship[product, week] <= m.demand[product, week] * m.regular_enabled[product] * planning_open

    def fulfill_limit_rule(m: ConcreteModel, product: str, week: str) -> Constraint:
        return m.fulfill[product, week] <= m.demand[product, week]

    def resource_capacity_rule(m: ConcreteModel, resource: str, week: str) -> Constraint:
        assigned_products = [product for product in m.PRODUCTS if m.resource_of[product] == resource]
        if not assigned_products:
            return Constraint.Skip
        return sum(
            m.fixed_shipment_launch[product, week] + m.regular_ship[product, week] + m.air_ship[product, week]
            for product in assigned_products
        ) <= m.capacity[resource, week]

    model.demand_balance = Constraint(model.PRODUCTS, model.WEEKS, rule=demand_balance_rule)
    model.inventory_balance = Constraint(model.PRODUCTS, model.WEEKS, rule=inventory_balance_rule)
    model.air_enable = Constraint(model.PRODUCTS, model.WEEKS, rule=air_enable_rule)
    model.regular_enable = Constraint(model.PRODUCTS, model.WEEKS, rule=regular_enable_rule)
    model.fulfill_limit = Constraint(model.PRODUCTS, model.WEEKS, rule=fulfill_limit_rule)
    model.resource_capacity = Constraint(model.RESOURCES, model.WEEKS, rule=resource_capacity_rule)

    add_option2_objective(model)
    return model
