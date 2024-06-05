from typing import Dict, List
from datetime import datetime
from collections import defaultdict, namedtuple
# Thrid-party dependencies
from networkx import DiGraph
from gstorm import GraphQLType
from ortools.sat.python.cp_model import CpModel, IntVar
# Scheduler dependencies
from dandori.helpers import datetools as dt
from .objetives import objetive_dict

ORTuple = namedtuple("ORTuple", "active start end duration interval")


def ignite_recipe(model: CpModel, GraphRecipe: DiGraph, pivot: datetime, scale="hours") -> Dict[str, list]:
    """This function initialize ortools variables for a recipe given its Network
    dependency graph

    Args:
        model (CpModel): CpModel from OR-tools' SAT
        GraphRecipe (DiGraph): Network Dependency graph from the recipe
        program (GraphQLType): Main Program of the scheduler
        scale (str, optional): Scale of the time to conver datetimes to integers. Defaults to "hours".

    Returns:
        Dict[str, list]: Data structure that storage all ortools varaibles created
    """
    # Primitive variables
    recipe = GraphRecipe.graph["recipe"]
    order = GraphRecipe.graph["order"]
    start = dt.to_int(order.startAt, pivot, scale)
    end = dt.to_int(order.endAt, pivot, scale)

    # Ignite data structures
    or_data = defaultdict(list)
    or_recipe = model.NewBoolVar(recipe.code + "_recipe")
    GraphRecipe.graph["or_recipe"] = or_recipe

    for node, info in GraphRecipe.nodes(data=True):
        ref = f"{recipe.code}_{node}"
        duration = info["task"].duration

        # If it is an optional process, it has its own or_active
        if info["task"].optional:
            or_active = model.NewBoolVar(ref + '_active')
        # Otherwise, if the or_recipe is activated, all non-optional processes will be activated
        else:
            or_active = or_recipe

        # Ortools variables
        or_start = model.NewIntVar(start, end, f"{ref}_start")
        or_end = model.NewIntVar(start, end, f"{ref}_end")
        or_duration = model.NewIntVar(duration, duration, f"{ref}_duration")
        or_interval = model.NewOptionalIntervalVar(
            or_start,
            or_duration,
            or_end,
            or_active,
            f"{ref}_interval")

        or_tuple = ORTuple(
            active=or_active,
            start=or_start,
            end=or_end,
            duration=or_duration,
            interval=or_interval,
        )

        GraphRecipe.nodes[node]["or_vars"] = or_tuple
        for resource in info["resources"]:
            or_data[resource.name].append(or_tuple)

    return or_data


def ignite_program(model: CpModel, program: GraphQLType, pivot: datetime, scale: str = "hours") -> Dict[str, list]:
    """This function initialize ortools variables for a fixed plans given its program

    Args:
        model (CpModel): CpModel from OR-tools' SAT
        program (GraphQLType): Main Program of the scheduler
        scale (str, optional): Scale of the time to conver datetimes to integers. Defaults to "hours".

    Returns:
        Dict[str, list]: Data structure that storage all ortools varaibles created
    """
    # Ignite data structures
    or_data = defaultdict(list)

    for plan in program.plans:
        # Primitive variables
        ref = id(plan)
        name = plan.resource.name
        start = dt.to_int(plan.startAt, pivot, scale)
        end = dt.to_int(plan.endAt, pivot, scale)
        duration = end - start

        # Interval will always be activated by default
        # or_active = model.NewConstant(1)
        or_start = model.NewIntVar(start, start, f'{ref}_start')
        or_end = model.NewIntVar(end, end, f'{ref}_end')
        or_duration = model.NewIntVar(duration, duration, f'{ref}_duration')
        or_interval = model.NewIntervalVar(
            or_start, or_duration, or_end, f'{ref}_interval')

        or_tuple = ORTuple(
            active=None,
            start=or_start,
            end=or_end,
            duration=or_duration,
            interval=or_interval,
        )

        or_data[name].append(or_tuple)

    return or_data


def ignite_transitions(model: CpModel, GraphRecipe: DiGraph) -> Dict[str, list]:
    """This function initialize ortools variables for transitions between dependent processes

    Args:
        model (CpModel): CpModel from OR-tools' SAT
        GraphRecipe (DiGraph): Network Dependency graph from the recipe

    Returns:
        Dict[str, list]: Data structure that storage all ortools varaibles created
    """
    # Ignite data structures
    or_trans = defaultdict(list)

    for u, v in GraphRecipe.edges():
        # Are there resources in common?
        u_resources = GraphRecipe.nodes[u]["resources"]
        v_resources = GraphRecipe.nodes[v]["resources"]
        resources = [res for res in u_resources if res in v_resources]

        if not resources:
            continue

        # Getting protovariables from u & v
        or_prev = GraphRecipe.nodes[u]["or_vars"]
        or_next = GraphRecipe.nodes[v]["or_vars"]
        proto_prev = or_prev.start.Proto()
        proto_next = or_next.end.Proto()

        # Getting superposition of domains. This defines transition interval
        start = min(proto_prev.domain[0], proto_next.domain[0])
        end = max(proto_next.domain[1], proto_next.domain[1])
        duration = (0, end - start)

        # or_start = model.NewIntVar(start, end, f"{u}->{v}_start")
        # or_end = model.NewIntVar(start, end, f"{u}->{v}_end")
        or_active = model.NewBoolVar(f"{u}->{v}_active")
        or_start = or_prev.end
        or_end = or_next.start
        or_duration = model.NewIntVar(*duration, f"{u}->{v}_duration")
        or_interval = model.NewOptionalIntervalVar(or_start, or_duration, or_end, or_active,
                                                   f"{u}->{v}_interval")
        or_tuple = ORTuple(
            active=or_active,
            start=or_start,
            end=or_end,
            duration=or_duration,
            interval=or_interval,
        )

        # If both processes u & v are activated, then transition interval is active too
        model.AddMultiplicationEquality(
            or_active, [or_prev.active, or_next.active])

        # Saving ORTuple generated in data structures
        GraphRecipe.edges[u, v]["or_vars"] = or_tuple
        for resource in resources:
            or_trans[resource.name].append(or_tuple)

    return or_trans


def ignite_optimizator(
        model: CpModel,
        or_data: Dict[str, list],
        or_trans: Dict[str, list],
        targets: List[str] = None,
        mode: str = "minimize") -> List[IntVar]:
    """This function initialize optimized mode given the target from the user.

    Args:
        model (CpModel): CpModel from Ortools' SAT module
        or_data (Dict[str, list], optional): Data structure with all ortools
            variables created. Defaults to defaultdict(list).
        target (str, optional): Name of the objetive to optimize. Defaults to "makespan".
        mode (str, optional): Select "minimize" or "maximize". Defaults to "minimize".

    Returns:
        IntVar: OR-tools IntVar that reflect the objetive value
    """
    if targets is None:
        targets = ["makespan"]
    # TODO: Investigar si se puede acotar de una forma eficiente el intervalo del target
    # TODO: Programar una función que te dé la ecuación a optimizar
    # TODO: Programar un set de optimizadores predefinidos como el makespan
    or_targets = [objetive_dict[target](model, or_data, or_trans)
                  for target in targets]

    if mode == "minimize":
        model.Minimize(sum(or_targets))
    else:  # "maximize"
        model.Maximize(sum(or_targets))
    return or_targets
