class Model:
    def __init__(self, elements, operators, delimiters):
        f"""
        :param elements: digits or fixed variables of the model, usually : e, 1, 2, 3, 4, 5...
        :param operators: dict(Operator1: function, ...)
        :param delimiters: [left_delimiter, right_delimiter] from symbol
        """
        self.elements = elements
        self.l_delimiter, self.r_delimiter = delimiters
        self.operators = operators

    def operators_char(self, priority=None):
        ops_char = []
        for op in self.operators.keys():
            if priority is None or op.priority == priority:
                ops_char.append(op.c)
        return ops_char

    def isdigit(self, char):
        return char in self.elements

    def operation(self, symbol):
        for op in self.operators.keys():
            if op.c == symbol:
                return self.operators[op]

    def l_delimiter_char(self):
        return self.l_delimiter.c

    def r_delimiter_char(self):
        return self.r_delimiter.c