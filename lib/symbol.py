from enum import Enum

"""
    Symbol
        - variable
        - operator
        - delimiter
"""

# delimiter are not handled
__LEFT_DELIMITER__ = ['(', '[', '{']
__RIGHT_DELIMITER__ = [')', ']', '}']
__DELIMITER__ = __LEFT_DELIMITER__ + __RIGHT_DELIMITER__


class Symbol:
    def __init__(self):
        pass

    def __str__(self):
        pass


class Delimiter(Symbol):
    def __init__(self, c):
        super().__init__()
        if c in __LEFT_DELIMITER__:
            self.c = '('
        elif c in __RIGHT_DELIMITER__:
            self.c = ')'
        else:
            raise Exception("{} is a wrong delimiter".format(c))

    def __str__(self):
        return str(self.c)


class Operator(Symbol):
    def __init__(self, c, notation, arity, priority):
        super().__init__()
        self.notation = notation
        self.c = c
        self.arity = arity
        self.priority = priority

    def __str__(self):
        return str(self.c)


class Variable(Symbol):
    def __init__(self, c):
        super().__init__()
        self.c = c

    def __str__(self):
        return str(self.c)


class Notation(Enum):
    POSTFIX = 0
    INFIX = 1
    PREFIX = 2


class Priority(Enum):
    HIGH = 0
    LOW = 1
