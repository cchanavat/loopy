from lib.symbol import *

# inspiration from https://tomekkorbak.com/2020/03/25/implementing-shunting-yard-parsing/


class Node:
    def __init__(self, symbol, left, right):
        self.symbol = symbol
        self.left = left
        self.right = right

    def is_leaf(self) -> bool:
        return self.left is None and self.right is None


class Parser:
    def __init__(self, model):
        """
            :param expr: expression to parse
            :param model: model used, see the class Model
        """
        self.model = model
        self.tokenized = []

    def evaluate(self, expr):
        tree = self.build(expr)
        return self.unfold(tree)

    def tokenize(self, expr):
        expr = ''.join(expr.split()) # let's remove the spaces
        tokenized = []
        prev = ''
        for char in expr:
            if self.model.isdigit(prev) and self.model.isdigit(char):
                tokenized.append(self.tokenized.pop() + char)
            else:
                tokenized.append(char)
            prev = char
        return tokenized

    def unfold(self, node):
        if node.is_leaf():
            return node.symbol
        else:
            op = self.model.operation(node.symbol)
            return op(self.unfold(node.left), self.unfold(node.right))

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


