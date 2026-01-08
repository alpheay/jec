import { CodeBlock } from "@/components/code-block";
import Link from "next/link";


export default function DecoratorsPage() {
    return (
        <article className="prose prose-invert max-w-none">
            <div className="not-prose mb-12">
                <h1 className="text-4xl font-bold tracking-tight text-foreground">
                    Decorators
                </h1>
                <p className="mt-4 text-xl text-muted-foreground leading-relaxed">
                    JEC provides a suite of powerful decorators to enhance your endpoints with cross-cutting concerns like logging, timing, authentication, and versioning.
                </p>
            </div>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Why Decorators?</h2>
                <p className="text-muted-foreground leading-relaxed mb-6">
                    Decorators allow you to wrap your route methods with additional functionality without cluttering the business logic.
                    In JEC, decorators are designed to work seamlessly with class-based routes.
                </p>

                <div className="grid gap-4 md:grid-cols-2">
                    <Link
                        href="/docs/decorators/logging"
                        className="block p-6 rounded-lg border border-border bg-card hover:border-accent-blue/50 transition-colors group"
                    >
                        <h3 className="text-lg font-medium text-foreground mb-2 group-hover:text-accent-blue transition-colors">
                            @log
                        </h3>
                        <p className="text-sm text-muted-foreground">
                            Automatic request/response logging for debugging and auditing.
                        </p>
                    </Link>

                    <Link
                        href="/docs/decorators/speed"
                        className="block p-6 rounded-lg border border-border bg-card hover:border-accent-blue/50 transition-colors group"
                    >
                        <h3 className="text-lg font-medium text-foreground mb-2 group-hover:text-accent-blue transition-colors">
                            @speed
                        </h3>
                        <p className="text-sm text-muted-foreground">
                            Performance monitoring and execution time tracking.
                        </p>
                    </Link>

                    <Link
                        href="/docs/decorators/authentication"
                        className="block p-6 rounded-lg border border-border bg-card hover:border-accent-blue/50 transition-colors group"
                    >
                        <h3 className="text-lg font-medium text-foreground mb-2 group-hover:text-accent-blue transition-colors">
                            @auth
                        </h3>
                        <p className="text-sm text-muted-foreground">
                            Role-based access control and request authentication.
                        </p>
                    </Link>

                    <Link
                        href="/docs/decorators/versioning"
                        className="block p-6 rounded-lg border border-border bg-card hover:border-accent-blue/50 transition-colors group"
                    >
                        <h3 className="text-lg font-medium text-foreground mb-2 group-hover:text-accent-blue transition-colors">
                            @version
                        </h3>
                        <p className="text-sm text-muted-foreground">
                            Semantic versioning enforcement for evolving APIs.
                        </p>
                    </Link>

                    <Link
                        href="/docs/decorators/deprecated"
                        className="block p-6 rounded-lg border border-border bg-card hover:border-accent-blue/50 transition-colors group"
                    >
                        <h3 className="text-lg font-medium text-foreground mb-2 group-hover:text-accent-blue transition-colors">
                            @deprecated
                        </h3>
                        <p className="text-sm text-muted-foreground">
                            Mark endpoints for deprecation with sunset dates and alternatives.
                        </p>
                    </Link>

                    <Link
                        href="/docs/decorators/ratelimit"
                        className="block p-6 rounded-lg border border-border bg-card hover:border-accent-blue/50 transition-colors group"
                    >
                        <h3 className="text-lg font-medium text-foreground mb-2 group-hover:text-accent-blue transition-colors">
                            @ratelimit
                        </h3>
                        <p className="text-sm text-muted-foreground">
                            Prevent abuse by limiting request frequency.
                        </p>
                    </Link>

                    <Link
                        href="/docs/decorators/timeout"
                        className="block p-6 rounded-lg border border-border bg-card hover:border-accent-blue/50 transition-colors group"
                    >
                        <h3 className="text-lg font-medium text-foreground mb-2 group-hover:text-accent-blue transition-colors">
                            @timeout
                        </h3>
                        <p className="text-sm text-muted-foreground">
                            Enforce execution time limits and cancel slow tasks.
                        </p>
                    </Link>

                    <Link
                        href="/docs/decorators/retry"
                        className="block p-6 rounded-lg border border-border bg-card hover:border-accent-blue/50 transition-colors group"
                    >
                        <h3 className="text-lg font-medium text-foreground mb-2 group-hover:text-accent-blue transition-colors">
                            @retry
                        </h3>
                        <p className="text-sm text-muted-foreground">
                            Improve resilience with automatic retries and backoff.
                        </p>
                    </Link>
                </div>
            </section>
        </article>
    );
}