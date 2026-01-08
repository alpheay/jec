import { Sidebar } from "@/components/sidebar";

export default function DocsLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen">
            <Sidebar />
            <main className="pl-64">
                <div className="mx-auto max-w-4xl px-8 py-12">
                    {children}
                </div>
            </main>
        </div>
    );
}
