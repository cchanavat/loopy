class CacheManager:
    def __init__(self):
        self.caches = {}

    def is_cached(self, expr):
        return expr in self.caches.keys()

    def cache(self, expr, table):
        self.caches[expr.expr] = Cache(expr, table)


class Cache:
    """
        Given an expression, a cache allows to access directly the computed element of the expression
        without recalculating elements
    """
    def __init__(self, expr_, table):
        """
        :param expr_: Expr expression to cache
        :param table: table that computes the expression
        """
        self.expr = expr_
        self.table = table

    def update(self, x, y, z):
        self.table.update(x, y, z)
