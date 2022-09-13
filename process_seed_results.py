import json
import argparse
import os

parser = argparse.ArgumentParser(
    description="Parses args"
)
parser.add_argument('-s',
                    '--seed',
                    help="Path to seed folder.",
                    required=True,
                    )
args = parser.parse_args()

dags_dir = os.path.join(args.seed, "dags")

for dag in os.listdir(dags_dir):
    datum = {"dag": dag}
    with open(os.path.join(dags_dir, dag, "results.json")) as f:
        results = json.load(f)

    total_tests = sum([relation["total"] for relation in results["baseline"]["test_outcomes"]])
    datum["total_tests"] = total_tests

    baseline_failers = [test["control_inputs"] for relation in results["baseline"]["test_outcomes"] for test in relation["failures"]]
    datum["baseline_failers"] = len(baseline_failers)

    print(dag)
    for job in results:
        if job == "baseline":
            continue
        # Non-baseline failers
        failers = [tuple(sorted(list(test["control_inputs"].items()))) for relation in results[job]["test_outcomes"] for test in relation["failures"]]
        non_baseline_failers = set(failers).difference([tuple(sorted(list(inputs.items()))) for inputs in baseline_failers])

        # Bug obfuscators
        bug_obfuscators = set([tuple(sorted(list(inputs.items()))) for inputs in baseline_failers]).difference(failers)
