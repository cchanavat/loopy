from loopy.model import *

table = [["0", "1", "2", "3", "4", "5", "6", "7"],
         ["1", "7", "5", "0", "6", "4", "3", "2"],
         ["2", "6", "4", "7", "0", "1", "5", "3"],
         ["3", "2", "7", "5", "1", "6", "4", "0"],
         ["4", "0", "3", "1", "5", "7", "2", "6"],
         ["5", "4", "6", "2", "3", "0", "7", "1"],
         ["6", "3", "1", "4", "7", "2", "0", "5"],
         ["7", "5", "0", "6", "2", "3", "1", "4"]]


table = array(table)
model = Model(table)
# print(model.mul_table)
# print(model.ldiv_table)
# model.test()

ax1 = Axiom("Ax Ay x*y\\a = x*y")
ax2 = Axiom(r"Aa Eb a*b\a = b*a")
ax3 = Axiom(r"Ax Ay x*y = x\y")
iam = Axiom(r"Ax Ay Az Au (u*(x*(y*z))\((x*y)*z))\((x*(y*z))\((x*y)*z)*u) = 0")
# print(ax1.left.eq(ax2.left, quantification_equality=False))

tm = TableMaker(model)
print(model.ldiv_table)
print(tm.make_table(ax3.right))