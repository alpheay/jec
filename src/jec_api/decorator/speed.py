
import functools
import logging
import time
from typing import Callable, Any

from .utils import get_dev_store, is_async

logger = logging.getLogger("jec_api")

def speed(func: Callable) -> Callable:
    """
    Decorator that measures and logs the execution time of an endpoint.
    
    Logs:
        - Function name and execution time in milliseconds
    
    Usage:
        class Users(Route):
            @speed
            async def get(self):
                return {"users": []}
    """
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs) -> Any:
        func_name = func.__qualname__
        start_time = time.perf_counter()
        
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.info(f"[SPEED] {func_name} | {elapsed_ms:.2f}ms")
            store = get_dev_store()
            if store:
                store.add_speed(func_name, elapsed_ms)
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs) -> Any:
        func_name = func.__qualname__
        start_time = time.perf_counter()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.info(f"[SPEED] {func_name} | {elapsed_ms:.2f}ms")
            store = get_dev_store()
            if store:
                store.add_speed(func_name, elapsed_ms)
    
    if is_async(func):
        return async_wrapper
    return sync_wrapper
