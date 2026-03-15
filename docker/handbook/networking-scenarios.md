# 網路模型實戰：通訊模式與 DNS 解析 / Networking in Practice: Communication Patterns & DNS

## Mental model｜心智模型

要掌握 Docker 網路，請先拋棄「容器只是跑在同一台機器上的 Process」這種過度簡化的想法。你應該將 Docker 網路想像成一個 **軟體定義的虛擬交換器（Software-defined Virtual Switch）**。

### 1. 隔離的網路堆疊 (Isolated Network Stack)
每個容器預設都擁有獨立的網路 Namespace。這意味著容器有自己的 `localhost`、自己的 IP 位址、路由表和 DNS 設定。
- **誤區**：在容器內指 `localhost` (127.0.0.1) 通常指的是容器自己，而不是宿主機 (Host)。
- **真相**：容器就像是接在同一個虛擬路由器（Docker Bridge）下的獨立電腦。

### 2. 內建 DNS 伺服器 (Embedded DNS Server)
Docker 在 `127.0.0.11` 運行了一個內嵌的 DNS resolver。這是 Docker 網路的靈魂。
- 當你使用 **User-defined Bridge Network** 時，這個 DNS 伺服器會自動將「容器名稱 (Container Name)」或「服務名稱 (Service Name)」解析為動態分配的容器 IP。
- 這實現了 **Service Discovery**：你不需要知道資料庫的 IP 是多少，你只需要知道它的名字是 `db`。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 始終使用自定義橋接網路 (Always use User-defined Bridge Networks)
預設的 `bridge` 網路（安裝 Docker 後自帶的那個）不支援透過容器名稱進行 DNS 解析，只能用 IP 或過時的 `--link`。
- **Pattern**: 在 `docker-compose.yml` 中，雖然預設會建立一個專屬網路，但顯式定義網路可以讓你更靈活地連接多個專案。
- **Why**: 啟用自動 DNS 解析 (Automatic Service Discovery)。

### 2. 應用程式綁定 0.0.0.0 (Bind to 0.0.0.0, not 127.0.0.1)
這是新手最常遇到的坑。許多框架（如 Flask, Django, Vite）預設只監聽 `localhost`。
- **Pattern**: 確保容器內的應用程式監聽 `0.0.0.0` (All interfaces)。
- **Why**: 來自 Host 的請求是透過 Docker Bridge 轉發進來的，對容器來說是外部流量，而非本地流量。

### 3. 最小權限埠口映射 (Least Privilege Port Mapping)
不要無腦映射所有埠口到 Host。
- **Pattern**:
  - **Frontend/API Gateway**: 需要對外服務，使用 `-p 80:80`。
  - **Database/Redis/Internal Services**: **不要** 使用 `-p` 映射到 Host，除非你需要從 Host 用 GUI 工具連線除錯。讓後端服務透過 Docker 內部網路直接連線資料庫。
- **Why**: 安全性。避免資料庫意外暴露在公網或內網中。

### 4. 跨平台 Host 存取 (Cross-platform Host Access)
當容器需要連線到宿主機上的服務（例如：本機開發中的另一個 API）時：
- **Pattern**: 使用 `host.docker.internal` DNS 名稱。
- **Note**: 在 Linux 上可能需要在 `docker run` 加入 `--add-host=host.docker.internal:host-gateway` (Docker v20.10+)。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Hardcoding IP Addresses
❌ **反模式**：在程式碼或設定檔中寫死 `172.17.0.x`。
- **後果**：容器重啟後 IP 可能改變，導致連線失敗。
- **解法**：永遠使用容器名稱或 Service Name。

### 2. 濫用 Host Network Mode (`--network host`)
❌ **反模式**：為了省去 port mapping 的麻煩，直接將所有容器設為 `network_mode: host`。
- **後果**：容器與 Host 共享網路堆疊，喪失網路隔離性，且埠口衝突風險大增（兩個容器不能監聽同一個 port）。
- **例外**：高效能需求（如 Load Balancer）或特殊的網路監控工具才考慮使用。

### 3. 依賴啟動順序而非健康檢查 (Depending on Startup Order)
❌ **反模式**：認為 `depends_on` 可以確保網路連通。
- **後果**：`depends_on` 只確保容器啟動順序，不代表資料庫已經 Ready to accept connections。
- **解法**：實作 Retry 機制或使用 `healthcheck` 搭配 `condition: service_healthy`。

---

## Checklists & workflows｜檢查清單與流程

### 網路連線除錯流程 (Network Troubleshooting Workflow)

當 Container A 無法連線到 Container B 時，請依序檢查：

- [ ] **1. 網路歸屬檢查**：
  - 執行 `docker network inspect <network_name>`。
  - 確認 A 和 B 都在 `Containers` 清單中。
- [ ] **2. DNS 解析測試**：
  - 進入 Container A：`docker exec -it <container_a> sh`。
  - 執行 `nslookup <container_b_name>` 或 `ping <container_b_name>`。
  - 如果 `nslookup` 失敗，檢查是否使用了 Default Bridge。
- [ ] **3. 埠口監聽檢查**：
  - 進入 Container B，確認應用程式是否監聽 `0.0.0.0` 而非 `127.0.0.1`。
  - (Linux 容器內) `netstat -tulpn` 或 `ss -tulpn`。
- [ ] **4. 防火牆與 Host 設定**：
  - 檢查 Host 的防火牆 (ufw/iptables) 是否擋住了 Docker 網段。
  - 檢查是否有 VPN 軟體干擾了路由。

### 生產環境網路檢查清單 (Production Readiness Checklist)

- [ ] 僅對外暴露必要的埠口 (Only expose public-facing ports)。
- [ ] 資料庫與快取服務僅存在於內部網路 (Backend tier network)。
- [ ] 使用自定義網路區隔不同應用堆疊 (Network segmentation)。
- [ ] 應用程式具備連線重試機制 (Connection retry logic)。

---

## Real-world examples｜實戰案例

### 案例一：標準的三層式架構 (Standard 3-Tier Architecture)

這是最常見的 `docker-compose` 網路配置，展示了前端公開、後端與資料庫隱藏的模式。

```yaml
version: '3.8'

services:
  # 反向代理/前端：唯一對外暴露埠口的服務
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    networks:
      - frontend-net
    depends_on:
      - api

  # 後端 API：同時連接前端網路與後端資料網路
  api:
    image: my-backend-app
    environment:
      # 使用服務名稱 "db" 連線，而非 IP
      - DB_HOST=db 
    networks:
      - frontend-net
      - backend-net

  # 資料庫：完全不暴露埠口 (-p)，僅在 backend-net 內部可見
  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=secret
    networks:
      - backend-net

networks:
  frontend-net:
  backend-net:
```

### 案例二：除錯工具箱 (The Debugging Sidecar)

當你懷疑容器網路有問題，但容器內只有精簡的 OS (Distroless/Alpine) 沒有工具時，啟動一個臨時的工具容器加入同一個網路進行診斷。

```bash
# 加入目標容器所在的網路 (假設網路名稱為 myproject_default)
# 使用 nicolaka/netshoot 這個充滿網路工具的神級 Image
docker run --rm -it --network myproject_default nicolaka/netshoot

# 進入後可以執行：
# nslookup db       <-- 測試 DNS
# curl api:8080     <-- 測試 HTTP 連通性
# dig db            <-- 詳細 DNS 資訊
```

### 案例三：解決 "Connection Refused" (Fixing Localhost Binding)

**情境**：你的 Node.js App 在容器內跑起來了，Log 顯示 `Listening on port 3000`，但你從 Host 瀏覽器連 `localhost:3000` 卻連不上。

**原因**：程式碼寫了 `app.listen(3000, 'localhost')`。

**修正**：

```javascript
// ❌ Anti-pattern: 只能被容器內部存取
// app.listen(3000, 'localhost');

// ✅ Best Practice: 允許來自 Docker Bridge 的流量
app.listen(3000, '0.0.0.0'); 
```

或者在 `package.json` / `CMD` 中指定：
```json
"scripts": {
  "start": "vite --host 0.0.0.0"
}
```