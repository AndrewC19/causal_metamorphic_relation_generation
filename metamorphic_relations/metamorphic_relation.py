"""Causal metamorphic relation classes."""
from abc import ABC, abstractmethod
from typing import List
from itertools import combinations
import networkx as nx
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
        self.adjustment_list = sorted(adjustment_list)
        self.dag = dag
        self.tests = None

    def generate_tests(self, sample_size=1, seed=0):
        np.random.seed(seed)
        source_input = self.input_var
        follow_up_input = f"{self.input_var}_prime"

        # Get all input values apart from the source_input and the adjustment list
        test_inputs = set()
        for node in self.dag.nodes:
            if ("X" in node) and (node != source_input):
                test_inputs.add(node)
        test_inputs = list(test_inputs | set(self.adjustment_list))

        assert source_input not in test_inputs, f"{source_input} should NOT be in {test_inputs}"
        assert len(test_inputs) == len(set(test_inputs)), f"Input names not unique {test_inputs} {count(test_inputs)}"

        # Assign random values to inputs between -10 and 10
        input_samples = pd.DataFrame(
            np.random.randint(-10, 10, size=(sample_size, len(test_inputs))),
            columns=sorted(test_inputs)
        )

        # Sample without replacement from the possible interventions (source and follow-up input pairs)
        candidate_interventions = np.array(list(combinations(range(-10, 11), 2)))
        random_intervention_indices = np.random.choice(candidate_interventions.shape[0], sample_size, replace=False)
        intervention_samples = pd.DataFrame(
            candidate_interventions[random_intervention_indices],
            columns=sorted([source_input] + [follow_up_input])
        )
        source_input_values = intervention_samples[[source_input]]
        follow_up_input_values = intervention_samples[[follow_up_input]]

        # Generate test tuples comprising source and follow-up inputs (interventions)
        self.tests = list(
            zip(
                source_input_values.to_dict(orient="records"),
                [{k.replace("_prime", ""): v for k, v in values.items()} for values in
                 follow_up_input_values.to_dict(orient="records")],
                input_samples.to_dict(orient="records") if not input_samples.empty else [{}] * len(source_input_values),
                [self.output_var] * len(source_input_values),
                [self] * len(source_input_values)
            )
        )

    def execute_tests(self, program ) -> List[dict]:
        failures = []
        for run in self.tests:
            source_input, follow_up_input, other_inputs, output, independence = run
            control = program(**(other_inputs | source_input))[output]
            treatment = program(**(other_inputs | follow_up_input))[output]
            if not self.assertion(control, treatment, run):
                failures.append({
                    "source_inputs": (other_inputs | source_input),
                    "source_outcome": control,
                    "follow_up_inputs": (other_inputs | follow_up_input),
                    "follow_up_outcome": treatment
                })

        return failures

    @abstractmethod
    def assertion(self, source_output, follow_up_output, run):
        """An assertion that is to be applied to an individual metamorphic test run."""
        ...

    @abstractmethod
    def oracle(self, test_failures):
        """An oracle procedure that determines whether the MR holds or not based on the test failures."""
        ...


class ShouldCause(CausalMetamorphicRelation):
    """A causal metamorphic relation asserting that changes to the input x should cause y to change when fixing the
    value of variables in the adjustment list.
    """

    def assertion(self, source_output, follow_up_output, run):
        return source_output != follow_up_output

    def oracle(self, test_failures):
        assert len(test_failures) < len(self.tests), f"{str(self)}: {len(test_failures)}/{len(self.tests)} tests failed."

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

    def assertion(self, source_output, follow_up_output, run):
        return source_output == follow_up_output

    def oracle(self, test_failures):
        assert len(test_failures) == 0, f"{str(self)} failed: {len(test_failures)}/{len(self.tests)} tests failed."

    def __str__(self):
        metamorphic_relation_string = f"{self.input_var} _||_ {self.output_var}"
        if self.adjustment_list:
            metamorphic_relation_string += f" | {self.adjustment_list}"
        return metamorphic_relation_string

    def __repr__(self):
        return self.__str__()
