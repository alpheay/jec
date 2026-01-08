
import re
import logging
import asyncio
from typing import Any, Optional, Tuple
from fastapi import Request

# Set up a default logger for JEC-API
logger = logging.getLogger("jec_api")

def get_dev_store() -> Any:
    """Get the DevConsoleStore if dev mode is active."""
    try:
        from ..dev.dev_console import get_store
        return get_store()
    except ImportError:
        return None

def find_request(args: tuple, kwargs: dict) -> Optional[Request]:
    """Find a FastAPI Request object in args or kwargs."""
    # Check kwargs first
    if 'request' in kwargs:
        req = kwargs['request']
        # Use duck typing instead of strict isinstance to avoid import mismatches
        # (e.g. starlette vs fastapi Request depending on version/environment)
        if hasattr(req, "app") and hasattr(req, "headers"):
            return req
    
    # Check args (skip first arg which is usually 'self')
    for arg in args:
        if isinstance(arg, Request) or (hasattr(arg, "app") and hasattr(arg, "headers")):
            return arg
    
    return None

def parse_version(version_str: str) -> Tuple[int, ...]:
    """Parse a version string into a tuple of integers for comparison."""
    # Remove any leading 'v' or 'V'
    version_str = version_str.lstrip('vV')
    # Extract numeric parts
    parts = re.findall(r'\d+', version_str)
    return tuple(int(p) for p in parts) if parts else (0,)

def check_version(client_version: str, operator: str, required_version: str) -> bool:
    """Check if client version satisfies the constraint."""
    client = parse_version(client_version)
    required = parse_version(required_version)
    
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

def is_async(func: Any) -> bool:
    """Check if a function is a coroutine function."""
    return asyncio.iscoroutinefunction(func)

def truncate(value: Any, max_length: int = 200) -> str:
    """Truncate a value's string representation for logging."""
    str_value = str(value)
    if len(str_value) > max_length:
        return str_value[:max_length] + "..."
    return str_value
