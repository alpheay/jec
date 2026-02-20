import functools
import logging
import inspect
from typing import Callable, Any, List, Optional
from inspect import Parameter

from fastapi import Request, HTTPException
from .utils import get_dev_store, find_request, is_async

logger = logging.getLogger("jec_api")


def auth(
    enabled: bool = True,
    *,
    roles: Optional[List[str]] = None,
    scopes: Optional[List[str]] = None,
    require_all: bool = False,
    custom_error: Optional[str] = None,
) -> Callable:
    """
    Decorator that enforces authentication and optional role/scope-based access control.
    
    This decorator delegates the actual authentication logic to a handler registered
    with the `Core` application.
    
    Args:
        enabled: Whether to enable authentication for this endpoint. Defaults to True.
        roles: Optional list of roles required to access this endpoint.
        scopes: Optional list of OAuth-style scopes required to access this endpoint.
        require_all: If True, require ALL roles/scopes. If False, require ANY one. Default: False
        custom_error: Custom 403 error message. Default: None
    
    Usage:
        # First, register your auth handler in your main app file:
        app = Core()
        
        async def my_auth_handler(request: Request, roles: list[str] = None, scopes: list[str] = None) -> bool:
            token = request.headers.get("Authorization")
            if not token:
                return False  # Will result in 403 Forbidden
                
            # Validate token...
            user_roles = ["user"]
            user_scopes = ["read:users"]
            
            if roles:
                for role in roles:
                    if role not in user_roles:
                        raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            if scopes:
                for scope in scopes:
                    if scope not in user_scopes:
                        raise HTTPException(status_code=403, detail="Insufficient scope")
            
            return True
            
        app.set_auth_handler(my_auth_handler)
        
        # Then use the decorator on your routes:
        class PrivateConfig(Route):
            @auth(True, roles=["admin"])
            async def get(self):
                return {"secret": "data"}
            
            @auth(True, roles=["admin", "moderator"], require_all=True)
            async def post(self):
                return {"status": "ok"}
                
            @auth(True, scopes=["read:users", "write:users"])
            async def put(self):
                return {"status": "updated"}
                
            @auth(False)  # Explicitly public
            async def delete(self):
                return {"status": "ok"}
    """
    _roles = roles or []
    _scopes = scopes or []

    def decorator(func: Callable) -> Callable:
        # Inspect the original function signature to handle 'request' injection
        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        
        request_param_present = False
        for param in params:
            if param.name == "request" or param.annotation == Request:
                request_param_present = True
                break
        
        def _get_error_message():
            if custom_error:
                return custom_error
            return "Not authenticated"
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            request = find_request(args, kwargs)
            
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
                
                # Call the handler validation with roles and scopes
                try:
                    # Try to call with both roles and scopes (new signature)
                    try:
                        result = await auth_handler(request, _roles, _scopes, require_all)
                    except TypeError:
                        # Fall back to old signature (just roles)
                        result = await auth_handler(request, _roles)
                    
                    if result is False:
                        raise HTTPException(status_code=403, detail=_get_error_message())
                except HTTPException as e:
                    # Log failure to dev console if needed
                    store = get_dev_store()
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
            request = find_request(args, kwargs)
            
            if enabled and request:
                auth_handler = getattr(request.app, "auth_handler", None)
                
                if not auth_handler:
                    logger.error(f"[AUTH] No auth handler registered for {func.__qualname__}")
                    raise HTTPException(
                        status_code=500, 
                        detail="Authentication is enabled but no handler is configured."
                    )
                
                try:
                    # For sync context, we still need to handle async auth handler
                    import asyncio
                    try:
                        result = asyncio.get_event_loop().run_until_complete(
                            auth_handler(request, _roles, _scopes, require_all)
                        )
                    except TypeError:
                        result = asyncio.get_event_loop().run_until_complete(
                            auth_handler(request, _roles)
                        )
                    
                    if result is False:
                        raise HTTPException(status_code=403, detail=_get_error_message())
                except HTTPException as e:
                    store = get_dev_store()
                    if store:
                        store.add_log("error", func.__qualname__, f"AUTH FAILED: {str(e)}")
                    raise e
                except Exception as e:
                    logger.error(f"[AUTH] Error in auth handler: {e}")
                    raise HTTPException(status_code=500, detail="Internal authentication error")

            if not request_param_present and 'request' in kwargs:
                kwargs.pop('request')
                
            return func(*args, **kwargs)

        # We will use the async wrapper for everything because auth is likely async
        final_wrapper = async_wrapper if is_async(func) else async_wrapper
        
        # Store auth metadata on the function for introspection
        final_wrapper._auth_enabled = enabled
        final_wrapper._auth_roles = _roles
        final_wrapper._auth_scopes = _scopes
        final_wrapper._auth_require_all = require_all
        
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
