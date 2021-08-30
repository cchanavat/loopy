from __future__ import annotations

from ast import literal_eval
from itertools import product

from numpy import array, where, isin, intersect1d, zeros, setdiff1d, loadtxt, savetxt


class Loop:
    """
    API for ld, rd and mul of a loop
    """

    def __init__(self, mul_table: array):
        """
        :param mul_table: mul_table of a loop represented by 0, ..., n-1, 0 is the identity
        """

        self.order = mul_table.shape[0]
        self.tmul = mul_table
        self.elements = array([i for i in range(self.order)])

        self.trd = zeros((self.order, self.order), dtype=int)
        self.tld = zeros((self.order, self.order), dtype=int)

        for x, y in product(self.elements, repeat=2):
            self.update_mul(x, y, self.mul(x, y))

    def update_mul(self, x, y, z):
        self.tmul[x, y] = z  # x * y = z
        self.tld[x, z] = y  # x \ z = y
        self.trd[z, y] = x  # z / y = x

    def mul(self, x, y):
        return self.tmul[x, y]

    def ld(self, x, y):
        return self.tld[x, y]

    def rd(self, x, y):
        return self.trd[x, y]

    def flatten_mul(self):
        return self.tmul.flatten()

    def flatten_ld(self):
        return self.tld.flatten()

    def flatten_rd(self):
        return self.trd.flatten()

    def __str__(self):
        return str(self.tmul)

    def __repr__(self):
        return str(self)

    def is_loop(self) -> bool:
        n = self.order
        if not (self.tmul[:, 0] == self.elements).all() or not (self.tmul[0, :] == self.elements).all():
            return False

        for i in range(n):
            if not isin(self.tmul[i, :], self.elements).all():
                return False
            if not isin(self.tmul[:, i], self.elements).all():
                return False

            if len(set(self.tmul[i, :])) != n:
                return False
            if len(set(self.tmul[:, i])) != n:
                return False

        return True

    def is_associative(self) -> bool:
        for x, y, z in product(self.elements, repeat=3):
            if self.mul(x, self.mul(y, z)) != self.mul(self.mul(x, y), z):
                return False
        return True

    def commutant(self) -> array:
        elements = []
        for x in self.elements:
            for y in self.elements:
                if self.mul(x, y) != self.mul(y, x):
                    break
            else:  # no break
                elements.append(x)
        return array(elements)

    def is_commutative(self) -> bool:
        commutant = set(self.commutant())
        return len(commutant) == self.order

    def is_group(self) -> bool:
        return self.is_loop() and self.is_associative()

    def sub_table(self, elements: array) -> array:
        indexes = where(isin(self.elements, elements))[0]
        new_table = self.tmul[:, indexes]
        indexes = where(isin(new_table[:, 0], elements))[0]
        return new_table[indexes, :]

    def is_subloop(self, subloop_elements: array) -> bool:
        for x, y in product(subloop_elements, repeat=2):
            if self.mul(x, y) not in subloop_elements:
                return False
        subloop_mul_table = self.sub_table(subloop_elements)
        return GeneralizedLoop(subloop_mul_table, subloop_elements).is_loop()

    def left_nucleus(self) -> array:
        elements = []
        for x in self.elements:
            for y, z in product(self.elements, repeat=2):
                if self.mul(x, self.mul(y, z)) != self.mul(self.mul(x, y), z):
                    break
            else:
                elements.append(x)
        return elements

    def middle_nucleus(self) -> array:
        elements = []
        for y in self.elements:
            for x, z in product(self.elements, repeat=2):
                if self.mul(x, self.mul(y, z)) != self.mul(self.mul(x, y), z):
                    break
            else:
                elements.append(y)
        return elements

    def right_nucleus(self) -> array:
        elements = []
        for z in self.elements:
            for x, y in product(self.elements, repeat=2):
                if self.mul(x, self.mul(y, z)) != self.mul(self.mul(x, y), z):
                    break
            else:
                elements.append(z)
        return elements

    def nucleus(self) -> array:
        left = self.left_nucleus()
        middle = self.middle_nucleus()
        right = self.right_nucleus()
        return intersect1d(intersect1d(left, middle), right)

    def center(self) -> array:
        return intersect1d(self.commutant(), self.nucleus())

    def left_coset(self, x: int, set_: array) -> array:
        """
        :return: xS where S is a subset of the loop's elements
        """
        coset = set([])
        for s in set_:
            coset.add(self.mul(x, s))
        return array(list(coset))

    def right_coset(self, x: int, set_: array) -> array:
        """
        :return: Sx where S is a subset of the loop's elements
        """
        coset = set([])
        for s in set_:
            coset.add(self.mul(s, x))
        return array(list(coset))

    def is_normal_subloop(self, subloop_elements: array) -> bool:
        if not self.is_subloop(subloop_elements):
            return False

        for x in self.elements:
            xS = self.left_coset(x, subloop_elements)
            Sx = self.right_coset(x, subloop_elements)
            if set(xS) != set(Sx):
                return False
        return True

    def quotient_loop(self, normal_subloop_elements: array) -> [Loop, array]:
        """
        :return: a loop and the canonical projection
        """
        if not self.is_normal_subloop(normal_subloop_elements):
            raise Exception(f"{normal_subloop_elements} is not a normal subloop")
        quotient_order = self.order // normal_subloop_elements.shape[0]

        canonical_projection = {}

        elements_left = self.elements
        quotient_elements = {}
        elements_quotient = {}
        rep_to_coset = {}
        for i in range(quotient_order):
            rep = min(elements_left)
            coset = self.left_coset(rep, set_=normal_subloop_elements)
            elements_left = setdiff1d(elements_left, coset)
            quotient_elements[i] = rep
            elements_quotient[rep] = i
            rep_to_coset[rep] = coset
            for x in coset:
                canonical_projection[x] = i

        quotient_table = zeros((quotient_order, quotient_order), dtype=int)
        for i, j in product(range(quotient_order), repeat=2):
            x = quotient_elements[i]
            y = quotient_elements[j]
            xy = self.mul(x, y)
            # finding the equivalence class where xy belongs
            for possible_rep, coset in rep_to_coset.items():
                if xy in coset:
                    rep = possible_rep
                    break
            else:
                raise Exception("Unexpected error during the construction of the quotient loop")

            quotient_table[i, j] = elements_quotient[rep]

        return Loop(quotient_table), canonical_projection

    def Z_c_plus_one(self, Z_c):
        quotient, projection = self.quotient_loop(Z_c)
        preimage = [x for x in self.elements if projection[x] in quotient.center()]
        return array(preimage)

    def nilpotency_class(self) -> int:
        Z = array([0])
        nilpotency = 0
        while len(set(Z)) != self.order:
            Z = self.Z_c_plus_one(Z)
            nilpotency += 1
            if nilpotency > self.order:
                raise Exception("This loop is not nilpotent")
        return nilpotency

    def product(self, A: Loop) -> Loop:
        mapping = {(a, b): i for i, (a, b) in enumerate(product(self.elements, A.elements))}
        mapping_rev = {i: (a, b) for i, (a, b) in enumerate(product(self.elements, A.elements))}
        n = self.order * A.order
        AB_table = zeros((n, n), dtype=int)
        for i, j in product(range(n), repeat=2):
            ai, bi = mapping_rev[i]
            aj, bj = mapping_rev[j]
            ak, bk = self.mul(ai, aj), A.mul(bi, bj)
            k = mapping[(ak, bk)]
            AB_table[i, j] = k

        return Loop(AB_table)

    @staticmethod
    def semidirect_product(G: Loop, aut: array, N: Loop):
        mapping = {(a, b): i for i, (a, b) in enumerate(product(G.elements, N.elements))}
        mapping_rev = {i: (a, b) for i, (a, b) in enumerate(product(G.elements, N.elements))}
        n = G.order * N.order
        GN_table = zeros((n, n), dtype=int)

        for i, j in product(range(n), repeat=2):
            gi, ni = mapping_rev[i]
            gj, nj = mapping_rev[j]
            gk, nk = G.mul(gi, gj), N.mul(ni, aut[gi, nj])
            k = mapping[(gk, nk)]
            GN_table[i, j] = k

        return Loop(GN_table)

    def copy(self):
        return Loop(self.tmul)


class LoopUtils:
    def __init__(self):
        pass

    @staticmethod
    def table_from_file(fname, shift=0):
        return loadtxt(fname, dtype=int) + shift

    @staticmethod
    def loop_from_file(fname, shift=0):
        return Loop(LoopUtils.table_from_file(fname, shift))

    @staticmethod
    def gap_file_prettyfier(fname):
        file = open(fname, 'r')
        struct = literal_eval(file.read())
        file.close()
        savetxt(fname, array(struct) - 1, fmt="%i")

    @staticmethod
    def save_arr(fname: str, arr: array, shift=0):
        savetxt(fname, arr + shift, fmt="%i")

    @staticmethod
    def save_loop(fname: str, A: Loop, shift=0):
        LoopUtils.save_arr(fname, A.tmul, shift)


class GeneralizedLoop(Loop):
    """
        Loops that can be indexed by anything. First element of elements is the identity
    """

    def __init__(self, mul_table: array, elements: array):
        n = elements.size
        self.elements_to_index = {e: i for i, e in enumerate(elements)}
        isom_mul_table = zeros((n, n), dtype=int)
        for x, y in product(elements, repeat=2):
            i, j = self.elements_to_index[x], self.elements_to_index[y]
            isom_mul_table[i, j] = self.elements_to_index[mul_table[i, j]]
        super().__init__(isom_mul_table)


class EmptyLoop(Loop):
    def __init__(self, order: int):
        mul_table = zeros((order, order), dtype=int)
        super().__init__(mul_table)


class LoopMorphism:
    def __init__(self, A: Loop, B: Loop, table: dict):
        self.A = A
        self.B = B
        self.table = table

    def im(self, a: int) -> int:
        return self.table[a]

    def is_morphism(self):
        for a1, a2 in product(self.A.elements, repeat=2):
            phi_12 = self.im(self.A.mul(a1, a2))
            phi1_phi2 = self.B.mul(self.im(a1), self.im(a2))
            if not phi_12 == phi1_phi2:
                return False
        return True

