# 程式碼生成最佳實踐與審查 / Code Generation Best Practices & Review

## Mental model｜心智模型

### 1. The "Overconfident Junior" Heuristic (過度自信的資淺工程師啟發法)
將 AI 視為一位**速度極快、閱讀量巨大，但缺乏判斷力且過度自信的資淺工程師（Junior Developer）**。
- 它寫出的程式碼通常語法正確（Syntactically correct），但在邏輯邊界（Edge cases）、安全性或業務上下文（Business context）上可能存在微妙的錯誤。
- **你的角色轉變**：從單純的「撰寫者（Writer）」轉變為「架構師兼審查者（Architect & Lead Reviewer）」。你不再逐字輸入，而是負責定義規格、審核產出並整合至系統中。

### 2. Probabilistic vs. Deterministic (機率性 vs. 決定性)
AI 是基於機率預測下一個 Token，而非基於邏輯推導。
- **Code Generation ≠ Code Compilation**：編譯器不會出錯，但 AI 會。
- **Verification Gap**：生成的程式碼越複雜，驗證所需的認知負荷（Cognitive Load）越高。若生成結果難以閱讀或驗證，請要求 AI 重寫或簡化，不要盲目接受。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Context-First Generation (上下文優先生成)
AI 缺乏對你專案全貌的理解。在要求生成程式碼前，先提供「上下文錨點」。
- **提供依賴資訊**：貼上相關的 Interface、Type Definition 或現有的 Utility function。
- **指定風格**：明確要求使用特定的 Library（如：`Use TanStack Query for data fetching`）或 Coding Style（如：`Functional programming style, no classes`）。

### 2. The "Scaffold & Fill" Pattern (鷹架填充模式)
不要試圖一次生成整個檔案或複雜模組。
- **Step 1**：先生成介面（Interface）、型別定義（Types）或函數簽名（Function Signatures）。
- **Step 2**：審查結構是否符合設計。
- **Step 3**：逐一要求 AI 實作具體的函數內容。
> *Why?* 這能大幅降低 AI 迷失方向（Hallucination）的機率，並讓你保持對架構的控制權。

### 3. AI-Driven TDD (AI 驅動的測試驅動開發)
利用 AI 生成測試案例，再來生成實作代碼。
- **Pattern**：
    1. 描述需求。
    2. Prompt: "Write Jest unit tests for this requirement, covering edge cases."
    3. Review 測試案例（這比 Review 實作邏輯容易）。
    4. Prompt: "Now write the implementation to pass these tests."
- 這建立了一個**自動化的驗證網**，是過濾 AI 錯誤最有效的方法。

### 4. Interactive Refinement (互動式優化)
將生成視為對話而非單次指令。
- **Critique Loop**：生成後，不要直接修 code，而是告訴 AI 哪裡錯了（例如：「這裡有 N+1 Query 問題」），讓它自我修正。這能確保 AI 的 Context 保持同步，方便後續修改。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Phantom Library" Hallucination (幽靈函式庫幻覺)
AI 經常會捏造「看起來很合理」但實際上不存在的 import 或 function method。
- **徵兆**：`import { specificUtils } from 'popular-lib'`，但該 library 根本沒這個 export。
- **後果**：Runtime Error 或 Build 失敗，浪費大量時間 debug。

### 2. Security Blindspots (安全性盲點)
AI 訓練資料包含大量未經審核的程式碼，容易生成不安全的實作。
- **常見漏洞**：
    - 直接拼接 SQL 字串（SQL Injection）。
    - Hardcoded Secrets/API Keys（即使是範例也可能不小心 commit）。
    - 缺乏 Input Validation 的 API Endpoint。
    - 使用過時或不安全的加密演算法（如 MD5）。

### 3. The "Looks Good To Me" (LGTM) Syndrome (看起來沒問題症候群)
因為變數命名優美、縮排整齊，開發者大腦會預設程式碼是正確的，從而跳過深入的邏輯檢查。
- **風險**：Off-by-one errors（差一錯誤）、錯誤的 Error Handling 流程、或是邏輯反轉（`if (!user)` 寫成 `if (user)`）。

### 4. Boilerplate Bloat (樣板程式碼膨脹)
AI 傾向於過度設計（Over-engineering），生成冗長的 boilerplate 而非簡潔的現代語法。
- **例子**：在可以使用 `async/await` 的地方寫了複雜的 `Promise` chain；或是過度拆分不必要的 helper functions。

---

## Checklists & workflows｜檢查清單與流程

在將 AI 生成的程式碼 Commit 進版控前，請務必執行以下檢查流程：

### Code Review Checklist (AI Specific)
- [ ] **Existence Check**：檢查所有引入的 Library、Method 是否真實存在且版本相容。
- [ ] **Security Scan**：
    - [ ] 是否有 Hardcoded 密碼或 Token？
    - [ ] 是否有 SQL/Command Injection 風險？
    - [ ] 是否對使用者輸入進行了驗證（Sanitization）？
- [ ] **Logic Verification**：
    - [ ] 邊界條件（Edge cases）：空陣列、null、undefined、負數是否會導致崩潰？
    - [ ] 迴圈終止條件是否正確？
- [ ] **Context Fit**：
    - [ ] 變數命名是否符合專案慣例？
    - [ ] 是否重複造輪子（Reinventing the wheel）而未重複使用現有的 Utils？
- [ ] **Test Coverage**：
    - [ ] 是否同步生成了單元測試？
    - [ ] 測試是否真的執行並通過？

### Decision Workflow (決策流程)

```mermaid
graph TD
    A[需求定義] --> B{邏輯複雜度?}
    B -->|低 / Boilerplate| C[直接生成實作]
    B -->|高 / 核心邏輯| D[先生成測試案例 / 介面]
    C --> E[人工審查 (Syntax & Style)]
    D --> F[人工審查 (Logic & Edge Cases)]
    F --> G[生成實作]
    E --> H[執行測試]
    G --> H
    H -->|失敗| I[將錯誤訊息回饋給 AI]
    I --> G
    H -->|通過| J[Commit]
```

---

## Real-world examples｜實戰案例

### Example 1: Handling Complex Regex (處理複雜正規表達式)

**❌ Bad Practice (Blind Trust):**
Prompt: "Write a regex to validate emails."
*Result:* AI generates a 100-character regex. Developer pastes it. It fails on valid emails like `user+tag@domain.co.uk`.

**✅ Good Practice (Explain & Verify):**
**Prompt:**
> "Generate a Regex for email validation that supports standard RFC 5322.
> **Also, explain how it works step-by-step.**
> **Finally, generate a set of test strings (both valid and invalid) to verify this regex.**"

**Review Action:**
1. 閱讀解釋，確認邏輯符合需求。
2. 將生成的測試字串放入線上 Regex 測試工具（如 Regex101）或單元測試中驗證。

### Example 2: Generating Data Transformation Logic (資料轉換邏輯)

**Scenario:** 你需要將後端 API 的 `Snake_Case` JSON 轉換為前端的 `CamelCase` 結構，並過濾掉未啟用的項目。

**Prompt Pattern (Context Injection):**
> "I have a source type:
> ```typescript
> type BackendUser = { user_id: number; is_active: boolean; role_list: string[] };
> ```
> And a target type:
> ```typescript
> type FrontendUser = { id: number; roles: string[] };
> ```
> Write a transformation function `adaptUser` that converts BackendUser to FrontendUser.
> **Constraint:** Filter out users where `is_active` is false. Use Lodash if helpful, or vanilla ES6."

**Review Focus:**
- 檢查 `is_active` 是在轉換前過濾還是在轉換後過濾（效能差異）。
- 檢查 `role_list` 到 `roles` 的 mapping 是否正確。
- 確保沒有遺漏欄位。