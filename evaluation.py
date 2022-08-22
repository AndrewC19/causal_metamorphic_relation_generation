import random
from argparse import ArgumentParser
from dag_generation import generate_dag
from synthetic_program_generation import generate_program


def generate_experiment(n_dags: int, n_nodes: int, p_edge: float):
    """Generate an experiment with user specified DAGs.

    The resulting programs will be saved in the evaluation directory (one will be created if it does not already exist).
    Within this directory, a subdirectory named nd_{n_dags}_nn_{n_nodes}_pe{p_edge} will be created.

    :param n_dags: Number of DAGs to generate.
    :param n_nodes: Number of nodes per DAG.
    :param p_edge: Probability of an edge being added between any two nodes.
    """
    experiment_directory = f"./evaluation/nd_{n_dags}_nn_{n_nodes}_pe_{p_edge}/"
    for n in range(n_dags):
        seed = random.randint(1, 100000)
        random.seed(seed)
        dag = generate_dag(n_nodes, p_edge)
        experiment_name = f"seed_{seed}"
        generate_program(
            dag,
            target_directory_path=experiment_directory,
            program_name=experiment_name,
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

    args = parser.parse_args()
    number_of_dags = 1
    number_of_nodes = 10
    probability_of_edge = 0.2
    if args.dags:
        number_of_dags = args.dags
    if args.nodes:
        number_of_nodes = args.nodes
    if args.edges:
        probability_of_edge = args.edges

    generate_experiment(number_of_dags, number_of_nodes, probability_of_edge)
