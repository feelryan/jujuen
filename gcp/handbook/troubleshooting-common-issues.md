# GCP 常見故障排除流程 / Troubleshooting Common GCP Issues

## Mental model｜心智模型

在 GCP 進行故障排除（Troubleshooting）時，最有效的心智模型是 **「請求路徑分層剝洋蔥」（Request Path Layering）**。不要將錯誤視為一個單一的黑盒子，而是將其拆解為請求流經的各個關卡。

### 1. The Request Lifecycle (請求生命週期)
當一個請求失敗時，它必定在以下某個環節被攔截或崩潰：
1.  **Edge / Network**: Cloud DNS, Cloud CDN, External Load Balancer.
2.  **Security Perimeter**: Cloud Armor, Firewall Rules, VPC Service Controls.
3.  **Compute / Infrastructure**: GKE Node, VM Instance, Cloud Run Revision.
4.  **Application Runtime**: 容器崩潰 (CrashLoopBackOff), 記憶體溢出 (OOM), 程式碼 Exception.
5.  **Identity & Access (IAM)**: Service Account 權限, Scopes, Workload Identity.
6.  **Dependencies**: 連線到 Cloud SQL, Redis, 或外部 API。

### 2. Signal vs. Noise (訊號與雜訊)
GCP 的錯誤訊息通常非常具體，但容易被淹沒。
- **4xx Errors**: 通常是 **配置** 或 **權限** 問題（Client Side / Auth）。
- **5xx Errors**: 通常是 **基礎設施** 或 **應用程式崩潰** 問題（Server Side）。
- **Quota Errors**: 資源耗盡，屬於 Capacity Planning 問題。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 利用 Trace ID 串聯全域日誌 (Correlation with Trace IDs)
在分散式系統中，單看一條 Log 是沒有意義的。
- **Pattern**: 確保你的應用程式讀取 `X-Cloud-Trace-Context` header，並將其寫入 Log 的 `trace` 欄位。
- **Benefit**: 這讓你能從 Cloud Load Balancer 的 Access Log 一路追蹤到後端 App 的 Application Log，甚至到資料庫的 Query Log。

### 2. IAM Policy Troubleshooter 是你的好朋友
遇到 `403 Permission Denied` 時，不要盲目猜測。
- **Practice**: 使用 GCP Console 中的 **Policy Troubleshooter**。
- **Action**: 輸入 `Principal` (誰), `Resource` (哪個 Bucket/VM), `Permission` (想做什麼)，它會告訴你哪條 Role 允許或拒絕了該操作。

### 3. 區分 Liveness 與 Readiness Probes
GCP Load Balancer 的 502 錯誤有一大半源自於錯誤的 Health Check 配置。
- **Readiness**: 流量是否應該進來？（失敗則切斷流量，回傳 502）。
- **Liveness**: 應用程式是否活著？（失敗則重啟 Pod/VM）。
- **Best Practice**: 不要讓 Readiness Probe 依賴外部服務（如 DB），否則 DB 一閃斷，所有 Pod 同時下線，導致雪崩。

### 4. 善用 Error Reporting
不要只看 Logging。**Cloud Error Reporting** 會自動聚合相似的 Stack Traces。
- **Pattern**: 每天早上檢查 Error Reporting 的 "New Errors"，這是發現新部署引入 Bug 的最快方式。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. "Works on my machine" (忽略防火牆規則)
- **Anti-pattern**: 在本地測試通過，部署到 GKE/GCE 後 LB 報 502。
- **Pitfall**: GCP 的 Load Balancer 使用特定的 IP 範圍來進行 Health Check (`130.211.0.0/22` 和 `35.191.0.0/16`)。
- **Consequence**: 如果你的 Firewall 或 Security Group 沒開這些 IP，LB 會認為後端全死，直接回傳 502。

### 2. 賦予過大權限以解決 403 (Over-privileged IAM)
- **Anti-pattern**: 遇到 Permission Denied，直接給 Service Account `Editor` 或 `Owner` 權限。
- **Risk**: 這是嚴重的資安漏洞。應遵循 **Least Privilege** 原則，缺什麼補什麼（例如只給 `roles/storage.objectViewer`）。

### 3. 忽略 Quota 限制 (Quota Blindness)
- **Anti-pattern**: 系統在促銷活動高峰期突然無法擴展（Scale-up failed）。
- **Pitfall**: 許多 Quota（如 Global IP 數量、CPU Core 數）是硬上限。
- **Fix**: 設定 Quota 監控警報，提前申請配額提升。

### 4. 混淆 Service Account 與 User Identity
- **Anti-pattern**: 在本地用 `gcloud auth login` (User Credential) 跑通了程式，上雲後用 Default Service Account 卻失敗。
- **Reason**: 本地 User 權限通常大於雲端上的 Service Account。務必在本地使用 `gcloud auth activate-service-account` 模擬真實環境。

---

## Checklists & workflows｜檢查清單與流程

### SOP 1: 502 Bad Gateway / 503 Service Unavailable 排查
當 Load Balancer 回傳 5xx 錯誤時：

- [ ] **檢查 Health Check 狀態**：
    - 到 Load Balancer 詳細頁面，查看 Backend Service 的健康狀態。是 `0/N` 嗎？
- [ ] **檢查防火牆 (Firewall Rules)**：
    - 是否允許來自 `130.211.0.0/22` 和 `35.191.0.0/16` 的 TCP 流量到達你的 Instance/Pod 端口？
- [ ] **檢查應用程式監聽端口 (Listening Port)**：
    - 應用程式是否真的監聽在 LB 設定的端口上？（例如 LB 送到 8080，但 App 聽在 80）。
- [ ] **檢查 Keep-Alive Timeout**：
    - HTTP(S) LB 的 Timeout 預設是 600s。如果後端 App (如 Gunicorn/Node.js) 的 Timeout 短於這個時間並主動切斷連線，LB 會報 502。
    - **Rule**: `LB Timeout < App Keep-Alive Timeout`。

### SOP 2: 403 Permission Denied (IAM) 排查
當應用程式存取 GCP 資源（如 GCS, BigQuery）失敗時：

- [ ] **確認身份 (Identity)**：
    - 檢查 Log，確認是哪個 `principalEmail` 發起的請求？是預期的 Service Account 嗎？
- [ ] **檢查 IAM Role**：
    - 該 Service Account 是否在目標資源上擁有正確的 Role？
- [ ] **檢查 Access Scopes (僅限 VM)**：
    - 如果是舊版 GCE VM，檢查 "Cloud API access scopes"。即使 IAM 給了權限，如果 Scope 設為 "Default" 且沒有 Storage 權限，依然會失敗。
    - **建議**: VM Scope 設為 `Allow full access to all Cloud APIs`，權限控制全交給 IAM。
- [ ] **檢查 VPC Service Controls**：
    - 如果專案有啟用 VPC-SC，檢查是否因為違反邊界規則而被阻擋（Log 中會有 `vpcServiceControls` 相關錯誤）。

### SOP 3: Quota Exceeded 排查
當部署失敗或擴展失敗時：

- [ ] **確認錯誤訊息**：
    - 訊息通常會包含 `Quota 'CPUS' exceeded` 或 `Limit '...' exceeded`。
- [ ] **檢查 Quota 頁面**：
    - 到 IAM & Admin > Quotas。
    - 篩選 `Service` (如 Compute Engine) 和 `Metric` (如 CPUs)。
- [ ] **解決方案**：
    - 短期：刪除閒置資源。
    - 長期：點擊 "Edit Quotas" 申請提升（需 24-48 小時審核）。

---

## Real-world examples｜實戰案例

### Case 1: GKE Ingress 502 的幽靈 (The GKE Ingress 502 Ghost)

**情境**：
開發團隊部署了一個新的 Microservice 到 GKE，配置了 Ingress。Pod 狀態顯示 `Running`，但在瀏覽器存取時卻間歇性出現 `502 Bad Gateway`，有時又要等 5-10 分鐘才恢復。

**排查過程**：
1.  **Check Logs**: LB Logs 顯示 `statusDetails: "failed_to_connect_to_backend"`。
2.  **Check Pods**: `kubectl get pods` 顯示全綠。
3.  **Check Firewall**: 發現 Terraform 腳本中，雖然建立了 Firewall Rule，但 `target_tags` 與 GKE Node 的 Network Tags 不匹配。
4.  **Root Cause**: GKE 自動建立的 Ingress Controller 會嘗試連線 NodePort。GCP 的 Health Check IP (`35.191.x.x`) 被防火牆擋住，導致 LB 認為所有 Backend 都是不健康的。
5.  **Fix**: 修正 Firewall Rule，允許 Health Check IP 範圍。

### Case 2: 隱藏的 IAM 拒絕 (The Hidden Organization Policy)

**情境**：
DevOps 工程師嘗試為一個新的 Service Account 建立 Key (`gcloud iam service-accounts keys create`)，卻收到 `FAILED_PRECONDITION` 或 `Permission Denied`，即便他擁有 `Service Account Admin` 權限。

**排查過程**：
1.  **Check IAM**: 確認該工程師確實有 `roles/iam.serviceAccountAdmin`。
2.  **Use Troubleshooter**: Policy Troubleshooter 顯示權限 `iam.serviceAccountKeys.create` 是允許的。
3.  **Look Deeper (Org Policy)**: 檢查 Organization Policies。
4.  **Root Cause**: 公司在 Organization 層級啟用了一個限制：`constraints/iam.disableServiceAccountKeyCreation`，禁止在任何專案中下載 Service Account Key JSON 檔（為了資安考量）。
5.  **Fix**: 改用 Workload Identity Federation，避免使用長效 Key。

### Case 3: Cloud Run 冷啟動連線超時 (Cloud Run Cold Start Timeout)

**情境**：
Cloud Run 服務在流量低谷後的第一個請求經常報 `504 Gateway Timeout`。

**排查過程**：
1.  **Check Metrics**: Cloud Run "Container startup latency" 飆高到 10 秒以上。
2.  **Check App Code**: 應用程式在啟動時會同步連線 Cloud SQL 並執行 Migration 檢查。
3.  **Root Cause**: 應用程式啟動邏輯太重，超過了預設的請求等待時間，或者剛好遇到 Cloud SQL 連線建立較慢。
4.  **Fix**:
    - 啟用 **Min Instances** (保持至少 1 個實例熱機)。
    - 優化啟動程式碼，將非必要的初始化（如 Migration）移至 Cloud Build 階段或獨立 Job 執行。