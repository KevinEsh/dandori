
from __future__ import annotations
from typing import List, Union
from datetime import datetime, date, time
from gstorm.GraphQLType import GraphQLType
from gstorm.helpers.typing_helpers import convert_to, list_convert_to, gql_repr, gql_list_repr
from gstorm.helpers.date_helpers import iso8601_to_local_date, get_datetime_object
import attr
from enum import Enum

class EliotVariableRangeAttrs(Enum):
	ID = 'ID'
	VARIABLE_RANGE_ID = 'VARIABLE_RANGE_ID'
	INSERTED_AT = 'INSERTED_AT'
	UPDATED_AT = 'UPDATED_AT'

mpath = 'scheduler.models'

@attr.s
class EliotVariableRange(GraphQLType):
    propertyCatalog: 'PropertyCatalog' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'PropertyCatalog'), metadata={'type':GraphQLType,'model':'PropertyCatalog'})
    variableRangeId: int = attr.ib(default=None, metadata={'type':int,'model':None})
