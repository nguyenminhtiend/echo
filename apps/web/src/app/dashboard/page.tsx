'use client';

import { useEffect, useState } from 'react';
import { apiFetch } from '@/lib/api-client';
import { Activity, Coins, Hash, History } from 'lucide-react';

type AgentStats = {
  total_runs: number;
  total_tokens: number;
  total_cost: number | string;
};

function formatCost(value: number | string): string {
  const n = typeof value === 'string' ? Number.parseFloat(value) : value;
  if (Number.isNaN(n)) {
    return '$0.00';
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 6,
  }).format(n);
}

export default function DashboardPage() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<AgentStats>({
    total_runs: 0,
    total_tokens: 0,
    total_cost: 0,
  });

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    apiFetch<AgentStats>('/api/agents/stats')
      .then((data) => {
        if (!cancelled) setStats(data);
      })
      .catch(() => {
        if (!cancelled) setStats({ total_runs: 0, total_tokens: 0, total_cost: 0 });
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  return (
    <div className="space-y-6 flex flex-col h-full min-h-0 pb-6">
      <h1 className="text-2xl font-bold font-heading">Dashboard</h1>
      
      <div className="grid gap-4 md:grid-cols-3">
        <div className="glass-panel ghost-border rounded-3xl p-6 relative overflow-hidden group hover:neural-glow hover:-translate-y-1 transition-all duration-300">
           <div className="flex items-center gap-3 mb-4">
             <div className="p-2 rounded-lg bg-obs-primary/10 ghost-border"><Activity size={18} className="text-obs-primary" /></div>
             <p className="font-label text-[11px] font-bold uppercase tracking-[0.1em] text-obs-outline">Total Runs</p>
           </div>
           <p className="text-4xl font-bold font-heading text-obs-on-surface">
             {loading ? <span className="animate-pulse">—</span> : stats.total_runs.toLocaleString()}
           </p>
        </div>
        
        <div className="glass-panel ghost-border rounded-3xl p-6 relative overflow-hidden group hover:neural-glow hover:-translate-y-1 transition-all duration-300">
           <div className="flex items-center gap-3 mb-4">
             <div className="p-2 rounded-lg bg-obs-tertiary/10 ghost-border"><Hash size={18} className="text-obs-tertiary" /></div>
             <p className="font-label text-[11px] font-bold uppercase tracking-[0.1em] text-obs-outline">Total Tokens</p>
           </div>
           <p className="text-4xl font-bold font-heading text-obs-on-surface">
             {loading ? <span className="animate-pulse">—</span> : stats.total_tokens.toLocaleString()}
           </p>
        </div>
        
        <div className="glass-panel ghost-border rounded-3xl p-6 relative overflow-hidden group hover:neural-glow hover:-translate-y-1 transition-all duration-300">
           <div className="flex items-center gap-3 mb-4">
             <div className="p-2 rounded-lg bg-accent/10 ghost-border"><Coins size={18} className="text-accent" /></div>
             <p className="font-label text-[11px] font-bold uppercase tracking-[0.1em] text-obs-outline">Total Cost</p>
           </div>
           <p className="text-3xl font-bold font-mono text-transparent bg-clip-text lithic-glow pb-1">
             {loading ? <span className="animate-pulse">—</span> : formatCost(stats.total_cost)}
           </p>
        </div>
      </div>
      
      <div className="flex-1 glass-panel ghost-border rounded-3xl p-6 flex flex-col min-h-0">
        <div className="flex items-center gap-3 mb-6">
          <History size={20} className="text-obs-outline" />
          <h2 className="text-lg font-bold font-heading">Recent Runs</h2>
        </div>
        <div className="flex-1 rounded-2xl bg-obs-surface-lowest/40 ghost-border p-8 flex border border-dashed border-obs-outline-variant/30 items-center justify-center">
           <div className="text-center">
             <div className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-obs-surface-highest/60 mb-4 ghost-border">
               <History size={24} className="text-obs-outline-variant/60" />
             </div>
             <p className="text-[15px] text-obs-outline font-sans">
               No agent runs yet. Submit a task from the Agent Console.
             </p>
           </div>
        </div>
      </div>
    </div>
  );
}
