"""Route base class for defining API endpoints."""

import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, get_type_hints
import inspect

from pydantic import BaseModel


# HTTP methods that can be used as method prefixes
HTTP_METHODS = {"get", "post", "put", "delete", "patch", "options", "head"}


class RouteMeta(type):
    """Metaclass that collects route information from class methods."""
    
    def __new__(mcs, name: str, bases: Tuple[type, ...], namespace: Dict[str, Any]) -> type:
        cls = super().__new__(mcs, name, bases, namespace)
        
        # Skip processing for the base Route class itself
        if name == "Route" and not bases:
            return cls
        
        # Collect endpoint methods: (http_method, sub_path, callable, type_hints)
        cls._endpoints: List[Tuple[str, str, Callable, Dict[str, Type]]] = []
        
        for attr_name, attr_value in namespace.items():
            if attr_name.startswith("_"):
                continue
            if not callable(attr_value):
                continue
            
            parsed = mcs._parse_method_name(attr_name)
            if parsed:
                http_method, sub_path = parsed
                # Extract type hints from method signature
                type_hints = mcs._extract_type_hints(attr_value)
                cls._endpoints.append((http_method, sub_path, attr_value, type_hints))
        
        return cls
    
    @staticmethod
    def _extract_type_hints(func: Callable) -> Dict[str, Type]:
        """Extract type hints from function signature, excluding 'self' and 'return'."""
        try:
            hints = get_type_hints(func)
        except Exception:
            # Fallback if get_type_hints fails (e.g., forward references)
            hints = getattr(func, '__annotations__', {})
        
        # Remove 'return' and 'self' from hints
        hints.pop('return', None)
        hints.pop('self', None)
        return hints
    
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
            get_details_by_item_id -> (GET, /details/{item_id})
        """
        name_lower = name.lower()
        
        # Check if starts with a known method
        found_method = None
        for method in HTTP_METHODS:
             if name_lower == method or name_lower.startswith(f"{method}_"):
                 found_method = method
                 break
        
        if not found_method:
            return None
        
        http_method = found_method.upper()
        
        # Split by "_by_" to separate path structure from parameters
        parts_by = name_lower.split("_by_")
        
        # First component contains the method and the path segments
        # e.g. "get_users"
        main_part = parts_by[0]
        main_segments = main_part.split("_")
        
        # First segment is the method, which we already verified
        path_segments = main_segments[1:]
        
        final_path_parts = []
        final_path_parts.extend(path_segments)
        
        # Subsequent components are parameters
        # e.g. "id" or "item_id"
        for param in parts_by[1:]:
             final_path_parts.append(f"{{{param}}}")
             
        if not final_path_parts:
            return (http_method, "/")
        
        sub_path = "/" + "/".join(final_path_parts)
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
    
    # Set by metaclass: (http_method, sub_path, callable, type_hints)
    _endpoints: List[Tuple[str, str, Callable, Dict[str, Type]]] = []
    
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
    def get_endpoints(cls) -> List[Tuple[str, str, Callable, Dict[str, Type]]]:
        """Get all endpoint definitions for this route class."""
        return cls._endpoints
