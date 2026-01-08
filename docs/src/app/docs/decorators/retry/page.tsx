
import { CodeBlock } from "@/components/code-block";

export default function RetryPage() {
    return (
        <article className="prose prose-invert max-w-none">
            <div className="not-prose mb-12">
                <h1 className="text-4xl font-bold tracking-tight text-foreground">
                    Retry Decorator
                </h1>
                <p className="mt-4 text-xl text-muted-foreground leading-relaxed">
                    Automatically retry operations that fail due to transient errors.
                </p>
            </div>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Usage</h2>
                <p className="text-muted-foreground leading-relaxed mb-4">
                    The <code>@retry</code> decorator handles exponential backoff and specific exception targeting.
                </p>

                <CodeBlock
                    filename="routes/upstream.py"
                    language="python"
                    code={`from jec_api.decorators import retry

# Retry 3 times, catching only ConnectionError, doubling wait time (1s, 2s, 4s)
@retry(attempts=3, delay=1.0, backoff=2.0, exceptions=(ConnectionError,))
async def flaky_upstream_call():
    ...`}
                />
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Signature</h2>

                <div className="rounded-xl border border-border overflow-hidden bg-card/50 backdrop-blur-sm shadow-2xl shadow-black/20">
                    <CodeBlock
                        language="python"
                        className="border-none rounded-none shadow-none"
                        code={`def retry(
    attempts: int = 3, 
    delay: float = 1.0, 
    backoff: float = 2.0, 
    exceptions: tuple = (Exception,)
)`}
                    />

                    <div className="p-6 border-t border-border bg-[#0f0f12]/30">
                        <ul className="space-y-3 text-sm text-muted-foreground list-none p-0 m-0">
                            <li><strong className="text-foreground font-mono">attempts</strong>: Total attempts (1 initial + retries).</li>
                            <li><strong className="text-foreground font-mono">delay</strong>: Initial wait time between retries (seconds).</li>
                            <li><strong className="text-foreground font-mono">backoff</strong>: Multiplier for delay after each failure.</li>
                            <li><strong className="text-foreground font-mono">exceptions</strong>: Tuple of Exception classes to catch.</li>
                        </ul>
                    </div>
                </div>
            </section>
        </article>
    );
}
