
import { CodeBlock } from "@/components/code-block";

export default function TypesPage() {
    return (
        <article className="prose prose-invert max-w-none">
            <div className="not-prose mb-12">
                <h1 className="text-4xl font-bold tracking-tight text-foreground">
                    Request & Response Types
                </h1>
                <p className="mt-4 text-xl text-muted-foreground leading-relaxed">
                    Leverage the full power of Pydantic models for type-safe request validation and response serialization.
                </p>
            </div>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Request Validation</h2>
                <p className="text-muted-foreground leading-relaxed mb-6">
                    JEC uses Pydantic models to define and validate request bodies. Simply define a Pydantic model and use it as a type hint for your route method argument.
                </p>
                <div className="mb-6 p-4 rounded-lg bg-card border border-border">
                    <p className="text-sm text-muted-foreground">
                        <strong className="text-accent-blue">Note:</strong> The first argument after <code>self</code> is treated as the request body. JEC will automatically validate the incoming JSON against your model.
                    </p>
                </div>
                <CodeBlock
                    filename="requests.py"
                    language="python"
                    code={`from pydantic import BaseModel
from jec_api import Route

# Define your request model
class CreateItemRequest(BaseModel):
    name: str
    price: float
    description: str | None = None
    is_offer: bool = False

class Items(Route):
    # Use the model as a type hint
    async def post(self, item: CreateItemRequest):
        # 'item' is now a valid instance of CreateItemRequest
        # If validation fails, JEC returns a 422 error automatically
        return {"name": item.name, "price": item.price}`}
                />
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Response Serialization</h2>
                <p className="text-muted-foreground leading-relaxed mb-6">
                    Define the structure of your API responses using Pydantic models. By specifying the return type hint, JEC automatically filters and serializes your data to match the model.
                </p>
                <CodeBlock
                    filename="responses.py"
                    language="python"
                    code={`from pydantic import BaseModel, EmailStr
from jec_api import Route

class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    # Private fields like 'password_hash' are excluded

class UserProfile(Route):
    # Define the return type
    async def get(self) -> User:
        user_data = self.db.get_user(1)
        # JEC ensures only fields defined in 'User' are returned
        return user_data`}
                />
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Accessing the Request Object</h2>
                <p className="text-muted-foreground leading-relaxed mb-6">
                    Sometimes you need access to the raw request object (e.g., to read headers, cookies, or client details). You can import <code>Request</code> from FastAPI (or Starlette) and add it as a parameter to your method.
                </p>
                <CodeBlock
                    language="python"
                    code={`from fastapi import Request
from jec_api import Route

class Debug(Route):
    async def get(self, request: Request):
        return {
            "client_host": request.client.host,
            "user_agent": request.headers.get("user-agent")
        }`}
                />
            </section>
        </article>
    );
}
