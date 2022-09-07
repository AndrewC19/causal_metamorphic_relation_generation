"""Causal metamorphic relation classes."""
from abc import ABC, abstractmethod
from typing import List


class CausalMetamorphicRelation(ABC):
    """A metamorphic relation base class."""

    def __init__(self, input_var: str, output_var: str, adjustment_list: List[str]):
        self.input_var = input_var
        self.output_var = output_var
        self.adjustment_list = adjustment_list

    @abstractmethod
    def generate_tests(self):
        ...

    @abstractmethod
    def execute_tests(self):
        ...


class ShouldCause(CausalMetamorphicRelation):
    """A causal metamorphic relation asserting that changes to the input x should cause y to change when fixing the
       value of variables in the adjustment list.
    """

    def generate_tests(self):
        ...

    def execute_tests(self):
        ...

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

    def generate_tests(self):
        ...

    def execute_tests(self):
        ...

    def __str__(self):
        metamorphic_relation_string = f"{self.input_var} ⫫ {self.output_var}"
        if self.adjustment_list:
            metamorphic_relation_string += f" | {self.adjustment_list}"
        return metamorphic_relation_string

    def __repr__(self):
        return self.__str__()
