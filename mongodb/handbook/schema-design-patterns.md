# 實戰 Schema 設計模式 / Practical Schema Design Patterns

## Mental model｜心智模型

在 MongoDB 中設計 Schema 與關聯式資料庫（RDBMS）有著根本上的不同。在 SQL 世界，我們習慣先設計「標準化（Normalized）」的資料結構，然後才去寫查詢；但在 MongoDB，**你必須先知道應用程式如何查詢資料，才能設計 Schema**。

### 核心思維：Access Patterns Drive Design
**存取模式驅動設計**。不要問「這筆資料跟那筆資料有什麼關係？」，要問「應用程式讀取這筆資料時，通常會不會順便讀取那筆資料？」。

1.  **Data Locality (資料在地性)**:
    *   **Rule**: "Data that is accessed together should be stored together."
    *   **Concept**: 硬碟（或記憶體）讀取是昂貴的。如果你的 UI 頁面需要顯示 User Profile 和他的 Recent Orders，在 RDBMS 你需要 Join；在 MongoDB，最佳做法通常是將 Recent Orders 直接 Embed 在 User Document 中。

2.  **The 16MB Constraint (16MB 限制)**:
    *   MongoDB 單一 Document 的硬上限是 16MB。這不是限制，而是一種提示：它強迫你思考「什麼資料屬於這個實體本身」，以及「什麼資料應該被拆分」。

3.  **Read vs. Write Ratio (讀寫比)**:
    *   **Read-heavy**: 傾向於 Embedding 和 Computed Pattern（預先計算），以空間換取讀取速度。
    *   **Write-heavy**: 傾向於 Referencing 或更細碎的 Documents，避免頻繁更新導致的大型 Document 重寫或移動。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Embedding vs. Referencing (內嵌 vs. 參照)

這是最基礎的決策點，取決於關係的數量級（Cardinality）與存取模式。

| 關係類型 | 數量級 (Cardinality) | 建議策略 | 範例 |
| :--- | :--- | :--- | :--- |
| **One-to-Few** | < 100 | **Embed** | User 擁有的地址 (Addresses) |
| **One-to-Many** | 100 ~ 1000 | **Embed** (視情況) | Blog Post 的標籤 (Tags) 或少量留言 |
| **One-to-Squillions** | > 1000+ | **Reference** | 系統 Log、大型電商的訂單紀錄 |

*   **Embedding**: 優點是讀取極快（一次 IO），支援 Atomic Transaction（單一 Document 更新原子性）。
*   **Referencing**: 優點是資料正規化，避免 Document 過大，適合無限增長的數據集。

### 2. The Bucket Pattern (桶模式)

**場景**：物聯網 (IoT) 數據、時間序列數據 (Time Series)、Log 記錄。
**問題**：如果你為每一秒的感測器數據建立一個 Document，索引大小會爆炸，且查詢一段時間範圍的數據效率低。

**實作**：
將一段時間內的數據「裝桶」到一個 Document 中。

```json
// Instead of 1000 small docs, use one bucket:
{
  "sensor_id": 123,
  "start_date": ISODate("2023-10-01T10:00:00"),
  "end_date": ISODate("2023-10-01T11:00:00"),
  "measurements": [
    { "ts": ISODate("..."), "temp": 22.5 },
    { "ts": ISODate("..."), "temp": 22.6 }
    // ... up to ~60-100 entries
  ],
  "transaction_count": 60,
  "sum_temp": 1350 // Pre-aggregated data
}
```
*   **Benefit**: 大幅減少 Index 數量，提高時間範圍查詢效率，且易於管理歷史資料封存。

### 3. The Attribute Pattern (屬性模式)

**場景**：電商產品目錄，不同類型的產品有完全不同的規格欄位（例如：衣服有 Size/Color，手機有 RAM/Storage）。
**問題**：如果為每個屬性建立單獨的欄位（`size`, `color`, `ram`, `storage`），Index 會變得非常稀疏且難以管理。

**實作**：
將屬性轉為 Key-Value 陣列。

```json
{
  "product_id": "p123",
  "name": "Super Phone",
  "specs": [
    { "k": "ram", "v": "16GB" },
    { "k": "storage", "v": "512GB" },
    { "k": "color", "v": "Black" }
  ]
}
```
*   **Indexing**: 建立一個 Multikey Index `createIndex({"specs.k": 1, "specs.v": 1})`。
*   **Benefit**: 一個索引就能查詢所有不同類型的屬性。

### 4. The Subset Pattern (子集模式)

**場景**：User Profile 或 Product Detail 頁面。
**問題**：一個產品可能有 5000 則評論，但頁面載入時只需要顯示「最新的 5 則」。如果每次都讀取整個 Document（包含 5000 則評論），記憶體浪費嚴重。

**實作**：
在主 Document 中只保留「Working Set」（最新的 5 則），其餘的移到另外的 Collection。

```json
// Product Collection
{
  "product_id": "p1",
  "latest_reviews": [ ... top 5 reviews ... ], // Fast access for UI
  "review_count": 5020
}

// Reviews Collection
{ "product_id": "p1", "review_text": "...", "date": ... } // The rest
```

### 5. The Computed Pattern (計算模式)

**場景**：需要頻繁讀取統計數據（如：訂單總金額、按讚數）。
**問題**：每次讀取時都執行 `$sum` 或 `$count` 聚合運算太耗效能。

**實作**：
在寫入時（Write time）計算並更新結果，而非讀取時（Read time）計算。
*   **Action**: 當新增一筆 Review 時，同時對 Product Document 執行 `$inc: { review_count: 1 }`。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The Unbounded Array (無限增長的陣列)
*   **Trap**: 將所有使用者的 Log 或留言都 `push` 到同一個陣列中。
*   **Consequence**: Document 最終會超過 16MB 導致寫入失敗；且陣列過大會導致更新效能低落（MongoDB 需重寫整個 Doc）。
*   **Fix**: 使用 Bucket Pattern 或改為 Referencing。

### 2. Massive Arrays & Indexing (巨型陣列索引)
*   **Trap**: 對一個包含數千個元素的陣列建立索引。
*   **Consequence**: 每一筆 Document 更新陣列時，Index 都要更新多個 Entry，導致 Write Latency 飆升。

### 3. Deeply Nested Structures (過度巢狀結構)
*   **Trap**: `data.level1.level2.level3.items`。
*   **Consequence**: 查詢語法變得極其複雜（Array Filters `$[elem]`），且更新特定深層元素容易出錯。
*   **Fix**: 盡量保持結構扁平（Flatter is better），通常不建議超過 3 層巢狀。

### 4. Fear of Duplication (害怕資料冗餘)
*   **Trap**: 堅持像 SQL 一樣完全不儲存重複資料，導致讀取時需要大量的 `$lookup`。
*   **Consequence**: 查詢效能低落。
*   **Fix**: 接受適度的 Denormalization。例如在 Order 中儲存當下的 Product Name 和 Price（Snapshot），這不僅是優化，更是業務邏輯正確性的要求（產品改名不應影響歷史訂單）。

---

## Checklists & workflows｜檢查清單與流程

在設計 Schema 之前，請依序執行以下步驟：

### Phase 1: Workload Analysis (工作負載分析)
- [ ] **列出 Access Patterns**: 應用程式最常執行的前 5 個查詢是什麼？
- [ ] **定義 R/W Ratio**: 這個資料主要是讀取多（Read-heavy）還是寫入多（Write-heavy）？
- [ ] **資料生命週期**: 資料是否需要過期自動刪除（TTL）？是否是時間序列數據？

### Phase 2: Relationship Mapping (關係對應)
- [ ] **One-to-Few**: 直接 Embed。
- [ ] **One-to-Many**:
    - [ ] 數量有限且常一起讀取？ -> Embed。
    - [ ] 數量無限或需獨立查詢？ -> Reference (Parent Referencing 通常優於 Child Referencing)。
- [ ] **Many-to-Many**: 雙向 Reference 或使用中間表概念（視查詢方向而定）。

### Phase 3: Optimization & Validation (優化與驗證)
- [ ] **檢查 Document Size**: 預估最大增長量是否會接近 16MB？
- [ ] **檢查 Index 覆蓋**: 你的主要查詢是否能被 Index 覆蓋（Covered Query）？
- [ ] **應用 Patterns**:
    - [ ] 是否有欄位多樣性問題？ -> 考慮 Attribute Pattern。
    - [ ] 是否有歷史數據歸檔需求？ -> 考慮 Bucket Pattern。
    - [ ] 是否有頻繁統計需求？ -> 考慮 Computed Pattern。

---

## Real-world examples｜實戰案例

### Case 1: Social Media Post & Comments (社群貼文)

**情境**：一個類似 Instagram 的貼文系統，讀取極多，寫入適中。

**Schema Design**:
```javascript
// Posts Collection
{
  "_id": ObjectId("..."),
  "user_id": 101,
  "image_url": "...",
  "caption": "Hello World",
  "created_at": ISODate("..."),
  // Computed Pattern: 預先計算總數，避免 count()
  "likes_count": 1542,
  "comments_count": 45,
  // Subset Pattern: 只存最新的 3 則留言供 Preview
  "preview_comments": [
    { "user": "Alice", "text": "Nice!" },
    { "user": "Bob", "text": "Cool!" }
  ]
}

// Comments Collection (處理剩下的留言)
{
  "_id": ObjectId("..."),
  "post_id": ObjectId("..."), // Parent Referencing
  "user_id": 202,
  "text": "Detailed comment...",
  "created_at": ISODate("...")
}
```

### Case 2: Multi-tenant SaaS Configuration (多租戶設定)

**情境**：一個 SaaS 平台，不同租戶（Tenant）有完全不同的設定選項，且未來會不斷新增設定項。

**Schema Design (Attribute Pattern)**:
```javascript
{
  "_id": ObjectId("..."),
  "tenant_id": "tenant_A",
  "configurations": [
    { "k": "theme_color", "v": "#FF5733" },
    { "k": "max_users", "v": 100 },
    { "k": "feature_x_enabled", "v": true }
  ]
}
```
**Index**: `db.configs.createIndex({ "tenant_id": 1, "configurations.k": 1, "configurations.v": 1 })`
**Query**: 尋找所有開啟 `feature_x` 的租戶：
`db.configs.find({ "configurations": { $elemMatch: { k: "feature_x_enabled", v: true } } })`