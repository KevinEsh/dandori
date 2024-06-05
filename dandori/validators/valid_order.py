from gstorm import GraphQLType
# * Validator dependencies
from dandori.validators.valid_metadata import valid_metadata
from dandori.validators.valid_material import valid_material
from dandori.validators.valid_uom import valid_uom


model = "Order"


def valid_order(order: GraphQLType, depth: int = 0) -> None:
    """Function to validate order data integrity

    Args:
        order (GraphQLType): nested dictionary with info about Orders

    Raises:
        ValueError: if model metadata is not Order
        ValueError: verify if start date is before end date
        ValueError: verify that priorities are in the range 0-10
    """
    modelname = valid_metadata(order)
    if modelname != model:
        raise ValueError(f"instance {order.id} is not '{model}' model")
    if not order.name:
        raise ValueError(f"{model} instance {order.id} has no 'name'")
    if not order.quantityUom:
        raise ValueError(f"{model} instance {order.id} has no 'quantityUom'")
    if not order.material:
        raise ValueError(f"{model} instance {order.id} has no 'material'")
    if order.startAt > order.endAt:
        raise ValueError(
            f"{model} instance {order.id} 'startAt' is greater than 'endAt'")
    if order.quantity < 0:
        raise ValueError(
            f"{model} instance {order.id} has 'quantity' lower than 0")
    if not 0 <= order.priority <= 100:
        raise ValueError(
            f"{model} instance {order.id} has 'priority' outside valid interval [0,100]")

    # Recursive validation
    if not depth:
        return

    valid_material(order.material, depth-1)
    valid_uom(order.quantityUom, depth-1)


if __name__ == "__main__":
    from dandori.models import Order, UnitOfMeasurement, Material
    from datetime import datetime
    m = Material(code="test-code")
    uom = UnitOfMeasurement(name="test-name", symbol="t")
    o = Order(code="3afsd", quantity=10, priority=11, quantityUom=uom,
              material=m, startAt=datetime.min)
    valid_order(o, depth=1)
