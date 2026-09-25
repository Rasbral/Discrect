class ValidationResult(dict):
    def __bool__(self):
        return bool(self.get("is_valid", False))


class Validator:
    @staticmethod
    def verify_equality(recursive_terms, explicit_terms, tolerance=1e-4):
        if not recursive_terms or not explicit_terms:
            return ValidationResult({
                "is_valid": False,
                "total_terms": 0,
                "matched_terms": 0,
                "discrepancy_count": 0,
                "match_percentage": 0.0,
                "max_absolute_error": 0.0,
                "mean_absolute_error": 0.0,
                "max_relative_error": 0.0,
                "tolerance": tolerance,
                "status": "EMPTY_DATA",
                "term_by_term_audit": []
            })

        if len(recursive_terms) != len(explicit_terms):
            return ValidationResult({
                "is_valid": False,
                "total_terms": max(len(recursive_terms), len(explicit_terms)),
                "matched_terms": 0,
                "discrepancy_count": abs(len(recursive_terms) - len(explicit_terms)),
                "match_percentage": 0.0,
                "max_absolute_error": -1.0,
                "mean_absolute_error": -1.0,
                "max_relative_error": -1.0,
                "tolerance": tolerance,
                "status": "LENGTH_MISMATCH",
                "term_by_term_audit": []
            })

        total_terms = len(recursive_terms)
        audit_list = []
        matched_count = 0
        abs_errors = []
        rel_errors = []

        for n in range(total_terms):
            rec_val = float(recursive_terms[n])
            exp_val = float(explicit_terms[n])

            abs_diff = abs(rec_val - exp_val)
            abs_errors.append(abs_diff)

            denom = max(abs(rec_val), 1.0)
            rel_diff = abs_diff / denom
            rel_errors.append(rel_diff)

            matches = abs_diff <= tolerance or rel_diff <= tolerance

            if matches:
                matched_count += 1

            audit_list.append({
                "n": n,
                "recursive": round(rec_val, 4),
                "explicit": round(exp_val, 4),
                "abs_diff": round(abs_diff, 6),
                "rel_diff_pct": round(rel_diff * 100, 4),
                "matches": matches
            })

        max_abs_err = max(abs_errors) if abs_errors else 0.0
        mean_abs_err = sum(abs_errors) / total_terms if total_terms > 0 else 0.0
        max_rel_err = max(rel_errors) if rel_errors else 0.0
        match_percentage = round((matched_count / total_terms) * 100, 2)
        is_all_valid = (matched_count == total_terms)
        status_code = "EXACT_MATCH" if is_all_valid else "DISCREPANCY_DETECTED"

        return ValidationResult({
            "is_valid": is_all_valid,
            "total_terms": total_terms,
            "matched_terms": matched_count,
            "discrepancy_count": total_terms - matched_count,
            "match_percentage": match_percentage,
            "max_absolute_error": round(float(max_abs_err), 8),
            "mean_absolute_error": round(float(mean_abs_err), 8),
            "max_relative_error": round(float(max_rel_err), 8),
            "tolerance": tolerance,
            "status": status_code,
            "term_by_term_audit": audit_list
        })
