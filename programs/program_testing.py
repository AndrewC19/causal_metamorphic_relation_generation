import argparse
import networkx as nx
import importlib
import json
from metamorphic_relations.metamorphic_relation_generation import generate_metamorphic_relations


parser = argparse.ArgumentParser(
    description="Parses args"
)
parser.add_argument('-p',
                    '--program',
                    help="Path to program file.",
                    required=True,
                    )
parser.add_argument('-d',
                    '--dag',
                    help="Path to causal dag.",
                    required=True,
                    )
parser.add_argument('-s',
                    '--seed',
                    help="A random seed for reproducibility. Defaults to 0.",
                    required=False,
                    )
parser.add_argument('-o',
                    '--outfile',
                    help="A location to save test results.",
                    required=False,
                    )
parser.add_argument('-c',
                    '--continue',
                    help="Flag to continue after first failure.",
                    required=False,
                    action=argparse.BooleanOptionalAction,
                    dest='continue_'
                    )
parser.add_argument('-t',
                    '--tests',
                    help="Number of tests to generate per relation.",
                    required=False,
                    type=int,
                    default=1)
args = parser.parse_args()
program_path = args.program
mod_spec = importlib.util.spec_from_file_location("program.program", program_path)
program = importlib.util.module_from_spec(mod_spec)
mod_spec.loader.exec_module(program)
dag = nx.nx_pydot.read_dot(args.dag)
sample_size = args.tests

seed = 0
if args.seed is not None:
    seed = int(args.seed)

results = []
for relation in generate_metamorphic_relations(dag):
    result = {"relation": str(relation), "total": 0, "failures": []}
    relation.generate_tests(seed=seed, sample_size=sample_size)
    result["total"] += len(relation.tests)
    failures = relation.execute_tests(program.program)
    try:
        relation.oracle(failures)
    except AssertionError as e:
        print(e)
        # Only add failures that result in MR failing (i.e. if all tests fail for --> and if one test fails for _||_)
        result["failures"] += failures
    results.append(result)


def get_failures(results_dict):
    failures = {"relation": [], "result": []}
    for result in results_dict:
        if len(result["failures"]) > 0:
            failures["relation"].append(result["relation"])
            failures["result"].append(result["failures"])
    return failures


if args.outfile is not None:
    with open(args.outfile, 'w') as f:
        print(json.dumps(results), file=f)

if args.continue_:
    assert all([len(result['failures']) == 0 for result in results]), f"Test Failures: {get_failures(results)}"
