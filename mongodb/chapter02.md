# Chapter 02: Advanced Schema Design Patterns
# 第 02 章：進階 Schema 設計模式

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

Unlike Relational Databases where normalization is the starting point, MongoDB schema design is driven primarily by **access patterns**. For a Senior Engineer, the challenge isn't just storing data, but structuring it to minimize I/O and maximize query performance under specific read/write ratios.
不同於關聯式資料庫以正規化（Normalization）為起點，MongoDB 的 Schema 設計主要由 **存取模式（Access Patterns）** 驅動。對於資深工程師而言，挑戰不僅在於儲存資料，而在於如何結構化資料以最小化 I/O，並在特定的讀寫比例下最大化查詢效能。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Decisively choose between Embedding and Referencing**: Evaluate trade-offs based on data cardinality, atomicity requirements, and the 16MB document limit.
    **果斷選擇 Embedding 或 Referencing**：根據資料基數（Cardinality）、原子性需求以及 16MB 文件限制來評估權衡。
2.  **Implement Advanced Patterns**: Apply the **Bucket Pattern** for time-series/IoT data, the **Attribute Pattern** for polymorphic product catalogs, and **Tree Patterns** for hierarchical structures.
    **實作進階模式**：針對時間序列/IoT 資料應用 **Bucket Pattern**，針對多型產品目錄應用 **Attribute Pattern**，以及針對階層結構應用 **Tree Patterns**。
3.  **Optimize for Workloads**: Refactor schemas to handle high-frequency writes or complex read aggregations efficiently.
    **針對負載優化**：重構 Schema 以有效處理高頻寫入或複雜的讀取聚合操作。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### The "Access Pattern First" Rule
### 「存取模式優先」法則

In SQL, you model the data to respect the entity relationships (3NF). In MongoDB, you model the data to respect the **application's queries**.
在 SQL 中，你根據實體關係來建立資料模型（第三正規化）。在 MongoDB 中，你根據 **應用程式的查詢方式** 來建立資料模型。

*   **Mental Model**: Think of your data layout like packing for a trip vs. organizing a library.
    *   **Embedding (Packing for a trip)**: You put your toothbrush, clothes, and charger in one suitcase. When you arrive (query), you grab the suitcase and have everything you need immediately.
    *   **Referencing (Library Catalog)**: Books are organized by category. To get a book and its author's biography, you look up the book, find the author ID, and then go to the biography section. It's cleaner but requires more "walking" (lookups).
*   **心智模型**：將你的資料佈局想像成「打包行李」與「圖書館歸檔」的對比。
    *   **Embedding（打包行李）**：你將牙刷、衣服和充電器放在同一個行李箱中。當你到達目的地（進行查詢）時，你拿起行李箱，立即就能獲得所需的一切。
    *   **Referencing（圖書館目錄）**：書籍按類別排列。要獲取一本書及其作者傳記，你需要先找到書，查看作者 ID，然後再去傳記區尋找。這樣更整潔，但需要更多的「走動」（Lookups）。

### Cardinality & The 16MB Cliff
### 基數（Cardinality）與 16MB 懸崖

*   **One-to-Few**: Embed. (e.g., Addresses for a User).
*   **One-to-Many**: Embed or Reference depending on "Many" size.
*   **One-to-Squillions**: Reference. (e.g., Logs for a Server).
*   **One-to-Few**：嵌入。（例如：使用者的地址）。
*   **One-to-Many**：視「Many」的大小決定嵌入或參照。
*   **One-to-Squillions（海量）**：參照。（例如：伺服器的 Log）。

The hard limit is the **BSON document size limit (16MB)**. If an array can grow unbounded, you *must* use referencing or the Bucket pattern.
硬性限制是 **BSON 文件大小限制（16MB）**。如果一個陣列可能會無限制增長，你 *必須* 使用參照或 Bucket 模式。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### Scenario 1: IoT / Time Series Data (Bucket Pattern)
### 場景 1：IoT / 時間序列資料（Bucket Pattern）

In a system monitoring millions of sensors, writing one document per reading is a naive approach that bloats the index size.
在監控數百萬個感測器的系統中，每一筆讀數寫入一份文件是一種天真的做法，這會導致索引大小膨脹。

*   **Design Impact**: Using the **Bucket Pattern** (grouping readings by hour/day into one document) reduces the number of documents and index entries significantly. This improves write throughput and compression ratios.
*   **設計影響**：使用 **Bucket Pattern**（將每小時/每天的讀數分組到一份文件中）可顯著減少文件數量與索引項目。這能提升寫入吞吐量與壓縮率。

### Scenario 2: E-commerce Catalog (Attribute Pattern)
### 場景 2：電子商務目錄（Attribute Pattern）

Products have different attributes (e.g., Laptops have CPU/RAM; Shirts have Size/Color). Creating sparse indexes on specific fields (`spec.cpu`, `spec.size`) is inefficient and hard to maintain.
產品具有不同的屬性（例如：筆電有 CPU/RAM；襯衫有尺寸/顏色）。在特定欄位（`spec.cpu`, `spec.size`）上建立稀疏索引（Sparse Indexes）既無效率又難以維護。

*   **Design Impact**: The **Attribute Pattern** moves these fields into an array of key-value pairs (`k: "cpu", v: "i7"`). You can then create a single compound index on the array, allowing efficient searching across disparate product types.
*   **設計影響**：**Attribute Pattern** 將這些欄位移入一個鍵值對陣列（`k: "cpu", v: "i7"`）。接著你可以在該陣列上建立單一的複合索引，從而實現跨不同產品類型的高效搜尋。

### Scenario 3: Threaded Comments (Tree Patterns)
### 場景 3：巢狀評論（Tree Patterns）

Displaying a Reddit-style comment thread requires reconstructing a hierarchy.
顯示 Reddit 風格的評論串需要重建階層結構。

*   **Design Impact**:
    *   **Parent Reference**: Good for updates, slow for retrieving a full subtree.
    *   **Materialized Path**: Stores the full path (e.g., `,root,comment1,comment2,`) in a string. Allows regex queries to fetch entire subtrees in one go.
*   **設計影響**：
    *   **Parent Reference**：適合更新，但讀取完整子樹較慢。
    *   **Materialized Path**：將完整路徑（例如 `,root,comment1,comment2,`）儲存為字串。允許透過 Regex 查詢一次抓取整個子樹。

---

## 4. Walkthrough: Optimizing IoT Sensor Data
## 4. 逐步示例：優化 IoT 感測器資料

### The Business Context
### 商業情境

We are building a weather monitoring system. Sensors report temperature and humidity every minute. We need to query historical data efficiently (e.g., "Average temperature for the last 24 hours").
我們正在建立一個天氣監控系統。感測器每分鐘回報溫度與濕度。我們需要高效地查詢歷史資料（例如：「過去 24 小時的平均溫度」）。

### Phase 1: Naive Approach (One Document Per Reading)
### 第一階段：天真做法（每一讀數一份文件）

```javascript
// Document structure
{
  "_id": ObjectId("..."),
  "sensor_id": 12345,
  "timestamp": ISODate("2023-10-27T10:00:00Z"),
  "temp": 22.5,
  "humidity": 60
}
```

*   **Analysis**:
    *   **Pros**: Simple to write.
    *   **Cons**: Huge number of documents (1 sensor = 1440 docs/day). Indexes on `sensor_id` + `timestamp` will become massive, consuming RAM and causing disk I/O on reads.
*   **分析**：
    *   **優點**：寫入簡單。
    *   **缺點**：文件數量龐大（1 個感測器 = 1440 份文件/天）。`sensor_id` + `timestamp` 的索引將變得非常巨大，消耗 RAM 並在讀取時導致磁碟 I/O。

### Phase 2: The Bucket Pattern (Optimized)
### 第二階段：Bucket Pattern（優化後）

We group readings by hour. This is a form of "Hybrid Embedding".
我們按小時將讀數分組。這是一種「混合嵌入（Hybrid Embedding）」的形式。

```javascript
// Document structure (One doc per sensor per hour)
{
  "_id": ObjectId("..."),
  "sensor_id": 12345,
  "start_date": ISODate("2023-10-27T10:00:00Z"),
  "end_date": ISODate("2023-10-27T11:00:00Z"),
  "count": 60,
  "sum_temp": 1350, // Pre-calculated for fast aggregation
  "readings": [
    { "ts": 10, "temp": 22.5, "hum": 60 }, // ts is minutes offset from start_date
    { "ts": 11, "temp": 22.6, "hum": 61 }
    // ... up to 60 entries
  ]
}
```

*   **Implementation Details**:
    *   **Upsert**: Use `updateOne` with `upsert: true`. Match on `sensor_id` and a "time bucket" (e.g., the hour).
    *   **$push**: Use `$push` to append to the `readings` array.
    *   **Pre-aggregation**: We can maintain `sum_temp` and `count` on write using `$inc`.
*   **實作細節**：
    *   **Upsert**：使用帶有 `upsert: true` 的 `updateOne`。比對 `sensor_id` 和「時間桶」（例如該小時）。
    *   **$push**：使用 `$push` 將資料追加到 `readings` 陣列。
    *   **預先聚合**：我們可以在寫入時使用 `$inc` 維護 `sum_temp` 和 `count`。

### Why this works
### 為何這行得通

1.  **Index Efficiency**: We reduced the index size by a factor of 60.
2.  **Locality**: All readings for an hour are in one disk block. Fetching one document gives you the whole hour's data.
3.  **Aggregation**: Calculating the average is faster because we pre-calculated the sum and count.
1.  **索引效率**：我們將索引大小縮減了 60 倍。
2.  **局部性（Locality）**：一小時內的所有讀數都在同一個磁碟區塊中。讀取一份文件即可獲得整小時的資料。
3.  **聚合**：計算平均值更快，因為我們預先計算了總和與計數。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 1. The "Mega-Array" (Unbounded Embedding)
### 1. 「巨型陣列」（無限制嵌入）

*   **Scenario**: Storing all user comments inside the User document or a Post document.
*   **Why it's bad**:
    *   You will hit the 16MB limit.
    *   Moving the document on disk (if it grows beyond allocated space) is expensive.
    *   Pagination becomes a nightmare (you have to fetch the whole array to slice it in application memory, or use complex projection).
*   **Fix**: Use **Referencing** or **Bucketing** (e.g., store 50 comments per bucket document).
*   **情境**：將所有使用者評論儲存在使用者文件或貼文文件中。
*   **為何不好**：
    *   你會觸發 16MB 限制。
    *   在磁碟上移動文件（如果增長超過分配空間）成本很高。
    *   分頁會變成惡夢（你必須取出整個陣列在應用程式記憶體中切割，或使用複雜的 Projection）。
*   **修正**：使用 **Referencing** 或 **Bucketing**（例如：每個 Bucket 文件儲存 50 則評論）。

### 2. Deeply Nested Objects
### 2. 過深巢狀物件

*   **Scenario**: `user.profile.settings.notifications.email.frequency`.
*   **Why it's bad**:
    *   Query syntax becomes verbose.
    *   Updates are complex (dot notation hell).
    *   Indexing specific sub-fields creates long index keys.
*   **Fix**: Flatten the structure where possible. Use dot notation only when logical grouping is strictly necessary.
*   **情境**：`user.profile.settings.notifications.email.frequency`。
*   **為何不好**：
    *   查詢語法變得冗長。
    *   更新變得複雜（點符號地獄）。
    *   索引特定子欄位會產生很長的索引鍵。
*   **修正**：盡可能扁平化結構。僅在嚴格需要邏輯分組時使用點符號。

### 3. Fear of Data Duplication
### 3. 害怕資料重複

*   **Scenario**: A Senior Engineer coming from SQL background refuses to store `user_name` in the `Order` document, insisting on joining `users` collection every time.
*   **Why it's bad**: MongoDB joins (`$lookup`) are expensive compared to SQL joins. They inhibit sharding performance.
*   **Fix**: **Extended Reference Pattern**. Embed frequently read, rarely changed fields (like `name`) in the referencing document. Accept that you might need a background job to update them if they change.
*   **情境**：一位 SQL 背景的資深工程師拒絕在 `Order` 文件中儲存 `user_name`，堅持每次都要去 `users` collection 進行關聯查詢。
*   **為何不好**：MongoDB 的關聯（`$lookup`）相較於 SQL JOIN 成本較高。它們會阻礙 Sharding 的效能。
*   **修正**：**Extended Reference Pattern**。在參照文件中嵌入頻繁讀取但鮮少變更的欄位（如 `name`）。接受如果這些欄位變更，可能需要背景作業來更新它們的事實。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: "How would you design a Product Catalog schema where different categories have completely different attributes?"
### Q1：「你會如何設計一個產品目錄 Schema，其中不同的類別擁有完全不同的屬性？」

*   **Key Points**:
    *   Discuss the **Attribute Pattern**.
    *   Explain why creating separate columns/fields for every possible attribute is bad (sparse indexes).
    *   Propose structure: `attributes: [ { k: "size", v: "L" }, { k: "material", v: "cotton" } ]`.
    *   Mention indexing `{ "attributes.k": 1, "attributes.v": 1 }`.
*   **關鍵要點**：
    *   討論 **Attribute Pattern**。
    *   解釋為何為每個可能的屬性建立單獨的欄位是不好的（稀疏索引）。
    *   提出結構建議：`attributes: [ { k: "size", v: "L" }, { k: "material", v: "cotton" } ]`。
    *   提及索引 `{ "attributes.k": 1, "attributes.v": 1 }`。

### Q2: "We have a write-heavy logging system. We are hitting IOPS limits. How can schema design help?"
### Q2：「我們有一個寫入繁重的日誌系統。我們正面臨 IOPS 瓶頸。Schema 設計能如何幫助？」

*   **Key Points**:
    *   Discuss **Bucket Pattern** to reduce the number of actual document writes (grouping logs).
    *   This reduces index updates (one index update per bucket vs. one per log).
    *   Discuss trade-offs: Real-time visibility (might need to wait to flush bucket) vs. Throughput.
*   **關鍵要點**：
    *   討論 **Bucket Pattern** 以減少實際文件寫入次數（將日誌分組）。
    *   這能減少索引更新（每個 Bucket 更新一次索引 vs. 每條日誌更新一次）。
    *   討論權衡：即時可見性（可能需要等待 Bucket 寫入）與吞吐量。

### Q3: "When should you DENORMALIZE data in MongoDB?"
### Q3：「在 MongoDB 中何時應該對資料進行反正規化（Denormalize）？」

*   **Key Points**:
    *   When the read/write ratio is high (Read-heavy).
    *   When data is read together but updated separately.
    *   When you want to avoid `$lookup` in critical paths.
    *   Example: Storing `author_name` in `comments` to display a thread without joining the `users` table.
*   **關鍵要點**：
    *   當讀寫比很高時（讀取繁重）。
    *   當資料被一起讀取但分開更新時。
    *   當你想在關鍵路徑中避免 `$lookup` 時。
    *   範例：在 `comments` 中儲存 `author_name`，以便在不關聯 `users` 表的情況下顯示評論串。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Key Takeaways
### 關鍵記憶點

1.  **Schema follows Queries**: Design based on how data is read, not just how it relates.
    **Schema 跟隨查詢**：根據資料讀取方式設計，而非僅根據關聯性。
2.  **Embed by Default, Reference when Necessary**: Embed for performance (locality), Reference for scalability (unbounded growth) or data integrity (many-to-many).
    **預設嵌入，必要時參照**：為了效能（局部性）選擇嵌入，為了擴充性（無限制增長）或資料完整性（多對多）選擇參照。
3.  **Bucket Pattern**: Essential for Time Series and IoT to save index space and IOPS.
    **Bucket Pattern**：對於時間序列和 IoT 至關重要，可節省索引空間與 IOPS。
4.  **Attribute Pattern**: Solves the "Polymorphic Data" problem efficiently with one compound index.
    **Attribute Pattern**：利用單一複合索引高效解決「多型資料」問題。
5.  **Avoid Unbounded Arrays**: Always consider the 16MB limit.
    **避免無限制陣列**：永遠要考慮 16MB 的限制。

### Next Steps
### 後續延伸

*   **Chapter 03**: Now that you have a schema, how do you make it fast? We will dive into **Advanced Indexing Strategies** (Compound, Partial, TTL, and Text Indexes).
*   **第 03 章**：既然你有了 Schema，如何讓它變快？我們將深入探討 **進階索引策略**（複合、部分、TTL 與全文索引）。