
import { CodeBlock } from "@/components/code-block";

export default function ConfigurationPage() {
    return (
        <article className="prose prose-invert max-w-none">
            <div className="not-prose mb-12">
                <h1 className="text-4xl font-bold tracking-tight text-foreground">
                    Application Configuration
                </h1>
                <p className="mt-4 text-xl text-muted-foreground leading-relaxed">
                    The <code>tinker</code> method provides a unified interface for configuring both application settings and the underlying Uvicorn server.
                </p>
            </div>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Developer Tools</h2>
                <p className="text-muted-foreground leading-relaxed mb-4">
                    Enable the developer console to inspect requests, performance, and logs in real-time.
                </p>
                <CodeBlock
                    language="python"
                    code={`app.tinker(
    dev=True,           # Enable Dev Console
    dev_path="/__dev__" # Custom path (default: /__dev__)
)`}
                />
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Strict Versioning</h2>
                <p className="text-muted-foreground leading-relaxed mb-4">
                    Enforce the presence of the <code>X-API-Version</code> header on all versioned endpoints.
                </p>
                <CodeBlock
                    language="python"
                    code={`app.tinker(strict_versioning=True)`}
                />
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Server Settings</h2>
                <p className="text-muted-foreground leading-relaxed mb-4">
                    Pass any additional keyword arguments to configure Uvicorn directly.
                </p>
                <CodeBlock
                    language="python"
                    code={`app.tinker(
    host="0.0.0.0",
    port=8080,
    workers=4,
    loop="uvloop"
)`}
                />
            </section>
        </article>
    );
}
