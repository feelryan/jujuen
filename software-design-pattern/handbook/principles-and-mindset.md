# 核心原則與設計思維模型 / Core Principles and Design Mindset

本章節不談教科書式的定義背誦，而是聚焦於資深工程師如何運用這些原則來權衡設計決策。軟體設計的本質是對抗「複雜度」與「變化」，所有原則都是為了這兩個目的服務。

## Mental model｜心智模型

### 1. 軟體熵與複雜度管理 (Entropy & Complexity Management)
軟體開發中唯一不變的就是「變化」。隨著功能增加，系統自然的傾向是變得混亂（熵增）。
- **設計的目標**：降低「認知負荷 (Cognitive Load)」與「變更成本 (Cost of Change)」。
- **思維轉換**：不要為了「使用模式」而設計，要為了「隔離變化」而設計。
- **核心指標**：
  - **Cohesion (內聚力)**：相關的東西聚在一起。高內聚通常意味著好維護。
  - **Coupling (耦合度)**：不相關的東西分開。低耦合意味著好修改。

### 2. 抽象化的階梯 (The Ladder of Abstraction)
設計模式位於抽象化的中間層。
- **太過具體 (Too Concrete)**：寫死邏輯 (Hard-coding)，難以擴充。
- **太過抽象 (Too Abstract)**：過度設計 (Over-engineering)，難以理解與除錯。
- **Sweet Spot**：在「現在的需求」與「可預見的未來變化」之間取得平衡。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. SOLID 的實戰詮釋
不要死記定義，請記住它們解決的問題：

- **SRP (單一職責)**：
  - *實戰*：一個 Class 是否只有「一個理由」需要被修改？如果改 UI 要動它，改資料庫 Schema 也要動它，它就違反了 SRP。
  - *技巧*：將大 Class 拆解為小的 Collaborators。
- **OCP (開閉原則)**：
  - *實戰*：新增功能時，是「寫新的 Class」還是「修改舊的 `if-else`」？
  - *技巧*：善用 **Strategy Pattern** 或 **Polymorphism** 取代巨型 Switch 語句。
- **LSP (里氏替換)**：
  - *實戰*：子類別是否偷偷丟出了父類別沒宣告的 Exception？或是改變了父類別的行為預期？
  - *技巧*：如果你的程式碼充滿了 `if (obj instanceof Dog)`，你可能違反了 LSP。
- **ISP (介面隔離)**：
  - *實戰*：不要強迫實作者依賴他們不需要的方法。
  - *技巧*：將胖介面 (Fat Interface) 拆分為多個專用介面 (Role Interfaces)。
- **DIP (依賴反轉)**：
  - *實戰*：高層邏輯 (Use Case) 不應依賴低層細節 (DB, API)。
  - *技巧*：依賴注入 (Dependency Injection) 是實現 DIP 的標準手段。

### 2. Composition over Inheritance (組合優於繼承)
這是現代軟體開發最重要的原則之一。
- **繼承的陷阱**：繼承是強耦合。你想要「香蕉」，但繼承給你「拿著香蕉的大猩猩以及整座森林」。
- **組合的優勢**：透過將功能委派給其他物件 (Has-a 關係)，可以在 Runtime 動態改變行為，且更容易測試。
- **Best Practice**：除非是嚴格的 `Is-a` 關係且行為幾乎不變，否則優先使用 Interface + Composition。

### 3. DRY vs. WET (Don't Repeat Yourself vs. Write Everything Twice)
- **DRY 的誤區**：看到兩段程式碼長得像就急著抽取共用函式。
- **Coincidental Duplication (巧合性重複)**：如果兩段程式碼邏輯相同，但「業務意義」不同（例如：驗證使用者年齡 vs. 驗證商品庫存數量），**不要**合併它們。
- **WET**：有時候，稍微重複寫兩次 (Write Everything Twice) 比錯誤的抽象化更好維護。等到第三次重複且確定是相同邏輯時，再進行重構 (Rule of Three)。

### 4. Law of Demeter (迪米特法則 / 最少知識原則)
- **原則**：不要和「陌生人」說話。
- **Bad**：`order.getCustomer().getAddress().getZipCode()` (Train wreck code)。這導致你的程式碼依賴了整個物件圖結構。
- **Good**：`order.getShippingZipCode()`。讓 `Order` 物件負責委派，封裝內部結構。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Premature Optimization & Abstraction (過早最佳化與抽象化)
- **症狀**：在需求還不明確時，就設計了複雜的繼承體系或泛型介面，試圖涵蓋「未來可能」的所有情況。
- **後果**：未來需求變更時，這個過早建立的架構反而變成阻礙，因為它猜錯了變化的方向。
- **解法**：**YAGNI (You Aren't Gonna Need It)**。只為當前的需求設計，但保持程式碼整潔以便未來重構。

### 2. God Object (上帝物件)
- **症狀**：一個名為 `Utils`, `Manager`, 或 `Controller` 的類別，擁有數千行程式碼，包含幾十個不相關的方法。
- **後果**：極難測試、多人協作時充滿 Merge Conflicts、修改 A 功能導致 B 功能壞掉。
- **解法**：識別職責，將其拆解為 `Validator`, `Repository`, `Service`, `Formatter` 等專責物件。

### 3. Golden Hammer (黃金鐵鎚)
- **症狀**：學會了某個模式（例如 Singleton 或 Observer），就覺得全世界的問題都可以用它解決。
- **後果**：導致程式碼晦澀難懂，為簡單問題引入不必要的複雜度。
- **解法**：了解每個模式的 **Trade-offs (取捨)**。沒有銀彈。

### 4. Anemic Domain Model (貧血模型)
- **症狀**：物件只有 Getter/Setter，所有業務邏輯都散落在 Service 層。
- **後果**：物件變成了單純的資料結構，失去了封裝的意義，邏輯重複且難以維護。
- **解法**：將屬於該物件的邏輯（如狀態檢核、計算）放回物件本身 (Rich Domain Model)。

---

## Checklists & workflows｜檢查清單與流程

在進行設計評審 (Design Review) 或程式碼審查 (Code Review) 時，使用此清單檢視設計品質。

### Design Decision Checklist
- [ ] **可測試性 (Testability)**：
  - 我能輕鬆地為這個類別撰寫 Unit Test 嗎？
  - 是否需要 Mock 太多依賴？（依賴過多通常代表職責過重）
- [ ] **單一職責 (SRP)**：
  - 我能用一句簡單的話描述這個類別在做什麼嗎？（如果用了 "And" 或 "Or"，可能職責過多）
- [ ] **耦合方向 (Dependency Direction)**：
  - 依賴關係是否指向「更穩定」的方向？（易變的 UI 依賴穩定的 Domain，而不是反過來）
- [ ] **擴充性 (Extensibility)**：
  - 如果未來要新增一種類型（例如新的付款方式），我需要修改現有程式碼，還是只需新增一個 Class？(OCP)
- [ ] **必要性 (YAGNI)**：
  - 這個介面或抽象層是為了解決「現在」的問題，還是憑空想像的「未來」？

### Refactoring Workflow (When to apply patterns)
1. **Make it work**: 先寫出髒髒的程式碼，確保功能正確。
2. **Make it right**: 觀察程式碼，識別 Code Smells（重複、過長方法、Feature Envy）。
3. **Apply Pattern**: 選擇合適的設計模式來消除 Smell。
4. **Make it fast**: 最後才考慮效能最佳化。

---

## Real-world examples｜實戰案例

### Scenario: Payment Processing System (付款處理系統)

#### ❌ The Anti-Pattern Way (Violating OCP & SRP)
一個巨大的 `PaymentService` 處理所有邏輯。

```java
// Bad Design: Hard to maintain, violates Open/Closed Principle
public class PaymentService {
    public void process(String type, double amount) {
        if (type.equals("CreditCard")) {
            // 50 lines of credit card logic
            // Validate card, call bank API...
        } else if (type.equals("PayPal")) {
            // 50 lines of PayPal logic
            // Login, verify token...
        } else if (type.equals("Bitcoin")) {
            // ...
        }
        // Every time a new payment method is added, we modify this file.
        // Risk of breaking existing logic is high.
    }
}
```

#### ✅ The Pattern Way (Strategy Pattern + Factory)
使用 **Strategy Pattern** 實現 OCP，使用 **Factory** 封裝建立邏輯。

```java
// 1. Define the Interface (Contract)
public interface PaymentStrategy {
    void pay(double amount);
}

// 2. Implement Concrete Strategies (Separation of Concerns)
public class CreditCardPayment implements PaymentStrategy {
    public void pay(double amount) { /* Credit Card specific logic */ }
}

public class PayPalPayment implements PaymentStrategy {
    public void pay(double amount) { /* PayPal specific logic */ }
}

// 3. Context / Usage (Open for extension, Closed for modification)
public class PaymentProcessor {
    private final PaymentStrategy strategy;

    // Dependency Injection (DIP)
    public PaymentProcessor(PaymentStrategy strategy) {
        this.strategy = strategy;
    }

    public void process(double amount) {
        // Polymorphism: The processor doesn't care WHICH method is used.
        this.strategy.pay(amount);
    }
}
```

**Why this is better:**
1.  **Isolation**: `CreditCard` 的邏輯壞了不會影響 `PayPal`。
2.  **Testability**: 可以輕鬆 Mock `PaymentStrategy` 來測試 `PaymentProcessor`。
3.  **Extensibility**: 新增 `ApplePay` 只需要新增一個 Class，完全不用改動 `PaymentProcessor` 的程式碼。