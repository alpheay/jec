
import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel
from jec_api import Route, Core
import os
import sys

# --- Sample Models ---
class UserItem(BaseModel):
    name: str
    age: int

# --- Sample Routes ---
class BodyParamsRoute(Route):
    path = "/users"
    
    async def post(self, user: UserItem):
        return {"received": user.name, "age": user.age}

class MultiParamRoute(Route):
    async def post_update(self, id: int, user: UserItem):
        return {"id": id, "name": user.name}

# --- Tests ---

def test_pydantic_body_param():
    app = Core()
    app.register(BodyParamsRoute)
    client = TestClient(app)
    
    data = {"name": "Charlie", "age": 30}
    resp = client.post("/users", json=data)
    
    assert resp.status_code == 200
    assert resp.json() == {"received": "Charlie", "age": 30}

def test_multi_param_with_body():
    app = Core()
    app.register(MultiParamRoute)
    client = TestClient(app)
    
    # Path/Query param 'id' + Body param 'user'
    data = {"name": "Alice", "age": 25}
    resp = client.post("/multi-param-route/update?id=1", json=data)
    
    assert resp.status_code == 200
    assert resp.json() == {"id": 1, "name": "Alice"}

def test_auto_discovery():
    # Add the test directory to sys.path so we can import mock_package
    test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mock_pkg_path = os.path.join(test_dir, "0.0.2")
    if mock_pkg_path not in sys.path:
        sys.path.insert(0, mock_pkg_path)
    
    app = Core()
    # Discover from the mock package
    app.discover("mock_package")
    
    client = TestClient(app)
    resp = client.get("/package-route")
    
    assert resp.status_code == 200
    assert resp.json() == {"source": "package"}

def test_path_override():
    class OverrideRoute(Route):
        path = "/v2/custom"
        def get(self): return {"ok": True}
    
    app = Core()
    app.register(OverrideRoute)
    client = TestClient(app)
    
    assert OverrideRoute.get_path() == "/v2/custom"
    assert client.get("/v2/custom").status_code == 200

def test_get_registered_routes():
    app = Core()
    app.register(BodyParamsRoute)
    app.register(MultiParamRoute)
    
    routes = app.get_registered_routes()
    assert BodyParamsRoute in routes
    assert MultiParamRoute in routes
    assert len(routes) == 2

