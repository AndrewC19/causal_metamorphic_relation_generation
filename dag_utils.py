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
                continue

        valid_non_causal_node_pairs.append(pair)

    return valid_non_causal_node_pairs


def get_exogenous_nodes(graph: nx.DiGraph):
    """List exogenous nodes in a given directed graph.

    :param graph: A networkx directed graph (nx.DiGraph)
    :return: A list of exogenous nodes (nodes without parents) in the
             directed graph.
    """
    return [node for node in graph.nodes if not list(graph.predecessors(node))]

