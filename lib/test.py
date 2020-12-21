import numpy as np
from lib.parser import *
from lib.table import *
from lib.symbol import *


# Some of the variables
var_e = Variable('e')
var_u = Variable('u')
var_v = Variable('v')
var_w = Variable('w')
var_x = Variable('x')
var_y = Variable('y')
var_z = Variable('z')

# Operator
star = Operator('*', Notation.INFIX, 2, Priority.LOW)
dot = Operator('.', Notation.INFIX, 2, Priority.HIGH)
left = Operator('\\', Notation.INFIX, 2, Priority.LOW)
right = Operator('/', Notation.INFIX, 2, Priority.LOW)

implies = Operator('>', Notation.INFIX, 2, Priority.LOW)
eq = Operator('=', Notation.INFIX, 2, Priority.LOW)
neq = Operator('^', Notation.INFIX, 2, Priority.LOW)
and_ = Operator('&', Notation.INFIX, 2, Priority.LOW)
or_ = Operator('|', Notation.INFIX, 2, Priority.LOW)

# Delimiter
lp = Delimiter('(')
rp = Delimiter(')')


def a(x, y, z):
    s = r"({x}*({y}*{z}))\(({x}*{y})*{z})".format(x=x, y=y, z=z)
    return s


def K(x, y):
    s = r"({y}*{x})\({x}*{y})".format(x=x, y=y)
    return s


delimiters = [lp, rp]

table_Z3_ = np.array([['e', '1', '2'],
                      ['1', '2', 'e'],
                      ['2', 'e', '1']])

table_Z3 = Table(table_Z3_, ['e', '1', '2'])

operators = {star: table_Z3.mul,
             dot: table_Z3.mul}

model_Z3 = Model(table_Z3.elements, operators, delimiters)
parser_Z3 = Parser(model_Z3)

# print(parser_Z3.evaluate("1*e.2"))
# print(parser_Z3.evaluate("1*e.2.2.e"))

table_D3_ = np.array([['e', 'a', 'b', 'c', 'd', 'f'],
                      ['a', 'e', 'd', 'f', 'b', 'c'],
                      ['b', 'f', 'e', 'd', 'c', 'a'],
                      ['c', 'd', 'f', 'e', 'a', 'b'],
                      ['d', 'c', 'a', 'b', 'f', 'e'],
                      ['f', 'b', 'c', 'a', 'e', 'd']])


table_D3 = Table(table_D3_)
operators = {star: table_D3.mul,
             dot: table_D3.mul,
             left: table_D3.ldiv,
             right: table_D3.rdiv}

model_D3 = Model(table_D3.elements, operators, delimiters)
parser_D3 = Parser(model_D3)

print(table_D3, '\n')

for expr in ["a.b", "a*b", "b.a", "a/a", r"e\a", r"d/b\a", "(a*a)", r"(a.a)\d", "d.a", r"c\d", "e/e.d", r"d.a\a", r"(d.a)\a"]:
    print(expr, ' = ', parser_D3.evaluate(expr))
