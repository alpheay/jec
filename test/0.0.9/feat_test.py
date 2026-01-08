
import pytest
import time
import asyncio
from fastapi import Request, HTTPException, Response
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from jec_api import Core, Route, auth, log, speed, version, deprecated, ratelimit, timeout, retry

# --- Mock Auth Handler ---
async def mock_auth_handler(request: Request, roles: list[str] = None, scopes: list[str] = None, require_all: bool = False) -> bool:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return False

    token = auth_header.split(" ")[1]
    
    token_data = {
        "admin-token": {"roles": ["admin"], "scopes": ["read:all", "write:all"]},
        "user-token": {"roles": ["user"], "scopes": ["read:users"]},
        "guest-token": {"roles": ["guest"], "scopes": []},
    }
    
    if token not in token_data:
        return False

    user_roles = token_data.get(token, {}).get("roles", [])
    user_scopes = token_data.get(token, {}).get("scopes", [])
    request.state.user = {"roles": user_roles, "scopes": user_scopes}

    # Check roles if provided
    if roles:
        if require_all:
            if not all(role in user_roles for role in roles):
                return False
        else:
            if not any(role in user_roles for role in roles):
                return False
    
    # Check scopes if provided
    if scopes:
        if require_all:
            if not all(scope in user_scopes for scope in scopes):
                return False
        else:
            if not any(scope in user_scopes for scope in scopes):
                return False
            
    return True


# =============================================================================
# Test Routes - Enhanced Existing Decorators
# =============================================================================

class LogSimple(Route):
    path = "/log/simple"
    @log
    async def get(self):
        return {"msg": "simple log"}

class LogConfigured(Route):
    path = "/log/configured"
    @log(level="debug", include_args=False, include_result=False, message="CustomPrefix")
    async def get(self):
        return {"msg": "configured log"}

class SpeedSimple(Route):
    path = "/speed/simple"
    @speed
    async def get(self):
        return {"msg": "fast"}

class SpeedWithThresholds(Route):
    path = "/speed/thresholds"
    @speed(warn_threshold_ms=1, error_threshold_ms=10)
    async def get(self):
        import asyncio
        await asyncio.sleep(0.005)  # 5ms - should trigger warning
        return {"msg": "slow"}

class VersionSimple(Route):
    path = "/version/simple"
    @version(">=1.0.0")
    async def get(self):
        return {"version": "1+"}

class VersionDeprecated(Route):
    path = "/version/deprecated"
    @version(">=1.0.0", deprecated=True, sunset="2025-12-01", message="Use v2 API")
    async def get(self):
        return JSONResponse(content={"version": "deprecated"})

class AuthSimple(Route):
    path = "/auth/simple"
    @auth(True)
    async def get(self):
        return {"status": "authenticated"}

class AuthWithScopes(Route):
    path = "/auth/scopes"
    @auth(True, scopes=["read:all"])
    async def get(self):
        return {"status": "has scope"}

class AuthRequireAll(Route):
    path = "/auth/require-all"
    @auth(True, roles=["admin", "user"], require_all=True)
    async def get(self):
        return {"status": "has all roles"}

class AuthCustomError(Route):
    path = "/auth/custom-error"
    @auth(True, custom_error="Custom auth failure message")
    async def get(self):
        return {"status": "ok"}


# =============================================================================
# Test Routes - New Decorators
# =============================================================================

class DeprecatedSimple(Route):
    path = "/deprecated/simple"
    @deprecated
    async def get(self):
        return JSONResponse(content={"msg": "deprecated"})

class DeprecatedWithMessage(Route):
    path = "/deprecated/message"
    @deprecated("Use /v2/endpoint instead", sunset="2025-06-01")
    async def get(self):
        return JSONResponse(content={"msg": "deprecated with message"})

class RateLimitSimple(Route):
    path = "/ratelimit/simple"
    @ratelimit(limit=3, window=60)
    async def get(self):
        return JSONResponse(content={"msg": "rate limited"})

class RateLimitGlobal(Route):
    path = "/ratelimit/global"
    @ratelimit(limit=2, window=60, by="global")
    async def get(self):
        return JSONResponse(content={"msg": "global rate limit"})

class TimeoutSimple(Route):
    path = "/timeout/simple"
    @timeout(seconds=5)
    async def get(self):
        return {"msg": "fast"}

class TimeoutSlow(Route):
    path = "/timeout/slow"
    @timeout(seconds=0.1, message="Operation timed out")
    async def get(self):
        await asyncio.sleep(0.5)  # Will timeout
        return {"msg": "should not see this"}

class RetrySimple(Route):
    path = "/retry/simple"
    attempt_count = 0
    
    @retry(attempts=3, delay=0.01, backoff=1.0)
    async def get(self):
        RetrySimple.attempt_count += 1
        if RetrySimple.attempt_count < 3:
            raise ValueError("Simulated failure")
        return {"msg": "succeeded after retry", "attempts": RetrySimple.attempt_count}


# =============================================================================
# Test Suite
# =============================================================================

def test_enhanced_log_decorator():
    """Test @log decorator with and without configuration."""
    app = Core()
    app.register(LogSimple)
    app.register(LogConfigured)
    client = TestClient(app)
    
    # Simple usage
    resp = client.get("/log/simple")
    assert resp.status_code == 200
    assert resp.json() == {"msg": "simple log"}
    
    # Configured usage
    resp = client.get("/log/configured")
    assert resp.status_code == 200
    assert resp.json() == {"msg": "configured log"}


def test_enhanced_speed_decorator():
    """Test @speed decorator with thresholds."""
    app = Core()
    app.register(SpeedSimple)
    app.register(SpeedWithThresholds)
    client = TestClient(app)
    
    # Simple usage
    resp = client.get("/speed/simple")
    assert resp.status_code == 200
    
    # With thresholds (should log warning)
    resp = client.get("/speed/thresholds")
    assert resp.status_code == 200


def test_enhanced_version_decorator():
    """Test @version decorator with deprecation support."""
    app = Core()
    app.register(VersionSimple)
    app.register(VersionDeprecated)
    client = TestClient(app)
    
    # Simple usage
    resp = client.get("/version/simple", headers={"X-API-Version": "1.0.0"})
    assert resp.status_code == 200
    
    # Deprecated endpoint should add headers
    resp = client.get("/version/deprecated", headers={"X-API-Version": "1.0.0"})
    assert resp.status_code == 200
    assert resp.headers.get("Deprecation") == "true"
    assert resp.headers.get("Sunset") == "2025-12-01"


def test_enhanced_auth_decorator():
    """Test @auth decorator with scopes and require_all."""
    app = Core()
    app.set_auth_handler(mock_auth_handler)
    app.register(AuthSimple)
    app.register(AuthWithScopes)
    app.register(AuthRequireAll)
    app.register(AuthCustomError)
    client = TestClient(app)
    
    # Simple auth
    assert client.get("/auth/simple").status_code == 403
    assert client.get("/auth/simple", headers={"Authorization": "Bearer user-token"}).status_code == 200
    
    # Scopes - user doesn't have read:all scope
    assert client.get("/auth/scopes", headers={"Authorization": "Bearer user-token"}).status_code == 403
    assert client.get("/auth/scopes", headers={"Authorization": "Bearer admin-token"}).status_code == 200
    
    # Require all - admin doesn't have 'user' role
    assert client.get("/auth/require-all", headers={"Authorization": "Bearer admin-token"}).status_code == 403
    
    # Custom error message
    resp = client.get("/auth/custom-error")
    assert resp.status_code == 403
    assert "Custom auth failure message" in resp.json().get("detail", "")


def test_deprecated_decorator():
    """Test @deprecated decorator."""
    app = Core()
    app.register(DeprecatedSimple)
    app.register(DeprecatedWithMessage)
    client = TestClient(app)
    
    # Simple deprecation
    resp = client.get("/deprecated/simple")
    assert resp.status_code == 200
    assert resp.headers.get("Deprecation") == "true"
    
    # With message and sunset
    resp = client.get("/deprecated/message")
    assert resp.status_code == 200
    assert resp.headers.get("Deprecation") == "true"
    assert resp.headers.get("Sunset") == "2025-06-01"


def test_ratelimit_decorator():
    """Test @ratelimit decorator."""
    app = Core()
    app.register(RateLimitSimple)
    app.register(RateLimitGlobal)
    client = TestClient(app)
    
    # First 3 requests should succeed
    for _ in range(3):
        resp = client.get("/ratelimit/simple")
        assert resp.status_code == 200
    
    # 4th request should be rate limited
    resp = client.get("/ratelimit/simple")
    assert resp.status_code == 429
    assert "Retry-After" in resp.headers


def test_timeout_decorator():
    """Test @timeout decorator."""
    app = Core()
    app.register(TimeoutSimple)
    app.register(TimeoutSlow)
    client = TestClient(app)
    
    # Fast endpoint should work
    resp = client.get("/timeout/simple")
    assert resp.status_code == 200
    
    # Slow endpoint should timeout
    resp = client.get("/timeout/slow")
    assert resp.status_code == 504
    assert "Operation timed out" in resp.json().get("detail", "")


def test_retry_decorator():
    """Test @retry decorator."""
    app = Core()
    RetrySimple.attempt_count = 0  # Reset counter
    app.register(RetrySimple)
    client = TestClient(app)
    
    resp = client.get("/retry/simple")
    assert resp.status_code == 200
    assert resp.json()["attempts"] == 3


def test_backward_compatibility():
    """Ensure existing 0.0.8 tests still work with enhanced decorators."""
    # Run the basic auth test
    class AuthPublic(Route):
        path = "/compat/public"
        @auth(False)
        async def get(self):
            return {"status": "public"}

    class AuthPrivate(Route):
        path = "/compat/private"
        @auth(True)
        async def get(self):
            return {"status": "private"}
    
    app = Core()
    app.set_auth_handler(mock_auth_handler)
    app.register(AuthPublic)
    app.register(AuthPrivate)
    client = TestClient(app)
    
    assert client.get("/compat/public").status_code == 200
    assert client.get("/compat/private").status_code == 403
    assert client.get("/compat/private", headers={"Authorization": "Bearer user-token"}).status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
