from typing import Callable, List, Dict
from ortools.constraint_solver.pywrapcp import RoutingIndexManager, RoutingModel,\
    DefaultRoutingSearchParameters
from scheduler.algorithms.scheduling.routing_scheduler.globals import MAX_COST_PER_ARC,\
    MAX_TIME_PER_ARC, MAX_WAIT_TIME


def ignite_routing_manager(
        num_orders: int, num_resources: int, starts: List[int],
        ends: List[int]) -> RoutingIndexManager:
    """Initialice Ortools Index Manager for Routing Planner

    Args:
        num_orders (int): Number of orders into the current demand. This order are represented with index 1, 2, 3
        num_resources (int): Number of ortools vehicules which represent the line of process in which orders are made
        starts (List[int]): Optional constrain which set the vehicule i first operate order j
        ends (List[int]): Optional constrain which set the vehicule i last operate order k

    Returns:
        RoutingIndexManager: Ortools Routing Model
    """
    or_manager = RoutingIndexManager(
        num_orders,  # Numero de ordenes a completar
        num_resources,  # Num de secciones = num de vehículos en routing o numero de unidades
        starts,  # Todas las ordenes inician en depot (nodo ficticio)
        ends,  # Todas las ordenes terminan en depot (nodo ficticio)
    )
    return or_manager


def ignite_routing_model(manager: RoutingIndexManager) -> RoutingModel:
    """Initialice Ortools Routing Model

    Args:
        manager (RoutingIndexManager): Result from ignite_index_manager

    Returns:
        RoutingModel: Ortools Routing Model
    """
    or_model = RoutingModel(manager)

    return or_model


def ignite_search_params(parameters: Dict[str, int]) -> None:
    """Set the user parameters into the Ortool Routing Model

    Args:
        parameters (Dict[str, int]): Dictionary containing at least the keys
            "heuristic", "metaheuristic" & "solvertime". For more information
            get global HEURISTICS & METAHEURISTICS

    Returns:
        None: No output
    """
    or_params = DefaultRoutingSearchParameters()

    # Setting first solution heuristic.
    or_params.first_solution_strategy = parameters["heuristic"]

    # Setting metaheuristic solution
    or_params.local_search_metaheuristic = parameters["metaheuristic"]

    # Setting max solver time for metaheuristic
    or_params.time_limit.seconds = parameters["solvertime"]

    return or_params


def ignite_cost_function(wrapped_function: Callable, or_model: RoutingModel):
    """Initialice wrapped cost function given by the user. Wrapping this function
    with costfunc_wrapper is a must

    Args:
        wrapped_function (Callable): Wrapped user functiong with costfunc_wrapper
        or_model ([type]): Ortools Routing Model

    Returns:
        Dimension: Ortools Dimension
    """
    # Register callable function
    or_cost = or_model.RegisterTransitCallback(wrapped_function)

    # Define cost_callback of each arc as objetive
    or_model.SetArcCostEvaluatorOfAllVehicles(or_cost)

    # Add Dimension constraint. Params explanation:
    # slack_max = 0: No need to "wait"/"add" value in a node in order to respect constrains
    # !capacity = MAX_COST_PER_ARC: Max cost of the vehicule per arc.
    # This restriction is used to avoid forbiden arcs if they return >= MAX_COST + 1
    # fix_start_cumul_to_zero = True: Cost of each route of a vehicule start in cero
    or_model.AddDimension(or_cost, 0, MAX_COST_PER_ARC, True, 'cost')

    # Set importance of pareto in longest route
    or_dimension = or_model.GetDimensionOrDie("cost")
    or_dimension.SetGlobalSpanCostCoefficient(1)

    return or_dimension


def ignite_time_function(wrapped_function: Callable, or_model: RoutingModel):
    """Initialice wrapped cost function given by the user. Wrapping this function
    with costfunc_wrapper is a must.

    Args:
        wrapped_function (Callable): Wrapped user functiong with costfunc_wrapper
        or_model (RoutingModel): OR-tools' Routing Model for implementing scheduler

    Returns:
        Dimension: Ortools Time Dimension
    """
    # Register callable function
    or_time = or_model.RegisterTransitCallback(wrapped_function)

    # Define cost_callback of each arc as objetive
    or_model.SetArcCostEvaluatorOfAllVehicles(or_time)

    # Add Dimension constraint. Params explanation:
    # slack_max = 0: No need to "wait"/"add" value in a node in order to respect constrains
    # !capacity = MAX_COST_PER_ARC: Max cost of the vehicule per arc. This restriction is used to avoid forbiden arcs if they return >= MAX_COST + 1
    # fix_start_cumul_to_zero = False: Cost of each route of a vehicule start in cero
    or_model.AddDimension(or_time, MAX_WAIT_TIME,
                          MAX_TIME_PER_ARC, False, 'time')

    # Set importance of pareto in longest route
    or_dimension = or_model.GetDimensionOrDie("time")
    or_dimension.SetGlobalSpanCostCoefficient(
        0)  # time does not affect optimizer

    return or_dimension


def add_skilled_vehicules(data: Dict, or_manager: RoutingIndexManager, or_model: RoutingModel) -> None:
    """Add restriction such that only the orders with the correct recipe can be
    processed into the skilled vehicule

    Args:
        data (Dict): Data structure with the information of the resources (vehicules)
            and the orders that can processes each.
        or_manager (RoutingIndexManager): Ortools manager
        or_model (RoutingModel): Ortools Routing model
    """
    for order_id, allowed_resources in data.items():
        # -1 is in case the vehicule is not used
        allowed_resources = [-1, *(allowed_resources)]
        or_order = or_manager.NodeToIndex(order_id)
        or_model.VehicleVar(or_order).SetValues(allowed_resources)


def add_time_windows(node_info: List, or_model: RoutingModel, or_manager: RoutingIndexManager, or_time) -> None:
    """Add restriction to each city (order) such that the expected time of arrival
    and left are inside the constraint interval of the order [startAt, endAt]

    Args:
        node_info (List): Data structure for
        or_model (RoutingModel): [description]
        or_manager (RoutingIndexManager): [description]
        or_time ([type]): [description]
    """
    depot = 0
    # Add time window constraints for each location except depot.
    for node in node_info:
        if node.id == depot:
            continue
        or_order = or_manager.NodeToIndex(node.id)
        or_time.CumulVar(or_order).SetRange(node.start, node.end)

    resources = []
    for node in node_info:
        resources.extend(node.allowed_resources)

    # Add time window constraints for each vehicle start node.
    for resource_id in set(resources):  # !
        or_start = or_model.Start(resource_id)
        or_time.CumulVar(or_start).SetRange(0, MAX_WAIT_TIME)
