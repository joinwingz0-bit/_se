# ⚡ Cloudflare 邊緣工作台 (Edge Workspace)

本專案為部署於 **Cloudflare Workers & Pages** 的全端網頁應用程式，結合靜態前端頁面與 Serverless 邊緣運算 API，提供即時節點偵測與個人待辦事項管理功能。

## 🌐 線上展示 (Live Demo)

- **網站首頁**：https://my-edge-workspace.s111410507.workers.dev
- **後端 API 測試**：https://my-edge-workspace.s111410507.workers.dev/api/hello

---

## ✨ 功能特色

1. **Cloudflare 邊緣節點即時檢測**：透過呼叫 Cloudflare 內建的 `/cdn-cgi/trace` 端點，自動偵測並顯示訪客連線的機房節點（Colo，如台北 `TPE`）、所在地區、HTTP 協定版本與 TLS 加密狀態。
2. **個人待辦事項清單 (Todo List)**：支援新增、勾選完成、刪除待辦事項，並透過瀏覽器 `localStorage` 自動保存資料，重新整理頁面也不會遺失。
3. **Serverless 後端 API 路由**：利用 Cloudflare Workers 攔截 `/api/hello` 路徑，回傳包含伺服器時間與邊緣節點資訊的動態 JSON 資料。

---

## 📁 專案目錄結構

```text
week9/
├── public/
│   └── index.html       # 前端網頁介面 (Tailwind CSS + Vanilla JS)
├── src/
│   └── index.js         # Cloudflare Worker 後端路由與 API 邏輯
├── wrangler.jsonc       # Cloudflare Wrangler 部署與靜態資源設定檔
└── readme.md            # 專案說明文件