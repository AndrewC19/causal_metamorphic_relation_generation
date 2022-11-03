import mccabe as mc
import os
import ast
import json
from argparse import ArgumentParser
from pathlib import Path


def get_mccabe_complexity(program_path, program_name=None):
    """Get McCabe complexity for a program using Ned's script:
    https://github.com/PyCQA/mccabe.

    :param program_path: Path to the python program whose complexity we wish to
                         measure.
    :return: McCabe complexity score for the program.
    """
    code = mc._read(program_path)
    tree = compile(code, program_path, "exec", ast.PyCF_ONLY_AST)
    visitor = mc.PathGraphingAstVisitor()
    visitor.preorder(tree, visitor)
    if not program_name:
        program_name = os.path.basename(program_path)[:-3]
    return visitor.graphs[program_name].complexity()


def flatten_program(program_path):
    with open(program_path) as f:
        head = True
        new_program = ""
        for line in f:
            print(line.strip())
            if line.strip() == '"""':
                print(line)
                new_program += line
                head = False
            elif line.startswith("\t\t") and not head:
                print(line)
                new_program += line[1:]
            else:
                new_program += line

    with open(program_path, 'w') as f:
        print(new_program, file=f)


if __name__ == "__main__":
    # flatten_program("./program_to_flatten.py")
    parser = ArgumentParser()
    parser.add_argument("-nn", dest="n_nodes", help="Target number of"
                                                    " nodes.")
    args = parser.parse_args()
    formatted_results = f"small_formatted_results_{args.n_nodes}_nodes"
    original_results = f"results_{args.n_nodes}_nodes"
    formatted_results_path_root = Path(formatted_results)
    json_file_list = [f for f in formatted_results_path_root.glob("*.json")]

    flattened_program_paths = []
    for json_file in json_file_list:
        dag_config = json_file.name.split("_seed")[0]
        seed_config = "seed_" + json_file.name.split("_seed")[1].split("_")[1]
        path_to_py_file = os.path.join(original_results, dag_config, seed_config,
                                       "flattened_program.py")

        if path_to_py_file not in flattened_program_paths:
            flatten_program(path_to_py_file)
            flattened_program_paths.append(path_to_py_file)

        mccabe_complexity = get_mccabe_complexity(path_to_py_file,
                                                  "program")
        with open(json_file) as f:
            data = json.load(f)
            for dag in data:
                dag["new_mccabe"] = mccabe_complexity

        with open(json_file, 'w') as f:
            print(json.dumps(data, indent=2), file=f)
