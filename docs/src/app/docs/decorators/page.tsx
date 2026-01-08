import { CodeBlock } from "@/components/code-block";

export default function DecoratorsPage() {
    return (
        <article className="prose prose-invert max-w-none">
            <div className="not-prose mb-12">
                <h1 className="text-4xl font-bold tracking-tight text-foreground">
                    Decorators
                </h1>
                <p className="mt-4 text-xl text-muted-foreground leading-relaxed">
                    Enhance your endpoints with built-in logging, performance monitoring, and versioning capabilities.
                </p>
            </div>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">@log</h2>
                <p className="text-muted-foreground leading-relaxed mb-6">
                    Logs the complete lifecycle of a request, including arguments on entry and return values (or exceptions) on exit.
                </p>
                <CodeBlock
                    filename="routes/users.py"
                    language="python"
                    code={`from jec_api.decorators import log

class Users(Route):
    @log
    async def get(self, user_id: int):
        # Logs: [CALL] Users.get | args=(user_id=1,)
        # ... processing ...
        # Logs: [RETURN] Users.get | result={...}
        return db.get_user(user_id)`}
                />
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">@speed</h2>
                <p className="text-muted-foreground leading-relaxed mb-6">
                    Measures the execution time of an endpoint and logs it. Useful for identifying slow operations.
                </p>
                <CodeBlock
                    filename="routes/data.py"
                    language="python"
                    code={`from jec_api.decorators import speed

class HeavyProcess(Route):
    @speed
    async def post(self):
        await costly_operation()
        # Logs: [SPEED] HeavyProcess.post | 145.23ms
        return {"status": "done"}`}
                />
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">@version</h2>
                <p className="text-muted-foreground leading-relaxed mb-6">
                    Enforces semantic versioning on endpoints based on the <code>X-API-Version</code> header.
                </p>

                <h3 className="text-xl font-medium text-foreground mb-3">Constraint Syntax</h3>
                <p className="text-muted-foreground leading-relaxed mb-4">
                    Supports standard comparison operators: <code>{`>=, <=, >, <, ==, !=`}</code>.
                </p>

                <CodeBlock
                    filename="routes/api.py"
                    language="python"
                    code={`from jec_api.decorators import version

class Api(Route):
    # Available for version 1.0.0 and above
    @version(">=1.0.0")
    async def get(self):
        return {"v": 1}
        
    # Replaced in version 2.0.0
    @version("<2.0.0")
    async def post(self):
        return "Legacy Endpoint"`}
                />

                <div className="mt-6 p-4 rounded-lg bg-card border border-border">
                    <h4 className="text-lg font-medium text-foreground mb-2">Strict Versioning</h4>
                    <p className="text-sm text-muted-foreground">
                        If <code>strict_versioning=True</code> is set in <code>app.tinker()</code>, checking for the <code>X-API-Version</code> header becomes mandatory.
                        If the header is missing, the endpoint will return a <code>400 Bad Request</code> error.
                    </p>
                </div>
            </section>
        </article>
    );
}
