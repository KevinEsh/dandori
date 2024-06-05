from collections import defaultdict
from datetime import datetime
from random import randint
from itertools import count
from typing import Dict, Tuple
from dandori.generators import ModelGenerator as mgen


guid = count(start=0, step=1)


def assing_random_unique_ids(data):
    """Assign random unique ids to all data generated from 'generate_random_inputs'
    """
    try:
        data["demand"].id = next(guid)
    except StopIteration:
        pass

    for order in data["demand"].orders:
        try:
            order.id = next(guid)
        except StopIteration:
            pass


def generate_random_inputs(cases: int = 1, size: Tuple[int] = (1, 1)) -> Dict[str, Dict[str, int]]:
    """Take a number of cases and generate a new random set of initial conditions

    Args:
        cases (int, optional): Number of new sets. Defaults to 1.
        size (Tuple[int], optional): Max size of the contiditions. Defaults to (1, 1).

    Returns:
        Dict[str, Dict[str, int]]: Conditions
    """
    inputs = {case: {
        "num_orders": randint(*size),
        "num_stops": randint(*size),
        "num_products": randint(*size),
        "num_ingredients": randint(*size),
        "num_processors": randint(*size),
        "num_stockers": randint(*size),
        "num_duals": randint(*size),
        "num_recipes_per_prod": randint(*size),
        "max_processes": randint(*size),
        # TODO: SDLSR-128 corregir el valor a uno mas estable
        "max_changeovers": randint(*size),
        "order_start_range": (0, 30),
        "order_extension": (100, 500),
        "stop_start_range": (0, 0),
        "stop_extension": (0, 100)
    } for case in range(cases)}

    return inputs


def build_models(
        num_products: int = 1,
        num_ingredients: int = 1,
        num_processors: int = 1,
        num_stockers: int = 1,
        num_duals: int = 1,
        num_uoms: int = 1,
        num_functions: int = 1,
        num_orders: int = 1,
        num_stops: int = 0,
        num_recipes_per_prod: int = 1,
        max_processes: int = 1,
        min_order_extension: int = 0,
        max_order_extension: int = 1000,
        min_stop_extension: int = 20,
        max_stop_extension: int = 20,
        order_start_range: tuple = (0, 0),
        stop_start_range: tuple = (0, 0),
        order_scale: str = "days",
        stop_scale: str = "hours",
        **kwargs: int):

    pivot = datetime.utcnow()

    processors, stockers, duals = mgen.build_plant(
        num_processors,
        num_stockers,
        num_duals)

    products, ingredients = mgen.build_materials(
        num_products,
        num_ingredients)

    uoms = mgen.build_uoms(
        num_uoms)

    functions = mgen.build_functions(
        uoms,
        num_functions)

    recipes = mgen.build_recipes(
        products,
        ingredients,
        processors,
        functions,
        num_recipes_per_prod,
        max_processes=max_processes,
        max_resources_per_process=randint(1, len(processors)//2 + 1),
        max_ingredients_per_process=randint(1, len(ingredients)//2 + 1),
    )

    changeovers = mgen.build_changeovers(
        products,
        functions
    )

    demand = mgen.build_demand(
        products, uoms, pivot,
        num_orders=num_orders,
        max_extension=max_order_extension,
        min_extension=min_order_extension,
        start_range=order_start_range,
        scale=order_scale,
    )

    stops = mgen.build_stops(
        processors,
        functions,
        pivot,
        num_stops=num_stops,
        max_extension=max_stop_extension,
        min_extension=min_stop_extension,
        start_range=stop_start_range,
        scale=stop_scale,
    )

    # Programa con planes pre-cargados
    program = mgen.build_program(
        demand, pivot,
        num_plans=0
    )

    data = defaultdict(lambda: None)
    data["pivot"] = pivot
    data["processors"] = processors
    data["stockers"] = stockers
    data["duals"] = duals
    data["products"] = products
    data["ingredients"] = ingredients
    data["recipes"] = recipes
    data["uoms"] = uoms
    data["demand"] = demand
    data["functions"] = functions
    data["changeovers"] = changeovers
    data["stops"] = stops
    data["program"] = program

    return data


if __name__ == "__main__":
    print(generate_random_inputs(1, size=(1, 1)))
