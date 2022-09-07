"""Functions for generating metamorphic relations from a causal DAG."""
import networkx as nx
from itertools import combinations
from metamorphic_relation import ShouldCause, ShouldNotCause
from dag_generation import generate_dag


def generate_metamorphic_relations(dag: nx.DiGraph):
    """Generate a list of metamorphic relations based on the structure of a causal DAG."""
    assert nx.is_directed_acyclic_graph(dag), "Error: Graph is not a DAG."
    metamorphic_relations = []

    # Iterate over all unique pairs of variables in the DAG
    unique_node_pairs = list(combinations(dag.nodes, 2))
    for node_pair in unique_node_pairs:
        cause, effect = node_pair

        # Adjust for the parents of the cause and effect to isolate the hypothesised causal effect of interest
        adjustment_set = set(dag.predecessors(cause)) | set(dag.predecessors(effect))

        # Confirm that adjustment set satisfies d-separation
        assert nx.d_separated(dag, {cause}, {effect}, adjustment_set), \
               f"{adjustment_set} does not d-separate {cause} and {effect} "

        # Where an edge is present, test for causality, otherwise test for independence
        if (cause, effect) in dag.edges:
            metamorphic_relations.append(ShouldCause(cause, effect, list(adjustment_set), dag))
        elif (effect, cause) in dag.edges:
            metamorphic_relations.append(ShouldCause(effect, cause, list(adjustment_set), dag))
        else:
            metamorphic_relations.append(ShouldNotCause(cause, effect, list(adjustment_set), dag))

    # Confirm that a single MR is produced for each unique node pair in the DAG
    assert len(metamorphic_relations) == len(unique_node_pairs), \
           f"Mismatch between number of generated MRs and unique node pairs."

    return metamorphic_relations


if __name__ == "__main__":
    causal_dag = generate_dag(20, 1)
    causal_dag_metamorphic_relations = generate_metamorphic_relations(causal_dag)
    print(causal_dag_metamorphic_relations)
