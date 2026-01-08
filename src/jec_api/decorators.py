"""Decorators for API endpoint logging and performance monitoring."""

import re
import time
import logging
import functools
from typing import Callable, Any, Optional

from fastapi import Request
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

# Set up a default logger for JEC-API
logger = logging.getLogger("jec_api")


def _get_dev_store():
    """Get the DevConsoleStore if dev mode is active."""
    try:
        from .dev.dev_console import get_store
        return get_store()
    except ImportError:
        return None


def auth(enabled: bool = True, roles: list[str] = None) -> Callable:
    """
    Decorator that enforces authentication and optional role-based access control.
    
    This decorator delegates the actual authentication logic to a handler registered
    with the `Core` application.
    
    Args:
        enabled: Whether to enable authentication for this endpoint. Defaults to True.
        roles: Optional list of roles required to access this endpoint.
               These are passed to the auth handler.
    
    Usage:
        # First, register your auth handler in your main app file:
        app = Core()
        
        async def my_auth_handler(request: Request, roles: list[str] = None) -> bool:
            token = request.headers.get("Authorization")
            if not token:
                return False  # Will result in 403 Forbidden
                
            # Validate token...
            user_roles = ["user"]
            if roles:
                for role in roles:
                    if role not in user_roles:
                        raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            return True
            
        app.set_auth_handler(my_auth_handler)
        
        # Then use the decorator on your routes:
        class PrivateConfig(Route):
            @auth(True, roles=["admin"])
            async def get(self):
                return {"secret": "data"}
                
            @auth(False)  # Explicitly public
            async def post(self):
                return {"status": "ok"}
    """
    roles = roles or []
    
    import inspect
    from inspect import Parameter

    def decorator(func: Callable) -> Callable:
        # Inspect the original function signature to handle 'request' injection
        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        
        request_param_present = False
        for param in params:
            if param.name == "request" or param.annotation == Request:
                request_param_present = True
                break
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            request = _find_request(args, kwargs)
            
            if enabled and request:
                # Get the auth handler from the app
                auth_handler = getattr(request.app, "auth_handler", None)
                
                if not auth_handler:
                    # If auth is required but no handler is set, this is a server configuration error
                    logger.error(f"[AUTH] No auth handler registered for {func.__qualname__}")
                    raise HTTPException(
                        status_code=500, 
                        detail="Authentication is enabled but no handler is configured."
                    )
                
                # Call the handler validation
                try:
                    result = await auth_handler(request, roles)
                    if result is False:
                        raise HTTPException(status_code=403, detail="Not authenticated")
                except HTTPException as e:
                    # Log failure to dev console if needed
                    store = _get_dev_store()
                    if store:
                        store.add_log("error", func.__qualname__, f"AUTH FAILED: {str(e)}")
                    raise e
                except Exception as e:
                    logger.error(f"[AUTH] Error in auth handler: {e}")
                    raise HTTPException(status_code=500, detail="Internal authentication error")

            # Remove injected request if not needed
            if not request_param_present and 'request' in kwargs:
                kwargs.pop('request')
                
            return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            # Sync wrapper logic is tricky because the handler might be async.
            # We enforce async handlers for now or require sync handlers to not await?
            # Actually, standardizing on async handlers is safer for FastAPI.
            # If the user provides a sync handler, it might block. 
            # But let's assume the user might define a sync handler too.
            # However, since this wrapper is sync, we can't await an async handler easily without helpers.
            # Best practice: make the wrapper async if we need to await auth? 
            # But we can't make the wrapper async if the decorated function is sync (it changes behavior from sync to async).
            # For simplicity in this iteration, we will implement the async wrapper primarily.
            # If the underlying function is sync, we can still use the async wrapper logic if we are in an async context (FastAPI handles this).
            # WAIT. If func is sync, FastAPI runs it in a threadpool. If we wrap it in async def, FastAPI runs it in the event loop.
            # So if we want to run async auth checks, we SHOULD always wrap in async def!
            # So we don't actually need a sync_wrapper for the outer part.
            
            # BUT, we have existing valid sync wrappers in other decorators.
            # Let's see how `log` does it. `log` has both.
            # If we force async wrapper, it changes the interface.
            # If the user defines `def get(self): ...` and we return `async def get(self): ...`, FastAPI is fine with it.
            # It just means the route is treated as an async path operation.
            # This is generally acceptable for auth which likely involves DB/IO.
            pass # We will use the async_wrapper for both cases below.
            
            # Re-implementing logic for the 'sync_wrapper' locally is hard if auth is async.
            # We will return the async_wrapper for ALL functions if auth is enabled.
            # This is a reasonable trade-off.
            
            # To be safe, let's just make one wrapper implementation that is async
            # and calls the original func appropriately.
            return func(*args, **kwargs) # Placeholder, we will use async_wrapper for all.

        # We will use the async wrapper for everything because auth is likely async (DB, etc)
        # and FastAPI handles async wrappers around sync functions perfectly fine.
        final_wrapper = async_wrapper
        
        # Modify signature if request param is missing
        if not request_param_present:
            new_params = params.copy()
            new_params.append(
                Parameter(
                    "request",
                    kind=Parameter.KEYWORD_ONLY,
                    annotation=Request,
                    default=None
                )
            )
            final_wrapper.__signature__ = sig.replace(parameters=new_params)
            
        return final_wrapper

    return decorator


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
        store = _get_dev_store()
        if store:
            store.add_log("info", func_name, f"CALL: {log_msg}", args=str(filtered_args))
        
        try:
            result = await func(*args, **kwargs)
            result_str = _truncate(result)
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
        
        store = _get_dev_store()
        if store:
            store.add_log("info", func_name, f"CALL: {log_msg}", args=str(filtered_args))
        
        try:
            result = func(*args, **kwargs)
            result_str = _truncate(result)
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
            store = _get_dev_store()
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
            store = _get_dev_store()
            if store:
                store.add_speed(func_name, elapsed_ms)
    
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
    
    import inspect
    from inspect import Parameter

    def decorator(func: Callable) -> Callable:
        # Inspect the original function signature
        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        
        # Check if 'request' is already in parameters
        request_param_present = False
        for param in params:
            if param.name == "request" or param.annotation == Request:
                request_param_present = True
                break
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            # Try to find Request in kwargs or args
            request = _find_request(args, kwargs)
            
            if request:
                client_version = request.headers.get("X-API-Version")
                
                # Check for strict versioning
                strict_versioning = getattr(request.app, "strict_versioning", False)
                
                if not client_version and strict_versioning:
                    # Log failure to dev console
                    store = _get_dev_store()
                    if store:
                        store.add_version_check(func.__qualname__, constraint, "MISSING", False)
                        
                    return JSONResponse(
                        status_code=400,
                        content={
                            "error": "API version required",
                            "detail": "This API requires strict versioning. Please provide the X-API-Version header.",
                            "required": "true"
                        }
                    )

                if client_version:
                    passed = _check_version(client_version, operator, required_version)
                    
                    # Log to dev console
                    store = _get_dev_store()
                    if store:
                        store.add_version_check(func.__qualname__, constraint, client_version, passed)
                    
                    if not passed:
                        return JSONResponse(
                            status_code=400,
                            content={
                                "error": "API version incompatible",
                                "detail": f"This endpoint requires API version {constraint}",
                                "your_version": client_version,
                                "required": constraint
                            }
                        )
            
            # If we injected request but the original function doesn't want it, remove it
            if not request_param_present and 'request' in kwargs:
                kwargs.pop('request')
                
            return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            request = _find_request(args, kwargs)
            
            if request:
                client_version = request.headers.get("X-API-Version")
                
                # Check for strict versioning
                strict_versioning = getattr(request.app, "strict_versioning", False)
                
                if not client_version and strict_versioning:
                    # Log failure to dev console
                    store = _get_dev_store()
                    if store:
                        store.add_version_check(func.__qualname__, constraint, "MISSING", False)
                        
                    return JSONResponse(
                        status_code=400,
                        content={
                            "error": "API version required",
                            "detail": "This API requires strict versioning. Please provide the X-API-Version header.",
                            "required": "true"
                        }
                    )

                if client_version:
                    passed = _check_version(client_version, operator, required_version)
                    
                    # Log to dev console
                    store = _get_dev_store()
                    if store:
                        store.add_version_check(func.__qualname__, constraint, client_version, passed)
                    
                    if not passed:
                        return JSONResponse(
                            status_code=400,
                            content={
                                "error": "API version incompatible",
                                "detail": f"This endpoint requires API version {constraint}",
                                "your_version": client_version,
                                "required": constraint
                            }
                        )
            
            # If we injected request but the original function doesn't want it, remove it
            if not request_param_present and 'request' in kwargs:
                kwargs.pop('request')

            return func(*args, **kwargs)
        
        # Store version info on the function for introspection
        wrapper = async_wrapper if _is_async(func) else sync_wrapper
        wrapper._version_constraint = constraint
        
        # Modify signature if request param is missing
        if not request_param_present:
            new_params = params.copy()
            new_params.append(
                Parameter(
                    "request",
                    kind=Parameter.KEYWORD_ONLY,
                    annotation=Request,
                    default=None
                )
            )
            wrapper.__signature__ = sig.replace(parameters=new_params)
            
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
