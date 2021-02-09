from lib.axiom import *
from lib.loop_gen import *
from lib.model import *


lid = Axiom("e*x", "x", variables=['x'])
rid = Axiom("x*e", "x", variables=['x'])
b1 = Axiom(r"x\(x*y)", "y", variables=['x', 'y'])
b2 = Axiom(r"x*(x\y)", "y", variables=['x', 'y'])
s1 = Axiom("(x*y)/y", "x", variables=['x', 'y'])
s2 = Axiom("(x/y)*y", "x", variables=['x', 'y'])

loop_axioms = [lid, rid, b1, b2, s1, s2]

