# 技術寫作與回饋撰寫技巧 / Technical Writing for Code Feedback

## Why this matters｜為什麼這個主題重要

對於 Taskify AI 的這份職缺（Software Engineering Specialist - RLHF/Code Evaluation），**「寫作」本身就是產品**。

1.  **The "Product" is the Feedback / 回饋即產品**：
    這不是一份單純寫程式的工作。你的產出是用來訓練 AI 模型的數據。如果你的 Code Review 只有「請修正這行」，AI 學不到東西。AI 需要知道 **「為什麼錯」、「潛在風險是什麼」以及「更好的做法是什麼」**。
2.  **Explicit over Implicit / 顯性知識優於隱性直覺**：
    作為擁有 15+ 年經驗的資深工程師 (Ryan)，你可能一眼就能看出程式碼的壞味道 (Code Smell)。但在這份工作中，你不能只憑直覺修復，必須將這種「資深直覺」轉化為**邏輯清晰、結構化的文字解釋**。
3.  **Cross-Language Context / 跨語言語境**：
    JD 要求 Python, JS, Java, C++ 等多語言能力。你需要用文字清楚解釋某些寫法在 Python 是 Pythonic 的，但在 Java 中可能是效能殺手。這種細微差別的文字化能力是錄取關鍵。

---

## Step‑by‑step strategy｜具體行動步驟

### Week 1: Audit & Mindset Shift (盤點與思維轉換)
- **Review your past Code Reviews**: 回顧你在 Innova Solutions 或 Hiveel 的 Code Review 紀錄。
    - *Bad:* "Fix this loop." (太簡短)
    - *Good:* "This nested loop creates O(N^2) complexity. Since the data set can be large, let's use a HashMap to optimize to O(N)." (解釋了原因與解法)
- **Analyze the "FDA 510K Spec" Experience**: 你的履歷中提到了撰寫 FDA 規格書的經驗。這是一個強大的資產。回想當時如何將複雜的技術細節寫得嚴謹、無歧義。這正是 AI 訓練需要的精準度。

### Week 2: Practice Structured Feedback (練習結構化回饋)
- **The "What-Why-How" Framework**: 練習對每一段有問題的代碼使用此框架：
    1.  **What**: 指出具體問題（語法錯誤、邏輯漏洞、效能低落）。
    2.  **Why**: 解釋為什麼這是個問題（會導致 Crash、記憶體洩漏、難以維護）。
    3.  **How**: 提供具體修正建議或程式碼片段。
- **Pick a LeetCode Problem**: 找一道 Medium 難度的題目，故意寫一個「能跑但很爛」的解法（例如變數命名不清、邊界條件未處理），然後扮演 Reviewer 寫一段 200 字的評語。

### Week 3: Resume & Profile Tuning (履歷與展示面微調)
- **Highlight "Mentorship"**: 在履歷中強調你如何透過 Code Review 指導初階工程師。
    - *Action:* 在 Innova Solutions 的經歷中，將 "Drove CI/CD and code quality improvements" 擴充為 "Established code review standards and provided detailed technical documentation to mentor junior developers, reducing production bugs."
- **Emphasize "Documentation"**: 強調你的 FDA 文件撰寫經驗，證明你有「高標準技術寫作」的能力。

### Week 4: Mock Simulation (模擬實戰)
- **Explain "Why" to a Non-Expert**: 試著用英文寫一段解釋「為什麼在 React 中直接修改 State 是錯誤的 (Mutation)」，假設讀者是一個剛學程式的 AI。檢查你的解釋是否包含術語定義、後果描述與正確範例。

---

## Examples & templates｜範例與句型

在面試或實際工作中，使用以下模板來展現你的專業度：

### Template 1: Correctness Issue (正確性問題)
> **Observation**: The function fails to handle `null` or `undefined` inputs for the `user_id` parameter.
> **Impact**: This will cause a `NullPointerException` (Java) / `TypeError` (JS) at runtime if the API returns an incomplete object.
> **Suggestion**: Add a guard clause at the beginning of the function to validate inputs.
> **Code Example**:
> ```javascript
> if (!userId) return; // Early return
> ```

### Template 2: Performance Issue (效能問題)
> **Observation**: The current implementation uses string concatenation inside a loop.
> **Impact**: In Java, strings are immutable. This creates a new object in every iteration, leading to $O(N^2)$ memory overhead and garbage collection pressure.
> **Suggestion**: Use `StringBuilder` (Java) or array join (JS) for efficient string manipulation.

### Template 3: Best Practice / Readability (最佳實踐)
> **Observation**: Variable names like `x`, `y`, and `temp` are used throughout the calculation logic.
> **Impact**: This reduces code readability and makes maintenance difficult for future developers.
> **Suggestion**: Rename variables to reflect their intent, e.g., `transactionAmount`, `taxRate`.

### Useful Phrases (實用句型)
- "While this approach works, it is not idiomatic in Python because..." (雖然這可行，但在 Python 中不道地，因為...)
- "Consider the edge case where the input list is empty..." (考慮輸入列表為空的邊界情況...)
- "This introduces a potential race condition when..." (這在...情況下引入了潛在的競爭條件)
- "To improve time complexity from $O(N^2)$ to $O(N)$, we recommend..." (為了將時間複雜度從...優化到...)

---

## Signals for interviewers｜要讓面試官看到的訊號

當你在 15 分鐘的 AI 面試或書面測驗中應用此策略時，面試官（或評分 AI）會尋找以下訊號：

1.  **Justification Capability (論證能力)**：
    你不是只給答案，而是給出「理由」。這顯示你具備 Senior Engineer 的思維深度。
2.  **Empathy for the Reader (讀者同理心)**：
    你的文字是否易懂？是否假設了讀者（AI 模型）不知道某些背景知識？清晰的解釋代表良好的 RLHF 訓練數據。
3.  **Attention to Detail (細節關注)**：
    JD 特別提到 "attention to implementation detail"。你能否發現那些「邏輯正確但實作粗糙」的地方（例如未關閉的 File Stream、多餘的 API 呼叫）？
4.  **Tone (語氣)**：
    保持客觀、建設性 (Constructive) 且權威 (Authoritative)，避免主觀批評（如 "This code is ugly" -> 改為 "This code violates PEP8 style guidelines"）。

---

## Common pitfalls｜常見錯誤與避免方式

- **Pitfall 1: Being too brief (過於簡短)**
    - *Avoid:* "Fix indentation."
    - *Fix:* "Python relies on indentation for block structure. The current mix of tabs and spaces will cause an `IndentationError`. Please standardize on 4 spaces."
- **Pitfall 2: Focusing only on syntax, ignoring logic (只看語法，忽略邏輯)**
    - *Avoid:* 只修正拼字錯誤，卻沒發現演算法本身是錯的。
    - *Fix:* 總是先驗證演算法邏輯，再看語法細節。
- **Pitfall 3: Subjectivity without standard (缺乏標準的主觀意見)**
    - *Avoid:* "I prefer a for-loop here."
    - *Fix:* "Using `map()` is preferred here as it aligns with functional programming paradigms and reduces side effects." (引用範式或標準)
- **Pitfall 4: Assuming Context (假設對方懂上下文)**
    - *Avoid:* 使用過多縮寫或內部術語而不解釋。
    - *Fix:* 像在寫技術文件一樣，第一次出現術語時稍微定義，確保上下文完整。

---

## Checklist｜檢查清單

在提交任何測驗或進行面試前，請確認：

- [ ] **結構完整**：我的回饋是否包含「觀察 (What) -> 影響 (Why) -> 建議 (How)」？
- [ ] **語氣客觀**：我是否使用了客觀的技術術語，而不是個人好惡？
- [ ] **涵蓋邊界**：我是否檢查了 Null、Empty List、Negative Numbers 等邊界情況？
- [ ] **語言特性**：我是否針對該程式語言（Python/Java/JS）的特性給出了正確建議？
- [ ] **履歷連結**：我是否在自我介紹中，將我的 FDA 文件經驗與 Code Review 經驗連結到「高品質技術寫作」這個需求上？