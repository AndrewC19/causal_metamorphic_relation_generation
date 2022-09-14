"""A library of utility functions for causal DAGs."""
import networkx as nx
from networkx.drawing.nx_pydot import to_pydot
from itertools import combinations
from helpers import safe_open_w
from typing import List
import json


def get_non_causal_node_pairs(dag: nx.DiGraph):
    """Get all pairs of nodes that do not share a directed edge in a causal DAG.

    This function iterates over all pairs of nodes in the graph between which there is
    no directed edge. It returns all pairs that, if an edge were added, would form a
    valid causal DAG (i.e. no cycle). Furthermore, an edge cannot be added from a
    later output to an earlier one.

    :param dag: A networkx directed graph representing a causal DAG.
    :return: A list of pairs of nodes that do not share a causal edge.
    """
    edges = dag.edges
    node_pairs = list(combinations(dag.nodes, 2))
    output_order = get_output_order(dag)

    # Remove existing causal edges
    non_causal_node_pairs = [(c, e) for (c, e) in node_pairs if ((c, e) not in edges) and ((e, c) not in edges)]

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

        # Output to output causation
        if cause_node[0] == "Y" and effect_node[0] == "Y":

            # Swap order if the cause appears after the effect in the source code
            if output_order.index(effect_node) < output_order.index(cause_node):
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


def to_dot(dag: nx.DiGraph, out_path: str, **kwargs):
    """Save DAG as a DOT file at the specified out path.

    :param dag: DAG to save as DOT.
    :param out_path: Path to which the DOT file will be saved.
    *kwargs: Additional keyword arguments
    """
    with safe_open_w(out_path) as dag_file:
        dot_dag = to_pydot(dag)
        dot_dag.set_comment(json.dumps(kwargs))
        dot_dag = dot_dag.to_string()
        dot_dag = dot_dag[:-3] + "}"  # Fixes networkx bug that adds newline to nodes
        dag_file.write(dot_dag)


def get_output_order(causal_dag: nx.DiGraph):
    """Gets the order of the outputs as they appear in the source code.

       The source code for a causal DAG is generated bottom-up, starting
       from the terminal output nodes (those with no further effects/
       outgoing edges) before progressing to the intermediate output
       nodes. Within each set of nodes, the order is determined by
       the node index.

       :param causal_dag: Causal DAG to obtain the output order of.
       :return outputs: A list of outputs in the order they appear
       in the source code.
    """
    output_nodes = [
        node for node in causal_dag if "Y" in node
    ]

    # The final lines of the file should handle the terminal output nodes
    terminal_output_nodes = [
        node for node in output_nodes if not causal_dag.out_degree(node)
    ]

    intermediate_output_nodes = [
        node for node in output_nodes if causal_dag.out_degree(node) > 0
    ]

    # Sort both terminal and intermediate outputs in descending order and combine
    # to form a list of [intermediate_outputs, terminal_outputs]
    sorted_terminal_output_nodes = sort_causal_dag_nodes(terminal_output_nodes, True)
    sorted_intermediate_output_nodes = sort_causal_dag_nodes(
        intermediate_output_nodes, True
    )

    nodes_in_source_code_order = (sorted_terminal_output_nodes + sorted_intermediate_output_nodes)
    nodes_in_source_code_order.reverse()
    return nodes_in_source_code_order


def sort_causal_dag_nodes(nodes: List, reverse: bool = False) -> List:
    """Sort a list of causal DAG nodes based on the numerical value only (i.e. not the X or Y in front).

    This method assumes that all nodes start with a single character and are strictly followed by integers.

    :param nodes: A list of strings representing nodes.
    :param reverse: Whether to reverse the order (i.e. descending order).
    :return:
    """
    nodes.sort(key=lambda node: int(node[1:]), reverse=reverse)
    return nodes
