# 1. 前言與學習目標 (Introduction & Learning Objectives)

在關聯式資料庫（RDBMS）中，正規化（Normalization）是黃金準則；但在 ElasticSearch（ES）的世界裡，為了極致的讀取效能，我們往往需要擁抱「反正規化（Denormalization）」。對於資深工程師而言，挑戰不在於如何建立索引，而在於如何根據 Access Patterns（存取模式）設計出能隨著資料量擴展的 Schema。

In Relational Database Management Systems (RDBMS), Normalization is the golden rule; however, in the realm of ElasticSearch (ES), to achieve extreme read performance, we often must embrace "Denormalization." For Senior Engineers, the challenge lies not in how to create an index, but in how to design a schema based on Access Patterns that scales with data volume.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精準選擇資料建模策略**：在 Object、Nested、Parent-Child 與 Denormalization 之間，根據讀寫比（Read/Write Ratio）與資料更新頻率做出正確的架構決策。
    **Select data modeling strategies with precision**: Make the correct architectural decisions between Object, Nested, Parent-Child, and Denormalization based on Read/Write Ratios and data update frequency.
2.  **防範 Mapping Explosion**：理解 Lucene 底層限制，並運用 `flattened` 資料型態與動態模板（Dynamic Templates）來防止索引崩潰。
    **Prevent Mapping Explosion**: Understand Lucene's underlying limitations and utilize the `flattened` data type and Dynamic Templates to prevent index crashes.
3.  **優化儲存與寫入效能**：透過合理的 Mapping 設定（如 `doc_values`, `norms`, `index`）來平衡儲存成本與查詢速度。
    **Optimize storage and write performance**: Balance storage costs and query speed through rational Mapping settings (e.g., `doc_values`, `norms`, `index`).

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 倒排索引與不可變性 (Inverted Index & Immutability)

ES 的核心是 Lucene，其底層檔案（Segment）是不可變的（Immutable）。這意味著「更新」一個文件實際上是「標記刪除舊文件並寫入新文件」。因此，頻繁更新單一欄位（如計數器）在 ES 中是非常昂貴的操作。

The core of ES is Lucene, and its underlying files (Segments) are immutable. This means that "updating" a document is effectively "marking the old document as deleted and writing a new one." Consequently, frequently updating a single field (like a counter) is a very expensive operation in ES.

**心智模型 (Mental Model)**：
將 RDBMS 想像成一個「活頁筆記本」，你可以隨時擦掉某一行重寫。將 ES 想像成一本「印刷好的百科全書」，如果你要修改一個字，你必須重新印製整頁（甚至整章）並替換掉舊的那頁。

**Mental Model**:
Think of an RDBMS as a "loose-leaf notebook" where you can erase and rewrite a line at any time. Think of ES as a "printed encyclopedia"; if you need to change a word, you have to reprint the entire page (or even the chapter) and replace the old one.

## 2.2 關聯性處理光譜 (The Spectrum of Handling Relationships)

在 ES 中處理關聯資料（Relationships）有四種主要方式，它們在效能與靈活性上呈現光譜分佈：

There are four main ways to handle relationships in ES, distributed across a spectrum of performance versus flexibility:

1.  **Inner Object (Default)**:
    *   **機制 (Mechanism)**: JSON 物件被攤平（Flattened）。`user.first` 和 `user.last` 變成獨立的陣列，失去了彼此的關聯。
    *   **適用 (Use Case)**: 一對一關聯，或不需要針對物件內部多個欄位進行「同時滿足」的查詢。
2.  **Nested**:
    *   **機制 (Mechanism)**: 每個子物件在內部被儲存為獨立的隱藏文件（Hidden Document），但在查詢時看起來像一個文件。
    *   **適用 (Use Case)**: 一對多關聯，且需要精確查詢子物件屬性（例如：`color: red` AND `size: L` 必須來自同一個 SKU）。
3.  **Parent-Child (Join field)**:
    *   **機制 (Mechanism)**: 類似 SQL Join。父文件與子文件是完全獨立的文件，但在同一個 Shard 上，透過 Routing 綁定。
    *   **適用 (Use Case)**: 一對多關聯，且子文件更新非常頻繁，或者父子寫入時間點完全不同步。
4.  **Denormalization**:
    *   **機制 (Mechanism)**: 資料冗餘。將需要的關聯資料直接複製到主文件中。
    *   **適用 (Use Case)**: 讀多寫少，追求極致查詢效能（Big Tech 最常用的模式）。

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 系統架構中的角色 (Role in System Architecture)

在大型分散式系統中，ES 通常不作為 Source of Truth（SoT）。SoT 往往是 DynamoDB、PostgreSQL 或 Cassandra。ES 扮演的是 **Secondary Index（二級索引）** 或 **Search Engine** 的角色。

In large-scale distributed systems, ES rarely serves as the Source of Truth (SoT). The SoT is usually DynamoDB, PostgreSQL, or Cassandra. ES plays the role of a **Secondary Index** or **Search Engine**.

*   **Data Flow**: App -> DB (SoT) -> CDC (Change Data Capture) / Event Bus (Kafka) -> Consumer -> ElasticSearch.
*   **Implication**: 資料建模時，我們不需要過度擔心正規化帶來的寫入複雜度，因為這是由非同步的 Pipeline 處理的。我們應專注於 **Read-Side Optimization**。

## 3.2 Mapping Explosion 的威脅 (The Threat of Mapping Explosion)

在 Log 分析或 SaaS 平台（允許使用者自定義欄位）場景中，若未加限制，Mapping 中的欄位數量會爆炸性增長。

In Log analytics or SaaS platform scenarios (allowing user-defined fields), without restrictions, the number of fields in the Mapping can grow explosively.

*   **後果 (Consequence)**: Cluster State 變得巨大，Master node 負載過重，導致整個 Cluster 不穩定甚至 Crash。
*   **設計視角 (Design View)**: 資深工程師必須在 Schema 設計階段就預見此風險，設定 `index.mapping.total_fields.limit` 並使用 `flattened` 類型。

---

# 4. 逐步示例 (Walkthrough / Example)

## 場景：電商訂單系統 (Scenario: E-commerce Order System)

我們需要索引訂單（Order），每個訂單包含多個商品（Products）。
需求：找出「同時購買了紅色（Color: Red）且尺寸為 L（Size: L）商品」的訂單。

We need to index Orders, where each Order contains multiple Products.
Requirement: Find orders that contain a product that is "BOTH Color: Red AND Size: L".

### 4.1 嘗試 1：Naive Object Mapping (失敗案例)
### 4.1 Attempt 1: Naive Object Mapping (Failure Case)

```json
// Document
{
  "order_id": "101",
  "products": [
    { "name": "T-Shirt", "color": "Red", "size": "S" },
    { "name": "Jeans", "color": "Blue", "size": "L" }
  ]
}
```

**Lucene 內部的儲存方式 (How Lucene stores it internally):**
```
order_id: ["101"]
products.color: ["Red", "Blue"]
products.size: ["S", "L"]
```

**查詢問題 (The Query Problem):**
如果你查詢 `products.color: "Red" AND products.size: "L"`，這個訂單會被匹配出來！因為它確實有 Red，也確實有 L。但這不是我們想要的（Red 是 S 號，L 是 Blue 的）。這就是 **Cross-object matching** 問題。

If you query `products.color: "Red" AND products.size: "L"`, this order will match! Because it does have "Red" and it does have "L". But this is not what we want (Red is S, L is Blue). This is the **Cross-object matching** problem.

### 4.2 嘗試 2：Nested Type (正確解法之一)
### 4.2 Attempt 2: Nested Type (One Correct Solution)

使用 `nested` 類型可以保持物件邊界。

Using the `nested` type preserves object boundaries.

```json
PUT /orders
{
  "mappings": {
    "properties": {
      "order_id": { "type": "keyword" },
      "products": { 
        "type": "nested",  // Key change
        "properties": {
          "name": { "type": "text" },
          "color": { "type": "keyword" },
          "size": { "type": "keyword" }
        }
      }
    }
  }
}
```

**查詢 (Query):**

```json
GET /orders/_search
{
  "query": {
    "nested": {
      "path": "products",
      "query": {
        "bool": {
          "must": [
            { "term": { "products.color": "Red" } },
            { "term": { "products.size": "L" } }
          ]
        }
      }
    }
  }
}
```

**Trade-off**:
*   **Pros**: 查詢精確。
*   **Cons**: 更新成本高。若訂單有 100 個商品，修改其中 1 個商品的價格，ES 必須重新索引父文件 + 所有 100 個子文件（共 101 個文件）。

### 4.3 嘗試 3：Parent-Child (Join) (特定場景解法)
### 4.3 Attempt 3: Parent-Child (Join) (Specific Scenario Solution)

如果商品資訊更新極度頻繁（例如庫存、即時價格），而訂單本身不變。

If product information updates extremely frequently (e.g., inventory, real-time price), while the order itself remains static.

```json
PUT /order_system
{
  "mappings": {
    "properties": {
      "relationship_field": {
        "type": "join",
        "relations": {
          "order": "product"
        }
      }
    }
  }
}
```

**寫入時 (Indexing):**
必須確保父子文件在同一個 Shard。
Must ensure parent and child documents are on the same Shard.

```bash
# Index Parent
PUT /order_system/_doc/1
{ "order_id": "1", "relationship_field": "order" }

# Index Child (Must specify routing!)
PUT /order_system/_doc/p1?routing=1
{ "name": "T-Shirt", "relationship_field": { "name": "product", "parent": "1" } }
```

**Trade-off**:
*   **Pros**: 父子完全解耦，更新子文件不影響父文件。
*   **Cons**: 查詢效能最差（Query-time join），記憶體消耗大。

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 依賴預設的動態 Mapping (Relying on Default Dynamic Mapping)

**錯誤描述 (Error)**: 直接塞 JSON 進 ES，讓 ES 自動猜測型別。
**後果 (Consequence)**:
1.  字串欄位會被同時存成 `text` (for full-text search) 和 `keyword` (for aggregation)。這浪費了大量磁碟空間與記憶體。
2.  日期或數字可能被誤判。

**最佳實踐 (Best Practice)**:
永遠顯式定義 Mapping (Explicit Mapping)。對於字串，明確決定是 `keyword` 還是 `text`。若不需要索引（只做展示），設定 `index: false`。

Always define Mapping explicitly. For strings, decide clearly between `keyword` and `text`. If indexing is not needed (display only), set `index: false`.

## 5.2 Mapping Explosion (欄位爆炸)

**錯誤描述 (Error)**: 允許使用者輸入任意 Key-Value 並存入頂層索引。例如 `metadata.user_custom_field_1`, `metadata.user_custom_field_2`...
**後果 (Consequence)**: 每個新的 Key 都會更新 Cluster State。當欄位超過 1000 (預設限制) 時，寫入會失敗；即使未超過，效能也會顯著下降。

**最佳實踐 (Best Practice)**:
使用 `flattened` 資料型態處理不可預知的結構化資料。

Use the `flattened` data type for unpredictable structured data.

```json
"metadata": {
  "type": "flattened"
}
```
這會將整個 JSON 物件視為單一欄位處理，允許搜尋但不會為每個 Key 建立獨立的倒排索引。
This treats the entire JSON object as a single field, allowing search but preventing the creation of separate inverted indexes for each key.

## 5.3 濫用 Nested Objects (Overusing Nested Objects)

**錯誤描述 (Error)**: 在一個文件中包含數千個 Nested objects。
**後果 (Consequence)**: 查詢 Nested 欄位時容易發生 Heap Memory 溢出（因為 Lucene 需要載入所有相關的隱藏文件來做 Join）。

**最佳實踐 (Best Practice)**:
如果子項目數量龐大，考慮將其拆分為獨立的索引（Denormalization），或使用 Parent-Child（如果更新頻繁），或者重新思考業務模型。

If the number of child items is huge, consider splitting them into a separate index (Denormalization), using Parent-Child (if updates are frequent), or rethinking the business model.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 在什麼情況下你會選擇 Denormalization 而不是 Nested 或 Parent-Child？
## Q1: When would you choose Denormalization over Nested or Parent-Child?

*   **高分回答要點 (Key Points for High Score)**:
    *   **讀寫權衡 (Read/Write Trade-off)**: 強調 ES 是為讀取優化的。如果資料是「寫一次，讀多次」（如歷史訂單），Denormalization 是首選，因為它避免了 Query-time join 的開銷。
    *   **空間換時間 (Space vs. Time)**: 承認資料冗餘會增加儲存成本，但在 Storage 便宜、Compute 昂貴的雲端環境下，這是合理的交換。
    *   **複雜度轉移 (Complexity Shift)**: Denormalization 將複雜度從查詢端（ES）轉移到了寫入端（Pipeline/Application），這通常更容易控制。

## Q2: 如何在 Production 環境中安全地修改 Mapping？
## Q2: How do you safely modify Mapping in a Production environment?

*   **高分回答要點 (Key Points for High Score)**:
    *   **不可變性 (Immutability)**: 首先指出 Mapping 中已存在的欄位型別是不能修改的（除了少數例外如 `ignore_above`）。
    *   **Reindex API**: 標準做法是建立一個新的 Index（v2），使用 `_reindex` API 將資料從 v1 搬到 v2。
    *   **Alias (別名)**: 這是關鍵。App 應該永遠只連線到 Alias。切換時，原子性地（Atomically）將 Alias 從 v1 指向 v2，實現 **Zero Downtime** 遷移。

## Q3: 你的 ES Cluster 出現了 "Mapping explosion" 導致 Master node 響應緩慢，你會如何排查與解決？
## Q3: Your ES Cluster is suffering from "Mapping explosion" causing slow Master node response. How do you troubleshoot and fix it?

*   **高分回答要點 (Key Points for High Score)**:
    *   **排查 (Troubleshoot)**: 檢查 `GET /_cluster/state` 或使用 Kibana 查看 Index Mapping，找出欄位數異常的 Index。
    *   **止血 (Mitigate)**: 暫時調大 `index.mapping.total_fields.limit`（治標不治本，僅為了恢復服務）。
    *   **根治 (Fix)**: 
        1. 識別動態欄位來源（通常是 Log 中的 JSON payload 或 User Input）。
        2. 修改 Mapping，將該部分欄位改為 `flattened` 類型或 `enabled: false`。
        3. 執行 Reindex 清理舊的 Mapping 垃圾。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 本章記憶錨點 (Key Takeaways)

1.  **ES != RDBMS**: 放棄正規化思維。為了讀取效能，資料冗餘（Denormalization）通常是最佳解。
2.  **Nested vs. Object**: 需要精確查詢陣列內物件屬性的組合（Array of Objects）時，必須用 `nested`，否則會遇到 Cross-object matching 問題。
3.  **Parent-Child**: 僅在子文件更新極度頻繁且父文件巨大的特殊場景使用；代價是查詢效能低落。
4.  **Mapping 是合約**: 永遠顯式定義 Mapping。不要依賴動態探測。
5.  **Flattened 救命**: 對於不可控的 JSON 結構，使用 `flattened` 類型防止 Mapping Explosion。
6.  **Alias 是標配**: 所有的索引設計都應配合 Alias 使用，以支援未來的 Reindex 與 Schema 變更。

## 後續延伸 (Next Steps)

*   **Next Chapter**: 掌握了資料建模後，下一步是 **Chapter 04: 查詢效能優化與 DSL 深度解析 (Query Optimization & Deep DSL)**。我們將探討如何編寫高效的 Bool Query、Filter Context 的快取機制以及 Function Score 的應用。
*   **Action Item**: 檢查你目前專案中的 ES Mapping，找出是否有 `text` 欄位未被使用（浪費空間），或者是否有潛在的 Mapping Explosion 風險。