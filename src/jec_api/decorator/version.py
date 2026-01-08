
import functools
import re
import logging
import inspect
from typing import Callable, Any
from inspect import Parameter

from fastapi import Request
from fastapi.responses import JSONResponse

from .utils import get_dev_store, find_request, check_version, is_async

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
            request = find_request(args, kwargs)
            
            if request:
                client_version = request.headers.get("X-API-Version")
                
                # Check for strict versioning
                strict_versioning = getattr(request.app, "strict_versioning", False)
                
                if not client_version and strict_versioning:
                    # Log failure to dev console
                    store = get_dev_store()
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
                    passed = check_version(client_version, operator, required_version)
                    
                    # Log to dev console
                    store = get_dev_store()
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
            request = find_request(args, kwargs)
            
            if request:
                client_version = request.headers.get("X-API-Version")
                
                # Check for strict versioning
                strict_versioning = getattr(request.app, "strict_versioning", False)
                
                if not client_version and strict_versioning:
                    # Log failure to dev console
                    store = get_dev_store()
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
                    passed = check_version(client_version, operator, required_version)
                    
                    # Log to dev console
                    store = get_dev_store()
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
        wrapper = async_wrapper if is_async(func) else sync_wrapper
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
