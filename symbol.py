from enum import Enum


class Symbol:
    def __init__(self, symbol_repr, symbol_type):
        self.repr = symbol_repr
        self.type = symbol_type


class SymbolType(Enum):
    OPERAND = 0
    OPERATOR = 1
    QUANTIFIER = 2
    DELIMITER = 3

