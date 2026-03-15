# 容器安全加固：非特權使用者與 Capabilities / Container Security Hardening: Non-root Users & Capabilities

## Mental model｜心智模型

要理解容器安全，必須打破「容器是輕量級虛擬機」的迷思，並建立以下兩個核心觀念：

### 1. 容器只是被隔離的 Process (Container is just a Process)
在 Linux 核心眼中，Docker 容器內的程式只是一個被 Namespace 和 Cgroups 限制住的 Process。
- **預設危險**：如果你在容器內是 `root` (UID 0)，而在 Host 機器上沒有做 User Namespace Remapping，那麼你在 Host 核心眼中也是 UID 0。一旦容器被突破（Container Breakout），攻擊者就擁有 Host 的 Root 權限。
- **防禦策略**：**不要讓你的應用程式以 God Mode (Root) 運行**。就像你不會在日常開發時一直使用 `sudo` 執行所有指令一樣。

### 2. 權限是瑞士軍刀，不是萬能鑰匙 (Capabilities slicing)
傳統 Linux 的 Root 權限是「全有或全無」(All or Nothing)。但 Linux Capabilities 將 Root 的權限切分成許多小塊（如 `CAP_NET_BIND_SERVICE` 綁定端口、`CAP_CHOWN` 修改檔案擁有者）。
- **最小權限原則**：你的 Web Server 真的需要修改系統時間 (`CAP_SYS_TIME`) 或載入核心模組 (`CAP_SYS_MODULE`) 嗎？如果不需要，就應該拿掉。
- **模型想像**：想像你給應用程式一個工具箱，預設裡面有電鋸、炸藥和雷射槍（Default Docker Capabilities）。安全加固就是把這些危險工具拿走，只留下一把螺絲起子（應用程式真正需要的權限）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 構建時建立並切換至非特權使用者 (Create and Switch to Non-root User)
不要依賴 Base Image 是否已經建立了使用者，最好在 Dockerfile 中顯式宣告。

```dockerfile
# ❌ Bad: 預設使用 Root 運行
FROM node:18
CMD ["npm", "start"]

# ✅ Good: 建立群組與使用者，並切換
FROM node:18-alpine
WORKDIR /app
# 建立一個指定 UID 的使用者 (避免與 Host ID 衝突)
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
# 確保檔案權限正確
COPY --chown=appuser:appgroup . .
# 切換使用者
USER appuser
CMD ["npm", "start"]
```

### 2. 執行時剝奪所有 Capabilities (Drop ALL Capabilities)
採取「白名單」策略：先拒絕所有權限，再逐一加回必要的。

**Docker Compose 範例：**
```yaml
services:
  web:
    image: my-app
    cap_drop:
      - ALL  # 丟棄所有權限
    cap_add:
      - NET_BIND_SERVICE # 僅加回綁定 < 1024 port 的權限 (如果真的需要)
```

### 3. 禁止提權 (No New Privileges)
防止容器內的 Process 透過 `setuid` 或 `setgid` 二進位檔案（如 `sudo`）獲取比啟動時更高的權限。

```yaml
# docker-compose.yml
services:
  web:
    security_opt:
      - no-new-privileges:true
```

### 4. 唯讀根檔案系統 (Read-only Root Filesystem)
如果駭客無法寫入檔案系統，他們就很難植入後門或下載惡意腳本。將根目錄設為唯讀，只掛載必要的臨時目錄（如 `/tmp`, `/run`）為可寫。

```yaml
services:
  web:
    read_only: true
    tmpfs:
      - /tmp
      - /run
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 為了方便使用 `--privileged`
- **現象**：因為權限不足導致程式報錯，開發者直接加上 `--privileged` flag。
- **後果**：這給予容器幾乎所有的 Host 權限（包含存取所有裝置）。這等於放棄了容器的所有安全隔離機制。
- **修正**：找出具體缺少的 Capability（例如需要操作 iptables 則加 `NET_ADMIN`），而不是給予全部。

### 2. 遇到 Permission Denied 就 `chmod 777`
- **現象**：掛載 Volume 後，容器內非 Root 使用者無法寫入，於是直接在 Host 上執行 `chmod -R 777 ./data`。
- **後果**：任何使用者（包含被入侵的服務）都可以隨意刪改資料。
- **修正**：確保 Host 上的目錄 UID/GID 與容器內的 `USER` UID/GID 一致，或者使用 Init Container 來修正權限。

### 3. 綁定特權端口 (Binding Privileged Ports)
- **現象**：堅持讓 Node.js 或 Python 監聽 Port 80。
- **問題**：Linux 預設 1024 以下的 Port 需要 Root 權限。
- **修正**：讓應用程式監聽非特權 Port（如 8080, 3000），並在 Docker 層或 Load Balancer 層做 Port Mapping (`80:8080`)。

### 4. 將 Secrets 寫死在 Dockerfile ENV
- **現象**：`ENV DB_PASSWORD=secret`。
- **後果**：任何人只要 `docker inspect` 映像檔就能看到密碼。
- **修正**：使用 Docker Secrets、掛載檔案，或是在 Runtime 時才傳入環境變數（且不要 commit 進 image）。

---

## Checklists & workflows｜檢查清單與流程

在將容器推向生產環境前，請執行以下安全檢查：

### Dockerfile 靜態分析
- [ ] **User Check**: 是否有 `USER <non-root>` 指令？且不是使用 UID 0？
- [ ] **Base Image**: 是否使用受信任且定期更新的 Base Image (如 Alpine, Distroless)？
- [ ] **Secrets**: 確認沒有 `COPY` 包含密碼的設定檔或 `.env` 檔進去。

### Runtime 配置 (Docker Compose / K8s Manifest)
- [ ] **Cap Drop**: 是否設定了 `cap_drop: ['ALL']`？
- [ ] **Privilege Escalation**: 是否開啟了 `no-new-privileges`？
- [ ] **Read-only**: 根目錄是否設為唯讀 (`read_only: true`)？
- [ ] **Resources**: 是否限制了 CPU 和 Memory（防止 DoS 攻擊）？

### Volume 權限驗證流程
1. 確定容器內運行的 UID (例如 `1001`)。
2. 檢查 Host 掛載目錄的擁有者是否對應 ( `chown 1001:1001 ./host-data` )。
3. 啟動容器，驗證應用程式是否能正常讀寫 Volume。

---

## Real-world examples｜實戰案例

### 案例：安全的 Node.js Web Service

這是一個典型的生產環境配置，展示了如何結合上述所有最佳實踐。

#### 1. Dockerfile (Hardened)

```dockerfile
FROM node:18-alpine

# 安裝 dumb-init 以正確處理 PID 1 信號 (優雅關閉)
RUN apk add --no-cache dumb-init

WORKDIR /app

# 建立專屬使用者，固定 UID 為 1000 以便於權限管理
RUN addgroup -g 1000 nodeapp && \
    adduser -u 1000 -G nodeapp -s /bin/sh -D nodeapp

# 複製 package.json 並安裝依賴
COPY package*.json ./
RUN npm ci --only=production

# 複製程式碼，並將擁有權交給 nodeapp
COPY --chown=nodeapp:nodeapp . .

# 切換至非特權使用者
USER nodeapp

# 應用程式監聽 3000 (非特權端口)
EXPOSE 3000

# 使用 dumb-init 啟動
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["node", "server.js"]
```

#### 2. docker-compose.yml (Security Context)

```yaml
version: '3.8'
services:
  api:
    build: .
    image: my-secure-api:v1
    container_name: secure_api
    
    # 端口映射：外部 80 -> 內部 3000
    ports:
      - "80:3000"
    
    # 安全性配置核心
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    # 如果不需要 ping 或其他網路操作，甚至不需要 NET_RAW
    # cap_add: [] # 保持為空，除非絕對必要
    
    # 檔案系統安全
    read_only: true
    tmpfs:
      - /tmp:rw,noexec,nosuid  # 限制 /tmp 不能執行程式
    
    # 環境變數 (不包含敏感 Secrets)
    environment:
      - NODE_ENV=production
    
    # 資源限制 (防止 DoS)
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 512M
    
    # 使用非 Root 使用者運行 (雙重保險，雖然 Dockerfile 已經指定)
    user: "1000:1000"
```

### 除錯技巧：當權限過於嚴格時
如果你發現設定 `cap_drop: [ALL]` 後應用程式崩潰，不要急著改回 `privileged`。請使用 `docker logs` 查看錯誤，如果是 `Operation not permitted`，請查閱該工具的文檔，找出它具體需要哪個 Capability（例如 `ping` 需要 `NET_RAW`，`chown` 需要 `CHOWN`），然後只補上那一個。