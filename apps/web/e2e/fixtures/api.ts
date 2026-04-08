const API = process.env.E2E_API_URL ?? 'http://localhost:8000';

export async function seedUser(email: string, password: string) {
  const r = await fetch(`${API}/auth/register`, {
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
    const r = await fetch(`${API}/health`);
    return r.ok;
  } catch {
    return false;
  }
}
