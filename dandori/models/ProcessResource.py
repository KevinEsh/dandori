
from __future__ import annotations
from typing import List, Union
from datetime import datetime, date, time
from gstorm.GraphQLType import GraphQLType
from gstorm.helpers.typing_helpers import convert_to, list_convert_to, gql_repr, gql_list_repr
from gstorm.helpers.date_helpers import iso8601_to_local_date, get_datetime_object
import attr
from enum import Enum

class ProcessResourceAttrs(Enum):
	ID = 'ID'
	INSERTED_AT = 'INSERTED_AT'
	UPDATED_AT = 'UPDATED_AT'

mpath = 'scheduler.models'

@attr.s
class ProcessResource(GraphQLType):
    resource: 'Resource' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Resource'), metadata={'type':GraphQLType,'model':'Resource'})
    process: 'Process' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Process'), metadata={'type':GraphQLType,'model':'Process'})
