from gstorm import GraphQLType
# * Validator dependencies
from dandori.validators.valid_metadata import valid_metadata
from dandori.validators.valid_material import valid_material
from dandori.validators.valid_resource import valid_resource
from dandori.validators.valid_function import valid_function

model = "Process"


def valid_process(process: GraphQLType, depth: int = 0) -> None:
    """Validate if input instance is a valid "Process" otherwise raise a ValueError exception

    Args:
        process (GraphQLType): GraphQLType instance from a "Process" class

    Raises:
        ValueError: Is not a Process' instance
        ValueError: Has no name
        ValueError: Has no timeFuntion defined
        ValueError: Has no ingredients defined
        ValueError: Has no resources defined
        ValueError: Is not connected with another Processes
    """
    modelname = valid_metadata(process)
    if modelname != model:
        raise ValueError(f"instance {process.id} is not '{model}' model")
    if not process.name:
        raise ValueError(f"{model} instance {process.id} has no 'name'")
    if not process.timeFunction:
        raise ValueError(
            f"{model} instance {process.id} has no 'timeFunction'")
    if not process.processMaterials:
        raise ValueError(
            f"{model} instance {process.id} has no 'processMaterials'")
    if not process.processResources:
        raise ValueError(
            f"{model} instance {process.id} has no 'processResources'")
    # elif not process.prevs and not process.nexts:
    #     raise ValueError(
    #         f"{model} instance {process.id} is not connected to other '{model}'")

    # Recursive validation
    if not depth:
        return

    valid_function(process.timeFunction)
    for arc in process.processMaterials:
        valid_material(arc.material, depth-1)
    for arc in process.processResources:
        valid_resource(arc.resource, depth-1)


if __name__ == "__main__":
    from dandori.models import Process, UnitOfMeasurement, Function, ProcessMaterial, \
        Material, ProcessResource, Resource
    p = Process(name="test",
                timeFunction=Function(code="test", uom=UnitOfMeasurement()),
                processMaterials=[ProcessMaterial(
                    material=Material(code="test"))],
                processResources=[ProcessResource(
                    resource=Resource(code="test"))])
    valid_process(p, depth=3)
