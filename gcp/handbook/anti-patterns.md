# 常見反模式與設計陷阱 / Common Anti-Patterns & Pitfalls

## Mental model｜心智模型

在 GCP (Google Cloud Platform) 的世界裡，最大的誤解往往來自於**「預設值」 (Defaults)** 與**「生產就緒」 (Production Ready)** 之間的巨大鴻溝。

GCP 的許多預設設定（如 Default VPC、Default Service Account）是為了讓開發者在 5 分鐘內完成 Hello World 而設計的，**絕非**為了長期維運的安全與穩定。

建立正確的心智模型，請記住以下原則：

1.  **Defaults are for Demos, Custom is for Production**：
    預設網路與權限通常過於寬鬆。在生產環境中，應採取「拒絕所有，僅開放必要」的白名單策略。
2.  **Assume Zonal Failure**：
    GCP 的 Zone（可用區）會壞。這不是「如果」的問題，是「何時」的問題。如果你的架構無法承受單一 Zone 離線，你的系統就不是高可用的。
3.  **Identity is the New Perimeter**：
    傳統防火牆不再足夠。IAM（身分識別與存取管理）是雲端安全的第一道防線，任何「方便」的權限賦予（如 Owner）都是潛在的後門。

---

## Patterns & best practices｜常見模式與最佳實務

在討論反模式之前，我們先確立什麼是「正確的姿勢」：

*   **Custom VPC Mode**：
    總是建立自定義 VPC，並明確規劃 Subnet 的 CIDR block。使用 **Private Google Access** 讓內部 VM 不需 Public IP 也能存取 Google API（如 Cloud Storage, BigQuery）。
*   **Regional Resources & HA**：
    資料庫使用 **Cloud SQL High Availability (HA)**，運算資源使用 **Managed Instance Groups (MIGs)** 並跨多個 Zones 分佈。
*   **Least Privilege (PoLP)**：
    使用 **Predefined Roles**（如 `roles/storage.objectViewer`）甚至 **Custom Roles**，而非 Primitive Roles（Owner, Editor, Viewer）。
*   **Workload Identity**：
    讓應用程式透過 GKE 或 Compute Engine 的 Service Account 自動驗證，**嚴格禁止**下載 Service Account Key (`.json`) 到本地或存入 Git。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

以下是 GCP 專案中最危險且常見的「坑」，請務必避開：

### 1. The "Default VPC" Trap｜過度依賴預設網路
*   **The Anti-Pattern**: 直接使用專案建立時自動生成的 `default` VPC。
*   **Why it's dangerous**:
    *   **Auto-mode Subnets**: 它會在全球每個 Region 自動建立 Subnet，浪費 IP 空間且難以管理防火牆邊界。
    *   **Permissive Firewalls**: 預設防火牆規則通常允許 `0.0.0.0/0` 的 SSH (22) 與 RDP (3389) 流量，這是駭客掃描的首要目標。
*   **The Fix**: 專案建立後，第一件事就是**刪除 default VPC**，或是建立一個新的 Custom VPC 並明確定義 Subnet。

### 2. Ignoring Zonal Failure｜忽視單一可用區故障
*   **The Anti-Pattern**: 部署單一台 VM，或將 GKE Cluster 設為 Zonal Cluster，並認為 Google 不會當機。
*   **Why it's dangerous**:
    *   GCP 的 SLA 通常是針對 **Multi-zone** 架構。單一 Zone 的維護或故障會導致服務完全中斷。
    *   許多開發者將 App Server 與 DB 都放在同一個 Zone (e.g., `asia-east1-a`)，一旦該 Zone 電力或網路異常，全線崩潰。
*   **The Fix**:
    *   Compute Engine: 使用 **Regional Managed Instance Groups (MIG)**。
    *   Cloud SQL: 啟用 **High Availability (HA)**（這會自動在另一個 Zone 建立 Standby）。
    *   GKE: 生產環境請使用 **Regional Cluster**。

### 3. Abusing Primitive Roles (Owner/Editor)｜濫用 Owner/Editor 權限
*   **The Anti-Pattern**: 為了方便，給開發者或 Service Account 賦予 `Project Owner` 或 `Project Editor` 角色。
*   **Why it's dangerous**:
    *   `Editor` 權限幾乎可以做任何事，包括刪除生產環境資料庫、修改防火牆規則。
    *   這違反了「最小權限原則」，且在資安稽核時是大忌。
*   **The Fix**:
    *   使用具體的 **Predefined Roles** (e.g., `roles/compute.networkAdmin`, `roles/cloudsql.client`)。
    *   善用 **IAM Recommender** 來移除過度寬鬆的權限。

### 4. Service Account Key Leakage｜服務帳號金鑰外洩
*   **The Anti-Pattern**: 為了讓外部程式或本地開發環境存取 GCP，下載 Service Account 的 JSON Key，並將其 commit 到 GitHub。
*   **Why it's dangerous**:
    *   這是 GCP 帳號被盜用（通常被拿來挖礦）的 **#1 原因**。GitHub 上有機器人 24 小時掃描這些 Key。
    *   Key 沒有過期時間，一旦外洩，除非手動撤銷，否則永久有效。
*   **The Fix**:
    *   **本地開發**: 使用 `gcloud auth application-default login`。
    *   **CI/CD (GitHub Actions/GitLab)**: 使用 **Workload Identity Federation**，完全不需要實體 Key 檔案。

### 5. Public Storage Buckets｜意外公開的儲存桶
*   **The Anti-Pattern**: 為了方便分享檔案，將 Cloud Storage Bucket 的權限設為 `allUsers` 擁有 `Storage Object Viewer`。
*   **Why it's dangerous**:
    *   這會讓全世界任何人都能讀取你的資料。許多企業資料外洩源於此。
*   **The Fix**:
    *   在 Organization Policy 層級強制執行 **"Domain Restricted Sharing"**。
    *   啟用 Bucket 的 **"Public Access Prevention"** 設定。

---

## Checklists & workflows｜檢查清單與流程

在將服務推向生產環境前，請執行此「反模式排除」檢查清單：

### Network & Security Check
- [ ] **No Default VPC**: 確認已停用或刪除 Default VPC，使用 Custom VPC。
- [ ] **Private Only**: 資料庫 (Cloud SQL/Memorystore) 僅使用 Private IP，不指派 Public IP。
- [ ] **Firewall Review**: 確認沒有 `0.0.0.0/0` 的 Ingress 規則（Load Balancer 除外）。SSH 應透過 **IAP (Identity-Aware Proxy)** 進行。
- [ ] **Public Access Prevention**: 所有存放敏感資料的 GCS Buckets 已開啟此選項。

### IAM & Identity Check
- [ ] **No Primitive Roles**: 確認 IAM 列表中沒有 User 或 Service Account 使用 `Owner`, `Editor`, `Viewer`。
- [ ] **No User-Managed Keys**: 檢查 Service Account 是否有下載的 Keys。若有，是否有輪替計畫？能否改用 Workload Identity？
- [ ] **Least Privilege**: 應用程式的 Service Account 是否僅擁有該 App 運作所需的最小權限？

### Reliability Check
- [ ] **Multi-Zone Deployment**: 運算資源是否跨至少 2 個 Zones？
- [ ] **HA Database**: Cloud SQL 是否已開啟 HA 模式？
- [ ] **Backup Strategy**: 是否設定了自動備份？是否驗證過還原流程？

---

## Real-world examples｜實戰案例

### Case 1: The "Crypto-Mining" Surprise (IAM Anti-Pattern)
**情境**：某新創團隊為了讓 Jenkins 能夠部署 App Engine，建立了一個 Service Account 並賦予 `Project Editor` 權限。工程師將 JSON Key 檔案放在專案根目錄，並不小心推送到 public GitHub repo。
**後果**：
1.  駭客機器人在 3 分鐘內偵測到 Key。
2.  利用 `Editor` 權限，駭客在該專案的所有 Region 啟動了最高規格的 GPU VM 進行挖礦。
3.  團隊隔天收到 Google Billing Alert，帳單已達 $15,000 USD。
**修正**：
*   撤銷 Key。
*   改用 **Workload Identity Federation** 連接 GitHub Actions 與 GCP，完全不使用長效型 JSON Key。
*   設定 **Budgets & Alerts**，在費用異常時立即通知。

### Case 2: The "Zonal Outage" Panic (Architecture Anti-Pattern)
**情境**：一個電商網站在 `asia-east1-a` 部署了一台高規格 VM 運行 Web Server，並連線到同一 Zone 的 Cloud SQL。
**事件**：`asia-east1-a` 發生冷卻系統異常，導致部分機櫃斷電。
**後果**：
*   網站完全無法存取。
*   因為沒有 HA，資料庫無法 Failover。
*   團隊試圖在 `asia-east1-b` 重開 VM，但因為該 Region 資源吃緊（大家都在搶修），導致 `Insufficient Resources` 錯誤，無法開機。
**修正**：
*   使用 **Regional Managed Instance Group**，設定最少 2 個實例分佈在不同 Zone。
*   Cloud SQL 啟用 **HA**，當 Primary Zone 故障時，自動切換到 Standby Zone。
*   前端掛載 **Global Load Balancer**，自動將流量導向健康的實例。