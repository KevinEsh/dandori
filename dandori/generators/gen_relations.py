from pydash import get
from random import sample
# * Typing dependencies
from typing import List, Tuple
from gstorm import GraphQLType
# * Helpers
from dandori.helpers import metadata as mt


def connect_models(objects_a: List[GraphQLType], objects_b: List[GraphQLType], sampled: int = None) -> Tuple[List[GraphQLType]]:
    """Given two list of Schedule-Logic instances of the same model, this funtion tries to create many-to-many relation models between the two list

    Args:
        objects_a (List[GraphQLType]): First list of instances. These instances have to have relation model with the second ones
        objects_b (List[GraphQLType]): Second list of instances. These instances have to have relation model with the first ones
        sampled (int, optional): Number of samples take from second list per each element of the first list. If argument is None, this function connect all elements. Defaults to None.

    Raises:
        RuntimeError: If there is no field between the two instances model of the lists

    Returns:
        Tuple[List[GraphQLType]]: Same lists of input objects 'a' and 'b' but connected downstream with the others
    """
    # Getting names of both instances
    a_mdlname = mt.get_schedule_logic_name(objects_a[0])
    b_mdlname = mt.get_schedule_logic_name(objects_b[0])

    # Getting Schedule-Logic model that correlates both models
    RelationModel = mt.get_relation_class(a_mdlname, b_mdlname)
    rel_mdlname = RelationModel.__name__
    rel_field = mt.plural_field(rel_mdlname)

    a_field = mt.get_relation_field(rel_mdlname, a_mdlname)
    b_field = mt.get_relation_field(rel_mdlname, b_mdlname)

    for obj_a in objects_a:
        selected_b = objects_b if not sampled else sample(objects_b, sampled)
        for obj_b in selected_b:
            # Creating instance of relation's model
            pair = {a_field: obj_a,
                    b_field: obj_b}
            relation = RelationModel(**pair)
            # Appending relation in both objects fields
            get(obj_a, rel_field).append(relation)
            get(obj_b, rel_field).append(relation)

    return objects_a, objects_b
