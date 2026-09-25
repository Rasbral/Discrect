# CloudOps Capacity Planning - Simulador de Sucesiones Recursivas

Sistema analítico para el **Tema 04: Sucesiones Recursivas** de **Matemática Discreta**. Modela y proyecta la demanda semanal de infraestructura en la nube mediante relaciones de recurrencia de **orden 1, 2 y 3 (nivel reto)**.

Deduce automáticamente la **fórmula explícita cerrada** resolviendo la ecuación característica (raíces reales, con multiplicidad y complejas conjugadas) y sistemas lineales para las constantes asociadas.

---

## Fundamentación Matemática

Para una relación lineal homogénea de orden $k \in \{1, 2, 3\}$:

$$a_n = c_1 a_{n-1} + c_2 a_{n-2} + \dots + c_k a_{n-k}$$

Con polinomio característico:

$$P(r) = r^k - c_1 r^{k-1} - c_2 r^{k-2} - \dots - c_k = 0$$

### Formas Cerradas Soportadas:
- **Orden 1:** $a_n = a_0 \cdot (c_1)^n$
- **Orden 2:**
  - Raíces reales distintas: $a_n = C_1 r_1^n + C_2 r_2^n$
  - Raíz real doble: $a_n = (C_1 + C_2 n) r^n$
  - Raíces complejas conjugadas: $a_n = \rho^n [ A \cos(n\theta) + B \sin(n\theta) ]$
- **Orden 3 (Nivel Reto):**
  - Tres raíces reales distintas: $a_n = C_1 r_1^n + C_2 r_2^n + C_3 r_3^n$
  - Raíz de multiplicidad 2 y simple: $a_n = (C_1 + C_2 n) r_m^n + C_3 r_s^n$
  - Raíz triple: $a_n = (C_1 + C_2 n + C_3 n^2) r^n$
  - Raíz real y par complejo conjugado: $a_n = C_1 r_1^n + \rho^n [ A \cos(n\theta) + B \sin(n\theta) ]$


## Instalación y Ejecución

### Ejecución en 1-Clic:
- **Windows:** Ejecutar `run.bat`
- **Linux/macOS:** Ejecutar `./run.sh`

### Ejecución Manual:
```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Iniciar servidor local
python app.py
```

La consola web estará disponible en `http://127.0.0.1:5000`. Proximamente
