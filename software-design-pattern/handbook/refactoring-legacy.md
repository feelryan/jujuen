# 重構實戰：從遺留代碼到模式應用 / Refactoring to Patterns: Handling Legacy Code

## Mental model｜心智模型

在處理遺留代碼（Legacy Code）時，資深工程師與初階工程師最大的思維差異在於對「風險」與「目標」的控管。

### 1. 遺留代碼的定義 (The Definition)
Michael Feathers 在《Working Effectively with Legacy Code》中給出了一個經典定義：「沒有測試的代碼就是遺留代碼」。
> **Legacy Code is code without tests.**

這意味著，無論代碼寫得多漂亮，如果沒有自動化測試保護，重構就是一場賭博。你的心智模型不應是「清理髒亂」，而是「建立安全網」。

### 2. 外科手術隱喻 (The Surgery Metaphor)
將重構視為「外科手術」：
- **生命跡象監測 (Tests)**：在動刀前，必須先接上心電圖（Characterization Tests/特徵測試），確保病患活著且功能正常。
- **接縫 (Seams)**：你不能隨意切開身體，必須找到組織間的接縫。在代碼中，這意味著找到可以切斷依賴、插入測試替身（Test Doubles）的地方。
- **微創手術 (Micro-refactoring)**：不要試圖一次換掉整顆心臟。先做 Sprout（萌芽）或 Wrap（包裝），逐步替換壞死組織。

### 3. Refactoring to Patterns
不要為了使用模式而重構。設計模式是重構的「目的地」，而非起點。
- **起點**：Code Smells（如過長的 `if-else`、巨大的 Class）。
- **過程**：一系列微小的重構步驟（Extract Method -> Move Method）。
- **終點**：自然浮現的設計模式（如 Strategy Pattern 或 State Pattern）。

---

## Patterns & best practices｜常見模式與最佳實務

在真實專案中，我們很少有機會「暫停開發兩個月來重構」。以下是邊開發邊重構（Refactoring while shipping）的實戰模式：

### 1. 建立安全網：特徵測試 (Characterization Tests)
在修改任何邏輯前，先寫測試來鎖定「當前的行為」（包含 Bug）。
- **Golden Master Technique**：
  1. 捕捉舊系統對特定輸入的輸出（Log、DB 狀態、Return value）。
  2. 將其視為「標準答案」。
  3. 確保重構後的輸出與標準答案 byte-for-byte 一致。

### 2. 阻斷依賴與接縫 (Breaking Dependencies & Seams)
遺留代碼通常高度耦合（Tightly Coupled）。你需要創造「接縫」來插入測試。
- **Extract Interface**：將具體類別依賴轉為介面依賴。
- **Subclass and Override Method**：在測試中繼承 Legacy Class，並 Override 掉那些連線 DB 或發送 Email 的方法（這是處理無法 DI 的靜態語言代碼的常見手段）。

### 3. 增量式重構策略 (Incremental Strategies)
當你必須在爛代碼中加新功能時，使用以下策略避免讓情況更糟：

#### A. Sprout Method / Class (萌芽法)
不要在原本已經很亂的 `process()` 方法中再塞入 50 行代碼。
- **做法**：創建一個全新的 Method 或 Class 來處理新邏輯，然後在舊代碼中呼叫它。
- **優點**：新代碼可以被完整測試（TDD），且不干擾舊邏輯。

#### B. Wrap Method / Class (包裝法)
當你需要在舊邏輯前後加入行為（如 Logging, Validation）時。
- **做法**：將舊方法改名（如 `doPay()`），建立一個同名的新方法 `pay()`，在其中呼叫 `doPay()` 並加上新邏輯。這其實就是 **Decorator Pattern** 的雛形。

### 4. 常見的「重構到模式」路徑 (Common Refactoring Paths)

| Code Smell | Refactoring Steps | Target Pattern |
| :--- | :--- | :--- |
| **Conditional Complexity**<br>(大量的 `if-else` 或 `switch`) | 1. Extract Method<br>2. Move Method<br>3. Replace Conditional with Polymorphism | **Strategy** or **State** |
| **Data Clumps**<br>(總是綁在一起出現的參數) | 1. Introduce Parameter Object<br>2. Preserve Whole Object | **Value Object** |
| **God Class**<br>(萬能類別) | 1. Extract Class<br>2. Move Method / Field | **Facade** or **Mediator** (to coordinate components) |
| **Null Checks**<br>(到處都是 `if (obj != null)`) | 1. Introduce Null Object | **Null Object Pattern** |

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The Big Rewrite (打掉重練)
- **現象**：工程師宣稱「這代碼沒救了，重寫比較快」。
- **後果**：重寫通常會丟失隱藏在舊代碼中的業務知識（Corner cases），且耗時通常是預估的 3 倍以上。最終產生一個「新的遺留系統」。
- **解法**：**Strangler Fig Pattern (絞殺榕模式)**。在舊系統旁建立新系統，逐步攔截流量與功能，直到舊系統枯萎。

### 2. Shotgun Surgery (霰彈槍式修改)
- **現象**：為了一個小改動，需要在 10 個不同的 class 中做修改。
- **後果**：極易漏改，導致系統不一致。
- **解法**：這通常意味著內聚力（Cohesion）過低。應先使用 **Move Method** 將相關邏輯集中到一個地方，再進行修改。

### 3. Premature Pattern Application (過早套用模式)
- **現象**：看到一個 `if` 就想用 Strategy Pattern，結果產生了 10 個只有一行代碼的 Class。
- **後果**：增加了系統的複雜度（Cognitive Load），卻沒有帶來足夠的靈活性。
- **原則**：**Rule of Three**。當類似的邏輯重複出現三次時，才考慮重構為模式。

### 4. Refactoring Tunnel Vision (重構隧道效應)
- **現象**：開始重構後停不下來，忘記了原本的業務目標，導致分支長達數週無法合併。
- **解法**：設定 Timebox（例如 1 小時），並嚴格遵守 **Campground Rule**（童子軍原則）：只清理你這次任務路徑上的代碼，不要試圖清理整座森林。

---

## Checklists & workflows｜檢查清單與流程

### Decision Workflow: Handling Legacy Code
當你需要修改一段遺留代碼時，請遵循此流程：

1.  **評估 (Assess)**：這段代碼有測試嗎？
    -   Yes → 直接進行 TDD / 重構。
    -   No → 進入步驟 2。
2.  **保護 (Cover)**：能否寫一個「特徵測試」來鎖定當前行為？
    -   Yes → 寫測試，然後重構。
    -   No (依賴太重) → 進入步驟 3。
3.  **解耦 (Break Dependencies)**：
    -   尋找接縫 (Seams)。
    -   提取介面 (Extract Interface) 或使用 Subclassing 覆寫依賴。
    -   **注意**：此步驟應盡量少改動邏輯，只改結構。
4.  **添加/修改 (Change)**：
    -   使用 **Sprout** 或 **Wrap** 技術添加新功能。
    -   或者，在測試保護下重構舊邏輯（Refactor to Pattern）。
5.  **驗證 (Verify)**：確保特徵測試通過，且新測試覆蓋了新邏輯。

### Refactoring Checklist

- [ ] **Safety First**: 我是否有自動化測試覆蓋了我即將修改的區域？
- [ ] **Baby Steps**: 我是否在每次微小的重構後都執行了測試？
- [ ] **No Behavior Change**: 在重構階段（Refactoring Phase），我是否確保沒有改變外部行為？（重構與添加功能應分開 commit）。
- [ ] **Commit Often**: 我是否每完成一個小的 Extract Method 或 Rename 就 commit 一次？（方便 revert）。
- [ ] **Pattern Justification**: 我引入這個設計模式是為了解決具體的複雜度問題，而不僅僅是為了「好看」？

---

## Real-world examples｜實戰案例

### Scenario: The "God" Order Service
你接手了一個電商系統，其中 `OrderService.java` 有 5000 行，其中 `calculateTotal(Order order)` 方法長達 300 行，充斥著各種會員等級、促銷活動的 `if-else`。

#### Before: Spaghetti Code
```java
public class OrderService {
    public double calculateTotal(Order order) {
        double total = 0;
        // ... 50 lines of base calculation ...
        
        if (order.getUser().getType() == "VIP") {
            // ... 20 lines of VIP logic ...
        } else if (order.getUser().getType() == "PLATINUM") {
             // ... 30 lines of Platinum logic ...
        }
        
        if (order.getDate().isHoliday()) {
            // ... holiday logic ...
        }
        // ... more chaos ...
        return total;
    }
}
```

#### Step 1: Create Safety Net
編寫 `OrderServiceTest`，使用一組固定的訂單數據（Golden Master），確保 `calculateTotal` 的輸出在重構前後完全一致。

#### Step 2: Extract Methods (Decomposition)
將巨大的方法拆解為具名的小方法。
```java
public double calculateTotal(Order order) {
    double base = calculateBasePrice(order);
    double discount = calculateUserDiscount(order); // Extracted
    double holidayPromo = calculateHolidayPromo(order); // Extracted
    return base - discount - holidayPromo;
}
```

#### Step 3: Move Method to Strategy (Refactoring to Pattern)
發現 `calculateUserDiscount` 依賴於 User Type，且變化頻繁。決定引入 **Strategy Pattern**。

1.  定義介面 `DiscountStrategy`。
2.  建立 `VipDiscountStrategy`, `PlatinumDiscountStrategy`。
3.  將邏輯搬移（Move Method）到這些類別中。

#### After: Clean & Extensible
```java
// Context
public class OrderService {
    private final DiscountFactory discountFactory; // Dependency Injection

    public double calculateTotal(Order order) {
        double base = calculateBasePrice(order);
        
        // Polymorphism replaces conditionals
        DiscountStrategy strategy = discountFactory.getStrategy(order.getUser());
        double discount = strategy.calculate(order);
        
        return base - discount;
    }
}

// Strategy Interface
public interface DiscountStrategy {
    double calculate(Order order);
}
```

**Result**:
- **可測試性**：每個 Strategy 可以單獨測試，不需要啟動整個 OrderService。
- **可維護性**：新增會員等級只需新增一個 Class，不需修改 `OrderService` (Open/Closed Principle)。
- **安全性**：透過特徵測試保證了重構過程沒有破壞既有商業邏輯。