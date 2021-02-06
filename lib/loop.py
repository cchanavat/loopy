from numpy import sort, array
from lib.latin import *


class LoopGeneratorNaive:
    """
        Create a random loop from a random generator that is a numpy array of integer from 0 (identity)
        to n - 1
    """
    def __init__(self, n, rng, max_iter=50):
        """
        :param n: dimension of the llop
        :param rng: random generator
        :param max_iter: max number of iteration before it raises an exception
        """
        self.n = n
        self.rng = rng
        self.latin_generator = LatinGenerator(self.n, self.rng)
        self.max_iter = max_iter

    def generate(self):
        identity = array([i for i in range(self.n)])

        for _ in range(self.max_iter):
            latin = self.latin_generator.generate()
            latin = latin[latin[:, 0].argsort()]
            if (latin[0, :] == identity).all():
                break
        else:
            raise Exception("Unable to generate a random loop with {}".format(self.max_iter))

        return latin


class LoopGenerator:
    def __init__(self, n, rng, max_iter=50):
        """
        :param n: dimension of the llop
        :param rng: random generator
        :param max_iter: max number of iteration before it raises an exception
        """
        self.n = n
        self.rng = rng
        self.max_iter = max_iter
