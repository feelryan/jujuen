# 資料持久化與權限管理陷阱 / Data Persistence & Permission Pitfalls

## Mental model｜心智模型

要掌握 Docker 的儲存與權限，必須打破「容器只是一個資料夾」的直覺，建立以下兩個核心觀念：

### 1. 容器是「借住的旅館」，Volume 才是「保險箱」
**Containers are ephemeral; Volumes are persistent.**
容器的設計本質是**用完即丟（Ephemeral）**。容器內部的寫入層（Container Layer）就像是旅館房間的便條紙，一旦你退房（刪除容器），上面的資料就進了碎紙機。
- **Bind Mounts**：像是把你自己家裡的抽屜直接搬進旅館房間用。你改了什麼，家裡原本的抽屜也會變。
- **Volumes**：像是旅館提供的專屬保險箱，由 Docker (旅館經理) 管理。即使你換了房間（新容器），保險箱裡的內容還在，且可以掛載到新房間。

### 2. Linux 核心只認 ID，不認使用者名稱
**The Kernel cares about UIDs/GIDs, not Usernames.**
這是權限問題最大的坑。
- 當你在 Host 機器上是 `alice (uid: 1000)`，但在容器內你是 `root (uid: 0)`。
- 當容器內的 `root` 在 Bind Mount 的目錄寫入檔案時，Host 看到的檔案擁有者就是 `root`。
- 結果：你在 Host 上想刪除或修改這些檔案時，會因為 `Permission denied` 而失敗，因為你只是 `alice`。
- **關鍵認知**：Docker 容器與 Host 共享同一個 Kernel，因此檔案系統的權限檢查是基於 **Numeric ID (UID/GID)** 進行的，容器內的 `/etc/passwd` 使用者名稱對 Host 毫無意義。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 依據用途選擇掛載類型 (Storage Strategy)
不要憑感覺選，請依照資料生命週期決定：

| 資料類型 (Data Type) | 推薦方式 (Recommended) | 理由 (Reasoning) |
| :--- | :--- | :--- |
| **資料庫檔案** (Database Data) | **Named Volume** | 效能最佳、由 Docker 託管、避免檔案系統格式差異（如 Windows/macOS 的 FS 效能問題）。 |
| **原始碼、設定檔** (Source Code, Config) | **Bind Mount** | 開發時需要即時修改並生效 (Hot-reload)。 |
| **敏感金鑰** (Secrets/Keys) | **Tmpfs / Secrets** | 避免寫入磁碟，僅存在記憶體中，容器重啟即消失。 |
| **編譯產物/快取** (Build Artifacts/Cache) | **Anonymous Volume** | 避免 Host 的 `node_modules` 覆蓋容器內的版本。 |

### 2. 解決開發環境權限問題：User Remapping
在開發環境（尤其是 Linux Host）使用 Bind Mount 時，最簡單的解法是讓容器以 Host 使用者的 ID 執行。

**Pattern: The "Current User" Injection**
在 `docker-compose.yml` 中動態注入當前使用者的 UID/GID：

```yaml
services:
  app:
    image: my-app
    # 讓容器內的 process 使用與 Host 相同的 UID:GID
    user: "${UID}:${GID}"
    volumes:
      - .:/app
```
*注意：這通常需要你在 `.env` 檔或 shell 中匯出 `UID` 和 `GID` 變數。*

### 3. 初始化資料的正確姿勢 (Initialization)
資料庫首次啟動通常需要初始 SQL。不要手動 copy 進去，善用官方 Image 的 Hook。
- **Postgres/MySQL**: 將 `.sql` 或 `.sh` 腳本放入 `/docker-entrypoint-initdb.d/`。容器首次建立 Volume 時會自動執行，且只執行一次。

### 4. 避免 `node_modules` 衝突 (The "Volume Trick")
當你 Bind Mount 專案根目錄時，Host 的 `node_modules` 會蓋掉容器內的。解決方法是使用一個匿名 Volume "反向掛載" 回去。

```yaml
volumes:
  - .:/app                # Bind Mount: Host 蓋掉 Container
  - /app/node_modules     # Anonymous Volume: 保護 Container 內該路徑不被 Host 覆蓋
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The `chmod 777` Hammer
**反模式**：遇到 `Permission denied` 就直接 `chmod -R 777 .`。
- **後果**：這不僅造成安全漏洞，還會導致 git 追蹤到檔案權限變更，弄髒 commit history。
- **修正**：找出正確的 UID/GID 對應，或使用 Docker 的 `--user` 參數。

### 2. Hardcoded Host Paths
**反模式**：在 `docker-compose.yml` 寫死絕對路徑。
```yaml
volumes:
  - /home/john/project/data:/var/lib/mysql  # Don't do this!
```
- **後果**：你的同事（或 CI Server）路徑跟我不一樣，專案無法跑。
- **修正**：使用相對路徑 `./data:/var/lib/mysql` 或 Named Volumes。

### 3. Root-owned Files on Host
**反模式**：容器以 Root 執行並產生 Log 或 Build Artifacts 到 Bind Mount 的目錄。
- **後果**：你在 Host 上想 `rm -rf` 清理專案時發現刪不掉，必須用 `sudo`，長久下來檔案權限亂成一團。
- **修正**：確保產生檔案的 Process 以非 Root 執行，或在 Entrypoint script 結束前修正檔案擁有者。

### 4. Database on Bind Mount (Cross-platform issues)
**反模式**：在 Windows/macOS 上透過 Docker Desktop 將資料庫 data 目錄 Bind Mount 到 Host。
- **後果**：極慢的 I/O 效能（因為跨越了 VM 檔案系統邊界），且可能因為鎖定機制（File Locking）不同導致資料庫損毀。
- **修正**：資料庫務必使用 **Named Volume**。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Choosing Storage Type
- [ ] **我需要這個資料在容器刪除後還存在嗎？**
    - No -> 使用 Container Layer (預設) 或 `tmpfs` (若需高效能/安全性)。
    - Yes -> 繼續往下。
- [ ] **我需要在 Host 機器上直接編輯這些檔案嗎？** (例如程式碼、設定檔)
    - Yes -> 使用 **Bind Mount** (`-v ./host/path:/container/path`)。
    - No -> 使用 **Volume** (`-v volume_name:/container/path`)。

### Permission Troubleshooting Workflow
當遇到 `Permission denied` 或檔案無法寫入時：
1.  **Check IDs**: 在容器內執行 `id`，在 Host 執行 `id`。
2.  **Inspect Ownership**: 在容器內執行 `ls -n <path>` 查看目錄的 **數字 ID**。
3.  **Verify Mount**: 執行 `docker inspect <container_id>` 確認 `Mounts` 區塊的 `RW` (Read-Write) 屬性是否為 `true`。
4.  **Fix Strategy**:
    - 開發環境：調整 `docker-compose` 的 `user: "${UID}:${GID}"`。
    - 生產環境：在 Dockerfile 建立專屬 user，並確保 `COPY --chown` 正確設定權限。

---

## Real-world examples｜實戰案例

### Scenario 1: The "Clean" Development Setup (Node.js)
這是一個標準的開發配置，解決了「程式碼熱更新」與「避免 `node_modules` 衝突」的問題。

```yaml
# docker-compose.yml
services:
  backend:
    image: node:18-alpine
    working_dir: /app
    # 使用 Host 的使用者 ID 執行，避免產生的檔案變成 root owned
    # 在 .env 檔中設定 UID=1000 (或你的 ID)
    user: "${UID}:${GID}" 
    command: npm run dev
    volumes:
      - .:/app                 # Bind Mount: 程式碼同步
      - /app/node_modules      # Anonymous Volume: 隔離依賴套件
    environment:
      - NODE_ENV=development
```

### Scenario 2: Production-Ready Database with Initialization
這個配置展示了如何正確持久化資料庫，並處理初始化腳本。

```yaml
# docker-compose.prod.yml
services:
  db:
    image: postgres:15
    restart: always
    environment:
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password # 安全性最佳實踐
      POSTGRES_DB: myappdb
    volumes:
      - db_data:/var/lib/postgresql/data  # 使用 Named Volume 獲得最佳效能
      - ./init-scripts:/docker-entrypoint-initdb.d:ro # 初始化 SQL，唯讀
    secrets:
      - db_password

volumes:
  db_data: # 宣告 Volume，Docker 會自動管理儲存位置

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

### Scenario 3: Fixing Permissions with Entrypoint (The "Fixer" Pattern)
如果無法使用 `user: UID` (例如容器內程式必須先以 root 啟動某些服務)，可以使用 Entrypoint 腳本在執行主程式前修正權限。

```bash
#!/bin/sh
# entrypoint.sh

# 假設 PUID 和 PGID 是透過 ENV 傳入的目標 ID
PUID=${PUID:-1000}
PGID=${PGID:-1000}

echo "Fixing permissions for /data..."
# 僅修正特定資料夾權限
chown -R "$PUID:$PGID" /data

# 降權並執行主程式 (gosu 是一個比 sudo 更適合容器的工具)
exec gosu "$PUID:$PGID" "$@"
```