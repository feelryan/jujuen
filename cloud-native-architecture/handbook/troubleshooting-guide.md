# 實戰故障排查與診斷流程 / Practical Troubleshooting & Diagnostics Guide

在雲原生架構中，故障排查（Troubleshooting）與傳統單體架構有著本質上的不同。服務是短暫的（Ephemeral）、網路是虛擬的（Overlay Network）、且依賴關係是動態的。本章節提供一套結構化的診斷思維與實戰 SOP，協助你在高壓的 Incident 情境下保持冷靜並精準定位問題。

---

## Mental model｜心智模型

### 1. The Onion Theory of Debugging (洋蔥剝皮理論)
不要一開始就跳進去檢查 Application Code。雲原生故障通常發生在不同層級，應由外而內、由下而上進行排查：
1.  **Cluster/Node Level**: 基礎設施是否健康？（Node 是否 Ready？資源是否耗盡？）
2.  **Controller Level**: 調度器是否正常工作？（Deployment/StatefulSet 是否有正確的 Replicas？）
3.  **Pod Level**: 容器是否啟動？（Status 是 Pending, CrashLoopBackOff 還是 Running？）
4.  **Network Level**: 服務間能否通訊？（DNS 解析、Service IP、Network Policy）
5.  **Application Level**: 程式邏輯錯誤？（HTTP 500, Exception Logs）

### 2. Evidence Preservation vs. Recovery (保留證據 vs. 快速恢復)
在傳統 VM 時代，重啟往往能解決問題。但在 Kubernetes 中，Pod 重啟（Restart）意味著容器內的暫存檔案與 Logs 可能會消失（如果沒有正確的 Log Shipping）。
*   **Mental Shift**: 在手動刪除 Pod 之前，先思考「我是否已經收集了足夠的 forensic data（鑑識資料）？」

### 3. Distributed Tracing as the Map (分散式追蹤即地圖)
在微服務中，單一服務的 Log 只是拼圖的一小塊。必須建立「請求鏈路（Request Path）」的思維。
*   **Concept**: 故障通常不是發生在服務「內部」，而是發生在服務「之間」。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Ephemeral Debug Containers (臨時除錯容器)
現代容器映像檔傾向使用 Distroless 或 Alpine 以縮減體積與攻擊面，這導致容器內沒有 `curl`, `ping` 甚至 `sh`。
*   **Practice**: 使用 `kubectl debug` 功能，將一個帶有完整工具箱（如 `nicolaka/netshoot`）的 Ephemeral Container 掛載到目標 Pod 上，共享 Process Namespace 與 Network Namespace。
*   **Command**: `kubectl debug -it <target-pod> --image=nicolaka/netshoot --target=<container-name>`

### 2. Structured Logging & Correlation IDs
*   **Practice**: 所有 Log 必須是 JSON 格式，且包含 `trace_id` 與 `span_id`。
*   **Why**: 當你在 Kibana/Loki 搜尋 `error` 時，你需要透過 ID 串聯起該請求在所有微服務中的軌跡。

### 3. The "Describe" First Approach
*   **Practice**: 在看 Log 之前，先看 Kubernetes Event。
*   **Why**: `kubectl describe pod <pod-name>` 中的 Events section 往往直接告訴你答案（例如：MountVolume.SetUp failed, Preempted, OOMKilled）。

### 4. Liveness vs. Readiness Separation
*   **Practice**: 嚴格區分 Liveness（我還活著嗎？）與 Readiness（我可以接客了嗎？）。
*   **Pattern**: 故障排查時，如果發現 Pod 不斷重啟，檢查 Liveness Probe；如果 Pod 活著但沒有流量進來，檢查 Readiness Probe。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Blind Restart" (盲目重啟)
*   **Anti-pattern**: 遇到問題直接刪除 Pod 讓 K8s 重建。
*   **Consequence**: 如果是 `CrashLoopBackOff`，重啟後問題依舊，且你失去了上一次崩潰前的現場（除非有持久化 Log）。如果是 Resource Limit 問題，重啟只是延後下一次 OOM 的時間。

### 2. Confusing Connection Refused with Timeout
*   **Anti-pattern**: 看到連線失敗就認為是服務掛了。
*   **Clarification**:
    *   **Connection Refused**: 封包到達了目標，但沒有 Process 監聽該 Port（服務沒起起來，或 Port 設定錯誤）。
    *   **Timeout**: 封包在路上丟失或被丟棄（防火牆、Network Policy 阻擋、路由錯誤）。
    *   **Pitfall**: 混淆兩者會導致你往錯誤的方向排查（例如在 Network Policy 問題上浪費時間檢查 Application Config）。

### 3. Ignoring Resource Limits (OOMKilled 隱形殺手)
*   **Anti-pattern**: 沒有設定 Request/Limit，或者 Limit 設定不合理。
*   **Pitfall**: 當 Pod 突然消失且沒有 Error Log 時，90% 是因為記憶體超限被 Kernel 的 OOM Killer 殺掉。這不會在 App Log 顯示，只會出現在 `kubectl describe` 的 `LastState: OOMKilled` 或 Node 的 `dmesg` 中。

---

## Checklists & workflows｜檢查清單與流程

當收到告警或回報異常時，請依照此決策樹進行排查：

### Phase 1: Pod Lifecycle Check (生死狀態確認)
- [ ] **Check Status**: `kubectl get pods`
    - **Pending**: 資源不足 (CPU/Mem)、Taint/Toleration 不匹配、PVC 無法綁定。
    - **ImagePullBackOff**: 映像檔名稱錯誤、Tag 不存在、Secret 權限不足。
    - **CrashLoopBackOff**: 應用程式啟動失敗、配置錯誤、Missing Environment Variables。
    - **Evicted**: Node 資源耗盡（Disk Pressure, Memory Pressure）。
- [ ] **Check Events**: `kubectl describe pod <pod-name>` (查看底部的 Events)。
- [ ] **Check Exit Code**:
    - `1`: 一般應用程式錯誤。
    - `137`: **OOMKilled** (128 + 9 SIGKILL)。需調大 Memory Limit 或修復 Memory Leak。
    - `143`: Graceful Termination (SIGTERM)。

### Phase 2: Application Logic Check (應用邏輯確認)
- [ ] **Check Logs**: `kubectl logs <pod-name> [-c <container-name>] --previous`
    - 使用 `--previous` 查看崩潰前的 Log。
- [ ] **Check Config**: 驗證掛載的 ConfigMap 與 Secret 是否正確。

### Phase 3: Networking & Connectivity Check (網路連通確認)
*如果 Pod 是 Running 但服務無法存取：*
- [ ] **Check Service**: `kubectl get svc` 確認 ClusterIP 與 Port 對應。
- [ ] **Check Endpoints**: `kubectl get endpoints <svc-name>`
    - 如果 Endpoints 為空，代表沒有 Pod 匹配 Service Selector，或 Pod 未通過 Readiness Probe。
- [ ] **DNS Check**: 進入 Pod 內部 (或是 debug container) 執行 `nslookup <service-name>`。
- [ ] **Network Policy**: 確認是否有 NetworkPolicy 阻擋了 Ingress/Egress 流量。

### Phase 4: Node & Infrastructure (基礎設施確認)
- [ ] **Check Node Status**: `kubectl get nodes` (Ready?)
- [ ] **Check Node Resources**: `kubectl top nodes` (CPU/Memory Load)

---

## Real-world examples｜實戰案例

### Scenario 1: The "Silent" Death (OOMKilled)
**症狀**: 客戶回報偶發性 502 Errors，監控顯示 Pod 數量穩定，但 Log 中沒有 Exception。
**排查**:
1. 執行 `kubectl get pods`，發現 `RESTARTS` 次數異常高。
2. 執行 `kubectl describe pod <pod-name>`。
3. 發現 `Last State: Terminated`, `Reason: OOMKilled`, `Exit Code: 137`。
**診斷**: 應用程式記憶體洩漏或流量突波超過 Limit。
**解法**: 暫時調高 Memory Limit，並使用 Profiler (如 pprof) 分析記憶體使用狀況。

### Scenario 2: The "It Works on My Machine" (Network Policy)
**症狀**: 前端服務 (Frontend) 呼叫後端服務 (Backend) 超時 (Timeout)，但在同一 Namespace 下手動測試 `curl` 卻可以通。
**排查**:
1. 檢查 Backend Service Endpoints -> 正常。
2. 檢查 Backend Pod Logs -> 沒有收到請求。
3. 懷疑網路阻擋。檢查 Network Policy: `kubectl get netpol`。
4. 發現 Backend 有一條 `Default-Deny` 規則，且 Allow List 只允許帶有 `role: api-gateway` label 的來源。
5. 檢查 Frontend Pod 的 Labels，發現缺少 `role: api-gateway`。
**解法**: 為 Frontend Pod 加上正確 Label，或修改 Network Policy 允許 Frontend 存取。

### Scenario 3: The "Infinite Pending" (Resource Quota)
**症狀**: 新部署的 Deployment 卡在 0/3 Ready，Pod 狀態一直是 Pending。
**排查**:
1. `kubectl describe pod <pending-pod-id>`。
2. Event 顯示: `FailedScheduling: 0/5 nodes are available: 5 Insufficient cpu.`。
3. 檢查 Cluster 資源，發現其實還有空閒 CPU。
4. 檢查 Namespace Quota: `kubectl describe resourcequota -n <namespace>`。
5. 發現 Namespace 的 CPU Requests Hard Limit 已達上限。
**解法**: 調整 ResourceQuota 或降低 Deployment 的 CPU Request 設定。