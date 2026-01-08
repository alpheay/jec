
import { CodeBlock } from "@/components/code-block";

export default function AdvancedVersioningPage() {
    return (
        <article className="prose prose-invert max-w-none">
            <div className="not-prose mb-12">
                <h1 className="text-4xl font-bold tracking-tight text-foreground">
                    Advanced Versioning
                </h1>
                <p className="mt-4 text-xl text-muted-foreground leading-relaxed">
                    Manage API lifecycles with strict enforcement, deprecation notices, and sunset headers. This works as a more nuanced version of the <code>@deprecated</code> decorator.
                </p>
            </div>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Deprecation & Sunset</h2>
                <p className="text-muted-foreground leading-relaxed mb-4">
                    Gracefully phase out old endpoints by adding <code>Deprecation</code> and <code>Sunset</code> headers to the response.
                </p>

                <CodeBlock
                    filename="routes/legacy.py"
                    language="python"
                    code={`# Deprecated Version
# Headers: Deprecation: true, Sunset: 2025-12-31
@version("<=1.0.0", deprecated=True, sunset="2025-12-31", message="Please upgrade to v2")
async def legacy_endpoint(): ...`}
                />
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Strict Versioning Enforcement</h2>
                <p className="text-muted-foreground leading-relaxed mb-4">
                    By default, version checks are permissive. You can force clients to send the <code>X-API-Version</code> header.
                </p>

                <div className="p-4 rounded-lg bg-card border border-border mb-4">
                    <p className="text-sm text-muted-foreground">
                        If <code>strict_versioning=True</code> is set in <code>app.tinker()</code>, the endpoint will return a <code>400 Bad Request</code> error if the header is missing.
                    </p>
                </div>

                <CodeBlock
                    language="python"
                    code={`# main.py
app.tinker(strict_versioning=True)`}
                />
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Detailed Signature</h2>

                <div className="rounded-xl border border-border overflow-hidden bg-card/50 backdrop-blur-sm shadow-2xl shadow-black/20">
                    <CodeBlock
                        filename="jec/internal/version.py"
                        language="python"
                        className="border-none rounded-none shadow-none"
                        code={`def version(
    constraint: str, *, 
    deprecated: bool = False, 
    sunset: str = None, 
    message: str = None
)`}
                    />

                    <div className="p-6 border-t border-border bg-[#0f0f12]/30">
                        <ul className="space-y-3 text-sm text-muted-foreground list-none p-0 m-0">
                            <li><strong className="text-foreground font-mono">constraint</strong>: Comparison string (e.g., <code>"&gt;=1.0.0"</code>).</li>
                            <li><strong className="text-foreground font-mono">deprecated</strong>: If <code>True</code>, adds <code>Deprecation: true</code> header.</li>
                            <li><strong className="text-foreground font-mono">sunset</strong>: ISO 8601 date string for endpoint removal (adds <code>Sunset</code> header).</li>
                            <li><strong className="text-foreground font-mono">message</strong>: Custom error message or deprecation notice.</li>
                        </ul>
                    </div>
                </div>
            </section>
        </article>
    );
}
