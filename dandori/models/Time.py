import random
from typing import Callable
import attr


# * code = "DEFAULT_SDL_TIME_CODE" *
def DEFAULT_TIME_FUNCTION(**kwargs):
    """Default function in general suited for scale in minutes"""
    return random.randint(5*60, 30*60)


@attr.s
class Time:
    """Time class for register callables functions in funbook
    """  # TODO [SDLMICRO-137]: eliminar esta clase
    duration: int = attr.ib(default=0)
    scale: str = attr.ib(default="hours")
    linked: bool = attr.ib(default=False)
    call: Callable = attr.ib(default=DEFAULT_TIME_FUNCTION)
