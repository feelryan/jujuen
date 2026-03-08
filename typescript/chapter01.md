# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，TypeScript 不應僅僅是一個「帶有型別檢查的 JavaScript」或是一個「讓 IDE 更好用的工具」。要駕馭大型系統的複雜度，你需要掌握 TypeScript 的型別系統本質：它是基於結構的（Structural）、在執行時會消失的（Erased），並且遵循特定的變異性規則（Variance）。

For senior engineers, TypeScript should not merely be viewed as "JavaScript with type checking" or a tool for "better IDE autocompletion." To manage the complexity of large-scale systems, you need to master the essence of TypeScript's type system: it is **Structural**, **Erased** at runtime, and follows specific **Variance** rules.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **深刻理解 Structural Typing**：解釋為何兩個不同名稱的 Class 或 Interface 可以互相指派，並知道何時該利用此特性、何時該避免。
    **Deeply understand Structural Typing**: Explain why Classes or Interfaces with different names can be assigned to each other, and know when to leverage this feature and when to avoid it.
2.  **掌握 Type Erasure 的邊界**：清楚區分「編譯時」與「執行時」的行為差異，避免寫出依賴型別進行執行時邏輯的錯誤程式碼。
    **Master the boundaries of Type Erasure**: Clearly distinguish between "compile-time" and "runtime" behaviors, avoiding bugs caused by relying on types for runtime logic.
3.  **內化 Covariance 與 Contravariance**：直覺地理解為何 `Array<Dog>` 可以指派給 `Array<Animal>`，但 `(dog: Dog) => void` 卻不能指派給 `(animal: Animal) => void`，這對於設計高階函數（Higher-Order Functions）與泛型庫至關重要。
    **Internalize Covariance and Contravariance**: Intuitively understand why `Array<Dog>` is assignable to `Array<Animal>`, but `(dog: Dog) => void` is NOT assignable to `(animal: Animal) => void`—crucial for designing Higher-Order Functions and generic libraries.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Models)

### 2.1 集合論觀點 (The Set Theory Mental Model)

最適合資深工程師的心智模型是將型別視為「值的集合（Set of Values）」。
The most suitable mental model for senior engineers is to view types as **Sets of Values**.

-   **`never`**：空集合（Empty set）。沒有任何值屬於此集合。
    **`never`**: The empty set. No value belongs to this set.
-   **`unknown`**：全集合（Universal set）。所有值都包含在內。
    **`unknown`**: The universal set. It contains all possible values.
-   **`A extends B`**：意味著集合 A 是集合 B 的子集（Subset）。
    **`A extends B`**: Means set A is a subset of set B.

這種觀點能解釋為何 `type A = string | number` 比 `string` 更「寬」（更廣泛），以及為何 Intersection (`&`) 通常會產生更具體的型別（集合的交集）。
This perspective explains why `type A = string | number` is "wider" than `string`, and why Intersection (`&`) usually results in a more specific type (the intersection of sets).

### 2.2 Structural Typing vs. Nominal Typing

TypeScript 使用 **Structural Typing**（又稱 Duck Typing），這與 Java 或 C# 的 **Nominal Typing**（基於名稱）截然不同。
TypeScript uses **Structural Typing** (also known as Duck Typing), which is fundamentally different from the **Nominal Typing** (name-based) used in Java or C#.

-   **Nominal (Java/C#)**: 即使兩個類別結構完全相同，如果名稱不同，它們就是不同的型別。
    **Nominal (Java/C#)**: Even if two classes have the exact same structure, if their names are different, they are different types.
-   **Structural (TS)**: 只要形狀（屬性與方法）相容，它們就是同一個型別。
    **Structural (TS)**: As long as the shape (properties and methods) is compatible, they are considered the same type.

### 2.3 Type Erasure (型別抹除)

TypeScript 的型別系統是「零成本抽象（Zero-cost abstraction）」的一種形式，但更準確地說是「編譯後消失」。
TypeScript's type system is a form of "zero-cost abstraction," but more accurately, it "disappears after compilation."

這意味著你無法在執行時使用 `interface` 進行 `instanceof` 檢查，也無法在執行時讀取泛型參數 `T` 的具體型別。這與 C# 的 Reified Generics 不同。
This means you cannot use `instanceof` on an `interface` at runtime, nor can you reflect on the concrete type of a generic parameter `T` at runtime. This differs from Reified Generics in C#.

### 2.4 Variance (變異性)

這是設計複雜泛型系統時最常遇到的痛點。
This is the most common pain point when designing complex generic systems.

-   **Covariance (共變)**: 如果 `Dog extends Animal`，則 `List<Dog>` 也是 `List<Animal>` 的子型別。這適用於**輸出（Outputs）**或唯讀屬性。
    **Covariance**: If `Dog extends Animal`, then `List<Dog>` is a subtype of `List<Animal>`. This applies to **Outputs** or read-only properties.
-   **Contravariance (逆變)**: 如果 `Dog extends Animal`，則函數 `(a: Animal) => void` 是 `(d: Dog) => void` 的子型別（注意方向反轉了）。這適用於**輸入（Inputs）**。
    **Contravariance**: If `Dog extends Animal`, then the function `(a: Animal) => void` is a subtype of `(d: Dog) => void` (note the direction is reversed). This applies to **Inputs**.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

### 3.1 DTO 與跨服務通訊 (DTOs & Inter-service Communication)

在微服務架構中，我們常定義 DTO (Data Transfer Object)。由於 TypeScript 是 Structural Typing，你不需要在每個服務中共享同一個 npm package 裡的 Class 定義。只要 JSON 結構符合介面定義，系統就能正常運作。
In a microservices architecture, we often define DTOs (Data Transfer Objects). Because TypeScript is structurally typed, you don't need to share the exact Class definition from a shared npm package across every service. As long as the JSON structure matches the interface definition, the system works.

*   **優點**：解耦。Consumer 可以只定義它關心的欄位（Subset），只要 Producer 提供的資料包含這些欄位即可。
    **Pros**: Decoupling. The Consumer can define only the subset of fields it cares about, as long as the Producer provides data containing those fields.
*   **風險**：如果過度依賴隱式結構，當 Producer 改名欄位時，Consumer 可能在執行時才發現錯誤（若沒有完整的 End-to-End 測試）。
    **Risks**: If relying too heavily on implicit structures, the Consumer might only discover errors at runtime when the Producer renames a field (if there are no comprehensive End-to-End tests).

### 3.2 執行時驗證層 (Runtime Validation Layer)

由於 **Type Erasure**，TypeScript 無法防止來自外部 API 或資料庫的髒資料（Dirty Data）。在系統設計上，必須在邊界（Boundary）引入 Schema Validation 函式庫（如 Zod, io-ts, Ajv）。
Due to **Type Erasure**, TypeScript cannot prevent dirty data from external APIs or databases. In system design, you must introduce Schema Validation libraries (like Zod, io-ts, Ajv) at the boundaries.

**架構模式 (Architectural Pattern):**
`External Data (JSON)` -> `Zod Parse (Runtime Check)` -> `Typed Data (Static TS Type)` -> `Business Logic`

這確保了「一旦進入核心邏輯層，型別絕對可信」。
This ensures that "once inside the core logic layer, the types are absolutely trustworthy."

---

# 4. 逐步示例 (Walkthrough / Example)

### 案例：理解函數參數的逆變 (Understanding Function Argument Contravariance)

這是一個資深工程師在設計 Event Handler 或 Plugin 系統時常踩的坑。
This is a common pitfall for senior engineers when designing Event Handlers or Plugin systems.

#### 1. 基礎設定 (Setup)

我們定義一個簡單的層次結構：
Let's define a simple hierarchy:

```typescript
class Animal {
  move() { console.log("Moving"); }
}

class Dog extends Animal {
  bark() { console.log("Woof!"); }
}

// A generic type for a handler function
type Handler<T> = (item: T) => void;
```

#### 2. 問題情境 (The Problem)

假設我們有一個接受 `Handler<Dog>` 的函數。我們是否可以傳入一個 `Handler<Animal>`？反之亦然？
Suppose we have a function that accepts a `Handler<Dog>`. Can we pass a `Handler<Animal>`? Or vice versa?

```typescript
function acceptDogHandler(handler: Handler<Dog>) {
  const myDog = new Dog();
  handler(myDog); // This will execute the handler with a Dog
}

const animalHandler: Handler<Animal> = (animal: Animal) => {
  animal.move(); // Safe: All animals can move
};

const dogHandler: Handler<Dog> = (dog: Dog) => {
  dog.bark(); // Safe: Dogs can bark
};
```

#### 3. 分析與正確做法 (Analysis & Solution)

**情境 A：傳入 `animalHandler` 給 `acceptDogHandler`**
**Scenario A: Passing `animalHandler` to `acceptDogHandler`**

```typescript
// Is this safe?
acceptDogHandler(animalHandler);
```

**思考**：`acceptDogHandler` 內部會傳入一個 `Dog` 實例。`animalHandler` 預期接收一個 `Animal`。
**Thinking**: Inside `acceptDogHandler`, a `Dog` instance is passed. `animalHandler` expects an `Animal`.
因為 `Dog` 是一個 `Animal`，所以 `animalHandler` 可以安全地處理它。這是安全的。
Since `Dog` is an `Animal`, `animalHandler` can safely handle it. This is **Safe**.

**情境 B：反向操作 (The Reverse)**

假設有一個 `acceptAnimalHandler`：
Suppose we have an `acceptAnimalHandler`:

```typescript
function acceptAnimalHandler(handler: Handler<Animal>) {
  const genericAnimal = new Animal();
  handler(genericAnimal);
}

// Is this safe?
// acceptAnimalHandler(dogHandler); // Error!
```

**思考**：`acceptAnimalHandler` 內部可能會傳入一個普通的 `Animal`（不是 `Dog`）。但 `dogHandler` 預期接收 `Dog` 並呼叫 `dog.bark()`。
**Thinking**: Inside `acceptAnimalHandler`, a generic `Animal` (not a `Dog`) might be passed. But `dogHandler` expects a `Dog` and calls `dog.bark()`.
普通的 `Animal` 沒有 `bark` 方法。這會導致執行時錯誤（Runtime Crash）。
A generic `Animal` does not have a `bark` method. This would cause a **Runtime Crash**.

#### 4. 結論 (Conclusion)

這證明了函數參數是 **Contravariant（逆變）** 的。
This proves that function arguments are **Contravariant**.

-   雖然 `Dog extends Animal`，
    Although `Dog extends Animal`,
-   但是 `Handler<Animal>` extends `Handler<Dog>`。
    `Handler<Animal>` extends `Handler<Dog>`.

在啟用 `strictFunctionTypes`（包含在 `strict: true` 中）時，TypeScript 會嚴格檢查這一點。
When `strictFunctionTypes` is enabled (included in `strict: true`), TypeScript strictly enforces this.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 誤用 `any` 逃避型別檢查 (Misusing `any` to Bypass Checks)

**錯誤 (Anti-pattern):** 使用 `any` 來解決複雜的型別錯誤。這會像病毒一樣擴散，破壞整個依賴鏈的型別安全。
**Anti-pattern:** Using `any` to solve complex type errors. This spreads like a virus, destroying type safety across the dependency chain.

**修正 (Fix):** 使用 `unknown` 並配合 Type Guards（型別守衛），或者使用 `// @ts-expect-error` 並附上註解說明為何這裡暫時無法通過檢查（至少這不會破壞型別推導）。
**Fix:** Use `unknown` with Type Guards, or use `// @ts-expect-error` with a comment explaining why the check fails (at least this doesn't break type inference).

### 5.2 模擬 Nominal Typing 的錯誤方式 (Incorrect Nominal Typing Simulation)

**錯誤 (Anti-pattern):** 依賴私有屬性 `private _name: string` 來區分結構相同的 Class。
**Anti-pattern:** Relying on private properties like `private _name: string` to distinguish structurally identical classes.

**修正 (Fix):** 使用 "Branded Types" (或稱 Opaque Types) 模式。
**Fix:** Use the "Branded Types" (or Opaque Types) pattern.

```typescript
// Branded Type Pattern
type UserId = string & { readonly __brand: unique symbol };
type OrderId = string & { readonly __brand: unique symbol };

const userId = "user_123" as UserId;
const orderId = "order_123" as OrderId;

// function processUser(id: UserId) { ... }
// processUser(orderId); // Compile Error! Safe.
```

### 5.3 忽略 Excess Property Checks 的限制 (Ignoring Limits of Excess Property Checks)

**陷阱 (Pitfall):** 認為 TypeScript 總是會阻止多餘的屬性。
**Pitfall:** Assuming TypeScript will always prevent excess properties.

```typescript
interface Point { x: number; y: number; }

const p1 = { x: 1, y: 2, z: 3 }; // Object literal
const p: Point = p1; // No Error! Structural typing allows extra fields via reference.
```

**解釋**: Object Literal 直接賦值時會有特殊檢查（Excess Property Check），但透過變數傳遞時，只要滿足結構（包含 x 和 y）即可。這在處理 API payload 時需特別注意，不要以為型別定義了就能過濾掉多餘欄位。
**Explanation**: Object literals get a special "Excess Property Check" on direct assignment. However, when assigned via a variable reference, as long as the structure is satisfied (has x and y), it passes. Be careful with API payloads; types do not filter out extra fields at runtime.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 請解釋 TypeScript 的 Type Erasure 對系統架構有什麼影響？
**Q1: Explain the impact of TypeScript's Type Erasure on system architecture.**

*   **高分回答要點 (Key Points)**:
    *   編譯後的程式碼不包含介面或型別資訊，因此無法在執行時依賴 TS 型別進行邏輯判斷。
    *   必須引入執行時驗證（如 Zod/Joi）來處理 I/O 邊界（API 請求、DB 讀取）。
    *   這與 Java/C# 的 Reflection 機制不同，影響了依賴注入（DI）容器的實作方式（通常需要 Token 或 Decorator metadata）。

### Q2: 為什麼 TypeScript 的函數參數是 Contravariant（逆變）的，而回傳值是 Covariant（共變）的？
**Q2: Why are function arguments Contravariant in TypeScript, while return values are Covariant?**

*   **高分回答要點 (Key Points)**:
    *   **Liskov Substitution Principle (LSP)**：子型別必須能替換父型別。
    *   對於回傳值（Producer），如果函數承諾回傳 `Animal`，它實際回傳 `Dog` 是安全的（使用者能處理 `Animal` 就能處理 `Dog`）。
    *   對於參數（Consumer），如果函數需要處理 `Dog`，你不能給它一個只能處理 `Animal` 的函數（因為該函數可能無法處理 `Dog` 特有的行為）。反之，給它一個能處理所有 `Animal` 的函數是安全的。

### Q3: 什麼是 Branded Types（或 Tagged Types），在什麼場景下你會使用它？
**Q3: What are Branded Types (or Tagged Types), and in what scenarios would you use them?**

*   **高分回答要點 (Key Points)**:
    *   Branded Types 用於在 Structural Typing 系統中模擬 Nominal Typing。
    *   場景：防止相同原始型別（如 `string` 或 `number`）的錯誤混用。例如：區分 `USD` 與 `EUR` 金額，或 `UserId` 與 `Email`。
    *   實作：透過 Intersection Type (`&`) 加上一個虛擬的 unique symbol 屬性。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)

1.  **Structural Typing**: TypeScript 關注的是形狀（Shape）而非名稱。如果它走起來像鴨子，它就是鴨子。
    **Structural Typing**: TypeScript cares about Shape, not Name. If it walks like a duck, it is a duck.
2.  **Type Erasure**: 型別在編譯後完全消失。不要依賴型別做執行時檢查。
    **Type Erasure**: Types disappear completely after compilation. Do not rely on types for runtime checks.
3.  **Variance**: 記住「輸入逆變（Contravariant），輸出共變（Covariant）」。這保證了函數替換的安全性。
    **Variance**: Remember "Inputs are Contravariant, Outputs are Covariant." This ensures the safety of function substitution.
4.  **Strictness**: `strictFunctionTypes` 是資深開發者必須開啟的選項，它能捕捉潛在的函數指派錯誤。
    **Strictness**: `strictFunctionTypes` is a must-have option for senior developers; it catches potential function assignment errors.
5.  **Boundaries**: 在系統邊界（API, DB）必須使用執行時驗證庫（Zod 等），因為 TS 無法保護那裡。
    **Boundaries**: Runtime validation libraries (Zod, etc.) must be used at system boundaries (API, DB) because TS cannot protect you there.

### 後續延伸 (Next Steps)

*   **下一章預告**: 掌握了型別系統的行為後，下一章我們將探討 **Advanced Generics & Utility Types**，學習如何編寫可重用且靈活的工具型別。
    **Next Chapter**: Having mastered the behavior of the type system, next we will explore **Advanced Generics & Utility Types**, learning how to write reusable and flexible utility types.
*   **建議練習**: 嘗試重構一個舊專案，將所有 `any` 替換為 `unknown` 或具體型別，並引入 Zod 進行 API 回傳值的驗證。
    **Suggested Practice**: Try refactoring an old project by replacing all `any` with `unknown` or concrete types, and introduce Zod for validating API responses.