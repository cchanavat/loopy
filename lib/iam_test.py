from numpy.random import RandomState
from lib.model import *
from lib.table import *
from lib.symbol import *
from lib.loop import *

star = Operator('*', Notation.INFIX, 2, Priority.LOW)
dot = Operator('.', Notation.INFIX, 2, Priority.HIGH)
left = Operator('\\', Notation.INFIX, 2, Priority.LOW)
right = Operator('/', Notation.INFIX, 2, Priority.LOW)

# Delimiter
lp = Delimiter('(')
rp = Delimiter(')')

delimiters = [lp, rp]


# TEST LOOP THEORY
lid = Axiom("0*x", "x", ['x'], "lid")
rid = Axiom("x*0", "x", ['x'], "rid")
b1 = Axiom("x\\(x*y)", "y", ['x', 'y'], "b1")
b2 = Axiom("x*(x\\y)", "y", ['x', 'y'], "b2")
s1 = Axiom("(x*y)/y", "x", ['x', 'y'], "s1")
s2 = Axiom("(x/y)*y", "x", ['x', 'y'], "s2")

loop_axioms = [lid, rid, b1, b2, s1, s2]


def a(x, y, z):
    s = r"({x}*({y}*{z}))\(({x}*{y})*{z})".format(x=x, y=y, z=z)
    return s


def K(x, y):
    s = r"({y}*{x})\({x}*{y})".format(x=x, y=y)
    return s


def T(u, x):
    s = r"({x}\({u}*{x}))".format(x=x, u=u)
    return s


def L(u, x, y):
    s = r"({y}*{x})\({y}*({x}*{u}))".format(u=u, x=x, y=y)
    return s


def R(u, x, y):
    s = "(({u}*{x})*{y})/({x}*{y})".format(u=u, x=x, y=y)
    return s


# AIM axioms :
identity = '0'
x, y, z, u, w = 'x', 'y', 'z', 'u', 'w'
variables = [x, y, z, u, w]

TT = Axiom(T(T(u, x), y), T(T(u, y), x), variables, "TT")
TL = Axiom(T(L(u, x, y), z), L(T(u, z), x, y), variables, "TL")
TR = Axiom(T(R(u, x, y), z), R(T(u, z), x, y), variables, "TR")
LR = Axiom(L(R(u, x, y), z, w), R(L(u, z, w), x, y), variables, "LR")
LL = Axiom(L(L(u, x, y), z, w), L(L(u, z, w), x, y), variables, "LL")
RR = Axiom(R(R(u, x, y), z, w), R(R(u, z, w), x, y), variables, "RR")

inner_axiom = [TT, TL, TR, LR, LL, RR]

Ka = Axiom(K(a(x, y, z), u), identity, variables, "Ka")
aK1 = Axiom(a(K(x, y), z, u), identity, variables, "aK1")
aK2 = Axiom(a(x, K(y, z), u), identity, variables, "aK2")
aK3 = Axiom(a(x, y, K(z, u)), identity, variables, "aK3")

aa1 = Axiom(a(a(x, y, z), u, w), identity, variables, "aa1")
aa2 = Axiom(a(x, a(y, z, u), w), identity, variables, "aa2")
aa3 = Axiom(a(x, y, a(z, u, w)), identity, variables, "aa3")

aim_conjecture = [Ka, aK1, aK2, aK3, aa1, aa2, aa3]

rng = RandomState(0)
for _ in range(2, 8):
    loop_generator = LoopGeneratorNaive(4, rng, max_iter=15000)
    my_loop = Table(loop_generator.generate().astype(str), identity="0")
    operators = {star: my_loop.mul,
                 dot: my_loop.mul,
                 left: my_loop.ldiv,
                 right: my_loop.rdiv}
    my_model = Model(my_loop, operators, delimiters)

    print(my_model.table)

    for axiom in loop_axioms:
        print(axiom.name, "is", my_model.is_true(axiom))
    print("")
    for axiom in inner_axiom:
        print(axiom.name, "is", my_model.is_true(axiom))
    print("")
    for axiom in aim_conjecture:
        print(axiom.name, "is", my_model.is_true(axiom))
    print("\n\n")