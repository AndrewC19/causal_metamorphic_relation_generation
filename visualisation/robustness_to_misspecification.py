import matplotlib.pyplot as plt
import pandas as pd
import glob
import pprint
from pathlib import Path


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
    results_to_csv("../results/formatted_results_30_nodes",
                   "../results/results_30_nodes.csv")
