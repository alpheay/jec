
import functools
import re
import logging
import inspect
from typing import Callable, Any, Optional
from inspect import Parameter

from fastapi import Request
from fastapi.responses import JSONResponse

from .utils import get_dev_store, find_request, check_version, is_async

logger = logging.getLogger("jec_api")


def version(
    constraint: str,
    *,
    deprecated: bool = False,
    sunset: Optional[str] = None,
    message: Optional[str] = None,
) -> Callable:
    """
    Decorator that enforces API version constraints on an endpoint.
    
    Checks the `X-API-Version` header against the specified constraint.
    Returns 400 Bad Request if the version is incompatible.
    
    Supported operators: >=, <=, >, <, ==, !=
    
    Args:
        constraint: Version constraint string (e.g., ">=1.0.0", "<2.0.0", "==1.5.0")
        deprecated: Mark endpoint as deprecated (adds Deprecation header). Default: False
        sunset: Sunset date for deprecated endpoint (ISO 8601 format). Default: None
        message: Custom deprecation/version message. Default: None
    
    Usage:
        class Users(Route):
            @version(">=1.0.0")
            async def get(self):
                return {"users": []}
            
            @version(">=1.0.0", deprecated=True, sunset="2025-06-01")
            async def get_old(self):
                return {"users": [], "warning": "Use v2"}
            
            @version(">=2.0.0", message="Use v3 API for better performance")
            async def post(self, data: CreateUserRequest):
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
        
        def _add_deprecation_headers(response: Any, request: Optional[Request] = None):
            """Add deprecation headers if endpoint is deprecated."""
            if not deprecated:
                return
            
            # For JSONResponse or Response objects, add headers
            if hasattr(response, 'headers'):
                response.headers["Deprecation"] = "true"
                if sunset:
                    response.headers["Sunset"] = sunset
                if message:
                    response.headers["X-Deprecation-Message"] = message
            
            # Log deprecation warning
            deprecation_msg = message or f"Endpoint {func.__qualname__} is deprecated"
            if sunset:
                deprecation_msg += f" (sunset: {sunset})"
            logger.warning(f"[DEPRECATED] {deprecation_msg}")
        
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
                        error_detail = message or f"This endpoint requires API version {constraint}"
                        return JSONResponse(
                            status_code=400,
                            content={
                                "error": "API version incompatible",
                                "detail": error_detail,
                                "your_version": client_version,
                                "required": constraint
                            }
                        )
            
            # If we injected request but the original function doesn't want it, remove it
            if not request_param_present and 'request' in kwargs:
                kwargs.pop('request')
                
            result = await func(*args, **kwargs)
            _add_deprecation_headers(result, request)
            return result
        
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
                        error_detail = message or f"This endpoint requires API version {constraint}"
                        return JSONResponse(
                            status_code=400,
                            content={
                                "error": "API version incompatible",
                                "detail": error_detail,
                                "your_version": client_version,
                                "required": constraint
                            }
                        )
            
            # If we injected request but the original function doesn't want it, remove it
            if not request_param_present and 'request' in kwargs:
                kwargs.pop('request')

            result = func(*args, **kwargs)
            _add_deprecation_headers(result, request)
            return result
        
        # Store version info on the function for introspection
        wrapper = async_wrapper if is_async(func) else sync_wrapper
        wrapper._version_constraint = constraint
        wrapper._deprecated = deprecated
        wrapper._sunset = sunset
        
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
