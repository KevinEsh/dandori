from contextlib import contextmanager
from typing import Callable, Iterator
from datetime import datetime
from scheduler.helpers.datetools import to_int


def report_solver(totaltime: int, status: str, log: Callable = print, scale: str = "seconds") -> None:
    """function to report the status of a execution of a solver context.

    Args:
        totaltime (int): Total time of execution
        status (str): Solver status
        log (Callable, optional): Function to output report. Defaults to print.
        scale (str, optional): Timescale in which totaltime is based. Defaults to "seconds".
    """
    log(f"Solver terminated with status {status} in {totaltime} {scale}")


@contextmanager
def solver_context(
        algorithm: str = None,
        verbose: int = 0,
        log: Callable = print,
        scale: str = "microseconds") -> Iterator[Callable[[str], None]]:
    """Solver printer that can be used as a context manager when running any type of algorithm.
    First will print the current datetime before solver is executed, then when the solver had
    finished will print current datetime and will return a funtion to report final status of solver.


    Args:
        algorithm (str, optional): Name of the algorithm. Defaults to None.
        log (Callable, optional): Function to output datetimes. Defaults to print.
        scale (str, optional): Timescale in which reporter will be based. Defaults to "seconds".

    Yields:
        Iterator[Callable[[str], None]]: [description]
    """
    # Before running algorithm
    time_start = datetime.now()
    if verbose:
        log(f"Starting {algorithm} solver at {time_start.isoformat()}")

    # After ending context, yield this function
    yield lambda status: report_solver(to_int(time_end, time_start, scale), status, log, scale)

    # Just after running algorithm
    time_end = datetime.now()
    if verbose:
        log(f"Closing {algorithm} solver at {time_end.isoformat()}")
