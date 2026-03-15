# 常見反模式與避坑指南 / Common Anti-patterns and Pitfalls

## Mental model｜心智模型

### 1. 容器是「進程」而非「虛擬機」
**Containers are Processes, not VMs.**
最根本的認知誤區在於將容器視為輕量級的 VM。
- **VM 思維**：我需要 SSH 進去安裝更新、我需要在裡面跑 Systemd 管理多個服務、我需要手動修改設定檔。
- **Docker 思維**：容器是不可變（Immutable）的單一進程封裝。如果需要變更，你應該重新構建映像檔（Rebuild Image），而不是修補運行中的容器。

### 2. 寵物 vs. 牲畜 (Pets vs. Cattle)
- **Pets (VMs)**：你給它取名字，生病了（故障）你會細心照料（修復）。
- **Cattle (Containers)**：它們只有編號，生病了你會直接替換掉（Kill & Respawn）。
在 Docker 的世界裡，任何容器都應該是**隨時可被替換（Disposable）**的。

---

## Patterns & best practices｜常見模式與最佳實務

### The "One Process Per Container" Principle
每個容器應該只關注於運行一個主要進程（及其子進程）。
- **Why**: 這樣做可以讓 Logs 收集、健康檢查（Healthcheck）、水平擴展（Scaling）和錯誤隔離變得簡單且標準化。
- **How**: 你的 `ENTRYPOINT` 或 `CMD` 應該直接啟動應用程式（如 `node server.js` 或 `java -jar app.jar`），而不是啟動一個 shell script 去跑背景服務。

### Immutable Infrastructure (不可變基礎設施)
一旦映像檔構建完成，它在開發、測試、生產環境中應該是完全一致的。
- **Configuration**: 使用環境變數（Environment Variables）或掛載 ConfigMap 來注入不同環境的配置，而不是在構建時將配置寫死（Hardcode）。

### Graceful Shutdown Handling
容器編排系統（如 K8s 或 Docker Swarm）會發送 `SIGTERM` 信號來停止容器。
- **Pattern**: 確保你的應用程式能接收並處理 OS Signals，完成正在進行的請求後再退出。避免使用 Shell form (`CMD ./start.sh`) 導致信號被 Shell 吞掉，無法傳遞給應用程式。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The `:latest` Tag Roulette (使用 `:latest` 標籤的賭博)
這是最常見也最危險的反模式。
- **The Mistake**: 在 `FROM` 指令或部署 yaml 中使用 `node:latest` 或 `my-app:latest`。
- **The Consequence**:
    - **不可重現性 (Non-reproducible)**：今天部署的版本和明天部署的版本可能完全不同（因為 Base Image 更新了）。
    - **回滾困難 (Rollback hell)**：當 `:latest` 壞掉時，你很難知道上一個能動的 `:latest` 到底是哪個 SHA。
- **The Fix**: 使用具體版本號（Specific Tags）或 SHA Digest。
    - ✅ `FROM node:18.16.0-alpine`
    - ✅ `image: my-app:v1.2.3`

### 2. The "Fat Container" (單一容器多進程)
- **The Mistake**: 在容器內安裝 `supervisor` 或 `systemd`，試圖同時運行 Nginx, PHP-FPM, 和 MySQL。
- **The Consequence**:
    - **破壞隔離性**：DB 崩潰可能不會導致容器重啟，Orchestrator 以為服務還活著。
    - **日誌混亂**：`docker logs` 會顯示所有服務的混合輸出，難以除錯。
- **The Fix**: 使用 Docker Compose 或 K8s Pods 將服務拆分為 Sidecar 或獨立容器。

### 3. Writing State to Container Layer (將狀態寫入容器層)
- **The Mistake**: 讓資料庫檔案、高頻率的 Logs 直接寫在容器的檔案系統內（沒有掛載 Volume）。
- **The Consequence**:
    - **效能低落**：容器的可寫層（Writable Layer）使用 Copy-on-Write (CoW) 機制，I/O 效能遠低於 Volume。
    - **資料遺失**：容器刪除或重建後，資料隨之消失。
- **The Fix**: 使用 Volumes 或 Bind Mounts 儲存持久化資料；Logs 則輸出到 `stdout/stderr`。

### 4. Build Secrets Leakage (構建時洩漏機密)
- **The Mistake**: `COPY id_rsa .` 或 `ENV AWS_KEY=...` 在 Dockerfile 中。
- **The Consequence**: 即使你在下一行刪除了該檔案，它仍然存在於映像檔的「歷史層（History Layer）」中，任何人 `docker history` 都能看到。
- **The Fix**: 使用 Docker BuildKit 的 `--mount=type=secret` 功能，或僅在 Runtime 通過環境變數注入。

### 5. The "Root" Default (預設 Root 權限)
- **The Mistake**: 沒有指定 `USER`，應用程式以 `root` 身份運行。
- **The Consequence**: 如果應用程式有漏洞被攻破，攻擊者可能獲得宿主機的 Root 權限（容器逃逸）。
- **The Fix**: 建立並切換到非特權使用者。
    ```dockerfile
    RUN addgroup -S appgroup && adduser -S appuser -G appgroup
    USER appuser
    ```

---

## Checklists & workflows｜檢查清單與流程

### Dockerfile Review Checklist
在提交 Dockerfile 之前，請檢查以下項目：

- [ ] **Base Image**: 是否使用了具體的版本標籤（非 `:latest`）？建議使用輕量級版本（如 `alpine` 或 `slim`）。
- [ ] **Security**: 是否建立了非 Root 使用者並使用 `USER` 指令切換？
- [ ] **Context**: 是否有 `.dockerignore` 檔案？（排除 `.git`, `node_modules`, 敏感文件）。
- [ ] **Layers**: 是否合併了相關的 `RUN` 指令以減少層數？（例如 `apt-get update && apt-get install ... && rm -rf /var/lib/apt/lists/*`）。
- [ ] **Secrets**: 確認沒有將 API Keys 或密碼硬編碼（Hardcode）在 Dockerfile 中。
- [ ] **Entrypoint**: 是否使用 Exec form `["executable", "param1"]` 以確保信號傳遞？

### Debugging Workflow (When things go wrong)
當容器行為不如預期時的決策樹：

1. **容器立即退出？**
   - 檢查 `docker logs <container_id>`。
   - 確認 `CMD` 或 `ENTRYPOINT` 是否是前台執行（Foreground）？（例如 Nginx 需 `daemon off;`）。
2. **連不上服務？**
   - 檢查 `docker port` 確認端口映射。
   - 確認應用程式監聽的是 `0.0.0.0` 而不是 `127.0.0.1`（localhost 在容器內僅代表容器本身）。
3. **構建速度太慢？**
   - 檢查 `.dockerignore` 是否遺漏了大檔案。
   - 檢查指令順序：變動頻率低的（如安裝依賴）放在前面，變動頻率高的（如 Copy Source Code）放在後面以利用快取。

---

## Real-world examples｜實戰案例

### Example 1: The "Zombie" Container (Signal Handling)

**❌ Bad Practice (Shell Form):**
```dockerfile
# Dockerfile
FROM node:18
WORKDIR /app
COPY . .
# 這樣啟動會產生一個 /bin/sh -c 的父進程，它不會轉發 SIGTERM 給 node
CMD npm start 
```
*後果*：當你執行 `docker stop`，Docker 等待 10 秒超時後強制 `SIGKILL`，導致 DB 連線未正常關閉或資料損壞。

**✅ Good Practice (Exec Form):**
```dockerfile
# Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY . .
# 直接執行 executable，PID 1 就是 node
CMD ["npm", "start"] 
```
*或者使用 `tini` 作為 init process*:
```dockerfile
RUN apk add --no-cache tini
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "app.js"]
```

### Example 2: The "Bloated" Image (Layer Optimization)

**❌ Bad Practice:**
```dockerfile
FROM ubuntu:22.04
# 每一行 RUN 都是一層，刪除檔案並不會減少上一層的大小
RUN apt-get update
RUN apt-get install -y vim git
RUN rm -rf /var/lib/apt/lists/* 
```

**✅ Good Practice:**
```dockerfile
FROM ubuntu:22.04
# 在同一層內完成安裝與清理
RUN apt-get update && apt-get install -y \
    vim \
    git \
    && rm -rf /var/lib/apt/lists/*
```

### Example 3: The "Latest" Tag Trap in CI/CD

**Scenario**: 你的 CI Pipeline 腳本寫著 `docker build -t myapp:latest .` 然後部署。
**Incident**: 某天 Postgres 推出了新的 Major Version 並標記為 `latest`。你的 App 重新部署後自動拉取了新的 DB Image，但資料庫檔案格式不相容，導致 Production 服務全掛。
**Fix**:
1. **Pin Versions**: 使用 `postgres:14.2`。
2. **Immutable Tags**: CI 構建時使用 Git Commit SHA 作為 Tag，例如 `myapp:git-a1b2c3d`。
3. **Promotion Strategy**: 只有經過測試的 Image 才會被 Retag 為 `release-v1.0` 並推送到生產環境。