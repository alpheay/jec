
import { CodeBlock } from "@/components/code-block";

export default function AdvancedLoggingPage() {
    return (
        <article className="prose prose-invert max-w-none">
            <div className="not-prose mb-12">
                <h1 className="text-4xl font-bold tracking-tight text-foreground">
                    Advanced Logging
                </h1>
                <p className="mt-4 text-xl text-muted-foreground leading-relaxed">
                    Fine-tune your logs with levels, truncation controls, and custom messages.
                </p>
            </div>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Privacy & Data Control</h2>
                <p className="text-muted-foreground leading-relaxed mb-4">
                    For sensitive endpoints, you might want to disable argument or result logging to prevent leaking PII.
                </p>

                <CodeBlock
                    filename="routes/auth.py"
                    language="python"
                    code={`# Privacy-Focused (No data logging)
# Logs: [CALL] sensitive_op / [RETURN] sensitive_op
@log(include_args=False, include_result=False)
async def sensitive_op(password: str): ...`}
                />
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Heavy Payloads</h2>
                <p className="text-muted-foreground leading-relaxed mb-4">
                    Prevent log flooding by setting a maximum length for logged arguments and results.
                </p>

                <CodeBlock
                    filename="routes/files.py"
                    language="python"
                    code={`# Debugging Heavy Payloads
# Truncates to 5000 chars, uses DEBUG level
@log(level="debug", max_length=5000, message="PAYLOAD_DEBUG")
async def process_large_file(file: bytes): ...`}
                />
            </section>

            <section className="mb-12">
                <h2 className="text-2xl font-semibold text-foreground mb-4">Detailed Signature</h2>

                <div className="rounded-xl border border-border overflow-hidden bg-card/50 backdrop-blur-sm shadow-2xl shadow-black/20">
                    <CodeBlock
                        language="python"
                        className="border-none rounded-none shadow-none"
                        code={`def log(
    func=None, *, 
    level: str = "info", 
    include_args: bool = True, 
    include_result: bool = True, 
    max_length: int = 200, 
    message: str = None
)`}
                    />

                    <div className="p-6 border-t border-border bg-[#0f0f12]/30">
                        <ul className="space-y-3 text-sm text-muted-foreground list-none p-0 m-0">
                            <li><strong className="text-foreground font-mono">level</strong>: Logging level (<code>"debug"</code>, <code>"info"</code>, <code>"warning"</code>, <code>"error"</code>). Default: <code>"info"</code>.</li>
                            <li><strong className="text-foreground font-mono">include_args</strong>: If <code>True</code>, logs function arguments on entry. Default: <code>True</code>.</li>
                            <li><strong className="text-foreground font-mono">include_result</strong>: If <code>True</code>, logs return value on exit. Default: <code>True</code>.</li>
                            <li><strong className="text-foreground font-mono">max_length</strong>: Truncates arguments and results to this length. Default: <code>200</code>.</li>
                            <li><strong className="text-foreground font-mono">message</strong>: Optional prefix tag for the log entry.</li>
                        </ul>
                    </div>
                </div>
            </section>
        </article>
    );
}
