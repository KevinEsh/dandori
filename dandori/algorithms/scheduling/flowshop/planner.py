from copy import deepcopy
from datetime import datetime
from collections import defaultdict
from typing import Callable, List, Tuple
# * Thrid-party dependencies
from attr import attrib, attrs
from gstorm import GraphQLType
from ortools.sat.python import cp_model
# * Scheduler dependencies
from dandori.helpers import graphtools as gt
from dandori.helpers import printers as pt
from dandori.helpers import metadata as mt
from dandori.models import Program, Demand, Time, FunctionType
from dandori.validators import valid_demand, valid_stop, valid_recipe, valid_program
# * Direct dependencies
from .traductor import insert_plans, insert_stops
from .ignition import ignite_optimizator, ignite_program, ignite_recipe, ignite_transitions
from .constrains import add_dependency, add_optional_process, add_resource_no_overlap, add_single_recipe


@attrs
class FlowShop(object):
    """Scheduler class for solving FlowShop scheduling problems

    Args:
        object (object): Father base class

    Raises:
        NotImplementedError: If some of the inputs are not implemented
        ValueError: If validator of data inputs are not valid

    Returns:
        FlowShop: New instance of solver
    """

    model = attrib(default=None)
    solver = attrib(default=None)
    printer = attrib(default=None)
    recetary = attrib(factory=lambda: defaultdict(list))  # material.name,[G]
    ignitions = attrib(factory=lambda: defaultdict(list))  # order.name,[G]
    or_data = attrib(factory=lambda: defaultdict(list))  # resource.name,[G]
    or_trans = attrib(factory=lambda: defaultdict(list))  # resource.name,[G]
    optionals = attrib(factory=lambda: defaultdict(list))  # process.code, [[str]]
    funbook = attrib(factory=lambda: defaultdict(Time))
    in_program = attrib(factory=Program)
    out_program = attrib(factory=Program)
    demand = attrib(factory=Demand)
    pivot = attrib(factory=datetime.utcnow)
    stops = attrib(factory=list)
    targets = attrib(factory=list)
    or_targets = attrib(factory=list)
    status = attrib(default="UNKNOWN")
    scale = attrib(default="minutes")
    optim_mode = attrib(default="minimize")
    batch_mode = attrib(default=False)

    def add_optionals(self, orderCode: str, processCode: str, groups: list[list[str]]) -> None:
        """Activate the optional resources constraint liked to the given process.
        This constraint is meant to select in a sigle process just a group of resources
        in the list given by the user.

        Args:
            orderCode (str): Code of the order which will have this constraint
            processCode (str): Code of the process inside a recipe
            groups (list[list[str]]): List of lists of the resource names of each group
                of optional resources
        """
        self.optionals[processCode].extend(groups)

    def add_stops(self, stops: List[GraphQLType]) -> None:
        """Add a list of new stops to be considered while running the model.
        Each stop will produce a plan into the program

        Args:
            stops (GraphQLType): List of Schedule-Logic's Stops to be added.
        """
        # Raise invalid stops and append them to list
        for stop in stops:
            valid_stop(stop)

        self.stops.extend(stops)

    def add_recipes(self, recipes: List[GraphQLType], locked: bool = False) -> None:
        """Add a new recipe to be considered as new way to create materials.
        This recipe will be registered in the recetary

        Args:
            recipes (GraphQLType): List of Schedule-Logic's Recipes to be added.
                Each has to have a list of processes conected in DAG form
            mode (str): Optional default "unlocked". You could choose between
                "unlock" & "locked"
        """
        # Raise invalid recipe
        for recipe in recipes:
            valid_recipe(recipe)

        # Register all recipes into the recetary
        for recipe in recipes:
            # Is the recipe already registered?
            if any(NetTemplate.graph["recipe"].code == recipe.code
                   for networks in self.recetary.values()
                   for NetTemplate in networks):
                return

            # Create graph template for the recipe
            NetTemplate = gt.create_network_template(recipe, self.funbook)
            NetTemplate.graph["locked"] = locked

            # Add the material the recetary and then append recipe graph template for future copies
            for rel in recipe.recipeMaterials:
                name = rel.material.name
                self.recetary[name].append(NetTemplate)

    def link_function(self, function: Callable, code: str) -> None:
        """This method links the current callable with identifier 'code' to all
        the Schedule-Logic's Functions with the same code in order to calculate
        process time in a fashinable way.

        Args:
            function (Callable): function to be called during execution, Has to
                return and integer and have 'order' & 'process' as inputs
            code (str): Identifier of the function
        """
        mt.raise_invalid_func(function, FunctionType.PROCESS_TIME)
        self.funbook[code].call = function
        self.funbook[code].linked = True

    def set_scale(self, scale: str) -> None:
        """Set time scale which integer OR-tools variables will be set

        Args:
            scale (str): Try one of the followings: "days", "hours", "minutes", "seconds"

        Raises:
            NotImplementedError: If your scale is not implemented
        """
        _scales = ["days", "hours", "minutes", "seconds"]
        if not scale in _scales:
            raise NotImplementedError(
                f'scale {scale} not implemented. Try one of this: {_scales}')
        self.scale = scale

    def set_pivot(self, pivot: datetime) -> None:
        """Set the minimal time to start fixing plans

        Args:
            pivot (datetime): Starting date
        """
        mt.raise_invalid_date(pivot)
        self.pivot = pivot

    def set_demand(self, demand: GraphQLType) -> None:
        """Set the orders to be scheduled for the algorithm. These orders has to have valida data

        Args:
            demand (GraphQLType): Demand object that contains a list of non-empty orders
        """
        # Raise invalid demand
        valid_demand(demand)
        # Copying all demand data
        self.demand = deepcopy(demand)

    def set_program(self, program: GraphQLType) -> None:
        """Set the plans to be forced scheduled for the algorithm. These plans has to have valid data

        Args:
            program (GraphQLType): Program object that constains a list of no-overlaped plans
        """
        # Raise invalid program
        valid_program(program)
        # Copying all program data
        self.in_program = deepcopy(program)

    def optimize(self, target: str = "makespan", mode: str = "minimize"):
        """Use this function to activate optimization mode and set objetive variable

        Args:
            target (str, optional): Name of the objetive to be optimized. Defaults to "makespan".
            mode (str, optional): Choose between "minimize" or "maximize". Defaults to "minimize".

        Raises:
            NotImplementedError: If "minimize" nor "maximize" were chosen
        """
        if mode not in ["minimize", "maximize"]:
            raise NotImplementedError(
                f"mode '{mode}' not implemented. Try 'minimize' or 'maximize'.")

        self.targets.append(target)
        self.optim_mode = mode

    def __init_model(self):
        """Ignite OR-tools' CpModel and CpSolver in order to create a new schedule program
        """
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.printer = cp_model.ObjectiveSolutionPrinter()
        self.solver.parameters.num_search_workers = 6

    def __init_demand(self):
        """Select all the available recipes for each order and make a Network
        Depency Graph from GraphTemplate
        """
        for order in self.demand.orders:
            # Ignite all the recipes for this order
            for NetTemplate in self.recetary[order.material.name]:
                GraphRecipe = deepcopy(NetTemplate)
                GraphRecipe.graph["order"] = order
                gt.calculate_durations(GraphRecipe)
                self.ignitions[order.name].append(GraphRecipe)

                # Save OR-tools' variables from processes
                or_output = ignite_recipe(
                    self.model, GraphRecipe, self.pivot, self.scale)
                for name, or_tuples in or_output.items():
                    self.or_data[name].extend(or_tuples)

                # Save OR-tools' variables from transitions
                if GraphRecipe.graph["locked"]:
                    or_output = ignite_transitions(self.model, GraphRecipe)
                    for name, or_tuples in or_output.items():
                        self.or_trans[name].extend(or_tuples)

    def __init_program(self):
        """Set forced ortools variables from program's plans
        """
        self.out_program = deepcopy(self.in_program)

        # Initialize stops into program's plans
        insert_stops(self.out_program, self.stops)

        or_output = ignite_program(
            self.model, self.out_program, self.pivot, self.scale)
        for name, or_list in or_output.items():
            self.or_data[name].extend(or_list)

    def __init_constrains(self):
        """Apply all constrains to or_data
        """
        for networks in self.ignitions.values():
            add_single_recipe(self.model, networks)  # One recipe for order
            for GraphRecipe in networks:
                add_dependency(self.model, GraphRecipe)  # Processes dependency
        add_resource_no_overlap(self.model, self.or_data, self.or_trans)

        if self.optionals:
            add_optional_process(self.model, self.recetary, )

    def __init_target(self):
        """Set objetive variable through math equation
        """
        if not self.targets:
            return

        self.or_targets = ignite_optimizator(
            self.model, self.or_data, self.or_trans,
            self.targets, self.optim_mode)

    def debug_mode(self, activated: bool = False) -> None:
        """This method is a settler for debugging mode in OR-tools

        Args:
            activated (bool, optional): True if wanted to activate OR-tools' debug mode. Defaults to False.
        """
        if activated:
            self.solver.parameters.log_search_progress = True
        else:
            self.solver.parameters.log_search_progress = False

    def run(self, verbose: int = 0) -> None:
        """Run the algorithm for scheduling given constrains, data and objetive

        Args:
            verbose (int, optional): Verbose mode 0,1 or 2. Defaults to 0.
        """
        self.__init_model()
        self.__init_demand()
        self.__init_program()
        self.__init_constrains()
        self.__init_target()

        # Running Ortools solver
        with pt.solver_context("flowshop", verbose) as report:
            s = self.solver.SolveWithSolutionCallback(self.model, self.printer)
            self.status = self.solver.StatusName(s)
        report(self.status)

    def result(self) -> Program:
        """Get program and demand generated for the scheduler.

        Returns:
            Program: New program, New demand
        """
        # No solution was found, return input program as output
        if self.status in ["MODEL_INVALID", "INFEASIBLE", "UNKNOWN"]:
            return self.in_program

        # Create and insert new plans into program if feasible solution was found
        for networks in self.ignitions.values():
            for GraphRecipe in networks:
                or_recipe = self.solver.Value(GraphRecipe.graph["or_recipe"])
                if not or_recipe:
                    continue
                insert_plans(self.out_program, self.solver,
                             GraphRecipe, self.pivot, self.scale)

        # Recalculating extension from the program
        self.out_program.startAt = min(
            plan.startAt for plan in self.out_program.plans)
        self.out_program.endAt = max(
            plan.endAt for plan in self.out_program.plans)

        return self.out_program

    def request(self) -> Demand:
        """Get the demand of orders requested by the given solution

        Returns:
            Demand: Newer demand requested by the solution in run()
        """
        # No solution was found, return input demand
        if self.status in ["MODEL_INVALID", "INFEASIBLE", "UNKNOWN"]:
            return self.demand
        return self.demand
