from gstorm import GraphQLType
# * Validator dependencies
from scheduler.validators.valid_metadata import valid_metadata
from scheduler.validators.valid_demand import valid_demand

model = "Program"


def valid_program(program: GraphQLType, depth: int = 0) -> None:
    """Validate if input instance is a valid "Program" otherwise raise a ValueError exception

    Args:
        program (GraphQLType): GraphQLType instance from a "Program" class

    Raises:
        ValueError: Is not a Program's instance
        ValueError: Has no guid
        ValueError: Extension is invalid
        ValueError: Has no status
        ValueError: Has niether demand to solve or came from one
    """
    modelname = valid_metadata(program)
    if modelname != model:
        raise ValueError(f"instance {program.id} is not '{model}' model")
    if not program.guid:
        raise ValueError(f"{model} instance {program.id} has no 'guid'")
    if program.startAt > program.endAt:
        raise ValueError(
            f"{model} instance {program.id} 'startAt' is greater than 'endAt'")
    if not program.status:
        raise ValueError(f"{model} instance {program.id} has no 'status'")
    if not program.toSolve and not program.request:
        raise ValueError(
            f"{model} instance {program.id} has neither 'toSolve' nor 'request'")

    # Recursive validation
    if not depth:
        return

    if program.toSolve:
        valid_demand(program.toSolve, depth-1)
    if program.request:
        valid_demand(program.request, depth-1)


if __name__ == "__main__":
    # Pa' juegar a las validaciones.
    from scheduler.models import Demand, Order, Program
    from datetime import datetime
    d1 = Demand(guid="test", orders=[Order(code="test")])
    d2 = Demand()
    f = Program(guid="122342", startAt=datetime.min, request=d1)
    valid_program(f, depth=2)
