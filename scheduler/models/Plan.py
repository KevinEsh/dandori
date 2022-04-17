
from __future__ import annotations
from typing import List, Union
from datetime import datetime, date, time
from gstorm.GraphQLType import GraphQLType
from gstorm.helpers.typing_helpers import convert_to, list_convert_to, gql_repr, gql_list_repr
from gstorm.helpers.date_helpers import iso8601_to_local_date, get_datetime_object
import attr
from enum import Enum
from .PlanStatus import PlanStatus

class PlanAttrs(Enum):
	ID = 'ID'
	END_AT = 'END_AT'
	PROGRESS = 'PROGRESS'
	QUANTITY = 'QUANTITY'
	START_AT = 'START_AT'
	INSERTED_AT = 'INSERTED_AT'
	UPDATED_AT = 'UPDATED_AT'

mpath = 'scheduler.models'

@attr.s
class Plan(GraphQLType):
    progress: int = attr.ib(default=0, metadata={'type':int,'model':None})
    quantity: int = attr.ib(default=0, metadata={'type':int,'model':None})
    quantityUom: 'UnitOfMeasurement' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'UnitOfMeasurement'), metadata={'type':GraphQLType,'model':'UnitOfMeasurement'})
    status: PlanStatus = attr.ib(default='PENDING', converter=convert_to(mpath,'PlanStatus'), metadata={'type':Enum,'model':'PlanStatus'})
    endAt: datetime = attr.ib(default=datetime.now(), converter=iso8601_to_local_date, metadata={'type':datetime,'model':None})
    startAt: datetime = attr.ib(default=datetime.now(), converter=iso8601_to_local_date, metadata={'type':datetime,'model':None})
    program: 'Program' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Program'), metadata={'type':GraphQLType,'model':'Program'})
    material: 'Material' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Material'), metadata={'type':GraphQLType,'model':'Material'})
    toSolve: 'Order' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Order'), metadata={'type':GraphQLType,'model':'Order'})
    request: 'Order' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Order'), metadata={'type':GraphQLType,'model':'Order'})
    resource: 'Resource' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Resource'), metadata={'type':GraphQLType,'model':'Resource'})
    process: 'Process' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Process'), metadata={'type':GraphQLType,'model':'Process'})
    recipe: 'Recipe' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Recipe'), metadata={'type':GraphQLType,'model':'Recipe'})
    stop: 'Stop' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Stop'), metadata={'type':GraphQLType,'model':'Stop'})
    lotPlans: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'LotPlan'), metadata={'type':list,'model':'LotPlan'})
