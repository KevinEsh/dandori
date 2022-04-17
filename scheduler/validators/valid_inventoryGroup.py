from gstorm import GraphQLType
from scheduler.validators.valid_metadata import valid_metadata
from scheduler.validators.valid_lot import valid_lot

model = "InventoryGroup"


def valid_inventoryGroup(invGroup: GraphQLType, depth: int = 0) -> None:
    """Function to validate InventoryGroup data integrity

    Args:
        inventorygroup (GraphQL object): nested dictionary with info about materials

    Raises:
        ValueError: if InventoryGroup insertedAt Date is later than update date, there is something wrong
        ValueError: if model metadata is not inventoryGroup
    """
    modelname = valid_metadata(invGroup)
    if modelname != model:
        raise ValueError(f"instance {invGroup.id} is not '{model}' model")
    if not invGroup.guid:
        raise ValueError(f"{model} instance {invGroup.id} has no 'guid'")
    if not invGroup.lots:
        raise ValueError(f"{model} instance {invGroup.id} has no 'lots'")

    # Recursive validation
    if not depth:
        return

    for lot in invGroup.lots:
        valid_lot(lot, depth-1)


if __name__ == "__main__":
    from scheduler.models import InventoryGroup, Lot
    lots = [Lot()]
    inv = InventoryGroup(guid="sdf")
    inv.lots.extend(lots)
    valid_inventoryGroup(inv)
