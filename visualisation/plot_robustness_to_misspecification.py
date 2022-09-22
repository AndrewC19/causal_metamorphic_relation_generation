"""Plot the robustness of the approach to model misspecification."""
import json
import os
import matplotlib.pyplot as plt
from typing import Iterable


def plot_robustness_to_misspecification(paths_to_results_json: Iterable):
    fig, axs = plt.subplots(5, 1, sharex=True, figsize=(8, 8))
    plt.xlabel("Structural Hamming Distance")
    axs[0].set_ylabel("TPs")
    axs[1].set_ylabel("TNs")
    axs[2].set_ylabel("FPs")
    axs[3].set_ylabel("FNs")
    axs[4].set_ylabel("MS")
    axs[4].set_ylim(0, 1)
    color_map = {'1': 'blue', '5': 'green', '10': 'red'}
    for results_json_path in paths_to_results_json:
        results_json = os.path.join(results_json_path, "results.json")
        n_tests = results_json_path.split('/')[-2].split('_t')[1].split('_')[0]
        with open(results_json, 'r') as f:
            results_dict = json.load(f)
            tp_ys = []
            tn_ys = []
            fp_ys = []
            fn_ys = []
            ms_ys = []
            xs = []
            for dag_dict in results_dict:
                mutations_dict = dag_dict["jobs"]
                tps, tns, fps, fns, mutants, mutants_killed = 0, 0, 0, 0, 0, 0
                shd = dag_dict["structural_hamming_distance"]
                for mutation, mutation_results in mutations_dict.items():
                    if mutation != "baseline":
                        tps += mutation_results["true_positive_relations"]
                        tns += mutation_results["true_negative_relations"]
                        fps += mutation_results["false_positive_relations"]
                        fns += mutation_results["false_negative_relations"]
                        mutants += 1
                        if mutation_results["true_positive_relations"] > 0:
                            mutants_killed += 1

                print("==============================================")
                print("SHD: ", shd)
                print("#Tests: ", n_tests)
                print("#Mutants: ", mutants)
                print("TPs: ", tps)
                print("TNs: ", tns)
                print("FPs: ", fps)
                print("FNs: ", fns)
                print("Mutation score: ", mutants_killed/mutants)
                tp_ys.append(tps)
                tn_ys.append(tns)
                fp_ys.append(fps)
                fn_ys.append(fns)
                ms_ys.append(mutants_killed/mutants)
                xs.append(shd)
                axs[0].scatter(xs, tp_ys, s=5, color=color_map[n_tests], label=n_tests)
                axs[1].scatter(xs, tn_ys, s=5, color=color_map[n_tests], label=n_tests)
                axs[2].scatter(xs, fp_ys, s=5, color=color_map[n_tests], label=n_tests)
                axs[3].scatter(xs, fn_ys, s=5, color=color_map[n_tests], label=n_tests)
                axs[4].scatter(xs, ms_ys, s=5, color=color_map[n_tests], label=n_tests)
    # plt.tight_layout()
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())
    plt.show()

if __name__ == "__main__":
    results_jsons = ["testing_no_conditional_small_t1_c25/seed_19094",
                     "testing_no_conditional_small_t5_c25/seed_19094",
                     "testing_no_conditional_small_t10_c25/seed_19094"]
    results_jsons = [os.path.join("../evaluation/", result) for result in results_jsons]
    plot_robustness_to_misspecification(results_jsons)