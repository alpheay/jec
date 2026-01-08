
import { CodeBlock } from "@/components/code-block";

export default function VersioningPage() {
    return (
        <article className="prose prose-invert max-w-none">
            <div className="not-prose mb-12">
                <h1 className="text-4xl font-bold tracking-tight text-foreground">
                    API Versioning
                </h1>
                <p className="mt-4 text-xl text-muted-foreground leading-relaxed">
                    Enforces semantic versioning on endpoints based on the <code>X-API-Version</code> header using the <code>@version</code> decorator.
                </p>
            </div>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Constraint Syntax</h2>
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
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Strict Versioning</h2>
                <div className="p-4 rounded-lg bg-card border border-border">
                    <p className="text-sm text-muted-foreground">
                        If <code>strict_versioning=True</code> is set in <code>app.tinker()</code>, checking for the <code>X-API-Version</code> header becomes mandatory.
                        If the header is missing, the endpoint will return a <code>400 Bad Request</code> error.
                    </p>
                </div>
                <CodeBlock
                    language="python"
                    code={`# main.py
app.tinker(strict_versioning=True)`}
                />
            </section>
        </article>
    );
}
