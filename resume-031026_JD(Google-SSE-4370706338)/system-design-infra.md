# 系統設計：診斷基礎設施 / System Design: Diagnostic Infrastructure | System Design: Diagnostic Infrastructure

## 1. 目標與範圍 | Goal & Scope
- 展示設計大規模、高可用性監控與診斷系統的能力（如日誌蒐集、指標聚合、警報觸發）。｜Demonstrate the ability to design large-scale, high-availability monitoring and diagnostic systems (e.g., log collection, metric aggregation, alert triggering).
- 連結過去在「警報系統」與「大規模資料索引」的經驗，證明能處理 Google 等級的資料量。｜Connect past experience in "alerting systems" and "large-scale data indexing" to prove capability in handling Google-scale data volumes.
- 針對 JD 提到的「測試機隊（Test Fleet）」與「NPI（新產品導入）」場景，提出具體的自動化診斷架構。｜Propose a specific automated diagnostic architecture addressing the "Test Fleet" and "NPI (New Product Introduction)" scenarios mentioned in the JD.

## 2. 簡短開場稿 | Opening Script

**30-Second Pitch (Focus on Infra & Diagnostics):**
「我有超過 15 年的軟體開發經驗，目前是 Google 認證的雲端架構師。我對診斷基礎設施並不陌生，我曾在中華電信主導設計國家級的『緊急訊息警報平台』與 e-SAV 雲端監控平台，這讓我對處理高併發、低延遲的訊號傳輸有深刻理解。近期在 Innova Solutions，我則專注於 GCP 環境下的自動化稽核與事件驅動架構。我擅長設計能從底層硬體訊號到上層應用日誌都能有效整合的系統。」

"I have over 15 years of software development experience and am a Google Certified Professional Cloud Architect. I am no stranger to diagnostic infrastructure; at Chunghwa Telecom, I led the design of the National Emergency Message Alert Platform and the e-SAV cloud monitoring platform, giving me deep insight into handling high-concurrency, low-latency signal transmission. Recently at Innova Solutions, I’ve focused on automated auditing and event-driven architectures within GCP. I specialize in designing systems that effectively integrate everything from low-level hardware signals to upper-layer application logs."

## 3. 關鍵故事與成就 | Key Stories & Achievements

### 故事一：國家級警報與監控平台 (中華電信) | Story 1: National Alert & Monitoring Platform (Chunghwa Telecom)
*此案例最貼近 Diagnostic Infrastructure 的『即時性』與『高可靠性』需求。*

- **情境 (Situation):** 需要建立一個國家級的緊急訊息警報平台與 e-SAV（感測器、警報、影像）雲端平台，整合多種異質系統。｜Needed to build a National Emergency Message Alert Platform and e-SAV (Sensor, Alert, Video) cloud platform, integrating multiple heterogeneous systems.
- **任務 (Task):** 設計一個高可用性架構，確保在緊急狀況下，監控數據與警報能即時且準確地傳遞，無單點故障。｜Design a high-availability architecture ensuring that monitoring data and alerts are delivered instantly and accurately during emergencies, with no single point of failure.
- **行動 (Action):** 我制定了系統架構與高階規格，整合 eGov 介面，並設計了能處理大量併發請求的訊息佇列機制。｜I defined the system architecture and high-level specs, integrated eGov interfaces, and designed message queue mechanisms to handle massive concurrent requests.
- **結果 (Result):** 成功交付系統，成為國家基礎設施的一部分；這證明我有能力設計處理關鍵訊號（Critical Signals）的可靠系統。｜Successfully delivered the system as part of national infrastructure; this proves my ability to design reliable systems for handling critical signals.

### 故事二：大規模日誌索引與搜尋 (USTOSHOP) | Story 2: Large-Scale Log Indexing & Search (USTOSHOP)
*此案例對應診斷系統中的『資料儲存』與『檢索』能力。*

- **情境 (Situation):** 系統擁有數百萬筆產品資料與交易紀錄，需要支援全文檢索與多欄位查詢，這與診斷日誌的查詢需求類似。｜The system hosted millions of product records and transaction logs, requiring full-text search and multi-field queries, similar to diagnostic log querying needs.
- **任務 (Task):** 建立一個高效的後端索引系統，確保查詢延遲極低，並能處理複雜的過濾條件。｜Build an efficient backend indexing system ensuring minimal query latency and handling complex filtering conditions.
- **行動 (Action):** 我實作了 ElasticSearch 叢集，設計了分片（Sharding）策略與倒排索引（Inverted Index），並優化了 Spring Boot 與 Node.js 的 API 介接層。｜I implemented an ElasticSearch cluster, designed sharding strategies and inverted indexes, and optimized the API interface layer using Spring Boot and Node.js.
- **結果 (Result):** 實現了毫秒級的查詢回應，這套索引與檢索的經驗可以直接應用於診斷日誌（Logs）的儲存與分析架構設計。｜Achieved millisecond-level query responses; this experience in indexing and retrieval is directly applicable to the storage and analysis architecture for diagnostic logs.

### 故事三：GCP 自動化與事件驅動架構 (Innova Solutions) | Story 3: GCP Automation & Event-Driven Architecture (Innova Solutions)
*此案例對應 JD 中的『自動化』與『雲端平台整合』。*

- **情境 (Situation):** 醫療影像平台需要針對新客戶自動配置資源，並需符合嚴格的稽核（Audit）需求。｜The medical imaging platform required automated resource provisioning for new customers and had to meet strict auditing requirements.
- **任務 (Task):** 設計自動化流程來觸發資源建立與日誌紀錄，減少人工介入並確保合規。｜Design automation workflows to trigger resource creation and logging, reducing manual intervention and ensuring compliance.
- **行動 (Action):** 利用 GCP Storage Events 觸發自動化動作（Push2Pacs），並建立客戶層級的定期稽核報告機制。｜Leveraged GCP Storage Events to trigger automated actions (Push2Pacs) and established a recurring mechanism for customer-level audit reports.
- **結果 (Result):** 提升了交付速度並確保了 100% 的操作可追溯性，這與診斷系統中「自動化修復（Auto-remediation）」的概念一致。｜Increased delivery velocity and ensured 100% operational traceability, aligning with the concept of "auto-remediation" in diagnostic systems.

## 4. 常見追問與應對 | Likely Follow‑ups & Responses

- **Q: How do you handle a "Thundering Herd" where thousands of machines send error logs simultaneously?**
  - **A (中文):** 我們需要在 Agent 端實作「抖動（Jitter）」與「緩衝（Buffering）」，並在接收端使用 Kafka/PubSub 進行削峰填谷。若負載過高，應啟動「採樣（Sampling）」或「降級（Shedding）」策略，優先保留關鍵錯誤。
  - **A (English):** We need to implement "Jitter" and "Buffering" at the Agent level, and use Kafka/PubSub at the ingestion layer for load leveling. If the load is too high, we should trigger "Sampling" or "Load Shedding" strategies, prioritizing critical errors.

- **Q: For the Test Fleet, how do you distinguish between a hardware failure and a software flake?**
  - **A (中文):** 這需要關聯分析（Correlation）。我會設計一個聚合層，比較同一批次硬體上的不同軟體表現，以及同一軟體在不同硬體上的表現。若僅特定機器報錯，則標記為潛在硬體故障並隔離該機器。
  - **A (English):** This requires correlation analysis. I would design an aggregation layer to compare different software versions on the same hardware batch, and vice versa. If errors are isolated to specific machines, I'd flag them as potential hardware failures and quarantine those nodes.

- **Q: How do you design for "Write-Heavy" diagnostic data?**
  - **A (中文):** 診斷數據通常是寫多讀少。我會選用 LSM-tree 結構的資料庫（如 Cassandra 或 BigTable）來優化寫入效能，並將熱數據（近期）與冷數據（歷史）分層儲存以節省成本。
  - **A (English):** Diagnostic data is typically write-heavy and read-rarely. I would choose an LSM-tree based database (like Cassandra or BigTable) to optimize write performance, and tier storage into Hot (recent) and Cold (historical) to save costs.

## 5. 技術深挖提示 | Technical Deep‑Dive Prompts

**預期考題：設計一個 Google 資料中心硬體健康度監控系統 (Design a hardware health monitoring system for Google Data Centers)**

**答題骨架 (Framework):**
1.  **需求分析 (Requirements):**
    -   *Functional:* 蒐集 metrics (CPU temp, fan speed), logs (kernel panic), heartbeat.
    -   *Non-Functional:* Scalability (百萬台機器), Low Latency (警報 < 1 min), Reliability (監控系統本身不能掛)。
2.  **高階架構 (High-Level Design):**
    -   **Agent (Sidecar/Daemon):** 跑在每台機器上，蒐集 `/proc` 或硬體感測器數據。
    -   **Ingestion (Push vs Pull):** 針對大規模 Fleet，通常採用 **Push** 到 Load Balancer -> Kafka (Buffer)。
    -   **Processing (Stream):** Flink/Dataflow 處理即時警報與去噪 (De-duplication)。
    -   **Storage:** Time-Series DB (Prometheus/Monarch) 存指標，Blob Store (GCS) 存原始日誌。
3.  **詳細設計 (Deep Dive):**
    -   *Agent 優化:* 使用 UDP 減少 overhead，或在本地預聚合 (Pre-aggregation)。
    -   *資料分區 (Partitioning):* 依照 `Cluster_ID` 或 `Rack_ID` 進行 Sharding。
4.  **瓶頸與解決 (Bottlenecks):**
    -   *單點故障:* 各組件皆需 Replica。
    -   *儲存成本:* 設定 Retention Policy，舊資料降採樣 (Downsampling)。

## 6. 常見陷阱與糾正 | Pitfalls & Corrections

-   **陷阱 1：過度關注應用層，忽略基礎設施層。**
    -   *錯誤:* 只談 HTTP 錯誤碼或 API Latency。
    -   *糾正:* JD 強調 "Hardware" 與 "Test Fleet"。要提到 Kernel logs, Disk I/O, Thermal metrics, Firmware versions 等底層指標。
    -   *Correction:* The JD emphasizes "Hardware" and "Test Fleet." Mention low-level metrics like Kernel logs, Disk I/O, Thermal metrics, and Firmware versions.

-   **陷阱 2：忽略「雜訊」處理。**
    -   *錯誤:* 假設所有 Log 都要存下來並觸發警報。
    -   *糾正:* 在大規模系統中，雜訊是巨大的。必須強調「去重（Deduplication）」、「聚合（Aggregation）」與「異常檢測（Anomaly Detection）」的重要性。
    -   *Correction:* In large-scale systems, noise is massive. Emphasize the importance of "Deduplication," "Aggregation," and "Anomaly Detection."

-   **陷阱 3：沒有閉環（Feedback Loop）。**
    -   *錯誤:* 系統只負責「顯示」錯誤。
    -   *糾正:* 優秀的診斷系統應該具備「可行動性（Actionability）」。例如：偵測到硬體故障 -> 自動建立 Ticket -> 自動將機器下線（Drain）-> 通知維修。
    -   *Correction:* A great diagnostic system must be "Actionable." E.g., Detect hardware failure -> Auto-create ticket -> Auto-drain node -> Notify repair.

## 7. 收尾與反問 | Closing & Questions for Interviewer

**收尾 (Closing):**
「總結來說，我結合了在中華電信建立國家級警報系統的高可用性經驗，以及在 Innova Solutions 的 GCP 自動化實務。我了解如何設計一個既能處理底層硬體訊號，又能在大規模環境下保持穩定的診斷基礎設施。」
"To summarize, I combine my experience building high-availability national alert systems at Chunghwa Telecom with GCP automation practices from Innova Solutions. I understand how to design a diagnostic infrastructure that handles low-level hardware signals while maintaining stability at scale."

**反問 (Questions):**
1.  "In the JD, it mentions 'Test Fleet'. Is the primary challenge currently the *volume* of data generated by NPI testing, or the *variety* of new hardware signals we need to support?" (針對 JD 的 Test Fleet 提問)
2.  "How integrated is the diagnostic toolchain with the automatic remediation systems currently? Are we moving towards a fully self-healing fleet?" (展現對自動化修復的願景)
3.  "For the 'System Programming' aspect, are we looking more at kernel-level instrumentation or user-space agents for data collection?" (釐清技術深度)