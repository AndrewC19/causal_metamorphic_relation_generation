import argparse
import networkx as nx
import importlib
from metamorphic_relations.metamorphic_relation_generation import generate_metamorphic_relations
import json


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
args = parser.parse_args()
program_path = args.program
mod_spec = importlib.util.spec_from_file_location("program.program", program_path)
program = importlib.util.module_from_spec(mod_spec)
mod_spec.loader.exec_module(program)
dag = nx.nx_pydot.read_dot(args.dag)

seed = 0
if args.seed is not None:
    seed = int(args.seed)

results = []
for relation in generate_metamorphic_relations(dag):
    result = {"relation": str(relation), "total": 0, "failures": []}
    relation.generate_tests(seed=seed)
    result["total"] += len(relation.tests)
    result["failures"] += relation.execute_tests(program.program, continue_after_failure=args.continue_)
    results.append(result)

if args.outfile is not None:
    with open(args.outfile, 'w') as f:
        print(json.dumps(results, indent=2), file=f)
if args.continue_:
    assert all([len(result['failures']) == 0 for result in results])
