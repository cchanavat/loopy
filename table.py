from warnings import warn
from itertools import product
from numpy import copy, empty
from loopy.parser import Parser


class Table:
    def __init__(self, table_, elements, ndim):
        self.table = table_.astype('str')
        self.elements = elements.astype('str')
        self.ndim = ndim

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
        return self.table[self.coordinates_of(*elements)]

    def update(self, *elements, new):
        self.table[self.coordinates_of(*elements)] = new

    def copy_table(self):
        return copy(self.table)

    def __str__(self):
        return str(self.table)

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
        for v in expr_.variables:
            if v.repr in rpn_repr:
                ndim += 1
        table_array = empty([self.model.cardinal] * ndim)
        table = Table(table_array, self.model.elements, ndim=ndim)

        if check_cache:
            warn("Warning : check_cache not supported yet")
        if cache_sub:
            warn("Warning : cache_sub not supported yet")

        for variable_instances in product(self.model.elements, repeat=ndim):
            val = table_function(
                **{expr_.variables[i].repr: variable_instances[i] for i in range(ndim)}
            )
            table.update(*variable_instances, new=val)

        return table
