"""
Class for managing custom score objects (e.g., "+20%").
"""
import re

SCORE_PATTERN = re.compile(r"(\!*)([\+\-\/\*])?([\d\.]+)(\%)?(.*)")

class Score:
    def __init__(self, invert, operator, value, percentage, leftovers):
        self.invert = invert
        self.operator = operator
        self.value = value
        self.percentage = percentage
        self.leftovers = leftovers

    @classmethod
    def parse(cls, score):
        match = SCORE_PATTERN.match(score)
        if not match:
            # TODO: Add context of feedback being processed
            raise ValueError(f"Invalid Score string: {score}")
        invert = bool(len(match.group(1)) % 2)
        operator = match.group(2)
        value = float(match.group(3))
        percentage = bool(match.group(4) == "%")
        leftovers = match.group(5)
        if percentage:
            value = value / 100.0
        return Score(invert, operator, value, percentage, leftovers)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Score(self.invert, self.operator, self.value/other, self.percentage, self.leftovers)
        return NotImplemented(f"Division is not supported between a Score and a {type(other)}")

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Score(self.invert, self.operator, self.value*other, self.percentage, self.leftovers)
        return NotImplemented(f"Multiplication is not supported between a Score and a {type(other)}")

    def __rmul__(self, other):
        return self.__mul__(other)

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return Score(self.invert, self.operator, self.value+other, self.percentage, self.leftovers)
        return NotImplemented(f"Addition is not supported between a Score and a {type(other)}")

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return Score(self.invert, self.operator, self.value-other, self.percentage, self.leftovers)
        return NotImplemented(f"Subtraction is not supported between a Score and a {type(other)}")

    def __str__(self):
        value = self.value
        if self.percentage:
            # TODO: Being careless with rounding here.
            value *= 100
        value = str(round(value))
        return (
            ("!" if self.invert else "")+self.operator+value+
            ("%" if self.percentage else "")+self.leftovers
        )

    def add_to_current(self, current):
        if self.operator in ("+", None, "") and not self.invert:
            current += self.value
        elif self.operator == "-" and not self.invert:
            current -= self.value
        elif self.operator == "*" and not self.invert:
            current *= self.value
        elif self.operator == "/" and not self.invert:
            current /= self.value
        return current


def combine_scores(scores, invert_scores=None) -> float:
    """
    Combines the scores (and possible invert_scores) into a single number.
    Args:
        scores ():
        invert_scores ():

    Returns:

    """
    total = 0
    for score in scores:
        if isinstance(score, (int, float)):
            total += score
        elif isinstance(score, str):
            total = Score.parse(score).add_to_current(total)
    if invert_scores:
        for score in invert_scores:
            if isinstance(score, str):
                total = Score.parse("!"+score).add_to_current(total)
    return round(total, 2)
