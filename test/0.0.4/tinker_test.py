
import pytest
from unittest.mock import patch, MagicMock
from fastapi import Request
from fastapi.testclient import TestClient
from jec_api import Core, Route, version

# --- Mock Routes ---

class SimpleRoute(Route):
    @version(">=1.0.0")
    async def get(self, request: Request):
        return {"status": "ok"}

# --- Tests ---

def test_tinker_updates_fastapi_attributes():
    """Test that tinker updates FastAPI application attributes."""
    app = Core()
    app.tinker(
        title="My Custom API",
        description="A tinkered API",
        version="9.9.9",
        docs_url="/custom-docs"
    )
    
    assert app.title == "My Custom API"
    assert app.description == "A tinkered API"
    assert app.version == "9.9.9"
    assert app.docs_url == "/custom-docs"

def test_tinker_stores_uvicorn_settings():
    """Test that tinker stores uvicorn settings in _uvicorn_config."""
    app = Core()
    app.tinker(
        host="127.0.0.1",
        port=8080,
        reload=True,
        log_level="warning"
    )
    
    assert app._uvicorn_config["host"] == "127.0.0.1"
    assert app._uvicorn_config["port"] == 8080
    assert app._uvicorn_config["reload"] is True
    assert app._uvicorn_config["log_level"] == "warning"

def test_tinker_sets_strict_versioning():
    """Test that tinker sets the strict_versioning flag."""
    app = Core()
    assert app.strict_versioning is False  # Default
    
    app.tinker(strict_versioning=True)
    assert app.strict_versioning is True
    
    app.tinker(strict_versioning=False)
    assert app.strict_versioning is False

@patch("uvicorn.run")
def test_run_calls_uvicorn_with_config(mock_run):
    """Test that run() calls uvicorn.run with the correct arguments."""
    app = Core()
    app.tinker(host="0.0.0.0", port=5000)
    
    app.run()
    
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    assert args[0] == app
    assert kwargs["host"] == "0.0.0.0"
    assert kwargs["port"] == 5000

def test_strict_versioning_enforcement_missing_header():
    """Test that missing header returns 400 when strict versioning is enabled."""
    app = Core()
    app.register(SimpleRoute)
    app.tinker(strict_versioning=True)
    
    client = TestClient(app)
    
    response = client.get("/simple-route")
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "API version required"
    assert data["required"] == "true"

def test_strict_versioning_success_with_header():
    """Test that request succeeds with header when strict versioning is enabled."""
    app = Core()
    app.register(SimpleRoute)
    app.tinker(strict_versioning=True)
    
    client = TestClient(app)
    
    response = client.get("/simple-route", headers={"X-API-Version": "1.0.0"})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_lax_versioning_allows_missing_header():
    """Test that missing header is allowed when strict versioning is disabled (default)."""
    app = Core()
    app.register(SimpleRoute)
    # Default strict_versioning=False
    
    client = TestClient(app)
    
    response = client.get("/simple-route")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
