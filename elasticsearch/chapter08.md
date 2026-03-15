# Chapter 08: Cluster Planning and ILM (集群規劃與生命週期管理)

## 1. Introduction & Learning Objectives (前言與學習目標)

In the lifecycle of an ElasticSearch adoption, moving from a development prototype to a production-grade cluster is a critical leap. Many Senior Engineers struggle not with the query syntax, but with operational stability: nodes running out of heap, shards becoming too numerous, or costs spiraling out of control. This chapter focuses on the architectural decisions required to host time-series data (logs, metrics, events) efficiently at scale.

在 ElasticSearch 的採用生命週期中，從開發原型過渡到生產級集群是一個關鍵的跨越。許多資深工程師並非受困於查詢語法，而是掙扎於維運的穩定性：節點 Heap 耗盡、Shard 數量過多，或是成本失控。本章專注於大規模託管時間序列資料（日誌、指標、事件）時所需的架構決策。

By the end of this chapter, you will be able to:
完成本章後，您將能夠：

1.  **Execute Capacity Planning:** Calculate required storage, RAM, and node count based on ingestion rate and retention policies.
    **執行容量規劃**：根據寫入速率與保留策略，計算所需的儲存空間、記憶體與節點數量。
2.  **Design Hot-Warm-Cold Architectures:** Implement tiered storage strategies to balance performance and cost.
    **設計 Hot-Warm-Cold 架構**：實作分層儲存策略，以平衡效能與成本。
3.  **Master Shard Sizing:** Apply the "Goldilocks" principle to shard sizes to avoid oversharding or hotspots.
    **掌握 Shard Sizing**：應用「黃金比例」原則設定 Shard 大小，避免過度切分或熱點問題。
4.  **Implement ILM (Index Lifecycle Management):** Automate the rollover, shrink, force-merge, and deletion of indices using native APIs.
    **實作 ILM（索引生命週期管理）**：使用原生 API 自動化索引的 Rollover、Shrink、Force-merge 與刪除作業。

---

## 2. Core Concepts & Mental Model (核心觀念與心智模型)

### 2.1 The Shard "Goldilocks Zone" (Shard 的黃金區間)

**Concept:** An ElasticSearch shard is a Lucene index. It consumes file handles, memory, and CPU.
*   **Too Small:** High overhead. The cluster state becomes large, and updates are slow. (The "Million Tiny Shards" death spiral).
*   **Too Large:** Recovery takes forever. Moving a 1TB shard between nodes is risky. Search threads get blocked longer.
*   **Just Right:** Generally, **10GB – 50GB** per shard is the industry standard recommendation for logging use cases.

**觀念**：ElasticSearch 的 Shard 本質上就是一個 Lucene 索引。它會消耗 File Handles、記憶體與 CPU。
*   **太小**：Overhead 過高。Cluster State 變得龐大，更新變慢（即「百萬微小 Shards」的死亡螺旋）。
*   **太大**：復原（Recovery）耗時過久。在節點間搬移 1TB 的 Shard 風險極高，且搜尋執行緒會被阻塞更久。
*   **剛好**：一般而言，針對日誌型應用，**10GB – 50GB** 是業界標準的建議大小。

### 2.2 Tiered Architecture (分層架構)

Think of your data like inventory in a retail store:
*   **Hot (The Showroom):** New items, high interaction, fast access required. Expensive real estate (NVMe SSD, High CPU).
*   **Warm (The Stockroom):** Recent items, accessed less frequently. Cheaper storage (SATA SSD/HDD), medium specs.
*   **Cold/Frozen (The Warehouse):** Old items, rarely needed but legally required. Cheapest storage (Object Store/S3 snapshots), minimal compute.

將資料想像成零售店的庫存：
*   **Hot（展示間）**：新品，互動頻繁，需要快速存取。昂貴的資源（NVMe SSD，高 CPU）。
*   **Warm（存貨間）**：近期的物品，存取頻率較低。較便宜的儲存（SATA SSD/HDD），中等規格。
*   **Cold/Frozen（倉庫）**：舊物品，極少需要但因法規需保留。最便宜的儲存（Object Store/S3 快照），極低的運算資源。

### 2.3 Index Lifecycle Management (ILM)

ILM is a **State Machine** for your indices. Instead of writing cron jobs to delete old indices (e.g., `curator`), you define a policy. The cluster monitors indices and transitions them through phases (Hot → Warm → Cold → Delete) based on age, size, or document count.

ILM 是索引的 **狀態機（State Machine）**。您不再需要編寫 Cron jobs（例如 `curator`）來刪除舊索引，而是定義策略。集群會監控索引，並根據時間、大小或文件數量，將其在不同階段（Hot → Warm → Cold → Delete）之間轉換。

---

## 3. Real-World & System Design View (實務場景與系統設計視角)

### 3.1 Architecture Diagram (Logical) (架構邏輯)

In a typical large-scale logging system (e.g., Centralized Logging for Microservices):

在典型的大規模日誌系統（例如：微服務的集中式日誌）中：

1.  **Ingest:** Logstash/Fluentd/Beats send data to an **Ingest Node** or Load Balancer.
2.  **Hot Phase:** Data lands in `logs-write` alias. Backed by NVMe SSDs. Heavy indexing, heavy reading.
3.  **Rollover:** When the index hits 50GB or 24 hours, ILM rolls it over. A new write index is created.
4.  **Warm Phase:** The old index is moved to Warm nodes (HDD). `Force Merge` is applied to reduce segment count (crucial for read performance).
5.  **Cold Phase:** After 30 days, move to Cold nodes or mount as a searchable snapshot (S3).
6.  **Delete:** After 90 days, the index is removed.

1.  **寫入**：Logstash/Fluentd/Beats 將資料發送到 **Ingest Node** 或負載平衡器。
2.  **Hot 階段**：資料進入 `logs-write` 別名。由 NVMe SSD 支援。高頻寫入，高頻讀取。
3.  **Rollover**：當索引達到 50GB 或 24 小時，ILM 執行 Rollover。建立新的寫入索引。
4.  **Warm 階段**：舊索引被搬移至 Warm 節點（HDD）。執行 `Force Merge` 以減少 Segment 數量（對讀取效能至關重要）。
5.  **Cold 階段**：30 天後，移至 Cold 節點或掛載為可搜尋快照（Searchable Snapshot, S3）。
6.  **刪除**：90 天後，移除索引。

### 3.2 Impact on System Attributes (對系統屬性的影響)

*   **Cost Efficiency:** By moving 80% of data to cheaper hardware, you can reduce infrastructure costs by 40-60%.
    **成本效益**：將 80% 的資料移至較便宜的硬體，可降低 40-60% 的基礎設施成本。
*   **Write Throughput:** Isolating Hot nodes ensures that heavy historical searches on Warm nodes don't impact ingestion performance (indexing latency).
    **寫入吞吐量**：隔離 Hot 節點可確保在 Warm 節點上進行的大量歷史搜尋不會影響寫入效能（索引延遲）。
*   **Recoverability:** Smaller shards (managed by ILM) recover faster than massive daily indices.
    **可恢復性**：由 ILM 管理的較小 Shards 比巨大的每日索引恢復得更快。

---

## 4. Walkthrough: Capacity Planning & ILM Implementation (逐步示例：容量規劃與 ILM 實作)

### Scenario (情境)
You need to design a cluster for **1TB of raw logs per day**.
Retention: 7 days Hot, 30 days Warm, Delete after 30 days.
Replica: 1 (Primary + 1 Replica).

您需要為 **每日 1TB 的原始日誌** 設計一個集群。
保留策略：7 天 Hot，30 天 Warm，30 天後刪除。
副本策略：1（Primary + 1 Replica）。

### Step 1: Capacity Planning Math (容量規劃計算)

**Raw to Disk Multiplier:**
ElasticSearch adds overhead (inverted index, doc values, stored fields). Usually 1.1x to 1.3x of raw size. Let's use **1.2x**.
Plus `replica = 1`, total multiplier is **2.4x**.

**原始資料轉磁碟倍數**：
ElasticSearch 有額外開銷（倒排索引、Doc Values、Stored Fields）。通常是原始大小的 1.1 倍到 1.3 倍。我們使用 **1.2 倍**。
加上 `replica = 1`，總倍數為 **2.4 倍**。

**Hot Tier Requirements:**
*   Daily Disk: 1TB * 2.4 = 2.4TB.
*   Total Hot (7 days): 2.4TB * 7 = 16.8TB.
*   Overhead Buffer (15% for merging/watermark): 16.8TB / 0.85 ≈ **20TB**.
*   *Hardware:* If using 2TB SSDs, you need ~10 data nodes (or fewer with larger disks).

**Hot 層需求**：
*   每日磁碟：1TB * 2.4 = 2.4TB。
*   總 Hot（7 天）：2.4TB * 7 = 16.8TB。
*   緩衝區（15% 用於 Merging/Watermark）：16.8TB / 0.85 ≈ **20TB**。
*   *硬體*：若使用 2TB SSD，約需 10 個 Data Nodes（若磁碟更大則節點更少）。

**Warm Tier Requirements:**
*   Days in Warm: 30 - 7 = 23 days.
*   Total Warm: 2.4TB * 23 = 55.2TB.
*   Buffer: 55.2TB / 0.85 ≈ **65TB**.
*   *Hardware:* High density HDD nodes.

**Warm 層需求**：
*   Warm 天數：30 - 7 = 23 天。
*   總 Warm：2.4TB * 23 = 55.2TB。
*   緩衝區：55.2TB / 0.85 ≈ **65TB**。
*   *硬體*：高密度 HDD 節點。

### Step 2: Configure Node Attributes (配置節點屬性)

In `elasticsearch.yml`, tag your nodes:

在 `elasticsearch.yml` 中標記您的節點：

```yaml
# On Hot Nodes
node.roles: [ data_hot, master, ingest ]
node.attr.data: hot

# On Warm Nodes
node.roles: [ data_warm ]
node.attr.data: warm
```

### Step 3: Define ILM Policy (定義 ILM 策略)

This policy handles the transition. Note the `force_merge` in the warm phase—this is critical for freeing up space and improving read speed on static data.

此策略處理轉換。請注意 Warm 階段的 `force_merge`——這對於釋放空間和提升靜態資料的讀取速度至關重要。

```json
PUT _ilm/policy/logs_policy
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_size": "50gb",       // Key: Size-based rollover
            "max_age": "24h"          // Fallback: Time-based
          },
          "set_priority": {
            "priority": 100           // High priority for recovery
          }
        }
      },
      "warm": {
        "min_age": "7d",              // Move after 7 days
        "actions": {
          "allocate": {
            "require": {
              "data": "warm"          // Move to Warm nodes
            }
          },
          "forcemerge": {
            "max_num_segments": 1     // Optimize for read-only
          },
          "shrink": {
            "number_of_shards": 1     // Optional: Reduce shard count
          },
          "set_priority": {
            "priority": 50
          }
        }
      },
      "delete": {
        "min_age": "30d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
```

### Step 4: Create Index Template (建立索引樣板)

Link the policy to the indices.

將策略連結到索引。

```json
PUT _index_template/logs_template
{
  "index_patterns": ["logs-*"],
  "template": {
    "settings": {
      "number_of_shards": 2,             // Initial shards for Hot
      "number_of_replicas": 1,
      "index.lifecycle.name": "logs_policy",
      "index.lifecycle.rollover_alias": "logs-write"
    }
  }
}
```

### Step 5: Bootstrap the First Index (初始化第一個索引)

```json
PUT logs-000001
{
  "aliases": {
    "logs-write": {
      "is_write_index": true
    }
  }
}
```

---

## 5. Common Pitfalls & Anti-patterns (常見錯誤與反模式)

### 5.1 The "Daily Index" Trap (「每日索引」陷阱)
*   **Anti-pattern:** Creating indices named `logs-2023-10-01`, `logs-2023-10-02`.
*   **Why it's bad:** Data volume fluctuates. On Black Friday, `logs-2023-11-24` might be 500GB (huge shards), while a quiet Sunday is 10GB. This creates uneven load and performance unpredictability.
*   **Solution:** Use **Rollover API** (via ILM) based on `max_size`. Let ElasticSearch decide when to cut a new index, not the calendar.

*   **反模式**：建立名為 `logs-2023-10-01`、`logs-2023-10-02` 的索引。
*   **壞處**：資料量會波動。在黑色星期五，`logs-2023-11-24` 可能高達 500GB（巨大的 Shards），而平靜的週日只有 10GB。這會導致負載不均和效能不可預測。
*   **解法**：使用基於 `max_size` 的 **Rollover API**（透過 ILM）。讓 ElasticSearch 決定何時切分新索引，而不是日曆。

### 5.2 Ignoring Force Merge (忽略 Force Merge)
*   **Anti-pattern:** Moving indices to Warm nodes without force-merging them to 1 segment.
*   **Why it's bad:** Warm nodes usually have slower disks. Searching through 50 small segments on an HDD is significantly slower than searching 1 large segment. Also, deleted documents (tombstones) consume space until a merge happens.
*   **Solution:** Always include a `forcemerge` action in the Warm phase of ILM.

*   **反模式**：將索引移至 Warm 節點，卻未將其 Force Merge 為 1 個 Segment。
*   **壞處**：Warm 節點通常使用較慢的磁碟。在 HDD 上搜尋 50 個小 Segments 遠比搜尋 1 個大 Segment 慢。此外，已刪除的文件（墓碑機制）在 Merge 發生前仍會佔用空間。
*   **解法**：務必在 ILM 的 Warm 階段包含 `forcemerge` 動作。

### 5.3 Oversharding (過度切分 Shard)
*   **Anti-pattern:** A cluster with 3 data nodes holding 10,000 shards.
*   **Why it's bad:** Each shard has overhead in the Cluster State (kept in heap on the Master). Too many shards cause the Master node to become unresponsive and slow down cluster updates.
*   **Rule of Thumb:** Aim for fewer than 20 shards per GB of Heap on a node. (e.g., 30GB Heap -> Max 600 shards per node).

*   **反模式**：一個只有 3 個 Data Nodes 的集群卻持有 10,000 個 Shards。
*   **壞處**：每個 Shard 在 Cluster State（保存在 Master 的 Heap 中）都有 Overhead。過多的 Shards 會導致 Master 節點無回應，並拖慢集群更新速度。
*   **經驗法則**：目標是每 GB Heap 的 Shard 數量少於 20 個。（例如：30GB Heap -> 每個節點最多 600 個 Shards）。

---

## 6. Interview & Discussion Hooks (面試與實務問答切入點)

### Q1: How would you handle a sudden spike in log volume (3x normal load)?
**Focus:** Scalability and protection.
*   **Answer Key:**
    *   **Short term:** Ensure the ingestion layer (Kafka/Redis) buffers the load so ES isn't overwhelmed.
    *   **ES Config:** Check if `refresh_interval` can be increased (e.g., 30s) to reduce indexing overhead.
    *   **ILM:** The size-based rollover will trigger faster. This is good; it keeps shard sizes consistent.
    *   **Capacity:** If disk fills up, ES hits flood stage watermark (read-only). Need to add nodes or delete old data immediately.

### Q1: 你會如何處理日誌量突然暴增（3 倍正常負載）的情況？
**重點**：可擴充性與保護機制。
*   **回答要點**：
    *   **短期**：確保接收層（Kafka/Redis）能緩衝負載，避免 ES 被壓垮。
    *   **ES 設定**：檢查是否可增加 `refresh_interval`（例如 30 秒）以減少索引 Overhead。
    *   **ILM**：基於大小的 Rollover 會更快觸發。這是好事，能保持 Shard 大小一致。
    *   **容量**：若磁碟滿了，ES 會觸發 Flood Stage Watermark（唯讀）。需立即增加節點或刪除舊資料。

### Q2: Why separate Master-eligible nodes from Data nodes?
**Focus:** Stability.
*   **Answer Key:** In small clusters (<5 nodes), mixed roles are fine. In large clusters, Data nodes are under heavy GC pressure from queries/indexing. If a Data node acts as Master and stalls due to GC, the whole cluster becomes unstable (flapping master). Dedicated masters ensure cluster state stability regardless of data load.

### Q2: 為什麼要將 Master-eligible 節點與 Data 節點分開？
**重點**：穩定性。
*   **回答要點**：在小型集群（<5 節點）中，混合角色無妨。在大型集群中，Data 節點承受查詢/索引帶來的巨大 GC 壓力。若 Data 節點兼任 Master 且因 GC 而停頓，整個集群會變得不穩定（Master 頻繁切換）。專用 Master 可確保無論資料負載如何，Cluster State 都能保持穩定。

### Q3: Explain the trade-off of `number_of_shards`.
**Focus:** Performance tuning.
*   **Answer Key:**
    *   **More Shards:** Faster indexing (parallel write) and potentially faster search (parallel read), BUT higher resource overhead and slower recovery.
    *   **Fewer Shards:** Less overhead, better compression, BUT limits maximum throughput (cannot utilize all nodes if shards < nodes).

### Q3: 請解釋 `number_of_shards` 的權衡（Trade-off）。
**重點**：效能調校。
*   **回答要點**：
    *   **較多 Shards**：索引速度較快（平行寫入），搜尋可能較快（平行讀取），**但是**資源 Overhead 較高且恢復速度較慢。
    *   **較少 Shards**：Overhead 較低，壓縮效果較佳，**但是**限制了最大吞吐量（若 Shards 數量 < 節點數量，則無法利用所有節點）。

---

## 7. Summary & Next Steps (小結與後續延伸)

### Summary (小結)
1.  **Capacity Planning:** Always calculate raw size * replication * overhead (approx 1.2x).
2.  **Shard Sizing:** Aim for **10GB-50GB**. Avoid the "million tiny shards" problem.
3.  **ILM is Mandatory:** Use ILM to automate lifecycle. Prefer **size-based rollover** over time-based rollover for write indices.
4.  **Hot-Warm-Cold:** Separate hardware profiles to optimize cost. Use NVMe for Hot, HDD/SATA for Warm.
5.  **Force Merge:** Essential for Warm/Cold phases to improve read performance and reclaim space.

### Next Steps (後續延伸)
*   **Next Chapter:** Performance Tuning (Indexing & Search Latency). Now that the cluster is planned, how do we make queries fly?
*   **Action Item:** Audit your current production cluster. Check the average shard size (`GET _cat/shards?v&s=store:desc`). Are they in the 10-50GB range? If not, plan a reindex or adjust ILM policies.

### 後續延伸
*   **下一章**：效能調校（索引與搜尋延遲）。既然集群規劃好了，我們該如何讓查詢飛快？
*   **行動項目**：稽核您目前的生產環境集群。檢查平均 Shard 大小（`GET _cat/shards?v&s=store:desc`）。它們是否在 10-50GB 的範圍內？如果不是，請規劃 Reindex 或調整 ILM 策略。