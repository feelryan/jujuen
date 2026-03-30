# 執行緒生命週期與同步機制 / Thread Lifecycle and Synchronization

## Mental model｜心智模型

在 Java 中，執行緒的生命週期與同步機制可以被理解為一個「狀態機（State Machine）」與「房間門禁系統（Access Control System）」的結合。
In Java, the thread lifecycle and synchronization mechanisms can be understood as a combination of a "State Machine" and an "Access Control System."

**1. 執行緒狀態機 (The Thread State Machine)**
不要把執行緒單純想成「執行中」或「停止」。在 JVM 中，執行緒在六種狀態間轉換：
Do not think of threads simply as "running" or "stopped." In the JVM, threads transition between six states:
- **NEW**: 剛建立，尚未啟動。 / Created, but not yet started.
- **RUNNABLE**: 在 JVM 中執行，但可能正在等待作業系統資源（如 CPU 時間片）。 / Executing in the JVM, but might be waiting for OS resources (like CPU time).
- **BLOCKED**: 試圖進入 `synchronized` 區塊，但鎖被別人拿走了（在門外排隊）。 / Trying to enter a `synchronized` block, but the lock is held by another thread (waiting outside the door).
- **WAITING**: 已經進門了，但條件不滿足，主動交出鎖並進入專屬休息室等待（如呼叫 `Object.wait()` 或 `LockSupport.park()`）。 / Inside the door, but conditions aren't met. Voluntarily releases the lock and waits in a waiting room (e.g., calling `Object.wait()` or `LockSupport.park()`).
- **TIMED_WAITING**: 帶有超時機制的等待（如 `Thread.sleep()` 或 `wait(timeout)`）。 / Waiting with a specified timeout (e.g., `Thread.sleep()` or `wait(timeout)`).
- **TERMINATED**: 執行完畢或異常終止。 / Completed execution or terminated abnormally.

**2. 同步機制的門禁模型 (The Access Control Model of Synchronization)**
- **`synchronized`**: 就像一扇「全自動感應門」。JVM 幫你處理開門（獲取鎖）與關門（釋放鎖），即使發生異常也會自動解鎖。但它只有一個共用的「休息室」（wait set）。
  Like a "fully automatic sliding door." The JVM handles opening (acquiring the lock) and closing (releasing the lock), even if an exception occurs. However, it only has one shared "waiting room" (wait set).
- **`ReentrantLock`**: 就像一扇「手動防盜門」。你需要明確地拿鑰匙開門（`lock()`）並記得鎖門（`unlock()`）。它提供了更進階的功能，例如：嘗試開門（`tryLock`）、可被打斷的排隊（`lockInterruptibly`），以及可以建立多個專屬休息室（`Condition`）。
  Like a "manual security door." You must explicitly unlock it (`lock()`) and remember to lock it back (`unlock()`). It offers advanced features like attempting to open (`tryLock`), interruptible queuing (`lockInterruptibly`), and the ability to create multiple dedicated waiting rooms (`Condition`).

---

## Patterns & best practices｜常見模式與最佳實務

**1. 預設使用 `synchronized`，需要進階功能才升級為 `ReentrantLock`**
**Default to `synchronized`, upgrade to `ReentrantLock` only when advanced features are needed.**
現代 JVM 對 `synchronized` 做了大量優化（如鎖消除、鎖粗化、偏向鎖與輕量級鎖）。除非你需要超時機制（Timeout）、公平鎖（Fairness）或多個條件變數（Multiple Conditions），否則 `synchronized` 的程式碼更簡潔且不易出錯。
Modern JVMs have heavily optimized `synchronized` (e.g., lock elimination, lock coarsening, biased locking, and lightweight locking). Unless you need timeouts, fairness, or multiple condition variables, `synchronized` results in cleaner and less error-prone code.

**2. 永遠在 `while` 迴圈中呼叫 `wait()` 或 `await()`**
**Always call `wait()` or `await()` inside a `while` loop.**
這是為了防止「虛假喚醒（Spurious Wakeups）」以及確保被喚醒時條件依然成立。
This prevents "spurious wakeups" and ensures the condition still holds true when the thread is awakened.
```java
// Good Practice
synchronized (lock) {
    while (!conditionIsMet) {
        lock.wait(); // 條件不滿足，繼續等待 / Wait if condition is not met
    }
    // 執行業務邏輯 / Execute business logic
}
```

**3. 縮小鎖的粒度 (Minimize Lock Granularity)**
只在真正需要保護的共享狀態上加鎖，避免將耗時的 I/O 操作或外部 API 呼叫放在鎖定區塊內。
Only lock the shared state that truly needs protection. Avoid placing time-consuming I/O operations or external API calls inside the locked block.

**4. `ReentrantLock` 必須搭配 `try-finally` 區塊**
**`ReentrantLock` must be paired with a `try-finally` block.**
確保無論是否發生 Exception，鎖最終都會被釋放。
Ensure the lock is always released, regardless of whether an exception occurs.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

**1. 鎖定在可變物件或字串常數上 (Locking on Mutable Objects or String Literals)**
- **Pitfall**: 使用 `String` 或 `Integer` 等包裝類別作為鎖。由於字串池（String Pool）和整數快取（Integer Cache）的存在，你可能會意外地與系統其他不相干的模組共用同一把鎖，導致嚴重的效能瓶頸或死結。
  Using `String` or wrapper classes like `Integer` as locks. Due to the String Pool and Integer Cache, you might accidentally share the same lock with completely unrelated modules in the system, causing severe performance bottlenecks or deadlocks.
- **Fix**: 永遠使用專屬的 `private final Object lock = new Object();` 作為鎖。
  Always use a dedicated `private final Object lock = new Object();` as the lock.

**2. 濫用 `notify()` 導致執行緒停滯 (Using `notify()` instead of `notifyAll()` causing thread stalls)**
- **Pitfall**: `notify()` 只會隨機喚醒一個等待中的執行緒。如果是生產者喚醒了另一個生產者，而不是消費者，可能會導致所有執行緒最終都進入 `WAITING` 狀態（死鎖的一種形式）。
  `notify()` wakes up only one random waiting thread. If a producer wakes up another producer instead of a consumer, it can lead to all threads eventually entering the `WAITING` state (a form of deadlock).
- **Fix**: 預設使用 `notifyAll()`。如果效能是極致考量，請改用 `ReentrantLock` 搭配多個 `Condition`。
  Default to `notifyAll()`. If performance is a critical concern, switch to `ReentrantLock` with multiple `Condition` variables.

**3. 巢狀鎖定導致死結 (Nested Locking leading to Deadlocks)**
- **Pitfall**: 執行緒 A 拿了鎖 1 去要鎖 2，同時執行緒 B 拿了鎖 2 去要鎖 1。
  Thread A holds Lock 1 and requests Lock 2, while Thread B holds Lock 2 and requests Lock 1.
- **Fix**: 確保所有執行緒以「相同的順序」獲取鎖；或者使用 `ReentrantLock.tryLock(timeout)` 來打破死結等待。
  Ensure all threads acquire locks in the "same order"; or use `ReentrantLock.tryLock(timeout)` to break the deadlock wait.

---

## Checklists & workflows｜檢查清單與流程

**鎖的選型決策樹 (Lock Selection Decision Tree):**
1. 我真的需要鎖嗎？(Do I really need a lock?) 
   👉 考慮無狀態設計 (Stateless design) 或 ThreadLocal。
2. 我可以用現成的並行集合嗎？(Can I use existing concurrent collections?) 
   👉 優先使用 `ConcurrentHashMap`, `BlockingQueue` 等。
3. 讀多寫少的情境？(Read-heavy, write-light scenario?) 
   👉 考慮 `ReentrantReadWriteLock` 或 `StampedLock`。
4. 需要超時中斷或精準喚醒？(Need timeouts, interrupts, or precise wakeups?) 
   👉 使用 `ReentrantLock` + `Condition`。
5. 其他一般同步需求？(Other general synchronization needs?) 
   👉 使用 `synchronized`。

**Code Review Checklist:**
- [ ] 檢查 `ReentrantLock` 的 `unlock()` 是否確實放在 `finally` 區塊的第一行？ (Is `unlock()` placed exactly in the `finally` block?)
- [ ] 檢查 `wait()` 或 `Condition.await()` 是否包裝在 `while` 迴圈中，並反覆檢查條件？ (Is `wait()`/`await()` wrapped in a `while` loop checking the condition?)
- [ ] 檢查鎖定的物件是否為 `private final`，避免鎖物件被中途替換？ (Is the locked object `private final` to prevent reassignment?)
- [ ] 是否有在鎖定區塊內呼叫外部 API 或進行 DB 查詢？（應盡量移出鎖定範圍） (Are there external API calls or DB queries inside the locked block? Move them out if possible.)

---

## Real-world examples｜實戰案例

### 案例 1：使用 ReentrantLock 與 Condition 實作精準喚醒 (Precise Wakeup with ReentrantLock and Condition)
在實作「生產者-消費者」模式時，`synchronized` + `wait/notifyAll` 會喚醒所有執行緒（包含同類），浪費 CPU 資源。使用 `ReentrantLock` 可以分離「未滿」與「未空」的等待室。
When implementing the Producer-Consumer pattern, `synchronized` + `wait/notifyAll` wakes up all threads (including those of the same type), wasting CPU cycles. `ReentrantLock` allows separating the "not full" and "not empty" waiting rooms.

```java
import java.util.LinkedList;
import java.util.Queue;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.ReentrantLock;

public class BoundedBuffer<T> {
    private final Queue<T> queue = new LinkedList<>();
    private final int capacity;
    
    // 1. 宣告手動鎖 / Declare the manual lock
    private final ReentrantLock lock = new ReentrantLock();
    // 2. 建立兩個專屬休息室 / Create two dedicated waiting rooms
    private final Condition notFull = lock.newCondition();
    private final Condition notEmpty = lock.newCondition();

    public BoundedBuffer(int capacity) {
        this.capacity = capacity;
    }

    public void put(T item) throws InterruptedException {
        lock.lock(); // 獲取鎖 / Acquire lock
        try {
            while (queue.size() == capacity) {
                // 滿了，生產者去 notFull 休息室等待
                // Full, producers wait in the notFull room
                notFull.await(); 
            }
            queue.add(item);
            // 放入物品後，只喚醒在 notEmpty 休息室的消費者
            // After putting an item, only wake up consumers in the notEmpty room
            notEmpty.signal(); 
        } finally {
            lock.unlock(); // 確保釋放鎖 / Ensure lock is released
        }
    }

    public T take() throws InterruptedException {
        lock.lock();
        try {
            while (queue.isEmpty()) {
                // 空了，消費者去 notEmpty 休息室等待
                // Empty, consumers wait in the notEmpty room
                notEmpty.await(); 
            }
            T item = queue.poll();
            // 拿走物品後，只喚醒在 notFull 休息室的生產者
            // After taking an item, only wake up producers in the notFull room
            notFull.signal(); 
            return item;
        } finally {
            lock.unlock();
        }
    }
}
```

### 案例 2：使用 tryLock 避免系統卡死 (Using tryLock to Prevent System Stalls)
在整合外部系統或高併發場景中，如果無法立即獲取鎖，我們可能希望快速失敗（Fail-fast）或執行降級邏輯（Fallback），而不是無限期等待。
In external system integrations or high-concurrency scenarios, if a lock cannot be acquired immediately, we might want to fail-fast or execute fallback logic instead of waiting indefinitely.

```java
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.ReentrantLock;

public class InventoryService {
    private final ReentrantLock inventoryLock = new ReentrantLock();

    public boolean deductInventory(String productId) {
        try {
            // 嘗試獲取鎖，最多等待 2 秒 / Try to acquire lock, wait up to 2 seconds
            if (inventoryLock.tryLock(2, TimeUnit.SECONDS)) {
                try {
                    // 執行扣庫存邏輯 / Execute inventory deduction logic
                    System.out.println("Inventory deducted for " + productId);
                    return true;
                } finally {
                    inventoryLock.unlock(); // 必須在內部 try-finally 釋放
                }
            } else {
                // 獲取鎖超時，執行降級邏輯（如：系統繁忙請稍後再試）
                // Lock acquisition timed out, execute fallback logic
                System.err.println("System busy, could not lock inventory for " + productId);
                return false;
            }
        } catch (InterruptedException e) {
            // 執行緒在等待鎖時被中斷 / Thread was interrupted while waiting for the lock
            Thread.currentThread().interrupt(); // 恢復中斷狀態 / Restore interrupt status
            return false;
        }
    }
}
```