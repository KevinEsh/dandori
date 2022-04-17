from pandas._testing import assert_frame_equal
import pandas as pd
from tests.fixtures import order_placer
from scheduler.algorithms.inventory.just_in_time.planner import JustInTime
from scheduler.models import Demand


def test_set(order_placer: JustInTime):
    """Tests if the inventory is setting as expected

    Args:
        order_placer (JustInTime): Order placer fixture.
    """
    inventory = pd.DataFrame({'quantity': {0: 210000, 1: 150000, 2: 36000, 3: 130000, 4: 200000},
                              'order': {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0},
                              'inventoryLevel': {0: 60000.0, 1: -90000.0, 2: -126000.0, 3: -256000.0, 4: -456000.0}
                              })
    assert not assert_frame_equal(
        order_placer.inventories['5000054'][0].drop('endAt', axis=1), inventory, check_datetimelike_compat=False)


def test_run(order_placer: JustInTime):
    """Tests if the inventory is the expected after run order placer.

    Args:
        order_placer (JustInTime): Order placer fixture.
    """
    storage_capacities = {"T-217": 269777}
    material_tank = {"5000054": "T-217"}
    reaccion_times = {('5000054', '200C'): 25,
                      ('5000054', '200CB'): 20,
                      ('5000054', '200HA'): 20}
    order_placer.run(storage_capacities, material_tank, reaccion_times)
    quantities = [155821.6, 186000.0, 130000.0]
    _quantities = order_placer.inventories['5000054'][1]
    assert quantities == _quantities


def test_result(order_placer: JustInTime):
    """Test if output of result method is the expected.

    Args:
        order_placer (JustInTime): Order placer fixture.
    """
    storage_capacities = {"T-217": 269777}
    material_tank = {"5000054": "T-217"}
    reaccion_times = {('5000054', '200C'): 25,
                      ('5000054', '200CB'): 20,
                      ('5000054', '200HA'): 20}
    order_placer.run(storage_capacities, material_tank, reaccion_times)
    assert isinstance(order_placer.result(), Demand)
