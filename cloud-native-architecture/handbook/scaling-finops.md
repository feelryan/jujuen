# 擴展策略與成本優化 (FinOps) / Scaling Strategies & FinOps

## Mental model｜心智模型

### 1. 資源的「呼吸」而非「囤積」 (Breathing vs. Hoarding)
傳統地端思維傾向於「以最大預估負載進行配置 (Provision for Peak)」，這在雲端是巨大的浪費。雲原生的核心心智模型是**動態調整 (Elasticity)**。想像你的基礎設施像是一個有機體，它應該隨著業務流量「呼吸」——在白天流量高峰時吸氣（擴展），在深夜低谷時呼氣（縮減）。

### 2. FinOps 的核心：單位經濟效益 (Unit Economics)
FinOps 不是單純的「省錢 (Cost Cutting)」，而是「賺錢 (Making Money)」。
- **錯誤思維**：「這個月雲端帳單太貴了，我們要砍機器。」
- **正確思維**：「我們每服務 1,000 個用戶的成本從 $0.5 降到了 $0.3，雖然總帳單增加，但利潤率提升了。」
你的目標是優化 **Cost per Transaction** 或 **Cost per Active User**。

### 3. 擴展的三維度 (The Three Dimensions of Scaling)
不要只想到加機器，要理解擴展的三個層次：
1.  **HPA (Horizontal Pod Autoscaler)**：增加 Pod 數量（人海戰術）。適用於無狀態 (Stateless) 服務。
2.  **VPA (Vertical Pod Autoscaler)**：增加單一 Pod 的 CPU/RAM（超人戰術）。適用於難以水平擴展的有狀態服務或單體應用。
3.  **CA (Cluster Autoscaler) / Karpenter**：增加 Node 數量（擴建辦公室）。當 Pod 塞不進現有節點時觸發。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 黃金標準：Requests 與 Limits 的設定 (The Golden Standard for Requests & Limits)
這是 Kubernetes 排程與成本控制的基石，必須精確設定。

- **Requests (保證值)**：
  - **定義**：K8s 排程器用來決定將 Pod 放在哪個 Node 的依據。
  - **最佳實務**：設定為應用程式在**正常負載下**的實際使用量（例如 P90 或 P95 數值）。
  - **FinOps 觀點**：如果 Requests 設得太高但沒用滿，這就是「Slack Cost」（閒置浪費），因為 K8s 已經為你預留了這些資源，無法給別人用。

- **Limits (上限值)**：
  - **定義**：容器能使用的硬上限。
  - **最佳實務**：
    - **CPU**：可以不設（讓它盡量用）或設得比 Requests 高出許多。注意：CPU 達到 Limit 會導致 Throttling（變慢），不會死掉。
    - **Memory**：**必須設定**。通常設為 Requests 的 1.2 ~ 1.5 倍作為緩衝。注意：Memory 達到 Limit 會導致 **OOM Kill**（直接重啟）。

### 2. 基於自定義指標的 HPA (HPA on Custom Metrics)
不要只依賴 CPU/Memory 進行擴展。
- **CPU 擴展的延遲**：當 CPU 飆高時，通常流量已經進來了，這時再擴展往往來不及（Cold Start 問題）。
- **模式**：使用 **KEDA (Kubernetes Event-driven Autoscaling)** 或 Prometheus Adapter。
  - **Web Service**：依據 `http_requests_per_second` 或 `active_connections`。
  - **Worker**：依據 `queue_depth` (佇列深度) 或 `queue_lag`。

### 3. 善用 Spot Instances (Spot Instances Strategy)
Spot Instances (競價實例) 通常比 On-Demand 便宜 60-90%，但隨時可能被收回。
- **適用場景**：Stateless API、Batch Jobs、CI/CD Agents。
- **混合部署模式 (Mixed Instance Policy)**：
  - 使用 Cluster Autoscaler 或 Karpenter 設定 Node Pool。
  - **Base Capacity**：前 N 個節點使用 On-Demand (確保最低服務水準)。
  - **Burst Capacity**：超過 N 的擴展部分使用 Spot Instances。
- **優雅退場 (Graceful Shutdown)**：應用程式必須能處理 `SIGTERM` 信號，在 30 秒-2 分鐘內完成當前請求並斷開連線，因為 Spot 回收通知很短。

### 4. 標籤策略 (Tagging Strategy)
無法測量就無法優化。
- **強制標籤**：所有資源（Pod, Node, LoadBalancer, Volume）都必須打上 `Team`, `Environment`, `Service`, `CostCenter` 標籤。
- **工具配合**：使用 Kubecost 或雲端原生的 Cost Explorer，依據標籤拆分帳單，將成本責任「左移 (Shift Left)」給開發團隊。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. HPA 與 VPA 的衝突 (HPA & VPA Conflict)
- **陷阱**：同時在**相同指標**（如 CPU）上啟用 HPA 和 VPA。
- **後果**：HPA 偵測到高負載試圖增加 Pod 數量，而 VPA 偵測到高負載試圖增加 Pod 規格。兩者互相干擾，導致擴展行為不可預測（Thrashing）。
- **解法**：通常對 Stateless 服務只用 HPA。如果必須混用，VPA 應設為 `Off` 或 `Initial` 模式（僅提供建議或僅在啟動時調整），或者 HPA 使用 Custom Metrics 而 VPA 使用 CPU/Mem。

### 2. 忽略 Pod Disruption Budgets (PDB)
- **陷阱**：為了省錢大量使用 Spot Instances，但沒有設定 PDB。
- **後果**：當雲端廠商回收 Spot 節點，或者 Cluster Autoscaler 試圖縮減節點（Bin packing）時，K8s 可能一次殺死所有 Pod，導致服務中斷。
- **解法**：設定 PDB `minAvailable: 1` 或 `maxUnavailable: 20%`，確保即使在節點回收時，服務仍有最低可用性。

### 3. 盲目的 Requests = Limits
- **陷阱**：為了追求極致穩定（Guaranteed QoS），將所有服務的 Requests 設為等於 Limits，且數值設得很高。
- **後果**：極低的資源利用率（通常 < 10%）。雖然服務很穩，但公司在為大量閒置的空氣付費。
- **例外**：核心資料庫或極度延遲敏感的應用（如高頻交易）才需要這樣做。

### 4. 忽略跨可用區流量費用 (Ignoring Cross-AZ Traffic Cost)
- **陷阱**：Pod 在 AZ-a，資料庫在 AZ-b，頻繁跨區讀寫。
- **後果**：雲端帳單中出現鉅額的 "Data Transfer" 費用。
- **解法**：利用 K8s 的 `Topology Spread Constraints` 或 `Service Topology`，盡量讓流量在同一個 AZ 內處理。

---

## Checklists & workflows｜檢查清單與流程

### Day-to-Day Deployment Checklist
在部署新服務或更新配置時使用：

- [ ] **Resource Requests 設定**：是否已根據壓測或歷史監控數據設定合理的 CPU/Memory Requests？
- [ ] **Resource Limits 設定**：Memory Limit 是否存在且大於 Requests（防止 OOM）？
- [ ] **Liveness/Readiness Probes**：是否已設定？（這影響擴展時新 Pod 何時能接流量）。
- [ ] **HPA 設定**：
    - [ ] 是否設定了 `minReplicas`（至少 2 以確保 HA）？
    - [ ] 是否設定了 `maxReplicas`（防止無限擴展導致帳單爆炸）？
    - [ ] 擴展指標是否合理（CPU vs Custom Metric）？
- [ ] **PDB (Pod Disruption Budget)**：是否已設定以保護服務在節點縮減時的可用性？
- [ ] **Graceful Shutdown**：程式碼是否能正確處理 `SIGTERM`？（對 Spot Instance 至關重要）。

### Monthly FinOps Review Workflow
每月一次的成本優化流程：

1.  **識別浪費 (Identify Waste)**：
    - 使用 Kubecost 或 Cloud Advisor 找出 "Idle" 資源。
    - 找出 Requests 與實際 Usage 差距過大的服務。
2.  **調整規格 (Right-Sizing)**：
    - 對於長期利用率低的服務，降低 Requests。
    - 對於經常 OOM 的服務，調高 Memory Limits。
    - 使用 **VPA "Off" mode** (Recommendation mode) 獲取 K8s 的官方建議值。
3.  **檢視 Spot 覆蓋率**：
    - Non-production 環境是否 100% 使用 Spot Instances？
    - Production 的 Stateless 服務是否能提高 Spot 比例？
4.  **清理殭屍資源**：
    - 刪除未掛載的 PVC (EBS/Disk)。
    - 刪除未使用的 Load Balancer 和 Public IP。

---

## Real-world examples｜實戰案例

### 案例一：非同步佇列處理器 (Async Queue Worker)
**情境**：一個處理影片轉檔的 Worker，消耗 CPU 且處理時間長。
**錯誤做法**：使用 CPU % 進行 HPA。
**問題**：當 CPU 飆高時，Worker 已經在忙碌中。如果佇列突然進來 1000 個任務，CPU 始終維持 100%，HPA 反應遲鈍，且可能在任務處理一半時縮容。

**最佳實踐配置**：
1.  **Metric**：使用 KEDA 監控 AWS SQS 或 Kafka 的 `QueueDepth`。
2.  **Logic**：`Target = 5 messages per pod`。如果佇列有 50 個訊息，就擴展到 10 個 Pod。
3.  **Scale Down**：設定 `stabilizationWindowSeconds: 300` (5分鐘)，避免任務還沒跑完就被縮容殺掉。
4.  **Node**：使用 Karpenter 配合 Spot Instances，因為轉檔是批次作業，成本敏感度高於延遲敏感度。

### 案例二：Java 應用程式的記憶體陷阱
**情境**：Java Spring Boot 應用，啟動時需要大量記憶體，運行時較少。
**挑戰**：如果按啟動需求設 Requests，運行時會浪費；如果按運行時設，啟動會 OOM 或超慢。

**解決方案**：
1.  **JVM 設定**：明確設定 `-Xms` (Initial Heap) 和 `-Xmx` (Max Heap)。讓 `-Xmx` 約為 Container Memory Limit 的 75-80%（預留給 Non-Heap memory）。
2.  **Burstable QoS**：
    - `Requests.memory`: 512Mi (運行時需求)
    - `Limits.memory`: 1Gi (啟動時緩衝)
    - *注意*：這屬於 Burstable QoS 類別，當節點記憶體緊繃時，這類 Pod 比 Guaranteed Pod 更容易被驅逐，需權衡風險。

### 案例三：Karpenter 的極速擴展
**情境**：電商閃購活動，流量在 1 分鐘內暴增 10 倍。
**傳統 CA 問題**：Cluster Autoscaler 需要先看到 Pod Pending，然後呼叫 Cloud API 開機器，等待機器 Boot up 加入 Cluster，耗時 3-5 分鐘。
**Karpenter 優化**：
- Karpenter 直接監聽 Pod 需求，繞過 Auto Scaling Groups (ASG)，直接呼叫 EC2 `CreateFleet` API。
- 使用 **Over-provisioning Pods** 模式：
  - 部署一個低優先級 (PriorityClass) 的 "Pause Pod" 佔用空間（例如佔用 10 個節點的資源）。
  - 當閃購流量進來，真實 App Pod (高優先級) 會搶佔資源，瞬間擠掉 Pause Pod。
  - Pause Pod 進入 Pending 狀態，觸發 Karpenter 擴展新節點（在背景慢慢擴），而真實 App 已經有現成資源可用。