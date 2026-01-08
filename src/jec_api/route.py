"""Route base class for defining API endpoints."""

import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Type
import inspect


# HTTP methods that can be used as method prefixes
HTTP_METHODS = {"get", "post", "put", "delete", "patch", "options", "head"}


class RouteMeta(type):
    """Metaclass that collects route information from class methods."""
    
    def __new__(mcs, name: str, bases: Tuple[type, ...], namespace: Dict[str, Any]) -> type:
        cls = super().__new__(mcs, name, bases, namespace)
        
        # Skip processing for the base Route class itself
        if name == "Route" and not bases:
            return cls
        
        # Collect endpoint methods
        cls._endpoints: List[Tuple[str, str, Callable]] = []
        
        for attr_name, attr_value in namespace.items():
            if attr_name.startswith("_"):
                continue
            if not callable(attr_value):
                continue
            
            parsed = mcs._parse_method_name(attr_name)
            if parsed:
                http_method, sub_path = parsed
                cls._endpoints.append((http_method, sub_path, attr_value))
        
        return cls
    
    @staticmethod
    def _parse_method_name(name: str) -> Optional[Tuple[str, str]]:
        """
        Parse method name to extract HTTP method and sub-path.
        
        Examples:
            get -> (GET, /)
            post -> (POST, /)
            get_by_id -> (GET, /{id})
            get_users -> (GET, /users)
            post_batch -> (POST, /batch)
            get_user_by_id -> (GET, /user/{id})
        """
        parts = name.lower().split("_")
        
        if not parts or parts[0] not in HTTP_METHODS:
            return None
        
        http_method = parts[0].upper()
        
        if len(parts) == 1:
            # Just the HTTP method: get, post, etc.
            return (http_method, "/")
        
        # Check for "by_" pattern indicating path parameter
        path_parts = []
        i = 1
        while i < len(parts):
            if parts[i] == "by" and i + 1 < len(parts):
                # Convert "by_id" to "{id}"
                param_name = parts[i + 1]
                path_parts.append(f"{{{param_name}}}")
                i += 2
            else:
                # Convert to kebab-case path segment
                path_parts.append(parts[i])
                i += 1
        
        if not path_parts:
            return (http_method, "/")
        
        sub_path = "/" + "/".join(path_parts)
        return (http_method, sub_path)


class Route(metaclass=RouteMeta):
    """
    Base class for defining API route endpoints.
    
    Inherit from this class and define methods with HTTP method prefixes:
    - get(), post(), put(), delete(), patch(), options(), head()
    - get_by_id(id: int) -> GET /{id}
    - get_users() -> GET /users
    - post_batch() -> POST /batch
    
    Optionally set `path` class attribute to override the auto-generated path.
    """
    
    # Override this to set a custom path instead of deriving from class name
    path: Optional[str] = None
    
    # Set by metaclass
    _endpoints: List[Tuple[str, str, Callable]] = []
    
    @classmethod
    def get_path(cls) -> str:
        """Get the base path for this route class."""
        if cls.path is not None:
            return cls.path if cls.path.startswith("/") else f"/{cls.path}"
        
        # Convert class name to kebab-case path
        # UserProfiles -> user-profiles
        name = cls.__name__
        # Insert hyphens before uppercase letters and lowercase everything
        kebab = re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower()
        return f"/{kebab}"
    
    @classmethod
    def get_endpoints(cls) -> List[Tuple[str, str, Callable]]:
        """Get all endpoint definitions for this route class."""
        return cls._endpoints
