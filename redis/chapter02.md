# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，僅僅知道「如何使用 Redis 指令」已不足以應對高併發與大數據量的挑戰。理解 Redis 的底層資料結構（Internal Encodings）是進行容量規劃、效能調優以及排查 Latency Spike 的關鍵。本章將深入剖析 Redis 物件背後的實作機制。

For senior engineers, knowing "how to use Redis commands" is no longer sufficient to handle high concurrency and massive data volumes. Understanding Redis's internal data structures (Internal Encodings) is crucial for capacity planning, performance tuning, and troubleshooting latency spikes. This chapter delves into the implementation mechanisms behind Redis objects.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **解釋 Redis 物件與底層編碼的映射關係**：理解為何同一個 `Hash` 或 `List` 在不同資料量下會有完全不同的記憶體佈局與效能表現。
    **Explain the mapping between Redis Objects and Internal Encodings**: Understand why the same `Hash` or `List` can have vastly different memory layouts and performance characteristics depending on data volume.
2.  **剖析核心底層結構（SDS, Skiplist, Listpack）**：掌握 Simple Dynamic String 的二進位安全特性，以及 Skiplist 如何在 ZSet 中取代平衡樹。
    **Dissect core internal structures (SDS, Skiplist, Listpack)**: Master the binary-safe properties of Simple Dynamic String and how Skiplist replaces balanced trees in ZSets.
3.  **評估時間與空間的權衡（Time-Space Trade-off）**：在系統設計時，能根據 Big O 複雜度與記憶體開銷，精準選擇最適合的資料型態與配置。
    **Evaluate Time-Space Trade-offs**: Precisely select the most suitable data types and configurations based on Big O complexity and memory overhead during system design.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 Redis Object vs. Internal Encoding
Redis 採用了一種「雙層」結構。對外，我們操作的是 **Redis Objects**（如 String, List, Hash, Set, ZSet）；對內，Redis 會根據資料的大小與類型，動態選擇最合適的 **Internal Encoding**。

Redis employs a "dual-layer" structure. Externally, we manipulate **Redis Objects** (e.g., String, List, Hash, Set, ZSet); internally, Redis dynamically selects the most appropriate **Internal Encoding** based on the size and type of the data.

這就像是 Java 中的 `List` 介面（Redis Object），底層可以是 `ArrayList` 或 `LinkedList`（Internal Encoding）。
This is analogous to the `List` interface in Java (Redis Object), where the underlying implementation could be `ArrayList` or `LinkedList` (Internal Encoding).

*   **Redis Object (`redisObject` struct)**: Contains metadata like type, encoding, LRU time, and a pointer to the actual data.
*   **Encoding**: The actual algorithm/structure used (e.g., `int`, `embstr`, `raw`, `listpack`, `hashtable`, `skiplist`).

## 2.2 關鍵底層結構 (Key Internal Structures)

### SDS (Simple Dynamic String)
Redis 不使用 C 語言標準的 String (`char*`)，而是設計了 SDS。
Redis does not use standard C strings (`char*`) but designed SDS instead.

*   **O(1) Length**: 記錄了長度，獲取字串長度無需遍歷。
    **O(1) Length**: Stores length, so retrieving string length does not require traversal.
*   **Binary Safe**: 不依賴 `\0` 終止符，可儲存圖片或序列化後的二進位資料。
    **Binary Safe**: Does not rely on the `\0` terminator, allowing storage of images or serialized binary data.
*   **Buffer Overflow Protection**: 修改字串前會自動檢查空間。
    **Buffer Overflow Protection**: Automatically checks for space before modifying the string.

### Skiplist (跳躍表)
用於 `Sorted Set (ZSet)` 的核心實作。它是一種機率性的資料結構，透過多層索引達到類似二元搜尋樹的效率。
Used as the core implementation for `Sorted Set (ZSet)`. It is a probabilistic data structure that achieves efficiency similar to binary search trees through multi-level indexing.

*   **Why not Balanced Tree (AVL/Red-Black)?**
    *   **Implementation Simplicity**: Skiplist 實作比紅黑樹簡單，易於除錯。
        **Implementation Simplicity**: Skiplist is simpler to implement than Red-Black trees and easier to debug.
    *   **Range Query**: 在區間查找（Range Scan）時，Skiplist 的表現優於樹結構（只需找到起點後跟隨指標）。
        **Range Query**: For range scans, Skiplist performs better than tree structures (just find the start and follow pointers).
    *   **Concurrency**: 雖然 Redis 是單執行緒，但在未來的並行化考量中，Skiplist 的鎖粒度控制較容易。
        **Concurrency**: Although Redis is single-threaded, Skiplist allows for easier lock granularity control in future parallelization considerations.

### Listpack / Ziplist (緊湊列表)
*註：Redis 7.0 後，Listpack 已逐漸取代 Ziplist，解決了連鎖更新（Cascading Update）的效能問題。*
*Note: Since Redis 7.0, Listpack has gradually replaced Ziplist, solving the performance issue of Cascading Updates.*

這是一塊連續的記憶體區塊，模擬陣列行為。
This is a contiguous block of memory simulating array behavior.

*   **Pros**: 極度節省記憶體（無指標開銷，Cache Locality 極佳）。
    **Pros**: Extremely memory efficient (no pointer overhead, excellent Cache Locality).
*   **Cons**: 插入與刪除需要記憶體重分配（Reallocation）與複製，時間複雜度較高。適合少量元素。
    **Cons**: Insertion and deletion require memory reallocation and copying, resulting in higher time complexity. Suitable for a small number of elements.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在系統設計中，選擇正確的 Redis 資料結構不僅影響開發速度，更直接決定了硬體成本與系統穩定性。
In system design, choosing the right Redis data structure not only affects development speed but also directly determines hardware costs and system stability.

## 3.1 記憶體優化 (Memory Optimization)
在儲存數百萬個小型物件（如 User Profile, IoT Device Status）時，直接使用 `String` 類型（Key-Value）會產生巨大的 Metadata 開銷。
When storing millions of small objects (e.g., User Profiles, IoT Device Status), using the `String` type (Key-Value) directly incurs huge metadata overhead.

*   **Strategy**: 將多個小物件聚合到一個 `Hash` 中。
    **Strategy**: Aggregate multiple small objects into a single `Hash`.
*   **Mechanism**: 當 Hash 內的欄位數量少且值很小時，Redis 會使用 `Listpack` 編碼。這能將記憶體佔用降低 5–10 倍。
    **Mechanism**: When the number of fields in a Hash is small and the values are small, Redis uses `Listpack` encoding. This can reduce memory usage by 5–10x.

## 3.2 延遲控制 (Latency Control)
理解底層結構有助於避免 "Big Key" 問題。
Understanding internal structures helps avoid "Big Key" problems.

*   **Scenario**: 刪除一個擁有 100 萬成員的 ZSet。
    **Scenario**: Deleting a ZSet with 1 million members.
*   **Impact**: 如果底層是 Skiplist，釋放記憶體涉及大量的指標操作，可能會阻塞 Main Thread 數百毫秒，導致線上服務瞬斷。
    **Impact**: If the underlying structure is a Skiplist, freeing memory involves extensive pointer operations, which may block the Main Thread for hundreds of milliseconds, causing service glitches.
*   **Solution**: 使用 `UNLINK` (Lazy Free) 代替 `DEL`。
    **Solution**: Use `UNLINK` (Lazy Free) instead of `DEL`.

---

# 4. 逐步示例 (Walkthrough / Example)

## 案例：設計即時排行榜 (Real-time Leaderboard)

### 4.1 需求 (Requirements)
我們需要維護一個遊戲的即時排行榜，包含 1,000 萬名玩家，需要支援：
We need to maintain a real-time leaderboard for a game with 10 million players, supporting:
1.  更新玩家分數 (Update Score)
2.  獲取 Top 100 玩家 (Get Top 100)
3.  查詢特定玩家排名 (Get Rank)

### 4.2 方案演進 (Solution Evolution)

#### Stage 1: Naive Approach (RDBMS or List)
使用資料庫排序或 Redis List。
Using database sorting or Redis List.
*   **Analysis**: List 插入特定位置是 O(N)，無法滿足高頻更新需求。
    **Analysis**: Inserting into a specific position in a List is O(N), which cannot meet high-frequency update requirements.

#### Stage 2: Redis Sorted Set (ZSet)
使用 `ZADD` 更新分數，`ZREVRANGE` 獲取排名。
Using `ZADD` to update scores and `ZREVRANGE` to get rankings.

*   **Internal View**:
    *   Redis 使用 **Dict (Hash Table)** 儲存 `Member -> Score` 的映射，保證 `ZSCORE` 為 O(1)。
        Redis uses a **Dict (Hash Table)** to store the `Member -> Score` mapping, ensuring `ZSCORE` is O(1).
    *   同時使用 **Skiplist** 儲存 `Score -> Member` 的排序，保證 `ZRANGE` 為 O(log N) + M。
        Simultaneously uses a **Skiplist** to store the `Score -> Member` sorting, ensuring `ZRANGE` is O(log N) + M.

#### Stage 3: Memory Optimization (ZipList/Listpack Tuning)
假設我們有許多「小型排行榜」（例如：每週公會排名，每個公會僅 50 人）。
Suppose we have many "small leaderboards" (e.g., weekly guild rankings, with only 50 members per guild).

*   **Configuration**:
    ```conf
    zset-max-listpack-entries 128
    zset-max-listpack-value 64
    ```
*   **Effect**: 當成員數小於 128 且元素小於 64 bytes 時，Redis 不會建立 Skiplist + Dict，而是使用緊湊的 **Listpack**。
    **Effect**: When members are fewer than 128 and elements are smaller than 64 bytes, Redis will not create a Skiplist + Dict, but instead use a compact **Listpack**.
*   **Trade-off**: 雖然查找變成了 O(N)，但因為 N 很小 (N < 128)，CPU Cache 命中率高，實際速度極快，且節省大量記憶體。
    **Trade-off**: Although lookup becomes O(N), since N is small (N < 128), CPU Cache hit rate is high, making it extremely fast in practice while saving significant memory.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 忽視編碼轉換導致的 CPU 飆升 (Ignoring CPU Spikes from Encoding Conversion)
*   **Pitfall**: 當 Hash 或 ZSet 的元素數量剛好超過 `max-listpack-entries` 閾值時，Redis 會將底層結構從 Listpack 轉換為 Hashtable/Skiplist。
    **Pitfall**: When the number of elements in a Hash or ZSet just exceeds the `max-listpack-entries` threshold, Redis converts the underlying structure from Listpack to Hashtable/Skiplist.
*   **Impact**: 這是一個一次性的 O(N) 操作。如果你的應用程式頻繁地在閾值邊緣徘徊（新增後刪除，再新增），會導致反覆的記憶體重分配與編碼轉換。
    **Impact**: This is a one-time O(N) operation. If your application frequently hovers around the threshold (add, then delete, then add again), it causes repeated memory reallocation and encoding conversions.
*   **Advice**: 預留 Buffer，或在容量規劃時明確區分「小集合」與「大集合」。
    **Advice**: Leave a buffer, or clearly distinguish between "small collections" and "large collections" during capacity planning.

## 5.2 濫用 String 儲存 JSON (Abusing Strings for JSON)
*   **Pitfall**: 將巨大的 JSON Blob 存入 String，每次只為了讀取其中一個欄位。
    **Pitfall**: Storing huge JSON blobs in Strings, only to read a single field each time.
*   **Why Bad**: 浪費網路頻寬，且序列化/反序列化消耗 Client 端 CPU。
    **Why Bad**: Wastes network bandwidth, and serialization/deserialization consumes Client-side CPU.
*   **Alternative**: 使用 Redis Hash (Flatten JSON) 或 RedisJSON 模組。這利用了底層 Dict 的 O(1) 查找特性。
    **Alternative**: Use Redis Hash (Flatten JSON) or the RedisJSON module. This leverages the O(1) lookup property of the underlying Dict.

## 5.3 對 Listpack/Ziplist 進行大範圍操作 (Heavy Operations on Listpack/Ziplist)
*   **Pitfall**: 在配置了很大 `list-max-listpack-size` 的 List 中執行隨機插入或刪除。
    **Pitfall**: Performing random insertions or deletions in a List configured with a very large `list-max-listpack-size`.
*   **Why Bad**: 緊湊結構的插入需要移動後續所有資料（Memmove），時間複雜度接近 O(N)。
    **Why Bad**: Insertion into a compact structure requires moving all subsequent data (Memmove), with time complexity approaching O(N).

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 為什麼 Redis 的 ZSet 使用 Skiplist 而不是紅黑樹 (Red-Black Tree) 或 B+ Tree？
**Why does Redis ZSet use Skiplist instead of Red-Black Tree or B+ Tree?**

*   **Key Points**:
    1.  **實作簡單 (Simplicity)**: Skiplist 代碼量少，易於維護。
    2.  **範圍查找 (Range Scan)**: ZSet 常用的 `ZRANGE` 在 Skiplist 中只需找到起點後遍歷指標，效率極高；平衡樹則需要複雜的中序遍歷。
    3.  **記憶體 (Memory)**: Skiplist 平均每個節點 1.33 個指標，平衡樹通常需要 2 個。
    4.  **併發潛力 (Concurrency Potential)**: 雖然 Redis 目前是單執行緒，但 Skiplist 在併發環境下的鎖競爭通常比平衡樹小（只需鎖局部）。

## Q2: 請解釋 Redis 的「漸進式 Rehash」(Incremental Rehash) 機制。
**Explain Redis's "Incremental Rehash" mechanism.**

*   **Key Points**:
    1.  Redis 的 Hash 表在擴容時，不會一次性將所有 Key 搬移到新表（這會阻塞主執行緒）。
    2.  相反，它維護兩個 Hash 表 (`ht[0]`, `ht[1]`)。
    3.  每次執行 CRUD 操作時，順便搬移一小部分 Bucket 到新表。
    4.  同時有 `serverCron` 定時任務協助搬移。
    5.  查詢時會先查舊表，再查新表。

## Q3: 什麼是 SDS？它解決了 C String 的哪些問題？
**What is SDS? What problems of C String does it solve?**

*   **Key Points**:
    1.  **O(1) Length**: 記錄 `len` 屬性。
    2.  **Binary Safe**: 不以 `\0` 為結尾，可存任意二進位資料。
    3.  **Buffer Overflow**: 修改前檢查 `free` 空間。
    4.  **Memory Allocation**: 預分配 (Pre-allocation) 減少 append 時的 syscall；惰性釋放 (Lazy free) 避免縮短字串後的頻繁重分配。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)
1.  **Object vs Encoding**: Redis 物件是介面，Encoding 是實作。同一指令在不同 Encoding 下複雜度可能不同。
2.  **SDS**: 二進位安全、O(1) 長度獲取、預分配記憶體。
3.  **Skiplist**: ZSet 的核心，優化了範圍查詢，實作比平衡樹簡單。
4.  **Listpack/Ziplist**: 犧牲 CPU 換取記憶體的緊湊結構，適合小數據量，具有極佳的 Cache Locality。
5.  **Trade-off**: 在設定 `max-listpack-entries` 等參數時，需平衡記憶體節省與 O(N) 操作帶來的 CPU 負擔。

## 下一步 (Next Steps)
掌握了底層結構後，下一章我們將探討 **Redis 的持久化機制 (Persistence: RDB & AOF)**。你將學習到底層結構如何被序列化到磁碟，以及 `fork()` 帶來的 Copy-on-Write 機制如何影響記憶體使用。

Having mastered the internal structures, in the next chapter we will explore **Redis Persistence Mechanisms (RDB & AOF)**. You will learn how these internal structures are serialized to disk and how the Copy-on-Write mechanism introduced by `fork()` affects memory usage.