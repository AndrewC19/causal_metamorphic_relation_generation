import operator
import networkx as nx
import pyparsing as pp
import random
import re
import os
from deap.gp import (
    PrimitiveSet,
    PrimitiveTree,
    genFull,
    Terminal,
    cxOnePoint,
    mutUniform,
)
from deap import creator, base, tools, algorithms
from dag_generation import generate_dag
from typing import List, Iterable
from math import ceil


def generate_program(
    causal_dag: nx.DiGraph,
    target_directory_path: str = "./synthetic_programs",
    program_name: str = "synthetic_program",
):
    """Generate an arithmetic python program with the same causal structure as the provided causal DAG.

    :param causal_dag: A networkx graph representing a causal DAG. This DAG will be used to produce a python program
                       with the same causal structure.
    :param target_directory_path: The path of the directory to which the program will be saved.
    :param program_name: The name the program will be saved as (excluding the .py extension).
    """
    input_nodes = [node for node in causal_dag.nodes if "X" in node]
    output_nodes = [node for node in causal_dag.nodes if "Y" in node]

    # Sort input and output nodes in ascending order
    sorted_input_nodes = sort_causal_dag_nodes(input_nodes, False)
    sorted_output_nodes = sort_causal_dag_nodes(output_nodes, False)

    # Use GP to construct a series of statements (program) with the same causal structure as the DAG
    statement_stack = construct_statement_stack_from_outputs_and_dag(
        output_nodes, causal_dag
    )

    # Write the program
    write_statement_stack_to_python_file(
        statement_stack,
        sorted_input_nodes,
        sorted_output_nodes,
        causal_dag,
        target_directory_path,
        program_name,
    )


def sort_causal_dag_nodes(nodes: List, reverse: bool = False) -> List:
    """Sort a list of causal DAG nodes based on the numerical value only (i.e. not the X or Y in front).

    This method assumes that all nodes start with a single character and are strictly followed by integers.

    :param nodes: A list of strings representing nodes.
    :param reverse: Whether to reverse the order (i.e. descending order).
    :return:
    """
    nodes.sort(key=lambda node: int(node[1:]), reverse=reverse)
    return nodes


def construct_statement_stack_from_outputs_and_dag(
    output_nodes: List, causal_dag: nx.DiGraph, constants_ratio: float = 0.2
):
    """Construct a stack of statements for each output in the causal DAG, with the same causal structure.

    This function iterates over the outputs in the causal DAG and uses GP to construct an arithmetic function
    (referred to as a statement herein) with the same causal structure. For example, for {X1, X2} --> Y, suitable
    functions include Y = add(X1, X2) and Y = sub(X2, X1).

    Our algorithm starts by constructing statements for terminal outputs and then proceeds to intermediate outputs.
    This results in a stack of statements that, upon reversal, can be piped into a python file to form the body of an
    executable function with the same causal structure as the specified causal DAG.

    Our GP uses a fitness function that ensures all solutions (statements) are affected by all causes (i.e. every cause
    of the output is in the statement). In addition, the fitness function prioritises solutions with the shortest
    chain of operators and values.

    :param output_nodes: A list of outputs that appear in the causal DAG.
    :param causal_dag: A networkx DiGraph representing a causal DAG from which the structure of the program will be
                       inferred.
    :param constants_ratio: Ratio of constants to variables to add to target (0.2 by default).
    :return: A list of syntax trees (PrimitiveTrees) representing statements that can be executed in python.
    """
    terminal_output_nodes = [
        node for node in output_nodes if not causal_dag.out_degree(node)
    ]
    intermediate_output_nodes = [
        node for node in output_nodes if causal_dag.out_degree(node) > 0
    ]

    # Split outputs into terminal and intermediate nodes and order in descending order for traversal
    sorted_terminal_output_nodes = sort_causal_dag_nodes(terminal_output_nodes, True)
    sorted_intermediate_output_nodes = sort_causal_dag_nodes(
        intermediate_output_nodes, True
    )
    nodes_ordered_for_traversal = (
        sorted_terminal_output_nodes + sorted_intermediate_output_nodes
    )
    statement_stack = []
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    for output_node in nodes_ordered_for_traversal:
        causes = [cause for (cause, effect) in causal_dag.in_edges(output_node)]

        # Construct a syntax tree representing the program
        pset = PrimitiveSet("dag_implementation", len(causes))

        # Add primitives of choice
        pset.addPrimitive(operator.add, 2)
        pset.addPrimitive(operator.mul, 2)
        pset.addPrimitive(operator.sub, 2)

        # Add random (non-zero) constants (such that there is a ~ 1:5 ratio between constants and variables)
        for x in range(ceil(constants_ratio * len(causes))):
            pset.addEphemeralConstant(
                f"negative_const_{output_node}_{x}_{random.randint(-10000, 10000)}",
                lambda: random.randint(-50, -1),
            )
            pset.addEphemeralConstant(
                f"positive_const_{output_node}_{x}_{random.randint(-10000, 10000)}",
                lambda: random.randint(1, 50),
            )

        # Convert variable names to those in DAG
        cause_map = {f"ARG{i}": c for i, c in enumerate(causes)}
        pset.renameArguments(**cause_map)

        # Create the individual comprising the allowed set of primitives (+, *, -, **)
        creator.create(
            "Individual", PrimitiveTree, fitness=creator.FitnessMin, pset=pset
        )

        # Grow trees with a depth bounded by [(#causes/2)+1, #causes] -- this follows from the fact that our primitives
        # are all binary (take two args). Hence, to ensure all causes are included in the function, the tree must have
        # at least causes/2 binary primitives, requiring a depth of the same value. # TODO: Check this.
        toolbox = base.Toolbox()
        toolbox.register(
            "expr",
            genFull,
            pset=pset,
            min_=int(len(causes) / 2) + 1,
            max_=int(len(causes)),
        )

        # Register parameters for evolution: individual, population, selection, mate, mutations
        toolbox.register(
            "individual", tools.initIterate, creator.Individual, toolbox.expr
        )
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register(
            "evaluate", synthetic_statement_fitness, causes=causes, pset=pset
        )
        toolbox.register("select", tools.selTournament, tournsize=3)
        toolbox.register("mate", cxOnePoint)
        toolbox.register("expr_mut", genFull, min_=1, max_=2)
        toolbox.register("mutate", mutUniform, expr=toolbox.expr_mut, pset=pset)

        # Create the population and hall of fame to store the best solution
        pop = toolbox.population(n=1000)
        hof = tools.HallOfFame(1)

        # Run the evolutionary algorithm and select the best solution
        _, _ = algorithms.eaSimple(
            pop, toolbox, 0.5, 0.1, 40, halloffame=hof, verbose=False
        )
        statement_stack.append((output_node, PrimitiveTree(hof[0])))
    return statement_stack


def synthetic_statement_fitness(individual, causes, pset):
    """A good statement is one that includes all of its causes, is short, and does not contain self subtraction.

    :param individual: A syntax tree representing the statement.
    :param causes: A list of the causes that must feature in the statement.
    :param pset: A PrimitiveSet used to generate the individual.
    :return: A float representing the fitness value.
    """
    causes_in_statement = []
    for node in individual:
        if isinstance(node, Terminal):
            causes_in_statement.append(node)

    causes = [pset.mapping[cause] for cause in causes]
    missing_causes = [cause for cause in causes if cause not in causes_in_statement]

    # Remove solutions that do not contain all causes
    if missing_causes:
        return (1.0,)

    # Remove solutions that include self subtraction
    if contains_self_subtraction(individual):
        return (1.0,)

    # We want the smallest statement that contains all variables
    return (1.0 - (1.0 / len(causes_in_statement)),)


def contains_self_subtraction(statement):
    subtract_parameters = re.search(r"sub\((\b\w  +\b),\s(\b\1\b)\)", str(statement))
    if subtract_parameters:
        return True


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
    method_definition_str = f"def {program_name}(\n{input_args_str}):\n"
    doc_str = '\t"""Causal structure:\n'
    doc_str += "".join([f"\t\t{edge}\n" for edge in causal_dag.edges])
    doc_str += '\t"""\n'
    return_str = (
        "\treturn " + "".join([f"{y}, " for y in sorted_output_nodes])[:-2] + "\n"
    )
    statement_stack.reverse()  # Reverse the stack of syntax trees to be in order of execution (later outputs last)
    formatted_program_statements = format_program_statements(statement_stack)

    with safe_open_w(
        os.path.join(target_directory_path, f"{program_name}.py")
    ) as program_file:
        program_file.write(method_definition_str)
        program_file.write(doc_str)
        program_file.writelines(formatted_program_statements)
        program_file.write(return_str)


def format_program_statements(program_statements):
    """Convert a list of arithmetic program statements from prefix to infix notation.

    For example:
        (1) [mul(5, Y3), mul(add(X2, X2), add(-8, X3))] --> [5*Y3, (X2+X2)*(-8+X3)]
        (2) [add(X1, X1), sub(mul(Y3, -4), sub(Y4, -4))] --> [X1+X1, (Y3*-4)-(Y4--4)]

    :param program_statements: A list of strings representing arithmetic statements in prefix form.
    :return: A list of strings representing equivalent arithmetic statements in infix form.
    """
    content = pp.Word(pp.alphanums) | "add" | "mul" | "sub" | "," | "-"
    identifier = pp.Word("_" + pp.alphas, "_" + pp.alphanums)
    parens = identifier("name") + pp.nestedExpr("(", ")", content=content)
    formatted_program_statements = []
    for output, program_statement in program_statements:
        program_statement = parens.parseString(str(program_statement)).asList()
        formatted_program_statement = prefix_statement_list_to_infix(program_statement)
        formatted_program_statements.append(
            f"\t{output} = {formatted_program_statement}\n"
        )
    return formatted_program_statements


def prefix_statement_list_to_infix(statement_list):
    """Convert an arithmetic program statement (in nested list format) from prefix to infix notation.

    For example:
        (1) ['mul', ['5', ',', 'Y3']] --> 5*Y3
        (2) ['mul', ['add', ['X2', ',', 'X2'], ',', 'add', ['-', '8', ',', 'X3']]] --> (X2+X2)*(-8+X3)

    :param statement_list: An arithmetic statement in prefix form specified as a nested list.
    :return: A string representing an equivalent arithmetic statement in infix form.
    """
    statement_str = ""

    # Base case: bottom level list or terminal
    if does_not_contain_list(statement_list):
        return "".join(statement_list)

    # Case 1: top level function and its parameters
    elif len(statement_list) == 2:
        functor = statement_list[0]
        args = statement_list[1]

        if functor == "add":
            replacement_operator = "+"
        elif functor == "sub":
            replacement_operator = "-"
        elif functor == "mul":
            replacement_operator = "*"
        else:
            replacement_operator = "/"
        return f"{prefix_statement_list_to_infix(args)}".replace(
            ",", replacement_operator
        )

    # Case 2: more than one function
    else:
        delimiter_index = statement_list.index(",")
        left_args = statement_list[:delimiter_index]
        right_args = statement_list[delimiter_index + 1 :]
        left_results = prefix_statement_list_to_infix(left_args)
        right_results = prefix_statement_list_to_infix(right_args)

        # If the result is not a terminal, enclose in brackets
        operators = ["+", "-", "*"]
        if any(operator_ in left_results for operator_ in operators):
            left_results = f"({left_results})"
        if any(operator_ in right_results for operator_ in operators):
            right_results = f"({right_results})"

    return f"{left_results},{right_results}"


def does_not_contain_list(x):
    if not isinstance(x, Iterable):
        return True

    for item in x:
        if isinstance(item, list):
            return False
    return True


def safe_open_w(path):
    """Open path for writing and create directories if they do not exist.

    Original implementation: https://stackoverflow.com/questions/23793987/write-file-to-a-directory-that-doesnt-exist
    Author: Jonathon Reinhart

    :param path: A path to the target directory. This may not exist yet.
    :return: An open path to be written to.
    """

    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, "w")


if __name__ == "__main__":
    dag = generate_dag(15, 0.2)
    generate_program(dag, target_directory_path="./evaluation/", program_name="program")
