class CacheManager:
    def __init__(self):
        self.caches = {}

    def is_cached(self, expr):
        return expr.expr in self.caches.keys()

    def cache(self, expr, table):
        self.caches[expr.expr] = Cache(expr, table)

    def get_table(self, expr):
        if not self.is_cached(expr):
            raise Exception(f"{expr} is not cached")
        return self.caches[expr.expr].table

    def delete_cache(self, expr):
        if self.is_cached(expr):
            del(self.caches[expr.expr])


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
