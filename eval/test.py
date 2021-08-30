from numpy import array
from loopy.model import *

table = [["0", "1", "2", "3", "4", "5", "6", "7"],
         ["1", "7", "5", "0", "6", "4", "3", "2"],
         ["2", "6", "4", "7", "0", "1", "5", "3"],
         ["3", "2", "7", "5", "1", "6", "4", "0"],
         ["4", "0", "3", "1", "5", "7", "2", "6"],
         ["5", "4", "6", "2", "3", "0", "7", "1"],
         ["6", "3", "1", "4", "7", "2", "0", "5"],
         ["7", "5", "0", "6", "2", "3", "1", "4"]]

# table = array(table)
# model = Model(table)
# print(model.mul_table)
# print(model.ldiv_table)
#
#
# ax1 = Axiom("Ax Ay x*y\\a = x*y")
# ax2 = Axiom(r"Aa Eb a*b\a = b*a")
# ax3 = Axiom(r"Ax Ay x*y = x\y")
# iam = Axiom(r"Ax Ay Az Au (u*(x*(y*z))\((x*y)*z))\((x*(y*z))\((x*y)*z)*u) = 0")
# # print(ax1.left.eq(ax2.left, quantification_equality=False))
#
# tm = TableMaker(model)
# print(model.ldiv_table)
# print(tm.make_table(ax3.right))
#
# table = array(table)
# model = Model(table)
#
# ax1 = Axiom("Ax Ey x*y = 0")
# ax2 = Axiom("Ex Ay x*y = 0")
# print(model.truth_value(ax1))
# print(model.truth_value(ax2))

moufang = [["0", "1", "2", "3", "4", "5"],
           ["1", "0", "4", "5", "2", "3"],
           ["2", "4", "5", "0", "3", "1"],
           ["3", "5", "0", "4", "1", "2"],
           ["4", "2", "3", "1", "5", "0"],
           ["5", "3", "1", "2", "0", "4"]]
moufang = array(moufang)
model = Model(moufang)

# ax = Axiom("Ax Ay Az z*(x*(z*y)) = ((z*x)*z)*y", model.lang)
# print(model.truth_value(ax))
#
# a1 = Axiom(r"Ax Ay Az Au (u*(x*(y*z))\((x*y)*z))\((x*(y*z))\((x*y)*z)*u) = 0")
# a2 = Axiom(r"Ax Ay Az Au ((y*x)\(x*y)*(z*u))\(((y*x)\(x*y)*z)*u) = 0")
# a3 = Axiom(r"Ax Ay Az Au (x*((z*y)\(y*z)*u))\((x*(z*y)\(y*z))*u) = 0")
# a4 = Axiom(r"Ax Ay Az Au (x*(y*(u*z)\(z*u)))\((x*y)*(u*z)\(z*u)) = 0")
# a5 = Axiom(r"Ax Ay Az Au Aw ((x*(y*z))\((x*y)*z)*(u*w))\(((x*(y*z))\((x*y)*z)*u)*w) = 0")
# a6 = Axiom(r"Ax Ay Az Au Aw (x*((y*(z*u))\((y*z)*u)*w))\((x*(y*(z*u))\((y*z)*u))*w) = 0")
# a7 = Axiom(r"Ax Ay Az Au Aw (x*(y*(z*(u*w))\((z*u)*w)))\((x*y)*(z*(u*w))\((z*u)*w)) = 0")
#
# axs = [a1, a2, a2, a4, a5, a6, a7]
#
# for ax in axs:
#     print(model.truth_value(ax))

table = array(table)
model = Model(table)
# ax1 = Axiom(r"Ax Ey x*y = y*x")
# ax2 = Axiom(r"Ax Ay x*y = x*y")
# ax3 = Axiom(r"Ax Ey y*x = 55")
#
# axs = [ax1, ax2, ax3]
#
# for ax in axs:
#     print(ax, model.truth_value(ax))
ax = Axiom(r"Ay Ax x*y = y")
model.truth_value(ax)