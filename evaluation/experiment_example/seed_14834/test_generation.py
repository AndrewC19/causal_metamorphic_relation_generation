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


def metamorphic_tests(
    independence: ConditionalIndependence, scenario: Scenario, confidence: float = 0.95, sample_size: int = 30, seed=0
):
    X = sorted(list(scenario.variables))
    X_prime = [scenario.treatment_variables[x].name for x in X]
    columns = X + X_prime
    samples = pd.DataFrame(
        lhsmdu.sample(len(columns), sample_size, randomSeed=seed).T,
        columns=columns,
    )
    print(samples)
    print(samples.columns)
    for col in X:
        samples[col] = lhsmdu.inverseTransformSample(scenario.variables[col].distribution, samples[col])
    for col in X:
        col_prime = scenario.treatment_variables[col].name
        samples[col_prime] = lhsmdu.inverseTransformSample(
            scenario.treatment_variables[col].distribution, samples[col_prime]
        )
    print(samples)
    x_values = samples[X]
    x_prime_values = {x[:-1]: v for x, v in samples[X_prime].items()}
    Z_values = samples[independence.Z]
    # assert len(x_values) == len(x_prime_values) == len(Z_values)
    return list(
        zip(
            pd.DataFrame(x_values).to_dict(orient="records"),
            pd.DataFrame(x_prime_values).to_dict(orient="records"),
            Z_values.to_dict(orient="records"),
            [independence.Y] * len(x_values),
            [independence] * len(x_values)
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

independences = dag.list_conditional_independence_relationships(search_heuristic="maximal")
independences = [i for i in independences if not i.Y.startswith("X")]

print(len(independences), "independences")


scenario = Scenario(set(variables))
scenario.setup_treatment_variables()


@pytest.mark.parametrize("run", construct_test_suite(independences, scenario))
def test_independence(run):
    print(run)
    x_value, x_prime_value, z_values, y, independence = run
    print(run)
    print(independence.Y)
    control = program(**(x_value | z_values))[y]
    treatment = program(**(x_prime_value | z_values))[y]
    assert control == treatment, f"Expected control {control} to equal treatment {treatment}"
