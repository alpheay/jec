
import { CodeBlock } from "@/components/code-block";

export default function AdvancedSpeedPage() {
    return (
        <article className="prose prose-invert max-w-none">
            <div className="not-prose mb-12">
                <h1 className="text-4xl font-bold tracking-tight text-foreground">
                    Advanced Speed Monitoring
                </h1>
                <p className="mt-4 text-xl text-muted-foreground leading-relaxed">
                    Set SLAs, configure alert thresholds, and expose performance metrics to clients.
                </p>
            </div>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">SLA Monitoring</h2>
                <p className="text-muted-foreground leading-relaxed mb-4">
                    Configure warning and error thresholds to automatically log when execution times exceed your Service Level Agreements.
                </p>

                <CodeBlock
                    filename="routes/critical.py"
                    language="python"
                    code={`# SLA Monitoring
# Warns if > 100ms, Errors if > 500ms
@speed(warn_threshold_ms=100, error_threshold_ms=500)
async def critical_path(): ...`}
                />
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Client Transparency</h2>
                <p className="text-muted-foreground leading-relaxed mb-4">
                    Automatically add an <code>X-Response-Time</code> header to the HTTP response to let clients know how long the request took to process.
                </p>

                <CodeBlock
                    filename="routes/public.py"
                    language="python"
                    code={`# Client Transparency
# Returns header: X-Response-Time: 12.5ms
@speed(include_in_response=True)
async def public_api(): ...`}
                />
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Detailed Signature</h2>

                <div className="rounded-xl border border-border overflow-hidden bg-card/50 backdrop-blur-sm shadow-2xl shadow-black/20">
                    <CodeBlock
                        language="python"
                        className="border-none rounded-none shadow-none"
                        code={`def speed(
    func=None, *, 
    warn_threshold_ms: float = None, 
    error_threshold_ms: float = None, 
    include_in_response: bool = False
)`}
                    />

                    <div className="p-6 border-t border-border bg-[#0f0f12]/30">
                        <ul className="space-y-3 text-sm text-muted-foreground list-none p-0 m-0">
                            <li><strong className="text-foreground font-mono">warn_threshold_ms</strong>: Log a warning if execution time exceeds this value (ms).</li>
                            <li><strong className="text-foreground font-mono">error_threshold_ms</strong>: Log an error if execution time exceeds this value (ms).</li>
                            <li><strong className="text-foreground font-mono">include_in_response</strong>: If <code>True</code>, adds <code>X-Response-Time</code> header to the HTTP response.</li>
                        </ul>
                    </div>
                </div>
            </section>
        </article>
    );
}
