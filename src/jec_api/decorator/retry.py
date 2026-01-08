
import functools
import logging
import asyncio
from typing import Callable, Any, Optional, Tuple, Type

from .utils import get_dev_store, is_async

logger = logging.getLogger("jec_api")


def retry(
    func: Callable = None,
    *,
    attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> Callable:
    """
    Decorator that automatically retries failed operations with exponential backoff.
    
    Can be used with or without configuration:
        @retry  # 3 attempts with exponential backoff
        @retry(attempts=5, delay=0.5)  # 5 attempts, starting with 0.5s delay
        @retry(exceptions=(ConnectionError, TimeoutError))  # Only retry specific exceptions
    
    Args:
        attempts: Maximum number of retry attempts. Default: 3
        delay: Initial delay between retries in seconds. Default: 1.0
        backoff: Multiplier for delay after each retry. Default: 2.0
        exceptions: Tuple of exception types to catch and retry. Default: (Exception,)
    
    Usage:
        class ExternalAPI(Route):
            @retry
            async def get(self):
                # May fail intermittently
                return await external_service.fetch()
            
            @retry(attempts=5, delay=0.5)
            async def post(self, data):
                return await external_service.send(data)
            
            @retry(exceptions=(ConnectionError, TimeoutError))
            async def connect(self):
                return await external_service.connect()
    """
    
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        async def async_wrapper(*args, **kwargs) -> Any:
            func_name = fn.__qualname__
            last_exception = None
            current_delay = delay
            
            for attempt in range(1, attempts + 1):
                try:
                    result = await fn(*args, **kwargs)
                    
                    # Log successful retry if this wasn't the first attempt
                    if attempt > 1:
                        logger.info(f"[RETRY] {func_name} | succeeded on attempt {attempt}")
                        store = get_dev_store()
                        if store:
                            store.add_log("info", func_name, f"RETRY: succeeded on attempt {attempt}")
                    
                    return result
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < attempts:
                        logger.warning(
                            f"[RETRY] {func_name} | attempt {attempt}/{attempts} failed: {e}. "
                            f"Retrying in {current_delay:.2f}s..."
                        )
                        
                        store = get_dev_store()
                        if store:
                            store.add_log(
                                "warning", 
                                func_name, 
                                f"RETRY: attempt {attempt}/{attempts} failed, retrying in {current_delay:.2f}s"
                            )
                        
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"[RETRY] {func_name} | all {attempts} attempts failed. Last error: {e}"
                        )
                        
                        store = get_dev_store()
                        if store:
                            store.add_log(
                                "error", 
                                func_name, 
                                f"RETRY: all {attempts} attempts failed"
                            )
            
            # All attempts failed, raise the last exception
            raise last_exception
        
        @functools.wraps(fn)
        def sync_wrapper(*args, **kwargs) -> Any:
            import time
            
            func_name = fn.__qualname__
            last_exception = None
            current_delay = delay
            
            for attempt in range(1, attempts + 1):
                try:
                    result = fn(*args, **kwargs)
                    
                    if attempt > 1:
                        logger.info(f"[RETRY] {func_name} | succeeded on attempt {attempt}")
                        store = get_dev_store()
                        if store:
                            store.add_log("info", func_name, f"RETRY: succeeded on attempt {attempt}")
                    
                    return result
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < attempts:
                        logger.warning(
                            f"[RETRY] {func_name} | attempt {attempt}/{attempts} failed: {e}. "
                            f"Retrying in {current_delay:.2f}s..."
                        )
                        
                        store = get_dev_store()
                        if store:
                            store.add_log(
                                "warning", 
                                func_name, 
                                f"RETRY: attempt {attempt}/{attempts} failed, retrying in {current_delay:.2f}s"
                            )
                        
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"[RETRY] {func_name} | all {attempts} attempts failed. Last error: {e}"
                        )
                        
                        store = get_dev_store()
                        if store:
                            store.add_log(
                                "error", 
                                func_name, 
                                f"RETRY: all {attempts} attempts failed"
                            )
            
            raise last_exception
        
        wrapper = async_wrapper if is_async(fn) else sync_wrapper
        
        # Store retry metadata for introspection
        wrapper._retry = True
        wrapper._retry_attempts = attempts
        wrapper._retry_delay = delay
        wrapper._retry_backoff = backoff
        
        return wrapper
    
    # Handle both @retry and @retry(...) syntax
    if func is not None:
        return decorator(func)
    return decorator
