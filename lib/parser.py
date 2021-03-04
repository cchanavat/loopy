from lib.symbol import *


# inspiration from https://tomekkorbak.com/2020/03/25/implementing-shunting-yard-parsing/


class Node:
    def __init__(self, symbol, left, right):
        self.symbol = symbol
        self.left = left
        self.right = right

    def is_leaf(self) -> bool:
        return self.left is None and self.right is None

    def __str__(self):
        if self.is_leaf():
            return str(self.symbol)
        return "{s} -> ({l}, {r})".format(s=str(self.symbol), l=str(self.left), r=str(self.right))


class Parser(Exception):
    def __init__(self, model):
        """
            :param model: model used, see the class Model
        """
        self.model = model

    def evaluate(self, expr):
        """
        Build the expression's tree and return the unfold evaluation
        :param expr: expression to evaluate
        :return: evaluation of the sentence according to the model
        """
        tree = self.build(expr)
        return self.unfold(tree)

    def tokenize(self, expr):
        expr = ''.join(expr.split())  # let's remove the spaces
        tokenized = []
        prev = ''
        for char in expr:
            if self.model.isdigit(prev) and self.model.isdigit(char):
                tokenized.append(tokenized.pop() + char)
            else:
                tokenized.append(char)
            prev = char
        return tokenized

    def unfold(self, node, map_var_to_element=None):
        if node.is_leaf():
            if map_var_to_element is not None:
                return map_var_to_element[node.symbol]
            return node.symbol
        else:
            op = self.model.operation(node.symbol)
            return op(self.unfold(node.left, map_var_to_element), self.unfold(node.right, map_var_to_element))

    def build(self, expr):
        tokenized = self.tokenize(expr)
        operator_stack = []
        operand_stack = []

        for char in tokenized:
            if self.model.isdigit(char):
                operand_stack.append(Node(char, None, None))
            elif char in self.model.operators_char(Priority.LOW) and len(operator_stack) > 0 \
                    and operator_stack[-1] in self.model.operators_char(Priority.HIGH):
                right = operand_stack.pop()
                op = operator_stack.pop()
                left = operand_stack.pop()
                operand_stack.append(Node(op, left, right))
                operator_stack.append(char)
            elif char == self.model.r_delimiter_char():
                while len(operator_stack) > 0 and operator_stack[-1] != self.model.l_delimiter_char():
                    right = operand_stack.pop()
                    op = operator_stack.pop()
                    left = operand_stack.pop()
                    operand_stack.append(Node(op, left, right))
                operator_stack.pop()
            else:
                operator_stack.append(char)
        while len(operator_stack) > 0:
            right = operand_stack.pop()
            op = operator_stack.pop()
            left = operand_stack.pop()
            operand_stack.append(Node(op, left, right))
        return operand_stack.pop()
