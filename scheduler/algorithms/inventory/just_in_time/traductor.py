from typing import List, Tuple, Dict
from datetime import timedelta
from pydash import group_by, find
import pandas as pd
import numpy as np
from scheduler.models import Order, Lot, Demand, InventoryGroup


def inventory_by_material(demand: Demand,
                          inventory_group: InventoryGroup) -> Dict[str, Tuple[pd.DataFrame, Lot]]:
    """Calculates raw inventory levels for every material.

    Args:
        demand (Demand): Scheduler's Demand model.
        inventory_group (InventoryGroup): Scheduler's InventoryGroup model.

    Returns:
        Dict[str, Tuple[pd.DataFrame, Lot]]: Material as keys, Raw inventory records and lot tuple as values.
    """
    orders_by_material = group_by(demand.orders, "material.code")
    inventories = {}
    for material, orders in orders_by_material.items():
        # Find lots on inventory groups.
        lot = find(inventory_group.lots,
                   lambda x: lambda _material=material: _material == x.material.code)
        orders = parse_orders_to_data_frame(orders)
        inventories[material] = set_inventory(orders, lot)
    return inventories


def parse_orders_to_data_frame(orders: List[Order]) -> pd.DataFrame:
    """Parses orders to data frame object.

    Args:
        orders (List[Order]): Scheduler's Order model requested.

    Returns:
        pd.DataFrame: endAt and quantity as columns. Tell us when and how much
        material we will need.
    """
    return pd.DataFrame([order.__dict__ for order in orders])[
        ['endAt', 'quantity']].sort_values(by='endAt')


def set_inventory(orders: pd.DataFrame, lot: Lot, order: List = None) -> Tuple[pd.DataFrame, Lot]:
    """Creates inventory records from orders and lot quantity

    Args:
        orders (pd.DataFrame): Parsed orders, see parse_orders_to_data_frame.
        lot (Lot): Scheduler's Lot model.
        order (List): Material requests for date.
    Returns:
        Tuple[pd.DataFrame, Lot]: Raw inventory records and lot.
    """
    orders = orders.copy()
    # If no order specify assume there is not request yet.
    if order is None:
        orders["order"] = np.zeros(orders.shape[0])
    else:
        orders["order"] = order
    inventory_level = []
    level = lot.quantity
    # Inventory levels are calculated from quantity on order requested and arriving order to storage.
    for quantity, request in zip(orders['quantity'], orders['order']):
        level = level - quantity + request
        inventory_level.append(level)
    orders['inventoryLevel'] = inventory_level
    return orders, lot


def calculate_orders(_inventory: pd.DataFrame, lot: Lot, full_capacity: int) -> pd.DataFrame:
    """Calculates order quantity from inventory level to ensure desired inventory
    levels and order (from request) fullfilment.

    Args:
        _inventory (pd.DataFrame): Raw inventory records from a material. No orders requested, see set_inventory function.
        lot (Lot): Scheduler's Lot model.
        full_capacity (int): Storage capacity of resource for material.

    Returns:
        pd.DataFrame: Processed inventory records, order column has been calculated.
    """
    _inventory = _inventory.copy()
    # Find if there are stockouts
    _inventory['flag'] = _inventory.apply(
        lambda x: x['inventoryLevel'] <= 0, axis=1)
    # While any stockouts
    while _inventory['flag'].sum() > 0:
        # Find where a replenishment will be needed and place and order there.
        idx = _inventory['flag'].idxmax()
        # Order size calculation.
        _inventory.at[idx, 'order'] = order_size(
            full_capacity, _inventory.at[idx - 1, 'inventoryLevel'])
        # Set inventory again using updated order values.
        _inventory, _ = set_inventory(_inventory, lot,
                                      _inventory['order'].values)
        # Update flag to look for future stockouts.
        _inventory['flag'] = _inventory.apply(
            lambda x: x['inventoryLevel'] <= 0, axis=1)
    return _inventory.drop('flag', axis=1)


def order_size(full_capacity: float, inventory_level: float) -> float:
    """Calculates order size from inventory level and full capacity.
    Orders are calculated taking the difference between 80% full capacity and the
    inventory level. This difference must be greater than zero.

    Args:
        full_capacity (float): Tank's full capacity.
        inventory_level (float): Available material.

    Returns:
        float: Quantity request.
    """
    return 0.8*full_capacity - inventory_level


def get_wide_window(inventory: pd.DataFrame) -> List:
    """Gets time window from requested orders on inventory.

    Args:
        inventory (Pd.DataFrame): Processed inventory records, order column has been calculated.

    Returns:
        List: (startAt, endAt)
    """
    lower_bound = inventory[inventory['order'] > 0].index - 1
    upper_bound = inventory[inventory['order'] > 0].index
    return list(zip(inventory.iloc[lower_bound]['endAt'],
                    inventory.iloc[upper_bound]['endAt']))


def get_planning_window(inventory: pd.DataFrame,
                        times: Dict[tuple, float], material: str) -> List[tuple]:
    """Gets planning window from wide window and reaccion times.

    Args:
        inventory (pd.DataFrame): Processed inventory records, order column has been calculated.
        times (Dict[tuple, float]): (material, equipment) as keys and time as values.
        material (str): Material code.

    Returns:
        List[tuple]: (startAt - min time, endAt - max time)
    """
    wide_window = get_wide_window(inventory)
    lower, upper = get_min_max(material, times)
    return list(map(lambda x: (x[0] - timedelta(hours=lower), x[1] - timedelta(hours=upper)), wide_window))


def get_min_max(material: str, times: Dict[Tuple[str, str], float]) -> Tuple[float, float]:
    """Gets minimum and maximum reaccion time asociated to a material.

    Args:
        material (str): Material code.
        times (Dict[Tuples[str, str], float]): (material, equipment) as keys and time as values.

    Returns:
        Tuple[float, float]: (min time, max time)
    """
    material_times = [value for key,
                      value in times.items() if key[0] == material]
    return min(material_times), max(material_times)
