"""A script for generating TOML mutation configuration files for the cosmic-ray python mutation testing library."""
import networkx as nx
import tomlkit
from tomlkit import aot, inline_table, nl, table, document, array
from helpers import safe_open_w
from dags.dag_utils import get_non_causal_node_pairs


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
    non_causal_node_pairs = get_non_causal_node_pairs(dag)
    for non_causal_node_pair in non_causal_node_pairs:
        cause_variable, effect_variable = non_causal_node_pair
        edge_addition_mutations.append({'cause_variable': cause_variable,
                                        'effect_variable': effect_variable})

    toml_document = document()

    # Add cosmic-ray table
    cosmic_ray_table = table()
    cosmic_ray_table.add("module-path", "../../../program.py")
    cosmic_ray_table.add("timeout", 20.0)
    cosmic_ray_table.add("excluded-modules", [])
    cosmic_ray_table.add("test-command", "python ../../../../../../programs/program_testing.py -p ../../../program.py -d ../DAG.dot -c -t 1")
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

    print(f"Generated {len(edge_addition_mutations)} VariableInserter mutations.")
    print(f"Generated {len(edge_deletion_mutations)} VariableReplacer mutations.")
