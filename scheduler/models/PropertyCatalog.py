
from __future__ import annotations
from typing import List, Union
from datetime import datetime, date, time
from gstorm.GraphQLType import GraphQLType
from gstorm.helpers.typing_helpers import convert_to, list_convert_to, gql_repr, gql_list_repr
from gstorm.helpers.date_helpers import iso8601_to_local_date, get_datetime_object
import attr
from enum import Enum

class PropertyCatalogAttrs(Enum):
	ID = 'ID'
	CODE = 'CODE'
	DESCRIPTION = 'DESCRIPTION'
	ENABLED = 'ENABLED'
	NAME = 'NAME'
	INSERTED_AT = 'INSERTED_AT'
	UPDATED_AT = 'UPDATED_AT'

mpath = 'scheduler.models'

@attr.s
class PropertyCatalog(GraphQLType):
    code: str = attr.ib(default='', metadata={'unique':True,'type':str,'model':None})
    name: str = attr.ib(default='', metadata={'type':str,'model':None})
    description: str = attr.ib(default='', metadata={'type':str,'model':None})
    enabled: bool = attr.ib(default=True, metadata={'type':bool,'model':None})
    valueUom: 'UnitOfMeasurement' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'UnitOfMeasurement'), metadata={'type':GraphQLType,'model':'UnitOfMeasurement'})
    categories: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'PropertyCategoryGroup'), metadata={'type':list,'model':'PropertyCategoryGroup'})
    properties: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Property'), metadata={'type':list,'model':'Property'})
    ranges: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'EliotVariableRange'), metadata={'type':list,'model':'EliotVariableRange'})
    states: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'EliotVariableState'), metadata={'type':list,'model':'EliotVariableState'})
