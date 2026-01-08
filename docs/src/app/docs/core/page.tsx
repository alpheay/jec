import { CodeBlock } from "@/components/code-block";
import Link from "next/link";


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
                <h2 className="text-2xl font-semibold text-foreground mb-4">Configuration</h2>
                <p className="text-muted-foreground leading-relaxed mb-6">
                    Configure your application settings, developer tools, and underlying server options.
                </p>

                <div className="flex">
                    <Link
                        href="/docs/core/configuration"
                        className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-accent-blue/10 text-accent-blue font-medium hover:bg-accent-blue/20 transition-colors"
                    >
                        View Configuration Guide
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                    </Link>
                </div>
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
        </article >
    );
}
