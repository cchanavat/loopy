import warnings
from loopy.symbol import Symbol, SymbolType


class Language:
    """
        Class that support first order logic in language used in loop theory
    """
    def __init__(self, identity='0'):
        self.identity = identity
        self.symbols = [
            Symbol('(', SymbolType.LDELIMITER, 'lp'),
            Symbol(')', SymbolType.RDELIMITER, 'rp'),
            Symbol('.', SymbolType.OPERATOR, 'dot'),
            Symbol('*', SymbolType.OPERATOR, 'star'),
            Symbol('/', SymbolType.OPERATOR, 'rd'),
            Symbol('\\', SymbolType.OPERATOR, 'ld'),
            Symbol(self.identity, SymbolType.OPERAND, 'id'),
            Symbol('=', SymbolType.OPERATOR, 'eq'),
            Symbol('!=', SymbolType.OPERATOR, 'neq'),
            Symbol('A', SymbolType.UNIVERSAL_QUANTIFIER, 'forall'),
            Symbol('E', SymbolType.EXISTENTIAL_QUANTIFIER, 'exists'),
        ]

        # for the O(1) access :
        self.repr_to_symbol = {s.repr: s for s in self.symbols}
        self.name_to_symbol = {s.name: s for s in self.symbols}
        self.name_to_repr = {s.name: s.repr for s in self.symbols}

    def add_symbol(self, symbol_repr, symbol_type, name):
        """
            Typically, call when constructing a new loop table with the symbol from 1 to n-1
        """
        if symbol_repr in self.repr_to_symbol.keys():
            warnings.warn(f"Symbol representation {symbol_repr} already exists in the language")
            return
        if name in self.name_to_symbol.keys():
            warnings.warn(f"Symbol name {name} already exists in the language")
            return

        symb = Symbol(symbol_repr, symbol_type, name)
        self.symbols.append(symb)

        self.repr_to_symbol[symbol_repr] = symb
        self.name_to_symbol[name] = symb
        self.name_to_repr[name] = symb.repr

    def is_quantifier(self, symbol_repr):
        if symbol_repr not in self.repr_to_symbol.keys():
            return False

        symbol_type = self.repr_to_symbol[symbol_repr].type
        return symbol_type == SymbolType.UNIVERSAL_QUANTIFIER or symbol_type == SymbolType.EXISTENTIAL_QUANTIFIER

    def type(self, symbol_repr):
        if symbol_repr not in self.repr_to_symbol.keys():
            return False
        return self.repr_to_symbol[symbol_repr].type

    def repr_max_len(self):
        """
        :return: the length of the longest symbol representation in the language
        """
        m = 0
        for s in self.symbols:
            s_len = len(s.repr)
            if s_len > m:
                m = s_len
        return m

    def list_of_repr(self):
        return [s.repr for s in self.symbols]
