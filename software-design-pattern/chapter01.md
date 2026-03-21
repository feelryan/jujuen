# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，SOLID 原則與物件導向（OO）早已不是新名詞，但在高壓的系統設計面試或大規模專案重構中，能否精準判斷「何時該遵守、何時該打破」這些原則，才是區分 Senior 與 Staff 工程師的關鍵。本章將超越教科書式的定義，聚焦於實戰中的權衡與架構思維。

For senior engineers, SOLID principles and Object-Oriented (OO) concepts are hardly new terms. However, in high-pressure system design interviews or large-scale project refactoring, the ability to precisely judge "when to adhere to and when to break" these principles is what distinguishes a Senior engineer from a Staff engineer. This chapter moves beyond textbook definitions to focus on trade-offs and architectural thinking in real-world scenarios.

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **重新定義 SRP 與 OCP**：不再只是「做一件事」或「開放封閉」，而是從「變更的軸心（Axis of Change）」與「插件式架構」的角度來理解。
    **Redefine SRP and OCP**: Move beyond "doing one thing" or "open-closed" to understanding them through the lens of "Axis of Change" and "Plugin Architecture."
2.  **掌握 Composition over Inheritance 的實戰邊界**：清楚解釋繼承（Inheritance）造成的 Fragile Base Class 問題，並能熟練運用組合（Composition）與委派（Delegation）來解耦。
    **Master the boundaries of Composition over Inheritance**: Clearly explain the Fragile Base Class problem caused by inheritance and skillfully use Composition and Delegation to decouple systems.
3.  **識別 SOLID 的過度設計（Over-engineering）**：在 Code Review 或設計討論中，能夠指出何時引入介面或抽象是不必要的複雜度。
    **Identify SOLID Over-engineering**: In Code Reviews or design discussions, point out when introducing interfaces or abstractions adds unnecessary complexity.
4.  **在系統設計面試中應用 DIP**：利用依賴反轉原則（Dependency Inversion Principle）來設計可測試、可替換的模組（如 Hexagonal Architecture）。
    **Apply DIP in System Design Interviews**: Use the Dependency Inversion Principle to design testable, swappable modules (e.g., Hexagonal Architecture).

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 SOLID 的深層解讀 (Deep Dive into SOLID)

許多開發者背誦 SOLID 口訣，卻忽略了它們是為了解決「依賴管理（Dependency Management）」問題而生的。
Many developers memorize the SOLID acronym but overlook that they were born to solve "Dependency Management" problems.

### SRP (Single Responsibility Principle) - 變更的來源
**直覺類比**：公司的財務報表與技術架構圖。這兩份文件不該由同一個人同時負責修改，因為它們回應的是不同部門（Stakeholders）的需求。
**Intuitive Analogy**: A company's financial report and its technical architecture diagram. These two documents shouldn't be modified by the same person simultaneously because they respond to the needs of different departments (Stakeholders).

**資深視角**：SRP 不是關於「函數行數」或「只做一件事」，而是關於「只有一個理由去修改它」。這個理由通常對應到業務上的一個特定角色（Actor）。
**Senior View**: SRP is not about "function length" or "doing one thing," but about having "only one reason to change." This reason usually corresponds to a specific Actor in the business context.

### OCP (Open/Closed Principle) - 插件思維
**直覺類比**：USB 接口。電腦主機（Core System）不需要為了插入新的滑鼠（Extension）而拆開機殼焊接電路。
**Intuitive Analogy**: USB ports. The computer tower (Core System) doesn't need to be opened and soldered to support a new mouse (Extension).

**資深視角**：OCP 的核心是多型（Polymorphism）。透過介面定義行為，讓新的實作可以被「注入」，而無需修改既有的調用程式碼。
**Senior View**: The core of OCP is Polymorphism. By defining behavior through interfaces, new implementations can be "injected" without modifying the existing calling code.

### LSP (Liskov Substitution Principle) - 行為的一致性
**資深視角**：這不僅是編譯器層面的型別相容，更是「契約（Contract）」的相容。如果你在子類別中拋出 `NotImplementedException`，或者改變了父類別預期的副作用（Side Effects），你就違反了 LSP。這會導致客戶端程式碼充滿 `if (obj instanceof SubClass)` 的壞味道。
**Senior View**: This isn't just about compiler-level type compatibility; it's about "Contract" compatibility. If you throw a `NotImplementedException` in a subclass or change the side effects expected by the parent class, you violate LSP. This leads to the code smell of `if (obj instanceof SubClass)` in client code.

### ISP (Interface Segregation Principle) - 避免胖介面
**資深視角**：不要強迫客戶端依賴他們不使用的方法。這在微服務的 API 設計或大型 SDK 開發中尤為重要。將一個巨大的 `GodInterface` 拆解為多個針對特定 Client 的小介面。
**Senior View**: Do not force clients to depend on methods they do not use. This is crucial in Microservices API design or large SDK development. Break down a massive `GodInterface` into multiple smaller interfaces tailored for specific Clients.

### DIP (Dependency Inversion Principle) - 權力反轉
**直覺類比**：牆上的插座。電器（高層策略）不依賴核電廠或風力發電廠（底層細節），而是依賴標準的電壓介面。
**Intuitive Analogy**: Wall sockets. Appliances (High-level policy) do not depend on nuclear or wind power plants (Low-level details) but on a standard voltage interface.

**資深視角**：高層模組不應依賴低層模組，兩者都應依賴抽象。這是 Clean Architecture 的基石。
**Senior View**: High-level modules should not depend on low-level modules; both should depend on abstractions. This is the cornerstone of Clean Architecture.

## 2.2 Composition over Inheritance (組合優於繼承)

**核心差異**：
*   **Inheritance (Is-a)**：白箱重用。子類別看得到父類別的內部，父類別的變更可能破壞子類別（Fragile Base Class Problem）。編譯期決定關係。
*   **Composition (Has-a)**：黑箱重用。物件僅透過公開介面互動。執行期可動態改變行為（Dependency Injection）。

**Core Differences**:
*   **Inheritance (Is-a)**: White-box reuse. Subclasses see the internals of the parent; changes in the parent can break the subclass (Fragile Base Class Problem). Relationships are determined at compile-time.
*   **Composition (Has-a)**: Black-box reuse. Objects interact only through public interfaces. Behaviors can be changed dynamically at runtime (Dependency Injection).

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型分散式系統中，SOLID 原則直接影響系統的**可測試性（Testability）**與**可維護性（Maintainability）**。

In large-scale distributed systems, SOLID principles directly impact the system's **Testability** and **Maintainability**.

## 3.1 Hexagonal Architecture (Ports and Adapters)
這是 DIP 的極致應用。
This is the ultimate application of DIP.

*   **Core Domain (High Level)**：定義 `Repository` 介面（Port）。
*   **Infrastructure (Low Level)**：實作 `PostgresRepository`（Adapter）。
*   **Benefit**：在單元測試時，可以輕鬆注入 `MockRepository`，完全不需要啟動真實資料庫。這讓 CI/CD 流程快上數倍。

*   **Core Domain (High Level)**: Defines the `Repository` interface (Port).
*   **Infrastructure (Low Level)**: Implements `PostgresRepository` (Adapter).
*   **Benefit**: During unit testing, a `MockRepository` can be easily injected without spinning up a real database. This makes CI/CD pipelines significantly faster.

## 3.2 SDK 與 Library 設計
當你設計一個供他人使用的 SDK 時，OCP 與 ISP 至關重要。
When designing an SDK for others, OCP and ISP are critical.

*   如果你違反 OCP，使用者每次升級你的 SDK 都需要重寫他們的程式碼。
*   如果你違反 ISP，使用者引入你的 SDK 可能會被強迫引入一堆他們不需要的 transitive dependencies（例如只想要 Logging 功能卻被強迫下載 AWS SDK）。

*   If you violate OCP, users have to rewrite their code every time they upgrade your SDK.
*   If you violate ISP, users importing your SDK might be forced to pull in a pile of transitive dependencies they don't need (e.g., wanting only Logging features but being forced to download the AWS SDK).

---

# 4. 逐步示例 (Walkthrough / Example)

## 場景：多通路通知服務 (Scenario: Multi-channel Notification Service)

我們需要設計一個服務，負責發送通知（Email, SMS, Push）。未來可能會增加 Slack 或 Webhook。

We need to design a service responsible for sending notifications (Email, SMS, Push). In the future, Slack or Webhooks might be added.

### 4.1 Naive Approach (Violation of OCP & SRP)

```typescript
class NotificationService {
  // 違反 SRP: 混合了不同通路的邏輯
  // Violates SRP: Mixes logic for different channels
  send(type: string, message: string, recipient: string) {
    if (type === 'email') {
      // Email logic: connect SMTP, format HTML...
      console.log(`Sending Email to ${recipient}: ${message}`);
    } else if (type === 'sms') {
      // SMS logic: connect Twilio...
      console.log(`Sending SMS to ${recipient}: ${message}`);
    }
    // 違反 OCP: 每次加新通路都要改這個方法
    // Violates OCP: Must modify this method for every new channel
  }
}
```

**問題**：
1.  每次新增通路都要修改 `NotificationService`，風險高且測試範圍大。
2.  依賴了所有具體的第三方 SDK（SMTP lib, Twilio SDK），導致 class 體積龐大。

**Issues**:
1.  Adding a channel requires modifying `NotificationService`, creating high risk and a large testing scope.
2.  It depends on all concrete third-party SDKs (SMTP lib, Twilio SDK), making the class massive.

### 4.2 Mature Solution (Applying SOLID & Composition)

我們使用 **Strategy Pattern** (Composition) 來重構。

We refactor using the **Strategy Pattern** (Composition).

**Step 1: Define Interface (DIP & ISP)**

```typescript
// 定義合約，高層模組依賴此介面
// Define contract, high-level modules depend on this interface
interface Notifier {
  send(message: string, recipient: string): Promise<void>;
}
```

**Step 2: Implement Strategies (SRP)**

```typescript
class EmailNotifier implements Notifier {
  async send(message: string, recipient: string): Promise<void> {
    // Only contains Email related logic
    console.log(`[SMTP] Sending Email to ${recipient}`);
  }
}

class SmsNotifier implements Notifier {
  async send(message: string, recipient: string): Promise<void> {
    // Only contains SMS related logic
    console.log(`[Twilio] Sending SMS to ${recipient}`);
  }
}
```

**Step 3: Composition in Context (OCP)**

```typescript
class NotificationManager {
  private notifiers: Map<string, Notifier>;

  constructor(notifiers: Map<string, Notifier>) {
    // 透過 Constructor Injection 傳入依賴
    // Dependencies passed via Constructor Injection
    this.notifiers = notifiers;
  }

  async notify(type: string, message: string, recipient: string) {
    const notifier = this.notifiers.get(type);
    if (!notifier) {
      throw new Error(`No notifier configured for type: ${type}`);
    }
    await notifier.send(message, recipient);
  }
}

// Usage
const notifiers = new Map<string, Notifier>();
notifiers.set('email', new EmailNotifier());
notifiers.set('sms', new SmsNotifier());
// 新增 Slack 時只需實作 SlackNotifier 並註冊，無需修改 NotificationManager
// To add Slack, just implement SlackNotifier and register it, no changes to NotificationManager
const service = new NotificationManager(notifiers);
```

### 4.3 Handling Cross-Cutting Concerns (Decorator Pattern)

如果我們需要為所有通知增加「重試機制」或「Log」，不要使用繼承（如 `RetryingEmailNotifier`）。請使用組合（Decorator）。

If we need to add "Retry Mechanism" or "Logging" for all notifications, do not use inheritance (e.g., `RetryingEmailNotifier`). Use Composition (Decorator).

```typescript
class RetryDecorator implements Notifier {
  constructor(private wrapped: Notifier, private maxRetries: number = 3) {}

  async send(message: string, recipient: string): Promise<void> {
    let attempts = 0;
    while (attempts < this.maxRetries) {
      try {
        await this.wrapped.send(message, recipient);
        return;
      } catch (e) {
        attempts++;
        console.warn(`Retry ${attempts}/${this.maxRetries}`);
      }
    }
    throw new Error('Failed after retries');
  }
}

// 組合出具有重試功能的 Email Notifier
// Compose an Email Notifier with retry capabilities
const robustEmailNotifier = new RetryDecorator(new EmailNotifier());
```

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 Interface Explosion (Header Interfaces)
**錯誤**：為每一個 Class 建立一個一模一樣的 Interface（例如 `UserService` 和 `IUserService`），即使只有一個實作。
**Pitfall**: Creating an identical Interface for every Class (e.g., `UserService` and `IUserService`), even if there is only one implementation.

**為何不好**：這是為了 Mock 而 Mock。如果該類別是 Domain Logic 且不依賴外部 I/O，直接測試 Class 即可。過多的介面增加了導航程式碼的認知負擔。
**Why it's bad**: This is mocking for the sake of mocking. If the class is Domain Logic and doesn't depend on external I/O, test the Class directly. Excessive interfaces increase the cognitive load of navigating the code.

## 5.2 Refused Bequest (LSP Violation)
**錯誤**：繼承了一個父類別，但對於其中某些方法，子類別無法支援，於是拋出 `UnsupportedOperationException`。
**Pitfall**: Inheriting from a parent class, but for certain methods, the subclass cannot support them, so it throws an `UnsupportedOperationException`.

**解決**：這意味著繼承階層設計錯誤。應該提取更小的介面（ISP），或者改用組合。
**Solution**: This implies a flawed inheritance hierarchy design. Extract smaller interfaces (ISP) or switch to composition.

## 5.3 God Object disguised as Dependency Injection
**錯誤**：將所有依賴都注入到一個巨大的 `Context` 物件中，然後在所有類別間傳遞這個 `Context`。
**Pitfall**: Injecting all dependencies into a massive `Context` object and passing this `Context` around to all classes.

**為何不好**：這隱藏了真實的依賴關係。你無法一眼看出某個 Class 到底需要什麼資源，這實際上是 Service Locator Pattern 的濫用。
**Why it's bad**: This hides the true dependencies. You cannot tell at a glance what resources a specific Class actually needs; this is effectively an abuse of the Service Locator Pattern.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

在面試 Senior/Staff 職位時，面試官常透過這些問題測試你對 Pattern 的理解深度。

When interviewing for Senior/Staff positions, interviewers often use these questions to test the depth of your understanding of patterns.

## Q1: "Can you describe a situation where you intentionally violated the DRY (Don't Repeat Yourself) principle?"
**高分回答要點**：
*   提到微服務之間的 Shared Library 陷阱。如果兩個服務共用一個 DTO，當一個服務變更需求時，會強迫另一個服務升級，造成耦合（Coupling）。
*   在這種情況下，適度的代碼重複（Duplication）比錯誤的抽象（Wrong Abstraction）更好。
**Key Points for a High Score**:
*   Mention the Shared Library trap between microservices. If two services share a DTO, a requirement change in one forces an upgrade in the other, causing Coupling.
*   In this context, moderate code duplication is better than the wrong abstraction.

## Q2: "Why is Composition favored over Inheritance? Give a concrete example where Inheritance failed you."
**高分回答要點**：
*   解釋 **Fragile Base Class** 問題。
*   舉例：原本有一個 `Bird` 父類別具有 `fly()` 方法。後來需要加入 `Penguin`，但企鵝不會飛。這時如果要維持繼承，就必須修改父類別或在子類別拋出異常（違反 LSP）。
*   解決方案：將 `Flyable` 提取為介面或行為組件，讓 `Bird` 擁有（Has-a）飛行能力，而不是定義為（Is-a）飛行物。
**Key Points for a High Score**:
*   Explain the **Fragile Base Class** problem.
*   Example: Originally had a `Bird` parent class with a `fly()` method. Later needed to add `Penguin`, but penguins can't fly. Maintaining inheritance would require modifying the parent or throwing exceptions in the subclass (violating LSP).
*   Solution: Extract `Flyable` as an interface or behavior component, allowing `Bird` to *have* (Has-a) flying ability rather than *being defined as* (Is-a) a flying thing.

## Q3: "How do you decide when to introduce a Design Pattern versus keeping the code simple (KISS)?"
**高分回答要點**：
*   **Rule of Three**：當類似的代碼出現第三次時才考慮重構為 Pattern。
*   **預測變更**：如果這部分邏輯是核心業務且預期會頻繁變更（High Churn Rate），則儘早引入 Pattern（如 Strategy 或 Factory）以符合 OCP。如果是穩定的工具函式，則保持簡單。
**Key Points for a High Score**:
*   **Rule of Three**: Only consider refactoring into a Pattern when similar code appears for the third time.
*   **Anticipating Change**: If the logic is core business and expected to change frequently (High Churn Rate), introduce Patterns (like Strategy or Factory) early to comply with OCP. If it's a stable utility function, keep it simple.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 本章記憶錨點 (Key Takeaways)
1.  **SOLID 是依賴管理工具**：它們幫助你隔離變更，防止修改 A 壞了 B。
    **SOLID is a dependency management toolkit**: They help you isolate changes, preventing modifications in A from breaking B.
2.  **SRP = Actor**：一個類別只應對一個業務角色負責。
    **SRP = Actor**: A class should be responsible to only one business actor.
3.  **OCP = Plugin**：透過多型讓系統可擴充。
    **OCP = Plugin**: Enable system extensibility through polymorphism.
4.  **DIP = Decoupling**：高層策略不應受限於底層實作細節。
    **DIP = Decoupling**: High-level policies should not be constrained by low-level implementation details.
5.  **Composition > Inheritance**：優先使用組合來組裝行為，避免繼承帶來的僵化結構。
    **Composition > Inheritance**: Prioritize composition to assemble behaviors, avoiding the rigid structures caused by inheritance.

## 下一步 (Next Steps)
理解了原則之後，我們需要具體的手段來「創建」這些解耦的物件。
Having understood the principles, we need concrete means to "create" these decoupled objects.

*   **Next Chapter**: **Creational Patterns (Factory, Builder, Singleton)**.
*   **Focus**: 我們將探討如何將物件的「創建邏輯」與「使用邏輯」分離，這是實現 DIP 與 OCP 的第一步實作。
*   **Focus**: We will explore how to separate object "creation logic" from "usage logic," which is the first practical step in implementing DIP and OCP.