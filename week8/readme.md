# SysPulse & NetGuard — 即時硬體遙測、網路連線審計與異常程序管控終端

## 一、專案簡介
**SysPulse & NetGuard** 是一套基於 Python `FastAPI`、`psutil` 與 `WebSocket` 建構的全端系統監控與資安網路審計工具。系統透過非同步架構每秒採集作業系統底層的硬體遙測數據，即時計算磁碟 I/O 與網路頻寬差值速率，並將本機所有活躍的 `TCP Socket` 網路連線反查對映至具體的執行程序（Process PID），同時具備系統負載超標自動抓包寫入 `SQLite` 資料庫與遠端一鍵終止異常程序之功能。

---

## 二、核心功能特色

1. **即時硬體遙測面板 (Real-Time Hardware Telemetry)**
   - 即時監控 CPU 總負載、當前運作時脈 (MHz) 與各邏輯核心 (Per-Core) 負載分佈。
   - 監控實體記憶體 (RAM) 與虛擬記憶體 (Swap) 使用率，並透過 `Chart.js` 繪製 60 秒動態趨勢波形圖。
   - 利用單調時鐘 (`time.monotonic()`) 精確計算兩次採樣間的**磁碟讀寫速率 (MB/s)** 與**網路上下行頻寬速率 (KB/s)**。

2. **高耗能程序排行與線上管控 (Process Management)**
   - 即時掃描系統所有運作中程序，依 CPU 與記憶體佔用率綜合排序前 15 名高耗能程序。
   - 支援前端即時關鍵字過濾（依程序名稱或 `PID` 搜尋）。
   - 提供安全防護機制的一鍵終止 (`Terminate`) 功能，自動阻擋對系統核心程序（如 `PID 0`、`PID 4` 及監控伺服器自身）的誤刪操作。

3. **活躍網路連線資安審計 (Active TCP Socket Auditing)**
   - 即時掃描本機所有處於 `ESTABLISHED`（已建立外部連線）與 `LISTEN`（監聽連接埠）狀態的 TCP 連線。
   - 自動將 `Local IP:Port` 與 `Remote IP:Port` 關聯反查至對應的應用程式名稱與 `PID`，快速揪出背景異常連外流量。

4. **系統卡頓元兇自動抓包與持久化 (Automated Anomaly Logging)**
   - 當 CPU 或 RAM 使用率突破自訂警戒門檻時，後端自動捕捉當下資源消耗排名第一的「元兇程序」，並透過 `aiosqlite` 非同步寫入本地 `syspulse.db` 資料庫。
   - 內建 15 秒冷卻機制 (`Cooldown`)，避免短時間內重複寫入相同峰值造成資料庫膨脹。

---

## 三、系統架構與檔案說明

```text
week8/
├── static/
│   └── index.html        # 前端戰情室儀表板 (Tailwind CSS + Chart.js + WebSocket Client)
├── database.py           # 非同步 SQLite 資料庫模組（負責異常峰值紀錄與歷史查詢）
├── monitor.py            # 作業系統底層遙測引擎（封裝 psutil 硬體採樣、速率差值計算與 Socket 反查）
├── main.py               # FastAPI 應用伺服器、背景常駐推播迴圈與 RESTful 控制 API
├── requirements.txt      # Python 套件依賴清單
└── README.md             # 專案說明文件