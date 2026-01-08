import pytest
from typing import List
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.testclient import TestClient

from jec_api.route import Route
from jec_api.router import Core

# --- Data Models ---
class UserRequest(BaseModel):
    username: str
    email: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

# --- Test Routes ---
class StrictRoute(Route):
    # Should map to GET /strict-route
    async def get(self):
        return {"message": "ok"}
    
    # Should NOT map
    async def get_something(self):
        return {"message": "should not exist"}

class DataObjectRoute(Route):
    # Should map to POST /data-object-route with validation
    async def post(self, payload: UserRequest) -> UserResponse:
        return UserResponse(id=1, **payload.model_dump())

    # Should map to GET /data-object-route
    async def get(self) -> List[UserResponse]:
        return [
            UserResponse(id=1, username="test", email="test@example.com")
        ]

# --- Tests ---

def test_strict_method_naming():
    """Test that only exact HTTP verbs are mapped."""
    app = Core()
    app.register(StrictRoute)
    
    client = TestClient(app)
    
    # Check valid endpoint
    response = client.get("/strict-route")
    assert response.status_code == 200
    assert response.json() == {"message": "ok"}
    
    # Check that 'get_something' did NOT create a route at /strict-route/something
    response = client.get("/strict-route/something")
    assert response.status_code == 404

def test_pydantic_integration():
    """Test request body and response model handling."""
    app = Core()
    app.register(DataObjectRoute)
    
    client = TestClient(app)
    
    # Test POST with valid data
    payload = {"username": "alice", "email": "alice@example.com"}
    response = client.post("/data-object-route", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
    
    # Test POST with invalid data (validation check)
    response = client.post("/data-object-route", json={"username": "alice"}) # missing email
    assert response.status_code == 422
    
    # Test GET response model
    response = client.get("/data-object-route")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["username"] == "test"

def test_endpoint_metadata_extraction():
    """Verify that type hints are correctly extracted and stored."""
    endpoints = DataObjectRoute.get_endpoints()
    
    # Find the POST endpoint
    post_endpoint = next(e for e in endpoints if e[0] == "POST")
    
    # unpack: method, path, func, req_type, resp_type
    _, _, _, req_type, resp_type = post_endpoint
    
    assert req_type is UserRequest
    assert resp_type is UserResponse
