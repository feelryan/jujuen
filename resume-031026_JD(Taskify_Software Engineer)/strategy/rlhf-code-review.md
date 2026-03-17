# RLHF 與代碼評估核心技能 / RLHF & Code Evaluation Mindset

## Why this matters｜為什麼這個主題重要

在 Taskify AI 的 JD 中，核心職責是 **"Review AI-generated code"** 與 **"Validate algorithms"**。這與傳統軟體開發（Software Development）有本質上的區別：

1.  **從「寫作者」轉變為「評審者」 (Author to Evaluator)**：
    *   傳統開發是你寫代碼解決問題；RLHF (Reinforcement Learning from Human Feedback) 標註則是你要判斷 AI 寫的代碼是否正確、安全、且符合最佳實踐。
    *   **Ryan 的優勢**：擁有 15+ 年經驗（Java, JS, C++），你看過的「壞代碼」比大多數人寫過的還多。這種資深經驗是判斷 AI 是否產生「隱晦 Bug」或「安全漏洞」的關鍵。

2.  **數據品質決定模型智商 (Data Quality is King)**：
    *   你的回饋將直接作為「獎勵模型 (Reward Model)」的訓練數據。若你的評分標準不一或回饋模糊，會導致模型學壞。
    *   JD 特別提到 **"Provide detailed feedback"** 與 **"Support model benchmarking"**，這意味著你需要提供結構化、邏輯嚴密的理由，而不僅僅是修復代碼。

3.  **多語言與安全性 (Polyglot & Security)**：
    *   JD 要求 Python, JS, Java, C++。AI 常在跨語言轉換時出錯（例如用 Python 的邏輯寫 C++ 指標）。
    *   Ryan 的 **Healthcare/FDA 背景** 與 **Google Cloud Architect 認證**，讓你對 Security (資安) 與 Compliance (合規) 有極高敏感度，這是 AI 代碼審查中非常高價值的技能（例如：識別 PII 洩漏、SQL Injection）。

---

## Step‑by‑step strategy｜具體行動步驟

### Week 1: 建立 RLHF 評測思維 (The RLHF Mindset)
*   **理解 3H 原則**：所有 AI 回覆評估都基於 **Helpful (有幫助)**、**Honest (誠實/準確)**、**Harmless (無害/安全)**。
    *   *Action*: 複習 Google Generative AI Leader 課程中的 "Responsible AI" 章節，將其概念對應到代碼審查（例如：Harmless = 不生成惡意腳本、無窮迴圈）。
*   **熟悉評分維度**：
    *   **Correctness (正確性)**：代碼是否可執行？邏輯是否符合 Prompt 要求？
    *   **Efficiency (效率)**：時間/空間複雜度是否最佳？（例如：AI 給了 $O(n^2)$ 解法，但存在 $O(n)$ 解法）。
    *   **Style & Best Practice (風格與規範)**：變數命名、模組化、註解是否清晰？

### Week 2: 針對性複習與實戰 (Targeted Review)
*   **多語言切換練習**：
    *   Ryan 的核心是 Java/JS，但 JD 提到 C++ 與 Python。
    *   *Action*: 每天花 30 分鐘在 LeetCode 上挑選一題 Medium 題目，先看 Python 解法，再看 C++ 解法，找出兩者語法與記憶體管理的差異（這常是 AI 搞混的地方）。
*   **模擬 AI 審查 (Mock Review)**：
    *   使用 ChatGPT 或 Claude，輸入：「請用 Java Spring Boot 寫一個處理 User Login 的 API，包含 DB 連線」。
    *   **練習**：不要只看代碼，試著找出它「沒做好」的地方（例如：密碼是否 Hash？有無 Input Validation？Exception Handling 是否完善？）。這就是面試時要做的事。

### Week 3: 撰寫「黃金回饋」 (Writing Golden Feedback)
*   **練習 Justification (論證撰寫)**：
    *   RLHF 標註不僅要改代碼，還要寫 "Why"。
    *   *Action*: 建立自己的「回饋模板」。與其說 "This is wrong"，不如說 "The code fails to handle the edge case where input is null, causing a NullPointerException. Suggested fix: add a null check on line 5."

### Week 4: 針對 15-minute AI Interview 的準備
*   **速度與準確度測試**：
    *   該職缺有 "15-minute AI interview"。這通常是自動化測驗，要求你在短時間內判斷代碼片段的輸出或 Bug。
    *   *Action*: 練習「人肉 Debug」。看一段 20 行的代碼，不跑編譯器，在 60 秒內說出它的 Output 或 Error。

---

## Examples & templates｜範例與範本

在面試或實際工作中，使用結構化的評估模板會顯得非常專業。

### 1. 代碼評估維度檢查表 (Code Evaluation Rubric)

| Dimension | Checkpoints (Ryan's Lens) |
| :--- | :--- |
| **Instruction Following** | AI 是否真的解決了 Prompt 提出的所有限制條件？（例如：Prompt 要求 "不使用遞迴"，AI 是否遵守了？） |
| **Correctness** | 邊界條件 (Edge cases) 是否處理？（空陣列、負數、大整數溢位）。 |
| **Security** | (Ryan 的強項) SQL Injection? XSS? Hardcoded secrets? PII exposure? |
| **Performance** | 是否有多餘的迴圈？記憶體洩漏 (Memory Leak) 風險？ |

### 2. 回饋撰寫範本 (Feedback Template)

當你需要解釋「為什麼這個 AI 生成的代碼不好」時，請套用此結構：

> **Issue Category**: [Logic Error / Security Vulnerability / Inefficiency / Hallucination]
>
> **Observation**: The model generated a valid syntax, BUT it uses `String` concatenation inside a loop for constructing the JSON response.
>
> **Impact**: In Java, this creates excessive immutable string objects, leading to $O(n^2)$ performance and potential memory overhead.
>
> **Correction**: Replace `String` concatenation with `StringBuilder` (or `StringBuffer` for thread safety).
>
> **Revised Code**: (Provide the optimized snippet)

### 3. 常見 AI 錯誤類型 (Common AI Failure Modes)

準備好識別這些模式：
*   **Hallucination (幻覺)**：引用了不存在的 Library 或 Method（例如：在 Java 裡呼叫了 Python 的函式庫）。
*   **Lazy Coding (偷懶)**：給出 `// ... rest of the code` 而不是完整實作。
*   **Logic Drift (邏輯漂移)**：開頭寫對了，但結尾忘記了開頭定義的變數。

---

## Signals for interviewers｜要讓面試官看到的訊號

在履歷篩選與面試中，你要透過這個策略傳達以下訊號，證明你比一般 Junior 工程師更適合做 RLHF：

1.  **"I don't just fix code; I teach the model."**
    *   展現你知道如何給出「可被學習」的回饋，而不僅僅是修正。
2.  **"I see the invisible bugs."**
    *   強調你在 **Healthcare/Finance (Innova/Ustoshop)** 的經驗，說明你會特別檢查資安與合規性漏洞，這是 AI 目前最弱的一環。
3.  **"I am Polyglot & Versatile."**
    *   雖然你是 Java/JS 專家，但你展示出對 C++ 指標管理或 Python 動態型別陷阱的理解。
4.  **"Attention to Detail."**
    *   RLHF 需要極高的細心度。提及你在 FDA 510K 專案中對規範的嚴謹度，證明你有能力處理高標準的數據標註。

---

## Common pitfalls｜常見錯誤與避免方式

1.  **陷阱：過度主觀 (Being too subjective)**
    *   *錯誤*：「這代碼寫得很醜。」
    *   *修正*：「這代碼違反了 PEP8 規範，且變數命名 `x`, `y` 無法反映業務邏輯，降低了可維護性。」
2.  **陷阱：忽略 Prompt 的意圖 (Ignoring the Prompt)**
    *   *錯誤*：AI 寫了一個完美的 QuickSort，但 Prompt 其實是要求 BubbleSort。你給了滿分。
    *   *修正*：永遠先確認 Prompt 的限制條件 (Constraints)。準確性是相對於 Prompt 而言的。
3.  **陷阱：只看 Happy Path (Ignoring Edge Cases)**
    *   *錯誤*：代碼在輸入正常時會跑，你就給 Pass。
    *   *修正*：身為資深工程師，你必須測試 `null`、空值、極大值。AI 常常在這些地方出錯。
4.  **陷阱：重寫而非修正 (Rewriting instead of Editing)**
    *   *錯誤*：完全刪除 AI 的代碼，貼上你自己的完美版本。
    *   *修正*：RLHF 的目標通常是「最小幅度修改 (Minimal Edit Distance)」以達到正確，這樣模型才能學習到具體哪裡錯了。

---

## Checklist｜檢查清單

- [ ] **Mindset Shift**: 我已理解我的角色是「老師/評審」，目標是提升模型品質。
- [ ] **Review Practice**: 我已嘗試 review 至少 3 段由 ChatGPT 生成的 Java/Python/C++ 代碼，並找出其中的潛在問題。
- [ ] **Security Lens**: 我準備好 2-3 個過去在 Healthcare/FinTech 領域遇到的資安案例，用來展示我能識別 AI 生成的危險代碼。
- [ ] **Feedback Formatting**: 我已練習寫出「問題分類 + 影響分析 + 具體修正」的結構化回饋。
- [ ] **Prompt Awareness**: 在評估代碼前，我習慣先仔細閱讀 Prompt 的每一個限制條件。