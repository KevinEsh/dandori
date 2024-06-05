from gstorm import GraphQLType
# * Validator dependency
from dandori.validators.valid_metadata import valid_metadata
from dandori.validators.valid_resource import valid_resource


model = "Stop"


def valid_stop(stop: GraphQLType, depth: int = 0) -> None:
    """Function to validate Stop data integrity

    Args:
        stop (GraphQL object): nested dictionary with info about Stops

    Raises:
        ValueError: if model metadata is not Stop
        ValueError: if resource insertedAt Date is later than update date, there is something wrong
    """
    modelname = valid_metadata(stop)
    if modelname != model:
        raise ValueError(f"instance {stop.id} is not '{model}' model")
    if not stop.stopReason:
        raise ValueError(
            f"{model} instance {stop.id} has no 'stopReason'")
    if stop.startAt > stop.endAt:
        raise ValueError(
            f"{model} instance {stop.id} 'startAt' is greater than 'endAt'")
    if not stop.cost:
        raise ValueError(
            f"{model} instance {stop.id} has no 'cost'")
    if not stop.stopResources:
        raise ValueError(
            f"{model} instance {stop.id} has no 'stopResources'")

    # Recursive validation
    if not depth:
        return

    for arc in stop.stopResources:
        valid_resource(arc.resource, depth-1)


if __name__ == "__main__":
    # Pa' juegar a las validaciones.
    from dandori.models import StopReason, Stop, Function, StopResource, Resource
    r = StopReason()
    f = Function()
    s = Stop(stopReason=r, cost=f, stopResources=[
             StopResource(resource=Resource(code="test"))])
    valid_stop(s, depth=1)
