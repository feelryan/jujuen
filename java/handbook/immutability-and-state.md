# 不可變性與狀態管理 / Immutability and State Management

## Mental model｜心智模型

在軟體工程中，**狀態（State）是一種負債**。當多個執行緒或模組共用並修改同一個物件的狀態時，系統的行為會變得難以預測，導致競爭條件（Race conditions）與難以重現的 Bug。

In software engineering, **state is a liability**. When multiple threads or modules share and modify the state of the same object, the system's behavior becomes unpredictable, leading to race conditions and hard-to-reproduce bugs.

不可變性（Immutability）的心智模型是：**將物件視為「值（Value）」，而不是「容器（Container）」。**
就像數字 `3` 永遠不會變成 `4`，如果你需要 `4`，你會產生一個新的數字。同理，不可變物件一旦被建立，其內部狀態就永遠不會改變。如果需要修改，我們不改變原物件，而是**建立並回傳一個包含新狀態的全新物件**。

The mental model for immutability is: **Treat objects as "Values", not "Containers".**
Just as the number `3` never changes into `4` (if you need `4`, you produce a new number), an immutable object's internal state never changes once created. If a modification is needed, we don't mutate the original object; instead, we **create and return a brand-new object with the updated state**.

**核心優勢 / Core Benefits:**
1. **Thread-Safety by Default (天生執行緒安全):** 沒有修改，就不需要鎖（Locks）。 / No mutation means no synchronization locks are needed.
2. **Side-Effect Free (無副作用):** 將物件傳遞給其他方法時，不必擔心它被偷偷修改。 / Passing objects to other methods carries zero risk of sneaky modifications.
3. **Cacheable (易於快取):** 不可變物件可以安全地被快取與共用。 / Immutable objects can be safely cached and shared.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. The "Final" Rule / 絕對的 Final 規則
將類別宣告為 `final` 以防止子類別覆寫方法並破壞不可變性；將所有欄位宣告為 `private final`，確保它們只能在建構子中被賦值一次。
Declare the class as `final` to prevent subclasses from overriding methods and breaking immutability. Declare all fields as `private final` to ensure they are assigned only once in the constructor.

### 2. Defensive Copying / 防禦性複製
當建構子接收可變物件（如 `java.util.Date`, `ArrayList`），或 Getter 需要回傳這些物件時，**絕對不要直接賦值或回傳原始參考**，必須建立副本。
When a constructor accepts mutable objects (like `java.util.Date`, `ArrayList`), or a getter returns them, **never assign or return the original reference directly**. You must create a copy.

### 3. "Wither" Methods / Wither 方法模式
不使用 Setter（`setXxx`），而是提供 `withXxx` 方法。這些方法會複製當前物件的所有狀態，僅替換掉需要修改的欄位，然後回傳新物件。
Instead of Setters (`setXxx`), provide `withXxx` methods. These methods copy all states of the current object, replace only the target field, and return a new instance.

### 4. Leverage Java Records / 善用 Java Records (Java 14+)
對於純粹的資料載體（Data Carriers），直接使用 `record`。它原生提供了不可變的欄位、建構子、`equals()`、`hashCode()` 與 `toString()`。
For pure data carriers, use `record`. It natively provides immutable fields, constructors, `equals()`, `hashCode()`, and `toString()`.

### 5. Truly Immutable Collections / 真正的不可變集合
使用 `List.of()`, `Set.of()`, `Map.of()` (Java 9+) 來建立集合，而不是 `Collections.unmodifiableList()`。
Use `List.of()`, `Set.of()`, `Map.of()` (Java 9+) to create collections, rather than `Collections.unmodifiableList()`.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### ❌ Shallow Immutability / 淺層不可變性
**問題 (Problem):** 類別與欄位都是 `final`，但欄位本身是一個可變物件（例如 `List<String>` 或 `HashMap`），且沒有進行防禦性複製。
The class and fields are `final`, but the field itself is a mutable object (e.g., `List<String>` or `HashMap`) without defensive copying.
**後果 (Consequence):** 外部呼叫者可以透過 Getter 取得該集合並呼叫 `.add()` 或 `.clear()`，神不知鬼不覺地改變了物件的內部狀態。
External callers can get the collection via a getter and call `.add()` or `.clear()`, silently mutating the object's internal state.

### ❌ Relying on `Collections.unmodifiableList()` / 誤用唯讀視圖當作不可變
**問題 (Problem):** `Collections.unmodifiableList(originalList)` 只是提供一個「唯讀視圖 (Read-only view)」。
`Collections.unmodifiableList(originalList)` only provides a "read-only view".
**後果 (Consequence):** 如果有人保留了 `originalList` 的參考並修改了它，這個「唯讀視圖」的內容也會跟著改變！請改用 `List.copyOf(originalList)`。
If someone holds a reference to `originalList` and modifies it, the contents of this "read-only view" will also change! Use `List.copyOf(originalList)` instead.

### ❌ Leaking `this` during Construction / 在建構期間洩漏 `this`
**問題 (Problem):** 在建構子尚未執行完畢前，就將 `this` 傳遞給其他監聽器或執行緒。
Passing `this` to other listeners or threads before the constructor has finished executing.
**後果 (Consequence):** 其他執行緒可能會看到一個「尚未完全初始化」的物件，破壞了 `final` 欄位的執行緒安全保證。
Other threads might see a "partially initialized" object, breaking the thread-safety guarantees of `final` fields.

---

## Checklists & workflows｜檢查清單與流程

在設計一個不可變類別時，請通過以下檢查：
When designing an immutable class, run through this checklist:

- [ ] **Class is `final`?** 類別是否宣告為 `final`？（或者建構子為 `private` 並提供靜態工廠方法）。
- [ ] **Fields are `private final`?** 所有狀態欄位是否都是 `private final`？
- [ ] **No Setters?** 是否已經移除了所有會改變內部狀態的方法（Setters）？
- [ ] **Defensive Copy In?** 建構子接收到陣列、集合或可變物件（如 `Date`）時，是否進行了深度複製（Deep copy）或使用了 `List.copyOf()`？
- [ ] **Defensive Copy Out?** Getter 回傳陣列、集合或可變物件時，是否回傳了副本或不可變集合（如 `Collections.unmodifiable...` 或 `List.copyOf()`）？
- [ ] **Modern API Alternative?** 是否能用現代且不可變的 API 替換舊 API？（例如：用 `java.time.Instant` 替換 `java.util.Date`）。
- [ ] **Record Candidate?** 這個類別是否可以直接宣告為 Java `record` 來減少樣板程式碼？

---

## Real-world examples｜實戰案例

### 案例一：傳統類別的防禦性複製演進 / Evolution of Defensive Copying

假設我們需要一個表示「促銷活動期間」的類別 `PromotionPeriod`。
Suppose we need a `PromotionPeriod` class representing a promotional timeframe.

**❌ Bad Example (Leaking state / 狀態外洩):**

```java
public class PromotionPeriod {
    private final Date startDate;
    private final Date endDate;

    public PromotionPeriod(Date startDate, Date endDate) {
        this.startDate = startDate; // Danger: Storing mutable reference directly
        this.endDate = endDate;
    }

    public Date getStartDate() {
        return startDate; // Danger: Returning mutable reference directly
    }
}

// 踩雷示範 / Pitfall demonstration:
Date start = new Date();
PromotionPeriod period = new PromotionPeriod(start, new Date());
start.setTime(start.getTime() + 9999999); // 💥 period 的內部狀態被改變了！ / period's internal state is mutated!
```

**✅ Good Example (Defensive Copying / 防禦性複製):**

```java
public final class PromotionPeriod {
    private final Date startDate;
    private final Date endDate;

    public PromotionPeriod(Date startDate, Date endDate) {
        // Defensive copy IN
        this.startDate = new Date(startDate.getTime());
        this.endDate = new Date(endDate.getTime());
    }

    public Date getStartDate() {
        // Defensive copy OUT
        return new Date(startDate.getTime());
    }
}
```

**🚀 Best Practice (Modern Immutable APIs / 現代不可變 API):**
放棄 `java.util.Date`，改用天生不可變的 `java.time` API。
Abandon `java.util.Date` and use the inherently immutable `java.time` API.

```java
import java.time.LocalDateTime;

public record PromotionPeriod(LocalDateTime startDate, LocalDateTime endDate) {
    public PromotionPeriod {
        if (startDate.isAfter(endDate)) {
            throw new IllegalArgumentException("Start date must be before end date");
        }
    }
}
// LocalDateTime 本身就是不可變的，加上 record，達到了完美的零樣板不可變性。
// LocalDateTime is immutable by itself. Combined with record, it achieves perfect zero-boilerplate immutability.
```

### 案例二：Wither 模式實作 / Implementing the "Wither" Pattern

當你需要更新不可變物件的某個屬性時，使用 `withXxx` 模式。
When you need to update a property of an immutable object, use the `withXxx` pattern.

```java
public final class ServerConfig {
    private final String host;
    private final int port;
    private final List<String> allowedIps;

    public ServerConfig(String host, int port, List<String> allowedIps) {
        this.host = host;
        this.port = port;
        // 確保集合不可變 / Ensure collection is immutable
        this.allowedIps = List.copyOf(allowedIps); 
    }

    // Wither method for port
    public ServerConfig withPort(int newPort) {
        // 回傳一個包含新 port 的全新物件，保留其他原有的狀態
        // Return a brand-new object with the new port, keeping other states intact
        return new ServerConfig(this.host, newPort, this.allowedIps);
    }
    
    // Getters...
}

// 使用方式 / Usage:
ServerConfig config = new ServerConfig("localhost", 8080, List.of("127.0.0.1"));
// config 本身不變，newConfig 獲得了新的 port
// config remains unchanged, newConfig gets the new port
ServerConfig newConfig = config.withPort(9090); 
```