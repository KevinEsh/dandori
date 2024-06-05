from dandori.algorithms.scheduling import FlowShop
from dandori.examples import build_models
from dandori.helpers.drawers import plot_gantt
from pydash import group_by


def print_solution(program) -> None:
    """Prints solution on console."""
    max_route_distance = 0
    plans_by_resource = group_by(program.plans, "resource.code")
    for resource_code, plans in plans_by_resource.items():
        plan_output = 'Sequence for section {}:\n'.format(resource_code)
        route_distance = 0
        for plan in plans:
            plan_output += ' {} -> '.format(plan.toSolve.code)
            route_distance += 1
        plan_output += '{}\n'.format(0)
        plan_output += 'Number of washes: {}\n'.format(route_distance)
        max_route_distance += route_distance
        print(plan_output)
    print('Total number of washes: {}'.format(max_route_distance))


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
    order_start_range=(0, 30)
)

planner = FlowShop()
planner.set_scale("minutes")
# planner.add_stops(data["stops"])
planner.add_recipes(data["recipes"], locked=True)
planner.set_demand(data["demand"])
planner.run(verbose=1)
program = planner.result()
print_solution(program)
if planner.status in ["OPTIMAL", "FEASIBLE"]:
    plot_gantt(program, "gantt2.jpg")
