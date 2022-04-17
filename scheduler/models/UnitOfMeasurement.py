
from __future__ import annotations
from typing import List, Union
from datetime import datetime, date, time
from gstorm.GraphQLType import GraphQLType
from gstorm.helpers.typing_helpers import convert_to, list_convert_to, gql_repr, gql_list_repr
from gstorm.helpers.date_helpers import iso8601_to_local_date, get_datetime_object
import attr
from enum import Enum
from .UomType import UomType

class UnitOfMeasurementAttrs(Enum):
	ID = 'ID'
	CODE = 'CODE'
	ELIOT_UNIT_ID = 'ELIOT_UNIT_ID'
	ENABLED = 'ENABLED'
	NAME = 'NAME'
	SYMBOL = 'SYMBOL'
	INSERTED_AT = 'INSERTED_AT'
	UPDATED_AT = 'UPDATED_AT'

mpath = 'scheduler.models'

@attr.s
class UnitOfMeasurement(GraphQLType):
    code: str = attr.ib(default='', metadata={'unique':True,'type':str,'model':None})
    name: str = attr.ib(default='', metadata={'type':str,'model':None})
    enabled: bool = attr.ib(default=True, metadata={'type':bool,'model':None})
    symbol: str = attr.ib(default='', metadata={'unique':True,'type':str,'model':None})
    uomType: UomType = attr.ib(default='UNIT', converter=convert_to(mpath,'UomType'), metadata={'type':Enum,'model':'UomType'})
    orders: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Order'), metadata={'type':list,'model':'Order'})
    plans: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Plan'), metadata={'type':list,'model':'Plan'})
    lots: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Lot'), metadata={'type':list,'model':'Lot'})
    functions: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Function'), metadata={'type':list,'model':'Function'})
    propertyCatalogs: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'PropertyCatalog'), metadata={'type':list,'model':'PropertyCatalog'})
    eliotUnitId: int = attr.ib(default=None, metadata={'type':int,'model':None})
