# 現代 MySQL 特性應用 (8.0+) | Modern MySQL Features (JSON, CTEs) / Modern MySQL Features (JSON, CTEs)

## Mental model｜心智模型

在 MySQL 8.0 之前，開發者往往將 MySQL 視為一個嚴格的「二維表格儲存引擎」，遇到階層資料（Hierarchical Data）或非結構化資料（Unstructured Data）時，通常會選擇在 Application Layer 處理，或是引入 Redis/MongoDB 等其他組件。

MySQL 8.0+ 改變了這個局勢，我們應該更新心智模型：

1.  **Hybrid Data Store (Relational + Document)**：
    MySQL 不再只是關聯式資料庫。透過 **JSON Data Type**，它能在維持 ACID 交易特性的同時，提供類似 NoSQL 的靈活性。你可以將它視為「具有強大關聯能力的 Document Store」。
2.  **SQL as a Programming Language**：
    過去冗長難讀的 Nested Subqueries（巢狀子查詢），現在可以透過 **CTEs (Common Table Expressions)** 像寫程式碼宣告變數一樣，將查詢邏輯模組化。
3.  **Analytics within OLTP**：
    透過 **Window Functions**，我們不再需要為了計算排名（Ranking）或移動平均（Moving Average）而進行複雜的 Self-Join 或將資料拉回應用層計算。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. JSON 欄位的正確使用姿勢 (JSON Usage Patterns)

不要把 MySQL 當作 MongoDB 用，而是採取 **Hybrid Approach**。

*   **EAV (Entity-Attribute-Value) 替代方案**：
    對於電商產品屬性（顏色、尺寸、材質...）這類稀疏且變動頻繁的欄位，使用 JSON 欄位取代傳統的 EAV 表格設計。
*   **Virtual Columns for Indexing (虛擬欄位索引)**：
    這是最重要的 Pattern。MySQL 無法直接對 JSON Blob 建立 B-Tree 索引，但可以對 **Generated Column (Virtual)** 建立索引。
    ```sql
    -- 建立虛擬欄位並索引
    ALTER TABLE products
    ADD COLUMN brand_id INT GENERATED ALWAYS AS (attributes->>'$.brand_id') VIRTUAL,
    ADD INDEX idx_brand (brand_id);
    ```
*   **Partial Updates**：
    使用 `JSON_SET` 或 `JSON_REPLACE` 只更新 JSON 中的特定路徑，避免讀取整個 JSON 再寫回（減少網路 I/O 與 Parsing 開銷）。

### 2. CTEs 的重構與遞迴 (CTE Patterns)

*   **Flattening Complex Logic (邏輯扁平化)**：
    將深層巢狀的 Subqueries 轉換為 CTEs 鏈。這不會改變執行計畫（大部分情況下），但會極大提升 SQL 的可讀性與維護性。
*   **Recursive CTEs for Hierarchies (遞迴查詢)**：
    處理分類樹、組織架構圖或評論串（Threaded Comments）時，使用 `WITH RECURSIVE` 取代傳統的 "Adjacency List" 多次查詢或 "Nested Set" 的複雜寫入。

### 3. Window Functions 實戰 (Window Function Patterns)

*   **Top-N per Group (分組取前 N 名)**：
    這是最經典的應用。例如：「找出每個類別中銷售額最高的前 3 個產品」。
    ```sql
    SELECT * FROM (
      SELECT *, RANK() OVER (PARTITION BY category_id ORDER BY sales DESC) as rnk
      FROM products
    ) t WHERE rnk <= 3;
    ```
*   **Efficient Pagination (高效分頁)**：
    在複雜報表中，使用 `COUNT(*) OVER()` 可以在一次查詢中同時獲得「當前頁資料」與「總筆數」，避免執行兩次重型查詢。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Schemaless" Trap (無架構陷阱)
*   **Anti-pattern**: 將核心業務邏輯（如 `user_email`, `order_status`）放入 JSON 欄位。
*   **Consequence**: 失去了 Foreign Key 約束，資料一致性難以保證；且無法享受原生欄位的高效型別檢查與儲存壓縮。
*   **Correction**: 核心欄位（用於 JOIN、WHERE 頻繁過濾、FK）必須是實體欄位；只有擴充屬性才放 JSON。

### 2. CTE Performance Assumption (CTE 效能迷思)
*   **Pitfall**: 以為 CTE 就等於 Temporary Table（會自動 Cache 結果）。
*   **Reality**: 在 MySQL 8.0 早期版本，CTE 只是語法糖（Inline View），多次引用同一個 CTE 會導致多次執行。雖然較新版本有改善（Materialization），但仍需透過 `EXPLAIN` 確認是否重複計算。

### 3. JSON Search without Extraction (無索引搜尋)
*   **Anti-pattern**: 直接在 WHERE 子句中使用 `JSON_EXTRACT(data, '$.key') = 'value'`。
*   **Consequence**: 這會導致 **Full Table Scan**，因為 MySQL 必須解析每一列的 JSON 字串。
*   **Correction**: 務必使用 Generated Column + Index。

### 4. Overusing Window Functions on Large Datasets
*   **Pitfall**: 在沒有適當 `PARTITION BY` 的情況下，對全表百萬級數據做 `ROW_NUMBER()` 或 `RANK()`。
*   **Consequence**: 這是記憶體殺手，可能導致大量的 Sort Buffer 使用與磁碟臨時檔寫入。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Should I use JSON? (我該用 JSON 嗎？)
- [ ] **資料結構是否固定？**
    - 是 → 使用一般 Relational Columns。
    - 否 → 繼續。
- [ ] **是否需要對該欄位做 Foreign Key 約束？**
    - 是 → 必須提取為一般 Column。
    - 否 → 繼續。
- [ ] **是否需要頻繁作為 WHERE 條件過濾？**
    - 是 → 使用 JSON + Generated Column Index。
    - 否 → 使用 JSON 即可。
- [ ] **是否只用於前端顯示，後端不需解析？**
    - 是 → 使用 JSON (Payload pattern)。

### Code Review Checklist for Modern Features
- [ ] **JSON**: 是否使用了 `->>` (unquote extraction) 而非 `->` 來處理字串比較？（避免引號造成的比對錯誤）。
- [ ] **JSON**: JSON 欄位的大小是否在合理範圍？（單列過大會影響 Page 載入效率）。
- [ ] **CTE**: 遞迴 CTE 是否設定了終止條件或 `cte_max_recursion_depth` 以防止無限迴圈？
- [ ] **Window Functions**: 是否在 `OVER` 子句中正確使用了索引欄位以避免額外的 Sorting？
- [ ] **Migration**: 是否確認生產環境 MySQL 版本 >= 8.0？（舊版 MariaDB 或 MySQL 5.7 支援度不同）。

---

## Real-world examples｜實戰案例

### Case 1: Deduplication using Window Functions (資料去重)

**情境**：Log 表中有重複的 Request ID，需要保留最新的一筆，刪除其餘的。

**Legacy Way**: 建立暫存表，GROUP BY 找出 ID，再 DELETE... 非常痛苦。

**Modern Way**:
```sql
WITH duplicates AS (
    SELECT 
        id, 
        ROW_NUMBER() OVER (
            PARTITION BY request_id 
            ORDER BY created_at DESC
        ) as rn
    FROM api_logs
)
DELETE FROM api_logs 
WHERE id IN (
    SELECT id FROM duplicates WHERE rn > 1
);
```

### Case 2: Dynamic Attributes with Indexing (動態屬性索引)

**情境**：SaaS 平台允許使用者自訂欄位（Custom Fields），且需要對這些欄位進行搜尋。

**Implementation**:
```sql
CREATE TABLE tickets (
    id BIGINT PRIMARY KEY,
    subject VARCHAR(255),
    custom_fields JSON, -- 存儲 {"priority": "high", "department": "sales"}
    
    -- 針對高頻搜尋欄位建立虛擬索引
    v_priority VARCHAR(20) GENERATED ALWAYS AS (custom_fields->>'$.priority') VIRTUAL,
    INDEX idx_priority (v_priority)
);

-- 查詢時會自動走索引
EXPLAIN SELECT * FROM tickets WHERE v_priority = 'high';
```

### Case 3: Recursive Category Tree (遞迴分類樹)

**情境**：電商網站的商品分類（電子產品 -> 手機 -> 智慧型手機），需要找出「電子產品」下的所有子分類 ID。

**Modern Way**:
```sql
WITH RECURSIVE category_path (id, name, path) AS (
    -- Anchor member (起點)
    SELECT id, name, CAST(name AS CHAR(200))
    FROM categories
    WHERE parent_id IS NULL -- 頂層分類
    
    UNION ALL
    
    -- Recursive member (遞迴部分)
    SELECT c.id, c.name, CONCAT(cp.path, ' > ', c.name)
    FROM categories c
    JOIN category_path cp ON cp.id = c.parent_id
)
SELECT * FROM category_path;
```