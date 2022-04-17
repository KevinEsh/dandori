
from __future__ import annotations
from typing import List, Union
from datetime import datetime, date, time
from gstorm.GraphQLType import GraphQLType
from gstorm.helpers.typing_helpers import convert_to, list_convert_to, gql_repr, gql_list_repr
from gstorm.helpers.date_helpers import iso8601_to_local_date, get_datetime_object
import attr
from enum import Enum

class DemandAttrs(Enum):
	ID = 'ID'
	END_AT = 'END_AT'
	GUID = 'GUID'
	START_AT = 'START_AT'
	INSERTED_AT = 'INSERTED_AT'
	UPDATED_AT = 'UPDATED_AT'

mpath = 'scheduler.models'

@attr.s
class Demand(GraphQLType):
    guid: str = attr.ib(default='', metadata={'unique':True,'type':str,'model':None})
    startAt: datetime = attr.ib(default=datetime.now(), converter=iso8601_to_local_date, metadata={'type':datetime,'model':None})
    endAt: datetime = attr.ib(default=datetime.now(), converter=iso8601_to_local_date, metadata={'type':datetime,'model':None})
    orders: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Order'), metadata={'type':list,'model':'Order'})
    solutions: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Program'), metadata={'type':list,'model':'Program'})
    requestedBy: 'Program' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Program'), metadata={'type':GraphQLType,'model':'Program'})
    plant: 'Plant' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Plant'), metadata={'type':GraphQLType,'model':'Plant'})
