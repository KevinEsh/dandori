import gstorm
import pydash
from typing import List
# * Helpers
from dandori.helpers.metadata import (
    get_schedule_logic_name, has_arcs, has_fields, raise_any_invalid, get_relation_field)


def upload_arcs(objects: List, more_fields: List = None, verbose: int = 0) -> None:
    if more_fields is None:
        more_fields = []
    # TODO: programar verbose
    # TODO: programar gestor de errores de gstorm

    # Validating model and arcs
    modelname = get_schedule_logic_name(objects[0])
    more_fields.extend(["prev", "next"])

    if not has_arcs(modelname):
        raise NotImplementedError(f"model {modelname} has no arcs")

    # Then iterates on all objects and upload the nexts arcs by one
    if not has_fields(modelname, fields=["nexts"]):
        raise Exception(f"model {modelname} has no attributes 'nexts'")

    for obj in objects:
        for arc in obj.nexts:
            response = gstorm.create(arc).children(more_fields).run()
            print(response.get("successful", False))


def upload_relations(objects: List, bmodelname: str, more_fields: List = None, verbose: int = 0) -> None:
    if more_fields is None:
        more_fields = []
    # TODO: programar verbose
    # TODO: programar gestor de errores de gstorm

    # Getting the model's name of all objects
    raise_any_invalid(bmodelname.capitalize())
    amodelname = get_schedule_logic_name(objects, single=True)
    field = get_relation_field(amodelname, bmodelname)
    more_fields.extend([amodelname.lower(), bmodelname.lower()])

    # Iterates on all objects and upload the relationship arcs by one
    for obj in objects:
        for rel in pydash.get(obj, field):
            response = gstorm.create(rel).children(more_fields).run()
            print(response.get("successful", False))
