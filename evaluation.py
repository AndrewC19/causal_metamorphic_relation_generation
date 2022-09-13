import os.path
import random
import glob
import networkx as nx
import importlib.util
import sys
import shutil
from time import time
from argparse import ArgumentParser
from dag_generation import generate_dag, mutate_dag
from program_generation import generate_program
from metamorphic_relation_generation import generate_metamorphic_relations
from mutation_config_generation import generate_causal_mutation_config
from helpers import safe_open_w
from dag_utils import structural_hamming_distance


def generate_experiment(
    n_dags: int,
    n_nodes: int,
    p_edge: float,
    p_conditional: float,
    experiment_directory_path: str = "./evaluation/experiment/",
    seed: int = 0
):
    """Generate an experiment with user specified DAGs.

    The resulting programs will be saved in the evaluation directory (one will
    be created if it does not already exist). Within this directory, a
    subdirectory with the experiment name will be produced. The details of the
    generated DAGs and experiments will be stored in params.txt.

    :param n_dags: Number of DAGs to generate.
    :param n_nodes: Number of nodes per DAG.
    :param p_edge: Probability of an edge being added between any two nodes.
    :param p_conditional: Probability of a node being made conditional.
    :param experiment_directory_path: A string denoting the name of the experiment.
    :param seed: Seed for reproducibility.
    """
    params_path = f"{experiment_directory_path}/params.txt"
    random.seed(seed)
    total_edges = 0
    total_nodes = 0

    for n in range(n_dags):
        # Set seed
        seed = random.randint(1, 100000)
        random.seed(seed)
        print(seed)
        # Create custom paths for experiment components
        seed_dir_path = os.path.join(experiment_directory_path, f"seed_{seed}")
        dag_dir_path = os.path.join(seed_dir_path, "dags")
        dag_path = os.path.join(dag_dir_path, "original_dag", "DAG.dot")

        # Generate DAG and record nodes and edges
        dag = generate_dag(n_nodes, p_edge, seed=seed, dot_path=dag_path)
        total_nodes += len(dag.nodes)
        total_edges += len(dag.edges)

        p_g_start_time = time()
        generate_program(
            dag,
            p_conditional=p_conditional,
            target_directory_path=seed_dir_path,
            program_name="program"
        )
        p_g_end_time = time()
        print(f"Program generation run time: {p_g_end_time - p_g_start_time}")

        # Check whether the program is semantically causal
        program_path = os.path.join(seed_dir_path, "program.py")
        try:
            generate_and_execute_metamorphic_relations(program_path, dag_path)
        except ValueError as e:
            # The program contain a mathematical function that evaluates to zero
            shutil.rmtree(seed_dir_path)
            print("Error: Function evaluates to zero.")
            print(e)
            continue
        except AssertionError as e:
            # There exist some MRs implied by the DAG that do not hold in the program
            # Hence, the program is causal in its syntax but not its semantics
            shutil.rmtree(seed_dir_path)
            print("Error: Syntactic causation only.")
            print(e)
            continue

        c_m_g_start_time = time()
        generate_causal_mutation_config(
            dag,
            target_directory_path=dag_path.replace("DAG.dot", "mutation_config.toml"),
        )
        c_m_g_end_time = time()
        print(f"Causal mutation generation run time: "
              f"{c_m_g_end_time - c_m_g_start_time}")

        # Create increasingly more misspecified DAGs
        m_ds_start_time = time()
        for p_invert in [0.25, 0.5, 0.75, 1]:
            out_path = os.path.join(dag_dir_path, f"misspecified_dag_{int(p_invert*100)}/DAG.dot")
            mutant_dag = mutate_dag(dag, p_invert, out_path, seed)
            shd = structural_hamming_distance(dag, mutant_dag)
            print(shd)
            generate_causal_mutation_config(
                mutant_dag,
                target_directory_path=out_path.replace("DAG.dot", "mutation_config.toml"),
            )
        m_ds_end_time = time()
        print(f"Mutate DAGs run time: {m_ds_end_time - m_ds_start_time}")

    average_nodes = total_nodes / n_dags
    average_edges = total_edges / n_dags
    write_params(params_path, n_dags, n_nodes, p_edge, experiment_directory_path,
                 average_nodes, average_edges)


def run_experiment(
    experiment_directory_path: str
):
    """Run the specified experiment.

    :param experiment_directory_path: Path to the root level of the experiment directory.
    """
    for dag_directory in glob.iglob(os.path.join(experiment_directory_path, "**/")):
        print(f"Experiment path: {dag_directory}")
        dag_path = os.path.join(dag_directory, "dags", "original_dag", "DAG.dot")
        program_path = os.path.join(dag_directory, "program.py")
        generate_and_execute_metamorphic_relations(program_path, dag_path)
        # mutated_dag_directory = os.path.join(dag_directory, "misspecified_dags/")
        # for mutated_dag_path in glob.iglob(os.path.join(mutated_dag_directory, "*.dot")):
        #     try:
        #         generate_and_execute_metamorphic_relations(program_path, mutated_dag_path)
        #     except AssertionError as e:
        #         print(e)


def generate_and_execute_metamorphic_relations(program_path, dag_path):
    """Generate MRs implied by the specified DAG and test against the given program.

    :param program_path: Path to the specified program.
    :param dag_path: Path to the specified causal DAG representing the causal relationships in the program.
    """
    true_dag = nx.nx_pydot.read_dot(dag_path)
    mod_spec = importlib.util.spec_from_file_location("program.program", program_path)
    program = importlib.util.module_from_spec(mod_spec)
    metamorphic_relations = generate_metamorphic_relations(true_dag)
    sys.modules["program.program"] = program
    mod_spec.loader.exec_module(program)
    for metamorphic_relation in metamorphic_relations:
        print(f"Testing: {metamorphic_relation}")
        metamorphic_relation.generate_tests()
        metamorphic_relation.execute_tests(program.program)


def write_params(
    path: str, n_dags: int, n_nodes: int, p_edge: float, experiment_name: str,
    a_nodes: float, a_edges: float
):
    """Write parameter details to a text file at the specified path.

    :param path: Path for the parameter details txt file to be saved to.
    :param n_dags: Number of DAGs generated.
    :param n_nodes: Number of nodes per DAG generated.
    :param p_edge: Probability of including an edge between any pair of nodes in
                   the generated DAG.
    :param experiment_name: Name of the experiment conducted.
    :param a_nodes: Average nodes per DAG generated (should equal n_nodes).
    :param a_edges: Average edges per DAG generated.
    """
    with safe_open_w(path) as params_file:
        params_file.writelines(
            [
                f"Experiment name: {experiment_name}\n",
                f"Number of DAGs generated: {n_dags}\n",
                f"Number of nodes per DAG: {n_nodes}\n",
                f"Probability of including an edge between any pair of nodes in"
                f" the DAG: {p_edge}\n",
                f"Average nodes per DAG: {a_nodes}\n",
                f"Average edges per DAG: {a_edges}\n"
            ]
        )


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-nd", "--dags", help="Number of DAGs to generate", type=int)
    parser.add_argument(
        "-nn", "--nodes", help="Number of nodes in generated DAG", type=int
    )
    parser.add_argument(
        "-pe",
        "--edges",
        help="Probability to include edge between any pair of nodes",
        type=float,
    )
    parser.add_argument(
        "-pc",
        "--conditional",
        help="Probability that an arbitrary non-terminal node is conditional",
        type=float,
        default=0.0
    )
    parser.add_argument("-en", "--experiment", help="Path to store the experiment", type=str)
    parser.add_argument("-s", "--seed", help="Random seed", type=int)
    parser.add_argument("-t", "--task", help="Task to conduct: 'gen' for generation or 'run' for running experiments.")
    args = parser.parse_args()
    number_of_dags = 1
    number_of_nodes = 10
    probability_of_edge = 0.2
    probability_of_conditional = 0.0
    experiment_directory_path = "./evaluation/experiment"
    seed = 0
    if args.dags:
        number_of_dags = args.dags
    if args.nodes:
        number_of_nodes = args.nodes
    if args.conditional:
        probability_of_conditional = args.conditional
    if args.edges:
        probability_of_edge = args.edges
    if args.experiment:
        experiment_directory_path = args.experiment
    if args.seed:
        seed = args.seed

    if (not args.task) or (args.task == 'gen'):
        start_time = time()
        generate_experiment(
            number_of_dags,
            number_of_nodes,
            probability_of_edge,
            p_conditional=probability_of_conditional,
            experiment_directory_path=experiment_directory_path,
            seed=seed
        )
        end_time = time()
        print(f"Experiment generation time: {end_time - start_time}s")

    if (not args.task) or (args.task == 'run'):
        run_start_time = time()
        run_experiment(experiment_directory_path)
        run_end_time = time()
        print(f"Experiment run time: {run_end_time - run_start_time}s")
