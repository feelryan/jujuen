# 智慧除錯與故障排除流程 / Intelligent Debugging & Troubleshooting Workflows

## Mental model｜心智模型

在引入 AI 輔助除錯時，工程師應將思維從「孤獨的偵探 (Lone Detective)」轉變為「指揮鑑識團隊的主管 (Forensic Team Lead)」。

AI 不是只會給答案的魔法師，而是一個擁有無限知識庫但缺乏「當下情境 (Context)」的資深助手。有效除錯的核心在於**資訊對稱**與**驗證機制**。

1.  **Context is King (情境為王)**：AI 無法讀取你的腦袋或整個專案結構（除非你提供）。錯誤訊息 (Stack Trace) 只是冰山一角，你需要提供「案發現場」的完整資訊（相關程式碼、環境變數、操作步驟）。
2.  **The "Rubber Duck" on Steroids (超級黃色小鴨)**：傳統的「黃色小鴨除錯法」是透過向靜物解釋來釐清思緒；AI 則是會回應、會提問、甚至會反駁你的小鴨。
3.  **Trust but Verify (信任但驗證)**：AI 提供的修復方案可能是「語法正確但邏輯錯誤」的，甚至是過時的 API。必須假設 AI 的解法是「建議」而非「真理」。

## Patterns & best practices｜常見模式與最佳實務

### 1. The "3C" Prompting Pattern (3C 提示模式)
為了獲得高品質的除錯建議，提示詞應包含三個維度：
-   **Code (程式碼)**：發生錯誤的函式或模組片段。
-   **Crash (崩潰資訊)**：完整的 Stack Trace、錯誤代碼或異常行為描述。
-   **Context (情境)**：你正在嘗試做什麼？這是什麼環境（Local/Prod）？你已經嘗試過哪些修復方式？

### 2. Explain-Fix-Test Loop (解釋-修復-測試 迴圈)
不要直接要求 AI "Fix this"。
-   **Explain**: 先問 "Explain why this error happens based on the code provided."（確認 AI 理解根因）。
-   **Fix**: 再問 "Suggest a fix that handles edge case X."（獲取解決方案）。
-   **Test**: 最後要求 "Generate a unit test to reproduce this bug and verify the fix."（生成回歸測試）。

### 3. Log Enrichment (日誌增強)
當錯誤不明顯（例如 Silent Failure）時，不要讓 AI 瞎猜。
-   **Pattern**: 要求 AI 幫你在關鍵路徑插入詳細的 Logging 語句。
-   **Prompt**: "I suspect a race condition in this function. Add strategic console logs or print statements with timestamps and thread IDs to help me trace the execution flow."

### 4. Error Translation (錯誤翻譯)
對於晦澀難懂的底層錯誤（如 C++ Segmentation Fault 或 Minified JavaScript Error），AI 擅長將其翻譯為人類可讀的邏輯錯誤。
-   **Practice**: 貼上混淆後的錯誤訊息與 Source Map 的片段（如果有的話），讓 AI 推導原始錯誤位置。

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Blind Paste" (盲目複製貼上)
-   **描述**：直接將 AI 給出的程式碼貼回 IDE 並執行，完全不閱讀內容。
-   **風險**：AI 可能引入了微妙的邏輯 Bug、刪除了必要的錯誤處理機制，或使用了不存在的 Package (Hallucination)。
-   **避免**：永遠先做 Code Review，再做 Copy Paste。

### 2. Leak by Prompting (提示詞洩密)
-   **描述**：將含有 API Key、資料庫密碼或客戶 PII (個人識別資訊) 的 Log 直接貼給公有 AI 模型。
-   **風險**：嚴重的資安違規與資料外洩。
-   **避免**：建立「淨化 (Sanitize)」習慣，將敏感字串替換為 `<REDACTED_TOKEN>` 後再發送。

### 3. Fixing Symptoms, Not Root Causes (治標不治本)
-   **描述**：AI 傾向於讓錯誤訊息消失。例如遇到 `NullReferenceException`，AI 可能建議加一個 `if (obj != null)` 檢查，但真正的問題可能是「為什麼 obj 會是 null？」。
-   **風險**：掩蓋了系統架構層面的問題，導致技術債累積。
-   **避免**：追問 AI "Is this just suppressing the error, or fixing the root cause?"

### 4. Context Window Overflow (上下文溢出)
-   **描述**：一次貼上幾千行無關的程式碼。
-   **風險**：AI 的注意力被分散，導致忽略了關鍵的錯誤細節，或產生幻覺。
-   **避免**：只提供與錯誤直接相關的 Call Stack 上下文。

## Checklists & workflows｜檢查清單與流程

在開始 AI 輔助除錯之前與之後，請遵循此標準作業程序 (SOP)：

### Phase 1: Preparation (準備階段)
- [ ] **Sanitization**: 我是否已從 Log 和程式碼中移除了所有密碼、金鑰和個資？
- [ ] **Isolation**: 我是否已定位到發生錯誤的最小程式碼範圍？
- [ ] **Reproduction**: 我是否能穩定重現此錯誤？

### Phase 2: Interaction (互動階段)
- [ ] **Prompt Structure**: 我是否提供了 **3C** (Code, Crash, Context)？
- [ ] **Root Cause Analysis**: 我是否先要求 AI 解釋原因，而不是只求代碼？
- [ ] **Constraint Setting**: 我是否告知 AI 專案的限制（例如：不能升級 Library 版本、必須相容舊瀏覽器）？

### Phase 3: Verification (驗證階段)
- [ ] **Code Review**: AI 的修復方案是否符合團隊的 Coding Style？有沒有引入多餘的依賴？
- [ ] **Test Case**: 我是否利用 AI 生成了針對此 Bug 的單元測試？
- [ ] **Regression Check**: 修復後是否破壞了現有的功能？

## Real-world examples｜實戰案例

### Example 1: Debugging a React Hydration Error
**情境**：Next.js 專案在 Console 出現 `Text content does not match server-rendered HTML`。

**Bad Prompt**:
> "Fix this error: Text content does not match server-rendered HTML."
> *(AI 可能會給出通用的建議，如關閉 SSR，這是糟糕的建議)*

**Good Prompt**:
> "I'm getting a hydration mismatch error in Next.js.
> **Code**: Here is my `Navbar` component which uses `window.localStorage` to check for dark mode preference. [Paste Code]
> **Context**: The error appears on initial load. I suspect it's because `window` is undefined on the server.
> **Task**: Explain why the mismatch happens and provide a fix that uses `useEffect` to handle client-side only rendering safely."

**Result**: AI 解釋了 Server 端渲染與 Client 端渲染的差異，並提供了使用 `useEffect` 或 `dynamic import` 的正確解法，而非粗暴地關閉檢查。

---

### Example 2: Deciphering a Python Pandas `SettingWithCopyWarning`
**情境**：資料處理 Pipeline 出現警告，雖然程式沒崩潰，但資料可能未正確寫入。

**Workflow**:
1.  **Input**: 貼上出現警告的程式碼片段與 Warning 訊息。
2.  **AI Analysis**: AI 指出你在對 DataFrame 的切片 (Slice) 進行賦值，Pandas 無法確定你是要修改原圖還是副本。
3.  **Solution**: AI 建議使用 `.loc[row_indexer, col_indexer] = value` 來明確指定賦值操作。
4.  **Verification**: 要求 AI 生成一個小的 DataFrame 範例，演示錯誤寫法與正確寫法的差異，確認警告消失且資料正確更新。

---

### Example 3: Troubleshooting SQL Performance
**情境**：某個 API 查詢回應時間過長 (Timeout)。

**Prompt**:
> "Here is my PostgreSQL query: [Paste SQL].
> Here is the table schema: [Paste Schema].
> The query takes 5 seconds to run on a table with 1M rows.
> I ran `EXPLAIN ANALYZE` and got this output: [Paste Plan].
> Analyze the query plan, identify the bottleneck (e.g., sequential scan), and suggest specific indexes to add."

**Result**: AI 分析執行計畫，指出 `WHERE user_id = ? AND status = 'active'` 正在進行全表掃描 (Seq Scan)，建議建立複合索引 (Composite Index)，並給出 `CREATE INDEX` 語法。