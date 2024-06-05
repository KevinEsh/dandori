
from __future__ import annotations
from typing import List, Union
from datetime import datetime, date, time
from gstorm.GraphQLType import GraphQLType
from gstorm.helpers.typing_helpers import convert_to, list_convert_to, gql_repr, gql_list_repr
from gstorm.helpers.date_helpers import iso8601_to_local_date, get_datetime_object
import attr
from enum import Enum

class PropertyAttrs(Enum):
	ID = 'ID'
	VALUE = 'VALUE'
	INSERTED_AT = 'INSERTED_AT'
	UPDATED_AT = 'UPDATED_AT'

mpath = 'scheduler.models'

@attr.s
class Property(GraphQLType):
    propertyCatalog: 'PropertyCatalog' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'PropertyCatalog'), metadata={'type':GraphQLType,'model':'PropertyCatalog'})
    value: str = attr.ib(default='', metadata={'type':str,'model':None})
    material: 'Material' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Material'), metadata={'type':GraphQLType,'model':'Material'})
    resource: 'Resource' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Resource'), metadata={'type':GraphQLType,'model':'Resource'})
    lot: 'Lot' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Lot'), metadata={'type':GraphQLType,'model':'Lot'})
    stop: 'Stop' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Stop'), metadata={'type':GraphQLType,'model':'Stop'})
    order: 'Order' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Order'), metadata={'type':GraphQLType,'model':'Order'})
