# 開發工作流：Docker Compose 與環境一致性 / Development Workflow: Docker Compose & Environment Consistency

## Mental model｜心智模型

### 1. 基礎設施即代碼的本地延伸 (IaC for Localhost)
不要將 Docker Compose 僅視為「一次啟動多個容器的腳本」。它是你本地開發環境的 **架構藍圖 (Architecture Blueprint)**。
Think of Docker Compose not just as a script to start containers, but as the **Architecture Blueprint** for your local development environment.

在傳統開發中，你需要手動安裝 MySQL、Redis、Node.js 到本機 OS；在 Docker Compose 模型中，這些依賴變成了 YAML 檔案中的聲明。你的本機 OS 應該保持乾淨，只安裝 Docker 和 IDE。

### 2. 服務拓撲圖 (Service Topology)
將 `docker-compose.yml` 想像成一張電路圖。每個 Service 是一個元件，Networks 是導線，Volumes 是硬碟插槽。
- **Services**: 應用程式的不同部分 (Frontend, Backend, DB)。
- **Networking**: 服務之間通過「服務名稱 (Service Name)」互相解析，而非 IP。
- **Volumes**: 連接「容器內部」與「開發者本機」的橋樑（特別是 Bind Mounts）。

### 3. 環境分層策略 (Layered Environments)
環境一致性並非指「開發環境與生產環境 100% 相同」，而是指「核心依賴相同，但配置適應場景」。
Consistency doesn't mean "Identical". It means "Same Dependencies, Context-aware Configuration".
- **Base**: 通用的架構定義。
- **Override**: 本地開發特有的配置（如 Hot-reload, Debugger ports）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. The Override Pattern (覆蓋模式)
這是管理多環境配置最強大的模式。不要維護 `docker-compose.dev.yml` 和 `docker-compose.prod.yml` 兩份完全獨立的檔案。
Instead of maintaining separate files, use the default override behavior.

- **`docker-compose.yml`**: 定義服務、映像檔、網路依賴（通用部分）。
- **`docker-compose.override.yml`**: 定義本地開發特有的配置（如 `volumes` 掛載源碼、暴露端口）。Docker Compose 會自動讀取並合併此檔案。
- **Git Strategy**: 將 `docker-compose.override.yml` 加入 `.gitignore`，但提供一個 `docker-compose.override.example.yml` 供團隊參考。

### 2. Bind Mounts for Hot Reloading (掛載源碼以實現熱重載)
在開發階段，使用 Bind Mounts 將本機源碼目錄映射到容器內，配合語言框架的 Watch Mode（如 `nodemon`, `uvicorn --reload`）。
Use Bind Mounts to map local source code into the container, enabling immediate feedback loops without rebuilding images.

```yaml
# docker-compose.override.yml
services:
  backend:
    volumes:
      - ./src:/app/src  # Sync code changes immediately
    command: npm run dev # Starts with nodemon/watch mode
```

### 3. Named Volumes for Persistence (具名卷用於資料持久化)
資料庫容器的資料應該存儲在 **Named Volumes** 中，而不是 Bind Mounts 或容器層內。這樣即使刪除容器，資料庫資料依然存在；且相比 Bind Mounts，Named Volumes 在某些 OS (如 Windows/Mac) 上有更好的 I/O 效能。

### 4. Wait-for-it Pattern (依賴啟動順序)
雖然 `depends_on` 控制啟動順序，但它不保證 Database **Ready** (已準備好接受連線)。
`depends_on` starts containers in order, but doesn't wait for the application inside to be ready.
- **Modern Approach**: 使用 `healthcheck` 搭配 `service_healthy` 條件。

```yaml
services:
  db:
    image: postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
  api:
    depends_on:
      db:
        condition: service_healthy
```

### 5. Environment Variables Hierarchy (環境變數層級)
- 使用 `.env` 檔案設定預設值（不進版控）。
- 在 `docker-compose.yml` 中明確列出需要的變數，方便除錯。
- 利用 `${VARIABLE:-default}` 語法提供 fallback。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Root" File Permission Hell (Root 權限地獄)
**現象**：容器內以 root 運行，生成的檔案（如 log, build artifacts）透過 Bind Mount 出現在本機，導致本機使用者無法刪除或修改。
**Pitfall**: Container runs as root, creating files on host via bind mount that the host user cannot edit/delete.
**解法**：在 Dockerfile 中建立非 root 使用者，或在 Compose 中指定 `user: "${UID}:${GID}"`。

### 2. Hardcoding Secrets in YAML (在 YAML 中寫死密鑰)
**現象**：直接在 `environment` 區塊寫 `PASSWORD=secret123` 並推送到 Git。
**後果**：安全漏洞。
**解法**：永遠透過 `.env` 檔案注入，或使用 Docker Secrets。

### 3. Copying `node_modules` / `venv` from Host (複製本機依賴庫)
**現象**：`COPY . .` 把本機的 `node_modules` (可能基於 macOS/Windows 編譯) 複製進 Linux 容器。
**後果**：Binary 不相容導致 crash。
**解法**：使用 `.dockerignore` 排除依賴目錄，並在容器構建過程中重新安裝依賴。

### 4. "It works on my machine" with Ports (端口衝突)
**現象**：硬性綁定 `80:80` 或 `5432:5432`。
**後果**：如果開發者本機已經跑了 Postgres，Compose 啟動會失敗。
**解法**：在 `.env` 中定義端口變數 `HOST_PORT=8080`，或允許 Docker 隨機分配（開發時較少用，但測試時有用）。

---

## Checklists & workflows｜檢查清單與流程

### Onboarding New Developer (新成員入職流程)
- [ ] **Clone**: 下載專案代碼。
- [ ] **Config**: 複製 `.env.example` 到 `.env`，複製 `docker-compose.override.example.yml` 到 `docker-compose.override.yml`。
- [ ] **Start**: 執行 `docker compose up -d`。
- [ ] **Verify**: 瀏覽器訪問 `localhost:PORT` 確認服務運行。
- [ ] **Result**: 在 15 分鐘內完成環境搭建，無需安裝語言 Runtime。

### Daily Dev Workflow (日常開發流程)
1. **Start**: `docker compose up -d` (啟動所有服務)。
2. **Logs**: `docker compose logs -f [service_name]` (查看特定服務日誌)。
3. **Shell**: `docker compose exec [service_name] /bin/sh` (進入容器執行 migration 或 script)。
4. **Rebuild**: 當 `package.json` 或 `Dockerfile` 變更時，執行 `docker compose up -d --build`。
5. **Cleanup**: 專案切換或重置時，`docker compose down` (保留資料) 或 `docker compose down -v` (刪除資料卷，徹底重置)。

### Troubleshooting Checklist (故障排除清單)
- [ ] **Port Conflict**: 是否出現 `Bind for 0.0.0.0:5432 failed: port is already allocated`？(檢查本機是否已有服務佔用)。
- [ ] **Volume Stale**: 代碼更新了但容器沒反應？(檢查是否正確配置了 Bind Mount)。
- [ ] **Network**: 服務 A 連不到服務 B？(檢查是否使用了 Service Name `http://backend:8000` 而非 `localhost`)。

---

## Real-world examples｜實戰案例

### Scenario: Full-Stack Web App (Node.js + Postgres + Redis)

這是一個典型的開發環境配置，展示了 Override 模式與 Healthcheck 的應用。

#### 1. `docker-compose.yml` (Base / Production-like structure)
```yaml
version: '3.8'
services:
  api:
    build: .
    image: myapp-api
    networks:
      - app-net
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASS}
    volumes:
      - db-data:/var/lib/postgresql/data
    networks:
      - app-net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:alpine
    networks:
      - app-net

volumes:
  db-data:

networks:
  app-net:
```

#### 2. `docker-compose.override.yml` (Local Development Only)
*此檔案不進 Git，每位開發者可依需求調整。*

```yaml
version: '3.8'
services:
  api:
    build:
      context: .
      target: dev-stage # 指向 Dockerfile 中的開發階段 (含 dev dependencies)
    command: npm run dev # 覆蓋預設 command，啟用 watch mode
    volumes:
      - ./src:/app/src # Bind Mount 源碼
      - ./package.json:/app/package.json
      # 技巧：使用匿名卷掛載 node_modules，防止本機空的 node_modules 覆蓋容器內的
      - /app/node_modules 
    environment:
      - NODE_ENV=development
      - DEBUG=app:*
    ports:
      - "3000:3000" # 僅在開發時暴露端口給本機
      - "9229:9229" # Debugger port

  db:
    ports:
      - "5432:5432" # 開發者可能想用本機 GUI 工具 (如 DBeaver) 連線 DB
```

### Key Takeaway
透過這種分離，CI/CD 系統可以直接使用 `docker-compose.yml` 進行測試或部署，而開發者在本地只需執行 `docker compose up` 即可自動合併這兩份配置，獲得具備熱重載與除錯功能的環境。