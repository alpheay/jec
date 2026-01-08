
import { CodeBlock } from "@/components/code-block";

export default function AdvancedAuthenticationPage() {
    return (
        <article className="prose prose-invert max-w-none">
            <div className="not-prose mb-12">
                <h1 className="text-4xl font-bold tracking-tight text-foreground">
                    Advanced Authentication
                </h1>
                <p className="mt-4 text-xl text-muted-foreground leading-relaxed">
                    Integrate JWTs, manage complex scopes, and handle user context securely.
                </p>
            </div>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">JWT Validation & User Context</h2>
                <p className="text-muted-foreground leading-relaxed mb-4">
                    A common pattern is decoding a JWT, validating it, and attaching the user object to the request state.
                </p>
                <CodeBlock
                    language="python"
                    code={`import jwt
from fastapi import HTTPException

async def jwt_auth_handler(request: Request, roles: list[str] = None) -> bool:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return False
        
    token = auth_header.split(" ")[1]
    
    try:
        # Decode token
        payload = jwt.decode(token, "APP_SECRET", algorithms=["HS256"])
        
        # Attach user to request state for endpoint access
        request.state.user = payload
        
        # Role Check
        if roles:
            user_roles = payload.get("roles", [])
            has_permission = any(role in user_roles for role in roles)
            if not has_permission:
                raise HTTPException(status_code=403, detail="Insufficient Permissions")
                
        return True
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        return False # Invalid token`}
                />
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Accessing User Data</h2>
                <p className="text-muted-foreground leading-relaxed mb-4">
                    Data attached to <code>request.state</code> in the auth handler becomes available in your endpoints.
                </p>
                <CodeBlock
                    filename="routes/profile.py"
                    language="python"
                    code={`class UserProfile(Route):
    @auth(True)
    async def get(self, request: Request):
        # Access user data set by the auth handler
        user_id = request.state.user["id"]
        return {"id": user_id, "name": request.state.user["name"]}`}
                />
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Detailed Signature</h2>

                <div className="rounded-xl border border-border overflow-hidden bg-card/50 backdrop-blur-sm shadow-2xl shadow-black/20">
                    <CodeBlock
                        language="python"
                        className="border-none rounded-none shadow-none"
                        code={`def auth(
    enabled: bool = True, *, 
    roles: list[str] = None, 
    scopes: list[str] = None, 
    require_all: bool = False, 
    custom_error: str = None
)`}
                    />

                    <div className="p-6 border-t border-border bg-[#0f0f12]/30">
                        <ul className="space-y-3 text-sm text-muted-foreground list-none p-0 m-0">
                            <li><strong className="text-foreground font-mono">roles</strong>: List of required user roles (e.g., <code>["admin", "mod"]</code>).</li>
                            <li><strong className="text-foreground font-mono">scopes</strong>: List of required OAuth scopes (e.g., <code>["read:users"]</code>).</li>
                            <li><strong className="text-foreground font-mono">require_all</strong>: If <code>True</code>, user must have all listed roles/scopes. If <code>False</code>, any match grants access.</li>
                            <li><strong className="text-foreground font-mono">custom_error</strong>: Custom message for <code>403 Forbidden</code> responses.</li>
                        </ul>
                    </div>
                </div>
            </section>
        </article>
    );
}
