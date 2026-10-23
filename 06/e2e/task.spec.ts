import { test, expect } from '@playwright/test';

test.describe('待辦任務端到端測試 (E2E)', () => {
  test('完整流程：瀏覽網頁 -> 新增任務 -> 驗證清單 -> 刪除任務', async ({ page }) => {
    // 1. 造訪頁面
    await page.goto('/');
    await expect(page).toHaveTitle('待辦任務管理系統');

    // 2. 輸入任務標題並點擊新增
    const taskInput = page.getByTestId('task-input');
    const addButton = page.getByTestId('add-button');

    await taskInput.fill('執行 Playwright 自動化測試');
    await addButton.click();

    // 3. 驗證任務出現在清單中
    const taskItem = page
      .getByTestId('task-item')
      .filter({ hasText: '執行 Playwright 自動化測試' });
    await expect(taskItem).toBeVisible();

    // 4. 點擊該項目的刪除按鈕
    const deleteButton = taskItem.getByTestId('delete-button');
    await deleteButton.click();

    // 5. 驗證該項目已從畫面中消失
    await expect(taskItem).not.toBeVisible();
  });

  test('表單驗證：輸入為空時應於畫面上呈現錯誤提示', async ({ page }) => {
    await page.goto('/');

    // 直接點擊新增（input 為空）
    const addButton = page.getByTestId('add-button');
    await addButton.click();

    // 驗證錯誤訊息元素
    const errorMsg = page.getByTestId('error-message');
    await expect(errorMsg).toBeVisible();
    await expect(errorMsg).toHaveText('標題不能為空');
  });
});