import numpy as np
import pandas as pd


class Table:
    def __init__(self, table, elements=None, identity='e'):
        """
        :param table: table of the loop
        :param elements: ORDERED elements (in respect of the table), default : same as first row
        :param identity: identity
        """
        self.n = table.shape[0]
        self.id = identity
        self.elements = elements or list(table[0])
        self.table = pd.DataFrame(table, index=self.elements, columns=self.elements)

    def mul(self, x, y):
        return self.table.loc[x, y]

    def ldiv(self, y, x):  # left div \
        """
            :param x: numerator
            :param y: denominator
            :return: z s.t z = y \ x
        """
        for z in self.elements:
            if x == self.mul(y, z):
                return z
        else:
            raise Exception("{x} = {y} * z has no solution".format(x=x, y=y))

    def rdiv(self, x, y):  # right div /
        """
            :param x: numerator
            :param y: denominator
            :return: z s.t z = x / y
        """
        for z in self.elements:
            if x == self.mul(z, y):
                return z
        else:
            raise Exception("{x} = z * {y} has no solution".format(x=x, y=y))

    def __str__(self):
        return str(self.table)
