
import { CodeBlock } from "@/components/code-block";

export default function RateLimitPage() {
    return (
        <article className="prose prose-invert max-w-none">
            <div className="not-prose mb-12">
                <h1 className="text-4xl font-bold tracking-tight text-foreground">
                    Rate Limit Decorator
                </h1>
                <p className="mt-4 text-xl text-muted-foreground leading-relaxed">
                    Protect your API from abuse by limiting request frequency.
                </p>
            </div>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Usage</h2>
                <p className="text-muted-foreground leading-relaxed mb-4">
                    The <code>@ratelimit</code> decorator enforces limits based on IP address, User ID, or globally.
                </p>

                <CodeBlock
                    filename="routes/expensive.py"
                    language="python"
                    code={`from jec_api.decorators import ratelimit

# 10 requests per minute per user ID
@ratelimit(limit=10, window=60, by="user")
async def expensive_query():
    ...`}
                />

                <h3 className="text-xl font-medium text-foreground mb-3 mt-6">Side Effects</h3>
                <ul className="list-disc pl-6 space-y-2 text-muted-foreground">
                    <li>Returns <code>429 Too Many Requests</code> when exceeded.</li>
                    <li>Adds headers: <code>X-RateLimit-Limit</code>, <code>X-RateLimit-Remaining</code>, <code>X-RateLimit-Reset</code>.</li>
                </ul>
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Signature</h2>

                <div className="rounded-xl border border-border overflow-hidden bg-card/50 backdrop-blur-sm shadow-2xl shadow-black/20">
                    <CodeBlock
                        language="python"
                        className="border-none rounded-none shadow-none"
                        code={`def ratelimit(
    limit: int = 100, 
    window: int = 60, 
    by: str = "ip", 
    message: str = None
)`}
                    />

                    <div className="p-6 border-t border-border bg-[#0f0f12]/30">
                        <ul className="space-y-3 text-sm text-muted-foreground list-none p-0 m-0">
                            <li><strong className="text-foreground font-mono">limit</strong>: Max requests allowed in window.</li>
                            <li><strong className="text-foreground font-mono">window</strong>: Time window in seconds.</li>
                            <li><strong className="text-foreground font-mono">by</strong>: Keying strategy: <code>"ip"</code> (client IP), <code>"user"</code> (auth user ID), or <code>"global"</code> (shared).</li>
                            <li><strong className="text-foreground font-mono">message</strong>: Custom error message for rate limit exceeded responses.</li>
                        </ul>
                    </div>
                </div>
            </section>
        </article>
    );
}
