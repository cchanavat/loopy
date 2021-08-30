from __future__ import annotations

from itertools import product
from os.path import isfile

from numpy import array, zeros, ones, loadtxt
from numpy.random import RandomState

from loopapy.loop import Loop, EmptyLoop
from loopapy.setup import THIS_DIR


class LoopGenerator:
    @staticmethod
    def cyclic(n: int) -> Loop:
        table = zeros((n, n), dtype=int)
        for i, j in product(range(n), repeat=2):
            table[i, j] = (i + j) % n
        return Loop(table)

    @staticmethod
    def dihedral(n: int) -> Loop:
        file_name = THIS_DIR + f"groups/D{n}.group"
        if not isfile(file_name):
            raise Exception("This Dihedral group is not in the database. Ask GAP instead")

        table = loadtxt(file_name, dtype=int)
        return Loop(table)


class CentralExtensionGenerator:
    def __init__(self):
        pass

    @staticmethod
    def generate(A: Loop, B: Loop, theta: array, phi: array = None) -> Loop:
        a = A.order
        b = B.order

        AB = EmptyLoop(a * b)
        AB_to_index = {(a, b): i for i, (a, b) in enumerate(product(A.elements, B.elements))}

        for a1, a2 in product(A.elements, repeat=2):
            for b1, b2 in product(B.elements, repeat=2):
                x = AB_to_index[(a1, b1)]
                y = AB_to_index[(a2, b2)]

                phi_a2 = a2 if phi is None else phi[b1, a2]

                prod = (A.mul(A.mul(a1, phi_a2), theta[b1, b2]), B.mul(b1, b2))
                xy = AB_to_index[prod]
                AB.update_mul(x, y, xy)

        return AB

    @staticmethod
    def random_theta(a: int, b: int, rng: RandomState):
        theta = zeros((b, b), dtype=int)
        theta[1:, 1:] = rng.randint(a, size=(b - 1, b - 1))
        return theta

    @staticmethod
    def space_size(A: Loop, B: Loop, fmt="%s"):
        n = (B.order - 1) ** 2
        if fmt == "%s":
            return f"{A.order} ^ {n}"
        else:
            return A.order ** n


class CsorgoTypeGenerator:
    def __init__(self):
        pass

    @staticmethod
    def generate(H_mul_table: array, f: array, rng: RandomState) -> Loop:
        """
        :param H_mul_table: Multiplication table of the group used for the generation. See the paper for more details
        :param f: (H/Z(H)) \to {-1, 1} symmetric trilinear alternating form
        :param rng:
        :return: A loop of nilpotency class 3 with abelian inner mapping
        """
        H = Loop(H_mul_table)
        M = H.center()

        HdM, projection = H.quotient_loop(M)
        A = [1, -1]

        f_shape = (HdM.order, HdM.order, HdM.order)
        if f.shape != (HdM.order, HdM.order, HdM.order):
            raise Exception(f"f's shape should be {f_shape}")

        def commutator(x, y):
            xy = H.mul(x, y)
            yx = H.mul(y, x)
            return H.ld(xy, yx)

        def one_or_none():
            return rng.choice(A)

        transversal = [0] + list({projection[x]: x for x in H.elements if projection[x] != 0}.values())
        factorisation = {H.mul(m, t): (m, t) for m, t in product(M, transversal)}

        delta = ones((H.order, H.order), dtype=int)
        mu = ones((H.order, H.order), dtype=int)

        # constructing delta

        # condition 5.1
        for i, j, k in product(transversal, repeat=3):
            c = commutator(i, j)
            f_ijk = f[projection[i], projection[j], projection[k]]
            for m in M:
                delta[c, H.mul(k, m)] = f_ijk

        # condition 5.3
        for t, s in product(transversal, repeat=2):
            if t == 0:
                delta[t, s] = 1
            if t == s:
                delta[t, s] = 1
            if t < s:
                delta[t, s] = one_or_none()
                delta[s, t] = one_or_none()

        # condition 5.4
        for h1, h2 in product(H.elements, repeat=2):
            m1, t1 = factorisation[h1]
            m2, t2 = factorisation[h2]
            delta[h1, h2] = delta[m1, t2] * delta[m2, t1] * delta[t1, t2]

        # constructing mu

        # condition 5.6
        for t in transversal:
            mu[t, t] = one_or_none()
            for m in M:
                mu[m, t] = delta[m, t]
                mu[t, m] = 1
                for n in M:
                    mu[m, n] = 1

        for t, s in product(transversal, repeat=2):
            if t < s:
                mu[t, s] = delta[t, s]
                mu[s, t] = 1
        mu[0, 0] = 1

        # condition 5.7
        for m1, m2, t1, t2 in product(M, M, transversal, transversal):
            h1 = H.mul(m1, t1)
            h2 = H.mul(m2, t2)
            mu[h1, h2] = mu[m1, t2] * mu[t1, t2]

        return CentralExtensionGenerator.generate(LoopGenerator.cyclic(2), H, (mu - 1) // -2)

        C_table = zeros((2 * H.order, 2 * H.order))
        C_isom = {(a, h): i for i, (a, h) in enumerate(product(A, H.elements))}
        for (a1, h1), (a2, h2) in product(C_isom.keys(), repeat=2):
            i, j = C_isom[(a1, h1)], C_isom[(a2, h2)]
            a = a1 * a2
            h = H.mul(h1, h2)
            C_table[i, j] = C_isom[(a * mu[h2, h1], h)]

        return C_table
