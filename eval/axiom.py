from enum import Enum
from itertools import product

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

        self.left_rpn = None
        self.right_rpn = None

        self.ndim = len(self.variables)

    def __str__(self):
        return self.base_expr


class AxiomVerifier:
    def __init__(self, model):
        self.model = model

    def is_true(self, axiom: Axiom, arithmetic_fun=None):
        """
            Verify whether an axiom is True in within self.model. If no arithmetic_fun is given,
            it will calculate the table of the right and left member, so it is better to pre-caclculate the this
            function if is_true is used a large number of time over the same axiom
        :param axiom: the axiom to verify
        :param arithmetic_fun: the lambda_function that will be called with each instance of the variables
        :return: If the axiom is true within self.model
        """
        if arithmetic_fun is None:
            return self._is_true_no_fun(axiom)
        return self._is_true_fun(axiom, arithmetic_fun)

    def _is_true_no_fun(self, axiom):
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
                # we need the = defined in model because of the special char
                return self.model.equal(left_table.of(*l_instance), right_table.of(*r_instance))

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

    def _is_true_fun(self, axiom: Axiom, fun):
        variable_list = axiom.variables

        def is_true_aux(variables, partial_instance):
            if not variables:
                return fun(**partial_instance)
            var = variables[0]

            if var.quantification == SymbolType.UNIVERSAL_QUANTIFIER:
                is_verified = True
                for x in self.model.elements:
                    # Python is lazy so it should avoid unnecessary recursive calls
                    partial_instance[var.repr] = x
                    is_verified = is_verified and is_true_aux(variables[1::], partial_instance)

            else:
                is_verified = False
                for x in self.model.elements:
                    partial_instance[var.repr] = x
                    is_verified = is_verified or is_true_aux(variables[1::], partial_instance)

            return is_verified

        return is_true_aux(variable_list, {})


class TruthValue(Enum):
    FALSE = 0
    TRUE = 1
    MAYBE = 2


class AxiomVerifierSAT:
    def __init__(self, axiom: Axiom, model):
        self.model = model
        self.axiom = axiom
        self.parser = Parser()

        self.left_rpn = [tok.repr for tok in self.parser.expr_to_rpn(axiom.left, self.model)]
        self.right_rpn = [tok.repr for tok in self.parser.expr_to_rpn(axiom.right, self.model)]

        self.literals_list = []

        self.term_dictionary = TermDictionary()

        var_value_map = {
            "*": self.model.mul,
            "/": self.model.rdiv,
            "\\": self.model.ldiv_lexical_order
        }

        for i, instance in enumerate(product(self.model.elements, repeat=self.axiom.ndim)):
            for var, val in zip(self.axiom.variables, instance):
                var_value_map[var.repr] = val

            left = []
            right = []
            for tok in self.left_rpn:
                left.append(var_value_map[tok])
            for tok in self.right_rpn:
                right.append(var_value_map[tok])

            self.literals_list.append(Literal(left, right, id_=i, term_dict=self.term_dictionary))


class Literal:
    def __init__(self, left, right, id_: int, term_dict):
        self.left = left
        self.right = right

        self.left_evaluated = False
        self.right_evaluated = False

        self.id = id_
        self.term_dict = term_dict

    def is_true(self) -> TruthValue:
        if self.left_evaluated and self.right_evaluated:
            return TruthValue.TRUE if self.left == self.right else TruthValue.FALSE
        return TruthValue.MAYBE

    def update(self, term, value):
        n_term = len(term)
        n_left = len(self.left)
        n_right = len(self.right)

        i = 0
        while i <= n_left - n_term:
            sub_list = self.left[i:(i + n_term)]
            if self.left[i] == sub_list[0] and sub_list == term:
                self.left[i:(i + n_term)] = [value]
                i = 0
                continue
            i += 1

        while i <= n_right - n_term:
            sub_list = self.right[i:(i + n_term)]
            if self.right[i] == sub_list[0] and sub_list == term:
                self.right[i:(i + n_term)] = [value]
                i = 0
                continue
            i += 1


class TermDictionary:
    def __init__(self):
        self.dict = {}

    def add(self, term, literal: Literal):
        if term in self.dict.keys():
            self.dict[term][literal.id] = literal
        else:
            self.dict[term] = {literal.id: literal}

    def remove(self, term, literal: Literal) -> bool:
        return False if self.dict[term].pop(literal.id, None) is None else True

    def update(self, term, value):
        for literal in self.dict[term]:
            literal.update(term, value)
            self.remove(term, literal)
