from typing import List
import lhsmdu
import pytest
import pandas as pd
from scipy.stats import uniform

from causal_testing.specification.conditional_independence import ConditionalIndependence
from causal_testing.specification.scenario import Scenario
from causal_testing.specification.variable import Input
from causal_testing.specification.causal_dag import CausalDAG


def metamorphic_tests(
    independence: ConditionalIndependence, scenario: Scenario, confidence: float = 0.95, sample_size: int = 30, seed=0
):
    x = independence.X
    x_prime = scenario.treatment_variables[independence.X].name
    columns = list(independence.Z) + [x, x_prime]
    samples = pd.DataFrame(
        lhsmdu.sample(len(columns), sample_size, randomSeed=seed).T,
        columns=columns,
    )
    for col in columns[:-1]:
        samples[col] = lhsmdu.inverseTransformSample(scenario.variables[col].distribution, samples[col])
    samples[x_prime] = lhsmdu.inverseTransformSample(scenario.treatment_variables[x].distribution, samples[x_prime])
    x_values = samples[x]
    x_prime_values = samples[x_prime]
    Z_values = samples[independence.Z]
    assert len(x_values) == len(x_prime_values) == len(Z_values)
    return list(
        zip(
            pd.DataFrame(x_values).to_dict(orient="records"),
            pd.DataFrame(x_prime_values).to_dict(orient="records"),
            Z_values.to_dict(orient="records"),
            independence.Y * len(x_values),
        )
    )


def construct_test_suite(independences: List[ConditionalIndependence], scenario: Scenario):
    test_suite = []
    for independence in independences:
        print(metamorphic_tests(independence, scenario))
        test_suite += metamorphic_tests(independence, scenario)
    return test_suite


"""
    This will obviously have to be replaced by a call to run whatever model needs to be run.
"""
def run_model(**kwargs):
    return {"Y": 0}


independence = ConditionalIndependence("X", "Y", ["A", "B"])
X = Input("X", float, uniform(0, 10))
Y = Input("Y", float, uniform(0, 10))
A = Input("A", float, uniform(0, 10))
B = Input("B", float, uniform(0, 10))
scenario = Scenario({X, Y, A, B})
scenario.setup_treatment_variables()


@pytest.mark.parametrize("run", construct_test_suite([independence], scenario))
def test_independence(run):
    x_value, x_prime_value, z_values, y = run
    control = run_model(**(x_value | z_values))[y]
    treatment = run_model(**(x_prime_value | z_values))[y]
    assert control == treatment, f"Expected control {control} to equal treatment {treatment}"


if __name__ == "__main__":
    dag_dot = """digraph G { A -> B; B -> C; D -> A; D -> C}"""
    with open("dag.dot", "w") as f:
        f.write(dag_dot)
    dag = CausalDAG("dag.dot")
    independences = dag.list_conditional_independence_relationships(search_heuristic="minimal")

    A = Input("A", float, uniform(0, 10))
    B = Input("B", float, uniform(0, 10))
    C = Input("C", float, uniform(0, 10))
    D = Input("D", float, uniform(0, 10))
    scenario = Scenario({A, B, C, D})
    scenario.setup_treatment_variables()
    print(construct_test_suite(independences, scenario))
