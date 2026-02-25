"""CLI for JEC utilities including deploy-readiness checks."""

from __future__ import annotations

import argparse
import importlib
import json
from dataclasses import asdict, dataclass
from typing import Any

from .core import Core
from .discovery import discover_routes


@dataclass
class Finding:
    id: str
    severity: str
    location: str
    message: str
    fix: str


SEVERITY_RANK = {"info": 1, "warning": 2, "error": 3}


def _load_app_from_target(target: str) -> Core | None:
    if ":" not in target:
        return None
    module_name, app_name = target.split(":", 1)
    module = importlib.import_module(module_name)
    app = getattr(module, app_name, None)
    return app if isinstance(app, Core) else None


def run_doctor(package: str = "routes", app_target: str | None = None) -> list[Finding]:
    findings: list[Finding] = []

    routes = discover_routes(package, recursive=True)
    seen: set[tuple[str, str]] = set()

    for route_class in routes:
        base_path = route_class.get_path()
        for method, sub_path, fn, _, _ in route_class.get_endpoints():
            full_path = base_path if sub_path == "/" else base_path.rstrip("/") + sub_path
            key = (method, full_path)
            location = f"{route_class.__name__}.{fn.__name__}"

            if key in seen:
                findings.append(
                    Finding(
                        id="JEC001",
                        severity="error",
                        location=location,
                        message=f"Duplicate route collision detected for {method} {full_path}.",
                        fix="Rename or move one of the colliding endpoints so each method+path pair is unique.",
                    )
                )
            seen.add(key)

            if method in {"POST", "PUT", "PATCH", "DELETE"} and not getattr(fn, "_auth_enabled", False):
                findings.append(
                    Finding(
                        id="JEC014",
                        severity="warning",
                        location=location,
                        message="Write endpoint has no authentication decorator.",
                        fix="Add @auth(...) to protect this endpoint, or explicitly use @auth(False) if intended.",
                    )
                )

            lowered = fn.__name__.lower()
            if any(token in lowered for token in {"report", "export", "sync"}) and not getattr(fn, "_timeout", False):
                findings.append(
                    Finding(
                        id="JEC031",
                        severity="warning",
                        location=location,
                        message="Potentially slow endpoint has no timeout decorator.",
                        fix="Add @timeout(seconds=...) with an endpoint-appropriate maximum runtime.",
                    )
                )

            if method == "GET" and not getattr(fn, "_cache", None):
                findings.append(
                    Finding(
                        id="JEC042",
                        severity="info",
                        location=location,
                        message="GET endpoint does not declare a cache strategy.",
                        fix="Consider adding @cache(ttl=...) where safe to reduce latency and server load.",
                    )
                )

    app = _load_app_from_target(app_target) if app_target else None
    if app is not None and not getattr(app, "error_envelope", True):
        findings.append(
            Finding(
                id="JEC022",
                severity="warning",
                location=app_target,
                message="Standard error envelope is disabled.",
                fix="Enable app.tinker(error_envelope=True) to keep client-side error handling consistent.",
            )
        )

    return findings


def _print_text(findings: list[Finding]) -> None:
    if not findings:
        print("No findings. Your project passed jec doctor checks.")
        return

    for finding in findings:
        print(f"{finding.id} [{finding.severity}] {finding.location}")
        print(f"{finding.message}")
        print(f"Fix: {finding.fix}\n")


def _exit_code(findings: list[Finding], fail_on: str) -> int:
    threshold = SEVERITY_RANK[fail_on]
    for finding in findings:
        if SEVERITY_RANK[finding.severity] >= threshold:
            return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="jec")
    sub = parser.add_subparsers(dest="command")

    doctor = sub.add_parser("doctor", help="Run deploy-readiness diagnostics.")
    doctor.add_argument("--strict", action="store_true", help="Alias for --fail-on warning")
    doctor.add_argument("--format", choices=["text", "json"], default="text")
    doctor.add_argument("--fail-on", choices=["error", "warning", "info"], default="error")
    doctor.add_argument("--package", default="routes", help="Package to scan for Route classes.")
    doctor.add_argument("--app", default=None, help="Optional app target in module:attribute format.")

    args = parser.parse_args(argv)

    if args.command != "doctor":
        parser.print_help()
        return 0

    fail_on = "warning" if args.strict else args.fail_on
    findings = run_doctor(package=args.package, app_target=args.app)

    if args.format == "json":
        print(json.dumps([asdict(item) for item in findings], indent=2))
    else:
        _print_text(findings)

    return _exit_code(findings, fail_on)


if __name__ == "__main__":
    raise SystemExit(main())
