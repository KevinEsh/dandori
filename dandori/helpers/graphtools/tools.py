"""
# indicando que las cantidades de los ingredientes ya no son funciones, sino numero enteros
Graph.recipe = Recipe(...) # Receta que provee de template para la creación del grafo
Graph.order = Order(...) # Orden que solicita la creación del grafo de receta
Graph.or_recipe = cp_model.IntVar(...)

Graph.nodes(data=True) ={
    "filtrado": {
        task=Task(
            process=Process(...),
            optional=True,
            group="g1234235"
            duration=0
            )

        "time": Time(
            call=Callable,
            linked=False
            ),

        "resources": [
            Resource(name="filtro 3", ...),
            Resource(name="tanque 2", ...),
        ],

        "ingredients": [
            {"material": Material(name="cheve"), "quantity": 0, "function": <python.function>, "calculated":False},
            {"material": Material(name="agua"), "quantity": 0,  "function": <python.function>, "calculated":False},
            {"material": Material(name="carbonato"), "quantity": 0, "function": <python.function>, "calculated":False},
        ],
    }
}"""

# Standard library imports
from itertools import combinations
from typing import Callable, List, Any, Dict
# Third-party imports
import pydash
from networkx import DiGraph, topological_sort, has_path, is_directed_acyclic_graph
# Local application imports
from dandori.models import Time, Ingredient, Task, Recipe, Plan, Changeover, Order


def prune_dag(Graph: DiGraph) -> DiGraph:
    """Prune redundant dependency edges in a network dependency dag graph.

    Args:
        Graph (DiGraph): Network Dependency in a DAG form

    Returns:
        DiGraph: New network dependency without redundant edges
    """
    # Create a copy of current DAG
    PrunedGraph = DiGraph(Graph)

    # Get Topological list order in DAG in order to optimize algorithm
    toplist = list(topological_sort(Graph))
    index = {node: index for index, node in enumerate(toplist)}
    edgelist = Graph.edges()

    # Remove redundant edges
    for u, v in edgelist:
        for i in toplist[index[u]+1:index[v]]:
            if has_path(Graph, u, i) and has_path(Graph, i, v):
                PrunedGraph.remove_edge(u, v)
                break

    return PrunedGraph


def is_dag(Graph: DiGraph) -> bool:
    """Checks weather a Graph is Directed Acyclic Graph (DAG)

    Args:
        Graph (DiGraph): Graph object to validate

    Returns:
        bool: is DAG
    """
    return is_directed_acyclic_graph(Graph)


def raise_node_not_registered(Graph: DiGraph, objects: List[object]) -> None:
    for obj in objects:
        if not Graph.has_node(obj.name):
            raise RuntimeError(
                f"Graph '{Graph.graph['code']}' has no node '{obj.name}'")


def connect_nodes(Graph: DiGraph, objects: List[object]) -> DiGraph:
    # TODO: probar la funcion con drawer.plot_diagram
    # TODO: programar los tests
    # TODO: raise has_arcs(modelname)
    # TODO: en caso de que no se tenga la lista nexts, intentar si tiene la lista prevs
    # TODO: si no tiene ninguna de las dos listas, levanta una excepción.
    raise_node_not_registered(Graph, objects)  # ? deberia?

    for obj in objects:
        u = obj.name
        for arc in obj.nexts:
            v = arc.next.name
            Graph.add_edge(u, v)  # Automatic node added if not exist

    return Graph


def selector(key: str) -> Callable:
    """For matching a key with a code in a Schedule-Logic datum

    Args:
        key: string to match instance

    Returns:
        Callable: function to iterate
    """
    def callback_selector(datum) -> bool:
        """For matching a key with a code in a Schedule-Logic datum

        Args:
            datum: instance to match

        Returns:
            bool: Has the code equal than the current key
        """
        return datum.code == key
    return callback_selector


def create_plan_graph(recipe: Recipe, plans: List[Plan]) -> DiGraph:
    """Generator of a graph dependency containing inside its nodes plans generated
    beforehand by a scheduling algorithm taking as template the master recipe

    Args:
        recipe (Recipe): Recipe which created the plans beforehand by a scheduling

    Returns:
        DiGraph: Network dependency of plans
    """
    if not plans:
        raise ValueError("'plans' must have at least be lenght one")

    GraphPlan = DiGraph(order=plans[0].order)
    processes = []

    for relation in recipe.recipeProcesses:
        # Find the node
        process = relation.process
        processes.append(process)

        linked_plans = pydash.filter_(plans, selector(process.code))

        # Raise if process is not identified in plans
        if not linked_plans:
            raise RuntimeError(f'process "{process.code}" has no linked plans')

        GraphPlan.add_node(
            process.code,
            plans=linked_plans,
        )

    connect_nodes(GraphPlan, processes)

    return prune_dag(GraphPlan)


def create_network_template(recipe: Recipe, funbook: Dict[str, Time]) -> DiGraph:
    # TODO: probar la funcion
    # TODO: programar los tests
    GraphRecipe = DiGraph(recipe=recipe)
    processes = []

    for relation in recipe.recipeProcesses:
        process = relation.process
        processes.append(process)

        # Get the function's code, initialice and Time  object & register it in funbook
        code = pydash.get(process.timeFunction, "code", default="SDL_CODE")
        # TODO: uom = pydash.get(process.timeFunction, "uom", default="hours")
        time = funbook[code]  # Time(call, function)
        # TODO: time.uom = uom

        task = Task(process=process)  # Task(duration, process)
        resources = [arc.resource for arc in process.processResources]
        # TODO: averiguar como poner la funcion de calculo de cantidad de ingredientes
        ingredients = [Ingredient(
            name=arc.material.name,
            # TODO: function=get_function(arc.quantityFunction),
            # TODO: scale=get_uom(arc.quantityFunction),
        ) for arc in process.processMaterials]

        GraphRecipe.add_node(
            process.name,
            task=task,
            time=time,
            resources=resources,
            ingredients=ingredients,
        )

    GraphRecipe = connect_nodes(GraphRecipe, processes)

    return prune_dag(GraphRecipe)


def create_orders_graph(
        orders: List[Order],
        changeovers: List[Changeover]) -> DiGraph:
    """Creates a DiGraph of allowed transitions where each node is a Order instance
    of the list 'orders' and directed edges are represented by an allowed transition
    between changeover.before (Material) and cahngeover.after (Material). The edge's
    cost is calculated by calling the function linked to changeover.changeoverFunction.
    Note that if there is no and edge between Order X and Order Y, that means their
    materials are not allowed to be processed in a sequence X->Y but no necessarilly
    Y->X.

    Args:
        orders (List[Order]): List of orders to be treated as nodes in graph
        changeovers (List[Changeover]): List of all transition data between materials

    Returns:
        DiGraph: Transition DiGraph. Best-case scenario: it's densely connected
    """
    TransGraph = DiGraph()
    transitions = {(c.before.code, c.after.code): c.changeoverFunction.code
                   for c in changeovers}

    # Create nodes from order list
    # ! "id" must have to start at 1 for order 0 is for depot in or-tools routing model
    for _id, order in enumerate(orders, 1):
        TransGraph.add_node(_id, order=order)

    # Create edges from transitions between materials of orders
    tuple_orders = TransGraph.nodes(data="order")

    for (p_id, prev_order), (n_id, next_order) in combinations(tuple_orders, 2):
        # Get material's code of both orders
        m1 = prev_order.material.code
        m2 = next_order.material.code

        # Find out if a pair has allowed transition in both directions
        if (m1, m2) in transitions:
            cost_code = transitions[m1, m2]
            TransGraph.add_edge(p_id, n_id, weight=cost_code)

        if (m2, m1) in transitions:
            cost_code = transitions[m2, m1]
            TransGraph.add_edge(n_id, p_id, weight=cost_code)

    return TransGraph


def calculate_durations(GraphRecipe: DiGraph, **args) -> None:
    """Triggers the callable function associated to each process which returns
    duration integer in the given scale

    Args:
        GraphRecipe (DiGraph): Network depencency already initialized
    """
    args["order"] = GraphRecipe.graph["order"]

    for _, info in GraphRecipe.nodes(data=True):
        args["process"] = info["task"].process
        info["task"].duration = int(info["time"].call(**args))


def calculate_quantities(GraphRecipe: DiGraph, redo: bool = False, **inputs: Any) -> None:
    """Triggers the callable function associated to each process which returns
    duration integer in the given scale

    Args:
        GraphRecipe (DiGraph): Network depencency already initialized
    """
    # Calculate duration of each process
    for _, list_ingredients in GraphRecipe.nodes(data="ingredients"):
        for ingredient in list_ingredients:
            if not redo and ingredient.calculated:
                continue  # The quantity had already been calculated
            # TODO: ver los inputs necesarios para ejecutar la funcion
            # TODO: Pegarle a los inputs, la lista de materiales y/o recursos
            ingredient.quantity = ingredient.function(**inputs)
            ingredient.calculated = True

    # TODO: comprobar si los datos que se modifican en GraphRecipe se actualizan globalmente
