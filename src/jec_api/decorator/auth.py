
import functools
import logging
import inspect
from typing import Callable, Any, List, Optional
from inspect import Parameter

from fastapi import Request, HTTPException
from .utils import get_dev_store, find_request

logger = logging.getLogger("jec_api")

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
                
                # Call the handler validation
                try:
                    result = await auth_handler(request, roles)
                    if result is False:
                        raise HTTPException(status_code=403, detail="Not authenticated")
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
