# Changelog 0.0.5

## New Features

### JEC DevTools (Developer Console)
Implementation of a real-time, dark-themed web console for API debugging and monitoring. The console provides a comprehensive view of all incoming traffic and library metrics.

- **Real-time Monitoring**: Uses Server-Sent Events (SSE) for instant dashboard updates.
- **Integrated Environment**: Enable via `core.tinker(dev=True)` and access at `/__dev__` by default.
- **Configurable Path**: Use `dev_path` in `tinker()` to change the console's base URL.
- **Responsive Design**: Modern, premium dark theme with a slate gray and black palette.

### Interactive UI/UX
- **Animated Sidebar**: A sophisticated sidebar that animates into view when a request is selected, preventing UI clutter.
- **Data Indicators**: Requests now feature colored indicator dots (slate for logs, yellow for performance, violet for versions) to signal available deep-dive data.
- **Collapsible Logs**: Detailed log entries can be expanded to view function arguments, return values, and timestamps.
- **Performance Visualization**: Real-time execution timing with color-coded status bars (green=fast, yellow=medium, red=slow).

### Enhanced Decorators
All core decorators have been updated to proactively push data to the DevTools suite when active:
- **`@log`**: Captures CALL and RETURN/ERROR events with full metadata.
- **`@speed`**: Records precise execution duration for performance profiling.
- **`@version`**: Logs version check results, including client versions and pass/fail status.

### Internal Improvements
- **`DevConsoleStore`**: A thread-safe, in-memory singleton store for managing metrics with memory-safe limiters (default: 1000 entries).
- **Graceful Error Handling**: The DevTools module is decoupled; decorators fail silently if the dev store is unavailable.

## Usage Example

```python
from jec_api import Core, Route, log, speed

class Health(Route):
    @log
    @speed
    async def get(self):
        return {"status": "ok"}

core = Core()
core.tinker(
    dev=True,
    dev_path="/__debug__",
    port=8080
)
core.register(Health)

if __name__ == "__main__":
    core.run()
```

## Technical Details

- **Module**: `src/jec_api/dev_console.py` contains the store logic and UI generation.
- **Middleware**: Integrated `dev_request_tracker` middleware in `Core` manages internal request logging.
- **Data Model**: Structured `dataclasses` for Requests, Logs, Speed Metrics, and Version Checks.
