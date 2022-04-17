
from __future__ import annotations
from typing import List, Union
from datetime import datetime, date, time
from gstorm.GraphQLType import GraphQLType
from gstorm.helpers.typing_helpers import convert_to, list_convert_to, gql_repr, gql_list_repr
from gstorm.helpers.date_helpers import iso8601_to_local_date, get_datetime_object
import attr
from enum import Enum

class ProcessAttrs(Enum):
	ID = 'ID'
	CODE = 'CODE'
	DESCRIPTION = 'DESCRIPTION'
	ENABLED = 'ENABLED'
	NAME = 'NAME'
	INSERTED_AT = 'INSERTED_AT'
	UPDATED_AT = 'UPDATED_AT'

mpath = 'scheduler.models'

@attr.s
class Process(GraphQLType):
    code: str = attr.ib(default='', metadata={'unique':True,'type':str,'model':None})
    name: str = attr.ib(default='', metadata={'type':str,'model':None})
    description: str = attr.ib(default='', metadata={'type':str,'model':None})
    enabled: bool = attr.ib(default=True, metadata={'type':bool,'model':None})
    timeFunction: 'Function' = attr.ib(default=None, repr=gql_repr, converter=convert_to(mpath,'Function'), metadata={'type':GraphQLType,'model':'Function'})
    changeovers: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Changeover'), metadata={'type':list,'model':'Changeover'})
    recipeProcesses: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'RecipeProcess'), metadata={'type':list,'model':'RecipeProcess'})
    processMaterials: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'ProcessMaterial'), metadata={'type':list,'model':'ProcessMaterial'})
    processResources: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'ProcessResource'), metadata={'type':list,'model':'ProcessResource'})
    prevs: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'ProcessArc'), metadata={'type':list,'model':'ProcessArc'})
    nexts: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'ProcessArc'), metadata={'type':list,'model':'ProcessArc'})
    plans: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'Plan'), metadata={'type':list,'model':'Plan'})
