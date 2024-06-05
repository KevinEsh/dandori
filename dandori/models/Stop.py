
from __future__ import annotations
from typing import List, Union
from datetime import datetime, date, time
from gstorm.GraphQLType import GraphQLType
from gstorm.helpers.typing_helpers import convert_to, list_convert_to, gql_repr, gql_list_repr
from gstorm.helpers.date_helpers import iso8601_to_local_date, get_datetime_object
import attr
from enum import Enum

class StopAttrs(Enum):
	ID = 'ID'
	END_AT = 'END_AT'
	SCHEDULED = 'SCHEDULED'
	START_AT = 'START_AT'
	INSERTED_AT = 'INSERTED_AT'
	UPDATED_AT = 'UPDATED_AT'

mpath = 'scheduler.models'

@attr.s
class Stop(GraphQLType):
    startAt: datetime = attr.ib(default=datetime.now(), converter=iso8601_to_local_date, metadata={'type':datetime,'model':None})
    endAt: datetime = attr.ib(default=datetime.now(), converter=iso8601_to_local_date, metadata={'type':datetime,'model':None})
    stopResources: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'StopResource'), metadata={'type':list,'model':'StopResource'})
    scheduled: bool = attr.ib(default=False, metadata={'type':bool,'model':None})
    cost: 'Function' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Function'), metadata={'type':GraphQLType,'model':'Function'})
    properties: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Property'), metadata={'type':list,'model':'Property'})
    stopReason: 'StopReason' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'StopReason'), metadata={'type':GraphQLType,'model':'StopReason'})
    plans: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Plan'), metadata={'type':list,'model':'Plan'})
