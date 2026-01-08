
import functools
import logging
import asyncio
from typing import Callable, Any, Optional

from fastapi import HTTPException

from .utils import get_dev_store, is_async

logger = logging.getLogger("jec_api")


def timeout(
    func: Callable = None,
    *,
    seconds: float = 30.0,
    message: Optional[str] = None,
) -> Callable:
    """
    Decorator that sets a maximum execution time for an endpoint.
    
    Can be used with or without configuration:
        @timeout  # Default 30s
        @timeout(seconds=5)  # 5 second max
        @timeout(seconds=60, message="Report generation timed out")
    
    Args:
        seconds: Maximum execution time in seconds. Default: 30.0
        message: Custom timeout error message. Default: None
    
    Raises:
        HTTPException: 504 Gateway Timeout if execution exceeds the limit
    
    Usage:
        class Reports(Route):
            @timeout
            async def get(self):
                return {"report": "data"}
            
            @timeout(seconds=60)
            async def generate_large_report(self):
                # Long running operation
                return {"report": "large_data"}
            
            @timeout(seconds=5, message="Quick operation timed out")
            async def quick_check(self):
                return {"status": "ok"}
    """
    
    def decorator(fn: Callable) -> Callable:
        error_message = message or f"Request timed out after {seconds} seconds"
        
        @functools.wraps(fn)
        async def async_wrapper(*args, **kwargs) -> Any:
            func_name = fn.__qualname__
            
            try:
                result = await asyncio.wait_for(
                    fn(*args, **kwargs),
                    timeout=seconds
                )
                return result
            except asyncio.TimeoutError:
                logger.error(f"[TIMEOUT] {func_name} | exceeded {seconds}s")
                
                store = get_dev_store()
                if store:
                    store.add_log("error", func_name, f"TIMEOUT: exceeded {seconds}s")
                
                raise HTTPException(
                    status_code=504,
                    detail=error_message
                )
        
        @functools.wraps(fn)
        def sync_wrapper(*args, **kwargs) -> Any:
            # For sync functions, we can't easily timeout without threads
            # We'll just execute normally and log a warning
            func_name = fn.__qualname__
            logger.warning(f"[TIMEOUT] {func_name} | @timeout on sync functions is not fully supported")
            return fn(*args, **kwargs)
        
        wrapper = async_wrapper if is_async(fn) else sync_wrapper
        
        # Store timeout metadata for introspection
        wrapper._timeout = True
        wrapper._timeout_seconds = seconds
        
        return wrapper
    
    # Handle both @timeout and @timeout(...) syntax
    if func is not None:
        return decorator(func)
    return decorator
