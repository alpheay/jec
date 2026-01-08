"""Route base class for defining API endpoints."""

import re
import inspect
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, get_type_hints


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
        # Each endpoint is: (http_method, sub_path, method_func, request_body_type, response_model)
        cls._endpoints: List[Tuple[str, str, Callable, Optional[Type], Optional[Type]]] = []
        
        for attr_name, attr_value in namespace.items():
            if attr_name.startswith("_"):
                continue
            if not callable(attr_value):
                continue
            
            parsed = mcs._parse_method_name(attr_name)
            if parsed:
                http_method, sub_path = parsed
                request_body_type, response_model = mcs._extract_type_hints(attr_value)
                cls._endpoints.append((http_method, sub_path, attr_value, request_body_type, response_model))
        
        return cls
    
    @staticmethod
    def _parse_method_name(name: str) -> Optional[Tuple[str, str]]:
        """
        Parse method name to extract HTTP method and sub-path.
        
        Only exact HTTP method names are mapped to endpoints:
            get -> (GET, /)
            post -> (POST, /)
            put -> (PUT, /)
            delete -> (DELETE, /)
            patch -> (PATCH, /)
            options -> (OPTIONS, /)
            head -> (HEAD, /)
        
        Methods like get_2, get_users, post_batch, etc. are NOT mapped.
        """
        # Only match exact HTTP method names
        if name.lower() in HTTP_METHODS:
            return (name.upper(), "/")
        
        return None
    
    @staticmethod
    def _extract_type_hints(method: Callable) -> Tuple[Optional[Type], Optional[Type]]:
        """
        Extract request body type and response model from method signature.
        
        Args:
            method: The method to inspect
            
        Returns:
            Tuple of (request_body_type, response_model)
            - request_body_type: The type hint for the first non-self parameter (if any)
            - response_model: The return type hint (if any)
        """
        request_body_type = None
        response_model = None
        
        try:
            sig = inspect.signature(method)
            hints = get_type_hints(method) if hasattr(method, '__annotations__') else {}
            
            # Get the first parameter that isn't 'self'
            params = list(sig.parameters.items())
            for param_name, param in params:
                if param_name == 'self':
                    continue
                # Get type hint for this parameter
                if param_name in hints:
                    request_body_type = hints[param_name]
                break  # Only take the first non-self parameter
            
            # Get return type
            if 'return' in hints:
                response_model = hints['return']
        except (ValueError, TypeError):
            # If we can't inspect the method, just return None for both
            pass
        
        return (request_body_type, response_model)


class Route(metaclass=RouteMeta):
    """Base class for defining API route endpoints.

    Inherit from this class and define methods with HTTP method prefixes:
    - get(), post(), put(), delete(), patch(), options(), head()
    
    Define request/response data objects using type hints:
    - async def post(self, data: CreateUserRequest) -> UserResponse:
    - async def get(self) -> List[UserResponse]:
    
    Optionally set `path` class attribute to override the auto-generated path.
    """
    
    # Override this to set a custom path instead of deriving from class name
    path: Optional[str] = None
    
    # Set by metaclass: (http_method, sub_path, method_func, request_body_type, response_model)
    _endpoints: List[Tuple[str, str, Callable, Optional[Type], Optional[Type]]] = []
    
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
    def get_endpoints(cls) -> List[Tuple[str, str, Callable, Optional[Type], Optional[Type]]]:
        """Get all endpoint definitions for this route class.
        
        Returns:
            List of tuples: (http_method, sub_path, method_func, request_body_type, response_model)
        """
        return cls._endpoints
