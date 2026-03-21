# 1. 前言與學習目標 (Introduction & Learning Objectives)

在資深工程師的職涯中，面對「全新專案（Greenfield）」的機會遠少於「既有系統（Brownfield/Legacy Code）」。如何安全地償還技術債，並將混亂的程式碼重構為符合設計模式的架構，是區分 Senior 與 Staff 工程師的關鍵能力。本章不只談論「什麼是設計模式」，更著重於「如何將爛 Code 演進為模式」。

In a Senior Software Engineer's career, opportunities to work on "Greenfield" projects are far rarer than working on "Brownfield/Legacy Code" systems. The ability to safely pay down technical debt and refactor chaotic code into a pattern-compliant architecture is a key differentiator between Senior and Staff engineers. This chapter focuses not just on "what design patterns are," but on "how to evolve bad code into patterns."

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **識別與診斷（Identify & Diagnose）**：能夠在 Legacy Code 中識別出適合引入特定設計模式的 Code Smells（程式碼異味），例如將龐大的 `if-else` 鏈重構為 **Strategy Pattern**。
    Identify Code Smells in Legacy Code that are suitable for introducing specific design patterns, such as refactoring massive `if-else` chains into the **Strategy Pattern**.
2.  **建立接縫（Create Seams）**：掌握在緊密耦合（Tightly Coupled）的系統中建立「接縫（Seams）」的技巧，以便在不破壞現有功能的前提下引入單元測試。
    Master the technique of creating "Seams" in tightly coupled systems to introduce unit tests without breaking existing functionality.
3.  **漸進式重構（Incremental Refactoring）**：理解並實作 **Strangler Fig Pattern**（絞殺榕模式）或 **Anti-Corruption Layer**（防腐層），以漸進方式替換舊邏輯，而非高風險的「Big Bang」重寫。
    Understand and implement the **Strangler Fig Pattern** or **Anti-Corruption Layer** to replace old logic incrementally, avoiding high-risk "Big Bang" rewrites.
4.  **權衡商業價值（Trade-off Business Value）**：在面試或實務中，能清晰解釋何時應該重構、何時應該容忍技術債，並以 ROI（投資報酬率）觀點說服 Stakeholders。
    Clearly explain when to refactor versus when to tolerate technical debt during interviews or practice, persuading stakeholders from an ROI perspective.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 重構與模式的關係 (Refactoring to Patterns)

許多工程師誤以為設計模式是在寫程式「之前」就決定好的。事實上，在處理 Legacy Code 時，設計模式往往是重構的「目標」，而非起點。這就是 Joshua Kerievsky 提出的 **"Refactoring to Patterns"** 概念。

Many engineers mistakenly believe that design patterns are decided "before" writing code. In reality, when dealing with Legacy Code, design patterns are often the "destination" of refactoring, not the starting point. This is the concept of **"Refactoring to Patterns"** proposed by Joshua Kerievsky.

*   **直覺類比**：想像你在整理一個雜亂無章的倉庫（Legacy Code）。你不會一開始就買好所有規格的收納箱（預設模式）。你會先將物品分類，發現「這裡有很多螺絲」，然後才決定買一個螺絲分類盒（引入適合的 Pattern）。
    **Intuitive Analogy**: Imagine organizing a chaotic warehouse (Legacy Code). You don't buy all specific storage bins (pre-defined patterns) right at the start. You sort the items first, realize "there are a lot of screws here," and *then* decide to buy a screw organizer (introduce the appropriate Pattern).

## 2.2 接縫 (Seams)

這是處理 Legacy Code 最重要的心智模型，由 Michael Feathers 定義。

This is the most critical mental model for dealing with Legacy Code, defined by Michael Feathers.

*   **定義**：接縫是指程式中的一個位置，你可以在不修改該處原始碼的情況下，改變程式的行為（通常是透過測試替身 Test Doubles）。
    **Definition**: A seam is a place where you can alter the behavior of the program without editing in that place (usually via Test Doubles).
*   **應用**：在重構前，必須先建立測試保護網。如果程式碼高度耦合（例如直接 `new Database()`），你就無法測試。你需要透過 **Dependency Injection (DI)** 或 **Extract Interface** 來創造接縫。
    **Application**: Before refactoring, you must establish a safety net of tests. If the code is tightly coupled (e.g., direct `new Database()`), you cannot test it. You need to create seams via **Dependency Injection (DI)** or **Extract Interface**.

## 2.3 技術債四象限 (The Technical Debt Quadrant)

Martin Fowler 的技術債四象限將債務分為「有意/無意」與「魯莽/謹慎」。

Martin Fowler's Technical Debt Quadrant categorizes debt into "Deliberate/Inadvertent" and "Reckless/Prudent".

*   **關鍵差異**：
    *   **Prudent & Deliberate（謹慎且有意）**：「我們現在必須發布，所以先寫死這個 Strategy，下週再重構。」——這是借貸。
    *   **Reckless & Inadvertent（魯莽且無意）**：「我不知道什麼是 Factory Pattern，所以我把所有邏輯都塞在 Controller 裡。」——這是無知。
*   **Key Differentiation**:
    *   **Prudent & Deliberate**: "We must ship now, so let's hardcode this Strategy and refactor next week." — This is borrowing.
    *   **Reckless & Inadvertent**: "I don't know what a Factory Pattern is, so I stuffed all logic into the Controller." — This is ignorance.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型系統設計與維運中，重構與技術債管理直接影響系統的 **可維護性 (Maintainability)** 與 **可測試性 (Testability)**。

In large-scale system design and operations, refactoring and technical debt management directly impact the system's **Maintainability** and **Testability**.

## 3.1 典型場景：單體裂解與防腐層 (Monolith Splitting & ACL)

當你需要將一個巨大的單體應用（Monolith）逐步拆解為微服務時，你不能讓新的微服務直接依賴舊的、混亂的資料庫 schema 或物件模型。

When you need to progressively split a massive Monolith into microservices, you cannot let the new microservices depend directly on the old, messy database schema or object models.

*   **Anti-Corruption Layer (ACL)**：這是一個介面卡模式（Adapter Pattern）與外觀模式（Facade Pattern）的架構級應用。它位於新舊系統之間，將舊系統的混亂模型轉換為新系統的乾淨模型，防止技術債「傳染」。
    **Anti-Corruption Layer (ACL)**: This is an architectural application of the Adapter and Facade Patterns. It sits between the new and old systems, translating the old system's messy models into the new system's clean models, preventing technical debt "contagion."

## 3.2 系統穩定性與 Feature Flags

在重構關鍵路徑（如支付流程）時，資深工程師會結合 **Strategy Pattern** 與 **Feature Flags**。

When refactoring critical paths (like payment flows), senior engineers combine the **Strategy Pattern** with **Feature Flags**.

*   **實作方式**：
    1.  定義一個 `PaymentStrategy` 介面。
    2.  保留舊邏輯為 `LegacyPaymentStrategy`。
    3.  實作新邏輯為 `ModernPaymentStrategy`。
    4.  在 Runtime 透過 Feature Flag 決定使用哪一個實作。
*   **Implementation**:
    1.  Define a `PaymentStrategy` interface.
    2.  Keep the old logic as `LegacyPaymentStrategy`.
    3.  Implement the new logic as `ModernPaymentStrategy`.
    4.  Decide which implementation to use at runtime via a Feature Flag.

這允許你在 Production 環境進行「金絲雀發布（Canary Release）」，將重構風險降至最低。

This allows you to perform "Canary Releases" in the Production environment, minimizing refactoring risk.

---

# 4. 逐步示例 (Walkthrough / Example)

## 案例背景 (Context)

我們有一個電子商務系統的 `OrderService`，負責處理訂單結帳。目前的程式碼是一個典型的 "God Class"，直接依賴了第三方支付 SDK（例如 PayPal）和資料庫操作。

We have an `OrderService` in an e-commerce system responsible for order checkout. The current code is a typical "God Class" that directly depends on third-party payment SDKs (e.g., PayPal) and database operations.

### 階段 1：原始的混亂代碼 (The Initial Mess)

這段程式碼難以測試，因為它直接 `new` 了外部依賴，且邏輯高度耦合。

This code is hard to test because it directly instantiates (`new`) external dependencies and the logic is tightly coupled.

```typescript
// Legacy Code: Hard to test, tightly coupled
class OrderService {
  processOrder(order: Order, paymentType: string): boolean {
    // 1. Validation Logic mixed in
    if (order.amount <= 0) return false;

    // 2. Direct dependency on Database (No Seam)
    const db = new DatabaseConnection("prod-db-url");
    
    // 3. Conditional complexity (Code Smell: Switch Statements)
    if (paymentType === "PAYPAL") {
      const paypal = new PayPalSDK(); // Hard dependency
      const result = paypal.makePayment(order.amount);
      if (result.success) {
        db.save(order, "PAID");
        return true;
      }
    } else if (paymentType === "STRIPE") {
      const stripe = new StripeSDK(); // Hard dependency
      const result = stripe.charge(order.amount);
      if (result.status === "200") {
        db.save(order, "PAID");
        return true;
      }
    }
    
    return false;
  }
}
```

### 階段 2：創造接縫與提取介面 (Creating Seams & Extracting Interfaces)

目標：引入 **Strategy Pattern** 來消除 `if-else`，並引入 **Dependency Injection** 來解耦。

Goal: Introduce the **Strategy Pattern** to eliminate `if-else` and introduce **Dependency Injection** for decoupling.

首先，定義支付處理的介面（Strategy Interface）。

First, define the interface for payment processing (Strategy Interface).

```typescript
interface PaymentProcessor {
  process(amount: number): boolean;
}

// Wrappers for external SDKs (Adapter Pattern)
class PayPalAdapter implements PaymentProcessor {
  private sdk = new PayPalSDK();
  process(amount: number): boolean {
    return this.sdk.makePayment(amount).success;
  }
}

class StripeAdapter implements PaymentProcessor {
  private sdk = new StripeSDK();
  process(amount: number): boolean {
    return this.sdk.charge(amount).status === "200";
  }
}
```

### 階段 3：重構主類別 (Refactoring the Main Class)

現在我們將 `OrderService` 重構為依賴介面，而非具體實作。

Now we refactor `OrderService` to depend on interfaces rather than concrete implementations.

```typescript
// Refactored Code: Testable, Decoupled
class OrderService {
  private paymentProcessors: Map<string, PaymentProcessor>;
  private db: DatabaseInterface;

  // Dependency Injection (Constructor Injection)
  constructor(
    db: DatabaseInterface, 
    processors: Map<string, PaymentProcessor>
  ) {
    this.db = db;
    this.paymentProcessors = processors;
  }

  processOrder(order: Order, paymentType: string): boolean {
    if (order.amount <= 0) return false;

    // Strategy Pattern usage
    const processor = this.paymentProcessors.get(paymentType);
    if (!processor) {
      throw new Error(`Payment method ${paymentType} not supported`);
    }

    const success = processor.process(order.amount);
    
    if (success) {
      this.db.save(order, "PAID");
      return true;
    }
    return false;
  }
}
```

### 階段 4：單元測試 (Unit Testing)

現在我們可以輕鬆地 Mock 資料庫與支付處理器，驗證 `OrderService` 的邏輯。

Now we can easily Mock the database and payment processors to verify the logic of `OrderService`.

```typescript
// Test Example (using a mocking framework concept)
const mockDb = new MockDatabase();
const mockPayPal = new MockPaymentProcessor(); // Always returns true
const processors = new Map();
processors.set("PAYPAL", mockPayPal);

const service = new OrderService(mockDb, processors);
const result = service.processOrder({ amount: 100 }, "PAYPAL");

assert(result === true);
assert(mockDb.saveCalled === true);
```

### 分析 (Analysis)

*   **複雜度**：我們將複雜度從 `OrderService` 轉移到了組裝物件的 Configuration 層（或 Dependency Injection Container）。
    **Complexity**: We shifted complexity from `OrderService` to the Configuration layer (or Dependency Injection Container) where objects are assembled.
*   **可擴充性**：新增一種支付方式只需新增一個 Adapter 並註冊到 Map 中，完全符合 **Open/Closed Principle (OCP)**。
    **Extensibility**: Adding a new payment method only requires adding an Adapter and registering it in the Map, fully complying with the **Open/Closed Principle (OCP)**.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 為了模式而模式 (Pattern Fever)

*   **錯誤描述**：看到一個簡單的 `if (isWeekend)` 判斷，就強行套用 Strategy Pattern。
    **Description**: Seeing a simple `if (isWeekend)` check and forcing a Strategy Pattern onto it.
*   **為何不好**：增加了不必要的類別與複雜度（Accidental Complexity）。
    **Why it's bad**: Increases unnecessary classes and Accidental Complexity.
*   **較佳方案**：遵循 **Rule of Three**。當類似的邏輯重複出現三次，或變更頻率很高時，才考慮重構為模式。
    **Better Approach**: Follow the **Rule of Three**. Only consider refactoring to a pattern when similar logic appears three times or changes frequently.

## 5.2 沒有測試的重構 (Refactoring Without Tests)

*   **錯誤描述**：在沒有建立「接縫」與測試保護網的情況下，直接修改 Legacy Code 的核心邏輯。
    **Description**: Directly modifying core logic of Legacy Code without establishing "seams" and a test safety net.
*   **為何不好**：這不是重構，這是賭博。你無法確保你的修改沒有破壞現有功能（Regression）。
    **Why it's bad**: This isn't refactoring; it's gambling. You cannot guarantee your changes haven't broken existing functionality (Regression).
*   **較佳方案**：先寫 **Characterization Tests**（特性測試），鎖定當前行為，再進行重構。
    **Better Approach**: Write **Characterization Tests** first to lock down current behavior, then refactor.

## 5.3 大爆炸重構 (Big Bang Refactoring)

*   **錯誤描述**：停止開發新功能兩個月，專門用來「清理技術債」。
    **Description**: Halting new feature development for two months specifically to "clean up technical debt."
*   **為何不好**：業務停擺，且長時間的分支（Long-lived branch）會導致巨大的 Merge Conflict 地獄。
    **Why it's bad**: Business halts, and long-lived branches lead to massive Merge Conflict hell.
*   **較佳方案**：**Boy Scout Rule**（童子軍法則）——每次觸碰程式碼時，讓它比你發現時乾淨一點點。
    **Better Approach**: **Boy Scout Rule** — Leave the code a little cleaner than you found it, every time you touch it.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 你如何處理一個完全沒有測試的 Legacy System？
**How do you handle a Legacy System with absolutely no tests?**

*   **高分回答要點**：
    *   承認不能直接重構。
    *   提到 **Characterization Tests**（特性測試）：不求測試邏輯正確，只求記錄當前行為（即使是 Bug 也要記錄）。
    *   尋找或創造 **Seams**（接縫）。
    *   優先針對「變更最頻繁」或「業務價值最高」的熱點進行重構，而非全盤重寫。

## Q2: 請解釋 Adapter Pattern 與 Facade Pattern 在重構中的區別？
**Explain the difference between Adapter Pattern and Facade Pattern in the context of refactoring.**

*   **高分回答要點**：
    *   **Adapter**：解決「介面不相容」問題。通常是一對一的轉換（例如將新的 `PaymentProcessor` 介面適配到舊的 `PayPalSDK`）。目的是讓舊元件能配合新系統。
    *   **Facade**：解決「介面複雜」問題。通常是一對多。為一個複雜的子系統（例如由多個類別組成的舊訂單系統）提供一個簡單的單一入口。目的是簡化呼叫。

## Q3: 什麼時候你應該選擇「重寫 (Rewrite)」而不是「重構 (Refactor)」？
**When should you choose to "Rewrite" instead of "Refactor"?**

*   **高分回答要點**：
    *   當技術棧已經完全過時（例如 COBOL 轉 Java），且找不到開發人員維護時。
    *   當重構的成本（時間/人力）經評估後顯著高於重寫時。
    *   當基礎架構或核心領域模型（Domain Model）有根本性的錯誤，無法透過漸進式修改修正時。
    *   強調這是一個 **Business Decision** 而非純技術決定。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 本章重點 (Key Takeaways)

1.  **Refactoring to Patterns**：設計模式是重構的「目的地」，用來解決具體的 Code Smells，而非預先設計的模板。
2.  **Seams (接縫)**：在修改 Legacy Code 前，必須先透過 DI 或介面提取創造接縫，以便插入測試。
3.  **Dependency Injection**：是解耦與提升可測試性的最強大工具，是許多設計模式（Strategy, State, Command）的基礎。
4.  **Strangler Fig Pattern**：在架構層面處理技術債的最佳實踐，允許新舊系統並存並逐步替換。
5.  **Safety First**：沒有測試的重構只是在冒險。先寫測試（Characterization Tests），再動程式碼。

## 後續延伸 (Next Steps)

*   **閱讀**：*Working Effectively with Legacy Code* (Michael Feathers) - 這是本章的聖經。
*   **閱讀**：*Refactoring to Patterns* (Joshua Kerievsky)。
*   **實作**：在下一個 Sprint 中，挑選一個複雜的 `switch/case` 或 `if-else` 區塊，嘗試用 Strategy Pattern 進行重構，並補上單元測試。
*   **下一章預告**：我們將探討 **Scalability Patterns**（可擴展性模式），學習如何在分散式系統中應用 CQRS 與 Event Sourcing。