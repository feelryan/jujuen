# 核心概念與心智模型：超越虛擬機 / Core Mental Models: Beyond Virtual Machines

## Mental model｜心智模型

要精通 Docker，首先必須打破「它是輕量級虛擬機（Lightweight VM）」的迷思。雖然這個比喻有助於初學者入門，但在工程實踐中，它會導致錯誤的架構決策。

正確的心智模型應該是：**容器是穿了隔離衣的行程（Processes with Isolation）。**

### 1. 它是行程，不是機器 (It's a Process, not a Machine)
在虛擬機（VM）中，你有一套完整的 Guest OS、Kernel 和 init system（如 systemd）。但在容器中，你只有一個與 Host OS 共用 Kernel 的行程。
- **驗證方式**：在 Host 機器上執行 `ps aux | grep <你的應用程式>`，你會直接看到該行程，只是它被限制在特定的 Namespace 中。

### 2. 隔離的三大支柱 (The Three Pillars of Isolation)
理解 Docker 其實是在操作 Linux Kernel 的三個核心功能：

1.  **Namespaces (What you see / 你能看見什麼)**
    - 決定了行程的「視野」。
    - **PID Namespace**：容器內的 PID 1 是你的 App，但在 Host 上它可能是 PID 12345。
    - **Network Namespace**：容器有自己的 localhost、IP 和 port，不與 Host 衝突。
    - **Mount Namespace**：容器看到獨立的檔案系統視圖。

2.  **Cgroups (What you use / 你能使用什麼)**
    - 決定了行程的「資源上限」。
    - 限制 CPU 使用率、記憶體大小。如果容器被 OOM Kill（Out of Memory），通常是 Cgroups 在運作。

3.  **UnionFS (How you store / 你如何儲存)**
    - 決定了檔案系統的「層狀結構」。
    - **Copy-on-Write (CoW)**：映像檔（Image）是唯讀的。當容器需要修改檔案時，Docker 會將該檔案從唯讀層複製到最上層的可寫層（Container Layer）。這解釋了為什麼容器啟動這麼快（不需要複製整個 OS）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 單一職責原則 (Single Process Principle)
每個容器應該只運行**一個**主要行程（及其子行程）。
- **Why**: 容器的生命週期綁定 PID 1。如果 PID 1 死掉，容器就停止。如果你在一個容器內跑 App + Log Agent + Cron，當 App 當機時，容器可能因為 Log Agent 還活著而顯示 "Healthy"，導致 Orchestrator（如 K8s）無法重啟它。
- **Pattern**: 使用 Sidecar 模式（在同一個 Pod 或 Network 內運行另一個容器）來處理 Logging 或 Proxy，而不是把它們塞進同一個容器。

### 2. 拋棄式架構 (Disposability)
將容器視為「不可變基礎設施（Immutable Infrastructure）」的最小單位。
- **Do**: 需要更新設定或程式碼時，構建新的 Image 並替換舊容器。
- **Don't**: 進入運行中的容器執行 `git pull` 或修改設定檔。
- **Mental Shift**: 這是 "Cattle" (牲畜)，不是 "Pets" (寵物)。壞了就殺掉換新的，不要嘗試「修復」它。

### 3. 正確處理 PID 1 與信號 (Signal Handling)
Linux Kernel 會對 PID 1 行程進行特殊處理（例如忽略預設的信號行為）。
- **Pattern**: 確保你的應用程式能接收並處理 `SIGTERM` 信號以進行優雅關機（Graceful Shutdown）。
- **Best Practice**: 在 `Dockerfile` 中使用 `ENTRYPOINT ["executable", "param1"]` (Exec form) 而非 `ENTRYPOINT command param1` (Shell form)。Shell form 會啟動 `/bin/sh` 作為 PID 1，導致信號無法傳遞給你的 App。

### 4. 狀態外置 (Externalized State)
容器層（Container Layer）是短暫且效能較差的（因為 CoW 機制）。
- **Pattern**: 資料庫檔案、上傳的圖片、日誌等「持久化數據」必須掛載 Volume。
- **Pattern**: 設定（Configuration）應透過環境變數（Environment Variables）注入，而非寫死在 Image 內。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Fat Container" (胖容器)
試圖將容器當作 VPS 使用。
- **徵兆**：Dockerfile 裡安裝了 `ssh-server`, `cron`, `syslog`, `vim`，並且使用 Supervisor 或 Systemd 來管理多個服務。
- **後果**：映像檔巨大、構建緩慢、難以水平擴展、日誌分散難以收集。

### 2. 濫用 `latest` 標籤 (Abusing the `latest` tag)
- **錯誤**：在生產環境部署 `myapp:latest`。
- **後果**：無法回滾（Rollback）、無法確定當前運行的版本、不同機器拉取到的 `latest` 可能不同（破壞一致性）。
- **修正**：使用具體的版號或 Git Commit SHA，如 `myapp:v1.2.3` 或 `myapp:a1b2c3d`。

### 3. 在容器內以 Root 執行 (Running as Root)
預設情況下，容器內的 Root 在 Host 上也是 Root（雖然 Capability 受限）。
- **風險**：如果容器逃逸（Container Breakout）漏洞發生，攻擊者將獲得 Host 的 Root 權限。
- **修正**：在 Dockerfile 中建立並切換到非特權使用者 (`USER appuser`)。

### 4. 忽視殭屍行程 (Ignoring Zombie Processes)
- **問題**：如果你的 App 產生子行程但沒有正確回收（wait），而它又是 PID 1，這些殭屍行程會累積並耗盡系統資源。
- **修正**：使用 `tini` (`docker run --init`) 或在 Dockerfile 中加入 init process wrapper。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: "Should I put this in the container?"
1. **是應用程式的核心二進制檔或原始碼嗎？** -> Yes: 放入 Image。
2. **是執行時需要的依賴庫（Libs）嗎？** -> Yes: 放入 Image。
3. **是敏感資訊（密碼、API Key）嗎？** -> Yes: **絕對不要**放入 Image，使用 Env Vars 或 Secrets。
4. **是會變動的數據（User Uploads, DB Data）嗎？** -> Yes: 使用 Volume 掛載。
5. **是設定檔嗎？** -> 盡量轉為 Env Vars，或在 Runtime 掛載 ConfigMap。

### Pre-commit Checklist for Dockerfile
- [ ] **Process Check**: 啟動後是否只有一個主要行程？
- [ ] **User Check**: 是否切換到了非 Root 使用者 (`USER`)？
- [ ] **Signal Check**: 發送 `docker stop` 時，App 是否能收到信號並優雅關閉（而不是等待 10秒被 Kill）？
- [ ] **Layer Check**: 變動最頻繁的指令（如 `COPY . .`）是否放在 Dockerfile 的後段以利用快取？
- [ ] **Clean Check**: 是否在同一層 `RUN` 指令中清理了 `apt-get` cache 或暫存檔？

---

## Real-world examples｜實戰案例

### 案例 A：從 VM 思維轉向容器思維

**❌ Anti-pattern (VM 思維)**
開發者小明寫了一個 Dockerfile，他想：「我需要 SSH 進去修 Bug，還需要 Cron 跑排程。」

```dockerfile
FROM ubuntu:20.04
RUN apt-get update && apt-get install -y openssh-server cron python3
COPY . /app
# 試圖用 shell script 啟動多個服務，這會導致信號處理失效且日誌難以管理
CMD /app/start_everything.sh 
```

**✅ Best Practice (容器思維)**
資深工程師重構了架構：
1.  **SSH**: 不需要。使用 `docker exec` 調試，或修改程式碼後重新部署。
2.  **Cron**: 移出容器。使用 Kubernetes CronJob 或外部排程器觸發 API。
3.  **Process**: 專注於 Web Server。

```dockerfile
FROM python:3.9-slim
# 建立非特權使用者
RUN groupadd -r app && useradd -r -g app app
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
# 切換使用者
USER app
# 使用 Exec form 確保 PID 1 正確
CMD ["python3", "app.py"]
```

### 案例 B：UnionFS 的 Copy-on-Write 陷阱

**情境**：
你發現容器磁碟佔用量異常高，但 Image 大小看起來正常。

**原因分析**：
應用程式啟動時會解壓縮一個 500MB 的 `data.zip` 到 `/tmp`，處理完後刪除。
- 在 VM 中：這只佔用暫時的空間，刪除後空間釋放。
- 在 Docker 中：
    1. `data.zip` 位於 Image Layer (唯讀)。
    2. 解壓縮寫入 `/tmp` -> 寫入 Container Layer (可寫層)。
    3. 刪除檔案 -> 在 Container Layer 標記為刪除（Whiteout），但**實際佔用的磁碟空間不會立即回收**，直到容器被刪除。

**解決方案**：
- 如果這是構建過程：確保 `解壓縮` 和 `刪除` 在同一個 `RUN` 指令中完成。
- 如果是運行過程：將 `/tmp` 掛載為 `tmpfs` (記憶體) 或 Volume，繞過 UnionFS 的 CoW 機制。