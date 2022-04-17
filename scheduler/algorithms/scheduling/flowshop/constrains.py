from typing import Dict, List
# Thrid dependencies
from pydash import group_by
from networkx import DiGraph
from ortools.sat.python.cp_model import CpModel


def add_dependency(model: CpModel, GraphRecipe: DiGraph) -> None:
    """Constrain for network dependency betweeen processes. In other words,
    if one process must be perfomed before another, this constrain achieve
    thar purpose.

    Args:
        model (CpModel): Ortools CpModel containing or_vars variables
        GraphRecipe (DiGraph): Network dependency graph of the recipe on spot
    """
    or_recipe = GraphRecipe.graph["or_recipe"]
    for u, v in GraphRecipe.edges():
        or_prev = GraphRecipe.nodes[u]["or_vars"]
        or_next = GraphRecipe.nodes[v]["or_vars"]
        model.Add(or_prev.end <= or_next.start
                  ).OnlyEnforceIf(or_recipe)


def add_resource_no_overlap(model: CpModel, or_data: Dict[str, list], or_trans: Dict[str, list]) -> None:
    """Constrains that ensure that just a single process will be performed at any
    time in any resource.

    Args:
        model (CpModel): Ortools CpModel containing or_vars variables
        or_data (Dict[str, list], optional): Dictionary of ORtuples hashed and
            group by the name of the resource. Each Ortuple represent a process
            task. Defaults to defaultdict(list).
        or_trans (Dict[str, list], optional): Dictionary of ORtuples hashed and
            group by the name of the resource. Each Ortuple represent a transition
            between two dependant processes. Defaults to defaultdict(list).
    """
    for name, or_list in or_data.items():
        or_list += or_trans[name]
        model.AddNoOverlap([or_tuple.interval for or_tuple in or_list])


def add_optional_process(model: CpModel, GraphRecipe: DiGraph) -> None:
    """Constrain for activating one optional processes of a group if the recipe
    were activated. Otherwise none of this optional processes wil be activated

    Args:
        model (CpModel): Ortools CpModel containing or_recipe variables
        GraphRecipe (DiGraph): Network dependency graph of the recipe on spot
    """
    # TODO: como identificar un conjunto de procesos opcionales que pertenecen al mismo proceso?
    # TODO: Lo anterior deberia de ir en el schedule-logic?
    optional_processes = group_by(
        [info for _, info in GraphRecipe.nodes(data=True) if info.get("optional")], "group")

    for processes in optional_processes.values():
        # Current recipe was activated, select one optional process per group
        model.Add(sum(info["or_vars"].active for info in processes) == 1
                  ).OnlyEnforceIf(GraphRecipe.or_recipe)
        # Current recipe was not activated, no optional process are activated
        model.Add(sum(info["or_vars"].active for info in processes) == 0
                  ).OnlyEnforceIf(GraphRecipe.or_recipe.Not())


def add_single_recipe(model: CpModel, networks: List[DiGraph]) -> None:
    """Constrain for activating just one recipe from the given list of networks

    Args:
        model (CpModel): Ortools CpModel containing or_recipe variables
        networks (List[DiGraph]): List of network dependency graphs which
            contains or_recipe variables
    """
    model.Add(sum(GraphRecipe.graph["or_recipe"] for GraphRecipe in networks) == 1)
