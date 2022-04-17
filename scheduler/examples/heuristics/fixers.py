from scheduler.examples import build_models
from scheduler.algorithms.scheduling import FlowShop
from scheduler.algorithms.heuristics import Fixers
# Typing imports
from typing import Tuple, Union
from gstorm import GraphQLType


def make_fixers_example(**kwargs: Union[int, str]) -> Tuple[GraphQLType]:
    """Make random data, generate a valid plan and then try to fix it with fixers

    Returns:
        Tuple[GraphQLType]: [description]
    """
    data = build_models(**kwargs)
    flowshop_model = FlowShop()
    flowshop_model.set_scale("minutes")
    flowshop_model.add_recipes(data["recipes"])
    flowshop_model.add_stops(data["stops"])
    flowshop_model.set_program(data["program"])
    flowshop_model.set_demand(data["demand"])
    flowshop_model.run()
    flowshop_program, _ = flowshop_model.result()

    # Setting Fixers' model
    fixers_model = Fixers()
    fixers_model.set_scale("minutes")
    fixers_model.set_pivot(data["pivot"])
    fixers_model.add_recipes(data["recipes"])
    fixers_model.set_program(flowshop_program)

    return fixers_model


if __name__ == "__main__":
    from scheduler.helpers import drawers as dw
    model = make_fixers_example(
        num_processors=5, max_resources=1, num_products=10)
    model.run()
    program = model.result()
    dw.plot_gantt(program)
