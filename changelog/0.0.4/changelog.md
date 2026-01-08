# Changelog 0.0.4

## New Features

### `core.tinker()` Configuration Method
Added a new `tinker()` method to the `Core` class that provides a unified way to configure both FastAPI application attributes and uvicorn server settings.

- **FastAPI Configuration**: Supports all standard FastAPI attributes such as `title`, `description`, `version`, `docs_url`, `redoc_url`, `openapi_url`, `debug`, `lifespan`, `middleware`, `exception_handlers`, and more.
- **Uvicorn Configuration**: All non-FastAPI kwargs are stored and passed to `uvicorn.run()` when `core.run()` is called. Common options include:
  - `host`: Server host address (e.g., `"127.0.0.1"` or `"0.0.0.0"`)
  - `port`: Server port number
  - `reload`: Enable auto-reload during development
  - `log_level`: Set logging verbosity
  - `workers`: Number of worker processes
- **Method Chaining**: Returns `self` for fluent configuration.

### `core.run()` Method
Added a `run()` method to start the uvicorn server programmatically.

- Applies all settings configured via `tinker()`.
- **Default Host Behavior**: Defaults to `"127.0.0.1"` if no host is specified, matching the behavior of the `uvicorn` CLI for consistency.
- Allows running the app via `python app.py` instead of requiring `uvicorn app:core`.

### Strict Versioning Mode
Added `strict_versioning` option to `tinker()` that enforces the `X-API-Version` header on all versioned endpoints.

- When `strict_versioning=True`, requests without an `X-API-Version` header will receive a `400 Bad Request` response.
- When `strict_versioning=False` (default), missing version headers are allowed.

## Usage Examples

### Basic Configuration
```python
from jec_api import Core

core = Core()
core.tinker(
    title="My API",
    description="A well-configured API",
    version="1.0.0",
    host="127.0.0.1",
    port=8000,
    reload=True
)

if __name__ == "__main__":
    core.run()
```

### Strict Versioning
```python
core.tinker(strict_versioning=True)
# Now all @version decorated endpoints require X-API-Version header
```

## Technical Details

- `tinker()` is implemented in `src/jec_api/core.py`.
- FastAPI attributes are set via `setattr()` if they exist on the app instance.
- Uvicorn settings are stored in `_uvicorn_config` dict and applied on `run()`.
- `strict_versioning` is stored as an instance attribute and checked by the `@version` decorator.

## Bug Fixes

### Consistent Host Binding
Fixed an issue where the `run()` method would display a different host in logs than what was actually being used. The server now correctly defaults to `127.0.0.1` when no host is specified, matching uvicorn CLI behavior.
