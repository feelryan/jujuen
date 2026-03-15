# 1. 前言與學習目標 (Introduction & Learning Goals)

作為資深工程師，在開發環境中運行 ElasticSearch (ES) 與在生產環境中維運它是兩回事。當數據量達到 TB 級別、QPS 達到數萬時，預設配置往往會導致災難。本章專注於「當事情出錯時該怎麼辦」以及「如何預防事情出錯」。

As a Senior Engineer, running ElasticSearch (ES) in a development environment is vastly different from operating it in production. When data volume hits terabytes and QPS reaches tens of thousands, default configurations often lead to disaster. This chapter focuses on "what to do when things go wrong" and "how to prevent things from going wrong."

完成本章後，你應該能夠：

By the end of this chapter, you should be able to:

1.  **診斷並解決記憶體問題 (Diagnose and resolve memory issues)**：區分 Java Heap 壓力、GC 停頓 (GC Pauses) 與 Circuit Breaker 觸發的根本原因。
2.  **處理叢集狀態異常 (Handle cluster state anomalies)**：熟練使用 Allocation Explain API 排查 Red/Yellow 狀態，並執行節點崩潰後的復原流程。
3.  **設計高可用監控體系 (Design HA monitoring systems)**：建立正確的監控指標 (Metrics) 與警報 (Alerts)，而不僅僅是看 CPU 使用率。
4.  **理解寫入拒絕與背壓 (Understand write rejection and backpressure)**：正確配置 Thread Pools 與 Queue，並在客戶端實作重試機制。

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

在深入故障排除之前，我們需要建立一個關於 ES 資源管理的正確心智模型。

Before diving into troubleshooting, we need to establish a correct mental model regarding ES resource management.

### 2.1 記憶體戰場：Heap vs. Off-Heap (The Memory Battlefield)

ES 的記憶體使用可以類比為**冰山**。
**JVM Heap** 是水面上的部分，負責存放物件實例、協調請求與部分快取 (Node Query Cache)。
**Off-Heap (OS Cache)** 是水面下的巨大基座，Lucene 依賴它來存放 Segment 檔案，這對搜尋效能至關重要。

ES memory usage can be analogized to an **iceberg**.
**JVM Heap** is the part above water, holding object instances, coordinating requests, and some caches (Node Query Cache).
**Off-Heap (OS Cache)** is the massive base underwater; Lucene relies on it to store Segment files, which is critical for search performance.

*   **關鍵規則 (Key Rule)**：Heap Size 不應超過實體記憶體的 50%，且不應超過 32GB (Compressed OOPs 限制)。剩下的 50% 必須留給 Lucene 使用。
*   **Key Rule**: Heap Size should not exceed 50% of physical RAM and should stay under 32GB (Compressed OOPs limit). The remaining 50% must be left for Lucene.

### 2.2 斷路器 (Circuit Breakers)

將 Circuit Breaker 想像成家裡的**保險絲**。當查詢或聚合操作 (Aggregations) 試圖載入過多數據到記憶體中，導致即將發生 OOM (Out of Memory) 時，斷路器會先跳閘，主動中斷請求以保護節點不崩潰。

Think of Circuit Breakers as the **fuses** in your home. When a query or aggregation attempts to load too much data into memory, threatening an OOM (Out of Memory) error, the breaker trips first, actively aborting the request to protect the node from crashing.

*   **Parent Circuit Breaker**: 總開關，監控所有斷路器的總和。
*   **Field Data Circuit Breaker**: 針對 Text 欄位進行聚合或排序時的記憶體消耗。
*   **Request Circuit Breaker**: 針對單個請求本身的結構大小（例如極大的 JSON body）。

### 2.3 叢集顏色與分片分配 (Cluster Color & Shard Allocation)

*   **Green**: 所有 Primary 和 Replica Shards 都已分配。
*   **Yellow**: 所有 Primary Shards 已分配，但部分 Replica Shards 未分配（資料可讀寫，但無高可用性）。
*   **Red**: 至少有一個 Primary Shard 未分配（部分資料遺失或不可用）。

*   **Green**: All Primary and Replica Shards are allocated.
*   **Yellow**: All Primary Shards are allocated, but some Replica Shards are not (Data is readable/writable, but no High Availability).
*   **Red**: At least one Primary Shard is unassigned (Partial data loss or unavailability).

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型分散式系統中，ES 通常位於資料管線的末端或作為輔助查詢引擎。

In large-scale distributed systems, ES usually sits at the end of a data pipeline or acts as a secondary query engine.

### 3.1 架構中的角色 (Role in Architecture)

1.  **Log Aggregation (ELK Stack)**: 高寫入吞吐量 (High Write Throughput)。故障通常發生在寫入隊列滿載 (Bulk Queue Rejection)。
2.  **Search Engine (E-commerce)**: 高讀取低延遲 (High Read, Low Latency)。故障通常源於複雜聚合導致的 CPU 飆升或 Field Data 撐爆 Heap。

### 3.2 故障隔離設計 (Failure Isolation Design)

為了避免單點故障擴散，資深工程師會設計以下機制：

To prevent single points of failure from spreading, senior engineers design the following mechanisms:

*   **Dedicated Master Nodes**: 在大型叢集（>10 個節點）中，務必將 Master 節點與 Data 節點分離。Master 負責維護 Cluster State，不應被繁重的 CRUD 操作拖垮。
*   **Shard Allocation Awareness**: 強制 ES 將 Primary 和 Replica 分配到不同的實體機架 (Rack) 或可用區 (Availability Zone, AZ)。
*   **Client-Side Load Balancing**: 應用程式端（或 Sidecar）應知道所有 Data Nodes 的地址，並進行 Round-robin，而非只打單一節點。

---

# 4. 逐步示例：排查 "Data too large" 與 GC 停頓 (Walkthrough: Troubleshooting "Data too large" & GC Pauses)

### 情境 (Scenario)

你的監控系統發出警報：ES 叢集回應變慢，部分查詢返回 503 錯誤。Kibana 顯示節點頻繁離線又重新加入。Log 中出現大量 `CircuitBreakingException: [parent] Data too large`。

Your monitoring system alerts: ES cluster response is slowing down, some queries return 503 errors. Kibana shows nodes frequently dropping off and rejoining. Logs show massive `CircuitBreakingException: [parent] Data too large`.

### 步驟 1: 確認 GC 狀態 (Check GC Status)

首先，檢查這是否是真正的記憶體洩漏，還是只是負載過高導致的 GC 頻繁。使用 `_nodes/stats` API。

First, check if this is a real memory leak or just frequent GC due to high load. Use the `_nodes/stats` API.

```bash
GET /_nodes/stats/jvm?human
```

**關注點 (Focus Points):**
*   `jvm.gc.collectors.old.collection_count`: 如果這個數字在短時間內急劇增加，代表發生了頻繁的 Full GC。
*   `jvm.mem.heap_used_percent`: 如果長時間維持在 75% 以上且 GC 後無法下降，說明 Heap 壓力極大。

### 步驟 2: 分析斷路器 (Analyze Circuit Breakers)

確認是哪種類型的記憶體佔用觸發了斷路器。

Confirm which type of memory usage triggered the breaker.

```bash
GET /_nodes/stats/breaker?human
```

如果 `fielddata` 的 `estimated_size` 很高，通常是因為開發者對 `text` 欄位執行了聚合 (Aggregation) 或排序 (Sorting)，這會強迫 ES 將倒排索引解壓縮並載入 Heap。

If `fielddata`'s `estimated_size` is high, it's usually because developers performed aggregations or sorting on `text` fields, forcing ES to uncompress the inverted index and load it into the Heap.

### 步驟 3: 尋找元兇查詢 (Identify the Culprit Query)

使用 Task Management API 查看當前正在執行的耗時任務。

Use the Task Management API to view currently running long-duration tasks.

```bash
GET /_tasks?detailed=true&actions=*search
```

**解決方案 (Solution):**
1.  **短期 (Short-term)**: 取消該任務 `POST /_tasks/{task_id}/_cancel`，或重啟節點（最後手段）。
2.  **長期 (Long-term)**:
    *   修改 Mapping，將該欄位改為 `keyword` 類型（使用 Doc Values，存放在 Disk/OS Cache 而非 Heap）。
    *   限制 `indices.breaker.total.limit`（預設 70% JVM Heap），確保保留緩衝區。

### 步驟 4: 處理 Unassigned Shards (Handling Unassigned Shards)

如果節點崩潰導致叢集變紅 (Red)，重啟後仍有 Shard 未分配，使用 Explain API。

If a node crash turns the cluster Red, and Shards remain unassigned after restart, use the Explain API.

```bash
GET /_cluster/allocation/explain
{
  "index": "my-index",
  "shard": 0,
  "primary": true
}
```

**常見原因與對策 (Common Causes & Fixes):**
*   `NODE_LEFT`: 等待 `index.unassigned.node_left.delayed_timeout`（預設 1m）。
*   `ALLOCATION_FAILED`: 磁碟滿了或檔案損壞。如果是磁碟滿，清理空間或調整 Watermark 設定。

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 盲目增加 Heap Size (Blindly Increasing Heap Size)

*   **錯誤 (Mistake)**: 看到 OOM 就把 Heap 從 30GB 加到 64GB。
*   **後果 (Consequence)**: 跨越 32GB 門檻後，JVM 停止使用 Compressed OOPs (Object Pointers)，指標從 32-bit 變 64-bit，導致記憶體使用效率下降，實際可用空間反而變少，且 GC 停頓時間大幅拉長。
*   **修正 (Fix)**: 保持在 30-31GB 以下。若不夠用，請水平擴展 (Horizontal Scaling) 增加節點。

### 5.2 忽視 Yellow 狀態 (Ignoring Yellow Status)

*   **錯誤 (Mistake)**: 認為「反正讀寫都正常，Yellow 沒關係」。
*   **後果 (Consequence)**: Yellow 代表 Replica 缺失。此時若 Primary 所在的節點硬體故障，數據將**永久遺失**。
*   **修正 (Fix)**: 設定監控警報，Yellow 狀態超過 5 分鐘即報警。

### 5.3 Mapping Explosion (Mapping Explosion)

*   **錯誤 (Mistake)**: 允許動態 Mapping，且寫入大量不固定的 Key（例如將 User Agent 或 URL 參數直接作為 Field Name）。
*   **後果 (Consequence)**: Cluster State 變得極其巨大（數百 MB）。每次 Mapping 更新都要同步給所有節點，導致 Master 節點阻塞，全叢集卡死。
*   **修正 (Fix)**: 設定 `index.mapping.total_fields.limit` (預設 1000)，並嚴格審查 Schema 設計。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

這些問題可用於評估候選人對 ES 維運的深度理解。

These questions can be used to assess a candidate's depth of understanding regarding ES operations.

### Q1: 生產環境中，ES 叢集突然變成 Red 狀態，你會如何排查？
**How would you troubleshoot if an ES cluster suddenly turns Red in production?**

*   **高分回答要點 (Key Points)**:
    1.  **止血**: 暫停非必要寫入，保護現場。
    2.  **診斷**: 使用 `_cluster/health` 確認受影響範圍，使用 `_cluster/allocation/explain` 找出 Shard 無法分配的具體原因（Disk full? Node left? Version mismatch?）。
    3.  **恢復**: 若是節點暫時離線，等待恢復；若是資料損壞，嘗試從 Replica 恢復或從 Snapshot 還原。
    4.  **預防**: 提及 Shard Allocation Awareness 和 Snapshot Lifecycle Management (SLM)。

### Q2: 為什麼我們建議將 Master 節點與 Data 節點分離？
**Why do we recommend separating Master nodes from Data nodes?**

*   **高分回答要點 (Key Points)**:
    1.  **資源隔離**: Data nodes 消耗大量 CPU/IO/Memory 進行索引和搜尋。若 Master 混用，資源耗盡會導致 Cluster State 無法更新。
    2.  **穩定性**: Master 負責節點成員管理與 Shard 分配。如果 Master 因 GC 停頓而被視為 "Failed"，會引發不必要的 Master Election 和 Shard Rebalancing，造成 "Flapping"（震盪）。
    3.  **腦裂 (Split Brain)**: 雖然 7.x+ 改進了共識算法，但分離節點仍是最佳實踐，確保 Quorum 穩定。

### Q3: 如何處理 ES 的寫入拒絕 (Write Rejection / 429 Errors)？
**How do you handle Write Rejection (429 Errors) in ES?**

*   **高分回答要點 (Key Points)**:
    1.  **理解機制**: 這是 ES 的自我保護。Thread Pool 滿了，Queue 也滿了。
    2.  **客戶端策略**: 實作指數退避 (Exponential Backoff) 重試機制。
    3.  **伺服器端優化**: 檢查 `write` thread pool 大小（通常是 CPU cores + 1）。不要盲目增加 Queue size（會導致 OOM）。
    4.  **架構優化**: 引入 Kafka 作為緩衝層，削峰填谷。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)

1.  **Heap < 32GB**: 永遠遵守 Compressed OOPs 的限制，留 50% 給 Lucene (OS Cache)。
2.  **Circuit Breakers**: 是最後一道防線，觸發代表查詢模式或 Schema 有問題，而不僅僅是資源不足。
3.  **Allocation Explain**: `_cluster/allocation/explain` 是解決 Red/Yellow 狀態的神器。
4.  **Master/Data Separation**: 在生產環境中，職責分離是穩定性的基石。
5.  **Monitor Queues & GC**: 監控 Thread Pool Queue 的拒絕數和 Old GC 的頻率，比單看 CPU 更重要。

### 後續延伸 (Next Steps)

*   **Next Chapter**: 效能調優 (Performance Tuning)。既然系統已經穩定了，下一章我們將探討如何優化 Indexing 速度與 Search Latency（例如：Segment Merging 策略、Refresh Interval 調整）。
*   **Action Item**: 檢查你當前生產環境的 `indices.breaker.total.limit` 設定，並確認是否有針對 `fielddata` 的監控警報。