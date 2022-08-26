import random
from argparse import ArgumentParser
from dag_generation import generate_dag
from program_generation import generate_program
from mutation_config_generation import generate_causal_mutation_config
from helpers import safe_open_w


def generate_experiment(
    n_dags: int, n_nodes: int, p_edge: float, experiment_name: str = "experiment", seed: int = 0
):
    """Generate an experiment with user specified DAGs.

    The resulting programs will be saved in the evaluation directory (one will be created if it does not already exist).
    Within this directory, a subdirectory with the experiment name will be produced. The details of the generated DAGs
    will be stored in params.txt.

    :param n_dags: Number of DAGs to generate.
    :param n_nodes: Number of nodes per DAG.
    :param p_edge: Probability of an edge being added between any two nodes.
    :param experiment_name: A string denoting the name of the experiment.
    """
    experiment_directory = f"./evaluation/{experiment_name}/"
    params_path = f"{experiment_directory}/params.txt"
    random.seed(seed)
    for n in range(n_dags):
        seed = random.randint(1, 100000)
        random.seed(seed)
        dag_path = f"{experiment_directory}/seed_{seed}"
        dot_path = f"{dag_path}/DAG.dot"
        mutation_path = f"{dag_path}/mutation_config.toml"
        dag = generate_dag(n_nodes, p_edge, seed=seed, dot_path=dot_path)
        generate_program(
            dag,
            target_directory_path=dag_path,
            program_name="program",
        )
        generate_causal_mutation_config(
            dag,
            target_directory_path=mutation_path,
        )

    write_params(params_path, n_dags, n_nodes, p_edge, experiment_name)


def write_params(
    path: str, n_dags: int, n_nodes: int, p_edge: float, experiment_name: str
):
    """Write parameter details to a text file at the specified path.

    :param n_dags: Number of DAGs generated.
    :param n_nodes: Number of nodes per DAG generated.
    :param p_edge: Probability of including an edge between any pair of nodes in the generated DAG.
    :param experiment_name: Name of the experiment conducted.
    :param path: Path for the parameter details txt file to be saved to.
    """
    with safe_open_w(path) as params_file:
        params_file.writelines(
            [
                f"Experiment name: {experiment_name}\n",
                f"Number of DAGs generated: {n_dags}\n",
                f"Number of nodes per dag: {n_nodes}\n",
                f"Probability of including an edge between any pair of nodes in the DAG: {p_edge}\n",
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

    generate_experiment(
        number_of_dags,
        number_of_nodes,
        probability_of_edge,
        experiment_name=experiment_name,
        seed=seed
    )
