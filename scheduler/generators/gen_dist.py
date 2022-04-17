import uuid
import random
from typing import Callable
from scheduler.generators.gen_base import BaseGenerator
from scheduler.helpers.wrappers import FunctionWrapper as fw


class DistributionGenerator(BaseGenerator):
    # TODO: modificar la logica de los parametros por defecto de cada distribucion para que pueda ser robusta
    __integer_distribitions = {
        'betavariate': random.betavariate,
        'choice': random.choice,
        'choices': random.choices,
        'expovariate': random.expovariate,
        'gammavariate': random.gammavariate,
        'gauss': random.gauss,
        'getrandbits': random.getrandbits,
        'getstate': random.getstate,
        'lognormvariate': random.lognormvariate,
        'normalvariate': random.normalvariate,
        'paretovariate': random.paretovariate,
        'randint': random.randint,
        'random': random.random,
        'randrange': random.randrange,
        'sample': random.sample,
        'setstate': random.setstate,
        'shuffle': random.shuffle,
        'triangular': random.triangular,
        'uniform': random.uniform,
        'vonmisesvariate': random.vonmisesvariate,
        'weibullvariate': random.weibullvariate
    }

    __string_distributions = {
        "uuid1": lambda: uuid.uuid1().hex,
        "uuid4": lambda: uuid.uuid4().hex,
    }

    @classmethod
    def create(cls, distname: str, seed: int = None, **params: int) -> Callable:
        """Returns a callable distribution function with defualt params if not specified.

        Args:
            distname (str): Name of the choice distribution. Must be implemented
            seed (int, optional): If user wants to set a seed for random numbers. Defaults to None.

        Raises:
            NotImplementedError: If value of `distname` is not listed will raise this exception

        Returns:
            Callable: Distribution callable function with defined params

        Examples:
            >>> from scheduler.generator import DistributionGenerator as dg
            >>> uniform = dg.create("uniform", a=0, b=10)
            >>> uniform(size=5)
            [5, 9, 6, 4, 1]
            >>> uniform(size=6, b=1)
            [0, 0, 1, 1, 0, 1]
            >>> uniform()
            [7]
            >>> uniform(a=10)
            [10]
        """
        if distname in cls.__integer_distribitions:
            random.seed(seed)
            distfunc = cls.__integer_distribitions[distname]
            return fw.int_wrapper(distfunc, **params)
        elif distname in cls.__string_distributions:
            distfunc = cls.__string_distributions[distname]
            return fw.str_wrapper(distfunc)
        else:
            raise NotImplementedError(
                f"distribution '{distname}' not implemented.")


if __name__ == "__main__":
    dgen = DistributionGenerator
    sfunc = dgen.create("uuid4")
    ifunct = dgen.create("uniform", a=0, b=10)

    for i in range(10):
        print(sfunc(suffix="product", length=10), ifunct(size=10, a=i+1))
