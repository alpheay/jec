
import pytest
import time
from fastapi import Request, HTTPException, Response
from fastapi.testclient import TestClient
from jec_api import Core, Route, auth
from jec_api.decorator import log, speed, version

# --- Mock Auth Handler ---
async def mock_auth_handler(request: Request, roles: list[str] = None) -> bool:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return False

    token = auth_header.split(" ")[1]
    
    token_roles = {
        "admin-token": ["admin"],
        "user-token": ["user"],
        "guest-token": ["guest"]
    }
    
    if token not in token_roles:
        return False

    user_roles = token_roles.get(token, [])
    request.state.user = {"roles": user_roles}

    if roles:
        has_permission = any(role in user_roles for role in roles)
        if not has_permission:
            return False 
            
    return True

# --- Test Routes ---

class AuthPublic(Route):
    path = "/auth/public"
    @auth(False)
    async def get(self):
        return {"status": "public"}

class AuthPrivate(Route):
    path = "/auth/private"
    @auth(True)
    async def get(self):
        return {"status": "private"}

class AuthAdmin(Route):
    path = "/auth/admin"
    @auth(True, roles=["admin"])
    async def get(self):
        return {"status": "admin"}

class AuthMixed(Route):
    path = "/auth/mixed"
    @auth(True, roles=["user", "admin"])
    async def get(self):
        return {"status": "mixed"}

class LogLogged(Route):
    path = "/log/logged"
    @log
    async def get(self, request: Request):
        return {"msg": "logged"}

class LogError(Route):
    path = "/log/error"
    @log
    async def get(self):
        raise ValueError("Intentional error")

class SpeedFast(Route):
    path = "/speed/fast"
    @speed
    async def get(self):
        return {"msg": "fast"}

class SpeedSlow(Route):
    path = "/speed/slow"
    @speed
    async def get(self):
        import asyncio
        await asyncio.sleep(0.01)
        return {"msg": "slow"}

class VersionV1(Route):
    path = "/version/v1"
    @version(">=1.0.0")
    async def get(self):
        return {"version": "1+"}

class VersionExact(Route):
    path = "/version/v2-exact"
    @version("==2.0.0")
    async def get(self):
        return {"version": "2.0.0"}

class VersionLt(Route):
    path = "/version/lt-v3"
    @version("<3.0.0")
    async def get(self):
        return {"version": "<3"}

class Combo(Route):
    path = "/combo/everything"
    @auth(True, roles=["admin"])
    @version(">=1.5.0")
    @log
    @speed
    async def get(self):
        return {"status": "combo"}

# --- Test Suite ---

def test_decorators_comprehensive():
    app = Core()
    app.set_auth_handler(mock_auth_handler)
    
    # Register routes - No kwargs needed as path is defined in class
    app.register(AuthPublic)
    app.register(AuthPrivate)
    app.register(AuthAdmin)
    app.register(AuthMixed)
    
    app.register(LogLogged)
    app.register(LogError)
    
    app.register(SpeedFast)
    app.register(SpeedSlow)
    
    app.register(VersionV1)
    app.register(VersionExact)
    app.register(VersionLt)
    
    app.register(Combo)
    
    client = TestClient(app)

    # --- 1. Auth Tests ---
    print("\n[TEST] Auth Tests")
    
    # Debug print mapped routes
    # for route in app.routes:
    #     print(f"Route: {route.path} {route.methods}")

    assert client.get("/auth/public").status_code == 200
    
    assert client.get("/auth/private").status_code == 403
    assert client.get("/auth/private", headers={"Authorization": "Bearer bad"}).status_code == 403
    assert client.get("/auth/private", headers={"Authorization": "Bearer user-token"}).status_code == 200
    
    assert client.get("/auth/admin", headers={"Authorization": "Bearer user-token"}).status_code == 403
    assert client.get("/auth/admin", headers={"Authorization": "Bearer admin-token"}).status_code == 200
    
    assert client.get("/auth/mixed", headers={"Authorization": "Bearer user-token"}).status_code == 200
    assert client.get("/auth/mixed", headers={"Authorization": "Bearer admin-token"}).status_code == 200
    
    # --- 2. Log Tests ---
    print("\n[TEST] Log Tests")
    resp = client.get("/log/logged")
    assert resp.status_code == 200
    assert resp.json() == {"msg": "logged"}
    
    with pytest.raises(ValueError):
        client.get("/log/error")
        
    # --- 3. Speed Tests ---
    print("\n[TEST] Speed Tests")
    resp = client.get("/speed/fast")
    assert resp.status_code == 200
    
    resp = client.get("/speed/slow")
    assert resp.status_code == 200
    
    # --- 4. Version Tests ---
    print("\n[TEST] Version Tests")
    
    assert client.get("/version/v1", headers={"X-API-Version": "1.0.0"}).status_code == 200
    resp = client.get("/version/v1", headers={"X-API-Version": "0.9.0"})
    assert resp.status_code == 400
    
    assert client.get("/version/v2-exact", headers={"X-API-Version": "2.0.0"}).status_code == 200
    assert client.get("/version/v2-exact", headers={"X-API-Version": "2.0.1"}).status_code == 400
    
    assert client.get("/version/lt-v3", headers={"X-API-Version": "2.9.9"}).status_code == 200
    assert client.get("/version/lt-v3", headers={"X-API-Version": "3.0.0"}).status_code == 400

    resp = client.get("/version/v1", headers={"X-API-Version": "invalid"})
    assert resp.status_code == 400 
    
    assert client.get("/version/v1").status_code == 200
    
    # --- 5. Combo Tests ---
    print("\n[TEST] Combo Tests")
    
    assert client.get("/combo/everything", headers={"X-API-Version": "1.5.0"}).status_code == 403
    
    assert client.get("/combo/everything", headers={
        "Authorization": "Bearer admin-token", 
        "X-API-Version": "1.0.0"
    }).status_code == 400
    
    resp = client.get("/combo/everything", headers={
        "Authorization": "Bearer admin-token",
        "X-API-Version": "1.6.0"
    })
    assert resp.status_code == 200
    assert resp.json() == {"status": "combo"}
