"""Dev Console - Real-time debugging console for JEC API."""

import time
import json
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from collections import deque
from threading import Lock

from fastapi import APIRouter, Request, Response
from fastapi.responses import HTMLResponse, StreamingResponse


@dataclass
class RequestLog:
    """HTTP request log entry."""
    id: str
    timestamp: str
    method: str
    path: str
    status_code: int
    duration_ms: float
    client_ip: str
    headers: Dict[str, str] = field(default_factory=dict)
    query_params: Dict[str, str] = field(default_factory=dict)


@dataclass
class LogEntry:
    """@log decorator entry."""
    id: str
    timestamp: str
    level: str  # info, warning, error
    function: str
    message: str
    args: str = ""
    result: str = ""


@dataclass
class SpeedMetric:
    """@speed decorator timing entry."""
    id: str
    timestamp: str
    function: str
    duration_ms: float
    path: str = ""


@dataclass
class VersionCheck:
    """@version decorator check entry."""
    id: str
    timestamp: str
    function: str
    constraint: str
    client_version: str
    passed: bool


class DevConsoleStore:
    """Thread-safe in-memory store for dev console metrics."""
    
    _instance: Optional["DevConsoleStore"] = None
    _lock = Lock()
    
    def __new__(cls) -> "DevConsoleStore":
        """Singleton pattern for global access."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, max_entries: int = 1000):
        if self._initialized:
            return
        self._initialized = True
        self._max_entries = max_entries
        self._counter = 0
        
        self.requests: deque = deque(maxlen=max_entries)
        self.logs: deque = deque(maxlen=max_entries)
        self.speed_metrics: deque = deque(maxlen=max_entries)
        self.version_checks: deque = deque(maxlen=max_entries)
        
        # SSE subscribers
        self._subscribers: List[asyncio.Queue] = []
        self._sub_lock = Lock()
    
    def _next_id(self) -> str:
        self._counter += 1
        return f"{self._counter:08d}"
    
    def _now(self) -> str:
        return datetime.now().isoformat()
    
    def add_request(self, **kwargs) -> RequestLog:
        entry = RequestLog(id=self._next_id(), timestamp=self._now(), **kwargs)
        self.requests.append(entry)
        self._notify("request", entry)
        return entry
    
    def add_log(self, level: str, function: str, message: str, **kwargs) -> LogEntry:
        entry = LogEntry(
            id=self._next_id(), 
            timestamp=self._now(),
            level=level,
            function=function,
            message=message,
            **kwargs
        )
        self.logs.append(entry)
        self._notify("log", entry)
        return entry
    
    def add_speed(self, function: str, duration_ms: float, path: str = "") -> SpeedMetric:
        entry = SpeedMetric(
            id=self._next_id(),
            timestamp=self._now(),
            function=function,
            duration_ms=duration_ms,
            path=path
        )
        self.speed_metrics.append(entry)
        self._notify("speed", entry)
        return entry
    
    def add_version_check(self, function: str, constraint: str, 
                          client_version: str, passed: bool) -> VersionCheck:
        entry = VersionCheck(
            id=self._next_id(),
            timestamp=self._now(),
            function=function,
            constraint=constraint,
            client_version=client_version,
            passed=passed
        )
        self.version_checks.append(entry)
        self._notify("version", entry)
        return entry
    
    def _notify(self, event_type: str, entry: Any):
        """Notify all SSE subscribers of new data."""
        data = {"type": event_type, "data": asdict(entry)}
        with self._sub_lock:
            for queue in self._subscribers:
                try:
                    queue.put_nowait(data)
                except asyncio.QueueFull:
                    pass  # Drop if queue is full
    
    def subscribe(self) -> asyncio.Queue:
        """Subscribe to real-time updates."""
        queue = asyncio.Queue(maxsize=100)
        with self._sub_lock:
            self._subscribers.append(queue)
        return queue
    
    def unsubscribe(self, queue: asyncio.Queue):
        """Unsubscribe from updates."""
        with self._sub_lock:
            if queue in self._subscribers:
                self._subscribers.remove(queue)
    
    def get_all(self) -> Dict[str, List[Dict]]:
        """Get all stored data."""
        return {
            "requests": [asdict(r) for r in self.requests],
            "logs": [asdict(l) for l in self.logs],
            "speed_metrics": [asdict(s) for s in self.speed_metrics],
            "version_checks": [asdict(v) for v in self.version_checks],
        }
    
    def clear(self):
        """Clear all stored data."""
        self.requests.clear()
        self.logs.clear()
        self.speed_metrics.clear()
        self.version_checks.clear()


# Global store instance
_store = DevConsoleStore()


def get_store() -> DevConsoleStore:
    """Get the global DevConsoleStore instance."""
    return _store


def create_dev_router(base_path: str = "/__dev__") -> APIRouter:
    """Create the dev console API router."""
    router = APIRouter(prefix=base_path, tags=["Dev Console"])
    
    @router.get("/", response_class=HTMLResponse)
    async def dev_console_ui():
        """Serve the dev console HTML UI."""
        return _get_console_html(base_path)
    
    @router.get("/api/all")
    async def get_all_data():
        """Get all stored metrics data."""
        return _store.get_all()
    
    @router.get("/api/requests")
    async def get_requests():
        """Get request log history."""
        return [asdict(r) for r in _store.requests]
    
    @router.get("/api/logs")
    async def get_logs():
        """Get decorator log entries."""
        return [asdict(l) for l in _store.logs]
    
    @router.get("/api/speed")
    async def get_speed_metrics():
        """Get speed timing metrics."""
        return [asdict(s) for s in _store.speed_metrics]
    
    @router.get("/api/versions")
    async def get_version_checks():
        """Get version check history."""
        return [asdict(v) for v in _store.version_checks]
    
    @router.get("/api/stream")
    async def sse_stream(request: Request):
        """Server-Sent Events stream for real-time updates."""
        async def event_generator():
            queue = _store.subscribe()
            try:
                # Send initial data
                yield f"data: {json.dumps({'type': 'init', 'data': _store.get_all()})}\n\n"
                
                while True:
                    if await request.is_disconnected():
                        break
                    try:
                        data = await asyncio.wait_for(queue.get(), timeout=30.0)
                        yield f"data: {json.dumps(data)}\n\n"
                    except asyncio.TimeoutError:
                        # Send heartbeat
                        yield f": heartbeat\n\n"
            finally:
                _store.unsubscribe(queue)
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )
    
    @router.post("/api/clear")
    async def clear_data():
        """Clear all stored metrics."""
        _store.clear()
        return {"status": "cleared"}
    
    return router


def _get_console_html(base_path: str) -> str:
    """Generate the dev console HTML with embedded CSS/JS."""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JEC DevTools</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        :root {{
            --bg-primary: #09090b;
            --bg-secondary: #0f0f12;
            --bg-card: #18181b;
            --bg-elevated: #1f1f23;
            --bg-hover: #27272a;
            --bg-active: #2e2e33;
            --border: #27272a;
            --border-light: #3f3f46;
            --text-primary: #fafafa;
            --text-secondary: #a1a1aa;
            --text-muted: #71717a;
            --text-dim: #52525b;
            --accent-green: #22c55e;
            --accent-emerald: #10b981;
            --accent-yellow: #eab308;
            --accent-orange: #f97316;
            --accent-red: #ef4444;
            --accent-blue: #3b82f6;
            --accent-violet: #8b5cf6;
            --accent-slate: #64748b;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }}
        
        /* Header */
        .header {{
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            padding: 14px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        
        .logo {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .logo-icon {{
            width: 32px;
            height: 32px;
            background: linear-gradient(135deg, #3f3f46 0%, #52525b 100%);
            border: 1px solid var(--border-light);
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 11px;
            color: var(--text-secondary);
            letter-spacing: 0.5px;
        }}
        
        .logo-text {{
            font-size: 16px;
            font-weight: 600;
            color: var(--text-primary);
            letter-spacing: -0.3px;
        }}
        
        .logo-text span {{
            color: var(--text-muted);
            font-weight: 400;
        }}
        
        .header-actions {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .status-badge {{
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 5px 10px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 4px;
            font-size: 12px;
            color: var(--text-secondary);
        }}
        
        .status-dot {{
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--accent-green);
            box-shadow: 0 0 6px var(--accent-green);
        }}
        
        .status-dot.disconnected {{
            background: var(--accent-red);
            box-shadow: 0 0 6px var(--accent-red);
        }}
        
        .btn {{
            padding: 6px 12px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 4px;
            color: var(--text-secondary);
            cursor: pointer;
            font-size: 12px;
            font-family: inherit;
            transition: all 0.15s;
        }}
        
        .btn:hover {{
            background: var(--bg-hover);
            border-color: var(--border-light);
            color: var(--text-primary);
        }}
        
        .btn-danger:hover {{
            border-color: var(--accent-red);
            color: var(--accent-red);
        }}
        
        /* Main Layout */
        .main {{
            display: grid;
            grid-template-columns: 1fr 380px;
            gap: 16px;
            padding: 16px;
            height: calc(100vh - 60px);
        }}
        
        /* Panels */
        .panel {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }}
        
        .panel-header {{
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: var(--bg-elevated);
        }}
        
        .panel-title {{
            font-weight: 500;
            font-size: 13px;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .panel-icon {{
            width: 16px;
            height: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0.6;
        }}
        
        .panel-count {{
            padding: 2px 6px;
            background: var(--bg-hover);
            border-radius: 3px;
            font-size: 11px;
            color: var(--text-muted);
            font-weight: 500;
        }}
        
        .panel-content {{
            flex: 1;
            overflow-y: auto;
        }}
        
        /* Requests */
        .request-item {{
            display: grid;
            grid-template-columns: 56px 1fr 50px 70px;
            gap: 12px;
            padding: 10px 16px;
            border-bottom: 1px solid var(--border);
            align-items: center;
            font-size: 12px;
            transition: background 0.1s;
            cursor: pointer;
        }}
        
        .request-item:hover {{
            background: var(--bg-hover);
        }}
        
        .method-badge {{
            padding: 3px 0;
            border-radius: 3px;
            font-weight: 600;
            font-size: 10px;
            text-align: center;
            font-family: 'JetBrains Mono', monospace;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }}
        
        .method-GET {{ background: rgba(34, 197, 94, 0.12); color: var(--accent-green); border: 1px solid rgba(34, 197, 94, 0.2); }}
        .method-POST {{ background: rgba(59, 130, 246, 0.12); color: var(--accent-blue); border: 1px solid rgba(59, 130, 246, 0.2); }}
        .method-PUT {{ background: rgba(234, 179, 8, 0.12); color: var(--accent-yellow); border: 1px solid rgba(234, 179, 8, 0.2); }}
        .method-DELETE {{ background: rgba(239, 68, 68, 0.12); color: var(--accent-red); border: 1px solid rgba(239, 68, 68, 0.2); }}
        .method-PATCH {{ background: rgba(139, 92, 246, 0.12); color: var(--accent-violet); border: 1px solid rgba(139, 92, 246, 0.2); }}
        
        .request-path {{
            font-family: 'JetBrains Mono', monospace;
            color: var(--text-primary);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            font-size: 12px;
        }}
        
        .status-code {{
            font-family: 'JetBrains Mono', monospace;
            font-weight: 500;
            font-size: 11px;
        }}
        
        .status-2xx {{ color: var(--accent-green); }}
        .status-3xx {{ color: var(--accent-blue); }}
        .status-4xx {{ color: var(--accent-yellow); }}
        .status-5xx {{ color: var(--accent-red); }}
        
        .duration {{
            color: var(--text-muted);
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            text-align: right;
        }}
        
        /* Sidebar */
        .sidebar {{
            display: flex;
            flex-direction: column;
            gap: 16px;
            overflow: hidden;
        }}
        
        .sidebar .panel {{
            flex: 1;
            min-height: 0;
        }}
        
        /* Interactive Log Entries */
        .log-item {{
            border-bottom: 1px solid var(--border);
            transition: background 0.1s;
        }}
        
        .log-item:hover {{
            background: var(--bg-hover);
        }}
        
        .log-header {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            cursor: pointer;
            user-select: none;
        }}
        
        .log-expand {{
            width: 16px;
            height: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-dim);
            transition: transform 0.15s;
            font-size: 10px;
        }}
        
        .log-item.expanded .log-expand {{
            transform: rotate(90deg);
        }}
        
        .log-level {{
            padding: 2px 5px;
            border-radius: 2px;
            font-size: 9px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }}
        
        .log-level-info {{ background: rgba(100, 116, 139, 0.2); color: var(--accent-slate); }}
        .log-level-warning {{ background: rgba(234, 179, 8, 0.15); color: var(--accent-yellow); }}
        .log-level-error {{ background: rgba(239, 68, 68, 0.15); color: var(--accent-red); }}
        
        .log-function {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: var(--text-secondary);
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        
        .log-time {{
            color: var(--text-dim);
            font-size: 10px;
            font-family: 'JetBrains Mono', monospace;
        }}
        
        .log-details {{
            display: none;
            padding: 0 12px 10px 36px;
            font-size: 11px;
        }}
        
        .log-item.expanded .log-details {{
            display: block;
        }}
        
        .log-message {{
            color: var(--text-primary);
            font-family: 'JetBrains Mono', monospace;
            background: var(--bg-primary);
            padding: 8px 10px;
            border-radius: 4px;
            border: 1px solid var(--border);
            word-break: break-all;
            white-space: pre-wrap;
            max-height: 120px;
            overflow-y: auto;
        }}
        
        .log-meta {{
            margin-top: 6px;
            display: flex;
            gap: 12px;
            color: var(--text-dim);
            font-size: 10px;
        }}
        
        .log-meta-item {{
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        
        .log-meta-label {{
            color: var(--text-muted);
        }}
        
        /* Speed Metrics */
        .speed-item {{
            padding: 8px 12px;
            border-bottom: 1px solid var(--border);
            transition: background 0.1s;
        }}
        
        .speed-item:hover {{
            background: var(--bg-hover);
        }}
        
        .speed-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 4px;
        }}
        
        .speed-function {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: var(--text-secondary);
        }}
        
        .speed-time {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            font-weight: 600;
        }}
        
        .speed-fast {{ color: var(--accent-green); }}
        .speed-medium {{ color: var(--accent-yellow); }}
        .speed-slow {{ color: var(--accent-red); }}
        
        .speed-bar {{
            height: 3px;
            background: var(--bg-primary);
            border-radius: 2px;
            overflow: hidden;
        }}
        
        .speed-bar-fill {{
            height: 100%;
            border-radius: 2px;
            transition: width 0.2s ease;
        }}
        
        /* Version Checks */
        .version-item {{
            padding: 8px 12px;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            gap: 10px;
            transition: background 0.1s;
        }}
        
        .version-item:hover {{
            background: var(--bg-hover);
        }}
        
        .version-status {{
            width: 6px;
            height: 6px;
            border-radius: 50%;
            flex-shrink: 0;
        }}
        
        .version-pass {{ background: var(--accent-green); box-shadow: 0 0 4px var(--accent-green); }}
        .version-fail {{ background: var(--accent-red); box-shadow: 0 0 4px var(--accent-red); }}
        
        .version-info {{
            flex: 1;
            min-width: 0;
        }}
        
        .version-function {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: var(--text-primary);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        
        .version-constraint {{
            font-size: 10px;
            color: var(--text-muted);
            margin-top: 2px;
        }}
        
        /* Empty State */
        .empty-state {{
            padding: 24px;
            text-align: center;
            color: var(--text-dim);
            font-size: 12px;
        }}
        
        /* Scrollbar */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: transparent;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: var(--border);
            border-radius: 3px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: var(--border-light);
        }}
        
        /* SVG Icons */
        .icon {{
            width: 14px;
            height: 14px;
            stroke: currentColor;
            stroke-width: 2;
            fill: none;
        }}
    </style>
</head>
<body>
    <header class="header">
        <div class="logo">
            <div class="logo-icon">JEC</div>
            <div class="logo-text">DevTools</div>
        </div>
        <div class="header-actions">
            <div class="status-badge">
                <span class="status-dot" id="status-dot"></span>
                <span id="status-text">Connected</span>
            </div>
            <button class="btn btn-danger" onclick="clearData()">Clear</button>
        </div>
    </header>
    
    <main class="main">
        <div class="panel">
            <div class="panel-header">
                <span class="panel-title">
                    <svg class="icon" viewBox="0 0 24 24"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
                    Requests
                    <span class="panel-count" id="request-count">0</span>
                </span>
            </div>
            <div class="panel-content" id="requests-list">
                <div class="empty-state">No requests captured yet</div>
            </div>
        </div>
        
        <div class="sidebar">
            <div class="panel">
                <div class="panel-header">
                    <span class="panel-title">
                        <svg class="icon" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
                        Logs
                        <span class="panel-count" id="log-count">0</span>
                    </span>
                </div>
                <div class="panel-content" id="logs-list">
                    <div class="empty-state">No logs yet</div>
                </div>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <span class="panel-title">
                        <svg class="icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                        Performance
                        <span class="panel-count" id="speed-count">0</span>
                    </span>
                </div>
                <div class="panel-content" id="speed-list">
                    <div class="empty-state">No timing data</div>
                </div>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <span class="panel-title">
                        <svg class="icon" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                        Versions
                        <span class="panel-count" id="version-count">0</span>
                    </span>
                </div>
                <div class="panel-content" id="version-list">
                    <div class="empty-state">No version checks</div>
                </div>
            </div>
        </div>
    </main>
    
    <script>
        const API_BASE = '{base_path}';
        
        let requests = [];
        let logs = [];
        let speedMetrics = [];
        let versionChecks = [];
        let expandedLogs = new Set();
        
        const requestsList = document.getElementById('requests-list');
        const logsList = document.getElementById('logs-list');
        const speedList = document.getElementById('speed-list');
        const versionList = document.getElementById('version-list');
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        
        function connect() {{
            const evtSource = new EventSource(API_BASE + '/api/stream');
            
            evtSource.onopen = () => {{
                statusDot.classList.remove('disconnected');
                statusText.textContent = 'Connected';
            }};
            
            evtSource.onmessage = (event) => {{
                const msg = JSON.parse(event.data);
                
                if (msg.type === 'init') {{
                    requests = msg.data.requests || [];
                    logs = msg.data.logs || [];
                    speedMetrics = msg.data.speed_metrics || [];
                    versionChecks = msg.data.version_checks || [];
                    renderAll();
                }} else if (msg.type === 'request') {{
                    requests.push(msg.data);
                    renderRequests();
                }} else if (msg.type === 'log') {{
                    logs.push(msg.data);
                    renderLogs();
                }} else if (msg.type === 'speed') {{
                    speedMetrics.push(msg.data);
                    renderSpeed();
                }} else if (msg.type === 'version') {{
                    versionChecks.push(msg.data);
                    renderVersions();
                }}
            }};
            
            evtSource.onerror = () => {{
                statusDot.classList.add('disconnected');
                statusText.textContent = 'Reconnecting...';
                evtSource.close();
                setTimeout(connect, 2000);
            }};
        }}
        
        function renderAll() {{
            renderRequests();
            renderLogs();
            renderSpeed();
            renderVersions();
        }}
        
        function renderRequests() {{
            document.getElementById('request-count').textContent = requests.length;
            if (requests.length === 0) {{
                requestsList.innerHTML = '<div class="empty-state">No requests captured yet</div>';
                return;
            }}
            
            requestsList.innerHTML = [...requests].reverse().map(r => {{
                const statusClass = r.status_code < 300 ? 'status-2xx' : 
                                   r.status_code < 400 ? 'status-3xx' :
                                   r.status_code < 500 ? 'status-4xx' : 'status-5xx';
                return `
                    <div class="request-item">
                        <span class="method-badge method-${{r.method}}">${{r.method}}</span>
                        <span class="request-path">${{escapeHtml(r.path)}}</span>
                        <span class="status-code ${{statusClass}}">${{r.status_code}}</span>
                        <span class="duration">${{r.duration_ms.toFixed(1)}}ms</span>
                    </div>
                `;
            }}).join('');
        }}
        
        function toggleLog(id) {{
            if (expandedLogs.has(id)) {{
                expandedLogs.delete(id);
            }} else {{
                expandedLogs.add(id);
            }}
            renderLogs();
        }}
        
        function renderLogs() {{
            document.getElementById('log-count').textContent = logs.length;
            if (logs.length === 0) {{
                logsList.innerHTML = '<div class="empty-state">No logs yet</div>';
                return;
            }}
            
            logsList.innerHTML = [...logs].reverse().slice(0, 100).map(l => {{
                const time = new Date(l.timestamp).toLocaleTimeString();
                const isExpanded = expandedLogs.has(l.id);
                return `
                    <div class="log-item ${{isExpanded ? 'expanded' : ''}}" onclick="toggleLog('${{l.id}}')">
                        <div class="log-header">
                            <span class="log-expand">&#9654;</span>
                            <span class="log-level log-level-${{l.level}}">${{l.level}}</span>
                            <span class="log-function">${{escapeHtml(l.function)}}</span>
                            <span class="log-time">${{time}}</span>
                        </div>
                        <div class="log-details">
                            <div class="log-message">${{escapeHtml(l.message)}}</div>
                            ${{l.args || l.result ? `
                            <div class="log-meta">
                                ${{l.args ? `<span class="log-meta-item"><span class="log-meta-label">args:</span> ${{escapeHtml(l.args)}}</span>` : ''}}
                                ${{l.result ? `<span class="log-meta-item"><span class="log-meta-label">result:</span> ${{escapeHtml(l.result.substring(0, 50))}}</span>` : ''}}
                            </div>
                            ` : ''}}
                        </div>
                    </div>
                `;
            }}).join('');
        }}
        
        function renderSpeed() {{
            document.getElementById('speed-count').textContent = speedMetrics.length;
            if (speedMetrics.length === 0) {{
                speedList.innerHTML = '<div class="empty-state">No timing data</div>';
                return;
            }}
            
            const maxTime = Math.max(...speedMetrics.map(s => s.duration_ms), 100);
            
            speedList.innerHTML = [...speedMetrics].reverse().slice(0, 50).map(s => {{
                const pct = Math.min((s.duration_ms / maxTime) * 100, 100);
                const speedClass = s.duration_ms < 50 ? 'speed-fast' : 
                                  s.duration_ms < 200 ? 'speed-medium' : 'speed-slow';
                const barColor = s.duration_ms < 50 ? 'var(--accent-green)' : 
                                s.duration_ms < 200 ? 'var(--accent-yellow)' : 'var(--accent-red)';
                return `
                    <div class="speed-item">
                        <div class="speed-header">
                            <span class="speed-function">${{escapeHtml(s.function)}}</span>
                            <span class="speed-time ${{speedClass}}">${{s.duration_ms.toFixed(2)}}ms</span>
                        </div>
                        <div class="speed-bar">
                            <div class="speed-bar-fill" style="width: ${{pct}}%; background: ${{barColor}};"></div>
                        </div>
                    </div>
                `;
            }}).join('');
        }}
        
        function renderVersions() {{
            document.getElementById('version-count').textContent = versionChecks.length;
            if (versionChecks.length === 0) {{
                versionList.innerHTML = '<div class="empty-state">No version checks</div>';
                return;
            }}
            
            versionList.innerHTML = [...versionChecks].reverse().slice(0, 30).map(v => `
                <div class="version-item">
                    <span class="version-status ${{v.passed ? 'version-pass' : 'version-fail'}}"></span>
                    <div class="version-info">
                        <div class="version-function">${{escapeHtml(v.function)}}</div>
                        <div class="version-constraint">${{v.constraint}} (client: ${{v.client_version || 'none'}})</div>
                    </div>
                </div>
            `).join('');
        }}
        
        function escapeHtml(str) {{
            if (!str) return '';
            return String(str)
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;');
        }}
        
        async function clearData() {{
            await fetch(API_BASE + '/api/clear', {{ method: 'POST' }});
            requests = [];
            logs = [];
            speedMetrics = [];
            versionChecks = [];
            expandedLogs.clear();
            renderAll();
        }}
        
        connect();
    </script>
</body>
</html>'''
