# 生產環境準備度：從 Docker 到編排系統 / Production Readiness: From Docker to Orchestration

## Mental model｜心智模型

### 1. 從「寵物」到「牲畜」 (Pets vs. Cattle)
在單機 Docker 或開發環境中，我們傾向於像照顧寵物一樣對待容器：我們知道它們的名字（Container Name），如果它們生病（Crash）了，我們會手動去重啟或修復。

進入編排系統（Orchestration，如 K8s, Swarm, ECS）的世界，心智模型必須轉變為「牲畜管理」：
- **不可變性 (Immutability)**：容器一旦啟動就不再變更。需要更新時，是殺掉舊的，換上新的。
- **短暫性 (Ephemerality)**：隨時準備好容器會被重啟、遷移或銷毀。
- **自動化 (Automation)**：不再依賴人工介入單一容器的生命週期，而是定義「期望狀態 (Desired State)」。

### 2. 應用程式即契約 (The Application as a Contract)
在編排系統中，Docker Image 不僅僅是程式碼的打包，它是一份與基礎設施簽訂的「契約」。
- **契約輸入**：環境變數 (Config)、Secret。
- **契約輸出**：標準輸出 (Logs)、健康狀態 (Health Checks)。
- **契約行為**：優雅停機 (Graceful Shutdown)、資源限制 (Resource Limits)。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 嚴格的無狀態設計 (Strict Statelessness)
這是擴展（Scaling）的基石。
- **Pattern**: 任何應用程式產生的持久化數據（User Uploads, Session Data）都**不能**寫入容器的本地檔案系統。
- **Implementation**:
  - Session $\rightarrow$ Redis / Memcached。
  - File Uploads $\rightarrow$ S3 / GCS / Azure Blob Storage。
  - Logs $\rightarrow$ Stdout/Stderr (由 Log Driver 收集)。

### 2. 生命週期探針 (Lifecycle Probes)
編排系統需要知道何時該重啟容器，何時該發送流量。
- **Liveness Probe (存活探針)**: "Am I running?"
  - 如果失敗，編排系統會重啟容器。用於偵測 Deadlock。
- **Readiness Probe (就緒探針)**: "Am I ready to serve traffic?"
  - 如果失敗，編排系統會停止發送流量（Load Balancer 移除 Endpoint），但**不會**重啟容器。用於等待資料庫連線或暖機。

### 3. 優雅停機 (Graceful Shutdown)
當編排系統進行 Rolling Update 或縮容時，會發送 `SIGTERM` 信號。
- **Best Practice**: 應用程式必須捕捉 `SIGTERM`。
- **Action**:
  1. 停止接收新的 Request。
  2. 完成正在處理中的 Request（在 timeout 允許範圍內）。
  3. 關閉資料庫連線與 File Handles。
  4. 退出 Process。
- **Note**: 如果你的 Entrypoint 是一個 Shell script，記得使用 `exec` 啟動 App，否則信號無法傳遞給子進程。

### 4. 配置外置化 (Externalized Configuration)
遵循 12-Factor App 原則。
- **Pattern**: 映像檔 (Image) 應該是「環境無關 (Environment Agnostic)」的。同一個 Image 應該能跑在 Dev, Staging, 和 Prod。
- **Implementation**: 使用環境變數 (Environment Variables) 或掛載 ConfigMap/Secret 來注入配置，絕對不要在 build time 將設定檔燒錄進 Image。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "PID 1" Zombie Problem
- **Anti-pattern**: 容器內的應用程式沒有正確處理 Unix Signals，導致 `docker stop` 等很久（直到被 `SIGKILL` 強殺）。
- **Why**: Linux kernel 對 PID 1 有特殊處理，預設不會轉發信號。
- **Fix**: 使用 `tini` 作為 init process（`docker run --init` 或在 Dockerfile 中使用 `ENTRYPOINT ["/usr/bin/tini", "--", "myapp"]`）。

### 2. 硬編碼 IP 或依賴啟動順序 (Hardcoded IPs & Startup Order)
- **Anti-pattern**: 依賴 `depends_on` 來確保 DB 先啟動，或者在程式碼中寫死其他容器的 IP。
- **Reality**: 在分散式系統中，Pod/Container IP 是動態變化的，且隨時可能重啟。
- **Fix**:
  - 使用 Service Discovery (DNS 名稱)。
  - 實作 "Wait-for-it" 邏輯或重試機制（Retry Logic），應用程式應能容忍 DB 暫時不可用並自我恢復。

### 3. 混合構建與執行環境 (Mixed Build & Runtime)
- **Anti-pattern**: 生產環境 Image 包含編譯器 (GCC, JDK)、原始碼或測試工具。
- **Risk**: 增加攻擊面，映像檔體積過大導致擴展變慢。
- **Fix**: 嚴格執行 **Multi-stage Builds**，產出的 Image 只包含 Binary 或 Runtime 必需品（Distroless 是一個好選擇）。

### 4. 本地掛載依賴 (Volume Mount Dependency)
- **Anti-pattern**: 在 Docker Compose 中習慣使用 `-v ./code:/app`，並期望在生產環境也這樣做。
- **Pitfall**: 在跨節點叢集中，Host Path Mount 通常不可行（除非使用 NFS/Ceph 等共享儲存，但這會引入複雜度）。
- **Fix**: 將程式碼完全打包進 Image。

---

## Checklists & workflows｜檢查清單與流程

在將服務從單機 Docker Compose 遷移至 Kubernetes 或 Swarm 之前，請執行此 Readiness Check：

### Architecture & State (架構與狀態)
- [ ] **Stateless**: 確認沒有依賴本地儲存的狀態（Session, Files）。
- [ ] **Config**: 所有配置是否都已提取為環境變數？
- [ ] **Secrets**: 敏感資訊（API Keys, Passwords）是否已從 Image 和 Git 中移除？

### Observability (可觀測性)
- [ ] **Logs**: Log 是否直接輸出到 `stdout`/`stderr`（JSON 格式尤佳）？
- [ ] **Health Checks**: 是否已實作 `/healthz` (Liveness) 和 `/ready` (Readiness) API 端點？
- [ ] **Metrics**: 是否有 Prometheus metrics endpoint (可選但建議)？

### Lifecycle & Reliability (生命週期與可靠性)
- [ ] **Signal Handling**: 測試過發送 `docker stop` 時，App 是否能優雅關閉？
- [ ] **Retry Logic**: DB 連線失敗時，App 會崩潰還是會重試？
- [ ] **Resource Limits**: 是否已評估 CPU/Memory 的 Request 與 Limit 基準值？

### Security (安全性)
- [ ] **Non-root**: Dockerfile 是否包含 `USER <uid>` 指令，避免以 root 身份執行？
- [ ] **Base Image**: 是否使用了最小化且掃描過漏洞的 Base Image？

---

## Real-world examples｜實戰案例

### Scenario: Legacy Node.js App Migration
**背景**：一個傳統 Node.js 應用，使用本地檔案系統儲存使用者上傳的頭像，並使用 `pm2` 在容器內管理多個進程。

#### ❌ Before (Not Production Ready)
*Dockerfile:*
```dockerfile
FROM node:14
WORKDIR /app
COPY . .
# Anti-pattern: Running as root by default
# Anti-pattern: Installing dev dependencies
RUN npm install 
CMD ["pm2-runtime", "app.js"] 
```
*Code Issue:*
```javascript
// Anti-pattern: Local file write
fs.writeFileSync('./public/uploads/' + filename, data);
```

#### ✅ After (Orchestration Ready)
*Refactored Code:*
```javascript
// Pattern: External storage (S3)
await s3Client.send(new PutObjectCommand({ Bucket: process.env.BUCKET, Key: filename, Body: data }));

// Pattern: Graceful Shutdown
process.on('SIGTERM', () => {
  server.close(() => {
    console.log('Process terminated');
  });
});
```

*Dockerfile (Optimized):*
```dockerfile
# Pattern: Multi-stage build
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
# Pattern: Non-root user
USER node 
# Pattern: Tini for signal handling
RUN apk add --no-cache tini
ENTRYPOINT ["/sbin/tini", "--"]
# Pattern: Direct execution (let K8s handle replication, not pm2)
CMD ["node", "app.js"]
```

*Kubernetes Readiness (Conceptual YAML):*
```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 3000
  initialDelaySeconds: 3
readinessProbe:
  httpGet:
    path: /ready
    port: 3000
env:
  - name: BUCKET_NAME
    valueFrom:
      configMapKeyRef:
        name: app-config
        key: bucket
```

這個轉變確保了應用程式可以隨意擴展到 10 個副本，且任何一個副本掛掉都不會導致數據丟失或服務中斷。