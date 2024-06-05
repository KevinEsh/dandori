
from __future__ import annotations
from typing import List, Union
from datetime import datetime, date, time
from gstorm.GraphQLType import GraphQLType
from gstorm.helpers.typing_helpers import convert_to, list_convert_to, gql_repr, gql_list_repr
from gstorm.helpers.date_helpers import iso8601_to_local_date, get_datetime_object
import attr
from enum import Enum
from .FunctionType import FunctionType

class FunctionAttrs(Enum):
	ID = 'ID'
	CODE = 'CODE'
	DESCRIPTION = 'DESCRIPTION'
	ENABLED = 'ENABLED'
	NAME = 'NAME'
	INSERTED_AT = 'INSERTED_AT'
	UPDATED_AT = 'UPDATED_AT'

mpath = 'scheduler.models'

@attr.s
class Function(GraphQLType):
    code: str = attr.ib(default='', metadata={'unique':True,'type':str,'model':None})
    name: str = attr.ib(default='', metadata={'type':str,'model':None})
    enabled: bool = attr.ib(default=True, metadata={'type':bool,'model':None})
    functionType: FunctionType = attr.ib(default='UNDEFINED', converter=convert_to(mpath,'FunctionType'), metadata={'type':Enum,'model':'FunctionType'})
    uom: 'UnitOfMeasurement' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'UnitOfMeasurement'), metadata={'type':GraphQLType,'model':'UnitOfMeasurement'})
    description: str = attr.ib(default='', metadata={'type':str,'model':None})
    processes: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Process'), metadata={'type':list,'model':'Process'})
    processMaterials: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'ProcessMaterial'), metadata={'type':list,'model':'ProcessMaterial'})
    materialArcs: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'MaterialArc'), metadata={'type':list,'model':'MaterialArc'})
    changeovers: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Changeover'), metadata={'type':list,'model':'Changeover'})
    stops: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Stop'), metadata={'type':list,'model':'Stop'})
