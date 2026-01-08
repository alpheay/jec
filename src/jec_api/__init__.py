"""JEC-API: Define FastAPI routes as classes."""

from .route import Route
from .core import Core
from .decorators import log, speed, version
from .dev.dev_console import DevConsoleStore, get_store
 
__all__ = ["Route", "Core", "log", "speed", "version", "DevConsoleStore", "get_store"]
__version__ = "0.1.0"
