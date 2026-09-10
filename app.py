# pyrefly: ignore [missing-import] (esto es porque no tengo las librerias instaladas)
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({"status": "success", "message": "API de Simulación Activa - Frontend en construcción"})

@app.route('/api/simulate', methods=['POST'])
def simulate():
    return jsonify({
        "status": "success",
        "data": {
            "recursive_terms": [],
            "explicit_terms": [],
            "formula": "a_n = C1*r1^n",
            "benchmark": {
                "recursive_us": 0.0,
                "explicit_us": 0.0
            },
            "diagnosis": "Estable"
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
