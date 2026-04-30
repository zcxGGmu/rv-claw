import { test, expect } from '@playwright/test';

test.describe('Chat Flow', () => {
  test('home page structure loads', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    const content = await page.content();
    expect(content).toContain('ScienceClaw');
  });
});
