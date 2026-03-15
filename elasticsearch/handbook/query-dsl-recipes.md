# 實用查詢 DSL 範式：Filter vs Query Context / Practical Query DSL Recipes: Filter vs. Query Context

## Mental model｜心智模型

在撰寫 Elasticsearch 查詢時，最核心的心智模型是區分 **「這筆資料有多符合？」(How well does it match?)** 與 **「這筆資料是否符合？」(Does it match?)**。這對應到 ES 的兩個執行 Context：

### 1. The Grader vs. The Bouncer (評分員與保鑣)

- **Query Context (The Grader / 評分員)**：
  - **關注點**：相關性評分 (`_score`)。
  - **行為**：不僅判斷是否匹配，還要計算匹配程度。例如：「這篇文章提到 'Elasticsearch' 5 次，比只提到 1 次的文章更相關」。
  - **成本**：較高。需要計算 TF-IDF / BM25。
  - **適用場景**：全文檢索 (Full-text search)、模糊搜尋。

- **Filter Context (The Bouncer / 保鑣)**：
  - **關注點**：集合過濾 (Yes / No)。
  - **行為**：二元判斷。例如：「狀態是否為 `active`？」、「價格是否大於 100？」。
  - **成本**：極低。不計算分數，且結果會被 **Bitset Cache** 快取。
  - **適用場景**：精確值查找 (Exact match)、範圍查詢 (Range)、權限控管。

### 2. The Funnel Strategy (漏斗策略)

高效的查詢應該像一個漏斗：
1.  先用 **Filter** (低成本、可快取) 快速排除大量不相關的資料。
2.  剩下的資料才進入 **Query** (高成本) 進行相關性算分與排序。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. The Standard `bool` Query Structure (標準布林查詢結構)

這是最通用的萬能起手式。將查詢邏輯拆解放入 `bool` 的四個子句中：

```json
{
  "query": {
    "bool": {
      "must": [
        { "match": { "title": "search terms" }}  // 必須符合，且參與算分 (Query Context)
      ],
      "filter": [
        { "term":  { "status": "published" }},   // 必須符合，不參與算分 (Filter Context)
        { "range": { "publish_date": { "gte": "2023-01-01" }}}
      ],
      "must_not": [
        { "term": { "category": "spam" }}        // 必須不符合，不參與算分 (Filter Context)
      ],
      "should": [
        { "term": { "tags": "featured" }}        // 若符合則加分，不強制 (Query Context)
      ]
    }
  }
}
```

### 2. Filter First (過濾優先原則)

只要業務邏輯不需要根據該欄位進行「排序」或「相關性加權」，一律放入 `filter`。
- **User ID / Category ID / Status / Tags**：這些通常是二元條件，放 `filter`。
- **Date Range / Price Range**：通常不需要算分，放 `filter`。

### 3. Handling Exact Matches (精確值處理)

- 使用 `term` query 配合 `keyword` 類型的欄位。
- **Pattern**: 如果你要找的是 ID、Enum、狀態碼，請確保 Mapping 是 `keyword` 並使用 `term` (在 filter 內)。

### 4. Date Rounding for Caching (日期範圍快取優化)

Elasticsearch 的 Filter Cache 依賴於查詢語句的一致性。
- **Bad**: `"gte": "now-1h"` (毫秒級變化，導致 Cache 永遠無法命中)。
- **Good**: `"gte": "now-1h/m"` (捨入到分鐘) 或 `"gte": "now/d"` (捨入到天)。這讓同一分鐘/天內的查詢可以共用 Cache。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Term on Text" Trap (`term` 查詢用於 `text` 欄位)

這是新手最常犯的錯誤。
- **錯誤**：對 mapping 為 `text` 的欄位（如 `content`）使用 `term` 查詢。
- **原因**：`text` 欄位會經過 Analyzer (分詞)，"Hello World" 會變成 `["hello", "world"]`。`term` 查詢尋找的是精確的 "Hello World"，導致找不到資料。
- **修正**：對 `text` 欄位使用 `match`，或對 `keyword` 子欄位使用 `term`。

### 2. Scoring Everything (過度算分)

- **錯誤**：將所有條件都塞進 `must`。
- **後果**：系統浪費 CPU 計算 `status="active"` 的相關性分數（這毫無意義，因為狀態只有是或否，沒有「比較 active」這種事）。
- **修正**：將非全文檢索的條件移至 `filter`。

### 3. Deep Pagination with `from` + `size`

- **錯誤**：使用 `from: 10000, size: 10` 進行深分頁。
- **後果**：ES 必須算出前 10010 筆資料的分數並排序，然後丟棄前 10000 筆，極度消耗記憶體與 CPU。
- **修正**：使用 `search_after` (推薦) 或 Scroll API (僅限資料匯出)。

### 4. Overusing Wildcards (濫用萬用字元)

- **錯誤**：`*keyword*` (Leading wildcard)。
- **後果**：無法利用 Inverted Index 的前綴優化，必須掃描所有 Term，效能極差。

---

## Checklists & workflows｜檢查清單與流程

在送出 Query DSL 到 Production 前，請執行此檢查：

### Decision Tree: Filter vs. Query

1. **這個條件是否影響結果的排序？**
   - 是 (例如：包含越多關鍵字越好) → **Query Context (`must` / `should`)**
   - 否 (例如：只要包含這個 ID 就好) → **Filter Context (`filter` / `must_not`)**

2. **這個欄位是文字搜尋 (Full-text) 還是結構化資料 (Structured)？**
   - 文字搜尋 (內容、標題) → 使用 **`match`**
   - 結構化資料 (ID、狀態、標籤) → 使用 **`term`** (記得檢查 Mapping 是否為 `keyword`)

### Optimization Checklist

- [ ] **Context Check**: 是否將所有不需要算分的條件都移到了 `filter` 區塊？
- [ ] **Mapping Check**: 用於 `term` 查詢的欄位是否為 `keyword` 類型？
- [ ] **Date Check**: 範圍查詢是否使用了時間捨入 (Rounding) 以利用 Cache？
- [ ] **Should Check**: 如果 `bool` 查詢中只有 `should` 子句，是否設定了 `minimum_should_match`？(否則可能回傳空集合或非預期結果)
- [ ] **Complexity Check**: 是否巢狀過深？(過多的 Nested Query 會嚴重影響效能)。

---

## Real-world examples｜實戰案例

### Scenario: E-commerce Product Search (電商商品搜尋)

**需求**：
1. 使用者搜尋 "running shoes" (全文檢索)。
2. 只顯示 "In Stock" (庫存) 的商品。
3. 價格範圍在 $50 - $200 之間。
4. 如果商品是 "Nike" (品牌)，稍微提高排序權重，但不要過濾掉其他品牌。
5. 排除 "Kids" 分類的商品。

**Implementation (DSL)**:

```json
GET /products/_search
{
  "query": {
    "bool": {
      // 1. Query Context: 負責 "How well does it match?"
      "must": [
        { 
          "match": { 
            "name": {
              "query": "running shoes",
              "operator": "and" // 提升精確度，兩個詞都要有
            }
          }
        }
      ],
      // 2. Filter Context: 負責 "Yes/No"，且會被 Cache
      "filter": [
        { "term": { "status": "in_stock" }},  // 精確值
        { "range": { "price": { "gte": 50, "lte": 200 }}}, // 範圍
        { "term": { "category.keyword": "shoes" }} // 確保是大分類
      ],
      // 3. Filter Context (Negative): 排除條件
      "must_not": [
        { "term": { "department": "kids" }}
      ],
      // 4. Query Context (Boost): 加分項，不影響納入與否，只影響排序
      "should": [
        { 
          "term": { 
            "brand.keyword": {
              "value": "Nike",
              "boost": 2.0 // 權重加倍
            }
          }
        }
      ]
    }
  },
  "_source": ["id", "name", "price", "brand"], // 只取需要的欄位，減少網路傳輸
  "size": 20
}
```

### Key Takeaways from Example:
- **Precision (精確率)**：透過 `operator: "and"` 和 `filter` 確保結果相關。
- **Recall (召回率)**：`should` 提供了個性化排序而不縮減結果集。
- **Performance (效能)**：大部分篩選邏輯 (Status, Price, Department) 都在 Filter Context 處理，減輕算分負擔。