# Chapter 03: Code Refactoring and Design Patterns
# 第 3 章：程式碼重構與設計模式應用

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

In this chapter, we move beyond simple code generation to high-level architectural improvements. For Senior Engineers, the value of AI lies not in typing faster, but in acting as a catalyst for paying down technical debt and modernizing legacy systems. We will explore how to leverage AI to identify architectural decay and apply standard design patterns effectively.
在本章中，我們將超越單純的程式碼生成，進階至高層次的架構改善。對於資深工程師而言，AI 的價值不在於打字更快，而在於作為償還技術債與現代化舊系統的催化劑。我們將探討如何利用 AI 識別架構腐壞（Architectural Decay），並有效地應用標準設計模式。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Detect & Diagnose Code Smells:** Use AI to analyze complex codebases and identify violations of SOLID principles or specific anti-patterns (e.g., God Class, Feature Envy).
    **偵測與診斷程式碼異味（Code Smells）：** 利用 AI 分析複雜的程式碼庫，並識別違反 SOLID 原則或特定反模式（如 God Class、Feature Envy）的地方。
2.  **Apply Design Patterns Contextually:** Leverage AI to suggest and implement appropriate design patterns (Strategy, Factory, Observer, etc.) to decouple logic, rather than blindly applying patterns where they aren't needed.
    **依情境應用設計模式：** 利用 AI 建議並實作合適的設計模式（如 Strategy、Factory、Observer 等）來解耦邏輯，而非盲目地在不需要的地方套用模式。
3.  **Modernize Legacy Code Safely:** Execute a strategy for refactoring legacy code (e.g., converting nested conditionals to polymorphism) while using AI to generate regression tests to ensure safety.
    **安全地現代化舊程式碼：** 執行舊程式碼重構策略（例如將巢狀條件判斷轉換為多型），同時利用 AI 生成回歸測試以確保安全性。
4.  **Evaluate AI Suggestions:** Critically assess AI-generated refactoring proposals for over-engineering or performance regressions.
    **評估 AI 建議：** 批判性地評估 AI 生成的重構提案，避免過度設計（Over-engineering）或效能倒退。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### The AI as a "Context-Aware Static Analysis Tool"
### AI 作為「具備上下文感知的靜態分析工具」

Traditionally, tools like SonarQube or ESLint rely on **Abstract Syntax Trees (AST)** and predefined rules to catch syntax errors or style violations. They are excellent at catching *syntactic* issues but struggle with *semantic* intent.
傳統上，像 SonarQube 或 ESLint 這類工具依賴 **抽象語法樹（AST）** 與預定義規則來捕捉語法錯誤或風格違規。它們非常擅長捕捉「語法」問題，但難以理解「語意」意圖。

**AI (LLMs)** operates differently. It functions closer to a **Senior Pair Programmer** who understands the *intent* of the code. It can recognize that a block of code is "trying to validate an order but is tightly coupled to the database," a nuance that AST-based tools often miss.
**AI (LLMs)** 的運作方式不同。它的功能更接近一位**資深結對工程師（Senior Pair Programmer）**，能理解程式碼的「意圖」。它能識別出某段程式碼「試圖驗證訂單，但與資料庫高度耦合」，這是基於 AST 的工具經常忽略的細微差別。

### Mental Model: Refactoring Pipeline
### 心智模型：重構流水線

When using AI for refactoring, visualize the process not as a single "fix this" command, but as a pipeline:
在使用 AI 進行重構時，不要將過程視為單一的「修復這個」指令，而應視為一個流水線：

1.  **Discovery (理解):** Feed the AI the code and ask it to explain the business logic. If the AI is confused, the code is likely too complex (Cognitive Complexity).
    **Discovery (理解):** 將程式碼提供給 AI 並要求其解釋商業邏輯。如果 AI 感到困惑，代表程式碼可能過於複雜（認知複雜度過高）。
2.  **Diagnosis (診斷):** Ask AI to identify violations of principles (SRP, DRY, DIP).
    **Diagnosis (診斷):** 要求 AI 識別違反原則的地方（SRP, DRY, DIP）。
3.  **Prescription (處方):** Ask for architectural options (e.g., "Should we use Strategy Pattern or Template Method here?").
    **Prescription (處方):** 詢問架構選項（例如：「這裡我們應該用策略模式還是樣板方法？」）。
4.  **Surgery (手術):** Generate the refactored code *and* the tests to verify it.
    **Surgery (手術):** 生成重構後的程式碼*以及*驗證用的測試。

### Difference: Linter vs. AI
### 差異對照：Linter vs. AI

| Feature | Linter / Static Analysis | AI-Assisted Refactoring |
| :--- | :--- | :--- |
| **Scope** | Line-by-line, File-level syntax | Logic flow, Architecture, Cross-file dependencies |
| **Detection** | Unused variables, formatting, basic bugs | "God Class", "Shotgun Surgery", "Primitive Obsession" |
| **Suggestion** | "Remove this variable" | "Extract this logic into a Strategy Pattern" |
| **Context** | Zero / Low | High (can consider variable names, comments, and intent) |

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### Modernizing Monoliths & Technical Debt
### 單體架構現代化與技術債

In a real-world production environment, you rarely write greenfield code. You are mostly maintaining or evolving existing systems. AI excels at **Legacy Modernization**.
在真實的生產環境中，你很少撰寫全新的程式碼（Greenfield）。你大多是在維護或演進現有系統。AI 在 **舊系統現代化（Legacy Modernization）** 方面表現卓越。

**Scenario:** You have a 5,000-line `OrderService.java` (a God Class).
**場景：** 你有一個 5,000 行的 `OrderService.java`（上帝類別）。

*   **Impact on Scalability:** The class is too risky to touch. New features are added as "patches" on top, increasing fragility.
    **對可擴充性的影響：** 該類別修改風險太高。新功能只能以「補丁」形式疊加，增加了脆弱性。
*   **AI's Role:**
    *   **Extract Microservices:** AI can help identify "Seams" (boundaries) in the code where logic can be extracted into a separate service or module.
    *   **Interface Extraction:** AI can generate interfaces for tightly coupled dependencies, enabling Dependency Injection (DI) and making the system testable.

### The "Boy Scout Rule" with AI
### 結合 AI 的「童子軍法則」

The Boy Scout Rule states: "Always leave the code better than you found it." With AI, the cost of this "cleanup" is drastically reduced.
童子軍法則指出：「離開時，程式碼要比你發現時更乾淨。」有了 AI，這種「清理」的成本大幅降低。

*   **Before:** Refactoring a complex `switch` statement might take 2 hours of analysis and testing.
    **過去：** 重構一個複雜的 `switch` 敘述可能需要 2 小時的分析與測試。
*   **After:** You can paste the snippet into an AI chat, ask for a "Strategy Pattern refactor with unit tests," review it in 10 minutes, and merge. This accelerates the rate at which technical debt is paid down.
    **現在：** 你可以將片段貼入 AI 聊天視窗，要求「使用策略模式重構並附帶單元測試」，10 分鐘內審查完畢並合併。這加速了償還技術債的速率。

---

## 4. Walkthrough: Refactoring a Payment Module
## 4. 逐步示例：重構支付模組

### The Problem: Spaghetti Code (Primitive Obsession)
### 問題：義大利麵程式碼（原始型別偏執）

We have a legacy payment processor that uses a massive `if-else` block to handle different payment methods. This violates the **Open/Closed Principle** (Open for extension, closed for modification).
我們有一個舊的支付處理器，使用巨大的 `if-else` 區塊來處理不同的支付方式。這違反了 **開閉原則（Open/Closed Principle）**（對擴充開放，對修改封閉）。

#### Step 1: The Legacy Code (Python Example)
#### 步驟 1：舊程式碼（Python 範例）

```python
class PaymentProcessor:
    def process_payment(self, amount: float, method: str, details: dict):
        if method == 'credit_card':
            print(f"Charging {amount} to Credit Card {details.get('number')}")
            # ... 20 lines of validation logic ...
        elif method == 'paypal':
            print(f"Redirecting to PayPal for {amount}")
            # ... 15 lines of API logic ...
        elif method == 'crypto':
            print(f"Processing crypto transaction for {amount}")
            # ... 30 lines of blockchain logic ...
        else:
            raise ValueError("Unknown payment method")
```

### Step 2: Diagnosis with AI
### 步驟 2：使用 AI 診斷

**Prompt:**
> "Analyze the following `PaymentProcessor` class. Identify any code smells and violations of SOLID principles. Suggest a design pattern to improve maintainability."
> 「分析以下的 `PaymentProcessor` 類別。識別任何程式碼異味與 SOLID 原則的違規之處。建議一個設計模式以提升可維護性。」

**AI Output (Summary):**
*   **Smell:** Long Method, Switch Statements.
*   **Violation:** Open/Closed Principle (adding a new method requires modifying existing code).
*   **Suggestion:** Use the **Strategy Pattern**. Create a common interface for payments and concrete classes for each method.

### Step 3: Refactoring Execution
### 步驟 3：執行重構

**Prompt:**
> "Refactor this code to use the Strategy Pattern.
> 1. Define an abstract base class `PaymentStrategy`.
> 2. Implement concrete strategies: `CreditCardStrategy`, `PayPalStrategy`, `CryptoStrategy`.
> 3. Update `PaymentProcessor` to accept a strategy instance.
> 4. Ensure type hinting is strictly used."
> 「將此程式碼重構為策略模式。
> 1. 定義抽象基底類別 `PaymentStrategy`。
> 2. 實作具體策略：`CreditCardStrategy`、`PayPalStrategy`、`CryptoStrategy`。
> 3. 更新 `PaymentProcessor` 以接受策略實例。
> 4. 確保嚴格使用型別提示。」

#### Refactored Code (Generated by AI)
#### 重構後的程式碼（由 AI 生成）

```python
from abc import ABC, abstractmethod

# 1. The Strategy Interface
class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float, details: dict) -> None:
        pass

# 2. Concrete Strategies
class CreditCardStrategy(PaymentStrategy):
    def pay(self, amount: float, details: dict) -> None:
        print(f"Charging {amount} to Credit Card {details.get('number')}")
        # Logic encapsulated here

class PayPalStrategy(PaymentStrategy):
    def pay(self, amount: float, details: dict) -> None:
        print(f"Redirecting to PayPal for {amount}")
        # Logic encapsulated here

# 3. Context
class PaymentProcessor:
    def __init__(self, strategy: PaymentStrategy):
        self.strategy = strategy

    def process(self, amount: float, details: dict):
        self.strategy.pay(amount, details)

# Usage
processor = PaymentProcessor(CreditCardStrategy())
processor.process(100.0, {"number": "1234-5678"})
```

### Step 4: Verification (The Critical Senior Step)
### 步驟 4：驗證（資深工程師的關鍵步驟）

A Senior Engineer knows that refactoring without tests is dangerous.
資深工程師知道，沒有測試的重構是危險的。

**Prompt:**
> "Generate `pytest` unit tests for the `CreditCardStrategy`. Also, create a test case that verifies the `PaymentProcessor` correctly delegates to the strategy."
> 「為 `CreditCardStrategy` 生成 `pytest` 單元測試。同時，建立一個測試案例來驗證 `PaymentProcessor` 是否正確地委派給策略。」

This ensures that while we changed the structure, the behavior remains correct.
這確保了雖然我們改變了結構，但行為仍然正確。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 1. Pattern Obsession (Over-engineering)
### 1. 模式偏執（過度設計）

*   **Pitfall:** Asking AI to "optimize" simple code often leads it to suggest complex patterns (e.g., applying Abstract Factory to a simple object creation).
    **錯誤：** 要求 AI「優化」簡單的程式碼，常導致它建議複雜的模式（例如對簡單的物件建立套用抽象工廠模式）。
*   **Why it's bad:** Increases cognitive load and boilerplate without adding value.
    **壞處：** 增加了認知負擔與樣板程式碼，卻未增加價值。
*   **Better Approach:** Explicitly ask AI: "Is a design pattern necessary here, or is a simple function extraction sufficient? List pros and cons."
    **較佳做法：** 明確詢問 AI：「這裡有必要使用設計模式嗎？還是簡單的函式提取就足夠了？請列出優缺點。」

### 2. Context Hallucination (Breaking Dependencies)
### 2. 上下文幻覺（破壞依賴關係）

*   **Pitfall:** Refactoring a method in isolation without providing the AI with the caller's context. The AI might change the method signature (arguments/return type).
    **錯誤：** 在未提供呼叫者上下文的情況下，單獨重構某個方法。AI 可能會更改方法簽章（參數/回傳型別）。
*   **Why it's bad:** Breaks the build or runtime compatibility with other parts of the system.
    **壞處：** 破壞建置或與系統其他部分的執行期相容性。
*   **Better Approach:** Always include the method signature and usage examples (call sites) in the prompt context.
    **較佳做法：** 務必在提示詞上下文中包含方法簽章與使用範例（呼叫點）。

### 3. Blindly Trusting "Modern" Syntax
### 3. 盲目信任「現代」語法

*   **Pitfall:** AI often suggests the latest language features (e.g., Python 3.12 features or Java 21 preview features) even if your production environment is on an older version.
    **錯誤：** AI 經常建議最新的語言功能（例如 Python 3.12 功能或 Java 21 預覽功能），即使你的生產環境是在較舊的版本上。
*   **Why it's bad:** Code works locally but crashes in CI/CD or production.
    **壞處：** 程式碼在本地端可運作，但在 CI/CD 或生產環境中崩潰。
*   **Better Approach:** Specify constraints: "Refactor this for Java 11 compatibility."
    **較佳做法：** 指定限制條件：「請針對 Java 11 相容性進行重構。」

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: Refactoring Strategy
### Q1: 重構策略

**Question:** "You inherit a legacy codebase with zero tests and high coupling. How do you use AI to help you refactor it safely?"
**問題：** 「你接手了一個零測試且高耦合的舊程式碼庫。你會如何利用 AI 協助你安全地重構它？」

**Key Points for High Score:**
**高分回答要點：**
*   **Characterization Tests:** First, use AI to generate "Characterization Tests" (tests that lock in current behavior, even bugs) before changing any code.
    **特徵測試：** 首先，在修改任何程式碼之前，利用 AI 生成「特徵測試」（鎖定當前行為的測試，即使是 Bug 也要鎖定）。
*   **Incremental Approach:** Don't rewrite everything. Use AI to identify the hottest/riskiest paths and refactor those first.
    **增量方法：** 不要重寫所有東西。利用 AI 識別最熱門/最高風險的路徑，並優先重構這些部分。
*   **Understanding over Editing:** Emphasize using AI to *explain* the code first to build a mental model.
    **理解重於編輯：** 強調先利用 AI *解釋*程式碼以建立心智模型。

### Q2: Design Pattern Trade-offs
### Q2: 設計模式的權衡

**Question:** "AI suggests replacing a series of conditionals with the Visitor Pattern. Would you accept this suggestion? Why or why not?"
**問題：** 「AI 建議將一系列條件判斷替換為 Visitor Pattern（訪問者模式）。你會接受這個建議嗎？為什麼？」

**Key Points for High Score:**
**高分回答要點：**
*   **Complexity Check:** Visitor pattern is powerful but introduces high complexity (double dispatch). Is the problem complex enough to warrant it?
    **複雜度檢查：** Visitor 模式強大但引入了高複雜度（雙重分派）。問題是否複雜到值得這樣做？
*   **Stability of Structure:** Visitor works best when the object structure is stable but operations change often. If the object structure changes frequently, Visitor is a bad choice.
    **結構穩定性：** Visitor 最適合物件結構穩定但操作經常變化的情況。如果物件結構頻繁變更，Visitor 是個糟糕的選擇。
*   **Seniority:** Demonstrate the ability to *reject* AI advice based on future maintainability concerns.
    **資深能力：** 展現出基於未來可維護性考量而*拒絕* AI 建議的能力。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Key Takeaways (記憶錨點)
### 重點摘要

1.  **Intent > Syntax:** AI is not just a linter; use it to understand and improve architectural intent.
    **意圖 > 語法：** AI 不僅是 Linter；用它來理解並改善架構意圖。
2.  **Refactoring Pipeline:** Discovery -> Diagnosis -> Prescription -> Surgery. Follow this flow.
    **重構流水線：** 理解 -> 診斷 -> 處方 -> 手術。遵循此流程。
3.  **Tests are Non-Negotiable:** Never refactor with AI without asking it to generate regression tests first.
    **測試不可妥協：** 絕不在未要求 AI 生成回歸測試的情況下進行重構。
4.  **Guard against Over-engineering:** Just because AI *can* apply a pattern doesn't mean it *should*.
    **防範過度設計：** 僅僅因為 AI *能*套用模式，不代表它*應該*這樣做。
5.  **Context is King:** Always provide surrounding code or interfaces to prevent breaking changes.
    **上下文為王：** 務必提供周邊程式碼或介面，以防止破壞性變更。

### Next Steps
### 下一步

*   **Practice:** Take a module from your current project that you hate touching. Use the "Discovery -> Diagnosis" prompt technique to analyze why it's bad.
    **實作：** 從你目前的專案中挑選一個你討厭碰觸的模組。使用「理解 -> 診斷」的提示技巧來分析它為什麼糟糕。
*   **Next Chapter:** Once code is refactored, how do we ensure it stays robust? Proceed to **Chapter 04: AI-Driven Testing and Quality Assurance**.
    **下一章：** 程式碼重構後，我們如何確保它保持強健？請前往 **第 4 章：AI 驅動的測試與品質保證**。