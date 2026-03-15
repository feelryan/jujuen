# 並行安全實戰：Data Race 檢測與鎖的策略 / Concurrency Safety: Data Race Detection & Locking Strategies

## Mental model｜心智模型

在 C++ 中處理並行（Concurrency）時，必須建立一個核心觀念：**「共享的可變狀態是萬惡之源」（Shared Mutable State is the root of all evil）。**

1.  **Happens-Before 關係**：
    不要只從「程式碼執行順序」思考，要從「記憶體可見性（Memory Visibility）」思考。如果執行緒 A 寫入變數 X，執行緒 B 讀取變數 X，除非你透過鎖（Mutex）或原子操作（Atomic）建立了 A 與 B 之間的 **Happens-Before** 關係，否則這就是 Undefined Behavior (Data Race)。

2.  **鎖的職責不是保護程式碼，是保護不變量（Invariants）**：
    `std::mutex` 不是用來標記「這段程式碼一次只能一個人跑」，而是用來保證「這段時間內，資料結構的狀態是完整且一致的」。

3.  **硬體現實（Cache Coherency）**：
    多核 CPU 的 L1/L2 Cache 透過 MESI 等協議同步。如果兩個執行緒頻繁修改同一個 Cache Line 上的不同變數（False Sharing），效能會因為 Cache Line 在核心間來回彈跳（Ping-pong）而崩潰。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 鎖的 RAII 管理 (Always use RAII for Locks)
永遠不要手動呼叫 `mu.lock()` 與 `mu.unlock()`。C++17 之後，`std::scoped_lock` 是預設首選，它能同時鎖住多個 mutex 且避免死鎖（Deadlock）。

```cpp
std::mutex mtx;
void thread_safe_function() {
    // ❌ Bad: Manual management, not exception safe
    // mtx.lock();
    // do_something();
    // mtx.unlock();

    // ✅ Good: C++17 scoped_lock (handles multiple locks automatically)
    std::scoped_lock lock(mtx); 
    do_something();
}
```

### 2. 最小化 Critical Section (Minimize Critical Sections)
持有鎖的時間越短越好。不要在持有鎖的時候做 I/O、記憶體分配（如果可能避免）或呼叫未知的 callback。

*   **Copy-Swap / Copy-Update 模式**：先在鎖內複製資料，釋放鎖，處理資料，如果需要寫回再拿鎖（需注意 ABA 或狀態變更問題）。

### 3. 讀寫分離 (Reader-Writer Locks)
對於「讀多寫少」的場景（如設定檔快取），使用 `std::shared_mutex` (C++17)。

```cpp
#include <shared_mutex>

class Config {
    mutable std::shared_mutex rw_mutex_;
    std::map<std::string, int> settings_;

public:
    int get(const std::string& key) const {
        // 多個執行緒可同時持有 shared_lock (Reader)
        std::shared_lock lock(rw_mutex_); 
        return settings_.at(key);
    }

    void set(const std::string& key, int value) {
        // 只有一個執行緒能持有 unique_lock (Writer)
        std::unique_lock lock(rw_mutex_);
        settings_[key] = value;
    }
};
```

### 4. 雙重檢查鎖定與單次初始化 (Double-Checked Locking & One-time Init)
不要自己發明 Double-Checked Locking，極容易寫錯。
*   **Singleton/Init**：使用 `std::call_once` 或 C++11 後的 `static` 區域變數（Magic Statics，保證執行緒安全）。

### 5. 強制使用 Thread Sanitizer (TSan)
人眼無法檢測所有的 Data Race。在 CI/CD 流程或本地測試中，**必須**開啟 TSan。
*   GCC/Clang: `-fsanitize=thread -g`
*   這能抓出 95% 以上隱晦的 Race Conditions。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. `volatile` 不是原子操作 (`volatile` != `std::atomic`)
這是從嵌入式 C 或 Java 轉過來的工程師最常犯的錯。在 C++ 中，`volatile` 僅禁止編譯器優化讀寫指令，**不保證**原子性，也**不保證**記憶體順序（Memory Ordering）。多執行緒通訊必須用 `std::atomic`。

### 2. 洩漏參考 (Leaking References)
保護了容器，卻回傳了容器內元素的 Reference 或 Pointer。

```cpp
class DataStore {
    std::mutex mtx_;
    std::vector<int> data_;
public:
    // ❌ DANGEROUS: 回傳的 reference 在鎖釋放後不再受保護
    int& get_item(size_t index) {
        std::lock_guard<std::mutex> lock(mtx_);
        return data_[index]; 
    }
};
// Caller: int& ref = store.get_item(0); 
// 其他執行緒此時修改 data_，ref 變成 dangling 或讀到髒資料。
```

### 3. 偽共享 (False Sharing)
兩個無邏輯關聯的原子變數（例如 `atomic<int> count_A` 和 `atomic<int> count_B`）如果在記憶體中靠太近（同一個 Cache Line，通常是 64 bytes），不同執行緒分別修改它們時，會導致嚴重的效能懲罰。
*   **Fix**: 使用 `alignas(64)` 強制對齊。

### 4. 過度自信的 Lock-free 程式設計
除非你是並行專家且經過嚴格 benchmark，否則**不要手寫 Lock-free 資料結構**。
*   `std::atomic` 的預設記憶體順序是 `memory_order_seq_cst`（最安全但最慢）。
*   錯誤使用 `memory_order_relaxed` 或 `acquire/release` 會導致極難除錯的 Bug。通常 `std::mutex` 的效能對於 99% 的應用都足夠好。

---

## Checklists & workflows｜檢查清單與流程

### Code Review Checklist
- [ ] **RAII**: 是否使用了 `std::scoped_lock` 或 `std::unique_lock`？有沒有手動呼叫 `unlock()`？
- [ ] **Deadlock Prevention**: 如果函式需要兩個以上的鎖，是否使用了 `std::scoped_lock(m1, m2)` 或保證了全域一致的加鎖順序？
- [ ] **Escape Analysis**: 是否有將受保護資料的 Reference/Pointer 回傳到鎖的範圍之外？
- [ ] **Granularity**: Critical Section 內是否包含了不必要的 I/O 或耗時運算？
- [ ] **Variables**: 跨執行緒共用的變數是否為 `std::atomic` 或由 mutex 保護？有沒有誤用 `volatile`？

### Debugging Workflow (當發生疑似 Race 時)
1.  **Reproduce**: 嘗試撰寫能重現問題的單元測試（通常需要高並發 loop）。
2.  **Sanitize**: 使用 `-fsanitize=thread` 重新編譯並執行。TSan 的報告通常會直接指出哪兩行程式碼發生了衝突。
3.  **Analyze**:
    *   如果是 Deadlock：檢查鎖的獲取順序。
    *   如果是 Data Race：檢查是否漏了鎖，或是鎖的範圍太小。
    *   如果是效能低落：檢查 `lock contention`（鎖競爭）程度，考慮 `std::shared_mutex` 或分片鎖（Sharded Locking）。

---

## Real-world examples｜實戰案例

### 案例 1：解決 False Sharing (效能優化)

在實作一個多執行緒計數器時，如果結構如下：

```cpp
// ❌ 容易發生 False Sharing
struct Counters {
    std::atomic<int> worker_a_count;
    std::atomic<int> worker_b_count;
};
```
當 Thread A 頻繁更新 `worker_a_count`，Thread B 頻繁更新 `worker_b_count`，因為兩者極可能在同一個 Cache Line，CPU 核心必須不斷讓對方的 Cache 失效。

**修正後：**

```cpp
// ✅ 使用 padding 強制隔離
struct Counters {
    alignas(64) std::atomic<int> worker_a_count;
    alignas(64) std::atomic<int> worker_b_count;
};
```
這在高效能佇列（Queue）或統計模組中非常常見。

### 案例 2：執行緒安全的觀察者模式 (避免 Deadlock)

一個常見的 Deadlock 場景是：持有鎖的情況下呼叫外部 Callback，而 Callback 又試圖呼叫回原本的物件獲取同一個鎖（Reentrancy），或者 Callback 試圖獲取另一個鎖導致順序倒置。

```cpp
class EventDispatcher {
    std::mutex mtx_;
    std::vector<std::function<void()>> listeners_;

public:
    void add_listener(std::function<void()> cb) {
        std::scoped_lock lock(mtx_);
        listeners_.push_back(cb);
    }

    void dispatch() {
        std::vector<std::function<void()>> local_listeners;
        
        {
            // 1. 只在複製列表時持有鎖
            std::scoped_lock lock(mtx_);
            local_listeners = listeners_;
        } // 鎖在這裡釋放

        // 2. 在鎖之外執行 Callback
        for (const auto& cb : local_listeners) {
            cb(); // 即使 cb 內部呼叫了 add_listener 也不會死鎖
        }
    }
};
```
**策略**：Snapshotting（快照）。將需要操作的資料複製一份出來，釋放鎖，然後在安全環境下操作副本。