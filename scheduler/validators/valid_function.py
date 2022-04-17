from gstorm import GraphQLType
# * Validator dependencies
from scheduler.validators.valid_metadata import valid_metadata
from scheduler.validators.valid_uom import valid_uom

model = "Function"


def valid_function(function: GraphQLType, depth: int = 0) -> None:
    """Validate if input instance is a valid "Funtion" otherwise raise a ValueError exception

    Args:
        function (GraphQLType): GraphQLType instance from a "Funtion" class

    Raises:
        ValueError: Is not a Funtion's instance
        ValueError: Has not code
        ValueError: Has not type
        ValueError: Has not uom associated
    """
    modelname = valid_metadata(function)
    if modelname != model:
        raise ValueError(f"instance {function.id} is not '{model}' model")
    if not function.code:
        raise ValueError(f"{model} instance {function.id} has no 'code'")
    if not function.functionType:
        raise ValueError(
            f"{model} instance {function.id} has no 'functionType'")
    if not function.uom:
        raise ValueError(f"{model} instance {function.id} has no 'uom'")

    # Recursive validation
    if not depth:
        return

    valid_uom(function.uom, depth-1)


if __name__ == "__main__":
    # Pa' juegar a las validaciones.
    from scheduler.models import Function, Material, UnitOfMeasurement
    uom = UnitOfMeasurement(name="test-uom", symbol="T")
    f = Function(code="10", uom=uom)
    f2 = Material()
    valid_function(f, depth=1)
