"""Functions for generating metamorphic relations from a causal DAG."""
import networkx as nx
from itertools import combinations
from metamorphic_relation import ShouldCause, ShouldNotCause
from dag_generation import generate_dag


def generate_metamorphic_relations(dag: nx.DiGraph):
    """Generate a list of metamorphic relations based on the structure of a causal DAG."""
    assert nx.is_directed_acyclic_graph(dag), "Error: Graph is not a DAG."
    metamorphic_relations = []

    print(dag.edges)

    # Iterate over all unique pairs of variables in the DAG
    unique_node_pairs = list(combinations(dag.nodes, 2))
    for node_pair in unique_node_pairs:
        cause, effect = node_pair

        # Do not check causality or independence amongst inputs
        if "X" in cause and "X" in effect:
            continue

        # Adjust for the parents of the cause and effect to isolate the hypothesised causal effect of interest
        adjustment_set = set(dag.predecessors(cause)) | set(dag.predecessors(effect))

        # Confirm that adjustment set satisfies d-separation
        assert nx.d_separated(dag, {cause}, {effect}, adjustment_set), \
               f"{adjustment_set} does not d-separate {cause} and {effect} "

        # Where an edge is present, test for causality, otherwise test for independence
        if (cause, effect) in dag.edges:
            adjustment_set -= {cause}  # Remove the cause from adjustment set, where cause --> effect
            metamorphic_relations.append(ShouldCause(cause, effect, list(adjustment_set - {cause}), dag))
        elif (effect, cause) in dag.edges:
            adjustment_set -= {effect}  # Remove the effect from adjustment set, where effect --> cause
            metamorphic_relations.append(ShouldCause(effect, cause, list(adjustment_set - {effect}), dag))
        else:
            cause, effect = sort_node_pair(cause, effect)
            metamorphic_relations.append(ShouldNotCause(cause, effect, list(adjustment_set), dag))

    return metamorphic_relations


def sort_node_pair(node_a, node_b):
    """Sort a pair of nodes such that inputs (X) precede outputs (Y), and lower nodes (X1) precede higher nodes (X2)."""

    # Case 1: (Y, X) --> (X, Y)
    if ("Y" in node_a) and ("X" in node_b):
        return node_b, node_a

    # Case 2: (X2, X1) --> (X1, X2) or (Y2, Y1) --> (Y1, Y2)
    if (node_a[0] == node_b[0]) and (int(node_a[1:]) > int(node_b[1:])):
        return node_b, node_a

    return node_a, node_b


if __name__ == "__main__":
    causal_dag = generate_dag(20, 1)
    causal_dag_metamorphic_relations = generate_metamorphic_relations(causal_dag)
    print(causal_dag_metamorphic_relations)
