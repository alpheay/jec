# Changelog 0.0.9

## Enhanced Decorators

We have significantly enhanced the decorator system to provide granular control while maintaining the simplicity of the original API. All decorators now support rich configuration options.

---

### 1. `@log` - Advanced Request Logging

Logs request lifecycle events including entry, exit, arguments, and results. improved with log levels and truncation control.

**Signature:**
```python
def log(
    func=None, *, 
    level: str = "info", 
    include_args: bool = True, 
    include_result: bool = True, 
    max_length: int = 200, 
    message: str = None
)
```

**Parameters:**
- `level`: Logging level (`"debug"`, `"info"`, `"warning"`, `"error"`). Default: `"info"`.
- `include_args`: If `True`, logs function arguments on entry. Default: `True`.
- `include_result`: If `True`, logs return value on exit. Default: `True`.
- `max_length`: Truncates arguments and results to this length to prevents log flooding. Default: `200`.
- `message`: Optional prefix tag for the log entry.

**Usage Examples:**

```python
# 1. Standard Usage (Defaults)
# Logs: [CALL] get_users | args=... / [RETURN] get_users | result=...
@log
async def get_users(): ...

# 2. Privacy-Focused (No data logging)
# Logs: [CALL] sensitive_op / [RETURN] sensitive_op
@log(include_args=False, include_result=False)
async def sensitive_op(password: str): ...

# 3. Debugging Heavy Payloads
@log(level="debug", max_length=5000, message="PAYLOAD_DEBUG")
async def process_large_file(file: bytes): ...
```

---

### 2. `@speed` - Performance Monitoring

Measures execution time with configurable alert thresholds.

**Signature:**
```python
def speed(
    func=None, *, 
    warn_threshold_ms: float = None, 
    error_threshold_ms: float = None, 
    include_in_response: bool = False
)
```

**Parameters:**
- `warn_threshold_ms`: Log a warning if execution time exceeds this value (ms).
- `error_threshold_ms`: Log an error if execution time exceeds this value (ms).
- `include_in_response`: If `True`, adds `X-Response-Time` header to the HTTP response.

**Usage Examples:**

```python
# 1. Standard Profiling
# Logs: [SPEED] calculate_stats | 45.2ms
@speed
async def calculate_stats(): ...

# 2. SLA Monitoring
# Warns if > 100ms, Errors if > 500ms
@speed(warn_threshold_ms=100, error_threshold_ms=500)
async def critical_path(): ...

# 3. Client Transparency
# Returns header: X-Response-Time: 12.5ms
@speed(include_in_response=True)
async def public_api(): ...
```

---

### 3. `@version` - API Versioning

Enforces semantic versioning via the `X-API-Version` header.

**Signature:**
```python
def version(
    constraint: str, *, 
    deprecated: bool = False, 
    sunset: str = None, 
    message: str = None
)
```

**Parameters:**
- `constraint`: Comparison string (e.g., `">=1.0.0"`, `"==2.0"`, `"<3.0"`).
- `deprecated`: If `True`, adds `Deprecation: true` header.
- `sunset`: ISO 8601 date string for endpoint removal (adds `Sunset` header).
- `message`: Custom error message or deprecation notice.

**Side Effects:**
- Returns `400 Bad Request` if version constraint fails.
- Adds `Deprecation` and `Sunset` headers if configured.

**Usage Examples:**

```python
# 1. Minimum Version
@version(">=1.5.0")
async def new_feature(): ...

# 2. Exact Version Match
@version("==2.0.0")
async def strict_endpoint(): ...

# 3. Deprecated Version
# Headers: Deprecation: true, Sunset: 2025-12-31
@version("<=1.0.0", deprecated=True, sunset="2025-12-31", message="Please upgrade to v2")
async def legacy_endpoint(): ...
```

---

### 4. `@auth` - Access Control

Enforces authentication types, roles, and scopes.

**Signature:**
```python
def auth(
    enabled: bool = True, *, 
    roles: list[str] = None, 
    scopes: list[str] = None, 
    require_all: bool = False, 
    custom_error: str = None
)
```

**Parameters:**
- `roles`: List of required user roles (e.g., `["admin", "mod"]`).
- `scopes`: List of required OAuth scopes (e.g., `["read:users"]`).
- `require_all`: If `True`, user must have **ALL** listed roles/scopes. If `False`, **ANY** match grants access.
- `custom_error`: Custom message for `403 Forbidden` responses.

**Usage Examples:**

```python
# 1. Public Endpoint
@auth(False)
async def login(): ...

# 2. Role-Based Access (ANY role)
# Access granted to 'admin' OR 'moderator'
@auth(True, roles=["admin", "moderator"])
async def moderate_content(): ...

# 3. Strict Scope & Role (ALL required)
# User needs 'admin' role AND 'write:system' scope
@auth(True, roles=["admin"], scopes=["write:system"], require_all=True)
async def system_update(): ...
```

---

## New Decorators

### 5. `@deprecated` - Endpoint Lifecycle

Explicitly marks an endpoint as deprecated.

**Signature:**
```python
def deprecated(
    message=None, *, 
    alternative: str = None, 
    sunset: str = None
)
```

**Side Effects:**
- Adds `Deprecation: true` header.
- Adds `Sunset: <date>` header if provided.
- Adds `X-Deprecation-Alternative: <path>` header if provided.

**Usage:**
```python
@deprecated("Use /v2/users instead", alternative="/v2/users", sunset="2025-06-01")
async def get_users_old(): ...
```

### 6. `@ratelimit` - Abuse Prevention

Limits request frequency by IP, User, or Globally.

**Signature:**
```python
def ratelimit(
    limit: int = 100, 
    window: int = 60, 
    by: str = "ip", 
    message: str = None
)
```

**Parameters:**
- `limit`: Max requests allowed in window.
- `window`: Time window in seconds.
- `by`: keying strategy: `"ip"` (client IP), `"user"` (auth user ID), or `"global"` (shared).

**Side Effects:**
- Returns `429 Too Many Requests` when exceeded.
- Adds headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.

**Usage:**
```python
# 10 requests per minute per user ID
@ratelimit(limit=10, window=60, by="user")
async def expensive_query(): ...
```

### 7. `@timeout` - Execution Limits

Enforces strict time limits on request processing.

**Signature:**
```python
def timeout(seconds: float = 30.0, message: str = None)
```

**Side Effects:**
- Raises `504 Gateway Timeout` if execution exceeds limit.
- Cancels the underlying asyncio task.

**Usage:**
```python
# Fails if not completed in 500ms
@timeout(seconds=0.5)
async def quick_search(): ...
```

### 8. `@retry` - Resilience

Automatically retries failed operations.

**Signature:**
```python
def retry(
    attempts: int = 3, 
    delay: float = 1.0, 
    backoff: float = 2.0, 
    exceptions: tuple = (Exception,)
)
```

**Parameters:**
- `attempts`: Total attempts (1 initial + retries).
- `delay`: Initial wait time between retries (seconds).
- `backoff`: Multiplier for delay after each failure.
- `exceptions`: Tuple of Exception classes to catch.

**Usage:**
```python
# Retry 3 times, catching only ConnectionError, doubling wait time (1s, 2s, 4s)
@retry(attempts=3, delay=1.0, backoff=2.0, exceptions=(ConnectionError,))
async def flaky_upstream_call(): ...
```
