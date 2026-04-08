import { expect, test } from '@playwright/test';

test('rag explorer search returns results', async ({ page, request }) => {
  // seed a chunk directly via API
  await request.post('http://localhost:8000/rag/chunks', {
    data: {
      source_path: 'e2e/sample.py',
      text: "def greet(name): return f'hello {name}'",
    },
  });

  await page.goto('/dashboard/rag');
  await page.getByPlaceholder(/search|query/i).fill('greet');
  await page.getByRole('button', { name: /search/i }).click();

  await expect(page.getByText(/greet/)).toBeVisible({ timeout: 10_000 });
});
