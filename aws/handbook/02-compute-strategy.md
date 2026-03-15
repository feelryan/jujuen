# 運算資源決策：VM、容器與 Serverless / Compute Strategy: EC2, Containers, and Serverless

## Mental model｜心智模型

在 AWS 選擇運算服務時，不要只看技術熱詞（Buzzwords），而應將其視為一個 **「控制權與維運責任的滑動條 (The Control vs. Responsibility Slider)」**。

你的決策本質上是在回答這個問題：**「我願意為了省去多少維運麻煩，而犧牲多少底層控制權？」**

### The Abstraction Spectrum (抽象化光譜)

1.  **EC2 (Virtual Machines)**: **Own the Car (買車自駕)**
    *   **Mental Model**: 你擁有整台機器的 OS root 權限。
    *   **Trade-off**: 極高的控制權（Kernel tuning, GPU drivers, networking），但你需要負責 Patching, Security updates, Scaling logic。
    *   **Sweet Spot**: Legacy Monoliths, 特殊 Kernel 需求, 高效能運算 (HPC), 資料庫自管。

2.  **Containers (ECS/EKS on Fargate)**: **Lease a Car (長期租賃)**
    *   **Mental Model**: 你只關心應用程式的打包 (Docker Image) 與資源定義 (CPU/RAM)，不關心底層 OS。
    *   **Trade-off**: 無法修改 Host OS，但省去了 Patching 節點的痛苦。
    *   **Sweet Spot**: Microservices, Long-running processes, 跨語言的服務堆疊。

3.  **Serverless (Lambda)**: **Uber/Taxi (叫車服務)**
    *   **Mental Model**: 你只關心「一段程式碼 (Function)」與「觸發事件 (Event)」。沒有 "Server" 的概念存在於你的視野中。
    *   **Trade-off**: 受到 Runtime 限制 (Timeouts, Memory limits)，存在 Cold Start，但完全沒有閒置成本 (Pay-per-use) 且自動擴展。
    *   **Sweet Spot**: Event-driven tasks, Glue logic, 不可預測的突發流量 (Bursty traffic), Cron jobs。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. The "Right-Sizing" Strategy (適材適用策略)
不要試圖用一種運算模式解決所有問題。混合架構 (Hybrid Compute) 往往是最佳解。
*   **Core API / Long-running Services**: 使用 **ECS Fargate**。它提供了穩定的延遲表現，且比 Lambda 在高負載下更具成本效益。
*   **Async Processing / Webhooks**: 使用 **Lambda**。例如 S3 上傳後的圖片處理、DynamoDB Stream 的觸發、第三方 Webhook 接收。
*   **Stateful / Legacy**: 使用 **EC2**。例如需要掛載 EBS 且極度依賴本地文件系統狀態的舊系統。

### 2. Compute Savings Patterns (成本優化模式)
*   **Graviton (ARM64) First**: 無論是 EC2, Fargate 或 Lambda，優先選擇 ARM64 架構（Graviton 處理器）。通常能獲得 **20% 的效能提升與 20% 的成本降低**。
*   **Spot Instances for Stateless**: 對於容錯率高的工作（如 Batch processing, CI/CD Agents），在 EC2/ECS 中使用 Spot Instances 可節省高達 **70-90%** 成本。
*   **Compute Savings Plans**: 一旦確定了基底流量（Baseline usage），務必購買 Compute Savings Plans（比 Reserved Instances 更靈活，涵蓋 EC2, Fargate, Lambda）。

### 3. Handling Lambda Cold Starts (應對冷啟動)
*   **Provisioned Concurrency**: 對於延遲敏感 (Latency-sensitive) 的核心路徑，付費開啟預配置並發，消除冷啟動。
*   **Language Selection**: 避免在 Lambda 上使用 Spring Boot (Java) 或大型 .NET Framework，除非配合 SnapStart。優先選擇 Node.js, Python, Go 或 Rust。

### 4. Container Orchestration Choice (容器調度選擇)
*   **ECS**: 適合 80% 的團隊。整合度高，學習曲線低，與 AWS 服務（ALB, IAM, CloudWatch）無縫接軌。
*   **EKS**: 僅當你需要 Kubernetes 特有的生態系（Helm charts, Istio, Specific Operators）或多雲策略時才選用。**不要為了簡歷好看而選 EKS，維運成本極高。**

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Lambda Pinball" (Lambda 彈珠台)
*   **Bad Practice**: Function A 呼叫 Function B，B 又呼叫 C (Synchronous/Chained invocation)。
*   **Consequence**: 延遲疊加 (Latency adds up)，且成本倍增（A 在等待 B 時，你同時在為 A 和 B 付費）。
*   **Solution**: 使用 **Step Functions** 進行編排，或改用 SQS/SNS/EventBridge 進行非同步解耦。

### 2. Lift-and-Shift Monolith to Lambda (單體應用硬搬 Lambda)
*   **Bad Practice**: 將整個龐大的 Web Framework (e.g., Django, Rails, Spring) 包進一個 Lambda Function (所謂的 "Lambdalith")。
*   **Consequence**: 巨大的 Package size 導致極慢的 Cold Start，且難以利用 Lambda 的並發優勢。
*   **Solution**: 如果必須跑單體應用，請用 **App Runner** 或 **Fargate**。

### 3. Ignoring Data Transfer Costs (忽視資料傳輸成本)
*   **Bad Practice**: 跨 Availability Zone (AZ) 的頻繁通訊。例如 EC2 (AZ-a) 頻繁呼叫 RDS (AZ-b)。
*   **Consequence**: 運算費用看似便宜，但 "Data Transfer" 帳單驚人。
*   **Solution**: 盡量保持流量在同一 AZ 內，或使用 VPC Endpoints (Interface Endpoints) 避免流量繞行公網。

### 4. Over-scaling DB Connections (資料庫連線耗盡)
*   **Bad Practice**: Lambda 直接連線關聯式資料庫 (RDS/PostgreSQL)，且流量瞬間飆高。
*   **Consequence**: Lambda 瞬間擴展出 1000 個實例，耗盡資料庫連線數 (Connection exhaustion)，導致服務崩潰。
*   **Solution**: 使用 **RDS Proxy** 或改用 DynamoDB (HTTP-based connection)。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Compute Selection (選型決策樹)

在開始新專案或功能時，請依序回答以下問題：

1.  **是否有硬體依賴 (GPU/Kernel) 或需安裝商業軟體授權？**
    *   [Yes] -> **EC2**
    *   [No] -> 繼續
2.  **應用程式是否需要長時間運行 (Long-running) 或需維持 WebSocket 連線？**
    *   [Yes] -> **ECS / EKS (Fargate)**
    *   [No] -> 繼續
3.  **流量是否高度不可預測 (Spiky) 或甚至會降為零？**
    *   [Yes] -> **Lambda**
    *   [No] -> 繼續
4.  **團隊是否具備 Kubernetes 維運能力且必須使用 K8s 生態？**
    *   [Yes] -> **EKS**
    *   [No] -> **ECS Fargate** (Default Choice)

### Pre-Flight Checklist (上線前檢查清單)

- [ ] **IAM Roles**: 是否遵循 Least Privilege？（例如：Lambda 不應擁有 `S3:*` 權限）。
- [ ] **VPC Settings**: 運算資源是否置於 Private Subnet？（除了 Load Balancer 或 NAT Gateway，不應有 Public IP）。
- [ ] **Logging**: 是否已設定 Log Retention Policy？（CloudWatch Logs 預設是 "Never Expire"，這是隱形成本殺手）。
- [ ] **Secrets Management**: 敏感資訊（DB 密碼、API Key）是否已移出環境變數，改用 Secrets Manager 或 Parameter Store？
- [ ] **Cost Tags**: 是否已標記 `CostCenter`, `Environment`, `Service` 標籤以便 FinOps 追蹤？

---

## Real-world examples｜實戰案例

### Scenario 1: The High-Traffic E-commerce Flash Sale (高併發搶購)
*   **Challenge**: 行銷活動導致流量在 1 分鐘內暴增 100 倍。
*   **Architecture**:
    *   **Frontend**: CloudFront + S3 (Static assets).
    *   **Ingestion**: API Gateway -> **Lambda** (處理瞬間請求，寫入 SQS)。Lambda 的快速擴展能力在此優於 Container（Container 擴展需要拉 Image、啟動時間）。
    *   **Processing**: **ECS Fargate** (Consumers) 從 SQS 讀取訂單並寫入資料庫。這裡使用 Fargate 是為了控制寫入資料庫的速率 (Throttling)，保護 DB 不被壓垮。

### Scenario 2: Enterprise Internal Tool (企業內部工具)
*   **Challenge**: 低流量，但需要高安全性，且預算有限。
*   **Architecture**:
    *   **Compute**: **Lambda**。因為內部工具晚上和週末沒人使用，Lambda 閒置時成本為 0。
    *   **Security**: Lambda 部署在 VPC 內，透過 VPC Endpoint 存取內部資源，完全不暴露在公網。
    *   **Database**: DynamoDB On-Demand mode (同樣是 Pay-per-request)。
    *   **Result**: 每月基礎設施成本趨近於 $0 (Free Tier 覆蓋大部分)。

### Scenario 3: Legacy Java App Migration (舊系統遷移)
*   **Challenge**: 一個 10 年歷史的 Java Spring Monolith，原本跑在地端 VM。
*   **Phase 1 (Rehost)**: 遷移至 **EC2** (Auto Scaling Group)。確保在雲端能跑，設定 ALB 與 RDS。
*   **Phase 2 (Replatform)**: 容器化 (Dockerize)，遷移至 **ECS Fargate**。省去 OS 維護，整合 CloudWatch Logs。
*   **Phase 3 (Refactor)**: 識別出最吃資源的「圖片縮圖功能」，將其剝離重寫為 **Lambda**，由 S3 Event 觸發。主程式瘦身。