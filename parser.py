from loopy.symbol import SymbolType


class Parser:
    """
        Tools for parsing expressions
    """
    def __init__(self):
        pass

    @staticmethod
    def tokenize(model, expr, variables=None):
        """
            tokenize self.expr with tokens from self.variables and the language. Careful, it prioritize the longest
            token, e.g. if x*y is a variable name, then it will be tokenized as ["x*y"] and not ["x", "*", "y"]
        :return: the tuple of the tokenized symbols
        """
        if variables is None:
            variables = expr.variables

        lang = model.lang
        tokens_symbols = tuple(lang.symbols) + variables

        max_token_len = max([len(symbol.repr) for symbol in tokens_symbols])

        tokenized = []
        i = 0
        len_expr = len(expr)

        while i < len_expr:
            tok_symbol = None
            temp_tok = ''
            tok_len = 0
            for j in range(1, 1 + max_token_len):
                temp_tok = expr[i:i+j]
                for symbol in tokens_symbols:
                    if temp_tok in symbol.repr:
                        tok_symbol = symbol
                        tok_len = j
            if tok_symbol is None:
                raise Exception(f"Could not tokenize properly `{expr}`. Unknown token in `{temp_tok}`")

            tokenized.append(tok_symbol)
            i += tok_len

        return tuple(tok for tok in tokenized)

    @staticmethod
    def tokenized_to_rpn(tokenized_symbol):
        """
            Transform tokenized_expression to Reverse Polish Notation
            Assume good parenthesis
        :param tokenized_symbol: tuple/list of Symbol, tokenized
        :return: the RPN stack of the expression
        """
        output_queue = []
        operator_stack = []
        for symbol in tokenized_symbol:
            if symbol.type == SymbolType.OPERAND:
                output_queue.append(symbol)
            elif symbol.type == SymbolType.OPERATOR:
                operator_stack.append(symbol)
            elif symbol.type == SymbolType.LDELIMITER:
                operator_stack.append(symbol)
            elif symbol.type == SymbolType.RDELIMITER:
                while operator_stack[-1].type != SymbolType.LDELIMITER:
                    output_queue.append(operator_stack.pop())
                operator_stack.pop()
            else:
                raise Exception(f"SymbolType `{symbol.type}` can't be converted.")

        while len(operator_stack) > 0:
            op = operator_stack.pop()
            if op.type != SymbolType.OPERATOR:
                raise Exception(f"Expression not valid, `{op}` should be an operator.")
            output_queue.append(op)

        return tuple(output_queue)

    def expr_to_rpn(self, model, expr, variables=None):
        """
            Transforms an expression to its symbolic RPN
            :return a tuple of Symbol
        """
        tok = self.tokenize(model, expr, variables)
        return self.tokenized_to_rpn(tok)

    def rpn_unfold(self, rpn):
        pass
