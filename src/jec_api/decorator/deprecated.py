import functools
import logging
from typing import Callable, Any, Optional, Union

from fastapi import Request
from fastapi.responses import JSONResponse

from .utils import get_dev_store, find_request, is_async

logger = logging.getLogger("jec_api")


def deprecated(
    message_or_func: Union[str, Callable] = None,
    *,
    message: Optional[str] = None,
    alternative: Optional[str] = None,
    sunset: Optional[str] = None,
) -> Callable:
    """
    Decorator that marks an endpoint as deprecated.
    
    Adds deprecation warnings and headers to responses.
    
    Can be used with or without configuration:
        @deprecated  # Simple deprecation warning
        @deprecated("Use /v2/users instead")  # With message
        @deprecated(alternative="/api/v2/users", sunset="2025-03-01")  # Full config
    
    Args:
        message: Custom deprecation warning message. Default: "This endpoint is deprecated"
        alternative: Suggested alternative endpoint. Default: None
        sunset: Date when endpoint will be removed (ISO 8601 format). Default: None
    
    Response Headers Added:
        - Deprecation: true
        - Sunset: <date> (if sunset is provided)
        - X-Deprecation-Alternative: <alternative> (if alternative is provided)
    
    Usage:
        class OldUsers(Route):
            path = "/v1/users"
            
            @deprecated
            async def get(self):
                return {"users": []}
            
            @deprecated("Use /v2/users instead", sunset="2025-06-01")
            async def post(self):
                return {"created": True}
            
            @deprecated(alternative="/api/v2/users")
            async def put(self):
                return {"updated": True}
    """
    
    def decorator(func: Callable) -> Callable:
        # Determine the deprecation message
        dep_message = message or "This endpoint is deprecated"
        
        def _add_deprecation_headers(result: Any):
            """Add deprecation headers to response."""
            if hasattr(result, 'headers'):
                result.headers["Deprecation"] = "true"
                if sunset:
                    result.headers["Sunset"] = sunset
                if alternative:
                    result.headers["X-Deprecation-Alternative"] = alternative
                if dep_message:
                    result.headers["X-Deprecation-Message"] = dep_message
        
        def _log_deprecation(func_name: str):
            """Log deprecation warning."""
            log_msg = f"[DEPRECATED] {func_name}: {dep_message}"
            if alternative:
                log_msg += f" (alternative: {alternative})"
            if sunset:
                log_msg += f" (sunset: {sunset})"
            logger.warning(log_msg)
            
            store = get_dev_store()
            if store:
                store.add_log("warning", func_name, f"DEPRECATED: {dep_message}")
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            func_name = func.__qualname__
            _log_deprecation(func_name)
            
            result = await func(*args, **kwargs)
            _add_deprecation_headers(result)
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            func_name = func.__qualname__
            _log_deprecation(func_name)
            
            result = func(*args, **kwargs)
            _add_deprecation_headers(result)
            return result
        
        wrapper = async_wrapper if is_async(func) else sync_wrapper
        
        # Store deprecation metadata for introspection
        wrapper._deprecated = True
        wrapper._deprecation_message = dep_message
        wrapper._deprecation_alternative = alternative
        wrapper._deprecation_sunset = sunset
        
        return wrapper
    
    # Handle different call signatures:
    # @deprecated - no args
    # @deprecated("message") - string arg
    # @deprecated(message="msg", alternative="/v2") - keyword args
    if message_or_func is None:
        # @deprecated() with no args
        return decorator
    elif callable(message_or_func):
        # @deprecated without parentheses
        return decorator(message_or_func)
    elif isinstance(message_or_func, str):
        # @deprecated("message")
        message = message_or_func
        return decorator
    else:
        return decorator
