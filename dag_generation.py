import networkx as nx
import random
from networkx.drawing.nx_pydot import to_pydot


def generate_dag(
        n_nodes: int,
        p_edge: float,
        seed: int = None) -> str:
    """Generate a random DAG with a specified number of nodes and edges.

    :param n_nodes: The number of nodes the DAG should contain.
    :param p_edge: The probability of edge creation.
    :param seed: An optional random seed.
    return: A string containing a DOT causal DAG.
    """
    if seed:
        random.seed(seed)

    # Create an Erdos-Renyi graph with n_nodes nodes and p_edge probability of edge creation
    erdos_renyi_graph = nx.erdos_renyi_graph(n_nodes, p_edge, directed=True)

    # Convert the Erdos-Renyi graph to a directed graph and remove cycles
    causal_dag = nx.DiGraph((cause, effect) for cause, effect in erdos_renyi_graph.edges() if cause < effect)

    # Identify any deleted nodes and add to causal DAG as an isolated node
    # We will treat such nodes as inputs with no effect
    isolated_nodes = [node for node in erdos_renyi_graph.nodes if node not in causal_dag.nodes]
    causal_dag.add_nodes_from(isolated_nodes)

    # Identify input nodes (exogenous) and output nodes (endogenous)
    input_nodes = get_exogenous_nodes(causal_dag)
    output_nodes = [node for node in causal_dag.nodes if node not in input_nodes]
    output_nodes.sort()

    # Rename inputs and outputs as X and Y variables, respectively
    input_node_map = {v: f"X{i+1}" for i, v in enumerate(input_nodes)}
    output_node_map = {v: f"Y{o+1}" for o, v in enumerate(output_nodes)}
    node_map = input_node_map | output_node_map
    input_output_causal_dag = nx.relabel_nodes(causal_dag, node_map)

    # Convert DAG to DOT string
    dot_input_output_causal_dag = to_pydot(input_output_causal_dag).to_string()
    return dot_input_output_causal_dag


def get_exogenous_nodes(graph: nx.DiGraph):
    """List exogenous nodes in a given directed graph.

    :param graph: A networkx directed graph (nx.DiGraph)
    :return: A list of exogenous nodes (nodes without parents) in the directed graph.
    """
    return [node for node in graph.nodes if not list(graph.predecessors(node))]


if __name__ == "__main__":
    dag = generate_dag(10, 0.5)
    print(dag)
