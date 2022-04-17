from uuid import uuid4
from typing import Dict
import pandas as pd
from attr import attrib, attrs
from scheduler.models import Order, Demand, InventoryGroup, UnitOfMeasurement, Plant
from scheduler.algorithms.inventory.just_in_time.traductor import inventory_by_material, \
    calculate_orders, get_planning_window


@attrs
class JustInTime:
    """
    Builds a Just In Time-like request system to mantain inventory levels and fullfil
    demand. It creates Demand and Orders solved by calculate_orders algorithm.
    """

    demand: Demand = attrib(default=None)
    inventory_group: InventoryGroup = attrib(default=None)
    inventories: Dict[str, pd.DataFrame]

    def set(self,
            demand: Demand,
            inventory_group: InventoryGroup
            ):
        """Sets inventories from demand and lots.

        Args:
            demand (Demand): Scheduler's Demand model.
            inventory_group (InventoryGroup): Scheduler's InventoryGroup model.
        """
        self.inventories = inventory_by_material(demand, inventory_group)

    def run(self, storage_capacities: Dict[str, float], material_tank: Dict[str, float],
            reaccion_times):
        """Finds orders quantity by material to ensure desired inventory levels.

        Args:
            storage_capacities (Dict[str, float], optional): Tank's storage capacities. \
                Defaults to STORAGE_CAPACITIES.
            material_tank (Dict[str, float], optional): Material to tank relationship. \
                Defaults to MATERIAL_PT_TANK.
        """
        for material, inventory in self.inventories.items():
            _inventory, lot = inventory
            # Tank's capacity
            full_capacity = storage_capacities[material_tank[material]]
            # Get orders.
            _inventory = calculate_orders(
                _inventory, lot, full_capacity)
            # Calculate window.
            planning_window = get_planning_window(
                _inventory, reaccion_times, material)
            # Keep orders greater than zero.
            order = _inventory[_inventory['order'] > 0]['order'].to_list()
            self.inventories[material] = (planning_window, order, lot)

    def result(self) -> Demand:
        """Creates a Scheduler's model Demand from orders solved by inventory
        algorithm at run method.

        Returns:
            Demand: Scheduler's Demand model.
        """
        solved_demand = Demand(
            guid="Process" + uuid4().hex,
            plant=Plant(code="PTLS"),
            orders=[]
        )
        for _, solution in self.inventories.items():
            for window, request in zip(solution[0], solution[1]):
                solved_demand.orders.append(
                    Order(code=uuid4().hex,
                          name=None,
                          priority=0,
                          quantity=request,
                          quantityUom=UnitOfMeasurement(symbol="kg"),
                          endAt=window[1],
                          startAt=window[0],
                          material=solution[-1].material,
                          demand=solved_demand)
                )
        return solved_demand
