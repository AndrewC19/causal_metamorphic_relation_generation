import operator
import networkx as nx
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
from typing import List


def generate_program(causal_dag: nx.DiGraph, program_name: str):
    """Generate an arithmetic python program with the same causal structure as the provided causal DAG.

    :param causal_dag: A networkx graph representing a causal DAG. This DAG will be used to produce a python program
                       with the same causal structure.
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
    output_nodes: List, causal_dag: nx.DiGraph
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

        # Convert variable names to those in DAG
        cause_map = {f"ARG{i}": c for i, c in enumerate(causes)}
        pset.renameArguments(**cause_map)

        # Create the individual comprising the allowed set of primitives (+, *, -, **)
        creator.create(
            "Individual", PrimitiveTree, fitness=creator.FitnessMin, pset=pset
        )

        # Grow trees with a depth bounded by [(#causes/2)+1, #causes] -- this follows from the fact that our primitives
        # are all binary (take two args). Hence, to ensure all causes are included in the function, the tree must have
        # at least causes/2 primitives.
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
        toolbox.register("expr_mut", genFull, min_=0, max_=2)
        toolbox.register("mutate", mutUniform, expr=toolbox.expr_mut, pset=pset)

        # Create the population and hall of fame to store the best solution
        pop = toolbox.population(n=10)
        hof = tools.HallOfFame(1)

        # Run the evolutionary algorithm and select the best solution
        _, _ = algorithms.eaSimple(
            pop, toolbox, 0.5, 0.1, 40, halloffame=hof, verbose=True
        )
        print(f"{output_node} is caused by: {causes}")
        statement_stack.append((output_node, PrimitiveTree(hof[0])))
    return statement_stack


def synthetic_statement_fitness(individual, causes, pset):
    """A good statement is one that includes all of its causes.

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
    if not missing_causes:
        return (0.0,)
    else:
        # We want the smallest statement that contains all variables
        return (1.0 / len(causes_in_statement),)


def write_statement_stack_to_python_file(
    statement_stack, sorted_input_nodes, sorted_output_nodes, causal_dag, program_name
):
    """Convert a statement stack to a python program and save under the synthetic_programs directory.

    :param statement_stack: A list of syntax trees that can be executed in python.
    :param sorted_input_nodes: A list of inputs sorted in ascending numerical order (i.e. X1, X2, X3 ...)
    :param sorted_output_nodes: A list of outputs sorted in ascending numerical order (i.e. Y1, Y2, Y3 ...)
    :param causal_dag: The causal DAG whose structure the program should match.
    :param program_name: A name for the generated python file (excluding the .py extension).
    """
    imports_str = "from operator import add, mul, sub\n\n\n"
    input_args_str = "".join([f"\t{x}: int,\n" for x in sorted_input_nodes])
    method_definition_str = f"def {program_name}(\n{input_args_str}):\n"
    doc_str = '\t"""Causal structure:\n'
    doc_str += "".join([f"\t\t{edge}\n" for edge in causal_dag.edges])
    doc_str += '\t"""\n'
    return_str = (
        "\treturn " + "".join([f"{y}, " for y in sorted_output_nodes])[:-2] + "\n"
    )
    statement_stack.reverse()  # Reverse the stack of syntax trees to be in order of execution (later outputs last)
    program_statements = [
        f"\t{output} = {statement}\n" for output, statement in statement_stack
    ]

    with open(f"./synthetic_programs/{program_name}.py", "w") as program_file:
        program_file.write(imports_str)
        program_file.write(method_definition_str)
        program_file.write(doc_str)
        program_file.writelines(program_statements)
        program_file.write(return_str)


if __name__ == "__main__":
    dag = generate_dag(15, 0.2)
    generate_program(dag, "synthetic_program")
