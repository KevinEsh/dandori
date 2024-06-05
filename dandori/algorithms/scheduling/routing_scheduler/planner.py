from copy import deepcopy
from datetime import datetime
from collections import defaultdict
from dandori.algorithms.scheduling.flowshop.ignition import ignite_program
from typing import Callable, List, Any
# Thrid-party dependencies
from networkx import DiGraph
from pydash import group_by
from attr import attrs, attrib
# First-party dependencies
from dandori.helpers.printers import solver_context
from dandori.algorithms.scheduling.flowshop import FlowShop
from dandori.validators import valid_demand, valid_recipe, valid_program,\
    valid_pivot, valid_stop, valid_changeover  # BUG: incluir el valid_pivot en __init_demand
from dandori.helpers.graphtools import create_network_template, create_orders_graph
from dandori.helpers.metadata import raise_invalid_func, raise_invalid_scale,\
    raise_invalid_date
from dandori.models import Program, Demand, Time, Recipe, FunctionType, Stop, \
    Changeover
# * Direct dependencies
from .globals import STATUS_NAME, DEFAULT_SEARCH, DEFAULT_PIVOT, DEFAULT_FUNCTION
from .traductor import create_or_indexmap, stack_fifo_plans, costfunc_wrapper, \
    get_vehicule_route, reset_program_interval
from .ignition import ignite_cost_function, ignite_routing_manager, ignite_search_params, \
    ignite_routing_model, add_skilled_vehicules


@attrs
class RoutingScheduler:
    """Routing Scheduler

    Raises:
        NotImplementedError: Not implemented
        KeyError: Not implemented
    """

    in_program = attrib(default=Program())
    in_demand = attrib(default=Demand())
    stops = attrib(default=[])
    recipes = attrib(default=[])
    or_model = attrib(default=None)
    or_manager = attrib(default=None)
    or_params = attrib(default=None)
    or_solution = attrib(default=None)
    or_dimension = attrib(default=None)
    or_starts = attrib(default=[])
    or_ends = attrib(default=[])
    vehicules = attrib(default=defaultdict(object))
    TransGraph = attrib(default=DiGraph())
    recetary = attrib(default=defaultdict(dict))  # material.code, [networks]
    costfunc = attrib(default=DEFAULT_FUNCTION)
    funbook = attrib(default=defaultdict(Time))
    parameters = attrib(default=DEFAULT_SEARCH)
    pivot = attrib(default=DEFAULT_PIVOT)
    status = attrib(default="ROUTING_NOT_SOLVED")
    scale = attrib(default="minutes")
    megamatrix = attrib(default=None)
    data = attrib(default=defaultdict(list))
    transitions = attrib(default=defaultdict(list))

    def set_scale(self, scale: str) -> None:
        """Set time scale which integer OR-tools variables will be set

        Args:
            scale (str): Try one of the followings: "days", "hours", "minutes", "seconds"

        Raises:
            NotImplementedError: If your scale is not implemented
        """
        raise_invalid_scale(scale)
        self.scale = scale

    def set_pivot(self, pivot: datetime) -> None:
        """Set the minimum datetime to start to place plans of model's solution

        Args:
            pivot (datetime): Timestamp which has to be <= than all order.startAt
                in other case this will be infeasible
        """
        raise_invalid_date(pivot)
        self.pivot = pivot

    def set_cost_function(self, function: Callable) -> None:
        """Set the cost function to be called when the model wants to calculate
        the transition between to materials (changeover transition)

        Args:
            function (Callable): Callable funtion. Has to have 'prev_order',
                'next_order', 'edge' as inputs parameters
        """
        raise_invalid_func(function, FunctionType.CHANGEOVER_COST)
        self.costfunc = function

    def set_vehicules(self, vehicules: List[Any]) -> None:
        """Register and map the given vehicules into integers

        Args:
            vehicules(List[Any]): List of the names of vehicules
        """
        self.vehicules.update(create_or_indexmap(vehicules))

    def set_parameters(self, **params: int) -> None:
        """Update if needed default parameters of OR-tools optimizator
        """
        self.parameters.update(params)

    def set_demand(self, demand: Demand) -> None:
        """Set the orders to be scheduled for the algorithm. These orders has
        to have valida data

        Args:
            demand (GraphQLType): Demand object that contains a list of
                non-empty orders
        """
        # Raise invalid demand & Copying all demand data
        valid_demand(demand, depth=1)
        self.in_demand = deepcopy(demand)

    def set_program(self, program: Program) -> None:
        """Set the plans to be forced scheduled for the algorithm. These plans
        has to have valid data

        Args:
            program (GraphQLType): Program object that constains a list of
                no-overlaped plans
        """
        # Raise invalid program & Copying all program data
        valid_program(program)
        self.in_program = deepcopy(program)

    def add_changeovers(self, changeovers: List[Changeover]) -> None:
        """Add new changeovers between two materials

        Args:
            changeovers (List[Changeover]): List of relations of transitions between
                changing processed materials in a resource
        """
        # Validate if data in changeover meets our necesities
        for changeover in changeovers:
            valid_changeover(changeover)
        # 'transitions' may contain several adj matrices in different processes
        self.transitions.update(group_by(changeovers, 'process.code'))

    def add_stops(self, stops: List[Stop]) -> None:
        """Add a list of new stops to be considered while running the model.
        Each stop will produce a plan into the program

        Args:
            stops (List[Stop]): List of Schedule-Logic's Stops to be added.
        """
        # Raise invalid recipe & Extend all stops
        for stop in stops:
            valid_stop(stop)
        self.stops.extend(stops)

    def add_recipes(self, recipes: List[Recipe], vehicule: str) -> None:
        """Add a new recipe to be considered as new way to create materials.
        This recipe will be registered in the recetary

        Args:
            recipes(List[Recipe]): List of Schedule-Logic's Recipes to be added.
                Each has to have a list of processes conected in DAG form
            vehicule(str): identifier of the vehicule.
        """
        # Raise invalid vehicule
        if vehicule not in self.vehicules:
            raise KeyError(
                f"vehicules code '{vehicule}' is not registered. Set it up with 'set_vehicules' method")

        # Raise invalid recipe & add to the list data
        for recipe in recipes:
            valid_recipe(recipe)
        self.recipes.extend(recipes)

        # Register all recipes into the recetary
        for recipe in recipes:
            # Create graph template for the recipe
            GraphRecipe = create_network_template(recipe, self.funbook)

            # Add the material to the recetary and then register recipe graph template
            for rel in recipe.recipeMaterials:
                code = rel.material.code
                self.recetary[code][vehicule] = GraphRecipe

    def link_function(self, function: Callable, codes: List[str]) -> None:
        """This method links the current callable with identifier 'code' to all
        the Schedule-Logic's Functions with the same code in order to calculate
        process time in a fashinable way

        Args:
            function(Callable): function to be called during execution, Has to
                return and integer and have 'order' & 'process' as inputs
            code(str): Identifier of the function
        """
        raise_invalid_func(function, FunctionType.PROCESS_TIME)
        for code in codes:
            self.funbook[code].call = function
            self.funbook[code].linked = True

    def __init_program(self) -> None:
        """Ignite program
        """
        self.in_program.toSolve = self.in_demand

    def __init_demand(self) -> None:
        """Create a transition graph for the given demand and the adjacency matrix
        """
        for order in self.demand.orders:
            valid_pivot(order, self.pivot)

        self.TransGraph = create_orders_graph(
            self.in_demand.orders,
            self.transitions)

        for _id, order in self.TransGraph.nodes(data="order"):
            code = order.material.code
            for vkey in self.recetary[code].keys():
                index = self.vehicules[vkey].index
                self.data[_id].append(index)
                self.vehicules[vkey].allowedOrders.append(_id)

    def __init_cp_model(self):
        """Init OR-tools models
        """
        self.or_starts = [0 for _ in range(len(self.vehicules))]
        self.or_ends = self.starts

        # Create the routing index manager.
        self.or_manager = ignite_routing_manager(
            self.TransGraph.number_of_nodes(),
            len(self.vehicules),
            self.or_starts,
            self.or_ends)

        # Create Routing Model.
        self.or_model = ignite_routing_model(self.or_manager)

    def __init_recipes(self) -> None:
        """Generates GraphRecipes for each of the user's recipes gave
        """
        # TODO: SDLSR-124
        return

    def __init_constrains(self) -> None:
        """Ignite all Or-tools constrains that fulfill the user's settled constrains
        """
        add_skilled_vehicules(
            self.data,
            self.vehicules,
            self.or_manager,
            self.or_model)

    def __init_cost_function(self) -> None:
        """Wrap cost funtion in order to build a user-hidden connection with
        OR-tools' engine
        """
        callback = costfunc_wrapper(
            self.costfunc,
            self.TransGraph,
            self.or_manager)

        # Ignite cost function with routing model
        self.or_dimension = ignite_cost_function(callback, self.or_model, coeff=100)

    def __init_search_params(self):
        """Ignite the hiperpameters for the Or-tools solver given by the user
        """
        self.or_params = ignite_search_params(self.parameters)

    def run(self):
        """Run the model & report status of solver
        """
        self.__init_recipes()
        self.__init_demand()
        self.__init_program()
        self.__init_cp_model()
        self.__init_constrains()
        self.__init_cost_function()
        self.__init_search_params()

        # Running Ortools solver
        with solver_context("RoutingScheduler") as report:
            params = self.or_params
            self.or_solution = self.or_model.SolveWithParameters(params)
            s = self.or_model.status()
            self.status = STATUS_NAME[s]
        report(self.status)

    def result(self) -> Program:
        """Generate the schedule program resulted from triggering run()

        Returns:
            Program: New Program instance
        """
        if self.status != "ROUTING_SUCCESS":
            return self.in_program

        out_program = deepcopy(self.in_program)

        # Get all the sequence of the orders grouped by vehicule
        group = get_vehicule_route(
            self.or_solution,
            self.or_model,
            self.or_manager,
            self.vehicules,
            self.TransGraph)

        # Generate plans for each order in fifo mode based on selected recipe
        for vehicule, orders in group.items():
            # This vehicule wasn't used
            if not orders:
                continue

            stack_fifo_plans(
                orders,
                vehicule,
                out_program,
                self.recetary,
                self.pivot,
                self.scale)

        reset_program_interval(out_program)

        return out_program

    def or_result(self) -> Program:
        """Generate the schedule program resulted by combining all the post-process
        of Flowshop model's result and the Routing Scheduler result.

        Returns:
            Program: New Program instance with the plans result of the model
        """
        if self.status != "ROUTING_SUCCESS":
            return self.in_program

        # Set and Fed the Flowshop model with the same data of Routing Scheduler
        post_planner = FlowShop()
        post_planner.set_scale(self.scale)
        post_planner.add_recipes(self.recipes)
        post_planner.set_program(self.in_program)
        post_planner.set_demand(self.in_demand)
        post_planner.add_stops(self.stops)

        # Run the post-planner for considering anothers constrains
        post_planner.run()

        return post_planner.result()
