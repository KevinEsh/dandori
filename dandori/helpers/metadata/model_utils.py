from sys import modules
from datetime import datetime
from inflect import engine
from inspect import getfullargspec
from collections import defaultdict
from enum import Enum
from typing import Callable, List, Union, Any
from gstorm import GraphQLType
from dandori.models import *
from dandori.models import __models__, __arcs__, __relations__, __enums__, __version__

_modules = modules[__name__]
eng = engine()

sdl_map_validation = defaultdict(lambda: lambda: False)
sdl_map_validation.update({
    "relation": lambda objname: objname in __relations__,
    "model": lambda objname: objname in __models__,
    "enum": lambda objname: objname in __enums__,
    "arcs": lambda objname: objname in __arcs__,
})

_global_time_scales = ["days", "hours", "minutes", "seconds"]


def raise_any_invalid(objname: str, sdltypes: List[str] = None):
    if sdltypes is None:
        sdltypes = ["model"]
    for sdl in sdltypes:
        if sdl_map_validation[sdl](objname):
            return
    raise NotImplementedError(
        f"'{objname}' not implemented in Schedule-Logic v{__version__} for {', '.join(sdltypes)}")


def raise_invalid_date(obj: Any) -> None:
    """Raise ValueError exception if input is not datetime.datetime instance

    Args:
        obj (Any): Any instance to be evaluated

    Raises:
        ValueError: Print a default message
    """
    if not isinstance(obj, datetime):
        raise ValueError(f"Expected 'datetime' instance. Got {type(obj)}")


def raise_invalid_scale(obj: Any) -> None:
    """Raise an exception if got an invalid time scale

    Args:
        obj (Any): Instance expected to be str and one of pre-defined time scales

    Raises:
        ValueError: If 'obj' instance is not str type
        NotImplementedError: If 'obj' instance is not one of the followings:
        "days", "hours", "minutes", "seconds"
    """
    if not isinstance(obj, str):
        raise ValueError(f"Expected 'str' instance but instead got {type(obj)}")

    if obj not in _global_time_scales:
        raise NotImplementedError(
            f'scale {obj} not implemented. Try one of this: {_global_time_scales}')


def get_schedule_logic_name(obj: Union[GraphQLType, Enum, str]) -> str:
    if isinstance(obj, (GraphQLType, Enum)):
        return obj.__class__.__name__
    elif isinstance(obj, str):
        return obj
    else:
        raise TypeError(
            f"expected 'GraphQLType', 'Enum' or 'str' object. Got: {obj}")


def get_model_class(obj: Union[GraphQLType, Enum, str], sdltypes: List[str] = None) -> GraphQLType:
    """Get Schedule-Logic class model from the given instance if it is in the current version

    Args:
        obj (Union[GraphQLType, str]): Instance of the Schedule-Logic model

    Raises:
        TypeError: If it is not an GraphQLType or str

    Returns:
        GraphQLType: Schedule-Logic class of the given instance
    """
    if sdltypes is None:
        sdltypes = ["model"]
    modelname = get_schedule_logic_name(obj)
    raise_any_invalid(modelname, sdltypes)

    if isinstance(obj, (GraphQLType, Enum)):
        return obj.__class__
    elif isinstance(obj, str):
        return getattr(_modules, obj)
    else:
        raise TypeError(
            f"instance has to be GraphQLType, Enum or str not {obj.__class__}")


def get_arc_class(obj: Union[GraphQLType, str]) -> GraphQLType:
    modelname = get_schedule_logic_name(obj)
    arcmodel = modelname + "Arc"

    if modelname in __arcs__:
        return get_model_class(modelname, ["arcs"])
    else:
        return get_model_class(arcmodel, ["arcs"])


def has_fields(modelname: str, fields: List) -> bool:
    # Getting public fields
    Model = getattr(_modules, modelname)
    public_fields = Model.get_public_fields()

    # Checking for existence
    if all(field in public_fields for field in fields):
        return True
    else:
        return False


def has_arcs(modelname: str) -> bool:
    raise_any_invalid(modelname)

    # Getting attributes of the class
    Model = getattr(_modules, modelname)
    fields = Model.get_public_fields()

    # Searching for one coincidence
    for field in fields:
        metamodel = Model.get_metadata(field)["model"]
        if metamodel in __arcs__:
            return True
    return False


def get_relation_field(obj_master: Union[GraphQLType, str], obj_slave: Union[GraphQLType, str], exception: bool = False) -> str:
    """This function search for a field in obj_master which is the same type of model that obj_slave.

    Args:
        obj_master (Union[GraphQLType, str]): Schedule-Logic model
        obj_slave (Union[GraphQLType, str]): Schedule-Logic model to use as key seach
        exception (bool, optional): If True raise exception in case no field was found else return None. Defaults to False.

    Raises:
        RuntimeError: In case no field was found between the two models

    Returns:
        str: field which connects 'obj_master' downstream with 'obj_slave'
    """
    slave_modelname = get_schedule_logic_name(obj_slave)
    MasterModel = get_model_class(obj_master, ["model", "arcs", "relation"])
    fields = set(MasterModel.get_public_fields()) - \
        {"id", "insertedAt", "updatedAt"}

    # TODO: (Opcional) En caso de que sean mas de un campo, entregar una lista de campos
    # Searching relation field of both models
    for field in fields:
        meta_modelname = MasterModel.get_metadata(field)["model"]
        if meta_modelname == slave_modelname:
            return field

        # No relation field was found, what's next?
    if exception:
        raise RuntimeError(
            f"No relation field was found between {MasterModel.__name__} and {slave_modelname}")
    return None


def get_relation_class(obj_a: Union[GraphQLType, str], obj_b: Union[GraphQLType, str]) -> GraphQLType:
    # Getting class model and name class
    amodelname = get_schedule_logic_name(obj_a).capitalize()
    bmodelname = get_schedule_logic_name(obj_b).capitalize()

    # Posibles relations between models
    relationname1 = amodelname + bmodelname
    relationname2 = bmodelname + amodelname

    # Return the real relation or die
    if sdl_map_validation["relation"](relationname1):
        return get_model_class(relationname1, ["relation"])
    elif sdl_map_validation["relation"](relationname2):
        return get_model_class(relationname2,  ["relation"])
    else:
        raise NotImplementedError(
            f"relation between {amodelname} and {bmodelname} not implemented in Schedule-Logic v{__version__}")


def __get_modelnames(objects: List[GraphQLType], single=False):
    # If it is a list, parse over all objects and get single names
    if isinstance(objects, list):
        modelnames = list({str(obj).split("(")[0] for obj in objects})
        if single:
            if len(modelnames) == 1:
                return modelnames[0]
            else:
                raise Exception(
                    f"list 'objects_a' has more than one model. Found {', '.join(modelnames)}")
        else:
            return modelnames


def plural_field(obj: Union[GraphQLType, Enum, str]) -> str:
    modelname = get_schedule_logic_name(obj)
    return eng.plural(modelname[0].lower() + modelname[1:])


def raise_invalid_func(function: Callable, ftype: FunctionType) -> None:
    """This method raise a ValueError exception if the given 'function' is not compatible with the Scheduler's standards

    Args:
        function (Callable): A callable function
        ftype (FunctionType): Type of output funtion. Read more about Schedule-Logic

    Raises:
        ValueError: If 'function' does not return an integer
        ValueError: If 'function' lacks the correct inputs
    """
    _inputs = {
        FunctionType.PROCESS_TIME: ["order", "process"],
        # TODO: Veficar cual es la mejor manera de invocar estas variables
        FunctionType.CHANGEOVER_COST: ["prev_order", "next_order", "changeover"],
        FunctionType.INGREDIENT_QUANTITY: ["order", "recipe"],
    }

    # Get function's metadata
    fargs = getfullargspec(function).annotations

    # Raise invalid function
    if not isinstance(function, Callable):
        raise ValueError(
            f"Instance {function} is not callable")
    if not fargs.get("return") == int:
        raise ValueError(
            f"Callable '{function.__name__}' does not return 'int' value")
    if not all(fargs.get(attr) for attr in _inputs[ftype]):
        raise ValueError(
            f"Callable '{function.__name__}' lacks one of the following parameters: {_inputs[ftype]}")


if __name__ == "__main__":
    def my_func(process: int, order: int) -> int:
        return 1 + 2
    a = 100

    raise_invalid_func(my_func, FunctionType.PROCESS_TIME)
