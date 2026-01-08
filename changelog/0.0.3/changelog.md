# Changelog 0.0.3

## New Features

### API Decorators
Added a suite of decorators to enhance API endpoint functionality and observability.

- **`@log`**: Automatically logs function calls, including arguments and return values (or exceptions). Supports both sync and async methods.
- **`@speed`**: Measures and logs the execution time of an endpoint in milliseconds. Useful for performance monitoring.
- **`@version`**: Enforces API versioning constraints.
    - Supports semantic versioning operators: `>=`, `<=`, `>`, `<`, `==`, `!=`.
    - Checks the `X-API-Version` header in the incoming request.
    - Returns a `400 Bad Request` if the version constraint is not met.
    - Requires the endpoint method to accept a `Request` object.

### Package Exports
- Exported `log`, `speed`, and `version` from the top-level `jec_api` package for easier imports.

## Technical Details
- Decorators are implemented in `src/jec_api/decorators.py`.
- They use `functools.wraps` to preserve method metadata.
- Internal helper `_is_async` ensures compatibility with FastAPI's async handler logic.
