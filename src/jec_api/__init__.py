"""JEC-API: Define FastAPI routes as classes."""

from .route import Route
from .core import Core
from .decorators import log, speed, version
 
__all__ = ["Route", "Core", "log", "speed", "version"]
__version__ = "0.1.0"
