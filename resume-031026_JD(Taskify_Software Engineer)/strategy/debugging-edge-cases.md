# 演算法驗證與除錯實戰 / Algorithm Validation & Debugging

這份攻略專為 **Ryan Hsiao** 量身打造。結合您 15+ 年的資深開發經驗（Java, C++, Python, JS）與 Taskify AI 的職缺需求（Code Evaluation/RLHF），本指南將協助您從「系統架構師」視角切換至「代碼審計員（Code Auditor）」視角，專注於捕捉 AI 生成代碼中的邏輯漏洞與邊界情況。

---

## Why this matters｜為什麼這個主題重要

### 1. The Core of the Role (職缺核心)
JD 明確指出職責包含 **"Review AI-generated code for technical accuracy"** 與 **"Validate algorithms"**。AI 模型（如 ChatGPT, Claude）生成的代碼通常在「快樂路徑（Happy Path）」上表現完美，但在邊界情況（Edge Cases）下經常崩潰。您的價值不在於寫出代碼，而在於**找出 AI 沒考慮到的盲點**。

### 2. Seniority as Leverage (資深經驗的槓桿)
作為一名資深工程師（Senior SE），您比初階工程師更了解「代碼在生產環境會如何失敗」。
- **Ryan's Advantage:** 您履歷中的 **TDD with JUnit5** 和 **FDA 510K (Medical context)** 經驗證明您具備嚴謹的驗證思維。
- **The Risk:** 資深工程師有時會過度關注「架構設計」，而忽略了基礎演算法的「實作細節（Implementation Details）」。此職缺需要您重新聚焦於 `Off-by-one error`、`Integer Overflow` 或 `Recursion Depth` 這些微觀細節。

### 3. RLHF Value (對模型訓練的價值)
在 RLHF（Reinforcement Learning from Human Feedback）中，指出「為什麼錯」比單純給出正確答案更有價值。您需要展示您能進行 **Root Cause Analysis (根本原因分析)**。

---

## Step‑by‑step strategy｜具體行動步驟

建議在接下來的 1-2 週內執行以下步驟：

### Step 1: Build an "Edge Case Taxonomy" (建立邊界案例分類學)
不要依賴直覺，建立一個系統化的檢查清單。針對您熟悉的語言（Java, Python, JS, C++），複習以下常見雷點：
- **Input Validity:** `Null`, `Undefined`, `Empty String/Array`, `Negative Numbers`.
- **Data Types:** `Integer Overflow` (Java/C++), `Floating Point Precision` (0.1 + 0.2 != 0.3 in JS/Python).
- **Structures:** Linked List 的 `Head/Tail` 操作，Graph 的 `Cycles`（環），Tree 的 `Unbalanced` 狀況。
- **Concurrency:** Race conditions (既然您懂 Java Spring Boot 與 Cloud，這點是加分項)。

### Step 2: Practice "Human Compiler" Drills (人腦編譯器訓練)
AI 面試或測驗通常要求您閱讀一段代碼並找出 Bug。
- **Action:** 每天花 20 分鐘在 LeetCode 上找 "Medium" 難度的題目，**不要寫程式**，而是去閱讀 "Discuss" 區別人的錯誤解法，試著在不執行代碼的情況下找出邏輯漏洞。

### Step 3: Polyglot Syntax Check (多語言語法檢核)
JD 要求 Python, JS, Java, C++。AI 常會混淆語言特性。
- **Action:** 複習跨語言差異。
    - *Sorting:* Python 的 `sort` 是穩定的嗎？C++ `std::sort` 呢？
    - *Memory:* C++ 需要手動釋放記憶體，Java/Python 則有 GC。AI 生成 C++ 代碼時常忘記 `delete` 或造成 Memory Leak。
    - *Scope:* JS 的 `var` vs `let` 變數提升（Hoisting）問題。

### Step 4: Refine Feedback Writing (優化回饋寫作)
您不僅要除錯，還要「教導」AI。
- **Action:** 練習撰寫 **Constructive Feedback**。
    - *Bad:* "This code is wrong."
    - *Good:* "The logic fails when `n=0`. The loop condition `i <= n` causes an IndexOutOfBoundsException. Suggest changing to `i < n` and adding a guard clause for empty inputs."

---

## Examples & templates｜範例與句型

在面試或實際工作中，使用結構化的語言來描述錯誤。

### 1. The "Bug Report" Template (除錯回饋範本)
當您發現 AI 代碼有誤時，請套用此結構：

> **Summary:** The algorithm correctly handles standard inputs but fails on edge cases.
> **Issue:** [Specific Edge Case, e.g., Empty Array]
> **Location:** Line 12, `for` loop condition.
> **Explanation:** The code assumes the input array always has at least one element. Accessing `arr[0]` throws an exception when `arr` is empty.
> **Correction:** Add a guard clause: `if (!arr || arr.length === 0) return null;`

### 2. Complexity Analysis Template (複雜度分析範本)
AI 常寫出效能低下的代碼（例如在雙重迴圈中做查找）。

> **Current Complexity:** Time $O(n^2)$, Space $O(1)$.
> **Critique:** While functional, the $O(n^2)$ approach will time out with large inputs (e.g., $N > 10^5$).
> **Optimization:** Using a Hash Map (or Dictionary) can reduce the lookup time to $O(1)$, bringing the total time complexity down to $O(n)$.

### 3. Specific Edge Case Checklist (針對性檢查清單)

| Category | Common AI Hallucinations / Bugs |
| :--- | :--- |
| **Math** | Division by zero; Integer overflow (Java/C++); Floating point equality checks. |
| **Recursion** | Missing base case (Stack Overflow); Redundant calculations (needs Memoization). |
| **Strings** | Unicode characters (Emoji handling); Case sensitivity; Trimming whitespace. |
| **Arrays** | Off-by-one errors (loops); Modifying array while iterating. |

---

## Signals for interviewers｜要讓面試官看到的訊號

若您依照上述策略準備，請在履歷篩選與 15 分鐘 AI 面試中展現以下特質：

1.  **The "Safety-First" Mindset (安全第一思維):**
    *   強調您在 Medical/Healthcare (Innova Solutions) 的背景，習慣於高標準的驗證與合規性檢查。這對 AI Code Evaluation 來說是極大的加分（代表您不會放過小錯誤）。
2.  **Polyglot Versatility (多語言切換能力):**
    *   展示您能迅速指出 "This is valid in Python but invalid in Java" 的能力。
3.  **Instructional Clarity (指導清晰度):**
    *   證明您不僅能寫 Code，還能清晰地解釋邏輯（這是 Technical Writer/Reviewer 的核心能力）。
4.  **Testing Rigor (測試嚴謹度):**
    *   主動提及 "I don't just look at the code; I mentally run it against a suite of test cases: null, negative, large scale, and concurrency scenarios."

---

## Common pitfalls｜常見錯誤與避免方式

### 1. Assuming the "Happy Path" is enough
*   **錯誤:** 看到代碼邏輯大方向正確就給予 "Pass"。
*   **修正:** 您的任務是 "Break the code"。假設輸入永遠是惡意的或格式錯誤的。

### 2. Overlooking Language-Specific Nuances
*   **錯誤:** 用 Python 的思維去審查 C++ 代碼（例如忽略 Pointer 或 Reference 的誤用）。
*   **修正:** 審查特定語言代碼時，切換該語言的「編譯器腦」。

### 3. Being Too Abstract
*   **錯誤:** 回饋只寫 "Optimize this function."
*   **修正:** 具體指出 "Replace the recursive Fibonacci with an iterative approach to avoid stack overflow for $n > 1000$."

---

## Checklist｜檢查清單

- [ ] **Mindset:** 我已準備好從「開發者」切換為「審計員/測試員」模式。
- [ ] **Review:** 我已複習 Big O Notation (Time/Space Complexity)。
- [ ] **Language:** 我已確認 Java, Python, JS, C++ 在 Array/String 處理上的主要語法差異。
- [ ] **Practice:** 我已嘗試對一段 AI 生成的代碼進行「找碴」，並寫出具體的修正建議。
- [ ] **Story:** 我準備好一個「過去工作中發現並修復棘手邊界情況 Bug」的故事（結合 JUnit5 經驗尤佳）。