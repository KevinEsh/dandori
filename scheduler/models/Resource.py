
from __future__ import annotations
from typing import List, Union
from datetime import datetime, date, time
from gstorm.GraphQLType import GraphQLType
from gstorm.helpers.typing_helpers import convert_to, list_convert_to, gql_repr, gql_list_repr
from gstorm.helpers.date_helpers import iso8601_to_local_date, get_datetime_object
import attr
from enum import Enum
from .ResourceType import ResourceType

class ResourceAttrs(Enum):
	ID = 'ID'
	CODE = 'CODE'
	DEVICE_ID = 'DEVICE_ID'
	ENABLED = 'ENABLED'
	NAME = 'NAME'
	INSERTED_AT = 'INSERTED_AT'
	UPDATED_AT = 'UPDATED_AT'

mpath = 'scheduler.models'

@attr.s
class Resource(GraphQLType):
    code: str = attr.ib(default='', metadata={'unique':True,'type':str,'model':None})
    name: str = attr.ib(default='', metadata={'type':str,'model':None})
    enabled: bool = attr.ib(default=True, metadata={'type':bool,'model':None})
    resourceType: ResourceType = attr.ib(default='UNDEFINED', converter=convert_to(mpath,'ResourceType'), metadata={'type':Enum,'model':'ResourceType'})
    properties: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Property'), metadata={'type':list,'model':'Property'})
    prevs: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'ResourceArc'), metadata={'type':list,'model':'ResourceArc'})
    nexts: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'ResourceArc'), metadata={'type':list,'model':'ResourceArc'})
    resourceMaterials: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'ResourceMaterial'), metadata={'type':list,'model':'ResourceMaterial'})
    processResources: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'ProcessResource'), metadata={'type':list,'model':'ProcessResource'})
    lots: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Lot'), metadata={'type':list,'model':'Lot'})
    plans: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Plan'), metadata={'type':list,'model':'Plan'})
    stopResources: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'StopResource'), metadata={'type':list,'model':'StopResource'})
    plant: 'Plant' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Plant'), metadata={'type':GraphQLType,'model':'Plant'})
    deviceId: int = attr.ib(default=None, metadata={'type':int,'model':None})
