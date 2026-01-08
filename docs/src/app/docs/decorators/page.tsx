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
                <h2 className="text-2xl font-semibold text-foreground mb-4">Advanced Decorators</h2>
                <div className="grid gap-4 md:grid-cols-2">
                    <a
                        href="/docs/decorators/versioning"
                        className="block p-6 rounded-lg border border-border bg-card hover:border-accent-blue/50 transition-colors group"
                    >
                        <h3 className="text-lg font-medium text-foreground mb-2 group-hover:text-accent-blue transition-colors">
                            @version
                        </h3>
                        <p className="text-sm text-muted-foreground">
                            Enforce semantic versioning on endpoints with flexible constraints.
                        </p>
                    </a>

                    <a
                        href="/docs/decorators/authentication"
                        className="block p-6 rounded-lg border border-border bg-card hover:border-accent-blue/50 transition-colors group"
                    >
                        <h3 className="text-lg font-medium text-foreground mb-2 group-hover:text-accent-blue transition-colors">
                            @auth
                        </h3>
                        <p className="text-sm text-muted-foreground">
                            Secure your endpoints with role-based access control and custom authentication logic.
                        </p>
                    </a>
                </div>
            </section>
        </article>
    );
}
