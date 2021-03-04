import sys
import numpy as np
from lib.latin import *
from lib.model import *


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
        identity = np.array([i for i in range(self.n)])

        for _ in range(self.max_iter):
            latin = self.latin_generator.generate()
            latin = latin[latin[:, 0].argsort()]
            if (latin[0, :] == identity).all():
                break
        else:
            raise Exception("Unable to generate a random loop with {}".format(self.max_iter))

        return latin


class LoopGenerator:
    def __init__(self, n, rng: np.random.RandomState, fill_method="lexico"):
        """
        :param n: dimension of the llop
        :param rng: random generator
        :param max_iter: max number of iteration before it raises an exception
        """
        self.n = n
        self.rng = rng
        self.fill_method = fill_method
        self.elements = np.array([i for i in range(n)]).astype("str")
        self.loop = np.zeros((n, n)).astype("str")
        self.special_char = '&'
        self.loop[:] = self.special_char

        # over the third dimension will be the proba of an the element i to be drawn
        self.possible_elements = np.zeros((self.n, self.n, self.n))
        self.initial_probabilities = 1 / self.n * np.ones(self.n)
        self.trajectory = []

        self.random_trajectory_generation = np.array([(i, j) for j in range(1, self.n) for i in range(1, self.n)])
        self.random_trajectory_generation = self.rng.permutation(self.random_trajectory_generation)
        self.random_trajectory_generation_index = 0
        self.number_of_case_to_fill = 0

        self.axioms = []
        self.loop_model = None

        self.verbose = True
        self.first_print_verbose = True

    def reset_loop(self):
        self.loop = np.zeros((self.n, self.n)).astype("str")
        self.special_char = '&'
        self.loop[:] = self.special_char

        self.possible_elements = np.zeros((self.n, self.n, self.n))
        self.initial_probabilities = 1 / self.n * np.ones(self.n)
        self.trajectory = []

        self.random_trajectory_generation = np.array([(i, j) for j in range(1, self.n) for i in range(1, self.n)])
        self.random_trajectory_generation = self.rng.permutation(self.random_trajectory_generation)
        self.random_trajectory_generation_index = 0
        self.number_of_case_to_fill = 0

    def generate(self, axiom_list=()):
        """
        :param axiom_list: list of Axiom that need to be verified in the loop. Note that identy should be '0'.
        :return: a loop that verify the axiom list
        """
        self.reset_loop()
        self.first_print_verbose = True

        self.loop[0, :] = self.elements
        self.loop[:, 0] = self.elements
        self.number_of_case_to_fill = (self.n - 1) ** 2
        self.loop_model = LoopModel(self.loop)

        for i in range(self.n):
            for j in range(self.n):
                self.possible_elements[i, j, :] = self.initial_probabilities

        self.axioms = axiom_list
        for axiom in self.axioms:
            axiom.preparse()
        self.aux_generate(1, 1)

        return self.loop

    def aux_generate(self, i0, j0):
        i, j = self.first_element_index(i0, j0)
        is_there_element_to_draw = True
        number_case_filled = 0
        while True:
            self.print_information(i, j)
            self.trajectory.append((i, j))
            if not is_there_element_to_draw:  # if no possible elements are left, we go back
                self.possible_elements[i, j, :] = self.initial_probabilities
                self.loop[i, j] = self.special_char
                i, j = self.previous_element_index(i, j)
                number_case_filled -= 1
                # we set the proba to 0 this element because we came back, so it will not work with it
                k = np.where(self.elements == self.loop[i, j])
                is_there_element_to_draw = self.set_probabilities_to_zero(i, j, k)
            else:
                choice = self.choose_element(i, j)
                self.loop[i, j] = choice

                if not self.is_partial_loop(i, j):
                    k = np.where(self.elements == choice)
                    is_there_element_to_draw = self.set_probabilities_to_zero(i, j, k)
                else:
                    number_case_filled += 1
                    # we break here because i, j has no spot for the next element
                    if number_case_filled == self.number_of_case_to_fill:
                        break
                    i, j = self.next_element_index(i, j)

    def next_element_index(self, i, j):
        ii, jj = i, j
        if self.fill_method == "lexico":
            jj = (jj + 1) % self.n
            if jj == 0:
                ii += 1
                jj = 1
            return ii, jj

        if self.fill_method == "random":
            self.random_trajectory_generation_index += 1
            return self.random_trajectory_generation[self.random_trajectory_generation_index]

        if self.fill_method == "rlexico":
            ii = (ii + 1) % self.n
            if ii == 0:
                jj += 1
                ii += 1
            return ii, jj

    def previous_element_index(self, i, j):
        ii, jj = i, j
        if self.fill_method == "lexico":
            jj = jj - 1
            ii = (ii - (jj < 1))
            if jj == 0:
                jj = self.n - 1
            return ii, jj

        if self.fill_method == "random":
            if self.random_trajectory_generation_index == 0:
                raise Exception("Cannot return the previous element index, it's already the first")
            self.random_trajectory_generation_index -= 1
            return self.random_trajectory_generation[self.random_trajectory_generation_index]

        if self.fill_method == "rlexico":
            jj = (jj - (ii < 1))
            ii = (ii - 1) % self.n
            return ii, jj

    def first_element_index(self, i0, j0):
        if self.fill_method == "lexico":
            return i0, j0

        if self.fill_method == "random":
            return self.random_trajectory_generation[self.random_trajectory_generation_index]

        if self.fill_method == "rlexico":
            return i0, j0

    def set_probabilities_to_zero(self, i, j, k):
        # if it's time to stop :
        self.possible_elements[i, j, k] = 0

        sum_proba = np.sum(self.possible_elements[i, j, :])
        if sum_proba == 0:
            return False

        # we normalize :
        self.possible_elements[i, j, :] = self.possible_elements[i, j, :] / sum_proba
        return True

    def is_partial_loop(self, i, j):
        # check uniqueness over (i, j) partial row and col
        if self.fill_method == "lexico":
            if len(set(self.loop[i, :j + 1])) < len(list(self.loop[i, :j + 1])):
                return False

            if len(set(self.loop[:i + 1, j])) < len(list(self.loop[:i + 1, j])):
                return False
        else:
            row = np.delete(self.loop[i, :], np.where(self.loop[i, :] == self.special_char))
            col = np.delete(self.loop[:, j], np.where(self.loop[:, j] == self.special_char))
            if len(set(row)) < len(list(row)):
                return False

            if len(set(col)) < len(list(col)):
                return False

        # check if axioms in self.axioms are verified over the partial table
        for axiom in self.axioms:
            if not self.is_partially_verified(axiom):
                return False

        return True

    def is_partially_verified(self, axiom):
        self.loop_model.set_table(self.loop)
        return self.loop_model.is_partially_verified(axiom)

    def choose_element(self, i, j, method="random"):
        if method == "random":
            return self.rng.choice(self.elements, p=self.possible_elements[i, j, :])

    def get_trajectory(self):
        return self.trajectory

    def print_information(self, i, j):
        # assume the filling method is lexico
        bar_len = self.n
        if self.verbose:
            percent = round((i * self.n + j + 1) / self.n ** 2, 2)
            block = int(round(bar_len * percent))
            text = "Percent of the loop filled : [{0}] {1}%".format("#" * block + "-" * (bar_len - block),
                                                                    percent * 100)

            if self.first_print_verbose:
                self.first_print_verbose = False
                text = "\n" + text
            else:
                text = "\r" + text

            print(text, end='')

