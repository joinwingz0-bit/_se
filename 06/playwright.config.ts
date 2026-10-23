import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  use: {
    baseURL: 'http://127.0.0.1:3000',
    headless: true, // 使用無頭瀏覽器
    trace: 'on-first-retry',
  },
  // 執行 E2E 測試前，Playwright 會自動在背景執行 cargo run 啟動 Rust 伺服器
  webServer: {
    command: 'cargo run',
    url: 'http://127.0.0.1:3000',
    reuseExistingServer: true,
    timeout: 60 * 1000,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});