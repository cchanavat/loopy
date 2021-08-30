from itertools import product

from numpy import zeros, array, equal as npequal
from tqdm import tqdm

from loopapy.loop import Loop


class Partition:
    def __init__(self, quotient: array, A: Loop, B: Loop):
        self.quotient = quotient
        self.qcard = len(self.quotient.keys())
        self.base_set = [theta for thetas in self.quotient.values() for theta in thetas]
        self.bcard = len(self.base_set)
        self.A = A
        self.B = B

    def proj(self, theta: array):
        for i, sigmas in self.quotient.items():
            for sigma in sigmas:
                if npequal(theta, sigma).all():
                    return i
        raise Exception("theta not found")

    def table(self, mul_law):
        table = zeros((self.bcard, self.bcard), dtype=int)
        for i, j in tqdm(product(range(self.bcard), repeat=2), total=self.bcard ** 2):
            theta_i, theta_j = self.base_set[i], self.base_set[j]
            theta_ij = mul_law(theta_i, theta_j)
            table[i, j] = self.proj(theta_ij)
        return table

    def quotient_table(self):
        quotient_table = zeros((self.qcard, self.qcard), dtype=int)
        for (i, thetas_i), (j, thetas_j) in tqdm(product(self.quotient.items(), repeat=2), total=self.qcard ** 2):
            mul_res = set()
            for theta_i, theta_j in product(thetas_i, thetas_j):
                theta_ij = self.mul(theta_i, theta_j)
                mul_res.add(self.proj(theta_ij))
                if len(mul_res) > 1:
                    return False
            quotient_table[i, j] = list(mul_res)[0]
        return quotient_table

    def pseudo_quotient_table(self):
        quotient_table = zeros((self.qcard, self.qcard), dtype=object)
        for (i, thetas_i), (j, thetas_j) in tqdm(product(self.quotient.items(), repeat=2), total=self.qcard ** 2):
            mul_res = set()
            for theta_i, theta_j in product(thetas_i, thetas_j):
                theta_ij = self.mul(theta_i, theta_j)
                mul_res.add(self.proj(theta_ij))
            quotient_table[i, j] = mul_res
        return quotient_table

    def closure_ij(self, i, j):
        need = set()
        for theta, sigma in product(self.quotient[i], self.quotient[j]):
            need.add(self.proj(self.mul(theta, sigma)))
        return need

    def closure(self, ks):
        close = set()
        new_close = set(ks)
        while new_close != close:
            close = new_close
            for i, j in product(close, repeat=2):
                new_close = new_close.union(self.closure_ij(i, j))
        return close

    def mul(self, t1, t2):
        b = self.B.order - 1
        t12 = zeros((b, b), dtype=int)
        for i, j in product(range(b), repeat=2):
            t12[i, j] = self.A.mul(t1[i, j], t2[i, j])
        return t12

    def pad(self, theta):
        padded = zeros((self.B.order, self.B.order), dtype=int)
        padded[1:, 1:] = theta
        return padded
