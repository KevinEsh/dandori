import pytest
import pydash as ph
from dandori.helpers import datetools as dt
from dandori.examples import generate_random_inputs

cases = generate_random_inputs(cases=5, size=(3, 5))


@pytest.mark.fixers
@pytest.mark.parametrize(["guid", "inputs"], cases.items())
def test_plan_start_after_order_start(fixers_result, guid, inputs):
    """Una orden tiene un intervalo de cumplimiento. Cada orden puede ser
    satisfecha por un conjunto de procesos de línea. La unión de estos
    intervalos de procesos de línea deben de completar el intervalo de la ordens.
    Args:
        getPlanner (function):  planner
    """
    program = fixers_result(guid, **inputs)
    assert program, \
        f"Program (guid={guid}) was not successful"

    for plan in program.plans:
        if not plan.toSolve:
            continue
        assert plan.startAt + dt.tolerance >= plan.toSolve.startAt, \
            f"Plan {id(plan)} 'startAt' is lower than Order 'startAt'"


@pytest.mark.fixers
@pytest.mark.parametrize(["guid", "inputs"], cases.items())
def test_plan_end_before_order_end(fixers_result, guid, inputs):
    """Una orden tiene un intervalo de cumplimiento. Cada orden puede ser
    satisfecha por un conjunto de procesos de línea. La unión de estos
    intervalos de procesos de línea deben de completar el intervalo de la ordens.
    Args:
        getPlanner (function):  planner
    """
    program = fixers_result(guid, **inputs)

    for plan in program.plans:
        if not plan.toSolve:
            continue
        assert plan.endAt - dt.tolerance <= plan.toSolve.endAt, \
            f"Plan {id(plan)} 'endAt' is greater than Order 'endAt'"


@pytest.mark.fixers
@pytest.mark.parametrize(["guid", "inputs"], cases.items())
def test_plan_start_before_end(fixers_result, guid, inputs):
    """Una orden tiene un intervalo de cumplimiento. Cada orden puede ser
    satisfecha por un conjunto de procesos de línea. La unión de estos
    intervalos de procesos de línea deben de completar el intervalo de la ordens.
    Args:
        getPlanner (function):  planner
    """
    program = fixers_result(guid, **inputs)

    for plan in program.plans:
        if not plan.toSolve:
            continue
        assert plan.startAt <= plan.endAt, \
            f"Plan {id(plan)} 'startAt' is greater than 'endAt'"


@pytest.mark.fixers
@pytest.mark.parametrize(["guid", "inputs"], cases.items())
def test_plan_no_overlaping_by_resource(fixers_result, guid, inputs):
    """Una orden tiene un intervalo de cumplimiento. Cada orden puede ser
    satisfecha por un conjunto de procesos de línea. La unión de estos
    intervalos de procesos de línea deben de completar el intervalo de la ordens.
    Args:
        getPlanner (function):  planner
    """
    program = fixers_result(guid, **inputs)
    plans_by_resource = ph.group_by(program.plans,
                                    lambda plan: plan.resource.name)

    for name, listplans in plans_by_resource.items():
        if not name or not listplans:
            continue
        sortedplans = sorted(listplans, key=lambda plan: plan.startAt)
        size = len(sortedplans)
        for i in range(1, size):
            plan_a = sortedplans[i-1]
            plan_b = sortedplans[i]
            assert not dt.is_intersected(plan_a, plan_b), \
                f"Plans {id(plan_a)} & {id(plan_b)} are overlaped in Resource {name}"
