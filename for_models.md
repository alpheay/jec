# JEC API Model Context

This document is a context guide for AI models to understand how to use the JEC (JSON Endpoint Configuration) API framework. JEC is a "packed superset" of FastAPI that introduces class-based routing, declarative decorators, and built-in developer tooling.

## Core Concepts

### 1. Application Setup
JEC uses a `Core` class that extends `FastAPI`. Configuration is handled via the `tinker()` method.

```python
from jec_api import Core

app = Core()

# Configure the app
app.tinker(
    title="My Service",
    version="1.0.0",
    dev=True,            # Enable /__dev__ console
    strict_versioning=True, # Require X-API-Version header
    # Other fastapi/uvicorn kwargs...
)

# Register routes
app.register(MyRoute)
# OR auto-discover
app.discover("my_package.routes")

if __name__ == "__main__":
    app.run(port=8000)
```

### 2. Class-Based Routing
Routes are defined as classes inheriting from `jec_api.Route`.
- **Path**: Auto-generated from class name (`UserProfiles` -> `/user-profiles`) or overridden via `path` attribute.
- **Methods**: Define methods named `get`, `post`, `put`, `delete`, `patch`, `options`, `head`.
- **Type Hints**: Use standard Pydantic models for request bodies and return types.

```python
from jec_api import Route
from pydantic import BaseModel

class CreateItem(BaseModel):
    name: str

class Items(Route):
    path = "/items"  # Optional override

    async def get(self) -> list[str]:
        """GET /items"""
        return ["item1", "item2"]

    async def post(self, data: CreateItem) -> dict:
        """POST /items"""
        return {"created": data.name}
```

## Decorators (The "Packed" Features)

JEC provides a suite of decorators to handle common API concerns declaratively.

### `@auth`
Enforces authentication and authorization. Requires `app.set_auth_handler()`.

```python
@auth(
    enabled=True,
    roles=["admin"],      # Optional: User must have one of these roles
    scopes=["read"],      # Optional: User must have one of these scopes
    require_all=False,    # If True, must have ALL roles/scopes
    custom_error="No access"
)
async def get(self): ...
```

#### Authentication Logic
The actual logic is decoupled from the decorator. You must register an async handler.

**Handler Signature:**
`async def handler(request: Request, roles: list[str], scopes: list[str], require_all: bool) -> bool`

```python
async def my_auth(request, roles, scopes, require_all):
    # 1. Verify Identity (Token, Session, etc.)
    user = await verify_token(request)
    if not user:
        return False
        
    # 2. Add User to Request State (Common Pattern)
    request.state.user = user

    # 3. Check Permissions (RBAC/Scopes)
    if roles:
        has_role = any(r in user.roles for r in roles)
        if not has_role: return False
    
    return True

app.set_auth_handler(my_auth)
```

### `@version`
Enforces API versioning via `X-API-Version` header. Supports SemVer operators.

```python
@version(">=1.0.0")
async def get(self): ...

@version("<2.0.0", deprecated=True, sunset="2026-01-01")
async def get_legacy(self): ...
```

### `@ratelimit`
Rate limits requests based on IP, user, or globally.

```python
@ratelimit(
    limit=100,
    window=60,       # seconds
    by="ip",         # "ip", "user" (uses request.state.user.id), "global"
    message="Slow down"
)
async def get(self): ...
```

### `@retry`
Automatically retries failed operations with exponential backoff.

```python
@retry(
    attempts=3,
    delay=1.0,
    backoff=2.0,
    exceptions=(ConnectionError,)
)
async def connect(self): ...
```

### `@log`
Logs request arguments and return values.

```python
@log(
    level="info",
    include_args=True,
    include_result=True,
    max_length=200
)
async def do_work(self): ...
```

### `@speed`
Monitors execution time and logs warnings/errors if thresholds are exceeded.

```python
@speed(
    warn_threshold_ms=100,
    error_threshold_ms=500,
    include_in_response=True # Adds X-Response-Time header
)
async def process(self): ...
```

### `@timeout`
Enforces a maximum execution time (Async only).

```python
@timeout(seconds=5.0)
async def quick_task(self): ...
```

### `@deprecated`
Marks endpoints as deprecated with headers (`Deprecation`, `Sunset`).

```python
@deprecated(
    message="Use v2",
    alternative="/v2/users",
    sunset="2025-12-31"
)
async def old_endpoint(self): ...
```

## Developer Tools

### JEC DevConsole
Enabled via `app.tinker(dev=True)`.
- Accessible at `/__dev__`.
- Provides real-time request logging, timing analysis, and error tracking.
- Driven by `DevConsoleStore` which collects data from decorators.

## Best Practices for Models

1.  **Always use `Route` classes**: Do not use standard FastAPI function-based views unless absolutely necessary.
2.  **Type everything**: Use Pydantic models for inputs and outputs to leverage JEC's validation.
3.  **Decorate liberally**: Use `@log` and `@speed` on complex endpoints for observability.
4.  **Version from start**: Use `@version(">=1.0.0")` to future-proof APIs.
5.  **Secure by Default**: Register an auth handler immediately and use `@auth` on sensitive routes.
6.  **Dependency Injection**: Use `request: Request` in method signatures if you need low-level access (e.g., for headers/state), but try to rely on Pydantic models for body data.

## Example: The "Full Stack" Endpoint

```python
from jec_api import Route, auth, version, ratelimit, log, speed, retry
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str

class UserProfile(Route):
    path = "/users/profile"

    # Stack Order: Auth -> Version -> RateLimit -> Speed -> Log -> Retry
    # (Though order is flexible, this is a common, safe pattern)
    @auth(roles=["user"], scopes=["profile:read"])
    @version(">=1.0.0")
    @ratelimit(limit=50, window=60, by="user")
    @speed(warn_threshold_ms=200)
    @log(level="debug")
    @retry(attempts=2, exceptions=(ConnectionError,))
    async def get(self) -> User:
        """
        Get user profile.
        Protected, versioned, rate-limited, monitored, and logged.
        """
        # Logic would go here...
        return User(id=1, name="Nik")
```
