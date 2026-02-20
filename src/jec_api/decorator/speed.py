import functools
import logging
import time
from typing import Callable, Any, Optional, Union

from .utils import get_dev_store, is_async

logger = logging.getLogger("jec_api")


def speed(
    func: Callable = None,
    *,
    warn_threshold_ms: Optional[float] = None,
    error_threshold_ms: Optional[float] = None,
    include_in_response: bool = False,
) -> Callable:
    """
    Decorator that measures and logs the execution time of an endpoint.
    
    Can be used with or without configuration:
        @speed  # Simple, zero-config
        @speed(warn_threshold_ms=100, error_threshold_ms=500)  # With thresholds
    
    Args:
        warn_threshold_ms: Log warning if execution exceeds this (milliseconds). Default: None
        error_threshold_ms: Log error if execution exceeds this (milliseconds). Default: None
        include_in_response: Add X-Response-Time header to response. Default: False
    
    Logs:
        - Function name and execution time in milliseconds
        - Warning if warn_threshold_ms is exceeded
        - Error if error_threshold_ms is exceeded
    
    Usage:
        class Users(Route):
            @speed
            async def get(self):
                return {"users": []}
            
            @speed(warn_threshold_ms=100, error_threshold_ms=500)
            async def post(self, data: CreateUserRequest):
                return {"created": True}
    """
    
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        async def async_wrapper(*args, **kwargs) -> Any:
            func_name = fn.__qualname__
            start_time = time.perf_counter()
            
            try:
                result = await fn(*args, **kwargs)
                return _process_result(result, func_name, start_time)
            except Exception:
                # Still log timing even on error
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                _log_timing(func_name, elapsed_ms)
                raise
        
        @functools.wraps(fn)
        def sync_wrapper(*args, **kwargs) -> Any:
            func_name = fn.__qualname__
            start_time = time.perf_counter()
            
            try:
                result = fn(*args, **kwargs)
                return _process_result(result, func_name, start_time)
            except Exception:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                _log_timing(func_name, elapsed_ms)
                raise
        
        def _process_result(result: Any, func_name: str, start_time: float) -> Any:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            _log_timing(func_name, elapsed_ms)
            
            # Add header to response if requested
            if include_in_response:
                # Check if result is a Response object with headers
                if hasattr(result, 'headers'):
                    result.headers["X-Response-Time"] = f"{elapsed_ms:.2f}ms"
            
            return result
        
        def _log_timing(func_name: str, elapsed_ms: float):
            # Determine log level based on thresholds
            if error_threshold_ms is not None and elapsed_ms > error_threshold_ms:
                logger.error(f"[SPEED] {func_name} | {elapsed_ms:.2f}ms (EXCEEDED ERROR THRESHOLD: {error_threshold_ms}ms)")
            elif warn_threshold_ms is not None and elapsed_ms > warn_threshold_ms:
                logger.warning(f"[SPEED] {func_name} | {elapsed_ms:.2f}ms (EXCEEDED WARN THRESHOLD: {warn_threshold_ms}ms)")
            else:
                logger.info(f"[SPEED] {func_name} | {elapsed_ms:.2f}ms")
            
            store = get_dev_store()
            if store:
                store.add_speed(func_name, elapsed_ms)
        
        if is_async(fn):
            return async_wrapper
        return sync_wrapper
    
    # Handle both @speed and @speed(...) syntax
    if func is not None:
        return decorator(func)
    return decorator
