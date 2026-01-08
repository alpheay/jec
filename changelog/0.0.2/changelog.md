# Changelog 0.0.2

## Features

### Strict Method Naming
- **Breaking Change**: Route methods are now **strictly** mapped to HTTP verbs.
- Only methods named exactly `get`, `post`, `put`, `delete`, `patch`, `options`, or `head` will be registered as endpoints.
- Previous behavior where methods like `get_users` or `post_item` were automatically mapped to `/users` or `/item` has been removed.
- This ensures explicit control over route definitions and prevents accidental endpoint exposure.

### Data Object Support
- Added native support for **Pydantic models** in route methods.
- **Request Body**: Type hints on the first non-self parameter are now automatically used as the request body model.
- **Response Model**: Return type hints are now automatically registered as the response model for the endpoint.
- This enables automatic validation, serialization, and OpenAPI schema generation for user-defined data objects.

## Usage Example

```python
from pydantic import BaseModel
from jec_api import Route

class CreateItem(BaseModel):
    name: str

class ItemResponse(BaseModel):
    id: int
    name: str

class Items(Route):
    # Strictly mapped to POST /items
    async def post(self, data: CreateItem) -> ItemResponse:
        return ItemResponse(id=1, name=data.name)

    # Strictly mapped to GET /items
    async def get(self) -> list[ItemResponse]:
        return []
        
    # NOT mapped (ignored)
    def get_helper(self):
        pass
```
