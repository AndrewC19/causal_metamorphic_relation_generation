"""A script for generating TOML mutation configuration files for the cosmic-ray python mutation testing library."""
import toml
import networkx as nx
import tomlkit

from dag_generation import generate_dag
from itertools import combinations
from helpers import safe_open_w
from pprint import pprint
from tomlkit import aot, inline_table, nl, table, document, array


def generate_causal_mutation_config(dag: nx.DiGraph, target_directory_path: str):
    """Generate a TOML configuration file listing causal mutations for the specified causal DAG.

    :param dag: A networkx directed graph representing a causal DAG.
    :param target_directory_path: The path to which the mutation config will be saved.
    """
    edge_deletion_mutations = []
    for edge in dag.edges:
        cause_variable, effect_variable = edge
        edge_deletion_mutations.append({'cause_variable': cause_variable,
                                        'effect_variable': effect_variable})

    edge_addition_mutations = []
    non_causal_node_pairs = _get_non_causal_node_pairs(dag)
    for non_causal_node_pair in non_causal_node_pairs:
        cause_variable, effect_variable = non_causal_node_pair
        edge_addition_mutations.append({'cause_variable': cause_variable,
                                        'effect_variable': effect_variable})

    toml_document = document()

    # Add cosmic-ray table
    cosmic_ray_table = table()
    cosmic_ray_table.add("module-path", "program.py")
    cosmic_ray_table.add("timeout", 20.0)
    cosmic_ray_table.add("excluded-modules", [])
    cosmic_ray_table.add("test-command", "pytest test_program.py")
    toml_document.add("cosmic-ray", cosmic_ray_table)
    toml_document.add(nl())

    # Add distributor table
    distributor_table = table()
    distributor_table.add("name", "local")
    cosmic_ray_table.add("distributor", distributor_table)
    toml_document.add(nl())

    # Add operators array of tables
    operators_array_of_tables = aot()

    # VariableReplacer (delete causal edges)
    variable_replacer_table = table()
    variable_replacer_table.add("name", "core/VariableReplacer")
    variable_replacer_args_array = array()
    for edge in edge_deletion_mutations:
        arg_inline_table = inline_table()
        arg_inline_table.update(edge)
        variable_replacer_args_array.append(arg_inline_table)
    variable_replacer_table.add("args", variable_replacer_args_array)
    operators_array_of_tables.append(variable_replacer_table)

    # VariableInserter (add causal edges)
    variable_inserter_table = table()
    variable_inserter_table.add("name", "core/VariableInserter")
    variable_inserter_args_array = array()
    for edge in edge_addition_mutations:
        arg_inline_table = inline_table()
        arg_inline_table.update(edge)
        variable_inserter_args_array.append(arg_inline_table)
    variable_inserter_table.add("args", variable_inserter_args_array)
    operators_array_of_tables.append(variable_inserter_table)

    # Add operators array of tables to cosmic-ray table
    cosmic_ray_table.add("operators", operators_array_of_tables)

    with safe_open_w(target_directory_path) as toml_file:
        tomlkit.dump(toml_document, toml_file)


def _get_non_causal_node_pairs(dag: nx.DiGraph):
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
        if cause_node[0] == "Y" and effect_node[0] == "Y" and (cause_node[1] > effect_node[1]):
            continue

        valid_non_causal_node_pairs.append(pair)

    return valid_non_causal_node_pairs


if __name__ == "__main__":
    dag = generate_dag(10, 0.2)
    dag_edges = _get_non_causal_node_pairs(dag)
    dag.add_edges_from(dag_edges)
    print(nx.is_directed_acyclic_graph(dag))
