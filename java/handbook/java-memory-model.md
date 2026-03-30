# Java 記憶體模型 (JMM) 核心概念 / Java Memory Model (JMM) Core Concepts

## Mental model｜心智模型

在多執行緒的環境下，不要把記憶體想像成一塊單一的、所有執行緒都能即時看到全貌的黑板。相反地，**你應該把 Java 記憶體模型 (JMM) 想像成一個「分散式系統」**。
In a multithreaded environment, do not think of memory as a single chalkboard where all threads can instantly see the whole picture. Instead, **you should mentalize the Java Memory Model (JMM) as a "distributed system" within your CPU.**

每個執行緒都有自己的「本地快取」（Working Memory，對應到 CPU L1/L2 Cache 與暫存器），而所有執行緒共用一個「主記憶體」（Main Memory）。JMM 是一組規則（合約），定義了執行緒的本地快取何時必須與主記憶體同步。
Each thread has its own "local cache" (Working Memory, mapping to CPU L1/L2 caches and registers), while all threads share a "Main Memory". The JMM is a set of rules (a contract) defining when a thread's local cache must synchronize with the main memory.

要駕馭 JMM，你只需要深刻理解三個核心維度（The Big Three）：
To master the JMM, you only need a deep understanding of three core dimensions (The Big Three):

1. **可見性 (Visibility)**：當執行緒 A 修改了共享變數，執行緒 B 何時能看到？（如果沒有同步機制，B 可能永遠讀取自己快取中的舊值）。
   **Visibility**: When Thread A modifies a shared variable, when does Thread B see it? (Without synchronization, B might read stale data from its own cache forever).
2. **原子性 (Atomicity)**：一個操作是否不可分割？例如 `count++` 其實包含「讀取、加一、寫回」三個步驟，它**不是**原子操作。
   **Atomicity**: Is an operation indivisible? For example, `count++` actually involves three steps: "read, increment, write back". It is **not** an atomic operation.
3. **有序性 (Ordering / Instruction Reordering)**：為了效能，編譯器與 CPU 會打亂程式碼的執行順序。JMM 透過 `Happens-Before` 原則來限制重排，確保程式邏輯的正確性。
   **Ordering / Instruction Reordering**: For performance, compilers and CPUs reorder instructions. The JMM uses the `Happens-Before` principle to restrict reordering and ensure logical correctness.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 狀態標記模式 (The State Flag Pattern)
當你需要一個開關來控制執行緒（例如優雅關閉、取消任務）時，使用 `volatile boolean`。`volatile` 保證了**可見性**，一旦某個執行緒將其設為 `true`，其他執行緒會立刻看到。
When you need a switch to control a thread (e.g., graceful shutdown, task cancellation), use a `volatile boolean`. `volatile` guarantees **visibility**; once a thread sets it to `true`, other threads will see it immediately.

### 2. 安全發佈與不可變性 (Safe Publication with Immutability)
利用 `final` 關鍵字。JMM 對 `final` 欄位有特殊的保證：只要物件在建構子中沒有發生「this 逸出 (this escape)」，其他執行緒一旦看到這個物件的參考，就一定能看到其 `final` 欄位的正確初始化值。
Leverage the `final` keyword. The JMM provides special guarantees for `final` fields: as long as the object doesn't suffer from "this escape" during construction, any thread that sees the object reference is guaranteed to see the correctly initialized values of its `final` fields.

### 3. 雙重檢查鎖定 (Double-Checked Locking, DCL)
在實作 Lazy Initialization 的 Singleton 時，必須將實例變數宣告為 `volatile`。這不僅是為了可見性，更是為了**禁止指令重排 (preventing instruction reordering)**，防止其他執行緒拿到一個「尚未初始化完成」的半成品物件。
When implementing Lazy Initialization for a Singleton, the instance variable must be declared as `volatile`. This is not just for visibility, but crucially for **preventing instruction reordering**, ensuring other threads do not get a "partially constructed" object.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### ❌ 誤以為 `volatile` 具備原子性 (Assuming `volatile` implies atomicity)
最常見的致命錯誤是寫出 `volatile int count = 0;` 然後多執行緒呼叫 `count++`。`volatile` 只能保證你讀到的是最新值，但無法防止多執行緒同時讀取同一個值並各自加一，導致更新遺失 (Lost Update)。
The most common fatal mistake is writing `volatile int count = 0;` and having multiple threads call `count++`. `volatile` only guarantees you read the latest value; it cannot prevent multiple threads from reading the same value simultaneously and incrementing it independently, leading to Lost Updates.
**💡 Fix:** 使用 `AtomicInteger` 或 `synchronized`。 / Use `AtomicInteger` or `synchronized`.

### ❌ 忽略 ARM 架構下的弱記憶體模型 (Ignoring Weak Memory Models on ARM)
在 x86 架構（傳統 Intel/AMD 伺服器）下，CPU 很少進行寫入重排，很多缺少 `volatile` 的併發 Bug 碰巧不會發作（It works on my machine）。但當專案遷移到 ARM 架構（如 AWS Graviton, Mac M1/M2）時，由於 ARM 採用弱記憶體模型 (Weak Memory Model)，隱藏的指令重排 Bug 會瞬間爆發，導致隨機崩潰。
On x86 architectures (traditional Intel/AMD servers), CPUs rarely reorder writes, so many concurrency bugs missing `volatile` happen to not manifest ("It works on my machine"). However, when migrating to ARM architectures (e.g., AWS Graviton, Mac M1/M2), which use a Weak Memory Model, hidden instruction reordering bugs will explode instantly, causing random crashes.

### ❌ 過度同步 (Over-synchronization)
為了修復併發問題，在所有方法上無腦加上 `synchronized`。這會導致執行緒排隊阻塞，嚴重拖垮效能，甚至引發死結 (Deadlock)。
Mindlessly adding `synchronized` to all methods to fix concurrency issues. This causes thread queuing and blocking, severely degrading performance, and can even lead to Deadlocks.

---

## Checklists & workflows｜檢查清單與流程

當你在處理跨執行緒共用的變數時，請走過以下決策樹：
When dealing with variables shared across threads, walk through this decision tree:

- [ ] **這個變數真的需要跨執行緒共享嗎？** (Does this variable really need to be shared?)
  - 如果能放進 ThreadLocal 或區域變數 (Local variable)，就不要共享。（Thread confinement 永遠是最安全的）。
  - If it can be put into a ThreadLocal or local variable, do not share it. (Thread confinement is always the safest).
- [ ] **它只是一個單純的狀態標記（如 true/false）嗎？** (Is it just a simple state flag?)
  - 如果是，且更新操作不依賴於目前的值，請使用 `volatile`。
  - If yes, and the update doesn't depend on the current value, use `volatile`.
- [ ] **它的更新依賴於目前的值嗎？（例如 i++ 或 i = i * 2）** (Does the update depend on the current value?)
  - 如果是，`volatile` 不夠用。請改用 `java.util.concurrent.atomic` 套件下的類別（如 `AtomicInteger`）。
  - If yes, `volatile` is not enough. Use classes from the `java.util.concurrent.atomic` package (e.g., `AtomicInteger`).
- [ ] **是否有多個變數需要同時保持一致性？** (Do multiple variables need to maintain consistency together?)
  - 如果有不變式 (Invariant) 牽涉多個變數（例如 `x` 和 `y` 必須同時更新），必須使用 `synchronized` 或 `ReentrantLock` 將它們包裝成原子操作。
  - If an invariant involves multiple variables (e.g., `x` and `y` must be updated together), you must use `synchronized` or `ReentrantLock` to wrap them into an atomic operation.

---

## Real-world examples｜實戰案例

### 案例一：優雅關閉的狀態標記 (Graceful Shutdown Flag)

這是在背景服務 (Background Daemon) 中最常見的模式。
This is the most common pattern in background daemons.

```java
public class BackgroundWorker implements Runnable {
    // 必須加上 volatile，否則主執行緒呼叫 stop() 時，
    // 工作執行緒可能永遠看不到 running 變成 false。
    // MUST use volatile, otherwise when the main thread calls stop(),
    // the worker thread might never see 'running' become false.
    private volatile boolean running = true;

    @Override
    public void run() {
        while (running) {
            doWork();
        }
        cleanup();
    }

    public void stop() {
        this.running = false; // 寫入操作會立刻對其他執行緒可見 / Write is immediately visible
    }
}
```

### 案例二：為什麼 DCL 一定要加 volatile？ (Why DCL strictly requires volatile?)

在面試與實戰中最常被問到的 Double-Checked Locking 陷阱。
The most frequently asked Double-Checked Locking pitfall in interviews and practice.

```java
public class ConfigurationManager {
    // 缺少 volatile 會導致災難！
    // Missing volatile here leads to disaster!
    private static volatile ConfigurationManager instance;

    private ConfigurationManager() {
        // 假設這裡有繁重的初始化工作
        // Assume heavy initialization here
    }

    public static ConfigurationManager getInstance() {
        if (instance == null) { // 第一次檢查 / First check
            synchronized (ConfigurationManager.class) {
                if (instance == null) { // 第二次檢查 / Second check
                    // 這行程式碼在底層分為三個步驟：
                    // 1. 分配記憶體空間 (Allocate memory)
                    // 2. 呼叫建構子初始化 (Initialize object)
                    // 3. 將記憶體位址賦值給 instance 變數 (Assign reference)
                    //
                    // 如果沒有 volatile，CPU 可能將步驟重排為 1 -> 3 -> 2。
                    // 此時另一個執行緒在「第一次檢查」時會看到 instance != null，
                    // 但拿到的是一個「尚未初始化完成」的半成品物件，導致 NullPointerException！
                    //
                    // Without volatile, the CPU might reorder to 1 -> 3 -> 2.
                    // Another thread at the "First check" will see instance != null,
                    // but it gets a "partially constructed" object, causing a NullPointerException!
                    instance = new ConfigurationManager(); 
                }
            }
        }
        return instance;
    }
}
```