import networkx as nx
import random
import os
import ast
import mccabe as mc
from dags.dag_generation import generate_dag
from dags.dag_utils import sort_causal_dag_nodes, get_output_order
from typing import Iterable
from helpers import safe_open_w
from time import time


def generate_program(
        causal_dag: nx.DiGraph,
        p_conditional: float = 0.0,
        target_directory_path: str = "./synthetic_programs",
        program_name: str = "synthetic_program"
):
    """Generate an arithmetic python program with the same causal structure as the provided causal DAG.

    :param causal_dag: A networkx graph representing a causal DAG. This DAG will be used to produce a python program
                       with the same causal structure.
    :param p_conditional: Probability that an arbitrary node is made conditional. This will be used to create an if
                          statement.
    :param target_directory_path: The path of the directory to which the program will be saved.
    :param program_name: The name the program will be saved as (excluding the .py extension).
    """
    random.seed(0)

    # With p_conditional probability, convert all non-terminal nodes to conditional type
    nodes_with_types = {}
    for node in causal_dag.nodes:
        n_type = "numerical"
        if (causal_dag.out_degree(node) > 0) and (random.random() < p_conditional):
            n_type = "conditional"
        nodes_with_types[node] = {"n_type": n_type}
    nx.set_node_attributes(causal_dag, nodes_with_types)

    input_nodes = [node for node in causal_dag.nodes if "X" in node]
    output_nodes = [node for node in causal_dag.nodes if "Y" in node]

    # Sort input and output nodes in ascending order
    sorted_input_nodes = sort_causal_dag_nodes(input_nodes, False)
    sorted_output_nodes = sort_causal_dag_nodes(output_nodes, False)

    # Construct a series of statements (program) with the same causal structure as the DAG
    pg_start_time = time()
    statement_stack = construct_statement_stack_from_dag(causal_dag)
    pg_end_time = time()
    print(f"Program Generation Time: {pg_end_time - pg_start_time}s")

    # Write the program
    format_start_time = time()
    write_statement_stack_to_python_file(
        statement_stack,
        sorted_input_nodes,
        sorted_output_nodes,
        causal_dag,
        target_directory_path,
        program_name,
    )
    format_end_time = time()
    print(f"Format time: {format_end_time - format_start_time}s")
    program_path = os.path.join(target_directory_path, f"{program_name}.py")

    # Compute the McCabe complexity: we subtract number of outputs since each computation
    # has a superfluous if statement that allows us to directly intervene on output values
    mccabe_complexity = get_mccabe_complexity(program_path) - len(output_nodes)
    print(f"McCabe complexity: {mccabe_complexity}")


def construct_statement_stack_from_dag(causal_dag: nx.DiGraph):
    """Construct a stack of statements for each output in the causal DAG, with the same causal structure.

    This function iterates over the outputs in the causal DAG and constructs linear arithmetic functions with the same
    causal structure (referred to as a statement herein). For example, for {X1, X2} --> Y ==> Y = (2*X1) + (-4*X2) + 10.

    Our algorithm starts by constructing statements for terminal outputs and then proceeds to intermediate outputs.
    This results in a stack of statements that, upon reversal, can be piped into a python file to form the body of an
    executable function with the same causal structure as the specified causal DAG.

    :param causal_dag: A networkx DiGraph representing a causal DAG from which the structure of the program will be
                       generated.
    :return: A list of strings representing statements that can be executed in python.
    """
    nodes_ordered_for_traversal = get_output_order(causal_dag)
    nodes_ordered_for_traversal.reverse()
    statement_stack = []

    for output_node in nodes_ordered_for_traversal:
        # Construct a linear equation for each node based on its causes
        causes = [cause for (cause, effect) in causal_dag.in_edges(output_node)]
        coefficients = [random.choice([random.randint(1, 10), random.randint(-10, -1)]) for _ in causes]
        expr = " + ".join([f"({c} * {x})" for c, x in zip(coefficients, causes)])
        expr += f" + {random.choice([random.randint(0, 10), random.randint(-10, 0)])}"

        # Add if not none before each output statement for controllability
        statement = f"\tif {output_node} is None:\n"
        conditional_parents = [cause for cause in causes if causal_dag.nodes[cause]["n_type"] == "conditional"]

        # Add conditional behaviour for conditional nodes
        if conditional_parents:
            # Place the linear equation within an if statement whose predicate is a function of all conditional causes
            predicate = " + ".join([f"{x}" for x in conditional_parents]) + " >= 0"

            # In the true branch (if), place the full linear equation
            statement += f"\t\tif {predicate}:\n"
            statement += f"\t\t\t{output_node} = {expr}\n"

            # In the false branch (else), place the linear equation without the non-conditional parents
            else_expr = " + ".join([f"({c} * {x})" for c, x in zip(coefficients, conditional_parents)])
            else_expr += f" + {random.choice([random.randint(0, 10), random.randint(-10, 0)])}"
            statement += f"\t\telse:\n"
            statement += f"\t\t\t{output_node} = {else_expr}\n"

        else:
            # No conditional parents so no if-then-else
            statement += f"\t\t{output_node} = {expr}\n"
        statement_stack.append(statement)

    return statement_stack


def write_statement_stack_to_python_file(
        statement_stack,
        sorted_input_nodes,
        sorted_output_nodes,
        causal_dag,
        target_directory_path,
        program_name,
):
    """Convert a statement stack to a python program and save under the synthetic_programs directory.

    :param statement_stack: A list of syntax trees that can be executed in python.
    :param sorted_input_nodes: A list of inputs sorted in ascending numerical order (i.e. X1, X2, X3 ...)
    :param sorted_output_nodes: A list of outputs sorted in ascending numerical order (i.e. Y1, Y2, Y3 ...)
    :param causal_dag: The causal DAG whose structure the program should match.
    :param target_directory_path: The directory to which the program will be saved.
    :param program_name: A name for the generated python file (excluding the .py extension).
    """
    input_args_str = "".join([f"\t{x}: int,\n" for x in sorted_input_nodes])
    input_args_str += "".join([f"\t{x}: int = None,\n" for x in sorted_output_nodes])
    method_definition_str = f"def {program_name}(\n{input_args_str}):\n"
    doc_str = '\t"""Causal structure:\n'
    doc_str += "".join([f"\t\t{edge}\n" for edge in causal_dag.edges])
    doc_str += '\t"""\n'
    return_str = (
            "\treturn {" + "".join([f"'{y}': {y}, " for y in sorted_output_nodes])[:-2] + "}\n"
    )
    statement_stack.reverse()  # Reverse the stack of syntax trees to be in order of execution (later outputs last)
    with safe_open_w(
            os.path.join(target_directory_path, f"{program_name}.py")
    ) as program_file:
        program_file.write(method_definition_str)
        program_file.write(doc_str)
        program_file.writelines(statement_stack)
        program_file.write(return_str)


def does_not_contain_list(x):
    if not isinstance(x, Iterable):
        return True

    for item in x:
        if isinstance(item, list):
            return False
    return True


def get_mccabe_complexity(program_path):
    """Get McCabe complexity for a program using Ned's script: https://github.com/PyCQA/mccabe.

    :param program_path: Path to the python program whose complexity we wish to measure.
    :return: McCabe complexity score for the program.
    """
    code = mc._read(program_path)
    tree = compile(code, program_path, "exec", ast.PyCF_ONLY_AST)
    visitor = mc.PathGraphingAstVisitor()
    visitor.preorder(tree, visitor)
    program_name = os.path.basename(program_path)[:-3]
    return visitor.graphs[program_name].complexity()


if __name__ == "__main__":
    dag = generate_dag(5, 0.3)
    generate_program(dag, 0.67, target_directory_path="../evaluation/", program_name="test_program")
