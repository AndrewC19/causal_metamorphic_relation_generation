import json
import argparse
import os
import pydot

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
dags = sorted(os.listdir(dags_dir), reverse=True)
assert "original_dag" == dags[0], f"Expected 'original_dag' to be the first DAG to process. Instead got {dags[0]}."

p_conditional = None
p_edge = None
p_invert_edge = None
structural_hamming_distance = None

for dag in dags:
    datum = {"dag": dag}
    with open(os.path.join(dags_dir, dag, "results.json")) as f:
        results = json.load(f)
    graph = pydot.graph_from_dot_file(os.path.join(dags_dir, dag, "DAG.dot"))[0]
    datum['dag_nodes'] = len(graph.get_nodes())
    datum['dag_edges'] = len(graph.get_edges())
    comment = json.loads(json.loads(graph.get_comment()))

    if dag == "original_dag":
        p_conditional = comment["p_conditional"]
        p_edge = comment["p_edge"]
        p_invert_edge = 0
        structural_hamming_distance = 0
    else:
        p_invert_edge = comment["p_invert_edge"]
        structural_hamming_distance = comment["structural_hamming_distance"]

    datum["p_conditional"] = p_conditional
    datum["p_edge"] = p_edge
    datum["p_invert_edge"] = p_invert_edge
    datum["structural_hamming_distance"] = structural_hamming_distance

    total_tests = sum([relation["total"] for relation in results["baseline"]["test_outcomes"]])
    datum["total_tests"] = total_tests

    baseline_failers = [test["control_inputs"] for relation in results["baseline"]["test_outcomes"] for test in relation["failures"]]
    datum["baseline_failers"] = len(baseline_failers)
    datum['non_baseline_failers'] = 0
    datum['bug_obfuscators'] = 0

    # We want the mutation score to come from those tests which pass on either the original or the mutated version of
    # the program. Tests which fail on both tell us nothing because they reflect the fact that the DAG does not reflect
    # the actual causal structure of the program.

    print(dag)
    for job in results:
        if job == "baseline":
            continue
        # Non-baseline failers
        failers = [tuple(sorted(list(test["control_inputs"].items()))) for relation in results[job]["test_outcomes"] for test in relation["failures"]]

        non_baseline_failers = set(failers).difference([tuple(sorted(list(inputs.items()))) for inputs in baseline_failers])
        datum['non_baseline_failers'] += len(non_baseline_failers)

        # Bug obfuscators
        # Tests which fail the baseline but which subsequently pass on a mutated version of the program
        bug_obfuscators = set([tuple(sorted(list(inputs.items()))) for inputs in baseline_failers]).difference(failers)
        datum['bug_obfuscators'] += len(bug_obfuscators)
    print(datum)
