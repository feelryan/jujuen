# 聚合框架應用與資料處理 / Aggregation Framework Mastery

## Mental model｜心智模型

要精通 MongoDB Aggregation Framework，請將其想像為一條 **「工廠流水線 (Assembly Line)」** 或 Unix 系統中的 **「Pipe (`|`)」** 機制。

1.  **流動式處理 (Stream Processing)**：
    資料（Documents）像水流一樣進入管道，經過一個個站點（Stages）。每個 Stage 負責特定的加工任務（過濾、變形、計算），上一站的輸出即為下一站的輸入。
    > **Concept**: `Input Documents` -> `Stage 1 ($match)` -> `Stage 2 ($group)` -> `Stage 3 ($project)` -> `Output`

2.  **資料引力 (Data Gravity)**：
    與其將大量原始數據拉回 Application Server 進行處理（ETL in App），不如將計算邏輯推向數據所在的 Database Engine（ELT in DB）。Aggregation 利用 C++ 編寫的底層引擎處理數據，遠比在 Python/Node.js 中處理百萬行 JSON 高效。

3.  **塑形者 (The Shaper)**：
    不同於 SQL 的 `SELECT *` 往往回傳固定結構，Aggregation 的核心能力在於 **Reshaping**。你可以隨意拆解 Array (`$unwind`)、合併關聯資料 (`$lookup`)、或是將 Rows 轉為 Columns (`$group` + `$push`)。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. The "Filter First" Strategy (過濾優先原則)
永遠將 `$match` 放在 Pipeline 的第一步（或盡可能靠前）。
*   **Why**: 只有在 Pipeline 起始處的 `$match` 能利用 **Index**。
*   **Benefit**: 減少後續 Stage 需要處理的 Document 數量，大幅降低記憶體消耗與 CPU 負載。

### 2. The Lookup-Unwind Pattern (關聯展開模式)
這是處理 1:N 關聯最常見的組合技，用於模擬 SQL 的 `LEFT JOIN`。
```javascript
[
  { $lookup: { from: "orders", localField: "_id", foreignField: "userId", as: "userOrders" } },
  { $unwind: "$userOrders" }, // 將 Array 展開為多個 Documents
  // 此時每個 Document 代表一個 Order，但包含 User 資訊
  { $match: { "userOrders.status": "paid" } }
]
```

### 3. Dashboard Faceting (單次查詢多維度分析)
使用 `$facet` 在一次 Query 中計算多個維度的統計數據，特別適合 Dashboard 應用。
*   **Scenario**: 同時需要「總銷售額」、「依類別分組」、「依地區分組」。
*   **Pattern**:
    ```javascript
    { $facet: {
        "totalSales": [ { $group: { _id: null, total: { $sum: "$amount" } } } ],
        "byCategory": [ { $group: { _id: "$category", count: { $sum: 1 } } } ],
        "topSpenders": [ { $sort: { amount: -1 } }, { $limit: 5 } ]
    }}
    ```

### 4. Materialized Views with `$merge` (實體化視圖)
對於極其耗時的報表（如月度營收），不要每次都即時計算 (On-the-fly)。
*   **Pattern**: 使用 `$merge` (或是舊的 `$out`) 將聚合結果寫入另一個 Collection。
*   **Usage**: 設定排程任務 (Cron Job) 執行 Pipeline，將結果 "Upsert" 到報表 Collection 中供前端快速讀取。

### 5. Efficient Pagination (高效分頁)
對於複雜查詢的分頁，不要只用 `find()`。
*   **Pattern**: 使用 `$facet` 同時獲取「當前頁資料」與「總筆數 (Total Count)」，避免執行兩次查詢。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "God Pipeline" (上帝管道)
*   **Bad**: 試圖在一個長達 20 個 Stage 的 Pipeline 中完成所有商業邏輯。
*   **Consequence**: 難以維護、難以除錯、難以優化。
*   **Fix**: 拆分邏輯，或在應用層做適當的組裝；若是報表需求，考慮拆分為多個 `$merge` 步驟。

### 2. Ignoring Memory Limits (忽視記憶體限制)
*   **Pitfall**: `$group` 和 `$sort` 預設有 100MB 的 RAM 限制。超過會報錯。
*   **Fix**:
    1.  盡早 `$project` 掉不需要的欄位以節省空間。
    2.  開啟 `{ allowDiskUse: true }` (會寫入暫存檔，速度變慢但不會 crash)。

### 3. `$lookup` Explosion (關聯爆炸)
*   **Pitfall**: 在大數據量集合上濫用 `$lookup` 且沒有適當的索引或過濾。這會導致 Cartesian Product (笛卡兒積) 效應或極高的 IOPS。
*   **Fix**: 確保 `foreignField` 有建立索引。盡量先 `$match` 主表再 `$lookup`。

### 4. Client-side Processing (客戶端處理)
*   **Anti-pattern**: `db.collection.find().toArray()` 然後在 Application Code 用 `map/reduce/filter` 跑迴圈。
*   **Consequence**: 網路頻寬被塞爆，App Server OOM (Out of Memory)。
*   **Fix**: 只要是「加總」、「平均」、「排序」、「篩選」，都應該在 MongoDB 端完成。

---

## Checklists & workflows｜檢查清單與流程

在部署 Aggregation Pipeline 到生產環境前，請執行以下檢查：

### Performance Optimization Checklist
- [ ] **Index Usage**: 第一個 `$match` 是否有命中 Index？（使用 `explain` 確認 `cursor` 類型）。
- [ ] **Data Reduction**: 是否在 `$lookup` 或 `$group` 之前使用了 `$project` 或 `$unset` 移除不必要的大型欄位（如 HTML 內容、Base64 圖片）？
- [ ] **Filter Order**: `$match` 是否位於 `$sort`、`$skip`、`$limit` 之前？（除非邏輯上必須先排序）。
- [ ] **Lookups**: `foreignField` 是否已建立索引？

### Reliability & Maintenance
- [ ] **Memory Safety**: 是否需要設置 `allowDiskUse: true`？預估數據量是否會超過 100MB？
- [ ] **Type Consistency**: 參與 `$group` 的欄位資料型別是否一致？（String 的 "1" 和 Number 的 1 會被視為不同組）。
- [ ] **Result Size**: 最終輸出的 Document 是否會超過 BSON 16MB 限制？（特別是使用 `$push` 產生大陣列時）。

### Debugging Workflow
1.  **Divide & Conquer**: 註解掉所有 Stages，只留第一個。
2.  **Step-by-Step**: 逐一解開註解，觀察每個 Stage 的輸出是否符合預期。
3.  **Explain Plan**: 使用 `db.collection.aggregate(pipeline, { explain: true })` 查看執行計畫。

---

## Real-world examples｜實戰案例

### Scenario 1: E-commerce Sales Report (電商銷售報表)
**需求**：計算 2023 年每個月的總銷售額與平均客單價，並按月份排序。

```javascript
db.orders.aggregate([
  // 1. Filter: 只抓 2023 年的訂單 (利用 Index)
  { $match: {
      orderDate: {
        $gte: ISODate("2023-01-01T00:00:00Z"),
        $lt: ISODate("2024-01-01T00:00:00Z")
      },
      status: "completed"
  }},
  // 2. Group: 按月份分組統計
  { $group: {
      _id: { $month: "$orderDate" }, // 提取月份作為 Key
      totalRevenue: { $sum: "$finalAmount" },
      avgOrderValue: { $avg: "$finalAmount" },
      orderCount: { $sum: 1 }
  }},
  // 3. Project: 格式化輸出
  { $project: {
      _id: 0,
      month: "$_id",
      revenue: "$totalRevenue",
      aov: { $round: ["$avgOrderValue", 2] }, // 四雪五入
      orders: "$orderCount"
  }},
  // 4. Sort: 按月份排序
  { $sort: { month: 1 } }
])
```

### Scenario 2: User Activity Feed with Details (動態牆資料組裝)
**需求**：取得最新的 10 則貼文，包含作者名稱（來自 users collection）與最新 2 則留言。

```javascript
db.posts.aggregate([
  // 1. Sort & Limit: 先縮小範圍，只拿最新的 10 篇
  { $sort: { createdAt: -1 } },
  { $limit: 10 },
  
  // 2. Lookup Author: 關聯作者資料
  { $lookup: {
      from: "users",
      localField: "authorId",
      foreignField: "_id",
      as: "authorInfo"
  }},
  
  // 3. Unwind: 將 authorInfo 陣列轉為物件 (因為是 1對1)
  { $unwind: "$authorInfo" },
  
  // 4. Lookup Comments: 關聯留言 (Pipeline Lookup Pattern)
  // 這裡使用 Pipeline 形式的 lookup 以便對留言進行 sort 和 limit
  { $lookup: {
      from: "comments",
      let: { pid: "$_id" },
      pipeline: [
        { $match: { $expr: { $eq: ["$postId", "$$pid"] } } },
        { $sort: { createdAt: -1 } },
        { $limit: 2 }, // 每個 Post 只拿最新 2 則留言，避免傳輸過多資料
        { $project: { content: 1, userId: 1 } }
      ],
      as: "recentComments"
  }},
  
  // 5. Project: 清理敏感資料 (如作者密碼)
  { $project: {
      title: 1,
      content: 1,
      "authorInfo.name": 1,
      "authorInfo.avatar": 1,
      recentComments: 1
  }}
])
```