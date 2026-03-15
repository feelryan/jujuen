# 故障排除與除錯指南 (Troubleshooting) / Troubleshooting and Debugging Guide

## Mental model｜心智模型

在 Jenkins 進行除錯時，必須建立 **「分層洋蔥 (Layered Onion)」** 的心智模型。Jenkins 並非單一應用程式，而是一個由多個層級組成的複雜分散式系統。當問題發生時，請先定位問題位於哪一層：

1.  **基礎設施層 (Infrastructure Layer)**：
    -   **Agent 資源**：Kubernetes Pod 是否被 OOM Kill？VM 是否磁碟滿了？網路是否通暢？
    -   **Master 資源**：Controller 的 JVM Heap 是否足夠？Disk I/O 是否過高？
2.  **Jenkins 核心與插件層 (Core & Plugins Layer)**：
    -   **Plugin Conflict**：新安裝的 Plugin 是否與舊版本衝突？
    -   **Queue & Scheduling**：Executor 是否耗盡？Build 是否卡在 Queue 中無法調度？
3.  **Pipeline 邏輯層 (Pipeline Logic Layer)**：
    -   **Syntax Error**：Groovy 語法錯誤、括號不匹配。
    -   **Runtime Error**：Shell script (`sh`) 執行失敗、環境變數未設定、權限不足。

**The "Detective" Mindset:**
不要只看「紅燈 (Build Failed)」，要看「案發現場」。
-   如果是 **Build 失敗**：通常是 Pipeline 邏輯或 Agent 環境問題。
-   如果是 **Build 卡住 (Hanging)**：通常是資源鎖死 (Deadlock)、無限迴圈或 Agent 通訊中斷。
-   如果是 **Jenkins 變慢/崩潰**：通常是 Master JVM 記憶體洩漏或大量併發導致的 I/O 瓶頸。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 善用 "Replay" 功能進行快速迭代 (Rapid Iteration with Replay)
不要為了修復一個 typo 而反覆 commit/push 到 Git。
-   **Pattern**: 在 Jenkins UI 的 Build 頁面左側點擊 **"Replay"**。
-   **Why**: 允許你直接在瀏覽器中修改當次 Build 的 Pipeline Script 並重新執行。這不會影響 Git repo，但能極快地驗證修復方案。
-   **Best Practice**: 驗證成功後，務必將修改複製回 IDE 並 Commit。

### 2. Pipeline 的二分法除錯 (Binary Search Debugging)
當 Pipeline 莫名其妙失敗且 Log 不明確時：
-   **Pattern**: 使用 `echo` 或 `error` 語句，或者註解掉一半的 `stages`。
-   **Action**: 如果註解掉後半段後成功了，問題就在後半段。重複此步驟直到縮小範圍至特定指令。

### 3. 處理 "Zombie" Builds 的腳本控制台 (Script Console for Zombies)
有時候 UI 上無法停止一個卡住的 Build（點了 'X' 沒反應）。
-   **Pattern**: 使用 `Manage Jenkins` -> `Script Console` 強制終止。
-   **Code Snippet**:
    ```groovy
    // 強制停止特定 Job 的所有執行中 Builds
    Jenkins.instance.getItemByFullName("Your-Job-Name")
        .getBuilds()
        .findAll { it.isBuilding() }
        .each { it.doStop(); println "Stopped ${it}" }
    ```

### 4. 針對 OOM 的防禦性配置 (Defensive Config for OOM)
-   **Container Agents**: 始終為 Kubernetes Agents 設定 Request/Limit。
-   **JVM Options**: 確保 Master 的 `Xmx` 設定合理（通常建議實體記憶體的 70-80%），並開啟 `-XX:+HeapDumpOnOutOfMemoryError` 以便事後分析。

### 5. 結構化日誌與 Timestamper (Structured Logs)
-   **Pattern**: 安裝 **Timestamper** plugin。
-   **Why**: 知道某個步驟「花了多久」比知道它「做了什麼」更能幫助定位效能瓶頸或卡住的原因。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Log Flooding (日誌洪水)
-   **Anti-pattern**: 在 Pipeline 中開啟 `set -x` 並且輸出了數百 MB 的文字（例如 dump 整個 DB schema 或 binary 內容）。
-   **Consequence**: 瀏覽器開啟 Console Output 時崩潰；Jenkins Master 的 Disk I/O 飆高甚至當機。
-   **Fix**: 使用 `logRotator` 限制日誌大小，或重定向詳細輸出到檔案 (`sh 'cmd > output.log'`) 並作為 Artifact 保存，而非直接印在 Console。

### 2. 盲目重啟 (Blind Restarts)
-   **Anti-pattern**: 遇到 Jenkins 變慢或卡住，直接重啟 Service 或 Kill Process。
-   **Consequence**: 失去了 **Thread Dump** 和現場證據，問題下次還會發生。
-   **Fix**: 重啟前，至少執行一次 `jstack <pid>` 保存 Thread Dump。

### 3. 在 Master Node 執行重量級任務 (Heavy Lifting on Master)
-   **Anti-pattern**: 在 `agent none` 或 `agent any` (當只有 master 時) 執行編譯、Docker build。
-   **Consequence**: Master CPU/Mem 耗盡，導致 UI 無法存取，所有 Agents 斷線。
-   **Fix**: 確保 Master 的 Executor 數量設為 0，強制所有任務在 Agent 上執行。

### 4. 忽略 "Scripts not permitted" 警告
-   **Anti-pattern**: 遇到 Sandbox 安全性錯誤時，盲目地在 "In-process Script Approval" 點擊 Approve，甚至關閉 Sandbox。
-   **Consequence**: 引入安全漏洞。
-   **Fix**: 將複雜邏輯移至 **Shared Library** (它在 Trusted Scope 執行)，或改寫程式碼避免使用受限的 Java API。

---

## Checklists & workflows｜檢查清單與流程

### Workflow: 處理 "Build 卡住 (Build Hanging)"

1.  **檢查 Console Output**：
    -   [ ] 最後一行 Log 是什麼？是否在等待 User Input (`input` step)？
    -   [ ] 是否開啟了 Timestamper？查看最後一行 Log 的時間與現在相差多久。
2.  **檢查 Agent 狀態**：
    -   [ ] Agent 是否顯示 "Offline"？
    -   [ ] (如果是 K8s) `kubectl get pod` 查看 Agent Pod 是否還在 Running？是否被 OOMKilled？
3.  **收集 Thread Dump (如果懷疑是死鎖)**：
    -   [ ] 進入 `https://<jenkins-url>/threadDump` 查看 Master 線程。
    -   [ ] 如果是 Agent 卡住，點擊該 Node 的頁面 -> `Thread Dump`。
    -   [ ] 搜尋關鍵字：`Deadlock` 或正在執行的 Pipeline 步驟名稱。
4.  **強制終止**：
    -   [ ] UI 點擊 `X` (Abort)。
    -   [ ] 無效則使用 Script Console 強制 `doStop()` 或 `doKill()`。

### Workflow: 處理 "Pipeline 語法/執行錯誤"

1.  **定位錯誤類型**：
    -   [ ] **Syntax Error**: 通常發生在 Build 開始前。檢查 `Jenkinsfile` 括號、縮排。
    -   [ ] **Groovy Runtime Error**: `NullPointerException`, `MissingMethodException`. 使用 Replay 插入 `println` 除錯。
    -   [ ] **Shell Error**: `exit code 127` (command not found), `exit code 1` (general error).
2.  **環境驗證**：
    -   [ ] 在 Pipeline 中加入 `sh 'env'` 或 `sh 'whoami'` 確認環境變數與執行身份。
    -   [ ] 檢查 Workspace 是否有殘留的髒檔案 (`cleanWs()` is your friend).

### Checklist: Jenkins 效能變差排查

- [ ] **Disk Space**: Master 的磁碟空間使用率是否超過 80%？
- [ ] **Plugin Updates**: 最近是否更新了核心插件？(查看 Plugin Manager -> Installed -> 依安裝時間排序)。
- [ ] **Garbage Collection**: 查看 GC Log，是否頻繁 Full GC？(Memory Leak 徵兆)。
- [ ] **Build History**: 是否保留了過多的舊 Build？(檢查 `Discard old builds` 設定)。

---

## Real-world examples｜實戰案例

### Case 1: The "Silent Killer" (OOM Killer on Agent)
**情境**：Build 執行到一半突然失敗，Console Log 顯示 `Channel closed` 或 `Connection reset`，但沒有具體的編譯錯誤訊息。
**排查**：
1.  開發者以為是網路問題，重試多次無效。
2.  檢查 Kubernetes 叢集：`kubectl get pod -w` 觀察 Build 過程。
3.  發現 Pod 狀態瞬間變成 `OOMKilled` 然後重啟或消失。
**解決**：
在 `podTemplate` 或 `agent` 定義中增加 Memory Limit。
```groovy
// Fix: Increase memory request/limit
container('jnlp') {
    resources(limit: [memory: '2Gi'], request: [memory: '1Gi'])
}
```

### Case 2: Groovy "Non-Serializable" Exception
**情境**：Pipeline 執行時報錯 `java.io.NotSerializableException: java.util.regex.Matcher`。
**原因**：Jenkins Pipeline (CPS) 會在每一步驟後將狀態序列化 (Serialize) 到磁碟以便暫停/恢復。某些 Java 物件（如 Matcher, Iterator, Network Socket）無法被序列化。
**錯誤寫法**：
```groovy
def matcher = (text =~ /pattern/) // Matcher is not serializable
sh "echo doing something" // Jenkins tries to save state here, but fails because 'matcher' is still in scope
if (matcher.find()) { ... }
```
**解決**：
使用 `@NonCPS` 註解函式，或將變數設為 null，或將邏輯封裝在字串處理中。
```groovy
// Fix: Use a method marked with @NonCPS for complex logic
@NonCPS
def hasMatch(text) {
    return (text =~ /pattern/).find()
}
```

### Case 3: The "Workspace Lock" (Resource Contention)
**情境**：兩個並行執行的 Job (Parallel Stages) 隨機失敗，報錯 `Workspace in use` 或 `File access denied`。
**原因**：多個並行任務試圖在同一個 Node 上使用同一個 Workspace 目錄。
**解決**：
確保並行區塊使用 `ws` (Workspace) step 分離工作目錄，或強制分配到不同 Agent。
```groovy
parallel(
    "Test A": {
        node('linux') {
            ws('workspace/test-a') { // Isolate workspace
                sh './run-test-a.sh'
            }
        }
    },
    "Test B": { ... }
)
```