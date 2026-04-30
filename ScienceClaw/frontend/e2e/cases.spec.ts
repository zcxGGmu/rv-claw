import { test, expect } from '@playwright/test';

test.describe('Cases Pipeline Flow', () => {
  test('cases page loads', async ({ page }) => {
    await page.goto('/chat/cases');
    await page.waitForLoadState('networkidle');
    const content = await page.content();
    expect(content).toContain('ScienceClaw');
  });
});
