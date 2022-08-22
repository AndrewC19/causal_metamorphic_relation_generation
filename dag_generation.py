import networkx as nx
import random
from networkx.drawing.nx_pydot import to_pydot, write_dot


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
        dot_input_output_causal_dag = to_pydot(input_output_causal_dag).to_string()
        write_dot(dot_input_output_causal_dag, dot_path)

    return input_output_causal_dag


def get_exogenous_nodes(graph: nx.DiGraph):
    """List exogenous nodes in a given directed graph.

    :param graph: A networkx directed graph (nx.DiGraph)
    :return: A list of exogenous nodes (nodes without parents) in the directed graph.
    """
    return [node for node in graph.nodes if not list(graph.predecessors(node))]


if __name__ == "__main__":
    dag = generate_dag(20, 0.5)
