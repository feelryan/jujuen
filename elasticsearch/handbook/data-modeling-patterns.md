# 資料建模模式：Denormalization 與關聯處理 / Data Modeling Patterns: Denormalization & Handling Relationships

## Mental model｜心智模型

在關聯式資料庫（RDBMS）中，我們習慣將資料「標準化（Normalize）」以減少冗餘並保證一致性；但在 Elasticsearch（ES）的世界裡，為了極致的搜尋效能，我們必須擁抱 **「反標準化（Denormalization）」**。

請建立以下的心智模型：

1.  **Write-time vs. Read-time Cost / 寫入時 vs. 讀取時成本**：
    *   **RDBMS**: Pay at read time. 資料寫入快（只存一份），但讀取時需要複雜的 JOIN，隨著資料量增加，JOIN 成本呈指數上升。
    *   **Elasticsearch**: Pay at write time. 在寫入時就將資料「攤平（Flatten）」或預先組裝好。讀取時幾乎不需要計算，直接掃描倒排索引（Inverted Index）。

2.  **Document as a Self-contained Unit / 文件即自足單元**：
    *   想像 ES 的 Document 是一份已經印好的「紙本報告」。你不能在讀這份報告時動態去查閱另一份檔案櫃裡的資料。所有的資訊（包含作者名稱、分類標籤）都必須印在這一張紙上。

3.  **No Joins (Mostly) / 幾乎沒有 Join**：
    *   ES 是分散式系統。真正的 JOIN 需要跨 Shard 甚至跨 Node 傳輸大量數據，這在分散式架構下是效能殺手。因此，所有的 Modeling 策略都是為了規避 Query-time Join。

---

## Patterns & best practices｜常見模式與最佳實務

在實戰中，處理關聯資料（Relationships）主要有四種模式，按推薦程度排序：

### 1. Denormalization (Flattening)｜反標準化（攤平）
**這是最推薦、效能最好的預設模式。**
將關聯資料直接複製到主文件中。

*   **Scenario**: Blog Post (主) 與 Author (從)。
*   **Implementation**: 在 `blog_post` index 中直接包含 `author_name` 和 `author_id` 欄位。
*   **Pros**: 搜尋速度最快，單次查詢即可取得所有顯示所需資訊。
*   **Cons**: 資料冗餘。如果 Author 改名，需要更新所有相關的 Blog Post（Write Amplification / 寫入放大）。

### 2. Nested Objects｜巢狀物件
解決 `Object` 陣列被 Lucene 攤平導致的查詢邏輯錯誤。

*   **The Problem**: 標準的 Object array 會被攤平，導致關聯丟失。
    *   Data: `[{name: "Nike", type: "Shoes"}, {name: "Apple", type: "Tech"}]`
    *   Flattened: `names: ["Nike", "Apple"]`, `types: ["Shoes", "Tech"]`
    *   Query: `name: Nike AND type: Tech` -> **Matches! (False Positive)**
*   **Implementation**: Mapping 設定 `type: "nested"`。ES 會在內部將每個 array item 索引為隱藏的獨立小文件。
*   **Pros**: 精確查詢（Precision）。保證物件內部的欄位關聯性。
*   **Cons**: 更新成本高（更新 parent 等於重寫所有 children）；Heap memory 消耗較大。

### 3. Parent-Child Relationship (Join Field)｜父子關聯
類似 SQL JOIN，但在 Index 內部實作。

*   **Scenario**: 1對多，且「多」的一方更新頻率極高，或生命週期完全獨立。例如：Product (父) 與 Logs/Reviews (子)。
*   **Implementation**: 使用 `join` field type。**必須確保 Parent 和 Child 在同一個 Shard (使用 Routing)**。
*   **Pros**: Parent 和 Child 可以獨立更新，互不影響。
*   **Cons**: 查詢效能比 Denormalization 慢 5-10 倍；Memory overhead 高；Routing 管理複雜。

### 4. Application-side Joins｜應用層 Join
不依賴 ES 的關聯功能，發送兩次查詢。

*   **Scenario**: 資料量小，或資料分布在不同系統（如 User 在 MySQL，Logs 在 ES）。
*   **Implementation**: 先查 ES 拿到 User IDs，再去 MySQL 查 User Details（或反之）。
*   **Pros**: 架構簡單，解耦。
*   **Cons**: 網路來回次數（Round-trip）增加；無法根據關聯欄位進行排序或過濾（例如：無法在 ES 中搜尋「住在台北的 User 所寫的 Log」）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Deeply Nested Objects / 過深的巢狀結構
*   **Pitfall**: 將複雜的商業邏輯全部塞入 Nested Object，甚至 Nested 包 Nested。
*   **Consequence**: 導致 "Mapping Explosion" 和極高的 Heap 使用率。ES 預設限制 `index.mapping.nested_objects.limit` 為 10000，這是有原因的。
*   **Fix**: 考慮拆分成獨立的 Index。

### 2. Ignoring Routing in Parent-Child / 忽略父子關聯的 Routing
*   **Pitfall**: 使用 Join field 但寫入 Child 時忘記指定 `routing` 參數（通常是 Parent ID）。
*   **Consequence**: Child 可能被分片到與 Parent 不同的 Shard，導致 `has_child` 或 `has_parent` 查詢找不到資料或報錯。

### 3. Fear of Duplication / 害怕資料冗餘
*   **Pitfall**: 開發者堅持 "Single Source of Truth"，不願意在 ES 存冗餘欄位。
*   **Consequence**: 被迫使用 Application-side joins 或 Script queries，導致系統效能低落。
*   **Advice**: 硬碟很便宜，工程師的時間和使用者的等待時間很貴。**Embrace duplication.**

### 4. Updating Denormalized Data Synchronously / 同步更新反標準化資料
*   **Pitfall**: 當 User 改名時，嘗試在同一個 HTTP Request 中同步更新該 User 的 100 萬條 Logs。
*   **Consequence**: Request Timeout，系統卡死。
*   **Fix**: 使用 Message Queue (Kafka/RabbitMQ) 進行非同步的 "Fan-out" 更新，接受 "Eventual Consistency"（最終一致性）。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Choosing the Right Pattern / 決策樹：選擇正確的模式

在設計 Schema 時，請依序回答以下問題：

1.  **資料是一對一 (1:1) 關係嗎？**
    *   Yes -> **Object / Flattened** (直接放在同一個 Doc)。
    *   No -> 繼續。

2.  **資料是一對多 (1:N) 關係嗎？**
    *   Yes -> 繼續。

3.  **你需要對 N 的部分進行「獨立物件」的精確搜尋嗎？**
    *   (例如：搜尋 `specs.color: red AND specs.size: XL` 必須是同一個 spec)
    *   No (只搜單一欄位) -> **Arrays of Objects** (標準做法，效能最好)。
    *   Yes -> 繼續。

4.  **N 的數量很大，或者 N 的更新頻率遠高於 1 嗎？**
    *   (例如：商品與其 10,000 則評論)
    *   Yes -> **Parent-Child (Join field)** (注意效能懲罰)。
    *   No (N 很少，且通常一起讀寫) -> **Nested Objects**。

5.  **兩者完全無關，只是偶爾需要一起顯示？**
    *   Yes -> **Application-side Joins**。

### Implementation Checklist / 實作檢核表

- [ ] **Denormalization**: 我是否已經將常用的過濾/排序欄位（如 `category_name`, `brand_name`）複製到主 Index 中？
- [ ] **Nested**: 我是否確認 Nested 陣列不會無限增長？（若會無限增長，應改用 Parent-Child 或獨立 Index）。
- [ ] **Parent-Child**: 我是否在寫入 Child document 時正確設定了 `routing` 參數？
- [ ] **Updates**: 針對反標準化的欄位，我是否有設計非同步的更新機制（Re-indexing strategy）？
- [ ] **Mapping**: 我是否將不需要被搜尋的關聯欄位設為 `enabled: false` 或 `index: false` 以節省空間？

---

## Real-world examples｜實戰案例

### Case 1: E-commerce Product Catalog (Nested Object)
**情境**：電商商品，每個商品有多個 SKU（規格），需要根據規格組合搜尋。

```json
// Mapping (Simplified)
{
  "mappings": {
    "properties": {
      "product_name": { "type": "text" },
      "skus": {
        "type": "nested", // Key decision: Nested
        "properties": {
          "color": { "type": "keyword" },
          "size": { "type": "keyword" },
          "price": { "type": "double" }
        }
      }
    }
  }
}

// Query: Find products with a SKU that is Red AND Size M
// 若不使用 Nested，會搜到 "Red Size L" + "Blue Size M" 的商品 (False Positive)
GET /products/_search
{
  "query": {
    "nested": {
      "path": "skus",
      "query": {
        "bool": {
          "must": [
            { "term": { "skus.color": "Red" } },
            { "term": { "skus.size": "M" } }
          ]
        }
      }
    }
  }
}
```

### Case 2: User & Order History (Denormalization)
**情境**：查詢訂單，並顯示下單者的名稱。使用者改名頻率極低。

```json
// Document Structure (Denormalized)
{
  "order_id": "1001",
  "total_amount": 500,
  "created_at": "2023-10-01",
  // User info is copied here
  "user": {
    "id": "u123",
    "full_name": "Alice Wang",  // Redundant, but fast for display
    "vip_level": "Gold"         // Redundant, allows filtering orders by VIP level
  }
}
```
*   **Trade-off**: 當 Alice 升級為 Platinum 會員時，後端 Worker 會啟動，批次更新 Alice 過去所有訂單的 `user.vip_level`，或者只更新最近半年的訂單（視業務需求而定）。

### Case 3: Company & Employees (Parent-Child)
**情境**：公司資訊很少變，但員工異動頻繁，且員工數量可能很多。需要搜尋「有員工叫 David 的公司」。

```json
// 1. Define Join Field
PUT /companies
{
  "mappings": {
    "properties": {
      "my_join_field": { 
        "type": "join",
        "relations": { "company": "employee" } 
      }
    }
  }
}

// 2. Index Parent (Company)
PUT /companies/_doc/c1
{
  "name": "TechCorp",
  "my_join_field": "company"
}

// 3. Index Child (Employee) - MUST use routing
PUT /companies/_doc/e1?routing=c1
{
  "name": "David",
  "role": "Engineer",
  "my_join_field": {
    "name": "employee",
    "parent": "c1"
  }
}
```