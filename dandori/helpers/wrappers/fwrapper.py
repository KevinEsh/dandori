from typing import Callable, Any
from random import randint, random
from inspect import getfullargspec


class FunctionWrapper:

    @classmethod
    def str_wrapper(cls, distfunc: Callable, **params: Any) -> Callable:
        """Decorator for a string function. The decorated function can output a suffix plus expected string. Also can be resized.

        Args:
            distfunc (Callable): Function that outputs strings

        Returns:
            Callable: Decorated function
        """
        def call(suffix: str = None, length: int = None, **callparams):
            params.update(callparams)
            # suffix insertion
            if suffix:
                return suffix + " " + distfunc(**params)[:length]
            else:
                return distfunc(**params)[:length]
        return call

    @classmethod
    def int_wrapper(cls, distfunc: Callable, **params: Any) -> Callable:
        """Decorator for a integer function. The decorated function can be called with default arguments and applies ReLu function. Also can be parsed into a list.

        Args:
            distfunc (Callable): Function that outputs integers

        Returns:
            Callable: Decorated function
        """
        if not params:
            params = getfullargspec(distfunc).args
            params.remove("self")
            params = {args: randint(i*50, (i+1)*50)  # TODO: logica para la funcion random.random
                      for i, args in enumerate(params)}

        def call(size: int = 1, **callparams: int):
            # ReLu funciton to distribution
            params.update(callparams)
            return [int(max(distfunc(**params), 0)) for _ in range(size)]
        return call
