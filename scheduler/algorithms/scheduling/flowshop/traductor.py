from typing import List
from datetime import datetime, timedelta
from collections import defaultdict
from ortools.sat.python.cp_model import CpSolver
from networkx import DiGraph
from scheduler.models import Plan, Program, Stop
from scheduler.helpers import datetools as dt


def insert_plans(
        program: Program,
        solver: CpSolver,
        GraphRecipe: DiGraph,
        pivot: datetime,
        scale: str = "hours") -> None:
    """Function to map the OR-tools' CpSolver's solution variables into the
    Schedule-Logic plans in order to generate a program solution considerating
    all constrains and objective-function.

    Args:
        program (Program): Schedule logic instance to insert all the plans
        solver (CpSolver): OR-tools instace to view the value of the CpModel's variables
        GraphRecipe (DiGraph): Recipe Graph to download all the OR-tools variables from
        pivot (datetime): Minimal timestamp from which we calculate intervals
        scale (str, optional): Time scale for the duration of the plans. Defaults to "hours".
    """
    for _, info in GraphRecipe.nodes(data=True):

        active = solver.Value(info["or_vars"].active)
        if not active:
            continue

        start = solver.Value(info["or_vars"].start)
        end = solver.Value(info["or_vars"].end)
        process = info["task"].process
        recipe = GraphRecipe.graph["recipe"]
        order = GraphRecipe.graph["order"]

        program.plans.extend([Plan(
            startAt=pivot + timedelta(**{scale: start}),
            endAt=pivot + timedelta(**{scale: end}),
            program=program,
            resource=resource,
            process=process,
            toSolve=order,
            material=order.material,
            recipe=recipe,
        ) for resource in info["resources"]])


def insert_stops(program: Program, stops: List[Stop]) -> None:
    """This functions take a list of stops and create an associated plan and
    append it to the main program. Before that, this function unite overlaped
    stops into one

    Args:
        program (Program): Main Schedule-Logic program
        stops (List[Stop]): List of Schedule-Logic's Stops
    """
    stops_by_res = defaultdict(list)
    for stop in stops:
        for arc in stop.stopResources:
            stops_by_res[arc.resource.name].append((arc.resource, stop))
    for group in stops_by_res.values():
        plans = [Plan(
            endAt=stop.endAt,
            startAt=stop.startAt,
            program=program,
            resource=resource,
            stop=stop
        ) for resource, stop in group]
        program.plans.extend(dt.squash_intervals(plans))
