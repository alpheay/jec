"""
Feature tests for jec-api v0.0.4

Tests for:
- core.tinker() configuration method
- core.run() uvicorn integration
- strict_versioning mode
- Default host behavior
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import Request
from fastapi.testclient import TestClient
from jec_api import Core, Route, version


# --- Mock Routes ---

class VersionedRoute(Route):
    path = "/versioned"
    
    @version(">=1.0.0")
    async def get(self, request: Request):
        return {"status": "ok", "method": "get"}
    
    @version(">=2.0.0")
    async def post(self, request: Request):
        return {"status": "ok", "method": "post"}


class UnversionedRoute(Route):
    path = "/unversioned"
    
    async def get(self):
        return {"status": "ok"}


# --- tinker() Tests ---

class TestTinkerFastAPIAttributes:
    """Test that tinker() correctly updates FastAPI application attributes."""
    
    def test_updates_title(self):
        app = Core()
        app.tinker(title="Custom Title")
        assert app.title == "Custom Title"
    
    def test_updates_description(self):
        app = Core()
        app.tinker(description="API Description")
        assert app.description == "API Description"
    
    def test_updates_version(self):
        app = Core()
        app.tinker(version="2.5.0")
        assert app.version == "2.5.0"
    
    def test_updates_docs_url(self):
        app = Core()
        app.tinker(docs_url="/swagger")
        assert app.docs_url == "/swagger"
    
    def test_updates_redoc_url(self):
        app = Core()
        app.tinker(redoc_url="/redoc-custom")
        assert app.redoc_url == "/redoc-custom"
    
    def test_updates_openapi_url(self):
        app = Core()
        app.tinker(openapi_url="/openapi.json")
        assert app.openapi_url == "/openapi.json"
    
    def test_updates_debug(self):
        app = Core()
        app.tinker(debug=True)
        assert app.debug is True
    
    def test_updates_multiple_attributes(self):
        app = Core()
        app.tinker(
            title="Multi",
            description="Test",
            version="3.0.0",
            debug=True
        )
        assert app.title == "Multi"
        assert app.description == "Test"
        assert app.version == "3.0.0"
        assert app.debug is True


class TestTinkerUvicornSettings:
    """Test that tinker() correctly stores uvicorn configuration."""
    
    def test_stores_host(self):
        app = Core()
        app.tinker(host="0.0.0.0")
        assert app._uvicorn_config["host"] == "0.0.0.0"
    
    def test_stores_port(self):
        app = Core()
        app.tinker(port=9000)
        assert app._uvicorn_config["port"] == 9000
    
    def test_stores_reload(self):
        app = Core()
        app.tinker(reload=True)
        assert app._uvicorn_config["reload"] is True
    
    def test_stores_log_level(self):
        app = Core()
        app.tinker(log_level="debug")
        assert app._uvicorn_config["log_level"] == "debug"
    
    def test_stores_workers(self):
        app = Core()
        app.tinker(workers=4)
        assert app._uvicorn_config["workers"] == 4
    
    def test_stores_multiple_settings(self):
        app = Core()
        app.tinker(
            host="127.0.0.1",
            port=5000,
            reload=False,
            log_level="warning"
        )
        assert app._uvicorn_config["host"] == "127.0.0.1"
        assert app._uvicorn_config["port"] == 5000
        assert app._uvicorn_config["reload"] is False
        assert app._uvicorn_config["log_level"] == "warning"
    
    def test_mixed_fastapi_and_uvicorn_settings(self):
        """Test that FastAPI attrs and uvicorn settings are handled separately."""
        app = Core()
        app.tinker(
            title="Mixed Test",  # FastAPI
            host="0.0.0.0",      # uvicorn
            port=8080            # uvicorn
        )
        assert app.title == "Mixed Test"
        assert "title" not in app._uvicorn_config
        assert app._uvicorn_config["host"] == "0.0.0.0"
        assert app._uvicorn_config["port"] == 8080


class TestTinkerMethodChaining:
    """Test that tinker() supports method chaining."""
    
    def test_returns_self(self):
        app = Core()
        result = app.tinker(title="Test")
        assert result is app
    
    def test_chained_calls(self):
        app = Core()
        app.tinker(title="First").tinker(version="1.0.0").tinker(host="0.0.0.0")
        assert app.title == "First"
        assert app.version == "1.0.0"
        assert app._uvicorn_config["host"] == "0.0.0.0"


# --- run() Tests ---

class TestRunMethod:
    """Test the run() method and uvicorn integration."""
    
    @patch("uvicorn.run")
    def test_calls_uvicorn_run(self, mock_run):
        app = Core()
        app.run()
        mock_run.assert_called_once()
    
    @patch("uvicorn.run")
    def test_passes_app_instance(self, mock_run):
        app = Core()
        app.run()
        args, _ = mock_run.call_args
        assert args[0] is app
    
    @patch("uvicorn.run")
    def test_passes_configured_host(self, mock_run):
        app = Core()
        app.tinker(host="192.168.1.1")
        app.run()
        _, kwargs = mock_run.call_args
        assert kwargs["host"] == "192.168.1.1"
    
    @patch("uvicorn.run")
    def test_passes_configured_port(self, mock_run):
        app = Core()
        app.tinker(port=3000)
        app.run()
        _, kwargs = mock_run.call_args
        assert kwargs["port"] == 3000
    
    @patch("uvicorn.run")
    def test_default_host_is_localhost(self, mock_run):
        """Test that default host is 127.0.0.1 when not specified."""
        app = Core()
        app.run()
        _, kwargs = mock_run.call_args
        assert kwargs["host"] == "127.0.0.1"
    
    @patch("uvicorn.run")
    def test_explicit_host_overrides_default(self, mock_run):
        """Test that explicit host setting overrides the default."""
        app = Core()
        app.tinker(host="0.0.0.0")
        app.run()
        _, kwargs = mock_run.call_args
        assert kwargs["host"] == "0.0.0.0"
    
    @patch("uvicorn.run")
    def test_does_not_modify_original_config(self, mock_run):
        """Test that run() doesn't modify the stored _uvicorn_config."""
        app = Core()
        app.tinker(port=8080)
        original_config = app._uvicorn_config.copy()
        app.run()
        # Original config should not have 'host' added
        assert app._uvicorn_config == original_config


# --- strict_versioning Tests ---

class TestStrictVersioning:
    """Test the strict_versioning mode."""
    
    def test_default_is_false(self):
        app = Core()
        assert app.strict_versioning is False
    
    def test_tinker_sets_strict_versioning_true(self):
        app = Core()
        app.tinker(strict_versioning=True)
        assert app.strict_versioning is True
    
    def test_tinker_sets_strict_versioning_false(self):
        app = Core()
        app.tinker(strict_versioning=True)
        app.tinker(strict_versioning=False)
        assert app.strict_versioning is False
    
    def test_strict_mode_rejects_missing_header(self):
        """Request without X-API-Version header should fail in strict mode."""
        app = Core()
        app.register(VersionedRoute)
        app.tinker(strict_versioning=True)
        client = TestClient(app)
        
        response = client.get("/versioned")
        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "API version required"
    
    def test_strict_mode_accepts_valid_header(self):
        """Request with valid X-API-Version header should succeed in strict mode."""
        app = Core()
        app.register(VersionedRoute)
        app.tinker(strict_versioning=True)
        client = TestClient(app)
        
        response = client.get("/versioned", headers={"X-API-Version": "1.5.0"})
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_strict_mode_rejects_invalid_version(self):
        """Request with version that doesn't match constraint should fail."""
        app = Core()
        app.register(VersionedRoute)
        app.tinker(strict_versioning=True)
        client = TestClient(app)
        
        # Requires >=2.0.0, sending 1.0.0
        response = client.post("/versioned", headers={"X-API-Version": "1.0.0"})
        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "API version incompatible"
    
    def test_lax_mode_allows_missing_header(self):
        """Request without header should succeed in lax mode (default)."""
        app = Core()
        app.register(VersionedRoute)
        # strict_versioning is False by default
        client = TestClient(app)
        
        response = client.get("/versioned")
        assert response.status_code == 200
    
    def test_unversioned_routes_unaffected(self):
        """Routes without @version decorator should work regardless of strict mode."""
        app = Core()
        app.register(UnversionedRoute)
        app.tinker(strict_versioning=True)
        client = TestClient(app)
        
        response = client.get("/unversioned")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


# --- Edge Cases ---

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_tinker_with_empty_kwargs(self):
        """Calling tinker with no arguments should not raise."""
        app = Core()
        result = app.tinker()
        assert result is app
    
    def test_tinker_unknown_fastapi_attr_goes_to_uvicorn(self):
        """Unknown kwargs should be treated as uvicorn settings."""
        app = Core()
        app.tinker(custom_setting="value")
        assert app._uvicorn_config["custom_setting"] == "value"
    
    def test_multiple_tinker_calls_accumulate(self):
        """Multiple tinker calls should accumulate settings."""
        app = Core()
        app.tinker(host="0.0.0.0")
        app.tinker(port=8080)
        assert app._uvicorn_config["host"] == "0.0.0.0"
        assert app._uvicorn_config["port"] == 8080
    
    def test_tinker_overwrites_previous_values(self):
        """Later tinker calls should overwrite previous values."""
        app = Core()
        app.tinker(port=8000)
        app.tinker(port=9000)
        assert app._uvicorn_config["port"] == 9000
