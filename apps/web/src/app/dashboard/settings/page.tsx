import { Cpu, Database, Network } from 'lucide-react';

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold font-heading">Settings</h1>
      
      <div className="glass-panel ghost-border rounded-3xl p-8 relative overflow-hidden shadow-2xl hover:neural-glow transition-all duration-500">
         <div className="absolute top-0 right-0 p-8 opacity-[0.03] pointer-events-none transform rotate-12 scale-150">
            <Cpu className="h-48 w-48 text-obs-primary" />
         </div>
         
         <div className="flex flex-col gap-8 relative z-10 w-full max-w-2xl">
            <div>
              <h2 className="text-xl font-bold font-heading flex items-center gap-3 mb-8">
                 <div className="h-10 w-10 rounded-xl bg-obs-primary/10 flex items-center justify-center border border-obs-primary/20">
                   <Cpu className="text-obs-primary" size={20} />
                 </div>
                 Model Configuration
              </h2>
            </div>
            
            <div className="grid gap-4">
              {/* LLM Detail */}
              <div className="flex items-center justify-between p-4 px-6 rounded-2xl bg-obs-surface-highest/40 ghost-border hover:bg-obs-surface-highest/60 transition-colors">
                <div className="flex items-center gap-4">
                  <div className="p-2 bg-obs-tertiary/10 rounded-lg">
                    <Database className="text-obs-tertiary" size={20} />
                  </div>
                  <div>
                    <p className="font-label text-[11px] text-obs-outline uppercase tracking-[0.1em] mb-0.5">LLM Engine</p>
                    <p className="font-sans text-sm font-semibold text-obs-on-surface">gemma4:8b (Ollama local)</p>
                  </div>
                </div>
                <div className="h-2.5 w-2.5 rounded-full bg-chart-4 animate-pulse shadow-[0_0_8px_var(--color-chart-4)]" />
              </div>
              
              {/* Embeddings Detail */}
              <div className="flex items-center justify-between p-4 px-6 rounded-2xl bg-obs-surface-highest/40 ghost-border hover:bg-obs-surface-highest/60 transition-colors">
                <div className="flex items-center gap-4">
                  <div className="p-2 bg-obs-primary/10 rounded-lg">
                    <Network className="text-obs-primary" size={20} />
                  </div>
                  <div>
                    <p className="font-label text-[11px] text-obs-outline uppercase tracking-[0.1em] mb-0.5">Embeddings</p>
                    <p className="font-sans text-sm font-semibold text-obs-on-surface">nomic-embed-text (768 dimensions)</p>
                  </div>
                </div>
                <div className="h-2.5 w-2.5 rounded-full bg-chart-4 shadow-[0_0_8px_var(--color-chart-4)]" />
              </div>
              
              {/* Ollama URL Detail */}
              <div className="flex items-center justify-between p-4 px-6 rounded-2xl bg-obs-surface-highest/40 ghost-border hover:bg-obs-surface-highest/60 transition-colors">
                <div className="flex items-center gap-4">
                  <div className="p-2 bg-accent/10 rounded-lg flex items-center justify-center font-mono text-xs font-bold text-accent w-9 h-9">
                    {`</>`}
                  </div>
                  <div>
                    <p className="font-label text-[11px] text-obs-outline uppercase tracking-[0.1em] mb-0.5">Ollama Rest API</p>
                    <p className="font-mono text-xs font-medium text-obs-on-surface-variant bg-obs-surface-lowest px-2 py-1 rounded inline-block mt-1 ghost-border">
                      http://localhost:11434
                    </p>
                  </div>
                </div>
                <div className="text-[10px] uppercase font-bold text-obs-on-surface bg-chart-4/20 border border-chart-4/30 px-2.5 py-1 rounded-md">
                  Alive
                </div>
              </div>
            </div>
         </div>
      </div>
    </div>
  );
}
