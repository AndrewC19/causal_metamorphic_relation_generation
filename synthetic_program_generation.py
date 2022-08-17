import operator
import networkx as nx
import random
from deap.gp import PrimitiveSet, PrimitiveTree, genFull, generate
from dag_generation import generate_dag
from typing import List


def generate_program(causal_dag: nx.DiGraph,
                     program_name: str):
    print(causal_dag.edges)
    input_nodes = [node for node in causal_dag.nodes if 'X' in node]
    output_nodes = [node for node in causal_dag.nodes if 'Y' in node]
    terminal_output_nodes = [node for node in output_nodes if not causal_dag.out_degree(node)]
    intermediate_output_nodes = [node for node in output_nodes if causal_dag.out_degree(node) > 0]

    # Sort input and output nodes in ascending order
    sorted_input_nodes = sort_causal_dag_nodes(input_nodes, False)
    sorted_output_nodes = sort_causal_dag_nodes(output_nodes, False)

    # Split outputs into terminal and intermediate nodes and order in descending order for traversal
    sorted_terminal_output_nodes = sort_causal_dag_nodes(terminal_output_nodes, True)
    sorted_intermediate_output_nodes = sort_causal_dag_nodes(intermediate_output_nodes, True)
    nodes_ordered_for_traversal = sorted_terminal_output_nodes + sorted_intermediate_output_nodes


    statement_stack = []
    for output_node in nodes_ordered_for_traversal:

        causes = [cause for (cause, effect) in causal_dag.in_edges(output_node)]

        # Construct a syntax tree representing the program
        pset = PrimitiveSet("dag_implementation", len(causes))

        # Add primitives of choice
        pset.addPrimitive(operator.add, 2)
        pset.addPrimitive(operator.mul, 2)
        pset.addPrimitive(operator.sub, 2)
        pset.addPrimitive(operator.truediv, 2)
        pset.addPrimitive(operator.pow, 2)

        # Convert variable names to those in DAG
        cause_map = {f"ARG{i}": c for i, c in enumerate(causes)}
        pset.renameArguments(**cause_map)

        # TODO: Find a way to ensure that all causes are in the tree
        expr = genFull(pset, min_=1, max_=2)
        statement_tree = PrimitiveTree(expr)

        # Add function to stack
        statement_stack.append((output_node, str(statement_tree)))

    print(statement_stack)

    # Write the program
    imports_str = "from operator import add, mul, sub, truediv, pow\n\n\n"
    input_args_str = "".join([f"\t{x}: int,\n" for x in sorted_input_nodes])
    method_definition_str = f"def {program_name}(\n{input_args_str}):\n"
    doc_str = '\t"""Causal structure:\n'
    doc_str += "".join([f"\t\t{edge}\n" for edge in causal_dag.edges])
    doc_str += '\t"""\n'
    return_str = "\treturn " + "".join([f"{y}, " for y in sorted_output_nodes])[:-2] + "\n"
    statement_stack.reverse()  # Reverse the stack of syntax trees to be in order of execution (later outputs last)
    program_statements = [f"\t{output} = {statement}\n" for output, statement in statement_stack]

    with open(f"./synthetic_programs/{program_name}.py", "w") as program_file:
        program_file.write(imports_str)
        program_file.write(method_definition_str)
        program_file.write(doc_str)
        program_file.writelines(program_statements)
        program_file.write(return_str)


def sort_causal_dag_nodes(nodes: List,
                          reverse: bool = False) -> List:
    nodes.sort(key=lambda node: int(node[1:]), reverse=reverse)
    return nodes


if __name__ == "__main__":
    causal_dag = generate_dag(5, 0.5, seed=3)
    program = generate_program(causal_dag, "synthetic_program")
