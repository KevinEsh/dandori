from typing import Dict, List, Callable
from datetime import datetime, timedelta
from collections import defaultdict, namedtuple
# Thrid-party dependencies
from pydash import group_by
from networkx import DiGraph, topological_sort
# Self dependencies
from dandori.models import Order, Plan, Program
from dandori.helpers.graphtools import calculate_durations
from dandori.algorithms.scheduling.routing_scheduler.globals import MAX_COST_PER_ARC

Vehicule = namedtuple("Vehicule", ["index", "allowedOrders"])


def create_or_indexmap(vehicules: List[str]) -> Dict[str, Vehicule]:
    """Create an dictionary for each of the vehicules and his allowed orders

    Args:
        vehicules (List[str]): List with the all the vehicules' names

    Returns:
        Dict[str, Vehicule]: Index map for all vehicules
    """
    return {code: Vehicule(index=_id, allowedOrders=[])
            for _id, code in enumerate(vehicules)}


def costfunc_wrapper(function: Callable, TransGraph: DiGraph, manager) -> Callable:
    """Wrap common function to readable ortools functions

    Args:
        function (Callable): Functio to wrap
        TransGraph (nx.DiGraph): Transition graph of materials
        manager ([type]): Ortools manager

    Returns:
        Callable: Wrapped function
    """
    def callback(from_index, to_index):
        """Decrypt ortools variables to nodes

        Args:
            from_index (IntVar): prev node
            to_index (IntVar): next node

        Raises:
            RuntimeError: In case wrapped function return a non-integer

        Returns:
            int: Arc cost
        """
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)

        # If it has the node "depot" (zero) just return 0 (zero cost)
        if from_node == to_node or not from_node or not to_node:
            return 0

        # If there is not edge, is in blacklist. return unreachable value
        edge = TransGraph.get_edge_data(from_node, to_node)  # default=None
        if not edge:
            return MAX_COST_PER_ARC + 1

        # Get orders and call cost_function
        prev_order = TransGraph.nodes[from_node].get("order")  # default:None
        next_order = TransGraph.nodes[to_node].get("order")  # default:None

        value = function(prev_order, next_order, edge)
        if not isinstance(value, int):
            raise RuntimeError(f"Callable '{function.__name__}' did not return a integer value")
        return value

    return callback


def print_solution(manager, routing, solution, vehicules):
    """Prints solution on console
    """
    max_route_distance = 0
    for _id, vh in vehicules.items():
        index = routing.Start(_id)
        plan_output = 'Sequence for section {}:\n'.format(vh)
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += ' {} -> '.format(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, _id)
        plan_output += '{}\n'.format(manager.IndexToNode(index))
        plan_output += 'Number of washes: {}\n'.format(route_distance)
        max_route_distance += route_distance
        print(plan_output)
    print('Total number of washes: {}'.format(max_route_distance))


def get_vehicule_route(
        solution, routing,
        manager, vehicules,
        TransGraph) -> Dict[str, Order]:
    """Retrive vehicule solution in Schedule Logic data

    Args:
        solution ([type]): Ortools solution
        routing ([type]): Ortools model
        manager ([type]): Ortools manager
        vehicules ([type]): List of vehicules
        TransGraph ([type]): DiGraph of transitions between materials

    Returns:
        Dict[str, Order]: Data structure of sequenced orders
    """
    group = defaultdict(list)

    for _id, vehicule in vehicules.items():
        or_index = routing.Start(_id)
        # Getting sorted orders to generate plans
        while not routing.IsEnd(or_index):
            # Depot node not valid
            node = manager.IndexToNode(or_index)
            # Swap to next order
            or_index = solution.Value(routing.NextVar(or_index))
            # Saving order into data structure
            if node != 0:
                group[vehicule].append(TransGraph.nodes[node]["order"])
    return group


def last_use_in_resources(program: Program, pivot: datetime) -> Dict[str, datetime]:
    """Generate a dictionary with the resource's code and the last use in the
    current program. Default date is equal to 'pivot'

    Args:
        program (Program): Program to be analysed
        pivot (datetime): Set a default date in case a resource is not registered
            in the given program.

    Returns:
        Dict[str, datetime]: Defaultdict that returns a the last use datetime in
            a resource through its code
    """
    last_used = defaultdict(lambda: pivot)
    plans_by_resource = group_by(program.plans, "resource.code")

    for code, plans in plans_by_resource.items():
        last_used[code] = max(plans, key=lambda plan: plan.endAt).endAt

    return last_used


def stack_fifo_plans(
        orders: List[Order],
        code: int, program: Program,
        recetary: Dict[str, Dict[str, DiGraph]],
        pivot: datetime, scale: str) -> None:
    """Give and order list and this function will give you a fifo program

    Args:
        orders (List[Order]): List of orders
        code (int): Name of vehicule
        program (Program): Global program to insert plans
        recetary (Dict[str, Dict[str, nx.DiGraph]]): Global recetary
        pivot (datetime): Point on time to start appending plans
        scale (str): Scale of time which funtions give the output

    Raises:
        RuntimeError: [description]
    """
    last_used = last_use_in_resources(program, pivot)

    for order in orders:
        # Get selected recipe given the vehicule for the current material
        # ! cuidado. La restriccion de dependencia solo se cumple si el grafo es lineal: 0->1->2->3
        # TODO: modificar el generador de planes para que respete la restricción de dependencia.
        # * Hint: guardar los minEndAt de los nodos ya explorados en un defaultdict y usar G.incoming[node]
        GraphRecipe = recetary[order.material.code].get(code)

        if not GraphRecipe:
            raise RuntimeError(
                f"There is no recipe associate with material '{order.material.code}' in vehicule '{code}'")

        GraphRecipe.graph["order"] = order
        calculate_durations(GraphRecipe)  # calculate extension or processes
        sorted_nodes = list(topological_sort(GraphRecipe))  # FIFO sort

        for node in sorted_nodes:
            # Get maxStartAt from resource occupancy and calculate minEndAt
            info = GraphRecipe.nodes[node]
            maxStartAt = max(last_used[r.code] for r in info["resources"])
            minEndAt = maxStartAt + timedelta(**{scale: info["task"].duration})

            # Update last used in resources
            for r in info["resources"]:
                last_used[r.code] = minEndAt

            # Create a plan for each resource in the current process
            program.plans.extend([
                Plan(
                    endAt=minEndAt,
                    startAt=maxStartAt,
                    material=order.material,
                    toSolve=order,
                    resource=resource,
                    process=info["task"].process,
                ) for resource in info["resources"]
            ])
    return


def reset_program_interval(program: Program):
    """Reset interval program according to new plans added

    Args:
        program (Program): Current program with plans
    """
    program.startAt = min(program.plans, key=lambda plan: plan.startAt).startAt
    program.endAt = max(program.plans, key=lambda plan: plan.endAt).endAt
