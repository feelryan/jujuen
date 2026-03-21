# 架構模式與分層設計 / Architectural Patterns and Layered Design

## Mental model｜心智模型

### 1. The "Onion" not the "Stack" (洋蔥模型而非單純堆疊)
傳統的分層常被想像成垂直堆疊（UI -> Service -> DB），但在現代架構思維中，請將系統想像成一顆**洋蔥**或**同心圓**。
- **核心 (Core)**：業務邏輯與領域模型（Domain Model）。這是系統最有價值的部分，它不應該知道外界的存在。
- **邊界 (Boundary)**：定義核心如何與外界溝通的介面（Interfaces/Ports）。
- **外層 (Infrastructure)**：資料庫、UI、第三方 API。這些只是「插件」。

**Key Rule (Dependency Rule)**: Source code dependencies must point only **inward**.
**關鍵法則（依賴法則）**：所有的源碼依賴方向必須**向內**指。外層（DB、Web）依賴內層（Use Cases），內層絕不依賴外層。

### 2. Plug-and-Play Console (遊戲主機隱喻)
將你的應用程式核心視為一台**遊戲主機**。
- **Ports (連接埠)**：主機上的插槽（HDMI, USB）。
- **Adapters (轉接器)**：手把、電視螢幕、硬碟。
- **Insight**：主機（核心邏輯）不在乎你接的是 Sony 電視還是 Samsung 電視（MySQL 還是 PostgreSQL），只要符合 HDMI 規格（Port Interface）即可運作。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Hexagonal Architecture (Ports and Adapters)
最適合業務邏輯複雜、需要長期維護的系統。
- **Ports (Inbound/Driving)**：定義外界如何使用系統（例如 `IOrderService`）。
- **Ports (Outbound/Driven)**：定義系統如何使用外界資源（例如 `IOrderRepository`, `IPaymentGateway`）。
- **Adapters**：實作上述介面。例如 `OrderController` 呼叫 Inbound Port；`SqlOrderRepository` 實作 Outbound Port。

### 2. Clean Architecture (The Implementation Strategy)
這是 Hexagonal 的具體落地策略，通常分為四層：
1.  **Entities**: 企業級業務規則（最純淨的邏輯）。
2.  **Use Cases**: 應用程式特定業務規則（負責指揮 Entities）。
3.  **Interface Adapters**: Controllers, Gateways, Presenters（負責轉換資料格式）。
4.  **Frameworks & Drivers**: DB, Web Framework, Devices（最外層細節）。

### 3. Vertical Slicing (垂直切分)
與其強制將整個專案分為 Controller/Service/Dao 資料夾，不如按**功能（Feature）**切分。
- **Structure**: `Features/PlaceOrder/`, `Features/CancelOrder/`.
- **Benefit**: 相關的 UI、邏輯、資料存取代碼聚在一起。修改一個功能時，不需要在多個層級資料夾間跳轉。適合 CQRS 架構。

### 4. DTO Pattern (Data Transfer Object)
**Strictly separate Domain Models from API Models.**
嚴格區分領域模型與 API 模型。
- **Input DTO**: 接收前端 JSON，進行基本格式驗證。
- **Domain Entity**: 核心邏輯運算，確保業務狀態一致性。
- **Output DTO / ViewModel**: 將 Entity 轉換為前端需要的格式（隱藏敏感欄位）。
- **Why?** 避免資料庫結構變更直接破壞 API 合約，也避免 API 需求污染領域邏輯。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The Anemic Domain Model (貧血模型)
**Symptom**: Entities 只有 getters/setters，所有的邏輯都寫在 Service 層（Transaction Script）。
**Consequence**: 業務邏輯分散、重複，Service 變成數千行的 "God Class"。
**Fix**: 將邏輯推回 Entity。例如 `order.calculateTotal()` 應該在 Order 物件內，而不是 `OrderService` 裡。

### 2. Leaky Abstractions (抽象洩漏)
**Symptom**: 在 Service 層或 Domain 層出現 `HttpServletRequest` (Web 依賴) 或 `SQLException` (DB 依賴)。
**Consequence**: 核心邏輯被綁死在特定的框架或資料庫上，無法單元測試。
**Fix**: 定義自定義 Exception，並在 Adapter 層做轉換；Controller 僅傳遞參數或 DTO 進 Service。

### 3. The "Fat Controller" (肥胖控制器)
**Symptom**: Controller 負責驗證參數、呼叫 DB、計算邏輯、回傳 View。
**Consequence**: 難以測試，邏輯無法重用。
**Fix**: Controller 應該只是個「交通警察」，只負責轉發請求給 Use Case/Service，並回傳結果。

### 4. Over-Engineering for CRUD (殺雞用牛刀)
**Symptom**: 一個簡單的「讀取使用者列表」功能，卻硬要套用完整的 Clean Architecture (Entity -> UseCase -> Gateway -> Presenter)。
**Consequence**: 開發效率極低，代碼量暴增。
**Fix**: 對於單純的 CRUD，允許 Controller 直接呼叫簡單的 Query Service 或 Repository（Relaxed Layering）。架構應該依據複雜度調整。

---

## Checklists & workflows｜檢查清單與流程

### Design Decision Checklist (架構決策檢核)
- [ ] **Complexity Check**: 這是一個簡單的 CRUD 應用，還是有複雜的狀態機與業務規則？(簡單 -> Layered; 複雜 -> Hexagonal/Clean)
- [ ] **Dependency Direction**: 檢查 `import` 語句。核心層（Domain/Use Case）是否有 `import` 外層（Web/DB）的套件？(如果有，必須重構)
- [ ] **Interface Ownership**: 介面（Interface）是否定義在「使用方（Consumer）」所在的層級？(例如 Repository Interface 應定義在 Domain 層，而非 Infrastructure 層)
- [ ] **Testing Strategy**: 我是否能在沒有 DB 或 Web Server 的情況下，單元測試我的核心業務邏輯？

### Layering Implementation Workflow (實作流程)
1.  **Define Domain**: 先寫 Entity 與 Value Objects。不考慮 DB Schema。
2.  **Define Use Cases**: 定義 Input/Output Port (Interfaces)。描述「系統能做什麼」。
3.  **Implement Logic**: 撰寫 Use Case 實作，操作 Entity。這時候寫 Unit Test。
4.  **Add Adapters (Outbound)**: 實作 Repository 介面（連接真實 DB 或 Mock）。
5.  **Add Adapters (Inbound)**: 實作 API Controller 或 CLI，呼叫 Use Case。
6.  **Wire up**: 使用 Dependency Injection (DI) 將實作注入介面。

---

## Real-world examples｜實戰案例

### Scenario: E-commerce "Checkout" (電商結帳)

#### ❌ The "Spaghetti" Way (Bad Layering)
*Controller 直接依賴具體實作，邏輯混雜。*

```java
// OrderController.java
public Response checkout(Request req) {
    // 1. Validation logic mixed in Controller
    if (req.getPrice() < 0) return Error(...);
    
    // 2. Direct DB dependency (SQL details leaking)
    String sql = "INSERT INTO orders ..."; 
    db.execute(sql);
    
    // 3. Third-party API dependency hardcoded
    StripeApi.charge(req.getCardToken()); 
    
    return Success;
}
```

#### ✅ The "Clean" Way (Ports & Adapters)
*依賴反轉，核心邏輯純淨。*

**1. Domain Layer (Core)**
```java
// Order.java (Rich Model)
public class Order {
    public void finalize() {
        if (this.items.isEmpty()) throw new DomainException("Empty order");
        this.status = Status.CONFIRMED;
    }
}

// IOrderRepository.java (Outbound Port)
public interface IOrderRepository {
    void save(Order order);
}

// IPaymentGateway.java (Outbound Port)
public interface IPaymentGateway {
    void charge(Money amount);
}
```

**2. Application Layer (Use Case)**
```java
// CheckoutUseCase.java
public class CheckoutUseCase {
    private final IOrderRepository repo;
    private final IPaymentGateway payment;

    // Constructor Injection
    public CheckoutUseCase(IOrderRepository repo, IPaymentGateway payment) {
        this.repo = repo;
        this.payment = payment;
    }

    public void execute(CheckoutCommand cmd) {
        Order order = repo.findById(cmd.orderId);
        order.finalize(); // Domain logic
        payment.charge(order.getTotal());
        repo.save(order);
    }
}
```

**3. Infrastructure Layer (Adapters)**
```java
// SqlOrderRepository.java (Implements Port)
public class SqlOrderRepository implements IOrderRepository {
    public void save(Order order) {
        // Hibernate or SQL implementation
    }
}

// OrderController.java (Inbound Adapter)
public class OrderController {
    private final CheckoutUseCase useCase; // Depends on abstraction
    
    @PostMapping("/checkout")
    public Response checkout(@RequestBody CheckoutDto dto) {
        useCase.execute(dto.toCommand());
        return Response.ok();
    }
}
```

### Key Takeaway
在這個架構下，如果你想把資料庫從 MySQL 換成 MongoDB，或者把支付從 Stripe 換成 PayPal，你只需要修改 **Infrastructure Layer** 的 Adapter，完全不需要觸碰 **Domain** 或 **Application** 層的代碼。這就是分層設計的終極目標：**Decoupling (解耦)**。