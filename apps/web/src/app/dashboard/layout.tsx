'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useUIStore } from '@/lib/stores/ui-store';

const NAV_ITEMS = [
  { href: '/dashboard', label: 'Overview' },
  { href: '/dashboard/agents', label: 'Agents' },
  { href: '/dashboard/rag', label: 'RAG Explorer' },
  { href: '/dashboard/settings', label: 'Settings' },
  { href: '/dashboard/admin', label: 'Admin' },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { sidebarOpen, toggleSidebar } = useUIStore();

  return (
    <div className="flex h-screen">
      {sidebarOpen && (
        <aside className="w-64 border-r bg-muted/40 p-4">
          <h2 className="mb-6 text-lg font-bold">E.C.H.O.</h2>
          <nav className="space-y-1">
            {NAV_ITEMS.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`block rounded-md px-3 py-2 text-sm ${
                  pathname === item.href ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'
                }`}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </aside>
      )}
      <main className="flex-1 overflow-auto p-6">
        <button onClick={toggleSidebar} className="mb-4 text-sm text-muted-foreground">
          {sidebarOpen ? 'Hide sidebar' : 'Show sidebar'}
        </button>
        {children}
      </main>
    </div>
  );
}
