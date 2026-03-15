# 前言與學習目標
# Introduction and Learning Objectives

在資深工程師的搜尋系統設計中，"能搜到資料" 僅僅是及格線，真正的挑戰在於 "如何讓最相關的資料排在第一位"。這不僅涉及文字匹配（Text Matching），更涉及業務邏輯（Business Logic）與相關性分數（Relevance Scoring）的權衡。本章將深入探討 ElasticSearch 的核心排序機制。

In the system design of search engines for senior engineers, "retrieving data" is merely the baseline. The real challenge lies in "ranking the most relevant data at the top." This involves not just Text Matching, but a trade-off between Business Logic and Relevance Scoring. This chapter dives deep into the core ranking mechanisms of ElasticSearch.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **深入理解 BM25 演算法**：解釋它與傳統 TF-IDF 的差異，以及如何透過參數調整（Tuning）來優化長短文本的搜尋結果。
    **Deeply understand the BM25 algorithm**: Explain how it differs from traditional TF-IDF and how to tune parameters to optimize search results for long and short texts.
2.  **掌握 Function Score 與 Scripting**：在不犧牲過多效能的前提下，將業務指標（如銷量、評價、地理距離）融入排序邏輯。
    **Master Function Score and Scripting**: Integrate business metrics (e.g., sales volume, ratings, geo-distance) into ranking logic without sacrificing too much performance.
3.  **實作高效能的 Rescoring 策略**：利用 `rescore` 機制解決 "複雜排序邏輯導致的高延遲" 問題，平衡精準度與回應速度。
    **Implement high-performance Rescoring strategies**: Use the `rescore` mechanism to solve "high latency caused by complex ranking logic," balancing precision and response speed.

---

# 核心觀念與心智模型
# Core Concepts & Mental Model

## 1. 從 TF-IDF 到 BM25：飽和度與正規化
## 1. From TF-IDF to BM25: Saturation and Normalization

ElasticSearch 5.0 之後，預設的相關性演算法由 TF-IDF 轉為 **Okapi BM25**。對於資深工程師而言，理解其數學直覺至關重要。

Since ElasticSearch 5.0, the default relevance algorithm has shifted from TF-IDF to **Okapi BM25**. For senior engineers, understanding its mathematical intuition is crucial.

*   **TF (Term Frequency) Saturation (詞頻飽和度)**:
    *   在傳統 TF-IDF 中，一個詞出現越多次，分數線性增長。這在長文中會導致偏差。
    *   BM25 引入了飽和機制（Saturation）。當一個詞出現次數達到一定程度後，對分數的貢獻會趨於平緩（asymptotically approaches a limit）。這意味著出現 100 次 "Apple" 的文章，其相關性不一定比出現 10 次的高出 10 倍。
    *   In traditional TF-IDF, the score grows linearly as a term appears more often. This creates bias in long documents.
    *   BM25 introduces a saturation mechanism. After a term appears a certain number of times, its contribution to the score plateaus. This means an article with 100 occurrences of "Apple" is not necessarily 10 times more relevant than one with 10 occurrences.

*   **Field Length Normalization (欄位長度正規化)**:
    *   BM25 會懲罰過長的欄位。如果兩個文檔都包含一次關鍵字，較短的文檔通常被認為相關性更高（因為關鍵字密度較大）。
    *   BM25 penalizes overly long fields. If two documents both contain the keyword once, the shorter document is usually considered more relevant (due to higher keyword density).

## 2. 排序的層次模型：Text vs. Business
## 2. The Layered Model of Ranking: Text vs. Business

在系統設計中，我們通常將排序視為兩個訊號的疊加：
In system design, we typically view ranking as a superposition of two signals:

1.  **Lexical Score (詞彙分數)**: 基於 BM25，代表 "這份文件與查詢詞的文字匹配程度"。
    **Lexical Score**: Based on BM25, representing "how well this document matches the query terms textually."
2.  **Boosting Score (加權分數)**: 基於業務邏輯（如 `popularity`, `recency`, `ctr`）。
    **Boosting Score**: Based on business logic (e.g., `popularity`, `recency`, `ctr`).

**心智模型 (Mental Model)**:
想像你在面試候選人。BM25 是 "關鍵字匹配"（履歷上有多少相關技能），而 Function Score 是 "加權調整"（學歷、年資、推薦信）。最終錄取分數是兩者的綜合函數，而非單一維度。

**Mental Model**:
Imagine interviewing candidates. BM25 is "keyword matching" (how many relevant skills are on the resume), while Function Score is "weighted adjustment" (education, years of experience, references). The final hiring score is a composite function of both, not a single dimension.

---

# 實務場景與系統設計視角
# Real-World & System Design View

## 1. 電商搜尋排序 (E-commerce Search Ranking)
## 1. E-commerce Search Ranking

在電商場景中，純文字相關性往往不足以轉化為銷售。
In e-commerce scenarios, pure text relevance is often insufficient to convert into sales.

*   **需求**: 用戶搜尋 "Running Shoes"。
    **Requirement**: User searches for "Running Shoes".
*   **挑戰**: 剛上架的新品（無銷量）與熱銷舊品（高銷量）如何排序？庫存不足的商品是否該降權？
    **Challenge**: How to rank newly listed items (no sales) vs. best-selling older items (high sales)? Should low-stock items be down-ranked?
*   **設計**:
    *   Base Query: `multi_match` (Title, Description).
    *   Function Score:
        *   `field_value_factor`: log(sales_count) —— 銷量越高分數越高，但取對數避免強者恆強。
        *   `gauss` (Decay Function): 針對 `publish_date` 做衰減，新品給予一定優勢。
        *   `script_score`: 若 `inventory < 5`，強制乘以 0.5 降權。

## 2. 效能與架構權衡 (Performance & Architecture Trade-offs)
## 2. Performance & Architecture Trade-offs

*   **Scripting 的代價**:
    在 ES 中使用 `script`（Painless 語言）非常靈活，但會阻止 ES 利用某些底層優化（如 Block-MAX WAND 演算法來跳過低分文檔）。
    **The Cost of Scripting**:
    Using `script` (Painless language) in ES is very flexible, but it prevents ES from utilizing certain low-level optimizations (like the Block-MAX WAND algorithm to skip low-scoring documents).

*   **Rescoring Pattern**:
    若排序邏輯極其複雜（例如涉及向量運算或複雜數學模型），不要對全量數據（100萬筆）進行計算。
    **Rescoring Pattern**:
    If the ranking logic is extremely complex (e.g., involving vector operations or complex mathematical models), do not compute it for the entire dataset (e.g., 1 million records).
    *   **Phase 1**: 用簡單的 BM25 + 輕量 Filter 取出 Top 500。
    *   **Phase 1**: Use simple BM25 + lightweight Filters to retrieve the Top 500.
    *   **Phase 2**: 使用 `rescore` 僅對這 500 筆進行昂貴的 Script 計算。
    *   **Phase 2**: Use `rescore` to perform expensive Script calculations only on these 500 records.

---

# 逐步示例：自定義排序邏輯
# Walkthrough / Example: Custom Ranking Logic

## 背景 (Context)
## Context

假設我們正在設計一個 **技術部落格搜尋引擎**。我們希望搜尋結果不僅相關，還要考慮文章的 "熱度"（按讚數）和 "時效性"（發布時間）。

Suppose we are designing a **Tech Blog Search Engine**. We want search results to be not only relevant but also account for the article's "popularity" (likes) and "recency" (publish date).

## 1. 基礎查詢 (Naive Approach)
## 1. Naive Approach

最簡單的做法是只用 `match`。這完全依賴 BM25。

The simplest approach is using only `match`. This relies entirely on BM25.

```json
GET /blogs/_search
{
  "query": {
    "match": {
      "content": "elasticsearch tuning"
    }
  }
}
```

**問題**: 一篇 5 年前的過時文章可能因為關鍵字密度高而排在第一。
**Problem**: An outdated article from 5 years ago might rank first due to high keyword density.

## 2. 引入 Function Score (Function Score Query)
## 2. Function Score Query

我們使用 `function_score` 來混合多種權重。

We use `function_score` to blend multiple weights.

```json
GET /blogs/_search
{
  "query": {
    "function_score": {
      "query": {
        "match": { "content": "elasticsearch tuning" }
      },
      "functions": [
        {
          // 1. Popularity Boost: Logarithmic scaling
          // 1. 熱度加權：對數平滑
          "field_value_factor": {
            "field": "likes",
            "factor": 1.2,
            "modifier": "log1p",
            "missing": 1
          }
        },
        {
          // 2. Recency Decay: Gauss function
          // 2. 時效衰減：高斯函數
          "gauss": {
            "publish_date": {
              "origin": "now",
              "scale": "30d",
              "offset": "7d",
              "decay": 0.5
            }
          }
        }
      ],
      "score_mode": "multiply", // How functions combine (sum, multiply, avg)
      "boost_mode": "multiply"  // How function score combines with query score
    }
  }
}
```

**解析 (Analysis)**:
*   **`log1p`**: 使用 `log(1 + likes)`。這很重要，因為 10 vs 100 的讚數差距很大，但 10000 vs 10100 的差距對相關性影響很小。
*   **`gauss`**: 定義了一個衰減曲線。`scale: 30d` 和 `decay: 0.5` 表示文章發布 30 天後，其時效分數會降為 0.5。`offset: 7d` 表示最近 7 天內的文章不衰減（滿分）。

## 3. 高效能優化：Rescoring (Performance Optimization)
## 3. Performance Optimization: Rescoring

如果我們的邏輯更複雜（例如需要 script 計算用戶個性化分數），我們應該將其移至 Rescore 階段。

If our logic is more complex (e.g., requiring script calculation for user personalization scores), we should move it to the Rescore phase.

```json
GET /blogs/_search
{
  "query": {
    "match": { "content": "elasticsearch tuning" }
  },
  "rescore": {
    "window_size": 50, // Only rescore the top 50 results
    "query": {
      "rescore_query": {
        "function_score": {
          "script_score": {
            "script": {
              "source": "Math.log10(doc['likes'].value + 2) * params.user_weight",
              "params": {
                "user_weight": 1.5
              }
            }
          }
        }
      },
      "query_weight": 1.0,
      "rescore_query_weight": 2.0 // Give high importance to the rescore logic
    }
  }
}
```

**為何這樣做可行？ (Why this works?)**
ES 只需要對數百萬筆資料做快速的 BM25 檢索，然後僅對前 50 筆執行昂貴的 Script 計算。這在 High-Traffic 系統中是標準模式。

ES only needs to perform fast BM25 retrieval on millions of records, and then execute the expensive Script calculation only on the top 50. This is a standard pattern in High-Traffic systems.

---

# 常見錯誤與反模式
# Common Pitfalls & Anti-patterns

## 1. 誤用 Sort 代替 Score
## 1. Misusing Sort instead of Score

*   **錯誤**: 直接使用 `sort: [{ "price": "asc" }]` 來排序搜尋結果。
    **Mistake**: Directly using `sort: [{ "price": "asc" }]` to order search results.
*   **後果**: 這會完全忽略相關性（BM25）。搜尋 "iPhone" 可能會因為排序而把一個由 "iPhone case" 配件（價格低）排在真正的 iPhone 手機前面。
    **Consequence**: This completely ignores relevance (BM25). Searching for "iPhone" might rank a cheap "iPhone case" accessory ahead of the actual iPhone phone due to the sort order.
*   **修正**: 應該將價格因素放入 `function_score` 或使用 `sort` 作為次級排序（Tie-breaker），或者使用 `rank_feature` 欄位類型。
    **Fix**: Incorporate price into `function_score`, use `sort` as a secondary tie-breaker, or use the `rank_feature` field type.

## 2. 線性加權陷阱
## 2. The Linear Boosting Trap

*   **錯誤**: 直接將銷量（Sales）加到分數上：`score = bm25_score + sales`。
    **Mistake**: Directly adding sales to the score: `score = bm25_score + sales`.
*   **後果**: 銷量高的商品會永遠霸榜，無論關鍵字匹配度多差。BM25 分數通常在 0-10 之間，而銷量可能是 10,000。
    **Consequence**: High-sales items will dominate the top results forever, regardless of how poor the keyword match is. BM25 scores are usually between 0-10, while sales could be 10,000.
*   **修正**: 始終使用 `log` 函數平滑數值，或將其標準化（Normalize）到 0-1 區間後再相乘。
    **Fix**: Always use `log` functions to smooth values, or normalize them to a 0-1 range before multiplying.

## 3. 在 Query 階段使用複雜 Script
## 3. Using Complex Scripts in Query Phase

*   **錯誤**: 在主查詢的 `function_score` 中使用複雜的 Painless script 處理所有文檔。
    **Mistake**: Using complex Painless scripts inside the main query's `function_score` to process all documents.
*   **後果**: CPU 使用率飆升，Latency 增加，且無法利用 Cache。
    **Consequence**: CPU usage spikes, Latency increases, and Caching becomes ineffective.
*   **修正**: 使用 `rescore`，或在 Indexing 階段預先計算好分數存入欄位（Denormalization）。
    **Fix**: Use `rescore`, or pre-calculate scores during the Indexing phase and store them in a field (Denormalization).

---

# 面試與實務問答切入點
# Interview & Discussion Hooks

## Q1: 如何設計一個同時考慮 "文字相關性" 與 "地理距離" 的搜尋功能？
## Q1: How do you design a search function that considers both "text relevance" and "geo-distance"?

*   **高分回答要點**:
    *   **Filter vs Scoring**: 首先用 `filter` (Geo-bounding box / distance) 排除過遠的結果（硬過濾，效能好）。
    *   **Decay Function**: 使用 `function_score` 的 `gauss` 或 `exp` 函數對距離進行衰減評分（軟排序）。
    *   **Trade-off**: 解釋為何不用 `sort` 按距離排（會犧牲關鍵字相關性）。
    *   **Key Points**:
        *   **Filter vs Scoring**: First use `filter` (Geo-bounding box / distance) to exclude results that are too far (hard filter, good performance).
        *   **Decay Function**: Use `gauss` or `exp` functions in `function_score` to apply decay scoring based on distance (soft ranking).
        *   **Trade-off**: Explain why not to simply `sort` by distance (it sacrifices keyword relevance).

## Q2: 我們的搜尋結果中，長文章總是比短文章排名低，即使長文章內容更豐富，為什麼？如何解決？
## Q2: In our search results, long articles always rank lower than short ones, even if the long articles are richer in content. Why? How to fix it?

*   **高分回答要點**:
    *   **BM25 Root Cause**: 指出 BM25 的長度正規化參數 `b` (length normalization)。預設情況下，BM25 認為短文中出現關鍵字比長文中出現更重要。
    *   **Tuning**: 可以調整 `b` 參數（預設 0.75）。降低 `b` 值會減少長度對分數的懲罰。
    *   **Alternative**: 檢查是否錯誤地使用了 `TF-IDF` 或者 Mapping 設定問題。
    *   **Key Points**:
        *   **BM25 Root Cause**: Point to the BM25 length normalization parameter `b`. By default, BM25 considers a keyword in a short text more significant than in a long text.
        *   **Tuning**: Adjust the `b` parameter (default 0.75). Lowering `b` reduces the penalty for length.
        *   **Alternative**: Check if `TF-IDF` is mistakenly used or if there are Mapping configuration issues.

## Q3: 在高併發場景下，如何優化帶有複雜 Script 的排序查詢？
## Q3: How do you optimize ranking queries with complex Scripts in high-concurrency scenarios?

*   **高分回答要點**:
    *   **Rescoring**: 僅對 Top N 結果應用 Script。
    *   **Pre-computation**: 將 Script 邏輯移至 Indexing time（寫入時計算），存為靜態欄位。
    *   **Rank Feature**: 使用 ES 7.x+ 的 `rank_feature` 欄位類型，這是專為提升數值型 boosting 效能設計的。
    *   **Key Points**:
        *   **Rescoring**: Apply the Script only to the Top N results.
        *   **Pre-computation**: Move Script logic to Indexing time (compute on write) and store as a static field.
        *   **Rank Feature**: Use the `rank_feature` field type in ES 7.x+, designed specifically for high-performance numeric boosting.

---

# 小結與後續延伸
# Summary & Next Steps

## 記憶錨點 (Key Takeaways)
*   **BM25 vs TF-IDF**: BM25 引入了詞頻飽和（Saturation）與長度正規化（Length Normalization），是現代搜尋的預設標準。
*   **Function Score**: 是實現自定義排序的核心工具，支援 `field_value_factor`（數值加權）、`gauss`（衰減函數）與 `script_score`（腳本）。
*   **Rescore Pattern**: 解決效能問題的黃金法則——"先粗排，後精排"。
*   **Logarithmic Smoothing**: 處理業務指標（如銷量、點擊）時，務必使用對數平滑，避免數值偏差過大。
*   **Ranking != Sorting**: 排序（Sorting）是絕對順序，評分（Scoring）是相對權重，搜尋場景通常需要後者。

## 後續延伸 (Next Steps)
*   **Next Chapter**: `Aggregations & Analytics` (聚合與分析)。學習如何利用 ES 進行即時的數據統計與 Faceted Search（分面搜尋）。
*   **Advanced Reading**: 研究 `Learning to Rank` (LTR) plugin，這是將機器學習模型引入 ES 排序的高階實踐。