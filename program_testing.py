import argparse
import networkx as nx
from metamorphic_relation_generation import generate_metamorphic_relations
from importlib import import_module
import re

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
                    help="A random seed for reproducabilility. Defaults to 0.",
                    required=False,
                    )
args = parser.parse_args()

program_path = args.program
if program_path.endswith(".py"):
    program_path = program_path[:-3]
program_path = re.sub(r'[/\\]', '.', program_path)  # replace slashes with . for module import
program = import_module(program_path).program  # Import program function from program module
dag = nx.nx_pydot.read_dot(args.dag)

seed = 0
if args.seed is not None:
    seed = int(args.seed)

for relation in generate_metamorphic_relations(dag):
    relation.generate_tests()
    relation.execute_tests(program)
