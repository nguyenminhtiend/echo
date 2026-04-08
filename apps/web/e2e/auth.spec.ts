import { expect, test } from '@playwright/test';

const baseURL = process.env.E2E_BASE_URL ?? 'http://localhost:3000';

const email = `e2e+${Date.now()}@example.com`;
const password = 'Password123!';

test('register -> login -> dashboard', async ({ page }) => {
  await page.goto('/register');
  await page.getByLabel(/name/i).fill('E2E User');
  await page.getByLabel(/email/i).fill(email);
  await page.getByLabel(/password/i).fill(password);
  await page.getByRole('button', { name: /sign up|register|create account/i }).click();

  await expect(page).toHaveURL(/\/dashboard/);
  await expect(page.getByRole('heading', { name: /dashboard|overview/i })).toBeVisible();
});

test('login existing user lands on dashboard', async ({ page, request }) => {
  const existing = `seeded+${Date.now()}@example.com`;
  await request.post(`${baseURL}/api/auth/sign-up/email`, {
    data: { email: existing, password, name: 'Seed' },
  });

  await page.goto('/login');
  await page.getByLabel(/email/i).fill(existing);
  await page.getByLabel(/password/i).fill(password);
  await page.getByRole('button', { name: /sign in|log in/i }).click();

  await expect(page).toHaveURL(/\/dashboard/);
});
