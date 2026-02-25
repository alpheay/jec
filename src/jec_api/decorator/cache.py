import functools
import hashlib
import json
import time
from dataclasses import dataclass
from fnmatch import fnmatch
from typing import Any, Callable, Optional

from fastapi import Request
from fastapi.responses import JSONResponse, Response

from .utils import find_request, is_async


@dataclass
class CacheEntry:
    value: Any
    status_code: int
    content_type: str
    headers: dict[str, str]
    expires_at: float
    stale_until: float
    etag: str


class MemoryCacheBackend:
    def __init__(self) -> None:
        self._store: dict[str, CacheEntry] = {}

    def get(self, key: str) -> Optional[CacheEntry]:
        return self._store.get(key)

    def set(self, key: str, entry: CacheEntry) -> None:
        self._store[key] = entry

    def invalidate(self, pattern: str) -> int:
        keys = [k for k in self._store if fnmatch(k, pattern)]
        for key in keys:
            self._store.pop(key, None)
        return len(keys)


_global_cache_backend = MemoryCacheBackend()


def set_cache_backend(backend: Any) -> None:
    global _global_cache_backend
    _global_cache_backend = backend


def get_cache_backend() -> Any:
    return _global_cache_backend


def _canonical_query(request: Request) -> str:
    items = sorted((k, v) for k, v in request.query_params.multi_items())
    return "&".join(f"{k}={v}" for k, v in items)


def _default_key(func_name: str, request: Request, vary: list[str]) -> str:
    pieces = [request.method.upper(), request.url.path, _canonical_query(request), func_name]
    for item in vary:
        if item == "query":
            continue
        if item.startswith("headers:"):
            header_name = item.split(":", 1)[1]
            pieces.append(f"h:{header_name}={request.headers.get(header_name, '')}")
    return "|".join(pieces)


def _compute_etag(payload: Any) -> str:
    if isinstance(payload, (dict, list)):
        raw = json.dumps(payload, sort_keys=True, default=str)
    else:
        raw = str(payload)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _build_response_from_entry(entry: CacheEntry, request: Request) -> Response:
    if request.headers.get("if-none-match") == entry.etag:
        return Response(status_code=304, headers={"ETag": entry.etag})

    response = JSONResponse(content=entry.value, status_code=entry.status_code)
    for k, v in entry.headers.items():
        response.headers[k] = v
    response.headers["ETag"] = entry.etag
    response.headers.setdefault("Cache-Control", "public")
    return response


def cache(
    ttl: int,
    *,
    key: Optional[str] = None,
    vary: Optional[list[str]] = None,
    stale_while_revalidate: int = 0,
    backend: str = "memory",
    cache_errors: bool = False,
) -> Callable:
    """Cache decorator for endpoint responses."""
    if ttl < 0:
        raise ValueError("ttl must be >= 0")

    vary = vary or ["query"]

    def decorator(func: Callable) -> Callable:
        func_name = func.__qualname__

        async def _resolve_key(request: Request) -> str:
            if key:
                template_data = {"path": request.url.path, "method": request.method.lower()}
                template_data.update(request.path_params)
                for header_name, header_value in request.headers.items():
                    template_data[f"h_{header_name.lower().replace('-', '_')}"] = header_value
                return key.format(**template_data)
            return _default_key(func_name, request, vary or [])

        async def _execute_and_cache(*args, **kwargs):
            request = find_request(args, kwargs)
            if request is None or ttl == 0:
                return await func(*args, **kwargs)

            active_backend = get_cache_backend() if backend == "memory" else get_cache_backend()
            cache_key = await _resolve_key(request)
            now = time.time()
            existing = active_backend.get(cache_key)

            if existing and existing.expires_at > now:
                return _build_response_from_entry(existing, request)

            if existing and existing.stale_until > now:
                return _build_response_from_entry(existing, request)

            result = await func(*args, **kwargs)

            status_code = getattr(result, "status_code", 200)
            if not cache_errors and status_code >= 400:
                return result

            if status_code not in {200, 203, 204} and not cache_errors:
                return result

            if isinstance(result, Response) and not isinstance(result, JSONResponse):
                return result

            if isinstance(result, JSONResponse):
                payload = json.loads(result.body.decode("utf-8")) if result.body else None
            else:
                payload = result

            etag = _compute_etag(payload)
            entry = CacheEntry(
                value=payload,
                status_code=status_code,
                content_type="application/json",
                headers={
                    "Cache-Control": f"public, max-age={ttl}, stale-while-revalidate={stale_while_revalidate}",
                    "Vary": ", ".join(vary),
                },
                expires_at=now + ttl,
                stale_until=now + ttl + max(stale_while_revalidate, 0),
                etag=etag,
            )
            active_backend.set(cache_key, entry)

            response = JSONResponse(content=payload, status_code=status_code)
            response.headers["Cache-Control"] = entry.headers["Cache-Control"]
            response.headers["Vary"] = entry.headers["Vary"]
            response.headers["ETag"] = etag
            return response

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await _execute_and_cache(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper = async_wrapper if is_async(func) else sync_wrapper
        wrapper._cache = {
            "ttl": ttl,
            "key": key,
            "vary": vary,
            "stale_while_revalidate": stale_while_revalidate,
            "backend": backend,
            "cache_errors": cache_errors,
        }
        return wrapper

    return decorator


def invalidate(pattern: str) -> int:
    """Invalidate cache keys matching a glob pattern."""
    backend = get_cache_backend()
    return backend.invalidate(pattern)
