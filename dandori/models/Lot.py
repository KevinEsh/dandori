
from __future__ import annotations
from typing import List, Union
from datetime import datetime, date, time
from gstorm.GraphQLType import GraphQLType
from gstorm.helpers.typing_helpers import convert_to, list_convert_to, gql_repr, gql_list_repr
from gstorm.helpers.date_helpers import iso8601_to_local_date, get_datetime_object
import attr
from enum import Enum
from .LotType import LotType

class LotAttrs(Enum):
	ID = 'ID'
	CODE = 'CODE'
	END_AT = 'END_AT'
	NAME = 'NAME'
	QUANTITY = 'QUANTITY'
	START_AT = 'START_AT'
	INSERTED_AT = 'INSERTED_AT'
	UPDATED_AT = 'UPDATED_AT'

mpath = 'scheduler.models'

@attr.s
class Lot(GraphQLType):
    code: str = attr.ib(default='', metadata={'unique':True,'type':str,'model':None})
    name: str = attr.ib(default='', metadata={'type':str,'model':None})
    lotType: LotType = attr.ib(default='LIMITED', converter=convert_to(mpath,'LotType'), metadata={'type':Enum,'model':'LotType'})
    startAt: datetime = attr.ib(default=datetime.now(), converter=iso8601_to_local_date, metadata={'type':datetime,'model':None})
    endAt: datetime = attr.ib(default=datetime.now(), converter=iso8601_to_local_date, metadata={'type':datetime,'model':None})
    quantity: int = attr.ib(default=0, metadata={'type':int,'model':None})
    quantityUom: 'UnitOfMeasurement' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'UnitOfMeasurement'), metadata={'type':GraphQLType,'model':'UnitOfMeasurement'})
    group: 'InventoryGroup' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'InventoryGroup'), metadata={'type':GraphQLType,'model':'InventoryGroup'})
    material: 'Material' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Material'), metadata={'type':GraphQLType,'model':'Material'})
    resource: 'Resource' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Resource'), metadata={'type':GraphQLType,'model':'Resource'})
    properties: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Property'), metadata={'type':list,'model':'Property'})
    lotPlans: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'LotPlan'), metadata={'type':list,'model':'LotPlan'})
