from numpy import zeros, concatenate, array
from lib.parser import *
import lib.model


class Axiom:
    def __init__(self, left, right, variables, name=None):
        """
            Axiom left = right where left and right are sentence of the model
        :param left: left
        :param right: right
        :param variables: list of variables used in the sentence
        :param name: name of the axiom
        :param preparse: avoid to recompute the tree structure of the axiom every time
        """
        self.left = left
        self.right = right
        self.name = name

        self.variables = []
        for var in variables:
            if var in self.left or var in self.right:
                self.variables.append(var)

        self.preparsed = False
        self.left_tree = None
        self.right_tree = None

    def __str__(self):
        return self.left + " = " + self.right

    def preparse(self):
        """
        Build a tree structure for the axiom to optimize the instanciation
        """
        self.preparsed = True
        # not very clean :
        model = lib.model.LoopModel(zeros((2, 2)))
        model.add_digits(self.variables)
        parser = Parser(model)
        self.left_tree = parser.build(self.left)
        self.right_tree = parser.build(self.right)
