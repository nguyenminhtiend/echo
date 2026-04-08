import { expect, test } from '@playwright/test';

test('rag explorer search completes without error', async ({ page }) => {
  await page.goto('/dashboard/rag');
  await expect(page.getByRole('heading', { name: /RAG Explorer/i })).toBeVisible();

  const queryResponse = page.waitForResponse(
    (res) => res.url().includes('/api/rag/query') && res.status() === 200,
  );
  await page.getByPlaceholder(/search|query/i).fill('e2e exploration query');
  await page.getByRole('button', { name: /search/i }).click();
  await queryResponse;

  await expect(page.getByText(/No results found|score:/i).first()).toBeVisible({
    timeout: 15_000,
  });
});
