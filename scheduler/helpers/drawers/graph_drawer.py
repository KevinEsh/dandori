from typing import Union
import matplotlib.pyplot as plt
from networkx import DiGraph, layout, draw_networkx
from scheduler.helpers.drawers.globals import CONFIG_RECIPE_GRAPH
from scheduler.models import Recipe


def plot_recipe(recipe: Union[DiGraph, Recipe], imagename: str = "recipe_graph.jpg", **options: str) -> None:
    """Plot and save graph image

    Args:
        Graph (nx.DiGraph): DiGraph to be plotted.
        imagename (str, optional): Name of the image to be saved. Defaults to
            "recipe_graph.jpg".
    """
    if isinstance(recipe, DiGraph):
        Graph = recipe
    else:
        return
    # TODO: SDLSR-144: implementar la posibilidad de pasar una instancia Recipe
    #     Graph = create_network_template(recipe)

    # TODO: SDLR-145: Mejorar la vizualizaciones de los procesos y de los recursos
    # Sidenote: https://www.youtube.com/watch?v=SpDI6-FvtJY
    CONFIG_RECIPE_GRAPH.update(options)
    positions = layout.spring_layout(Graph)
    draw_networkx(Graph, positions, arrows=True, **CONFIG_RECIPE_GRAPH)
    plt.savefig(imagename)
    plt.close()
    return
