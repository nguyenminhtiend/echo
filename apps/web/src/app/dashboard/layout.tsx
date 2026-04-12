'use client';

import {
  Bell,
  Bot,
  Database,
  HelpCircle,
  LayoutDashboard,
  LogOut,
  Rocket,
  Search,
  Settings,
  ShieldCheck
} from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const NAV_ITEMS = [
  { href: '/dashboard', label: 'Overview', icon: LayoutDashboard },
  { href: '/dashboard/agents', label: 'Agents', icon: Bot },
  { href: '/dashboard/rag', label: 'RAG Explorer', icon: Database },
  { href: '/dashboard/settings', label: 'Settings', icon: Settings },
  { href: '/dashboard/admin', label: 'Admin', icon: ShieldCheck }
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  function isActive(href: string) {
    if (href === '/dashboard') return pathname === href;
    return pathname.startsWith(href);
  }

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Ambient background glow */}
      <div className="fixed top-[-10%] right-[-5%] w-[40%] h-[40%] bg-obs-primary/5 blur-[120px] rounded-full pointer-events-none z-0" />
      <div className="fixed bottom-[-10%] left-[-5%] w-[30%] h-[30%] bg-obs-primary-container/5 blur-[100px] rounded-full pointer-events-none z-0" />

      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-full w-64 z-40 bg-[rgba(10,10,12,0.6)] backdrop-blur-2xl border-r border-white/5 flex flex-col pt-20 pb-6 shadow-2xl shadow-obs-primary-container/10">
        <div className="px-6 mb-8">
          <h1 className="text-xl font-black text-obs-primary font-headline tracking-tighter">
            E.C.H.O.
          </h1>
          <p className="font-label text-[10px] uppercase tracking-widest text-obs-outline mt-1">
            Logic Engine v1.0
          </p>
        </div>

        <nav className="flex-1 space-y-1">
          {NAV_ITEMS.map((item) => {
            const active = isActive(item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-4 py-3 transition-all duration-300 ${
                  active
                    ? 'text-obs-primary bg-obs-primary/10 border-l-2 border-obs-primary'
                    : 'text-obs-outline border-l-2 border-transparent hover:text-obs-on-surface-variant hover:bg-white/5 hover:translate-x-0.5'
                }`}
              >
                <Icon className="h-[18px] w-[18px]" />
                <span className="font-label text-xs uppercase tracking-widest">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="px-4 mt-auto space-y-4">
          <button
            type="button"
            className="w-full py-3 rounded-xl lithic-glow text-primary-foreground font-headline font-bold text-sm tracking-tight active:scale-95 duration-200 flex items-center justify-center gap-2 shadow-lg shadow-obs-primary-container/20"
          >
            <Rocket className="h-4 w-4" />
            Deploy Agent
          </button>
          <div className="pt-4 border-t border-white/5 space-y-1">
            <Link
              href="/help"
              className="flex items-center gap-3 px-4 py-2 text-obs-outline hover:text-obs-on-surface-variant transition-colors"
            >
              <HelpCircle className="h-4 w-4" />
              <span className="font-label text-[10px] uppercase tracking-widest">Help</span>
            </Link>
            <button
              type="button"
              className="w-full flex items-center gap-3 px-4 py-2 text-obs-outline hover:text-obs-on-surface-variant transition-colors"
            >
              <LogOut className="h-4 w-4" />
              <span className="font-label text-[10px] uppercase tracking-widest">Logout</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Top Header */}
      <header className="fixed top-0 w-full z-50 h-16 flex justify-between items-center px-6 bg-[rgba(10,10,12,0.4)] backdrop-blur-xl border-b border-white/5 shadow-[0_8px_32px_0_rgba(139,92,246,0.06)]">
        <div className="flex items-center gap-8 pl-64">
          <span className="text-2xl font-bold tracking-tighter text-obs-primary font-headline">
            E.C.H.O.
          </span>
          <div className="relative hidden lg:block">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-obs-outline" />
            <input
              type="text"
              className="bg-white/5 border-none rounded-full py-1.5 pl-10 pr-4 text-xs font-label text-obs-on-surface placeholder:text-obs-outline focus:ring-1 focus:ring-obs-primary/50 w-64 outline-none"
              placeholder="Search operations..."
            />
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            type="button"
            className="p-2 text-obs-outline hover:bg-white/5 rounded-full transition-colors active:scale-95 duration-200"
          >
            <Bell className="h-5 w-5" />
          </button>
          <button
            type="button"
            className="p-2 text-obs-outline hover:bg-white/5 rounded-full transition-colors active:scale-95 duration-200"
          >
            <Settings className="h-5 w-5" />
          </button>
          <div className="h-8 w-8 rounded-full overflow-hidden bg-obs-surface-highest border border-white/10 ml-2 flex items-center justify-center">
            <span className="text-xs font-bold text-obs-primary font-headline">U</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="pl-64 pt-16 flex-1 min-h-0 overflow-hidden relative z-10">{children}</main>
    </div>
  );
}
