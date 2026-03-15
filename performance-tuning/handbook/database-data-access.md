# 資料庫查詢與存取模式優化 / Database Query and Access Pattern Optimization

在效能調優的領域中，資料庫往往是系統的「最終瓶頸」。無論你的應用程式伺服器（App Server）擴展得再多，如果資料庫層（Data Layer）的存取模式不佳，整個系統的吞吐量（Throughput）仍會被拖垮。本章節不談深奧的資料庫核心原理，而是聚焦於開發者在寫程式碼與 SQL 時最常遇到的效能殺手與解決方案。

---

## Mental model｜心智模型

要優化資料庫存取，你需要建立以下三個核心觀念：

### 1. The "Library" Analogy (圖書館隱喻)
將資料庫想像成一座巨大的圖書館：
- **Full Table Scan (全表掃描)**：你要找一本特定的書，但沒有索書號，只能從第一排書架走到最後一排，一本一本看。這是最慢的。
- **Indexing (索引)**：你查了目錄卡（Index），直接走到特定書架（Page/Block）拿書。
- **Covering Index (覆蓋索引)**：你要找的資訊（例如書名和作者）直接寫在目錄卡上，你甚至不需要走到書架去拿書就能回答問題。這是最快的。

### 2. Network Round-trips are Expensive (網路往返極其昂貴)
應用程式與資料庫通常位於不同的伺服器。每一次查詢（Query）都是一次網路 I/O。
- **Anti-pattern**: 迴圈中呼叫 DB（N+1 問題）。這就像去超市買 10 樣東西，但每買一樣東西都結帳一次並跑回家一趟。
- **Goal**: 盡量減少往返次數（Batching）或一次帶回足夠（但不過量）的資料。

### 3. Set-based vs. Procedural Thinking (集合思考 vs. 程序思考)
- **Procedural (程式碼思維)**：用 `for` 迴圈處理每一行資料。
- **Set-based (SQL 思維)**：用 `WHERE`, `JOIN`, `GROUP BY` 一次處理一批符合條件的資料集合。
- **Rule**: 盡量讓資料庫做它擅長的集合運算，而不是把所有原始資料拉回 App 層用迴圈過濾。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Indexing Strategy (索引策略)
索引不是越多越好，寫入時需要維護索引成本。
- **Leftmost Prefix Rule (最左前綴原則)**：對於複合索引 `(A, B, C)`，查詢條件必須包含 `A` 才能用到索引；如果只查 `B` 或 `C`，索引無效。
- **Covering Index (覆蓋索引)**：設計索引時，考慮將 `SELECT` 的欄位包含在索引中（或是使用 `INCLUDE` 子句），避免 "Key Lookup" / "Bookmark Lookup"（回表查詢）。
- **Cardinality (基數)**：在低基數欄位（如 `Gender`: Male/Female）建索引通常效益極低，除非數據分佈極度不均。

### 2. Efficient Query Patterns (高效查詢模式)
- **Select Specific Columns**: 永遠禁止 `SELECT *`。它會消耗額外的網路頻寬、記憶體，並破壞覆蓋索引的可能性。
- **Keyset Pagination (Seek Method)**: 避免在大數據量使用 `OFFSET` 分頁。
    - *Bad*: `LIMIT 10 OFFSET 100000` (DB 需讀取並丟棄前 10 萬筆)。
    - *Good*: `WHERE id > last_seen_id LIMIT 10` (直接跳轉，複雜度 O(1) 或 O(log N))。

### 3. Connection Pooling (連線池管理)
建立資料庫連線（TCP Handshake + Auth）非常耗時。
- **Reuse Connections**: 確保應用程式使用 Connection Pool（如 HikariCP, PgBouncer）。
- **Sizing**: Pool Size 不是越大越好。通常 `CPU Core Count * 2 + Effective Spindle Count` 是一個基準。過大的 Pool 會導致 Context Switching 與資源競爭。

### 4. Batching & Bulk Operations (批次操作)
- **Read**: 使用 `WHERE id IN (...)` 取代迴圈單筆查詢。
- **Write**: 使用 `INSERT INTO table VALUES (...), (...), (...)` 或 `COPY` 指令，而非單筆 INSERT。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The N+1 Query Problem
這是 ORM（如 Hibernate, Entity Framework, Rails ActiveRecord）使用者最常犯的錯誤。
- **現象**: 查詢 1 次主表（例如 `Users`），然後對結果集中的每一筆資料再發送 1 次查詢去拿關聯資料（例如 `Orders`）。
- **後果**: 100 個 User 導致 101 次 DB 查詢。
- **解法**: 使用 **Eager Loading** (e.g., `Include`, `Joined Load`, `Preload`)。

### 2. Functions on Indexed Columns (索引欄位上的函式操作)
- **Bad**: `WHERE YEAR(created_at) = 2023`
    - 資料庫必須對每一行計算 `YEAR()` 函數，導致全表掃描（Index Scan 變 Full Scan）。
- **Good**: `WHERE created_at >= '2023-01-01' AND created_at < '2024-01-01'`
    - 這樣可以使用 Range Scan。

### 3. Implicit Type Conversion (隱式型別轉換)
- **情境**: 欄位是 `VARCHAR`，但查詢傳入 `INT`。
- **後果**: DB 可能會將欄位轉型來匹配參數，這會導致索引失效。
- **原則**: 確保應用程式傳入的參數型別與 DB Schema 完全一致。

### 4. Long-Running Transactions (長事務)
- **Anti-pattern**: 在開啟 Transaction 後，進行外部 API 呼叫、複雜計算或等待使用者輸入。
- **後果**: 鎖（Locks）被長時間佔用，導致其他查詢阻塞（Blocking）甚至死鎖（Deadlock），連線池耗盡。
- **原則**: Transaction 範圍要盡可能小，只包含必要的 DB 操作。

---

## Checklists & workflows｜檢查清單與流程

### Performance Troubleshooting Workflow (效能排查流程)

當遇到資料庫效能問題時，請依照此流程操作：

1.  **Identify (識別)**：
    - 查看 APM (Application Performance Monitoring) 找出慢的 Endpoint。
    - 檢查 DB 的 **Slow Query Log**。
2.  **Analyze (分析)**：
    - 取得該 SQL 的 **Query Plan (EXPLAIN / EXPLAIN ANALYZE)**。
    - 關注關鍵字：`Full Table Scan` (全表掃描), `Filesort` (外部排序), `Temporary Table` (臨時表)。
3.  **Optimize (優化)**：
    - **Schema 層**: 增加或調整 Index。
    - **Query 層**: 改寫 SQL（移除 `SELECT *`，移除欄位函數，改寫 Join）。
    - **App 層**: 檢查是否 N+1，是否需要 Cache。
4.  **Verify (驗證)**：
    - 再次執行 `EXPLAIN` 確認 Cost 降低。
    - 進行壓力測試確保沒有副作用。

### Code Review Checklist (程式碼審查清單)

- [ ] **No N+1**: 迴圈內是否有 DB 查詢？關聯資料是否使用了 Eager Loading？
- [ ] **Index Usage**: `WHERE`, `JOIN`, `ORDER BY` 的欄位是否有對應的索引？是否符合最左前綴原則？
- [ ] **SARGable**: 查詢條件是否對索引友善（無欄位函數運算）？
- [ ] **Selectivity**: 是否只選取了需要的欄位（沒有 `SELECT *`）？
- [ ] **Transaction Scope**: 交易區塊內是否包含了不必要的外部 I/O 或耗時運算？
- [ ] **Pagination**: 是否在大數據表上使用了深度的 `OFFSET` 分頁？

---

## Real-world examples｜實戰案例

### Case 1: The "Invisible" Index Failure (隱形索引失效)

**情境**: 一個電商訂單查詢介面，使用者反應搜尋「訂單編號」非常慢。資料庫明明在 `order_code` (VARCHAR) 上建了索引。

**Bad Code (Java/Hibernate 範例)**:
```java
// 傳入的是 Long 型別，但 DB 欄位是 String (VARCHAR)
List<Order> orders = orderRepo.findByOrderCode(123456789L);
```

**SQL 實際執行狀況**:
```sql
-- DB 為了比較，將 varchar 轉為 int，導致全表掃描
SELECT * FROM orders WHERE CAST(order_code AS SIGNED) = 123456789;
```

**Fix**: 將輸入參數轉為 String，確保與 DB 型別一致。

### Case 2: Optimizing N+1 in Reports (報表中的 N+1 優化)

**情境**: 匯出「使用者及其最新訂單」的 CSV 報表。

**Bad Pattern**:
```python
users = db.query("SELECT * FROM users") # 1 query
for user in users:
    # N queries (如果 users 有 1000 人，這裡就跑 1000 次)
    latest_order = db.query("SELECT * FROM orders WHERE user_id = ? ORDER BY date DESC LIMIT 1", user.id)
    print(user.name, latest_order.amount)
```

**Optimization (Application-side Join / Batching)**:
```python
users = db.query("SELECT * FROM users")
user_ids = [u.id for u in users]

# 1 query to fetch all related orders
orders = db.query("SELECT * FROM orders WHERE user_id IN (?)", user_ids)

# In-memory mapping
orders_map = group_by_user(orders) 

for user in users:
    latest = get_latest(orders_map[user.id])
    print(user.name, latest.amount)
```
*結果：從 1001 次查詢降低為 2 次查詢。*

### Case 3: The "Wait Queue" Spike (連線池爆滿)

**情境**: 促銷活動開始，系統突然回應 502 Bad Gateway，DB CPU 使用率不高，但 App Log 顯示 `ConnectionPoolTimeoutException`。

**Root Cause**:
開發者在 Transaction 內發送了 Email。
```csharp
using (var scope = new TransactionScope()) {
    db.Execute("UPDATE inventory SET count = count - 1 WHERE id = @id");
    
    // 這裡卡住了！SMTP Server 回應慢，導致 DB 連線與 Lock 無法釋放
    emailService.SendConfirmation(user); 
    
    scope.Complete();
}
```

**Fix**: 將非 DB 操作移出 Transaction 範圍。
```csharp
// 1. DB Transaction
using (var scope = new TransactionScope()) {
    db.Execute("UPDATE inventory SET count = count - 1 WHERE id = @id");
    scope.Complete();
}

// 2. External Service (即使失敗，庫存已扣，可透過重試機制補發信)
emailService.SendConfirmation(user);
```