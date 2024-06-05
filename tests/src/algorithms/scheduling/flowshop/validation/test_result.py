from typing import Callable
import pytest
import pydash as ph
from dandori.helpers import datetools as dt
from dandori.examples import generate_random_inputs

cases = generate_random_inputs(cases=5, size=(3, 5))


@pytest.mark.flowshop
@pytest.mark.parametrize(["guid", "inputs"], cases.items())
def test_plan_start_after_order_start(flowshop_result, guid, inputs):
    """Una orden tiene un intervalo de cumplimiento. Cada orden puede ser
    satisfecha por un conjunto de procesos de línea. La unión de estos
    intervalos de procesos de línea deben de completar el intervalo de la ordens.
    Args:
        getPlanner (function):  planner
    """
    program, status = flowshop_result(guid, **inputs)

    assert status not in ["MODEL_INVALID", "INFEASIBLE", "UNKNOWN"], \
        f"Program (guid={guid}) was not successful"

    for plan in program.plans:
        if not plan.toSolve:
            continue
        assert plan.startAt + dt.tolerance >= plan.toSolve.startAt, \
            f"Plan {id(plan)} 'startAt' is lower than Order 'startAt'"


@pytest.mark.flowshop
@pytest.mark.parametrize(["guid", "inputs"], cases.items())
def test_plan_end_before_order_end(flowshop_result, guid, inputs):
    """Una orden tiene un intervalo de cumplimiento. Cada orden puede ser
    satisfecha por un conjunto de procesos de línea. La unión de estos
    intervalos de procesos de línea deben de completar el intervalo de la ordens.
    Args:
        getPlanner (function):  planner
    """
    program, status = flowshop_result(guid, **inputs)

    assert status not in ["MODEL_INVALID", "INFEASIBLE", "UNKNOWN"], \
        f"Program (guid={guid}) was not successful"

    for plan in program.plans:
        if not plan.toSolve:
            continue
        assert plan.endAt - dt.tolerance <= plan.toSolve.endAt, \
            f"Plan {id(plan)} 'endAt' is greater than Order 'endAt'"


@pytest.mark.flowshop
@pytest.mark.parametrize(["guid", "inputs"], cases.items())
def test_plan_start_before_end(flowshop_result, guid, inputs):
    """Una orden tiene un intervalo de cumplimiento. Cada orden puede ser
    satisfecha por un conjunto de procesos de línea. La unión de estos
    intervalos de procesos de línea deben de completar el intervalo de la ordens.
    Args:
        getPlanner (function):  planner
    """
    program, status = flowshop_result(guid, **inputs)

    assert status not in ["MODEL_INVALID", "INFEASIBLE", "UNKNOWN"], \
        f"Program (guid={guid}) was not successful"

    for plan in program.plans:
        if not plan.toSolve:
            continue
        assert plan.startAt <= plan.endAt, \
            f"Plan {id(plan)} 'startAt' is greater than 'endAt'"


@pytest.mark.flowshop
@pytest.mark.parametrize(["guid", "inputs"], cases.items())
def test_plan_no_overlaping_by_resource(flowshop_result, guid, inputs):
    """Una orden tiene un intervalo de cumplimiento. Cada orden puede ser
    satisfecha por un conjunto de procesos de línea. La unión de estos
    intervalos de procesos de línea deben de completar el intervalo de la ordens.
    Args:
        getPlanner (function):  planner
    """
    program, status = flowshop_result(guid, **inputs)

    assert status not in ["MODEL_INVALID", "INFEASIBLE", "UNKNOWN"], \
        f"Program (guid={guid}) was not successful"

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


@pytest.mark.flowshop
@pytest.mark.parametrize(["guid", "inputs"], cases.items())
def test_optional_resources(flowshop_result: Callable, guid: int, inputs: dict[str, int]):
    """Optional group resources constraint. This works by selecting just one group
    of resources inside a process specified by the user. Scheduler must be able to
    select just one group in every iteration of the test that best optimize the
    objetive function

    Args:
        flowshop_result (Callable): Fixture for create a flowhop model
        guid (int): Parameter for recognize a specific flowshop model
        inputs (dict[str, int]): Parameters for randomly create input data
    """
    program, status = flowshop_result(guid, **inputs)

    assert status not in ["MODEL_INVALID", "INFEASIBLE", "UNKNOWN"], \
        f"Program (guid={guid}) was not successful"

    code = "TORC-FLWS"
    plans_by_process = ph.filter_(program.plans,
                                  lambda plan: plan.process.name == code)
    optional_resource_names = [plan.resource.name for plan in plans_by_process]

    assert optional_resource_names in [["A", "B"], ["C", "D"], ["E"], ["F"]], \
        f"Optional group Resouces are not correctly selected in Process '{code}'"

# def test_capacity_plans_by_resource(program, model):
#     """Test: De todos los lotes generados por la planeación, ninguno
#     de estos lotes debe de tener una cantidad asignada mayor que la capacidad
#     máxima del recurso al cual sea asignada.

#     Args:
#         getflowshoplanner (function): fsplanner
#     """
#     program, *_ = getflowshopPlanner
#     plans_by_resource = group_by(
#         program.plans, lambda plan: plan.resource.name)

#     for resource, plans in plans_by_resource.items():
#         if not resource or not plans:
#             continue
#         capacity = plans[0].resource.parameters["capacity"]
#         assert all(plan.quantity <= capacity for plan in plans), \
#             f'Un Resource con cantidad {plan.quantity} supera la capacidad del recurso {resource}'

# # 2


# def test_no_overlapping_lots_by_resource(getPlanner,):
#     """Test: De todos los tanques ningún tanque debe tener mas de dos lotes
#     asignados a mismo tiempo. Esto es, la intersección en los tiempos de lotes
#     de un solo tanque nunca debe de ocurrir y debe de haber un tiempo entre
#     ellos llamado LTR (lavado, trasiego, rellenado).

#     Args:
#         getPlanner (function):  planner
#     """
#     program, *_ = getPlanner
#     plans_by_resource = group_by(
#         program.plans, lambda plan: plan.resource.name)

#     for resource, plans in plans_by_resource.items():
#         if not resource or not plans:
#             continue
#         intervals = sorted([(plan.startAt, plan.endAt)
#                             for plan in plans], key=lambda plan: plan[0])
#         # Evaluando la condición de no traslape
#         for i in range(1, len(intervals)):
#             assert not.is_intersected(intervals[i-1], intervals[i]), \
#                 f'Dos o más Plans usan el mismo tanque {resource} al mismo tiempo'

# # 3


# def test_resource_empty(getflowshopPlanner):
#     """Test: el recurso debe estar vacio para considerarse antes de la planeacion

#     Args:
#         getflowshoplanner (function): fsplanner
#     """
#     program, *_ = getflowshopPlanner
#     plans_by_resource = group_by(
#         program.plans, lambda plan: plan.resource.name)

#     for resource, plans in plans_by_resource.items():
#         if not resource or not plans:
#             continue
#         for plan in plans:
#             assert plan.quantity is not None, \
#                 f'Un Resource con cantidad {plan.quantity} el recurso {resource} no esta vacio para la planeación deseada'

# # 4


# def test_compatibility_processes_by_lot(getPlanner,):
#     """Test:  la secuencia entre materiales a procesar puede llegar a ser inviable, se debe de corroborar
#     la viabilidad de la secuencia A->B

#     Args:
#         getPlanner (function):  planner
#     """
#     program, material_orders = getPlanner
#     plans_by_order = group_by(
#         program.plans, lambda plan: plan.toSolveOrder.name)

#     # Filtrando y creando los intervalos de los procesos de linea por orden
#     for order, plans in plans_by_order.items():
#         if not order or not plans:
#             continue
#         current_order = find(material_orders, lambda o: o.name == order)
#         for plan in plans:
#             assert.is_compatible(current_order.material, plan.material), \
#                 f"El MaterialOrder {order} tiene asignado un Plan con incompatibilidad enetre el recuso siguiente"

# # 5


# def test_quantity_plans_by_order(getPlanner):
#     """Test: Para cada uno de los lotes, existe un conjunto de procesos de línea.
#     la cantidad de los procesos de línea no debe de superar a la cantidad total del
#     lote asignado.
#     Args:
#         getPlanner (function):  planner
#     """
#     program, material_orders = getPlanner
#     plans_by_order = group_by(
#         program.plans, lambda plan: plan.toSolveOrder.name)

#     # Revisando la cantidad en los lotes
#     for order, plans in plans_by_order.items():
#         if not order or not plans:
#             continue
#         current_order = find(material_orders, lambda o: o.name == order)
#         order_parameter["quantity"] = current_order.parameter["quantity"]
#         # Calculando la cantidad de volumen embotellado (procesos de linea)
#         total_bottled = sum(plan.parameter["quantity"] for plan in plans)
#         # Evaluando restricción
#         assert total_bottled <= order_parameter["quantity"], \
#             f'Cantidad procesada por Plans asignados a la MaterialOrder {order} supera a la cantidad de la misma orden'

# # 1


# def test_invetory_disponibility(getPlanner):
#     """Test: se tiene que corroborar que existe inventario disponible para llevar a cabo la orden solicitada
#         Args:
#         getPlanner (function):  planner
#     """

#     program, *_ = getPlanner
#     plans_by_resource = group_by(
#         program.plans, lambda plan: plan.resource.name)

#     for resource, plans in plans_by_resource.items():
#         if not resource or not plans:
#             continue
#         for plan in plans:
#             for i in plan.planInventories:
#                 assert is_intersected(plan.planInventories.inventory.startAt[i], plan.startAt), \
#                     f'El inventario {Inventory.type} no esta disponible para suplir el plan '

# # 2


# def test_invetory_resource_conectivity(getPlanner):
#     """Test: cada inventario está conectado a recursos específicos, por lo que se debe verificar la compatibilidad
#         de inventarios con recursos

#         Args:
#         getPlanner (function):  planner
#     """

#     program, *_ = getPlanner
#     plans_by_resource = group_by(
#         program.plans, lambda plan: plan.inventory.resource)

#     for resource, plans in plans_by_resource.items():
#         if not resource or not plans:
#             continue
#         for plan in plans:
#             for i in plan.planInventories:
#                 assert.is_intersected(plan.planInventories.inventory.startAt[i], plan.startAt), \
#                     f'El inventario {Inventory.type} no esta disponible para suplir el plan '
