# 核心思維模型：Copilot 而非 Autopilot / Core Mental Models: Copilot, Not Autopilot

## Mental model｜心智模型

在 AI 輔助開發的時代，工程師最危險的錯誤並非「不會寫 Prompt」，而是誤以為 AI 是全自動駕駛（Autopilot）。建立正確的心智模型是高效且安全使用 AI 工具的前提。

### 1. 機率機器 vs. 邏輯機器 (Probabilistic vs. Deterministic)
軟體工程是建立在**確定性邏輯（Deterministic Logic）**之上的，但 LLM（大型語言模型）本質上是**機率預測機器（Probabilistic Engine）**。
- **The Gap**：AI 輸出的程式碼只是「看起來最像正確答案」的文字接龍，而非經過編譯器驗證的邏輯真理。
- **Implication**：你必須假設 AI **隨時都在撒謊或產生幻覺**，直到你親自驗證為止。

### 2. 資深工程師帶著實習生 (Senior with Intern)
將 AI 視為一位**博學多聞、打字飛快，但經驗不足且容易過度自信的實習生**。
- **角色分配**：
  - **你 (Senior)**：負責架構決策、定義問題邊界、審查程式碼安全性與正確性。
  - **AI (Intern)**：負責生成樣板代碼（Boilerplate）、快速實作具體函式、解釋文檔或轉換語法。
- **責任歸屬**：實習生寫出的 Bug，是審查者（你）的責任。

### 3. 生成與驗證的不對稱性 (Asymmetry of Generation and Verification)
AI 大幅降低了「生成程式碼」的成本，但這意味著「驗證程式碼」的成本與重要性成倍增加。
- **Rule of Thumb**：如果生成一段程式碼需要 1 分鐘，你應該預留至少 2-3 分鐘進行閱讀、理解與測試。如果生成的代碼複雜到你無法驗證，**請不要使用它**。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 迭代式提示 (Iterative Prompting / The Ping-Pong Pattern)
不要期望一個 Prompt 就能產出完美的生產級代碼。
- **做法**：先要求 AI 產出介面（Interface）或偽代碼（Pseudo-code），確認邏輯無誤後，再要求實作細節。
- **Example**：
  1. "Propose a JSON structure for user profile." (Review structure)
  2. "Generate TypeScript interfaces based on this JSON." (Review types)
  3. "Write a validation function for this interface." (Review logic)

### 2. 測試驅動輔助 (AI-Assisted TDD)
利用 AI 擅長推理邊界條件的特性，先生成測試，再生成實作。
- **做法**：
  1. 描述需求，請 AI 生成 Unit Test cases（包含 Happy path 與 Edge cases）。
  2. 人工審查測試案例是否合理。
  3. 再請 AI 撰寫通過這些測試的實作代碼。
- **Benefit**：這能有效防止 AI 產生「看起來能跑但邏輯有漏洞」的程式碼。

### 3. 上下文策展 (Context Curation)
AI 的表現取決於你餵給它什麼資訊（Garbage In, Garbage Out）。
- **做法**：在使用 Copilot 或 Chat 介面時，明確開啟相關的檔案（Open Tabs），或將相關的型別定義（Type Definitions）、資料庫 Schema 貼入對話中。
- **Pattern**：`Role` + `Context (Code/Schema)` + `Task` + `Constraints`。

### 4. 解釋回溯 (Explain It Back)
當 AI 生成一段複雜的邏輯（如 Regex 或複雜 SQL）時，要求它反向解釋這段代碼。
- **做法**："Explain line-by-line how this SQL query handles null values."
- **Benefit**：強迫 AI 重新檢視邏輯，往往能讓它自己發現幻覺或錯誤。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 盲目貼上 (The YOLO Paste)
- **現象**：直接複製 AI 產出的代碼並 Commit，完全沒有逐行閱讀。
- **後果**：引入了不存在的函式庫（Hallucinated Imports）、安全漏洞（如 SQL Injection），或微妙的邏輯錯誤（Off-by-one error）。

### 2. 依賴 AI 進行架構設計 (Architectural Autopilot)
- **現象**：詢問 AI "如何設計一個電商系統？" 並照單全收。
- **後果**：AI 傾向於給出「教科書式」的標準答案，忽略了你專案的具體限制（Legacy code、團隊技術棧、成本考量）。架構決策必須由人類主導。

### 3. 敏感資料洩漏 (Data Leakage)
- **現象**：將含有 API Keys、資料庫密碼或 PII（個人識別資訊）的代碼直接貼入公開的 LLM 對話框。
- **後果**：嚴重資安違規。
- **修正**：在貼入代碼前，務必將敏感字串替換為 `<API_KEY_HERE>` 或使用企業版/本地部署的 AI 工具。

### 4. 技能萎縮 (Skill Atrophy)
- **現象**：過度依賴 AI 寫基礎語法，導致連簡單的 loop 或 filter 都無法手寫。
- **後果**：在沒有 AI 的環境（如白板面試、Production 環境緊急除錯）下喪失工作能力。

---

## Checklists & workflows｜檢查清單與流程

在將 AI 生成的代碼合併到主分支前，請執行以下檢查：

### 🔍 Code Review Checklist for AI Code
- [ ] **理解性 (Comprehension)**：我是否完全理解這段代碼的每一行在做什麼？（如果看不懂，絕不 Commit）
- [ ] **安全性 (Security)**：代碼中是否包含 Hardcoded secrets？是否對輸入進行了消毒（Sanitization）？
- [ ] **正確性 (Correctness)**：是否檢查了常見的 AI 錯誤（如：使用了不存在的 API、錯誤的參數順序、過時的語法）？
- [ ] **邊界條件 (Edge Cases)**：AI 是否只處理了 Happy Path？Null/Undefined/Empty List 是否會導致崩潰？
- [ ] **效能 (Performance)**：這段代碼是否引入了不必要的迴圈或高複雜度運算？

### 🔄 AI-Assisted Development Workflow
1. **Define**: 人類定義問題與輸入/輸出規格。
2. **Prompt**: 提供上下文，要求 AI 生成方案或草稿。
3. **Verify**:
   - 靜態檢查：Linter, Type Checker。
   - 動態檢查：Unit Tests。
   - 人工檢查：邏輯審查。
4. **Refine**: 根據驗證結果，手動修改或要求 AI 優化。
5. **Commit**: 只有在通過所有驗證後，才將其視為「我的代碼」提交。

---

## Real-world examples｜實戰案例

### Case 1: The "Hallucinated Library" Trap
**Scenario**: 你請 AI 幫忙處理 PDF 轉檔，它給出了一段 Python code。
```python
# AI Generated
import pdf_magic_tool  # 🚨 Warning: This library might not exist!
def convert(file):
    return pdf_magic_tool.parse(file).to_text()
```
**Reality**: `pdf_magic_tool` 根本不存在，或者是 AI 記錯了名字。
**Action**: 在執行前，先去 PyPI/NPM 搜尋該套件是否存在，並檢查其維護狀態。

### Case 2: The "Subtle Bug" in Regex
**Scenario**: 你請 AI 寫一個驗證 Email 的 Regex。
**AI Output**: `^[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-zA-Z]+$`
**Review**: 乍看之下可以運作。
**Pitfall**: 這個 Regex 不支援 `user.name@example.com`（有點號）或 `user+tag@example.com`。
**Action**: 不要只看 Regex，要求 AI 生成「測試這個 Regex 的 5 個正向案例與 5 個負向案例」，你會立刻發現問題。

### Case 3: Refactoring Legacy Code (Good Use Case)
**Scenario**: 有一段沒人敢動的義大利麵代碼（Spaghetti Code）。
**Workflow**:
1. 貼上舊代碼，Prompt: "Explain what this code does in plain English." (建立理解)
2. Prompt: "Generate unit tests for this code covering all branches." (建立安全網)
3. 運行測試確保通過。
4. Prompt: "Refactor this code to be more readable and functional, keeping the same logic."
5. 運行測試確保重構後行為一致。