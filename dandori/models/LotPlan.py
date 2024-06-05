
from __future__ import annotations
from typing import List, Union
from datetime import datetime, date, time
from gstorm.GraphQLType import GraphQLType
from gstorm.helpers.typing_helpers import convert_to, list_convert_to, gql_repr, gql_list_repr
from gstorm.helpers.date_helpers import iso8601_to_local_date, get_datetime_object
import attr
from enum import Enum

class LotPlanAttrs(Enum):
	ID = 'ID'
	NAME = 'NAME'
	INSERTED_AT = 'INSERTED_AT'
	UPDATED_AT = 'UPDATED_AT'

mpath = 'scheduler.models'

@attr.s
class LotPlan(GraphQLType):
    name: str = attr.ib(default='', metadata={'type':str,'model':None})
    plan: 'Plan' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Plan'), metadata={'type':GraphQLType,'model':'Plan'})
    lot: 'Lot' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Lot'), metadata={'type':GraphQLType,'model':'Lot'})
