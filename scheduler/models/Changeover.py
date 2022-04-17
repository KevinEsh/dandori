
from __future__ import annotations
from typing import List, Union
from datetime import datetime, date, time
from gstorm.GraphQLType import GraphQLType
from gstorm.helpers.typing_helpers import convert_to, list_convert_to, gql_repr, gql_list_repr
from gstorm.helpers.date_helpers import iso8601_to_local_date, get_datetime_object
import attr
from enum import Enum

class ChangeoverAttrs(Enum):
	ID = 'ID'
	INSERTED_AT = 'INSERTED_AT'
	UPDATED_AT = 'UPDATED_AT'

mpath = 'scheduler.models'

@attr.s
class Changeover(GraphQLType):
    before: 'Material' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Material'), metadata={'type':GraphQLType,'model':'Material'})
    after: 'Material' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Material'), metadata={'type':GraphQLType,'model':'Material'})
    process: 'Process' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Process'), metadata={'type':GraphQLType,'model':'Process'})
    changeoverFunction: 'Function' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Function'), metadata={'type':GraphQLType,'model':'Function'})
