# 故障排除指南與診斷流程 / Troubleshooting Guide and Diagnostic Workflows

## Mental model｜心智模型

在排查 GitLab CI/CD 問題時，最有效的思維方式是將系統視為 **「分層的傳遞鏈 (Layered Delivery Chain)」**。當問題發生時，請先定位問題落在哪一層，而不是盲目地修改程式碼。

### The 3-Layer Diagnostic Model (三層診斷模型)

1.  **定義層 (Definition Layer - The Blueprint)**
    *   **核心問題**：YAML 語法是否正確？邏輯流程是否符合預期？
    *   **症狀**：Pipeline 無法建立 (Yaml invalid)、Job 順序錯誤、變數未生效。
    *   **負責對象**：GitLab Server (Linter)。

2.  **編排層 (Orchestration Layer - The Manager)**
    *   **核心問題**：任務是否被正確調度？是否有資源可用？
    *   **症狀**：Pipeline 狀態為 `Pending` (Stuck)、`Timeout`、Runner 無法接單。
    *   **負責對象**：GitLab Coordinator & Sidekiq。

3.  **執行層 (Execution Layer - The Worker)**
    *   **核心問題**：腳本執行環境是否正常？指令是否報錯？網路是否通暢？
    *   **症狀**：Job 狀態為 `Failed`、Script error、Connection refused、Docker image pull failed。
    *   **負責對象**：GitLab Runner & Executor (Docker/K8s/Shell)。

> **Key Insight**: 大多數 "Stuck" 的問題發生在 **編排層**（找不到 Runner），而大多數 "Failed" 的問題發生在 **執行層**（環境或腳本錯誤）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Enable Debug Tracing (開啟除錯追蹤)
當 Job 失敗且 log 資訊不足時，不要猜測。透過變數開啟 GitLab Runner 的詳細日誌。
*   **Pattern**: 在 `.gitlab-ci.yml` 或 CI/CD Settings 變數中設定 `CI_DEBUG_TRACE: "true"`。
*   **Effect**: 這會顯示 Runner 處理腳本的每一個步驟，包含變數展開 (expansion) 的過程，極有助於排查變數未生效或 Shell 解析錯誤的問題。
    *   *注意：這可能會在 Log 中暴露敏感資訊，請謹慎使用並在排查後關閉。*

### 2. Artifacts for Failure Analysis (失敗現場保留)
當測試失敗或畫面渲染錯誤時，單看文字 Log 是不夠的。
*   **Pattern**: 設定 `artifacts` 的 `when: on_failure` 策略。
*   **Usage**:
    ```yaml
    test_job:
      script: npm run test:e2e
      artifacts:
        when: on_failure
        paths:
          - cypress/screenshots/
          - logs/error.log
        expire_in: 1 day
    ```

### 3. Interactive Web Terminal (互動式終端機)
如果你使用共享 Runner 或 Kubernetes Runner，本地難以完全模擬環境。
*   **Pattern**: 在 Job 運行時（或重試時），點擊右側 sidebar 的 "Debug" (Terminal) 按鈕。
*   **Benefit**: 直接進入正在運行的容器內執行 `ls`, `env`, `curl` 等指令，即時驗證環境狀態。

### 4. The "Echo Debug" Strategy (回顯除錯法)
在腳本執行關鍵指令前，先印出當前上下文。
*   **Pattern**:
    ```yaml
    script:
      - echo "Current User: $(whoami)"
      - echo "Current Dir: $(pwd)"
      - echo "Environment: $DEPLOY_ENV"  # 檢查變數是否為空
      - ./deploy.sh
    ```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Blind Retry" Loop (盲目重試迴圈)
*   **Anti-pattern**: 看到紅色叉叉就直接按 Retry，期望它「這次會過」。
*   **Why it's bad**: 如果不是網路波動 (Transient Network Issue)，重試只是浪費 Runner 資源 (Compute Credits) 並延遲修復時間。
*   **Correction**: 先看 Log 的最後 10 行，確認 Exit Code。

### 2. Swallowing Errors (吞噬錯誤)
*   **Anti-pattern**: 在 script 中使用 `command || true` 或過度依賴 `allow_failure: true` 來讓 Pipeline 變綠。
*   **Why it's bad**: 這會隱藏真正的問題（如測試未執行、依賴安裝失敗），導致壞掉的程式碼被部署到生產環境。
*   **Correction**: 只有在「該失敗不影響整體交付」時才允許失敗，否則應修復根本原因。

### 3. Debugging by Printing Secrets (印出機密資訊)
*   **Anti-pattern**: 為了檢查 API Key 是否正確，直接 `echo $API_KEY`。
*   **Why it's bad**: 即使你馬上刪除 Job log，GitLab 資料庫或 Runner 硬碟中可能仍有殘留，且 Log 可能已被轉發到 SIEM 系統。
*   **Correction**: 使用 `md5sum` 或檢查字串長度來驗證，例如 `echo ${API_KEY:0:3}***` 或 `echo -n $API_KEY | md5sum`。

### 4. Ignoring Runner Caches (忽視快取污染)
*   **Anti-pattern**: 假設每次 Job 都是全新的環境，卻忽略了 Runner 本地的 Docker Cache 或 GitLab CI Cache。
*   **Correction**: 當遇到詭異的依賴問題時，嘗試點擊 "Clear Runner Caches" 或在 Job 中暫時停用 Cache。

---

## Checklists & workflows｜檢查清單與流程

### Scenario A: Pipeline is Stuck (Pending)
*Pipeline 停滯在 Pending 狀態，沒有任何 Job 開始執行。*

- [ ] **Check Tags (檢查標籤)**: Job 定義的 `tags` 是否與現有的 Runner 標籤完全匹配？（這是最常見原因）
- [ ] **Check Runner Status (檢查 Runner 狀態)**: 到 `Settings > CI/CD > Runners` 確認 Runner 是否亮綠燈 (Online) 且未被暫停 (Not Paused)。
- [ ] **Check Run Untagged**: 如果 Job 沒有 tag，Runner 是否勾選了 "Run untagged jobs"？
- [ ] **Check Concurrency Limits**: 是否達到專案或群組的 CI Quota 上限？或是 Runner 的 `concurrent` 設定已滿？

### Scenario B: Job Failed with "Script Failure"
*Job 執行了但報錯結束。*

- [ ] **Check Exit Code**: 是 `1` (一般錯誤), `127` (Command not found), 還是 `137` (OOM Killed)?
- [ ] **Check Environment Variables**: 變數是否在 Settings 中被設為 `Protected`，但該 Job 跑在非 Protected Branch 上？（導致變數為空）
- [ ] **Check Dependencies**: 是否因為網路問題導致 `npm install` / `pip install` 失敗？
- [ ] **Check Workdir**: 是否誤以為在 Git root，但其實被 `cd` 到了子目錄？

### Scenario C: Runner Connectivity / System Errors
*出現 "Job failed (system failure)" 或 "Dial tcp..." 錯誤。*

- [ ] **Check Disk Space**: Runner 機器是否磁碟已滿 (Docker images/volumes 堆積)？
- [ ] **Check Network/Firewall**: Runner 是否無法連線到 GitLab Server (`git fetch` 失敗) 或無法連線到外部 Registry？
- [ ] **Check Docker Daemon**: Runner 上的 Docker Service 是否活著？

### Scenario D: 500 Errors on GitLab UI
*操作 GitLab 介面時出現 500 錯誤。*

- [ ] **Check Status Page**: 確認是否為 GitLab.com 官方故障。
- [ ] **Check Merge Request Size**: Diff 是否過大導致 Timeout？
- [ ] **Check Webhooks**: 是否有錯誤配置的 Webhook 導致操作卡頓或失敗？

---

## Real-world examples｜實戰案例

### Example 1: The "Invisible" Variable Issue (變數隱形事件)

**情境**：開發者在 CI/CD Settings 設定了 `AWS_ACCESS_KEY_ID`，但在 Feature branch 的 Pipeline 中，部署腳本一直報錯 "Missing Credentials"。

**診斷流程**：
1.  開發者加上 `echo "Key length: ${#AWS_ACCESS_KEY_ID}"`，發現長度為 0。
2.  檢查 Settings，發現該變數被勾選了 **"Protect variable"**。
3.  **Root Cause**: "Protect variable" 表示該變數只會暴露給 "Protected Branches" (如 `main` / `master`)。Feature branch 不是受保護分支，因此讀不到變數。
4.  **Fix**: 取消勾選 Protect variable，或將該變數限制範圍 (Environment Scope) 設定正確。

### Example 2: The "Docker in Docker" Network Failure (DinD 連線失敗)

**情境**：使用 `docker:dind` 服務來 build image，卻報錯 `Cannot connect to the Docker daemon at tcp://docker:2375`.

**診斷流程**：
1.  檢查 `.gitlab-ci.yml` 是否有定義 `services: - docker:dind`。
2.  檢查 Runner 是否為 Kubernetes Executor。
3.  **Root Cause**: 在 GitLab 12.4+ 或新版 Docker (19.03+) 中，TLS 預設開啟。如果沒有正確設定 `DOCKER_TLS_CERTDIR`，Client 會嘗試用非 TLS port 連線但 Server 拒絕，或者 Hostname 解析錯誤。
4.  **Fix**:
    ```yaml
    variables:
      DOCKER_HOST: tcp://docker:2376
      DOCKER_TLS_CERTDIR: "/certs"
      DOCKER_TLS_VERIFY: 1
      DOCKER_CERT_PATH: "$DOCKER_TLS_CERTDIR/client"
    ```

### Example 3: The "Zombie" Cache (快取殭屍)

**情境**：`npm install` 成功，但 `npm run build` 卻報錯說找不到某個 module，即便 `package.json` 已經更新了。

**診斷流程**：
1.  查看 Log，發現 `node_modules` 是從 Cache 恢復的。
2.  **Root Cause**: `node_modules` 內的快取檔案損壞，或者 `package-lock.json` 與快取內容不一致，但 `npm install` 判斷錯誤沒有重新下載。
3.  **Fix**:
    *   短期：在 Pipeline 介面點擊 "Clear Runner Caches"。
    *   長期：修改 Cache Key 的策略，綁定 lock file。
    ```yaml
    cache:
      key:
        files:
          - package-lock.json
      paths:
        - node_modules/
    ```