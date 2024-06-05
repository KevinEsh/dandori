from dandori.algorithms.scheduling import RoutingScheduler
from dandori.examples import build_models
from dandori.helpers.drawers import plot_gantt
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
    stop_start_range=(0, 0),
    order_start_range=(0, 30)
)

planner = RoutingScheduler()
planner.set_scale("minutes")
planner.add_stops(data["stops"])
planner.add_recipes(data["recipes"], vehicule=[0, 1, 2, 3, 4])
planner.set_demand(data["demand"])
planner.run(verbose=1)

program = planner.result()
if planner.status in ["OPTIMAL", "FEASIBLE"]:
    plot_gantt(program)
