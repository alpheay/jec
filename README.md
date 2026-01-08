# JEC-API

## Features

- **Class-Based Routes**: Group related endpoints into a single class.
- **Strict Method Mapping**: Methods named `get`, `post`, `put`, `delete`, `patch`, `options`, or `head` are automatically mapped to their respective HTTP verbs.
- **Data Object Support**: Built-in support for **Pydantic models**. Type hints are automatically used for request body validation and response model registry.
- **FastAPI Native**: Fully compatible with FastAPI dependencies and OpenAPI generation.

## Installation

```bash
pip install jec-api
```

## Quick Start

1. **Define a Route Class**

```python
# routes.py
from pydantic import BaseModel
from jec_api import Route

class UserResponse(BaseModel):
    id: int
    name: str

class CreateUser(BaseModel):
    name: str

class Users(Route):
    # Strictly mapped to GET /users
    async def get(self) -> list[UserResponse]:
        """List all users"""
        return [UserResponse(id=1, name="Alice")]

    # Strictly mapped to POST /users
    async def post(self, data: CreateUser) -> UserResponse:
        """Create a user"""
        return UserResponse(id=2, name=data.name)

class UserDetail(Route):
    # Custom path with parameter
    path = "/users/{user_id}"

    async def get(self, user_id: int) -> UserResponse:
        """Get user by ID"""
        return UserResponse(id=user_id, name="Alice")
```

2. **Create the App**

```python
# main.py
from jec_api import Core

core = Core(title="My API")

# Auto-discover routes from a module/package
core.discover("routes")

# Or register manually
from routes import Users
core.register(Users)
```

3. **Run it**

```bash
uvicorn main:core --reload
```

## Usage Guide

### Defining Routes

Inherit from `jec_api.Route` to create a route group. The class name is automatically converted to kebab-case to form the base path (e.g., `UserProfiles` -> `/user-profiles`), unless you override it with the `path` attribute.

### Method Mapping

JEC-API maps methods to HTTP verbs based on their exact names:

| Method Name | HTTP Verb | Path |
|-------------|-----------|------|
| `get()`     | GET       | `/`  |
| `post()`    | POST      | `/`  |
| `put()`     | PUT       | `/`  |
| `delete()`  | DELETE    | `/`  |
| `patch()`   | PATCH     | `/`  |
| `options()` | OPTIONS   | `/`  |
| `head()`    | HEAD      | `/`  |

> **Note**: Methods with other names (e.g., `get_users`, `helper_method`) are ignored and will not be registered as API endpoints.

### Path Parameters

To define routes with path parameters, override the `path` attribute on the `Route` class.

```python
class Users(Route):
    path = "/users/{id}"
    
    async def get(self, id: int):
        return {"id": id}
```

### Data Validation and Objects

JEC-API leverages Pydantic for data validation and schema generation.

1.  **Request Body**: The type hint of the first non-`self` parameter is used as the request body.
2.  **Response Model**: The return type hint is used as the `response_model` for the OpenAPI schema and serialization.

```python
class Users(Route):
    async def post(self, data: UserSchema) -> UserResponse:
        # data is automatically validated and parsed
        return UserResponse(...)
```

### Manual Registration

You can register routes manually if you prefer not to use auto-discovery:

```python
from my_routes import MyRoute
app.register(MyRoute, tags=["Custom Tag"])
```

### Auto-Discovery

The `discover()` method recursively searches the specified package for any classes inheriting from `Route` and registers them.

```python
app.discover("src.routes")
```

## License

MIT License
