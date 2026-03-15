# 1. 前言與學習目標 (Introduction & Learning Objectives)

在雲端架構的設計中，「運算（Compute）」是最核心的支柱。對於資深工程師而言，挑戰不在於如何啟動一個實例（Instance），而在於如何在 EC2（Virtual Machines）、Containers（ECS/EKS）與 Serverless（Lambda）之間做出符合成本效益、效能需求與維運能力的最佳決策。

In cloud architecture design, "Compute" is the central pillar. For a Senior Engineer, the challenge isn't how to launch an instance, but how to make the optimal decision between EC2 (Virtual Machines), Containers (ECS/EKS), and Serverless (Lambda) based on cost-efficiency, performance requirements, and operational capability.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **建立精準的選型框架**：根據工作負載特性（如：長執行時間 vs. 突發流量），在 VM、Container 與 Serverless 間做出權衡。
    **Establish a precise selection framework**: Trade-off between VM, Container, and Serverless based on workload characteristics (e.g., long-running vs. bursty traffic).
2.  **掌握 Serverless 的深層機制**：深入理解 Lambda 的 Cold Start、並發模型（Concurrency Model）與 VPC ENI 的運作原理。
    **Master the deep mechanics of Serverless**: Deeply understand Lambda's Cold Start, Concurrency Model, and how VPC ENIs operate.
3.  **優化成本與效能**：識別「Serverless 比 VM 貴」的臨界點，並懂得利用 Spot Instances 與 Fargate Spot 進行混合架構設計。
    **Optimize cost and performance**: Identify the tipping point where "Serverless becomes more expensive than VM," and know how to utilize Spot Instances and Fargate Spot for hybrid architecture design.
4.  **應對系統設計面試**：在 System Design Interview 中，有條理地解釋為何選擇某種運算服務，並能防禦（Defend）你的設計。
    **Tackle System Design Interviews**: Articulately explain why a specific compute service was chosen and defend your design during System Design Interviews.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 抽象化光譜 (The Spectrum of Abstraction)

我們可以將 AWS 的運算服務視為一個「控制權 vs. 便利性」的光譜。
We can view AWS compute services as a spectrum of "Control vs. Convenience."

1.  **EC2 (Virtual Machines)**
    *   **概念 (Concept)**：你擁有完整的作業系統（OS）控制權。就像「買了一台伺服器並放在雲端」。
    *   **責任 (Responsibility)**：需自行處理 OS Patching、Security Groups、Networking 設定、Scaling scripts (Auto Scaling Groups)。
    *   **適用 (Best for)**：Legacy 應用遷移（Lift & Shift）、需要特殊 Kernel 設定、GPU 高運算、Stateful 應用（如資料庫自建）。
    *   **Analogy**: Owning a car. You change the oil, tires, and drive it yourself.

2.  **Containers (ECS / EKS / Fargate)**
    *   **概念 (Concept)**：將應用程式與依賴打包。ECS/EKS 是調度器（Orchestrator），Fargate 是無伺服器運算引擎（Compute Engine）。
    *   **責任 (Responsibility)**：
        *   **EC2 Mode**: 仍需管理底層 Node 的 OS。
        *   **Fargate Mode**: AWS 管理 OS 與 Patching，你只專注於 Container 定義與網路。
    *   **適用 (Best for)**：Microservices、長時間運行的服務、批次處理（Batch Processing）、跨雲遷移（K8s）。
    *   **Analogy**: Leasing a fleet or using a moving service. You pack the boxes (containers), they handle the transport logistics.

3.  **Serverless (Lambda)**
    *   **概念 (Concept)**：事件驅動（Event-driven）的短暫運算單元。沒有「伺服器」的概念，只有「函數（Function）」。
    *   **責任 (Responsibility)**：只負責 Application Code。AWS 處理 Scaling、Patching、Availability。
    *   **適用 (Best for)**：Event trigger (S3 upload, DB stream)、Glue code、不定時的突發流量、REST API (配合 API Gateway)。
    *   **Analogy**: Uber/Ride-sharing. You just say where to go (code logic), you don't care about the car or maintenance, and you pay per ride (execution).

## 2.2 關鍵差異矩陣 (Key Differences Matrix)

| Feature | EC2 | ECS/EKS (Fargate) | Lambda |
| :--- | :--- | :--- | :--- |
| **Scaling Speed** | Slow (Minutes) | Medium (Seconds to Minutes) | Fast (Milliseconds to Seconds) |
| **Pricing Model** | Per Second/Hour (Instance uptime) | Per vCPU/GB Second | Per Request + GB-Second (Duration) |
| **State** | Stateful / Stateless | Stateless (mostly) | Strictly Stateless |
| **Max Duration** | Unlimited | Unlimited | 15 Minutes (Hard Limit) |
| **Ops Overhead** | High (OS mgmt) | Medium (Cluster/Task def) | Low (Code only) |

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在系統設計面試與實務架構中，選擇運算資源通常取決於 **Latency（延遲）**、**Throughput（吞吐量）** 與 **Cost（成本）** 的權衡。

In system design interviews and practical architecture, choosing compute resources usually depends on the trade-offs between **Latency**, **Throughput**, and **Cost**.

## 3.1 典型架構模式 (Typical Architecture Patterns)

### A. The "Serverless First" Approach (Modern Web Apps)
*   **架構 (Architecture)**: CloudFront -> API Gateway -> Lambda -> DynamoDB/Aurora Serverless.
*   **優勢 (Pros)**: 極低的維運成本，自動擴展至零（Scale to Zero），適合新創或流量波動大的產品。
*   **劣勢 (Cons)**: 高流量下成本可能高於 Container；Cold Start 可能影響 UX。

### B. The "Microservices on Containers" Approach (Enterprise Standard)
*   **架構 (Architecture)**: ALB -> ECS/EKS (Fargate) -> RDS.
*   **優勢 (Pros)**: 穩定的延遲表現，標準化的部署流程（Docker），容易除錯與監控（Sidecar pattern）。
*   **劣勢 (Cons)**: 即使沒有流量也需支付最低運算費用；Cluster 升級與維護（特別是 EKS）有一定門檻。

### C. The "Hybrid / Strangler Fig" Pattern (Migration)
*   **架構 (Architecture)**: ALB 根據 Path Routing，將舊流量導向 EC2 (Monolith)，新功能導向 Lambda 或 Fargate。
*   **意義 (Significance)**: 這是資深工程師在處理 Legacy System 遷移時最常使用的策略，逐步剝離單體應用。

## 3.2 決策樹 (Decision Tree for System Design)

當你在面試中被問到「你會用什麼來跑這段邏輯？」時，可以參考以下思路：
When asked "What would you use to run this logic?" in an interview, consider the following thought process:

1.  **Is it a long-running process (> 15 mins)?**
    *   Yes -> **EC2 or ECS/EKS**. (Lambda will timeout).
2.  **Does it require GPU or specialized Kernel modules?**
    *   Yes -> **EC2** (Most flexible) or **EKS with Managed Node Groups**.
3.  **Is the traffic highly unpredictable and "bursty"?**
    *   Yes -> **Lambda** (Scales faster than Auto Scaling Groups).
4.  **Is steady-state cost a primary concern for high throughput?**
    *   Yes -> **EC2/ECS Reserved Instances or Spot**. (Lambda becomes expensive at high, constant RPS).

---

# 4. 逐步示例 (Walkthrough / Example)

## 案例：圖片處理管線 (Scenario: Image Processing Pipeline)

**背景 (Context)**：使用者上傳高解析度圖片，系統需產生縮圖（Thumbnail）並加上浮水印。
**User uploads high-resolution images; the system needs to generate thumbnails and add watermarks.**

### 階段一：Naive Approach (EC2 Polling)

*   **Design**: 一台 EC2 跑一個 Cron job 或無窮迴圈，不斷檢查 S3 Bucket 是否有新檔案。
*   **Code Logic**:
    ```python
    while True:
        files = s3.list_objects(...)
        for f in files:
            process(f)
        sleep(5)
    ```
*   **Critique**:
    *   **Inefficient**: 沒檔案時也在空轉（付費）。
    *   **Not Scalable**: 突然上傳 1000 張圖，單機處理不過來，需手動開機器。

### 階段二：Event-Driven (S3 -> Lambda)

*   **Design**: 設定 S3 Event Notification 觸發 Lambda。
*   **Flow**: User Upload -> S3 -> Lambda (Trigger) -> Process -> Save to S3.
*   **Pros**:
    *   **Cost**: 沒上傳就不付錢。
    *   **Scale**: 1000 張圖同時上傳，AWS 會啟動 ~1000 個 Lambda 實例並行處理（視 Account Limit 而定）。
*   **Cons (Edge Case)**:
    *   若圖片超大（如 500MB TIFF），處理時間超過 15 分鐘 -> **Lambda Timeout**。
    *   若依賴庫（如 ImageMagick, OpenCV）很大，Lambda Deployment Package 超過 250MB -> **Deployment Fail**。

### 階段三：Mature Solution (Hybrid: S3 -> SQS -> ECS/Lambda)

對於資深工程師，我們會考慮「解耦（Decoupling）」與「控制並發（Concurrency Control）」。
For a Senior Engineer, we consider "Decoupling" and "Concurrency Control".

*   **Design**: User Upload -> S3 -> **SQS** -> Lambda (or ECS Fargate).
*   **Why SQS?**
    *   **Buffering**: 防止下游資料庫或 API 被瞬間流量打掛。
    *   **Batching**: Lambda 可以一次從 SQS 讀取 10 條訊息處理，分攤 Cold Start 成本。
    *   **DLQ (Dead Letter Queue)**: 處理失敗的圖片可以隔離重試，不會丟失。

**程式碼片段 (Lambda Handler with SQS Batch):**

```python
def lambda_handler(event, context):
    # event contains a batch of records from SQS
    for record in event['Records']:
        try:
            # S3 info is inside the SQS message body
            process_image(record['body'])
        except Exception as e:
            # Handle partial failure: 
            # In production, you might return specific IDs to SQS to only retry failed ones
            # (ReportBatchItemFailures)
            print(f"Failed to process {record['messageId']}: {e}")
            
    return {"statusCode": 200}
```

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 Lambda Pinball (Distributed Monolith)
*   **錯誤 (Pitfall)**: Lambda A 呼叫 Lambda B，B 又呼叫 C。
*   **後果 (Consequence)**:
    *   **Cost**: 你在為 A 的等待時間付費（Double Billing）。
    *   **Debugging**: 追蹤 Request ID 變得極其困難（Distributed Tracing Nightmare）。
    *   **Latency**: 延遲疊加。
*   **修正 (Fix)**: 使用 **Step Functions** 來協調工作流程（Orchestration），而不是函數間直接呼叫。

## 5.2 忽略 Cold Start 的影響 (Ignoring Cold Starts)
*   **錯誤 (Pitfall)**: 在需要低延遲的 API 上使用 Java/Spring Boot on Lambda，且未啟用 SnapStart 或 Provisioned Concurrency。
*   **後果 (Consequence)**: 首個請求延遲可能高達 5-10 秒，導致 Client Timeout。
*   **修正 (Fix)**:
    *   選擇輕量 Runtime (Node.js, Python, Go, Rust)。
    *   使用 **Provisioned Concurrency**（預熱）。
    *   對於 Java，啟用 **SnapStart**。

## 5.3 錯誤的 VPC 配置 (VPC Misconfiguration)
*   **錯誤 (Pitfall)**: 將 Lambda 放入 VPC，但不需要存取私有資源（如 RDS）。
*   **後果 (Consequence)**: 雖然 AWS 已優化 Hyperplane ENI，但放入 VPC 仍會增加 ENI 建立的潛在延遲，並消耗 Subnet IP。
*   **修正 (Fix)**: 除非 Lambda 必須存取 VPC 內的資源（RDS, ElastiCache），否則保持 Lambda 在 VPC 之外（可直接存取 DynamoDB, S3 等公有服務）。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

這些問題可用於面試或團隊技術討論，檢驗對 AWS 運算的掌握度。
These questions can be used in interviews or team technical discussions to test mastery of AWS Compute.

## Q1: "How do you choose between ECS Fargate and Lambda for a new microservice?"
*   **高分回答要點 (Key Points)**:
    *   **Traffic Pattern**: 流量平穩且高 -> Fargate (Cost efficient)；流量稀疏或突發 -> Lambda。
    *   **Latency Sensitivity**: 極致低延遲 -> Fargate (Always on)；可容忍 Cold Start -> Lambda。
    *   **Resource Limits**: 記憶體/CPU 需求是否超過 Lambda 上限（10GB RAM / 6 vCPU）。
    *   **Team Skillset**: 團隊是否熟悉 Docker/K8s 生態 vs Serverless 事件驅動開發。

## Q2: "Explain the 'Double Billing' problem in Serverless architectures."
*   **高分回答要點 (Key Points)**:
    *   解釋當 Lambda A 同步呼叫 Lambda B 時，A 在等待 B 回應期間仍處於執行狀態並計費。
    *   提出解決方案：改為非同步呼叫（Asynchronous invocation），或使用 SQS/EventBridge 解耦，或使用 Step Functions。

## Q3: "We have a monolithic application on EC2. How would you migrate it to Serverless without downtime?"
*   **高分回答要點 (Key Points)**:
    *   提到 **Strangler Fig Pattern**。
    *   在 EC2 前面架設 **ALB (Application Load Balancer)** 或 **API Gateway**。
    *   逐個 Endpoint 識別並重寫為 Lambda。
    *   調整 ALB 規則，將特定路徑（如 `/api/v2/users`）導向新的 Lambda Target Group，其餘流量仍走 EC2。
    *   監控、驗證、最後退役舊 EC2。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 本章重點 (Key Takeaways)
1.  **Trade-offs**: EC2 提供控制權，Lambda 提供開發速度，Containers (Fargate) 位於中間平衡點。
2.  **Cost Model**: Lambda 適合低使用率或突發流量；EC2/Fargate 適合高且穩定的負載。
3.  **Limits**: 牢記 Lambda 的 15 分鐘限制與 Cold Start 特性。
4.  **Architecture**: 善用 SQS/EventBridge 進行解耦，避免 Lambda 直接同步呼叫 Lambda。
5.  **Security**: 最小權限原則（IAM Roles）在所有運算服務中都是首要考量。

## 下一步 (Next Steps)
*   **延伸閱讀**: 深入研究 AWS **Firecracker**（MicroVM 技術），了解 Lambda 與 Fargate 底層是如何實現隔離的。
*   **實作練習**: 建立一個 Step Functions Workflow，協調多個 Lambda 函數與 DynamoDB 的互動。
*   **下一章預告**: 既然搞定了運算，接下來我們需要儲存資料。下一章將探討 **AWS Storage Strategy: S3, EBS, and EFS**。