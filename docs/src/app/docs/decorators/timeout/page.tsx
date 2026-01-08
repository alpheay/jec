
import { CodeBlock } from "@/components/code-block";

export default function TimeoutPage() {
    return (
        <article className="prose prose-invert max-w-none">
            <div className="not-prose mb-12">
                <h1 className="text-4xl font-bold tracking-tight text-foreground">
                    Timeout Decorator
                </h1>
                <p className="mt-4 text-xl text-muted-foreground leading-relaxed">
                    Enforce strict time limits on request processing to prevent hanging connections.
                </p>
            </div>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Usage</h2>
                <p className="text-muted-foreground leading-relaxed mb-4">
                    The <code>@timeout</code> decorator cancels the underlying task if it takes too long.
                </p>

                <CodeBlock
                    filename="routes/search.py"
                    language="python"
                    code={`from jec_api.decorators import timeout

# Fails if not completed in 500ms
@timeout(seconds=0.5)
async def quick_search():
    ...`}
                />

                <h3 className="text-xl font-medium text-foreground mb-3 mt-6">Side Effects</h3>
                <ul className="list-disc pl-6 space-y-2 text-muted-foreground">
                    <li>Raises <code>504 Gateway Timeout</code> if execution exceeds limit.</li>
                    <li>Cancels the underlying asyncio task.</li>
                </ul>
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Signature</h2>

                <div className="rounded-xl border border-border overflow-hidden bg-card/50 backdrop-blur-sm shadow-2xl shadow-black/20">
                    <CodeBlock
                        language="python"
                        className="border-none rounded-none shadow-none"
                        code={`def timeout(seconds: float = 30.0, message: str = None)`}
                    />

                    <div className="p-6 border-t border-border bg-[#0f0f12]/30">
                        <ul className="space-y-3 text-sm text-muted-foreground list-none p-0 m-0">
                            <li><strong className="text-foreground font-mono">seconds</strong>: Maximum execution time before timeout. Default: <code>30.0</code>.</li>
                            <li><strong className="text-foreground font-mono">message</strong>: Custom error message for timeout responses.</li>
                        </ul>
                    </div>
                </div>
            </section>
        </article>
    );
}
