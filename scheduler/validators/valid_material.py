from gstorm import GraphQLType
# * Validators dependencies
from scheduler.validators.valid_metadata import valid_metadata


model = "Material"


def valid_material(material: GraphQLType, depth: int = 0) -> None:
    """Function to validate material data integrity

    Args:
        material (GraphQL object): nested dictionary with info about materials

    Raises:
        ValueError: if model metadata is not Material
        ValueError: if material insertedAt Date is later than update date, there is something wrong
    """
    modelname = valid_metadata(material)
    if modelname != model:
        raise ValueError(f"instance {material.id} is not '{model}' model")
    if not material.code:
        raise ValueError(f"{model} instance {material.id} has no 'code'")
