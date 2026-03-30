## 1. 前言與學習目標
## 1. Introduction & Learning Objectives

身為資深工程師，我們對 Java 的認知不能僅停留在「如何使用語法」，而必須深入理解語言演進背後的設計哲學與底層實作。Java 從 8 到 21+ 的演進，不僅僅是語法糖的增加，更是從純粹的物件導向程式設計（OOP）向「資料導向程式設計（Data-Oriented Programming, DOP）」與「函數式思維」的典範轉移。
As a senior engineer, our understanding of Java must go beyond "how to use the syntax" to deeply comprehending the design philosophy and underlying implementations behind the language's evolution. The evolution of Java from 8 to 21+ is not merely the addition of syntactic sugar, but a paradigm shift from pure Object-Oriented Programming (OOP) towards "Data-Oriented Programming (DOP)" and functional thinking.

完成本章後，你應該能做到以下幾點：
After completing this chapter, you should be able to:

*   **精通現代 Java 核心特性**：熟練運用 Records、Sealed Classes 與 Pattern Matching，並能解釋它們如何提升領域驅動設計（DDD）的強健性。
    **Master Modern Java Core Features**: Proficiently utilize Records, Sealed Classes, and Pattern Matching, and explain how they enhance the robustness of Domain-Driven Design (DDD).
*   **透析 Collection 底層機制**：精確描述 `HashMap` 與 `ConcurrentHashMap` 在 Java 8+ 的結構變化（如 Treeification 與 CAS 機制），並能在高併發場景下做出正確的資料結構選型。
    **Deconstruct Collection Internals**: Accurately describe the structural changes of `HashMap` and `ConcurrentHashMap` in Java 8+ (e.g., Treeification and CAS mechanisms), and make correct data structure selections in high-concurrency scenarios.
*   **掌握 Stream API 的效能邊界**：理解 Stream 的延遲執行（Lazy Evaluation）與 Spliterator 原理，並能避開 Parallel Stream 帶來的隱藏效能陷阱。
    **Grasp the Performance Boundaries of Stream API**: Understand Stream's lazy evaluation and Spliterator principles, and avoid the hidden performance pitfalls brought by Parallel Streams.

---

## 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 資料導向程式設計 (Data-Oriented Programming, DOP)
### Data-Oriented Programming (DOP)

在傳統 OOP 中，我們習慣將狀態（State）隱藏在行為（Behavior）之後；但在現代分散式系統中，我們經常需要在微服務之間傳遞不可變的資料。Java 引入的 Records、Sealed Classes 與 Pattern Matching，正是為了支援 DOP。
In traditional OOP, we are accustomed to hiding state behind behavior; however, in modern distributed systems, we frequently need to pass immutable data between microservices. The introduction of Records, Sealed Classes, and Pattern Matching in Java is precisely to support DOP.

*   **Records (Java 14+)**：可以類比為 C# 的 `record` 或 Scala 的 `case class`。它們是透明且不可變的資料載體（Immutable Data Carriers）。心智模型：將其視為「只包含資料的純粹值（Value Object）」，編譯器會自動生成 `equals()`, `hashCode()` 與 `toString()`。
    **Records (Java 14+)**: Can be compared to C#'s `record` or Scala's `case class`. They are transparent and immutable data carriers. Mental model: Treat them as "pure values containing only data (Value Objects)"; the compiler automatically generates `equals()`, `hashCode()`, and `toString()`.
*   **Sealed Classes (Java 15+)**：提供了代數資料型別（Algebraic Data Types, ADT）中的「和型別（Sum Types）」。它限制了哪些類別可以繼承它。心智模型：這是一個「封閉的宇宙」，讓編譯器知道所有可能的子型別，這與 TypeScript 中的 Union Types (`type A = B | C`) 在概念上非常相似。
    **Sealed Classes (Java 15+)**: Provide "Sum Types" from Algebraic Data Types (ADT). It restricts which classes can extend it. Mental model: This is a "closed universe" that lets the compiler know all possible subtypes, conceptually very similar to Union Types in TypeScript (`type A = B | C`).
*   **Pattern Matching (Java 16/21+)**：結合 `switch` 表達式，它允許我們直接對資料結構進行解構（Destructuring）。
    **Pattern Matching (Java 16/21+)**: Combined with `switch` expressions, it allows us to destructure data structures directly.

### 集合與 Stream 的底層心智模型
### Mental Model of Collections and Streams

*   **HashMap 的演進**：從單純的「陣列 + 鏈結串列（Array + LinkedList）」演進為「陣列 + 鏈結串列 / 紅黑樹（Red-Black Tree）」。當 Hash 碰撞嚴重（同一個 bucket 節點數達到 8）時，鏈結串列會轉換為紅黑樹，將最壞時間複雜度從 $O(n)$ 降至 $O(\log n)$。
    **Evolution of HashMap**: Evolved from a simple "Array + LinkedList" to "Array + LinkedList / Red-Black Tree". When hash collisions are severe (node count in the same bucket reaches 8), the linked list treeifies into a Red-Black tree, reducing the worst-case time complexity from $O(n)$ to $O(\log n)$.
*   **Stream 的管線化（Pipeline）**：心智模型應視為「帶有閥門的水管」。中間操作（Intermediate Operations，如 `filter`, `map`）只是設定閥門的條件，**不會**觸發水流；直到終端操作（Terminal Operation，如 `collect`, `findFirst`）被呼叫時，資料才會以「深度優先（Depth-First）」的方式流過管線，這就是延遲評估（Lazy Evaluation）。
    **Stream Pipelining**: The mental model should be viewed as "water pipes with valves". Intermediate operations (like `filter`, `map`) only set the conditions of the valves and **do not** trigger the water flow; data only flows through the pipeline in a "Depth-First" manner when a terminal operation (like `collect`, `findFirst`) is invoked. This is Lazy Evaluation.

---

## 3. 實務場景與系統設計視角 (Real-World & System Design View)

在 Production 環境與系統架構中，現代 Java 特性對系統的非功能性需求（Non-Functional Requirements）有著深遠的影響：
In production environments and system architectures, modern Java features have a profound impact on the system's Non-Functional Requirements (NFRs):

### 領域驅動設計與可維護性 (DDD & Maintainability)
### Domain-Driven Design & Maintainability

在實作 DDD 的 Domain Events 或 CQRS 的 Commands 時，使用 `Sealed Interface` 加上 `Record` 是目前的 Best Practice。它保證了事件型別的窮舉性。當未來系統需要新增一種 Event 時，編譯器會強迫你在所有的 `switch` 區塊中處理這個新 Event，從根本上消除了「忘記處理新狀態」的 Runtime Bug。
When implementing Domain Events in DDD or Commands in CQRS, using `Sealed Interface` combined with `Record` is the current Best Practice. It guarantees the exhaustiveness of event types. When the system needs to add a new Event in the future, the compiler will force you to handle this new Event in all `switch` blocks, fundamentally eliminating the runtime bug of "forgetting to handle a new state".

### 併發與效能 (Concurrency & Performance)
### Concurrency & Performance

不可變性（Immutability）是高併發系統的基石。大量使用 Records 作為 DTO（Data Transfer Objects）或快取資料，可以完全免除執行緒同步（Synchronization）的開銷。
Immutability is the cornerstone of high-concurrency systems. Heavily using Records as DTOs (Data Transfer Objects) or cached data can completely eliminate the overhead of thread synchronization.

對於 `ConcurrentHashMap`，Java 8 移除了 Segment Lock（分段鎖），改用 `CAS (Compare-And-Swap)` 與針對單一 Node 頭節點的 `synchronized`。這表示在分散式快取本地化（Local Cache）的場景中，寫入衝突的粒度被降到了最低，極大地提升了吞吐量。
For `ConcurrentHashMap`, Java 8 removed Segment Locks and switched to `CAS (Compare-And-Swap)` along with `synchronized` on the head of a single Node. This means in scenarios of localizing distributed caches (Local Cache), the granularity of write conflicts is minimized, drastically improving throughput.

---

## 4. 逐步示例 (Walkthrough / Example)

### 場景：重構支付處理模組 (Scenario: Refactoring a Payment Processing Module)

**問題背景 (Business Context)**：
一個電商系統需要處理多種支付方式（信用卡、PayPal、加密貨幣）。舊有的 Java 8 程式碼使用了大量的 `instanceof` 與強制轉型，且容易在新增支付方式時遺漏處理邏輯。
An e-commerce system needs to process multiple payment methods (Credit Card, PayPal, Crypto). The legacy Java 8 code uses a lot of `instanceof` and casting, and is prone to missing handling logic when a new payment method is added.

**Step 1: 舊有做法 (Naive Approach - Java 8)**
**Step 1: Naive Approach (Java 8)**

```java
// Legacy Java 8 approach
public interface Payment {}
public class CreditCard implements Payment { /* getters/setters */ }
public class PayPal implements Payment { /* getters/setters */ }

public void process(Payment payment) {
    if (payment instanceof CreditCard) {
        CreditCard cc = (CreditCard) payment;
        // process CC
    } else if (payment instanceof PayPal) {
        PayPal pp = (PayPal) payment;
        // process PayPal
    } else {
        throw new IllegalArgumentException("Unknown payment type"); // Runtime risk!
    }
}
```

**Step 2: 現代化重構 (Modern Solution - Java 21+)**
**Step 2: Modern Solution (Java 21+)**

我們利用 `sealed` 介面定義支付方式的邊界，並用 `record` 宣告不可變的資料載體，最後用 Pattern Matching for `switch` 進行處理。
We use a `sealed` interface to define the boundaries of payment methods, `record` to declare immutable data carriers, and finally Pattern Matching for `switch` to process them.

```java
// 1. Define a closed hierarchy using sealed interface
public sealed interface Payment permits CreditCard, PayPal, Crypto {}

// 2. Use records for immutable data carriers
public record CreditCard(String cardNumber, String expDate) implements Payment {}
public record PayPal(String email) implements Payment {}
public record Crypto(String walletAddress, String network) implements Payment {}

// 3. Pattern Matching with switch (Java 21)
public void process(Payment payment) {
    // The compiler enforces exhaustiveness. No 'default' branch is needed!
    // If we add a new Payment type later, this code will fail to compile until updated.
    switch (payment) {
        case CreditCard cc -> processCreditCard(cc.cardNumber());
        case PayPal pp     -> processPayPal(pp.email());
        case Crypto c      -> processCrypto(c.walletAddress(), c.network());
    };
}
```

**為何這個做法更好？ (Why is this better?)**
1.  **編譯期安全 (Compile-time Safety)**：`switch` 是窮舉的（Exhaustive）。如果未來新增了 `ApplePay` 但沒有在這裡處理，程式將無法編譯。
    **Compile-time Safety**: The `switch` is exhaustive. If `ApplePay` is added in the future but not handled here, the code will not compile.
2.  **減少樣板程式碼 (Reduced Boilerplate)**：`record` 自動處理了建構子與資料存取，且 Pattern Matching 直接完成了型別檢查與變數綁定（Destructuring），時間複雜度為 $O(1)$ 的型別分派。
    **Reduced Boilerplate**: `record` automatically handles constructors and data access, and Pattern Matching directly completes type checking and variable binding (Destructuring), providing $O(1)$ type dispatching.

---

## 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 坑 1：濫用 Parallel Stream (Misusing Parallel Streams)
*   **錯誤案例**：在處理少量資料或包含 I/O 操作（如呼叫外部 API、資料庫查詢）的 Stream 上使用 `.parallel()`。
    **Anti-pattern**: Using `.parallel()` on streams processing small datasets or containing I/O operations (like external API calls, DB queries).
*   **為何不好**：Parallel Stream 預設共用 JVM 全局的 `ForkJoinPool.commonPool()`。如果其中一個 Parallel Stream 阻塞在 I/O 上，會耗盡整個 Pool 的執行緒，導致系統中其他使用 Parallel Stream 的地方全部卡死（Thread Starvation）。
    **Why it's bad**: Parallel Streams share the JVM's global `ForkJoinPool.commonPool()` by default. If one Parallel Stream blocks on I/O, it exhausts the threads in the entire pool, causing all other places in the system using Parallel Streams to freeze (Thread Starvation).
*   **較佳方案**：Parallel Stream 僅適用於**大量資料**且為**純 CPU 密集型**的計算。對於 I/O 密集型任務，應使用非同步框架（如 `CompletableFuture` 並指定獨立的 Thread Pool）或 Java 21 的 Virtual Threads。
    **Better Alternative**: Parallel Streams are only suitable for **large datasets** and **purely CPU-bound** computations. For I/O-bound tasks, use asynchronous frameworks (like `CompletableFuture` with a dedicated Thread Pool) or Java 21's Virtual Threads.

### 坑 2：在 Stream 中修改外部狀態 (Modifying External State in Streams)
*   **錯誤案例**：在 `forEach` 或 `map` 中，將資料 `add` 到外部的 `ArrayList` 中。
    **Anti-pattern**: Adding data to an external `ArrayList` inside a `forEach` or `map` operation.
*   **為何不好**：這破壞了函數式程式設計的無副作用（Side-effect free）原則。如果未來將 Stream 改為 Parallel，會立刻引發 `ConcurrentModificationException` 或資料遺失。
    **Why it's bad**: This violates the side-effect-free principle of functional programming. If the Stream is later changed to Parallel, it will immediately trigger a `ConcurrentModificationException` or data loss.
*   **較佳方案**：永遠使用 `Collectors`（如 `.collect(Collectors.toList())`）來聚合結果。
    **Better Alternative**: Always use `Collectors` (e.g., `.collect(Collectors.toList())`) to aggregate results.

### 坑 3：JPA Entity 誤用 Record (Misusing Records for JPA Entities)
*   **錯誤案例**：將 Hibernate / JPA 的 `@Entity` 宣告為 `record`。
    **Anti-pattern**: Declaring Hibernate / JPA `@Entity` as a `record`.
*   **為何不好**：JPA 規範要求 Entity 必須有預設建構子（No-arg constructor）且為可變的（Mutable），因為 Hibernate 底層依賴 CGLIB/ByteBuddy 建立 Proxy 子類別來實現 Lazy Loading。Record 是 `final` 且不可變的，完全與 JPA 生命週期衝突。
    **Why it's bad**: The JPA specification requires Entities to have a no-arg constructor and be mutable, because Hibernate relies on CGLIB/ByteBuddy to create Proxy subclasses for Lazy Loading. Records are `final` and immutable, completely conflicting with the JPA lifecycle.
*   **較佳方案**：Entity 保持為一般的 `class`，但可以將查詢結果（Projections）或 DTO 宣告為 `record`。
    **Better Alternative**: Keep Entities as regular `class`es, but declare query results (Projections) or DTOs as `record`s.

---

## 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

身為面試官，我通常會透過以下問題來鑑別候選人是「只會寫 Code」還是「真正理解底層與架構」：
As an interviewer, I typically use the following questions to distinguish whether a candidate "just writes code" or "truly understands the internals and architecture":

*   **Q1: 「請解釋 Java 8 之後 HashMap 的實作改變？為什麼要引入紅黑樹而不是 AVL 樹？」**
    **"Explain the implementation changes in HashMap since Java 8. Why introduce a Red-Black Tree instead of an AVL Tree?"**
    *   *高分要點*：提到 Hash 碰撞導致 LinkedList 退化成 $O(n)$ 的問題。說明 Treeification 的閾值（8）與 Untreeification 的閾值（6）。解釋紅黑樹是「弱平衡樹」，在插入/刪除時的旋轉次數少於嚴格平衡的 AVL 樹，更適合 HashMap 這種頻繁寫入的場景。
        *High-score points*: Mention the issue of Hash collisions degrading LinkedLists to $O(n)$. Explain the Treeification threshold (8) and Untreeification threshold (6). Explain that a Red-Black Tree is a "weakly balanced tree", requiring fewer rotations during insertion/deletion than a strictly balanced AVL tree, making it more suitable for HashMap's frequent write scenarios.

*   **Q2: 「ConcurrentHashMap 在 Java 8 中是如何實現高併發的？與 Java 7 有何不同？」**
    **"How does ConcurrentHashMap achieve high concurrency in Java 8? How does it differ from Java 7?"**
    *   *高分要點*：指出 Java 7 使用 `Segment` 陣列（分段鎖），鎖的粒度較粗。Java 8 移除了 `Segment`，直接使用 Node 陣列，並利用 `CAS` 操作插入新節點；若發生碰撞，則只對該 bucket 的頭節點（Head Node）加上 `synchronized` 鎖。鎖的粒度降到了單一 bucket，大幅提升併發度。
        *High-score points*: Point out that Java 7 uses an array of `Segment`s (lock striping) with coarser lock granularity. Java 8 removed `Segment`s, directly using a Node array and utilizing `CAS` operations to insert new nodes; if a collision occurs, it only applies a `synchronized` lock on the Head Node of that bucket. The lock granularity is reduced to a single bucket, significantly boosting concurrency.

*   **Q3: 「如果在大型單體系統中逐步導入 Java 17/21 的新特性，你會如何拆解步驟？」**
    **"If you were to gradually introduce Java 17/21 new features into a large monolithic system, how would you break down the steps?"**
    *   *高分要點*：展現架構師思維。第一步：升級 JDK 運行環境（Runtime），享受 ZGC 或 G1 的效能紅利，程式碼保持不變。第二步：在邊界層（Controller DTOs, API Responses）引入 `Record` 替換 Lombok。第三步：在核心業務邏輯（Domain Layer）重構複雜的條件判斷，引入 `Sealed Classes` 與 Pattern Matching 強化領域模型。
        *High-score points*: Demonstrate architect thinking. Step 1: Upgrade the JDK Runtime to enjoy performance dividends from ZGC or G1, keeping code unchanged. Step 2: Introduce `Record`s at the boundary layers (Controller DTOs, API Responses) to replace Lombok. Step 3: Refactor complex conditionals in the core business logic (Domain Layer), introducing `Sealed Classes` and Pattern Matching to strengthen the domain model.

---

## 7. 小結與後續延伸 (Summary & Next Steps)

**本章記憶錨點 (Memory Anchors)：**
**Chapter Memory Anchors:**
1.  **DOP 典範轉移**：Records (不可變資料) + Sealed Classes (封閉型別) + Pattern Matching (解構) = 現代 Java 領域建模的黃金三角。
    **DOP Paradigm Shift**: Records (Immutable Data) + Sealed Classes (Closed Types) + Pattern Matching (Destructuring) = The Golden Triangle of modern Java domain modeling.
2.  **HashMap 底層**：陣列 + 鏈結串列 + 紅黑樹。碰撞閾值 8 轉樹，6 退化為鏈結串列。
    **HashMap Internals**: Array + LinkedList + Red-Black Tree. Collision threshold 8 for treeification, 6 for untreeification.
3.  **ConcurrentHashMap 併發機制**：Java 8+ 捨棄分段鎖，改用 `CAS` + `synchronized` 鎖定頭節點，鎖粒度最小化。
    **ConcurrentHashMap Concurrency**: Java 8+ abandons segment locks in favor of `CAS` + `synchronized` on the head node, minimizing lock granularity.
4.  **Stream 延遲評估**：中間操作不執行，終端操作才觸發深度優先的資料流。
    **Stream Lazy Evaluation**: Intermediate operations do not execute; terminal operations trigger depth-first data flow.
5.  **Parallel Stream 陷阱**：預設共用 `commonPool`，絕對不要在其中執行 I/O 阻塞操作。
    **Parallel Stream Pitfall**: Shares the `commonPool` by default; absolutely never execute I/O blocking operations within it.

**後續延伸 (Next Steps)：**
**Next Steps:**
*   掌握了現代 Java 的資料結構與 API 後，下一步應深入探討 **Java 併發模型與 Virtual Threads (Project Loom)**。理解 Virtual Threads 如何以極低的成本取代傳統的 Thread-per-request 模型，徹底改變 I/O 密集型應用的架構設計。
    After mastering modern Java data structures and APIs, the next step is to dive deep into the **Java Concurrency Model and Virtual Threads (Project Loom)**. Understand how Virtual Threads replace the traditional Thread-per-request model at a fraction of the cost, revolutionizing the architectural design of I/O-bound applications.
*   探索 **JVM 記憶體模型與垃圾回收器（如 ZGC, Shenandoah）**，這對於發揮現代 Java 應用的極致效能至關重要。
    Explore the **JVM Memory Model and Garbage Collectors (e.g., ZGC, Shenandoah)**, which is crucial for maximizing the performance of modern Java applications.