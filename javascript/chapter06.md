# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，JavaScript 的元程式設計（Metaprogramming）不再只是為了炫技，而是構建高層次抽象（High-level Abstractions）、開發通用函式庫（Libraries/SDKs）以及深入理解現代框架（如 Vue 3, MobX, Redux Toolkit）的核心技能。本章將超越基礎語法，探討如何攔截並定義語言的基本行為。

For Senior Engineers, JavaScript Metaprogramming is no longer just about showing off tricks; it is a core skill for building high-level abstractions, developing generic libraries/SDKs, and deeply understanding modern frameworks (like Vue 3, MobX, Redux Toolkit). This chapter goes beyond basic syntax to explore how to intercept and define the fundamental behavior of the language.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **實作響應式系統核心（Implement Core Reactivity）：** 使用 `Proxy` 與 `Reflect` 構建類似 Vue 3 的資料攔截與依賴追蹤機制。
    **Implement Core Reactivity:** Build data interception and dependency tracking mechanisms similar to Vue 3 using `Proxy` and `Reflect`.
2.  **正確處理上下文與繼承（Handle Context & Inheritance Correctly）：** 理解為何直接存取屬性會導致 `this` 指向錯誤，並掌握 `Reflect` 在 Prototype Chain 中的關鍵作用。
    **Handle Context & Inheritance Correctly:** Understand why direct property access leads to incorrect `this` context, and master the critical role of `Reflect` in the Prototype Chain.
3.  **利用 Symbols 進行架構設計（Architect with Symbols）：** 使用 `Symbol` 實作真正的私有元數據（Metadata）、自定義迭代器（Iterators）與避免命名衝突。
    **Architect with Symbols:** Use `Symbol` to implement true private metadata, custom iterators, and avoid naming collisions.
4.  **識別元程式設計的效能陷阱（Identify Metaprogramming Performance Pitfalls）：** 評估 Proxy 在高頻操作下的開銷，並避免常見的無限遞迴（Infinite Recursion）錯誤。
    **Identify Metaprogramming Performance Pitfalls:** Evaluate the overhead of Proxies in high-frequency operations and avoid common infinite recursion errors.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 Proxy：攔截器 (The Interceptor)

將 `Proxy` 想像成物件的「守門員」或「海關」。在外部程式碼與目標物件（Target Object）之間，所有的操作（讀取、寫入、刪除、函式呼叫等）都必須經過這一層。你可以在這裡進行驗證、記錄、修改數據，甚至拒絕存取。

Think of a `Proxy` as a "Gatekeeper" or "Customs Officer" for an object. Between the external code and the Target Object, all operations (read, write, delete, function calls, etc.) must pass through this layer. Here, you can validate, log, modify data, or even deny access.

*   **Traps (陷阱/攔截點):** 定義在 Handler 中的方法（如 `get`, `set`, `apply`），用來捕獲特定操作。
    **Traps:** Methods defined in the Handler (like `get`, `set`, `apply`) used to capture specific operations.
*   **Target (目標):** 被代理的原始物件。
    **Target:** The original object being proxied.

### 2.2 Reflect：預設行為轉發器 (The Default Behavior Forwarder)

如果 `Proxy` 是自定義邏輯，`Reflect` 就是標準行為的鏡像。它提供了一組與 Proxy Traps 一一對應的靜態方法。

If `Proxy` is the custom logic, `Reflect` is the mirror of standard behavior. It provides a set of static methods that correspond one-to-one with Proxy Traps.

*   **為什麼需要它？ (Why do we need it?)**
    1.  **標準化回傳值 (Standardized Returns):** `Reflect.set` 回傳布林值（成功/失敗），比傳統 `try-catch` 或沈默失敗更適合程式化處理。
        **Standardized Returns:** `Reflect.set` returns a boolean (success/failure), which is more programmatic than traditional `try-catch` or silent failures.
    2.  **接收者上下文 (Receiver Context):** 最重要的一點，`Reflect` 允許我們傳遞 `receiver` 參數，確保 Getter/Setter 中的 `this` 正確指向 Proxy 本身，而非原始 Target。
        **Receiver Context:** Most importantly, `Reflect` allows us to pass a `receiver` argument, ensuring that `this` inside Getters/Setters points correctly to the Proxy itself, not the original Target.

### 2.3 Symbols：唯一識別符 (Unique Identifiers)

`Symbol` 是原始型別，保證全域唯一。在系統設計中，它常被用來當作「隱藏的」物件屬性 Key，用於儲存框架內部的狀態（如 `isReactive` 標記），而不會污染使用者的資料命名空間。

`Symbol` is a primitive type guaranteed to be globally unique. In system design, it is often used as "hidden" object property keys to store framework-internal state (like an `isReactive` flag) without polluting the user's data namespace.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型系統或框架開發中，元程式設計通常扮演「底層基礎設施」的角色。

In large-scale systems or framework development, metaprogramming typically plays the role of "underlying infrastructure."

### 3.1 響應式狀態管理 (Reactive State Management)
**場景 (Scenario):** 前端框架（Vue, MobX）或後端即時資料同步系統。
**應用 (Application):**
利用 `Proxy` 監聽資料變更。當屬性被讀取時，收集依賴（Dependency Collection）；當屬性被寫入時，觸發更新（Trigger Updates）。
**優勢 (Advantage):** 相比 `Object.defineProperty`（Vue 2），Proxy 可以監聽陣列索引變化、屬性刪除以及動態新增的屬性。

**Scenario:** Frontend frameworks (Vue, MobX) or backend real-time data synchronization systems.
**Application:**
Use `Proxy` to observe data changes. When a property is read, collect dependencies; when a property is written, trigger updates.
**Advantage:** Compared to `Object.defineProperty` (Vue 2), Proxy can observe array index changes, property deletions, and dynamically added properties.

### 3.2 防禦性程式設計與 SDK (Defensive Programming & SDKs)
**場景 (Scenario):** 提供給第三方開發者使用的 API Client 或 SDK。
**應用 (Application):**
使用 `Proxy` 驗證輸入參數型別，或在存取已棄用（Deprecated）屬性時發出警告，而無需修改現有的物件結構。
**系統觀點 (System View):** 增強了系統的**可觀測性 (Observability)** 與 **強健性 (Robustness)**，能在開發階段即時反饋錯誤用法。

**Scenario:** API Clients or SDKs provided to third-party developers.
**Application:**
Use `Proxy` to validate input parameter types or warn when accessing deprecated properties, without modifying the existing object structure.
**System View:** Enhances **Observability** and **Robustness**, providing immediate feedback on incorrect usage during the development phase.

### 3.3 虛擬化與延遲載入 (Virtualization & Lazy Loading)
**場景 (Scenario):** ORM (Object-Relational Mapping) 函式庫。
**應用 (Application):**
當存取關聯資料（如 `user.posts`）時，Proxy 攔截讀取操作，此時才觸發資料庫查詢（Lazy Loading），而非一開始就載入所有資料。

**Scenario:** ORM (Object-Relational Mapping) libraries.
**Application:**
When accessing related data (e.g., `user.posts`), the Proxy intercepts the read operation and triggers the database query only then (Lazy Loading), rather than loading all data upfront.

---

# 4. 逐步示例：構建一個迷你響應式系統 (Walkthrough: Building a Mini Reactive System)

我們將實作一個類似 Vue 3 核心的響應式包裝器。這展示了 `Proxy`、`Reflect` 與 `WeakMap` 的協同工作。

We will implement a reactive wrapper similar to the Vue 3 core. This demonstrates the synergy of `Proxy`, `Reflect`, and `WeakMap`.

### 4.1 基礎架構 (Infrastructure)

首先，我們需要一個儲存依賴的容器。使用 `WeakMap` 是為了避免記憶體洩漏（Memory Leaks），當目標物件不再被使用時，其依賴關係也能被垃圾回收（GC）。

First, we need a container to store dependencies. Using `WeakMap` prevents memory leaks, ensuring that when the target object is no longer used, its dependencies can also be garbage collected.

```javascript
// Global bucket to store dependencies
// Structure: target -> key -> Set of effects
const targetMap = new WeakMap();

// Active effect (the function currently running)
let activeEffect = null;

function track(target, key) {
  if (!activeEffect) return;
  
  let depsMap = targetMap.get(target);
  if (!depsMap) {
    depsMap = new Map();
    targetMap.set(target, depsMap);
  }
  
  let dep = depsMap.get(key);
  if (!dep) {
    dep = new Set();
    depsMap.set(key, dep);
  }
  
  dep.add(activeEffect);
}

function trigger(target, key) {
  const depsMap = targetMap.get(target);
  if (!depsMap) return;
  
  const dep = depsMap.get(key);
  if (dep) {
    dep.forEach(effect => effect());
  }
}

// Helper to register an effect
function effect(fn) {
  activeEffect = fn;
  fn(); // Run once to collect dependencies
  activeEffect = null;
}
```

### 4.2 實作 Reactive Proxy (Implementing the Reactive Proxy)

這是核心部分。我們使用 `Reflect` 來確保預設行為，並處理 `receiver` 以支援繼承。

This is the core part. We use `Reflect` to ensure default behavior and handle the `receiver` to support inheritance.

```javascript
const isObject = (val) => val !== null && typeof val === 'object';

// Symbol to mark an object as reactive to avoid double-wrapping
const IS_REACTIVE = Symbol('isReactive');

function reactive(target) {
  // 1. Check if already reactive
  if (target[IS_REACTIVE]) {
    return target;
  }

  if (!isObject(target)) {
    return target;
  }

  const handler = {
    get(target, key, receiver) {
      // 2. Handle the special flag
      if (key === IS_REACTIVE) return true;

      // 3. Track dependency
      track(target, key);

      // 4. Reflect guarantees correct 'this' binding
      const res = Reflect.get(target, key, receiver);

      // 5. Deep reactivity (Lazy)
      // Only wrap nested objects when they are accessed
      if (isObject(res)) {
        return reactive(res);
      }

      return res;
    },
    set(target, key, value, receiver) {
      const oldValue = target[key];
      // 6. Reflect returns boolean
      const result = Reflect.set(target, key, value, receiver);

      // 7. Trigger updates only if value changed and set succeeded
      if (result && oldValue !== value) {
        trigger(target, key);
      }
      return result;
    }
  };

  return new Proxy(target, handler);
}
```

### 4.3 驗證與測試 (Verification & Testing)

```javascript
const state = reactive({
  count: 0,
  user: { name: 'Alice' }
});

effect(() => {
  console.log(`Count is: ${state.count}, User is: ${state.user.name}`);
});
// Output: Count is: 0, User is: Alice

state.count++; 
// Output: Count is: 1, User is: Alice

state.user.name = 'Bob'; 
// Output: Count is: 1, User is: Bob
```

**為什麼這在實務中可行？ (Why does this work in practice?)**
這種模式將「狀態變更」與「副作用（UI 更新、日誌）」解耦。`Reflect.get` 傳入 `receiver` 是關鍵，如果 `state` 是一個 Class Instance 且有 Getter 依賴 `this`，沒有 `receiver` 則 `this` 會指向原始物件而非 Proxy，導致依賴追蹤失效。

This pattern decouples "state changes" from "side effects (UI updates, logs)." Passing `receiver` to `Reflect.get` is crucial; if `state` were a Class Instance with a Getter relying on `this`, without `receiver`, `this` would point to the original object instead of the Proxy, causing dependency tracking to fail.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 忽略 `this` 綁定問題 (Ignoring `this` Binding Issues)
**錯誤 (Pitfall):** 在 Proxy Handler 中直接使用 `target[key]` 而非 `Reflect.get(target, key, receiver)`。
**後果 (Consequence):** 當目標物件有 Getter 且該 Getter 存取其他屬性時，這些內部存取不會觸發 Proxy 的 `get` trap，導致依賴追蹤不完整。
**修正 (Fix):** 始終使用 `Reflect.get` 並傳遞第三個參數 `receiver`。

**Pitfall:** Using `target[key]` directly in the Proxy Handler instead of `Reflect.get(target, key, receiver)`.
**Consequence:** When the target object has a Getter that accesses other properties, those internal accesses won't trigger the Proxy's `get` trap, leading to incomplete dependency tracking.
**Fix:** Always use `Reflect.get` and pass the third argument, `receiver`.

### 5.2 代理私有欄位 (Proxying Private Fields)
**錯誤 (Pitfall):** 嘗試 Proxy 含有 Private Fields (`#field`) 的 Class Instance。
**後果 (Consequence):** JavaScript 的 Private Fields 檢查依賴於嚴格的物件身份（Identity）。Proxy 物件與原始物件身份不同，存取 `#field` 會拋出 `TypeError: Cannot read private member...`。
**修正 (Fix):** 這是 Proxy 的已知限制。解決方案通常涉及在 `get` trap 中綁定原始 target 的方法，但这會破壞響應式。通常建議響應式物件使用 Plain Object 而非複雜 Class。

**Pitfall:** Attempting to Proxy a Class Instance containing Private Fields (`#field`).
**Consequence:** JavaScript's Private Fields check relies on strict object identity. The Proxy object has a different identity than the original object, so accessing `#field` throws `TypeError: Cannot read private member...`.
**Fix:** This is a known limitation of Proxy. Solutions often involve binding methods to the original target inside the `get` trap, but this breaks reactivity. It is generally recommended to use Plain Objects for reactive objects instead of complex Classes.

### 5.3 過度代理與效能 (Over-Proxying & Performance)
**錯誤 (Pitfall):** 對所有物件（包括不可變的大型資料、第三方 Library 實例）進行 Deep Proxy。
**後果 (Consequence):** Proxy 比普通物件存取慢（雖然現代引擎已優化，但仍有 overhead）。遞迴包裝大型結構會導致顯著的初始化延遲。
**修正 (Fix):** 使用 `shallowReactive`（只代理第一層）或 `markRaw`（標記不需代理的物件，如 Vue 3 的做法）。

**Pitfall:** Deep Proxying everything (including immutable large data, third-party library instances).
**Consequence:** Proxies are slower than normal object access (though modern engines have optimized this, overhead remains). Recursively wrapping large structures causes significant initialization latency.
**Fix:** Use `shallowReactive` (proxy only the first level) or `markRaw` (mark objects that should not be proxied, as done in Vue 3).

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 為什麼 Vue 3 要從 `Object.defineProperty` 遷移到 `Proxy`？
**Why did Vue 3 migrate from `Object.defineProperty` to `Proxy`?**

*   **高分回答要點 (Key Points):**
    1.  **完整性 (Completeness):** `defineProperty` 無法攔截屬性的新增與刪除，也無法有效攔截陣列索引操作（需 hack）。Proxy 解決了這些問題。
    2.  **效能 (Performance):** `defineProperty` 需要在初始化時遞迴遍歷所有屬性（Eager Observation）。Proxy 可以實作 Lazy Observation（只在存取嵌套物件時才包裝）。
    3.  **Map/Set 支援:** Proxy 可以代理 Map 和 Set，這在舊版實作極其困難。

*   **Key Points:**
    1.  **Completeness:** `defineProperty` cannot intercept property addition/deletion, nor effectively intercept array index operations (requires hacks). Proxy solves these.
    2.  **Performance:** `defineProperty` requires recursive traversal of all properties at initialization (Eager Observation). Proxy allows for Lazy Observation (wrapping nested objects only when accessed).
    3.  **Map/Set Support:** Proxy can proxy Map and Set, which was extremely difficult in the old implementation.

### Q2: 解釋 `Reflect` 的作用，為什麼不直接操作物件？
**Explain the role of `Reflect`. Why not manipulate the object directly?**

*   **高分回答要點 (Key Points):**
    1.  **語義一致性:** `Reflect` 方法與 Proxy Traps 一一對應。
    2.  **回傳值處理:** `Reflect.set` 回傳 Boolean 讓我們知道寫入是否成功，這對於庫開發者至關重要（避免 `use strict` 下的 throw）。
    3.  **Receiver 與 Prototype:** 這是最深層的點。當 Proxy 作為 Prototype 時，`Reflect.get/set` 的 `receiver` 參數確保了操作是針對原始呼叫者（Instance）而非 Prototype 鏈上的 Proxy，維持正確的 `this` 綁定。

*   **Key Points:**
    1.  **Semantic Consistency:** `Reflect` methods correspond one-to-one with Proxy Traps.
    2.  **Return Value Handling:** `Reflect.set` returns a Boolean indicating success, which is crucial for library developers (avoiding throws in `use strict`).
    3.  **Receiver & Prototype:** This is the deepest point. When a Proxy acts as a Prototype, the `receiver` argument in `Reflect.get/set` ensures operations target the original caller (Instance) rather than the Proxy on the prototype chain, maintaining correct `this` binding.

### Q3: 如何設計一個安全的沙箱環境執行不可信的程式碼？
**How would you design a secure sandbox environment to execute untrusted code?**

*   **高分回答要點 (Key Points):**
    *   提及使用 `Proxy` 創建一個 `with(proxy) { ... }` 作用域。
    *   利用 `has` trap 攔截所有變數查找（Variable Lookup）。
    *   利用 `get` trap 阻止存取全域物件（如 `window`, `process`）或敏感 API。
    *   這也是許多微前端（Micro-frontend）框架隔離 JS 的原理。

*   **Key Points:**
    *   Mention using `Proxy` to create a `with(proxy) { ... }` scope.
    *   Use the `has` trap to intercept all Variable Lookups.
    *   Use the `get` trap to block access to global objects (like `window`, `process`) or sensitive APIs.
    *   This is also the principle behind JS isolation in many Micro-frontend frameworks.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)
1.  **Proxy 是攔截器 (Interceptor):** 它是 JavaScript 中唯一能攔截語言底層操作（如 `in` 運算符、`new`、`delete`）的機制。
2.  **Reflect 是轉發器 (Forwarder):** 始終將 Proxy Trap 轉發給 `Reflect`，並記得傳遞 `receiver` 以修復 `this` 指向。
3.  **Symbols 用於隱藏 (Hiding):** 使用 Symbols 儲存框架狀態（如 `_isReactive`），避免與使用者代碼衝突。
4.  **Lazy Reactivity:** 利用 Proxy 的特性，只在存取屬性時才進行深層代理，提升初始化效能。
5.  **Private Fields 限制:** Proxy 無法透明代理 Class 的 Private Fields (`#field`)，這是架構設計時需注意的邊界。

### 後續延伸 (Next Steps)
*   **Generators & Iterators (Chapter 07):** 學習如何結合 `Symbol.iterator` 與 Generator 函數，自定義物件的遍歷行為，這常與 Proxy 結合使用於構建複雜的數據結構。
*   **深入閱讀:** 研究 `immer` 庫的源碼，它利用 Proxy 實現了不可變數據結構（Immutable Data Structures）的 Copy-on-write 機制。