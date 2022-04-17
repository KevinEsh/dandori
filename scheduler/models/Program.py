
from __future__ import annotations
from typing import List, Union
from datetime import datetime, date, time
from gstorm.GraphQLType import GraphQLType
from gstorm.helpers.typing_helpers import convert_to, list_convert_to, gql_repr, gql_list_repr
from gstorm.helpers.date_helpers import iso8601_to_local_date, get_datetime_object
import attr
from enum import Enum
from .ProgramStatus import ProgramStatus

class ProgramAttrs(Enum):
	ID = 'ID'
	END_AT = 'END_AT'
	GUID = 'GUID'
	START_AT = 'START_AT'
	INSERTED_AT = 'INSERTED_AT'
	UPDATED_AT = 'UPDATED_AT'

mpath = 'scheduler.models'

@attr.s
class Program(GraphQLType):
    guid: str = attr.ib(default='', metadata={'unique':True,'type':str,'model':None})
    startAt: datetime = attr.ib(default=datetime.now(), converter=iso8601_to_local_date, metadata={'type':datetime,'model':None})
    endAt: datetime = attr.ib(default=datetime.now(), converter=iso8601_to_local_date, metadata={'type':datetime,'model':None})
    status: ProgramStatus = attr.ib(default='UNINITIALIZED', converter=convert_to(mpath,'ProgramStatus'), metadata={'type':Enum,'model':'ProgramStatus'})
    inventoryGroup: 'InventoryGroup' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'InventoryGroup'), metadata={'type':GraphQLType,'model':'InventoryGroup'})
    toSolve: 'Demand' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Demand'), metadata={'type':GraphQLType,'model':'Demand'})
    request: 'Demand' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Demand'), metadata={'has_one':True,'type':GraphQLType,'model':'Demand'})
    plans: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Plan'), metadata={'type':list,'model':'Plan'})
