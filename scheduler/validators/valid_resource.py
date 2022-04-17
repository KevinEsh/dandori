from gstorm import GraphQLType
# * Validator dependency
from scheduler.validators.valid_metadata import valid_metadata


model = "Resource"


def valid_resource(resource: GraphQLType, depth: int = 0) -> None:
    """Function to validate Resource data integrity

    Args:
        resource (GraphQL object): nested dictionary with info about Resources

    Raises:
        ValueError: if model metadata is not Resource
        ValueError: if resource insertedAt Date is later than update date, there is something wrong
    """
    modelname = valid_metadata(resource)
    if modelname != model:
        raise ValueError(f"instance {resource.id} is not '{model}' model")
    if not resource.code:
        raise ValueError(f"{model} instance {resource.id} has no 'code'")
    if not resource.resourceType:
        raise ValueError(
            f"{model} instance {resource.id} has no 'resourceType'")

    # Recursive validation
    if not depth:
        return
