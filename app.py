import sys
import traceback
import flask
from flask import Flask, render_template, request, jsonify
import sympy as sp
import numpy as np

from backend.recurrence_solver import RecurrenceSolver
from backend.telemetry_generator import TelemetryGenerator
from backend.benchmark import BenchmarkEngine
from backend.validator import Validator
from backend.interpreter import CloudOpsInterpreter

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/tutorial')
def tutorial():
    try:
        return render_template('components/tutorial_dashboard.html')
    except Exception:
        return render_template('index.html')


@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        "status": "online",
        "service": "CloudOps Recurrence Simulation Engine",
        "message": "Servidor Flask y Motor Matemático operativos al 100%",
        "environment": {
            "python_version": sys.version.split()[0],
            "flask_version": "3.1.3",
            "sympy_version": sp.__version__,
            "numpy_version": np.__version__
        },
        "supported_orders": [1, 2, 3],
        "features": [
            "Ecuación característica simbólica y numérica",
            "Soporte para raíces reales, múltiples y complejas conjugadas",
            "Benchmarking de latencia con resolución de microsegundos",
            "Validación término a término con auditoría de error",
            "Telemetría sintética y simulación de perturbaciones locales",
            "Diagnóstico contextual y proyección de saturación de clúster"
        ]
    })


@app.route('/api/presets', methods=['GET'])
def get_presets():
    presets = TelemetryGenerator.get_presets()
    return jsonify({
        "success": True,
        "count": len(presets),
        "presets": presets
    })


@app.route('/api/random-scenario', methods=['GET'])
def random_scenario():
    order = request.args.get('order', default=None, type=int)
    preset_type = request.args.get('preset', default=None, type=str)

    try:
        scenario = TelemetryGenerator.generate_random_scenario(order=order, preset_type=preset_type)
        return jsonify({
            "success": True,
            "scenario": scenario
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error al generar escenario: {str(e)}"
        }), 400


@app.route('/api/solve', methods=['POST'])
def solve_recurrence():
    data = request.get_json(silent=True) or {}

    try:
        order = int(data.get('order', 2))
        if order not in [1, 2, 3]:
            return jsonify({"success": False, "error": f"El orden debe ser 1, 2 o 3. Recibido: {order}"}), 400

        coefficients = data.get('coefficients')
        if not coefficients or len(coefficients) != order:
            return jsonify({
                "success": False,
                "error": f"Se requieren exactamente {order} coeficientes para una relación de orden {order}."
            }), 400
        coefficients = [float(c) for c in coefficients]

        initial_conditions = data.get('initial_conditions')
        if not initial_conditions or len(initial_conditions) != order:
            return jsonify({
                "success": False,
                "error": f"Se requieren exactamente {order} condiciones iniciales [a_0, ...] para orden {order}."
            }), 400
        initial_conditions = [float(ic) for ic in initial_conditions]

        n_terms = int(data.get('n_terms', 20))
        if n_terms < order:
            n_terms = order
        if n_terms > 100:
            n_terms = 100

        capacity_threshold = data.get('capacity_threshold')
        if capacity_threshold is not None:
            capacity_threshold = float(capacity_threshold)

        metric_type = data.get('metric_type', 'vCPU Cores')
        unit = data.get('unit', 'cores')
        repetitions = int(data.get('repetitions', 300))
        noise_level = float(data.get('noise_level', 0.035))

        solver = RecurrenceSolver(
            order=order,
            coefficients=coefficients,
            initial_conditions=initial_conditions
        )
        solver_summary = solver.get_summary()

        terms_recursive = solver.generate_terms_recursive(n_terms)
        terms_explicit = solver.generate_terms_explicit(n_terms)

        terms_telemetry = TelemetryGenerator.generate_traffic_perturbations(
            terms_explicit,
            noise_ratio=noise_level
        )

        validation_result = Validator.verify_equality(
            recursive_terms=terms_recursive,
            explicit_terms=terms_explicit,
            tolerance=1e-4
        )

        benchmark_result = BenchmarkEngine.run_benchmark_comparison(
            solver=solver,
            n_terms=n_terms,
            repetitions=repetitions,
            test_single_nth=True
        )

        cloudops_diagnosis = CloudOpsInterpreter.diagnose(
            roots=solver_summary["roots"],
            terms=terms_recursive,
            capacity_threshold=capacity_threshold,
            metric_name=metric_type,
            unit=unit
        )

        response_payload = {
            "success": True,
            "inputs": {
                "order": order,
                "coefficients": coefficients,
                "initial_conditions": initial_conditions,
                "n_terms": n_terms,
                "capacity_threshold": capacity_threshold,
                "metric_type": metric_type,
                "unit": unit
            },
            "math_solution": solver_summary,
            "series": {
                "n_indices": list(range(n_terms)),
                "recursive_terms": terms_recursive,
                "explicit_terms": terms_explicit,
                "telemetry_terms": terms_telemetry
            },
            "validation": validation_result,
            "benchmark": benchmark_result,
            "cloudops_diagnosis": cloudops_diagnosis
        }

        return jsonify(response_payload)

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Error en el cálculo analítico: {str(e)}"
        }), 500


@app.route('/api/benchmark', methods=['POST'])
def run_benchmark_endpoint():
    data = request.get_json(silent=True) or {}

    try:
        order = int(data.get('order', 2))
        coefficients = [float(c) for c in data.get('coefficients', [1.2, -0.2])]
        initial_conditions = [float(ic) for ic in data.get('initial_conditions', [100.0, 120.0])]
        n_terms = int(data.get('n_terms', 30))
        repetitions = int(data.get('repetitions', 500))

        solver = RecurrenceSolver(order, coefficients, initial_conditions)
        benchmark_data = BenchmarkEngine.run_benchmark_comparison(
            solver=solver,
            n_terms=n_terms,
            repetitions=repetitions,
            test_single_nth=True
        )

        return jsonify({
            "success": True,
            "benchmark": benchmark_data
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route('/api/validate', methods=['POST'])
def validate_series_endpoint():
    data = request.get_json(silent=True) or {}
    rec = data.get('recursive_terms', [])
    exp = data.get('explicit_terms', [])
    tol = float(data.get('tolerance', 1e-4))

    result = Validator.verify_equality(rec, exp, tolerance=tol)
    return jsonify(result)


@app.route('/api/docs/theory', methods=['GET'])
def get_theory_docs():
    return jsonify({
        "topic_id": "tema_04_sucesiones_recursivas",
        "orders": [
            {
                "order": 1,
                "name": "Orden 1",
                "equation": "a_n = c_1 a_{n-1}",
                "characteristic_eq": "r - c_1 = 0 \\implies r = c_1",
                "explicit_form": "a_n = a_0 \\cdot (c_1)^n"
            },
            {
                "order": 2,
                "name": "Orden 2",
                "equation": "a_n = c_1 a_{n-1} + c_2 a_{n-2}",
                "characteristic_eq": "r^2 - c_1 r - c_2 = 0",
                "cases": [
                    {
                        "type": "distinct_real",
                        "formula": "a_n = C_1 r_1^n + C_2 r_2^n"
                    },
                    {
                        "type": "double_real",
                        "formula": "a_n = (C_1 + C_2 n) r^n"
                    },
                    {
                        "type": "complex_conjugate",
                        "formula": "a_n = \\rho^n [ A \\cos(n\\theta) + B \\sin(n\\theta) ]"
                    }
                ]
            },
            {
                "order": 3,
                "name": "Orden 3",
                "equation": "a_n = c_1 a_{n-1} + c_2 a_{n-2} + c_3 a_{n-3}",
                "characteristic_eq": "r^3 - c_1 r^2 - c_2 r - c_3 = 0",
                "cases": [
                    {
                        "type": "three_distinct_real",
                        "formula": "a_n = C_1 r_1^n + C_2 r_2^n + C_3 r_3^n"
                    },
                    {
                        "type": "double_real_and_single",
                        "formula": "a_n = (C_1 + C_2 n) r_m^n + C_3 r_s^n"
                    },
                    {
                        "type": "triple_real",
                        "formula": "a_n = (C_1 + C_2 n + C_3 n^2) r^n"
                    },
                    {
                        "type": "complex_and_real",
                        "formula": "a_n = C_1 r_1^n + \\rho^n [ A \\cos(n\\theta) + B \\sin(n\\theta) ]"
                    }
                ]
            }
        ]
    })


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 CloudOps Dashboard - Simulador de Sucesiones Recursivas")
    print("📡 Servidor Flask local inicializado en http://127.0.0.1:5000")
    print("📚 Matemática Discreta - Tema 04: Sucesiones Recursivas")
    print("=" * 60)
    app.run(debug=True, host='127.0.0.1', port=5000)