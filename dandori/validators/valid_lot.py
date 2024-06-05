from gstorm import GraphQLType
from dandori.validators.valid_metadata import valid_metadata
from dandori.validators.valid_resource import valid_resource
from dandori.validators.valid_material import valid_material
from dandori.validators.valid_uom import valid_uom

model = "Lot"


def valid_lot(lot: GraphQLType, depth: int = 0) -> None:
    """Validate if input instance is a valid "Lot" otherwise raise a ValueError exception

    Args:
        lot (GraphQLType): [description]

    Raises:
        ValueError: if model metadata is not Lot
        ValueError: if Lot has no lotType
        ValueError: if quantity is lower than cero
        ValueError: if quantity has no UnitOfMeasurement
        ValueError: if Lot has no Material
        ValueError: if Lot has not Resource
        ValueError: if startAt is lower than endAt
    """
    modelname = valid_metadata(lot)
    if modelname != model:
        raise ValueError(f"instance {lot.id} is not '{model}' model")
    if not lot.lotType:
        raise ValueError(f"{model} instance {lot.id} has no 'lotType'")
    if lot.quantity < 0:
        raise ValueError(
            f"{model} instance {lot.id} has 'quantity' lower than 0")
    if not lot.quantityUom:
        raise ValueError(f"{model} instance {lot.id} has no 'quantityUom'")
    if not lot.material:
        raise ValueError(f"{model} instance {lot.id} has no 'material'")
    if not lot.resource:
        raise ValueError(f"{model} instance {lot.id} has no 'resource'")
    if lot.startAt > lot.endAt:
        raise ValueError(
            f"{model} instance {lot.id} 'startAt' is greater than 'endAt'")

    # Recursive validation
    if not depth:
        return

    valid_material(lot.material, depth-1)
    valid_resource(lot.resource, depth-1)
    valid_uom(lot.quantityUom, depth-1)


if __name__ == "__main__":
    from dandori.models import Lot, UnitOfMeasurement, Material, Resource
    uom = UnitOfMeasurement()
    m = Material()
    r = Resource()
    lt = Lot(quantity=1, quantityUom=uom, material=m, resource=r)
    valid_lot(lt, depth=1)
