import math
import numpy as np
import sympy as sp


class RecurrenceSolver:
    def __init__(self, order, coefficients, initial_conditions):
        if order not in [1, 2, 3]:
            raise ValueError(f"El orden debe ser 1, 2 o 3. Recibido: {order}")
        if len(coefficients) != order:
            raise ValueError(f"Se esperaban {order} coeficientes, pero se recibieron {len(coefficients)}")
        if len(initial_conditions) != order:
            raise ValueError(f"Se esperaban {order} condiciones iniciales, pero se recibieron {len(initial_conditions)}")

        self.order = int(order)
        self.coefficients = [float(c) for c in coefficients]
        self.initial_conditions = [float(ic) for ic in initial_conditions]
        
        self.roots_info = []
        self.roots_raw = []
        self.constants = []
        self.solution_type = "unknown"
        self.explicit_formula_text = ""
        self.explicit_formula_latex = ""
        self.sympy_formula_str = ""
        self.char_poly_text = ""
        self.char_poly_latex = ""
        self.steps = []
        
        self._analyze()

    def _analyze(self):
        self._build_characteristic_polynomial()
        self.solve_characteristic_equation()
        self._solve_linear_system_for_constants()
        self._build_explicit_formula()
        self._generate_step_by_step()

    def _build_characteristic_polynomial(self):
        poly_terms_text = [f"r^{self.order}"]
        poly_terms_latex = [f"r^{{{self.order}}}" if self.order > 1 else "r"]

        for i, c in enumerate(self.coefficients):
            power = self.order - (i + 1)
            coeff = -c
            sign_str = " + " if coeff >= 0 else " - "
            abs_coeff = abs(coeff)
            coeff_formatted = f"{abs_coeff:.4g}"

            if power == 0:
                var_str = ""
                var_latex = ""
            elif power == 1:
                var_str = "r"
                var_latex = "r"
            else:
                var_str = f"r^{power}"
                var_latex = f"r^{{{power}}}"

            if abs_coeff == 1 and power > 0:
                poly_terms_text.append(f"{sign_str}{var_str}")
                poly_terms_latex.append(f"{sign_str}{var_latex}")
            else:
                poly_terms_text.append(f"{sign_str}{coeff_formatted}{var_str}")
                poly_terms_latex.append(f"{sign_str}{coeff_formatted} {var_latex}")

        self.char_poly_text = "".join(poly_terms_text) + " = 0"
        self.char_poly_latex = "".join(poly_terms_latex) + " = 0"

    def solve_characteristic_equation(self):
        poly_coeffs = [1.0] + [-c for c in self.coefficients]
        raw_roots = np.roots(poly_coeffs)
        self.roots_raw = list(raw_roots)
        self.roots_info = []

        cleaned_roots = []
        for r in raw_roots:
            real_part = float(r.real)
            imag_part = float(r.imag)
            if abs(imag_part) < 1e-6:
                cleaned_roots.append(complex(real_part, 0.0))
            else:
                cleaned_roots.append(complex(real_part, imag_part))

        if self.order == 1:
            r1 = cleaned_roots[0]
            self.solution_type = "order1"
            self.roots_info.append(self._format_root_dict(1, r1, multiplicity=1))

        elif self.order == 2:
            r1, r2 = cleaned_roots[0], cleaned_roots[1]
            if abs(r1.imag) > 1e-6 or abs(r2.imag) > 1e-6:
                self.solution_type = "order2_complex"
                if r1.imag < 0:
                    r1, r2 = r2, r1
                self.roots_info.append(self._format_root_dict(1, r1, multiplicity=1, is_complex=True))
                self.roots_info.append(self._format_root_dict(2, r2, multiplicity=1, is_complex=True))
            elif abs(r1.real - r2.real) < 1e-5:
                self.solution_type = "order2_double"
                self.roots_info.append(self._format_root_dict(1, r1, multiplicity=2))
                self.roots_info.append(self._format_root_dict(2, r2, multiplicity=2))
            else:
                self.solution_type = "order2_distinct"
                self.roots_info.append(self._format_root_dict(1, r1, multiplicity=1))
                self.roots_info.append(self._format_root_dict(2, r2, multiplicity=1))

        elif self.order == 3:
            complex_roots = [r for r in cleaned_roots if abs(r.imag) > 1e-6]
            real_roots = [r for r in cleaned_roots if abs(r.imag) <= 1e-6]

            if len(complex_roots) >= 2:
                self.solution_type = "order3_complex"
                real_r = real_roots[0]
                c1, c2 = complex_roots[0], complex_roots[1]
                if c1.imag < 0:
                    c1, c2 = c2, c1
                self.roots_info.append(self._format_root_dict(1, real_r, multiplicity=1))
                self.roots_info.append(self._format_root_dict(2, c1, multiplicity=1, is_complex=True))
                self.roots_info.append(self._format_root_dict(3, c2, multiplicity=1, is_complex=True))
            else:
                vals = sorted([r.real for r in real_roots])
                if abs(vals[0] - vals[1]) < 1e-5 and abs(vals[1] - vals[2]) < 1e-5:
                    self.solution_type = "order3_triple"
                    for idx, val in enumerate(vals, 1):
                        self.roots_info.append(self._format_root_dict(idx, complex(val, 0.0), multiplicity=3))
                elif abs(vals[0] - vals[1]) < 1e-5:
                    self.solution_type = "order3_double"
                    self.roots_info.append(self._format_root_dict(1, complex(vals[0], 0.0), multiplicity=2))
                    self.roots_info.append(self._format_root_dict(2, complex(vals[1], 0.0), multiplicity=2))
                    self.roots_info.append(self._format_root_dict(3, complex(vals[2], 0.0), multiplicity=1))
                elif abs(vals[1] - vals[2]) < 1e-5:
                    self.solution_type = "order3_double"
                    self.roots_info.append(self._format_root_dict(1, complex(vals[1], 0.0), multiplicity=2))
                    self.roots_info.append(self._format_root_dict(2, complex(vals[2], 0.0), multiplicity=2))
                    self.roots_info.append(self._format_root_dict(3, complex(vals[0], 0.0), multiplicity=1))
                else:
                    self.solution_type = "order3_distinct"
                    for idx, val in enumerate(vals, 1):
                        self.roots_info.append(self._format_root_dict(idx, complex(val, 0.0), multiplicity=1))

        return self.roots_info

    def _format_root_dict(self, index, val, multiplicity=1, is_complex=False):
        real_p = float(val.real)
        imag_p = float(val.imag)
        modulus = float(abs(val))
        angle_rad = float(math.atan2(imag_p, real_p))
        angle_deg = float(math.degrees(angle_rad))

        if is_complex or abs(imag_p) > 1e-6:
            sign = "+" if imag_p >= 0 else "-"
            display_str = f"{real_p:.4g} {sign} {abs(imag_p):.4g}i"
            latex_str = f"{real_p:.4g} {sign} {abs(imag_p):.4g}i"
            type_str = "complex"
        else:
            display_str = f"{real_p:.4g}"
            latex_str = f"{real_p:.4g}"
            type_str = "real"

        return {
            "index": index,
            "real": real_p,
            "imag": imag_p,
            "modulus": modulus,
            "angle_rad": angle_rad,
            "angle_deg": angle_deg,
            "multiplicity": multiplicity,
            "type": type_str,
            "display": display_str,
            "latex": latex_str
        }

    def _solve_linear_system_for_constants(self):
        self.constants = []

        if self.order == 1:
            c1 = self.initial_conditions[0]
            self.constants = [
                {"name": "C_1", "symbol": "C_1", "value": float(c1), "formatted": f"{c1:.4g}"}
            ]

        elif self.order == 2:
            a0, a1 = self.initial_conditions[0], self.initial_conditions[1]

            if self.solution_type == "order2_distinct":
                r1 = self.roots_info[0]["real"]
                r2 = self.roots_info[1]["real"]
                M = np.array([[1.0, 1.0], [r1, r2]], dtype=float)
                rhs = np.array([a0, a1], dtype=float)
                try:
                    c_vals = np.linalg.solve(M, rhs)
                except np.linalg.LinAlgError:
                    c_vals = np.linalg.lstsq(M, rhs, rcond=None)[0]

                self.constants = [
                    {"name": "C_1", "symbol": "C_1", "value": float(c_vals[0]), "formatted": f"{c_vals[0]:.4g}"},
                    {"name": "C_2", "symbol": "C_2", "value": float(c_vals[1]), "formatted": f"{c_vals[1]:.4g}"}
                ]

            elif self.solution_type == "order2_double":
                r = self.roots_info[0]["real"]
                c1 = a0
                if abs(r) > 1e-9:
                    c2 = (a1 - c1 * r) / r
                else:
                    c2 = 0.0
                self.constants = [
                    {"name": "C_1", "symbol": "C_1", "value": float(c1), "formatted": f"{c1:.4g}"},
                    {"name": "C_2", "symbol": "C_2", "value": float(c2), "formatted": f"{c2:.4g}"}
                ]

            elif self.solution_type == "order2_complex":
                alpha = self.roots_info[0]["real"]
                beta = self.roots_info[0]["imag"]
                A = a0
                if abs(beta) > 1e-9:
                    B = (a1 - alpha * A) / beta
                else:
                    B = 0.0
                self.constants = [
                    {"name": "A", "symbol": "A", "value": float(A), "formatted": f"{A:.4g}"},
                    {"name": "B", "symbol": "B", "value": float(B), "formatted": f"{B:.4g}"}
                ]

        elif self.order == 3:
            a0, a1, a2 = self.initial_conditions[0], self.initial_conditions[1], self.initial_conditions[2]

            if self.solution_type == "order3_distinct":
                r1 = self.roots_info[0]["real"]
                r2 = self.roots_info[1]["real"]
                r3 = self.roots_info[2]["real"]
                M = np.array([
                    [1.0, 1.0, 1.0],
                    [r1, r2, r3],
                    [r1**2, r2**2, r3**2]
                ], dtype=float)
                rhs = np.array([a0, a1, a2], dtype=float)
                try:
                    c_vals = np.linalg.solve(M, rhs)
                except np.linalg.LinAlgError:
                    c_vals = np.linalg.lstsq(M, rhs, rcond=None)[0]

                self.constants = [
                    {"name": "C_1", "symbol": "C_1", "value": float(c_vals[0]), "formatted": f"{c_vals[0]:.4g}"},
                    {"name": "C_2", "symbol": "C_2", "value": float(c_vals[1]), "formatted": f"{c_vals[1]:.4g}"},
                    {"name": "C_3", "symbol": "C_3", "value": float(c_vals[2]), "formatted": f"{c_vals[2]:.4g}"}
                ]

            elif self.solution_type == "order3_double":
                rm = self.roots_info[0]["real"]
                rs = self.roots_info[2]["real"]
                M = np.array([
                    [1.0, 0.0, 1.0],
                    [rm, rm, rs],
                    [rm**2, 2.0 * (rm**2), rs**2]
                ], dtype=float)
                rhs = np.array([a0, a1, a2], dtype=float)
                try:
                    c_vals = np.linalg.solve(M, rhs)
                except np.linalg.LinAlgError:
                    c_vals = np.linalg.lstsq(M, rhs, rcond=None)[0]

                self.constants = [
                    {"name": "C_1", "symbol": "C_1", "value": float(c_vals[0]), "formatted": f"{c_vals[0]:.4g}"},
                    {"name": "C_2", "symbol": "C_2", "value": float(c_vals[1]), "formatted": f"{c_vals[1]:.4g}"},
                    {"name": "C_3", "symbol": "C_3", "value": float(c_vals[2]), "formatted": f"{c_vals[2]:.4g}"}
                ]

            elif self.solution_type == "order3_triple":
                r = self.roots_info[0]["real"]
                M = np.array([
                    [1.0, 0.0, 0.0],
                    [r, r, r],
                    [r**2, 2.0 * (r**2), 4.0 * (r**2)]
                ], dtype=float)
                rhs = np.array([a0, a1, a2], dtype=float)
                try:
                    c_vals = np.linalg.solve(M, rhs)
                except np.linalg.LinAlgError:
                    c_vals = np.linalg.lstsq(M, rhs, rcond=None)[0]

                self.constants = [
                    {"name": "C_1", "symbol": "C_1", "value": float(c_vals[0]), "formatted": f"{c_vals[0]:.4g}"},
                    {"name": "C_2", "symbol": "C_2", "value": float(c_vals[1]), "formatted": f"{c_vals[1]:.4g}"},
                    {"name": "C_3", "symbol": "C_3", "value": float(c_vals[2]), "formatted": f"{c_vals[2]:.4g}"}
                ]

            elif self.solution_type == "order3_complex":
                r1 = self.roots_info[0]["real"]
                alpha = self.roots_info[1]["real"]
                beta = self.roots_info[1]["imag"]
                M = np.array([
                    [1.0, 1.0, 0.0],
                    [r1, alpha, beta],
                    [r1**2, alpha**2 - beta**2, 2.0 * alpha * beta]
                ], dtype=float)
                rhs = np.array([a0, a1, a2], dtype=float)
                try:
                    c_vals = np.linalg.solve(M, rhs)
                except np.linalg.LinAlgError:
                    c_vals = np.linalg.lstsq(M, rhs, rcond=None)[0]

                self.constants = [
                    {"name": "C_1", "symbol": "C_1", "value": float(c_vals[0]), "formatted": f"{c_vals[0]:.4g}"},
                    {"name": "A", "symbol": "A", "value": float(c_vals[1]), "formatted": f"{c_vals[1]:.4g}"},
                    {"name": "B", "symbol": "B", "value": float(c_vals[2]), "formatted": f"{c_vals[2]:.4g}"}
                ]

        return self.constants

    def _build_explicit_formula(self):
        if self.order == 1:
            c1 = self.constants[0]["value"]
            r1 = self.roots_info[0]["real"]
            self.explicit_formula_text = f"a_n = {c1:.4g} * ({r1:.4g})^n"
            self.explicit_formula_latex = f"a_n = {c1:.4g} \\cdot ({r1:.4g})^{{n}}"

        elif self.order == 2:
            if self.solution_type == "order2_distinct":
                c1 = self.constants[0]["value"]
                c2 = self.constants[1]["value"]
                r1 = self.roots_info[0]["real"]
                r2 = self.roots_info[1]["real"]
                sign2 = " + " if c2 >= 0 else " - "
                self.explicit_formula_text = f"a_n = {c1:.4g} * ({r1:.4g})^n{sign2}{abs(c2):.4g} * ({r2:.4g})^n"
                self.explicit_formula_latex = f"a_n = {c1:.4g} \\cdot ({r1:.4g})^{{n}} {sign2} {abs(c2):.4g} \\cdot ({r2:.4g})^{{n}}"

            elif self.solution_type == "order2_double":
                c1 = self.constants[0]["value"]
                c2 = self.constants[1]["value"]
                r = self.roots_info[0]["real"]
                sign2 = " + " if c2 >= 0 else " - "
                self.explicit_formula_text = f"a_n = ({c1:.4g}{sign2}{abs(c2):.4g} * n) * ({r:.4g})^n"
                self.explicit_formula_latex = f"a_n = ({c1:.4g} {sign2} {abs(c2):.4g} n) \\cdot ({r:.4g})^{{n}}"

            elif self.solution_type == "order2_complex":
                A = self.constants[0]["value"]
                B = self.constants[1]["value"]
                rho = self.roots_info[0]["modulus"]
                theta = self.roots_info[0]["angle_rad"]
                sign_b = " + " if B >= 0 else " - "
                self.explicit_formula_text = f"a_n = ({rho:.4g})^n * [{A:.4g} * cos({theta:.4g} * n){sign_b}{abs(B):.4g} * sin({theta:.4g} * n)]"
                self.explicit_formula_latex = f"a_n = ({rho:.4g})^{{n}} \\left[ {A:.4g} \\cos({theta:.4g} n) {sign_b} {abs(B):.4g} \\sin({theta:.4g} n) \\right]"

        elif self.order == 3:
            if self.solution_type == "order3_distinct":
                c1 = self.constants[0]["value"]
                c2 = self.constants[1]["value"]
                c3 = self.constants[2]["value"]
                r1 = self.roots_info[0]["real"]
                r2 = self.roots_info[1]["real"]
                r3 = self.roots_info[2]["real"]
                sign2 = " + " if c2 >= 0 else " - "
                sign3 = " + " if c3 >= 0 else " - "
                self.explicit_formula_text = (
                    f"a_n = {c1:.4g} * ({r1:.4g})^n{sign2}{abs(c2):.4g} * ({r2:.4g})^n{sign3}{abs(c3):.4g} * ({r3:.4g})^n"
                )
                self.explicit_formula_latex = (
                    f"a_n = {c1:.4g} \\cdot ({r1:.4g})^{{n}} {sign2} {abs(c2):.4g} \\cdot ({r2:.4g})^{{n}} {sign3} {abs(c3):.4g} \\cdot ({r3:.4g})^{{n}}"
                )

            elif self.solution_type == "order3_double":
                c1 = self.constants[0]["value"]
                c2 = self.constants[1]["value"]
                c3 = self.constants[2]["value"]
                rm = self.roots_info[0]["real"]
                rs = self.roots_info[2]["real"]
                sign2 = " + " if c2 >= 0 else " - "
                sign3 = " + " if c3 >= 0 else " - "
                self.explicit_formula_text = (
                    f"a_n = ({c1:.4g}{sign2}{abs(c2):.4g} * n) * ({rm:.4g})^n{sign3}{abs(c3):.4g} * ({rs:.4g})^n"
                )
                self.explicit_formula_latex = (
                    f"a_n = ({c1:.4g} {sign2} {abs(c2):.4g} n) \\cdot ({rm:.4g})^{{n}} {sign3} {abs(c3):.4g} \\cdot ({rs:.4g})^{{n}}"
                )

            elif self.solution_type == "order3_triple":
                c1 = self.constants[0]["value"]
                c2 = self.constants[1]["value"]
                c3 = self.constants[2]["value"]
                r = self.roots_info[0]["real"]
                sign2 = " + " if c2 >= 0 else " - "
                sign3 = " + " if c3 >= 0 else " - "
                self.explicit_formula_text = (
                    f"a_n = ({c1:.4g}{sign2}{abs(c2):.4g} * n{sign3}{abs(c3):.4g} * n^2) * ({r:.4g})^n"
                )
                self.explicit_formula_latex = (
                    f"a_n = ({c1:.4g} {sign2} {abs(c2):.4g} n {sign3} {abs(c3):.4g} n^{{2}}) \\cdot ({r:.4g})^{{n}}"
                )

            elif self.solution_type == "order3_complex":
                c1 = self.constants[0]["value"]
                A = self.constants[1]["value"]
                B = self.constants[2]["value"]
                r1 = self.roots_info[0]["real"]
                rho = self.roots_info[1]["modulus"]
                theta = self.roots_info[1]["angle_rad"]
                sign_b = " + " if B >= 0 else " - "
                self.explicit_formula_text = (
                    f"a_n = {c1:.4g} * ({r1:.4g})^n + ({rho:.4g})^n * [{A:.4g} * cos({theta:.4g} * n){sign_b}{abs(B):.4g} * sin({theta:.4g} * n)]"
                )
                self.explicit_formula_latex = (
                    f"a_n = {c1:.4g} \\cdot ({r1:.4g})^{{n}} + ({rho:.4g})^{{n}} \\left[ {A:.4g} \\cos({theta:.4g} n) {sign_b} {abs(B):.4g} \\sin({theta:.4g} n) \\right]"
                )

        try:
            n_sym = sp.Symbol('n', integer=True)
            y_sym = sp.Function('y')
            rec_sym = y_sym(n_sym)
            for j, c in enumerate(self.coefficients, 1):
                rec_sym -= sp.Rational(str(round(c, 4))) * y_sym(n_sym - j)
            
            ics = {y_sym(i): sp.Rational(str(round(ic, 4))) for i, ic in enumerate(self.initial_conditions)}
            sol_sym = sp.rsolve(rec_sym, y_sym(n_sym), ics)
            if sol_sym is not None:
                self.sympy_formula_str = str(sp.simplify(sol_sym))
        except Exception:
            self.sympy_formula_str = ""

    def _generate_step_by_step(self):
        self.steps = []

        rec_display = "a_n = " + " + ".join([f"{c:.4g} a_{{n-{i+1}}}" for i, c in enumerate(self.coefficients)])
        rec_display = rec_display.replace("+ -", "- ")
        ics_display = ", ".join([f"a_{i} = {ic:.4g}" for i, ic in enumerate(self.initial_conditions)])

        self.steps.append({
            "step": 1,
            "name": "recurrence_definition",
            "latex": f"{rec_display} \\quad \\text{{con}} \\quad {ics_display}"
        })

        self.steps.append({
            "step": 2,
            "name": "characteristic_equation",
            "latex": f"P(r) = {self.char_poly_latex}"
        })

        roots_latex_list = [f"r_{{{r['index']}}} = {r['latex']}" for r in self.roots_info]
        self.steps.append({
            "step": 3,
            "name": "roots_solution",
            "latex": ", \\quad ".join(roots_latex_list)
        })

        self.steps.append({
            "step": 4,
            "name": "general_solution",
            "latex": self._get_general_solution_template_latex()
        })

        self.steps.append({
            "step": 5,
            "name": "initial_conditions_system",
            "latex": self._get_initial_conditions_system_latex()
        })

        const_latex_list = [f"{c['name']} = {c['formatted']}" for c in self.constants]
        self.steps.append({
            "step": 6,
            "name": "constants_solution",
            "latex": ", \\quad ".join(const_latex_list)
        })

        self.steps.append({
            "step": 7,
            "name": "explicit_formula",
            "latex": self.explicit_formula_latex
        })

    def _get_general_solution_template_latex(self):
        if self.order == 1:
            return "a_n = C_1 \\cdot (r_1)^n"
        elif self.order == 2:
            if self.solution_type == "order2_distinct":
                return "a_n = C_1 \\cdot (r_1)^n + C_2 \\cdot (r_2)^n"
            elif self.solution_type == "order2_double":
                return "a_n = (C_1 + C_2 \\cdot n) \\cdot (r)^n"
            elif self.solution_type == "order2_complex":
                return "a_n = \\rho^n \\left[ A \\cos(n \\theta) + B \\sin(n \\theta) \\right]"
        elif self.order == 3:
            if self.solution_type == "order3_distinct":
                return "a_n = C_1 \\cdot (r_1)^n + C_2 \\cdot (r_2)^n + C_3 \\cdot (r_3)^n"
            elif self.solution_type == "order3_double":
                return "a_n = (C_1 + C_2 \\cdot n) \\cdot (r_m)^n + C_3 \\cdot (r_s)^n"
            elif self.solution_type == "order3_triple":
                return "a_n = (C_1 + C_2 \\cdot n + C_3 \\cdot n^2) \\cdot (r)^n"
            elif self.solution_type == "order3_complex":
                return "a_n = C_1 \\cdot (r_1)^n + \\rho^n \\left[ A \\cos(n \\theta) + B \\sin(n \\theta) \\right]"
        return "a_n = \\sum C_i r_i^n"

    def _get_initial_conditions_system_latex(self):
        if self.order == 1:
            return f"n = 0: \\quad C_1 = {self.initial_conditions[0]:.4g}"
        elif self.order == 2:
            a0, a1 = self.initial_conditions[0], self.initial_conditions[1]
            if self.solution_type == "order2_distinct":
                r1, r2 = self.roots_info[0]["real"], self.roots_info[1]["real"]
                return f"\\begin{{cases}} C_1 + C_2 = {a0:.4g} \\\\ C_1 ({r1:.4g}) + C_2 ({r2:.4g}) = {a1:.4g} \\end{{cases}}"
            elif self.solution_type == "order2_double":
                r = self.roots_info[0]["real"]
                return f"\\begin{{cases}} C_1 = {a0:.4g} \\\\ (C_1 + C_2)({r:.4g}) = {a1:.4g} \\end{{cases}}"
            elif self.solution_type == "order2_complex":
                alpha, beta = self.roots_info[0]["real"], self.roots_info[0]["imag"]
                return f"\\begin{{cases}} A = {a0:.4g} \\\\ ({alpha:.4g}) A + ({beta:.4g}) B = {a1:.4g} \\end{{cases}}"
        elif self.order == 3:
            a0, a1, a2 = self.initial_conditions[0], self.initial_conditions[1], self.initial_conditions[2]
            return f"\\begin{{cases}} a_0 = {a0:.4g} \\\\ a_1 = {a1:.4g} \\\\ a_2 = {a2:.4g} \\end{{cases}}"
        return ""

    def generate_terms_recursive(self, n_terms):
        if n_terms <= 0:
            return []
        
        terms = []
        for i in range(min(n_terms, self.order)):
            terms.append(float(self.initial_conditions[i]))

        for i in range(self.order, n_terms):
            val = 0.0
            for j in range(self.order):
                val += self.coefficients[j] * terms[i - (j + 1)]
            if abs(val) > 1e15:
                val = 1e15 if val > 0 else -1e15
            terms.append(float(val))

        return [round(t, 6) for t in terms]

    def generate_terms_explicit(self, n_terms):
        if n_terms <= 0:
            return []

        terms = []

        if self.order == 1:
            c1 = self.constants[0]["value"]
            r1 = self.roots_info[0]["real"]
            for n in range(n_terms):
                if r1 == 0.0:
                    val = c1 if n == 0 else 0.0
                else:
                    try:
                        val = c1 * (r1 ** n)
                    except OverflowError:
                        val = 1e15
                terms.append(float(val))

        elif self.order == 2:
            if self.solution_type == "order2_distinct":
                c1, c2 = self.constants[0]["value"], self.constants[1]["value"]
                r1, r2 = self.roots_info[0]["real"], self.roots_info[1]["real"]
                for n in range(n_terms):
                    try:
                        p1 = c1 * (r1 ** n) if r1 != 0.0 or n == 0 else 0.0
                        p2 = c2 * (r2 ** n) if r2 != 0.0 or n == 0 else 0.0
                        val = p1 + p2
                    except OverflowError:
                        val = 1e15
                    terms.append(float(val))

            elif self.solution_type == "order2_double":
                c1, c2 = self.constants[0]["value"], self.constants[1]["value"]
                r = self.roots_info[0]["real"]
                for n in range(n_terms):
                    try:
                        base = r ** n if r != 0.0 or n == 0 else 0.0
                        val = (c1 + c2 * n) * base
                    except OverflowError:
                        val = 1e15
                    terms.append(float(val))

            elif self.solution_type == "order2_complex":
                A, B = self.constants[0]["value"], self.constants[1]["value"]
                rho = self.roots_info[0]["modulus"]
                theta = self.roots_info[0]["angle_rad"]
                for n in range(n_terms):
                    try:
                        p_rho = (rho ** n) if rho != 0.0 or n == 0 else 0.0
                        trig = A * math.cos(n * theta) + B * math.sin(n * theta)
                        val = p_rho * trig
                    except OverflowError:
                        val = 1e15
                    terms.append(float(val))

        elif self.order == 3:
            if self.solution_type == "order3_distinct":
                c1 = self.constants[0]["value"]
                c2 = self.constants[1]["value"]
                c3 = self.constants[2]["value"]
                r1 = self.roots_info[0]["real"]
                r2 = self.roots_info[1]["real"]
                r3 = self.roots_info[2]["real"]
                for n in range(n_terms):
                    try:
                        p1 = c1 * (r1 ** n) if r1 != 0.0 or n == 0 else 0.0
                        p2 = c2 * (r2 ** n) if r2 != 0.0 or n == 0 else 0.0
                        p3 = c3 * (r3 ** n) if r3 != 0.0 or n == 0 else 0.0
                        val = p1 + p2 + p3
                    except OverflowError:
                        val = 1e15
                    terms.append(float(val))

            elif self.solution_type == "order3_double":
                c1, c2, c3 = self.constants[0]["value"], self.constants[1]["value"], self.constants[2]["value"]
                rm = self.roots_info[0]["real"]
                rs = self.roots_info[2]["real"]
                for n in range(n_terms):
                    try:
                        base_m = rm ** n if rm != 0.0 or n == 0 else 0.0
                        base_s = rs ** n if rs != 0.0 or n == 0 else 0.0
                        val = (c1 + c2 * n) * base_m + c3 * base_s
                    except OverflowError:
                        val = 1e15
                    terms.append(float(val))

            elif self.solution_type == "order3_triple":
                c1, c2, c3 = self.constants[0]["value"], self.constants[1]["value"], self.constants[2]["value"]
                r = self.roots_info[0]["real"]
                for n in range(n_terms):
                    try:
                        base = r ** n if r != 0.0 or n == 0 else 0.0
                        val = (c1 + c2 * n + c3 * (n ** 2)) * base
                    except OverflowError:
                        val = 1e15
                    terms.append(float(val))

            elif self.solution_type == "order3_complex":
                c1 = self.constants[0]["value"]
                A = self.constants[1]["value"]
                B = self.constants[2]["value"]
                r1 = self.roots_info[0]["real"]
                rho = self.roots_info[1]["modulus"]
                theta = self.roots_info[1]["angle_rad"]
                for n in range(n_terms):
                    try:
                        p1 = c1 * (r1 ** n) if r1 != 0.0 or n == 0 else 0.0
                        p_rho = (rho ** n) if rho != 0.0 or n == 0 else 0.0
                        trig = A * math.cos(n * theta) + B * math.sin(n * theta)
                        val = p1 + p_rho * trig
                    except OverflowError:
                        val = 1e15
                    terms.append(float(val))

        return [round(t, 6) for t in terms]

    def get_explicit_formula(self):
        return {
            "formula_text": self.explicit_formula_text,
            "formula_latex": self.explicit_formula_latex,
            "sympy_formula": self.sympy_formula_str
        }

    def get_summary(self):
        return {
            "order": self.order,
            "coefficients": self.coefficients,
            "initial_conditions": self.initial_conditions,
            "solution_type": self.solution_type,
            "characteristic_polynomial_text": self.char_poly_text,
            "characteristic_polynomial_latex": self.char_poly_latex,
            "roots": self.roots_info,
            "constants": self.constants,
            "explicit_formula_text": self.explicit_formula_text,
            "explicit_formula_latex": self.explicit_formula_latex,
            "sympy_formula": self.sympy_formula_str,
            "steps": self.steps
        }
