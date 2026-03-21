# 反模式與過度設計陷阱 / Anti-Patterns and Pitfalls of Over-Engineering

## Mental model｜心智模型

在軟體設計的旅程中，最大的敵人往往不是「不懂模式」，而是「太愛模式」。要避免反模式（Anti-Patterns）與過度設計（Over-Engineering），你需要建立以下的心智模型：

### 1. 負債思維 (Code as Liability)
每一行程式碼、每一層抽象（Abstraction）、每一個引入的設計模式，本質上都是**負債**，而不是資產。它們增加了維護成本與認知負擔（Cognitive Load）。
- **原則**：只有當「不使用模式帶來的痛苦（如重複代碼、難以測試）」大於「引入模式的成本」時，才使用設計模式。
- **YAGNI (You Ain't Gonna Need It)**：不要為了「未來可能的需求」而現在就實作複雜的擴充性。

### 2. 演化式設計 (Evolutionary Design)
完美的架構不是一開始就畫出來的，而是重構出來的。
- **Rule of Three**：第一次寫死，第二次複製，第三次才重構出模式。
- **Pattern as a Target, not a Start**：設計模式是重構的**目標（Target）**，而不是起點。當你發現代碼有壞味道（Bad Smell）時，模式是用來消除味道的工具。

### 3. 複雜度守恆 (Conservation of Complexity)
業務邏輯的複雜度是不會消失的，它只能被轉移。
- **God Object**：試圖將所有複雜度塞進一個類別，導致內部混亂。
- **Poltergeists (過度拆分)**：試圖將複雜度分散到太多細碎的類別，導致類別間的交互變得極度複雜，讓人看不懂全貌。
- **平衡點**：優秀的設計是在「單一類別的內部複雜度」與「類別之間的交互複雜度」之間取得平衡。

---

## Patterns & best practices｜常見模式與最佳實務

在對抗反模式時，我們通常採用以下實務策略來保持代碼健康：

### 1. 漸進式重構 (Refactoring to Patterns)
不要一開始就套用 `AbstractFactory` 或 `Strategy`。
- **實作**：先寫出簡單、直觀的 `if-else` 或程序式代碼。
- **觸發點**：當條件判斷超過 3 層，或同類型的邏輯在多處重複時，再引入 `Strategy` 或 `Template Method`。

### 2. 關注點分離 (Separation of Concerns)
這是對抗 God Object 最有效的武器。
- **單一職責原則 (SRP)**：一個類別只能有一個改變的理由。
- **實作**：將 `UserManager` 拆解為 `UserRepository` (資料存取), `UserValidator` (驗證), `UserNotificationService` (通知)。

### 3. 組合優於繼承 (Composition over Inheritance)
這是對抗 Spaghetti Code 和脆弱基類（Fragile Base Class）的良方。
- **問題**：過深的繼承樹會導致子類別與父類別強耦合，修改父類別會導致不可預期的破壞。
- **實作**：使用介面（Interface）與依賴注入（Dependency Injection）來組合功能，而不是透過繼承來獲得功能。

### 4. 領域驅動設計 (DDD) 的戰術應用
避免「貧血模型 (Anemic Domain Model)」——即只有 Getter/Setter 的資料物件與充滿邏輯的 Service。
- **實作**：將業務邏輯（如狀態檢核、計算）放回 Entity 或 Value Object 中，讓物件擁有行為。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

以下是真實專案中最常見的陷阱，請務必警惕：

### 1. The God Object (上帝物件 / The Blob)
- **徵兆**：一個名為 `Manager`, `Controller`, `System` 的類別，擁有 3000+ 行代碼，包含 SQL 查詢、商業邏輯、日誌記錄和格式化輸出。
- **後果**：無人敢改，牽一髮動全身，測試極難撰寫。
- **解法**：使用 `Extract Class` 重構手法，按職責切分。

### 2. Spaghetti Code (義大利麵代碼)
- **徵兆**：程式流程充滿了 `GOTO` (在現代語言中表現為過多的巢狀 `if-else`、`switch`、以及混亂的 `try-catch` 跳轉)，難以追蹤執行順序。
- **後果**：無法理解業務流程，Debug 變成噩夢。
- **解法**：使用 `State Pattern` 或 `Strategy Pattern` 取代複雜的條件判斷；使用 `Guard Clauses` 減少巢狀層級。

### 3. Golden Hammer (黃金鐵鎚)
- **徵兆**：「手裡拿著錘子，看什麼都像釘子」。例如：熟悉 Singleton，於是將 Config、DB 連線、甚至 User Session 全部做成 Singleton。
- **後果**：全域狀態汙染，單元測試無法並行執行，隱藏的依賴關係。
- **解法**：強迫自己學習多種模式，並練習依賴注入 (DI)。

### 4. Poltergeists (搗蛋鬼 / 幽靈類別)
- **徵兆**：專案中存在大量「只有轉發功能」的類別，它們沒有狀態，也沒有真正的邏輯，只是呼叫另一個類別的方法。通常是過度分層或過度設計的產物。
- **後果**：檔案數量爆炸，導航代碼時需要跳轉十幾層才能找到真正的邏輯。
- **解法**：`Inline Class`，將無用的中間層移除。

### 5. Premature Optimization (過早最佳化)
- **徵兆**：在沒有效能數據支持下，為了「效率」而犧牲可讀性。例如使用 Object Pool 管理 3 個小物件，或手寫複雜的 Cache 機制。
- **後果**：代碼複雜度上升，但效能提升微乎其微，甚至引入 Bug。
- **解法**：Make it work, make it right, make it fast. 先寫出可讀的代碼，遇到瓶頸再優化。

---

## Checklists & workflows｜檢查清單與流程

在決定引入一個設計模式或架構決策前，請執行此檢查：

### Design Decision Checklist (設計決策檢核表)

- [ ] **痛點檢核**：我現在引入這個模式，是為了解決**當下已經存在**的痛點（重複、耦合、難測），還是為了解決「想像中」的未來問題？
- [ ] **複雜度檢核**：引入這個模式後，新進的 Junior Engineer 能在 5 分鐘內看懂這段代碼在做什麼嗎？
- [ ] **替代方案**：有沒有更簡單的方法？（例如：用一個 `Map` 取代 `Factory`，用一個 `Function` 取代 `Command`）。
- [ ] **命名檢核**：我的類別名稱是否具體？（避免使用 `Manager`, `Processor`, `Handler` 這種模糊字眼，除非你真的沒辦法）。
- [ ] **三法則檢核**：這個邏輯是否已經重複出現了三次？如果只有一次，請先 Hardcode。

### Decision Tree for Patterns

1. **Is the logic duplicated?**
   - No -> Keep it simple (KISS).
   - Yes -> Proceed.
2. **Is the duplication structure identical but behavior different?**
   - Yes -> Consider `Strategy` or `Template Method`.
   - No -> Just extract a common method/function.
3. **Does the object creation logic require complex assembly?**
   - Yes -> Consider `Builder` or `Factory`.
   - No -> Just use `new` or a simple constructor.
4. **Do you need to decouple the sender from the receiver?**
   - Yes -> Consider `Observer` or `Command`.
   - No -> Direct method call is fine.

---

## Real-world examples｜實戰案例

### Case 1: The "Hello World" Enterprise Edition (Over-Engineering)

**情境**：開發者需要寫一個功能，將字串轉為大寫。

**❌ Anti-Pattern (Over-Engineering):**
建立 `StringProcessorInterface`, `UpperCaseProcessorImpl`, `ProcessorFactory`, `ProcessorFactoryImpl`, `DependencyInjector`... 只為了呼叫 `.toUpperCase()`。

```java
// 這是過度設計的典型
public interface StringOperation {
    String execute(String input);
}

public class UpperCaseOperation implements StringOperation {
    public String execute(String input) { return input.toUpperCase(); }
}

public class OperationFactory {
    public static StringOperation getOperation(String type) {
        if ("upper".equals(type)) return new UpperCaseOperation();
        return null;
    }
}
// 使用時：
// String result = OperationFactory.getOperation("upper").execute("hello");
```

**✅ Best Practice (KISS):**
直接寫，直到你有「多種」字串處理策略且需要在執行期切換時，才考慮重構。

```java
// 直接使用，簡單明瞭
String result = "hello".toUpperCase();
```

### Case 2: The God Object (Refactoring)

**情境**：一個電商系統的 `OrderManager` 類別。

**❌ Anti-Pattern (God Object):**

```python
class OrderManager:
    def create_order(self, user, items):
        # 1. Validate User (50 lines)
        # 2. Check Inventory (DB connection code here)
        # 3. Calculate Price (Complex tax logic mixed in)
        # 4. Save to DB (Raw SQL strings)
        # 5. Send Email (SMTP code mixed in)
        # 6. Log to File (File I/O code mixed in)
        pass
```

**✅ Best Practice (Separation of Concerns):**
將職責委派給專業的物件，`OrderService` 只負責協調流程（Orchestration）。

```python
class OrderService:
    def __init__(self, validator, inventory, pricing, repo, notifier):
        self.validator = validator
        self.inventory = inventory
        self.pricing = pricing
        self.repo = repo
        self.notifier = notifier

    def create_order(self, user, items):
        self.validator.validate(user)            # 職責 1
        self.inventory.check(items)              # 職責 2
        total = self.pricing.calculate(items)    # 職責 3
        order = self.repo.save(user, items, total) # 職責 4
        self.notifier.send_confirmation(user)    # 職責 5
        return order
```

### Case 3: Golden Hammer (Singleton Abuse)

**情境**：為了方便存取，將 `DatabaseConnection` 設計成 Singleton。

**❌ Anti-Pattern:**
```csharp
public class DB {
    private static DB instance;
    // 全域共用一個連線，導致無法並行測試，且隱藏了依賴
    public static DB Instance { get { ... } } 
    public void Query(string sql) { ... }
}

// 在任何地方隨意呼叫，導致代碼緊密耦合
public void ProcessUser() {
    DB.Instance.Query("UPDATE users ...");
}
```

**✅ Best Practice (Dependency Injection):**
讓依賴顯性化（Explicit Dependencies），並由容器管理生命週期（即使它是單例的生命週期，也不要用 Singleton 模式實作）。

```csharp
public class UserService {
    private readonly IDatabase _db;

    // 透過建構子注入，測試時可以輕易換成 MockDatabase
    public UserService(IDatabase db) {
        _db = db;
    }

    public void ProcessUser() {
        _db.Query("UPDATE users ...");
    }
}
```