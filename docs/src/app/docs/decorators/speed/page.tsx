import { CodeBlock } from "@/components/code-block";

export default function SpeedPage() {
    return (
        <article className="prose prose-invert max-w-none">
            <div className="not-prose mb-12">
                <h1 className="text-4xl font-bold tracking-tight text-foreground">
                    Performance Monitoring
                </h1>
                <p className="mt-4 text-xl text-muted-foreground leading-relaxed">
                    The <code>@speed</code> decorator helps you identify bottlenecks by measuring execution time.
                </p>
            </div>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">The @speed Decorator</h2>
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

                <div className="mt-8 p-4 rounded-lg bg-card border border-border">
                    <p className="text-muted-foreground">
                        Need SLAs, error thresholds, or public response headers? Check the <a href="/docs/decorators/speed/advanced" className="text-accent-blue hover:text-accent-blue/80 transition-colors">Advanced Usage</a> guide.
                    </p>
                </div>
            </section>
        </article>
    );
}
