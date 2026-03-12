# 1. 前言與學習目標 (Introduction & Learning Goals)

對於資深工程師而言，JavaScript 的內建資料結構早已不限於 Array 與 Object。在處理高頻交易、大數據流（Streams）或長期運行的 Node.js 服務時，選擇正確的資料結構直接決定了系統的記憶體佔用與 CPU 效率。本章旨在超越基礎語法，深入探討 V8 引擎下的進階結構與演算法優化。

For senior engineers, JavaScript's built-in data structures extend far beyond Arrays and Objects. When dealing with high-frequency trading, large data streams, or long-running Node.js services, selecting the right data structure directly dictates system memory footprint and CPU efficiency. This chapter aims to go beyond basic syntax, diving deep into advanced structures and algorithmic optimizations under the V8 engine.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精準選擇 Map/Set 與 Object/Array**：理解 Hash Map 機制，並在需要頻繁增刪或非字串鍵值（Non-string Keys）的場景中做出正確決策。
    **Select Map/Set vs. Object/Array with precision**: Understand Hash Map mechanisms and make correct decisions for scenarios requiring frequent additions/deletions or non-string keys.
2.  **利用 WeakMap/WeakSet 管理記憶體**：在設計快取（Caching）或 DOM 關聯資料時，防止記憶體洩漏（Memory Leaks）。
    **Manage memory with WeakMap/WeakSet**: Prevent memory leaks when designing caches or associating data with DOM nodes.
3.  **實作高效的 Iterators 與 Generators**：處理無限序列或大型資料集，實現 Lazy Evaluation（惰性求值）以降低記憶體峰值。
    **Implement efficient Iterators and Generators**: Handle infinite sequences or large datasets, achieving Lazy Evaluation to reduce memory peaks.
4.  **運用 TypedArrays 優化二進位資料處理**：在 WebGL、WebAssembly 或 Node.js Buffer 操作中，提升數值運算效能。
    **Optimize binary data handling with TypedArrays**: Boost numerical computation performance in WebGL, WebAssembly, or Node.js Buffer operations.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 Map & Set：真正的 Hash 結構 (True Hash Structures)

在 ES6 之前，我們常濫用 Object 當作 Map。然而，Object 的鍵值僅限於 String 或 Symbol，且帶有 Prototype chain 的雜訊。
Before ES6, we often abused Objects as Maps. However, Object keys are restricted to Strings or Symbols and come with the noise of the Prototype chain.

-   **Mental Model**: `Map` 是一個有序的 Hash Map。它記住了插入順序（Insertion Order），這點與許多其他語言的 Hash Map 不同，使其非常適合實作 LRU Cache。
    **Mental Model**: `Map` is an ordered Hash Map. It remembers Insertion Order, unlike Hash Maps in many other languages, making it ideal for implementing LRU Caches.
-   **Set**: 數學上的集合，保證值的唯一性。底層實作類似 Map，但只有 Key 沒有 Value。
    **Set**: A mathematical set guaranteeing value uniqueness. Under the hood, it's implemented similarly to a Map, but with Keys only (no Values).

## 2.2 WeakMap & WeakSet：幽靈參考 (Ghost References)

這是資深面試中常考的記憶體管理概念。
This is a frequent topic in senior interviews regarding memory management.

-   **Concept**: `WeakMap` 的 Key 必須是 Object。它對 Key 的引用是「弱引用」（Weak Reference）。如果該 Object 在程式其他地方被回收（GC），那麼它在 WeakMap 中的對應項目也會自動消失。
    **Concept**: The Keys of a `WeakMap` must be Objects. It holds a "weak reference" to the Key. If that Object is garbage collected (GC) elsewhere in the program, its entry in the WeakMap automatically disappears.
-   **Analogy**: 想像你在圖書館的一本書（Object）上貼了一張便利貼（Value）。如果圖書館把這本書銷毀了，便利貼自然也就沒了，你不需要特地去撕掉它。
    **Analogy**: Imagine putting a sticky note (Value) on a library book (Object). If the library destroys the book, the sticky note is gone too; you don't need to manually remove it.

## 2.3 Generators & Iterators：拉取式流 (Pull-based Streams)

-   **Concept**: 傳統 Array 是「推（Push）」模式，一次將所有資料載入記憶體；Generator 是「拉（Pull）」模式，呼叫者要一個，生產者才算一個。
    **Concept**: Traditional Arrays use a "Push" model, loading all data into memory at once; Generators use a "Pull" model, where the producer computes a value only when the caller requests it.
-   **State Machine**: Generator 本質上是一個可暫停（Pause）與恢復（Resume）的狀態機。
    **State Machine**: A Generator is essentially a state machine that can be paused and resumed.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 高頻資料處理與快取 (High-Frequency Data Processing & Caching)

在設計後端服務的 In-memory Cache 時，`Map` 是首選。
When designing In-memory Caches for backend services, `Map` is the premier choice.

-   **效能 (Performance)**: 在頻繁增刪鍵值的情況下，`Map` 的效能通常優於 `Object`（V8 引擎優化）。
    **Performance**: For frequent addition and removal of keys, `Map` generally outperforms `Object` (V8 engine optimizations).
-   **LRU Cache**: 利用 `Map` 的插入順序特性，我們可以極低成本地實作 Least Recently Used 演算法，不需要額外的 Linked List 結構。
    **LRU Cache**: Leveraging the insertion order property of `Map`, we can implement the Least Recently Used algorithm with very low overhead, eliminating the need for an additional Linked List structure.

## 3.2 DOM Metadata 與私有資料 (DOM Metadata & Private Data)

在前端框架或 Library 設計中（例如 React 或 Vue 的內部機制），我們常需要將 metadata 綁定到 DOM 節點。
In frontend frameworks or library design (e.g., internal mechanisms of React or Vue), we often need to bind metadata to DOM nodes.

-   **Memory Leak Prevention**: 若使用普通 `Map` 或 `Object` 儲存 DOM 節點參考，當 DOM 被移除時，JS 端的引用會阻止 GC 回收該節點，導致 Memory Leak。使用 `WeakMap` 則完美解決此問題。
    **Memory Leak Prevention**: If using a standard `Map` or `Object` to store DOM node references, the JS-side reference prevents GC from collecting the node when it's removed from the DOM, causing a Memory Leak. `WeakMap` solves this perfectly.

## 3.3 大數據流式處理 (Large Data Stream Processing)

當需要處理 CSV 解析、Log 分析等大檔案（如 10GB+）時：
When processing large files like CSV parsing or Log analysis (e.g., 10GB+):

-   **Generators**: 使用 Generator 配合 Node.js Streams，可以逐行讀取並處理資料，將記憶體佔用維持在常數級別（O(1) space），而非 O(n)。
    **Generators**: Using Generators with Node.js Streams allows for line-by-line reading and processing, keeping memory usage at a constant level (O(1) space) rather than O(n).

---

# 4. 逐步示例 (Walkthrough / Example)

## 案例：實作 O(1) 的 LRU Cache (Implementing an O(1) LRU Cache)

這是一個經典的 System Design / Coding Interview 題目。目標是設計一個固定大小的 Cache，當滿了的時候，移除最久未被使用的項目。
This is a classic System Design / Coding Interview problem. The goal is to design a fixed-size cache that removes the least recently used item when full.

### Naive Approach (Array / Object)
使用 Array 儲存物件，每次存取都要遍歷 Array 找到項目並移動到尾端。
Using an Array to store objects. Every access requires traversing the Array to find the item and move it to the end.
-   **Time Complexity**: O(n) for `get` and `put`. (Too slow).

### Optimized Approach (Map)
利用 `Map.prototype.keys()` 返回的 Iterator 是按插入順序排列的特性。
Leveraging the fact that `Map.prototype.keys()` returns an Iterator based on insertion order.

-   **Logic**:
    1.  **Get**: 如果 Key 存在，先刪除再重新設定（Delete then Set）。這會將該 Key 移到 Map 的最後面（最新）。
    2.  **Put**: 如果 Key 已存在，先刪除。設定新值。如果 Size 超過限制，刪除 Map 的第一個 Key（最舊）。
    **Logic**:
    1.  **Get**: If the Key exists, delete it and re-set it. This moves the Key to the end of the Map (most recent).
    2.  **Put**: If the Key exists, delete it first. Set the new value. If Size exceeds the limit, delete the first Key in the Map (oldest).

```javascript
class LRUCache {
  constructor(capacity) {
    this.capacity = capacity;
    this.cache = new Map(); // Map preserves insertion order
  }

  /**
   * Get value by key
   * Time Complexity: O(1)
   */
  get(key) {
    if (!this.cache.has(key)) return -1;

    const value = this.cache.get(key);
    // Refresh: remove and re-insert to mark as most recently used
    this.cache.delete(key);
    this.cache.set(key, value);
    return value;
  }

  /**
   * Put key-value pair
   * Time Complexity: O(1)
   */
  put(key, value) {
    if (this.cache.has(key)) {
      this.cache.delete(key);
    }
    
    this.cache.set(key, value);

    // Evict least recently used if over capacity
    if (this.cache.size > this.capacity) {
      // The first key in the map is the oldest
      // Map.keys().next().value gives the first key
      const oldestKey = this.cache.keys().next().value;
      this.cache.delete(oldestKey);
    }
  }
}

// Usage
const lru = new LRUCache(2);
lru.put(1, 1);
lru.put(2, 2);
console.log(lru.get(1)); // returns 1, cache: {2=2, 1=1}
lru.put(3, 3);           // evicts key 2, cache: {1=1, 3=3}
console.log(lru.get(2)); // returns -1 (not found)
```

### 為什麼可行？ (Why it works?)
在 JavaScript 的 `Map` 規範中，迭代順序必須是插入順序。這使得我們不需要手動維護 Double Linked List 就能達到 O(1) 的效果。
In the JavaScript `Map` specification, iteration order must be insertion order. This allows us to achieve O(1) performance without manually maintaining a Double Linked List.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 誤用 Object 作為 Hash Map (Misusing Object as Hash Map)

-   **Anti-pattern**: `const map = {}; map[userInput] = value;`
-   **Why it's bad**:
    1.  **Prototype Pollution**: 如果 `userInput` 是 `"__proto__"`，可能會破壞整個應用程式的邏輯。
    2.  **Performance**: 對於頻繁增刪 Key 的操作，V8 對 `Map` 的優化優於 `Object`。
    3.  **Key Types**: Object Key 自動轉為字串，這在 Key 為物件或數字時會導致意外的碰撞（e.g., `obj[{}]` 和 `obj[{x:1}]` 是一樣的 key `"[object Object]"`）。
-   **Solution**: 預設使用 `Map`，除非你需要 JSON 序列化或固定的結構定義。

## 5.2 試圖遍歷 WeakMap (Trying to iterate over WeakMap)

-   **Anti-pattern**: 試圖使用 `for...of` 遍歷 `WeakMap` 或檢查其 `size`。
-   **Why it's bad**: `WeakMap` 是不可枚舉的（Non-enumerable）。由於 GC 的不確定性，無法保證當前有多少元素存在。
-   **Solution**: 如果需要遍歷，請使用普通的 `Map`；如果需要自動 GC，請接受無法遍歷的限制。

## 5.3 過度使用 TypedArrays (Overusing TypedArrays)

-   **Anti-pattern**: 在一般的商業邏輯中使用 `Int32Array` 來替代普通 Array，認為這樣會比較快。
-   **Why it's bad**: 雖然 `TypedArrays` 節省記憶體，但在普通 JS 運算中，轉換成本與缺乏彈性（固定長度）可能降低開發效率，且 V8 對普通 Array 的優化（Packed Arrays）已經非常高效。
-   **Solution**: 僅在處理 Binary Data、WebGL、Canvas 像素操作或極大量數值運算時使用 `TypedArrays`。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 請比較 JavaScript 中 Map 與 Object 的差異，並說明在什麼場景下你會選擇 Map？
**Compare Map and Object in JavaScript. In what scenarios would you choose Map?**

-   **Key Points**:
    -   **Keys**: Map 支援任意型別（包括 Object），Object 僅支援 String/Symbol。
    -   **Order**: Map 保證插入順序，Object 的順序在舊版瀏覽器或特定情況下不可靠（雖然現代 ES 規範已定義順序，但 Map 更直觀）。
    -   **Performance**: Map 在頻繁增刪（add/remove）場景下效能較佳。
    -   **Prototype**: Map 是乾淨的（無 prototype chain 干擾）。

## Q2: 解釋 WeakMap 的運作原理，並舉一個實際應用案例。
**Explain how WeakMap works and provide a real-world use case.**

-   **Key Points**:
    -   **Weak Reference**: Key 必須是 Object，且不計入 Garbage Collection 的引用計數。
    -   **Use Case**: 儲存 DOM 節點的額外資料（如 Event Listeners 或 Metadata），當節點從 DOM 樹移除時，資料自動釋放，防止 Memory Leak。
    -   **Privacy**: 用於模擬 Class 的私有屬性（在 `#private` 語法出現前）。

## Q3: 什麼是 Generator？它如何幫助處理無限序列或大型資料集？
**What is a Generator? How does it help in processing infinite sequences or large datasets?**

-   **Key Points**:
    -   **Lazy Evaluation**: 資料是「被要求時」才計算產生的，而非一次性產生。
    -   **Memory Efficiency**: 處理 1GB 的 Log 檔時，不需要一次讀入 RAM，而是用 `yield` 逐行回傳。
    -   **Control Flow**: 可暫停與恢復執行，是 `async/await` 的底層基礎。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)
1.  **Map > Object**: 對於動態 Key、非字串 Key 或需要頻繁增刪的 Hash 結構，優先使用 `Map`。
2.  **WeakMap for Memory Safety**: 在關聯資料到 Objects（如 DOM 節點）時，使用 `WeakMap` 避免記憶體洩漏。
3.  **Generators for Streams**: 使用 Generator 處理大型資料集或無限序列，實現 O(1) 的記憶體佔用。
4.  **TypedArrays for Binary**: 在處理 Buffer、WebGL 或底層二進位協定時，使用 `TypedArrays`。
5.  **Complexity Awareness**: 理解 `Map.prototype.delete` + `set` 的組合技可達成 O(1) 的 LRU 更新。

## 後續延伸 (Next Steps)
-   **非同步模式 (Asynchronous Patterns)**: 既然掌握了 Generator，下一章應深入探討 `Async Iterators` (`for await...of`)、Promise 的內部實作以及 Event Loop 的微任務（Microtask）佇列機制。
-   **V8 記憶體分析**: 學習使用 Chrome DevTools 的 Memory Profiler 來驗證 `WeakMap` 的 GC 行為。