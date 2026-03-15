# 常見反模式與開發陷阱 / Common Anti-patterns & Pitfalls

## Mental model｜心智模型

在 MongoDB 的開發過程中，最大的誤區往往源自於將關聯式資料庫（RDBMS）的思維直接套用到文件式資料庫上，或者是完全忽視了實體限制（如 16MB 文件上限）。

要避免陷阱，你需要建立以下的心智模型：

1.  **資料存取優先於資料結構 (Access Patterns over Data Modeling)**：
    在 SQL 中，我們傾向先設計「完美的正規化表格」，再寫 SQL 去查詢。在 MongoDB，你必須先問「應用程式如何讀取這些資料？」，再決定資料長什麼樣子。
    > **Rule of Thumb**: Data that is accessed together should be stored together. (一起被讀取的資料，應該存放在一起。)

2.  **文件大小是有物理邊界的 (The 16MB Hard Limit)**：
    MongoDB 的單一文件（Document）最大限制為 16MB。這不僅是儲存限制，更是效能邊界。任何可能「無限增長」的陣列設計，最終都會撞上這堵牆。

3.  **寫入成本 vs. 讀取成本 (Write Heavy vs. Read Heavy)**：
    反模式通常發生在「為了寫入方便而犧牲讀取效能」（如過度正規化導致大量 `$lookup`），或「為了讀取方便而導致寫入崩潰」（如巨大的巢狀陣列導致頻繁的 Document 移動與索引更新）。

---

## Patterns & best practices｜常見模式與最佳實務

針對常見的陷阱，以下是業界標準的修正模式（Remediation Patterns）：

### 1. The Subset Pattern (子集模式)
**解決問題**：無限制陣列增長（Unbounded Arrays）與 16MB 限制。
**實作**：不要將所有關聯資料（如評論、Log）都塞進主文件。只在主文件中保留「最近的」或「最常存取的」一小部分（Subset），其餘資料存入另一個 Collection。

### 2. The Computed Pattern (計算屬性模式)
**解決問題**：頻繁的聚合運算（Aggregation）導致 CPU 飆高。
**實作**：不要在讀取時才計算 `sum` 或 `count`。在寫入時就利用 `$inc` 更新主文件中的統計欄位（如 `total_views`, `review_count`）。這是一種「以寫入換取讀取效能」的策略。

### 3. The Bucket Pattern (桶模式)
**解決問題**：物聯網（IoT）或時間序列資料導致索引過大與文件數量過多。
**實作**：不要為每一秒的感測器數據建立一個 Document。將特定時間範圍（如一小時）的數據「打包」進一個 Document 的陣列中。這能大幅減少索引大小並提升查詢效率。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The Unbounded Array (無限制陣列增長)
這是最經典的 MongoDB 反模式。
- **情境**：在 `User` 文件中有一個 `activity_log` 陣列，每次使用者操作就 `$push` 一筆紀錄。
- **後果**：
  - 文件大小迅速膨脹，最終超過 16MB 導致寫入失敗。
  - **Padding Overhead**：MongoDB 需要不斷在硬碟上移動文件以尋找更大的連續空間，導致 IOPS 飆升。
  - 查詢效能下降，因為即便只需要最後一筆，也必須讀取整個大陣列到記憶體。
- **修正**：使用 **Subset Pattern** 或將 Log 獨立為 Time-series Collection。

### 2. Massive Arrays & Indexing (巨大陣列索引)
- **情境**：對一個包含數千個元素的陣列欄位建立索引。
- **後果**：**Multikey Index** 的大小會爆炸性成長。每當陣列更新，索引維護成本極高，嚴重拖慢寫入速度。

### 3. Over-Normalization (過度正規化 / 濫用 $lookup)
- **情境**：將資料拆得像 SQL 一樣細（User, Order, OrderItems, Product 都在不同 Collection），然後在 API 層或使用 `$lookup` 進行多次 Join。
- **後果**：MongoDB 的 `$lookup` 效能遠不如 SQL JOIN。過度依賴聚合查詢會導致延遲過高。
- **修正**：適度 **Denormalization**（反正規化）。例如在 `Order` 中直接嵌入 `Product` 的快照（名稱、當下價格），只在必要時才關聯。

### 4. Monotonically Increasing Shard Keys (單調遞增的分片鍵)
- **情境**：在大規模分片叢集中，使用 `_id` (ObjectId) 或 `timestamp` 作為 Shard Key。
- **後果**：**Hotspotting**。因為新資料的 Key 總是比舊的大，所有新的寫入請求都會集中在最後一個 Chunk（即同一台 Shard Server），導致叢集寫入效能無法水平擴展。
- **修正**：使用 Hashed Shard Key 或複合鍵（Compound Shard Key）來打散寫入分佈。

### 5. The "Skip" Pagination Trap (Skip 分頁陷阱)
- **情境**：使用 `.find().skip(50000).limit(20)` 進行分頁。
- **後果**：資料庫必須掃描並丟棄前 50,000 筆資料才能回傳後 20 筆。隨著頁數增加，回應時間線性增長。
- **修正**：使用 **Keyset Pagination (Cursor-based)**。例如 `.find({ _id: { $gt: last_seen_id } }).limit(20)`。

### 6. Case-Insensitive Regex without Index (無索引的大小寫模糊搜尋)
- **情境**：使用 `/keyword/i` 進行搜尋。
- **後果**：這通常會導致 **Full Collection Scan**，因為標準索引對 Regex 支援有限，且大小寫轉換極耗 CPU。
- **修正**：使用 **Collation** 建立大小寫不敏感索引，或使用 **Text Index** / **Atlas Search**。

---

## Checklists & workflows｜檢查清單與流程

在將 Schema 部署到生產環境前，請執行此檢查清單：

### Schema Design Review
- [ ] **Array Growth Check**: 是否有任何陣列可能無限增長？如果有，是否有實作上限（Limit）或封存機制？
- [ ] **Document Size**: 預估文件在極端情況下的大小是否遠小於 16MB？（建議保持在數 KB 到數百 KB）。
- [ ] **Cardinality**: 經常查詢的欄位是否有適當的索引？
- [ ] **Data Locality**: 經常一起顯示的資料，是否在同一個文件或只需一次查詢即可取得？

### Performance & Operations
- [ ] **Query Explanation**: 是否對關鍵查詢執行過 `.explain("executionStats")`？確認沒有 `COLLSCAN`。
- [ ] **Index Coverage**: 查詢是否被索引覆蓋（Covered Query），即不需要讀取實際文件？
- [ ] **Shard Key Strategy**: (若有分片) Shard Key 是否有足夠的基數（Cardinality）且寫入分佈均勻？
- [ ] **Update Operations**: 是否大量使用 `$set` 替換整個物件？應改用 `$inc`, `$push`, `$set` (針對特定欄位) 以減少傳輸量。

---

## Real-world examples｜實戰案例

### Case 1: E-commerce Product Reviews (電商商品評論)

#### ❌ Anti-pattern: Embedding All Reviews
將所有評論直接塞入 Product 文件。

```json
// BAD: Document grows indefinitely
{
  "_id": "prod_123",
  "name": "Wireless Headphones",
  "reviews": [
    { "user": "alice", "text": "Great!", "rating": 5 },
    { "user": "bob", "text": "Okay...", "rating": 3 },
    // ... 50,000 more reviews ...
  ]
}
```
**後果**：讀取商品詳情頁變慢（載入太多不需要的資料），寫入新評論時鎖定整份文件，最終撞到 16MB 牆。

#### ✅ Best Practice: Subset Pattern + Reference
只嵌入「最新 5 筆」評論供快速顯示，其餘存入 `Reviews` collection。

```json
// GOOD: Product Collection
{
  "_id": "prod_123",
  "name": "Wireless Headphones",
  "review_stats": { "count": 50002, "avg_rating": 4.5 }, // Computed Pattern
  "latest_reviews": [ // Subset Pattern
    { "user": "charlie", "text": "Love it", "rating": 5 },
    { "user": "dave", "text": "Battery life is good", "rating": 4 }
  ]
}

// GOOD: Reviews Collection
{
  "_id": "rev_999",
  "product_id": "prod_123", // Reference
  "user": "alice",
  "text": "Great!",
  "rating": 5,
  "created_at": ISODate("...")
}
```

### Case 2: Social Media Feed (社群動態牆)

#### ❌ Anti-pattern: Complex Graph Lookup
使用者開啟 App 時，後端嘗試即時聚合：
1. 抓取 User 的關注列表 (Followings)。
2. 用 `$in` 查詢這些人的所有貼文。
3. 再 `$lookup` 貼文的作者資訊。
4. 依時間排序。

**後果**：隨著關注人數增加，查詢變得極慢（Scatter-Gather Query）。

#### ✅ Best Practice: Fan-out on Write
當使用者 A 發布貼文時，系統背景作業將貼文 ID 推送到所有粉絲的 `Timeline` 列表中（或專屬的 Timeline Collection）。
讀取時，只需查詢 `Timeline` collection，無需複雜運算。這是典型的「寫入擴散」（Fan-out on Write）策略，雖然增加寫入負擔，但保證了讀取的高效能（O(1) 或 O(k)）。