# 開發者專用的提示工程模式 / Prompt Engineering Patterns for Developers

## Mental model｜心智模型

在與 AI 協作開發時，最關鍵的思維轉變是將 Prompt 視為 **「函數呼叫 (Function Call)」** 而非單純的聊天對話。

### 1. The "Function Call" Metaphor
想像你正在呼叫一個名為 `generateCode` 的函數。如果你傳入的參數模糊不清（例如 `null` 或 `any`），回傳的結果就會充滿隨機性。
- **Context (上下文)** 是全域變數或依賴注入。
- **Instruction (指令)** 是核心邏輯。
- **Constraints (限制)** 是型別檢查與邊界條件。

### 2. Stochastic vs. Deterministic
軟體工程追求確定性 (Deterministic)，但 LLM 本質是機率模型 (Stochastic)。提示工程的核心目標，就是 **「透過增加約束條件，收斂機率分佈」**，讓 AI 的輸出落在你可接受的「正確程式碼」範圍內。

---

## Patterns & best practices｜常見模式與最佳實務

以下是針對程式碼生成與技術問題解決的高效模式：

### 1. The Persona Pattern (角色設定模式)
設定 AI 的專業背景，可以隱式地設定輸出的程式碼風格、命名慣例與技術深度。

> **Template:**
> "Act as a **[Role]** expert in **[Tech Stack]**. You prioritize **[Quality Attribute]** (e.g., performance, readability, security)."

- **Why:** 一個 "Senior Go Engineer" 寫出的錯誤處理方式，與一個 "Junior Developer" 完全不同。

### 2. Few-Shot Prompting (少樣本提示模式)
這是開發者最強大的工具。不要只告訴 AI 做什麼，給它看 **「輸入範例」** 與 **「期望的輸出範例」**。

> **Example:**
> "Convert the following raw data into our internal Type definitions.
>
> Example Input: `{"id": 1, "status": "active"}`
> Example Output: `interface User { id: number; status: 'active' | 'inactive'; }`
>
> Now convert this: `...`"

- **Why:** 範例比文字描述更能精準傳達程式碼風格 (Code Style) 與結構。

### 3. Chain-of-Thought (CoT) for Logic (思維鏈模式)
當需要處理複雜演算法或除錯時，強制 AI 逐步思考。

> **Instruction:**
> "Before generating the code, explain your logic step-by-step. Outline the algorithm complexity and potential edge cases."

- **Why:** 讓 AI 先輸出自然語言的邏輯推演，可以大幅降低邏輯錯誤（Hallucination）的機率。

### 4. The "Context-Constraint" Sandwich (上下文-限制三明治)
將核心任務夾在「上下文資訊」與「嚴格限制」之間。

1.  **Context:** 貼上相關的 Schema、現有程式碼片段或依賴版本。
2.  **Task:** 具體要做什麼（例如：寫一個 API endpoint）。
3.  **Constraints:** 不准使用哪些庫、必須遵循的命名規則、錯誤處理方式。

### 5. Iterative Refinement (迭代優化模式)
不要期望一次 Prompt 就能完美。
- **Round 1:** 生成核心邏輯。
- **Round 2:** "Now refactor this to be more functional style." (現在重構為函數式風格)
- **Round 3:** "Add extensive comments and JSDoc." (加入詳細註解與文件)

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Do It All" Prompt (萬能提示陷阱)
試圖在一個 Prompt 裡要求 AI 「設計架構、寫完後端、寫完前端並加上測試」。
- **Consequence:** 輸出會被截斷，邏輯前後不連貫，細節被忽略。
- **Fix:** **Split & Conquer**。先生成介面 (Interface)，再生成實作 (Implementation)，最後生成測試 (Tests)。

### 2. Ambiguous Adjectives (模糊形容詞)
使用 "Clean code", "Best practices", "High performance" 這種主觀詞彙。
- **Consequence:** AI 的 "Best practice" 可能過時或是你不喜歡的風格。
- **Fix:** 具體化。改用 "Follow the Airbnb Style Guide", "Use O(n) complexity", "Implement Early Return pattern"。

### 3. Ignoring the Knowledge Cutoff (忽視知識截止點)
假設 AI 知道上週才發布的 Library 版本特性。
- **Consequence:** AI 會編造不存在的 API (Hallucination)。
- **Fix:** **RAG (Retrieval-Augmented Generation)** 的手動版——將官方文件的關鍵段落直接貼在 Prompt 中作為 Context。

### 4. The "Blind Paste" (盲目複製)
直接將 AI 產出的程式碼貼進 Production，不經過審查或測試。
- **Consequence:** 引入安全漏洞或微妙的邏輯 Bug。
- **Fix:** 始終保持 **Human-in-the-loop**。AI 是副駕駛，你是機長。

---

## Checklists & workflows｜檢查清單與流程

在發送 Prompt 請求生成程式碼之前，請快速掃描此清單：

### Prompt Construction Checklist
- [ ] **Role defined?** 是否指定了專家角色與技術堆疊？
- [ ] **Context provided?** 是否提供了相關的 Type definitions、DB Schema 或現有程式碼風格？
- [ ] **Specific constraints?** 是否指定了 Library 版本（如 `Next.js 14 App Router` 而非僅 `Next.js`）？
- [ ] **Output format?** 是否指定了輸出格式（如 "Only output the code block", "Markdown format"）？
- [ ] **Examples included?** 對於複雜轉換，是否提供了 Few-Shot 範例？

### Debugging Workflow with AI
1.  **Isolate:** 提供最小可重現範例 (Minimal Reproducible Example)，而非整份檔案。
2.  **Error Log:** 貼上完整的 Stack Trace。
3.  **Hypothesis:** 詢問 "What are 3 potential causes for this error?" 而非直接求 Code。
4.  **Verify:** 要求 AI 寫一個測試案例來證明修復有效。

---

## Real-world examples｜實戰案例

### Scenario 1: Generating Unit Tests (單元測試生成)

**❌ Bad Prompt:**
> "Write tests for this function."

**✅ Good Prompt (Pattern: Context + Few-Shot + Constraints):**
> **Context:**
> I am using `Jest` and `React Testing Library`.
> Here is the component code: `[...paste code...]`
>
> **Constraints:**
> - Use `userEvent` instead of `fireEvent`.
> - Test for accessibility violations using `jest-axe`.
> - Do not test implementation details, test user behavior.
>
> **Reference Style (Few-Shot):**
> Here is an example of how we structure tests in this project:
> `[...paste a small existing test file...]`
>
> **Task:**
> Generate a test suite for the component provided above covering success, error, and loading states.

---

### Scenario 2: Refactoring Legacy Code (遺留代碼重構)

**❌ Bad Prompt:**
> "Make this code better."

**✅ Good Prompt (Pattern: Persona + CoT + Specific Goal):**
> **Role:** Act as a Senior Python Backend Engineer focused on maintainability.
>
> **Task:** Refactor the following `process_data` function.
>
> **Goals:**
> 1. Reduce Cyclomatic Complexity (remove deep nesting).
> 2. Add type hints (Python 3.10+ style).
> 3. Extract the validation logic into a separate helper function.
>
> **Process:**
> First, explain the issues you see in the current code.
> Second, outline your refactoring plan.
> Finally, show the refactored code.
>
> **Code:**
> `[...paste legacy code...]`

---

### Scenario 3: SQL Query Optimization (SQL 優化)

**✅ Good Prompt (Pattern: Context-Constraint Sandwich):**
> **Schema Context:**
> Table `Orders` (id, user_id, created_at, total)
> Table `Users` (id, region, signup_date)
> Indexes: `Orders(created_at)`, `Users(region)`
>
> **Problem:**
> The following query is slow when filtering by region and date range:
> `SELECT * FROM Orders o JOIN Users u ON o.user_id = u.id WHERE ...`
>
> **Task:**
> Optimize this query for PostgreSQL 15.
>
> **Constraints:**
> - Explain why the current query might be ignoring indexes.
> - Suggest composite indexes if necessary.
> - Provide the `EXPLAIN ANALYZE` reasoning for your solution.