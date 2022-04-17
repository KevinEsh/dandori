from typing import OrderedDict, Union
from scheduler.examples.gen_inputs import assing_random_unique_ids
from scheduler.examples import build_models
from scheduler.algorithms.scheduling import FlowShop
from scheduler.models import Material, Process, Recipe, Resource, Order
from scheduler.generators.gen_model import connect_models


def make_flowshop_example(
        with_ids: bool = False,
        with_optional: bool = False,
        ** kwargs: Union[int, str]) -> FlowShop:

    # Setting Flowshop's model
    data = build_models(**kwargs)
    if with_ids:
        assing_random_unique_ids(data)

    if with_optional:
        torc = "TORC-FLWS"  # Test Optional Resource Constraint - FlowShop
        material = Material(code=torc)
        process = Process(code=torc)
        torc_recipe = Recipe(code=torc)
        resources = [Resource(code=i, name=i) for i in ["A", "B", "C", "D", "E", "F"]]
        connect_models([process], resources)
        connect_models([torc_recipe], [process])
        connect_models([torc_recipe], [material])
        torc_order = Order(code=torc, name=torc, material=material)
        # Append artificial order & recipe to input data
        data["demand"].orders.append(torc_order)
        data["recipes"].append(torc_recipe)

    model = FlowShop()
    model.set_scale("minutes")
    model.set_pivot(data["pivot"])
    model.set_program(data["program"])
    model.set_demand(data["demand"])
    model.add_recipes(data["recipes"])
    model.add_stops(data["stops"])

    return model


if __name__ == "__main__":
    from scheduler.helpers import drawers as dw
    planner = make_flowshop_example(
        num_processors=5, max_resources=1, num_products=10)
    planner.run()
    program = planner.result()
    dw.plot_gantt(program)
