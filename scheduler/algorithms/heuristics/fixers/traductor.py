from typing import List, Dict
from pydash import group_by, filter_
from collections import defaultdict
from datetime import datetime, timedelta
from networkx import DiGraph, topological_sort

from scheduler.models import Program, Plan, Recipe
from scheduler.helpers.datetools import is_intersected
from scheduler.helpers.graphtools.tools import create_plan_graph


def reset_interval_program(program: Program) -> None:
    """Function to update program after an modification

    Args:
        program (Program): Program to be updated
    """
    if not program.plans:
        return

    # Reset program's interval
    program.startAt = min(plan.startAt for plan in program.plans)
    program.endAt = max(plan.endAt for plan in program.plans)


def solve_overlaped_dependency(GraphPlan: DiGraph) -> None:
    """Solve overlapped graph dependency

    Args:
        GraphPlan (DiGraph): Graph contained connected plans
    """
    nodes = list(topological_sort(GraphPlan))

    for i in range(1, len(nodes)):
        u = nodes[i-1]
        v = nodes[i]
        prev_plan = GraphPlan[i-1]["plan"]
        next_plan = GraphPlan[i]["plan"]
        # Delay next plan if it is overlaped and depend of each others, else skip
        if (u, v) in GraphPlan.edges() and is_intersected(prev_plan, next_plan):
            delay_plans([next_plan], prev_plan.endAt)


def identify_common_recipe(plans: List[Plan], recetary: Dict) -> Recipe:
    """Takes a list of plans and retrieve the common recipe that generated the plans

    Args:
        plans (List[Plan]): List of plans with common recipe
        recetary (Dict): Dictionary of recipes

    Raises:
        RuntimeError: If the plans has more than one common recipe

    Returns:
        Recipe: Common recipe
    """
    all_recipes = []
    for plan in plans:
        mcode = plan.order.material.code
        rcode = plan.recipe.code  # !
        recipe = recetary[mcode][rcode]
        all_recipes.append(recipe)

    if len(all_recipes) > 1:
        ids = [plan.id for plan in plans]
        raise RuntimeError(f"List of plans {ids} has more than one common recipe")

    return all_recipes[0]


def stick_plans_to_graphs(program: Program, recetary: Dict) -> Dict[str, DiGraph]:
    """This function regenerates the graph recipes where the plans were created

    Args:
        program (Program): Program to solve
        recetary (Dict): Dictionary of recipes

    Returns:
        Dict[str, DiGraph]: GraphPlans sorted by order code
    """
    # Group plan by orders
    plans_by_order = group_by(program.plans, "order.code")
    graphs = defaultdict()

    for code, plans in plans_by_order.items():
        recipe = identify_common_recipe(plans, recetary)
        GraphPlan = create_plan_graph(recipe, plans)
        graphs[code] = GraphPlan

    return graphs


def delay_plans(plans: List[Plan], newStartAt: datetime, gap: int = 1) -> Plan:
    """Push the current plan to a new begining

    Args:
        plan (Plan): Plan to be modified
        newStartAt (datetime): New begining of the plan with the same extension

    Returns:
        Plan: Same plan with the interval time moved
    """
    gap = timedelta(seconds=gap)

    for plan in plans:
        extension = plan.endAt - plan.startAt
        plan.startAt = newStartAt + gap
        plan.endAt = newStartAt + extension + gap


def solve_overlaped_plans(program: List[Plan], recetary: Dict, pivot: datetime, max_tries: int = 10) -> None:
    """Solve overlaped plans in resource line

    Args:
        plans_tofix (List[Plan]): List of connected plans on the same program
        recetary (Dict): Global recetary of the materials
    """
    # Grouped by same resource in order to keep intact the no-overlap constrain in same resource
    graphs = stick_plans_to_graphs(program, recetary)
    plans_by_resource = group_by(program.plans, 'resource.code')
    overlaped_register = {code: False for code in plans_by_resource}

    iteration = 0
    while not all(overlaped_register.values()) and iteration < max_tries:
        iteration += 1
        for plans in plans_by_resource.values():
            # Sort & filter plans for easily detect overlaped
            plans = sorted(plans, key=lambda plan: plan.startAt)
            plans = filter_(plans, lambda plan: plan.endAt >= pivot)

            for i in range(1, len(plans)):
                if is_intersected(plans[i], plans[i-1]):
                    # Delay next plan if it is overlaped by prev else skip
                    delay_plans(plans[i], plans[i-1].endAt)
                    GraphPlan = graphs[plans[i].order.code]
                    solve_overlaped_dependency(GraphPlan)

    if all(overlaped_register.values()):
        return 1  # FEASIBLE
    else:
        return 3  # UNFEASIBLE
