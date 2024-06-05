from datetime import datetime
from gstorm import GraphQLType
# * Validators dependencies
from dandori.validators.valid_metadata import valid_metadata


def valid_pivot(obj: GraphQLType, pivot: datetime) -> None:
    """Validate if input instance is on time for the pivot

    Args:
        obj (GraphQLType): GraphQLType instance with endAt
        pivot (datetime): Minimum timestamp of the object

    Raises:
        ValueError: Is not a Demand's instance
        ValueError: Has no guid
        ValueError: Extension is invalid
        ValueError: Has no status
        ValueError: Has niether demand to solve or came from one
    """
    modelname = valid_metadata(obj)
    if 'endAt' not in obj.get_public_fields():
        raise ValueError(f"{modelname} instance {obj.id} has no 'endAt' attribute")
    if obj.endAt <= pivot:
        raise ValueError(f"{modelname} instance {obj.id} not in time for 'pivot'")
