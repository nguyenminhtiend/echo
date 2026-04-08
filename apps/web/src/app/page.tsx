import { headers } from 'next/headers';
import Link from 'next/link';
import { redirect } from 'next/navigation';
import { auth } from '@/lib/auth';

export default async function Home() {
  const session = await auth.api.getSession({ headers: await headers() });
  if (session) {
    redirect('/dashboard');
  }

  return (
    <div className="flex min-h-screen flex-col bg-zinc-950 text-zinc-50">
      <main className="flex flex-1 flex-col items-center justify-center px-6 py-24">
        <div className="mx-auto max-w-2xl text-center">
          <p className="mb-3 text-sm font-medium uppercase tracking-[0.2em] text-emerald-400/90">
            E.C.H.O.
          </p>
          <h1 className="mb-4 text-4xl font-bold tracking-tight sm:text-5xl">
            Enterprise Cognitive Hub &amp; Orchestration
          </h1>
          <p className="mb-2 text-lg text-zinc-400">
            A self-hosted, multi-agent AI platform that orchestrates specialized agents across your
            SDLC — from code and reviews to tests, security, docs, and architecture.
          </p>
          <p className="mb-10 text-sm text-zinc-500">
            Run locally with your own models. Your code stays on your machine.
          </p>
          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link
              href="/login"
              className="inline-flex h-11 min-w-[140px] items-center justify-center rounded-lg border border-zinc-600 bg-transparent px-6 text-sm font-medium text-zinc-100 transition-colors hover:border-zinc-400 hover:bg-zinc-900"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="inline-flex h-11 min-w-[140px] items-center justify-center rounded-lg bg-emerald-500 px-6 text-sm font-semibold text-zinc-950 transition-colors hover:bg-emerald-400"
            >
              Get Started
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
