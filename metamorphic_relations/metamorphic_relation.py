"""Causal metamorphic relation classes."""
from abc import ABC, abstractmethod
from typing import List
import networkx as nx
from importlib import import_module
from itertools import combinations
import pandas as pd
import numpy as np


def count(lst):
    counts = {}
    for item in lst:
        if item not in counts:
            counts[item] = 0
        counts[item] += 1
    return counts


class CausalMetamorphicRelation(ABC):
    """A metamorphic relation base class."""

    def __init__(self, input_var: str, output_var: str, adjustment_list: List[str], dag: nx.DiGraph):
        self.input_var = input_var
        self.output_var = output_var
        self.adjustment_list = adjustment_list
        self.dag = dag

    def generate_tests(self, sample_size=1, seed=0):
        np.random.seed(seed)
        X = self.input_var
        X_prime = f"{self.input_var}_prime"

        inputs = list(set([v for v in self.dag.nodes if len(set(self.dag.predecessors(v))) == 0 and v != X] +
                          self.adjustment_list))
        assert X not in inputs, f"{X} should NOT be in {inputs}"
        columns = inputs + [X] + [X_prime]
        assert len(inputs) == len(set(inputs)), f"Input names not unique {inputs} {count(inputs)}"
        assert len(columns) == len(set(columns)), f"Column names not unique {columns} {count(columns)}"

        input_samples = pd.DataFrame(
            np.random.randint(-10, 10, size=(sample_size, len(inputs))),
            columns=sorted(inputs)
        )
        # Sample without replacement from the possible interventions
        candidate_interventions = np.array(list(combinations(range(-10, 11), 2)))
        random_intervention_indices = np.random.choice(candidate_interventions.shape[0], sample_size, replace=False)
        intervention_samples = pd.DataFrame(
            candidate_interventions[random_intervention_indices],
            columns=sorted([X] + [X_prime])
        )
        X_values = intervention_samples[[X]]
        X_prime_values = intervention_samples[[X_prime]]
        self.tests = list(
            zip(
                X_values.to_dict(orient="records"),
                [{k.replace("_prime", ""): v for k, v in values.items()} for values in
                 X_prime_values.to_dict(orient="records")],
                input_samples.to_dict(orient="records") if not input_samples.empty else [{}] * len(X_values),
                [self.output_var] * len(X_values),
                [self] * len(X_values)
            )
        )

    @abstractmethod
    def execute_tests(self, program, continue_after_failure=False) -> List[dict]:
        ...


class ShouldCause(CausalMetamorphicRelation):
    """A causal metamorphic relation asserting that changes to the input x should cause y to change when fixing the
    value of variables in the adjustment list.
    """

    def execute_tests(self, program, continue_after_failure=False) -> List[dict]:
        failures = []
        for run in self.tests:
            x_value, x_prime_value, other_inputs, y, independence = run
            control = program(**(other_inputs | x_value))[y]
            treatment = program(**(other_inputs | x_prime_value))[y]
            ok = control != treatment
            if not continue_after_failure:
                assert ok, f"Expected control {control} NOT to equal treatment {treatment} for\n{run}"
            if not ok:
                failures.append({
                    "control_inputs": (other_inputs | x_value),
                    "control_outcome": control,
                    "treatment_inputs": (other_inputs | x_prime_value),
                    "treatment_outcome": treatment
                })

        return failures

    def __str__(self):
        metamorphic_relation_str = f"{self.input_var} --> {self.output_var}"
        if self.adjustment_list:
            metamorphic_relation_str += f" | {self.adjustment_list}"
        return metamorphic_relation_str

    def __repr__(self):
        return self.__str__()


class ShouldNotCause(CausalMetamorphicRelation):
    """A causal metamorphic relation asserting that changes to the input x should not cause y to change when fixing the
    value of variables in the adjustment list.
    """

    def execute_tests(self, program, continue_after_failure=False) -> List[str]:
        failures = []
        for run in self.tests:
            x_value, x_prime_value, other_inputs, y, independence = run
            control = program(**(other_inputs | x_value))[y]
            treatment = program(**(other_inputs | x_prime_value))[y]
            ok = control == treatment
            if not continue_after_failure:
                assert ok, f"Expected control {control} to equal treatment {treatment} for\n{run}"
            if not ok:
                failures.append({
                    "control_inputs": (other_inputs | x_value),
                    "control_outcome": control,
                    "treatment_inputs": (other_inputs | x_prime_value),
                    "treatment_outcome": treatment
                })
            return failures

    def __str__(self):
        metamorphic_relation_string = f"{self.input_var} ⫫ {self.output_var}"
        if self.adjustment_list:
            metamorphic_relation_string += f" | {self.adjustment_list}"
        return metamorphic_relation_string

    def __repr__(self):
        return self.__str__()
