# Mapping 設定最佳實踐與動態映射陷阱 / Mapping Best Practices & Dynamic Mapping Pitfalls

## Mental model｜心智模型

### 1. Schema on Write (寫入時定義)
Elasticsearch 雖然被稱為 "Schemaless"（無模式），但這是一個行銷術語，實際上它是 **"Schema on Write"**。當你寫入第一筆資料時，如果沒有預先定義，ES 會根據 JSON 內容「猜測」欄位型別。
- **核心觀念**：ES 的猜測通常是為了「廣泛適用」而非「效能最佳」。一旦猜錯（例如將產品 ID `12345` 猜成 `long` 而非 `keyword`），後續修正成本極高（必須 Reindex）。
- **The "Contract"**：把 Mapping 視為你與搜尋引擎之間的「合約」。你必須明確告訴它：這欄位是用來全文檢索的（Text），還是用來精確過濾與聚合的（Keyword）。

### 2. Immutability (不可變性)
一旦一個欄位被建立並寫入資料，其定義（Mapping）幾乎是**不可變更**的。
- 你不能將一個已存在的 `text` 欄位直接改成 `long`。
- **解決方案**：唯一的修改路徑是 **Create New Index (with correct mapping) -> Reindex Data -> Alias Switch**。因此，前期設計至關重要。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Explicit Mapping Over Dynamic Mapping (優先使用顯式映射)
在生產環境中，永遠不要依賴預設的 Dynamic Mapping。
- **Pattern**: 在 Index 建立時，明確定義所有已知欄位。
- **Configuration**: 設定 `dynamic: strict`（遇到未知欄位則報錯拒絕寫入）或 `dynamic: false`（忽略未知欄位，只存 `_source` 但不建立索引）。

### 2. Text vs. Keyword Strategy (文字與關鍵字策略)
這是最常見的決策點，請遵循以下矩陣：

| 需求 (Requirement) | 欄位型別 (Field Type) | 範例 (Example) |
| :--- | :--- | :--- |
| 全文檢索、模糊搜尋、分詞 (Full-text search, Tokenization) | `text` | 產品描述、文章內容 |
| 精確比對、過濾、排序、聚合 (Exact match, Filter, Sort, Aggregation) | `keyword` | Status Code, UUID, Tags, Email |
| **既要搜尋又要聚合** (Both search and aggregation) | **Multi-fields** | 產品名稱 (`name` & `name.raw`) |

### 3. Storage & Performance Optimization (儲存與效能優化)
不要為不需要的功能付費（儲存空間與 CPU）。
- **Disable `norms`**: 如果欄位不需要計算相關性評分（Relevance Scoring），例如過濾用的 Tag 或 ID，設定 `"norms": false` 可節省大量記憶體。
- **Disable `doc_values`**: 如果欄位永遠不會用於排序（Sort）或聚合（Aggregation），只用於全文搜尋，設定 `"doc_values": false`。
- **Disable `index`**: 如果欄位只需要存下來展示（在 `_source` 中），但永遠不需要被搜尋，設定 `"index": false`。

### 4. Dynamic Templates for Controlled Flexibility (使用動態樣板控制彈性)
如果你無法預知所有欄位（例如 Log 系統收集不同服務的日誌），使用 **Dynamic Templates** 來制定規則，而非依賴預設行為。
- **Rule**: "所有以 `_id` 結尾的字串欄位，自動設為 `keyword`"。
- **Rule**: "所有字串欄位預設為 `keyword`，除非特別指定"（適合 Log 場景）。

### 5. Use `flattened` for Unstructured Objects
當你有一個欄位是隨意的 JSON 物件（例如 `metadata` 或 `labels`），且你不需要對其內部欄位做複雜查詢，請使用 `flattened` 型別。這能避免 Mapping Explosion。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Mapping Explosion (映射爆炸)
- **現象**：Index 中的欄位數量過多（預設限制 1000 個）。常見於將使用者輸入的 Key 直接作為欄位名稱（例如 `user_attributes.color`, `user_attributes.size`...）。
- **後果**：Cluster state 變得巨大，Master node 記憶體耗盡，導致集群崩潰。
- **Fix**：將動態 Key 轉為 Nested 結構（`key: "color", value: "red"`）或使用 `flattened` 型別。

### 2. The "String" Trap (字串陷阱)
- **現象**：依賴預設 Mapping，ES 會將字串同時存為 `text` 和 `keyword` (multi-field)。
- **後果**：雖然方便，但會導致索引大小膨脹一倍，且寫入效能下降。
- **Fix**：明確指定只需要 `keyword` 或 `text`，除非真的兩者都需要。

### 3. Numeric Types for IDs (數字型別的 ID)
- **現象**：將 `Order ID: 123456` 存為 `long` 或 `integer`。
- **後果**：雖然看起來是數字，但你不會對 ID 做數學運算（加減乘除）或範圍查詢（Range Query 效能優化是針對 BKD tree）。對 ID 進行 `term` 查詢時，`keyword` 通常比數字型別更有效率且更直觀。
- **Fix**：如果不需要範圍查詢或數學運算，ID 請使用 `keyword`。

### 4. Deeply Nested Objects (過深的巢狀物件)
- **現象**：濫用 `nested` 型別。
- **後果**：`nested` 文件在內部是作為獨立的 hidden documents 儲存的。更新父文件會導致所有子文件重索引，且查詢效能開銷大。

---

## Checklists & workflows｜檢查清單與流程

### Mapping Design Checklist (上線前檢核)

- [ ] **Explicit Mapping**: 是否已為所有已知欄位定義 Mapping？
- [ ] **Dynamic Policy**: 生產環境是否已設定 `dynamic: strict` 或使用了受控的 `dynamic_templates`？
- [ ] **Type Check**:
    - [ ] ID 類欄位是否設為 `keyword`？
    - [ ] 不需要分詞的字串是否設為 `keyword`？
    - [ ] 只有真正需要全文檢索的欄位才設為 `text`？
- [ ] **Optimization**:
    - [ ] 不需要評分（Scoring）的 `text` 欄位是否關閉了 `norms`？
    - [ ] 不需要聚合/排序的欄位是否關閉了 `doc_values`？
    - [ ] 不需要被搜尋的欄位（只展示用）是否關閉了 `index`？
- [ ] **Safety**: 是否使用了 Index Template 來管理未來的 Index（如 `logs-2023-10`）？

### Workflow: Handling Mapping Changes (變更流程)

1. **Create New Index**: 建立一個新 Index (`v2`)，套用新的 Mapping 定義。
2. **Reindex**: 使用 `_reindex` API 將舊資料 (`v1`) 倒或是新 Index (`v2`)。
3. **Verify**: 驗證新 Index 的資料正確性與搜尋行為。
4. **Switch Alias**: 原子性地切換 Alias 指向新 Index。
   ```json
   POST /_aliases
   {
       "actions": [
           { "remove": { "index": "my-index-v1", "alias": "my-index" } },
           { "add":    { "index": "my-index-v2", "alias": "my-index" } }
       ]
   }
   ```

---

## Real-world examples｜實戰案例

### Scenario 1: Log Aggregation (日誌收集)
**情境**：收集大量應用程式 Log，欄位不固定，但我們希望預設情況下，字串都能用來做 `term` 聚合（例如 `host`, `level`），只有明確指定的 `message` 欄位做全文檢索。

```json
PUT _index_template/logs-template
{
  "index_patterns": ["logs-*"],
  "template": {
    "settings": {
      "number_of_shards": 3,
      "number_of_replicas": 1
    },
    "mappings": {
      "dynamic_templates": [
        {
          "strings_as_keywords": {
            "match_mapping_type": "string",
            "mapping": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        }
      ],
      "properties": {
        "@timestamp": { "type": "date" },
        "message": { "type": "text" }, 
        "http_status": { "type": "keyword" } // 明確指定，即使它是數字樣貌
      }
    }
  }
}
```

### Scenario 2: E-commerce Product Search (電商商品)
**情境**：商品名稱需要全文檢索，同時需要用名稱做精確排序。商品屬性（Attributes）是動態的 JSON，不需要個別索引內部欄位，只需儲存。

```json
PUT /products
{
  "mappings": {
    "dynamic": "strict", // 禁止寫入未定義欄位
    "properties": {
      "product_id": { "type": "keyword" },
      "name": {
        "type": "text",
        "analyzer": "standard", // 或特定語言 analyzer
        "fields": {
          "raw": { 
            "type": "keyword" // 用於排序或聚合
          }
        }
      },
      "description": { 
        "type": "text",
        "norms": true // 需要計算相關性評分
      },
      "tags": {
        "type": "keyword",
        "norms": false // 不需要評分，只做過濾
      },
      "attributes": {
        "type": "flattened" // 避免 Mapping Explosion，整個物件視為一個欄位
      },
      "price": { "type": "integer" }, // 價格需要 Range Query
      "created_at": { "type": "date" }
    }
  }
}
```