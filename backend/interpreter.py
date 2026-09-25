import math


class CloudOpsInterpreter:
    @classmethod
    def diagnose_stability(cls, roots):
        return cls.diagnose(roots, terms=None, capacity_threshold=None)

    @classmethod
    def diagnose(cls, roots, terms=None, capacity_threshold=None, metric_name="vCPU Cores", unit="cores"):
        moduli = []
        is_oscillatory = False
        oscillation_period = None
        dominant_root = None
        dominant_modulus = 0.0

        for r in roots:
            if isinstance(r, dict):
                mod = float(r.get("modulus", abs(complex(r.get("real", 0), r.get("imag", 0)))))
                moduli.append(mod)
                if r.get("type") == "complex" or abs(r.get("imag", 0.0)) > 1e-5:
                    is_oscillatory = True
                    theta = abs(float(r.get("angle_rad", 0.0)))
                    if theta > 1e-4:
                        oscillation_period = round((2.0 * math.pi) / theta, 1)
                elif r.get("real", 0.0) < -0.05:
                    is_oscillatory = True
                    oscillation_period = 2.0
            else:
                c_val = complex(r)
                mod = abs(c_val)
                moduli.append(mod)
                if abs(c_val.imag) > 1e-5 or c_val.real < -0.05:
                    is_oscillatory = True
                    if abs(c_val.imag) > 1e-5:
                        theta = abs(math.atan2(c_val.imag, c_val.real))
                        if theta > 1e-4:
                            oscillation_period = round((2.0 * math.pi) / theta, 1)
                    else:
                        oscillation_period = 2.0

            if mod > dominant_modulus:
                dominant_modulus = mod
                dominant_root = r

        dominant_modulus = round(dominant_modulus, 4)

        if dominant_modulus < 0.98:
            regime = "CONVERGENT"
            status = "UNDERUTILIZATION"
            alert_level = "info"
            badge_color = "#3b82f6"
            growth_pct = round((dominant_modulus - 1.0) * 100, 2)
            health_score = 85

        elif 0.98 <= dominant_modulus <= 1.02:
            regime = "EQUILIBRIUM"
            status = "STABLE"
            alert_level = "success"
            badge_color = "#10b981"
            growth_pct = round((dominant_modulus - 1.0) * 100, 2)
            health_score = 98

        elif 1.02 < dominant_modulus <= 1.15:
            regime = "GROWTH"
            status = "ORGANIC_GROWTH"
            alert_level = "warning"
            badge_color = "#f59e0b"
            growth_pct = round((dominant_modulus - 1.0) * 100, 2)
            health_score = 75

        else:
            regime = "DIVERGENT"
            status = "CRITICAL_DIVERGENCE"
            alert_level = "danger"
            badge_color = "#ef4444"
            growth_pct = round((dominant_modulus - 1.0) * 100, 2)
            health_score = 30

        oscillation_report = {
            "has_oscillations": is_oscillatory,
            "period_weeks": oscillation_period
        }

        capacity_report = {
            "threshold": float(capacity_threshold) if capacity_threshold is not None else None,
            "threshold_exceeded": False,
            "saturation_week": None,
            "weeks_to_saturation": None,
            "peak_value": 0.0,
            "peak_headroom_pct": 0.0
        }

        if terms and capacity_threshold is not None and capacity_threshold > 0:
            cap = float(capacity_threshold)
            peak_val = max(terms) if terms else 0.0
            peak_pct = round((peak_val / cap) * 100, 1) if cap > 0 else 0.0

            saturation_idx = None
            for idx, val in enumerate(terms):
                if val >= cap:
                    saturation_idx = idx
                    break

            if saturation_idx is not None:
                capacity_report["threshold_exceeded"] = True
                capacity_report["saturation_week"] = saturation_idx
                capacity_report["weeks_to_saturation"] = saturation_idx
                if alert_level != "danger":
                    alert_level = "warning"
                    badge_color = "#f59e0b"
                health_score = min(health_score, 45)
            else:
                capacity_report["threshold_exceeded"] = False

            capacity_report["peak_value"] = round(float(peak_val), 2)
            capacity_report["peak_headroom_pct"] = peak_pct

        return {
            "regime": regime,
            "status": status,
            "alert_level": alert_level,
            "badge_color": badge_color,
            "dominant_root_modulus": dominant_modulus,
            "growth_rate_pct": growth_pct,
            "health_score": health_score,
            "oscillation_report": oscillation_report,
            "capacity_report": capacity_report,
            "metric_evaluated": metric_name,
            "unit": unit
        }
