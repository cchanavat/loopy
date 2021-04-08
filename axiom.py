from loopy.language import Language
from loopy.symbol import Symbol, SymbolType


class Variable(Symbol):
    def __init__(self, name, quantification):
        super().__init__(name, SymbolType.OPERAND, name)
        self.quantification = quantification
        self.is_variable = True

    def __repr__(self):
        return str(self)


class Expr:
    def __init__(self, expr, variables):
        self.expr = expr
        self.variables = variables
        self.rpn = None

    def eq(self, other, quantification_equality=False):
        """
        CAUTION :
             - Aa Ab a*b != Ab Aa a*b even though they are the same (quantification permutation is not supported yet)
             - (x*y) != x*y yet
        :param other: other Expr to compare with self
        :param quantification_equality: If True, ensure that it has same quantification,
        e.g (Aa Eb) a*b != (Aa Ab) a*b
        :return: boolean
        """
        nb_variables = len(self.variables)

        if nb_variables != len(other.variables):
            return False

        variable_mapper = {}
        for i in range(nb_variables):
            this_var = self.variables[i]
            other_var = other.variables[i]
            if quantification_equality and this_var.quantification != other_var.quantification:
                return False
            variable_mapper[this_var.repr] = other_var.repr

        copy_expr = self.expr
        for this_repr, other_repr in variable_mapper.items():
            copy_expr = copy_expr.replace(this_repr, other_repr)

        return copy_expr == other.expr

    def __str__(self):
        return str(self.expr)

    def __len__(self):
        return len(self.expr)

    def __getitem__(self, item):
        return self.expr[item]


class Axiom:
    """
        An axiom must have the following structure :
        "Qx1␣Qx2␣...␣Qxn␣f(x1, ..., xn)␣=␣g(x1, ..., xn)"
        where the Qs are existential or universal quantifiers and f and g are functions expressed using operations
        in lang (e.g f(x1, x2, x3) = (x1*x2)/x3)

        Note that ␣ denotes spaces and serves as delimiter, particularly there must be no space in f nor g.
    """

    def __init__(self, expr, lang=None):
        if lang is None:
            self.lang = Language()
        else:
            self.lang = lang

        self.eq = self.lang.name_to_symbol['eq']

        self.base_expr = expr

        self.split_expr = self.base_expr.split()

        variables = []
        for tok in self.split_expr:
            if self.lang.is_quantifier(tok[0]):
                v = Variable(tok[1:], self.lang.type(tok[0]))
                variables.append(v)

        # to ensure right order of quantifiers
        self.variables = tuple(v for v in variables)

        # currently, no OR nor AND are supported in the axiom definition, improve code below if needed
        n = len(self.split_expr)
        for i in range(n):
            if self.split_expr[i] == self.eq.repr:
                left = self.split_expr[i - 1]
                right = self.split_expr[i + 1]
                break
        else:
            raise Exception("No ' = ' find in the expression")

        self.left = Expr(left, self.variables)
        self.right = Expr(right, self.variables)

    def __str__(self):
        return self.base_expr


class AxiomVerifier:
    def __init__(self, model):
        self.model = model

    def is_true(self, axiom: Axiom):
        # left = axiom.left
        # right = axiom.right
        # if not self.cache_manager.is_cached(left):
        #     self.cache_manager.cache(left, self, axiom.variables)
        #
        # if not self.cache_manager.is_cached(right):
        #     self.cache_manager.cache(right, self, axiom.variables)
        pass
