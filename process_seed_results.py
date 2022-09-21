import json
import argparse
import os
import pydot
import mccabe as mc
import ast


def get_mccabe_complexity(program_path):
    """Get McCabe complexity for a program using Ned's script: https://github.com/PyCQA/mccabe.

    :param program_path: Path to the python program whose complexity we wish to measure.
    :return: McCabe complexity score for the program.
    """
    code = mc._read(program_path)
    tree = compile(code, program_path, "exec", ast.PyCF_ONLY_AST)
    visitor = mc.PathGraphingAstVisitor()
    visitor.preorder(tree, visitor)
    program_name = os.path.basename(program_path)[:-3]
    return visitor.graphs[program_name].complexity()


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

data = []
for dag in dags:
    datum = {"dag": dag}
    datum["mccabe"] = get_mccabe_complexity(os.path.join(args.seed, "program.py"))

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

    # True - Passed baseline
    # False - Failed baseline
    # Positive - Caught a bug (i.e. test outcome = failed)
    # Negative - Didn't catch a bug (i.e. test outcome = passed)

    datum["jobs"] = {job: {} for job in results}
    # baseline_failed_tests = [tuple(sorted(list(test["source_inputs"].items()))) for relation in results["baseline"]["test_outcomes"] for test in relation["failures"]]
    baseline_failed_relations = [result['relation'] for result in results["baseline"]["test_outcomes"] if not result["passed"]]
    # datum["jobs"]["baseline"]["positive_tests"] = len(baseline_failed_tests)
    datum["jobs"]["baseline"]["positive_relations"] = len(baseline_failed_relations)


    datum["num_jobs"] = len(results)

    for job in results:
        if job == "baseline":
            continue

        # Positive
        # failed_tests = [tuple(sorted(list(test["source_inputs"].items()))) for relation in results[job]["test_outcomes"] for test in relation["failures"]]
        failed_relations = [relation["relation"] for relation in results[job]["test_outcomes"] if not relation["passed"]]

        # Passed baseline - Failed on mutant
        # True positive - i.e. mutant finders
        # datum["jobs"][job]['true_positive_tests'] = len(set(failed_tests).difference(baseline_failed_tests))
        datum["jobs"][job]['true_positive_relations'] = len(set(failed_relations).difference(baseline_failed_relations))

        # Failed on baseline - Failed on mutant
        # False positive - i.e. DAG misspecification finders
        # datum["jobs"][job]['false_positive_tests'] = len(set(failed_tests).intersection(baseline_failed_tests))
        datum["jobs"][job]['false_positive_relations'] = len(set(failed_relations).intersection(baseline_failed_relations))

        # Passed baseline - Passed mutant
        # True Negatives - i.e. unaffected by misspecification or mutation
        total_tests = sum([result["total"] for result in results[job]["test_outcomes"]])
        total_relations = len(results[job]["test_outcomes"])
        # datum["jobs"][job]["true_negative_tests"] = total_tests - len(set(baseline_failed_tests).union(failed_tests))
        datum["jobs"][job]["true_negative_relations"] = total_relations - len(set(baseline_failed_relations).union(failed_relations))
        assert len(set(baseline_failed_relations).union(failed_relations)) <= total_relations


        # Failed baseline - Passed mutant
        # False Negatives - i.e. mutant obfuscators
        # datum["jobs"][job]["false_negative_tests"] = len(set(baseline_failed_tests).difference(failed_tests))
        datum["jobs"][job]["false_negative_relations"] = len(set(baseline_failed_relations).difference(failed_relations))
    data.append(datum)

with open(os.path.join(args.seed, "results.json"), 'w') as f:
    print(json.dumps(data, indent=2), file=f)
