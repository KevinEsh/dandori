import attr
from copy import deepcopy
from typing import Dict, Tuple, List
from gstorm import GraphQLType
from dandori.helpers import printers as prt
from dandori.validators import valid_demand, valid_inventoryGroup, valid_stop
from dandori.algorithms.heuristics.priority_scheduler.preprocessing import weighted_priorities, \
    parse_to_dataframe, get_scores


@attr.s
class PriorityScheduler:
    _weights: Dict[str, float] = attr.ib(default=dict())
    _demand: GraphQLType = attr.ib(default=None)
    _invGroup: GraphQLType = attr.ib(default=None)
    _stops: List[GraphQLType] = attr.ib(default=list())
    _scores: Dict[int, int] = attr.ib(default=dict())
    _range: Tuple[int] = attr.ib(default=(0, 100))
    status: str = attr.ib(default="UNKNOWN")

    def set_weights(self, **weights: float) -> None:
        self._weights = weights

    def set_priority_range(self, a: int, b: int) -> None:
        self._range = (a, b)

    def add_demand(self, demand: GraphQLType) -> None:
        """Set the orders to be scheduled for the algorithm. These orders has to have valid data

        Args:
            demand (GraphQLType): Demand object that contains a list of non-empty orders
        """
        # Raise invalid demand
        valid_demand(demand)
        # Copying all demand data
        self._demand = deepcopy(demand)

    def add_stops(self, stops: List[GraphQLType]) -> None:
        """Set the stops to be scheduled for the algorithm. These stops has to have valid data

        Args:
            stops (List[GraphQLType]): List of Stop objects that contains info about inactivity of resources
        """
        # Raise invalid stop
        for stop in stops:
            valid_stop(stop)
        # Copying all stops data
        self._stops.extend(deepcopy(stops))

    def add_inventories(self, inventoryGroup: GraphQLType) -> None:
        """Set the lots to be scheduled for the algorithm. These lots has to have valid data

        Args:
            inventoryGroup (List[GraphQLType]): List of Stop objects that contains info about inactivity of resources
        """
        # Raise invalid stop
        valid_inventoryGroup(inventoryGroup)
        # Copying all stops data
        self._invGroup = deepcopy(inventoryGroup)

    def run(self) -> None:
        # Checking if there are at least one order
        if not self._demand.orders or not self._weights:
            self.status = "UNFEASIBLE"
            return

        # Running PriorityScheduler solver
        with prt.solver_context("PriorityScheduler") as report:
            dataframe = parse_to_dataframe(self._demand)
            weighted_priorities(dataframe, self._weights, self._range)
            self._scores = get_scores(dataframe)
            self.status = "FEASIBLE"
        report(self.status)

    def result(self) -> None:
        if self.status in ["UNFEASIBLE", "UNKNOWN"]:
            return None

        for i, order in enumerate(self._demand.orders):
            order.priority = self._scores[i]
        return self._demand


if __name__ == "__main__":
    from dandori.generators import ModelGenerator as mgen
    from dandori.models import UnitOfMeasurement

    # Setting.
    uom = UnitOfMeasurement(name="kilogram", symbol="kg")
    products, ingrediens = mgen.build_materials(
        num_products=10, num_ingredients=1)
    demand = mgen.build_demand(
        products, [uom], num_orders=10, max_extension=10, min_extension=0, scale="days", max_quantity=10)

    model = PriorityScheduler()
    model.add_demand(demand)
    model.set_priority_range(0, 100)
    model.set_weights(endAt=0.3, startAt=0.1, priority=0.3)
    model.run()
    for o in model.result().orders:
        print(o.id, o.priority)
