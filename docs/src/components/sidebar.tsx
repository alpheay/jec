"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
    BookOpen,
    Home,
    Zap,
    Code2,
    Layers,
    Settings,
    ExternalLink,
    ChevronRight,
} from "lucide-react";

interface NavItem {
    title: string;
    href: string;
    icon?: React.ReactNode;
    external?: boolean;
}

interface NavSection {
    title: string;
    items: NavItem[];
}

const navigation: NavSection[] = [
    {
        title: "Overview",
        items: [
            { title: "Introduction", href: "/docs", icon: <BookOpen className="w-4 h-4" /> },
            { title: "Getting Started", href: "/docs/getting-started", icon: <Zap className="w-4 h-4" /> },
        ],
    },
    {
        title: "Core Concepts",
        items: [
            { title: "Routes", href: "/docs/routes", icon: <Layers className="w-4 h-4" /> },
            { title: "Decorators", href: "/docs/decorators", icon: <Code2 className="w-4 h-4" /> },
            { title: "Configuration", href: "/docs/configuration", icon: <Settings className="w-4 h-4" /> },
        ],
    },
    {
        title: "Resources",
        items: [
            { title: "GitHub", href: "https://github.com/alpheay/jec", icon: <ExternalLink className="w-4 h-4" />, external: true },
        ],
    },
];

export function Sidebar() {
    const pathname = usePathname();

    // Handle basePath for GitHub Pages
    const basePath = process.env.NODE_ENV === 'production' ? '/jec' : '';
    const normalizedPathname = pathname.replace(basePath, '') || '/';

    return (
        <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-border bg-sidebar">
            <div className="flex h-full flex-col">
                {/* Logo */}
                <div className="flex h-16 items-center gap-3 border-b border-sidebar-border px-6">
                    <div className="flex h-8 w-8 items-center justify-center rounded-md bg-gradient-to-br from-zinc-700 to-zinc-600 border border-zinc-500/50">
                        <span className="text-xs font-bold text-zinc-200 tracking-wide">JEC</span>
                    </div>
                    <div className="flex flex-col">
                        <span className="text-sm font-semibold text-foreground tracking-tight">JEC API</span>
                        <span className="text-[10px] text-muted-foreground">Documentation</span>
                    </div>
                </div>

                {/* Navigation */}
                <nav className="flex-1 overflow-y-auto px-3 py-4">
                    <div className="space-y-6">
                        {/* Home link */}
                        <Link
                            href="/"
                            className={cn(
                                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                                normalizedPathname === "/"
                                    ? "bg-sidebar-accent text-sidebar-accent-foreground"
                                    : "text-muted-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                            )}
                        >
                            <Home className="w-4 h-4" />
                            Home
                        </Link>

                        {navigation.map((section) => (
                            <div key={section.title}>
                                <h4 className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground/70">
                                    {section.title}
                                </h4>
                                <ul className="space-y-1">
                                    {section.items.map((item) => {
                                        const isActive = normalizedPathname === item.href ||
                                            (item.href !== "/docs" && normalizedPathname.startsWith(item.href));

                                        return (
                                            <li key={item.href}>
                                                <Link
                                                    href={item.href}
                                                    target={item.external ? "_blank" : undefined}
                                                    rel={item.external ? "noopener noreferrer" : undefined}
                                                    className={cn(
                                                        "group flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-all",
                                                        isActive
                                                            ? "bg-sidebar-accent text-sidebar-accent-foreground font-medium"
                                                            : "text-muted-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground"
                                                    )}
                                                >
                                                    {item.icon && (
                                                        <span className={cn(
                                                            "transition-colors",
                                                            isActive ? "text-accent-blue" : "text-muted-foreground group-hover:text-muted-foreground"
                                                        )}>
                                                            {item.icon}
                                                        </span>
                                                    )}
                                                    <span className="flex-1">{item.title}</span>
                                                    {isActive && !item.external && (
                                                        <ChevronRight className="w-3 h-3 text-accent-blue" />
                                                    )}
                                                </Link>
                                            </li>
                                        );
                                    })}
                                </ul>
                            </div>
                        ))}
                    </div>
                </nav>

                {/* Footer */}
                <div className="border-t border-sidebar-border p-4">
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span>v0.0.6</span>
                        <span className="flex items-center gap-1.5">
                            <span className="h-1.5 w-1.5 rounded-full bg-accent-green animate-pulse"></span>
                            Active
                        </span>
                    </div>
                </div>
            </div>
        </aside>
    );
}
