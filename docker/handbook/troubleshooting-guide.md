# 實戰故障排除指南：日誌、檢測與除錯工具 / Practical Troubleshooting Guide: Logs, Inspect, and Debugging Tools

## Mental model｜心智模型

在 Docker 的世界中，除錯不應該是「猜測」，而是一場基於證據的「鑑識科學」。要建立有效的除錯心智模型，請將容器視為一個 **黑盒子飛行記錄器（Black Box Flight Recorder）**。

當容器墜毀（Crash）或行為異常時，我們透過三個層次來獲取資訊：

1.  **外部狀態（The Shell）**：容器是死是活？Exit Code 是多少？這是最外層的訊號。
2.  **標準輸出（The Output）**：應用程式在臨死前吐出了什麼？這是 `STDOUT/STDERR` 的日誌。
3.  **內部環境（The Environment）**：容器啟動時的參數、環境變數、掛載路徑是否如你預期？這是 `docker inspect` 的領域。

**關鍵觀念：**
容器是**短暫的（Ephemeral）**。如果容器啟動失敗，它通常會立即消失（Exited）。因此，除錯的核心在於**攔截（Intercept）**那個失敗的瞬間，或是在容器消失後**驗屍（Post-mortem）**。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 標準化日誌輸出 (Log to STDOUT/STDERR)
應用程式不應將日誌寫入容器內的檔案（如 `/var/log/app.log`），除非你有掛載 Volume。
*   **Pattern**: 應用程式直接將日誌吐到標準輸出。
*   **Why**: 這樣 `docker logs` 才能捕捉到資訊，且能被 Fluentd 或 Logstash 等收集器直接讀取。

### 2. 覆寫 Entrypoint 進行除錯 (Override Entrypoint)
當容器一啟動就 Crash，導致你無法 `exec` 進去查看時，這是最強大的技巧。
*   **Command**: `docker run --rm -it --entrypoint /bin/sh <image_name>`
*   **Why**: 這會忽略原本導致崩潰的啟動指令，讓你進入 Shell 手動執行啟動 script，逐步觀察哪一行報錯。

### 3. 使用臨時除錯容器 (Sidecar Debugging / Netshoot)
生產環境的 Image 通常是精簡版（如 Alpine 或 Distroless），裡面沒有 `curl`, `ping`, `telnet`。
*   **Pattern**: 使用 `nicolaka/netshoot` 等工具容器掛載到目標容器的網路 namespace。
*   **Command**: `docker run -it --net container:<target_container_id> nicolaka/netshoot`
*   **Why**: 讓你擁有全套網路除錯工具，卻不污染原本的 Image。

### 4. 善用 `docker inspect` 的格式化輸出
`inspect` 輸出的 JSON 太長，善用 `--format` (Go template) 快速提取資訊。
*   **Pattern**: 快速查 IP 或 Mounts。
*   **Command**: `docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container_id>`

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 忽視 Exit Codes (Ignoring Exit Codes)
*   **Anti-pattern**: 看到容器停止就直接重啟，不看它是怎麼死的。
*   **Pitfall**:
    *   `Exit Code 0`: 正常結束（可能是程式邏輯跑完就退出了，但你預期它是 Service）。
    *   `Exit Code 137`: **OOM Killer (Out Of Memory)**。這是最常見的死因，代表記憶體不足被系統殺掉。
    *   `Exit Code 127`: Command not found（通常是 Entrypoint 寫錯）。

### 2. 在容器內安裝除錯工具 (Installing tools in running containers)
*   **Anti-pattern**: 進到正在跑的容器執行 `apt-get update && apt-get install vim`。
*   **Pitfall**: 這會增加容器體積，且重啟後就消失了。且在生產環境通常沒有 root 權限或網路權限這樣做。應使用 Sidecar 模式。

### 3. 依賴 `latest` 標籤除錯
*   **Anti-pattern**: 除錯時不確定當前跑的是哪個版本。
*   **Pitfall**: `latest` 是浮動的。你以為你在 debug 新版程式碼，其實 Docker cache 讓你跑的是舊版。務必使用明確的版本號或 SHA hash。

### 4. 誤判 `localhost`
*   **Anti-pattern**: 在容器 A 中嘗試連線 `localhost:3306` 來存取容器 B 的資料庫。
*   **Pitfall**: 容器的 `localhost` 指的是容器自己。容器間通訊必須使用 **Service Name**（Docker Compose）或 **Container IP**。

---

## Checklists & workflows｜檢查清單與流程

當遇到容器問題時，請依照此標準化流程（SOP）進行排查：

### Phase 1: 容器無法啟動或立即死亡 (Startup Failures)

- [ ] **檢查狀態與 Exit Code**
  - 執行 `docker ps -a`。
  - 狀態是 `Exited (137)`？ -> 檢查記憶體限制 (OOM)。
  - 狀態是 `Exited (127)`？ -> 檢查 Entrypoint 指令路徑是否正確。
  - 狀態是 `Restarting`？ -> 進入 Crash Loop，立即查看 Log。
- [ ] **查看日誌 (Logs)**
  - 執行 `docker logs --tail 100 <container_id>`。
  - 如果沒有 Log，代表程式在輸出 Log 前就崩潰，或寫錯地方（寫到檔案而非 STDOUT）。
- [ ] **手動啟動除錯 (Manual Start)**
  - 使用 `docker run --rm -it --entrypoint sh <image_name>` 進入容器。
  - 手動執行啟動指令，觀察錯誤訊息。

### Phase 2: 容器執行中但行為異常 (Runtime Issues)

- [ ] **進入容器檢查 (Exec)**
  - 執行 `docker exec -it <container_id> /bin/sh` (或 `bash`)。
  - 檢查關鍵設定檔內容：`cat /app/config.json`。
  - 檢查環境變數：`env`。
- [ ] **檢查資源使用量 (Stats)**
  - 執行 `docker stats`。
  - CPU 是否飆高？記憶體是否接近上限？
- [ ] **檢查網路連線 (Networking)**
  - 容器內 DNS 解析是否正常？`nslookup database-host`。
  - 端口是否監聽？`netstat -tulpn` (若無指令可用 Sidecar 模式)。

### Phase 3: 設定與環境驗證 (Configuration Audit)

- [ ] **檢查詳細設定 (Inspect)**
  - `docker inspect <container_id>`。
  - **Mounts**: 宿主機路徑是否正確？讀寫權限（RW/RO）是否正確？
  - **Env**: 傳入的密碼或 API Key 是否正確？

---

## Real-world examples｜實戰案例

### 案例一：神秘的 Exit Code 137 (The OOM Killer)

**情境**：一個 Java 應用程式容器不定時重啟，Log 中沒有任何 Exception 堆疊追蹤（Stack Trace），突然就斷了。

**診斷步驟**：
1.  `docker ps -a` 顯示 `Exited (137) 2 minutes ago`。
2.  `docker inspect <id> | grep OOMKilled` 顯示 `true`。
3.  **原因**：Docker 限制了容器記憶體（例如 512MB），但 JVM Heap 設定過大或未啟用容器感知（Container Awareness）。
4.  **解法**：調整 Docker 記憶體限制，或在 JVM 參數加入 `-XX:MaxRAMPercentage`。

### 案例二：Windows 到 Linux 的換行符號陷阱 (CRLF vs LF)

**情境**：構建了一個 Python 腳本的 Image，但在啟動時報錯：`/bin/sh: /app/entrypoint.sh: not found`，即使你確認檔案真的在那裡。

**診斷步驟**：
1.  使用 `docker run -it --entrypoint sh <image>` 進入容器。
2.  `ls -la /app/entrypoint.sh` 確認檔案存在且有執行權限。
3.  使用 `cat -v /app/entrypoint.sh` 查看內容。
4.  **發現**：看到行尾有 `^M` 符號。
5.  **原因**：開發者在 Windows 上編輯檔案，使用了 CRLF (`\r\n`)，但 Linux Shell 只接受 LF (`\n`)。這導致直譯器把 `#!/bin/sh\r` 當作路徑，當然找不到。
6.  **解法**：在 IDE 中將 Line Ending 改為 LF，或在 Dockerfile 中加入 `RUN sed -i 's/\r$//' entrypoint.sh`。

### 案例三：連線被拒 (Connection Refused on Localhost)

**情境**：Web 容器嘗試連線 Redis 容器，設定檔寫 `REDIS_HOST=localhost`，結果報錯 `Connection Refused`。

**診斷步驟**：
1.  進入 Web 容器：`docker exec -it web_container sh`。
2.  `ping localhost` -> 回應是 `127.0.0.1` (Web 容器自己)。
3.  **原因**：容器隔離性。Web 容器的 Localhost 不是宿主機，也不是 Redis 容器。
4.  **解法**：
    *   若使用 Docker Compose，將 `REDIS_HOST` 改為 Service 名稱（例如 `redis`）。
    *   若需連線宿主機上的服務，使用 `host.docker.internal` (Mac/Windows) 或 `--network host` (Linux)。