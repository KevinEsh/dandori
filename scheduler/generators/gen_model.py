from sys import modules
from random import choice, randint
from typing import List, Tuple, Union
from datetime import datetime, timedelta
# * Third-party dependencies
from attr import attrs
from networkx import DiGraph
from gstorm import GraphQLType
# * Generator dependencies
from scheduler.generators.gen_relations import connect_models
from scheduler.generators.gen_graph import GraphGenerator as ggen
from scheduler.generators.gen_dist import DistributionGenerator as dgen
# * Model dependencies
from scheduler.helpers import metadata as mt
from scheduler.helpers import graphtools as grt
from scheduler.models import __models__, __enums__, __relations__, __arcs__
from scheduler.models import *

_modules = modules[__name__]
_random_str = dgen.create("uuid4")


@attrs
class ModelGenerator:

    @classmethod
    def create(cls,
               model: Union[GraphQLType, str],
               size: int = 1,
               ignore: List = None,
               from_graph: DiGraph = None,
               **choices: list) -> List[GraphQLType]:
        if ignore is None:
            ignore = []

        # TODO: definir una logica para .ignore y .choice parecida a la de gstrom
        if model in __models__:
            if from_graph and isinstance(from_graph, DiGraph):
                return cls.__create_from_graph(from_graph, model)
        elif model in __enums__:
            return cls.__create_random_enum(model, size)
        else:
            raise NotImplementedError(f"model '{model}' not implemented.")

    @classmethod
    def __create_from_graph(cls, Graph: DiGraph, modelname: str) -> List[GraphQLType]:
        """This new functionality is useful to create any Schedule-Logic models
        with arcs into a NetworkX's DiGraph in order to represent a both concise
        and robust data-structure.

        Args:
            Graph (DiGraph): Any DiGraph from NetworkX
            modelname (str): Name of the Schedule-Logic model. This model has to have "arcs"

        Returns:
            List[GraphQLType]: List of connected instanes in the same way that input Graph
        """
        Model = mt.get_model_class(modelname)
        ModelArc = mt.get_arc_class(modelname)
        objects = {node: Model(name=_random_str(modelname.lower(),  length=7))
                   for node in Graph.nodes()}

        for u, v in Graph.edges():
            oprev = objects[u]
            onext = objects[v]
            arc_prev = ModelArc(prev=oprev, next=onext)
            arc_next = ModelArc(prev=onext, next=oprev)
            oprev.nexts.append(arc_prev)
            onext.prevs.append(arc_next)

        return list(objects.values())

    @classmethod
    def __create_random_enum(cls, enumname, choices):
        # TODO: aplicar la logica de choices e ignore
        if enumname in choices:
            options = choices[enumname]
            return choice(options)
        else:
            options = list(__enums__[enumname])
            return choice(options)

    @classmethod
    def build_plant(
            cls,
            num_processors: int = 1,
            num_stockers: int = 1,
            num_duals: int = 1) -> Tuple[List[GraphQLType]]:
        """This function generates the three types of resources that make up the
        operating machines of a manufacturing plant

        Args:
            num_processors (int, optional): Number of machines that only can
                process materials. Defaults to 1.
            num_stockers (int, optional): Number of machines that only can
                storage materials. Defaults to 1.
            num_duals (int, optional): Number of machines that can do both
                process and storage machines. Defaults to 1.

        Returns:
            Tuple[List[GraphQLType]]: Instances generates and encapsulated into
                lists
        """
        # TODO: (Opcional) revisar si esta funcion se puede generalizar el nombre del proce
        processors = [Resource(
            code=_random_str(length=7),
            name=_random_str("processor", length=7),
            resourceType=ResourceType.PROCESSOR)
            for _ in range(num_processors)]

        stockers = [Resource(
            code=_random_str(length=7),
            name=_random_str("stocker", length=7),
            resourceType=ResourceType.STOCKER)
            for _ in range(num_stockers)]

        duals = [Resource(
            code=_random_str(length=7),
            name=_random_str("dual", length=7),
            resourceType=ResourceType.MIX)
            for _ in range(num_duals)]

        return processors, stockers, duals

    @classmethod
    def build_materials(cls, num_products: int = 1, num_ingredients: int = 1) -> Tuple[List[GraphQLType]]:
        """This function generates the two types of materials related into a
        manufactuing plant: Products and Ingredients.
        Besides there is no distinction between both of them in current Schedule
        Logic's version.recip, there is important to segregate them in Scheduler

        Args:
            num_products (int, optional): Number of materials that can have a
                recipe. Defaults to 1.
            num_ingredients (int, optional): Number of materials that only can
                be used to as ingredients into a recipe. Defaults to 1.

        Returns:
            Tuple[List[GraphQLType]]: Instances generates and encapsulated into
                lists
        """
        # TODO: (Opcional) revisar si esta funcion se puede generalizar aun mas el nombre
        ingredients = [Material(
            code=_random_str(length=7),
            name=_random_str("ingredient", length=7))
            for _ in range(num_ingredients)]

        products = [Material(
            code=_random_str(length=7),
            name=_random_str("product", length=7))
            for _ in range(num_products)]

        return products, ingredients

    @classmethod
    def build_recipes(
            cls,
            products: List[GraphQLType],
            ingredients: List[GraphQLType],
            resources: List[GraphQLType],
            functions: List[GraphQLType],
            num_recipes_per_prod: int = 1,
            max_processes: int = 1,
            max_resources_per_process: int = 1,
            max_ingredients_per_process: int = 1) -> Tuple[List[GraphQLType]]:
        """This function take a list of products and generate one or more valid
        fictional recipes for each of them.

        Args:
            products (List[GraphQLType]): List of materials which will be attached
                to one or more fictional recipes
            ingredients (List[GraphQLType]): List of materials which will be
                sampled inside processes in order to create valid recipes
            resources (List[GraphQLType]): List of resources which will be
                sampled inside processes in order to create valid recipes
            num_recipes_per_prod (int, optional): Number of recipes to generate
                for each element of 'products'. Defaults to 1.
            max_processes (int, optional): Maximum number of connected processes
                in a recipe. Defaults to 1.
            max_resources_per_process (int, optional): Maximum number of resources attached
                in a process. Defaults to 1.
            max_ingredients (int, optional): Maximum number of ingredients
                attached in a process. Defaults to 1.

        Returns:
            Tuple[List[GraphQLType]]: List of Schedule-Logic's Recipes generated during runtime
        """
        # For each product generate 'num_recipes_per_prod' Recipes
        recipes = []
        for product in products:
            for _ in range(num_recipes_per_prod):
                recipe = Recipe(
                    code=_random_str(length=7),
                    name=_random_str("recipe", length=7),
                    rank=randint(0, 10),
                )
                recipes.append(recipe)

                # Connecting recipe and product
                relation = RecipeMaterial(recipe=recipe, material=product)
                product.recipeMaterials.append(relation)
                recipe.recipeMaterials.append(relation)

                # Creating and connecting processes in a dag form
                GraphRecipe = grt.prune_dag(ggen.create("path", max_processes))
                processes = cls.create("Process", from_graph=GraphRecipe)

                # Assing one random function to timeFunction
                for p in processes:
                    p.timeFunction = choice(functions)

                # Connecting instanteces. Recipe to all process and each process to a set of ingredients and resources
                connect_models([recipe], processes)
                connect_models(processes, resources,
                               sampled=max_resources_per_process)
                connect_models(processes, ingredients,
                               sampled=max_ingredients_per_process)

        return recipes

    @classmethod
    def build_demand(
            cls,
            products: List[GraphQLType],
            uoms: List[GraphQLType],
            pivot: datetime = datetime.now(),
            **kwargs: int) -> GraphQLType:
        """This function take a list of products to generate a new random demand
        for testing purposes

        Args:
            products (List[GraphQLType]): List of materials from the schedule
                logic model to sample from
            uoms (List[GraphQLType]): List of UnitsOfMeasuments from the schedule
                logic model to sample from
            pivot (datetime): Datetime from which all the order.startAt will be set
            scale (str): Chose one of this: "days", "hours", "minutes", "seconds"
            num_orders (int): Total of Orders to be generated
            max_quantity (int): Maximum value to 'quantity' field
            max_extension (int): Maximum value in selected `scale` to set order.endAt
            min_extension (int): Minimum value in selected `scale` to set order.endAt

        Returns:
            GraphQLType: Demand model with a list of valid orders
        """
        # Getting hyperparameters
        scale = kwargs.get("scale", "hours")
        num_orders = kwargs.get("num_orders", 1)
        max_qua = kwargs.get("max_quantity", 1)
        max_ext = kwargs.get("max_extension", 1)
        min_ext = kwargs.get("min_extension", max(1, max_ext))
        start_range = kwargs.get("start_range", (0, 0))

        # Generating new orders into a new demand
        demand = Demand(guid=_random_str("demand", length=16), startAt=pivot)
        for _ in range(num_orders):
            extension = timedelta(**{scale: randint(min_ext, max_ext)})
            startAt = pivot + timedelta(**{scale: randint(*start_range)})
            order = Order(
                code=_random_str(length=8),
                name=_random_str("order", length=8),
                priority=randint(1, 100),
                quantity=randint(1, max_qua),
                quantityUom=choice(uoms),
                material=choice(products),
                startAt=startAt,
                endAt=startAt + extension,
            )
            demand.orders.append(order)
        last = max(demand.orders, key=lambda order: order.endAt)
        demand.endAt = last.endAt
        return demand

    @classmethod
    def build_stops(
            cls,
            resources: List[GraphQLType],
            costs: List[GraphQLType],
            pivot: datetime,
            **kwargs: int) -> List[GraphQLType]:
        """This function take a list of resources and generate a list of random
        stops for testing purposes

        Args:
            resources (List[GraphQLType]): List of Resources from the schedule
                logic model to sample from
            costs (List[GraphQLType]): List of Functions from the schedule-logic
                model to sample from
            pivot (datetime): Datetime from which all the order.startAt will be set
            scale (str): Chose one of this: "days", "hours", "minutes", "seconds"
            num_stops (int): Total of Orders to be generated
            max_reasons (int): Maximum number of StopReasons to sample from
            max_extension (int): Maximum value in selected `scale` to set order.endAt
            min_extension (int): Minimum value in selected `scale` to set order.endAt
            max_start (int): Maximum value in selected `scale` to set order.startAt
            min_start (int): Minimum value in selected `scale` to set order.startAt

        Returns:
            List[GraphQLType]: List of valid Stops instances from schedule-logic model
        """
        # Getting hyperparameters
        scale = kwargs.get("scale", "hours")
        num_stops = kwargs.get("num_stops", 1)
        max_reasons = kwargs.get("max_reasons", 1)
        max_ext = kwargs.get("max_extension", 1)
        min_ext = kwargs.get("min_extension", max(1, max_ext))
        start_range = kwargs.get("start_range", (0, 0))

        # Creating random reasons for stops
        reasons = [StopReason(
            code=_random_str(length=8),
            name=_random_str("reason", length=8),
            description=_random_str(length=16),)
            for _ in range(max_reasons)]

        # Creating random stops through sampling data
        stops = []
        for _ in range(num_stops):
            reason = choice(reasons)
            cost = choice(costs)
            resource = choice(resources)
            extension = timedelta(**{scale: randint(min_ext, max_ext)})
            startAt = pivot + timedelta(**{scale: randint(*start_range)})
            stop = Stop(
                stopReason=reason,
                startAt=startAt,
                endAt=startAt + extension,
                scheduled=choice([True, False]),
                cost=cost,
            )
            connect_models([resource], [stop])
            reason.stops.append(stop)
            cost.stops.append(stop)
            stops.append(stop)
        return stops

    @classmethod
    def build_uoms(cls, num_uoms: int = 1) -> List[GraphQLType]:
        """This function builds a given number of random UnitOfMeasurements for testing purposes

        Args:
            num_uoms (int, optional): Number of Uoms to be generated. Defaults to 1.

        Returns:
            List[GraphQLType]: List of instances of UnitOfMeasurement
        """
        return [UnitOfMeasurement(
            code=_random_str(length=4),
            name=_random_str("uom", length=4),
            symbol=_random_str(length=2),
            uomType=choice(list(UomType)),
        ) for _ in range(num_uoms)]

    @classmethod
    def build_functions(cls, uoms: List[GraphQLType], num_functions: int = 1) -> List[GraphQLType]:
        """This function takes a list of UnitOfMeasument's instances & builds a
        return given number of random Functions for testing purposes.

        Args:
            uoms (List[GraphQLType]): List of UnitsOfMeasurements to sample from
            num_functions (int, optional): Number of Functions to be generated.
                Defaults to 1.

        Returns:
            Tuple[GraphQLType]: List of instances of Function
        """
        return [Function(
            code=_random_str(length=8),
            name=_random_str("function", length=8),
            functionType=choice(list(FunctionType)),
            uom=choice(uoms),
        )]

    @classmethod
    def build_program(cls, demand: GraphQLType, pivot: datetime = datetime.now(), num_plans: int = 1) -> GraphQLType:
        # TODO: (Opcional) agregar planes aleatorios como condiciones iniciales
        program = Program(
            guid=_random_str("program", length=16),
            status=choice(list(ProgramStatus)),
            startAt=pivot,
            toSolve=demand,
        )
        if not program.plans:
            program.endAt = pivot
        else:
            program.endAt = max(program.plans, key=lambda p: p.endAt).endAt
        return program

    @classmethod
    def build_changeovers(cls, products: List[Material], functions: List[Function]) -> List[Changeover]:
        """This function takes a list of UnitOfMeasument's instances & builds a
        return given number of random Functions for testing purposes.

        Args:
            uoms (List[GraphQLType]): List of UnitsOfMeasurements to sample from
            num_functions (int, optional): Number of Functions to be generated.
                Defaults to 1.

        Returns:
            Tuple[GraphQLType]: List of instances of Function
        """
        # TODO: SDLSR-128
        return
