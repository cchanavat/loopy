from numpy import ndarray, array, size
from loopy.axiom import Axiom, AxiomVerifier
from loopy.cache import CacheManager
from loopy.language import Language
from loopy.parser import Parser
from loopy.symbol import SymbolType
from loopy.table import Table, TableMaker


class Model:
    def __init__(self, mul_table: ndarray, identity='0'):
        """
        :param mul_table: multiplication table of the loop
        :param identity: identity element of the loop
        """
        self.identity_repr = identity
        self.lang = Language(identity=self.identity_repr)

        self.elements = mul_table[0, :]
        self.mul_table = Table(mul_table, self.elements, ndim=2)

        self.cardinal = size(self.elements)

        self.ldiv_table = self._make_ldiv_table()
        self.rdiv_table = self._make_rdiv_table()

        # I don't really understand the namespace stuff but it seems to work
        self.lambda_binary_operations = {
            self.lang.name_to_repr["star"]: lambda a, b: lambda **namespace: self.mul(a(**namespace), b(**namespace)),
            self.lang.name_to_repr["ld"]: lambda a, b: lambda **namespace: self.ldiv(a(**namespace), b(**namespace)),
            self.lang.name_to_repr["rd"]: lambda a, b: lambda **namespace: self.rdiv(a(**namespace), b(**namespace)),
        }

        self.arithmetic_function_generator = ArithmeticFunctionGenerator(self.lambda_binary_operations)

        for elt in self.elements:
            if elt != self.identity_repr:
                self.lang.add_symbol(elt, SymbolType.OPERAND, elt)

        self.cache_manager = CacheManager()

    def mul(self, x, y):
        return self.mul_table.of(x, y)

    def ldiv(self, x, y):
        return self.ldiv_table.of(x, y)

    def rdiv(self, x, y):
        return self.rdiv_table.of(x, y)

    def is_true(self, axiom: Axiom):
        av = AxiomVerifier(self)
        return av.is_true(axiom)

    def _make_ldiv_table(self):
        ldiv_table = Table(self.mul_table.copy_table(), self.elements, ndim=2)
        for y in self.elements:
            for x in self.elements:
                for z in self.elements:
                    if x == self.mul_table.of(y, z):
                        ldiv_table.update(x, y, new=z)
        return ldiv_table

    def _make_rdiv_table(self):
        rdiv_table = Table(self.mul_table.copy_table(), self.elements, ndim=2)
        for y in self.elements:
            for x in self.elements:
                for z in self.elements:
                    if x == self.mul_table.of(z, y):
                        rdiv_table.update(x, y, new=z)
        return rdiv_table

    def test(self):
        axiom = Axiom(r"Ax Ay Az At ((x*y)/z)*t = t*(z/(x*y))", lang=self.lang)
        tp = Parser()
        tok = tp.tokenize(self, axiom.left, axiom.variables)
        print(tok)
        rpn = tp.tokenized_to_rpn(tok)
        print(rpn)

        tok = tp.tokenize(self, axiom.right)
        print(tok)
        rpn = tp.tokenized_to_rpn(tok)
        print(rpn)


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


