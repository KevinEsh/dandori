from gstorm import GraphQLType
# * Validator dependency
from dandori.validators.valid_metadata import valid_metadata
from dandori.validators.valid_resource import valid_resource
from dandori.validators.valid_process import valid_process
from dandori.validators.valid_stop import valid_stop
from dandori.validators.valid_uom import valid_uom

model = "Plan"


def valid_plan(plan: GraphQLType, depth: int = 0) -> None:
    """Function to validate Plan data integrity

    Args:
        stop (GraphQL object): nested dictionary with info about Plans

    Raises:
        ValueError: if model metadata is not Plan
        ValueError: if progress is lower than cero
        ValueError: if quantity is lower than cero
        ValueError: if quantity has no UnitOfMeasurement
        ValueError: if has no status
        ValueError: if startAt is lower than endAt
        ValueError: if has no process or stop
    """
    modelname = valid_metadata(plan)
    if modelname != model:
        raise ValueError(f"instance {plan.id} is not '{model}' model")
    if plan.progress < 0:
        raise ValueError(
            f"{model} instance {plan.id} has 'progress' lower than 0")
    if plan.quantity < 0:
        raise ValueError(
            f"{model} instance {plan.id} has 'quantity' lower than 0")
    if not plan.quantityUom:
        raise ValueError(
            f"{model} instance {plan.id} has no 'quantityUom'")
    if not plan.resource:
        raise ValueError(
            f"{model} instance {plan.id} has no 'resource'")
    if not plan.status:
        raise ValueError(
            f"{model} instance {plan.id} has no 'status'")
    if plan.startAt > plan.endAt:
        raise ValueError(
            f"{model} instance {plan.id} 'startAt' is greater than 'endAt'")
    if not (plan.process or plan.stop):
        raise ValueError(
            f"{model} instance {plan.id} has no 'process' or 'stop'")

    # Recursive validation
    if not depth:
        return

    valid_uom(plan.quantityUom, depth-1)
    valid_resource(plan.resource, depth-1)
    if plan.process:
        valid_process(plan.process, depth-1)
    else:
        valid_stop(plan.stop, depth-1)


if __name__ == "__main__":
    # Pa' juegar a las validaciones.
    from dandori.models import Plan, Stop, Process, UnitOfMeasurement, \
        Resource, Function, ProcessMaterial, ProcessResource
    from datetime import datetime
    m = Resource(code="test")
    t = Function()
    u = UnitOfMeasurement(name="test", symbol="t")
    f = Process(name="test", timeFunction=t,
                processMaterials=[ProcessMaterial()],
                processResources=[ProcessResource()])
    r = Stop(stopReason="hola", cost="tim")
    s = Plan(quantityUom=u, startAt=datetime.min, stop=r, resource=m)
    valid_plan(s, depth=1)
