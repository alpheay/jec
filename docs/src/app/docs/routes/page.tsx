import { CodeBlock } from "@/components/code-block";

export default function RoutesPage() {
    return (
        <article className="prose prose-invert max-w-none">
            <div className="not-prose mb-12">
                <h1 className="text-4xl font-bold tracking-tight text-foreground">
                    Routing System
                </h1>
                <p className="mt-4 text-xl text-muted-foreground leading-relaxed">
                    JEC uses a class-based routing system that intuitively maps Python methods to HTTP endpoints.
                </p>
            </div>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">The Route Class</h2>
                <p className="text-muted-foreground leading-relaxed mb-6">
                    Every route in your application must inherit from `Route`. This base class handles the magic of converting your methods into FastAPI endpoints.
                </p>
                <CodeBlock
                    language="python"
                    code={`from jec_api import Route

class MyRoute(Route):
    ...`}
                />
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Defining Endpoints</h2>
                <p className="text-muted-foreground leading-relaxed mb-6">
                    Define endpoints by naming your class methods after HTTP verbs (`get`, `post`, `put`, `delete`, `patch`).
                </p>
                <CodeBlock
                    filename="routes/items.py"
                    language="python"
                    code={`class Items(Route):
    # GET /items
    async def get(self):
        return {"items": []}

    # POST /items
    async def post(self, item: dict):
        return {"created": item}
        
    # DELETE /items
    async def delete(self):
        return {"deleted": True}`}
                />

                <div className="mt-6 p-4 rounded-lg bg-card border border-border">
                    <p className="text-sm text-muted-foreground">
                        <strong className="text-accent-yellow">Important:</strong> Only exact method names are mapped. Methods like `get_items` or `post_v2` are ignored and treated as internal helpers.
                    </p>
                </div>
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Path Configuration</h2>

                <h3 className="text-xl font-medium text-foreground mb-3">Automatic Path Generation</h3>
                <p className="text-muted-foreground leading-relaxed mb-4">
                    By default, the path is derived from the class name using kebab-case.
                </p>
                <ul className="list-none space-y-2 mb-6 text-muted-foreground ml-4">
                    <li><code>UserProfiles</code> → <code>/user-profiles</code></li>
                    <li><code>APIStatus</code> → <code>/api-status</code></li>
                    <li><code>Home</code> → <code>/home</code></li>
                </ul>

                <h3 className="text-xl font-medium text-foreground mb-3">Custom Paths</h3>
                <p className="text-muted-foreground leading-relaxed mb-4">
                    Override the path by setting the <code>path</code> class attribute.
                </p>
                <CodeBlock
                    language="python"
                    code={`class UserProfile(Route):
    path = "/users/me/profile"  # Custom path
    
    async def get(self):
        ...`}
                />
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Request & Response Types</h2>
                <p className="text-muted-foreground leading-relaxed mb-6">
                    JEC uses Pydantic models for robust validation and serialization.
                </p>
                <div className="flex">
                    <a
                        href="/docs/routes/types"
                        className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-accent-blue/10 text-accent-blue font-medium hover:bg-accent-blue/20 transition-colors"
                    >
                        Learn about Types
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                    </a>
                </div>
            </section>
        </article>
    );
}
