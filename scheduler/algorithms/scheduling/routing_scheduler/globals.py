from random import randint
from ortools.constraint_solver import routing_enums_pb2
from datetime import datetime


MAX_COST_PER_ARC = 1 << 28
MAX_TIME_PER_ARC = 1 << 28
MAX_WAIT_TIME = 1 << 28

HEURISTICS = routing_enums_pb2.FirstSolutionStrategy().Value.items()
METAHEURISTICS = routing_enums_pb2.LocalSearchMetaheuristic().Value.items()

DEFAULT_PIVOT = datetime.utcnow()
DEFAULT_SEARCH = {
    "heuristic": 15,  # AUTOMATIC
    "metaheuristic": 2,  # GUIDED_LOCAL_SEARCH
    "solvertime": 60,  # 1 minute
}

STATUS_NAME = {
    0: "ROUTING_NOT_SOLVED",  # Problem not solved yet.
    1: "ROUTING_SUCCESS",  # Problem solved successfully.
    2: "ROUTING_FAIL",  # No solution found to the problem.
    3: "ROUTING_FAIL_TIMEOUT",  # Time limit reached before finding a solution.
    4: "ROUTING_INVALID",  # Model, model parameters, or flags are not valid.
}


def DEFAULT_FUNCTION(**kwargs):
    """Default funtion time

    Returns:
        int: random time
    """
    return randint(5, 30)
