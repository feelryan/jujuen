# 設計決策檢核表與 Troubleshooting / Design Decision Checklist and Troubleshooting

## Mental model｜心智模型

在掌握了各種設計模式後，工程師面臨的最大挑戰往往不是「如何實作」，而是「何時使用」以及「何時**不**使用」。

### 1. 複雜度預算 (Complexity Budget)
將設計模式視為一種「昂貴的資產」。每一個引入的模式都會增加系統的**認知負載 (Cognitive Load)** 和**間接層 (Indirection)**。
- **Default State:** 最簡單、直觀的程式碼（KISS 原則）。
- **Spending the Budget:** 只有當「重複性問題」或「變更的痛苦」超過了引入模式的成本時，才花費預算去使用設計模式。

### 2. 處方籤思維 (Prescription Mindset)
不要拿著錘子找釘子。設計模式是醫生開的「處方籤」，而不是維他命。
- **先診斷 (Diagnosis):** 這裡的痛點是什麼？是物件建立太複雜？是演算法頻繁變更？還是介面不相容？
- **後開藥 (Prescription):** 針對痛點選擇特定的模式。如果沒有病徵，就不要開藥。

### 3. 演進式設計 (Evolutionary Design)
完美的架構不是一開始就畫出來的，而是重構出來的。
- **Rule of Three:** 第一次只管寫出來；第二次不得不重複時，忍受它；第三次重複時，再重構並套用模式。

---

## Patterns & best practices｜常見模式與最佳實務

在決策過程中，資深工程師通常遵循以下最佳實務來評估方案：

### 1. 隔離變動點 (Isolate the Variation)
這是所有設計模式的元模式 (Meta-pattern)。
- **做法：** 找出系統中「最容易改變」的部分，並將其與「穩定」的部分隔離開來。
- **應用：** 如果變動的是「演算法」，考慮 **Strategy**；如果變動的是「物件結構」，考慮 **Visitor**；如果變動的是「狀態轉換」，考慮 **State**。

### 2. 優先使用組合而非繼承 (Favor Composition over Inheritance)
- **決策點：** 當你想要擴充一個類別的功能時。
- **Best Practice：** 除非是嚴格的 `is-a` 關係且父類別設計為可繼承，否則優先使用 **Decorator** 或 **Strategy** (組合) 來取代繼承。這能避免類別爆炸 (Class Explosion) 和脆弱的基礎類別問題。

### 3. 依賴反轉決策 (Dependency Inversion Decision)
- **情境：** 高層模組（如業務邏輯）直接依賴低層模組（如資料庫驅動）。
- **Best Practice：** 引入介面（Interface）。讓高層與低層都依賴於抽象。這是 **Factory**、**Strategy**、**Observer** 等模式能運作的基礎。

### 4. 建立邊界 (Boundary Setting)
- **情境：** 整合第三方 Library 或 Legacy Code。
- **Best Practice：** 永遠不要讓第三方物件滲透到你的核心領域。使用 **Adapter** 或 **Facade** 來建立防腐層 (Anti-Corruption Layer)。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 模式強迫症 (Patternitis / Pattern Obsession)
- **徵兆：** 為了一個簡單的 "Hello World" 或 CRUD 功能，建立了 Factory, Strategy, AbstractFactory 和 Singleton。
- **後果：** 產生了大量的「意外複雜度 (Accidental Complexity)」，讓新進成員難以理解程式碼流向。
- **解法：** YAGNI (You Ain't Gonna Need It)。如果現在只有一種付款方式，不要寫 Strategy Pattern，寫一個 `if` 就好。

### 2. 黃金錘 (Golden Hammer)
- **徵兆：** 手上只有一把錘子，看什麼都是釘子。例如：不管什麼情況都用 **Singleton**（導致全域狀態混亂），或不管什麼邏輯都用 **Strategy**。
- **後果：** 系統變得僵化或難以測試。

### 3. 過早抽象化 (Premature Abstraction)
- **徵兆：** 在還沒看到第二個具體案例前，就先定義了 Generic Interface。
- **後果：** 往往預測錯誤，導致介面充滿了只對某一個實作有意義的 `null` 參數或空方法（違反 LSP）。

### 4. 上帝介面 (God Interface / Interface Bloat)
- **徵兆：** 一個介面擁有幾十個方法。
- **後果：** 實作者被迫實作不需要的方法。
- **解法：** 應用介面隔離原則 (ISP)，將大介面拆分為多個小的、專注的介面。

---

## Checklists & workflows｜檢查清單與流程

在決定引入設計模式，或進行 Code Review 時，請使用此檢核表。

### Decision Tree: Which Pattern? (簡易決策樹)

1. **物件建立問題 (Creation)**
   - 建立過程很複雜？ → `Builder`
   - 需要隱藏具體類別？ → `Factory Method`
   - 需要保證全域唯一？ → `Singleton` (小心使用)

2. **物件結構問題 (Structure)**
   - 介面不相容？ → `Adapter`
   - 需要動態增加職責？ → `Decorator`
   - 需要簡化複雜子系統？ → `Facade`
   - 物件與實作需要分離？ → `Bridge`

3. **物件行為問題 (Behavior)**
   - 演算法需要切換？ → `Strategy`
   - 狀態改變影響行為？ → `State`
   - 一對多通知？ → `Observer`
   - 步驟固定，細節不同？ → `Template Method`
   - 需要解耦請求發送者與執行者？ → `Command`

### Design Review Checklist (設計審查清單)

- [ ] **必要性驗證：** 這個模式解決了當前存在的具體問題嗎？還是為了解決「未來可能發生」的問題？
- [ ] **複雜度權衡：** 引入這個模式增加的類別數量與理解成本，是否小於它帶來的解耦效益？
- [ ] **命名規範：** 類別名稱是否反映了模式意圖？(e.g., `UserFactory`, `PaymentStrategy`, `OrderEventListener`)
- [ ] **可測試性：** 套用模式後，單元測試是否變得更容易撰寫（更容易 Mock/Stub）？
- [ ] **團隊認知：** 團隊成員是否都理解這個模式？如果這是一個冷門模式，是否有足夠的文件說明？
- [ ] **重構路徑：** 如果未來需求變更，移除這個模式的成本高嗎？

---

## Real-world examples｜實戰案例

### Scenario 1: The "If-Else" Hell (支付閘道重構)

**情境：**
一個電商系統的 `PaymentService` 中充滿了大量的 `if-else` 判斷。
```java
// Bad Smell
public void processPayment(String type) {
    if (type.equals("CREDIT_CARD")) { ... }
    else if (type.equals("PAYPAL")) { ... }
    else if (type.equals("APPLE_PAY")) { ... }
    // 每次新增支付方式都要修改這裡，違反 OCP
}
```

**決策流程：**
1. **診斷：** 違反 Open-Closed Principle，且 `processPayment` 方法過長。
2. **選擇模式：** 行為隨 `type` 變化 → **Strategy Pattern**。物件建立邏輯需要封裝 → **Factory Pattern**。
3. **實作：**
   - 定義 `PaymentStrategy` 介面。
   - 實作 `CreditCardStrategy`, `PaypalStrategy`。
   - 使用 `PaymentStrategyFactory` 根據 type 回傳對應策略。
   - `PaymentService` 只需要呼叫 `strategy.pay()`。

### Scenario 2: The "God Object" Logger (過度設計修正)

**情境：**
一個簡單的內部工具，開發者為了展現架構能力，設計了 `ILogger`, `AbstractLogger`, `ConsoleLogger`, `FileLogger`, `LoggerFactory`, `LoggerSingleton`。但實際上系統只需要印出到 Console。

**Troubleshooting：**
1. **診斷：** 過度設計 (Over-engineering)。增加了不必要的檔案跳轉，且沒有實際的擴充需求。
2. **修正 (Refactoring)：**
   - 移除 Factory 和 Abstract 層。
   - 直接使用一個簡單的 `Logger` 類別或直接呼叫 logging library。
   - **Lesson:** 在需求不明確或極其簡單時，KISS (Keep It Simple, Stupid) 優於任何模式。

### Scenario 3: Legacy System Integration (遺留系統整合)

**情境：**
新系統需要呼叫一個 10 年前的 SOAP 服務來取得匯率，該服務的介面極其複雜且參數命名混亂。

**決策流程：**
1. **診斷：** 直接在業務邏輯中呼叫 SOAP 服務會汙染程式碼，且難以測試。
2. **選擇模式：** 需要轉換介面並隔離髒代碼 → **Adapter Pattern** 或 **Facade Pattern**。
3. **實作：**
   - 建立 `ExchangeRateProvider` (Target Interface) 定義新系統需要的乾淨介面。
   - 建立 `SoapExchangeRateAdapter` 實作上述介面，內部封裝 SOAP 呼叫的醜陋細節。
   - 業務邏輯只依賴 `ExchangeRateProvider`。