# 06 - Rust Web 待辦任務系統與 Playwright E2E 自動化測試

本專案為軟體工程課程作業（`_se/06`），實作一個基於 **Rust (Axum + Tokio)** 的輕量級待辦任務（To-Do List）Web 應用程式，並整合完整的多層次自動化測試架構，包含單元測試、API 整合測試，以及使用 **Playwright** 進行無頭瀏覽器（Headless Browser）端到端（E2E）測試。

---

## 🛠️ 技術棧 (Tech Stack)

| 類別                  | 技術與工具                               | 說明                                         |
| :-------------------- | :--------------------------------------- | :------------------------------------------- |
| **後端框架**          | Rust、`axum` (v0.7.9)、`tokio` (v1.54.1) | 非同步高效能 Web 伺服器與路由處理            |
| **中介軟體與序列化**  | `tower-http`、`serde`、`serde_json`      | 靜態檔案服務與 JSON 資料序列化               |
| **前端介面**          | HTML5 / CSS3 / Vanilla JavaScript        | 輕量化前端待辦事項介面 (`static/index.html`) |
| **單元與整合測試**    | Rust Built-in Test (`cargo test`)        | 驗證資料模型邏輯與 RESTful API 端點          |
| **端到端 (E2E) 測試** | `@playwright/test` (Chromium)            | 自動化模擬真實使用者於無頭瀏覽器操作流程     |

---

## 📂 專案目錄結構

```text
_se/06/
├── e2e/
│   └── task.spec.ts       # Playwright E2E 端到端測試腳本
├── src/
│   ├── main.rs            # Rust 伺服器啟動入口 (綁定 [http://127.0.0.1:3000](http://127.0.0.1:3000))
│   ├── lib.rs             # Axum 路由定義與 API 狀態處理邏輯
│   └── models.rs          # 待辦事項資料結構定義與單元測試
├── static/
│   └── index.html         # 前端使用者介面 (新增、查詢與刪除任務)
├── tests/
│   └── api_test.rs        # 後端 RESTful API 整合測試
├── Cargo.toml             # Rust 專案設定與相依套件清單
├── package.json           # Node.js / Playwright 測試環境設定
├── playwright.config.ts   # Playwright 設定檔 (支援自動啟動背景 Cargo 伺服器)
└── readme.md              # 專案說明文件
```

---

## 🚀 快速開始與執行方式

### 1. 啟動 Web 伺服器

在專案目錄 (`_se/06`) 下執行以下指令編譯並啟動後端服務：

```powershell
cargo run
```

伺服器啟動後，開啟瀏覽器前往 `http://127.0.0.1:3000` 即可使用待辦任務系統。

### 2. 執行 Rust 單元測試與 API 整合測試

驗證後端資料模型 (`src/models.rs`) 與 API 路由 (`tests/api_test.rs`) 是否運作正常：

```powershell
cargo test
```

### 3. 執行 Playwright E2E 端到端測試

`playwright.config.ts` 已配置 `webServer` 自動化啟動機制，執行測試時會自動在背景執行 `cargo run` 並等待 `http://127.0.0.1:3000` 就緒，無須手動開關伺服器：

```powershell
# 首次執行時安裝前端測試依賴與 Chromium 瀏覽器核心
npm install
npx playwright install chromium

# 執行 E2E 自動化測試
npx playwright test
```

---

## 🧪 E2E 測試案例與執行結果

在 `e2e/task.spec.ts` 中實作了兩項核心使用者情境測試：

1. **完整 CRUD 流程測試**：模擬使用者開啟網頁 ➔ 輸入並新增待辦任務 ➔ 驗證任務正確渲染於 DOM 清單中 ➔ 點擊刪除按鈕並確認任務自畫面移除。
2. **表單防呆驗證測試**：模擬使用者未輸入內容（空白）直接送出表單，驗證前端是否正確攔截並於畫面上呈現錯誤提示訊息。

### 測試通過終端機輸出紀錄

```text
Running 2 tests using 1 worker

  ✓  1 [chromium] › e2e\task.spec.ts:4:7 › 待辦任務端到端測試 (E2E) › 完整流程：瀏覽網頁 -> 新增任務 -> 驗證清單 -> 刪除任務 (608ms)
  ✓  2 [chromium] › e2e\task.spec.ts:30:7 › 待辦任務端到端測試 (E2E) › 表單驗證：輸入為空時應於畫面上呈現錯誤提示 (141ms)

  2 passed (2.8s)
```

---

## 💡 開發與環境排錯紀錄 (Troubleshooting)

在 Windows 環境下建置 Rust 與 Playwright 整合測試時，針對下列環境問題進行了排錯與優化：

### 1. Playwright 設定檔型別檢查 (`playwright.config.ts`)

- **問題描述**：`reuseExistingServer: !process.env.CI` 在未設定全域 Node 型別配置時，VS Code TypeScript 檢查器會提示 `找不到名稱 'process' (ts(2580))`。
- **解決方案**：安裝 `@types/node` 開發依賴，並將本地測試環境設定調整為 `reuseExistingServer: true`，確保本地重複執行測試時能高效重用已啟動的 Rust 伺服器。

### 2. Windows 編譯器連結器 (`link.exe`) 與中文路徑相容性問題

- **問題描述**：
  1. Windows 預設的 `x86_64-pc-windows-msvc` 工具鏈依賴龐大的 Visual Studio C++ Build Tools，未安裝時會出現 `error: linker 'link.exe' not found`。
  2. 改用輕量級 `stable-x86_64-pc-windows-gnu` 與 WinLibs MinGW 編譯器後，GNU 的 `dlltool.exe` 與 `ld.exe` 在讀取包含中文字元的 Windows 使用者路徑（`C:\Users\<中文使用者名稱>\...`）時，會因非 ASCII 字元編碼問題報錯 (`Can't open def file` 與 `cannot find libstd-*.rlib: Invalid argument`)。
- **解決方案**：
  將 Rust 工具鏈目錄、編譯目標暫存區與系統暫存變數重新指向純英文路徑，徹底避開 MinGW 連結器對中文路徑的限制：

```powershell
# 將環境變數永久寫入 Windows 使用者設定，解決中文路徑編譯問題
[Environment]::SetEnvironmentVariable("RUSTUP_HOME", "C:\rustup", "User")
[Environment]::SetEnvironmentVariable("CARGO_TARGET_DIR", "C:\cargo-target", "User")
[Environment]::SetEnvironmentVariable("TEMP", "C:\temp", "User")
[Environment]::SetEnvironmentVariable("TMP", "C:\temp", "User")
```