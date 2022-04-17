import networkx as nx
from random import randint
from scheduler.generators.gen_base import BaseGenerator


class GraphGenerator(BaseGenerator):

    @classmethod
    def create(cls, graphtype: str, maxnodes: int = 10, density: float = 0.1, seed: int = None) -> nx.DiGraph:
        """Generate a class of random graph for general purpose

        Args:
            graphtype (str): Could be one of the followings: "dag", "rootdat", "tree"
            size (int): Number of nodes
            density (float, optional): Probability p of add an edge between any pair of nodes. Defaults to 0.3.

        Returns:
            nx.DiGraph: Generated graph with the given specifications
        """
        if graphtype == "dag":
            return cls.__create_random_dag(maxnodes, density)
        elif graphtype == "rootdag":
            return cls.__create_random_rootdag(maxnodes, density)
        elif graphtype == "tree":
            return cls.__create_random_tree(maxnodes, seed)
        elif graphtype == "path":
            return cls.__create_random_path(maxnodes)

    @classmethod
    def __create_random_dag(cls, maxnodes: int, density: float) -> nx.DiGraph:
        """Generate a Directed Acyclic Graph

        Args:
            maxnodes (int): number of nodes
            density (float): probability p of making an edge between to pair of nodes

        Returns:
            nx.DiGraph: Random DAG
        """
        Graph = nx.gnp_random_graph(maxnodes, density, directed=True)
        return nx.DiGraph(
            [(u, v) if u < v else (v, u) for u, v in Graph.edges()])

    @classmethod
    def __create_random_tree(cls, maxnodes: int, seed: int = None) -> nx.DiGraph:
        # TODO: terminar de conectar el arbol
        Graph = nx.random_tree(maxnodes, seed)
        return nx.DiGraph(
            [(u, v) if u < v else (v, u) for u, v in Graph.edges()])

    @classmethod
    def __create_random_rootdag(cls, maxnodes: int, density: float) -> nx.DiGraph:
        """Generate a Directed Acyclic Graph with one final node with no out degree

        Args:
            maxnodes (int): number of nodes
            density (float): probability p of making an edge between to pair of nodes

        Returns:
            nx.Digraph: Random rooted DAG
        """
        Graph = cls.__create_random_dag(maxnodes-1, density)
        Graph.add_node(maxnodes-1)
        for node in Graph.nodes():
            if not Graph.out_degree(node) and node != maxnodes - 1:
                Graph.add_edge(node, maxnodes-1)
        return Graph

    @classmethod
    def __create_random_path(cls, maxnodes: int) -> nx.DiGraph:
        Graph = nx.path_graph(randint(1, maxnodes), create_using=nx.DiGraph)
        return Graph


if __name__ == "__main__":
    G = GraphGenerator.create("path")
    print(G)
    print(G.nodes())
    print(G.edges())
    print(G.is_directed())
