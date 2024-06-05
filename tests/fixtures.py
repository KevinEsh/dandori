import pytest
from dandori.examples.gen_inputs import build_models
import random
import pandas as pd
import numpy as np
from copy import deepcopy
from dandori.examples.scheduling import make_flowshop_example
from dandori.algorithms.scheduling.flowshop.ignition import ignite_optimizator, ignite_program, ignite_transitions
from dandori.algorithms.scheduling.flowshop.constrains import add_dependency, add_resource_no_overlap, add_single_recipe
from dandori.helpers import datetools as dt
from dandori.models import Lot, Demand, InventoryGroup, Material, Order
from dandori.algorithms.inventory.just_in_time.planner import JustInTime
from datetime import datetime


def solve_rounded_plans(program, scale):
    """Solve rounded plans
    Args:
        program (Program): program
        scale (str): scale
    """
    for plan in program.plans:
        plan.endAt = dt.round_date(plan.endAt, scale)
        plan.startAt = dt.round_date(plan.startAt, scale)


@pytest.fixture(scope='session')
def build_instances():
    """Build instances
    Returns:
        [type]: [description]
    """
    cache_models = {}

    def build_and_save(guid, **inputs):
        """Build and save
        Args:
            guid (str): guid
        Returns:
            Program: program
        """
        if not guid in cache_models:
            cache_models[guid] = build_models(**inputs)
        return cache_models[guid]
    return build_and_save


@pytest.fixture(scope='session')
def routing_result():
    """Generate routing's program and demand given some inputs to create a ranmdom scenary. If guid is already registered, return cache to save runtime
    """
    cache_result = {}

    def run_and_save(guid, **inputs):
        """Run & Save
        Args:
            guid (str): guid
        Returns:
            Program: program
        """
        if not guid in cache_result:
            model = make_flowshop_example(**inputs)
            model.run()
            program = model.result()
            solve_rounded_plans(program, model.scale)
            cache_result[guid] = (program, model.status)
        return cache_result[guid]
    return run_and_save


@pytest.fixture(scope='session')
def flowshop_result():
    """Generate flowshop's program and demand given some inputs to create a ranmdom scenary. If guid is already registered, return cache to save runtime
    """
    cache_result = {}

    def run_and_save(guid, **inputs):
        """Run & Save
        Args:
            guid (str): guid
        Returns:
            Program: program
        """
        if not guid in cache_result:
            model = make_flowshop_example(**inputs)
            model.run()
            program = model.result()
            solve_rounded_plans(program, model.scale)
            cache_result[guid] = (program, model.status)
        return cache_result[guid]
    return run_and_save


@pytest.fixture(scope='session')
def fixers_result():
    """Generate flowshop's program, mess it and try to fix it with the fixers heuristics.
    If guid is already registered, return cache to save runtime
    """
    cache_result = {}

    def run_and_save(guid, **inputs):
        """Run & Save
        Args:
            guid (str): guid
        Returns:
            Program: program
        """
        if not guid in cache_result:
            model = make_flowshop_example(**inputs)
            model.run()
            program = model.result()
            solve_rounded_plans(program, model.scale)
            cache_result[guid] = program
        return cache_result[guid]
    return run_and_save


@pytest.fixture(scope='session')
def random_datetime():
    """Random datetime
    Returns:
        datetime: random date
    """
    start_date = int(datetime(2021, 1, 1, 1, 1, 1).timestamp())
    end_date = int(datetime.now().timestamp())
    random_date = datetime.fromtimestamp(random.randint(start_date, end_date))
    return random_date, datetime.fromtimestamp(start_date), datetime.fromtimestamp(end_date)


@pytest.fixture(scope='session')
def random_data_frame():
    """Generates a data frame of random integers.
    Returns:
        pd.DataFrame: A, B, C, D as columns and integers between 1 and 100 as values.
    """
    return pd.DataFrame(np.random.randint(
        0, 100, size=(100, 4)), columns=list('ABCD'))


@pytest.fixture(scope='session')
def random_demand():
    """Generates random demand.
    Returns:
        GraphQLType: Demand model
    """
    data = build_models()
    return data['demand']


@pytest.fixture(scope='session')
def ignit_program():
    """
    By giving a Flowshop model no run, executes just the ignit program.
    """
    def init_program(model, **inputs):
        """
        Select all the available recipes for each order and make a Network Depency Graph from GraphTemplate
        Args:
        model: Flowshop
        """
        model._FlowShop__init_model()
        or_output = ignite_program(
            model.model, model.in_program, model.pivot, model.scale)
        for name, or_list in or_output.items():
            model.or_data[name].extend(or_list)
        return "Pass on program ignit test"
    return init_program


@pytest.fixture(scope='session')
def ignit_constrains():
    """
    By giving a Flowshop model no run, executes just the ignit constrain.
    """
    def init_constrains(model, **inputs):
        """
        Select all the available recipes for each order and make a Network Depency Graph from GraphTemplate
        Args:
            model: Flowshop
        """
        for networks in model.ignitions.values():
            add_single_recipe(model.model, networks)  # One recipe for order
            for GraphRecipe in networks:
                # Processes dependency
                add_dependency(model.model, GraphRecipe)
        add_resource_no_overlap(model.model, model.or_data, model.or_trans)
        return "Pass on constrain ignit test"
    return init_constrains


@pytest.fixture(scope='session')
def ignit_target():
    """
    By giving a Flowshop model no run, executes just the ignit target.
    """
    def init_target(model, **inputs):
        """
        Set objetive variable through math equation
        Args:
            model: Flowshop
        """
        if not model.targets:
            return "No target provided"
        model.or_targets = ignite_optimizator(
            model, model.or_data, model.or_trans,
            model.targets, model.optim_mode)
        return "Pass on target ignit test"
    return init_target


@pytest.fixture(scope='function')
def order_placer() -> JustInTime:
    """Generates an order placer from 'dummy' data.

    Returns:
        JustInTime: With initialized inventory.
    """
    dummy_material = Material(code='5000054')
    inventory_group = InventoryGroup(
        lots=[Lot(material=dummy_material, quantity=270000)])
    demand = Demand(
        orders=[Order(quantity=210000, endAt="2021-03-22T00:00:00Z",
                      material=dummy_material),
                Order(quantity=150000,
                      endAt="2021-03-26T00:00:00Z", material=dummy_material),
                Order(quantity=36000,
                      endAt="2021-03-27T00:00:00Z", material=dummy_material),
                Order(quantity=130000,
                      endAt="2021-04-04T00:00:00Z", material=dummy_material),
                Order(quantity=200000,
                      endAt="2021-04-15T00:00:00Z", material=dummy_material),
                ])
    op = JustInTime()
    op.set(demand, inventory_group)
    return op
