# JEC-API

## Features

- **Class-Based Routes**: Group related endpoints (e.g., CRUD operations) into a single class.
- **Auto-Discovery**: Automatically find and register route classes from your project packages.
- **Smart Method Naming**: API paths and HTTP methods are inferred from your method names (e.g., `get_by_id` becomes `GET /{id}`).
- **FastAPI Native**: Fully compatible with FastAPI dependencies, models, and OpenAPI generation.

## Installation

```bash
pip install jec-api
```

*(Note: If the package is not yet on PyPI, install from source)*

```bash
pip install .
```

## Quick Start

1. **Define a Route Class**

```python
# routes.py
from jec_api import Route

class Users(Route):
    # Optional: explicitly set path, otherwise defaults to /users
    # path = "/my-users"

    async def get(self):
        """List all users"""
        return [{"id": 1, "name": "Alice"}]

    async def get_by_id(self, id: int):
        """Get user by ID"""
        return {"id": id, "name": "Alice"}

    async def post(self, name: str):
        """Create a user"""
        return {"id": 2, "name": name}
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

### Method Naming Convention

JEC-API parses your method names to determine the HTTP verb and path parameters:

| Method Name | HTTP Verb | Generated Path |
|-------------|-----------|----------------|
| `get()` | GET | `/` |
| `post()` | POST | `/` |
| `get_by_id(id)` | GET | `/{id}` |
| `delete_by_id(id)` | DELETE | `/{id}` |
| `get_users()` | GET | `/users` |
| `post_batch_update()` | POST | `/batch-update` |

### Path Parameters

To define path parameters, use the `_by_{param}` pattern in your method name.
For example, `get_by_user_id` will generate a path `/{user_id}`.

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
