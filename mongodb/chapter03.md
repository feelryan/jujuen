# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，MongoDB 的索引不僅僅是 `ensureIndex` 或 `createIndex` 那麼簡單。在千萬級甚至億級資料量的系統中，錯誤的索引策略會導致 CPU 飆升、磁碟 I/O 飽和，甚至引發整個 Cluster 的連鎖崩潰。本章旨在從底層原理出發，建立正確的索引設計思維。

For senior engineers, MongoDB indexing is far more than just running `ensureIndex` or `createIndex`. In systems with tens or hundreds of millions of documents, a flawed indexing strategy can cause CPU spikes, saturate disk I/O, and even trigger a cascading failure of the entire cluster. This chapter aims to build a robust indexing mindset based on underlying principles.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精通 ESR 法則**：深刻理解 Equality（精確匹配）、Sort（排序）與 Range（範圍查詢）在 B-Tree 索引中的優先順序與物理意義。
    **Master the ESR Rule**: Deeply understand the priority and physical implications of Equality, Sort, and Range within B-Tree indexes.
2.  **解讀執行計畫 (Explain Plans)**：能透過 `executionStats` 快速識別 `COLLSCAN`、記憶體排序 (In-memory Sort) 與索引覆蓋 (Covered Queries) 的差異。
    **Interpret Explain Plans**: Quickly identify `COLLSCAN`, In-memory Sort, and Covered Queries using `executionStats`.
3.  **運用進階索引類型**：在適當場景使用 Partial Indexes (部分索引) 與 TTL Indexes 來優化儲存成本與資料生命週期。
    **Apply Advanced Index Types**: Use Partial Indexes and TTL Indexes in appropriate scenarios to optimize storage costs and data lifecycles.
4.  **權衡讀寫效能**：在系統設計面試或實務中，能清晰闡述索引對 Write Throughput 的影響及應對策略。
    **Balance Read/Write Performance**: Clearly articulate the impact of indexes on Write Throughput and mitigation strategies during system design interviews or practice.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 B-Tree 遍歷與 ESR 法則 (B-Tree Traversal & The ESR Rule)

MongoDB 的預設儲存引擎 WiredTiger 使用 B-Tree 結構。理解索引效能的關鍵，在於想像資料庫如何遍歷這棵樹。**ESR 法則**是設計複合索引 (Compound Index) 的黃金準則：

MongoDB's default storage engine, WiredTiger, uses a B-Tree structure. The key to understanding index performance lies in visualizing how the database traverses this tree. The **ESR Rule** is the golden standard for designing Compound Indexes:

1.  **E (Equality) - 精確匹配**：
    應放在索引的最左側。這能以最低成本過濾掉絕大多數不相關的節點，縮小搜尋範圍。
    **E (Equality)**: Should be placed at the far left of the index. This filters out the vast majority of irrelevant nodes at the lowest cost, narrowing the search scope.
2.  **S (Sort) - 排序**：
    應緊接在 Equality 之後。如果索引順序與查詢要求的排序一致，MongoDB 可以直接依序讀取索引節點，而無需將結果載入記憶體進行昂貴的排序運算 (Blocking Sort)。
    **S (Sort)**: Should follow immediately after Equality. If the index order matches the query's sort order, MongoDB can scan index nodes sequentially without loading results into memory for an expensive Blocking Sort.
3.  **R (Range) - 範圍查詢**：
    應放在索引的最後。一旦使用了範圍查詢（如 `$gt`, `$lt`），索引在該欄位之後的順序就無法保證對後續欄位有效，因此範圍欄位後的索引欄位通常無法用於排序或進一步的高效過濾。
    **R (Range)**: Should be placed at the end. Once a range query (e.g., `$gt`, `$lt`) is used, the index order for subsequent fields is no longer guaranteed to be contiguous, rendering them ineffective for sorting or further efficient filtering.

## 2.2 索引覆蓋 (Covered Queries)

這是效能優化的極致狀態。當一個查詢的所有回傳欄位（Projection）與查詢條件都包含在同一個索引中時，MongoDB **完全不需要讀取實際的文檔 (Document)**，僅從 RAM 中的索引頁就能回傳結果。

This is the ultimate state of performance optimization. When all returned fields (Projection) and query conditions are contained within a single index, MongoDB **does not need to read the actual document**, returning results solely from index pages in RAM.

> **Mental Model**: 想像你在圖書館找書。
> *   **一般查詢**：查目錄卡（Index），找到書的位置，走到書架拿書（Fetch Document），翻開書找內容。
> *   **索引覆蓋**：你要找的資訊（例如書名與出版年份）直接寫在目錄卡上。你根本不用走到書架去拿書。
>
> **Mental Model**: Imagine finding a book in a library.
> *   **Normal Query**: Check the catalog card (Index), find the location, walk to the shelf to get the book (Fetch Document), and open it to find content.
> *   **Covered Query**: The information you need (e.g., Title and Year) is written directly on the catalog card. You don't need to walk to the shelf at all.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 寫入放大與索引維護成本 (Write Amplification & Maintenance Cost)

在系統設計中，我們常說 "Read-heavy" vs "Write-heavy"。對於 MongoDB：
- 每增加一個索引，寫入操作（Insert/Update/Delete）的成本就會增加，因為必須同時更新 B-Tree。
- **實務法則**：盡量不要超過 5-10 個索引，除非有強烈的讀取需求支撐。

In system design, we often distinguish between "Read-heavy" and "Write-heavy" workloads. For MongoDB:
- Every index added increases the cost of write operations (Insert/Update/Delete) because the B-Tree must be updated simultaneously.
- **Rule of Thumb**: Try not to exceed 5-10 indexes per collection unless there is a strong read requirement justifying it.

## 3.2 記憶體工作集 (Working Set in RAM)

MongoDB 的效能極度依賴 RAM。理想情況下，所有的 **Indexes** 和 **Active Working Set (熱資料)** 都應該能放入 RAM。
- 如果索引過大導致 RAM 放不下，會發生 Page Faults，磁碟 I/O 成為瓶頸，延遲從 `ms` 級別退化到 `s` 級別。
- **Partial Index** 在此發揮巨大作用：例如只為 `status: "active"` 的訂單建立索引，可以節省大量記憶體。

MongoDB performance is heavily reliant on RAM. Ideally, all **Indexes** and the **Active Working Set** should fit into RAM.
- If indexes are too large for RAM, Page Faults occur, Disk I/O becomes the bottleneck, and latency degrades from `ms` to `s`.
- **Partial Indexes** play a huge role here: for example, indexing only orders with `status: "active"` can save significant memory.

## 3.3 架構圖視角 (Architectural View)

在 Replica Set 架構中：
1.  **Primary**: 處理寫入。過多的索引會拖慢 Primary 的寫入速度，進而增加 Replication Lag。
2.  **Secondary**: 雖然主要處理讀取，但它必須重放 (Replay) Primary 的 Oplog。如果索引導致寫入過慢，Secondary 也會跟不上，導致讀寫分離架構下的資料一致性視窗變大。

In a Replica Set architecture:
1.  **Primary**: Handles writes. Too many indexes slow down writes on the Primary, subsequently increasing Replication Lag.
2.  **Secondary**: While mainly handling reads, it must replay the Primary's Oplog. If indexes cause slow writes, Secondaries will struggle to keep up, widening the consistency window in read/write splitting architectures.

---

# 4. 逐步示例 (Walkthrough / Example)

## 場景：電商訂單查詢 (Scenario: E-commerce Order Query)

假設我們有一個 `orders` collection，包含以下欄位：
Suppose we have an `orders` collection with the following fields:

```json
{
  "_id": "ObjectId(...)",
  "userId": 12345,
  "status": "SHIPPED",
  "totalAmount": 250.00,
  "orderDate": "2023-10-27T10:00:00Z"
}
```

### 4.1 需求 (Requirement)
找出某個使用者 (`userId`) 在特定金額以上 (`totalAmount > 100`) 的訂單，並按日期 (`orderDate`) 排序。

Find orders for a specific user (`userId`) with an amount greater than 100 (`totalAmount > 100`), sorted by date (`orderDate`).

```javascript
db.orders.find({
  userId: 12345,
  totalAmount: { $gt: 100 }
}).sort({ orderDate: -1 })
```

### 4.2 Naive Approach (直覺但錯誤的做法)

許多工程師會直覺地認為：「我要查 userId，過濾 amount，然後排 date」，所以索引應該是：
Many engineers intuitively think: "I query userId, filter by amount, then sort by date," so the index should be:

```javascript
// Bad Index for this query
db.orders.createIndex({ userId: 1, totalAmount: 1, orderDate: -1 })
```

**分析 (Analysis)**：
這違反了 ESR 法則。
- **E**: `userId` (OK)
- **R**: `totalAmount` (Range)
- **S**: `orderDate` (Sort)
- 順序變成了 **E -> R -> S**。
- 當 MongoDB 使用索引過濾完 `userId` 和 `totalAmount` 後，剩下的結果在索引樹中**不再是依照 `orderDate` 排序的**。因此，MongoDB 必須在記憶體中進行排序 (`SORT` stage)，這在資料量大時非常慢。

This violates the ESR rule.
- **E**: `userId` (OK)
- **R**: `totalAmount` (Range)
- **S**: `orderDate` (Sort)
- The order becomes **E -> R -> S**.
- After MongoDB filters by `userId` and `totalAmount` using the index, the remaining results are **no longer sorted by `orderDate`** within the index tree. Consequently, MongoDB must perform an in-memory sort (`SORT` stage), which is very slow for large datasets.

### 4.3 Mature Solution (成熟的解法 - ESR)

根據 ESR，我們應該將 Sort 移到 Range 之前：
According to ESR, we should move Sort before Range:

```javascript
// Good Index (ESR compliant)
db.orders.createIndex({ userId: 1, orderDate: -1, totalAmount: 1 })
```

**為什麼有效？ (Why it works?)**
1.  **Equality**: 定位到 `userId: 12345` 的分支。
2.  **Sort**: 在該分支下，資料已經按 `orderDate` 排好序了。MongoDB 只要依序讀取即可。
3.  **Range**: 在讀取過程中，檢查 `totalAmount > 100`。如果不符合，就跳過該索引節點，繼續讀下一個。
4.  **結果**: 沒有記憶體排序 (`SORT` stage)，只有索引掃描 (`IXSCAN`) 和抓取文檔 (`FETCH`)。

1.  **Equality**: Locates the branch for `userId: 12345`.
2.  **Sort**: Within that branch, data is already sorted by `orderDate`. MongoDB just needs to scan sequentially.
3.  **Range**: During the scan, it checks `totalAmount > 100`. If it doesn't match, it skips that index node and moves to the next.
4.  **Result**: No in-memory sort (`SORT` stage), only index scan (`IXSCAN`) and document fetch (`FETCH`).

### 4.4 進階優化：Partial Index (Advanced Optimization)

如果業務邏輯只關心「未完成」的訂單（例如 `status` 為 `PENDING` 或 `PROCESSING`），且歷史訂單佔了 90% 的資料量，我們可以建立部分索引：

If the business logic only cares about "open" orders (e.g., `status` is `PENDING` or `PROCESSING`), and historical orders make up 90% of the data, we can create a Partial Index:

```javascript
db.orders.createIndex(
  { userId: 1, orderDate: -1 },
  { partialFilterExpression: { status: { $in: ["PENDING", "PROCESSING"] } } }
);
```

**效益**: 索引大小減少 90%，大幅降低 RAM 佔用與寫入開銷。
**Benefit**: Index size reduced by 90%, significantly lowering RAM usage and write overhead.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 忽略 Sort 導致的記憶體錯誤 (Ignoring Sort-Induced Memory Errors)

- **錯誤**: 查詢觸發了記憶體排序，且結果集超過 100MB (MongoDB 預設限制)。
- **後果**: 查詢直接報錯失敗 (`Executor error during find command :: caused by :: Sort exceeded memory limit`)。
- **修正**: 使用符合 ESR 的索引，或使用 `allowDiskUse()`（但這會導致效能驟降，僅建議用於後台分析）。

- **Pitfall**: A query triggers an in-memory sort, and the result set exceeds 100MB (MongoDB default limit).
- **Consequence**: The query fails with an error (`Executor error during find command :: caused by :: Sort exceeded memory limit`).
- **Fix**: Use an ESR-compliant index, or use `allowDiskUse()` (though this drastically reduces performance and is only recommended for background analytics).

## 5.2 在低基數 (Low Cardinality) 欄位建立單一索引 (Single Index on Low Cardinality Fields)

- **錯誤**: `db.users.createIndex({ gender: 1 })`。
- **原因**: 如果 `gender` 只有 "Male/Female"，索引幾乎沒有過濾效果。MongoDB 可能會選擇全表掃描 (`COLLSCAN`) 而忽略此索引，因為掃描索引後再回表 (Fetch) 的成本可能比直接掃描文檔更高。
- **修正**: 這種欄位通常只適合放在複合索引的後段，或是配合高基數欄位使用。

- **Pitfall**: `db.users.createIndex({ gender: 1 })`.
- **Reason**: If `gender` only has "Male/Female", the index offers little filtering power. MongoDB might choose a full collection scan (`COLLSCAN`) over this index, as the cost of scanning the index and then fetching documents can be higher than scanning documents directly.
- **Fix**: Such fields are usually only suitable as part of a compound index (typically at the end) or combined with high-cardinality fields.

## 5.3 正規表達式開頭通配符 (Regex with Leading Wildcard)

- **錯誤**: `db.users.find({ name: /.*John/ })`。
- **原因**: 就像查字典不能查「所有以 'tion' 結尾的字」一樣，B-Tree 無法優化左側模糊的查詢。這會導致全索引掃描或全表掃描。
- **修正**: 使用 Text Search (`$text`) 或外部搜尋引擎 (Elasticsearch/Atlas Search)。如果是前綴查詢 (`/^John/`)，索引是有效的。

- **Pitfall**: `db.users.find({ name: /.*John/ })`.
- **Reason**: Just like you can't efficiently look up "all words ending in 'tion'" in a dictionary, B-Trees cannot optimize queries with a wildcard at the beginning. This results in a full index scan or full collection scan.
- **Fix**: Use Text Search (`$text`) or an external search engine (Elasticsearch/Atlas Search). If it's a prefix query (`/^John/`), the index is effective.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何排查並解決 MongoDB 的慢查詢 (Slow Query)？
**How do you troubleshoot and resolve a slow query in MongoDB?**

*   **高分回答要點 (Key Points)**:
    1.  **Detection**: 使用 MongoDB Atlas Profiler 或開啟 Slow Query Log (設定 `slowms` 閾值) 捕捉慢查詢。
    2.  **Analysis**: 針對該查詢跑 `.explain("executionStats")`。
    3.  **Metrics**: 檢查 `totalKeysExamined` (掃描索引數) vs `totalDocsExamined` (掃描文檔數) vs `nReturned` (回傳數)。理想比例應接近 1:1:1。如果 `totalKeysExamined` 遠大於 `nReturned`，代表索引效率低。
    4.  **Action**: 檢查是否違反 ESR 法則，是否有 `SORT` stage，並建立或優化索引。

## Q2: 請解釋 ESR 法則，並舉例說明為何 Range 放在 Sort 之前會導致效能問題。
**Explain the ESR rule and illustrate why placing Range before Sort causes performance issues.**

*   **高分回答要點 (Key Points)**:
    1.  定義 E, S, R。
    2.  解釋 B-Tree 結構：在 Equality 確定後，子樹是排序的。
    3.  **關鍵點**: 一旦進行 Range 過濾（例如 `age > 20`），我們跨越了多個索引分支。雖然每個分支內部可能有序，但跨分支的結果集合併後，對於下一個欄位而言通常是無序的，因此必須進行記憶體排序。

## Q3: 什麼是 TTL 索引？它有什麼限制？
**What is a TTL Index and what are its limitations?**

*   **高分回答要點 (Key Points)**:
    1.  **用途**: 自動刪除過期資料（如 Session, Logs）。
    2.  **機制**: 背景執行緒每 60 秒檢查一次。
    3.  **限制**: 只能用於單一欄位索引（或複合索引的特定情境），欄位必須是 Date 類型或包含 Date 的 Array。
    4.  **坑**: 刪除大量資料時會造成 IO 壓力，可能影響 Primary 效能並導致 Oplog 暴增，影響 Replication。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 記憶錨點 (Key Takeaways)
1.  **ESR Rule**: 永遠優先考慮 **Equality -> Sort -> Range** 的順序來設計複合索引。
2.  **Explain is King**: 善用 `explain("executionStats")`，看到 `COLLSCAN` 或 `SORT` (in-memory) 就要警覺。
3.  **Covered Queries**: 最快的查詢是不讀取 Document 的查詢。
4.  **Cost of Indexes**: 索引不是免費的，會消耗 RAM 並拖慢寫入速度。
5.  **Partial Indexes**: 用於減少索引大小，特別是針對「活躍資料」或「異常狀態」的查詢。

## 後續延伸 (Next Steps)
- **Sharding (分片)**: 當單機索引優化達到極限，或資料量超過單機磁碟/記憶體限制時，如何設計 Shard Key？(Chapter 04)
- **Aggregation Pipeline Optimization**: 學習索引如何在 `$match`, `$sort`, `$group` 階段發揮作用。

---
*End of Chapter 03*