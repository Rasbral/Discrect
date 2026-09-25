import time
import math


class BenchmarkEngine:
    @staticmethod
    def measure_latency(func, *args, **kwargs):
        start_time = time.perf_counter()
        
        result = None
        if func is not None:
            result = func(*args, **kwargs)
            
        end_time = time.perf_counter()
        latency_us = (end_time - start_time) * 1_000_000
        
        return result, round(latency_us, 2)

    @classmethod
    def run_benchmark_comparison(cls, solver, n_terms=30, repetitions=500, test_single_nth=True):
        if repetitions < 10:
            repetitions = 10
        if repetitions > 5000:
            repetitions = 5000

        for _ in range(5):
            solver.generate_terms_recursive(n_terms)
            solver.generate_terms_explicit(n_terms)

        rec_latencies = []
        rec_total_start = time.perf_counter()
        for _ in range(repetitions):
            t0 = time.perf_counter()
            solver.generate_terms_recursive(n_terms)
            t1 = time.perf_counter()
            rec_latencies.append((t1 - t0) * 1_000_000)
        rec_total_time_ms = (time.perf_counter() - rec_total_start) * 1000

        exp_latencies = []
        exp_total_start = time.perf_counter()
        for _ in range(repetitions):
            t0 = time.perf_counter()
            solver.generate_terms_explicit(n_terms)
            t1 = time.perf_counter()
            exp_latencies.append((t1 - t0) * 1_000_000)
        exp_total_time_ms = (time.perf_counter() - exp_total_start) * 1000

        rec_avg_us = sum(rec_latencies) / repetitions
        rec_min_us = min(rec_latencies)
        rec_max_us = max(rec_latencies)
        rec_std_us = math.sqrt(sum((x - rec_avg_us) ** 2 for x in rec_latencies) / repetitions)

        exp_avg_us = sum(exp_latencies) / repetitions
        exp_min_us = min(exp_latencies)
        exp_max_us = max(exp_latencies)
        exp_std_us = math.sqrt(sum((x - exp_avg_us) ** 2 for x in exp_latencies) / repetitions)

        speedup_series = round(rec_avg_us / exp_avg_us, 2) if exp_avg_us > 0 else 1.0

        nth_index = n_terms - 1
        nth_rec_latencies = []
        for _ in range(repetitions):
            t0 = time.perf_counter()
            seq = solver.generate_terms_recursive(n_terms)
            _ = seq[-1]
            t1 = time.perf_counter()
            nth_rec_latencies.append((t1 - t0) * 1_000_000)

        nth_exp_latencies = []
        for _ in range(repetitions):
            t0 = time.perf_counter()
            _ = solver.generate_terms_explicit(n_terms)[-1]
            t1 = time.perf_counter()
            nth_exp_latencies.append((t1 - t0) * 1_000_000)

        nth_rec_avg_us = sum(nth_rec_latencies) / repetitions
        nth_exp_avg_us = sum(nth_exp_latencies) / repetitions
        nth_speedup = round(nth_rec_avg_us / nth_exp_avg_us, 2) if nth_exp_avg_us > 0 else 1.0

        return {
            "repetitions": repetitions,
            "n_terms": n_terms,
            "target_nth_term": nth_index,
            "recursive": {
                "avg_latency_us": round(rec_avg_us, 3),
                "min_latency_us": round(rec_min_us, 3),
                "max_latency_us": round(rec_max_us, 3),
                "std_latency_us": round(rec_std_us, 3),
                "total_time_ms": round(rec_total_time_ms, 3),
                "time_complexity": "O(n)",
                "space_complexity": "O(n)"
            },
            "explicit": {
                "avg_latency_us": round(exp_avg_us, 3),
                "min_latency_us": round(exp_min_us, 3),
                "max_latency_us": round(exp_max_us, 3),
                "std_latency_us": round(exp_std_us, 3),
                "total_time_ms": round(exp_total_time_ms, 3),
                "time_complexity": "O(1)",
                "space_complexity": "O(1)"
            },
            "comparison": {
                "series_speedup": speedup_series,
                "latency_delta_us": round(rec_avg_us - exp_avg_us, 3),
                "faster_method": "explicit" if exp_avg_us <= rec_avg_us else "recursive",
                "nth_term_rec_us": round(nth_rec_avg_us, 3),
                "nth_term_exp_us": round(nth_exp_avg_us, 3),
                "nth_term_speedup": nth_speedup
            }
        }
