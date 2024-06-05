from gstorm import GraphQLType
# * Validator dependencies
from dandori.validators.valid_metadata import valid_metadata
from dandori.validators.valid_order import valid_order

model = "Demand"


def valid_demand(demand: GraphQLType, depth: int = 0) -> None:
    """Validate if input instance is a valid "Demand" otherwise raise a ValueError
    exception

    Args:
        demand (GraphQLType): GraphQLType instance from a "Demand" class

    Raises:
        ValueError: Is not a Demand's instance
        ValueError: Has no guid
        ValueError: Extension is invalid
        ValueError: Has no status
        ValueError: Has niether demand to solve or came from one
    """
    modelname = valid_metadata(demand)
    if modelname != model:
        raise ValueError(f"instance {demand.id} is not '{model}' model")
    if not demand.guid:
        raise ValueError(f"{model} instance {demand.id} has no 'guid'")
    if demand.startAt > demand.endAt:
        raise ValueError(f"{model} instance {demand.id} 'startAt' is greater than 'endAt'")
    if not demand.orders:
        raise ValueError(f"{model} instance {demand.id} has no 'orders'")

    # Recursive validation
    if not depth:
        return

    for order in demand.orders:
        valid_order(order, depth-1)


if __name__ == "__main__":
    # Pa' juegar a las validaciones.
    from dandori.models import Program, Demand
    from datetime import datetime
    d1 = Demand()
    d2 = Demand()
    f = Program(guid="122342", startAt=datetime.min, request=d1)
    valid_demand(f)
