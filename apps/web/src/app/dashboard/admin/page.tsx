import { ShieldAlert, Receipt, Users } from 'lucide-react';

export default function AdminPage() {
  return (
    <div className="space-y-6 flex flex-col h-full min-h-0">
      <h1 className="text-2xl font-bold font-heading">Admin Panel</h1>
      <div className="grid gap-6 md:grid-cols-3 flex-1 min-h-0 pb-6">
        <div className="glass-panel ghost-border rounded-3xl p-6 md:p-8 relative overflow-hidden group hover:neural-glow transition-all duration-300 flex flex-col">
          <div className="h-12 w-12 rounded-xl bg-obs-primary/10 flex items-center justify-center mb-5 border border-obs-primary/20">
            <Users className="text-obs-primary" size={24} />
          </div>
          <h3 className="font-heading text-lg font-bold mb-3">Users</h3>
          <p className="text-sm text-muted-foreground flex-1 leading-relaxed">
            User management will be available once Better Auth is fully integrated.
          </p>
          <div className="mt-6 inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-obs-surface-highest/60 ghost-border font-mono text-[10px] uppercase tracking-wider text-obs-on-surface-variant w-fit">
            <span className="h-1.5 w-1.5 rounded-full bg-chart-4 shadow-[0_0_5px_var(--color-chart-4)] animate-pulse"></span> Service Active
          </div>
        </div>
        
        <div className="glass-panel ghost-border rounded-3xl p-6 md:p-8 relative overflow-hidden group hover:neural-glow transition-all duration-300 flex flex-col">
          <div className="h-12 w-12 rounded-xl bg-obs-tertiary/10 flex items-center justify-center mb-5 border border-obs-tertiary/20">
            <Receipt className="text-obs-tertiary" size={24} />
          </div>
          <h3 className="font-heading text-lg font-bold mb-3">Cost Reports</h3>
          <p className="text-sm text-muted-foreground flex-1 leading-relaxed">
            Aggregated cost data from the cost_ledger table will appear here. Tracking token expenditures across pods.
          </p>
          <div className="mt-6 inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-obs-surface-highest/60 ghost-border font-mono text-[10px] uppercase tracking-wider text-obs-on-surface-variant w-fit">
            <span className="h-1.5 w-1.5 rounded-full bg-chart-3 shadow-[0_0_5px_var(--color-chart-3)]"></span> Syncing
          </div>
        </div>
        
        <div className="glass-panel ghost-border rounded-3xl p-6 md:p-8 relative overflow-hidden group hover:neural-glow transition-all duration-300 flex flex-col">
           <div className="h-12 w-12 rounded-xl bg-obs-error/10 flex items-center justify-center mb-5 border border-obs-error/20">
            <ShieldAlert className="text-obs-error" size={24} />
          </div>
          <h3 className="font-heading text-lg font-bold mb-3">Audit Logs</h3>
          <p className="text-sm text-muted-foreground flex-1 leading-relaxed">
            All LLM calls and agent actions are securely logged for compliance review and zero-trust verification.
          </p>
           <div className="mt-6 inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-obs-surface-highest/60 ghost-border font-mono text-[10px] uppercase tracking-wider text-obs-on-surface-variant w-fit">
            <span className="h-1.5 w-1.5 rounded-full bg-chart-2 shadow-[0_0_5px_var(--color-chart-2)]"></span> Logging Enabled
          </div>
        </div>
      </div>
    </div>
  );
}
