import { headers } from 'next/headers';
import Link from 'next/link';
import { redirect } from 'next/navigation';
import { auth } from '@/lib/auth';
import {
  Activity,
  Bot,
  Code2,
  FileText,
  ShieldCheck,
  Terminal,
} from 'lucide-react';

export default async function Home() {
  const session = await auth.api.getSession({ headers: await headers() });
  if (session) {
    redirect('/dashboard');
  }

  return (
    <div className="flex min-h-screen flex-col bg-obs-surface text-foreground overflow-hidden relative">
      {/* Background ambient lighting */}
      <div className="absolute inset-0 z-0 pointer-events-none neural-glow opacity-30 mix-blend-screen" />
      <div className="absolute top-[20%] left-[50%] -translate-x-1/2 w-full max-w-[800px] h-[500px] bg-obs-primary/10 blur-[120px] rounded-full pointer-events-none" />
      
      <main className="relative z-10 flex flex-1 flex-col items-center px-6 py-20 lg:py-32 scroll-smooth">
        {/* Hero Section */}
        <div className="mx-auto max-w-4xl text-center flex flex-col items-center">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 mb-8 rounded-full glass-panel ghost-border text-xs font-mono text-obs-primary tracking-[0.15em] uppercase shimmer-border">
            <span className="relative flex h-2 w-2">
              <span className="animate-pulse absolute inline-flex h-full w-full rounded-full bg-obs-primary opacity-80"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-obs-primary"></span>
            </span>
            System Online
          </div>
          <h1 className="mb-6 font-heading text-5xl md:text-7xl font-bold tracking-tight text-balance leading-tight drop-shadow-sm">
            Enterprise Cognitive Hub &amp; <br />
            <span className="lithic-glow text-transparent bg-clip-text">Orchestration</span>
          </h1>
          <p className="mb-12 text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto font-sans text-balance opacity-90 leading-relaxed">
            A self-hosted, multi-agent AI platform that orchestrates specialized agents across your
            SDLC — from code and reviews to tests, security, docs, and architecture.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-24 w-full sm:w-auto">
            <Link
              href="/login"
              className="inline-flex h-12 w-full sm:min-w-[160px] items-center justify-center rounded-xl ghost-border glass-panel px-8 text-sm font-label font-medium transition-all hover:bg-obs-surface-high hover:neural-glow hover:text-obs-primary"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="inline-flex h-12 w-full sm:min-w-[160px] items-center justify-center rounded-xl bg-obs-primary px-8 text-sm font-label font-semibold text-primary-foreground transition-all hover:scale-[1.02] active:scale-95 shadow-[0_0_30px_rgba(208,188,255,0.3)] hover:shadow-[0_0_40px_rgba(208,188,255,0.5)]"
            >
              Get Started
            </Link>
          </div>
        </div>

        {/* Bento Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto w-full z-10">
          
          {/* Main Card */}
          <div className="md:col-span-2 glass-panel ghost-border rounded-[2rem] p-8 md:p-10 relative overflow-hidden group hover:neural-glow transition-all duration-500 hover:-translate-y-1">
            <div className="absolute -right-16 -top-16 opacity-[0.03] group-hover:opacity-10 transition-opacity duration-700 pointer-events-none transform group-hover:rotate-12 group-hover:scale-110">
              <Bot size={300} strokeWidth={1} className="text-obs-primary" />
            </div>
            <div className="relative z-10 flex flex-col h-full justify-between">
              <div>
                <h3 className="font-heading text-2xl font-bold mb-4 flex items-center gap-3 drop-shadow-md">
                   <div className="p-2 rounded-xl bg-obs-surface-high/50 ghost-border">
                     <Bot className="text-obs-primary" size={24} />
                   </div>
                   Multi-Agent Engine
                </h3>
                <p className="text-muted-foreground font-sans max-w-sm leading-relaxed text-[15px]">
                  Deploy autonomous AI pods that work collectively to review, rewrite, and reinforce your entire codebase in real time.
                </p>
              </div>
              <div className="mt-8 flex flex-wrap gap-3">
                <div className="px-4 py-1.5 rounded-lg bg-obs-surface-highest/60 ghost-border font-mono text-[11px] uppercase tracking-wider text-obs-on-surface-variant flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-chart-4 shadow-[0_0_5px_var(--color-chart-4)]"></span> Model independent
                </div>
                <div className="px-4 py-1.5 rounded-lg bg-obs-surface-highest/60 ghost-border font-mono text-[11px] uppercase tracking-wider text-obs-on-surface-variant flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-chart-2 shadow-[0_0_5px_var(--color-chart-2)]"></span> Private network
                </div>
              </div>
            </div>
          </div>

          <div className="glass-panel ghost-border rounded-[2rem] p-8 md:p-10 group hover:neural-glow transition-all duration-500 flex flex-col justify-between hover:-translate-y-1">
            <div>
              <div className="w-12 h-12 rounded-2xl bg-obs-tertiary/10 flex items-center justify-center mb-6 border border-obs-tertiary/20">
                <Activity className="text-obs-tertiary" size={24} />
              </div>
              <h3 className="font-heading text-xl font-bold mb-3">Real-time CI/CD</h3>
            </div>
            <p className="text-[15px] text-muted-foreground font-sans leading-relaxed">Agents intercept PRs before they merge, catching regressions instantly with near-zero latency.</p>
          </div>

          <div className="glass-panel ghost-border rounded-[2rem] p-8 md:p-10 group hover:neural-glow transition-all duration-500 flex flex-col justify-between hover:-translate-y-1">
            <div>
              <div className="w-12 h-12 rounded-2xl bg-obs-primary/10 flex items-center justify-center mb-6 border border-obs-primary/20">
                <ShieldCheck className="text-obs-primary" size={24} />
              </div>
              <h3 className="font-heading text-xl font-bold mb-3">Zero Trust</h3>
            </div>
            <p className="text-[15px] text-muted-foreground font-sans leading-relaxed">Your code stays on your machine. Data privacy and isolation guaranteed by design.</p>
          </div>

          <div className="md:col-span-2 glass-panel ghost-border rounded-[2rem] p-8 md:p-10 group hover:neural-glow transition-all duration-500 relative flex flex-col justify-center overflow-hidden hover:-translate-y-1">
             <div className="absolute right-0 top-0 w-1/2 h-full bg-gradient-to-l from-obs-surface-high/50 to-transparent pointer-events-none" />
             <div className="relative z-10 flex flex-col md:flex-row items-center gap-8">
                <div className="flex-1">
                  <div className="w-12 h-12 rounded-2xl bg-accent/10 flex items-center justify-center mb-6 border border-accent/20">
                    <Terminal className="text-accent" size={24} />
                  </div>
                  <h3 className="font-heading text-xl font-bold mb-3">Local Environment</h3>
                  <p className="text-[15px] text-muted-foreground font-sans leading-relaxed">Run the entire platform locally inside Docker. Minimal setup, zero external dependencies required.</p>
                </div>
                <div className="flex-1 w-full bg-[#0a0a0c]/80 rounded-2xl p-5 font-mono text-sm text-obs-on-surface-variant ghost-border shadow-inner">
                  <div className="flex gap-2 mb-4 border-b border-white/5 pb-3">
                    <div className="w-3 h-3 rounded-full bg-obs-error/70"></div>
                    <div className="w-3 h-3 rounded-full bg-obs-tertiary/70"></div>
                    <div className="w-3 h-3 rounded-full bg-chart-4/70"></div>
                  </div>
                  <div className="space-y-1">
                    <div><span className="text-chart-4 font-bold select-none">$</span> docker compose up -d</div>
                    <div><span className="text-chart-4 font-bold select-none">$</span> echo-cli start agents</div>
                    <div className="text-muted-foreground pt-2 animate-pulse"># All pods operational.</div>
                  </div>
                </div>
             </div>
          </div>
          
        </div>
      </main>
    </div>
  );
}
