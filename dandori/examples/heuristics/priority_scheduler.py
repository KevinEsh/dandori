import pandas as pd
from numpy.random import binomial
from dandori.algorithms.heuristics import priority_scheduler as PriorityScheduler
from dandori.generators import ModelGenerator as mgen
from dandori.models import UnitOfMeasurement
from dandori.services import gqlc

# Setting.
uom = UnitOfMeasurement(name="kilogram", symbol="kg")
products, ingrediens = mgen.build_materials(num_products=10, num_ingredients=1)
demand = mgen.build_demand(
    products, [uom], num_orders=3, max_extension=10, min_extension=0, scale="days", max_quantity=10)
# Parse to pandas.
orders = pd.DataFrame([order.__dict__ for order in demand.orders])
viable_orders = orders[['endAt', 'priority', 'quantity']]
# Orders with priority score.
viable_orders = PriorityScheduler.weighted_priorities(dataframe=viable_orders, weights={
    'priority': 0.5, 'endAt': 0.4, 'quantity': 0.1})
