const WEB = process.env.E2E_BASE_URL ?? 'http://localhost:3000';
const API = process.env.E2E_API_URL ?? 'http://localhost:8000';

export async function seedUser(email: string, password: string) {
  const r = await fetch(`${WEB}/api/auth/sign-up/email`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ email, password, name: 'E2E' }),
  });
  if (!r.ok && r.status !== 409) {
    throw new Error(`seedUser failed: ${r.status}`);
  }
}

export async function apiHealthy(): Promise<boolean> {
  try {
    const [webRes, apiRes] = await Promise.all([
      fetch(WEB, { method: 'GET' }),
      fetch(`${API}/health`),
    ]);
    return webRes.ok && apiRes.ok;
  } catch {
    return false;
  }
}
