
import { CodeBlock } from "@/components/code-block";

export default function DeprecatedPage() {
    return (
        <article className="prose prose-invert max-w-none">
            <div className="not-prose mb-12">
                <h1 className="text-4xl font-bold tracking-tight text-foreground">
                    Deprecated Decorator
                </h1>
                <p className="mt-4 text-xl text-muted-foreground leading-relaxed">
                    Explicitly mark endpoints as deprecated to signal upcoming removal to clients.
                </p>
            </div>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Usage</h2>
                <p className="text-muted-foreground leading-relaxed mb-4">
                    The <code>@deprecated</code> decorator adds standard headers to inform clients about the deprecation status and alternative endpoints.
                </p>

                <CodeBlock
                    filename="routes/legacy.py"
                    language="python"
                    code={`from jec_api.decorators import deprecated

@deprecated("Use /v2/users instead", alternative="/v2/users", sunset="2025-06-01")
async def get_users_old():
    ...`}
                />

                <h3 className="text-xl font-medium text-foreground mb-3 mt-6">Side Effects</h3>
                <ul className="list-disc pl-6 space-y-2 text-muted-foreground">
                    <li>Adds <code>Deprecation: true</code> header.</li>
                    <li>Adds <code>Sunset: &lt;date&gt;</code> header if provided.</li>
                    <li>Adds <code>X-Deprecation-Alternative: &lt;path&gt;</code> header if provided.</li>
                </ul>
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Signature</h2>

                <div className="rounded-xl border border-border overflow-hidden bg-card/50 backdrop-blur-sm shadow-2xl shadow-black/20">
                    <CodeBlock
                        language="python"
                        className="border-none rounded-none shadow-none"
                        code={`def deprecated(
    message=None, *, 
    alternative: str = None, 
    sunset: str = None
)`}
                    />

                    <div className="p-6 border-t border-border bg-[#0f0f12]/30">
                        <ul className="space-y-3 text-sm text-muted-foreground list-none p-0 m-0">
                            <li><strong className="text-foreground font-mono">message</strong>: Human-readable deprecation notice for clients.</li>
                            <li><strong className="text-foreground font-mono">alternative</strong>: Path or URL to the replacement endpoint.</li>
                            <li><strong className="text-foreground font-mono">sunset</strong>: ISO 8601 date string indicating when the endpoint will be removed.</li>
                        </ul>
                    </div>
                </div>
            </section>
        </article>
    );
}
