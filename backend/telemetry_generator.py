import random

class TelemetryGenerator:
    @staticmethod
    def generate_random_scenario(order):
        coefficients = [round(random.uniform(-1.5, 2.5), 2) for _ in range(order)]
        initial_conditions = [random.randint(10, 100) for _ in range(order)]
        return {
            "coefficients": coefficients,
            "initial_conditions": initial_conditions,
            "order": order
        }
