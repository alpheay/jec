"""Auto-discovery of Route classes from packages and directories."""

import importlib
import importlib.util
import inspect
import logging
import pkgutil
import sys
from pathlib import Path
from typing import List, Type

from .route import Route

logger = logging.getLogger("jec_api.discovery")


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
    
    # Check if it's an absolute path or a path that exists relative to cwd
    package_path = Path(package)
    
    if package_path.is_absolute() and package_path.is_dir():
        # Absolute directory path provided directly
        route_classes.extend(_discover_from_directory(package_path, recursive))
    elif package_path.is_dir():
        # Relative path that resolves from cwd - resolve it fully
        route_classes.extend(_discover_from_directory(package_path.resolve(), recursive))
    else:
        # Try as a Python package name first
        try:
            route_classes.extend(_discover_from_package(package, recursive))
        except ModuleNotFoundError:
            # Not an installed/importable package - try resolving as a relative
            # directory from the caller's file location (not cwd, which is unreliable)
            resolved = _resolve_from_caller(package)
            if resolved is not None and resolved.is_dir():
                route_classes.extend(_discover_from_directory(resolved, recursive))
            else:
                # Also try cwd as a last resort for backwards compatibility
                cwd_path = Path.cwd() / package
                if cwd_path.is_dir():
                    route_classes.extend(_discover_from_directory(cwd_path, recursive))
                else:
                    locations_tried = [f"package '{package}'"]
                    if resolved is not None:
                        locations_tried.append(str(resolved))
                    locations_tried.append(str(cwd_path))
                    raise ValueError(
                        f"Could not find package or directory: '{package}'. "
                        f"Looked in: {', '.join(locations_tried)}"
                    )
    
    return route_classes


def _resolve_from_caller(package: str) -> "Path | None":
    """
    Resolve a package/directory name relative to the calling file's location.
    
    Walks the call stack to find the first frame outside of jec_api,
    then resolves the package name relative to that file's directory.
    This makes discovery work regardless of process working directory.
    """
    frame = inspect.currentframe()
    try:
        # Walk up the stack to find the caller outside jec_api
        caller_frame = frame
        while caller_frame is not None:
            caller_frame = caller_frame.f_back
            if caller_frame is None:
                break
            caller_file = caller_frame.f_globals.get("__file__")
            if caller_file is None:
                continue
            caller_path = Path(caller_file).resolve()
            # Skip frames from within jec_api itself
            this_package_dir = Path(__file__).resolve().parent
            if not str(caller_path).startswith(str(this_package_dir)):
                caller_dir = caller_path.parent
                candidate = caller_dir / package
                return candidate
    finally:
        del frame
    return None


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
        except Exception as e:
            logger.warning(
                "Failed to import module '%s' during route discovery: %s",
                modname,
                e,
            )
            continue
    
    return route_classes


def _discover_from_directory(directory: Path, recursive: bool) -> List[Type[Route]]:
    """Discover routes from a directory of Python files."""
    route_classes: List[Type[Route]] = []
    directory = directory.resolve()
    
    # Add both the directory itself and its parent to sys.path so that:
    # - modules inside the directory can be imported by name
    # - the directory can be treated as a package (imported by its folder name)
    paths_to_add = []
    dir_str = str(directory)
    parent_str = str(directory.parent)
    
    for p in (dir_str, parent_str):
        if p not in sys.path:
            sys.path.insert(0, p)
            paths_to_add.append(p)
    
    try:
        pattern = "**/*.py" if recursive else "*.py"
        
        for py_file in directory.glob(pattern):
            if py_file.name.startswith("_"):
                continue
            
            try:
                module = _load_module_from_file(py_file)
                if module:
                    route_classes.extend(_extract_routes_from_module(module))
            except Exception as e:
                logger.warning(
                    "Failed to import '%s' during route discovery: %s",
                    py_file,
                    e,
                )
                continue
    finally:
        for p in paths_to_add:
            try:
                sys.path.remove(p)
            except ValueError:
                pass
    
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
