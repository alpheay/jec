
import functools
import logging
from typing import Callable, Any

from .utils import get_dev_store, is_async, truncate

logger = logging.getLogger("jec_api")

def log(func: Callable) -> Callable:
    """
    Decorator that logs API function calls with request/response info.
    
    Logs:
        - Function name and arguments on entry
        - Return value or exception on exit
    
    Usage:
        class Users(Route):
            @log
            async def get(self):
                return {"users": []}
    """
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs) -> Any:
        func_name = func.__qualname__
        
        # Log entry with args (excluding 'self' for cleaner output)
        filtered_args = args[1:] if args else args  # Skip 'self'
        log_msg = f"args={filtered_args} kwargs={kwargs}"
        logger.info(f"[CALL] {func_name} | {log_msg}")
        
        # Push to dev console if active
        store = get_dev_store()
        if store:
            store.add_log("info", func_name, f"CALL: {log_msg}", args=str(filtered_args))
        
        try:
            result = await func(*args, **kwargs)
            result_str = truncate(result)
            logger.info(f"[RETURN] {func_name} | result={result_str}")
            if store:
                store.add_log("info", func_name, f"RETURN: {result_str}", result=result_str)
            return result
        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            logger.error(f"[ERROR] {func_name} | exception={error_msg}")
            if store:
                store.add_log("error", func_name, f"ERROR: {error_msg}")
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs) -> Any:
        func_name = func.__qualname__
        
        filtered_args = args[1:] if args else args
        log_msg = f"args={filtered_args} kwargs={kwargs}"
        logger.info(f"[CALL] {func_name} | {log_msg}")
        
        store = get_dev_store()
        if store:
            store.add_log("info", func_name, f"CALL: {log_msg}", args=str(filtered_args))
        
        try:
            result = func(*args, **kwargs)
            result_str = truncate(result)
            logger.info(f"[RETURN] {func_name} | result={result_str}")
            if store:
                store.add_log("info", func_name, f"RETURN: {result_str}", result=result_str)
            return result
        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            logger.error(f"[ERROR] {func_name} | exception={error_msg}")
            if store:
                store.add_log("error", func_name, f"ERROR: {error_msg}")
            raise
    
    # Return appropriate wrapper based on function type
    if is_async(func):
        return async_wrapper
    return sync_wrapper
