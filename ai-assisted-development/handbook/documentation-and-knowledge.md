# 技術文件撰寫與知識管理 / Technical Documentation & Knowledge Management

在 AI 輔助開發的時代，文件撰寫不再是開發流程中的「事後諸葛」或苦差事。AI 擅長將結構化的邏輯（Code）轉換為自然語言（Documentation），這使得我們可以從「撰寫者（Writer）」轉變為「編輯者（Editor）」。本章節探討如何利用 AI 高效生成高品質的文件，並維護專案的知識庫。

## Mental model｜心智模型

### 1. The Translator, Not the Author (翻譯者而非原創者)
將 AI 視為一位精通「程式語言」與「人類語言」的**翻譯官**。
- **Code is Truth**: 程式碼是唯一的真理來源。
- **AI is the Bridge**: AI 的工作是將程式碼的行為翻譯成人類可讀的說明，或是將人類的意圖（User Stories）翻譯成技術規格。
- **You are the Editor-in-Chief**: AI 產出的文件草稿必須由你審核。AI 容易產生「看似合理但細節錯誤」的幻覺（Hallucinations），你必須確保文件與程式碼行為的一致性。

### 2. Documentation as Code (文件即代碼)
在使用 AI 時，應堅持將文件視為程式碼的一部分。
- 文件應與程式碼同生共死（Co-located）。
- 利用 AI 在寫 Code 的當下（Context 最清晰時）生成文件，而不是等到專案結束才補。
- **Context Awareness**: 提供給 AI 的上下文越多（例如相關的 Interface 定義、資料庫 Schema），生成的準確度越高。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. The "Intent-First" Commenting (意圖優先註釋)
不要讓 AI 解釋「程式碼在做什麼」（What），而是要求它解釋「為什麼這樣做」（Why）。
- **Pattern**: 選取一段複雜邏輯，Prompt AI：「為這段程式碼生成註解，解釋其業務邏輯與邊界條件處理，而非逐行解釋語法。」
- **Benefit**: 避免產生 `i++ // increment i` 這種無效註釋，轉而生成 `// 使用指數退避策略重試連線，防止伺服器過載`。

### 2. Automated API Documentation (自動化 API 文件)
利用 AI 將函式簽章（Function Signature）轉換為標準格式文件（JSDoc, Docstrings, Swagger/OpenAPI）。
- **Pattern**:
    - 輸入：Raw Code (e.g., a Python function).
    - Prompt: "Generate Google-style docstrings for this function. Include args, return values, and potential exceptions based on the code logic."
    - 輸出：標準化、格式完美的文件區塊。

### 3. The "Commit Message Composer" (提交訊息作曲家)
將 `git diff` 的內容交給 AI，生成符合 Conventional Commits 規範的訊息。
- **Pattern**:
    - 輸入：`git diff --staged` 的輸出。
    - Prompt: "Summarize these changes into a Conventional Commit message (feat, fix, chore). Use bullet points for the body."
- **Benefit**: 確保 Commit History 清晰、結構化，便於日後生成 Changelog。

### 4. Legacy Code Explanation (遺留代碼解讀)
面對沒有文件的 Legacy Code，使用 AI 進行逆向工程文件化。
- **Pattern**:
    - 輸入：一段難懂的 Spaghetti Code。
    - Prompt: "Explain this code's logic in plain English. Create a flowchart description and list any side effects."
    - Action: 將生成的解釋精簡後，作為模組層級的 README 或註解寫回程式碼中。

### 5. README & Onboarding Generation
- **Pattern**: 提供專案結構（File Tree）與關鍵檔案（package.json, main entry point），要求 AI 生成 `README.md`。
- **Focus**: 安裝步驟、環境變數設置、如何執行測試。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Captain Obvious" (廢話連篇)
- **Anti-pattern**: 讓 AI 對每一行程式碼都生成註解。
- **Result**: 程式碼變得冗長且難以閱讀，註解與程式碼邏輯高度重複。
- **Fix**: 只針對 Public API、複雜演算法或非直觀的 Workaround 生成文件。

### 2. The "Hallucinated Parameter" (參數幻覺)
- **Anti-pattern**: 盲目信任 AI 生成的 API 文件，未檢查參數名稱或型別。
- **Risk**: AI 可能會根據變數命名猜測用途，導致文件描述了不存在的參數（例如將 `userId` 描述為 `userObject`）。
- **Fix**: 始終對照程式碼簽章（Signature）進行核對。

### 3. Stale Documentation (過期文件)
- **Anti-pattern**: 修改了程式碼邏輯，但忘記要求 AI 更新對應的註解或文件。
- **Risk**: 誤導其他開發者，比沒有文件更糟糕。
- **Fix**: 養成習慣，在 Refactoring 的 Prompt 中加入指令：「...並更新相關的 JSDoc/註解以反映這些變更。」

### 4. Leaking Secrets in Docs (文件洩密)
- **Pitfall**: AI 可能會將程式碼中的 Hardcoded string（即使是測試用的）視為預設值寫入公開文件中。
- **Fix**: 在生成文件後，搜尋並移除任何潛在的敏感資訊或內部 IP 位置。

---

## Checklists & workflows｜檢查清單與流程

### Workflow: AI-Assisted Documentation Cycle

1.  **Code**: 完成功能開發。
2.  **Generate**: 選取程式碼片段，使用 AI 生成草稿（Docstring/README section）。
3.  **Verify**: 人工審查（Accuracy Check）。
4.  **Refine**: 調整語氣，補充 AI 無法得知的業務背景（Context Injection）。
5.  **Commit**: 將文件與程式碼一同提交。

### Checklist: Before You Merge

- [ ] **準確性驗證**：AI 生成的參數、回傳值型別是否與程式碼完全一致？
- [ ] **去廢話**：是否移除了 "This function does..." 這類無意義的開頭？
- [ ] **業務邏輯**：文件是否解釋了 *Why* 而不僅是 *How*？
- [ ] **格式檢查**：生成的 Markdown 或 JSDoc 格式是否符合專案規範（Linting）？
- [ ] **無幻覺**：是否檢查了 AI 捏造的依賴項或環境變數？
- [ ] **敏感資訊**：確認文件中未包含 Key、Password 或內部伺服器路徑。

---

## Real-world examples｜實戰案例

### Example 1: Generating JSDoc for a Utility Function

**Input (Code):**
```javascript
const calculateBackoff = (attempt, base = 100, cap = 10000) => {
  const sleep = Math.min(cap, base * 2 ** attempt);
  return sleep * (0.8 + Math.random() * 0.4);
};
```

**Prompt:**
> Generate JSDoc for this function. Explain the "Jitter" logic clearly.

**AI Output (Draft):**
```javascript
/**
 * Calculates the sleep duration for exponential backoff with jitter.
 *
 * @param {number} attempt - The current retry attempt number (0-indexed).
 * @param {number} [base=100] - The base delay in milliseconds.
 * @param {number} [cap=10000] - The maximum delay allowed in milliseconds.
 * @returns {number} The calculated delay in milliseconds, including a random jitter
 *                   factor between 0.8 and 1.2 to prevent thundering herd problem.
 */
const calculateBackoff = ...
```
*Critique: AI 正確識別了 Jitter 的範圍 (0.8 ~ 1.2) 並解釋了其用途（防止驚群效應），這是高品質的輔助。*

### Example 2: Creating a Commit Message from `git diff`

**Context:**
Developer fixed a bug in the login flow where the session wasn't cleared on logout.

**Prompt:**
> Write a conventional commit message for this change.
> Diff: `UserSession.js: + clearStorage() in logout()`

**AI Output:**
```text
fix(auth): ensure local storage is cleared upon user logout

- Added `clearStorage()` call within the `logout` method in UserSession.js.
- Prevents stale session data from persisting after logout.
```

### Example 3: Translating Logic to Human Language (ADR Draft)

**Scenario:** You need to explain a complex SQL query optimization to the product manager or in an Architecture Decision Record (ADR).

**Prompt:**
> Explain this SQL query in simple terms. Focus on why we used a specific index and how it improves performance for the 'Dashboard' view.

**AI Output:**
> "This query retrieves the daily sales summary. Instead of scanning the entire 'Orders' table (which has millions of rows), it uses a pre-calculated index based on 'Date' and 'Region'. This makes the Dashboard load in under 200ms instead of 5 seconds."

*Takeaway: 利用 AI 將技術實作轉換為「商業價值」描述，是溝通與知識管理的強大工具。*