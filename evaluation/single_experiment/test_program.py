from pathlib import Path
from typing import List, Tuple
from importlib import import_module
import argparse
import lhsmdu
import re
import pandas as pd

from scipy.stats import uniform

from causal_testing.specification.conditional_independence import ConditionalIndependence
from causal_testing.specification.scenario import Scenario
from causal_testing.specification.variable import Input, Output
from causal_testing.specification.causal_dag import CausalDAG


# pd.set_option('display.max_columns', 500)


def get_dir_path() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Parses args"
    )
    parser.add_argument('-p',
                        '--path',
                        help="Path to seed directory containing DAG.dot and program.py",
                        required=True,
                        )
    parser.add_argument('-s',
                        '--seed',
                        help="A random seed",
                        required=False,
                        )
    return parser.parse_args()


def count(lst):
    counts = {}
    for item in lst:
        if item not in counts:
            counts[item] = 0
        counts[item] += 1
    return counts


def independence_metamorphic_tests(
        independence: ConditionalIndependence, scenario: Scenario, sample_size: int = 1, seed=0
):
    X = independence.X
    X_prime = scenario.treatment_variables[X].name.replace("'", "_prime")
    inputs = list(set([v.name for v in scenario.variables.values() if
                       isinstance(v, Input) and v.name not in (list(independence.Z) + [X])] + [X]))
    inputs_prime = [scenario.treatment_variables[x].name.replace("'", "_prime") for x in inputs]
    columns = inputs + [x for x in independence.Z if x != X] + inputs_prime
    assert len(set(inputs).intersection(inputs_prime)) == 0, f"{set(inputs).intersection(inputs_prime)} should be empty"
    assert len(inputs) == len(set(inputs)), f"Input names not unique {inputs} {count(inputs)}"
    assert len(inputs_prime) == len(
        set(inputs_prime)), f"Input prime names not unique {inputs_prime} {count(inputs_prime)}"
    assert len(columns) == len(set(columns)), f"Column names not unique {columns} {count(columns)}"
    samples = pd.DataFrame(
        lhsmdu.sample(len(columns), sample_size, randomSeed=seed).T,
        columns=columns,
    )
    for col in columns[:-len(inputs_prime)]:
        samples[col] = lhsmdu.inverseTransformSample(scenario.variables[col].distribution, samples[col])
    for x, x_prime in zip(inputs, inputs_prime):
        samples[x_prime] = lhsmdu.inverseTransformSample(scenario.treatment_variables[x].distribution, samples[x_prime])
    X_values = samples[inputs]
    X_prime_values = samples[inputs_prime]
    Z_values = samples[independence.Z]
    # assert False
    # assert len(x_values) == len(x_prime_values) == len(Z_values)
    return list(
        zip(
            X_values.to_dict(orient="records"),
            [{k.replace("_prime", ""): v for k, v in values.items()} for values in
             X_prime_values.to_dict(orient="records")],
            Z_values.to_dict(orient="records"),
            [independence.Y] * len(X_values),
            [independence] * len(X_values)
        )
    )


def construct_independence_test_suite(independences: List[ConditionalIndependence], scenario: Scenario):
    test_suite = []
    for independence in independences:
        test_suite += independence_metamorphic_tests(independence, scenario)
    return test_suite


def dependence_metamorphic_tests(
        edge: Tuple[str, str], scenario: Scenario, dag: CausalDAG, sample_size: int = 1, seed=0
):
    X = edge[0]
    X_prime = scenario.treatment_variables[X].name.replace("'", "_prime")

    adjustment_set = min([x for x in dag.direct_effect_adjustment_sets([edge[0]], [edge[1]]) if edge[1] not in x])

    inputs = list(set([v.name for v in scenario.variables.values() if isinstance(v, Input) and v.name != X] + list(
        adjustment_set)))
    assert X not in inputs, f"{X} should NOT be in {inputs}"
    columns = inputs + [X] + [X_prime]
    assert len(inputs) == len(set(inputs)), f"Input names not unique {inputs} {count(inputs)}"
    assert len(columns) == len(set(columns)), f"Column names not unique {columns} {count(columns)}"
    samples = pd.DataFrame(
        lhsmdu.sample(len(columns), sample_size, randomSeed=seed).T,
        columns=columns,
    )
    for col in columns[:-1]:
        samples[col] = lhsmdu.inverseTransformSample(scenario.variables[col].distribution, samples[col])
    samples[X_prime] = lhsmdu.inverseTransformSample(scenario.treatment_variables[X].distribution, samples[X_prime])
    X_values = samples[[X]]
    X_prime_values = samples[[X_prime]]
    other_inputs = samples[inputs]
    return list(
        zip(
            X_values.to_dict(orient="records"),
            [{k.replace("_prime", ""): v for k, v in values.items()} for values in
             X_prime_values.to_dict(orient="records")],
            other_inputs.to_dict(orient="records") if not other_inputs.empty else [{}] * len(X_values),
            [edge[1]] * len(X_values),
            [edge] * len(X_values),
            [adjustment_set] * len(X_values)
        )
    )


def construct_dependence_test_suite(edges: List[Tuple[str, str]], scenario: Scenario):
    test_suite = []
    for edge in edges:
        test = dependence_metamorphic_tests(edge, scenario, dag)
        assert len(test) > 0, "Must be at least one test"
        test_suite += test
    assert len(test_suite) == len(
        edges), f"Expected test suite to contain {len(edges)} tests but it actually contained {len(test_suite)}"
    return test_suite


args = get_dir_path()
dir_path = args.path
dir_module_path = dir_path + ".program"
dir_module_path = re.sub(r'[/\\]', '.', dir_module_path)  # replace slashes with . for module import

seed = 0
if args.seed is not None:
    seed = int(args.seed)
lhsmdu.setRandomSeed(seed)

program = import_module(dir_module_path).program  # Import program function from program module
dag = CausalDAG(str(Path(dir_path) / "DAG.dot"))

variables = [Input(x, float, uniform(0, 10)) for x in dag.graph.nodes if x.startswith("X")]
variables += [Output(y, float, uniform(0, 10)) for y in dag.graph.nodes if y.startswith("Y")]

independences = dag.list_conditional_independence_relationships(search_heuristic="min_direct")
independences = [i for i in independences if not i.Y.startswith("X")]

scenario = Scenario(set(variables))
scenario.setup_treatment_variables()

for run in construct_dependence_test_suite(dag.graph.edges, scenario):
    x_value, x_prime_value, other_inputs, y, independence, adjustment_set = run
    control = program(**(other_inputs | x_value))[y]
    treatment = program(**(other_inputs | x_prime_value))[y]
    if y == "Y8":
        print(run)
        print(control, treatment)
    assert control != treatment, f"Expected control {control} NOT to equal treatment {treatment} for\n{run}"


for run in construct_independence_test_suite(independences, scenario):
    x_value, x_prime_value, z_values, y, independence = run
    control = program(**(x_value | z_values))[y]
    treatment = program(**(x_prime_value | z_values))[y]
    assert control == treatment, f"Expected control {control} to equal treatment {treatment}"
