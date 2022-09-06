import random
from time import time
from argparse import ArgumentParser
from dag_generation import generate_dag, mutate_dag
from program_generation import generate_program
from mutation_config_generation import generate_causal_mutation_config
from helpers import safe_open_w
from dag_utils import structural_hamming_distance


def generate_experiment(
    n_dags: int,
    n_nodes: int,
    p_edge: float,
    experiment_name: str = "experiment",
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
    :param experiment_name: A string denoting the name of the experiment.
    """
    experiment_directory = f"./evaluation/{experiment_name}/"
    params_path = f"{experiment_directory}/params.txt"
    random.seed(seed)
    total_edges = 0
    total_nodes = 0
    for n in range(n_dags):
        # Set seed
        seed = random.randint(1, 100000)
        random.seed(seed)

        # Create custom paths for experiment components
        dag_path = f"{experiment_directory}/seed_{seed}"
        dot_path = f"{dag_path}/DAG.dot"
        mutation_path = f"{dag_path}/mutation_config.toml"
        mutant_dag_path = f"{dag_path}/misspecified_dags"

        # Generate DAG and record nodes and edges
        dag = generate_dag(n_nodes, p_edge, seed=seed, dot_path=dot_path)
        total_nodes += len(dag.nodes)
        total_edges += len(dag.edges)

        p_g_start_time = time()
        generate_program(
            dag,
            target_directory_path=dag_path,
            program_name="program",
        )
        p_g_end_time = time()
        print(f"Program generation run time: {p_g_end_time - p_g_start_time}")

        c_m_g_start_time = time()
        generate_causal_mutation_config(
            dag,
            target_directory_path=mutation_path,
        )
        c_m_g_end_time = time()
        print(f"Causal mutation generation run time: "
              f"{c_m_g_end_time - c_m_g_start_time}")

        # Create increasingly more misspecified DAGs
        m_ds_start_time = time()
        for p_invert in [0.25, 0.5, 0.75, 1]:
            out_path = f"{mutant_dag_path}/misspecified_dag_{p_invert*100}pct.dot"
            mutant_dag = mutate_dag(dag, p_invert, out_path)
            shd = structural_hamming_distance(dag, mutant_dag)
            print(shd)
        m_ds_end_time = time()
        print(f"Mutate DAGs run time: {m_ds_end_time - m_ds_start_time}")

    average_nodes = total_nodes / n_dags
    average_edges = total_edges / n_dags
    write_params(params_path, n_dags, n_nodes, p_edge, experiment_name,
                 average_nodes, average_edges)


def write_params(
    path: str, n_dags: int, n_nodes: int, p_edge: float, experiment_name: str,
    a_nodes: int, a_edges: int
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
    parser.add_argument("-en", "--experiment", help="Name of the experiment", type=str)
    parser.add_argument("-s", "--seed", help="Random seed", type=int)

    args = parser.parse_args()
    number_of_dags = 1
    number_of_nodes = 10
    probability_of_edge = 0.2
    experiment_name = "experiment_1"
    seed = 0
    if args.dags:
        number_of_dags = args.dags
    if args.nodes:
        number_of_nodes = args.nodes
    if args.edges:
        probability_of_edge = args.edges
    if args.experiment:
        experiment_name = args.experiment
    if args.seed:
        seed = args.seed
    start_time = time()
    generate_experiment(
        number_of_dags,
        number_of_nodes,
        probability_of_edge,
        experiment_name=experiment_name,
        seed=seed
    )
    end_time = time()
    print(f"Run time: {end_time - start_time}")
