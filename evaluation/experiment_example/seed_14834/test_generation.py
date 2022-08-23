from typing import List
import lhsmdu
import pytest
import pandas as pd
from scipy.stats import uniform
from program import program

from causal_testing.specification.conditional_independence import ConditionalIndependence
from causal_testing.specification.scenario import Scenario
from causal_testing.specification.variable import Input, Output
from causal_testing.specification.causal_dag import CausalDAG

pd.set_option('display.max_columns', 500)

def count(lst):
    counts = {}
    for item in lst:
        if item not in counts:
            counts[item] = 0
        counts[item] += 1
    return counts

def metamorphic_tests(
    independence: ConditionalIndependence, scenario: Scenario, confidence: float = 0.95, sample_size: int = 1, seed=0
):
    print(independence)
    X = independence.X
    X_prime = scenario.treatment_variables[X].name.replace("'", "_prime")
    inputs = list(set([v.name for v in scenario.variables.values() if isinstance(v, Input) and v.name not in (list(independence.Z) + [X])] + [X]))
    inputs_prime = [scenario.treatment_variables[x].name.replace("'", "_prime") for x in inputs]
    columns = inputs + [x for x in independence.Z if x != X] + inputs_prime
    assert len(set(inputs).intersection(inputs_prime)) == 0, f"{set(inputs).intersection(inputs_prime)} should be empty"
    assert len(inputs) == len(set(inputs)), f"Input names not unique {inputs} {count(inputs)}"
    assert len(inputs_prime) == len(set(inputs_prime)), f"Input prime names not unique {inputs_prime} {count(inputs_prime)}"
    assert len(columns) == len(set(columns)), f"Column names not unique {columns} {count(columns)}"
    samples = pd.DataFrame(
        lhsmdu.sample(len(columns), sample_size, randomSeed=seed).T,
        columns=columns,
    )
    print(samples)
    for col in columns[:-len(inputs_prime)]:
        print(col)
        samples[col] = lhsmdu.inverseTransformSample(scenario.variables[col].distribution, samples[col])
    for x, x_prime in zip(inputs, inputs_prime):
        samples[x_prime] = lhsmdu.inverseTransformSample(scenario.treatment_variables[x].distribution, samples[x_prime])
    X_values = samples[inputs]
    X_prime_values = samples[inputs_prime]
    Z_values = samples[independence.Z]
    print(samples)
    print("x_values", X_values.to_dict(orient="records"))
    print("x_prime_values", [{k.replace("_prime", ""): v for k, v in values.items()} for values in X_prime_values.to_dict(orient="records")],)
    # assert False
    # assert len(x_values) == len(x_prime_values) == len(Z_values)
    return list(
        zip(
            X_values.to_dict(orient="records"),
            [{k.replace("_prime", ""): v for k, v in values.items()} for values in X_prime_values.to_dict(orient="records")],
            Z_values.to_dict(orient="records"),
            [independence.Y] * len(X_values),
            [independence] * len(X_values)
        )
    )


def construct_test_suite(independences: List[ConditionalIndependence], scenario: Scenario):
    test_suite = []
    for independence in independences:
        print(metamorphic_tests(independence, scenario))
        test_suite += metamorphic_tests(independence, scenario)
    return test_suite


dag = CausalDAG("DAG.dot")

variables = [Input(x, float, uniform(0, 10)) for x in dag.graph.nodes if x.startswith("X")]
variables += [Output(y, float, uniform(0, 10)) for y in dag.graph.nodes if y.startswith("Y")]

independences = dag.list_conditional_independence_relationships(search_heuristic="min_direct")
independences = [i for i in independences if not i.Y.startswith("X")]

scenario = Scenario(set(variables))
scenario.setup_treatment_variables()


@pytest.mark.parametrize("run", construct_test_suite(independences, scenario))
def test_independence(run):
    x_value, x_prime_value, z_values, y, independence = run
    control = program(**(x_value | z_values))[y]
    treatment = program(**(x_prime_value | z_values))[y]
    assert control == treatment, f"Expected control {control} to equal treatment {treatment}"

if __name__ == "__main__":
    print("independences", independences)
