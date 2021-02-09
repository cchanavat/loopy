from itertools import product
from lib.parser import *
from lib.axiom import *
from lib.table import *


class Model:
    def __init__(self, table, operators, delimiters):
        """
        :param table: np array that represent the loop
        :param operators: dict(Operator1: function, ...)
        :param delimiters: [left_delimiter, right_delimiter] from symbol
        """
        self.table = table
        self.elements = self.table[:, 0]
        self.l_delimiter, self.r_delimiter = delimiters
        self.operators = operators
        self.parser = Parser(self)

        self.element_to_index = {}  # optimisation
        for i, x in enumerate(self.elements):
            self.element_to_index[x] = i

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

    def evaluate(self, expr):
        """
        :param expr: string expression that will be evaluate
        :return: the evaluate expression
        e.g. in the model of (Z/3Z, +) "evaluate(1+1+1)" return 0
        """
        return self.parser.evaluate(expr)

    def equal(self, a, b):
        return self.evaluate(a) == self.evaluate(b)

    @staticmethod
    def instantiate(expr, var, elements):
        """
        :param expr: expression to instantiate
        :param var: ordered variables that will be replaced
        :param elements: ordered elements that will replace the variables
        :return: the new expression
        """
        new_expr = expr
        for v, e in zip(var, elements):
            new_expr = new_expr.replace(v, e)
        return new_expr

    def is_true(self, axiom: Axiom):
        """
        :param axiom: axiom we want to check
        :return: whether or not this particular axiom is true in this model
        """
        var = axiom.variables
        left = axiom.left
        right = axiom.right
        n = len(var)
        if n == 0:
            return self.equal(left, right)

        for elts in product(self.elements, repeat=n):
            left_instance = self.instantiate(left, var, elts)
            right_instance = self.instantiate(right, var, elts)
            if not self.equal(left_instance, right_instance):
                return False

        return True

    # implementation of loop operations
    def mul(self, x, y):
        ix = self.element_to_index[x]
        iy = self.element_to_index[y]
        return self.table[ix, iy]

    def ldiv(self, y, x):  # left div \
        """
            :param x: numerator
            :param y: denominator
            :return: z s.t z = y \ x
        """
        for z in self.elements:
            if x == self.mul(y, z):
                return z
        else:
            raise Exception("{x} = {y} * z has no solution".format(x=x, y=y))

    def rdiv(self, x, y):  # right div /
        """
            :param x: numerator
            :param y: denominator
            :return: z s.t z = x / y
        """
        for z in self.elements:
            if x == self.mul(z, y):
                return z
        else:
            raise Exception("{x} = z * {y} has no solution".format(x=x, y=y))

    def __str__(self):
        return str(pd.DataFrame(self.table, index=self.elements, columns=self.elements))


class LoopModel(Model):
    def __init__(self, array, identity="0"):
        """
            Higher level model for loop, just give a numpy array and all default parameters are set up correctly.
            Implement special character methods
        :param array: the numpy array that represent the loop
        :param identity: identity element of the numpy array, "0" by def.
        :param operators: operations that can be applied, default are the common operation left, right and mul
        :param delimiters: default are ( and )
        """
        self.identity = identity
        self.special_character = '&'

        operators = {Operator('*', Notation.INFIX, 2, Priority.LOW): self.mul,
                     Operator('.', Notation.INFIX, 2, Priority.HIGH): self.mul,
                     Operator('\\', Notation.INFIX, 2, Priority.LOW): self.ldiv,
                     Operator('/', Notation.INFIX, 2, Priority.LOW): self.rdiv}

        lp = Delimiter('(')
        rp = Delimiter(')')
        delimiters = [lp, rp]

        super().__init__(array.astype(str), operators, delimiters)

        # LOOP AXIOMS
        lid = Axiom("0*x", "x", ['x'], "lid")
        rid = Axiom("x*0", "x", ['x'], "rid")
        b1 = Axiom("x\\(x*y)", "y", ['x', 'y'], "b1")
        b2 = Axiom("x*(x\\y)", "y", ['x', 'y'], "b2")
        s1 = Axiom("(x*y)/y", "x", ['x', 'y'], "s1")
        s2 = Axiom("(x/y)*y", "x", ['x', 'y'], "s2")

        self.loop_axioms = [lid, rid, b1, b2, s1, s2]

    def is_loop(self):
        for axiom in self.loop_axioms:
            if not self.is_true(axiom):
                return False
        return True

    def set_table(self, table):
        """
            Does not modify identity or elements
        :param table: table
        :return: None
        """
        self.table = table

    def is_partially_verified(self, axiom):
        return self.is_true(axiom)

    def mul(self, x, y):
        if x == self.special_character or y == self.special_character:
            return self.special_character
        ix = self.element_to_index[x]
        iy = self.element_to_index[y]
        return self.table[ix, iy]

    def ldiv(self, y, x):  # left div \
        """
            :param x: numerator
            :param y: denominator
            :return: z s.t z = y \ x
        """
        if x == self.special_character or y == self.special_character:
            return self.special_character
        can_be_partial = False
        for z in self.elements:
            m = self.mul(y, z)
            if m == self.special_character:
                can_be_partial = True
            if x == m:
                return z
        else:
            if can_be_partial:
                return self.special_character
            else:
                raise Exception("{x} = {y} * z has no solution".format(x=x, y=y))

    def rdiv(self, x, y):  # right div /
        """
            :param x: numerator
            :param y: denominator
            :return: z s.t z = x / y
        """
        if x == self.special_character or y == self.special_character:
            return self.special_character
        can_be_partial = False
        for z in self.elements:
            m = self.mul(z, y)
            if m == self.special_character:  # maybe it was this z but it is not calculated yet
                can_be_partial = True
            if x == m:
                return z
        else:
            if can_be_partial:
                return self.special_character
            else:
                raise Exception("{x} = z * {y} has no solution".format(x=x, y=y))

    def isdigit(self, char):
        return super(LoopModel, self).isdigit(char) or char == self.special_character

    def equal(self, a, b):
        a_eval = self.evaluate(a)
        b_eval = self.evaluate(b)
        a_special = a_eval == self.special_character
        b_special = b_eval == self.special_character
        return a_eval == b_eval or a_special or b_special
