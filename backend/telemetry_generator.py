import random
import math
import numpy as np


class TelemetryGenerator:
    PRESETS = {
        "stable": {
            "id": "stable",
            "name": "Equilibrio Operativo (Steady State)",
            "order": 2,
            "coefficients": [1.2, -0.2],
            "initial_conditions": [120.0, 140.0],
            "capacity_threshold": 300.0,
            "metric_type": "vCPU Cores",
            "unit": "cores"
        },
        "growth": {
            "id": "growth",
            "name": "Crecimiento Sostenible",
            "order": 2,
            "coefficients": [1.28, -0.216],
            "initial_conditions": [256.0, 280.0],
            "capacity_threshold": 800.0,
            "metric_type": "Memoria RAM (GB)",
            "unit": "GB"
        },
        "explosive": {
            "id": "explosive",
            "name": "Desborde Crítico",
            "order": 1,
            "coefficients": [1.32],
            "initial_conditions": [60.0],
            "capacity_threshold": 600.0,
            "metric_type": "Instancias EC2 / Nodos",
            "unit": "nodos"
        },
        "oscillatory": {
            "id": "oscillatory",
            "name": "Ciclo Diurno-Nocturno",
            "order": 2,
            "coefficients": [1.414, -1.0],
            "initial_conditions": [200.0, 280.0],
            "capacity_threshold": 480.0,
            "metric_type": "Solicitudes (kRPS)",
            "unit": "kRPS"
        },
        "order3_challenge": {
            "id": "order3_challenge",
            "name": "Clúster Kubernetes (Reto Orden 3)",
            "order": 3,
            "coefficients": [1.95, -1.755, 0.8505],
            "initial_conditions": [80.0, 95.0, 115.0],
            "capacity_threshold": 320.0,
            "metric_type": "Pods Kubernetes",
            "unit": "pods"
        }
    }

    METRICS = [
        {"name": "vCPU Cores", "unit": "cores", "base_min": 50, "base_max": 200, "threshold_mult": 2.5},
        {"name": "Memoria RAM (GB)", "unit": "GB", "base_min": 64, "base_max": 512, "threshold_mult": 2.2},
        {"name": "Instancias EC2 / VMs", "unit": "instancias", "base_min": 10, "base_max": 80, "threshold_mult": 3.0},
        {"name": "Solicitudes (kRPS)", "unit": "kRPS", "base_min": 100, "base_max": 400, "threshold_mult": 2.0},
        {"name": "Pods Kubernetes", "unit": "pods", "base_min": 30, "base_max": 150, "threshold_mult": 2.8}
    ]

    @classmethod
    def get_presets(cls):
        return list(cls.PRESETS.values())

    @classmethod
    def get_preset(cls, preset_id):
        return cls.PRESETS.get(preset_id, cls.PRESETS["stable"])

    @classmethod
    def generate_random_scenario(cls, order=None, preset_type=None):
        if preset_type and preset_type in cls.PRESETS:
            return cls.get_preset(preset_type)

        if order is None:
            order = random.choice([1, 2, 3])
        else:
            order = int(order)
            if order not in [1, 2, 3]:
                order = 2

        metric_info = random.choice(cls.METRICS)
        metric_name = metric_info["name"]
        metric_unit = metric_info["unit"]

        if order == 1:
            c1 = round(random.choice([
                random.uniform(0.88, 0.98),
                random.uniform(1.00, 1.03),
                random.uniform(1.05, 1.15),
                random.uniform(1.20, 1.32)
            ]), 3)
            coefficients = [c1]
            base_val = random.randint(metric_info["base_min"], metric_info["base_max"])
            initial_conditions = [float(base_val)]

        elif order == 2:
            behavior = random.choice(["distinct_real", "complex", "double_real"])
            if behavior == "distinct_real":
                r1 = random.uniform(0.95, 1.15)
                r2 = random.uniform(-0.4, 0.4)
                c1 = round(r1 + r2, 3)
                c2 = round(- (r1 * r2), 3)
            elif behavior == "complex":
                rho = random.uniform(0.90, 1.05)
                theta = random.uniform(math.pi / 6, math.pi / 2.5)
                c1 = round(2 * rho * math.cos(theta), 3)
                c2 = round(- (rho ** 2), 3)
            else:
                r = random.uniform(0.92, 1.10)
                c1 = round(2 * r, 3)
                c2 = round(- (r ** 2), 3)

            coefficients = [c1, c2]
            base_val = float(random.randint(metric_info["base_min"], metric_info["base_max"]))
            delta = base_val * random.uniform(0.05, 0.20)
            initial_conditions = [round(base_val, 1), round(base_val + delta, 1)]

        elif order == 3:
            r1 = random.uniform(0.95, 1.12)
            if random.random() < 0.6:
                rho = random.uniform(0.85, 1.02)
                theta = random.uniform(math.pi / 4, math.pi / 2)
                p1 = r1 + 2 * rho * math.cos(theta)
                p2 = rho**2 + 2 * r1 * rho * math.cos(theta)
                p3 = r1 * (rho ** 2)
                c1 = round(p1, 3)
                c2 = round(-p2, 3)
                c3 = round(p3, 3)
            else:
                r2 = random.uniform(0.2, 0.7)
                r3 = random.uniform(-0.5, 0.3)
                p1 = r1 + r2 + r3
                p2 = r1*r2 + r1*r3 + r2*r3
                p3 = r1*r2*r3
                c1 = round(p1, 3)
                c2 = round(-p2, 3)
                c3 = round(p3, 3)

            coefficients = [c1, c2, c3]
            base_val = float(random.randint(metric_info["base_min"], metric_info["base_max"]))
            delta1 = base_val * random.uniform(0.04, 0.15)
            delta2 = delta1 + base_val * random.uniform(0.04, 0.15)
            initial_conditions = [round(base_val, 1), round(base_val + delta1, 1), round(base_val + delta2, 1)]

        first_term = initial_conditions[0]
        capacity_threshold = round(first_term * metric_info["threshold_mult"], 1)

        return {
            "id": f"random_order_{order}_{random.randint(100, 999)}",
            "name": f"Escenario Aleatorio (Orden {order})",
            "order": order,
            "coefficients": coefficients,
            "initial_conditions": initial_conditions,
            "capacity_threshold": capacity_threshold,
            "metric_type": metric_name,
            "unit": metric_unit
        }

    @staticmethod
    def generate_traffic_perturbations(base_terms, noise_ratio=0.035, seed=None):
        if not base_terms:
            return []

        rng = random.Random(seed) if seed is not None else random.Random()
        perturbed_terms = []

        for i, val in enumerate(base_terms):
            if val == 0.0:
                perturbed_terms.append(0.0)
                continue

            jitter_pct = rng.gauss(0, noise_ratio)
            if rng.random() < 0.05:
                burst = rng.uniform(0.05, 0.12)
                jitter_pct += burst

            noisy_val = val * (1.0 + jitter_pct)
            if val >= 0 and noisy_val < 0:
                noisy_val = 0.0

            perturbed_terms.append(round(noisy_val, 4))

        return perturbed_terms
