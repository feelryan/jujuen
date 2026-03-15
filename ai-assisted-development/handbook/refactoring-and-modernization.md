# 重構、優化與遺留代碼現代化 / Refactoring, Optimization, and Legacy Code Modernization

## Mental model｜心智模型

在利用 AI 進行重構與現代化時，不應將 AI 視為「全自動翻新機器」，而應視為一位 **「博學但缺乏上下文的考古學家兼翻譯官」 (Knowledgeable but Context-Unaware Archaeologist & Translator)**。

### 核心概念 / Core Concepts

1.  **Chesterton's Fence (切斯特頓的柵欄原則)**：
    *   **Concept**: 在移除或修改一段看似愚蠢的舊程式碼之前，必須先理解當初為什麼要這樣寫。
    *   **AI Role**: AI 非常擅長解釋「這段程式碼在做什麼 (What)」，但往往不知道「為什麼要這樣做 (Why)」。
    *   **Action**: 先利用 AI 進行 **Code Explanation (代碼解釋)**，確認理解無誤後，再進行 **Refactoring (重構)**。

2.  **Behavior Preservation (行為保留)**：
    *   **Concept**: 重構的定義是在「不改變外部行為」的前提下改善內部結構。
    *   **AI Role**: AI 生成的優化代碼可能會無意中改變邊緣案例 (Edge cases) 的處理邏輯。
    *   **Action**: 必須建立 **Safety Net (測試保護網)**。AI 應先生成測試案例，確保舊代碼通過測試，再生成新代碼並通過相同測試。

3.  **Cognitive Load Reduction (降低認知負荷)**：
    *   **Concept**: 現代化的目標是讓代碼更易讀、更易維護。
    *   **AI Role**: AI 是降低認知負荷的槓桿，它能將晦澀的變數命名 (`var a, b, x`) 轉換為語意化命名，或將巢狀的 Callback hell 攤平。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. The "Explain-Then-Refactor" Loop (先解釋，後重構迴圈)
不要直接要求 AI 重寫代碼，這容易導致幻覺或邏輯遺失。請遵循以下模式：
*   **Step 1**: "Explain this code to me line by line. What are the edge cases?" (請逐行解釋這段代碼，有哪些邊緣案例？)
*   **Step 2**: "Based on your explanation, suggest a refactoring plan to improve readability." (根據你的解釋，提出一個提升可讀性的重構計畫。)
*   **Step 3**: "Execute the plan." (執行計畫。)

### 2. Generating "Characterization Tests" (生成特徵測試)
面對沒有測試的 Legacy Code，先讓 AI 幫你寫測試，鎖定當前行為。
*   **Prompt Pattern**: "Write a comprehensive unit test suite for the following legacy function using [Testing Framework]. Cover happy paths and edge cases to capture its *current* behavior exactly, even if the behavior seems buggy."
*   **Why**: 這是重構的安全網，確保 AI 的優化沒有破壞現有業務邏輯。

### 3. Syntax Modernization (語法現代化)
將舊語法轉換為現代語法（Idiomatic usage），提升效能與安全性。
*   **Java**: `for` loops $\rightarrow$ `Stream API`
*   **JavaScript**: Callbacks/Promises $\rightarrow$ `async/await`
*   **Python**: List comprehensions, Type hinting additions.
*   **Prompt**: "Convert this code to modern [Language] syntax (version X+). Use idiomatic patterns but strictly preserve logic."

### 4. Semantic Renaming (語意化命名優化)
AI 對於推斷變數用途非常強大。
*   **Context**: 當你看到 `int d; // elapsed time in days`。
*   **Action**: 讓 AI 掃描整段邏輯，建議更精確的命名（如 `daysSinceLastLogin`），並自動完成所有引用的替換。

### 5. Pattern-Based Refactoring (基於設計模式的重構)
識別代碼中的 "Code Smells" 並應用設計模式。
*   **Example**: 將巨大的 `switch/case` 或 `if/else` 鏈轉換為 **Strategy Pattern (策略模式)** 或 **Polymorphism (多型)**。
*   **Prompt**: "Identify design patterns that could simplify this class. Refactor it to use the Strategy Pattern to handle the conditional logic."

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Big Bang" Rewrite (大爆炸式重寫)
*   **Anti-pattern**: 將整個檔案（數百行）貼給 AI 並說「幫我優化」。
*   **Risk**: AI 會遺失細節，忽略錯誤處理，甚至產生幻覺（Hallucination），創造出不存在的函數調用。
*   **Correction**: 採用 **Iterative Refactoring (迭代式重構)**，一次只重構一個函數或一個模組。

### 2. Blindly Trusting "Optimization" (盲目相信優化)
*   **Anti-pattern**: AI 建議將某個演算法從 $O(n^2)$ 優化為 $O(n)$，開發者直接複製貼上。
*   **Risk**: 優化後的演算法可能忽略了數據規模較小時的常數開銷，或者改變了排序穩定性 (Stability)，甚至引入了新的 Bug。
*   **Correction**: 要求 AI 解釋優化的原理，並對比前後的 Benchmark 或邏輯正確性。

### 3. Losing Business Intent (遺失業務意圖)
*   **Anti-pattern**: 讓 AI 清理「冗餘代碼」，結果它刪除了看似無用但實際是為了相容舊系統的邏輯（例如特定的資料格式轉換）。
*   **Risk**: 系統崩潰或資料損毀。
*   **Correction**: 在 Prompt 中明確標註 "Strictly preserve all business logic and side effects" (嚴格保留所有業務邏輯與副作用)。

### 4. Security Regression (安全性退化)
*   **Anti-pattern**: 在現代化過程中，AI 移除了看似醜陋的輸入驗證代碼。
*   **Risk**: 該代碼可能是為了防禦 SQL Injection 或 XSS 而特意寫的 Patch。
*   **Correction**: 重構後必須進行安全性掃描，並詢問 AI：「這次重構是否移除了任何潛在的安全檢查？」

---

## Checklists & workflows｜檢查清單與流程

在進行 AI 輔助重構時，請依照此流程操作：

### Workflow: The Safety Sandwich (安全三明治流程)
1.  **Analyze (分析)**: AI 解釋代碼 $\rightarrow$ 人工確認理解。
2.  **Secure (固化)**: AI 生成測試 $\rightarrow$ 運行測試確保通過（Green）。
3.  **Refactor (重構)**: AI 執行重構 $\rightarrow$ 人工 Code Review。
4.  **Verify (驗證)**: 再次運行測試 $\rightarrow$ 確保依然通過（Green）。

### Checklist for Reviewers

- [ ] **Logic Preservation**: 重構後的代碼邏輯流程是否與原代碼一致？(Did the logic flow remain consistent?)
- [ ] **Test Coverage**: 是否有針對該模組的單元測試？重構前後測試是否都通過？(Do tests pass both before and after?)
- [ ] **Naming**: 變數與函數命名是否更清晰且符合上下文？(Are names clearer and context-aware?)
- [ ] **Comments**: 重要的 "Why" 註解是否被保留？AI 是否添加了必要的文檔註解？(Are "Why" comments preserved?)
- [ ] **Dependencies**: 是否引入了不必要的外部依賴？(Did it introduce unnecessary dependencies?)
- [ ] **Hallucinations**: 檢查是否有調用不存在的方法或屬性？(Check for non-existent method calls.)

---

## Real-world examples｜實戰案例

### Example 1: De-obfuscating Legacy Variables (變數去模糊化)

**Scenario**: 維護一段 10 年前的計費邏輯，變數全是 `a`, `b`, `t`。

**Original Code (Legacy):**
```python
def c(a, b):
    t = 0
    if a > 100:
        t = a * 0.9
    else:
        t = a
    return t * b
```

**Prompt**:
> "Analyze this Python function. Infer the meaning of variables `a`, `b`, and `t` based on standard e-commerce logic (price, quantity, discount). Rename variables to be semantic and add type hints."

**AI Refactored Code:**
```python
def calculate_total_price(price: float, quantity: int) -> float:
    """Calculates total price applying a 10% discount for prices over 100."""
    discounted_price = 0.0
    if price > 100:
        discounted_price = price * 0.9
    else:
        discounted_price = price
    
    return discounted_price * quantity
```

### Example 2: Modernizing Control Flow (控制流程現代化)

**Scenario**: 將 JavaScript 的 Callback Hell 轉換為現代 `async/await`。

**Original Code (Callback Hell):**
```javascript
function getUserData(id, callback) {
  db.findUser(id, function(err, user) {
    if (err) return callback(err);
    db.getPermissions(user.roleId, function(err, perms) {
      if (err) return callback(err);
      callback(null, { user, perms });
    });
  });
}
```

**Prompt**:
> "Refactor this JavaScript code to use `async/await` and `try/catch` for error handling. Keep the function signature compatible if possible, or suggest a modern signature."

**AI Refactored Code:**
```javascript
async function getUserData(id) {
  try {
    const user = await db.findUser(id);
    const perms = await db.getPermissions(user.roleId);
    return { user, perms };
  } catch (error) {
    throw error; // Or handle error appropriately
  }
}
```

### Example 3: Extracting Methods from "God Methods" (上帝函數拆解)

**Scenario**: 一個長達 200 行的 `processOrder` 函數。

**Workflow**:
1.  選取前 50 行（負責驗證庫存）。
2.  **Prompt**: "Extract the selected code into a private method named `validateInventory`. Pass necessary parameters."
3.  選取中間 50 行（負責付款）。
4.  **Prompt**: "Extract this into `processPayment`."
5.  最後重組主函數，使其讀起來像是一個高層次的流程描述。