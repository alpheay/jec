import pytest
import logging
from fastapi import Request
from fastapi.testclient import TestClient
from jec_api import Route, Core, log, speed, version

# --- Test Routes ---

class ObservabilityRoute(Route):
    @log
    @speed
    async def get(self):
        return {"status": "async_ok"}

    @log
    @speed
    def post(self):
        return {"status": "sync_ok"}

class VersionedRoute(Route):
    path = "/v-test"

    @version(">=1.0.0")
    async def get(self, request: Request):
        return {"version": "v1+"}

    @version(">=2.0.0")
    async def post(self, request: Request):
        return {"version": "v2+"}

    @version("==1.5.0")
    def put(self, request: Request):
        return {"version": "exact_1.5.0"}

# --- Tests ---

def test_log_and_speed_decorators(caplog):
    """Test that @log and @speed work and generate logs."""
    app = Core()
    app.register(ObservabilityRoute)
    client = TestClient(app)
    
    with caplog.at_level(logging.INFO):
        # Test Async
        response = client.get("/observability-route")
        assert response.status_code == 200
        assert response.json() == {"status": "async_ok"}
        
        # Verify logs
        log_text = caplog.text
        assert "[CALL] ObservabilityRoute.get" in log_text
        assert "[SPEED] ObservabilityRoute.get" in log_text
        assert "[RETURN] ObservabilityRoute.get" in log_text

        caplog.clear()

        # Test Sync
        response = client.post("/observability-route")
        assert response.status_code == 200
        assert response.json() == {"status": "sync_ok"}
        
        # Verify logs
        log_text = caplog.text
        assert "[CALL] ObservabilityRoute.post" in log_text
        assert "[SPEED] ObservabilityRoute.post" in log_text
        assert "[RETURN] ObservabilityRoute.post" in log_text

def test_version_decorator_success():
    """Test version constraints that should pass."""
    app = Core()
    app.register(VersionedRoute)
    client = TestClient(app)

    # Test >=1.0.0 with 1.0.0
    response = client.get("/v-test", headers={"X-API-Version": "1.0.0"})
    assert response.status_code == 200
    assert response.json()["version"] == "v1+"

    # Test >=1.0.0 with 1.5.0
    response = client.get("/v-test", headers={"X-API-Version": "1.5.0"})
    assert response.status_code == 200

    # Test >=2.0.0 with 2.1.0
    response = client.post("/v-test", headers={"X-API-Version": "2.1.0"})
    assert response.status_code == 200
    assert response.json()["version"] == "v2+"

    # Test ==1.5.0 with 1.5.0 (sync)
    response = client.put("/v-test", headers={"X-API-Version": "1.5.0"})
    assert response.status_code == 200
    assert response.json()["version"] == "exact_1.5.0"

def test_version_decorator_failure():
    """Test version constraints that should fail."""
    app = Core()
    app.register(VersionedRoute)
    client = TestClient(app)

    # Test >=2.0.0 with 1.0.0
    response = client.post("/v-test", headers={"X-API-Version": "1.0.0"})
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "API version incompatible"
    assert ">=2.0.0" in data["detail"]

    # Test ==1.5.0 with 1.4.9
    response = client.put("/v-test", headers={"X-API-Version": "1.4.9"})
    assert response.status_code == 400

def test_version_decorator_no_header():
    """Test behavior when no X-API-Version header is provided (should pass)."""
    app = Core()
    app.register(VersionedRoute)
    client = TestClient(app)

    # Should pass if header is missing
    response = client.get("/v-test")
    assert response.status_code == 200
