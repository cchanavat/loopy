from numpy import zeros


# adapted from https://play.golang.org/p/7Ycmxh5T5EP
# Jacobson and Matthews' algorithm
class LatinGenerator:
    def __init__(self, n, rng):
        self.rng = rng
        self.n = n

    def swap(self, a, b):
        if self.rng.randint(0, 2):
            return a, b
        return b, a

    def generate(self):
        n = self.n
        xy = zeros((n, n), dtype="int")
        xz = zeros((n, n), dtype="int")
        yz = zeros((n, n), dtype="int")

        for i in range(n):
            for j in range(n):
                k = (i + j) % n
                xy[i, j] = k
                xz[i, k] = j
                yz[j, k] = i

        proper = True
        m = [0, 0, 0]
        mxy, mxz, myz = 0, 0, 0
        min_iter = n * n * n
        it = 0
        while it < min_iter or not proper:
            if proper:
                i, j, k = self.rng.randint(n, size=3)
                while xy[i, j] == k:
                    i, j, k = self.rng.randint(n, size=3)
                # find i2 such that[i2, j, k] is 1. same for j2, k2
                i2 = yz[j, k]
                j2 = xz[i, k]
                k2 = xy[i, j]
                i2_, j2_, k2_ = i, j, k
            else:
                i, j, k = m[0], m[1], m[2]
                # find one such that [i2, j, k] is 1, same for j2, k2.
                # each is either the value stored in the corresponding
                # slice, or one of our three temporary "extra" 1s.
                # That's because (i, j, k) is -1.
                i2, i2_ = self.swap(yz[j, k], myz)
                j2, j2_ = self.swap(xz[i, k], mxz)
                k2, k2_ = self.swap(xy[i, j], mxy)
            proper = xy[i2, j2] == k2

            if not proper:
                m = [i2, j2, k2]
                mxy = xy[i2, j2]
                myz = yz[j2, k2]
                mxz = xz[i2, k2]

            xy[i, j] = k2_
            xy[i, j2] = k2
            xy[i2, j] = k2
            xy[i2, j2] = k

            yz[j, k] = i2_
            yz[j, k2] = i2
            yz[j2, k] = i2
            yz[j2, k2] = i

            xz[i, k] = j2_
            xz[i, k2] = j2
            xz[i2, k] = j2
            xz[i2, k2] = j
            it += 1

        return xy
