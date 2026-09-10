class RecurrenceSolver:
    def __init__(self, order, coefficients, initial_conditions):
        self.order = order
        self.coefficients = coefficients
        self.initial_conditions = initial_conditions
        self.roots = []
        self.constants = []

    def solve_characteristic_equation(self):
        return self.roots

    def get_explicit_formula(self):
        return "a_n = C1(r1)^n"

    def generate_terms_recursive(self, n_terms):
        return list(self.initial_conditions)
    
    def generate_terms_explicit(self, n_terms):
        return list(self.initial_conditions)
