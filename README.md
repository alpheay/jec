# JEC-API

A powerful wrapper around FastAPI that brings class-based routing, strict method mapping, and modern developer tools to your API development.

## Features

- **Class-Based Routes**: Group related endpoints into a single class for better organization.
- **Strict Method Mapping**: Methods named `get`, `post`, `put`, etc., are automatically mapped to HTTP verbs.
- **Data Object Support**: Native Pydantic integration for automatic request/response validation and schema generation.
- **API Decorators**: Built-in `@log`, `@speed`, and `@version` decorators for observability and control.
- **Programmatic Configuration**: Unified `core.tinker()` method to configure FastAPI and Uvicorn.
- **JEC DevTools**: Real-time, dark-themed developer console at `/__dev__` for monitoring traffic and performance.

## Installation

```bash
pip install jec-api
```

## Quick Start

1. **Define a Route Class**

```python
from pydantic import BaseModel
from jec_api import Route, log, speed

class UserResponse(BaseModel):
    id: int
    name: str

class Users(Route):
    @log
    @speed
    async def get(self) -> list[UserResponse]:
        """List all users with logging and speed tracking"""
        return [UserResponse(id=1, name="Alice")]
```

2. **Configure and Run**

```python
from jec_api import Core
from routes import Users

core = Core()
core.tinker(
    title="My API",
    dev=True,      # Enable JEC DevTools
    reload=True    # Auto-reload on changes
)

core.register(Users)

if __name__ == "__main__":
    core.run(port=8000)
```

## Usage Guide

### Defining Routes

Inherit from `jec_api.Route`. The class name is converted to kebab-case for the base path (e.g., `UserProfiles` -> `/user-profiles`), unless overridden with the `path` attribute.

### Method Mapping

Methods named exactly after HTTP verbs (e.g., `get`, `post`) are registered as endpoints. Others are ignored.

### API Decorators

Enhance your endpoints with built-in decorators:

- **`@log`**: Logs function calls, arguments, and return values/exceptions.
- **`@speed`**: Measures execution time in milliseconds.
- **`@version(">=1.0.0")`**: Enforces semver constraints via the `X-API-Version` header.

### Configuration (`core.tinker()`)

The `tinker()` method provides a unified interface for configuration:

- **FastAPI Options**: `title`, `description`, `version`, `docs_url`, etc.
- **Uvicorn Options**: `host`, `port`, `reload`, `log_level`, etc.
- **DevTools**: Set `dev=True` to enable the developer console.
- **Versioning**: `strict_versioning=True` to require version headers on all versioned routes.

### JEC DevTools

Access a premium, real-time monitoring dashboard at `/__dev__` (or your custom `dev_path`). It provides:
- Live request/response tracking via SSE.
- Visual execution timing (Green/Yellow/Red).
- Expanded logs for @log decorated methods.
- Version check results.

## License

MIT License
