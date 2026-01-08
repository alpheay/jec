"use client";

import { useEffect, useRef, useState } from "react";
import Prism from "prismjs";
import { Check, Copy } from "lucide-react";
import { cn } from "@/lib/utils";

// Import common languages
import "prismjs/components/prism-python";
import "prismjs/components/prism-typescript";
import "prismjs/components/prism-javascript";
import "prismjs/components/prism-bash";
import "prismjs/components/prism-json";
import "prismjs/components/prism-yaml";
import "prismjs/components/prism-markdown";

interface CodeBlockProps {
    code: string;
    language?: string;
    filename?: string;
    showLineNumbers?: boolean;
    className?: string;
}

export function CodeBlock({
    code,
    language = "typescript",
    filename,
    showLineNumbers = false,
    className,
}: CodeBlockProps) {
    const codeRef = useRef<HTMLElement>(null);
    const [copied, setCopied] = useState(false);

    useEffect(() => {
        if (codeRef.current) {
            Prism.highlightElement(codeRef.current);
        }
    }, [code, language]);

    const handleCopy = async () => {
        await navigator.clipboard.writeText(code);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const lines = code.split("\n");

    return (
        <div
            className={cn(
                "code-block-wrapper group relative rounded-xl border border-border bg-card/80 backdrop-blur-sm overflow-hidden shadow-2xl shadow-black/20",
                className
            )}
        >
            {/* Window Header */}
            <div className="flex items-center gap-2 border-b border-border bg-[#1f1f23] px-4 py-3">
                {/* macOS-style window dots */}
                <div className="flex gap-1.5">
                    <div className="h-3 w-3 rounded-full bg-accent-red/80"></div>
                    <div className="h-3 w-3 rounded-full bg-accent-yellow/80"></div>
                    <div className="h-3 w-3 rounded-full bg-accent-green/80"></div>
                </div>
                {filename && (
                    <span className="ml-2 text-xs text-muted-foreground font-mono">
                        {filename}
                    </span>
                )}
            </div>

            {/* Copy button */}
            <button
                onClick={handleCopy}
                className={cn(
                    "absolute right-3 top-14 z-10 flex h-8 w-8 items-center justify-center rounded-md border transition-all",
                    copied
                        ? "border-accent-green/50 bg-accent-green/10 text-accent-green"
                        : "border-border bg-[#1f1f23] text-muted-foreground opacity-0 group-hover:opacity-100 hover:border-border hover:bg-[#27272a] hover:text-foreground"
                )}
                aria-label={copied ? "Copied!" : "Copy code"}
            >
                {copied ? (
                    <Check className="h-4 w-4" />
                ) : (
                    <Copy className="h-4 w-4" />
                )}
            </button>

            {/* Code */}
            <div className="relative overflow-x-auto bg-[#0f0f12]">
                {showLineNumbers && (
                    <div className="absolute left-0 top-0 flex flex-col py-6 pl-4 pr-3 text-right select-none border-r border-border">
                        {lines.map((_, i) => (
                            <span
                                key={i}
                                className="text-sm leading-relaxed text-muted-foreground/40 font-mono"
                            >
                                {i + 1}
                            </span>
                        ))}
                    </div>
                )}
                <pre
                    className={cn(
                        "p-6 text-sm leading-relaxed overflow-x-auto font-mono",
                        showLineNumbers && "pl-14"
                    )}
                >
                    <code ref={codeRef} className={`language-${language}`}>
                        {code}
                    </code>
                </pre>
            </div>
        </div>
    );
}
