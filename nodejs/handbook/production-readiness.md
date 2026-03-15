# 生產環境部署與維運最佳實踐 / Production Readiness & Operations Best Practices

## Mental model｜心智模型

在開發環境（Development）與生產環境（Production）之間，Node.js 的運作邏輯存在巨大的鴻溝。要跨越這個鴻溝，你需要建立以下的心智模型：

### 1. 寵物 vs. 牲畜 (Pets vs. Cattle)
在開發時，你的 Node.js process 像是「寵物」，你細心呵護它，手動啟動它，看著 console log。但在生產環境，它應該是「牲畜」。
- **Disposable（可拋棄）**：任何一個實體（Instance）掛掉都應該能自動被替換，而不影響整體服務。
- **Stateless（無狀態）**：不要在記憶體中儲存 Session 或狀態，因為 Process 隨時會重啟。狀態應存於 Redis 或 DB。

### 2. 單執行緒的脆弱性 (The Fragility of Single Thread)
Node.js 的 Event Loop 是單執行緒的。這意味著：
- **沒有隔離**：一個未捕獲的異常（Uncaught Exception）會導致整個 Process 崩潰。
- **沒有併發計算**：單一 Process 只能利用一顆 CPU 核心。
- **結論**：你必須依賴外部工具（Process Manager 或 Container Orchestrator）來確保高可用性（High Availability）與負載平衡。

### 3. 優雅的離場 (Graceful Shutdown)
想像你的應用程式是一間餐廳。當你要打烊（部署新版或擴展縮編）時，你不能直接把客人的盤子收走趕人（`kill -9`）。你需要：
1.  掛上「準備打烊」的牌子（停止接收新 Request）。
2.  讓還在吃飯的客人吃完（處理完當前的 Request）。
3.  關燈鎖門（關閉 DB 連線、釋放資源）。
4.  離開（Process Exit）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Process Management & Clustering
不要在生產環境直接使用 `node index.js`。

- **PM2 (Virtual Machine / Bare Metal)**:
  - 使用 `pm2 start ecosystem.config.js`。
  - **Cluster Mode**: 設定 `instances: 'max'` 或 `instances: 2`，讓 PM2 自動利用多核 CPU 並負載平衡流量。
  - **Auto Restart**: 當 App 崩潰時自動重啟。

- **Docker / Kubernetes (Containerized)**:
  - 在容器化環境中，通常建議**不要**在容器內使用 PM2 的 Cluster Mode，而是讓 K8s 的 ReplicaSet 來管理水平擴展（Horizontal Scaling）。
  - **PID 1 Problem**: Node.js 不適合當 PID 1（它不會轉發 Signals 也不會處理 Zombie Processes）。請使用 `tini` 作為 entrypoint，或使用 `docker run --init`。

### 2. Graceful Shutdown Implementation
必須監聽系統訊號（Signals）並正確回應。

- **SIGTERM**: 這是 Orchestrator (如 K8s) 叫你「請停止」的訊號。
- **SIGINT**: 通常是開發者按 Ctrl+C 發出的訊號。

### 3. Health Checks (Liveness vs. Readiness)
不要只回傳 `200 OK`。

- **Liveness Probe (我還活著嗎？)**:
  - 檢查 Event Loop 是否阻塞。如果長時間未回應，應重啟 Process。
- **Readiness Probe (我能接客嗎？)**:
  - 檢查 DB 連線、Redis 連線是否正常。如果 DB 斷了，Load Balancer 應暫時停止派送流量給這個實體，而不是重啟它（重啟也連不上 DB）。

### 4. Logging & Observability
- **Structured Logging**: 使用 `pino` 或 `winston` 輸出 **JSON** 格式的 log。不要用 `console.log`（它是同步的且格式難以被 Log Aggregator 解析）。
- **Correlation ID**: 在 Request 進入時生成一個 UUID，並在所有的 Log 中帶上這個 ID，以便追蹤跨服務的請求路徑。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### ❌ Ignoring Uncaught Exceptions / Unhandled Rejections
- **錯誤做法**：在 `uncaughtException` 中只記錄 Log 但不退出 Process。
- **後果**：應用程式處於「不確定狀態（Corrupted State）」，可能會導致資料損毀或記憶體洩漏。
- **正確做法**：Log 錯誤 -> 執行 Graceful Shutdown -> `process.exit(1)` -> 讓 PM2/Docker 重啟它。

### ❌ Running as Root
- **錯誤做法**：在 Dockerfile 中直接以 root 身份執行 Node.js。
- **後果**：如果應用程式有 RCE（遠端代碼執行）漏洞，駭客將獲得容器的最高權限。
- **正確做法**：使用 `USER node` 指令切換到非特權使用者。

### ❌ Hard-coding Secrets
- **錯誤做法**：將 API Key 或 DB 密碼寫在 code 裡或 commit 到 git。
- **正確做法**：使用環境變數（Environment Variables），配合 `dotenv` (開發) 或 K8s Secrets (生產)。

### ❌ Blocking the Event Loop
- **錯誤做法**：在主執行緒進行繁重的 CPU 運算（如加密大量數據、影像處理）。
- **後果**：Health check 超時，導致無限重啟迴圈。
- **正確做法**：使用 Worker Threads 或將計算任務卸載到專門的微服務。

---

## Checklists & workflows｜檢查清單與流程

### Deployment Readiness Checklist
在部署到生產環境前，請確認以下項目：

- [ ] **Environment Variables**: `NODE_ENV` 設為 `production` (這會大幅優化 Express/Koa 等框架的效能)。
- [ ] **Process Manager**: 已設定 PM2 或 Docker Restart Policy (`always` or `on-failure`)。
- [ ] **Graceful Shutdown**: 已實作 `SIGTERM` 與 `SIGINT` 處理邏輯，並設定了強制退出的 timeout（例如 10秒）。
- [ ] **Security**: 已使用 `helmet` 設定 HTTP Headers，並移除 `X-Powered-By: Express`。
- [ ] **Logging**: Log 輸出為 JSON 格式，且 Log Level 可透過 ENV 動態調整。
- [ ] **Error Handling**: 全域捕捉了 `uncaughtException` 與 `unhandledRejection`。
- [ ] **NPM Audit**: 執行過 `npm audit` 確保相依套件無重大漏洞。
- [ ] **Memory Limit**: 若在容器內，已設定 Node.js 的 `--max-old-space-size` (通常設為容器記憶體限制的 75-80%)。

---

## Real-world examples｜實戰案例

### 1. Robust Graceful Shutdown Pattern
這是一個可以直接套用的 Boilerplate，處理了 HTTP Server 與 Database 的關閉順序。

```javascript
const express = require('express');
const app = express();
const server = app.listen(3000);

// 模擬資料庫連線
const db = {
  close: () => console.log('Database connection closed.')
};

function gracefulShutdown(signal) {
  console.info(`${signal} signal received: closing HTTP server`);
  
  // 1. 停止接收新的連線
  server.close(() => {
    console.log('HTTP server closed');
    
    // 2. 關閉資料庫連線或其他資源
    db.close();
    
    // 3. 退出 Process (0 代表正常退出)
    process.exit(0);
  });

  // 4. 強制退出機制：如果 10 秒內沒關完，強制殺掉
  setTimeout(() => {
    console.error('Could not close connections in time, forcefully shutting down');
    process.exit(1);
  }, 10000);
}

// 監聽訊號
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// 處理未捕獲的異常：必須退出
process.on('uncaughtException', (err) => {
  console.error('Uncaught Exception:', err);
  process.exit(1); // 讓 Process Manager 重啟
});
```

### 2. PM2 Ecosystem Config (ecosystem.config.js)
用於 VM 或 Bare Metal 部署的標準配置。

```javascript
module.exports = {
  apps: [{
    name: "my-api-service",
    script: "./dist/index.js",
    instances: "max",       // 使用所有 CPU 核心
    exec_mode: "cluster",   // 開啟 Cluster Mode
    env_production: {
      NODE_ENV: "production",
      PORT: 8080
    },
    max_memory_restart: "1G", // 記憶體洩漏防護：超過 1G 自動重啟
    wait_ready: true,         // 等待應用程式發送 process.send('ready')
    listen_timeout: 5000,     // 如果 5秒內沒 ready 視為失敗
    kill_timeout: 3000        // 給 Graceful Shutdown 3秒時間
  }]
}
```

### 3. Dockerfile Best Practice (Production Stage)
多階段建構（Multi-stage build）與安全性設定。

```dockerfile
# Build Stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production Stage
FROM node:18-alpine
WORKDIR /app

# 安裝 tini 以解決 PID 1 問題
RUN apk add --no-cache tini

# 僅複製必要的檔案
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package*.json ./
# 僅安裝 production dependencies
RUN npm ci --only=production

# 切換非 root 使用者
USER node

# 使用 tini 作為 entrypoint
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "dist/index.js"]
```