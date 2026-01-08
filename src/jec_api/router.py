"""Core - FastAPI wrapper with class-based route registration."""

import asyncio
import inspect
from typing import Any, Callable, List, Type, Optional
from fastapi import FastAPI, APIRouter
from fastapi.routing import APIRoute

from .route import Route
from .discovery import discover_routes


class Core(FastAPI):
    """
    FastAPI application with class-based route registration.
    
    Usage:
        app = Core()
        app.discover("routes")  # Auto-discover from package
        app.register(MyRoute)   # Or register manually
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._registered_routes: List[Type[Route]] = []
    
    def register(self, route_class: Type[Route], **router_kwargs) -> "Core":
        """
        Register a Route subclass with the application.
        
        Args:
            route_class: A class that inherits from Route
            **router_kwargs: Additional kwargs passed to APIRouter (tags, etc.)
        
        Returns:
            Self for method chaining
        """
        if not isinstance(route_class, type) or not issubclass(route_class, Route):
            raise TypeError(f"{route_class} must be a subclass of Route")
        
        if route_class is Route:
            raise ValueError("Cannot register the base Route class directly")
        
        base_path = route_class.get_path()
        endpoints = route_class.get_endpoints()
        
        if not endpoints:
            return self  # No endpoints to register
        
        # Create an instance of the route class
        instance = route_class()
        
        # Determine tags from class name if not provided
        if "tags" not in router_kwargs:
            router_kwargs["tags"] = [route_class.__name__]
        
        # Register each endpoint
        for http_method, sub_path, method_func, type_hints in endpoints:
            # Build full path
            if sub_path == "/":
                full_path = base_path
            else:
                full_path = base_path.rstrip("/") + sub_path
            
            # Bind the method to the instance
            bound_method = getattr(instance, method_func.__name__)
            
            # Check for Pydantic body parameters
            endpoint_func = self._create_endpoint(bound_method, type_hints)
            
            # Get the appropriate router method (get, post, etc.)
            router_method = getattr(self, http_method.lower())
            
            # Register the route
            router_method(
                full_path,
                **router_kwargs,
            )(endpoint_func)
        
        self._registered_routes.append(route_class)
        return self
    
    def _create_endpoint(self, bound_method: Callable, type_hints: dict) -> Callable:
        """
        Create an endpoint function with proper signature for FastAPI.
        
        If type hints contain Pydantic models, they become body parameters.
        Path parameters are automatically extracted from the path by FastAPI.
        """
        from pydantic import BaseModel
        import functools
        
        # Separate body params (Pydantic models) from other params (path/query)
        body_params = {}
        other_params = {}
        
        for param_name, param_type in type_hints.items():
            if isinstance(param_type, type) and issubclass(param_type, BaseModel):
                body_params[param_name] = param_type
            else:
                other_params[param_name] = param_type
        
        # If no body params, just return the bound method as-is
        if not body_params:
            return bound_method
        
        # Create a wrapper that FastAPI can introspect
        # We need to build a function with the correct signature dynamically
        
        # For simplicity, we'll handle the common case of a single body param
        if len(body_params) == 1:
            body_param_name, body_model = list(body_params.items())[0]
            
            @functools.wraps(bound_method)
            async def wrapper(**kwargs):
                return await bound_method(**kwargs) if asyncio.iscoroutinefunction(bound_method) else bound_method(**kwargs)
            
            # Update wrapper's annotations so FastAPI picks up the body param
            sig = inspect.signature(bound_method)
            wrapper.__annotations__ = {**type_hints}
            wrapper.__signature__ = sig
            
            return wrapper
        
        # Multiple body params or complex case - just return bound method
        # FastAPI will handle based on annotations
        return bound_method
    
    def discover(
        self,
        package: str,
        *,
        recursive: bool = True,
        **router_kwargs
    ) -> "Core":
        """
        Auto-discover and register Route subclasses from a package.
        
        Args:
            package: Package name or path to discover routes from
            recursive: Whether to search subdirectories
            **router_kwargs: Additional kwargs passed to each route's registration
        
        Returns:
            Self for method chaining
        """
        route_classes = discover_routes(package, recursive=recursive)
        
        for route_class in route_classes:
            self.register(route_class, **router_kwargs)
        
        return self
    
    def get_registered_routes(self) -> List[Type[Route]]:
        """Get a list of all registered Route classes."""
        return self._registered_routes.copy()
