
import { CodeBlock } from "@/components/code-block";
import Link from "next/link";


export default function AuthenticationPage() {
    return (
        <article className="prose prose-invert max-w-none">
            <div className="not-prose mb-12">
                <h1 className="text-4xl font-bold tracking-tight text-foreground">
                    Authentication & Authorization
                </h1>
                <p className="mt-4 text-xl text-muted-foreground leading-relaxed">
                    A robust, flexible authentication system designed to work seamlessly with JEC's class-based routes.
                </p>
            </div>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">The @auth Decorator</h2>
                <p className="text-muted-foreground leading-relaxed mb-6">
                    You can secure your endpoints using the <code>@auth</code> decorator found in <code>jec_api.decorators</code>.
                </p>

                <h3 className="text-xl font-medium text-foreground mb-3">Basic Usage</h3>
                <CodeBlock
                    filename="routes/secure.py"
                    language="python"
                    code={`from jec_api import Route
from jec_api.decorators import auth

class SecureData(Route):
    @auth(True)  # Requires authentication
    async def get(self):
        return {"data": "secure"}

    @auth(False) # Public endpoint
    async def post(self):
        return {"data": "public"}`}
                />

                <h3 className="text-xl font-medium text-foreground mb-3 mt-8">Role-Based Access Control (RBAC)</h3>
                <p className="text-muted-foreground leading-relaxed mb-4">
                    You can specify required roles. The auth handler receives these roles and can enforce them.
                </p>
                <CodeBlock
                    filename="routes/admin.py"
                    language="python"
                    code={`class AdminPanel(Route):
    @auth(True, roles=["admin", "superuser"])
    async def delete(self):
        return {"status": "deleted"}`}
                />
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Configuration Guide</h2>
                <p className="text-muted-foreground leading-relaxed mb-6">
                    The system is agnostic to the authentication method (JWT, OAuth, API Key, etc.). You provide the logic by registering an <strong>Auth Handler</strong>.
                </p>

                <h3 className="text-xl font-medium text-foreground mb-3">Setting up the Auth Handler</h3>
                <p className="text-muted-foreground leading-relaxed mb-4">
                    Register your handler using <code>app.set_auth_handler()</code>. The handler must be an <code>async</code> function that accepts <code>request</code> and <code>roles</code>.
                </p>
                <CodeBlock
                    filename="main.py"
                    language="python"
                    code={`from jec_api import Core
from fastapi import Request

app = Core()

async def my_auth(request: Request, roles: list[str] = None) -> bool:
    # 1. Check for token
    token = request.headers.get("Authorization")
    if token != "SecretToken":
        return False  # Deny access (403)
        
    return True # Allow access

app.set_auth_handler(my_auth)`}
                />

                <div className="mt-8 p-4 rounded-lg bg-card border border-border">
                    <p className="text-muted-foreground">
                        Need JWT integration, scope validation, or user context management? Check the <Link href="/docs/decorators/authentication/advanced" className="text-accent-blue hover:text-accent-blue/80 transition-colors">Advanced Usage</Link> guide.
                    </p>
                </div>
            </section>
        </article>
    );
}
