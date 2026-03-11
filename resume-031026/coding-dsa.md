# 程式測驗 (DS&A) / Coding & Algorithms | Coding & Algorithms

## 1. 目標與範圍 | Goal & Scope
- 展示將抽象問題轉化為可執行、乾淨且高效程式碼的能力。
  - Demonstrate the ability to translate abstract problems into executable, clean, and efficient code.
- 驗證對基礎資料結構（Array, Map, Set, Tree）與演算法複雜度（Big O）的掌握。
  - Validate mastery of fundamental data structures (Array, Map, Set, Tree) and algorithmic complexity (Big O).
- 評估邊界情況處理（Edge Cases）與程式碼的可維護性，而不僅僅是解出答案。
  - Evaluate handling of edge cases and code maintainability, not just solving the problem.
- 針對資深工程師：面試官會更看重變數命名、模組化設計以及與實際業務場景的連結。
  - For Senior Engineers: Interviewers will prioritize variable naming, modular design, and connections to real-world business scenarios.

## 2. 簡短開場稿 | Opening Script
*此環節通常直接進入解題，但你需要先聲明使用的語言與策略。*
*This section usually jumps straight into coding, but you need to declare your language and strategy first.*

- **選擇語言與策略聲明 | Language & Strategy Declaration**
  - 「我將使用 **Python** 進行解題，因為它的語法簡潔，適合白板面試。不過在實際生產環境中，我同樣熟悉使用 **TypeScript** 或 **Java** 來處理強型別與大型系統。」
  - "I will use **Python** for this problem due to its concise syntax, which is great for whiteboard interviews. However, in production environments, I am equally comfortable using **TypeScript** or **Java** for strong typing and large-scale systems."
  - 「在開始寫程式碼之前，我想先確認一下輸入資料的限制與預期的輸出格式，並討論幾個潛在的邊界情況。」
  - "Before I start coding, I’d like to clarify the input constraints and expected output format, and discuss a few potential edge cases."

## 3. 關鍵故事與成就 | Key Stories & Achievements
*雖然這是 Coding 環節，但在解釋複雜度或優化思路時，引用過去經驗能展現資深價值。*
*While this is a coding session, referencing past experience when explaining complexity or optimization demonstrates senior value.*

- **案例一：搜尋索引與查詢優化 (Hiveel / USTOSHOP)**
  - **情境**：需要處理數百萬筆產品或車輛資料的搜尋請求。
    - **Context**: Needed to handle search requests for millions of products or vehicle data.
  - **行動**：實作了基於 ElasticSearch 的索引機制，並在後端優化了查詢邏輯（如多欄位匹配與鄰近查詢）。
    - **Action**: Implemented ElasticSearch-based indexing and optimized backend query logic (e.g., multi-field matching and proximity queries).
  - **DSA 應用**：理解 **Inverted Index（倒排索引）** 的原理，並在 Java/Node.js 層優化資料過濾演算法，減少 $O(n)$ 的線性掃描，轉為 $O(1)$ 或 $O(\log n)$ 的 lookup。
    - **DSA Application**: Understood **Inverted Index** principles and optimized data filtering algorithms in the Java/Node.js layer, reducing linear scans $O(n)$ to $O(1)$ or $O(\log n)$ lookups.

- **案例二：排程演算法與自動化 (Innova Solutions)**
  - **情境**：醫療影像平台需要處理週期性的客戶稽核報告與自動化動作（Push2Pacs）。
    - **Context**: The medical imaging platform needed to handle recurring customer audit reports and automated actions (Push2Pacs).
  - **行動**：設計了排程機制與事件驅動的處理流程。
    - **Action**: Designed scheduling mechanisms and event-driven processing flows.
  - **DSA 應用**：使用 **Queue（佇列）** 來管理任務執行順序，確保高併發下的任務不遺漏；處理時間區間重疊（Interval Overlap）問題以避免資源衝突。
    - **DSA Application**: Used **Queues** to manage task execution order ensuring no drops under high concurrency; handled **Interval Overlap** problems to avoid resource conflicts.

- **案例三：數位錢包與加密簽章 (USTOSHOP)**
  - **情境**：開發支援 Bitcoin/Ethereum 的數位錢包功能。
    - **Context**: Developed digital wallet features supporting Bitcoin/Ethereum.
  - **行動**：實作 RSA 簽章驗證與交易整合。
    - **Action**: Implemented RSA signature verification and transaction integration.
  - **DSA 應用**：涉及 **Bit manipulation（位元運算）** 與大數運算邏輯，這在處理加密雜湊或低階資料優化時非常關鍵。
    - **DSA Application**: Involved **Bit manipulation** and large number arithmetic logic, which is crucial when dealing with cryptographic hashes or low-level data optimization.

## 4. 常見追問與應對 | Likely Follow‑ups & Responses

- **Q: 你的解法時間複雜度是多少？如果是大規模資料怎麼辦？**
  - **Q: What is the time complexity of your solution? What if the data scale is massive?**
  - **A:** 「目前的解法是 $O(n \log n)$ 因為使用了排序。如果資料量大到無法放入記憶體（Stream Data），我會改用 **Heap (Priority Queue)** 來維護前 K 個元素，將空間複雜度降至 $O(k)$。」
  - **A:** "The current solution is $O(n \log n)$ due to sorting. If the data is too large to fit in memory (Stream Data), I would switch to using a **Heap (Priority Queue)** to maintain the top K elements, reducing space complexity to $O(k)$."

- **Q: 為什麼選擇 Hash Map 而不是 Array？**
  - **Q: Why did you choose a Hash Map instead of an Array?**
  - **A:** 「因為我們需要頻繁地根據 ID 查找使用者。Array 的查找是 $O(n)$，而 Hash Map 平均是 $O(1)$。雖然 Map 會消耗更多記憶體空間，但在這個 Web 服務場景下，回應速度（Latency）比些微的記憶體消耗更重要。」
  - **A:** "Because we need frequent user lookups by ID. Array lookup is $O(n)$, while Hash Map is $O(1)$ on average. Although a Map consumes more memory, in this web service scenario, response latency is prioritized over minor memory overhead."

- **Q: 這段程式碼在多執行緒（Multi-thread）環境下安全嗎？**
  - **Q: Is this code safe in a multi-threaded environment?**
  - **A:** 「目前的寫法使用了全域變數/共享狀態，這不是 Thread-safe 的。在 Java 中我會使用 `ConcurrentHashMap`，或者在設計上改用無狀態（Stateless）函數，將狀態交由資料庫或 Redis 處理（參考我在 Innova 的雲端架構經驗）。」
  - **A:** "The current implementation uses global variables/shared state, so it is not thread-safe. In Java, I would use `ConcurrentHashMap`, or design it as stateless functions, delegating state management to the DB or Redis (referencing my cloud architecture experience at Innova)."

## 5. 技術深挖提示 | Technical Deep‑Dive Prompts
*針對你的背景，面試官可能會在 Coding 題目後延伸到以下領域：*
*Given your background, interviewers might extend the coding problem into these areas:*

- **字串與陣列處理 (String/Array Manipulation)**
  - 預期：處理 JSON 解析、日誌分析或搜尋關鍵字匹配。
  - Expectation: Handling JSON parsing, log analysis, or search keyword matching.
  - 策略：熟練使用 Two Pointers（雙指標）與 Sliding Window（滑動視窗）。
  - Strategy: Master **Two Pointers** and **Sliding Window** techniques.

- **樹與圖的遍歷 (Tree/Graph Traversal)**
  - 預期：醫療影像的資料夾結構、權限繼承（Innova 經驗）或車輛分類層級。
  - Expectation: Folder structures for medical images, permission inheritance (Innova exp), or vehicle classification hierarchies.
  - 策略：熟練 BFS（廣度優先，用於最短路徑）與 DFS（深度優先，用於窮舉路徑）。
  - Strategy: Master **BFS** (for shortest path) and **DFS** (for exhaustive paths).

- **遞迴與動態規劃 (Recursion & DP)**
  - 預期：雖然較少見，但可能出現在資源分配或路徑優化問題。
  - Expectation: Less common, but may appear in resource allocation or path optimization problems.
  - 策略：先寫出暴力的遞迴解，再加上 Memoization（記憶化）優化。
  - Strategy: Write the brute-force recursive solution first, then optimize with **Memoization**.

## 6. 常見陷阱與糾正 | Pitfalls & Corrections

- **陷阱 1：沈默編碼 (Silent Coding)**
  - *錯誤*：拿到題目後埋頭苦寫，寫完才解釋。
  - *Mistake*: Diving into code immediately and explaining only after finishing.
  - *糾正*：**Think Aloud（放聲思考）**。先解釋你的思路，「我打算先用暴力法解決，然後用 Map 優化...」，確認面試官同意再動手。
  - *Correction*: **Think Aloud**. Explain your thought process first: "I plan to start with a brute-force approach, then optimize using a Map...", and get buy-in before coding.

- **陷阱 2：忽略輸入驗證 (Ignoring Input Validation)**
  - *錯誤*：假設輸入永遠是完美的（例如陣列不為空、數字為正）。
  - *Mistake*: Assuming input is always perfect (e.g., non-empty arrays, positive numbers).
  - *糾正*：作為資深工程師，必須主動寫出或口頭檢查 `if (!input) return;` 這種防禦性程式碼。
  - *Correction*: As a Senior Engineer, you must proactively write or verbally check defensive code like `if (!input) return;`.

- **陷阱 3：變數命名過於隨意 (Poor Variable Naming)**
  - *錯誤*：使用 `x`, `y`, `temp`, `arr` 等無意義命名。
  - *Mistake*: Using `x`, `y`, `temp`, `arr` without context.
  - *糾正*：使用具備業務意義的命名，如 `patientIndex`, `vehicleList`, `retryCount`。這能展現你在大型專案（如 Innova/Chunghwa）中的協作素養。
  - *Correction*: Use business-context names like `patientIndex`, `vehicleList`, `retryCount`. This shows your collaboration standards from large projects (Innova/Chunghwa).

## 7. 收尾與反問 | Closing & Questions for Interviewer

- **收尾 recap 範例 | Closing Recap Example**
  - 「總結來說，我使用 Hash Map 優化了查找速度，並考慮了空值與邊界情況。這與我在 Innova 處理醫療資料時的原則一致：效能固然重要，但程式碼的穩健性（Robustness）與可讀性更是關鍵。」
  - "To summarize, I optimized lookup speed using a Hash Map and accounted for null values and edge cases. This aligns with my principles handling medical data at Innova: while performance is important, code robustness and readability are key."

- **建議提問 | Suggested Questions**
  - 「在貴團隊目前的 codebase 中，對於程式碼效能優化與可讀性之間，通常是如何權衡的？」
  - "In your team's current codebase, how do you typically balance code performance optimization versus readability?"
  - 「團隊在 Code Review 時，對於演算法複雜度有硬性的規範嗎？還是更傾向於依賴雲端資源的擴展性？」
  - "During Code Reviews, does the team have strict standards for algorithmic complexity, or do you tend to rely more on the scalability of cloud resources?"