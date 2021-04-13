from enum import Enum


class Symbol:
    def __init__(self, symbol_repr, symbol_type, symbol_name):
        self.repr = symbol_repr
        self.type = symbol_type
        self.name = symbol_name
        self.is_variable = False

    def __str__(self):
        return str(self.repr)

    def __repr__(self):
        return str(self)


class Variable(Symbol):
    def __init__(self, name, quantification):
        super().__init__(name, SymbolType.OPERAND, name)
        self.quantification = quantification
        self.is_variable = True

    def __repr__(self):
        return str(self)


class SymbolType(Enum):
    OPERAND = 0
    OPERATOR = 1
    LDELIMITER = 2
    RDELIMITER = 3
    UNIVERSAL_QUANTIFIER = 4
    EXISTENTIAL_QUANTIFIER = 5
