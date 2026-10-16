# Docker 微服務系統建置與學習記錄

本專案實作了一套基於 Docker 與 Docker Compose 的多容器微服務架構，涵蓋 Nginx 反向代理、Python (FastAPI) 後端 API 與 PostgreSQL 資料庫，並提供網頁儀表板驗證服務連通性。

---

## 一、 Docker 學習記錄與常用指令

### 1. 核心概念理解
- **Image（映像檔）**：唯讀的應用程式模板，包含執行所需的所有程式碼、依賴庫與環境。
- **Container（容器）**：由 Image 啟動的執行實例，具備獨立命名空間（Namespace）與檔案系統，容器彼此隔離。
- **Dockerfile**：定義自動構建自訂 Image 步驟的腳本文件。
- **Docker Compose**：多容器編排工具，透過單一 YAML 檔案定義網路、儲存卷與服務依賴關係。

### 2. 常用操作指令速查
```bash
# 映像檔操作
docker pull <image_name>          # 下載映像檔
docker images                     # 列出本地映像檔
docker rmi <image_id>             # 刪除映像檔

# 容器操作
docker run -d -p 8080:80 --name <name> <image>  # 背景執行並做連接埠對應
docker ps                         # 檢視運行中的容器
docker ps -a                      # 檢視全部容器（含已停止）
docker stop <container_name>      # 停止容器
docker rm <container_name>        # 刪除容器
docker logs -f <container_name>   # 即時查看容器日誌
docker exec -it <container_name> bash # 進入容器內部互動終端

# Docker Compose 操作
docker compose up -d --build      # 建置並在背景啟動所有服務
docker compose down               # 停止並移除所有服務與網路
docker compose ps                 # 查看編排中的容器狀態
docker compose logs -f            # 查看所有容器的綜合輸出日誌