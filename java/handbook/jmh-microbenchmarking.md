# JMH 微基準測試實務 / JMH Microbenchmarking in Practice

## Mental model｜心智模型

在 Java 世界裡，效能測試最大的敵人就是 **JVM 本身**。現代的 JVM 內建了極度聰明的即時編譯器（JIT Compiler），它會在執行期間動態分析程式碼，並進行激進的優化（例如：消除死代碼、常數摺疊、迴圈展開）。

如果你只用一個簡單的 `for` 迴圈搭配 `System.nanoTime()` 來測量效能，你測到的通常不是「程式碼執行的速度」，而是「JVM 發現這段程式碼沒用，把它整個刪掉的速度」。

**JMH (Java Microbenchmark Harness)** 的心智模型就是一個「**防作弊的科學實驗室**」。它透過嚴格的控制變因（預熱、狀態隔離、黑洞機制），欺騙並引導 JIT 編譯器，確保你測量的是真實的業務邏輯效能，而不是編譯器優化後的幻象。

---

In the Java ecosystem, the biggest enemy of performance testing is the **JVM itself**. Modern JVMs are equipped with incredibly smart Just-In-Time (JIT) compilers that dynamically analyze code at runtime and apply aggressive optimizations (e.g., Dead Code Elimination, Constant Folding, Loop Unrolling).

If you try to measure performance using a simple `for` loop and `System.nanoTime()`, you are rarely measuring "how fast the code runs." Instead, you are usually measuring "how fast the JVM realizes this code does nothing and deletes it."

The mental model for **JMH (Java Microbenchmark Harness)** is an "**anti-cheat scientific laboratory**." Through strict variable control (warm-ups, state isolation, blackholes), it tricks and guides the JIT compiler, ensuring you measure the actual performance of your business logic, not an illusion created by compiler optimizations.

## Patterns & best practices｜常見模式與最佳實務

### 1. 狀態隔離與注入 / State Isolation and Injection (`@State`)
不要在 `@Benchmark` 方法內初始化大型物件。使用 `@State` 標註類別，讓 JMH 在測試前準備好資料。這不僅能分離「初始化時間」與「執行時間」，還能控制多執行緒下的狀態共用範圍（`Scope.Thread` 或 `Scope.Benchmark`）。

Do not initialize large objects inside the `@Benchmark` method. Use the `@State` annotation on a class to let JMH prepare the data before the test. This separates "initialization time" from "execution time" and controls state sharing across threads (`Scope.Thread` or `Scope.Benchmark`).

### 2. 吞噬結果的黑洞 / Consuming Results with `Blackhole`
為了防止 JIT 編譯器觸發「死代碼消除（Dead Code Elimination, DCE）」，你必須讓 JVM 認為計算結果是有用的。你可以直接 `return` 計算結果，或者將結果傳遞給 `Blackhole.consume()`。

To prevent the JIT compiler from triggering Dead Code Elimination (DCE), you must convince the JVM that the computed result is used. You can either `return` the result directly from the method or pass it to `Blackhole.consume()`.

### 3. 充分的預熱 / Sufficient Warm-up (`@Warmup`)
Java 程式剛啟動時是直譯執行的，速度很慢。必須經過足夠的次數呼叫，JIT 才會將其編譯為高度優化的機器碼。永遠要設定 `@Warmup`，讓程式碼達到「穩定狀態（Steady State）」後再開始測量。

Java code runs slowly at startup because it is interpreted. It must be invoked enough times for the JIT compiler to compile it into highly optimized machine code. Always configure `@Warmup` to let the code reach a "Steady State" before actual measurement begins.

### 4. 選擇正確的測量模式 / Choosing the Right Benchmark Mode (`@BenchmarkMode`)
根據你的業務場景選擇指標：
- `Mode.Throughput`：每秒可執行的次數（適合批次處理、高併發場景）。
- `Mode.AverageTime`：每次執行的平均時間（適合延遲敏感的 API）。
- `Mode.SampleTime`：抽樣執行時間，包含最大/最小延遲分佈（適合評估 P99 延遲）。

Choose the metric based on your business scenario:
- `Mode.Throughput`: Operations per unit of time (best for batch processing, high concurrency).
- `Mode.AverageTime`: Average time per operation (best for latency-sensitive APIs).
- `Mode.SampleTime`: Samples execution time, providing max/min latency distribution (best for evaluating P99 latency).

## Anti-patterns & pitfalls｜反模式與踩雷點

### ❌ 反模式 1：常數摺疊 (Constant Folding)
**情境**：在測試方法中寫死輸入參數（例如 `int a = 10; int b = 20; return a + b;`）。
**後果**：JIT 編譯器在編譯期就會算出結果是 `30`，執行期根本沒有進行加法運算，導致測出來的效能好得不切實際。
**解法**：將輸入參數定義在 `@State` 類別中，打破常數摺疊。

**Scenario**: Hardcoding input parameters in the benchmark method (e.g., `int a = 10; int b = 20; return a + b;`).
**Consequence**: The JIT compiler calculates the result (`30`) during compilation. No addition happens at runtime, resulting in unrealistically fast performance metrics.
**Solution**: Define input parameters inside a `@State` class to defeat constant folding.

### ❌ 反模式 2：自己寫迴圈 (Loop Unrolling Trap)
**情境**：在 `@Benchmark` 方法裡面寫一個 `for (int i=0; i<1000; i++)` 來放大執行時間。
**後果**：JIT 會進行「迴圈展開（Loop Unrolling）」優化，甚至將迴圈內的邏輯向量化（Vectorization），這與實際生產環境單次呼叫的行為完全不同。
**解法**：讓 `@Benchmark` 方法只包含單次操作的邏輯，把「重複呼叫」的工作交給 JMH 框架處理。

**Scenario**: Writing a `for (int i=0; i<1000; i++)` loop inside the `@Benchmark` method to amplify execution time.
**Consequence**: The JIT compiler will apply "Loop Unrolling" or even vectorization, which behaves completely differently from a single invocation in a production environment.
**Solution**: Keep the `@Benchmark` method focused on a single operation. Let the JMH framework handle the repetitive invocations.

### ❌ 反模式 3：在 IDE 內執行最終測試 (Running Final Tests in IDE)
**情境**：直接在 IntelliJ IDEA 或 Eclipse 中點擊 "Run" 來獲取基準測試報告。
**後果**：IDE 附加的 Debugger、Profiler 或背景任務會嚴重干擾 CPU 快取與執行緒排程，導致數據抖動（Jitter）。
**解法**：永遠透過 Maven/Gradle 打包成獨立的 Uber JAR，並在安靜的終端機環境中執行。

**Scenario**: Clicking "Run" directly in IntelliJ IDEA or Eclipse to get the final benchmark report.
**Consequence**: IDE-attached debuggers, profilers, or background tasks severely interfere with CPU caches and thread scheduling, causing data jitter.
**Solution**: Always package the benchmark as a standalone Uber JAR via Maven/Gradle and run it in a quiet terminal environment.

## Checklists & workflows｜檢查清單與流程

在提交 JMH 測試報告或根據測試結果修改生產程式碼前，請確認以下事項：
Before submitting a JMH report or modifying production code based on the results, verify the following:

- [ ] **State Management**: 所有的測試輸入資料是否都宣告在 `@State` 類別中，而不是在方法內 hardcode？ / *Are all test inputs declared in a `@State` class rather than hardcoded in the method?*
- [ ] **DCE Prevention**: `@Benchmark` 方法是否有回傳值（return），或者使用了 `Blackhole.consume()`？ / *Does the `@Benchmark` method return a value, or use `Blackhole.consume()`?*
- [ ] **Warm-up**: 是否設定了至少 3-5 次的 `@Warmup` 迭代？ / *Are there at least 3-5 `@Warmup` iterations configured?*
- [ ] **Environment**: 執行測試的機器是否處於「安靜狀態」（關閉瀏覽器、通訊軟體、不相關的 Docker 容器）？ / *Is the test machine in a "quiet state" (browsers, chat apps, and unrelated Docker containers closed)?*
- [ ] **Execution**: 最終數據是否來自命令列執行的 Uber JAR（`java -jar target/benchmarks.jar`），而非 IDE？ / *Are the final metrics generated from a command-line Uber JAR execution (`java -jar target/benchmarks.jar`) rather than an IDE?*
- [ ] **Sanity Check**: 測試結果的數量級是否合理？（如果一個複雜字串操作顯示只需要 0.001 奈秒，通常代表代碼被 JIT 消除掉了）。 / *Is the magnitude of the result logical? (If a complex string operation takes 0.001 nanoseconds, it usually means the code was eliminated by JIT).*

## Real-world examples｜實戰案例

以下是一個真實世界常見的場景：**比較字串串接的效能**。這個範例展示了如何正確使用 `@State`、`@Setup`、`Blackhole` 以及避免死代碼消除。

Below is a common real-world scenario: **Comparing String concatenation performance**. This example demonstrates the correct use of `@State`, `@Setup`, `Blackhole`, and how to avoid dead code elimination.

```java
import org.openjdk.jmh.annotations.*;
import org.openjdk.jmh.infra.Blackhole;

import java.util.concurrent.TimeUnit;

// 1. 設定測量模式為吞吐量 (每秒操作次數)
// 1. Set benchmark mode to Throughput (operations per second)
@BenchmarkMode(Mode.Throughput)
@OutputTimeUnit(TimeUnit.MILLISECONDS)
// 2. 設定預熱與正式測量的迭代次數
// 2. Configure warmup and measurement iterations
@Warmup(iterations = 3, time = 1)
@Measurement(iterations = 5, time = 1)
@Fork(1) // 啟動一個獨立的 JVM 行程進行測試 / Fork a separate JVM process for testing
// 3. 宣告狀態範圍，確保變數不會被常數摺疊
// 3. Declare state scope to prevent constant folding
@State(Scope.Thread)
public class StringConcatenationBenchmark {

    private String prefix;
    private String suffix;
    private int number;

    @Setup(Level.Trial)
    public void setup() {
        // 在測試開始前初始化資料，這段時間不計入效能測量
        // Initialize data before the trial starts; this time is not measured
        prefix = "User_";
        suffix = "_ID";
        number = 42;
    }

    // ❌ 反模式演示 (Anti-pattern Demo)
    // JIT 可能會發現結果沒被使用，直接把整段邏輯刪除 (DCE)
    // JIT might realize the result is unused and delete the logic entirely (DCE)
    @Benchmark
    public void badBenchmark() {
        String result = prefix + number + suffix;
    }

    // ✅ 最佳實踐 1：直接回傳結果
    // ✅ Best Practice 1: Return the result directly
    @Benchmark
    public String goodBenchmarkWithReturn() {
        return prefix + number + suffix;
    }

    // ✅ 最佳實踐 2：使用 StringBuilder 並將結果餵給 Blackhole
    // ✅ Best Practice 2: Use StringBuilder and feed the result to a Blackhole
    @Benchmark
    public void stringBuilderBenchmark(Blackhole blackhole) {
        StringBuilder sb = new StringBuilder();
        sb.append(prefix).append(number).append(suffix);
        
        // 強迫 JVM 認為這個結果是有用的，防止優化掉 StringBuilder 的操作
        // Force the JVM to think this result is useful, preventing optimization of StringBuilder operations
        blackhole.consume(sb.toString());
    }
}
```

**執行方式 / How to run:**
```bash
# 1. 透過 Maven 打包 (產生包含 JMH 依賴的 Uber JAR)
# 1. Package via Maven (generates an Uber JAR with JMH dependencies)
mvn clean verify

# 2. 在終端機執行 (可加上正則表達式過濾特定測試)
# 2. Run in terminal (regex can be added to filter specific tests)
java -jar target/benchmarks.jar StringConcatenationBenchmark
```