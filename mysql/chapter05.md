# Chapter 05: High-Performance Schema Design
# 第 5 章：高效能 Schema 設計與資料建模

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

As a Senior Software Engineer, schema design is no longer just about defining tables to satisfy business requirements; it is about predicting how data grows and how queries interact with the storage engine. A poor schema design is often the root cause of performance bottlenecks that cannot be fixed by indexing or caching alone.
作為資深軟體工程師，Schema 設計不再僅是為了滿足業務需求而定義資料表；它是關於預測資料如何增長以及查詢如何與儲存引擎互動。糟糕的 Schema 設計往往是效能瓶頸的根本原因，這些問題通常無法單靠索引或快取來解決。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Evaluate Normalization Trade-offs**: Decide when to strictly normalize (3NF) and when to intentionally denormalize to reduce join complexity and improve read performance.
    **評估正規化的權衡**：決定何時嚴格執行正規化（3NF），以及何時為了降低 Join 複雜度與提升讀取效能而刻意進行反正規化。
2.  **Optimize Data Types**: Choose the most efficient data types (e.g., `VARCHAR` vs. `CHAR`, `INT` vs. `BIGINT`, `TIMESTAMP` vs. `DATETIME`) to minimize storage footprint and maximize buffer pool efficiency.
    **最佳化資料型別**：選擇最高效的資料型別（例如 `VARCHAR` vs. `CHAR`、`INT` vs. `BIGINT`、`TIMESTAMP` vs. `DATETIME`），以最小化儲存空間並最大化 Buffer Pool 的效率。
3.  **Master JSON in MySQL**: Understand the specific use cases for the JSON data type versus traditional relational columns, and the performance implications of mixing paradigms.
    **掌握 MySQL 中的 JSON**：理解 JSON 資料型別與傳統關聯式欄位的具體使用場景，以及混合使用兩種典範對效能的影響。
4.  **Execute Schema Changes Safely**: Design strategies for modifying large tables (Online DDL) without causing downtime or locking production databases.
    **安全執行 Schema 變更**：設計針對大表變更（Online DDL）的策略，確保在不造成停機或鎖死正式環境資料庫的情況下完成修改。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 Storage Efficiency = Performance
### 2.1 儲存效率即效能

**Mental Model**: Think of the MySQL InnoDB Buffer Pool as a limited "hot RAM" workspace. The smaller your data types, the more rows fit into a single 16KB page. More rows per page mean fewer disk I/O operations and better cache hit rates.
**心智模型**：將 MySQL InnoDB Buffer Pool 想像成有限的「熱區記憶體」工作空間。你的資料型別越小，單個 16KB 的 Page 能容納的行數就越多。每頁行數越多，意味著越少的磁碟 I/O 操作以及更高的快取命中率。

*   **Formal Definition**: Schema optimization in MySQL is largely about **Packing Density**.
    **正規定義**：MySQL 的 Schema 最佳化很大程度上是關於**堆疊密度（Packing Density）**。

### 2.2 The Cost of NULL
### 2.2 NULL 的代價

**Concept**: `NULL` is not just "no value"; it is a special state that requires extra handling logic in the database engine.
**觀念**：`NULL` 不僅僅是「沒有值」；它是一種需要資料庫引擎額外邏輯處理的特殊狀態。

*   **Storage**: InnoDB needs an extra bit per row to track nullability for columns.
    **儲存**：InnoDB 需要為每一行額外保留位元（bit）來追蹤欄位是否為 NULL。
*   **Logic**: Comparison operations (`=`, `<>`, `<`) yield `NULL` (unknown) rather than `TRUE` or `FALSE`, complicating query logic and index usage.
    **邏輯**：比較運算（`=`, `<>`, `<`）會產生 `NULL`（未知）而非 `TRUE` or `FALSE`，這會使查詢邏輯與索引使用變得複雜。

### 2.3 Relational vs. JSON (Hybrid Model)
### 2.3 關聯式與 JSON（混合模型）

**Analogy**:
*   **Relational Columns**: Like a strictly organized filing cabinet. Fast to search, rigid structure.
*   **JSON Columns**: Like a "junk drawer" or a generic box labeled "Misc". Flexible, fits anything, but hard to find a specific item without rummaging through everything.
**類比**：
*   **關聯式欄位**：像是一個嚴格分類的檔案櫃。搜尋速度快，結構僵化。
*   **JSON 欄位**：像是一個「雜物抽屜」或貼著「雜項」標籤的箱子。彈性大，什麼都裝得下，但若要找特定物品則需翻箱倒櫃。

**Key Takeaway**: Use JSON for data that is *rarely queried by specific keys* or has *highly variable attributes*. Use columns for anything used in `WHERE`, `JOIN`, or `ORDER BY` clauses.
**關鍵結論**：將 JSON 用於*極少被特定鍵值查詢*或具有*高度變動屬性*的資料。任何用於 `WHERE`、`JOIN` 或 `ORDER BY` 子句的資料，都應使用獨立欄位。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

In a distributed system or microservices architecture, the database schema often dictates the boundaries of service scalability.
在分散式系統或微服務架構中，資料庫 Schema 往往決定了服務擴展性的邊界。

### 3.1 Impact on Scalability & Maintenance
### 3.1 對擴展性與維護性的影響

1.  **Read/Write Split & Replication Lag**:
    **讀寫分離與複製延遲**：
    Heavy schemas with `TEXT` or large `JSON` blobs increase the size of binary logs (binlogs), which can increase replication lag between the master and read replicas.
    帶有 `TEXT` 或大型 `JSON` 物件的笨重 Schema 會增加 Binary Log（binlog）的大小，這可能導致主庫（Master）與讀取副本（Read Replicas）之間的複製延遲增加。

2.  **Schema Evolution (The "Alter Table" Problem)**:
    **Schema 演進（Alter Table 問題）**：
    In a CI/CD pipeline, a schema change that locks a table for 10 minutes is unacceptable. Senior engineers must design schemas that are resilient to change or use tools that allow non-blocking updates.
    在 CI/CD 流程中，鎖住資料表 10 分鐘的 Schema 變更通常是不可接受的。資深工程師必須設計對變更有彈性的 Schema，或使用允許非阻塞更新的工具。

3.  **The "Wide Table" vs. "Join" Trade-off**:
    **「寬表」與「Join」的權衡**：
    *   **OLTP Systems**: Prefer narrower tables. Updates are faster (less redo log data), and buffer pool utilization is higher.
    *   **Analytics/Reporting**: Often prefer denormalized "wide tables" to avoid expensive joins.
    *   **OLTP 系統**：傾向較窄的表。更新速度較快（Redo Log 資料較少），且 Buffer Pool 利用率較高。
    *   **分析/報表**：通常傾向反正規化的「寬表」以避免昂貴的 Join 操作。

---

## 4. Walkthrough / Example
## 4. 逐步示例

### Scenario: Designing an E-commerce Order System
### 情境：設計一個電商訂單系統

**Problem**: We need to store order details. An order has a status, a user, timestamps, and a flexible set of metadata (e.g., shipping tracking info, promo codes applied, custom gift messages).
**問題**：我們需要儲存訂單細節。訂單包含狀態、使用者、時間戳記，以及一組彈性的 Metadata（例如：物流追蹤資訊、使用的促銷代碼、客製化禮物訊息）。

#### 4.1 Naive Approach (The Anti-Pattern)
#### 4.1 幼稚的做法（反模式）

```sql
CREATE TABLE orders (
    id VARCHAR(255) PRIMARY KEY,  -- UUID stored as string
    user_id INT,
    status VARCHAR(50),           -- 'created', 'paid', 'shipped'...
    metadata TEXT,                -- Serialized PHP/Python object or JSON string
    created_at DATETIME,
    updated_at DATETIME
);
```

**Critique**:
**評論**：
1.  **ID**: `VARCHAR(255)` for a UUID is huge and slow.
2.  **Status**: `VARCHAR(50)` wastes space for a finite set of states.
3.  **Metadata**: `TEXT` is stored off-page (mostly) and requires manual parsing in the app.
4.  **NULLs**: Columns are nullable by default (in some configs), leading to ambiguity.

#### 4.2 Refined Solution (High Performance)
#### 4.2 改良方案（高效能）

```sql
CREATE TABLE orders (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    public_id BINARY(16) NOT NULL, -- UUID optimized storage if needed for external API
    user_id BIGINT UNSIGNED NOT NULL,
    status TINYINT UNSIGNED NOT NULL DEFAULT 0, -- Map to enum in code: 0=created, 1=paid...
    attributes JSON, -- Native JSON type
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_user_created (user_id, created_at), -- Covering index for "My Orders" page
    INDEX idx_public_id (public_id)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC CHARACTER SET utf8mb4;
```

**Analysis of Improvements**:
**改進分析**：

1.  **Primary Key**: `BIGINT UNSIGNED` is 8 bytes and sequential. This keeps the Clustered Index compact and minimizes page splitting (fragmentation).
    **主鍵**：`BIGINT UNSIGNED` 佔 8 bytes 且具順序性。這能保持叢集索引（Clustered Index）緊湊並最小化分頁拆分（碎片化）。
2.  **Public ID**: If you need UUIDs for APIs, store them as `BINARY(16)` (16 bytes) instead of `VARCHAR(36)` (36+ bytes).
    **公開 ID**：如果 API 需要 UUID，將其儲存為 `BINARY(16)`（16 bytes）而非 `VARCHAR(36)`（36+ bytes）。
3.  **Status**: `TINYINT` takes 1 byte. `VARCHAR(50)` takes length + 1 bytes. Massive savings on millions of rows.
    **狀態**：`TINYINT` 佔 1 byte。`VARCHAR(50)` 佔長度 + 1 bytes。在百萬級資料列中節省巨大空間。
4.  **JSON**: Using the native `JSON` type allows us to use functions like `JSON_EXTRACT` or create Virtual Columns for indexing specific keys later if requirements change.
    **JSON**：使用原生 `JSON` 型別允許我們使用 `JSON_EXTRACT` 等函數，或在未來需求變更時針對特定 Key 建立虛擬欄位（Virtual Columns）進行索引。
5.  **Timestamp**: `TIMESTAMP` (4 bytes) vs `DATETIME` (5-8 bytes). Note: `TIMESTAMP` stops at year 2038, so use `DATETIME` if longevity > 2038 is critical, but for logs/orders, `TIMESTAMP` is often efficient enough or `BIGINT` (epoch) is used.
    **時間戳**：`TIMESTAMP`（4 bytes）vs `DATETIME`（5-8 bytes）。注意：`TIMESTAMP` 在 2038 年結束，若需支援 2038 年以後請用 `DATETIME`，但對於日誌/訂單，`TIMESTAMP` 通常夠用，或改用 `BIGINT`（Epoch）。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 The "Generic String" Trap
### 5.1 「通用字串」陷阱

*   **Anti-pattern**: Using `VARCHAR(255)` for everything "just in case."
*   **Why it's bad**: While `VARCHAR` only stores used characters, MySQL internal temporary tables (used for sorting/grouping) may allocate memory based on the *declared* length. This can cause queries to spill to disk unnecessarily.
*   **Correction**: Be precise. If a zip code is 10 chars, use `VARCHAR(10)` or `CHAR(10)`.
*   **反模式**：為了「以防萬一」將所有欄位都設為 `VARCHAR(255)`。
*   **壞處**：雖然 `VARCHAR` 僅儲存實際使用的字元，但 MySQL 內部暫存表（用於排序/分組）可能會根據*宣告*的長度來分配記憶體。這可能導致查詢不必要地溢出到磁碟（Spill to disk）。
*   **修正**：精準定義。如果郵遞區號是 10 個字元，請用 `VARCHAR(10)` 或 `CHAR(10)`。

### 5.2 Abusing JSON for Relational Data
### 5.2 濫用 JSON 儲存關聯式資料

*   **Anti-pattern**: Storing `customer_name` or `order_status` inside a JSON column.
*   **Why it's bad**: You cannot efficiently join on JSON fields without generated columns. Updating a single field in a JSON document often requires rewriting the entire JSON blob (Write Amplification).
*   **Correction**: Extract core business logic fields to dedicated columns. Use JSON only for "extra" attributes.
*   **反模式**：將 `customer_name` 或 `order_status` 存放在 JSON 欄位中。
*   **壞處**：若無生成欄位（Generated Columns），你無法有效地對 JSON 欄位進行 Join。更新 JSON 文件中的單一欄位通常需要重寫整個 JSON 物件（寫入放大）。
*   **修正**：將核心業務邏輯欄位提取為專用欄位。僅將 JSON 用於「額外」屬性。

### 5.3 Blocking Schema Changes
### 5.3 阻塞式 Schema 變更

*   **Anti-pattern**: Running `ALTER TABLE big_table ADD COLUMN x ...` directly in production during peak hours.
*   **Why it's bad**: Depending on the MySQL version and operation, this can lock the table, causing a site outage.
*   **Correction**:
    *   MySQL 8.0+: Supports "Instant DDL" for adding columns (adds metadata only, no table rebuild).
    *   Older versions / Complex changes: Use tools like `gh-ost` or `pt-online-schema-change`.
*   **反模式**：在尖峰時段直接在正式環境執行 `ALTER TABLE big_table ADD COLUMN x ...`。
*   **壞處**：取決於 MySQL 版本與操作類型，這可能會鎖住資料表，導致網站服務中斷。
*   **修正**：
    *   MySQL 8.0+：支援「Instant DDL」來新增欄位（僅修改 Metadata，不重建資料表）。
    *   舊版本 / 複雜變更：使用 `gh-ost` 或 `pt-online-schema-change` 等工具。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### 6.1 UUID vs. Auto-Increment ID
### 6.1 UUID vs. Auto-Increment ID

*   **Question**: "We are designing a distributed system. Should we use UUIDs or Auto-Increment Integers as Primary Keys in MySQL? What are the trade-offs?"
    **問題**：「我們正在設計一個分散式系統。在 MySQL 中我們應該使用 UUID 還是 Auto-Increment 整數作為主鍵？有什麼權衡？」
*   **Key Answer Points**:
    *   **Performance**: Auto-Increment is sequential, keeping the B+ Tree balanced and writes strictly appended (sequential I/O). UUIDs (version 4) are random, causing page splits and random I/O (fragmentation).
    *   **Security**: Auto-Increment exposes business volume (ID=100 vs ID=1000). UUIDs hide this.
    *   **Solution**: Use Auto-Increment internally for the Primary Key (Clustered Index) and a separate UUID column (indexed) for external API references. Or use UUID v7 (time-ordered).
    *   **高分回答要點**：
        *   **效能**：Auto-Increment 是順序的，能保持 B+ Tree 平衡且寫入是嚴格追加的（順序 I/O）。UUID（v4）是隨機的，會導致分頁拆分與隨機 I/O（碎片化）。
        *   **安全性**：Auto-Increment 會暴露業務量（ID=100 vs ID=1000）。UUID 能隱藏這點。
        *   **解法**：內部使用 Auto-Increment 作為主鍵（叢集索引），並為外部 API 引用使用獨立的 UUID 欄位（加索引）。或者使用 UUID v7（基於時間排序）。

### 6.2 Handling Schema Migrations on 1TB Tables
### 6.2 處理 1TB 大表的 Schema 遷移

*   **Question**: "You need to add a column to a 1TB table in a 24/7 system. How do you do it without downtime?"
    **問題**：「你需要為一個 24/7 系統中的 1TB 大表新增欄位。如何在不停機的情況下完成？」
*   **Key Answer Points**:
    *   Check MySQL version: Can we use Instant DDL?
    *   If not, explain the "Ghost" approach (create shadow table, sync triggers/binlogs, cut-over).
    *   Mention impact on replication lag and disk I/O throttling.
    *   **高分回答要點**：
        *   檢查 MySQL 版本：能否使用 Instant DDL？
        *   若否，解釋「Ghost」方法（建立影子表、同步 Triggers/Binlogs、最後切換）。
        *   提及對複製延遲（Replication Lag）的影響以及磁碟 I/O 的限流（Throttling）。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Summary
### 小結

1.  **Smaller is Faster**: Always choose the smallest data type that fits the business need to maximize Buffer Pool efficiency.
    **越小越快**：總是選擇能滿足業務需求的最小資料型別，以最大化 Buffer Pool 效率。
2.  **Avoid NULL**: Use `NOT NULL` with `DEFAULT` values wherever possible to simplify logic and save storage bits.
    **避免 NULL**：盡可能使用 `NOT NULL` 搭配 `DEFAULT` 值，以簡化邏輯並節省儲存位元。
3.  **JSON Wisely**: Use JSON for flexibility, but never for columns that are frequently filtered or joined.
    **明智使用 JSON**：利用 JSON 獲得彈性，但絕不要用於頻繁過濾或 Join 的欄位。
4.  **Online DDL**: Schema changes in production must be non-blocking. Master tools like `gh-ost` or MySQL 8.0 Instant DDL.
    **Online DDL**：正式環境的 Schema 變更必須是非阻塞的。掌握 `gh-ost` 或 MySQL 8.0 Instant DDL 等工具。
5.  **Primary Keys Matter**: Prefer sequential IDs (Int/BigInt/UUIDv7) over random UUIDs for Clustered Index performance.
    **主鍵很重要**：為了叢集索引效能，優先選擇順序 ID（Int/BigInt/UUIDv7）而非隨機 UUID。

### Next Steps
### 後續延伸

*   **Study**: Deep dive into **InnoDB Page Structure** to understand exactly how records are stored physically.
    **學習**：深入研究 **InnoDB Page Structure**，了解記錄在物理上究竟是如何儲存的。
*   **Practice**: Set up a local MySQL instance, populate a table with 10 million rows, and practice using `pt-online-schema-change` to modify it while running a load test script.
    **實作**：建立本地 MySQL 實例，填充一張 1000 萬行的表，並在執行負載測試腳本的同時，練習使用 `pt-online-schema-change` 進行修改。
*   **Next Chapter**: Proceed to **Chapter 06: Advanced Indexing Strategies**, where we will discuss how to query this schema efficiently.
    **下一章**：進入 **Chapter 06: 進階索引策略**，我們將討論如何高效地查詢這個 Schema。