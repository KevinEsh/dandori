import attr
from gstorm.GraphQLType import GraphQLType


@attr.s
class Task:
    process: GraphQLType = attr.ib(default=None)
    optional: bool = attr.ib(default=False)
    group: str = attr.ib(default="")
    duration: int = attr.ib(default=0)
