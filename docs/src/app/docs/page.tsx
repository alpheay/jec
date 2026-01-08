import Link from "next/link";
import { ArrowRight, BookOpen, Zap, Code2 } from "lucide-react";
import { CodeBlock } from "@/components/code-block";

export default function DocsIntroduction() {
    return (
        <article className="prose prose-invert max-w-none">
            {/* Header */}
            <div className="not-prose mb-12">
                <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
                    <BookOpen className="w-4 h-4" />
                    <span>Introduction</span>
                </div>
                <h1 className="text-4xl font-bold tracking-tight text-foreground">
                    Welcome to JEC API
                </h1>
                <p className="mt-4 text-xl text-muted-foreground leading-relaxed">
                    Just Encapsulated Controllers — the class-based system for building modern,
                    clean, and maintainable Application Program Interfaces in Python.
                </p>
            </div>

            {/* What is JEC */}
            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">What is JEC?</h2>
                <p className="text-muted-foreground leading-relaxed mb-6">
                    JEC is a lightweight framework built on top of FastAPI that brings class-based
                    routing to your Python APIs. Instead of scattering route definitions across
                    decorator functions, JEC lets you organize your endpoints into clean,
                    logical controller classes.
                </p>

                <div className="grid gap-4 sm:grid-cols-3 not-prose">
                    {[
                        {
                            icon: Code2,
                            title: "Clean Architecture",
                            description: "Organize endpoints into intuitive class structures",
                            color: "text-accent-blue",
                            bgColor: "bg-accent-blue/10",
                        },
                        {
                            icon: Zap,
                            title: "Powerful Decorators",
                            description: "Add logging, speed checks, and versioning easily",
                            color: "text-accent-yellow",
                            bgColor: "bg-accent-yellow/10",
                        },
                        {
                            icon: BookOpen,
                            title: "Zero Config",
                            description: "Convention over configuration for rapid development",
                            color: "text-accent-green",
                            bgColor: "bg-accent-green/10",
                        },
                    ].map((feature) => (
                        <div
                            key={feature.title}
                            className="rounded-lg border border-border bg-card p-4"
                        >
                            <div className={`inline-flex rounded-md p-2 ${feature.bgColor}`}>
                                <feature.icon className={`h-4 w-4 ${feature.color}`} />
                            </div>
                            <h3 className="mt-3 font-medium text-foreground text-sm">
                                {feature.title}
                            </h3>
                            <p className="mt-1 text-xs text-muted-foreground">
                                {feature.description}
                            </p>
                        </div>
                    ))}
                </div>
            </section>

            {/* The Name */}
            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">About the Name</h2>
                <p className="text-muted-foreground leading-relaxed mb-4">
                    JEC can stand for many things, depending on your mood:
                </p>
                <ul className="space-y-2 not-prose">
                    {[
                        { name: "Just Encapsulated Controllers", desc: "The official meaning — class-based API organization" },
                        { name: "Jolly Enough Curses", desc: "For when debugging at 3am feels magical" },
                        { name: "Jupiter Eats Comets", desc: "Because your APIs should be astronomical" },
                    ].map((item) => (
                        <li key={item.name} className="flex items-start gap-3">
                            <span className="mt-2 h-1.5 w-1.5 rounded-full bg-accent-violet shrink-0"></span>
                            <div>
                                <span className="font-medium text-foreground">{item.name}</span>
                                <span className="text-muted-foreground"> — {item.desc}</span>
                            </div>
                        </li>
                    ))}
                </ul>
            </section>

            {/* Quick Example */}
            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Quick Example</h2>
                <p className="text-muted-foreground leading-relaxed mb-6">
                    Here&apos;s what a JEC route looks like. Notice how each HTTP method is simply
                    a method on the class:
                </p>

                <div className="not-prose">
                    <CodeBlock
                        filename="routes/users.py"
                        language="python"
                        code={`from jec import Route
from jec.decorators import log, speed, version

class UsersRoute(Route):
    """Handles all /users endpoints."""
    
    @log
    @speed
    async def get(self):
        """GET /users - List all users"""
        return {"users": await self.db.get_users()}
    
    @log
    @version(">=1.0.0")
    async def post(self, user: UserCreate):
        """POST /users - Create a new user"""
        return await self.db.create_user(user)
    
    async def get_by_id(self, user_id: int):
        """GET /users/{user_id} - Get user by ID"""
        return await self.db.get_user(user_id)`}
                    />
                </div>
            </section>

            {/* Key Features */}
            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Key Features</h2>
                <div className="space-y-4 not-prose">
                    {[
                        {
                            title: "Class-Based Routes",
                            description: "Group related endpoints together in controller classes. Methods automatically map to HTTP verbs.",
                        },
                        {
                            title: "Decorator System",
                            description: "Use @log for automatic logging, @speed for performance monitoring, and @version for API versioning.",
                        },
                        {
                            title: "Dev Console",
                            description: "Built-in real-time debugging console accessible at /__dev__ to monitor requests, logs, and performance.",
                        },
                        {
                            title: "FastAPI Powered",
                            description: "Full compatibility with FastAPI features including async/await, dependency injection, and OpenAPI.",
                        },
                    ].map((feature, i) => (
                        <div key={feature.title} className="flex gap-4">
                            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-accent-blue/10 text-sm font-medium text-accent-blue">
                                {i + 1}
                            </div>
                            <div>
                                <h3 className="font-medium text-foreground">{feature.title}</h3>
                                <p className="text-sm text-muted-foreground mt-1">{feature.description}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </section>

            {/* Next Steps */}
            <section className="not-prose">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Next Steps</h2>
                <div className="grid gap-4 sm:grid-cols-2">
                    <Link
                        href="/docs/getting-started"
                        className="group rounded-lg border border-border bg-card p-5 transition-all hover:border-accent-blue/50 hover:bg-card/80"
                    >
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="rounded-md bg-accent-green/10 p-2">
                                    <Zap className="h-4 w-4 text-accent-green" />
                                </div>
                                <div>
                                    <h3 className="font-medium text-foreground">Getting Started</h3>
                                    <p className="text-sm text-muted-foreground">Install and create your first API</p>
                                </div>
                            </div>
                            <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-accent-blue transition-colors" />
                        </div>
                    </Link>

                    <Link
                        href="https://github.com/alpheay/jec"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="group rounded-lg border border-border bg-card p-5 transition-all hover:border-accent-violet/50 hover:bg-card/80"
                    >
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="rounded-md bg-accent-violet/10 p-2">
                                    <Code2 className="h-4 w-4 text-accent-violet" />
                                </div>
                                <div>
                                    <h3 className="font-medium text-foreground">View Source</h3>
                                    <p className="text-sm text-muted-foreground">Explore the code on GitHub</p>
                                </div>
                            </div>
                            <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-accent-violet transition-colors" />
                        </div>
                    </Link>
                </div>
            </section>
        </article>
    );
}
