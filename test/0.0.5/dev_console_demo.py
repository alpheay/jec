"""Test file to demo dev console functionality."""

from jec_api import Core, Route, log, speed, version
from fastapi import Request

class Users(Route):
    """Example route with all decorators."""
    
    @log
    @speed
    @version(">=1.0.0")
    async def get(self, request: Request):
        """Get all users."""
        return {"users": ["alice", "bob", "charlie"]}
    
    @log
    @speed
    async def post(self):
        """Create a new user."""
        return {"created": True, "user": "newuser"}


class Health(Route):
    """Health check endpoint."""
    path = "/health"
    
    @speed
    async def get(self):
        return {"status": "ok"}


# Create the application
core = Core(title="Dev Console Demo", version="1.0.0")

# Enable dev mode with configurable path
core.tinker(dev=True, dev_path="/__dev__", port=8000)

# Register routes
core.register(Users)
core.register(Health)

if __name__ == "__main__":
    core.run()
