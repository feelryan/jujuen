# 運算服務選型決策矩陣 / Compute Service Decision Matrix

在 GCP 的生態系中，選擇正確的運算服務（Compute Service）是架構設計的第一道關卡。這不僅影響開發速度，更直接決定了未來的維運成本（Ops Cost）與財務成本（Bill）。

本章節將協助你穿越 GCE、GKE、Cloud Run 與 App Engine 的迷霧，做出最適合當下情境的決策。

---

## Mental Model｜心智模型

要理解 GCP 的運算服務，不能只看功能列表，而應建立 **「抽象化程度 vs. 控制權 (Abstraction vs. Control)」** 的光譜模型。

### 1. The "Ops Slider" Spectrum (維運光譜)

想像你有一個滑桿，左邊是 **IaaS (Infrastructure as a Service)**，右邊是 **Serverless**：

*   **極左 (GCE)**：你擁有完整的 OS 控制權，但也必須負責 Patching、Scaling 設定與硬體維護。就像**自建透天厝**，想怎麼改都行，但水電維修自己來。
*   **中間偏左 (GKE)**：你管理的是 Container Orchestration (K8s)，Google 管理底層 VM。就像**大型公寓大廈**，有管委會（K8s Master）幫你處理公共事務，但你仍需管理住戶（Pods）的行為規範。
*   **極右 (Cloud Run / App Engine)**：你只管程式碼與容器，Google 負責剩下的一切。就像**飯店**，入住即用，按日（或按秒）計費，但不能隨意打掉牆壁。

### 2. The "Cattle vs. Pets" Concept (寵物與牲畜)

*   **Pets (GCE)**：每一台 VM 都有名字，生病了（當機）你會去修它。
*   **Cattle (GKE / Cloud Run)**：容器是可替換的，生病了直接殺掉換新的。**現代化架構應盡量往此方向移動。**

---

## Patterns & Best Practices｜常見模式與最佳實務

在實戰中，我們遵循以下決策路徑與最佳實踐：

### 1. "Cloud Run First" Strategy (Cloud Run 優先策略)
對於大多數新的 Web 應用、API 服務或事件驅動處理（Event-driven processing），**預設首選 Cloud Run**。
*   **Why:** 0 維運成本、自動擴展至 0 (Scale to Zero)、按請求計費。
*   **Condition:** 應用程式必須是 **Stateless (無狀態)** 且已容器化。

### 2. GKE for Complex Orchestration (GKE 適用於複雜調度)
當你的系統符合以下特徵時，請選擇 GKE：
*   需要微服務治理（Service Mesh, Istio）。
*   需要混合使用 Stateful (如資料庫) 與 Stateless 服務。
*   需要特殊的硬體控制（如 GPU 切割、TPU）或特定的網路協議（非 HTTP/gRPC）。
*   **Team Maturity:** 團隊中有熟悉 Kubernetes 的工程師。

### 3. GCE for "Lift and Shift" (GCE 適用於搬遷與特殊需求)
*   **Legacy Apps:** 尚未容器化的舊系統，直接搬遷上雲。
*   **Kernel Modification:** 需要修改 OS Kernel 參數或安裝特定驅動程式。
*   **Databases:** 自建高客製化資料庫（雖建議優先用 Cloud SQL/AlloyDB，但有時需自建）。

### 4. App Engine (GAE) - The Niche Choice
*   **現狀：** 隨著 Cloud Run 的成熟，GAE 的適用場景已大幅縮減。
*   **適用：** 快速原型開發（Rapid Prototyping）或極度依賴 GAE 內建功能（如 Search API, Memcache）的舊專案。新專案建議避免使用，以防 Vendor Lock-in。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Resume Driven Development (簡歷驅動開發)
*   **Anti-pattern:** 團隊只有 3 個人，流量很小，卻堅持架設 GKE Standard Cluster，只因為「K8s 很潮」或「想寫在履歷上」。
*   **Consequence:** 80% 的時間花在維護 K8s 版本升級與除錯，而非開發業務功能。
*   **Fix:** 使用 Cloud Run 或 GKE Autopilot。

### 2. Treating Containers like VMs (把容器當 VM 用)
*   **Anti-pattern:** 在 Cloud Run 或 GKE 的容器內執行背景長駐 Process、寫入本地 Log 檔案、或依賴本地 IP。
*   **Consequence:** 擴展時資料遺失、Log 消失、服務不穩定。
*   **Fix:** 確保應用程式符合 **12-Factor App** 原則，Log 輸出至 stdout/stderr，狀態存入 Redis/SQL。

### 3. Ignoring Cold Starts (忽視冷啟動)
*   **Anti-pattern:** 在 Cloud Run 上部署肥大的 Java/Spring Boot 應用，且未設定 `min-instances`。
*   **Consequence:** 第一個使用者的請求延遲高達 10-20 秒。
*   **Fix:** 優化啟動時間、使用 GraalVM、或設定 `min-instances` 保持暖機。

### 4. The "Standard Environment" Trap (標準環境陷阱)
*   **Anti-pattern:** 過度依賴 App Engine Standard 的 proprietary APIs。
*   **Consequence:** 未來想遷移到 GKE 或其他雲端時，需要重寫大量程式碼。
*   **Fix:** 盡量使用標準 Docker 容器與標準 Client Libraries。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree Workflow (決策樹流程)

請依照順序回答以下問題，以決定運算服務：

1.  **Is it containerized? (已容器化？)**
    *   No $\rightarrow$ **Compute Engine (GCE)** (並制定容器化計畫)
    *   Yes $\rightarrow$ 繼續 Q2

2.  **Is it strictly Stateless? (完全無狀態？)**
    *   No (需依賴本地磁碟持久化) $\rightarrow$ **GKE** (StatefulSets) or **GCE**
    *   Yes $\rightarrow$ 繼續 Q3

3.  **Do you need custom OS kernel / specific protocols (non-HTTP/TCP/UDP)?**
    *   Yes $\rightarrow$ **GKE** or **GCE**
    *   No $\rightarrow$ 繼續 Q4

4.  **Do you have a dedicated Ops team / K8s expertise?**
    *   No $\rightarrow$ **Cloud Run** (強烈建議)
    *   Yes $\rightarrow$ 繼續 Q5

5.  **Scale & Complexity Assessment:**
    *   單純 API / Web App / Event Handler $\rightarrow$ **Cloud Run**
    *   龐大的微服務架構 / 複雜的 Service Mesh 需求 $\rightarrow$ **GKE**

### Pre-Launch Checklist (上線前檢查清單)

- [ ] **Cost Estimation:** 是否已使用 GCP Calculator 估算成本？（注意 GKE 的 Cluster Management Fee 與 Cloud Run 的 Request/CPU 費用差異）。
- [ ] **Scaling Limits:** 是否已設定 Max Instances 以防止 DDoS 導致帳單爆炸？（特別是 Cloud Run 與 App Engine）。
- [ ] **Health Checks:** 是否已設定正確的 Liveness 與 Readiness Probes？
- [ ] **IAM Roles:** 運算服務的 Service Account 是否遵循最小權限原則（Least Privilege）？（切勿直接使用 Default Compute Service Account）。
- [ ] **VPC Connectivity:** 是否需要存取 Private IP 的 Cloud SQL 或 Memorystore？（Cloud Run 需設定 Serverless VPC Access Connector 或 Direct VPC Egress）。

---

## Real-world examples｜實戰案例

### Scenario A: The Marketing Campaign Site (行銷活動網站)
*   **情境：** 流量不可預測，可能瞬間爆量，活動結束後歸零。
*   **選擇：** **Cloud Run**。
*   **理由：** 自動快速擴展（Auto-scaling）應對爆量，無人訪問時費用為 0。
*   **架構：** Load Balancer -> Cloud Run -> Firestore。

### Scenario B: Legacy ERP Migration (舊版 ERP 遷移)
*   **情境：** 10 年前的 Windows Server 應用，依賴特定 Registry 設定，無法容器化。
*   **選擇：** **Compute Engine (GCE)**。
*   **理由：** 這是唯一的選擇。
*   **優化：** 使用 Managed Instance Group (MIG) 搭配 Auto-healing 來確保高可用性（HA），即便無法 Auto-scaling。

### Scenario C: Fintech Microservices Platform (金融微服務平台)
*   **情境：** 50+ 個微服務，需要嚴格的網路政策（Network Policies）、mTLS 加密通訊、以及 Canary Deployment 流程。
*   **選擇：** **GKE (Standard or Autopilot)**。
*   **理由：** 需要 Kubernetes 生態系的豐富工具（如 Istio/Anthos Service Mesh）來治理流量與資安。Cloud Run 雖然也能做部分，但在複雜的服務溝通治理上 GKE 仍是王者。

### Scenario D: Data Processing Worker (背景資料處理)
*   **情境：** 每天凌晨 2 點收到 CSV 檔案，需解析並寫入 BigQuery，處理時間約 30 分鐘。
*   **選擇：** **Cloud Run Jobs**。
*   **理由：** 不同於 Cloud Run Services (Web Server)，Cloud Run Jobs 專為「執行完即結束」的任務設計，不會有 HTTP Timeout 的限制（最長可達 24 小時），且比維持一台 GCE VM 更省錢。