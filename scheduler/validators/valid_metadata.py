from pydash import get
from gstorm import GraphQLType
from scheduler.helpers import metadata as mt

_sdltypes = ["model", "arcs", "relation", "enum"]


def valid_metadata(datum: GraphQLType) -> str:
    Model = mt.get_model_class(datum, _sdltypes)
    fields = Model.get_public_fields()

    # Valid each non-empty attribute
    for field in fields:
        attribute = get(datum, field)
        if not attribute:
            continue
        # Ensure all got the expected type
        expectedtype = Model.get_metadata(field)["type"]
        if not isinstance(attribute, expectedtype):
            raise ValueError(
                f"instance {id(datum)} has invalid type in field '{field}'. Got {type(attribute)} instead of {expectedtype}")
        # Ensure all got the expected model if any
        expectedmodel = Model.get_metadata(field)["model"]
        if expectedmodel:
            if expectedtype == list:
                submodels = attribute
            else:
                submodels = [attribute]
            # Validation each sub-instance
            for submodel in submodels:
                submodelname = mt.get_schedule_logic_name(submodel)
                if submodelname != expectedmodel:
                    raise ValueError(
                        f"instance {id(datum)} has invalid model in field '{field}'. Got '{submodelname}' instead of '{expectedmodel}'")
    return Model.__name__
