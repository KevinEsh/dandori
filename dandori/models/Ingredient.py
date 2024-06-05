import attr
from typing import Callable, List
from gstorm.GraphQLType import GraphQLType


@attr.s
class Ingredient:
    name: str = attr.ib(default='')
    quantity: int = attr.ib(default=0)
    scale: str = attr.ib(default="kilograms")
    calculated: bool = attr.ib(default=False)
    function: Callable = attr.ib(default=lambda: 10)
    properties: List[GraphQLType] = attr.ib(factory=list)
