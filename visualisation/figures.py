import pandas as pd
from pathlib import Path
from plotnine import *
from matplotlib import rc

rc('font', **{'family': 'serif', 'serif': ['Computer Modern']}, )
rc('text', usetex=True)


def label_n_tests(n_tests):
    return f"Test suite size = {n_tests}"


def label_p_edge(p_edge):
    return f"$p_e = {p_edge}$"


def plot_robustness_to_misspecification_from_csv(results_csv_path):
    results_df = pd.read_csv(results_csv_path)
    p = (ggplot(results_df,
                aes("structural_hamming_distance", "mutation_score"))
         + geom_point(size=.1, alpha=.25, color="gray", shape='o')
         + stat_smooth(method='loess', level=0.95, color="purple", size=0.75)
         + facet_wrap('~p_edge', labeller=label_p_edge)
         + labs(x="Structural Hamming Distance",
                y="Mutation Score",
                title=f"Robustness to A1 with 20 node CSGs")
         + scale_y_continuous(limits=(0, 1), )
         + scale_color_discrete(guide=False)).save(filename="RQ1.pdf", path="../figures",
                                                   format="pdf")


def plot_robustness_to_conditional_complexity_from_csv(results_csv_path):
    results_df = pd.read_csv(results_csv_path)
    no_misspecification_results_df = results_df.loc[
        (results_df["p_invert_edge"] == 0)]
    (ggplot(no_misspecification_results_df,
            aes("new_mccabe", "mutation_score", color="factor(n_tests)"))
     + geom_point(size=.1, alpha=0.5, color="gray", shape='o')
     + stat_smooth(method='loess', level=0.95, color="purple", size=0.75)
     + facet_grid('n_tests ~ p_edge', labeller=labeller(cols=label_p_edge,
                                                        rows=label_n_tests),
                  scales='free_y')
     + labs(x="McCabe Complexity Score",
            y="Mutation Score",
            title="Robustness to A2 with 20 node CSGs")
     + scale_y_continuous(limits=(0.4, 1))
     + scale_color_discrete(guide=False)).save(filename="RQ2.pdf",
                                               path="../figures",
                                               format="pdf")


def results_to_csv(results_path: str, out_file_name: str):
    results_df = pd.DataFrame()
    results_path_root = Path(results_path)
    json_file_list = [f for f in results_path_root.glob("*.json")]
    for json_file in json_file_list:
        json_content = pd.read_json(json_file)
        for dag in json_content.itertuples(index=True):
            index = dag[0]
            mutations_dict = dag.jobs
            ms, tps, tns, fps, fns = process_mutation_dict(mutations_dict)
            json_content.at[index, "mutation_score"] = ms
            json_content.at[index, "true_positives"] = tps
            json_content.at[index, "true_negatives"] = tns
            json_content.at[index, "false_positives"] = fps
            json_content.at[index, "false_negatives"] = fns
        results_df = results_df.append(json_content, ignore_index=True)
    results_df = results_df.drop(columns=["jobs"])
    results_df.to_csv(out_file_name)


def mean_mutation_score_for_tests_at_min_max_mccabe(results_csv_path):
    df = pd.read_csv(results_csv_path)
    no_misspecification_df = df.loc[df["structural_hamming_distance"] == 0]
    for test_suite_size in no_misspecification_df["n_tests"].unique():
        test_suite_size_df = no_misspecification_df.loc[
            no_misspecification_df["n_tests"] == test_suite_size]
        min_mccabe = test_suite_size_df["new_mccabe"].min()
        max_mccabe = test_suite_size_df["new_mccabe"].max()
        min_mccabe_df = test_suite_size_df.loc[
            test_suite_size_df["new_mccabe"] == min_mccabe]
        max_mccabe_df = test_suite_size_df.loc[
            test_suite_size_df["new_mccabe"] == max_mccabe]
        mean_mutation_score_at_min_mccabe = min_mccabe_df["mutation_score"].mean()
        mean_mutation_score_at_max_mccabe = max_mccabe_df["mutation_score"].mean()
        print(f"Mean mutation score at {min_mccabe} McCabe for test suite size"
              f" {test_suite_size}: {mean_mutation_score_at_min_mccabe}")
        print(f"Mean mutation score at {max_mccabe} McCabe for test suite size"
              f" {test_suite_size}: {mean_mutation_score_at_max_mccabe}")
        print(f"Difference between mutation score at min and max McCabe:"
              f"{round(mean_mutation_score_at_min_mccabe - mean_mutation_score_at_max_mccabe, 3)}")

def process_mutation_dict(mutation_dict):
    mutants_killed = 0
    total_mutants = 0
    tps, tns, fps, fns = 0, 0, 0, 0
    for mutation, results_dict in mutation_dict.items():
        if mutation != "baseline":
            tps += results_dict["true_positive_relations"]
            tns += results_dict["true_negative_relations"]
            fps += results_dict["false_positive_relations"]
            fns += results_dict["false_negative_relations"]

            # A mutant is killed if at least one test catches it (TP)
            if results_dict["true_positive_relations"] > 0:
                mutants_killed += 1
            total_mutants += 1
    mutation_score = mutants_killed / total_mutants
    return mutation_score, tps, tns, fps, fns


if __name__ == "__main__":
    RESULTS_PATH = "../second_corrected_results/results_20_nodes.csv"
    # results_to_csv("../second_corrected_results/formatted_results_30_nodes",
    #                "../second_corrected_results/results_30_nodes.csv")
    plot_robustness_to_misspecification_from_csv(RESULTS_PATH)
    plot_robustness_to_conditional_complexity_from_csv(RESULTS_PATH)
    mean_mutation_score_for_tests_at_min_max_mccabe(RESULTS_PATH)