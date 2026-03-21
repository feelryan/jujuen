# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，GoF (Gang of Four) 設計模式不再是需要死記硬背的類別圖（Class Diagrams），而是一種「溝通語言」與「重構直覺」。在現代軟體開發中，這些模式往往隱藏在框架（Frameworks）與語言特性（Language Features）之下。本章的目標是透過現代化的視角，重新審視經典模式。

For senior engineers, GoF (Gang of Four) design patterns are no longer class diagrams to be rote-memorized, but rather a "communication language" and a "refactoring intuition." In modern software development, these patterns are often hidden beneath frameworks and language features. The goal of this chapter is to revisit classic patterns through a modern lens.

完成本章後，你應該能夠：
After completing this chapter, you should be able to:

1.  **識別框架源碼中的模式**：理解 Spring 的 IoC 容器如何實作 Factory 模式，或 React Hooks 如何體現 Observer 概念。
    **Identify patterns in framework source code:** Understand how Spring's IoC container implements the Factory pattern, or how React Hooks embody Observer concepts.
2.  **運用模式解決複雜度**：在系統設計面試或實務中，利用 Strategy 與 Factory 模式消除大規模的 `if-else` 或 `switch` 邏輯。
    **Apply patterns to manage complexity:** Use Strategy and Factory patterns to eliminate massive `if-else` or `switch` logic during system design interviews or real-world scenarios.
3.  **權衡模式的利弊**：清楚解釋何時該引入 Decorator 模式來處理 Cross-cutting concerns（橫切關注點），以及何時這會導致系統過度設計（Over-engineering）。
    **Evaluate trade-offs:** Clearly explain when to introduce the Decorator pattern for cross-cutting concerns, and when it leads to over-engineering.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 模式的現代化轉變 (The Modern Shift of Patterns)

傳統 GoF 模式強調「類別與繼承（Class & Inheritance）」，而現代應用則更傾向於「介面與組合（Interface & Composition）」以及「函數式編程（Functional Programming）」。

Traditional GoF patterns emphasized "Class & Inheritance," whereas modern applications lean heavily towards "Interface & Composition" and "Functional Programming."

-   **Factory (工廠模式)**：
    -   *Classic*: `Creator` 類別與繼承結構。
    -   *Modern*: 依賴注入容器（DI Container）或簡單的函數閉包（Closures）。Spring `BeanFactory` 是一個超級工廠；在 Go 或 TS 中，往往只是一個回傳 Interface 的函數。
    -   *Mental Model*: **"The Assembler"** — 負責將依賴關係組裝好，讓使用者只專注於使用介面。

-   **Strategy (策略模式)**：
    -   *Classic*: 建立一個介面與多個實作類別。
    -   *Modern*: Lambda 表達式或高階函數（Higher-Order Functions）。在 Java Stream API 或 Python 中，傳入一個 `Comparator` 或 `filter` 函數就是策略模式的極致簡化。
    -   *Mental Model*: **"The Plug-in"** — 在執行時動態抽換演算法的核心邏輯。

-   **Observer (觀察者模式)**：
    -   *Classic*: `Subject` 維護一個 `Observer` 列表。
    -   *Modern*: Reactive Streams (RxJava, RxJS), Event Bus, 或 React 的 `useEffect` (監聽 state 變化)。
    -   *Mental Model*: **"The Broadcaster"** — 解耦觸發事件的一方與響應事件的一方。

-   **Decorator (裝飾者模式)**：
    -   *Classic*: 包裝物件以擴充功能。
    -   *Modern*: Middleware (Express.js, ASP.NET Core), Python Decorators (`@`), 或 React HOC (Higher-Order Components)。
    -   *Mental Model*: **"The Wrapper / The Middleware"** — 像洋蔥一樣層層包裹核心邏輯，處理 Logging, Auth, Caching 等。

## 2.2 觀念對照 (Concept Comparison)

| 概念 (Concept) | 傳統 GoF 實作 (Traditional GoF) | 現代框架/語言實作 (Modern Framework/Language) |
| :--- | :--- | :--- |
| **Factory** | `public class ShapeFactory` | Spring `@Bean`, Angular Dependency Injection |
| **Strategy** | `public class QuickSort implements SortStrategy` | `list.sort((a, b) => a - b)` (Lambdas) |
| **Observer** | `subject.attach(observer)` | `document.addEventListener`, RxJS `Observable`, Kafka Consumer |
| **Decorator** | `new BufferedInputStream(new FileInputStream(file))` | `@Transactional`, Python Decorators, HTTP Middleware |

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在系統設計（System Design）中，我們很少直接畫出 UML 類別圖，但模式的**精神**決定了架構的可擴充性。

In System Design, we rarely draw UML class diagrams directly, but the **spirit** of the patterns dictates the architecture's extensibility.

## 3.1 支付閘道整合 (Payment Gateway Integration) - Strategy & Factory
**場景**：一個電商系統需要支援 PayPal, Stripe, Apple Pay 多種支付方式。
**Scenario**: An e-commerce system needs to support PayPal, Stripe, and Apple Pay.

-   **架構角色**：
    -   **Strategy**: 定義統一的 `PaymentProcessor` 介面（`pay`, `refund`）。
    -   **Factory**: 根據使用者的選擇（Region, Currency, User Preference）決定實例化哪個 Strategy。
-   **影響**：
    -   **可維護性**：新增一種支付方式只需新增一個 Class 並註冊到 Factory，不需修改核心結帳流程（Open/Closed Principle）。
    -   **測試性**：可以輕鬆注入 `MockPaymentStrategy` 進行單元測試。

## 3.2 跨切面關注點 (Cross-Cutting Concerns) - Decorator / Chain of Responsibility
**場景**：所有的 API 請求都需要進行 Authentication、Logging 和 Rate Limiting。
**Scenario**: All API requests require Authentication, Logging, and Rate Limiting.

-   **架構角色**：
    -   **Decorator (Middleware)**：每個 Middleware 都是一個裝飾者，它接收 Request，處理部分邏輯，然後呼叫 `next()`。
-   **影響**：
    -   **安全性**：Auth 邏輯集中在最外層，業務邏輯開發者不需要在每個 Controller 寫 `if (!user.isLoggedIn)`。
    -   **可觀測性**：可以在最外層的 Decorator 統一計算 Request Latency 並送往 Monitoring System (Prometheus/Datadog)。

---

# 4. 逐步示例 (Walkthrough / Example)

我們將以 **"多渠道通知服務 (Multi-channel Notification Service)"** 為例，展示如何從 naive 的寫法演進到結合 **Strategy** 與 **Factory** 的現代化寫法。

We will use a **"Multi-channel Notification Service"** as an example to demonstrate the evolution from a naive implementation to a modern approach combining **Strategy** and **Factory**.

### 4.1 階段一：Naive Implementation (The Anti-pattern)

這是資淺工程師常見的寫法，充滿了 `if-else`，違反了單一職責原則（SRP）與開閉原則（OCP）。

This is a common approach for junior engineers, full of `if-else` statements, violating the Single Responsibility Principle (SRP) and the Open/Closed Principle (OCP).

```typescript
class NotificationService {
  send(type: string, message: string, recipient: string) {
    if (type === 'EMAIL') {
      // Connect to SMTP
      // Construct Email body
      console.log(`Sending Email to ${recipient}: ${message}`);
    } else if (type === 'SMS') {
      // Connect to Twilio/AWS SNS
      // Validate phone number
      console.log(`Sending SMS to ${recipient}: ${message}`);
    } else if (type === 'SLACK') {
      // Call Slack Webhook
      console.log(`Posting to Slack for ${recipient}: ${message}`);
    } else {
      throw new Error('Unknown notification type');
    }
  }
}
```

### 4.2 階段二：引入 Strategy Pattern (Refactoring)

我們定義介面，並將實作拆分。

We define an interface and split the implementation.

```typescript
// 1. The Strategy Interface
interface NotificationStrategy {
  send(message: string, recipient: string): Promise<void>;
}

// 2. Concrete Strategies
class EmailStrategy implements NotificationStrategy {
  async send(message: string, recipient: string) {
    console.log(`[Email Logic] Sending to ${recipient}`);
  }
}

class SmsStrategy implements NotificationStrategy {
  async send(message: string, recipient: string) {
    console.log(`[SMS Logic] Sending to ${recipient}`);
  }
}

// 3. Usage (Still requires manual instantiation)
const emailService = new EmailStrategy();
emailService.send("Hello", "user@example.com");
```

### 4.3 階段三：現代化 Factory 與 Map Lookup (Production Ready)

在實務上，我們不會手動 `new` 這些策略。我們會使用一個 Map（註冊表）來取代 `switch-case`，並結合依賴注入。

In practice, we don't manually `new` these strategies. We use a Map (Registry) to replace `switch-case` and combine it with Dependency Injection.

```typescript
// Enums for type safety
enum ChannelType {
  EMAIL = 'EMAIL',
  SMS = 'SMS',
  SLACK = 'SLACK'
}

// Factory / Registry
class NotificationStrategyFactory {
  private strategies: Map<ChannelType, NotificationStrategy> = new Map();

  constructor() {
    // In a real framework like Spring or NestJS, 
    // these would be injected automatically via DI.
    this.register(ChannelType.EMAIL, new EmailStrategy());
    this.register(ChannelType.SMS, new SmsStrategy());
  }

  register(type: ChannelType, strategy: NotificationStrategy) {
    this.strategies.set(type, strategy);
  }

  getStrategy(type: ChannelType): NotificationStrategy {
    const strategy = this.strategies.get(type);
    if (!strategy) {
      throw new Error(`No strategy found for type: ${type}`);
    }
    return strategy;
  }
}

// Context (The Client)
class NotificationContext {
  constructor(private factory: NotificationStrategyFactory) {}

  async notifyUser(type: ChannelType, message: string, user: string) {
    const strategy = this.factory.getStrategy(type);
    
    // Cross-cutting concern: Logging (Decorator pattern could apply here too)
    console.time(`Sending ${type}`);
    
    await strategy.send(message, user);
    
    console.timeEnd(`Sending ${type}`);
  }
}

// Usage
const factory = new NotificationStrategyFactory();
const service = new NotificationContext(factory);

service.notifyUser(ChannelType.EMAIL, "Welcome!", "alice@example.com");
```

**分析 (Analysis)**：
-   **複雜度**：時間複雜度從 O(N) (if-else chain) 降為 O(1) (Map lookup)。
-   **擴充性**：新增 Slack 支援時，只需實作 `SlackStrategy` 並在 Factory 註冊，完全不觸碰 `NotificationContext`。

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

資深工程師在應用模式時，常犯的錯誤不是「不懂模式」，而是「過度使用」或「誤用」。

Senior engineers often make mistakes not because they "don't understand the patterns," but because of "overuse" or "misuse."

1.  **過度設計 (Over-Engineering / Pattern Happy)**
    -   *描述*：為了一個只有兩種變體且未來極少變動的邏輯（例如：性別顯示）建立完整的 Factory + Strategy。
    -   *Why it's bad*：增加了不必要的類別數量與程式碼跳轉（Indirection），降低了可讀性。
    -   *Solution*：簡單的 `Map` 查找或 Enum 方法往往足夠。**Rule of Three**: 等到有第三種變體或邏輯變複雜時再重構。

2.  **裝飾者地獄 (Decorator Hell)**
    -   *描述*：在 Python 或 Java 中層層堆疊 Decorators/Annotations，導致無法追蹤執行順序或副作用。
    -   *Example*：`@Transactional @Cacheable @Log @Validate ... public void doSomething()`
    -   *Why it's bad*：如果 `@Cacheable` 在 `@Transactional` 之前執行，可能導致資料庫交易未開啟就嘗試快取，引發 Bug。
    -   *Solution*：明確定義 Middleware/Interceptor 的優先級順序；對於過於複雜的組合，考慮使用 Facade 模式封裝。

3.  **濫用 Singleton (Singleton Abuse)**
    -   *描述*：將所有 Service 都設計成 Singleton，卻在其中保存了可變狀態（Mutable State）。
    -   *Why it's bad*：在並發環境（Concurrency）下會導致 Race Conditions。在單元測試時，Singleton 的狀態難以重置，導致測試互相干擾。
    -   *Solution*：依賴 DI 容器管理 Singleton Scope，並確保 Singleton 物件是無狀態的（Stateless）。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

在面試 Senior 職位時，面試官通常不會問「請定義 Factory 模式」，而是問「你在什麼情境下使用了它」。

When interviewing for Senior positions, interviewers usually won't ask "Please define the Factory pattern," but rather "In what context did you use it?"

### Q1: 如何消除程式碼中大量的 `if-else` 或 `switch` 語句？
**How do you eliminate massive `if-else` or `switch` statements in code?**

-   **高分回答要點 (Key Points)**：
    -   提到 **Strategy Pattern** 將行為封裝。
    -   提到使用 **Factory** 或 **Map/Dictionary** 進行 O(1) 的策略查找。
    -   補充說明：如果邏輯非常簡單（例如只是回傳不同字串），使用 Configuration Map 即可，不需要完整的 Class。
    -   進階：提到在資料庫驅動的設計中，可以將策略設定檔存在 DB，實現動態開關功能（Feature Flags）。

### Q2: 請比較 Decorator 模式與 Proxy 模式的差異？
**Please compare the Decorator pattern and the Proxy pattern.**

-   **高分回答要點 (Key Points)**：
    -   **意圖（Intent）不同**：Decorator 專注於**增加功能**（Enhance behavior），Proxy 專注於**控制存取**（Control access）。
    -   **實務案例**：
        -   Decorator: `GzipOutputStream` (增加壓縮功能), React HOC (增加 Props)。
        -   Proxy: Hibernate Lazy Loading (控制 DB 存取), Nginx Reverse Proxy (控制網路流量), Protection Proxy (權限檢查)。
    -   雖然結構相似（都包裝了另一個物件），但使用場景完全不同。

### Q3: 在現代框架（如 Spring, React）中，你看到了哪些 GoF 模式的影子？
**What traces of GoF patterns do you see in modern frameworks (like Spring, React)?**

-   **高分回答要點 (Key Points)**：
    -   **Spring**: `ApplicationContext` 是 Factory；AOP 是動態代理（Dynamic Proxy）與 Decorator 的結合；`ApplicationEvent` 是 Observer。
    -   **React**: Components 組合是 Composite 模式；`useEffect` / State 變更是 Observer 模式；HOC 是 Decorator 模式。
    -   這顯示了你不是死背書，而是能將理論映射到日常工具。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 記憶錨點 (Key Takeaways)
1.  **Factory** 是物件的組裝線，現代多由 DI 容器（如 Spring）代勞。
2.  **Strategy** 讓演算法可抽換，現代多配合 Lambda 或 Map Lookup 實作，消除 `if-else`。
3.  **Observer** 解耦了事件源與處理者，是 Event-Driven Architecture 的基石。
4.  **Decorator** 用於處理橫切關注點（Logging, Auth），類似洋蔥皮層層包裹。
5.  **Composition over Inheritance**：現代模式應用更傾向於組合而非繼承。

## 後續延伸 (Next Steps)
-   **實作練習**：嘗試在你目前的專案中，找到一個超過 20 行的 `switch` 語句，並使用 Strategy + Factory 重構它。
-   **延伸閱讀**：下一章將探討 **"Concurrency Patterns" (並發模式)**，例如 Producer-Consumer, Fan-out/Fan-in，這對於高流量系統設計至關重要。
-   **深入源碼**：閱讀你常用的 HTTP Client 函式庫源碼（如 Axios 或 OkHttp），尋找 Interceptor（Decorator）的實作方式。