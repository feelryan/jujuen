# 結構模式：介面適配與封裝 / Structural Patterns: Interface Adaptation and Wrappers

## Mental model｜心智模型

在軟體架構中，結構模式（Structural Patterns）解決的核心問題是 **「如何將物件和類別組合成更大的結構，同時保持結構的彈性與高效」**。

對於本章節聚焦的 Adapter, Decorator, Facade 與 Proxy，你可以建立以下的心智模型：**「包裝器（Wrappers）」與「中介層（Intermediaries）」**。

1.  **適配（Adaptation）是「翻譯機」**：
    當兩個物件因介面不相容而無法溝通時，我們不修改原本的程式碼，而是套上一個轉接頭（Adapter）。就像出國旅行用的萬用插座，牆壁上的電（Legacy Code/Third-party API）沒變，你的電器（Client Code）也沒變，中間的 Adapter 負責轉換電壓與插孔形狀。

2.  **裝飾（Decoration）是「洋蔥式包裝」**：
    當你想為物件增加功能（如 Log、快取、權限檢查），但不想透過繼承（Inheritance）製造出爆炸多的子類別時，你將物件一層一層包起來。每一層裝飾器都實作相同的介面，Client 甚至不知道它呼叫的是核心物件還是包裝過的物件。

3.  **外觀（Facade）是「總機櫃檯」**：
    系統內部可能很複雜（幾十個微服務、複雜的初始化流程），Facade 提供一個簡單的單一窗口。Client 只需要對 Facade 說「我要結帳」，Facade 會負責去協調庫存、金流、物流系統。

4.  **代理（Proxy）是「替身或保鑣」**：
    Client 以為它在跟真實物件溝通，但其實是對著替身說話。這個替身可以控制存取權限（Protection Proxy）、延遲載入（Virtual Proxy/Lazy Loading）或處理網路通訊（Remote Proxy）。

---

## Patterns & best practices｜常見模式與最佳實務

在真實專案中，這些模式通常以以下形式出現：

### 1. Adapter: The Anti-Corruption Layer (ACL)
在整合第三方服務（如 Stripe, AWS S3）或遺留系統（Legacy System）時，不要讓外部的資料結構（DTOs）直接滲透到你的核心業務邏輯中。
*   **Practice**: 定義一個屬於你 Domain 的 `Interface`（例如 `IFileStorage`），然後撰寫一個 `S3Adapter` 實作該介面。
*   **Benefit**: 當你想從 AWS 換到 Azure 時，只需更換 Adapter，業務邏輯完全不用改。

### 2. Decorator: Middleware & Interceptors
現代框架中的 Middleware（如 Express.js, ASP.NET Core）或攔截器（Interceptors）本質上就是 Decorator 模式的應用。
*   **Practice**: 使用 Decorator 處理 **Cross-cutting concerns（橫切關注點）**。例如：`CachingDecorator` 包裹 `Repository`，`LoggingDecorator` 包裹 `Service`。
*   **Benefit**: 符合單一職責原則（SRP），業務邏輯不被雜訊（Log, Cache code）污染。

### 3. Facade: Service Layer / API Gateway
在微服務或模組化架構中，Facade 常體現為 Service Layer 或 API Gateway 中的 Aggregator。
*   **Practice**: 封裝複雜的業務流程。例如 `OrderFacade.placeOrder()` 內部依序呼叫 `InventorySystem.check()`, `PaymentGateway.charge()`, `EmailService.send()`。
*   **Benefit**: 降低 Client 與子系統的耦合度（Loose Coupling）。

### 4. Proxy: Lazy Loading & Security
*   **Practice**: ORM (如 Hibernate, Entity Framework) 使用 Proxy 實現 **Lazy Loading**。當你存取 `User.Orders` 時，Proxy 才會真正發送 SQL 查詢。
*   **Practice**: 在存取敏感物件前，使用 Proxy 檢查當前使用者的 Role（RBAC）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The God Adapter (全能適配器)
*   **Bad Smell**: Adapter 不僅僅做介面轉換，還包含了大量的業務邏輯、驗證邏輯，甚至修復了 Legacy Code 的 Bug。
*   **Consequence**: Adapter 變得難以維護且違反 SRP。
*   **Fix**: Adapter 應只負責「翻譯」。業務邏輯應移至 Domain Service，Bug 修復應在 Legacy Code 或透過 Decorator 處理。

### 2. Decorator Hell (裝飾器地獄)
*   **Bad Smell**: 過度使用 Decorator，導致物件被包了 10 層以上。
*   **Consequence**: Stack trace 變得極度難讀，Debug 時找不到錯誤源頭；初始化程式碼變得冗長且易錯。
*   **Fix**: 使用 Dependency Injection (DI) Container 來管理裝飾器的組裝；或者考慮 AOP (Aspect-Oriented Programming) 工具。

### 3. Leaky Facade (洩漏的外觀)
*   **Bad Smell**: Facade 的方法回傳了子系統的內部物件（如 Entity 或 DB Connection），或者 Facade 允許 Client 繞過它直接存取子系統。
*   **Consequence**: 喪失了封裝的意義，Client 再次與子系統緊密耦合。
*   **Fix**: Facade 應該回傳專用的 DTO，並確保子系統對外不可見（例如設為 `internal` 或 `package-private`）。

### 4. Proxy Performance Overhead (代理效能開銷)
*   **Bad Smell**: 在高頻呼叫的路徑上使用了過多的動態代理（Dynamic Proxies, Reflection-based）。
*   **Consequence**: 系統效能顯著下降。
*   **Fix**: 對於效能敏感區塊，手動實作靜態 Proxy，或謹慎評估 Reflection 的成本。

---

## Checklists & workflows｜檢查清單與流程

### Decision Framework: 該選哪一個？

- **Q1: 你是否需要使用一個現有的類別，但它的介面不符合你的需求？**
    - [ ] Yes -> 使用 **Adapter**。
- **Q2: 你是否需要在不修改現有程式碼的情況下，動態地為物件增加行為？**
    - [ ] Yes -> 使用 **Decorator**。
- **Q3: 你是否需要簡化一個複雜系統的介面，提供一個統一的入口？**
    - [ ] Yes -> 使用 **Facade**。
- **Q4: 你是否需要控制對某個物件的存取（權限、延遲載入、網路存取）？**
    - [ ] Yes -> 使用 **Proxy**。

### Implementation Checklist

- [ ] **Interface Consistency**: 所有的 Wrapper (Decorator/Proxy) 是否嚴格遵守了原始介面契約？
- [ ] **Composition over Inheritance**: 確認你是透過「持有物件（Composition）」而不是「繼承物件」來擴充功能。
- [ ] **Error Handling Translation**: (針對 Adapter/Facade) 來自底層或第三方 API 的 Exception，是否已轉換為 Domain Exception？不要讓 `StripeException` 直接拋到 UI 層。
- [ ] **Transparency**: (針對 Proxy/Decorator) Client 是否能感知到它正在使用 Wrapper？理想情況下應該是無感知的（Transparent）。

---

## Real-world examples｜實戰案例

### Scenario 1: Adapter for 3rd-Party Payment (Anti-Corruption Layer)

你正在開發電商系統，原本只支援 PayPal，現在要加入 Stripe，未來可能還有更多。

```typescript
// 1. Target Interface (Your Domain)
interface IPaymentProcessor {
  pay(amount: number, currency: string): Promise<boolean>;
}

// 2. Adaptee (3rd Party Library - Stripe)
class StripeSDK {
  makeCharge(cents: number, token: string): StripeResponse { /* ... */ }
}

// 3. Adapter
class StripeAdapter implements IPaymentProcessor {
  private stripe: StripeSDK;

  constructor(stripe: StripeSDK) {
    this.stripe = stripe;
  }

  async pay(amount: number, currency: string): Promise<boolean> {
    // 轉換邏輯：Dollars to Cents
    const cents = amount * 100;
    try {
      const response = this.stripe.makeCharge(cents, "default_token");
      return response.status === 'succeeded';
    } catch (e) {
      // 轉換錯誤：3rd party error -> Domain error
      throw new PaymentFailedException(e.message);
    }
  }
}
```

### Scenario 2: Decorator for Caching & Logging

你有一個讀取資料庫的 Repository，希望加上快取功能，但不想改動原本的 SQL 邏輯。

```typescript
interface IUserRepository {
  getById(id: string): Promise<User>;
}

// Concrete Component
class SqlUserRepository implements IUserRepository {
  async getById(id: string): Promise<User> {
    return db.query("SELECT * FROM users WHERE id = ?", [id]);
  }
}

// Decorator: Caching
class CachedUserRepository implements IUserRepository {
  private innerRepo: IUserRepository;
  private cache: Map<string, User>;

  constructor(repo: IUserRepository) {
    this.innerRepo = repo;
  }

  async getById(id: string): Promise<User> {
    if (this.cache.has(id)) {
      console.log("Cache Hit");
      return this.cache.get(id);
    }
    
    const user = await this.innerRepo.getById(id);
    this.cache.set(id, user);
    return user;
  }
}

// Usage (Composition)
const repo = new CachedUserRepository(new SqlUserRepository());
```

### Scenario 3: Facade for Complex System Initialization

啟動一個遊戲引擎或複雜的報表系統往往涉及多個子系統。

```typescript
class GameEngineFacade {
  private physics: PhysicsSystem;
  private sound: SoundSystem;
  private graphics: GraphicsSystem;

  constructor() {
    this.physics = new PhysicsSystem();
    this.sound = new SoundSystem();
    this.graphics = new GraphicsSystem();
  }

  public startGame(level: string) {
    // 封裝複雜的啟動順序
    this.physics.initialize();
    this.sound.loadAssets(level);
    this.graphics.setupResolution(1920, 1080);
    this.graphics.renderLoadingScreen();
    console.log("Game Started");
  }
}

// Client 只需要一行程式碼
new GameEngineFacade().startGame("Level_1");
```