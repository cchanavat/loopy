class Axiom:
    def __init__(self, left, right, variables, name=None):
        self.left = left
        self.right = right
        self.name = name

        self.variables = []
        for var in variables:
            if var in self.left or var in self.right:
                self.variables.append(var)

    def __str__(self):
        return self.left + " = " + self.right
