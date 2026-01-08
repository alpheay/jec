# JEC Documentation Guide

This guide explains how to add and maintain documentation for the JEC API project.

## Adding a New Documentation Page

### 1. Create the Page File

Create a new folder and `page.tsx` file in `src/app/docs/`:

```tsx
// src/app/docs/my-topic/page.tsx
import { CodeBlock } from "@/components/code-block";

export default function MyTopicPage() {
  return (
    <article className="prose prose-invert max-w-none">
      {/* Header */}
      <div className="not-prose mb-12">
        <h1 className="text-4xl font-bold tracking-tight text-foreground">
          My Topic Title
        </h1>
        <p className="mt-4 text-xl text-muted-foreground leading-relaxed">
          Brief description of this documentation section.
        </p>
      </div>

      {/* Content sections */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold text-foreground mb-4">Section Title</h2>
        <p className="text-muted-foreground leading-relaxed mb-6">
          Your content here...
        </p>
      </section>
    </article>
  );
}
```

### 2. Add to Sidebar Navigation

Update `src/components/sidebar.tsx` to include your new page:

```tsx
const navigation: NavSection[] = [
  {
    title: "Section Name",
    items: [
      { 
        title: "My Topic", 
        href: "/docs/my-topic", 
        icon: <YourIcon className="w-4 h-4" /> 
      },
    ],
  },
];
```

## Using Code Blocks

The `CodeBlock` component provides syntax highlighting with a premium macOS-style window design featuring:

- **Window header** with colored traffic light dots (red, yellow, green)
- **Glassmorphism effects** with backdrop blur and shadow
- **Copy functionality** that appears on hover
- **Prism.js syntax highlighting** for clean, consistent code display

### Basic Usage

```tsx
import { CodeBlock } from "@/components/code-block";

<CodeBlock
  language="python"
  code={`def hello():
    return "Hello, World!"`}
/>
```

### With Filename Header

```tsx
<CodeBlock
  filename="example.py"
  language="python"
  code={`from jec import Route

class MyRoute(Route):
    async def get(self):
        return {"message": "Hello"}`}
/>
```

### With Line Numbers

```tsx
<CodeBlock
  language="python"
  showLineNumbers
  code={`# Line 1
# Line 2
# Line 3`}
/>
```

### Supported Languages

- `python` - Python code
- `typescript` / `javascript` - JS/TS code
- `bash` - Shell commands
- `json` - JSON data
- `yaml` - YAML configuration
- `markdown` - Markdown content

## Styling Guidelines

### Typography

Use Tailwind CSS classes from our theme:

```tsx
// Headings
<h1 className="text-4xl font-bold tracking-tight text-foreground">...</h1>
<h2 className="text-2xl font-semibold text-foreground mb-4">...</h2>

// Body text
<p className="text-muted-foreground leading-relaxed">...</p>

// Inline code
<code className="bg-secondary px-1.5 py-0.5 rounded text-sm font-mono">...</code>
```

### Colors

Use our accent colors for visual hierarchy:

| Color | CSS Variable | Use Case |
|-------|--------------|----------|
| Blue | `text-accent-blue` | Primary actions, links |
| Green | `text-accent-green` | Success, active states |
| Yellow | `text-accent-yellow` | Warnings, highlights |
| Violet | `text-accent-violet` | Decorators, special |
| Red | `text-accent-red` | Errors, destructive |

### Cards and Containers

```tsx
// Feature card
<div className="rounded-lg border border-border bg-card p-4">
  ...
</div>

// Interactive card
<div className="rounded-lg border border-border bg-card p-4 transition-all hover:border-accent-blue/50">
  ...
</div>
```

## Page Transitions

Page transitions are handled automatically via the CSS View Transitions API in `globals.css`. All internal navigation will have smooth fade transitions.

For client-side navigation, use Next.js `Link` component:

```tsx
import Link from "next/link";

<Link href="/docs/my-page">Go to page</Link>
```

## Icons

We use [Lucide React](https://lucide.dev/icons/) for icons:

```tsx
import { BookOpen, Code2, Zap } from "lucide-react";

<BookOpen className="w-4 h-4 text-accent-blue" />
```

## Running Locally

```bash
cd docs
npm run dev
```

The site will be available at `http://localhost:3000`.

## Building for Production

```bash
npm run build
```

This generates a static export in the `out/` folder, ready for GitHub Pages deployment.

## Theme Reference

The theme is defined in `globals.css` and matches the JEC Dev Console. Key variables:

```css
/* Backgrounds */
--background: #09090b;    /* Primary background */
--card: #18181b;          /* Card backgrounds */
--sidebar: #0f0f12;       /* Sidebar background */

/* Text */
--foreground: #fafafa;    /* Primary text */
--muted-foreground: #a1a1aa;  /* Secondary text */

/* Accents */
--accent-blue: #3b82f6;
--accent-green: #22c55e;
--accent-yellow: #eab308;
--accent-violet: #8b5cf6;
--accent-red: #ef4444;
```
