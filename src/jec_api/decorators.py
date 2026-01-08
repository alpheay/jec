"""Decorators for API endpoint logging and performance monitoring."""

import re
import time
import logging
import functools
from typing import Callable, Any, Optional

from fastapi import Request
from fastapi.responses import JSONResponse

# Set up a default logger for JEC-API
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
        logger.info(f"[CALL] {func_name} | args={filtered_args} kwargs={kwargs}")
        
        try:
            result = await func(*args, **kwargs)
            logger.info(f"[RETURN] {func_name} | result={_truncate(result)}")
            return result
        except Exception as e:
            logger.error(f"[ERROR] {func_name} | exception={type(e).__name__}: {e}")
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs) -> Any:
        func_name = func.__qualname__
        
        filtered_args = args[1:] if args else args
        logger.info(f"[CALL] {func_name} | args={filtered_args} kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.info(f"[RETURN] {func_name} | result={_truncate(result)}")
            return result
        except Exception as e:
            logger.error(f"[ERROR] {func_name} | exception={type(e).__name__}: {e}")
            raise
    
    # Return appropriate wrapper based on function type
    if _is_async(func):
        return async_wrapper
    return sync_wrapper


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
    
    if _is_async(func):
        return async_wrapper
    return sync_wrapper


def version(constraint: str) -> Callable:
    """
    Decorator that enforces API version constraints on an endpoint.
    
    Checks the `X-API-Version` header against the specified constraint.
    Returns 400 Bad Request if the version is incompatible.
    
    Supported operators: >=, <=, >, <, ==, !=
    
    Args:
        constraint: Version constraint string (e.g., ">=1.0.0", "<2.0.0", "==1.5.0")
    
    Usage:
        class Users(Route):
            @version(">=1.0.0")
            async def get(self):
                return {"users": []}
            
            @version(">=2.0.0")
            async def post(self, data: CreateUserRequest):
                # Only available in API v2.0.0+
                return {"created": True}
    """
    # Parse the constraint
    match = re.match(r'^(>=|<=|>|<|==|!=)?(.+)$', constraint.strip())
    if not match:
        raise ValueError(f"Invalid version constraint: {constraint}")
    
    operator = match.group(1) or "=="
    required_version = match.group(2).strip()
    
    # Validate version format (basic semver)
    if not re.match(r'^\d+(\.\d+)*', required_version):
        raise ValueError(f"Invalid version format: {required_version}")
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            # Try to find Request in kwargs or args
            request = _find_request(args, kwargs)
            
            if request:
                client_version = request.headers.get("X-API-Version")
                
                if client_version:
                    if not _check_version(client_version, operator, required_version):
                        return JSONResponse(
                            status_code=400,
                            content={
                                "error": "API version incompatible",
                                "detail": f"This endpoint requires API version {constraint}",
                                "your_version": client_version,
                                "required": constraint
                            }
                        )
            
            return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            request = _find_request(args, kwargs)
            
            if request:
                client_version = request.headers.get("X-API-Version")
                
                if client_version:
                    if not _check_version(client_version, operator, required_version):
                        return JSONResponse(
                            status_code=400,
                            content={
                                "error": "API version incompatible",
                                "detail": f"This endpoint requires API version {constraint}",
                                "your_version": client_version,
                                "required": constraint
                            }
                        )
            
            return func(*args, **kwargs)
        
        # Store version info on the function for introspection
        wrapper = async_wrapper if _is_async(func) else sync_wrapper
        wrapper._version_constraint = constraint
        return wrapper
    
    return decorator


def _find_request(args: tuple, kwargs: dict) -> Optional[Request]:
    """Find a FastAPI Request object in args or kwargs."""
    # Check kwargs first
    if 'request' in kwargs and isinstance(kwargs['request'], Request):
        return kwargs['request']
    
    # Check args (skip first arg which is usually 'self')
    for arg in args:
        if isinstance(arg, Request):
            return arg
    
    return None


def _parse_version(version_str: str) -> tuple:
    """Parse a version string into a tuple of integers for comparison."""
    # Remove any leading 'v' or 'V'
    version_str = version_str.lstrip('vV')
    # Extract numeric parts
    parts = re.findall(r'\d+', version_str)
    return tuple(int(p) for p in parts) if parts else (0,)


def _check_version(client_version: str, operator: str, required_version: str) -> bool:
    """Check if client version satisfies the constraint."""
    client = _parse_version(client_version)
    required = _parse_version(required_version)
    
    # Pad versions to same length for comparison
    max_len = max(len(client), len(required))
    client = client + (0,) * (max_len - len(client))
    required = required + (0,) * (max_len - len(required))
    
    if operator == ">=":
        return client >= required
    elif operator == "<=":
        return client <= required
    elif operator == ">":
        return client > required
    elif operator == "<":
        return client < required
    elif operator == "==":
        return client == required
    elif operator == "!=":
        return client != required
    
    return False


def _is_async(func: Callable) -> bool:
    """Check if a function is a coroutine function."""
    import asyncio
    return asyncio.iscoroutinefunction(func)


def _truncate(value: Any, max_length: int = 200) -> str:
    """Truncate a value's string representation for logging."""
    str_value = str(value)
    if len(str_value) > max_length:
        return str_value[:max_length] + "..."
    return str_value
