import argparse
import networkx as nx
import importlib
from metamorphic_relation_generation import generate_metamorphic_relations


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
args = parser.parse_args()
program_path = args.program
mod_spec = importlib.util.spec_from_file_location("program.program", program_path)
program = importlib.util.module_from_spec(mod_spec)
mod_spec.loader.exec_module(program)
dag = nx.nx_pydot.read_dot(args.dag)

seed = 0
if args.seed is not None:
    seed = int(args.seed)

for relation in generate_metamorphic_relations(dag):
    relation.generate_tests()
    relation.execute_tests(program.program)
