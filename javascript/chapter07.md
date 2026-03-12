# 1. 前言與學習目標 (Introduction & Learning Goals)

作為資深工程師，模組化（Modularity）不僅僅是將程式碼拆分成多個檔案，它是系統架構的基石。在大型專案中，錯誤的模組設計會導致打包體積膨脹、循環依賴（Circular Dependencies）難以除錯，甚至影響 Micro-frontends 的拆分策略。本章將深入探討 JavaScript 模組系統的底層機制與架構決策。

As a Senior Engineer, modularity is not just about splitting code into files; it is the cornerstone of system architecture. In large-scale projects, poor module design leads to bloated bundle sizes, hard-to-debug circular dependencies, and hinders micro-frontend strategies. This chapter dives deep into the underlying mechanisms of JavaScript module systems and architectural decision-making.

完成本章後，您將能夠：
By the end of this chapter, you will be able to:

1.  **深度剖析 CJS 與 ESM 的執行差異**：理解為何 Tree-shaking 依賴 ESM 的靜態分析特性，以及 Node.js 如何處理這兩者的互通性。
    **Deeply analyze CJS vs. ESM execution differences**: Understand why tree-shaking relies on ESM's static analysis and how Node.js handles interoperability between them.
2.  **解決複雜的循環依賴（Circular Dependencies）**：掌握 CJS 與 ESM 在循環引用時的行為差異，並使用設計模式（如 Dependency Injection）重構程式碼。
    **Resolve complex Circular Dependencies**: Master the behavioral differences of CJS and ESM during circular references and refactor code using design patterns (e.g., Dependency Injection).
3.  **設計可擴展的狀態管理架構**：區分 Server State 與 Client State，並評估何時該引入 Global Store 或 Atomic State。
    **Design scalable State Management architectures**: Distinguish between Server State and Client State, and evaluate when to introduce a Global Store or Atomic State.
4.  **評估 Micro-frontends 的適用性**：理解 Module Federation 的基礎，並能從組織架構與技術複雜度層面權衡是否採用微前端。
    **Evaluate the applicability of Micro-frontends**: Understand the basics of Module Federation and weigh the adoption of micro-frontends from both organizational and technical complexity perspectives.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 CommonJS (CJS) vs. ES Modules (ESM)

### 直覺類比 (Intuitive Analogy)

-   **CommonJS** 就像是**影印機**。當你 `require` 一個模組時，你拿到的是該物件在該時間點的一份**副本（Copy）**。如果原模組後來改變了內部的基本型別值，你手上的副本不會自動更新，除非重新 require。
-   **ES Modules** 就像是**即時連結（Live Link）**或**指標（Pointer）**。當你 `import` 一個值，你持有的是對該記憶體位置的引用。如果原模組更新了該值，你的引用也會讀取到最新值。

-   **CommonJS** is like a **photocopier**. When you `require` a module, you get a **copy** of the object at that moment. If the original module updates a primitive value later, your copy won't automatically update unless you require it again.
-   **ES Modules** are like **live links** or **pointers**. When you `import` a value, you hold a reference to that memory location. If the original module updates the value, your reference sees the latest value.

### 關鍵差異 (Key Differences)

| Feature | CommonJS (CJS) | ES Modules (ESM) |
| :--- | :--- | :--- |
| **Loading** | Synchronous (Runtime) | Asynchronous capable (Compile-time analysis + Runtime) |
| **Structure** | Dynamic (can `require` in `if` blocks) | Static (imports must be top-level*) |
| **Values** | Copied values (Primitives) | Live bindings (References) |
| **Tree-shaking**| Difficult/Impossible | Native support (Static analysis) |
| **Scope** | `this` is `module.exports` | `this` is `undefined` |

*\*註：Dynamic `import()` 允許在 ESM 中動態載入，但標準 `import` 語句是靜態的。*
*\*Note: Dynamic `import()` allows runtime loading in ESM, but standard `import` statements are static.*

## 2.2 循環依賴 (Circular Dependencies)

在大型系統中，模組 A 依賴 B，B 又依賴 A 是常見現象。
In large systems, Module A depending on B, and B depending on A is a common phenomenon.

-   **CJS**：當遇到循環時，它會返回目前已執行到的 `exports` 物件的**不完整副本**。這通常會導致 `undefined` 錯誤，但不會直接 crash 程式（除非你嘗試存取該屬性）。
-   **ESM**：由於是靜態分析，引擎知道有哪些 export。但在執行階段，如果存取了尚未初始化的變數（Temporal Dead Zone），會直接拋出 `ReferenceError`。

-   **CJS**: When a cycle is encountered, it returns an **incomplete copy** of the `exports` object processed so far. This often leads to `undefined` errors but doesn't immediately crash the program (unless you try to access a property on it).
-   **ESM**: Due to static analysis, the engine knows what is exported. However, at runtime, if you access a variable that hasn't been initialized yet (Temporal Dead Zone), it throws a `ReferenceError`.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 打包與效能優化 (Bundling & Optimization)

在 Production 環境中，我們幾乎總是使用 Bundlers (Webpack, Vite, Rollup)。
In production environments, we almost always use Bundlers (Webpack, Vite, Rollup).

-   **Tree-shaking**: 這是 ESM 的殺手級應用。因為 `import` 是靜態的，Bundler 可以在建置階段建立依賴圖（Dependency Graph），並安全地移除未使用的 export（Dead Code Elimination）。CJS 難以做到這一點，因為 `require` 可能是動態計算的。
-   **Tree-shaking**: This is the killer feature of ESM. Because `import` is static, the bundler can build a dependency graph at build time and safely remove unused exports (Dead Code Elimination). CJS struggles with this because `require` can be dynamically computed.

## 3.2 微前端架構 (Micro-frontends Architecture)

當單體前端（Frontend Monolith）變得過於龐大，導致部署緩慢且團隊耦合過高時，我們會考慮微前端。
When a Frontend Monolith becomes too large, leading to slow deployments and tight team coupling, we consider Micro-frontends.

-   **Module Federation (Webpack 5+)**: 允許在執行階段（Runtime）動態載入其他建置產物中的模組。這本質上依賴於非同步模組載入機制。
-   **Module Federation (Webpack 5+)**: Allows dynamic loading of modules from other build artifacts at runtime. This inherently relies on asynchronous module loading mechanisms.

### 架構示意 (Architecture Overview)

```text
[Host Application (Shell)]
       |
       +--- Loads Remote Entry (remoteEntry.js)
       |
       +--- [Remote App A (Checkout Team)]
       |       |-- Exposes: ./Button, ./CheckoutFlow
       |       |-- Shared Libs: React, Lodash (Singleton)
       |
       +--- [Remote App B (Inventory Team)]
               |-- Exposes: ./ProductList
```

在這種架構下，**Shared Dependencies** 的管理至關重要。如果處理不當（例如版本衝突或 CJS/ESM 混用），會導致 Singleton（如 React Context）失效。
In this architecture, managing **Shared Dependencies** is critical. Mishandling them (e.g., version conflicts or mixing CJS/ESM) can cause Singletons (like React Context) to break.

---

# 4. 逐步示例 (Walkthrough / Example)

## 4.1 深入解析循環依賴 (Deep Dive: Circular Dependencies)

這是一個經典的面試題，也是實務中常見的 Bug 來源。
This is a classic interview question and a common source of bugs in practice.

### 案例背景 (Scenario)
我們有兩個模組：`parent.js` 和 `child.js`。Parent 依賴 Child，Child 也依賴 Parent。

### CommonJS 的行為 (CJS Behavior)

```javascript
// parent.js
const child = require('./child');

exports.message = 'Hello from Parent';
console.log('Child message:', child.message);

// child.js
const parent = require('./parent');

exports.message = 'Hello from Child';
console.log('Parent message:', parent.message);
```

**執行流程 (Execution Flow):**
1. `main` 載入 `parent`。
2. `parent` 執行第一行 `require('./child')`。
3. 暫停 `parent`，開始載入 `child`。
4. `child` 執行第一行 `require('./parent')`。
5. **關鍵點**：Node.js 檢測到 `parent` 正在載入中（尚未完成），於是返回 `parent` 目前的 `exports` 物件（此時是空物件 `{}`）。
6. `child` 繼續執行，印出 `Parent message: undefined`。
7. `child` 完成執行，匯出 `{ message: 'Hello from Child' }`。
8. `parent` 恢復執行，拿到 `child` 的完整匯出。
9. `parent` 印出 `Child message: Hello from Child`。

**結果**：不會 Crash，但資料不一致。
**Result**: No crash, but inconsistent data.

### ES Modules 的行為 (ESM Behavior)

```javascript
// parent.mjs
import { message as childMessage } from './child.mjs';

export const message = 'Hello from Parent';
console.log('Child message:', childMessage);

// child.mjs
import { message as parentMessage } from './parent.mjs';

export const message = 'Hello from Child';
console.log('Parent message:', parentMessage);
```

**執行流程 (Execution Flow):**
1. **Parsing Phase**: 建立所有模組的 Module Record，分析 export/import，建立記憶體連結（Bindings）。此時不執行程式碼。
2. **Execution Phase**:
   - 進入 `child.mjs`。
   - 嘗試存取 `parentMessage`。
   - 雖然連結已建立，但 `parent.mjs` 還沒執行到 `export const message = ...` 這一行。
   - **Crash**: `ReferenceError: Cannot access 'message' before initialization`.

### 解決方案 (Solution)

在 ESM 中，利用函數提升（Hoisting）或延遲執行來解決。
In ESM, solve this using function hoisting or deferred execution.

```javascript
// parent.mjs
import { getChildMessage } from './child.mjs';
export function getParentMessage() { return 'Hello from Parent'; }
console.log(getChildMessage()); // Works if called after initialization

// child.mjs
import { getParentMessage } from './parent.mjs';
export function getChildMessage() { return 'Hello from Child'; }
// Don't access getParentMessage() at the top level immediately
```

**最佳實踐**：使用 **Dependency Injection** 或將共用邏輯抽取到第三個模組 `shared.js`，打破循環。
**Best Practice**: Use **Dependency Injection** or extract shared logic into a third module `shared.js` to break the cycle.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 Dual Package Hazard

**錯誤描述 (Description):**
Library 作者試圖同時支援 CJS 和 ESM，但配置錯誤，導致使用者在同一個專案中同時載入了兩個版本的 Library。
Library authors try to support both CJS and ESM but misconfigure it, causing users to load both versions of the library in the same project.

**為何不好 (Why it's bad):**
1. **Bundle Size**: 程式碼被打包兩次。
2. **Instanceof Failure**: `instanceA instanceof ClassA` 會回傳 `false`，因為一個來自 CJS 版本，一個來自 ESM 版本。這在 React Context 或 Error handling 中是災難性的。

**解決方案 (Solution):**
使用 Node.js 的 `package.json` `exports` 欄位精確定義入口，並確保 Wrapper 模式正確（例如 CJS 只是 ESM 的一層薄薄的 wrapper，或者反之）。
Use the `exports` field in Node.js `package.json` to precisely define entry points, and ensure the wrapper pattern is correct (e.g., CJS is just a thin wrapper around ESM, or vice versa).

## 5.2 濫用 Barrel Files (Overusing Barrel Files)

**錯誤描述 (Description):**
在 `index.js` 中 `export * from './moduleA'; export * from './moduleB';`，並在專案中大量使用。

**為何不好 (Why it's bad):**
雖然方便，但在某些 Bundler 配置下，這會導致 Tree-shaking 失效。如果你只想要 `moduleA`，但因為 Barrel file 的副作用（Side Effects），Bundler 可能被迫把 `moduleB` 也打包進去。

**解決方案 (Solution):**
標記 `sideEffects: false` 在 `package.json` 中，或者在大型專案中直接引用特定路徑（雖不便但效能較好）。

## 5.3 全域狀態的誤用 (Misuse of Global State)

**錯誤描述 (Description):**
將所有 API 資料（Server State）都塞進 Redux/MobX 等 Client Global Store。

**為何不好 (Why it's bad):**
Server State 有其獨特的生命週期（Caching, Revalidation, Deduplication）。手動在 Redux 中管理 `isLoading`, `isError`, `data` 會產生大量 Boilerplate 且容易出錯。

**解決方案 (Solution):**
分離 **Server State** (使用 React Query, SWR, Apollo) 與 **Client UI State** (使用 Context, Zustand, Redux)。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

這些問題旨在測試候選人對模組化與架構的深度理解。
These questions are designed to test a candidate's deep understanding of modularity and architecture.

## Q1: 請解釋 ESM 的 "Live Bindings" 與 CJS 的 "Copied Values" 有何不同？
**Please explain the difference between ESM's "Live Bindings" and CJS's "Copied Values".**

*   **高分回答要點 (Key Points):**
    *   CJS 匯出的是物件屬性的淺拷貝（基本型別），一旦匯出，模組內部的變更不會反映到外部。
    *   ESM 匯出的是記憶體參考（Reference），模組內部變更變數值，外部 import 的值會隨之改變。
    *   這影響了 Mocking 和 Circular Dependencies 的處理方式。

## Q2: 在設計一個大型前端系統時，你會如何決定是否採用 Micro-frontends？
**When designing a large-scale frontend system, how do you decide whether to adopt Micro-frontends?**

*   **高分回答要點 (Key Points):**
    *   **不是為了技術潮**：Micro-frontends 主要是為了解決「組織擴張」問題（Conway's Law），而非單純的技術效能。
    *   **權衡 (Trade-offs)**：雖然解耦了部署，但增加了基礎建設複雜度、樣式隔離難度、以及共用依賴（Shared Dependencies）的版本管理成本。
    *   **替代方案**：Monorepo 配合良好的模組邊界（Modular Monolith）通常是更好的起點。

## Q3: 專案中出現了循環依賴導致的 Crash，你會如何排查與解決？
**Your project crashed due to a circular dependency. How would you investigate and resolve it?**

*   **高分回答要點 (Key Points):**
    *   **工具**：使用 `madge` 或 Webpack 插件來視覺化依賴圖。
    *   **短期修復**：利用 `var` 提升（不推薦）或延遲存取（在函數內 require/import）。
    *   **長期重構**：提取共用邏輯至 `common` 模組，或使用 Dependency Injection 模式將依賴作為參數傳入，而非直接 import。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 記憶錨點 (Key Takeaways)

1.  **ESM 是標準**：新專案應預設使用 ESM，它支援靜態分析、Tree-shaking 和瀏覽器原生執行。
2.  **CJS 是執行時載入**：它返回物件副本，處理循環依賴時會返回不完整物件。
3.  **Live Bindings**：ESM 的匯入是動態連結，這對狀態同步和 Mocking 有深遠影響。
4.  **狀態分離**：不要把 Server State 當作 Global UI State 管理。
5.  **架構複雜度守恆**：Micro-frontends 不會消除複雜度，只是將其從程式碼層面轉移到了 DevOps 和協調層面。

## 後續延伸 (Next Steps)

*   **延伸閱讀**: 深入研究 Webpack 5 的 **Module Federation** 配置細節。
*   **實作練習**: 在一個 Monorepo 中設定兩個互相依賴的套件，分別用 CJS 和 ESM 實作，親自體驗 `dual package hazard`。
*   **下一章預告**: **Chapter 08: Asynchronous Programming Patterns** (將探討 Event Loop 深度機制、Microtasks vs Macrotasks、以及高效的併發控制)。