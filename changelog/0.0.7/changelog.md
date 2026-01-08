# Changelog 0.0.8

## New Features

### Authentication & Authorization System

The 0.0.8 release introduces a robust, flexible authentication system designed to work seamlessly with JEC's class-based routes.

#### The `@auth` Decorator
You can now secure your endpoints using the `@auth` decorator found in `jec_api.decorators`.

**Basic Usage:**
```python
from jec_api import Route
from jec_api.decorators import auth

class SecureData(Route):
    @auth(True)  # Requires authentication
    async def get(self):
        return {"data": "secure"}

    @auth(False) # Public endpoint
    async def get_public(self):
        return {"data": "public"}
```

**Role-Based Access Control (RBAC):**
You can specify required roles. The auth handler receives these roles and can enforce them.
```python
class AdminPanel(Route):
    @auth(True, roles=["admin", "superuser"])
    async def delete(self):
        return {"status": "deleted"}
```

### Configuration Guide

The system is designed to be agnostic to the authentication method (JWT, OAuth, API Key, etc.). You provide the logic by registering an **Auth Handler**.

#### Setting up the Auth Handler

Register your handler using `app.set_auth_handler()`. The handler must be an `async` function that accepts `request` and `roles`.

**Signature:**
```python
async def auth_handler(request: Request, roles: list[str]) -> bool
```

**Simple Example:**
```python
from jec_api import Core
from fastapi import Request

app = Core()

async def my_auth(request: Request, roles: list[str] = None) -> bool:
    # 1. Check for token
    token = request.headers.get("Authorization")
    if token != "SecretToken":
        return False  # Deny access (403)
        
    return True # Allow access

app.set_auth_handler(my_auth)
```

### Advanced Use Cases

#### 1. OAuth2 / JWT Validation with User Context
In a real-world scenario, you often want to decode a JWT, validate it, and perhaps attach the user to the request for the endpoint to use.

```python
import jwt
from fastapi import HTTPException

APP_SECRET = "my-secret-key"

async def jwt_auth_handler(request: Request, roles: list[str] = None) -> bool:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return False
        
    token = auth_header.split(" ")[1]
    
    try:
        # Decode token
        payload = jwt.decode(token, APP_SECRET, algorithms=["HS256"])
        
        # Attach user to request state for endpoint access
        request.state.user = payload
        
        # Role Check
        if roles:
            user_roles = payload.get("roles", [])
            # Check if user has ANY of the required roles (or ALL, depending on your policy)
            # Here we enforce that the user must have at least one of the allowed roles
            has_permission = any(role in user_roles for role in roles)
            if not has_permission:
                raise HTTPException(status_code=403, detail="Insufficient Permissions")
                
        return True
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        return False # Invalid token
```

#### 2. Accessing User Data in Endpoints
Since the handler can modify `request.state`, you can access authentication data in your routes.

```python
class UserProfile(Route):
    @auth(True)
    async def get(self, request: Request):
        # Access user data set by the auth handler
        user_id = request.state.user["id"]
        return {"id": user_id, "name": request.state.user["name"]}
```

#### 3. Database Lookup in Auth
You can perform database operations within the auth handler. Since the handler is async, this won't block the event loop.

```python
async def db_backed_auth(request: Request, roles: list[str] = None) -> bool:
    api_key = request.headers.get("X-API-Key")
    
    # Assume 'db' is your database instance available globally or via dependency
    user = await db.users.find_one({"api_key": api_key})
    
    if not user:
        return False
        
    if roles and user.role not in roles:
        return False
        
    request.state.user = user
    return True
```

#### 4. Complex Scoping Policies
You can implement complex logic for scopes. For example, ensuring a user has *all* required roles, or checking resource-specific permissions.

```python
@auth(True, roles=["resource:read", "resource:write"])
async def sensitive_op(self): ...

async def complex_handler(request: Request, roles: list[str] = None) -> bool:
    # ... authenticate user ...
    
    if roles:
        # Require ALL roles specified in the decorator
        missing_roles = [r for r in roles if r not in user_scopes]
        if missing_roles:
            raise HTTPException(403, f"Missing scopes: {missing_roles}")
            
    return True
```
