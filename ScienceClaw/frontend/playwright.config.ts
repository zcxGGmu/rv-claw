import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E configuration for RV-Claw.
 *
 * Prerequisites:
 *   1. Start infrastructure: docker compose up -d mongo postgres redis
 *   2. Start backend: cd ScienceClaw/backend && uvicorn backend.main:app --host 0.0.0.0 --port 12001
 *   3. Install browsers: npx playwright install chromium
 *
 * Run tests:
 *   npm run test:e2e
 */
export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['html', { open: 'never' }], ['list']],

  use: {
    // Frontend base URL (Vite dev server)
    baseURL: 'http://localhost:5173',
    // Backend API base URL for request fixture
    extraHTTPHeaders: {
      'Accept': 'application/json',
    },
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
