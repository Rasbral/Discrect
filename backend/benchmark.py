import time

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
