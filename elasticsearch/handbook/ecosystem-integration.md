# 生態系整合：與 RDBMS 及 Kafka 的協作 / Ecosystem Integration: Syncing with RDBMS & Kafka

## Mental model｜心智模型

在大多數的企業級架構中，Elasticsearch (ES) 很少作為 **Source of Truth (SoT, 真實資料源)** 存在。它通常扮演 **Derived Data System (衍生資料系統)** 的角色，目的是為了提供 RDBMS（如 MySQL, PostgreSQL）無法做到的全文搜尋或高效聚合能力。

建立正確的心智模型至關重要：

1.  **ES 是「投影 (Projection)」而非「原始檔」**：
    想像 RDBMS 是圖書館的「藏書庫」（實體書，權威資料），而 ES 是「卡片目錄系統」（索引，快速查找）。你永遠不應該只修改卡片目錄而不修改藏書。資料流向應永遠是單向的：`SoT -> Integration Layer -> Elasticsearch`。

2.  **最終一致性 (Eventual Consistency) 是常態**：
    除非你願意犧牲巨大的寫入效能與可用性來實作分散式交易 (Distributed Transactions)，否則你必須接受「寫入 RDBMS」與「在 ES 搜尋到」之間存在時間差 (Lag)。你的架構目標是讓這個 Lag 可控且可監控，而不是消滅它。

3.  **冪等性 (Idempotency) 是救命稻草**：
    在分散式系統中，訊息可能會重複發送 (At-least-once delivery)。ES 的寫入操作必須設計為冪等的。最簡單的做法是：**強制讓 ES 的 `_id` 等於 RDBMS 的 Primary Key**。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 同步策略選擇矩陣 (Synchronization Strategy Matrix)

在實戰中，主要有三種同步模式，請根據業務需求選擇：

| 模式 | 工具範例 | 延遲 (Latency) | 複雜度 | 適用場景 | 關鍵缺點 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **應用層雙寫 (Dual Write)** | App Code | 低 (ms 級) | 低 | 原型開發、非關鍵業務 | 資料易不一致 (Drift)，需額外修復機制 |
| **批次輪詢 (Batch Polling)** | Logstash (JDBC), Custom Script | 高 (分鐘級) | 中 | 報表、對即時性要求不高的搜尋 | 難以處理「物理刪除 (Hard Delete)」，對 DB 有壓力 |
| **變更資料擷取 (CDC)** | Debezium + Kafka | 低 (秒/亞秒級) | 高 | 核心搜尋業務、高吞吐量 | 架構維運成本高 |

### 2. The Gold Standard: CDC Pipeline (Debezium + Kafka)

這是目前業界處理大規模資料同步的標準架構。

-   **流程**：`RDBMS (Binlog/WAL) -> Debezium -> Kafka Topic -> Logstash/Kafka Connect -> Elasticsearch`
-   **優勢**：
    -   **解耦 (Decoupling)**：搜尋系統掛掉不會影響主交易系統。
    -   **完整性**：CDC 透過資料庫日誌 (Log) 抓取變更，不會漏掉任何一次 Update 或 Delete。
    -   **削峰填谷**：Kafka 作為緩衝，防止流量暴衝打掛 ES。

### 3. Logstash JDBC Polling 的最佳實踐

如果你不想維護 Kafka，選擇使用 Logstash 定期 Query DB，請遵守以下原則：
-   **使用 `sql_last_value`**：利用遞增 ID 或 `updated_at` 時間戳記來追蹤進度。
-   **處理刪除的技巧**：JDBC Input 無法感知物理刪除。
    -   *解法 A*：使用「軟刪除 (Soft Delete)」，即 `is_deleted = 1`，Logstash 仍能抓到更新並同步至 ES（隨後透過 ILM 或 Query 濾除）。
    -   *解法 B*：定期執行「全量同步」或「ID 比對腳本」來清理 ES 中多餘的資料。

### 4. 處理關聯資料 (Handling Relationships)

RDBMS 是正規化的 (Normalized)，ES 是反正規化的 (Denormalized)。
-   **Join at Index Time**：在寫入 ES 前（如在 Logstash filter 或 Kafka Streams 中）將多張 Table 的資料組裝成一個寬表 (Wide Document)。這是讀取效能最好的做法。
-   **Nested / Join Field**：除非必要，盡量避免在 ES 使用 Nested 或 Parent-Child，這會嚴重影響效能與維護性。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Dual Write" Trap (雙寫陷阱)
最常見的錯誤是在 Application Code 裡這樣寫：
```python
# Anti-pattern
def save_user(user):
    db.save(user)       # 1. 寫入 DB
    es.index(user)      # 2. 寫入 ES (如果這裡失敗了怎麼辦？)
```
**後果**：如果步驟 2 失敗（網路超時、ES 滿載），或者步驟 1 回滾但步驟 2 已經成功，你的資料庫與搜尋引擎就會永久不一致。
**修正**：如果必須雙寫，請務必搭配一個背景的 **Reconciliation Job (對帳/修復腳本)** 定期比對雙邊資料。

### 2. 忽視順序性 (Ignoring Ordering)
在 CDC 架構中，同一筆資料的 `Create -> Update -> Delete` 順序至關重要。
**踩雷點**：如果 Kafka Topic 沒有根據 Primary Key 設定 Partition Key，同一筆資料的變更可能會散落在不同 Partition，導致消費者亂序處理（先收到 Delete 再收到 Update）。
**修正**：確保 Kafka Producer 使用資料的主鍵 (ID) 作為 Partition Key。

### 3. 濫用 ES 作為主要資料庫
**踩雷點**：因為 ES 存取方便，開發者開始直接把非搜尋用的資料（如 User Session、交易細節）只存在 ES，而不存 RDBMS。
**後果**：ES 在極端情況下（Split Brain, Shard Corruption）可能會遺失資料，且其交易保證 (Transaction Guarantee) 遠不如 RDBMS。

### 4. Mapping 爆炸 (Mapping Explosion)
**踩雷點**：直接將 RDBMS 的 JSON 欄位不加過濾地倒進 ES，且開啟 Dynamic Mapping。
**後果**：髒資料導致 ES Mapping 欄位數激增，引發 Cluster Instability。
**修正**：設定 `dynamic: false` 或 `strict`，只索引明確定義的欄位。

---

## Checklists & workflows｜檢查清單與流程

### Decision Workflow: 選擇同步方案

1.  **資料量與頻率？**
    -   低頻、少量 -> **Logstash JDBC / App Dual Write**
    -   高頻、海量 -> **Kafka + CDC**
2.  **即時性要求？**
    -   T+1 (隔天) -> **Batch Dump**
    -   分鐘級 -> **Logstash Schedule**
    -   秒級 -> **CDC (Debezium)**
3.  **是否需要處理物理刪除？**
    -   是 -> **CDC** 或 **App Dual Write (with delete logic)**
    -   否 (Soft Delete only) -> **Logstash JDBC** 亦可

### Implementation Checklist (實作檢核表)

-   [ ] **ID 對應**：ES 的 `_id` 是否已設定為 DB 的 Primary Key？（確保冪等性）
-   [ ] **版本控制**：是否考慮使用 `external` versioning (利用 DB 的 `updated_at` 或 version number) 防止舊資料覆蓋新資料？
-   [ ] **刪除策略**：我是否已定義當 DB 資料刪除時，ES 該如何反應？(Delete document vs. Update status)
-   [ ] **錯誤處理 (DLQ)**：當同步失敗（如 Mapping 錯誤）時，是否有 Dead Letter Queue 儲存失敗訊息，而不是直接卡死 Pipeline？
-   [ ] **Mapping 嚴格度**：是否已關閉不必要的 Dynamic Mapping？
-   [ ] **重做索引 (Reindexing)**：當 Mapping 需要變更時，是否有「零停機」的 Reindex 流程（如使用 Alias 切換）？
-   [ ] **監控**：是否監控了同步延遲 (Lag)？(例如：比較 DB 最新寫入時間與 ES 最新資料時間)。

---

## Real-world examples｜實戰案例

### 案例：電商商品搜尋 (E-commerce Product Search)

**情境**：
商品資料分散在 `products` (基本資訊), `inventory` (庫存), `categories` (分類) 三張表中。需要提供依庫存、分類篩選的即時搜尋。

**架構設計 (CDC Pattern)**：

1.  **Source**: MySQL (開啟 Binlog)。
2.  **Ingest**: Debezium Connector 監聽這三張表的變更。
3.  **Buffer**: Kafka Topics (`db.products`, `db.inventory`, `db.categories`)。
4.  **Transformation (The Tricky Part)**:
    -   因為資料分散，單純將 Kafka 倒入 ES 會導致資料破碎。
    -   **解法 1 (KStream)**：使用 Kafka Streams 或 KSQL 將三個 Topic 進行 `Join`，生成一個完整的 `ProductComposite` 物件。
    -   **解法 2 (Enrichment)**：Logstash 收到 `inventory` 變更時，反查 DB 撈取 `product` 資訊（需注意 DB 壓力）。
    -   **解法 3 (Parent-Child)**：ES 中使用 Join type，但效能較差，通常不推薦用於高流量電商。
    -   *推薦選擇解法 1 或在應用層組裝後發送事件。*
5.  **Sink**: Logstash / Kafka Connect 將組裝好的 JSON 寫入 ES。

**Pseudo-code (Logstash Pipeline for Simple Table):**

```ruby
input {
  jdbc {
    jdbc_driver_library => "mysql-connector-java.jar"
    jdbc_driver_class => "com.mysql.jdbc.Driver"
    jdbc_connection_string => "jdbc:mysql://localhost:3306/shop"
    jdbc_user => "user"
    # 使用 sql_last_value 追蹤進度
    statement => "SELECT * FROM products WHERE updated_at > :sql_last_value"
    use_column_value => true
    tracking_column => "updated_at"
    tracking_column_type => "timestamp"
    schedule => "* * * * *" # 每分鐘執行
  }
}

filter {
  # 簡單的資料轉換
  mutate {
    remove_field => ["@version", "@timestamp"]
    rename => { "product_id" => "[@metadata][id]" } # 準備用作 _id
  }
}

output {
  elasticsearch {
    hosts => ["http://es-node:9200"]
    index => "products-v1"
    # 關鍵：使用 DB ID 作為 ES Document ID
    document_id => "%{[@metadata][id]}"
    doc_as_upsert => true
  }
}
```

**故障排除場景**：
某天發現搜尋結果中，某商品的價格與詳細頁面不一致。
1.  **檢查 Lag**：Kafka Consumer Group 是否有積壓 (Lag)？
2.  **檢查 DLQ**：是否有因為 Mapping 衝突（例如價格欄位送來了字串）導致寫入失敗？
3.  **緊急修復**：手動觸發該商品的 Update 事件，或使用 `_update` API 強制覆蓋 ES 資料。