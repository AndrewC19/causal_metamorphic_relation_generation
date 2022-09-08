"""A library of utility functions for causal DAGs."""
import networkx as nx
from itertools import combinations


def get_non_causal_node_pairs(dag: nx.DiGraph):
    """Get all pairs of nodes that do not share a directed edge in a causal DAG.

    This function iterates over all pairs of nodes in the graph between which there is
    no directed edge. It returns all pairs that, if an edge were added, would form a
    valid causal DAG (i.e. no cycle).

    :param dag: A networkx directed graph representing a causal DAG.
    :return: A list of pairs of nodes that do not share a causal edge.
    """
    edges = dag.edges
    node_pairs = list(combinations(dag.nodes, 2))

    # Remove existing causal edges
    non_causal_node_pairs = [pair for pair in node_pairs if pair not in edges]

    # Remove input to input causation, output to input causation, and cycles
    valid_non_causal_node_pairs = []
    for pair in non_causal_node_pairs:
        cause_node, effect_node = pair

        # Input to input causation
        if cause_node[0] == "X" and effect_node[0] == "X":
            continue

        # Output to input causation
        if cause_node[0] == "Y" and effect_node[0] == "X":
            continue

        # Cyclic causation
        if cause_node[0] == "Y" and effect_node[0] == "Y":
            cause_index = int(cause_node[1:])
            effect_index = int(effect_node[1:])
            if cause_index > effect_index:
                pair = (effect_node, cause_node)

        valid_non_causal_node_pairs.append(pair)

    return valid_non_causal_node_pairs


def get_exogenous_nodes(graph: nx.DiGraph):
    """List exogenous nodes in a given directed graph.

    :param graph: A networkx directed graph (nx.DiGraph)
    :return: A list of exogenous nodes (nodes without parents) in the
             directed graph.
    """
    return [node for node in graph.nodes if not list(graph.predecessors(node))]


def structural_hamming_distance(
        true_graph: nx.DiGraph,
        other_graph: nx.DiGraph
):
    """Compute structural hamming distance between a pair of graphs.

    This implementation follows the definition from the following paper:
        Structural Intervention Distance (SID) for Evaluating Causal
        Graphs (Peters and Buhlmann, 2014), page 2.

    Informally, the structural hamming distance is the number of edges that must
    be changed (by removing, adding, or reversing its direction) to make the
    two DAGs structurally equivalent.

    :param true_graph: The true causal DAG.
    :param other_graph: The graph to compare against the true causal DAG.
    :returns: structural hamming distance.
    """
    true_edge_set = set(true_graph.edges)
    other_edge_set = set(other_graph.edges)
    exclusive_true_edges = true_edge_set - other_edge_set
    exclusive_other_edges = other_edge_set - true_edge_set
    return len(exclusive_true_edges) + len(exclusive_other_edges)
