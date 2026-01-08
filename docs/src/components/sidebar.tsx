"use client";

import { useState, useEffect } from "react";
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
    Layout,
    Cpu,
    Terminal
} from "lucide-react";

interface NavItem {
    title: string;
    href: string;
    icon?: React.ReactNode;
    external?: boolean;
    items?: NavItem[];
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
            {
                title: "Core Application",
                href: "/docs/core",
                icon: <Cpu className="w-4 h-4" />,
                items: [
                    { title: "Configuration", href: "/docs/core/configuration" }
                ]
            },
            {
                title: "Routes",
                href: "/docs/routes",
                icon: <Layers className="w-4 h-4" />,
                items: [
                    { title: "Types & Validation", href: "/docs/routes/types" }
                ]
            },
            {
                title: "Decorators",
                href: "/docs/decorators",
                icon: <Code2 className="w-4 h-4" />,
                items: [
                    {
                        title: "Authentication",
                        href: "/docs/decorators/authentication",
                        items: [
                            { title: "Advanced Auth", href: "/docs/decorators/authentication/advanced" }
                        ]
                    },
                    {
                        title: "Logging",
                        href: "/docs/decorators/logging",
                        items: [
                            { title: "Advanced Logging", href: "/docs/decorators/logging/advanced" }
                        ]
                    },
                    {
                        title: "Speed",
                        href: "/docs/decorators/speed",
                        items: [
                            { title: "Advanced Monitoring", href: "/docs/decorators/speed/advanced" }
                        ]
                    },
                    {
                        title: "Versioning",
                        href: "/docs/decorators/versioning",
                        items: [
                            { title: "Advanced Versioning", href: "/docs/decorators/versioning/advanced" }
                        ]
                    },
                    { title: "Deprecated", href: "/docs/decorators/deprecated" },
                    { title: "Rate Limit", href: "/docs/decorators/ratelimit" },
                    { title: "Timeout", href: "/docs/decorators/timeout" },
                    { title: "Retry", href: "/docs/decorators/retry" },
                ]
            },
            { title: "Developer Tools", href: "/docs/dev-tools", icon: <Terminal className="w-4 h-4" /> },
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
                                <ul className="space-y-0.5">
                                    {section.items.map((item) => (
                                        <SidebarItem
                                            key={item.href}
                                            item={item}
                                            pathname={normalizedPathname}
                                        />
                                    ))}
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

function SidebarItem({ item, pathname, depth = 0 }: { item: NavItem; pathname: string; depth?: number }) {
    const isActive = pathname === item.href;
    const isChildActive = item.items?.some(child =>
        pathname === child.href || pathname.startsWith(child.href + '/')
    );
    const [isOpen, setIsOpen] = useState(isChildActive || isActive);

    // Expand if a child becomes active
    useEffect(() => {
        if (isChildActive) {
            setIsOpen(true);
        }
    }, [isChildActive]);

    const hasChildren = item.items && item.items.length > 0;
    const isExpanded = isOpen || isChildActive;

    return (
        <li>
            <div className="relative group">
                <div className="flex items-center">
                    <Link
                        href={item.href}
                        target={item.external ? "_blank" : undefined}
                        rel={item.external ? "noopener noreferrer" : undefined}
                        className={cn(
                            "flex-1 flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-all",
                            isActive
                                ? "bg-sidebar-accent text-sidebar-accent-foreground font-medium"
                                : "text-muted-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground"
                        )}
                        onClick={() => {
                            if (hasChildren && !isOpen) setIsOpen(true);
                        }}
                    >
                        {item.icon && (
                            <span className={cn(
                                "transition-colors",
                                isActive ? "text-accent-blue" : "text-muted-foreground group-hover:text-muted-foreground"
                            )}>
                                {item.icon}
                            </span>
                        )}
                        <span>{item.title}</span>
                    </Link>
                    {hasChildren && (
                        <button
                            onClick={(e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                setIsOpen(!isOpen);
                            }}
                            className="p-2 text-muted-foreground hover:text-foreground transition-colors rounded-md hover:bg-sidebar-accent/50 mr-1"
                        >
                            <ChevronRight
                                className={cn(
                                    "w-3.5 h-3.5 transition-transform duration-200",
                                    isExpanded ? "rotate-90" : ""
                                )}
                            />
                        </button>
                    )}
                </div>

                {hasChildren && (
                    <div
                        className={cn(
                            "grid transition-[grid-template-rows] duration-300 ease-in-out",
                            isExpanded ? "grid-rows-[1fr]" : "grid-rows-[0fr]"
                        )}
                    >
                        <ul className="overflow-hidden ml-4 border-l border-sidebar-border/50">
                            <div className="mt-0.5 space-y-0.5">
                                {item.items!.map((child) => (
                                    <SidebarItem
                                        key={child.href}
                                        item={child}
                                        pathname={pathname}
                                        depth={depth + 1}
                                    />
                                ))}
                            </div>
                        </ul>
                    </div>
                )}
            </div>
        </li>
    );
}
