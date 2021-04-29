from numpy import ndarray, size, empty

from loopy.axiom import Axiom, AxiomVerifier
from loopy.cache import CacheManager
from loopy.language import Language
from loopy.parser import Parser
from loopy.symbol import SymbolType
from loopy.table import Table, TableMaker


class Model:
    def __init__(self, mul_table: ndarray, identity='0', special_char=None):
        """
        :param mul_table: multiplication table of the loop
        :param identity: identity element of the loop
        """
        self.identity_repr = identity
        self.lang = Language(identity=self.identity_repr)

        self.special_char = special_char
        if self.special_char is not None:
            self.lang.add_symbol(special_char, SymbolType.OPERAND, 'special')

        self.elements = mul_table[0, :]
        self.mul_table = Table(mul_table, self.elements, ndim=2, special_char=self.special_char)

        self.cardinal = size(self.elements)

        self.ldiv_table = self._make_ldiv_table()
        self.rdiv_table = self._make_rdiv_table()

        # I don't really understand the namespace stuff but it seems to work
        self.lambda_binary_operations = {
            self.lang.name_to_repr["star"]:
                lambda a, b: lambda **namespace: self.mul(a(**namespace), b(**namespace)),

            self.lang.name_to_repr["ld"]:
                lambda a, b: lambda **namespace: self.ldiv_lexical_order(a(**namespace), b(**namespace)),

            self.lang.name_to_repr["rd"]:
                lambda a, b: lambda **namespace: self.rdiv(a(**namespace), b(**namespace)),
        }

        self.arithmetic_function_generator = ArithmeticFunctionGenerator(self.lambda_binary_operations)

        for elt in self.elements:
            if elt != self.identity_repr:
                self.lang.add_symbol(elt, SymbolType.OPERAND, elt)

        self.cache_manager = CacheManager()

    def equal(self, x, y):
        """
        :param x: string representation of a symbol
        :param y: string representation of a symbol
        :return: if x == y
        """
        if self.special_char is not None and (x == self.special_char or y == self.special_char):
            return True
        return x == y

    def change_tables(self, mul_table, ldiv_table, rdiv_table):
        self.mul_table = mul_table
        self.ldiv_table = ldiv_table
        self.rdiv_table = rdiv_table

    def mul(self, x, y):
        return self.mul_table.of(x, y)

    def ldiv_lexical_order(self, x, y):
        """
            compute x \\\\ y
            use this one with RPN
        """
        return self.ldiv(y, x)

    def ldiv(self, x, y):
        return self.ldiv_table.of(x, y)

    def rdiv(self, x, y):
        return self.rdiv_table.of(x, y)

    def update_mul(self, x, y, new, update_cache=False):
        self.mul_table.update(x, y, new=new)
        self.ldiv_table.update(new, x, new=y)
        self.rdiv_table.update(new, y, new=x)
        if update_cache:
            self.update_cache()

    def update_cache(self):
        """
        Recalculate the whole cache, so can be very expensive
        """
        table_maker = TableMaker(self)
        for cache in self.cache_manager.caches.values():
            expr = cache.expr
            new_table = table_maker.make_table(expr)
            self.cache_manager.cache(expr, new_table)

    def truth_value(self, axiom: Axiom, arithmetic_fun=None):
        av = AxiomVerifier(self)
        return av.is_true(axiom, arithmetic_fun)

    def axiom_to_function(self, axiom: Axiom):
        """
        Take an axiom and give back a Python function that gives the truth value when called with actual instances
        of the variable
        (preserve order of the quantifiers)
        :param axiom: axiom to transform
        :return: Callable Python function
        """
        parser = Parser()
        rpn_left = parser.expr_to_rpn(self, axiom.left)
        rpn_right = parser.expr_to_rpn(self, axiom.right)

        left_fun = self.arithmetic_function_generator.make(rpn_left)
        right_fun = self.arithmetic_function_generator.make(rpn_right)

        return lambda **kwargs: self.equal(left_fun(**kwargs), right_fun(**kwargs))

    def _make_ldiv_table(self):
        ldiv_table = self.empty_operation_table()
        for y in self.elements:
            for x in self.elements:
                for z in self.elements:
                    if x == self.mul_table.of(y, z):
                        ldiv_table.update(x, y, new=z)
        return ldiv_table

    def _make_rdiv_table(self):
        rdiv_table = self.empty_operation_table()
        for y in self.elements:
            for x in self.elements:
                for z in self.elements:
                    if x == self.mul_table.of(z, y):
                        rdiv_table.update(x, y, new=z)
        return rdiv_table

    def empty_operation_table(self):
        """
        An empty table for mul, rd or ld is filled with the special_char if one, otherwise with the identity.
        :return: a Table() that has to be completely filled if no special char
        """
        table = empty((self.cardinal, self.cardinal), dtype='int8').astype('str')
        filling_char = self.special_char if self.special_char is not None else self.identity_repr
        table[:, :] = filling_char
        return Table(table, self.elements, ndim=2, special_char=self.special_char)

    def __str__(self):
        return str(self.mul_table)


# thank you :
# https://stackoverflow.com/questions/62938038/building-a-function-with-x-y-parameters-using-reverse-polish-notation
class ArithmeticFunctionGenerator:
    def __init__(self, lambda_functions):
        """
            Take a RPN expression and convert it to a callable Python function
        """
        self.lambda_functions = lambda_functions

    def make(self, rpn):
        stack = []
        for token in rpn:
            if token.type == SymbolType.OPERATOR:
                arg2 = stack.pop()
                arg1 = stack.pop()

                result = self.lambda_functions[token.repr](arg1, arg2)
                stack.append(result)
            else:
                if not token.is_variable:
                    stack.append(lambda *, _num=token.repr, **namespace: _num)
                else:
                    stack.append(lambda *, _token=token.repr, **namespace: namespace[_token])

        return stack.pop()
