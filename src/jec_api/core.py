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
        self._uvicorn_config: dict = {}
        self.strict_versioning: bool = False
    
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
    

    def tinker(self, **kwargs) -> "Core":
        """
        Configure the application and underlying uvicorn server.
        
        Args:
            **kwargs: Configuration options.
                - FastAPI attributes (title, description, etc.) update the app.
                - strict_versioning: Enable strict API version enforcement (default: False).
                - All other kwargs are stored and passed to uvicorn.run().
        
        Returns:
            Self for method chaining
        """
        # Handle strict_versioning specifically
        if "strict_versioning" in kwargs:
            self.strict_versioning = kwargs.pop("strict_versioning")
        
        # FastAPI attributes that can be updated
        app_attrs = {
            "title", "description", "version", "openapi_url", "docs_url", 
            "redoc_url", "swagger_ui_oauth2_redirect_url", "swagger_ui_init_oauth",
            "middleware", "exception_handlers", "on_startup", "on_shutdown",
            "lifespan", "terms_of_service", "contact", "license_info", 
            "servers", "root_path", "root_path_in_servers", "responses", 
            "callbacks", "webhooks", "deprecated", "include_in_schema",
            "debug"
        }
        
        for k, v in kwargs.items():
            if k in app_attrs:
                if hasattr(self, k):
                    setattr(self, k, v)
            else:
                self._uvicorn_config[k] = v
        
        return self

    def run(self):
        """
        Run the application using uvicorn.
        """
        import uvicorn
        config = self._uvicorn_config.copy()
        # Default to 127.0.0.1 if host not specified to match uvicorn CLI behavior
        if "host" not in config:
            config["host"] = "127.0.0.1"
        uvicorn.run(self, **config)

    def get_registered_routes(self) -> List[Type[Route]]:
        """Get a list of all registered Route classes."""
        return self._registered_routes.copy()
