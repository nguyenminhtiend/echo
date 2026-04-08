import { expect, test } from '@playwright/test';

const baseURL = process.env.E2E_BASE_URL ?? 'http://localhost:3000';

const email = `runner+${Date.now()}@example.com`;
const password = 'Password123!';

test.beforeEach(async ({ page, request }) => {
  await request.post(`${baseURL}/api/auth/sign-up/email`, {
    data: { email, password, name: 'Runner' },
  });
  await page.goto('/login');
  await page.getByLabel(/email/i).fill(email);
  await page.getByLabel(/password/i).fill(password);
  await page.getByRole('button', { name: /sign in|log in/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);
});

test('submit agent task -> run appears -> trace viewer opens', async ({ page }) => {
  await page.goto('/dashboard/agents');
  await page.getByLabel(/task/i).fill('Write a hello world function');
  await page.getByRole('button', { name: /submit|run|start/i }).click();

  const runLink = page
    .locator('a')
    .filter({ hasText: /hello world/i })
    .first();
  await expect(runLink).toBeVisible({ timeout: 15_000 });

  await runLink.click();
  await expect(page.getByText(/trace|supervisor|coder/i).first()).toBeVisible({ timeout: 15_000 });
});
