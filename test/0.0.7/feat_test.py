
import pytest
from fastapi.testclient import TestClient
from fastapi import Request, HTTPException
from jec_api import Core, Route
from jec_api.decorators import auth

# --- Auth Handler Mock ---
async def mock_auth_handler(request: Request, roles: list[str] = None) -> bool:
    """
    Mock handler for testing.
    Expects Authorization: Bearer <token>
    - "admin-token" -> matches role "admin"
    - "user-token" -> matches role "user"
    - anything else -> invalid
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return False

    token = auth_header.split(" ")[1]
    user_roles = []
    
    if token == "admin-token":
        user_roles = ["admin"]
        request.state.user = {"name": "Admin User"}
    elif token == "user-token":
        user_roles = ["user"]
        request.state.user = {"name": "Normal User"}
    else:
        return False # Invalid token
            
    # If specific roles are required, check them
    if roles:
        # Check if user has ANY of the required roles
        has_permission = any(role in user_roles for role in roles)
        if not has_permission:
            return False # Insufficient permissions
            
    return True # Allow access

# --- Routes for Testing ---
class PublicRoute(Route):
    @auth(False)
    async def get(self):
        return {"msg": "public"}

class SecureRoute(Route):
    @auth(True)
    async def get(self, request: Request):
        return {"msg": "secure", "user": getattr(request.state, "user", {}).get("name")}

class AdminRoute(Route):
    @auth(True, roles=["admin"])
    async def post(self):
        return {"msg": "admin_only"}

class MixedRoute(Route):
    @auth(True, roles=["user", "admin"])
    async def put(self):
        return {"msg": "user_or_admin"}

# --- Tests ---
def test_auth_features():
    app = Core()
    app.set_auth_handler(mock_auth_handler)
    
    app.register(PublicRoute)
    app.register(SecureRoute)
    app.register(AdminRoute)
    app.register(MixedRoute)
    
    client = TestClient(app)

    # 1. Public Endpoint - Should work without auth
    resp = client.get("/public-route")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json() == {"msg": "public"}

    # 2. Secure Endpoint - No Token -> 403
    resp = client.get("/secure-route")
    assert resp.status_code == 403, "Expected 403 for missing token property"

    # 3. Secure Endpoint - Invalid Token -> 403
    resp = client.get("/secure-route", headers={"Authorization": "Bearer bad"})
    assert resp.status_code == 403, "Expected 403 for invalid token"

    # 4. Secure Endpoint - Valid Token -> 200
    resp = client.get("/secure-route", headers={"Authorization": "Bearer user-token"})
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["msg"] == "secure"
    assert resp.json()["user"] == "Normal User"

    # 5. Admin Route - User Token -> 403 (Missing role)
    resp = client.post("/admin-route", headers={"Authorization": "Bearer user-token"})
    assert resp.status_code == 403, "Expected 403 for insufficient permissions (user accessing admin)"

    # 6. Admin Route - Admin Token -> 200
    resp = client.post("/admin-route", headers={"Authorization": "Bearer admin-token"})
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    # 7. Admin Route - No Token -> 403
    resp = client.post("/admin-route")
    assert resp.status_code == 403, "Expected 403 for missing token on admin route"

    # 8. Mixed Route - User Token -> 200 (Has one of the roles)
    resp = client.put("/mixed-route", headers={"Authorization": "Bearer user-token"})
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # 9. Mixed Route - Admin Token -> 200 (Has one of the roles)
    resp = client.put("/mixed-route", headers={"Authorization": "Bearer admin-token"})
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
