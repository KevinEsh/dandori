from gstorm import GraphQLType
# * Validator dependencies
from dandori.validators.valid_process import valid_process
from dandori.validators.valid_metadata import valid_metadata
from dandori.validators.valid_material import valid_material
from dandori.validators.valid_function import valid_function

model = "Changeover"


def valid_changeover(changeover: GraphQLType, depth: int = 0) -> None:
    """Validate if input instance is a valid "Changeover" otherwise raise a ValueError exception

    Args:
        changeover (GraphQLType): GraphQLType instance from a "Process" class

    Raises:
        ValueError: Is not a Process' instance
        ValueError: Has no name
        ValueError: Has no timeFuntion defined
        ValueError: Has no ingredients defined
        ValueError: Has no resources defined
        ValueError: Is not connected with another Processes
    """
    modelname = valid_metadata(changeover)
    if modelname != model:
        raise ValueError(f"instance {changeover.id} is not '{model}' model")
    if not changeover.changeoverFunction:
        raise ValueError(f"{model} instance {changeover.id} has no 'changeoverFunction'")
    if not changeover.before:
        raise ValueError(f"{model} instance {changeover.id} has no 'before'")
    if not changeover.after:
        raise ValueError(f"{model} instance {changeover.id} has no 'after'")
    if not changeover.process:
        raise ValueError(f"{model} instance {changeover.id} has no 'process'")

    # Recursive validation
    if not depth:
        return

    valid_function(changeover.changeoverFunction, depth-1)
    valid_material(changeover.before, depth-1)
    valid_material(changeover.after, depth-1)
    valid_process(changeover.process)


if __name__ == "__main__":
    from dandori.models import Changeover, Process, Material, Function
    a = Material()
    b = Material()
    p = Process()
    f = Function()
    c = Changeover(before=b, after=a, process=p, changeoverFunction=f)

    valid_changeover(c, depth=1)
