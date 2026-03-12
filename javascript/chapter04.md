# 1. 前言與學習目標 (Introduction & Learning Objectives)

在資深工程師的職涯階段，程式碼的價值不僅在於「能跑」，更在於「可維護性」與「可測試性」。JavaScript 作為一門多範式（Multi-paradigm）語言，允許我們靈活混用物件導向（OOP）與函數式編程（FP）。本章的目標不是爭論哪種範式更好，而是探討如何結合兩者優勢，解決複雜的架構問題。

At the Senior Engineer career stage, the value of code lies not just in "working," but in "maintainability" and "testability." As a multi-paradigm language, JavaScript allows us to flexibly mix Object-Oriented Programming (OOP) and Functional Programming (FP). The goal of this chapter is not to debate which paradigm is superior, but to explore how to combine the strengths of both to solve complex architectural problems.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精準運用混合範式**：理解何時使用 OOP 封裝狀態，何時使用 FP（Currying, Composition）處理資料流。
    **Master Hybrid Paradigms**: Understand when to use OOP to encapsulate state and when to use FP (Currying, Composition) to handle data flow.
2.  **實踐經典設計模式**：在 JavaScript 中正確實作 Singleton, Observer, Factory 等模式，並理解 ES Modules 如何改變了 Singleton 的實作方式。
    **Implement Classic Design Patterns**: Correctly implement Singleton, Observer, and Factory patterns in JavaScript, and understand how ES Modules have changed the implementation of Singletons.
3.  **優化程式碼結構**：利用 Immutability（不可變性）與 Pure Functions（純函數）來降低系統副作用，提升單元測試的容易度。
    **Optimize Code Structure**: Leverage Immutability and Pure Functions to reduce system side effects and improve the ease of unit testing.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 OOP vs. FP：狀態管理 vs. 資料轉換
## 2.1 OOP vs. FP: State Management vs. Data Transformation

在 JavaScript 的心智模型中，我們可以這樣區分：
In the mental model of JavaScript, we can distinguish them as follows:

-   **OOP (Object-Oriented Programming)**：將「資料」與「行為」打包在一起。適合模擬有狀態的實體（如 `User`, `DatabaseConnection`）。核心在於**封裝（Encapsulation）**。
    **OOP**: Bundles "data" and "behavior" together. Suitable for modeling stateful entities (e.g., `User`, `DatabaseConnection`). The core is **Encapsulation**.
-   **FP (Functional Programming)**：將「資料」與「行為」分離。資料流經一系列函數管道（Pipeline）進行轉換。核心在於**不可變性（Immutability）**與**組合（Composition）**。
    **FP**: Separates "data" from "behavior." Data flows through a series of function pipelines for transformation. The core is **Immutability** and **Composition**.

> **Senior View**: 不要成為基本教義派。在 React 中，我們常看到 Component 是 FP 的（Function Components），但底層的狀態管理或複雜的業務邏輯 Service 可能是 OOP 的 Class。
> **Senior View**: Don't be a purist. In React, we often see Components as FP (Function Components), but the underlying state management or complex business logic Services might be OOP Classes.

## 2.2 關鍵 FP 概念 (Key FP Concepts)

### Currying (柯里化)
將一個接受多個參數的函數，轉換為一系列接受單一參數的函數。這在設定檔注入（Dependency Injection）或事件處理中非常有用。
Transforming a function that takes multiple arguments into a sequence of functions that each take a single argument. This is extremely useful in dependency injection or event handling.

```javascript
// Normal function
const add = (a, b) => a + b;

// Curried function
const curriedAdd = (a) => (b) => a + b;
const addFive = curriedAdd(5); // Partial application
console.log(addFive(10)); // 15
```

### Composition (函數組合)
將多個小函數組合成一個大函數，數據像流水線一樣經過處理。
Combining multiple small functions into one larger function, where data is processed like an assembly line.

### Immutability (不可變性)
不直接修改原始物件，而是返回一個新的修改後的副本。這是 Redux 等狀態管理庫的核心，能避免 Race Conditions 和難以追蹤的 Bug。
Instead of modifying the original object directly, return a new modified copy. This is the core of state management libraries like Redux, avoiding Race Conditions and hard-to-trace bugs.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型系統設計中，設計模式與範式決定了程式碼的**邊界（Boundaries）**與**耦合度（Coupling）**。
In large-scale system design, design patterns and paradigms determine the **boundaries** and **coupling** of the code.

## 3.1 Singleton Pattern：配置與連線池
## 3.1 Singleton Pattern: Config & Connection Pools

**場景 (Scenario)**：Database Client、Logger 實例、App Configuration。
**Scenario**: Database Client, Logger instance, App Configuration.

**實務演進 (Evolution)**：
早期的 JS 使用 IIFE (Immediately Invoked Function Expression) 來模擬 Singleton。在現代 Node.js 或 Frontend Build System (Webpack/Vite) 中，**ES Modules 本身就是 Singleton**。
Early JS used IIFE to simulate Singletons. In modern Node.js or Frontend Build Systems (Webpack/Vite), **ES Modules are Singletons by default**.

```javascript
// db.js
// This module is evaluated once. Subsequent imports share the same instance.
class Database {
  constructor() { /* connect */ }
}
export const db = new Database();
```

## 3.2 Observer Pattern：解耦微服務與模組
## 3.2 Observer Pattern: Decoupling Microservices & Modules

**場景 (Scenario)**：前端 UI 事件響應、Node.js 的 `EventEmitter`、分散式系統中的 Pub/Sub 機制。
**Scenario**: Frontend UI event response, Node.js `EventEmitter`, Pub/Sub mechanisms in distributed systems.

**系統觀點 (System View)**：
Observer 模式允許模組 A 觸發事件，而不需要知道模組 B、C、D 的存在。這極大提升了系統的可擴充性。
The Observer pattern allows Module A to trigger events without knowing the existence of Modules B, C, or D. This greatly enhances system scalability.

## 3.3 Factory Pattern：隱藏建立邏輯
## 3.3 Factory Pattern: Hiding Creation Logic

**場景 (Scenario)**：跨平台應用（根據環境回傳不同的 Logger 或 Storage 實作）、測試環境 Mocking。
**Scenario**: Cross-platform apps (returning different Logger or Storage implementations based on environment), Mocking in test environments.

---

# 4. 逐步示例 (Walkthrough / Example)

我們將設計一個具有 **Middleware 機制** 的 HTTP Request 處理器。這是一個結合 Factory (建立實例)、Composition (處理邏輯) 與 Singleton (全域配置) 的經典案例。
We will design an HTTP Request Handler with a **Middleware mechanism**. This is a classic case combining Factory (creation), Composition (processing logic), and Singleton (global config).

## 4.1 需求背景 (Background)
我們需要一個 `apiClient`，它能夠：
We need an `apiClient` that can:
1.  自動附加 Auth Token。
2.  統一處理錯誤 logging。
3.  允許開發者擴充（Middleware）。

## 4.2 實作步驟 (Implementation Steps)

### Step 1: 定義 FP 工具函數 (Define FP Utilities)
首先，我們需要一個 `compose` 函數來串接 middleware。
First, we need a `compose` function to chain middlewares.

```javascript
// Composition utility: executes functions from right to left (or left to right for pipe)
const pipe = (...fns) => (x) => fns.reduce((v, f) => f(v), x);
```

### Step 2: 建立 Factory 與 Currying 配置 (Factory & Currying Config)
使用 Factory Pattern 來產生 client，並利用 Closure 隱藏細節。
Use the Factory Pattern to generate the client, leveraging Closure to hide details.

```javascript
const createApiClient = (baseUrl) => {
  // Private config
  let middlewares = [];

  // Method to add middleware (Builder/Chainable pattern)
  const use = (fn) => {
    middlewares.push(fn);
  };

  // The core request function
  const request = async (endpoint, options = {}) => {
    // Initial context
    const context = { url: `${baseUrl}${endpoint}`, options, ...options };

    // Compose middlewares: Each middleware receives context and returns modified context
    // This is a simplified version of Redux/Express middleware composition
    const processPipeline = pipe(...middlewares);
    
    try {
      const finalContext = await processPipeline(context);
      // Mocking fetch for demonstration
      console.log(`[Fetching] ${finalContext.url} with headers:`, finalContext.options.headers);
      return { data: "Success" }; 
    } catch (error) {
      console.error("Request failed", error);
      throw error;
    }
  };

  return { use, request };
};
```

### Step 3: 定義 Middlewares (Defining Middlewares)
這些是 Pure Functions（或接近 Pure），負責轉換 config 物件。
These are Pure Functions (or close to it), responsible for transforming the config object.

```javascript
// Middleware 1: Auth Token Injector
const withAuth = (token) => (ctx) => {
  const headers = { ...ctx.options.headers, Authorization: `Bearer ${token}` };
  return { ...ctx, options: { ...ctx.options, headers } };
};

// Middleware 2: Logger
const withLogging = (ctx) => {
  console.log(`[Log] Preparing request to: ${ctx.url}`);
  return ctx;
};
```

### Step 4: 整合使用 (Integration)

```javascript
// Usage
const api = createApiClient('https://api.example.com');

// Register middlewares
api.use(withLogging);
api.use(withAuth('secret-token-123')); // Currying in action

// Execute
api.request('/users/1');
```

**分析 (Analysis)**：
-   **可維護性**：新增功能（如 Retry 機制）只需寫一個新的 Middleware 函數，不需修改 `createApiClient` 核心。
-   **測試性**：每個 Middleware 都是獨立函數，可以單獨測試。
-   **Maintainability**: Adding features (like Retry logic) only requires writing a new Middleware function, without modifying the `createApiClient` core.
-   **Testability**: Each Middleware is an independent function and can be tested in isolation.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 濫用 Class 繼承 (Abusing Class Inheritance)
**錯誤 (Pitfall)**：建立深層繼承鏈，例如 `class AdminUser extends User extends Person extends Entity`。這導致 "Fragile Base Class" 問題，父類別一改，子類別全掛。
**Error**: Creating deep inheritance chains. This leads to the "Fragile Base Class" problem, where changing the parent breaks all children.

**修正 (Fix)**：**Composition over Inheritance**。使用 Factory 或 Mixin 模式將功能「組合」進去，而不是繼承下來。
**Fix**: **Composition over Inheritance**. Use Factory or Mixin patterns to "compose" features in, rather than inheriting them down.

## 5.2 全域可變 Singleton (Global Mutable Singleton)
**錯誤 (Pitfall)**：在 Singleton 中保存大量可變狀態（Mutable State），且沒有嚴格的存取控制。這在並發請求（Node.js）或大型前端應用中會導致難以重現的 Bug。
**Error**: Keeping massive Mutable State in a Singleton without strict access control. This leads to unreproducible bugs in concurrent requests (Node.js) or large frontend apps.

**修正 (Fix)**：Singleton 應盡量無狀態（Stateless），或者狀態應透過 Redux/RxJS 等專門的狀態管理庫來管理，確保單向資料流。
**Fix**: Singletons should be as Stateless as possible, or state should be managed via dedicated libraries like Redux/RxJS to ensure unidirectional data flow.

## 5.3 過度設計 (Over-engineering)
**錯誤 (Pitfall)**：為了寫「漂亮」的 FP 代碼，使用了過度複雜的 Point-free style 或深層 Currying，導致代碼可讀性下降。
**Error**: Using overly complex Point-free style or deep Currying just to write "beautiful" FP code, resulting in reduced readability.

**修正 (Fix)**：**Readability > Cleverness**。如果一個箭頭函數超過 3 層嵌套，請考慮改寫為具名函數或一般流程控制。
**Fix**: **Readability > Cleverness**. If an arrow function has more than 3 levels of nesting, consider rewriting it as a named function or standard flow control.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 請解釋 JavaScript 中的 Prototype Chain，以及它與 Class 的關係？
## Q1: Explain the Prototype Chain in JavaScript and its relationship to Classes?

**高分回答要點 (Key Points)**：
-   JS 的 `class` 只是語法糖（Syntactic Sugar），底層仍是基於 Prototype 的繼承。
-   解釋 `__proto__` 與 `prototype` 的區別。
-   提到 `Object.create()` 是一種更直接利用 Prototype 的方式。
-   **資深觀點**：在現代開發中，我們更傾向於使用 Composition 而非深層的 Prototype 繼承。
-   JS `class` is just Syntactic Sugar; underneath, it's still Prototype-based inheritance.
-   Explain the difference between `__proto__` and `prototype`.
-   Mention `Object.create()` as a more direct way to leverage Prototypes.
-   **Senior View**: In modern development, we prefer Composition over deep Prototype inheritance.

## Q2: 你如何在不使用 Class 的情況下實作 Private Variable？
## Q2: How do you implement Private Variables without using Classes?

**高分回答要點 (Key Points)**：
-   使用 **Closure (閉包)**。
-   Factory Pattern 範例：函數內部定義變數，僅回傳操作該變數的方法（Getter/Setter），外部無法直接存取。
-   提及現代 JS 的 `#privateField` 語法作為 Class 的替代方案。
-   Use **Closure**.
-   Factory Pattern example: Define variables inside a function and return only the methods (Getter/Setter) to manipulate them; external access is blocked.
-   Mention modern JS `#privateField` syntax as the alternative for Classes.

## Q3: 什麼是 Pure Function？為什麼它在 React 或 Redux 中很重要？
## Q3: What is a Pure Function? Why is it important in React or Redux?

**高分回答要點 (Key Points)**：
-   定義：相同的輸入永遠得到相同的輸出（Deterministic），且沒有副作用（No Side Effects）。
-   重要性：使單元測試極其簡單；支援 Time-travel debugging；React 的 `memo` 和 `useEffect` 依賴 Referential Equality，Pure Function 確保了狀態更新的可預測性。
-   Definition: Same input always yields same output (Deterministic), and No Side Effects.
-   Importance: Makes unit testing extremely simple; enables Time-travel debugging; React's `memo` and `useEffect` rely on Referential Equality, and Pure Functions ensure predictability of state updates.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 記憶錨點 (Key Takeaways)
1.  **多範式融合**：資深工程師懂得在適當場景切換 OOP（封裝服務）與 FP（資料處理）。
    **Multi-paradigm Fusion**: Senior engineers know when to switch between OOP (encapsulating services) and FP (data processing).
2.  **Singleton 實作**：ES Modules 是現代 JS 中最自然的 Singleton 實作方式。
    **Singleton Implementation**: ES Modules are the most natural way to implement Singletons in modern JS.
3.  **Composition over Inheritance**：優先使用函數組合或 Object Composition，避免脆弱的繼承鏈。
    **Composition over Inheritance**: Prefer function composition or object composition to avoid fragile inheritance chains.
4.  **Immutability**：是提升系統穩定性與可預測性的基石，特別是在並發與 UI 狀態管理中。
    **Immutability**: The cornerstone of system stability and predictability, especially in concurrency and UI state management.
5.  **Factory Pattern**：利用 Closure 隱藏建立細節與私有狀態，比直接 `new Class` 更具彈性。
    **Factory Pattern**: Uses Closure to hide creation details and private state, offering more flexibility than direct `new Class`.

## 後續延伸 (Next Steps)
-   **下一章 (Chapter 05)**：非同步編程模型 (Asynchronous Programming Models) — 深入探討 Event Loop, Promises, Async/Await 以及 Generators。
-   **延伸閱讀**：研究 `RxJS` (Reactive Extensions)，這是 Observer Pattern 與 FP Iterator Pattern 的極致結合。
-   **Next Chapter (Chapter 05)**: Asynchronous Programming Models — Deep dive into Event Loop, Promises, Async/Await, and Generators.
-   **Further Reading**: Study `RxJS` (Reactive Extensions), the ultimate combination of Observer Pattern and FP Iterator Pattern.