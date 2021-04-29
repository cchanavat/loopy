from warnings import warn
from itertools import product
from numpy import copy, empty, pad, append
from loopy.parser import Parser


class Table:
    def __init__(self, table_, elements, ndim, special_char=None):
        self.table = table_.astype('str')
        self.elements = elements.astype('str')
        self.ndim = ndim

        self.has_been_padded = False
        self.special_char = special_char
        if self.special_char is not None:
            self.table = pad(self.table, (0, 1), constant_values=self.special_char)
            if self.special_char not in elements:
                self.elements = append(self.elements, self.special_char)
            self.has_been_padded = True

        self.element_to_index = {}  # optimisation
        for i, x in enumerate(self.elements):
            self.element_to_index[x] = i

    def index_of(self, x):
        return self.element_to_index[x]

    def coordinates_of(self, *elements):
        ndim = len(elements)
        if ndim != self.ndim:
            raise Exception(f"This table has dimension {self.ndim} not {ndim}")

        return tuple([self.index_of(x) for x in elements])

    def of(self, *elements):
        c = self.coordinates_of(*elements)
        return self.table[c]

    def at(self, *coordinates):
        return self.table[tuple(coordinates)]

    def update(self, *elements, new):
        self.table[self.coordinates_of(*elements)] = new

    def unpad_table(self):
        """
        :return: self.table without padding
        """
        if self.has_been_padded:
            ind = tuple([slice(0, -1)] * self.ndim)
            return self.table[ind]
        return self.table

    def copy_table(self):
        """
        :return: a deep copy of self.table
        """
        return copy(self.unpad_table())

    def copy(self):
        """
        :return: a deep copy of self
        """
        return Table(self.copy_table(), self.elements, self.ndim, self.special_char)

    def __str__(self):
        return str(self.unpad_table())

    def __repr__(self):
        return str(self)


class TableMaker:
    def __init__(self, model):
        """
            Create a Table given and expression
        """
        self.model = model

    def make_table(self, expr_, check_cache=False, cache_sub=False):
        """
        WARNING : if the Expr is `Ax Ay Az x*y` this method will return a table of dim 2, avoiding
        unnecessary z dimension.
        :param expr_: Expr, expression to make a table with
        :param check_cache: optional use od model's cache_manager. If True, this method will check for every
        sub-expression if it's not already cached
        :param cache_sub: if true, will cache every sub_expression not yet cached
        :return: the table of expr
        """
        parser = Parser()
        rpn = parser.expr_to_rpn(self.model, expr_)
        table_function = self.model.arithmetic_function_generator.make(rpn)

        ndim = 0
        rpn_repr = [s.repr for s in rpn]
        expr_variables = []
        for v in expr_.variables:
            if v.repr in rpn_repr:
                ndim += 1
                expr_variables.append(v)  # we need to preserve the order
        table_array = empty([self.model.cardinal] * ndim)
        table = Table(table_array, self.model.elements, ndim=ndim, special_char=self.model.special_char)

        if check_cache:
            warn("Warning : check_cache not supported yet")
        if cache_sub:
            warn("Warning : cache_sub not supported yet")

        for variable_instances in product(self.model.elements, repeat=ndim):
            val = table_function(
                **{expr_variables[i].repr: variable_instances[i] for i in range(ndim)}
            )
            table.update(*variable_instances, new=val)

        return table
