# 泛型 (Generics) 與通配符實務 / Generics and Wildcards in Practice

## Mental model｜心智模型

泛型在 Java 中經常讓開發者感到困惑，因為它的運作方式與 C++ 的 Templates 或 C# 的 Generics 截然不同。要駕馭 Java 泛型，你需要建立兩個核心心智模型：
Generics in Java often confuse developers because they work very differently from C++ Templates or C# Generics. To master Java generics, you need to build two core mental models:

**1. 編譯期的安全網與型別擦除 (Compile-time Safety Net & Type Erasure)**
Java 的泛型純粹是**編譯期 (Compile-time)** 的幻覺。為了與舊版 Java 保持向後相容，編譯器會在編譯時將泛型資訊「擦除」(Type Erasure)，替換為 `Object` 或其上限型別 (Bound)，並在需要的地方自動補上轉型 (Casting) 程式碼。
Java generics are purely a **compile-time** illusion. To maintain backward compatibility with older Java versions, the compiler "erases" generic information at compile time (Type Erasure), replacing it with `Object` or its bound, and automatically inserts casting code where necessary.
*   **實務意義 / Practical Implication:** 在執行期 (Runtime)，`List<String>` 和 `List<Integer>` 是完全相同的類別 (`ArrayList.class`)。你無法在執行期使用 `instanceof` 檢查泛型型別，這也是為什麼 JSON 反序列化時經常需要傳遞 `TypeReference` 的原因。
    At runtime, `List<String>` and `List<Integer>` are exactly the same class (`ArrayList.class`). You cannot use `instanceof` to check generic types at runtime, which is why JSON deserialization often requires passing a `TypeReference`.

**2. 資料流向與 PECS 原則 (Data Flow & The PECS Principle)**
當你設計 API 並考慮使用通配符 (`?`) 時，請專注於「資料的流向」。
When designing APIs and considering wildcards (`?`), focus on the "direction of data flow".
*   **Producer `Extends` (PE):** 如果你的方法需要從集合中**讀取**資料（集合是資料的生產者），請使用 `? extends T`。
    If your method needs to **read** data from a collection (the collection produces data for you), use `? extends T`.
*   **Consumer `Super` (CS):** 如果你的方法需要將資料**寫入**集合中（集合是資料的消費者），請使用 `? super T`。
    If your method needs to **write** data into a collection (the collection consumes your data), use `? super T`.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 嚴格在 API 邊界套用 PECS (Strictly Apply PECS at API Boundaries)
在設計函式庫或共用元件時，方法參數應盡可能寬容。使用 PECS 可以最大化 API 的靈活性。
When designing libraries or shared components, method parameters should be as forgiving as possible. Using PECS maximizes API flexibility.

```java
// Good: 支援將 List<Integer> 複製到 List<Number>
// Good: Supports copying List<Integer> to List<Number>
public static <T> void copyData(List<? extends T> source, List<? super T> destination) {
    for (T item : source) {
        destination.add(item);
    }
}
```

### 2. 優先使用泛型方法而非通配符 (Favor Generic Methods Over Wildcards)
如果型別參數在方法的多個參數之間，或者參數與回傳值之間存在依賴關係，請使用具名的泛型參數 (`<T>`)，而不是通配符 (`?`)。
If there is a dependency between multiple parameters, or between a parameter and the return type, use a named generic parameter (`<T>`) instead of a wildcard (`?`).

```java
// Bad: 型別關係遺失，回傳的 List 只能是 List<?>
// Bad: Type relationship is lost, returned List can only be List<?>
public static List<?> merge(List<?> list1, List<?> list2) { ... }

// Good: 明確宣告 T，確保輸入與輸出的型別一致性
// Good: Explicitly declare T to ensure type consistency between input and output
public static <T> List<T> merge(List<T> list1, List<T> list2) { ... }
```

### 3. 使用遞迴型別限制 (Recursive Type Bounds for Fluent APIs)
在設計 Builder 模式或需要方法鏈 (Method Chaining) 的繼承體系時，使用 `<T extends Comparable<T>>` 或 `<T extends Builder<T>>` 來確保子類別回傳正確的型別。
When designing Builder patterns or inheritance hierarchies that require method chaining, use bounds like `<T extends Comparable<T>>` or `<T extends Builder<T>>` to ensure subclasses return the correct type.

```java
public abstract class BaseBuilder<T extends BaseBuilder<T>> {
    public T withName(String name) {
        // ... logic
        return self(); // 透過 self() 回傳正確的子類型 / Return correct subtype via self()
    }
    protected abstract T self();
}
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 回傳通配符型別 (Returning Wildcard Types)
**反模式：** 方法的回傳型別宣告為 `List<? extends User>`。
**Anti-pattern:** Declaring method return types as `List<? extends User>`.
*   **後果 / Consequence:** 這會將處理通配符的負擔強加給呼叫者 (Caller)，導致呼叫端程式碼充滿編譯錯誤或需要強制轉型。
    This forces the burden of dealing with wildcards onto the caller, leading to compile errors or forced casting in the client code.
*   **解法 / Solution:** 回傳確切的型別，例如 `List<User>`。通配符只應該出現在方法的**輸入參數**中。
    Return exact types, like `List<User>`. Wildcards should only appear in method **input parameters**.

### 2. 濫用原生型別 (Using Raw Types)
**反模式：** 為了貪圖方便或相容舊程式碼，直接使用 `List` 而不是 `List<Object>` 或 `List<?>`。
**Anti-pattern:** Using `List` instead of `List<Object>` or `List<?>` for convenience or legacy compatibility.
*   **後果 / Consequence:** 原生型別會完全關閉編譯器的泛型檢查，導致執行期拋出 `ClassCastException`。
    Raw types completely disable the compiler's generic checks, leading to `ClassCastException` at runtime.
*   **解法 / Solution:** 如果真的不知道型別，請使用無界通配符 `List<?>`。它依然保有型別安全性（例如你不能隨意 `add` 元素進去）。
    If you truly don't know the type, use the unbounded wildcard `List<?>`. It still maintains type safety (e.g., you cannot arbitrarily `add` elements to it).

### 3. 泛型與陣列的衝突 (Heap Pollution with Generic Arrays)
**踩雷點：** 嘗試建立泛型陣列 `new T[10]` 或 `new List<String>[10]` 會導致編譯錯誤。但使用可變參數 (Varargs) 時，編譯器會隱式建立陣列，可能導致 Heap Pollution。
**Pitfall:** Attempting to create generic arrays like `new T[10]` or `new List<String>[10]` causes compile errors. However, using Varargs implicitly creates an array, which can lead to Heap Pollution.
*   **解法 / Solution:** 盡量使用 `List<T>` 代替陣列。如果必須使用泛型可變參數，確保方法內部不會修改該陣列，並加上 `@SafeVarargs` 註解。
    Prefer `List<T>` over arrays. If you must use generic varargs, ensure the method doesn't modify the array internally and annotate it with `@SafeVarargs`.

---

## Checklists & workflows｜檢查清單與流程

### 通配符決策樹 (Wildcard Decision Tree)
當你在方法參數中猶豫要填什麼型別時，請遵循此流程：
When hesitating about what type to use for a method parameter, follow this workflow:

1.  **這個參數只用來提供資料給方法讀取嗎？ (Is this parameter only providing data for the method to read?)**
    *   👉 是：使用 `? extends T` (Producer)。
2.  **這個參數只用來接收方法寫入的資料嗎？ (Is this parameter only receiving data written by the method?)**
    *   👉 是：使用 `? super T` (Consumer)。
3.  **這個參數既要被讀取，又要被寫入嗎？ (Is this parameter both read from and written to?)**
    *   👉 是：使用精確型別 `T`，不要使用通配符。
4.  **你完全不在乎集合裡裝什麼型別，只呼叫與型別無關的方法（如 `size()`, `clear()`）嗎？ (Do you completely not care about the type, only calling type-independent methods like `size()`, `clear()`?)**
    *   👉 是：使用無界通配符 `?`。

### Code Review 檢查清單 (Code Review Checklist)
- [ ] 我已經確認程式碼中沒有使用任何原生型別 (Raw Types，例如單獨的 `Map` 或 `List`)。 / I have verified there are no Raw Types used in the code.
- [ ] API 的回傳值沒有包含通配符 (例如沒有回傳 `Set<? extends Entity>`)。 / API return types do not contain wildcards.
- [ ] 針對集合參數，我已經根據 PECS 原則套用了正確的通配符，以提升 API 靈活性。 / For collection parameters, I have applied correct wildcards based on PECS to improve API flexibility.
- [ ] 所有的 `@SuppressWarnings("unchecked")` 都有加上註解說明為何在此處是安全的。 / All `@SuppressWarnings("unchecked")` annotations are accompanied by comments explaining why it is safe.

---

## Real-world examples｜實戰案例

### 案例 1：JSON 反序列化與 TypeReference (JSON Deserialization & TypeReference)
由於型別擦除，像 Jackson 或 Gson 這樣的 JSON 庫在反序列化泛型集合時會遇到困難。它們無法在執行期知道 `List<T>` 中的 `T` 是什麼。
Due to Type Erasure, JSON libraries like Jackson or Gson struggle when deserializing generic collections. They cannot know what `T` is in `List<T>` at runtime.

**實戰解法：使用匿名子類別保留泛型資訊 (Practical Solution: Using anonymous subclasses to retain generic info)**

```java
// 反模式：執行期 T 被擦除，Jackson 會反序列化成 List<LinkedHashMap>
// Anti-pattern: T is erased at runtime, Jackson deserializes into List<LinkedHashMap>
List<User> users = objectMapper.readValue(jsonString, List.class); 

// 最佳實踐：利用 TypeReference (Super Type Token 模式)
// Best Practice: Utilize TypeReference (Super Type Token pattern)
// 透過建立匿名子類別 {}，編譯器會將泛型資訊編譯進子類別的 metadata 中
// By creating an anonymous subclass {}, the compiler bakes the generic info into the subclass metadata
List<User> users = objectMapper.readValue(
    jsonString, 
    new com.fasterxml.jackson.core.type.TypeReference<List<User>>() {}
);
```

### 案例 2：實作通用的過濾器/規格模式 (Generic Specification Pattern)
在 Spring Data JPA 或領域驅動設計 (DDD) 中，我們經常需要組合不同的查詢條件。PECS 原則在這裡非常關鍵。
In Spring Data JPA or Domain-Driven Design (DDD), we often need to combine different query conditions. The PECS principle is crucial here.

```java
public interface Specification<T> {
    boolean isSatisfiedBy(T item);

    // 為什麼使用 ? super T？
    // Why use ? super T?
    // 因為如果我們有一個 Specification<Animal>，它理應可以被用來過濾 Dog (Dog 是 Animal 的子類)。
    // Because if we have a Specification<Animal>, it should logically be usable to filter Dogs.
    // other 是一個 Consumer，它會消耗傳入的 T，所以用 super。
    // 'other' is a Consumer that consumes the passed T, hence 'super'.
    default Specification<T> and(Specification<? super T> other) {
        return item -> this.isSatisfiedBy(item) && other.isSatisfiedBy(item);
    }
}

// 實戰應用 / Real-world application:
Specification<Dog> isGoldenRetriever = dog -> dog.getBreed().equals("Golden");
Specification<Animal> isHealthy = animal -> animal.getHealthScore() > 80;

// 完美編譯！我們將一個 Animal 的條件 (Consumer Super) 結合到 Dog 的條件上。
// Compiles perfectly! We combined an Animal condition (Consumer Super) onto a Dog condition.
Specification<Dog> healthyGolden = isGoldenRetriever.and(isHealthy);
```