# 相關性評分調校實戰 / Relevance Scoring & Tuning in Practice

## Mental model｜心智模型

在關聯式資料庫（RDBMS）中，查詢結果通常是二元的（Binary）：這一行資料「符合」或「不符合」條件。但在搜尋引擎（Search Engine）中，核心問題不是「有沒有」，而是「有多像」。

要掌握 ElasticSearch 的相關性調校，你需要建立以下三個層次的心智模型：

1.  **BM25 是基石 (The Baseline)**：
    預設的評分演算法（BM25）基於三個變數：
    *   **TF (Term Frequency)**：關鍵字在該文件中出現越多次，分數越高（但在 BM25 中有飽和度上限，不會無限增長）。
    *   **IDF (Inverse Document Frequency)**：關鍵字在整個索引中越罕見（如 "Kubernetes" vs "the"），權重越高。
    *   **Field Length Norm**：欄位內容越短（如標題 vs 全文），命中關鍵字時的分數越高。
    *   *Mental Check:* 這是「文本相關性」，代表「這份文件提到這個詞的程度」。

2.  **商業邏輯是加權 (Business Logic as Boosters)**：
    單純的文本相關性通常不足以滿足業務需求。你需要疊加商業價值：
    *   **Recency**：越新的文章越重要。
    *   **Popularity**：銷量高、評價好的商品排前面。
    *   **Sponsored**：付費推廣的內容置頂。
    *   *Mental Check:* 這是「業務相關性」，通常透過 `function_score` 或 `boost` 來實現。

3.  **排序是漏斗 (Ranking as a Funnel)**：
    不要試圖對全量數據做昂貴的精細排序。
    *   **L1 (Recall)**：快速撈出前 1000 筆大概相關的資料（Cheap Query）。
    *   **L2 (Rescore)**：對這 1000 筆進行精細的腳本運算或重排序（Expensive Logic）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Query-Time Boosting (查詢時加權)
永遠優先使用 Query-Time Boosting 而非 Index-Time Boosting。
*   **Pattern**: 在 `multi_match` 中使用 `^` 符號來定義權重。
*   **Why**: 標題（Title）通常比描述（Description）更能代表使用者意圖。

```json
{
  "multi_match": {
    "query": "iphone case",
    "fields": ["title^3", "category^2", "description"],
    "type": "best_fields" // 或 cross_fields，視分詞策略而定
  }
}
```

### 2. Function Score for Business Logic (使用 Function Score 處理業務邏輯)
這是調校的核心戰場。將文本分數與數值特徵（時間、銷量）結合。
*   **Decay Functions (衰減函數)**: 用於「時間」或「地理位置」。例如：新聞發布超過 7 天後，分數開始依高斯曲線下降。
*   **Field Value Factor**: 用於「人氣」或「銷量」。
    *   *Tip*: 務必使用 `modifier: "log1p"` 或 `saturation`。因為銷量 10,000 的商品不代表比銷量 100 的商品「相關 100 倍」，避免分數失衡。

### 3. Rescoring for Performance (使用 Rescoring 優化效能)
當你需要執行複雜的 Script（例如計算向量距離、複雜的個人化邏輯）時，不要對所有匹配文件執行。
*   **Pattern**: 使用 `rescore` 僅對 Top N (e.g., window_size: 50) 結果進行二次計分。

### 4. Tie-Breaker (平手決勝局)
當多個文件分數相同時，ES 預設按 `_doc` ID 排序（無意義）。
*   **Practice**: 始終加入一個確定性的第二排序鍵（如 `created_at` 或 `id`），確保分頁瀏覽時結果順序穩定。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Whac-A-Mole" Tuning (打地鼠式調校)
*   **Anti-pattern**: 收到一個客訴說「搜尋 A 找不到 B」，於是調整參數修好了 A，結果導致 C、D、E 的排序爛掉。
*   **Solution**: 在調整前，必須建立 **Ranking Evaluation (Rank Eval API)** 或至少有一組「黃金測試集（Golden Set）」，確保調整是整體優化而非局部過擬合。

### 2. Ignoring Stopwords in Precision Context (在精確度場景忽略停用詞)
*   **Pitfall**: 過度積極地移除停用詞（如 "to", "be", "not"）。
*   **Example**: 搜尋 "To be or not to be"，如果移除停用詞，可能變成空查詢或匹配到完全無關的內容。
*   **Fix**: 在 `match` 查詢中使用 `cutoff_frequency` 或保留停用詞但給予極低權重，或者使用 Shingles。

### 3. Boosting Popularity Linearly (線性加權人氣)
*   **Pitfall**: 直接將分數乘以銷量 (`score * sales`)。
*   **Consequence**: 一個完全不相關但銷量極高的商品（如衛生紙），會出現在搜尋「iPhone」的結果首位，因為它的銷量權重壓過了文本相關性。
*   **Fix**: 使用 `log` 函數平滑化，並限制 `max_boost`。

### 4. Misunderstanding `minimum_should_match`
*   **Pitfall**: 設定為 100% 導致長尾詞搜尋無結果；設定太低導致雜訊過多。
*   **Fix**: 使用階梯式設定，例如 `"2<-25% 9<-3"` (2 個詞以下需全中，大於 2 個詞允許少匹配 25%...)。

---

## Checklists & workflows｜檢查清單與流程

### Relevance Tuning Workflow (調校工作流)

1.  **Define Metric**: 定義什麼是「好」的結果（是點擊率 CTR？還是轉換率？或是 Top 3 命中率？）。
2.  **Capture Baseline**: 使用 `_explain` API 理解當前為何某個文檔排在前面/後面。
3.  **Create Test Set**: 準備至少 20-50 個典型搜尋詞及其「預期理想排序」。
4.  **Apply Tuning**: 調整 Query DSL (Boosting, Function Score)。
5.  **Regression Test**: 跑測試集，確保沒有破壞其他查詢的品質。

### Implementation Checklist (實作檢核表)

- [ ] **Analyzers**: 是否針對不同欄位使用了正確的分詞器？（例如 `keyword` 用於過濾，`standard`/`ik` 用於搜尋）。
- [ ] **Field Weights**: 是否已提升重要欄位（如 `title`, `sku`）的權重？
- [ ] **Text Norms**: 對於不需要長度歸一化的欄位（如 Tag 標籤），是否已在 Mapping 中關閉 `norms`？
- [ ] **Function Score**: 是否對數值型加權使用了 `log` 或 `saturation` 函數防止分數爆炸？
- [ ] **Zero Results**: 是否設定了 Fallback 機制（如 Fuzziness 或放寬 `minimum_should_match`）以避免零結果？
- [ ] **Explain**: 在開發環境是否使用 `explain: true` 驗證過分數計算細節？

---

## Real-world examples｜實戰案例

### Scenario: E-commerce Product Search (電商商品搜尋)

**需求**：
1.  使用者搜尋 "Running Shoes"。
2.  標題中有 "Running Shoes" 的權重最高。
3.  商品類別為 "Shoes" 的權重次之。
4.  **新商品**（最近 30 天上架）要加分。
5.  **高評價**（Rating 4.5+）要加分，但不能讓舊的高評價商品完全壓過新商品。

**Solution DSL (Pseudo-code)**:

```json
GET /products/_search
{
  "query": {
    "function_score": {
      "query": {
        "multi_match": {
          "query": "Running Shoes",
          "fields": [
            "name^4",          // 核心匹配，權重最高
            "category^2",      // 類別匹配
            "description"
          ],
          "type": "best_fields",
          "tie_breaker": 0.3
        }
      },
      "functions": [
        {
          // 業務邏輯 1: 新商品加權 (Recency)
          "gauss": {
            "publish_date": {
              "origin": "now",
              "scale": "30d",
              "decay": 0.5     // 30天前的商品，此項分數衰減至 0.5
            }
          },
          "weight": 2
        },
        {
          // 業務邏輯 2: 高評價加權 (Popularity)
          "field_value_factor": {
            "field": "rating",
            "factor": 1.2,
            "modifier": "sqrt", // 使用平方根平滑化，避免分數差異過大
            "missing": 2.5      // 給予無評價商品一個預設中位數
          },
          "weight": 1.5
        }
      ],
      "score_mode": "sum",      // 各 function 分數相加
      "boost_mode": "multiply"  // 最終與 query 分數相乘
    }
  }
}
```

### Key Takeaway
這個查詢展示了 **Text Relevance (BM25)** 與 **Business Relevance (Gauss/Field Factor)** 的完美結合。它避免了單純依賴文字導致推薦出「十年前的絕版鞋」，也避免了單純依賴銷量導致「永遠只看得到那幾雙爆款」。