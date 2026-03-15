# 索引策略與最佳實踐 | Indexing Strategy & Best Practices

## Mental model｜心智模型

### 1. 字典與目錄 (The Dictionary & Catalog)
將 MySQL 的 InnoDB 索引想像成一本**「排序好的電話簿」**。
- **Clustered Index (Primary Key)**：就是電話簿的正文內容，按照姓氏（ID）排序，旁邊直接寫著電話號碼與地址（Row Data）。
- **Secondary Index (Non-Clustered)**：是書後的「附錄索引」。例如按照「居住城市」排序的列表。這個列表只告訴你名字（Primary Key），如果你需要詳細地址，你必須拿著這個名字回到正文（Clustered Index）去查找。這個動作稱為 **回表 (Bookmark Lookup / Row Lookup)**。

### 2. B+Tree 的代價 (The Cost of B+Tree)
B+Tree 是一種為磁碟 I/O 優化的資料結構。
- **讀取 (Read)**：極快。透過二分搜尋法 ($O(\log N)$) 快速定位。
- **寫入 (Write)**：有代價。每次 INSERT/UPDATE/DELETE，資料庫都需要維護這棵樹的平衡與排序。
- **核心權衡**：索引是用「寫入效能」與「磁碟空間」來換取「讀取效能」。

### 3. 索引即排序 (Index is Sorted Data)
這是理解「最左前綴」與「範圍查詢」的關鍵。索引中的數據是物理上嚴格排序的。
- 複合索引 `(A, B, C)` 就像是把資料先按 A 排，A 相同時按 B 排，B 相同時按 C 排。
- 如果你跳過 A 直接找 B，就像在電話簿裡不看姓氏直接找名字，索引完全失效。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 複合索引設計法則：ESR (Equality, Sort, Range)
設計複合索引時，欄位的順序至關重要。請遵循 **ESR 原則** 來決定欄位順序：

1.  **E (Equality)**：將精確匹配的欄位放在最前面（如 `user_id = 123`）。
2.  **S (Sort)**：將需要排序的欄位放在中間（如 `ORDER BY created_at`）。
3.  **R (Range)**：將範圍查詢的欄位放在最後（如 `age > 18`）。

> **Why?** 一旦在索引中使用了範圍查詢（Range），該欄位之後的索引列就無法用於排序或過濾了（因為範圍之後的數據不再是有序的）。

### 2. 覆蓋索引 (Covering Index)
這是最高效的查詢模式。如果一個索引包含了查詢所需的所有欄位（SELECT 的欄位 + WHERE 的欄位），MySQL 就不需要執行「回表」操作。

- **Pattern**:
  ```sql
  -- Index: (user_id, email)
  SELECT email FROM users WHERE user_id = 5566;
  ```
- **Benefit**: `EXPLAIN` 結果中會出現 `Using index`。這能將隨機 I/O 轉變為順序 I/O，效能提升巨大。

### 3. 最左前綴原則 (Leftmost Prefix Rule)
對於複合索引 `(col1, col2, col3)`：
- ✅ 有效：查詢 `col1`、查詢 `col1` AND `col2`、查詢 `col1` AND `col2` AND `col3`。
- ❌ 無效：查詢 `col2`、查詢 `col3`、查詢 `col2` AND `col3`。
- ⚠️ 部分有效：查詢 `col1` AND `col3`（只有 `col1` 走索引，`col3` 變成過濾條件）。

### 4. 前綴索引 (Prefix Indexing)
針對很長的 VARCHAR 或 TEXT 欄位，不要索引整個字串，只索引前 N 個字元。
- **Pattern**: `CREATE INDEX idx_desc ON products(description(20));`
- **Trade-off**: 節省空間，但無法用於 `ORDER BY` 或覆蓋索引。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 在索引欄位上做運算 (Functions on Indexed Columns)
這是最常見的效能殺手。一旦對欄位使用了函數，索引即失效。

- ❌ **Bad**:
  ```sql
  SELECT * FROM orders WHERE YEAR(created_at) = 2023;
  -- MySQL 必須掃描全表，計算每一行的 YEAR()
  ```
- ✅ **Good**:
  ```sql
  SELECT * FROM orders WHERE created_at BETWEEN '2023-01-01' AND '2023-12-31';
  -- 轉換為範圍查詢，可以使用索引
  ```

### 2. 隱式型別轉換 (Implicit Type Conversion)
當欄位定義與查詢值的型別不符時，MySQL 會自動轉型，這等同於使用了函數。

- ❌ **Bad**: `phone_number` 是 VARCHAR，但查詢用 INT。
  ```sql
  SELECT * FROM users WHERE phone_number = 0912345678;
  ```
- ✅ **Good**:
  ```sql
  SELECT * FROM users WHERE phone_number = '0912345678';
  ```

### 3. 低基數索引 (Low Cardinality Index)
不要對重複率極高的欄位建立索引（例如：性別、IsDeleted）。
- 如果一個查詢回傳超過表中 20%-30% 的資料，MySQL 優化器通常會放棄索引，直接全表掃描（Full Table Scan），因為隨機 I/O 的回表成本比順序掃描更高。

### 4. 過度索引 (Over-Indexing)
- 每個索引都會拖慢 INSERT/UPDATE/DELETE。
- 不要為每個欄位單獨建索引，應該優先考慮複合索引。
- **Redundant Index**: 如果已有 `(A, B)`，則不需要再單獨建 `(A)`，但可能需要 `(B)`。

### 5. LIKE 通配符在前 (Leading Wildcard)
- ❌ `LIKE '%keyword'`：無法使用索引（B+Tree 從左邊開始排）。
- ✅ `LIKE 'keyword%'`：可以使用索引。

---

## Checklists & workflows｜檢查清單與流程

### Index Design Checklist (設計階段)
- [ ] **基數檢查 (Cardinality)**：這個欄位的唯一值多嗎？如果只有 'Active'/'Inactive'，通常不需要索引。
- [ ] **查詢頻率**：這個欄位常被用於 `WHERE`, `JOIN`, `ORDER BY`, `GROUP BY` 嗎？
- [ ] **複合優先**：能否將這個新索引合併到現有的複合索引中（擴展現有索引）？
- [ ] **最左前綴**：複合索引的順序是否符合最常用的查詢模式？
- [ ] **覆蓋索引機會**：是否多加一個欄位到索引中，就能避免回表？

### Query Optimization Workflow (優化階段)
1.  **執行 EXPLAIN**：
    - 檢查 `type`：是否為 `ref`, `range`, `const`？（避免 `ALL`, `index`）。
    - 檢查 `key`：是否用到了預期的索引？
    - 檢查 `key_len`：索引使用的長度是否符合預期（檢查是否只有部分命中）？
    - 檢查 `Extra`：
        - ✅ `Using index` (Covering Index, 完美)。
        - ⚠️ `Using index condition` (ICP, 尚可)。
        - ❌ `Using filesort` (需要額外排序，記憶體不足時會寫入磁碟)。
        - ❌ `Using temporary` (建立了臨時表)。
2.  **檢查 WHERE 子句**：是否有函數運算？是否有隱式轉型？
3.  **檢查 ORDER BY**：排序欄位是否符合索引順序？

---

## Real-world examples｜實戰案例

### Case 1: 電商訂單查詢 (The ESR Rule Application)

**場景**：後台需要查詢「某個使用者」在「某個狀態」下的訂單，並按「建立時間」倒序排列。

**Schema**:
```sql
CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT,
    status TINYINT,
    created_at DATETIME,
    amount DECIMAL(10,2),
    ...
);
```

**Query**:
```sql
SELECT * FROM orders
WHERE user_id = 1001 AND status = 1
ORDER BY created_at DESC;
```

**索引策略分析**:
1. ❌ Index `(created_at)`: 雖然排序快，但掃描範圍太大。
2. ❌ Index `(user_id, status)`: 快速過濾，但 MySQL 需要額外進行 Filesort 來排序 `created_at`。
3. ✅ Index `(user_id, status, created_at)`:
   - `user_id` (Equality) -> 定位。
   - `status` (Equality) -> 定位。
   - `created_at` (Sort) -> 數據已經排好序，直接讀取即可。

### Case 2: 分頁優化 (Pagination with Covering Index)

**場景**：大數據量表的分頁查詢，越往後翻越慢。

**Bad Query**:
```sql
-- 當 offset 很大時 (e.g., 1,000,000)，MySQL 必須掃描 1,000,010 行並丟棄前 1,000,000 行
SELECT * FROM logs WHERE type = 'error' ORDER BY id LIMIT 1000000, 10;
```

**Optimization (Late Row Lookup)**:
利用覆蓋索引先只查出 ID，再回表拿資料。

```sql
SELECT * FROM logs t
INNER JOIN (
    -- 這裡只查 id，利用覆蓋索引 (type, id)，速度極快
    SELECT id FROM logs
    WHERE type = 'error'
    ORDER BY id
    LIMIT 1000000, 10
) sub ON t.id = sub.id;
```
**原理**：子查詢中只讀取索引（不回表），快速定位到那 10 個 ID，然後外層查詢只需要做 10 次回表，而不是 1,000,010 次掃描。