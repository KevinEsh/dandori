
from __future__ import annotations
from typing import List, Union
from datetime import datetime, date, time
from gstorm.GraphQLType import GraphQLType
from gstorm.helpers.typing_helpers import convert_to, list_convert_to, gql_repr, gql_list_repr
from gstorm.helpers.date_helpers import iso8601_to_local_date, get_datetime_object
import attr
from enum import Enum

class PropertyCategoryAttrs(Enum):
	ID = 'ID'
	CODE = 'CODE'
	NAME = 'NAME'
	INSERTED_AT = 'INSERTED_AT'
	UPDATED_AT = 'UPDATED_AT'

mpath = 'scheduler.models'

@attr.s
class PropertyCategory(GraphQLType):
    code: str = attr.ib(default='', metadata={'unique':True,'type':str,'model':None})
    name: str = attr.ib(default='', metadata={'type':str,'model':None})
    properties: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'PropertyCategoryGroup'), metadata={'type':list,'model':'PropertyCategoryGroup'})
