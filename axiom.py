from loopy.language import Language
from loopy.parser import Parser
from loopy.symbol import Variable, SymbolType
from loopy.table import TableMaker


class Expr:
    def __init__(self, expr, variables):
        self.expr = expr
        self.variables = variables
        self.rpn = None
        self.indexes_of_used_variables = None

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

    def compute_rpn(self, model):
        parser = Parser()
        self.rpn = parser.expr_to_rpn(model, self)

    def _compute_indexes_of_used_variables(self):
        rpn_repr = [s.repr for s in self.rpn]
        self.indexes_of_used_variables = []
        for i in range(len(self.variables)):
            if self.variables[i].repr in rpn_repr:
                self.indexes_of_used_variables.append(i)

    def coordinates_formatter(self, coordinates, model, compute_rpn=False):
        """
        Suppose self is "Ax Ay Az x*y", usually, during the instantiation, we'll have
        (x, y, z) = (1, 2, 3). But then when we'll call the Table that represents "a*b" it won't
        work because it is supposed to have only two coordinates. This method solves the problem
        by returning only the coordinates that are used in self.expr
        :param coordinates: array of the full coordinates
        :param model: model to use
        :param compute_rpn: if True, recompute the RPN of self
        :return: the array of the partial coordinates, in the right order
        """
        if compute_rpn or self.rpn is None:
            self.compute_rpn(model)
            self._compute_indexes_of_used_variables()

        return [coordinates[i] for i in self.indexes_of_used_variables]

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
        left = axiom.left
        right = axiom.right

        cache_manager = self.model.cache_manager
        table_maker = TableMaker(self.model)
        if not cache_manager.is_cached(left):
            left_table = table_maker.make_table(left)
            cache_manager.cache(left, left_table)

        if not cache_manager.is_cached(right):
            right_table = table_maker.make_table(right)
            cache_manager.cache(right, right_table)

        left_table = cache_manager.get_table(left)
        right_table = cache_manager.get_table(right)

        variable_list = axiom.variables

        def is_true_aux(variables, partial_instance):
            if not variables:
                l_instance = left.coordinates_formatter(partial_instance, self.model)
                r_instance = right.coordinates_formatter(partial_instance, self.model)
                return left_table.of(*l_instance) == right_table.of(*r_instance)
            var = variables[0]

            if var.quantification == SymbolType.UNIVERSAL_QUANTIFIER:
                is_verified = True
                for x in self.model.elements:
                    # Python is lazy so it should avoid unnecessary recursive calls
                    is_verified = is_verified and is_true_aux(variables[1::], partial_instance + [x])

            else:
                is_verified = False
                for x in self.model.elements:
                    is_verified = is_verified or is_true_aux(variables[1::], partial_instance + [x])

            return is_verified

        return is_true_aux(variable_list, [])
