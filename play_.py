from dandori.algorithms.scheduling import FlowShop
from dandori.examples import build_models
from dandori.helpers.drawers import plot_gantt
from dandori.models import Order, Process
from pydash import group_by

data = build_models(
    num_products=10,
    num_ingredients=1,
    num_processors=10,
    max_resources=1,
    max_processes=5,
    num_orders=20,
    num_stops=10,
    min_stop_extension=20,
    max_stop_extension=100,
    min_order_extension=0,
    max_order_extension=1000,
    max_stop_start=300,
    order_start_range=(0, 0)
)


def my_function(order: Order, process: Process) -> int:
    ...
    q = order.material.quantity * 32 / 60
    return q


def my_func_b(order: Order, process: Process) -> int:
    ...
    return 100


planner = FlowShop()
planner.set_scale("minutes")
# planner.add_stops(data["stops"])
planner.add_recipes(data["recipes"], locked=True)

planner.link_function(my_function, "A")
planner.link_function(my_func_b, "B")
planner.link_function(my_func_b, "C")
planner.link_function(my_func_b, "D")
planner.link_function(my_func_b, "E")

planner.set_demand(data["demand"])
planner.optimize()
planner.run(verbose=1)
program = planner.result()

if planner.status in ["OPTIMAL", "FEASIBLE"]:
    plot_gantt(program)
