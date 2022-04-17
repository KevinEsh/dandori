from gstorm import GraphQLType
# * Validators dependencies
from scheduler.validators.valid_metadata import valid_metadata


model = "UnitOfMeasurement"


def valid_uom(material: GraphQLType, depth: int = 0) -> None:
    """Function to validate material data integrity

    Args:
        material (GraphQL object): nested dictionary with info about materials

    Raises:
        ValueError: if model metadata is not Material
        ValueError: if has no name
        ValueError: if has no symbol
        ValueError: if has no uomType
    """
    modelname = valid_metadata(material)
    if modelname != model:
        raise ValueError(f"instance {material.id} is not '{model}' model")
    if not material.name:
        raise ValueError(f"{model} instance {material.id} has no 'name'")
    if not material.symbol:
        raise ValueError(f"{model} instance {material.id} has no 'symbol'")
    if not material.uomType:
        raise ValueError(f"{model} instance {material.id} has no 'uomType'")

    # Recursive validation
    if not depth:
        return


if __name__ == "__main__":
    from scheduler.models import UnitOfMeasurement
    uom = UnitOfMeasurement(name="test uom", symbol="T", UomType=None)
    valid_uom(uom)
