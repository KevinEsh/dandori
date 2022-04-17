from scheduler.algorithms.heuristics.priority_scheduler.preprocessing import normalize_data, parse_to_dataframe, datetime_to_int
from tests.fixtures import random_data_frame
from tests.fixtures import random_demand


def test_normalize_data(random_data_frame):
    """Tests that all values from a random data frame are between 0 and 1, after normalization.

    Args:
        random_data_frame (function): Random data frame of integers.
    """
    dataframe = random_data_frame.copy()
    normalize_data(dataframe, dataframe.columns.to_list())
    assert ((dataframe >= 0) & (dataframe <= 1)).all(
        axis=None), "There are not normalized values"


def test_parse_to_dataframe(random_demand):
    """Tests that any attribute from a demand model is missing after a data frame parsing.

    Args:
        random_demand (function): Demand model.
    """
    columns = parse_to_dataframe(random_demand).columns.to_list()
    expected_columns = ['__sync__', '__errors__', 'id', 'insertedAt', 'updatedAt', 'code', 'name', 'priority', 'quantity',
                        'quantityUom', 'endAt', 'startAt', 'material', 'demand', 'solvedByPlans', 'requiredByPlans', 'properties', '_public_keys']
    assert expected_columns == columns, "There are missing attributes when parsing to data frame"


def test_datetime_to_int(random_demand):
    """Test that all expected fields are parsed from datetime to int.

    Args:
        random_demand (function): Demand model.
    """
    fields = ["startAt", "endAt", "insertedAt", "updatedAt"]
    random_demand_data_frame = parse_to_dataframe(random_demand)
    datetime_to_int(random_demand_data_frame)
    assert all(random_demand_data_frame[fields].dtypes ==
               'int64'), "There are errors at parsing from date to int"
