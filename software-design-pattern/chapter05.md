# Chapter 05: Architectural Patterns and Layered Design
# 第五章：架構模式與分層設計

## 1. 前言與學習目標 (Introduction and Learning Objectives)

對於資深工程師而言，架構模式不僅僅是將程式碼放入不同的資料夾，而是關於「依賴關係的管理」與「業務邏輯的保護」。本章將超越傳統的 MVC，深入探討 Hexagonal Architecture (Ports and Adapters) 與 Clean Architecture。這些模式的核心目標是一致的：將核心業務邏輯與外部框架、資料庫及 UI 隔離。

For senior engineers, architectural patterns are not just about organizing code into different folders; they are about "dependency management" and "protection of business logic." This chapter moves beyond traditional MVC to explore Hexagonal Architecture (Ports and Adapters) and Clean Architecture. The core goal of these patterns is identical: to isolate core business logic from external frameworks, databases, and UIs.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **區分並應用不同的分層策略**：理解 Layered Architecture、Hexagonal Architecture 與 Clean Architecture 的演進脈絡與適用場景。
    **Distinguish and apply different layering strategies**: Understand the evolution and use cases of Layered Architecture, Hexagonal Architecture, and Clean Architecture.
2.  **實作依賴反轉 (DIP) 於架構層級**：學會如何透過 Interface 與 Adapter 讓業務邏輯不依賴於資料庫或 Web 框架，而是讓基礎設施依賴於業務規則。
    **Implement Dependency Inversion (DIP) at the architectural level**: Learn how to use Interfaces and Adapters so that business logic does not depend on the database or Web framework, but rather infrastructure depends on business rules.
3.  **評估工程權衡 (Trade-offs)**：在 System Design 面試或實務中，能夠解釋為何引入這些模式會增加初期開發成本 (Boilerplate)，但能換取長期的可測試性 (Testability) 與可維護性 (Maintainability)。
    **Evaluate engineering trade-offs**: In System Design interviews or practice, explain why introducing these patterns adds initial development cost (boilerplate) but trades for long-term testability and maintainability.

---

## 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 從 MVC 到以領域為中心 (From MVC to Domain-Centric)

傳統的 MVC (Model-View-Controller) 或 N-Tier 架構通常是「資料庫驅動 (Database-Driven)」的。在這種架構下，業務邏輯層往往依賴於資料存取層 (DAL)，導致資料庫 Schema 的變更會波及整個系統。

Traditional MVC (Model-View-Controller) or N-Tier architectures are often "Database-Driven." In such architectures, the Business Logic Layer often depends on the Data Access Layer (DAL), causing changes in the Database Schema to ripple through the entire system.

**心智模型轉變**：
想像系統是一個「洋蔥」或「六邊形」。
*   **核心 (Core)**：純粹的業務邏輯與實體 (Entities)。這裡不應該知道 SQL、HTTP 或 JSON 的存在。
*   **邊界 (Boundaries)**：透過 Interface 定義的合約 (Ports)。
*   **外層 (Outer Layers)**：實作細節，如 DB Adapter、Rest Controller、UI。

**Mental Model Shift**:
Imagine the system as an "Onion" or a "Hexagon."
*   **Core**: Pure business logic and Entities. It should not know that SQL, HTTP, or JSON exist.
*   **Boundaries**: Contracts defined via Interfaces (Ports).
*   **Outer Layers**: Implementation details, such as DB Adapters, Rest Controllers, UI.

### 2.2 依賴規則 (The Dependency Rule)

這是 Clean Architecture 最重要的規則：**原始碼的依賴關係只能指向內部 (Source code dependencies must point only inward)**。

This is the most important rule of Clean Architecture: **Source code dependencies must point only inward**.

*   **錯誤 (Wrong)**: `BusinessLogic` imports `SQLDatabaseRepository`
*   **正確 (Right)**: `SQLDatabaseRepository` implements `RepositoryInterface` (defined in Business Layer).

### 2.3 Ports and Adapters (Hexagonal Architecture)

*   **Port (埠)**：由核心層定義的介面 (Interface)。例如 `OrderRepository` 或 `PaymentService`。
*   **Adapter (轉接器)**：連接外部世界的實作。
    *   **Driving Adapter (Primary)**：觸發應用程式執行的人或系統 (例如 Controller, CLI)。
    *   **Driven Adapter (Secondary)**：應用程式呼叫的外部系統 (例如 Database, External API)。

*   **Port**: An interface defined by the core layer. E.g., `OrderRepository` or `PaymentService`.
*   **Adapter**: Implementation that connects to the outside world.
    *   **Driving Adapter (Primary)**: Actors or systems that trigger the application (e.g., Controller, CLI).
    *   **Driven Adapter (Secondary)**: External systems called by the application (e.g., Database, External API).

---

## 3. 實務場景與系統設計視角 (Real-World & System Design View)

### 3.1 微服務內部的架構 (Architecture Inside Microservices)

在大型分散式系統中，每個微服務 (Microservice) 內部如何組織程式碼至關重要。雖然微服務架構解決了服務間的解耦，但若服務內部是「義大利麵條式程式碼 (Spaghetti Code)」，該服務仍難以維護。

In large distributed systems, how code is organized *inside* each microservice is crucial. While microservices architecture solves inter-service decoupling, if the service internals are "Spaghetti Code," the service remains hard to maintain.

*   **應用場景**：核心業務複雜的服務 (如訂單處理、計費引擎)。
*   **不適用場景**：簡單的 CRUD 服務或 Proxy 服務 (過度設計)。

*   **Use Case**: Services with complex core business logic (e.g., Order Processing, Billing Engine).
*   **Non-Use Case**: Simple CRUD services or Proxy services (Over-engineering).

### 3.2 可測試性與更換基礎設施 (Testability and Swappable Infrastructure)

**System Design 視角**：
當面試官問：「如果我們要將資料庫從 MySQL 遷移到 MongoDB，或者將 REST API 改為 gRPC，你的架構如何支援？」

**System Design View**:
When an interviewer asks: "If we need to migrate the database from MySQL to MongoDB, or change the REST API to gRPC, how does your architecture support this?"

*   **Clean Architecture 的回答**：
    由於 Use Case (業務邏輯) 只依賴於 Port (Interface)，我們只需撰寫新的 Adapter (例如 `MongoOrderAdapter` 或 `GrpcOrderController`) 並在啟動時注入即可。核心邏輯完全不需要修改。這也意味著我們可以在單元測試中輕鬆 Mock 資料庫。

*   **Clean Architecture Answer**:
    Since the Use Case (business logic) only depends on the Port (Interface), we simply write a new Adapter (e.g., `MongoOrderAdapter` or `GrpcOrderController`) and inject it at startup. The core logic remains untouched. This also means we can easily mock the database in unit tests.

---

## 4. 逐步示例 (Walkthrough / Example)

### 案例背景 (Scenario)

我們需要設計一個「電子商務結帳系統 (E-commerce Checkout System)」。
業務規則：
1. 檢查庫存。
2. 如果庫存充足，扣除庫存並建立訂單。
3. 訂單建立後，發送確認 Email。

We need to design an "E-commerce Checkout System."
Business Rules:
1. Check inventory.
2. If inventory is sufficient, deduct inventory and create an order.
3. After the order is created, send a confirmation email.

### 階段一：Naive Layered Architecture (常見但有缺陷)

這是典型的 Controller -> Service -> Repository 依賴鏈。

This is the typical Controller -> Service -> Repository dependency chain.

```typescript
// ❌ Bad: Service depends directly on Infrastructure details

// Infrastructure Layer (Data Models mixed with Logic)
class InventoryModel { ... } // ORM Model

// Service Layer
class CheckoutService {
    private repo: SqlInventoryRepository; // Direct dependency on SQL implementation

    constructor() {
        this.repo = new SqlInventoryRepository();
    }

    async checkout(productId: string, quantity: number) {
        // Business logic mixed with DB logic
        const item = await this.repo.findById(productId);
        if (item.count < quantity) throw new Error("Out of stock");
        
        item.count -= quantity;
        await this.repo.save(item);
        // ... sending email logic hardcoded here
    }
}
```

**問題 (Issues)**：
*   無法在沒有資料庫的情況下測試 `checkout` 邏輯。
*   如果更換 ORM 或 Email Provider，必須修改 `CheckoutService`。

**Issues**:
*   Cannot test `checkout` logic without a database.
*   If changing ORM or Email Provider, `CheckoutService` must be modified.

### 階段二：Clean / Hexagonal Architecture (成熟解法)

我們將依賴反轉，並定義明確的 Ports。

We will invert the dependencies and define explicit Ports.

#### 1. Domain Layer (Core) - No external dependencies

```typescript
// Domain Entity (Pure Object)
export class Product {
    constructor(public id: string, public stock: number) {}

    hasStock(quantity: number): boolean {
        return this.stock >= quantity;
    }

    decreaseStock(quantity: number): void {
        if (!this.hasStock(quantity)) throw new Error("Domain Error: Out of stock");
        this.stock -= quantity;
    }
}

// Port (Output Port / Driven Port)
export interface InventoryRepository {
    findById(id: string): Promise<Product | null>;
    save(product: Product): Promise<void>;
}

export interface NotificationService {
    sendOrderConfirmation(orderId: string): Promise<void>;
}
```

#### 2. Application Layer (Use Cases) - Orchestrates the flow

```typescript
// Use Case (Input Port Implementation)
export class CheckoutUseCase {
    constructor(
        private inventoryRepo: InventoryRepository, // Dependency Injection
        private notifier: NotificationService
    ) {}

    async execute(productId: string, quantity: number): Promise<void> {
        const product = await this.inventoryRepo.findById(productId);
        if (!product) throw new Error("Product not found");

        // Pure Domain Logic
        product.decreaseStock(quantity);

        // Persist state
        await this.inventoryRepo.save(product);

        // Notify
        await this.notifier.sendOrderConfirmation("new-order-id");
    }
}
```

#### 3. Infrastructure Layer (Adapters) - The dirty details

```typescript
// Adapter for InventoryRepository (SQL Implementation)
class SqlInventoryAdapter implements InventoryRepository {
    async findById(id: string): Promise<Product | null> {
        // Convert SQL Row -> Domain Entity
        const row = await db.query("SELECT * FROM products WHERE id = ?", [id]);
        return new Product(row.id, row.stock);
    }
    
    async save(product: Product): Promise<void> {
        // Convert Domain Entity -> SQL Row
        await db.query("UPDATE products SET stock = ? WHERE id = ?", [product.stock, product.id]);
    }
}

// Wiring (Main / Dependency Injection Container)
const repo = new SqlInventoryAdapter();
const notifier = new EmailNotificationAdapter();
const useCase = new CheckoutUseCase(repo, notifier); // Injected!

// Driving Adapter (Controller)
router.post('/checkout', async (req, res) => {
    await useCase.execute(req.body.productId, req.body.quantity);
    res.status(200).send("OK");
});
```

**分析 (Analysis)**：
*   `CheckoutUseCase` 完全不知道 SQL 或 SMTP 的存在。
*   測試時，我們可以傳入 `MockInventoryRepository` 和 `MockNotificationService`，在記憶體中驗證邏輯，速度極快。

**Analysis**:
*   `CheckoutUseCase` is completely unaware of SQL or SMTP.
*   During testing, we can pass `MockInventoryRepository` and `MockNotificationService` to verify logic in-memory, which is extremely fast.

---

## 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 貧血模型 (Anemic Domain Model)

*   **錯誤描述**：Domain Entities 只有 Getter/Setter，所有的業務邏輯都寫在 Service (Use Case) 層。
*   **為何不好**：這違背了物件導向設計，導致 Service 層變得臃腫且難以維護。業務規則應該盡可能靠近資料 (即在 Entity 內部，如上述 `product.decreaseStock()`)。
*   **修正**：將狀態檢核與變更邏輯移回 Entity。

*   **Description**: Domain Entities only have Getters/Setters, and all business logic resides in the Service (Use Case) layer.
*   **Why it's bad**: This violates Object-Oriented Design, causing the Service layer to become bloated and hard to maintain. Business rules should be as close to the data as possible (i.e., inside the Entity, like `product.decreaseStock()` above).
*   **Fix**: Move state validation and mutation logic back into the Entity.

### 5.2 抽象洩漏 (Leaky Abstractions)

*   **錯誤描述**：將 ORM 的 Entity (如 Hibernate `@Entity` 或 TypeORM 物件) 直接作為 Domain Entity 使用，甚至傳遞到 Controller 層。
*   **為何不好**：UI 層或業務層直接依賴了資料庫結構。為了效能調整 DB Schema 時，可能會破壞前端合約。
*   **修正**：堅持使用 Mapper 模式，在 Adapter 層將 DB Entity 轉換為純 Domain Entity。

*   **Description**: Using ORM Entities (like Hibernate `@Entity` or TypeORM objects) directly as Domain Entities, or even passing them to the Controller layer.
*   **Why it's bad**: The UI or Business layer depends directly on the database structure. Tuning DB Schema for performance might break frontend contracts.
*   **Fix**: Strictly use the Mapper pattern to convert DB Entities to pure Domain Entities within the Adapter layer.

### 5.3 過度工程化 (Over-Engineering)

*   **錯誤描述**：對一個簡單的 CRUD 應用程式 (例如只有 Create/Read 功能的後台管理) 強行套用完整的 Clean Architecture。
*   **為何不好**：增加了大量的 Interface、Adapter 和 Mapper 程式碼，卻沒有帶來邏輯隔離的好處 (因為根本沒有複雜邏輯)。
*   **修正**：對於簡單的 CRUD，傳統的 Layered Architecture (Controller -> Service -> Repository) 已經足夠且更高效。

*   **Description**: Forcing full Clean Architecture on a simple CRUD application (e.g., an admin panel with only Create/Read functions).
*   **Why it's bad**: Adds a massive amount of Interface, Adapter, and Mapper code without bringing the benefit of logic isolation (since there is no complex logic).
*   **Fix**: For simple CRUD, traditional Layered Architecture (Controller -> Service -> Repository) is sufficient and more efficient.

---

## 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 請向 Junior 工程師解釋為什麼我們要寫這麼多 Interface，而不直接呼叫 Database Class？
**Explain to a Junior engineer why we write so many Interfaces instead of calling the Database Class directly?**

*   **高分回答要點**：
    *   **解耦 (Decoupling)**：解釋「依賴反轉」。我們希望高層策略 (業務規則) 不受低層細節 (DB 驅動更新) 影響。
    *   **測試 (Testing)**：強調單元測試的重要性。如果直接依賴 DB，測試就會變慢且脆弱 (Flaky)。Interface 允許我們使用 Test Doubles。
    *   **並行開發 (Parallel Dev)**：後端邏輯開發時，資料庫可能還沒準備好，我們可以先針對 Interface 寫程式。

*   **Key Points**:
    *   **Decoupling**: Explain "Dependency Inversion." We want high-level policy (business rules) to be immune to low-level details (DB driver updates).
    *   **Testing**: Emphasize unit testing. Direct DB dependency makes tests slow and flaky. Interfaces allow Test Doubles.
    *   **Parallel Dev**: Business logic can be developed against the interface even if the database isn't ready.

### Q2: 在 Clean Architecture 中，跨層的資料轉換 (Mapping) 會導致效能問題嗎？你會如何權衡？
**In Clean Architecture, does cross-layer data mapping cause performance issues? How do you trade off?**

*   **高分回答要點**：
    *   **承認成本**：是的，物件轉換 (DTO -> Domain -> ORM) 有 CPU 與記憶體成本。
    *   **規模觀點**：在大多數業務應用中，I/O (DB/Network) 才是瓶頸，物件轉換的開銷通常可忽略不計。
    *   **例外處理**：如果是高頻交易或巨量資料處理，我們可以針對特定路徑 (Fast Path) 放寬架構限制，繞過完整的層級 (CQRS 模式中的 Query 端常這樣做)。

*   **Key Points**:
    *   **Acknowledge Cost**: Yes, object mapping (DTO -> Domain -> ORM) has CPU and memory costs.
    *   **Scale Perspective**: In most business apps, I/O (DB/Network) is the bottleneck; mapping overhead is usually negligible.
    *   **Exception Handling**: For high-frequency trading or massive data processing, we can relax architectural constraints for specific paths (Fast Path), often seen in the Query side of CQRS.

### Q3: 你的 Domain Layer 應該包含依賴注入 (DI) 的框架註解嗎 (例如 `@Inject` or `@Service`)？
**Should your Domain Layer contain Dependency Injection (DI) framework annotations (e.g., `@Inject` or `@Service`)?**

*   **高分回答要點**：
    *   **理想情況**：不應該。Domain Layer 應該是 "Framework Agnostic" (與框架無關)。
    *   **實務妥協**：有些團隊為了便利，會使用標準規範 (如 Java 的 JSR-330 `javax.inject`)，這是可以接受的，因為它不是特定框架 (如 Spring) 的依賴。但絕對不能依賴特定框架的具體實作。

*   **Key Points**:
    *   **Ideal**: No. The Domain Layer should be "Framework Agnostic."
    *   **Pragmatic Compromise**: Some teams use standard specs (like Java's JSR-330 `javax.inject`) for convenience, which is acceptable as it's not a specific framework dependency. But never depend on specific framework implementations.

---

## 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)

1.  **依賴方向 (Dependency Direction)**：永遠指向內部。基礎設施依賴業務邏輯，而非相反。
2.  **Ports & Adapters**：Ports 是介面 (合約)，Adapters 是實作 (外掛)。應用程式是核心。
3.  **可測試性 (Testability)**：架構的主要驅動力之一。如果你的架構難以進行單元測試，那就是設計有問題。
4.  **Database is a Detail**：資料庫只是一個存儲機制，不應主導系統設計。
5.  **Use Cases**：清楚地表達系統「能做什麼」，而不是系統「由什麼組成」。

### 後續延伸 (Next Steps)

*   **實作練習**：嘗試重構一個現有的 CRUD 模組，將其改寫為 Hexagonal Architecture，並為其核心邏輯撰寫不依賴 DB 的單元測試。
*   **延伸閱讀**：
    *   **Chapter 06**: 將探討 **Domain-Driven Design (DDD)**，這是填充 Clean Architecture "Domain Layer" 內容的最佳實踐。
    *   **CQRS (Command Query Responsibility Segregation)**：學習如何將讀取與寫入模型分離，以解決 Clean Architecture 在複雜查詢場景下的效能問題。