"""Causal metamorphic relation classes."""
from abc import ABC, abstractmethod
from typing import List
import networkx as nx
from importlib import import_module
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

    def __init__(self, input_var: str, output_var: str, adjustment_list: List[str], dir_module_path: str, dag: str):
        self.input_var = input_var
        self.output_var = output_var
        self.adjustment_list = adjustment_list
        self.dag = nx.DiGraph(nx.nx_pydot.read_dot(dag))
        self.program = import_module(dir_module_path).program  # Import program function from program module

    def generate_tests(self, sample_size=1):
        ...

    @abstractmethod
    def execute_tests(self):
        ...


class ShouldCause(CausalMetamorphicRelation):
    """A causal metamorphic relation asserting that changes to the input x should cause y to change when fixing the
    value of variables in the adjustment list.
    """
    
    def generate_tests(self, sample_size=1):
        X = self.input_var
        X_prime = f"{self.input_var}_prime"
    
        inputs = list(set([v for v in self.dag.nodes if len(set(self.dag.predecessors(v))) == 0 and v != X] +
            self.adjustment_list))
        assert X not in inputs, f"{X} should NOT be in {inputs}"
        columns = inputs + [X] + [X_prime]
        assert len(inputs) == len(set(inputs)), f"Input names not unique {inputs} {count(inputs)}"
        assert len(columns) == len(set(columns)), f"Column names not unique {columns} {count(columns)}"
        samples = pd.DataFrame(
            np.random.rand(sample_size, len(columns)),
            columns=columns,
        )
        for col in columns[:-1]:
            samples[col] = samples[col] * 10
        samples[X_prime] = samples[X_prime] * 10
        X_values = samples[[X]]
        X_prime_values = samples[[X_prime]]
        other_inputs = samples[inputs]
        self.tests = list(
            zip(
                X_values.to_dict(orient="records"),
                [{k.replace("_prime", ""): v for k, v in values.items()} for values in
                 X_prime_values.to_dict(orient="records")],
                other_inputs.to_dict(orient="records") if not other_inputs.empty else [{}] * len(X_values),
                [self.output_var] * len(X_values),
                [self] * len(X_values)
            )
        )


    def execute_tests(self):
        for run in self.tests:
            x_value, x_prime_value, other_inputs, y, independence = run
            control = self.program(**(other_inputs | x_value))[y]
            treatment = self.program(**(other_inputs | x_prime_value))[y]
            assert control != treatment, f"Expected control {control} NOT to equal treatment {treatment} for\n{run}"

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

    def generate_tests(self, sample_size=1):
        X = self.input_var
        inputs = list(set([v for v in self.dag.nodes if
                           len(list(self.dag.predecessors(v))) == 0 and v not in (self.adjustment_list + [X])] + [X]))
        inputs_prime = [f"{x}_prime" for x in inputs]
        columns = inputs + [x for x in self.adjustment_list if x != X] + inputs_prime
        assert len(set(inputs).intersection(inputs_prime)) == 0, f"{set(inputs).intersection(inputs_prime)} should be empty"
        assert len(inputs) == len(set(inputs)), f"Input names not unique {inputs} {count(inputs)}"
        assert len(inputs_prime) == len(
            set(inputs_prime)), f"Input prime names not unique {inputs_prime} {count(inputs_prime)}"
        assert len(columns) == len(set(columns)), f"Column names not unique {columns} {count(columns)}"
        samples = pd.DataFrame(
            np.random.rand(sample_size, len(columns)),
            columns=columns,
        )
        for col in columns:
            samples[col] = samples[col] * 10
        X_values = samples[inputs]
        X_prime_values = samples[inputs_prime]
        Z_values = samples[self.adjustment_list]
        # assert False
        # assert len(x_values) == len(x_prime_values) == len(Z_values)
        self.tests = list(
            zip(
                X_values.to_dict(orient="records"),
                [{k.replace("_prime", ""): v for k, v in values.items()} for values in
                 X_prime_values.to_dict(orient="records")],
                Z_values.to_dict(orient="records") if not Z_values.empty else [{}] * len(X_values),
                [self.output_var] * len(X_values),
                [self] * len(X_values)
            )
        )

    def execute_tests(self):
        for run in self.tests:
            x_value, x_prime_value, other_inputs, y, independence = run
            control = self.program(**(other_inputs | x_value))[y]
            treatment = self.program(**(other_inputs | x_prime_value))[y]
            assert control == treatment, f"Expected control {control} to equal treatment {treatment} for\n{run}"

    def __str__(self):
        metamorphic_relation_string = f"{self.input_var} ⫫ {self.output_var}"
        if self.adjustment_list:
            metamorphic_relation_string += f" | {self.adjustment_list}"
        return metamorphic_relation_string

    def __repr__(self):
        return self.__str__()


if __name__ == "__main__":
    should_cause = ShouldCause(
        input_var="X1",
        output_var="Y1",
        adjustment_list=[],
        dir_module_path="evaluation.single_experiment.seed_17612.program",
        dag="evaluation/single_experiment/seed_17612/DAG.dot",
    )
    should_cause.generate_tests()
    should_cause.execute_tests()
    
    should_not_cause = ShouldNotCause(
        input_var="X3",
        output_var="Y1",
        adjustment_list=["X1"],
        dir_module_path="evaluation.single_experiment.seed_17612.program",
        dag="evaluation/single_experiment/seed_17612/DAG.dot",
    )
    should_not_cause.generate_tests()
    should_not_cause.execute_tests()
