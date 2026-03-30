# 集合框架 (Collections) 底層與選型 / Collections Framework Deep Dive and Selection

## Mental model｜心智模型

在現代 Java 開發中，選擇集合框架不再只是單純比較時間複雜度（Big-O notation），更重要的是**硬體同理心（Mechanical Sympathy）**與**底層資料結構的擴容成本**。
In modern Java development, choosing a collection framework is no longer just about comparing time complexity (Big-O notation). It's more about **Mechanical Sympathy** and the **resizing costs of underlying data structures**.

1. **連續記憶體 vs. 節點指標 (Contiguous Memory vs. Node Pointers)**
   現代 CPU 高度依賴快取（L1/L2/L3 Cache）。`ArrayList` 底層是連續陣列，能完美利用 CPU Cache Prefetching（預取機制）；而 `LinkedList` 的節點散落在記憶體各處，會導致嚴重的 Cache Miss。這就是為什麼在實務中，即使是從中間插入元素，`ArrayList` 往往還是比 `LinkedList` 快。
   Modern CPUs rely heavily on caches (L1/L2/L3). `ArrayList` is backed by a contiguous array, perfectly utilizing CPU Cache Prefetching. `LinkedList` nodes are scattered across memory, causing severe Cache Misses. This is why in practice, even for middle insertions, `ArrayList` is often faster than `LinkedList`.

2. **擴容的隱藏成本 (The Hidden Cost of Resizing)**
   集合的「無限增長」是一種錯覺。當 `ArrayList` 滿載時，它需要分配一個大 1.5 倍的新陣列並複製資料（`System.arraycopy`）；當 `HashMap` 滿載（達到 Load Factor 0.75）時，它需要分配兩倍大的陣列並重新計算所有元素的雜湊位置（Rehashing）。這些操作在資料量大時極度消耗 CPU 與記憶體。
   The "infinite growth" of collections is an illusion. When an `ArrayList` is full, it allocates a new array 1.5x the size and copies data (`System.arraycopy`). When a `HashMap` is full (reaches Load Factor 0.75), it allocates a 2x larger array and recalculates the hash positions of all elements (Rehashing). These operations are extremely CPU and memory-intensive for large datasets.

3. **HashMap 的進化 (The Evolution of HashMap)**
   在 Java 8 之後，`HashMap` 的 Bucket 發生嚴重碰撞時（預設超過 8 個元素），會從單向鏈結串列（Linked List）轉換為紅黑樹（Red-Black Tree），將最壞情況的查詢時間從 O(N) 降至 O(log N)，以防止 Hash 碰撞的阻斷服務攻擊（DoS）。
   Since Java 8, when a `HashMap` bucket experiences severe collisions (default > 8 elements), it transforms from a Linked List to a Red-Black Tree, reducing the worst-case lookup time from O(N) to O(log N) to prevent Hash Collision Denial of Service (DoS) attacks.

---

## Patterns & best practices｜常見模式與最佳實務

- **預先分配容量 (Pre-size Collections)**
  如果你已知資料的大致數量，永遠在初始化時指定容量。這能完全消除擴容帶來的效能損耗。
  If you know the approximate number of elements, always specify the capacity during initialization. This completely eliminates the performance penalty of resizing.
  ```java
  // Good: Pre-sizing an ArrayList
  List<User> users = new ArrayList<>(10000); 

  // Good: Pre-sizing a HashMap (Java 19+)
  Map<String, User> userMap = HashMap.newHashMap(10000);
  
  // Good: Pre-sizing a HashMap (Pre-Java 19)
  // Formula: expectedSize / loadFactor(0.75) + 1
  Map<String, User> userMap = new HashMap<>((int)(10000 / 0.75f) + 1);
  ```

- **預設使用 ArrayList (Default to ArrayList)**
  除非你有極度明確的理由（例如實作特定的 Queue），否則 List 的首選永遠是 `ArrayList`。
  Unless you have an extremely specific reason (e.g., implementing a specific Queue), your first choice for a List should always be `ArrayList`.

- **使用 ArrayDeque 取代 Stack 與 LinkedList (Use ArrayDeque over Stack and LinkedList)**
  當你需要 LIFO（堆疊）或 FIFO（佇列）時，使用 `ArrayDeque`。傳統的 `Stack` 類別繼承自 `Vector`，帶有不必要的同步鎖（Synchronized）；而 `LinkedList` 記憶體開銷過大。
  When you need LIFO (Stack) or FIFO (Queue), use `ArrayDeque`. The legacy `Stack` class extends `Vector` and carries unnecessary synchronization locks, while `LinkedList` has excessive memory overhead.

- **善用不可變集合 (Leverage Immutable Collections)**
  對於唯讀的資料字典或配置，使用 Java 9+ 提供的 `List.of()`, `Set.of()`, `Map.of()`。它們不僅語法簡潔，底層實作也比標準集合更節省記憶體，且能防止意外修改。
  For read-only data dictionaries or configurations, use Java 9+ `List.of()`, `Set.of()`, `Map.of()`. They are not only concise but also more memory-efficient under the hood than standard collections and prevent accidental modifications.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

- **❌ 盲目使用 LinkedList (Blindly using LinkedList)**
  **Pitfall:** 以為「經常需要插入/刪除」就該用 `LinkedList`。實際上，`LinkedList` 每個節點都需要額外的物件標頭（Object Header）與前後指標，極度浪費記憶體，且 Cache Locality 極差。
  **Pitfall:** Thinking "frequent inserts/deletes" means you should use `LinkedList`. In reality, every `LinkedList` node requires an extra Object Header and next/prev pointers, wasting memory and suffering from terrible Cache Locality.

- **❌ 可變物件作為 Map 的 Key (Mutable Objects as Map Keys)**
  **Pitfall:** 將物件放入 `HashMap` 或 `HashSet` 後，修改了參與 `hashCode()` 計算的屬性。這會導致該物件在 Map 中「永久迷失」，造成記憶體洩漏（Memory Leak）。
  **Pitfall:** Modifying properties involved in `hashCode()` calculation after an object is put into a `HashMap` or `HashSet`. This causes the object to be "permanently lost" in the Map, leading to a Memory Leak.
  ```java
  // Anti-pattern
  Point p = new Point(1, 2);
  Set<Point> set = new HashSet<>();
  set.add(p);
  p.setX(10); // ❌ The hashcode changed! set.contains(p) will now return false.
  ```

- **❌ 在大型 List 中頻繁呼叫 `contains()` (Frequent `contains()` on large Lists)**
  **Pitfall:** `ArrayList.contains()` 是 O(N) 的線性掃描。如果資料量大且需要頻繁檢查元素是否存在，應該先將其轉換為 `HashSet` O(1)。
  **Pitfall:** `ArrayList.contains()` is an O(N) linear scan. If the dataset is large and existence checks are frequent, convert it to a `HashSet` O(1) first.

- **❌ 錯誤的陣列轉集合操作 (Incorrect Array to Collection conversion)**
  **Pitfall:** 使用 `Arrays.asList(array)` 返回的是一個固定大小的視圖（Fixed-size view），呼叫 `.add()` 或 `.remove()` 會拋出 `UnsupportedOperationException`。
  **Pitfall:** `Arrays.asList(array)` returns a fixed-size view. Calling `.add()` or `.remove()` will throw an `UnsupportedOperationException`.
  ```java
  // Correct way to get a mutable list:
  List<String> list = new ArrayList<>(Arrays.asList(array));
  // Or in modern Java:
  List<String> list = new ArrayList<>(List.of(array));
  ```

---

## Checklists & workflows｜檢查清單與流程

### 集合選型決策樹 / Collection Selection Decision Tree

- [ ] **需要 Key-Value 對應？ (Need Key-Value mapping?)**
  - 無順序要求 (No order needed) ➡️ `HashMap`
  - 需保持插入順序 (Need insertion order) ➡️ `LinkedHashMap`
  - 需依 Key 排序 (Need sorted keys) ➡️ `TreeMap`
- [ ] **需要確保元素唯一性？ (Need uniqueness?)**
  - 無順序要求 (No order needed) ➡️ `HashSet`
  - 需保持插入順序 (Need insertion order) ➡️ `LinkedHashSet`
  - 需依元素排序 (Need sorted elements) ➡️ `TreeSet`
- [ ] **單純儲存元素，允許重複？ (Just storing elements, duplicates allowed?)**
  - 預設選擇 (Default choice) ➡️ `ArrayList`
  - 需要 LIFO/FIFO 操作 (Need LIFO/FIFO operations) ➡️ `ArrayDeque`

### 程式碼審查清單 / Code Review Checklist

- [ ] **Capacity Initialization:** 如果已知集合大小，是否已在建構子中指定初始容量？ (If the size is known, is the initial capacity specified in the constructor?)
- [ ] **Immutability:** 作為 `Map` Key 的物件，其類別是否為不可變（Immutable），或者其 `hashCode()` 與 `equals()` 依賴的欄位是否宣告為 `final`？ (Are objects used as `Map` keys immutable, or are the fields used in `hashCode()`/`equals()` declared `final`?)
- [ ] **Thread Safety:** 這個集合是否會被多個執行緒同時存取？如果是，是否已改用 `ConcurrentHashMap` 或 `CopyOnWriteArrayList`？ *(註：詳見並行集合章節)* (Will this collection be accessed by multiple threads? If so, have you switched to `ConcurrentHashMap` or `CopyOnWriteArrayList`? *(Note: See Concurrent Collections chapter)*)
- [ ] **Return Types:** API 的回傳型別是否盡可能使用介面（如 `List`, `Map`）而非實作類別（如 `ArrayList`, `HashMap`），以保留未來重構的彈性？ (Do API return types use interfaces (e.g., `List`, `Map`) instead of implementations (e.g., `ArrayList`, `HashMap`) to preserve refactoring flexibility?)

---

## Real-world examples｜實戰案例

### 案例 1：批次資料處理的效能優化 (Example 1: Performance Optimization in Batch Processing)

**場景 (Scenario):** 從資料庫撈取 100,000 筆訂單，並依據 `userId` 進行分組。
Fetching 100,000 orders from a database and grouping them by `userId`.

**優化前 (Before Optimization):**
```java
public Map<Long, List<Order>> groupOrdersByUser(List<Order> orders) {
    // ❌ Pitfall: Default HashMap capacity is 16. 
    // Inserting 100k elements will trigger rehashing ~13 times.
    Map<Long, List<Order>> userOrders = new HashMap<>();
    for (Order order : orders) {
        userOrders.computeIfAbsent(order.getUserId(), k -> new ArrayList<>())
                  .add(order);
    }
    return userOrders;
}
```

**優化後 (After Optimization):**
```java
public Map<Long, List<Order>> groupOrdersByUser(List<Order> orders) {
    // ✅ Best Practice: Pre-allocate Map capacity.
    // Assuming we know there are roughly 10,000 unique users.
    int expectedUsers = 10000;
    Map<Long, List<Order>> userOrders = HashMap.newHashMap(expectedUsers); // Java 19+
    
    for (Order order : orders) {
        // ✅ Best Practice: Pre-allocate List if average orders per user is known (e.g., 10)
        userOrders.computeIfAbsent(order.getUserId(), k -> new ArrayList<>(10))
                  .add(order);
    }
    return userOrders;
}
```

### 案例 2：使用 LinkedHashMap 實作簡易 LRU 快取 (Example 2: Simple LRU Cache using LinkedHashMap)

**場景 (Scenario):** 在不引入外部套件（如 Guava/Caffeine）的情況下，實作一個保留最近使用紀錄的記憶體快取（Least Recently Used Cache）。
Implementing an in-memory Least Recently Used (LRU) cache without introducing external libraries.

**實作 (Implementation):**
`LinkedHashMap` 提供了一個受保護的方法 `removeEldestEntry`，覆寫它就能輕鬆打造 LRU 快取。
`LinkedHashMap` provides a protected method `removeEldestEntry`. Overriding it easily creates an LRU cache.

```java
public class SimpleLRUCache<K, V> extends LinkedHashMap<K, V> {
    private final int maxCapacity;

    public SimpleLRUCache(int maxCapacity) {
        // initialCapacity, loadFactor, accessOrder (true for LRU, false for Insertion Order)
        super(maxCapacity, 0.75f, true);
        this.maxCapacity = maxCapacity;
    }

    @Override
    protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        // 當元素數量超過最大容量時，自動移除最舊（最少存取）的元素
        // Automatically remove the eldest (least recently accessed) element when capacity is exceeded
        return size() > maxCapacity;
    }
}

// Usage:
Map<String, String> cache = new SimpleLRUCache<>(3);
cache.put("A", "1");
cache.put("B", "2");
cache.put("C", "3");
cache.get("A");      // Access "A", moving it to the end (most recently used)
cache.put("D", "4"); // Triggers removal of "B" (eldest)
```