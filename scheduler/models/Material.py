
from __future__ import annotations
from typing import List, Union
from datetime import datetime, date, time
from gstorm.GraphQLType import GraphQLType
from gstorm.helpers.typing_helpers import convert_to, list_convert_to, gql_repr, gql_list_repr
from gstorm.helpers.date_helpers import iso8601_to_local_date, get_datetime_object
import attr
from enum import Enum

class MaterialAttrs(Enum):
	ID = 'ID'
	CODE = 'CODE'
	ENABLED = 'ENABLED'
	NAME = 'NAME'
	INSERTED_AT = 'INSERTED_AT'
	UPDATED_AT = 'UPDATED_AT'

mpath = 'scheduler.models'

@attr.s
class Material(GraphQLType):
    code: str = attr.ib(default='', metadata={'unique':True,'type':str,'model':None})
    name: str = attr.ib(default='', metadata={'type':str,'model':None})
    enabled: bool = attr.ib(default=True, metadata={'type':bool,'model':None})
    properties: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Property'), metadata={'type':list,'model':'Property'})
    prevs: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'MaterialArc'), metadata={'type':list,'model':'MaterialArc'})
    nexts: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'MaterialArc'), metadata={'type':list,'model':'MaterialArc'})
    recipeMaterials: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'RecipeMaterial'), metadata={'type':list,'model':'RecipeMaterial'})
    resourceMaterials: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'ResourceMaterial'), metadata={'type':list,'model':'ResourceMaterial'})
    processMaterials: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'ProcessMaterial'), metadata={'type':list,'model':'ProcessMaterial'})
    plans: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Plan'), metadata={'type':list,'model':'Plan'})
    orders: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Order'), metadata={'type':list,'model':'Order'})
    lots: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Lot'), metadata={'type':list,'model':'Lot'})
    befores: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Changeover'), metadata={'type':list,'model':'Changeover'})
    afters: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Changeover'), metadata={'type':list,'model':'Changeover'})
    materialPlants: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'MaterialPlant'), metadata={'type':list,'model':'MaterialPlant'})
