
import functools
import logging
from typing import Callable, Any, Optional, Union

from .utils import get_dev_store, is_async, truncate

logger = logging.getLogger("jec_api")

# Log level mapping
_LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}


def log(
    func: Callable = None,
    *,
    level: str = "info",
    include_args: bool = True,
    include_result: bool = True,
    max_length: int = 200,
    message: Optional[str] = None,
) -> Callable:
    """
    Decorator that logs API function calls with request/response info.
    
    Can be used with or without configuration:
        @log  # Simple, zero-config
        @log(level="debug", include_args=False)  # Customized
    
    Args:
        level: Log level - "debug", "info", "warning", "error". Default: "info"
        include_args: Whether to log function arguments. Default: True
        include_result: Whether to log return value. Default: True
        max_length: Maximum length for truncated values. Default: 200
        message: Custom log message prefix. Default: None
    
    Logs:
        - Function name and arguments on entry (if include_args=True)
        - Return value or exception on exit (if include_result=True)
    
    Usage:
        class Users(Route):
            @log
            async def get(self):
                return {"users": []}
            
            @log(level="debug", include_args=False)
            async def post(self, data: CreateUserRequest):
                return {"created": True}
    """
    
    def decorator(fn: Callable) -> Callable:
        log_level = _LOG_LEVELS.get(level.lower(), logging.INFO)
        prefix = f"[{message}] " if message else ""
        
        @functools.wraps(fn)
        async def async_wrapper(*args, **kwargs) -> Any:
            func_name = fn.__qualname__
            
            # Log entry with args (excluding 'self' for cleaner output)
            if include_args:
                filtered_args = args[1:] if args else args  # Skip 'self'
                log_msg = f"args={filtered_args} kwargs={kwargs}"
                logger.log(log_level, f"{prefix}[CALL] {func_name} | {log_msg}")
                
                # Push to dev console if active
                store = get_dev_store()
                if store:
                    store.add_log(level, func_name, f"CALL: {log_msg}", args=str(filtered_args))
            else:
                logger.log(log_level, f"{prefix}[CALL] {func_name}")
                store = get_dev_store()
                if store:
                    store.add_log(level, func_name, "CALL")
            
            try:
                result = await fn(*args, **kwargs)
                if include_result:
                    result_str = truncate(result, max_length)
                    logger.log(log_level, f"{prefix}[RETURN] {func_name} | result={result_str}")
                    store = get_dev_store()
                    if store:
                        store.add_log(level, func_name, f"RETURN: {result_str}", result=result_str)
                return result
            except Exception as e:
                error_msg = f"{type(e).__name__}: {e}"
                logger.error(f"{prefix}[ERROR] {func_name} | exception={error_msg}")
                store = get_dev_store()
                if store:
                    store.add_log("error", func_name, f"ERROR: {error_msg}")
                raise
        
        @functools.wraps(fn)
        def sync_wrapper(*args, **kwargs) -> Any:
            func_name = fn.__qualname__
            
            if include_args:
                filtered_args = args[1:] if args else args
                log_msg = f"args={filtered_args} kwargs={kwargs}"
                logger.log(log_level, f"{prefix}[CALL] {func_name} | {log_msg}")
                
                store = get_dev_store()
                if store:
                    store.add_log(level, func_name, f"CALL: {log_msg}", args=str(filtered_args))
            else:
                logger.log(log_level, f"{prefix}[CALL] {func_name}")
                store = get_dev_store()
                if store:
                    store.add_log(level, func_name, "CALL")
            
            try:
                result = fn(*args, **kwargs)
                if include_result:
                    result_str = truncate(result, max_length)
                    logger.log(log_level, f"{prefix}[RETURN] {func_name} | result={result_str}")
                    store = get_dev_store()
                    if store:
                        store.add_log(level, func_name, f"RETURN: {result_str}", result=result_str)
                return result
            except Exception as e:
                error_msg = f"{type(e).__name__}: {e}"
                logger.error(f"{prefix}[ERROR] {func_name} | exception={error_msg}")
                store = get_dev_store()
                if store:
                    store.add_log("error", func_name, f"ERROR: {error_msg}")
                raise
        
        # Return appropriate wrapper based on function type
        if is_async(fn):
            return async_wrapper
        return sync_wrapper
    
    # Handle both @log and @log(...) syntax
    if func is not None:
        # Called as @log without parentheses
        return decorator(func)
    # Called as @log(...) with parentheses
    return decorator
