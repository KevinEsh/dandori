from typing import Dict
from ortools.sat.python.cp_model import CpModel, IntVar


def makespan(model: CpModel, or_data: Dict[str, list], or_trans: Dict[str, list], target: str = "makespan") -> IntVar:
    """Activate makespan objetive

    Args:
        model (CpModel): OR-tools' SAT module.
        or_data (Dict[str, list]): Data structure with all ortools variables created.
        target (str, optional): Name of the variable. Defaults to "makespan".

    Returns:
        IntVar: Ortools variable in charge of tracking makespan
    """
    or_target = model.NewIntVar(0, 1 << 28, target)
    model.AddMaxEquality(or_target, [or_tuple.end
                                     for or_list in or_data.values()
                                     for or_tuple in or_list if or_tuple.active])
    return or_target


def transitions(model: CpModel,  or_data: Dict[str, list], or_trans: Dict[str, list], target="transitions") -> IntVar:
    or_target = model.NewIntVar(0, 1 << 28, target)
    model.Add(or_target == sum([or_tuple.duration
                                for or_list in or_trans.values()
                                for or_tuple in or_list if or_tuple.active]))
    return or_target


objetive_dict = {
    "makespan": makespan,
    "transitions": transitions,
}
