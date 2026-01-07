"""Auto-discovery of Route classes from packages and directories."""

import importlib
import importlib.util
import pkgutil
import sys
from pathlib import Path
from typing import List, Type

from .route import Route


def discover_routes(package: str, *, recursive: bool = True) -> List[Type[Route]]:
    """
    Discover all Route subclasses in a package or directory.
    
    Args:
        package: Package name (e.g., "routes") or path to directory
        recursive: Whether to search subdirectories
    
    Returns:
        List of Route subclasses found
    """
    route_classes: List[Type[Route]] = []
    
    # Check if it's a path or a package name
    package_path = Path(package)
    
    if package_path.is_dir():
        # It's a directory path
        route_classes.extend(_discover_from_directory(package_path, recursive))
    else:
        # Try as a package name
        try:
            route_classes.extend(_discover_from_package(package, recursive))
        except ModuleNotFoundError:
            # Maybe it's a relative path from cwd
            cwd_path = Path.cwd() / package
            if cwd_path.is_dir():
                route_classes.extend(_discover_from_directory(cwd_path, recursive))
            else:
                raise ValueError(f"Could not find package or directory: {package}")
    
    return route_classes


def _discover_from_package(package_name: str, recursive: bool) -> List[Type[Route]]:
    """Discover routes from an installed package."""
    route_classes: List[Type[Route]] = []
    
    package = importlib.import_module(package_name)
    
    if not hasattr(package, "__path__"):
        # Single module, not a package
        route_classes.extend(_extract_routes_from_module(package))
        return route_classes
    
    # Walk through the package
    prefix = package_name + "."
    
    for importer, modname, ispkg in pkgutil.walk_packages(
        package.__path__,
        prefix=prefix,
    ):
        if not recursive and ispkg:
            continue
        
        try:
            module = importlib.import_module(modname)
            route_classes.extend(_extract_routes_from_module(module))
        except Exception:
            # Skip modules that fail to import
            continue
    
    return route_classes


def _discover_from_directory(directory: Path, recursive: bool) -> List[Type[Route]]:
    """Discover routes from a directory of Python files."""
    route_classes: List[Type[Route]] = []
    
    # Add directory to sys.path temporarily if needed
    dir_str = str(directory.parent.resolve())
    added_to_path = False
    
    if dir_str not in sys.path:
        sys.path.insert(0, dir_str)
        added_to_path = True
    
    try:
        pattern = "**/*.py" if recursive else "*.py"
        
        for py_file in directory.glob(pattern):
            if py_file.name.startswith("_"):
                continue
            
            try:
                module = _load_module_from_file(py_file)
                if module:
                    route_classes.extend(_extract_routes_from_module(module))
            except Exception:
                # Skip files that fail to import
                continue
    finally:
        if added_to_path:
            sys.path.remove(dir_str)
    
    return route_classes


def _load_module_from_file(file_path: Path):
    """Load a Python module from a file path."""
    module_name = file_path.stem
    
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        return None
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    
    return module


def _extract_routes_from_module(module) -> List[Type[Route]]:
    """Extract all Route subclasses from a module."""
    route_classes: List[Type[Route]] = []
    
    for name in dir(module):
        if name.startswith("_"):
            continue
        
        obj = getattr(module, name)
        
        # Check if it's a class that inherits from Route (but not Route itself)
        if (
            isinstance(obj, type)
            and issubclass(obj, Route)
            and obj is not Route
            and obj.__module__ == module.__name__
        ):
            route_classes.append(obj)
    
    return route_classes
