
from __future__ import annotations
from typing import List, Union
from datetime import datetime, date, time
from gstorm.GraphQLType import GraphQLType
from gstorm.helpers.typing_helpers import convert_to, list_convert_to, gql_repr, gql_list_repr
from gstorm.helpers.date_helpers import iso8601_to_local_date, get_datetime_object
import attr
from enum import Enum

class InventoryGroupAttrs(Enum):
	ID = 'ID'
	GUID = 'GUID'
	INSERTED_AT = 'INSERTED_AT'
	UPDATED_AT = 'UPDATED_AT'

mpath = 'scheduler.models'

@attr.s
class InventoryGroup(GraphQLType):
    guid: str = attr.ib(default='', metadata={'unique':True,'type':str,'model':None})
    programs: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Program'), metadata={'type':list,'model':'Program'})
    lots: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Lot'), metadata={'type':list,'model':'Lot'})
