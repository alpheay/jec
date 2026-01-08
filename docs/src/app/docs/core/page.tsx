import { CodeBlock } from "@/components/code-block";

export default function CorePage() {
    return (
        <article className="prose prose-invert max-w-none">
            <div className="not-prose mb-12">
                <h1 className="text-4xl font-bold tracking-tight text-foreground">
                    Core Application
                </h1>
                <p className="mt-4 text-xl text-muted-foreground leading-relaxed">
                    The <code>Core</code> class is the heart of JEC, extending FastAPI with enhanced discovery and configuration capabilities.
                </p>
            </div>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Initialization</h2>
                <p className="text-muted-foreground leading-relaxed mb-6">
                    <code>Core</code> inherits directly from <code>FastAPI</code>, so it accepts all standard FastAPI arguments.
                </p>
                <CodeBlock
                    filename="main.py"
                    language="python"
                    code={`from jec_api import Core

app = Core(
    title="Production API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url=None
)`}
                />
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Configuration via <code>tinker()</code></h2>
                <p className="text-muted-foreground leading-relaxed mb-6">
                    The <code>tinker</code> method provides a unified interface for configuring both application settings and the underlying Uvicorn server server.
                </p>

                <h3 className="text-xl font-medium text-foreground mb-3">Dev Mode</h3>
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

                <h3 className="text-xl font-medium text-foreground mb-3 mt-8">Strict Versioning</h3>
                <p className="text-muted-foreground leading-relaxed mb-4">
                    Enforce the presence of the <code>X-API-Version</code> header on all versioned endpoints.
                </p>
                <CodeBlock
                    language="python"
                    code={`app.tinker(strict_versioning=True)`}
                />

                <h3 className="text-xl font-medium text-foreground mb-3 mt-8">Server Settings</h3>
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

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Route Registration</h2>
                <p className="text-muted-foreground leading-relaxed mb-6">
                    JEC offers two ways to register routes: manual registration and auto-discovery.
                </p>

                <h3 className="text-xl font-medium text-foreground mb-3">Manual Registration</h3>
                <CodeBlock
                    language="python"
                    code={`from routes.users import UserRoute

app.register(UserRoute, tags=["Users"])`}
                />

                <h3 className="text-xl font-medium text-foreground mb-3 mt-6">Auto Discovery</h3>
                <p className="text-muted-foreground leading-relaxed mb-4">
                    Automatically find and register all <code>Route</code> subclasses in a package.
                </p>
                <CodeBlock
                    language="python"
                    code={`# Discover all routes in the "routes" package
app.discover("routes", recursive=True)`}
                />
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Running the App</h2>
                <p className="text-muted-foreground leading-relaxed mb-6">
                    Use the <code>run()</code> method to start the server with your configured settings.
                </p>
                <CodeBlock
                    language="python"
                    code={`if __name__ == "__main__":
    app.run()`}
                />
            </section>
        </article>
    );
}
