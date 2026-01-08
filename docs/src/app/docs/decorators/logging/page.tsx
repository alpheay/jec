import { CodeBlock } from "@/components/code-block";
import Link from "next/link";


export default function LoggingPage() {
    return (
        <article className="prose prose-invert max-w-none">
            <div className="not-prose mb-12">
                <h1 className="text-4xl font-bold tracking-tight text-foreground">
                    Request Logging
                </h1>
                <p className="mt-4 text-xl text-muted-foreground leading-relaxed">
                    The <code>@log</code> decorator provides automatic, comprehensive logging for your API endpoints.
                </p>
            </div>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">The @log Decorator</h2>
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

                <div className="mt-8 p-4 rounded-lg bg-card border border-border">
                    <p className="text-muted-foreground">
                        Need more control over log levels, truncation, or privacy? Check the <Link href="/docs/decorators/logging/advanced" className="text-accent-blue hover:text-accent-blue/80 transition-colors">Advanced Usage</Link> guide.
                    </p>
                </div>
            </section>
        </article>
    );
}
