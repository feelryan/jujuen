# Streams API 最佳實踐與效能陷阱 / Streams API Best Practices and Performance Pitfalls

## Mental model｜心智模型

想像 Streams 是一條**工廠流水線（Assembly Line）**，而不是儲存資料的倉庫。資料從來源進入，經過一系列的加工站（中間操作 Intermediate Operations，如 `filter`, `map`），最後在包裝站（終端操作 Terminal Operations，如 `collect`, `reduce`）產出結果。
Think of Streams as a **factory assembly line**, not a warehouse for storing data. Data enters from a source, passes through processing stations (Intermediate Operations like `filter`, `map`), and is finally assembled at the packaging station (Terminal Operations like `collect`, `reduce`).

掌握 Streams 的三個核心心智模型：
Master the three core mental models of Streams:

1. **延遲執行 (Lazy Evaluation)**：在呼叫終端操作（如 `collect` 或 `count`）之前，中間的 `filter` 或 `map` 完全不會執行。這就像是先畫好流水線的設計圖，直到按下啟動按鈕才開始運作。
   **Lazy Evaluation**: Intermediate operations (`filter`, `map`) are not executed until a terminal operation (`collect`, `count`) is invoked. It’s like drawing the blueprint of the assembly line first, and nothing moves until you press the start button.
2. **一次性消耗 (Single-use)**：Stream 就像水流，流過去就沒了。你不能對同一個 Stream 物件呼叫兩次終端操作。
   **Single-use**: A Stream is like flowing water; once it passes, it's gone. You cannot invoke terminal operations twice on the same Stream instance.
3. **宣告式編程 (Declarative Programming)**：你告訴程式「要做什麼 (What)」，而不是「怎麼做 (How)」。底層的迭代邏輯交由 JVM 最佳化。
   **Declarative Programming**: You tell the program "What to do" instead of "How to do it". The underlying iteration logic is left to the JVM to optimize.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 優先使用 Primitive Streams 避免裝箱成本 / Prefer Primitive Streams to Avoid Boxing Costs
在處理大量數值運算時，`Stream<Integer>` 會產生大量的物件建立與垃圾回收（GC）開銷。請使用 `IntStream`, `LongStream`, `DoubleStream`。
When processing large amounts of numerical data, `Stream<Integer>` generates massive object creation and Garbage Collection (GC) overhead. Use `IntStream`, `LongStream`, and `DoubleStream` instead.

```java
// ❌ Anti-pattern: Unnecessary boxing/unboxing
int sum = users.stream()
               .map(User::getAge) // Returns Stream<Integer>
               .reduce(0, Integer::sum);

// ✅ Best Practice: Use mapToInt
int sum = users.stream()
               .mapToInt(User::getAge) // Returns IntStream
               .sum();
```

### 2. 善用進階收集器 (Advanced Collectors) / Leverage Advanced Collectors
不要在 `forEach` 裡面手動 put 資料到 Map，應該使用 `Collectors.groupingBy` 或 `Collectors.toMap`。
Do not manually put data into a Map inside a `forEach` loop. Instead, use `Collectors.groupingBy` or `Collectors.toMap`.

```java
// ✅ Best Practice: Grouping and downstream collectors
Map<Department, Long> countByDept = employees.stream()
    .collect(Collectors.groupingBy(
        Employee::getDepartment, 
        Collectors.counting() // Downstream collector
    ));
```

### 3. 使用方法引用提升可讀性 / Use Method References for Readability
當 Lambda 表達式只是單純呼叫一個現有方法時，替換為方法引用（Method Reference）。
When a Lambda expression simply calls an existing method, replace it with a Method Reference.

```java
// ❌ Less readable
users.stream().filter(u -> u.isActive()).map(u -> u.getName()).toList();

// ✅ Best Practice
users.stream().filter(User::isActive).map(User::getName).toList();
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 濫用平行流 (The `parallelStream()` Trap)
這是最致命的效能陷阱。`parallelStream()` 預設共用 JVM 全局的 `ForkJoinPool.commonPool()`。如果你在平行流中執行**阻塞型 I/O**（如打 API、查 DB），會耗盡整個 Thread Pool，導致應用程式其他部分的平行流或非同步任務全部卡死。
This is the most fatal performance trap. `parallelStream()` shares the JVM's global `ForkJoinPool.commonPool()` by default. If you perform **blocking I/O** (e.g., HTTP calls, DB queries) inside a parallel stream, it will exhaust the entire thread pool, starving all other parallel streams or async tasks in the application.

*   **Rule of thumb**: 只有在「資料量極大」且「純 CPU 密集型運算」時才使用 `parallelStream()`。遇到 I/O 任務，請改用 `CompletableFuture`。
*   **Rule of thumb**: Use `parallelStream()` ONLY for "massive datasets" with "pure CPU-intensive computations". For I/O tasks, use `CompletableFuture` instead.

### 2. 在 Stream 中產生副作用 (Side-effects in Streams)
Stream 的操作應該是無狀態（Stateless）且純粹（Pure）的。在 `forEach` 或 `map` 中修改外部變數，不僅破壞了函數式編程的原則，在平行處理時更會引發 Thread-safety 問題。
Stream operations should be stateless and pure. Modifying external variables inside `forEach` or `map` not only violates functional programming principles but also causes thread-safety issues during parallel processing.

```java
// ❌ Anti-pattern: Modifying external state (Side-effect)
List<String> activeNames = new ArrayList<>();
users.stream()
     .filter(User::isActive)
     .forEach(u -> activeNames.add(u.getName())); // Not thread-safe!

// ✅ Best Practice: Collect the results
List<String> activeNames = users.stream()
     .filter(User::isActive)
     .map(User::getName)
     .toList(); // Thread-safe and declarative
```

### 3. `Collectors.toMap` 的 Key 衝突陷阱 / Duplicate Keys Trap in `Collectors.toMap`
當使用 `toMap` 時，如果來源資料有重複的 Key，預設會拋出 `IllegalStateException`。
When using `toMap`, if the source data contains duplicate keys, it throws an `IllegalStateException` by default.

```java
// ❌ Pitfall: Throws exception if two users have the same ID
Map<String, User> userMap = users.stream()
    .collect(Collectors.toMap(User::getId, Function.identity()));

// ✅ Fix: Provide a merge function to resolve conflicts
Map<String, User> userMap = users.stream()
    .collect(Collectors.toMap(
        User::getId, 
        Function.identity(),
        (existing, replacement) -> existing // Keep the first one on conflict
    ));
```

---

## Checklists & workflows｜檢查清單與流程

在 Code Review 時，請用以下清單檢查 Streams API 的使用：
During Code Review, use the following checklist to verify Streams API usage:

- [ ] **無狀態驗證 (Statelessness)**：Stream 內部（如 `map`, `filter`, `forEach`）是否修改了外部變數？如果是，請重構為 `collect` 或 `reduce`。
  **Statelessness**: Do stream operations (`map`, `filter`, `forEach`) modify external variables? If yes, refactor using `collect` or `reduce`.
- [ ] **避免裝箱 (Avoid Boxing)**：是否對大量的整數/浮點數使用了 `Stream<Integer>`？請替換為 `IntStream` 等 Primitive Streams。
  **Avoid Boxing**: Are you using `Stream<Integer>` for large amounts of numbers? Replace with primitive streams like `IntStream`.
- [ ] **Map 衝突處理 (Map Conflict Handling)**：使用 `Collectors.toMap` 時，是否已經考慮了 Key 重複的可能性並提供了 Merge Function？
  **Map Conflict Handling**: When using `Collectors.toMap`, have you considered duplicate keys and provided a Merge Function?
- [ ] **平行流決策 (Parallel Stream Decision)**：
  - 是否使用了 `parallelStream()`？ (Did you use `parallelStream()`?)
  - 任務是否包含 I/O 操作（DB, HTTP）？如果是 ➔ **絕對不要用**。 (Does it contain I/O? If yes ➔ **DO NOT USE**.)
  - 資料量是否大於 10,000 筆且為 CPU 密集運算？如果否 ➔ **改回循序流 (`stream()`)**，因為 Thread Context Switch 的成本可能高於平行化收益。 (Is the dataset > 10,000 and CPU-intensive? If no ➔ **Revert to sequential `stream()`**, as thread context switch overhead might outweigh parallel benefits.)

---

## Real-world examples｜實戰案例

### 案例 1：複雜的分組與資料轉換 / Complex Grouping and Transformation
**情境**：我們有一批訂單，需要依據「客戶 ID」進行分組，並計算每個客戶的「總消費金額」。
**Scenario**: We have a list of orders. We need to group them by "Customer ID" and calculate the "Total Spend" for each customer.

```java
public record Order(String customerId, BigDecimal amount) {}

public Map<String, BigDecimal> calculateTotalSpendPerCustomer(List<Order> orders) {
    return orders.stream()
        .collect(Collectors.groupingBy(
            Order::customerId,
            // Downstream collector: mapping and reducing
            Collectors.mapping(
                Order::amount,
                Collectors.reducing(BigDecimal.ZERO, BigDecimal::add)
            )
        ));
}
```

### 案例 2：平行流的 I/O 災難與解法 / The Parallel Stream I/O Disaster and Solution
**情境**：需要發送 100 封 Email。開發者為了加速，使用了 `parallelStream()`。
**Scenario**: Need to send 100 emails. The developer used `parallelStream()` to speed it up.

```java
// ❌ 災難級寫法 (Disaster pattern)
// 這會佔用 ForkJoinPool.commonPool()，導致系統其他依賴該 Pool 的功能全部卡住
// This blocks ForkJoinPool.commonPool(), freezing other system features relying on it.
users.parallelStream().forEach(user -> emailService.send(user.getEmail()));

// ✅ 實戰解法 (Real-world solution)
// 針對 I/O 密集型任務，應使用自訂 Thread Pool 搭配 CompletableFuture
// For I/O intensive tasks, use a custom Thread Pool with CompletableFuture.
ExecutorService emailExecutor = Executors.newFixedThreadPool(20);

List<CompletableFuture<Void>> futures = users.stream()
    .map(user -> CompletableFuture.runAsync(
        () -> emailService.send(user.getEmail()), 
        emailExecutor
    ))
    .toList();

// 等待所有 Email 發送完畢 / Wait for all emails to be sent
CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();
```