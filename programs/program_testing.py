import argparse
import networkx as nx
import importlib
import json
from helpers import safe_open_w
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
    result = {"relation": str(relation), "total": 0, "failed": False}
    relation.generate_tests(seed=seed, sample_size=sample_size)
    result["total"] += len(relation.tests)
    failures = relation.execute_tests(program.program)
    try:
        relation.oracle(failures)
    except AssertionError as e:
        print(e)
        # Only add failures that result in MR failing (i.e. if all tests fail for --> and if one test fails for _||_)
        result["failed"] = True
    results.append(result)


def get_failures(results_dict):
    failed_relations = []
    for relation_result in results_dict:
        if relation_result["failed"]:
            failed_relations.append(relation_result["relation"])
    return failed_relations


if args.outfile is not None:
    with safe_open_w(args.outfile) as f:
        print(json.dumps(results), file=f)

if args.continue_:
    assert all([not result['failed'] for result in results]),\
        f"Failed MRs: {get_failures(results)}"
