import { test, expect } from '@playwright/test';

test.describe('Frontend Auth Flow', () => {
  test('login page loads', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/.*login.*/);
    const content = await page.content();
    expect(content).toContain('ScienceClaw');
  });

  test('home page reachable', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    const content = await page.content();
    expect(content).toContain('ScienceClaw');
  });
});
