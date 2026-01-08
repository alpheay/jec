from jec_api import Route, version
from fastapi import Request

class SimpleRoute(Route):
    @version(">=1.0.0")
    async def get(self, request: Request):
        return {"status": "ok"}

class Test(Route):
    async def get(self, request: Request):
        return {"status": "ok"}
