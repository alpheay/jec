import { CodeBlock } from "@/components/code-block";

export default function DevToolsPage() {
    return (
        <article className="prose prose-invert max-w-none">
            <div className="not-prose mb-12">
                <h1 className="text-4xl font-bold tracking-tight text-foreground">
                    Developer Tools
                </h1>
                <p className="mt-4 text-xl text-muted-foreground leading-relaxed">
                    JEC includes a powerful, built-in Developer Console to inspect and debug your API in real-time.
                </p>
            </div>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Enabling the Console</h2>
                <p className="text-muted-foreground leading-relaxed mb-6">
                    Enable the tools by setting <code>dev=True</code> in your <code>tinker()</code> configuration.
                </p>
                <CodeBlock
                    language="python"
                    code={`app.tinker(
    dev=True,
    dev_path="/__dev__"  # Default path
)`}
                />
                <p className="mt-4 text-muted-foreground">
                    Once enabled, navigate to <code>http://localhost:8000/__dev__</code> to access the console.
                </p>
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Features</h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="p-6 rounded-lg bg-card border border-border">
                        <h3 className="text-lg font-bold text-foreground mb-2">Request Tracking</h3>
                        <p className="text-muted-foreground text-sm">
                            View a realtime timeline of all incoming requests, including their method, path, status code, and duration.
                        </p>
                    </div>

                    <div className="p-6 rounded-lg bg-card border border-border">
                        <h3 className="text-lg font-bold text-foreground mb-2">Log Inspection</h3>
                        <p className="text-muted-foreground text-sm">
                            See logs captured by the <code>@log</code> decorator directly associated with the specific request that generated them.
                        </p>
                    </div>

                    <div className="p-6 rounded-lg bg-card border border-border">
                        <h3 className="text-lg font-bold text-foreground mb-2">Endpoint Tester</h3>
                        <p className="text-muted-foreground text-sm">
                            A built-in HTTP client to send requests to your API, inspect usage, and verify behavior without leaving the console.
                        </p>
                    </div>

                    <div className="p-6 rounded-lg bg-card border border-border">
                        <h3 className="text-lg font-bold text-foreground mb-2">Performance Metrics</h3>
                        <p className="text-muted-foreground text-sm">
                            Visualize slow endpoints marked with <code>@speed</code> to identify bottlenecks in your application.
                        </p>
                    </div>
                </div>
            </section>
        </article>
    );
}
