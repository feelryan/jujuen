# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，AI 輔助開發不僅僅是使用 GitHub Copilot 自動補全程式碼，更是一種思維模式的轉變。本章旨在將你的視角從「尋求答案」轉變為「引導思考」，讓你能夠駕馭 LLM (Large Language Model) 處理高複雜度的工程問題。

For senior engineers, AI-assisted development is more than just using GitHub Copilot for code completion; it is a paradigm shift in mindset. This chapter aims to shift your perspective from "seeking answers" to "guiding thought," enabling you to harness LLMs (Large Language Models) to tackle high-complexity engineering problems.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **運用進階提示技巧 (Apply Advanced Prompting Techniques)**：熟練使用 Chain-of-Thought (CoT) 與 Few-Shot Prompting 來解決非顯而易見 (non-trivial) 的邏輯問題與架構設計。
    Master Chain-of-Thought (CoT) and Few-Shot Prompting to solve non-trivial logic problems and architectural designs.
2.  **管理上下文策略 (Manage Context Strategy)**：理解 Context Window 的限制與運作機制，學會如何篩選最關鍵的資訊以獲得高品質的 AI 回應。
    Understand the limitations and mechanics of the Context Window, and learn how to curate the most critical information to obtain high-quality AI responses.
3.  **建立 AI 協作模式 (Establish AI Collaboration Patterns)**：將 AI 定位為一個「博學但需要監督的資深結對程式設計師 (Pair Programmer)」，而非單純的搜尋引擎。
    Position AI as a "knowledgeable but supervised Senior Pair Programmer" rather than a simple search engine.
4.  **識別幻覺與邊界 (Identify Hallucinations & Boundaries)**：在 System Design 面試或實務中，快速判斷 AI 建議的方案是否可行，並識別潛在的資安與效能風險。
    Quickly assess the feasibility of AI-suggested solutions in System Design interviews or practice, and identify potential security and performance risks.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 LLM 作為無狀態的推論引擎 (LLM as a Stateless Inference Engine)

請將 LLM 想像成一個**沒有長期記憶、但閱讀速度極快且博學的資深實習生**。它不知道你昨天寫了什麼 code，除非你在當下的對話 (Context) 中明確告訴它。

Imagine the LLM as a **senior intern with no long-term memory but incredible reading speed and vast knowledge**. It does not know what code you wrote yesterday unless you explicitly tell it in the current conversation (Context).

*   **Context Window (上下文視窗)**：這是 AI 的「工作記憶體 (Working Memory)」。對於資深工程師來說，Prompt Engineering 的本質就是**記憶體管理 (Memory Management)**——如何在這個有限的空間內，放入最相關的 Interface 定義、資料庫 Schema 或錯誤日誌，以換取最精準的輸出。
    *   **Context Window**: This is the AI's "Working Memory." For senior engineers, Prompt Engineering is essentially **Memory Management**—how to fit the most relevant Interface definitions, Database Schemas, or error logs into this limited space to get the most precise output.

## 2.2 提示工程的層次 (Hierarchy of Prompt Engineering)

我們將提示工程分為三個層次，資深工程師應主要運作在 Level 2 與 Level 3：

We categorize prompt engineering into three levels, with senior engineers primarily operating at Level 2 and Level 3:

1.  **Zero-Shot (Level 1)**：直接提問。「寫一個 Python function 處理 JSON。」
    Direct question. "Write a Python function to process JSON."
2.  **Few-Shot (Level 2)**：提供範例。「這是我們公司的 Error Handling 風格（附上程式碼），請依照此風格撰寫新的 API。」這能顯著提升程式碼的一致性。
    Providing examples. "Here is our company's Error Handling style (code attached); please write a new API following this style." This significantly improves code consistency.
3.  **Chain-of-Thought (Level 3)**：強迫模型「展示計算過程」。在要求產出程式碼前，先要求 AI 解釋邏輯步驟。這能大幅減少邏輯漏洞 (Logical Flaws)。
    Forcing the model to "show its work." Asking the AI to explain the logical steps *before* generating the code. This drastically reduces logical flaws.

## 2.3 區分：Prompting vs. Fine-tuning vs. RAG

*   **Prompting**: 在 Context Window 內解決問題（本章重點）。
    Solving problems within the Context Window (Focus of this chapter).
*   **Fine-tuning**: 改變模型的權重，讓它學會新的語言或極度專業的領域知識（成本高，通常非首選）。
    Changing model weights to teach it a new language or highly specialized domain knowledge (High cost, usually not the first choice).
*   **RAG (Retrieval-Augmented Generation)**: 動態地從外部知識庫檢索資訊並注入 Prompt（這是 Prompting 的延伸應用）。
    Dynamically retrieving information from an external knowledge base and injecting it into the Prompt (An extension of Prompting).

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在 Production 環境與大型系統設計中，AI 輔助開發不僅是寫 code，更是架構決策的輔助。

In production environments and large-scale system design, AI-assisted development is not just about writing code; it's an aid for architectural decisions.

## 3.1 遺留系統重構 (Legacy System Refactoring)

這是 AI 最強大的應用場景之一。
This is one of the most powerful use cases for AI.

*   **場景 (Scenario)**：你需要將一個複雜的 Python Monolith 模組重寫為 Go Microservice。
    You need to rewrite a complex Python Monolith module into a Go Microservice.
*   **做法 (Approach)**：不要直接貼程式碼叫它翻譯。
    Do not just paste the code and ask it to translate.
    1.  **Extract Logic**: 先貼上 Python code，要求 AI 用自然語言總結業務邏輯 (Business Rules extraction)。
        Paste the Python code first and ask the AI to summarize the Business Rules in natural language.
    2.  **Verify**: 人工確認邏輯無誤。
        Manually verify the logic.
    3.  **Generate**: 提供 Go 的 Struct 定義，要求 AI 根據總結的邏輯實作。
        Provide the Go Struct definitions and ask the AI to implement based on the summarized logic.
*   **價值 (Value)**：確保業務邏輯在語言轉換過程中不丟失，且符合 Go 的 Idiomatic 寫法。
    Ensures business logic is not lost during translation and adheres to Go's idiomatic style.

## 3.2 測試驅動開發增強 (Enhanced TDD)

*   **場景 (Scenario)**：為一個涉及多個 Microservices 的 API 撰寫 Integration Test。
    Writing Integration Tests for an API involving multiple Microservices.
*   **做法 (Approach)**：先將 Swagger/OpenAPI spec 和相關的 Data Model 貼給 AI，要求它生成測試案例 (Test Cases)，包含 Happy Path 與 Edge Cases。
    Feed the Swagger/OpenAPI spec and relevant Data Models to the AI, asking it to generate Test Cases, including Happy Paths and Edge Cases.
*   **可維護性影響 (Maintainability Impact)**：AI 擅長生成 boilerplate code，這讓工程師更願意撰寫完整的測試，從而提升系統穩定性。
    AI excels at generating boilerplate code, making engineers more willing to write comprehensive tests, thereby improving system stability.

## 3.3 架構評審 (Architecture Review)

*   **場景 (Scenario)**：你設計了一個分散式鎖 (Distributed Lock) 機制。
    You designed a Distributed Lock mechanism.
*   **做法 (Approach)**：描述你的設計（例如使用 Redis Redlock），然後 Prompt：「扮演一位資深分散式系統專家，請找出這個設計中可能存在的 Race Condition 或單點故障。」
    Describe your design (e.g., using Redis Redlock), then Prompt: "Act as a senior distributed systems expert. Please identify potential Race Conditions or Single Points of Failure in this design."

---

# 4. 逐步示例 (Walkthrough / Example)

## 案例：優化複雜的 SQL 查詢 (Optimizing a Complex SQL Query)

**背景 (Context)**：
你正在處理一個 PostgreSQL 資料庫，有一個查詢執行緩慢。該查詢涉及 `Orders`, `OrderItems`, 和 `Products` 表的 Join，目的是找出「過去一個月內銷售總額最高的前 10 名產品類別」。

You are working with a PostgreSQL database and have a slow-running query. The query involves joining `Orders`, `OrderItems`, and `Products` tables to find the "Top 10 product categories by total sales in the last month."

### 步驟 1：Naive Approach (Level 1 Prompting)

**Prompt:**
> "Optimize this SQL query for me: `SELECT ...`"

**結果 (Result)**：
AI 可能會建議加索引 (Index)，或重寫語法，但通常缺乏對資料分佈的理解，優化效果有限。
The AI might suggest adding indexes or rewriting syntax, but it often lacks understanding of data distribution, leading to limited optimization.

### 步驟 2：Advanced Approach with CoT & Context (Level 3 Prompting)

**Prompt:**

> **Role**: Act as a PostgreSQL Performance Expert.
>
> **Context**:
> 1.  **Schema**:
>     - `Orders (id, user_id, created_at, status)` - ~10M rows.
>     - `OrderItems (id, order_id, product_id, quantity, price)` - ~50M rows.
>     - `Products (id, category_id, name)` - ~100k rows.
> 2.  **Problem**: The following query takes 5 seconds to run. We need it under 200ms.
> 3.  **Current Indexes**: `Orders(created_at)`, `OrderItems(order_id)`.
>
> **Query**:
> ```sql
> SELECT p.category_id, SUM(oi.quantity * oi.price) as total_sales
> FROM Orders o
> JOIN OrderItems oi ON o.id = oi.order_id
> JOIN Products p ON oi.product_id = p.id
> WHERE o.created_at >= NOW() - INTERVAL '1 month'
> GROUP BY p.category_id
> ORDER BY total_sales DESC
> LIMIT 10;
> ```
>
> **Task**:
> 1.  **Analyze**: Explain the execution plan and why it might be slow (Chain-of-Thought).
> 2.  **Strategy**: Propose 2 different strategies (e.g., Indexing vs. Denormalization).
> 3.  **Solution**: Provide the optimized SQL or DDL for the best strategy.

**AI 的思考過程 (AI's Chain-of-Thought)**：
1.  **Analyze**: AI 會指出 `JOIN` 操作在大表 (`OrderItems`) 上非常昂貴。雖然 `Orders` 有時間索引，但過濾後的 ID 列表去 Join 50M 行的 `OrderItems` 仍然很慢。
    AI points out that the `JOIN` operation on the large table (`OrderItems`) is expensive. Although `Orders` has a time index, joining the filtered ID list with 50M rows of `OrderItems` is still slow.
2.  **Strategy**:
    *   *Option A*: 複合索引 (Composite Index)。在 `OrderItems` 上建立覆蓋索引 (Covering Index)。
    *   *Option B*: 預計算 (Pre-aggregation)。建立一個 Materialized View。
3.  **Solution**: AI 建議建立 Materialized View 或 Summary Table，因為這是一個典型的 OLAP 查詢跑在 OLTP 系統上。

**為何這樣做有效 (Why this works)**：
你提供了**資料規模 (Cardinality)** 和 **現有索引 (Constraints)**。AI 不再是猜測語法，而是進行**成本估算 (Cost Estimation)**。這就是資深工程師使用 AI 的方式。
You provided **Data Cardinality** and **Current Constraints**. The AI is no longer guessing syntax but performing **Cost Estimation**. This is how senior engineers use AI.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 上下文污染 (Context Pollution)

*   **錯誤 (Mistake)**：為了省事，把整個檔案或無關的 Config 全部貼進 Prompt。
    Copy-pasting entire files or irrelevant Configs into the Prompt to save time.
*   **後果 (Consequence)**：LLM 的注意力機制 (Attention Mechanism) 會被稀釋，導致它關注到錯誤的變數或邏輯，甚至產生幻覺。
    The LLM's Attention Mechanism gets diluted, causing it to focus on wrong variables or logic, or even hallucinate.
*   **修正 (Fix)**：只提供相關的 Interface、Function Signature 和必要的 Context。使用 `<context>...</context>` 標籤來明確分隔參考資料。
    Provide only relevant Interfaces, Function Signatures, and necessary Context. Use `<context>...</context>` tags to clearly delimit reference material.

## 5.2 盲目信任生成的 Library (Blind Trust in Generated Libraries)

*   **錯誤 (Mistake)**：直接 `npm install` 或 `pip install` AI 建議的套件。
    Directly running `npm install` or `pip install` for packages suggested by AI.
*   **後果 (Consequence)**：AI 可能會產生「幻覺套件 (Hallucinated Packages)」，這是一個已知的供應鏈攻擊向量 (Supply Chain Attack vector)。駭客會註冊這些常見的幻覺名稱並植入惡意程式碼。
    AI can generate "Hallucinated Packages," a known Supply Chain Attack vector. Hackers register these common hallucinated names and inject malicious code.
*   **修正 (Fix)**：永遠先 Google 確認該套件存在且信譽良好。
    Always Google first to verify the package exists and is reputable.

## 5.3 放棄架構主導權 (Surrendering Architectural Agency)

*   **錯誤 (Mistake)**：問 AI「我應該用 MongoDB 還是 PostgreSQL？」並直接照做。
    Asking AI "Should I use MongoDB or PostgreSQL?" and following it blindly.
*   **後果 (Consequence)**：AI 給出的通常是通用建議，缺乏對你公司特定基礎設施、團隊技能樹和維運成本的考量。
    AI usually gives generic advice, lacking context on your company's specific infrastructure, team skill set, and operational costs.
*   **修正 (Fix)**：要求 AI 列出 Pros & Cons，但**你自己做決定**。
    Ask AI to list Pros & Cons, but **you make the decision**.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

這些問題可用於面試 Senior 候選人，或在團隊內部進行技術分享。
These questions can be used to interview Senior candidates or for internal tech talks.

## Q1: 你如何驗證 AI 生成的程式碼的正確性，特別是在處理邊界條件時？
**How do you verify the correctness of AI-generated code, especially regarding edge cases?**

*   **高分回答要點 (Key Points)**：
    *   不只看 Happy Path，會主動要求 AI 生成針對 Edge Cases (如 Null, Empty List, Negative values) 的單元測試。
    *   檢查是否有 Security Vulnerabilities (如 SQL Injection, XSS)，即使 AI 聲稱已處理。
    *   人工 Code Review，將 AI 視為 Junior Engineer。

## Q2: 在重構大型 Legacy Code 時，你會如何利用 AI 輔助？
**How would you leverage AI when refactoring a large Legacy Codebase?**

*   **高分回答要點 (Key Points)**：
    *   使用 AI 進行「解釋代碼 (Code Explanation)」來快速理解未知的邏輯。
    *   利用 AI 生成 Regression Tests，在修改前先鎖定行為。
    *   逐步遷移 (Incremental Migration)，而非一次性重寫，並利用 AI 轉換語法但保持邏輯結構。

## Q3: 請描述一次 AI 給出了錯誤建議（幻覺），你如何發現並修正的經驗？
**Describe a time when AI gave incorrect advice (hallucination). How did you detect and fix it?**

*   **高分回答要點 (Key Points)**：
    *   展示對底層原理的理解（例如：AI 亂用了一個不存在的 API 方法）。
    *   強調查閱官方文件 (Official Documentation) 作為 Source of Truth 的重要性。
    *   說明如何調整 Prompt (如加入 "Only use standard library") 來修正 AI 的行為。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)

1.  **Context is King**: 你的 Prompt 品質取決於你提供的 Context 品質。像管理記憶體一樣管理你的 Context Window。
    The quality of your Prompt depends on the quality of the Context you provide. Manage your Context Window like you manage memory.
2.  **Chain-of-Thought**: 對於複雜邏輯，先讓 AI 思考 (Analyze)，再讓 AI 實作 (Implement)。
    For complex logic, let the AI think (Analyze) first, then implement.
3.  **Trust but Verify**: AI 是你的結對程式設計師，不是你的技術主管。你必須擁有最終的 Code Review 權力。
    AI is your Pair Programmer, not your Tech Lead. You must retain final Code Review authority.
4.  **Iterative Prompting**: 把 Prompt 當作程式碼一樣進行迭代、除錯和優化。
    Treat Prompts like code: iterate, debug, and optimize them.

## 下一步 (Next Steps)

*   **實作 (Action)**：挑選你目前專案中一個棘手的 Bug 或一段難懂的 Legacy Code，嘗試使用 CoT 技巧讓 AI 幫你分析。
    Pick a tricky Bug or a piece of obscure Legacy Code in your current project and try using CoT techniques to have AI analyze it for you.
*   **延伸閱讀 (Reading)**：研究如何在你的 IDE (如 VS Code) 中設定 Custom Instructions 或 Snippets，將本章學到的 Prompt 技巧固化為工具。
    Research how to set up Custom Instructions or Snippets in your IDE (e.g., VS Code) to solidify the Prompt techniques learned in this chapter into tools.
*   **預告 (Preview)**：下一章我們將探討 **AI-Driven Testing & Debugging**，深入挖掘如何利用 AI 自動化生成高覆蓋率的測試套件。
    In the next chapter, we will explore **AI-Driven Testing & Debugging**, diving deep into how to use AI to automate the generation of high-coverage test suites.