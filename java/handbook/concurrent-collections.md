# 並行集合與鎖機制 / Concurrent Collections and Locking Mechanisms

## Mental model｜心智模型

在單執行緒的世界裡，資料結構就像是一個人的專屬書桌，你可以隨意整理；但在多執行緒的高併發場景中，資料結構變成了一個「公共圖書館」。
In a single-threaded world, a data structure is like your private desk where you can organize things freely. However, in a highly concurrent, multi-threaded scenario, it becomes a "public library."

初階工程師的直覺通常是「把整個圖書館鎖起來」（例如使用 `Collections.synchronizedMap` 或 `Hashtable`），這保證了安全，但犧牲了效能。資深工程師的心智模型則是**「降低鎖的粒度 (Granularity) 與競爭 (Contention)」**。
A junior engineer's instinct is often to "lock the entire library" (e.g., using `Collections.synchronizedMap` or `Hashtable`). This guarantees safety but sacrifices performance. A senior engineer's mental model focuses on **"reducing lock granularity and contention."**

理解 Java 並行集合的核心在於掌握以下三個維度：
Understanding Java's concurrent collections relies on mastering these three dimensions:

1. **Lock Stripping & Lock-Free (鎖分離與無鎖設計)**：如 `ConcurrentHashMap` 利用 CAS (Compare-And-Swap) 和細粒度的 Node 鎖，讓不同執行緒可以同時修改 Map 的不同部分。
   *Like `ConcurrentHashMap`, which uses CAS and fine-grained Node locks so different threads can modify different parts of the Map simultaneously.*
2. **Copy-on-Write (寫入時複製)**：如 `CopyOnWriteArrayList`，讀取時完全不加鎖，寫入時複製一份底層陣列。這是一種「空間換取時間」的極端樂觀策略。
   *Like `CopyOnWriteArrayList`, which requires no locks for reading but copies the underlying array on writing. It's an extreme optimistic strategy trading space for time.*
3. **Weakly Consistent Iterators (弱一致性迭代器)**：並行集合的迭代器不會拋出 `ConcurrentModificationException`，但它們反映的是迭代器建立「當下或之後某個時間點」的狀態，不保證絕對即時。
   *Iterators of concurrent collections won't throw `ConcurrentModificationException`, but they reflect the state at or some time after the iterator's creation, guaranteeing no absolute real-time consistency.*

---

## Patterns & best practices｜常見模式與最佳實務

- **使用 `computeIfAbsent` 實作本地快取 / Use `computeIfAbsent` for Local Caching**
  在 `ConcurrentHashMap` 中，利用 `computeIfAbsent` 可以保證「檢查並計算」的原子性，避免快取擊穿（Cache Breakdown）時多個執行緒重複計算相同的值。
  In `ConcurrentHashMap`, using `computeIfAbsent` ensures the atomicity of "check-and-compute", preventing multiple threads from redundantly computing the same value during a cache breakdown.

- **讀多寫少的清單使用 `CopyOnWriteArrayList` / Use `CopyOnWriteArrayList` for Read-Heavy Lists**
  對於觀察者模式（Observer Pattern）中的 Listener 清單，或是系統啟動後極少修改的白名單配置，這是最完美的選擇。
  This is the perfect choice for Listener lists in the Observer Pattern, or whitelist configurations that are rarely modified after system startup.

- **生產者-消費者模式首選 `BlockingQueue` / Prefer `BlockingQueue` for Producer-Consumer Patterns**
  不要自己用 `wait()` 和 `notify()` 造輪子。使用 `ArrayBlockingQueue` (有界，預防 OOM) 或 `LinkedBlockingQueue` 來解耦生產者與消費者。
  Don't reinvent the wheel with `wait()` and `notify()`. Use `ArrayBlockingQueue` (bounded, prevents OOM) or `LinkedBlockingQueue` to decouple producers and consumers.

- **高併發計數器使用 `LongAdder` / Use `LongAdder` for High-Concurrency Counters**
  取代 `AtomicLong`。`LongAdder` 在內部將計數分散到多個變數（Cell）中，大幅降低了 CAS 失敗重試的 CPU 消耗，最後再求和。
  Replace `AtomicLong`. `LongAdder` internally distributes the counts across multiple variables (Cells), significantly reducing the CPU overhead of CAS retry failures, and sums them up at the end.

- **樂觀讀取使用 `StampedLock` / Use `StampedLock` for Optimistic Reads**
  如果你的場景是讀取極多、寫入極少，且允許偶爾重試，`StampedLock` 的樂觀讀取效能遠勝於傳統的 `ReentrantReadWriteLock`。
  If your scenario has extremely high reads, very few writes, and allows occasional retries, the optimistic reading performance of `StampedLock` vastly outperforms the traditional `ReentrantReadWriteLock`.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

- **❌ Check-Then-Act 競態條件 / Check-Then-Act Race Conditions**
  **[Pitfall]** 以為用了 `ConcurrentHashMap` 就絕對安全，卻寫出 `if (!map.containsKey(key)) { map.put(key, value); }` 的程式碼。這兩個操作之間依然會發生 Context Switch，導致資料覆蓋。
  **[Pitfall]** Assuming `ConcurrentHashMap` makes everything safe, writing `if (!map.containsKey(key)) { map.put(key, value); }`. A context switch can still occur between these two operations, leading to data overwrites.
  **[Fix]** 使用 `putIfAbsent()` 或 `computeIfAbsent()`。
  **[Fix]** Use `putIfAbsent()` or `computeIfAbsent()`.

- **❌ 依賴 `size()` 或 `isEmpty()` 做業務邏輯 / Relying on `size()` or `isEmpty()` for Business Logic**
  **[Pitfall]** 在高併發下，並行集合的 `size()` 是一個「估計值」而不是絕對精確的快照。如果依賴 `if (queue.size() < 10)` 來決定是否放入元素，極易出錯。
  **[Pitfall]** Under high concurrency, `size()` of a concurrent collection is an "estimate," not an absolutely precise snapshot. Relying on `if (queue.size() < 10)` to decide whether to enqueue is highly error-prone.
  **[Fix]** 依賴方法本身的回傳值，例如 `queue.offer(element)` 失敗會回傳 false。
  **[Fix]** Rely on the return values of the methods themselves, e.g., `queue.offer(element)` returns false if it fails.

- **❌ 濫用 `CopyOnWriteArrayList` 導致 OOM / Abusing `CopyOnWriteArrayList` causing OOM**
  **[Pitfall]** 在寫入頻繁的場景（例如日誌收集）或資料量極大的清單使用 COW。每次 `add()` 都會複製整個底層陣列，導致嚴重的記憶體消耗與 GC 壓力。
  **[Pitfall]** Using COW in write-heavy scenarios (like log collection) or with massive lists. Every `add()` copies the entire underlying array, causing severe memory footprint and GC pressure.

- **❌ 忘記在 `finally` 區塊釋放顯式鎖 / Forgetting to Release Explicit Locks in `finally` Blocks**
  **[Pitfall]** 使用 `ReentrantLock` 時，如果在 `lock()` 和 `unlock()` 之間拋出異常，鎖將永遠不會被釋放，導致死結 (Deadlock)。
  **[Pitfall]** When using `ReentrantLock`, if an exception is thrown between `lock()` and `unlock()`, the lock will never be released, resulting in a deadlock.

---

## Checklists & workflows｜檢查清單與流程

在選擇集合與鎖機制時，請遵循以下決策流程：
Follow this decision workflow when choosing collections and locking mechanisms:

- [ ] **是否真的需要執行緒安全？ / Do I really need thread safety?**
  - 如果變數是區域變數 (Local variable) 或 ThreadLocal，直接使用 `HashMap` / `ArrayList`，避免無謂的效能損耗。
  - *If the variable is local or ThreadLocal, use `HashMap` / `ArrayList` directly to avoid unnecessary performance overhead.*
- [ ] **讀寫比例為何？ / What is the Read/Write ratio?**
  - 讀極多、寫極少 (Read-heavy, Write-rarely) 且資料量不大 ➔ 考慮 `CopyOnWriteArrayList` 或 `StampedLock`。
  - *Read-heavy, write-rarely, and small data size ➔ Consider `CopyOnWriteArrayList` or `StampedLock`.*
  - 讀寫皆頻繁 (Frequent reads and writes) ➔ 使用 `ConcurrentHashMap` 或 `ReentrantLock`。
  - *Frequent reads and writes ➔ Use `ConcurrentHashMap` or `ReentrantLock`.*
- [ ] **是否需要阻塞等待？ / Do I need blocking behavior?**
  - 需要在佇列滿時等待，空時阻塞 ➔ 使用 `ArrayBlockingQueue`。
  - *Need to wait when the queue is full and block when empty ➔ Use `ArrayBlockingQueue`.*
- [ ] **複合操作是否具備原子性？ / Are compound operations atomic?**
  - 檢查程式碼中是否有 `get` 接著 `put` 的邏輯，將其重構為 `compute`、`merge` 或 `putIfAbsent`。
  - *Check for `get` followed by `put` logic in the code, refactor them into `compute`, `merge`, or `putIfAbsent`.*
- [ ] **顯式鎖的釋放是否安全？ / Is explicit lock release safe?**
  - 確保所有的 `lock.unlock()` 都寫在 `try-finally` 區塊的 `finally` 中。
  - *Ensure all `lock.unlock()` calls are placed inside the `finally` block of a `try-finally` statement.*

---

## Real-world examples｜實戰案例

### 案例 1：安全的本地快取實作 / Safe Local Cache Implementation

這是在實務中最常見的 `ConcurrentHashMap` 應用場景。
This is the most common real-world application of `ConcurrentHashMap`.

```java
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class UserProfileCache {
    private final Map<String, UserProfile> cache = new ConcurrentHashMap<>();

    // ❌ 反模式：Check-Then-Act (非執行緒安全)
    // ❌ Anti-pattern: Check-Then-Act (Not thread-safe)
    public UserProfile getUserProfileBad(String userId) {
        if (!cache.containsKey(userId)) {
            // 如果兩個執行緒同時到達這裡，資料庫會被查詢兩次
            // If two threads reach here simultaneously, the DB is queried twice
            UserProfile profile = fetchFromDatabase(userId);
            cache.put(userId, profile);
        }
        return cache.get(userId);
    }

    // ✅ 最佳實踐：使用 computeIfAbsent 保證原子性
    // ✅ Best Practice: Use computeIfAbsent for atomicity
    public UserProfile getUserProfileGood(String userId) {
        // 只有當 key 不存在時，才會執行 fetchFromDatabase
        // 且 ConcurrentHashMap 保證同一個 key 的計算只會執行一次
        // fetchFromDatabase is executed only if the key is absent.
        // ConcurrentHashMap guarantees the computation for the same key runs only once.
        return cache.computeIfAbsent(userId, this::fetchFromDatabase);
    }

    private UserProfile fetchFromDatabase(String userId) {
        System.out.println("Querying database for: " + userId);
        return new UserProfile(userId); // 模擬耗時的 DB 查詢 / Simulating expensive DB query
    }
}
```

### 案例 2：事件監聽器管理器 / Event Listener Manager

使用 `CopyOnWriteArrayList` 來管理 Listener，避免在觸發事件時因為有新的 Listener 註冊而拋出異常。
Using `CopyOnWriteArrayList` to manage Listeners, avoiding exceptions thrown during event dispatching if a new Listener registers concurrently.

```java
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

public class EventPublisher {
    // ✅ 適合讀多寫少的場景 (觸發事件頻繁，但新增/移除監聽器較少)
    // ✅ Suitable for read-heavy scenarios (frequent event dispatching, rare listener modifications)
    private final List<EventListener> listeners = new CopyOnWriteArrayList<>();

    public void registerListener(EventListener listener) {
        listeners.add(listener); // 寫入時會複製底層陣列 / Copies underlying array on write
    }

    public void publishEvent(Event event) {
        // 迭代時完全不需要加鎖，也不會拋出 ConcurrentModificationException
        // No locking required during iteration, and no ConcurrentModificationException
        for (EventListener listener : listeners) {
            listener.onEvent(event);
        }
    }
}
```

### 案例 3：標準的顯式鎖使用範本 / Standard Explicit Lock Template

當並行集合無法滿足複雜的多變數狀態同步時，我們需要退回到顯式鎖。
When concurrent collections cannot satisfy complex multi-variable state synchronization, we fall back to explicit locks.

```java
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class AccountTransfer {
    private final Lock lock = new ReentrantLock();
    private double balance;

    public void deposit(double amount) {
        lock.lock(); // 1. 獲取鎖 / Acquire lock
        try {
            // 2. 業務邏輯放在 try 區塊內 / Business logic inside try block
            balance += amount;
        } finally {
            // 3. 確保在 finally 釋放鎖，防止死結 / Ensure lock release in finally to prevent deadlock
            lock.unlock(); 
        }
    }
}
```