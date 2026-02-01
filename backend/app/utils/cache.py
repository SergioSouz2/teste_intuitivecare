import time
from functools import wraps

def timed_cache(ttl_seconds):
    """Cache simples em memória por ttl_seconds"""
    def decorator(func):
        cache = {}
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            if "value" in cache and now - cache["time"] < ttl_seconds:
                return cache["value"]
            result = func(*args, **kwargs)
            cache["value"] = result
            cache["time"] = now
            return result
        return wrapper
    return decorator
