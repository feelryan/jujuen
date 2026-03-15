# Chapter 06: 系統設計中的資安模式
# Chapter 06: Security Patterns in System Design

## 1. 前言與學習目標
## 1. Introduction & Learning Objectives

在系統設計面試（System Design Interview）與高階架構規劃中，安全性往往被視為一個「非功能性需求（Non-functional Requirement）」，但在 Big Tech 的標準中，它是核心架構的一部分。本章不討論基礎的 OWASP Top 10 漏洞修補，而是聚焦於如何設計**可重複使用的資安基礎設施模式**。
In System Design Interviews and high-level architectural planning, security is often treated as a "Non-functional Requirement." However, by Big Tech standards, it is a core part of the architecture. This chapter moves beyond basic OWASP Top 10 patching and focuses on how to design **reusable security infrastructure patterns**.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **設計機密管理系統（Secure Vault）**：理解並應用信封加密（Envelope Encryption）與動態憑證（Dynamic Secrets）的概念。
    **Design a Secret Management System (Secure Vault):** Understand and apply concepts like Envelope Encryption and Dynamic Secrets.
2.  **建構不可竄改的稽核日誌（Audit Logging）**：設計高吞吐量且符合合規要求（Compliance-ready）的異步日誌系統。
    **Build Immutable Audit Logging:** Design high-throughput, compliance-ready, asynchronous logging systems.
3.  **實作分散式限流（Distributed Rate Limiting）**：在高併發環境下，區分 Throttling 與 Rate Limiting，並解決分散式計數器的 Race Condition 問題。
    **Implement Distributed Rate Limiting:** Distinguish between Throttling and Rate Limiting in high-concurrency environments and solve race conditions in distributed counters.

---

## 2. 核心觀念與心智模型
## 2. Core Concepts & Mental Model

### 2.1 信封加密（Envelope Encryption）
### 2.1 Envelope Encryption

在設計像 HashiCorp Vault 或 AWS KMS 這樣的系統時，核心模型是「信封加密」。我們不直接使用主金鑰（Master Key / KEK - Key Encryption Key）加密大量資料，而是生成一個資料金鑰（DEK - Data Encryption Key）來加密資料，再用 KEK 加密 DEK。
When designing systems like HashiCorp Vault or AWS KMS, the core mental model is "Envelope Encryption." We do not use the Master Key (KEK - Key Encryption Key) to encrypt bulk data directly. Instead, we generate a Data Encryption Key (DEK) to encrypt the data, and then encrypt the DEK using the KEK.

*   **直覺類比**：你有一把萬能鑰匙（KEK），但你不會把它交給警衛去鎖每一個保險箱。相反，你為每個保險箱打造一把專用鑰匙（DEK），鎖上保險箱後，再用萬能鑰匙把這把專用鑰匙鎖在一個小盒子裡。
    **Intuitive Analogy:** You have a Master Key (KEK), but you don't give it to the guard to lock every safe. Instead, you forge a specific key (DEK) for each safe. After locking the safe, you use the Master Key to lock that specific key inside a small box.

### 2.2 漏桶與權杖桶（Leaky Bucket vs. Token Bucket）
### 2.2 Leaky Bucket vs. Token Bucket

在設計 Rate Limiter 時，必須選擇演算法模型。
When designing a Rate Limiter, you must choose an algorithmic model.

*   **Token Bucket（權杖桶）**：允許突發流量（Bursty Traffic）。只要桶裡有權杖，請求就能通過。適合一般 API 限流。
    **Token Bucket:** Allows for bursty traffic. As long as there are tokens in the bucket, requests can pass. Suitable for general API rate limiting.
*   **Leaky Bucket（漏桶）**：強制平滑輸出（Smoothed Outflow）。無論進來的流量多快，水龍頭流出的速度是固定的。適合保護對寫入速度敏感的資料庫或下游服務。
    **Leaky Bucket:** Enforces smoothed outflow. No matter how fast the incoming traffic is, the outflow rate is fixed. Suitable for protecting write-sensitive databases or downstream services.

### 2.3 寫入後不可變（WORM - Write Once, Read Many）
### 2.3 WORM (Write Once, Read Many)

對於 Audit Logging，核心模型是「不可變性（Immutability）」。一旦日誌被寫入，就不應被修改或刪除，直到保留期限結束。這通常透過 Append-only 的儲存結構或區塊鏈式的雜湊鏈（Hash Chain）來實現。
For Audit Logging, the core model is "Immutability." Once a log is written, it should not be modified or deleted until the retention period expires. This is typically implemented via append-only storage structures or blockchain-like hash chains.

---

## 3. 實務場景與系統設計視角
## 3. Real-World & System Design View

### 3.1 架構中的位置
### 3.1 Position in Architecture

在典型的 Microservices 架構中，這些模式通常位於以下位置：
In a typical Microservices architecture, these patterns are usually located as follows:

1.  **Secure Vault**：作為獨立的中心化服務（Centralized Service），或是透過 Sidecar 模式注入到 Application Pod 中。這避免了應用程式直接持有明文設定檔。
    **Secure Vault:** Acts as a centralized service or is injected into Application Pods via the Sidecar pattern. This prevents applications from holding plaintext configuration files.
2.  **Rate Limiter**：通常位於 API Gateway 層（處理 L7 流量）或 Load Balancer（處理 L4 流量），也可以作為 Middleware 嵌入在服務內部（用於保護特定資源）。
    **Rate Limiter:** Usually sits at the API Gateway layer (handling L7 traffic) or Load Balancer (handling L4 traffic), or can be embedded as Middleware within services (to protect specific resources).
3.  **Audit Service**：通常是一個異步的 Consumer。業務服務將事件發送到 Message Queue（如 Kafka），Audit Service 消費這些事件並寫入 Cold Storage（如 S3/Glacier 或 Elasticsearch）。
    **Audit Service:** Typically an asynchronous Consumer. Business services send events to a Message Queue (e.g., Kafka), and the Audit Service consumes these events and writes them to Cold Storage (e.g., S3/Glacier or Elasticsearch).

### 3.2 效能與安全性的權衡（Trade-offs）
### 3.2 Trade-offs: Performance vs. Security

*   **Vault**：每次讀取 Secret 都呼叫遠端 Vault 會增加 Latency 並造成單點故障風險。
    *   *Solution*：使用 Client-side Caching，但必須設定嚴格的 TTL（Time-To-Live）。
*   **Vault:** Calling a remote Vault for every secret read increases latency and creates a single point of failure risk.
    *   *Solution:* Use Client-side Caching, but with a strict TTL (Time-To-Live).

*   **Rate Limiter**：精確的全域計數（Global Counter）需要鎖定分散式快取（如 Redis），這會降低吞吐量。
    *   *Solution*：使用「最終一致性」的計數，或在本地記憶體做預聚合（Pre-aggregation），再同步到 Redis。
*   **Rate Limiter:** Precise global counting requires locking distributed caches (like Redis), which reduces throughput.
    *   *Solution:* Use "eventually consistent" counting, or perform pre-aggregation in local memory before syncing to Redis.

---

## 4. 逐步示例：分散式限流器設計
## 4. Walkthrough: Designing a Distributed Rate Limiter

### 4.1 問題背景
### 4.1 Problem Context

我們需要保護一個高併發的 Payment API，限制每個 User ID 每秒最多發送 10 個請求（10 TPS）。系統運行在 Kubernetes 上，有多個 Pods。
We need to protect a high-concurrency Payment API, limiting each User ID to a maximum of 10 requests per second (10 TPS). The system runs on Kubernetes with multiple Pods.

### 4.2 Naive Approach: Local Counter
### 4.2 Naive Approach: Local Counter

最直覺的做法是在每個 Application Instance 的記憶體中使用 `HashMap<UserId, Count>`。
The most intuitive approach is to use a `HashMap<UserId, Count>` in the memory of each Application Instance.

*   **問題**：Load Balancer 會將流量分發到不同 Pod。如果 User 的請求被分散到 3 個 Pod，實際限流值變成了 30 TPS。這無法實現精確的全域限流。
    **Problem:** The Load Balancer distributes traffic across different Pods. If a User's requests are spread across 3 Pods, the actual limit becomes 30 TPS. This fails to achieve precise global rate limiting.

### 4.3 Mature Solution: Redis + Lua Script (Sliding Window / Token Bucket)
### 4.3 Mature Solution: Redis + Lua Script (Sliding Window / Token Bucket)

我們使用 Redis 作為集中式儲存。為了避免 "Check-then-Act" 的 Race Condition（即兩個請求同時讀取計數器，都以為沒超標，然後同時加 1），我們必須保證操作的原子性（Atomicity）。
We use Redis as centralized storage. To avoid the "Check-then-Act" Race Condition (where two requests read the counter simultaneously, both think it's under the limit, and both increment it), we must ensure operation atomicity.

**Lua Script Implementation (Fixed Window Counter):**

```lua
-- KEYS[1]: The unique key for the user (e.g., "ratelimit:user:123:timestamp")
-- ARGV[1]: The limit (e.g., 10)
-- ARGV[2]: The window size in seconds (e.g., 1)

local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])

-- Increment the counter
local current = redis.call("INCR", key)

if current == 1 then
    -- If this is the first request, set the expiration
    redis.call("EXPIRE", key, window)
end

if current > limit then
    return 0 -- Rejected
else
    return 1 -- Allowed
end
```

### 4.4 複雜度與邊界分析
### 4.4 Complexity & Edge Case Analysis

*   **時間複雜度**：Redis Lua 腳本執行極快，接近 O(1)。
    **Time Complexity:** Redis Lua script execution is extremely fast, close to O(1).
*   **空間複雜度**：O(U)，其中 U 是活躍用戶數。過期 Key 會被 Redis 自動清除。
    **Space Complexity:** O(U), where U is the number of active users. Expired keys are automatically evicted by Redis.
*   **邊界情況（Edge Case）**：
    *   **Redis 故障**：如果 Redis 掛了，API 應該 Fail-open（允許通過）還是 Fail-closed（拒絕所有）？對於 Payment API，通常選擇 Fail-closed 或降級到本地限流。
    *   **Redis Failure:** If Redis goes down, should the API Fail-open (allow traffic) or Fail-closed (reject all)? For a Payment API, Fail-closed or degrading to local rate limiting is usually preferred.
    *   **臨界點突波（Window Boundary Spike）**：固定視窗（Fixed Window）在視窗切換瞬間（例如 00:59 到 01:00）可能允許雙倍流量。改用 Sliding Window Log 或 Token Bucket 可解決此問題。
    *   **Window Boundary Spike:** Fixed Window can allow double traffic at the moment the window switches (e.g., 00:59 to 01:00). Using Sliding Window Log or Token Bucket solves this.

---

## 5. 常見錯誤與反模式
## 5. Common Pitfalls & Anti-patterns

### 5.1 依賴 IP 進行限流
### 5.1 Rate Limiting Based on IP

*   **錯誤描述**：僅使用 `Client IP` 作為限流的 Key。
    **Description:** Using only `Client IP` as the key for rate limiting.
*   **為何不好**：大型企業或學校網路通常共用同一個 NAT IP 出口。封鎖一個 IP 可能會誤殺成千上萬個合法使用者。此外，攻擊者可以輕易使用 Botnet 輪替 IP。
    **Why it's bad:** Large enterprises or campus networks often share a single NAT IP exit. Blocking one IP could affect thousands of legitimate users. Also, attackers can easily rotate IPs using Botnets.
*   **較佳方案**：優先使用 `API Key` 或 `User ID`。若必須針對未登入用戶，可結合 `IP + UserAgent` 或使用 Device Fingerprinting。
    **Better Approach:** Prioritize `API Key` or `User ID`. If you must limit unauthenticated users, combine `IP + UserAgent` or use Device Fingerprinting.

### 5.2 同步寫入稽核日誌
### 5.2 Synchronous Audit Logging

*   **錯誤描述**：在處理業務邏輯的同一個 DB Transaction 中，同步寫入 Audit Log 到資料庫。
    **Description:** Writing Audit Logs to the database synchronously within the same DB Transaction as the business logic.
*   **為何不好**：這增加了 Transaction 的鎖定時間，降低系統吞吐量。若 Log 寫入失敗，會導致業務交易回滾（Rollback），這是不可接受的偶合。
    **Why it's bad:** This increases the lock time of the transaction, reducing system throughput. If the log write fails, it causes the business transaction to rollback, which is an unacceptable coupling.
*   **較佳方案**：使用「Fire-and-forget」模式，將 Log 發送到 Kafka/SQS，由專門的 Consumer 異步寫入。
    **Better Approach:** Use a "Fire-and-forget" pattern, sending logs to Kafka/SQS, and have a dedicated Consumer write them asynchronously.

### 5.3 在程式碼中自幹加密演算法
### 5.3 Rolling Your Own Crypto

*   **錯誤描述**：開發者試圖自己實作 AES 加密流程，或是將 Key 硬編碼在 Config 中。
    **Description:** Developers attempting to implement AES encryption flows themselves, or hardcoding keys in configs.
*   **為何不好**：加密實作極易出錯（如 IV 重複使用、Padding Oracle 攻擊）。
    **Why it's bad:** Encryption implementation is prone to errors (e.g., IV reuse, Padding Oracle attacks).
*   **較佳方案**：使用經過驗證的高階程式庫（如 Google Tink, AWS Encryption SDK）並整合 KMS。
    **Better Approach:** Use proven high-level libraries (e.g., Google Tink, AWS Encryption SDK) and integrate with KMS.

---

## 6. 面試與實務問答切入點
## 6. Interview & Discussion Hooks

### Q1: 請設計一個能夠處理百萬級 QPS 的分散式限流系統。
### Q1: Design a distributed rate limiting system capable of handling million-level QPS.

*   **高分回答要點**：
    *   **分層架構**：在 Load Balancer 層做粗粒度過濾（防 DDoS），在 Application 層做細粒度業務限流。
    *   **本地 + 遠端快取**：為了減少 Redis 負載，可以在本地記憶體扣除一部分 Token（例如一次取 10 個），用完再向 Redis 申請（Batching）。
    *   **降級策略**：當 Redis 延遲過高時，自動切換為本地限流模式。
*   **Key Points for High Score:**
    *   **Layered Architecture:** Coarse-grained filtering at the Load Balancer layer (Anti-DDoS), fine-grained business limiting at the Application layer.
    *   **Local + Remote Cache:** To reduce Redis load, deduct tokens in batches locally (e.g., fetch 10 at a time) and request more from Redis only when exhausted (Batching).
    *   **Degradation Strategy:** Automatically switch to local rate limiting when Redis latency is too high.

### Q2: 我們需要儲存使用者的信用卡號（PII），你會如何設計儲存與存取方案？
### Q2: We need to store user credit card numbers (PII). How would you design the storage and access scheme?

*   **高分回答要點**：
    *   **Tokenization**：真正的卡號不應進入主業務資料庫，而是存入獨立的 PCI-DSS 合規 Vault，並換回一個 Token 給業務系統使用。
    *   **Envelope Encryption**：解釋 DEK/KEK 機制。
    *   **Access Control**：只有極少數服務有權限用 Token 換回卡號（Detokenization）。
*   **Key Points for High Score:**
    *   **Tokenization:** Real card numbers should not enter the main business DB. Store them in a separate PCI-DSS compliant Vault and exchange them for a Token used by the business system.
    *   **Envelope Encryption:** Explain the DEK/KEK mechanism.
    *   **Access Control:** Only very few services should have permission to exchange the Token back for the card number (Detokenization).

### Q3: 如何確保 Audit Log 不被惡意管理員竄改？
### Q3: How do you ensure Audit Logs are not tampered with by a malicious administrator?

*   **高分回答要點**：
    *   **WORM Storage**：使用 S3 Object Lock (Compliance Mode) 或類似技術。
    *   **Hash Chain / Merkle Tree**：將每條日誌的 Hash 包含在下一條日誌中，任何修改都會破壞鏈條。
    *   **Least Privilege**：即便是管理員，也不應擁有刪除 Log 的權限（Separation of Duties）。
*   **Key Points for High Score:**
    *   **WORM Storage:** Use S3 Object Lock (Compliance Mode) or similar technologies.
    *   **Hash Chain / Merkle Tree:** Include the hash of each log entry in the next one; any modification breaks the chain.
    *   **Least Privilege:** Even administrators should not have permission to delete logs (Separation of Duties).

---

## 7. 小結與後續延伸
## 7. Summary & Next Steps

### 記憶錨點 (Key Takeaways)
1.  **Envelope Encryption**：用 DEK 加密資料，用 KEK 加密 DEK。這是大規模金鑰管理的標準。
2.  **Rate Limiting vs. Throttling**：前者是業務邏輯（付費等級），後者是基礎設施保護（防過載）。
3.  **Redis + Lua**：是實作分散式限流的黃金組合，保證了原子性。
4.  **Async Auditing**：稽核日誌必須是異步且不可變的（Immutable），避免阻塞主流程。
5.  **Fail-closed vs. Fail-open**：在設計資安機制時，必須明確定義系統故障時的預設行為。

### 後續延伸 (Next Steps)
*   **延伸閱讀**：研究 **Google Zanzibar** 論文，了解全球規模的 ACL（Access Control List）系統是如何設計的。
*   **實作練習**：使用 HashiCorp Vault 的 Transit Engine 實作一個簡單的加密代理服務（Encryption Proxy）。
*   **下一章預告**：我們將探討 **Identity & Access Management (IAM)** 在微服務間的傳遞（OAuth2, OIDC, JWT）。