# Chapter 04: Concurrency, Atomics & Memory Model
# 第四章：並行程式設計與記憶體模型

## 1. 前言與學習目標 (Introduction & Learning Goals)

對於資深工程師而言，並行程式設計（Concurrency）不僅僅是使用 `std::thread` 或 `std::mutex` 來保護共享變數。在高效能運算、低延遲系統（如高頻交易、遊戲引擎、資料庫核心）中，理解硬體如何處理記憶體、編譯器如何重排指令是至關重要的。

For senior engineers, concurrency is more than just using `std::thread` or `std::mutex` to protect shared variables. In high-performance computing and low-latency systems (e.g., HFT, game engines, database kernels), understanding how hardware handles memory and how compilers reorder instructions is critical.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **掌握 C++ 記憶體模型（Memory Model）：** 理解 "Happens-before" 關係以及為何它是正確性的基石。
    **Master the C++ Memory Model:** Understand the "Happens-before" relationship and why it is the cornerstone of correctness.
2.  **精通記憶體順序（Memory Ordering）：** 超越預設的 `seq_cst`，正確使用 `acquire`、`release` 與 `relaxed` 來優化無鎖（Lock-free）程式碼。
    **Master Memory Ordering:** Move beyond the default `seq_cst` and correctly use `acquire`, `release`, and `relaxed` to optimize lock-free code.
3.  **解決偽共享（False Sharing）：** 識別並修復因 CPU Cache Line 競爭導致的效能殺手。
    **Solve False Sharing:** Identify and fix performance killers caused by CPU Cache Line contention.
4.  **實作基礎無鎖結構：** 設計一個正確的單生產者/單消費者（SPSC）佇列。
    **Implement Basic Lock-free Structures:** Design a correct Single-Producer/Single-Consumer (SPSC) queue.

---

## 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 C++ 記憶體模型與指令重排 (The C++ Memory Model & Instruction Reordering)

**觀念：** 你的程式碼並不是按照你寫的順序執行的。編譯器為了優化會重排指令，CPU 為了效能會亂序執行（Out-of-order execution），快取（Cache）系統會延遲寫入。C++ 記憶體模型是一份「合約」，定義了在什麼條件下，一個執行緒的寫入對另一個執行緒是可見的。

**Concept:** Your code does not execute in the exact order you write it. Compilers reorder instructions for optimization, CPUs execute out-of-order for performance, and cache systems delay writes. The C++ Memory Model is a "contract" that defines under what conditions a write by one thread becomes visible to another.

**心智模型：** 想像你在寫一份文件（變數寫入），然後發送一個通知（Atomic Flag）。
*   **Sequential Consistency (`seq_cst`):** 全世界所有人都同時看到文件和通知，且順序絕對一致。這很安全，但協調成本極高（類似強一致性資料庫）。
*   **Acquire/Release:** 你發出通知（Release），接收者看到通知後（Acquire），保證能看到你在發通知前寫好的文件。至於其他的雜事，順序不重要。
*   **Relaxed:** 你只是隨手寫個筆記，不保證別人什麼時候看到，也不保證別人看到的順序和你寫的順序有關。

**Mental Model:** Imagine writing a document (variable write) and then sending a notification (Atomic Flag).
*   **Sequential Consistency (`seq_cst`):** Everyone in the world sees the document and notification simultaneously, in a strictly consistent order. Safe, but coordination costs are high (like a strong-consistency DB).
*   **Acquire/Release:** You send a notification (Release), and once the receiver sees it (Acquire), they are guaranteed to see the document you wrote *before* the notification. Other unrelated tasks don't matter.
*   **Relaxed:** You just scribble a note. No guarantees on when others see it, or if they see it in the order you wrote it.

### 2.2 原子操作與鎖 (Atomics vs. Locks)

*   **Lock (Mutex):** 作業系統層級的機制。當鎖被佔用時，執行緒會進入休眠（Context Switch），開銷大。
*   **Atomic (Lock-free):** CPU 指令層級（如 x86 的 `LOCK` 前綴或 ARM 的 `LDREX/STREX`）。執行緒不會休眠，通常使用 Busy-wait 或 CAS (Compare-And-Swap) 迴圈。

*   **Lock (Mutex):** OS-level mechanism. When a lock is held, threads go to sleep (Context Switch), which is expensive.
*   **Atomic (Lock-free):** CPU instruction level (e.g., `LOCK` prefix on x86 or `LDREX/STREX` on ARM). Threads do not sleep; they typically use Busy-wait or CAS (Compare-And-Swap) loops.

### 2.3 偽共享 (False Sharing)

**定義：** 當多個執行緒頻繁修改位於同一個 Cache Line（通常是 64 bytes）上的不同變數時，會導致 CPU 核心不斷地使對方的 Cache 失效（Cache Coherency Protocol, MESI），造成嚴重的效能下降。

**Definition:** When multiple threads frequently modify different variables that reside on the same Cache Line (typically 64 bytes), it causes CPU cores to constantly invalidate each other's cache (Cache Coherency Protocol, MESI), leading to severe performance degradation.

---

## 3. 實務場景與系統設計視角 (Real-World & System Design View)

### 3.1 低延遲訊息傳遞 (Low-Latency Messaging)

在微服務架構的 Sidecar（如 Envoy）或高頻交易系統中，執行緒間的通訊（IPC）不能容忍 Mutex 帶來的微秒級延遲。
**應用：** 使用基於 Ring Buffer 的 Lock-free Queue 來在 Network IO Thread 和 Worker Thread 之間傳遞請求。

In microservice sidecars (like Envoy) or HFT systems, Inter-Process Communication (IPC) cannot tolerate the microsecond-level latency introduced by Mutexes.
**Application:** Use a Ring Buffer-based Lock-free Queue to pass requests between Network IO Threads and Worker Threads.

### 3.2 統計計數器 (Metrics Counters)

系統中常有全域計數器（如 `request_count`）。如果用 `std::mutex` 保護，會成為瓶頸。
**應用：** 使用 `std::atomic<uint64_t>` 配合 `std::memory_order_relaxed`。因為我們只在乎最終數字大致正確，不在乎某個執行緒是否晚了幾奈秒看到更新。

Systems often have global counters (e.g., `request_count`). Protecting them with `std::mutex` creates a bottleneck.
**Application:** Use `std::atomic<uint64_t>` with `std::memory_order_relaxed`. We only care that the final number is roughly correct, not if a thread sees the update a few nanoseconds late.

### 3.3 單例模式 (Singleton Pattern)

經典的 "Double-Checked Locking" 在 C++11 之前是不安全的。
**應用：** C++11 後，靜態區域變數的初始化是執行緒安全的（Magic Statics），或者使用 `std::call_once`，其底層依賴正確的記憶體屏障（Memory Barriers）。

The classic "Double-Checked Locking" was unsafe before C++11.
**Application:** Post-C++11, static local variable initialization is thread-safe (Magic Statics), or use `std::call_once`, which relies on correct Memory Barriers under the hood.

---

## 4. 逐步示例：單生產者單消費者無鎖佇列 (Walkthrough: SPSC Lock-free Queue)

我們將實作一個簡單的固定大小 Ring Buffer。這是理解 Acquire/Release 語意最經典的案例。

We will implement a simple fixed-size Ring Buffer. This is the classic case for understanding Acquire/Release semantics.

### 4.1 Naive Approach (使用 Mutex)

最直覺的做法是使用 `std::mutex` 保護 `push` 和 `pop`。

The most intuitive approach is to use `std::mutex` to protect `push` and `pop`.

```cpp
// 這是安全但較慢的版本 (Safe but slower)
template<typename T>
class BlockingQueue {
    std::mutex mtx;
    std::queue<T> q;
public:
    void push(T val) {
        std::lock_guard<std::mutex> lock(mtx);
        q.push(val);
    }
    bool pop(T& val) {
        std::lock_guard<std::mutex> lock(mtx);
        if(q.empty()) return false;
        val = q.front();
        q.pop();
        return true;
    }
};
```

**缺點：** 鎖競爭（Contention）會導致 Context Switch，破壞 CPU Cache locality。
**Drawback:** Lock contention leads to Context Switches, destroying CPU Cache locality.

### 4.2 Mature Approach (Lock-free with Acquire/Release)

我們使用 `std::atomic` 來管理 `head` 和 `tail` 索引。關鍵在於：**寫入資料必須在更新索引之前完成並對消費者可見。**

We use `std::atomic` to manage `head` and `tail` indices. The key is: **Data writes must complete and be visible to the consumer BEFORE the index is updated.**

```cpp
#include <atomic>
#include <vector>
#include <optional>

template<typename T, size_t Capacity>
class LockFreeRingBuffer {
    std::vector<T> buffer;
    // 使用 alignas 防止偽共享 (Use alignas to prevent False Sharing)
    alignas(64) std::atomic<size_t> head {0}; // Consumer index
    alignas(64) std::atomic<size_t> tail {0}; // Producer index

public:
    LockFreeRingBuffer() : buffer(Capacity) {}

    // 僅由生產者呼叫 (Called only by Producer)
    bool push(const T& item) {
        size_t current_tail = tail.load(std::memory_order_relaxed);
        size_t next_tail = (current_tail + 1) % Capacity;

        // 檢查是否已滿 (Check if full)
        // 這裡需要 acquire，確保我們讀到最新的 head
        // Here we need acquire to ensure we read the latest head
        if (next_tail == head.load(std::memory_order_acquire)) {
            return false; 
        }

        buffer[current_tail] = item; // 非原子寫入 (Non-atomic write)

        // 關鍵點：Release
        // 確保上面的 buffer 寫入對讀取 tail 的執行緒可見
        // Critical: Release
        // Ensures the buffer write above is visible to threads reading tail
        tail.store(next_tail, std::memory_order_release); 
        return true;
    }

    // 僅由消費者呼叫 (Called only by Consumer)
    std::optional<T> pop() {
        size_t current_head = head.load(std::memory_order_relaxed);

        // 關鍵點：Acquire
        // 與 push 中的 store(release) 配對。
        // 確保如果我們看到了新的 tail，我們也能看到 buffer 中的資料。
        // Critical: Acquire
        // Pairs with store(release) in push.
        // Ensures if we see the new tail, we also see the data in buffer.
        if (current_head == tail.load(std::memory_order_acquire)) {
            return std::nullopt; // Empty
        }

        T item = buffer[current_head]; // 安全讀取 (Safe read)

        // 更新 head 不需要同步資料，只要原子性即可，但為了保險起見
        // 在 SPSC 中，release 語意通常用於發布 "slot is free" 的訊號給生產者
        // Updating head doesn't need data sync, just atomicity, but to be safe
        // In SPSC, release semantics are used to publish "slot is free" signal to producer
        head.store((current_head + 1) % Capacity, std::memory_order_release);
        return item;
    }
};
```

### 4.3 分析 (Analysis)

1.  **Memory Ordering:**
    *   `tail.store(..., release)`: 保證這行之前的所有寫入（即 `buffer[current_tail] = item`）不會被重排到這行之後。
    *   `tail.load(..., acquire)`: 保證這行之後的所有讀取（即 `item = buffer[current_head]`）不會被重排到這行之前。
    *   這構成了一個 **Synchronizes-with** 關係。

2.  **False Sharing:**
    *   我們使用 `alignas(64)` 強制 `head` 和 `tail` 位於不同的 Cache Line。
    *   如果沒有這行，生產者寫 `tail` 會讓消費者的 `head` 所在的 Cache Line 失效（若兩者相鄰），導致消費者讀取 `head` 變慢。

---

## 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 誤用 `volatile` (Misusing `volatile`)

*   **錯誤：** 認為 `volatile bool flag = true;` 是執行緒安全的。
*   **原因：** 在 C++ 中，`volatile` 僅禁止編譯器優化（省略讀寫），**不保證** 原子性，也 **不提供** 記憶體屏障（Memory Barrier）。硬體仍可亂序執行。
*   **修正：** 必須使用 `std::atomic<bool>`。

*   **Pitfall:** Thinking `volatile bool flag = true;` is thread-safe.
*   **Why:** In C++, `volatile` only prevents compiler optimization (elision), it guarantees **neither** atomicity **nor** memory barriers. Hardware can still reorder.
*   **Fix:** Must use `std::atomic<bool>`.

### 5.2 過度使用 `shared_ptr` 於多執行緒 (Overusing `shared_ptr` in Multithreading)

*   **錯誤：** 在多個執行緒間傳遞同一個 `shared_ptr` 物件並修改它。
*   **原因：** `shared_ptr` 的引用計數（Control Block）是原子的，但 `shared_ptr` 物件本身（指向資料的指標）的操作**不是**原子的。
*   **修正：** 使用 `std::atomic<std::shared_ptr<T>>` (C++20) 或改用鎖保護。

*   **Pitfall:** Passing and modifying the same `shared_ptr` object across threads.
*   **Why:** The reference count (Control Block) is atomic, but operations on the `shared_ptr` object itself (the pointer to data) are **not**.
*   **Fix:** Use `std::atomic<std::shared_ptr<T>>` (C++20) or protect with a lock.

### 5.3 忽略 ABA 問題 (Ignoring the ABA Problem)

*   **錯誤：** 在實作 Lock-free Stack/LinkedList 時，僅使用 CAS (Compare-And-Swap) 檢查指標值。
*   **原因：** 一個指標的值從 A 變 B 又變回 A，CAS 會認為它沒變過，但記憶體內容可能已改變（例如節點被釋放又重分配）。
*   **修正：** 使用帶有版本號的指標（Tagged Pointers）或 Hazard Pointers / RCU。

*   **Pitfall:** Using simple CAS on pointer values when implementing Lock-free Stack/LinkedList.
*   **Why:** A pointer value changing A -> B -> A looks unchanged to CAS, but the memory content might have changed (e.g., node freed and reallocated).
*   **Fix:** Use Tagged Pointers (versioning) or Hazard Pointers / RCU.

---

## 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 解釋 `std::memory_order_relaxed` 的使用場景與風險。
**Explain the use cases and risks of `std::memory_order_relaxed`.**

*   **回答要點：**
    *   **定義：** 僅保證操作的原子性，不保證與其他執行緒的順序（無 Happens-before 關係）。
    *   **場景：** 統計計數器（Incrementing a counter）、檢查某個 flag 是否曾經被設定過（但不依賴該 flag 來讀取其他資料）。
    *   **風險：** 如果用它來做 "Data Ready" 的標記，讀取者可能看到標記為 true，但讀到的資料卻是舊的（因為寫入被重排了）。

### Q2: 什麼是 False Sharing？如何檢測與修復？
**What is False Sharing? How to detect and fix it?**

*   **回答要點：**
    *   **機制：** 多個核心修改同一 Cache Line 的不同變數，導致 Cache Line Ping-pong。
    *   **檢測：** 使用 `perf c2c` (Linux) 或 Intel VTune 觀察 "Hit Modified" 或 "Store-Load Forwarding" 事件。
    *   **修復：** 使用 `alignas(std::hardware_destructive_interference_size)` 或手動 padding 將變數隔開。

### Q3: 為什麼 Double-Checked Locking 需要 `atomic` 和 `acquire/release`？
**Why does Double-Checked Locking require `atomic` and `acquire/release`?**

*   **回答要點：**
    *   `instance = new Singleton();` 其實分三步：1. 分配記憶體 2. 建構物件 3. 指標賦值。
    *   如果沒有 Memory Barrier，步驟 3 可能在步驟 2 之前發生（重排）。
    *   另一個執行緒可能看到非 null 的指標，但物件尚未建構完成，導致 Crash。
    *   必須在寫入指標時用 `release`，讀取指標時用 `acquire`。

---

## 7. 小結與後續延伸 (Summary & Next Steps)

### 重點回顧 (Key Takeaways)

1.  **Atomicity != Ordering:** `std::atomic` 保證操作不被撕裂（Tearing），但 Memory Ordering 決定了操作的可見順序。
2.  **Acquire/Release is the Sweet Spot:** 大多數無鎖結構應使用 Acquire/Release 語意，而非預設的 `seq_cst`（太慢）或 `relaxed`（太危險）。
3.  **Hardware Matters:** 理解 Cache Line (64 bytes) 對於避免 False Sharing 至關重要。
4.  **Tools:** 善用 ThreadSanitizer (`-fsanitize=thread`) 來檢測 Data Race。

### 後續延伸 (Next Steps)

*   **Advanced Lock-free:** 學習 Hazard Pointers 或 RCU (Read-Copy-Update) 機制以解決記憶體回收問題。
*   **C++20 Coroutines:** 探索並行程式設計的另一種典範：非同步協程（Asynchronous Coroutines），這在下一章可能會討論。
*   **Parallel Algorithms:** 研究 C++17 `<execution>` 中的並行演算法（`std::for_each(std::execution::par, ...)`）。