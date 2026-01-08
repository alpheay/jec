"""Core - FastAPI wrapper with class-based route registration."""

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
        # Endpoint tuple: (http_method, sub_path, method_func, request_body_type, response_model)
        for http_method, sub_path, method_func, request_body_type, response_model in endpoints:
            # Build full path
            if sub_path == "/":
                full_path = base_path
            else:
                full_path = base_path.rstrip("/") + sub_path
            
            # Bind the method to the instance
            bound_method = getattr(instance, method_func.__name__)
            
            # Get the appropriate router method (get, post, etc.)
            router_method = getattr(self, http_method.lower())
            
            # Build route kwargs
            route_kwargs = dict(router_kwargs)
            
            # Add response_model if defined
            if response_model is not None:
                route_kwargs["response_model"] = response_model
            
            # Register the route
            # Note: request_body_type is automatically handled by FastAPI
            # through the method's parameter type hints
            router_method(
                full_path,
                **route_kwargs,
            )(bound_method)
        
        self._registered_routes.append(route_class)
        return self
    
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
