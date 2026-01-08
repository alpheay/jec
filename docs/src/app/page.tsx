import Link from "next/link";
import { ArrowRight, Zap, Shield, Code2, Layers, Terminal, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-accent-blue/5 via-transparent to-accent-violet/5" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-gradient-radial from-accent-blue/10 to-transparent blur-3xl" />

        {/* Grid pattern */}
        <div
          className="absolute inset-0 opacity-[0.02]"
          style={{
            backgroundImage: `linear-gradient(var(--border) 1px, transparent 1px), linear-gradient(90deg, var(--border) 1px, transparent 1px)`,
            backgroundSize: '60px 60px',
          }}
        />

        <div className="relative mx-auto max-w-6xl px-6 py-24 sm:py-32 lg:py-40">
          {/* Badge */}
          <div className="flex justify-center mb-8">
            <div className="inline-flex items-center gap-2 rounded-full border border-border bg-card/50 px-4 py-1.5 text-sm backdrop-blur-sm">
              <Sparkles className="w-4 h-4 text-accent-yellow" />
              <span className="text-muted-foreground">Version 0.0.6 — Now with Dev Console</span>
            </div>
          </div>

          {/* Main heading */}
          <div className="text-center">
            <h1 className="text-5xl font-bold tracking-tight sm:text-6xl lg:text-7xl">
              <span className="text-foreground">Just Encapsulated</span>
              <br />
              <span className="bg-gradient-to-r from-accent-blue via-accent-violet to-accent-blue bg-clip-text text-transparent">
                Controllers
              </span>
            </h1>

            <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-muted-foreground sm:text-xl">
              The class-based system for building Application Program Interfaces.
              Clean, intuitive, and powerful routing for modern Python APIs.
            </p>

            {/* CTA Buttons */}
            <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
              <Button asChild size="lg" className="gap-2 bg-accent-blue hover:bg-accent-blue/90 text-white">
                <Link href="/docs">
                  Get Started
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="gap-2">
                <Link href="https://github.com/alpheay/jec" target="_blank" rel="noopener noreferrer">
                  <Terminal className="w-4 h-4" />
                  View on GitHub
                </Link>
              </Button>
            </div>
          </div>

          {/* Code preview */}
          <div className="mt-16 sm:mt-20">
            <div className="mx-auto max-w-3xl rounded-xl border border-border bg-card/80 backdrop-blur-sm overflow-hidden shadow-2xl shadow-black/20">
              {/* Window header */}
              <div className="flex items-center gap-2 border-b border-border bg-[#1f1f23] px-4 py-3">
                <div className="flex gap-1.5">
                  <div className="h-3 w-3 rounded-full bg-accent-red/80"></div>
                  <div className="h-3 w-3 rounded-full bg-accent-yellow/80"></div>
                  <div className="h-3 w-3 rounded-full bg-accent-green/80"></div>
                </div>
                <span className="ml-2 text-xs text-muted-foreground font-mono">routes/users.py</span>
              </div>

              {/* Code content */}
              <pre className="p-6 text-sm leading-relaxed overflow-x-auto font-mono">
                <code>
                  <span className="text-accent-violet">from</span> <span className="text-foreground">jec</span> <span className="text-accent-violet">import</span> <span className="text-foreground">Route</span>{"\n"}
                  <span className="text-accent-violet">from</span> <span className="text-foreground">jec.decorators</span> <span className="text-accent-violet">import</span> <span className="text-foreground">log, speed, version</span>{"\n\n"}
                  <span className="text-accent-violet">class</span> <span className="text-accent-blue">UsersRoute</span><span className="text-muted-foreground">(</span><span className="text-foreground">Route</span><span className="text-muted-foreground">):</span>{"\n"}
                  <span className="text-muted-foreground">{"    "}</span><span className="text-accent-yellow">@log</span>{"\n"}
                  <span className="text-muted-foreground">{"    "}</span><span className="text-accent-yellow">@speed</span>{"\n"}
                  <span className="text-muted-foreground">{"    "}</span><span className="text-accent-yellow">@version</span><span className="text-muted-foreground">(</span><span className="text-accent-green">{'">=1.0.0"'}</span><span className="text-muted-foreground">)</span>{"\n"}
                  <span className="text-muted-foreground">{"    "}</span><span className="text-accent-violet">async def</span> <span className="text-accent-blue">get</span><span className="text-muted-foreground">(</span><span className="text-foreground">self</span><span className="text-muted-foreground">):</span>{"\n"}
                  <span className="text-muted-foreground">{"        "}</span><span className="text-zinc-500"># Automatically maps to GET /users</span>{"\n"}
                  <span className="text-muted-foreground">{"        "}</span><span className="text-accent-violet">return</span> <span className="text-muted-foreground">{"{"}</span><span className="text-accent-green">{'"users"'}</span><span className="text-muted-foreground">:</span> <span className="text-muted-foreground">[...]&rbrace;</span>
                </code>
              </pre>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="border-t border-border bg-card/30">
        <div className="mx-auto max-w-6xl px-6 py-24 sm:py-32">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Built for Modern APIs
            </h2>
            <p className="mt-4 text-lg text-muted-foreground">
              Everything you need to build production-ready APIs, out of the box.
            </p>
          </div>

          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {[
              {
                icon: Code2,
                title: "Class-Based Routes",
                description: "Organize your endpoints with clean, intuitive class structures. Each HTTP method maps automatically.",
                color: "text-accent-blue",
                bgColor: "bg-accent-blue/10",
              },
              {
                icon: Zap,
                title: "Powerful Decorators",
                description: "Add logging, performance monitoring, and version checks with simple decorators.",
                color: "text-accent-yellow",
                bgColor: "bg-accent-yellow/10",
              },
              {
                icon: Shield,
                title: "Version Control",
                description: "Built-in API versioning with semantic version constraints for safe evolution.",
                color: "text-accent-violet",
                bgColor: "bg-accent-violet/10",
              },
              {
                icon: Terminal,
                title: "Dev Console",
                description: "Real-time debugging console to monitor requests, logs, and performance metrics.",
                color: "text-accent-green",
                bgColor: "bg-accent-green/10",
              },
              {
                icon: Layers,
                title: "FastAPI Powered",
                description: "Built on top of FastAPI for async support, automatic OpenAPI docs, and validation.",
                color: "text-accent-orange",
                bgColor: "bg-accent-orange/10",
              },
              {
                icon: Sparkles,
                title: "Zero Boilerplate",
                description: "Convention over configuration. Get started in seconds with sensible defaults.",
                color: "text-accent-red",
                bgColor: "bg-accent-red/10",
              },
            ].map((feature) => (
              <div
                key={feature.title}
                className="group relative rounded-xl border border-border bg-card p-6 transition-all hover:border-border hover:bg-card/80"
              >
                <div className={`inline-flex rounded-lg p-2.5 ${feature.bgColor}`}>
                  <feature.icon className={`h-5 w-5 ${feature.color}`} />
                </div>
                <h3 className="mt-4 text-lg font-semibold text-foreground">
                  {feature.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Start Section */}
      <div className="border-t border-border">
        <div className="mx-auto max-w-6xl px-6 py-24 sm:py-32">
          <div className="grid gap-12 lg:grid-cols-2 lg:gap-16 items-center">
            <div>
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
                Get started in seconds
              </h2>
              <p className="mt-4 text-lg text-muted-foreground">
                Install JEC and create your first API endpoint with just a few lines of code.
              </p>

              <div className="mt-8 space-y-4">
                {[
                  "Install via pip",
                  "Create your route class",
                  "Run your server",
                ].map((step, i) => (
                  <div key={step} className="flex items-center gap-4">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent-blue/10 text-sm font-medium text-accent-blue">
                      {i + 1}
                    </div>
                    <span className="text-foreground">{step}</span>
                  </div>
                ))}
              </div>

              <div className="mt-8">
                <Button asChild className="gap-2 bg-accent-blue hover:bg-accent-blue/90 text-white">
                  <Link href="/docs">
                    Read the docs
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </Button>
              </div>
            </div>

            <div className="rounded-xl border border-border bg-card overflow-hidden">
              <div className="flex items-center gap-2 border-b border-border bg-[#1f1f23] px-4 py-3">
                <Terminal className="h-4 w-4 text-muted-foreground" />
                <span className="text-xs text-muted-foreground font-mono">Terminal</span>
              </div>
              <pre className="p-6 text-sm leading-relaxed overflow-x-auto font-mono">
                <code>
                  <span className="text-muted-foreground">$</span> <span className="text-accent-green">pip install jec-api</span>{"\n\n"}
                  <span className="text-muted-foreground">$</span> <span className="text-accent-green">python app.py</span>{"\n"}
                  <span className="text-accent-blue">INFO</span><span className="text-muted-foreground">:     Uvicorn running on</span> <span className="text-accent-green">http://127.0.0.1:8000</span>{"\n"}
                  <span className="text-accent-blue">INFO</span><span className="text-muted-foreground">:     Dev console at</span> <span className="text-accent-yellow">/__dev__</span>
                </code>
              </pre>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-border">
        <div className="mx-auto max-w-6xl px-6 py-8">
          <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
            <div className="flex items-center gap-3">
              <div className="flex h-7 w-7 items-center justify-center rounded-md bg-gradient-to-br from-zinc-700 to-zinc-600 border border-zinc-500/50">
                <span className="text-[10px] font-bold text-zinc-200">JEC</span>
              </div>
              <span className="text-sm text-muted-foreground">
                Just Encapsulated Controllers
              </span>
            </div>
            <div className="flex items-center gap-6 text-sm text-muted-foreground">
              <Link href="/docs" className="hover:text-foreground transition-colors">
                Documentation
              </Link>
              <Link href="https://github.com/alpheay/jec" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">
                GitHub
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
