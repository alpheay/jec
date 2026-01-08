
import functools
import logging
import time
from typing import Callable, Any, Optional, Dict
from collections import defaultdict

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from .utils import get_dev_store, find_request, is_async

logger = logging.getLogger("jec_api")

# In-memory rate limit storage
# Structure: {key: [(timestamp, count), ...]}
_rate_limit_store: Dict[str, list] = defaultdict(list)


def ratelimit(
    func: Callable = None,
    *,
    limit: int = 100,
    window: int = 60,
    by: str = "ip",
    message: Optional[str] = None,
) -> Callable:
    """
    Decorator that applies rate limiting to an endpoint.
    
    Can be used with or without configuration:
        @ratelimit  # Default: 100 req/min per IP
        @ratelimit(limit=10, window=60)  # 10 req/min
        @ratelimit(limit=1000, window=3600, by="user")  # 1000 req/hour per user
    
    Args:
        limit: Maximum number of requests allowed in the time window. Default: 100
        window: Time window in seconds. Default: 60
        by: Rate limit key - "ip", "user", or "global". Default: "ip"
        message: Custom 429 error message. Default: None
    
    Response Headers Added:
        - X-RateLimit-Limit: Maximum requests allowed
        - X-RateLimit-Remaining: Requests remaining in current window
        - X-RateLimit-Reset: Seconds until window resets
    
    Usage:
        class Users(Route):
            @ratelimit
            async def get(self):
                return {"users": []}
            
            @ratelimit(limit=10, window=60)
            async def post(self):
                return {"created": True}
            
            @ratelimit(limit=5, window=60, message="Too many login attempts")
            async def login(self):
                return {"token": "..."}
    """
    
    def decorator(fn: Callable) -> Callable:
        def _get_rate_limit_key(request: Optional[Request], func_name: str) -> str:
            """Generate rate limit key based on 'by' parameter."""
            if by == "global":
                return f"global:{func_name}"
            elif by == "user":
                # Try to get user ID from request state or auth header
                if request and hasattr(request, 'state') and hasattr(request.state, 'user'):
                    user_id = getattr(request.state.user, 'id', None) or request.state.user.get('id', 'unknown')
                    return f"user:{user_id}:{func_name}"
                elif request:
                    # Fall back to auth header hash
                    auth = request.headers.get("Authorization", "anonymous")
                    return f"user:{hash(auth)}:{func_name}"
                return f"user:anonymous:{func_name}"
            else:  # by == "ip"
                if request and request.client:
                    return f"ip:{request.client.host}:{func_name}"
                return f"ip:unknown:{func_name}"
        
        def _check_rate_limit(key: str) -> tuple[bool, int, int]:
            """
            Check if rate limit is exceeded.
            Returns: (is_allowed, remaining, reset_seconds)
            """
            current_time = time.time()
            window_start = current_time - window
            
            # Clean old entries and count recent requests
            _rate_limit_store[key] = [
                ts for ts in _rate_limit_store[key] 
                if ts > window_start
            ]
            
            current_count = len(_rate_limit_store[key])
            remaining = max(0, limit - current_count - 1)
            
            if current_count >= limit:
                # Calculate reset time
                if _rate_limit_store[key]:
                    oldest = min(_rate_limit_store[key])
                    reset_seconds = int(oldest + window - current_time)
                else:
                    reset_seconds = window
                return False, 0, max(1, reset_seconds)
            
            # Record this request
            _rate_limit_store[key].append(current_time)
            
            # Calculate approximate reset time (when first request in window expires)
            if _rate_limit_store[key]:
                oldest = min(_rate_limit_store[key])
                reset_seconds = int(oldest + window - current_time)
            else:
                reset_seconds = window
            
            return True, remaining, max(1, reset_seconds)
        
        def _add_rate_limit_headers(result: Any, remaining: int, reset_seconds: int):
            """Add rate limit headers to response."""
            if hasattr(result, 'headers'):
                result.headers["X-RateLimit-Limit"] = str(limit)
                result.headers["X-RateLimit-Remaining"] = str(remaining)
                result.headers["X-RateLimit-Reset"] = str(reset_seconds)
        
        @functools.wraps(fn)
        async def async_wrapper(*args, **kwargs) -> Any:
            func_name = fn.__qualname__
            request = find_request(args, kwargs)
            key = _get_rate_limit_key(request, func_name)
            
            is_allowed, remaining, reset_seconds = _check_rate_limit(key)
            
            if not is_allowed:
                error_msg = message or f"Rate limit exceeded. Try again in {reset_seconds} seconds."
                logger.warning(f"[RATELIMIT] {func_name} | key={key} | exceeded")
                
                store = get_dev_store()
                if store:
                    store.add_log("warning", func_name, f"RATELIMIT EXCEEDED: {key}")
                
                response = JSONResponse(
                    status_code=429,
                    content={
                        "error": "Too Many Requests",
                        "detail": error_msg,
                        "retry_after": reset_seconds
                    }
                )
                response.headers["Retry-After"] = str(reset_seconds)
                response.headers["X-RateLimit-Limit"] = str(limit)
                response.headers["X-RateLimit-Remaining"] = "0"
                response.headers["X-RateLimit-Reset"] = str(reset_seconds)
                return response
            
            result = await fn(*args, **kwargs)
            _add_rate_limit_headers(result, remaining, reset_seconds)
            return result
        
        @functools.wraps(fn)
        def sync_wrapper(*args, **kwargs) -> Any:
            func_name = fn.__qualname__
            request = find_request(args, kwargs)
            key = _get_rate_limit_key(request, func_name)
            
            is_allowed, remaining, reset_seconds = _check_rate_limit(key)
            
            if not is_allowed:
                error_msg = message or f"Rate limit exceeded. Try again in {reset_seconds} seconds."
                logger.warning(f"[RATELIMIT] {func_name} | key={key} | exceeded")
                
                store = get_dev_store()
                if store:
                    store.add_log("warning", func_name, f"RATELIMIT EXCEEDED: {key}")
                
                response = JSONResponse(
                    status_code=429,
                    content={
                        "error": "Too Many Requests",
                        "detail": error_msg,
                        "retry_after": reset_seconds
                    }
                )
                response.headers["Retry-After"] = str(reset_seconds)
                response.headers["X-RateLimit-Limit"] = str(limit)
                response.headers["X-RateLimit-Remaining"] = "0"
                response.headers["X-RateLimit-Reset"] = str(reset_seconds)
                return response
            
            result = fn(*args, **kwargs)
            _add_rate_limit_headers(result, remaining, reset_seconds)
            return result
        
        wrapper = async_wrapper if is_async(fn) else sync_wrapper
        
        # Store rate limit metadata for introspection
        wrapper._ratelimit = True
        wrapper._ratelimit_limit = limit
        wrapper._ratelimit_window = window
        wrapper._ratelimit_by = by
        
        return wrapper
    
    # Handle both @ratelimit and @ratelimit(...) syntax
    if func is not None:
        return decorator(func)
    return decorator
