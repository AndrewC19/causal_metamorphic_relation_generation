import networkx as nx
import random
from networkx.drawing.nx_pydot import to_pydot
from networkx.exception import NetworkXError
from helpers import safe_open_w
from dag_utils import get_non_causal_node_pairs, get_exogenous_nodes


def generate_dag(
    n_nodes: int, p_edge: float, seed: int = None, dot_path: str = None
) -> nx.DiGraph:
    """Generate a random DAG with a specified number of nodes and edges.

    1. Sample a random Erdos Renyi graph with the specified number of nodes and probability of edges. The nodes in this
       graph are labelled in ascending numerical order.
    2. Convert the Erdos Renyi graph to a directed graph and remove cycles by deleting edges that point from nodes with
       a larger numerical label to nodes with a smaller numerical label (e.g. 2 --> 1).
    3. Convert exogenous nodes to inputs, labelling them in ascending order as X1, X2, ..., Xn.
    4. Convert endogenous nodes to output, labelling them in ascending order as Y1, Y2, ..., Yn.
    5. Return a networkx directed graph representing the causal DAG.

    Example output for generate_dag(n_nodes=3, p_edge=0.8):

        strict digraph  {
        X1;
        Y1;
        X2;
        X1 -> Y1;
        X2 -> Y1;
        }


    :param n_nodes: The number of nodes the DAG should contain.
    :param p_edge: The probability of edge creation.
    :param seed: An optional random seed.
    :param dot_path: An optional path to save a DOT file.
    return: A string containing a DOT causal DAG.
    """
    if seed:
        random.seed(seed)

    # Create an Erdos-Renyi graph with n_nodes nodes and p_edge probability of edge creation
    erdos_renyi_graph = nx.erdos_renyi_graph(n_nodes, p_edge, directed=True)

    # Convert the Erdos-Renyi graph to a directed graph and remove cycles
    causal_dag = nx.DiGraph(
        (cause, effect) for cause, effect in erdos_renyi_graph.edges() if cause < effect
    )

    # Identify any deleted nodes and add to causal DAG as an isolated node
    # We will treat such nodes as inputs with no effect
    isolated_nodes = [
        node for node in erdos_renyi_graph.nodes if node not in causal_dag.nodes
    ]
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

    if dot_path:
        with safe_open_w(dot_path) as dag_file:
            dot_input_output_causal_dag = to_pydot(input_output_causal_dag).to_string()
            dag_file.write(dot_input_output_causal_dag)

    return input_output_causal_dag


def mutate_dag(causal_dag: nx.DiGraph, p_invert_edge: float):
    """Invert potential edges in the causal DAG with a specified probability.

    An edge (or absence thereof) can only be inverted if the resulting causal
    DAG remains acyclic.

    :param causal_dag: A networkx directed graph representing the causal DAG.
    :param p_invert_edge: Probability that an arbitrary edge (or lack thereof)
    is inverted.
    """
    non_causal_node_pairs = get_non_causal_node_pairs(causal_dag)
    invertible_node_pairs = list(causal_dag.edges) + non_causal_node_pairs

    for node_pair in invertible_node_pairs:
        if random.random() < p_invert_edge:
            try:
                causal_dag.remove_edge(*node_pair)
            except NetworkXError:
                causal_dag.add_edge(*node_pair)

    assert nx.is_directed_acyclic_graph(causal_dag)
    return causal_dag


if __name__ == "__main__":
    dag = generate_dag(15, 0.5)
    mutated_dag = mutate_dag(dag, 0.5)
