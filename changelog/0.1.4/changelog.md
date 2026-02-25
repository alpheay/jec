# Changelog 0.1.4

## Overview
Version `0.1.4` focuses on safer defaults and deployment confidence. This release introduces three major capabilities:

1. Standardized error handling envelopes (Feature 3)
2. A first-class cache decorator (cache feature from roadmap)
3. A deploy-readiness diagnostics command (`jec doctor`, Feature 8)

Together, these changes reduce boilerplate while improving consistency for both API authors and client developers.

---

## Added: Standard Error Envelope by Default

### What changed
- Added a new error handling module at `src/jec_api/error_handling.py`.
- `Core` now installs default middleware and exception handlers during app initialization.
- Every request now gets a request id (`X-Request-Id`) generated or propagated from incoming headers.
- Validation, HTTP exceptions, and unhandled exceptions are normalized into a consistent envelope containing:
  - `error.code`
  - `error.message`
  - optional `error.details`
  - `request_id`
  - `timestamp`
- Sensitive fields are redacted in validation details (`password`, `token`, `authorization`, `api_key`, `secret`).
- Added `Core.tinker(...)` flags:
  - `error_envelope`
  - `error_include_details`
  - `error_redaction`

### Developer experience impact
- **Predictable error shape for all clients:** front-end, mobile, and SDK consumers no longer need endpoint-specific parsing logic.
- **Faster debugging:** request ids are always returned in both headers and payloads, making logs/traces easier to correlate.
- **Safer defaults:** accidental leakage of sensitive values in validation errors is reduced by default redaction.
- **Configurable strictness:** teams can keep defaults in production while enabling richer details in development.

---

## Added: First-Class Cache Decorator

### What changed
- Added `src/jec_api/decorator/cache.py` with:
  - `@cache(...)` decorator
  - in-memory cache backend
  - key generation from method/path/query (+ optional vary headers)
  - TTL handling with optional stale-while-revalidate window
  - `ETag` support and `304` handling for matching `If-None-Match`
  - cache invalidation helper: `cache_invalidate(pattern)`
- Exported decorator APIs through:
  - `src/jec_api/decorator/__init__.py`
  - `src/jec_api/__init__.py`
- Added `Core.tinker(cache_backend="memory")` plumbing to configure backend selection.

### Developer experience impact
- **Performance with one line:** developers can cache expensive read endpoints without writing per-route cache plumbing.
- **Built-in HTTP semantics:** ETag and cache-control behavior improve browser/client efficiency out of the box.
- **Operational simplicity:** wildcard invalidation (`users:*`) makes cache refresh strategies easier to implement during writes.
- **Safer sharing defaults:** only successful response classes are cached by default, minimizing accidental caching of errors.

---

## Added: `jec doctor` Deploy-Readiness Command

### What changed
- Added CLI implementation in `src/jec_api/cli.py` and entry module `src/jec_api/__main__.py`.
- Introduced `jec doctor` command with support for:
  - `--strict`
  - `--format json`
  - `--fail-on {error,warning,info}`
  - `--package <package>` for route discovery scope
  - `--app <module:app>` for optional app-level checks
- Implemented initial diagnostic rule set with stable IDs and severity levels, including:
  - route collision detection
  - write endpoint auth warnings
  - slow-endpoint timeout recommendations
  - GET endpoint caching recommendations
  - app-level warning when standardized envelope is disabled

### Developer experience impact
- **Pre-deploy confidence:** catches common production mistakes before shipping.
- **Actionable findings:** each rule includes fix guidance so teams can remediate quickly.
- **CI-friendly:** non-zero exit behavior with severity threshold supports merge gates.
- **Machine-readable output:** JSON mode enables automated annotations/reporting.

---

## Internal notes
- `@auth(...)` now exposes metadata on wrapped functions to support diagnostics tooling.
- Existing behavior remains compatible with current route/decorator usage patterns.

