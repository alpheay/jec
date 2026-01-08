
import pytest
from fastapi.testclient import TestClient
from jec_api import Route, Core

# --- Sample Routes for Testing ---

class SimpleRoute(Route):
    """Basic route with default path /simple-route"""
    
    def get(self):
        return {"msg": "get"}
    
    def post(self):
        return {"msg": "post"}

class CustomPathRoute(Route):
    """Route with custom path"""
    path = "/custom"
    
    def get(self):
        return {"msg": "custom get"}

class ParameterRoute(Route):
    """Route with path parameters"""
    path = "/items"
    
    def get_by_id(self, id: int):
        return {"id": id}
    
    def get_details_by_item_id(self, item_id: str):
        return {"item_id": item_id}
        
class MethodParsingRoute(Route):
    """Testing the method name parsing logic"""
    
    def get_users(self):
        return {"type": "users"}
        
    def post_create_user(self):
        return {"action": "create"}
        
    def put_user_by_id(self, id: int):
        return {"update": id}

# --- Tests ---

def test_route_path_generation():
    """Test that paths are generated correctly from class names or custom attributes."""
    assert SimpleRoute.get_path() == "/simple-route"
    assert CustomPathRoute.get_path() == "/custom"
    # Test kebab-case conversion
    class UserProfileSettings(Route): pass
    assert UserProfileSettings.get_path() == "/user-profile-settings"

def test_endpoint_parsing():
    """Test that methods are correctly parsed into HTTP methods and paths."""
    endpoints = ParameterRoute.get_endpoints()
    
    # We expect get_by_id -> GET /{id}
    # and get_details_by_item_id -> GET /details/{item_id}
    
    assert len(endpoints) == 2
    
    methods = {func.__name__: (method, path) for method, path, func, _ in endpoints}
    
    assert "get_by_id" in methods
    assert methods["get_by_id"] == ("GET", "/{id}")
    
    assert "get_details_by_item_id" in methods
    assert methods["get_details_by_item_id"] == ("GET", "/details/{item_id}")

def test_complex_parsing():
    """Test more complex parsing scenarios."""
    endpoints = MethodParsingRoute.get_endpoints()
    methods = {func.__name__: (method, path) for method, path, func, _ in endpoints}
    
    # get_users -> GET /users
    assert methods["get_users"] == ("GET", "/users")
    
    # post_create_user -> POST /create/user
    assert methods["post_create_user"] == ("POST", "/create/user")
    
    # put_user_by_id -> PUT /user/{id}
    assert methods["put_user_by_id"] == ("PUT", "/user/{id}")

def test_app_registration_and_requests():
    """Test that routes work when registered to the Core app."""
    app = Core()
    app.register(SimpleRoute)
    app.register(CustomPathRoute)
    app.register(ParameterRoute)
    
    client = TestClient(app)
    
    # Test SimpleRoute
    resp = client.get("/simple-route")
    assert resp.status_code == 200
    assert resp.json() == {"msg": "get"}
    
    resp = client.post("/simple-route")
    assert resp.status_code == 200
    assert resp.json() == {"msg": "post"}
    
    # Test CustomPathRoute
    resp = client.get("/custom")
    assert resp.status_code == 200
    assert resp.json() == {"msg": "custom get"}
    
    # Test ParameterRoute
    resp = client.get("/items/123")
    assert resp.status_code == 200
    assert resp.json() == {"id": 123}
    
    resp = client.get("/items/details/abc")
    assert resp.status_code == 200
    assert resp.json() == {"item_id": "abc"}

def test_invalid_registration():
    """Test registration validation."""
    app = Core()
    
    # Should fail if not a Route subclass
    with pytest.raises(TypeError):
        app.register(dict)
        
    # Should fail if registering base Route class
    with pytest.raises(ValueError):
        app.register(Route)

def test_get_registered_routes():
    """Test retrieving registered routes."""
    app = Core()
    app.register(SimpleRoute)
    
    routes = app.get_registered_routes()
    assert len(routes) == 1
    assert routes[0] == SimpleRoute

if __name__ == "__main__":
    # Allow running directly if pytest is not used
    # But usually this file is meant for pytest
    pass