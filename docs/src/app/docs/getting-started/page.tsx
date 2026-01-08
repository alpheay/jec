import { CodeBlock } from "@/components/code-block";

export default function GettingStartedPage() {
    return (
        <article className="prose prose-invert max-w-none">
            <div className="not-prose mb-12">
                <h1 className="text-4xl font-bold tracking-tight text-foreground">
                    Getting Started
                </h1>
                <p className="mt-4 text-xl text-muted-foreground leading-relaxed">
                    Setup your first JEC API project in minutes with our modern, class-based FastAPI wrapper.
                </p>
            </div>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Installation</h2>
                <p className="text-muted-foreground leading-relaxed mb-6">
                    Install the package using your preferred package manager.
                </p>
                <CodeBlock
                    language="bash"
                    code="pip install jec-api"
                />
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Quick Start</h2>
                <p className="text-muted-foreground leading-relaxed mb-6">
                    Create a minimal application by initializing the <code>Core</code> class and registering a simple route.
                </p>

                <CodeBlock
                    filename="main.py"
                    language="python"
                    code={`from jec_api import Core, Route

# 1. Define your route
class Hello(Route):
    async def get(self):
        return {"message": "Hello from JEC!"}

# 2. Initialize the app
app = Core(
    title="My First JEC App",
    description="A simple API using JEC Framework"
)

# 3. Register routes
app.register(Hello)

# 4. Run the server
if __name__ == "__main__":
    app.run()`}
                />

                <div className="mt-6 p-4 rounded-lg bg-card border border-border">
                    <p className="text-sm text-muted-foreground">
                        <strong className="text-accent-blue">Note:</strong> By default, the route path is derived from the class name.
                        <code>Hello</code> becomes <code>/hello</code>. You can override this by setting the <code>path</code> attribute on the class.
                    </p>
                </div>
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Project Structure</h2>
                <p className="text-muted-foreground leading-relaxed mb-6">
                    We recommend the following structure for larger applications:
                </p>

                <CodeBlock
                    language="bash"
                    code={`my_project/
├── main.py              # Application entry point
├── routes/              # Route definitions
│   ├── __init__.py
│   ├── users.py
│   └── items.py
└── requirements.txt`}
                />
            </section>
        </article>
    );
}
