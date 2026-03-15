# 查詢效能與資料獲取模式 / Query Performance & Data Fetching Patterns

## Mental model｜心智模型

在設計 API 與資料庫互動時，工程師常犯的錯誤是將「記憶體內的物件操作」思維直接套用到「資料庫查詢」上。為了構建高效能系統，你需要建立以下的心智模型：

### 1. 往返成本 (Round-Trip Latency)
每一次資料庫查詢都是一次網路請求。
- **錯誤思維**：像操作 Array 一樣操作 DB，需要什麼就隨手 query 一下。
- **正確模型**：資料庫是「昂貴的遠端服務」。你的目標是 **「用最少的次數，搬運最精確的資料」**。
  - **Minimize Trips**：能一次拿完的，不要分十次拿（解決 N+1）。
  - **Minimize Payload**：只需要 3 個欄位，不要 `SELECT *`（解決 Over-fetching）。

### 2. 資料庫的視角 (The Database Perspective)
資料庫不在乎你的 Class 結構，它只在乎 I/O 與 CPU。
- **Offset Pagination**：資料庫必須讀取並丟棄前 N 筆資料才能給你第 N+1 筆。當 N 很大時，這就是災難。
- **Cursor Pagination**：直接告訴資料庫「從上次看到的這行開始讀」，這是 O(1) 或 O(log N) 的操作，而非 O(N)。

### 3. ORM 是雙面刃 (ORM as a Double-Edged Sword)
ORM (Object-Relational Mapping) 隱藏了 SQL 的複雜性，但也隱藏了效能殺手。
- **Mental Model**：ORM 不是魔法，它是 SQL 生成器。你必須時刻意識到：「這行 code 到底生成了什麼 SQL？」

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 分頁策略：Cursor vs. Offset (Pagination Strategy)

選擇分頁策略取決於你的 UI 需求與資料量級。

| 策略 | 適用場景 | 優點 | 缺點 |
| :--- | :--- | :--- | :--- |
| **Offset-based** <br> `LIMIT 10 OFFSET 1000` | 後台管理列表、需要跳頁功能 (Jump to page 5) | 實作簡單、直觀 | **效能極差** (Deep Pagination)、資料新增/刪除時會導致頁面內容重複或遺漏 |
| **Cursor-based (Keyset)** <br> `WHERE id < cursor LIMIT 10` | Infinite Scroll (無限捲動)、社群動態牆 (Feeds)、高併發讀取 | **效能極高** (利用 Index)、資料穩定性高 | 無法跳頁、實作較複雜、需要唯一的排序欄位 |

**實戰建議**：
- 對於 **C 端用戶的 Feed** 或 **海量資料**，**強制使用 Cursor-based**。
- Cursor 通常是 base64 編碼的字串（包含 `last_id` 和 `sort_value`）。

### 2. 解決 N+1 問題 (Solving the N+1 Problem)

當你獲取一個列表（例如：文章），然後在迴圈中獲取關聯資料（例如：作者），就會產生 N+1 問題。

**Pattern: Eager Loading / Batching**
- **SQL 思維**：使用 `IN` 子句一次撈取所有關聯 ID。
- **ORM 實作**：
  - Rails: `Post.includes(:author)`
  - Laravel: `Post::with('author')->get()`
  - Node/Prisma: `include: { author: true }`
- **GraphQL**：使用 **DataLoader** 模式，將單個 resolve 請求收集起來，在 next tick 合併成一次 DB 查詢。

### 3. 投影與資料傳輸優化 (Projection & Payload Optimization)

**Pattern: DTO / ViewModel Projection**
永遠不要將 DB Entity 直接序列化回傳給 Client。
- **只查詢需要的欄位**：避免 `SELECT *`。特別是當表中有 `TEXT` 或 `BLOB` 欄位時，這會嚴重拖慢 I/O。
- **JSON 序列化成本**：龐大的 JSON 不僅消耗網路頻寬，也消耗 Server 和 Client 的 CPU 解析時間。

### 4. 搜尋與過濾 (Search & Filtering)

**Pattern: Index-Aware Filtering**
- 確保 API 允許過濾的欄位（Filterable Fields）都有對應的索引。
- **Composite Index (複合索引)**：如果用戶常同時過濾 `status` 和 `created_at`，單獨的索引可能不夠，需要 `(status, created_at)` 的複合索引。
- **限制過濾複雜度**：不要讓前端隨意組合 SQL 條件。提供有限的過濾參數，或者使用 Search Engine (Elasticsearch/Meilisearch) 處理全文檢索。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Loop Query" (迴圈內查詢)
最經典的效能殺手。
```python
# ❌ Anti-pattern
users = db.get_users()
for user in users:
    # 每一圈都打一次 DB，網路延遲累積成災難
    profile = db.get_profile(user.id) 
```

### 2. Deep Pagination with Offset (深分頁陷阱)
當你請求 `page=10000, size=20` 時，資料庫實際上做了：
`SELECT * FROM items LIMIT 20 OFFSET 200000;`
資料庫必須掃描並丟棄前 200,000 行。這會導致資料庫 CPU 飆升，甚至鎖表。

### 3. Client-side Filtering (客戶端過濾)
先撈出所有資料，再用程式碼過濾。
- **❌ 錯誤**：`const allUsers = await db.User.findAll(); const activeUsers = allUsers.filter(u => u.isActive);`
- **後果**：當資料量從 100 筆變成 100 萬筆時，應用程式記憶體會爆炸 (OOM)，資料庫 I/O 也會被塞滿。

### 4. Premature Optimization vs. Negligence (過早優化 vs. 忽視)
- **忽視**：不做任何索引，認為「現在資料少沒關係」。等資料量大了，加索引可能導致鎖表 downtime。
- **過早優化**：為了極致效能寫了極其複雜的 Raw SQL，導致難以維護，而實際上 ORM 的效能已經足夠。

---

## Checklists & workflows｜檢查清單與流程

在 Code Review 或上線前，請對照以下清單：

### ✅ Schema & Indexing Check
- [ ] 用於 `WHERE`、`ORDER BY`、`JOIN` 的欄位是否有建立索引？
- [ ] 是否有複合索引 (Composite Index) 支援常見的多欄位查詢？
- [ ] 是否避免了在索引欄位上使用函數？（例如 `WHERE YEAR(created_at) = 2023` 會導致索引失效，應改為範圍查詢）。

### ✅ Query Logic Check
- [ ] **N+1 檢查**：是否有在迴圈中呼叫 DB？是否有使用 ORM 的 `include` / `with` / `join`？
- [ ] **分頁檢查**：API 是否強制分頁？是否有 `max_limit` 防止用戶一次請求 10,000 筆資料？
- [ ] **欄位檢查**：是否有 `SELECT *`？是否排除了不需要的大型欄位（如文章內容、Base64 圖片）？

### ✅ Monitoring & Validation
- [ ] **SQL Log**：在開發環境開啟 SQL Log，親眼確認一個 API Request 到底觸發了幾條 SQL。
- [ ] **Explain Analyze**：對於複雜查詢，是否跑過 `EXPLAIN` 確認執行計畫 (Execution Plan)？

---

## Real-world examples｜實戰案例

### Scenario 1: 高效的無限捲動 (Cursor Pagination Implementation)

假設我們要實作一個類似 Instagram 的動態牆。

**❌ Bad Practice (Offset):**
```sql
-- 當用戶滑到第 100 頁時，效能極差
SELECT * FROM posts 
ORDER BY created_at DESC 
LIMIT 10 OFFSET 1000;
```

**✅ Best Practice (Cursor):**
前端傳來最後一篇文章的 `cursor` (例如: `created_at` timestamp 或 ID)。

```sql
-- 加上索引: CREATE INDEX idx_posts_created_at ON posts(created_at);
SELECT id, title, created_at 
FROM posts 
WHERE created_at < '2023-10-27T10:00:00Z' -- Cursor value
ORDER BY created_at DESC 
LIMIT 10;
```
*結果：無論滑到第幾頁，查詢速度都一樣快。*

### Scenario 2: 解決 N+1 問題 (E-commerce Order List)

需求：顯示訂單列表，以及每張訂單的購買者姓名。

**❌ Anti-pattern (Pseudo-code):**
```javascript
const orders = await Order.findAll({ limit: 20 }); // Query 1
const result = [];

for (const order of orders) {
  // Query 2...21 (N+1 Problem)
  const user = await User.findById(order.userId); 
  result.push({ ...order, userName: user.name });
}
```

**✅ Best Practice (Batching/Eager Loading):**
```javascript
// ORM 會自動轉成兩條高效 SQL:
// 1. SELECT * FROM orders LIMIT 20;
// 2. SELECT * FROM users WHERE id IN (1, 2, 5, ...);
const orders = await Order.findAll({ 
  limit: 20,
  include: ['user'] // Eager load
});

// 記憶體內組裝，無需額外 DB 查詢
const result = orders.map(o => ({ ...o, userName: o.user.name }));
```