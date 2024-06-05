from dandori.algorithms.heuristics.priority_scheduler.planner import PriorityScheduler
from tests.fixtures import random_demand


def test_run(random_demand):
    """Tests that the priorities are inside the expected range (0 to 100).

    Args:
        random_demand (function): Demand model.
    """
    model = PriorityScheduler()
    model.add_demand(random_demand)
    model.set_priority_range(0, 100)
    model.set_weights(endAt=0.3, startAt=0.1, priority=0.3)
    model.run()
    assert not [o.priority for o in model.result().orders if o.priority >
                100 or o.priority < 0], "There are priorities outside range"
