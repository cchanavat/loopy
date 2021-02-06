from itertools import product
from lib.parser import *
from lib.axiom import *


class Model:
    def __init__(self, table, operators, delimiters):
        f"""
        :param elements: digits or fixed variables of the model, usually : e, 1, 2, 3, 4, 5...
        :param operators: dict(Operator1: function, ...)
        :param delimiters: [left_delimiter, right_delimiter] from symbol
        """
        self.table = table
        self.elements = self.table.elements
        self.l_delimiter, self.r_delimiter = delimiters
        self.operators = operators
        self.parser = Parser(self)

    def operators_char(self, priority=None):
        ops_char = []
        for op in self.operators.keys():
            if priority is None or op.priority == priority:
                ops_char.append(op.c)
        return ops_char

    def isdigit(self, char):
        return char in self.table.elements

    def operation(self, symbol):
        for op in self.operators.keys():
            if op.c == symbol:
                return self.operators[op]

    def l_delimiter_char(self):
        return self.l_delimiter.c

    def r_delimiter_char(self):
        return self.r_delimiter.c

    def evaluate(self, expr):
        """
        :param expr: string expression that will be evaluate
        :return: the evaluate expression
        e.g. in the model of (Z/3Z, +) "evaluate(1+1+1)" return 0
        """
        return self.parser.evaluate(expr)

    def equal(self, a, b):
        return self.evaluate(a) == self.evaluate(b)

    @staticmethod
    def instantiate(expr, var, elements):
        """
        :param expr: expression to instantiate
        :param var: ordered variables that will be replaced
        :param elements: ordered elements that will replace the variables
        :return: the new expression
        """
        new_expr = expr
        for v, e in zip(var, elements):
            new_expr = new_expr.replace(v, e)
        return new_expr

    def is_true(self, axiom: Axiom):
        """
        :param axiom: axiom we want to check
        :return: whether or not this particular axiom is true in this model
        """
        var = axiom.variables
        left = axiom.left
        right = axiom.right
        n = len(var)
        if n == 0:
            return self.equal(left, right)

        for elts in product(self.elements, repeat=n):
            left_instance = self.instantiate(left, var, elts)
            right_instance = self.instantiate(right, var, elts)
            if not self.equal(left_instance, right_instance):
                return False

        return True

