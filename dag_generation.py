import networkx as nx
from networkx.drawing.nx_pydot import to_pydot


def generate_dag(n_nodes: int, p_edge: float) -> str:
    """Generate a random DAG with a specified number of nodes and edges.

    :param n_nodes: The number of nodes the DAG should contain.
    :param p_edge: The probability of edge creation.
    return: A string containing a DOT causal DAG.
    """
    # n_edges = int(np.random.normal(n_nodes*n_edges_factor, n_nodes/2))
    erdos_renyi_graph = nx.erdos_renyi_graph(n_nodes, p_edge, directed=True)
    causal_dag = nx.DiGraph((cause, effect) for cause, effect in erdos_renyi_graph.edges() if cause < effect)
    dot_causal_dag = to_pydot(causal_dag).to_string()
    return dot_causal_dag


if __name__ == "__main__":
    dag = generate_dag(10, 0.5)
    print(dag)
