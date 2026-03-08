# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，TypeScript 不僅僅是「加上型別註釋的 JavaScript」，它具備一套圖靈完備（Turing-complete）的型別系統。本章的目標是讓你從「型別的使用者」轉變為「型別的設計者」，特別是在開發共用函式庫（Shared Libraries）、SDK 或複雜業務邏輯時。

For senior engineers, TypeScript is more than just "JavaScript with types"; it possesses a Turing-complete type system. The goal of this chapter is to transition you from a "type consumer" to a "type designer," especially when developing shared libraries, SDKs, or complex business logic.

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **掌握進階泛型語法**：熟練使用 Conditional Types（條件型別）、Mapped Types（映射型別）與 Template Literal Types（樣板字面值型別）。
    **Master Advanced Generic Syntax**: Proficiently use Conditional Types, Mapped Types, and Template Literal Types.
2.  **運用 `infer` 關鍵字**：理解並實作型別推斷與提取（例如從 Promise 或函數回傳值中提取型別）。
    **Apply the `infer` Keyword**: Understand and implement type inference and extraction (e.g., extracting types from Promises or function return values).
3.  **閱讀與撰寫 Utility Types**：能夠從頭實作如 `Pick`, `Omit`, `Partial`, `ReturnType` 等內建工具型別，並創造自定義的複雜型別。
    **Read and Write Utility Types**: Be able to implement built-in utility types like `Pick`, `Omit`, `Partial`, `ReturnType` from scratch, and create custom complex types.
4.  **提升 API 設計的安全性**：利用型別系統在編譯時期捕捉邏輯錯誤（如路由參數檢查、權限矩陣驗證）。
    **Enhance API Design Safety**: Leverage the type system to catch logic errors at compile-time (such as router parameter checks or permission matrix validation).

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

在進入「型別體操（Type Gymnastics）」之前，必須建立一個核心的心智模型：**TypeScript 的型別系統本身就是一種函數式程式語言，它在編譯時期（Compile-time）執行。**

Before diving into "Type Gymnastics," we must establish a core mental model: **The TypeScript type system is itself a functional programming language that executes at compile-time.**

### 2.1 型別即函數 (Types as Functions)

-   **泛型 (Generics)** 是函數的參數。
    **Generics** are function arguments.
-   **條件型別 (Conditional Types)** 是 `if/else` 邏輯。
    **Conditional Types** are `if/else` logic.
-   **映射型別 (Mapped Types)** 是迴圈與物件轉換（類似 `.map()`）。
    **Mapped Types** are loops and object transformations (similar to `.map()`).
-   **遞迴型別 (Recursive Types)** 是遞迴函數，用於處理巢狀結構。
    **Recursive Types** are recursive functions used to handle nested structures.

```typescript
// Mental Model Mapping
// --------------------

// Programming Logic:
// function isString(val) { return typeof val === 'string' ? 'yes' : 'no'; }
type IsString<T> = T extends string ? 'yes' : 'no';

// Programming Logic:
// const newObj = {}; for (const key in obj) { newObj[key] = transform(obj[key]); }
type Mapped<T> = { [K in keyof T]: T[K] }; // Basic identity map
```

### 2.2 關鍵語法定義 (Key Syntax Definitions)

#### Conditional Types & `infer`
這是型別運算的基礎。`infer` 就像是正則表達式（Regex）中的「捕獲群組（Capture Group）」，用於宣告一個待推斷的變數。

This is the foundation of type computation. `infer` acts like a "Capture Group" in Regular Expressions, used to declare a variable to be inferred.

```typescript
// If T extends Array<something>, let 'U' be that 'something', otherwise return T
type UnpackArray<T> = T extends Array<infer U> ? U : T;

type A = UnpackArray<string[]>; // string
type B = UnpackArray<number>;   // number
```

#### Template Literal Types
允許在型別層級進行字串拼接與模式比對，這在處理 API 路徑、CSS 類名或事件名稱時極為強大。

Allows string concatenation and pattern matching at the type level, which is incredibly powerful when handling API paths, CSS class names, or event names.

```typescript
type EventName<T extends string> = `on${Capitalize<T>}`;
type ClickEvent = EventName<'click'>; // "onClick"
```

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型系統設計中，我們不會為了炫技而使用複雜型別。我們使用它們是為了**將 Runtime 的不確定性轉移到 Compile-time 的確定性**。

In large-scale system design, we don't use complex types just to show off. We use them to **shift Runtime uncertainty to Compile-time certainty**.

### 3.1 典型應用場景 (Typical Use Cases)

1.  **Type-Safe API Clients / SDKs**:
    當你設計一個供全公司使用的 SDK 時，你希望使用者輸入 API 路徑後，自動提示該路徑需要的參數與回傳型別。
    When designing an SDK for company-wide use, you want users to get automatic hints for required parameters and return types after typing an API path.

2.  **Configuration Validation**:
    在 Infrastructure as Code (IaC) 工具（如 Pulumi 或 CDK 的封裝）中，確保設定檔的結構與依賴關係正確。
    In Infrastructure as Code (IaC) tools (like wrappers around Pulumi or CDK), ensuring the structure and dependencies of configuration files are correct.

3.  **Database ORM / Query Builders**:
    如 Prisma 或 TypeORM，利用映射型別將資料庫 Schema 自動轉換為 TypeScript 型別，確保 `select` 欄位與回傳物件完全匹配。
    Like Prisma or TypeORM, using mapped types to automatically convert database schemas into TypeScript types, ensuring `select` fields perfectly match the return object.

### 3.2 對系統品質的影響 (Impact on System Quality)

-   **可維護性 (Maintainability)**: 當後端 API 變更時，前端如果使用了由 OpenAPI 生成的進階型別，編譯會直接報錯，而不是等到運行時崩潰。
    **Maintainability**: When backend APIs change, if the frontend uses advanced types generated from OpenAPI, the compilation will fail immediately, rather than crashing at runtime.
-   **開發者體驗 (DX)**: 優秀的型別推斷能提供強大的 IntelliSense，減少查閱文件的時間。
    **Developer Experience (DX)**: Excellent type inference provides powerful IntelliSense, reducing time spent consulting documentation.

---

# 4. 逐步示例：型別安全的路由參數提取 (Walkthrough: Type-Safe Route Parameter Extraction)

### 情境 (Scenario)
我們需要實作一個 `navigate` 函數。我們希望當開發者輸入路徑字串（如 `/users/:id/posts/:postId`）時，TS 能自動要求開發者提供正確的參數物件 `{ id: string; postId: string }`。

We need to implement a `navigate` function. We want TS to automatically require the developer to provide the correct parameter object `{ id: string; postId: string }` when they input a path string (e.g., `/users/:id/posts/:postId`).

### Step 1: 基礎定義 (Basic Definition)
最直覺的做法是使用 `string` 和 `Record<string, string>`，但這沒有型別安全。

The most intuitive approach is using `string` and `Record<string, string>`, but this lacks type safety.

```typescript
function navigate(path: string, params: Record<string, string>) {
  // implementation...
}
// No error, but 'random' is not in the path!
navigate('/user/:id', { random: '123' }); 
```

### Step 2: 利用 Template Literals 與 infer 遞迴提取 (Recursive Extraction with Template Literals & infer)
我們需要撰寫一個工具型別，解析字串並提取以 `:` 開頭的部分。

We need to write a utility type that parses the string and extracts parts starting with `:`.

```typescript
// 1. Helper to check if string is a param (starts with :)
//    If S is ":id", returns "id". Otherwise returns never.
type RemoveColon<S> = S extends `:${infer R}` ? R : never;

// 2. Recursive parser
//    Split string by "/" and check each segment
type ExtractParams<Path extends string> = 
  // If Path matches "Start/Rest", split it
  Path extends `${infer Start}/${infer Rest}`
    ? (RemoveColon<Start> | ExtractParams<Rest>) // Recurse both sides
    : RemoveColon<Path>; // Base case: end of string

// Testing the type
type Params = ExtractParams<'/users/:id/posts/:postId'>; 
// Result: "id" | "postId"
```

### Step 3: 構建最終函數型別 (Building the Final Function Type)
現在我們將提取出的 Union Type 轉換為物件型別。

Now we convert the extracted Union Type into an object type.

```typescript
// Convert Union "id" | "postId" to { id: string; postId: string }
type RouteParams<P extends string> = {
  [K in ExtractParams<P>]: string;
};

// The function signature
function navigate<P extends string>(
  path: P, 
  params: RouteParams<P>
): void {
  console.log(`Navigating to ${path} with`, params);
}

// Usage
// ✅ Correct
navigate('/users/:id', { id: '123' });

// ❌ Error: Property 'postId' is missing
// navigate('/users/:id/posts/:postId', { id: '123' }); 

// ❌ Error: Object literal may only specify known properties, and 'wrong' does not exist
// navigate('/users/:id', { id: '123', wrong: 'oops' });
```

### 複雜度分析 (Complexity Analysis)
-   **編譯效能 (Compilation Performance)**: 這種遞迴型別在字串長度過長或巢狀過深時，可能會觸發 TS 的遞迴限制（Recursion Limit）。在實務中，路徑通常不會太長，所以是安全的。
    **Compilation Performance**: Such recursive types might trigger the TS Recursion Limit if the string is too long or nested too deeply. In practice, paths are usually not that long, so it is safe.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 聯合型別的分發特性 (Distributive Conditional Types)
這是資深工程師最常遇到的坑。當泛型 `T` 是一個 Union Type 時，`T extends U` 會對 Union 中的**每一個成員**單獨進行運算，然後將結果聯合起來。

This is the most common pitfall for senior engineers. When generic `T` is a Union Type, `T extends U` will operate on **each member** of the Union individually, and then union the results.

```typescript
type ToArray<T> = T extends any ? T[] : never;

type Result = ToArray<string | number>;
// Expectation: (string | number)[]
// Reality: string[] | number[]  <-- Distributed!
```

**解決方案 (Solution)**: 使用 Tuple `[]` 包裹泛型來禁止分發。
**Solution**: Wrap the generic in a Tuple `[]` to disable distribution.

```typescript
type ToArraySafe<T> = [T] extends [any] ? T[] : never;
type ResultSafe = ToArraySafe<string | number>; // (string | number)[]
```

### 5.2 過度工程化 (Over-Engineering / "Write-Only Types")
寫出極其複雜的型別體操，導致團隊其他成員無法理解或維護。
Writing extremely complex type gymnastics that make it impossible for other team members to understand or maintain.

-   **反模式**: 一個型別定義超過 20 行，且沒有任何註解。
    **Anti-pattern**: A type definition exceeding 20 lines without any comments.
-   **建議**: 將複雜型別拆解為小的、可命名的工具型別（如 `ExtractParams` 拆分為 `Split`, `Filter`, `Map` 等步驟）。
    **Recommendation**: Break down complex types into small, nameable utility types (e.g., split `ExtractParams` into `Split`, `Filter`, `Map` steps).

### 5.3 誤用 `any` 破壞泛型 (Misusing `any` breaks Generics)
在泛型約束中使用 `any` 會關閉型別檢查。應盡量使用 `unknown` 或具體的約束（如 `extends Record<string, unknown>`）。

Using `any` in generic constraints turns off type checking. Prefer `unknown` or specific constraints (like `extends Record<string, unknown>`).

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

這些問題可用於面試 Senior 候選人，或在團隊內進行技術分享討論。

These questions can be used to interview Senior candidates or for technical sharing discussions within the team.

### Q1: 請解釋 `infer` 關鍵字的作用，並舉一個實際例子。
**Please explain the role of the `infer` keyword and provide a real-world example.**

*   **高分回答要點**:
    *   說明 `infer` 只能在 Conditional Types 的 `extends` 子句中使用。
    *   類比為「宣告一個型別變數」供後續使用。
    *   實例：`ReturnType` 的實作，或從 `Promise<T>` 解包出 `T`，或從陣列提取元素型別。

### Q2: TypeScript 的內建工具型別 `Pick` 和 `Omit` 是如何實作的？
**How are TypeScript's built-in utility types `Pick` and `Omit` implemented?**

*   **高分回答要點**:
    *   `Pick<T, K>` 使用 Mapped Types: `{ [P in K]: T[P] }`。
    *   `Omit<T, K>` 使用 `Pick` 搭配 `Exclude`: `Pick<T, Exclude<keyof T, K>>`。
    *   這展示了候選人對 Key Remapping 和 Mapped Types 的理解。

### Q3: 你曾在專案中遇到過 TypeScript 編譯效能問題嗎？如何解決？
**Have you ever encountered TypeScript compilation performance issues in a project? How did you solve them?**

*   **高分回答要點**:
    *   提到過深的遞迴型別或過大的 Union Types 會導致編譯緩慢。
    *   解決方案包括：簡化型別邏輯、使用 `interface` 代替 `type`（在某些情況下 interface 緩存效能較好）、或將大型專案拆分為 Project References。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)
1.  **型別即邏輯**：TS 型別系統具備條件判斷、迴圈與變數賦值（`infer`）的能力。
    **Types as Logic**: The TS type system possesses capabilities for conditional judgment, loops, and variable assignment (`infer`).
2.  **`infer` 是手術刀**：用於精準提取複雜結構內部的型別資訊。
    **`infer` is a Scalpel**: Used to precisely extract type information from within complex structures.
3.  **Template Literal Types**：讓字串處理進入了型別檢查的領域，特別適合 API 與路由定義。
    **Template Literal Types**: Bring string manipulation into the realm of type checking, especially suitable for API and route definitions.
4.  **警惕分發特性**：處理 Union Types 時，務必確認是否需要 `[T]` 來禁止分發。
    **Beware of Distributivity**: When handling Union Types, always verify if `[T]` is needed to disable distribution.
5.  **可讀性至上**：型別體操是為了服務開發效率，而非增加認知負擔。
    **Readability First**: Type gymnastics serve development efficiency, not to increase cognitive load.

### 後續延伸 (Next Steps)
-   **進階閱讀**: 深入研究 `zod` 或 `type-fest` 等函式庫的原始碼，看看它們如何處理極端邊界情況。
    **Advanced Reading**: Deep dive into the source code of libraries like `zod` or `type-fest` to see how they handle extreme edge cases.
-   **下一章預告 (Chapter 03)**: **TypeScript Decorators & Metaprogramming**。我們將探討如何在執行時期（Runtime）利用 Metadata 進行依賴注入與驗證，這是許多後端框架（如 NestJS）的核心。
    **Next Chapter Preview (Chapter 03)**: **TypeScript Decorators & Metaprogramming**. We will explore how to use Metadata at Runtime for dependency injection and validation, which is the core of many backend frameworks (like NestJS).