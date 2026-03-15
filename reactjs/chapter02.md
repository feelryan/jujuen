# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，React Hooks 不僅僅是 `useState` 或 `useEffect` 的語法糖，而是邏輯復用（Logic Reuse）與副作用管理（Side Effect Management）的核心原語。本章將跳脫基礎 API 介紹，深入探討如何構建強健的 Custom Hooks，並解決 React 閉包（Closure）機制帶來的常見陷阱。

For senior engineers, React Hooks are not merely syntactic sugar for `useState` or `useEffect`; they are the core primitives for Logic Reuse and Side Effect Management. This chapter moves beyond basic API introductions to explore how to build robust Custom Hooks and solve common pitfalls caused by React's Closure mechanism.

完成本章後，你應該能夠：
After completing this chapter, you should be able to:

1.  **掌握進階 Custom Hooks 設計模式**：能夠將複雜的 UI 邏輯（如表單驗證、事件監聽、API 輪詢）抽離為可測試、可復用的 Hooks。
    **Master Advanced Custom Hooks Design Patterns**: Extract complex UI logic (e.g., form validation, event listeners, API polling) into testable, reusable Hooks.
2.  **徹底解決 Closure Trap（閉包陷阱）**：理解 Stale Closure 的成因，並能熟練運用 `useRef` pattern 來存取最新狀態而不觸發非必要的 Effect 執行。
    **Solve the Closure Trap**: Understand the root cause of Stale Closures and proficiently use the `useRef` pattern to access the latest state without triggering unnecessary Effect executions.
3.  **精準控制 Render 與 Paint 時機**：清楚區分 `useEffect` 與 `useLayoutEffect` 的執行順序，並知道何時使用 `useImperativeHandle` 來處理非典型的父子組件互動。
    **Precisely Control Render and Paint Timing**: Clearly distinguish the execution order of `useEffect` vs. `useLayoutEffect`, and know when to use `useImperativeHandle` for atypical parent-child interactions.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 Hooks 是一種「快照」 (Hooks as Snapshots)

在 React 的 Functional Component 中，每一次 Render 都有其獨立的 Props、State 與 Event Handlers。這意味著在某次 Render 內定義的函數（包括傳給 `useEffect` 的 callback），其內部所看見的變數值，永遠鎖定在該次 Render 發生時的狀態。這就是所謂的「閉包陷阱」或「過期閉包」（Stale Closure）的來源。

In React Functional Components, every render has its own Props, State, and Event Handlers. This means that functions defined within a specific render (including callbacks passed to `useEffect`) "see" variable values locked to the state at the time of that render. This is the source of the so-called "Closure Trap" or "Stale Closure."

> **Mental Model**: 把每一次 Render 想像成一張**靜態的照片（Snapshot）**。Effect 函數是照片中的一部分，它捕捉了當時所有的變數值。如果 Effect 沒有重新執行（因為依賴陣列未變），它依然拿著舊照片裡的數據。
>
> **Mental Model**: Imagine each render as a **static photograph (Snapshot)**. The Effect function is part of that photo, capturing all variable values at that moment. If the Effect does not re-run (because the dependency array hasn't changed), it is still holding onto the data from the old photo.

## 2.2 Render Phase vs. Commit Phase

理解 `useEffect` 與 `useLayoutEffect` 的關鍵在於 React 的渲染流程：
The key to understanding `useEffect` vs. `useLayoutEffect` lies in React's rendering flow:

1.  **Render Phase**: React 呼叫組件函數，計算 Virtual DOM 的差異（Diffing）。
    **Render Phase**: React calls component functions and calculates Virtual DOM differences (Diffing).
2.  **Commit Phase**: React 將變更寫入真實 DOM。
    **Commit Phase**: React applies changes to the real DOM.
3.  **Layout Effects (`useLayoutEffect`)**: 在 DOM 變更後、瀏覽器繪製（Paint）**之前**同步執行。這會阻塞瀏覽器渲染。
    **Layout Effects (`useLayoutEffect`)**: Runs synchronously after DOM mutations but **before** the browser paints. This blocks browser rendering.
4.  **Paint**: 瀏覽器將畫面繪製到螢幕上。
    **Paint**: The browser draws the screen.
5.  **Passive Effects (`useEffect`)**: 在瀏覽器繪製**之後**非同步執行。
    **Passive Effects (`useEffect`)**: Runs asynchronously **after** the browser paints.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 Headless UI 與邏輯抽象化 (Headless UI & Logic Abstraction)

在大型系統或 Component Library 設計中，資深工程師傾向於將「行為（Behavior）」與「外觀（Appearance）」分離。Custom Hooks 是實現 **Headless UI** 的最佳工具。

In large-scale systems or Component Library design, senior engineers tend to separate "Behavior" from "Appearance." Custom Hooks are the premier tool for implementing **Headless UI**.

-   **場景 (Scenario)**: 設計一個 Autocomplete（自動完成）組件。
-   **做法 (Approach)**:
    -   `useAutocomplete`: 負責處理輸入過濾、鍵盤導航（ArrowDown/Up）、選單開關狀態、ARIA 屬性計算。
    -   `AutocompleteComponent`: 只負責接收 Hook 回傳的 props 並渲染 UI。
-   **優勢 (Benefit)**: 同一套邏輯可以輕易套用到 Material Design、Tailwind UI 或自家 Design System 的實作中，極大提升了可維護性。

## 3.2 處理 Legacy Integration 與效能 (Handling Legacy Integration & Performance)

雖然 React 提倡 Declarative（宣告式）編程，但在實務上我們常需整合 D3.js、Google Maps 或 HTML5 Canvas 等 Imperative（指令式）的庫。

While React advocates for Declarative programming, in practice, we often need to integrate with Imperative libraries like D3.js, Google Maps, or HTML5 Canvas.

-   **useLayoutEffect**: 用於測量 DOM 元素尺寸（如 Tooltip 定位）或在畫面閃爍前同步修改 DOM。若使用 `useEffect` 測量並更新位置，使用者可能會看到元件「跳動」（Layout Shift）。
    **useLayoutEffect**: Used for measuring DOM element dimensions (e.g., Tooltip positioning) or synchronously modifying the DOM before the screen flickers. Using `useEffect` to measure and update position might cause the user to see the component "jump" (Layout Shift).
-   **useImperativeHandle**: 當父組件需要直接呼叫子組件內部的某個方法（例如：`videoRef.current.play()` 或 `modalRef.current.open()`）時，這是唯一的正規逃生艙（Escape Hatch）。
    **useImperativeHandle**: When a parent component needs to directly call a method inside a child component (e.g., `videoRef.current.play()` or `modalRef.current.open()`), this is the only legitimate Escape Hatch.

---

# 4. 逐步示例 (Walkthrough / Example)

## 案例：解決 Event Listener 的 Stale Closure 問題
## Case: Solving the Stale Closure in Event Listeners

假設我們需要一個 Hook 來監聽 `window` 的 `resize` 事件，並在 callback 中存取當前的 `count` 狀態。

Suppose we need a Hook to listen to the `window` `resize` event and access the current `count` state within the callback.

### 1. Naive Approach (Buggy)

```javascript
function useWindowResize(callback) {
  useEffect(() => {
    const handler = () => {
      callback(); // 這裡的 callback 是舊的！(Here callback is stale!)
    };
    window.addEventListener('resize', handler);
    return () => window.removeEventListener('resize', handler);
  }, []); // Empty dependency array means effect runs once
}

// Usage
const [count, setCount] = useState(0);
useWindowResize(() => {
  console.log(count); // Always logs 0 (Initial State)
});
```

**問題**：由於 `useEffect` 的依賴為空，`handler` 永遠引用第一次 Render 時建立的 `callback`。而該 `callback` 閉包內的 `count` 永遠是 0。
**Problem**: Since the `useEffect` dependency is empty, `handler` always references the `callback` created during the first render. The `count` inside that `callback` closure is always 0.

### 2. Standard Approach (Performance Issue)

```javascript
function useWindowResize(callback) {
  useEffect(() => {
    const handler = () => callback();
    window.addEventListener('resize', handler);
    return () => window.removeEventListener('resize', handler);
  }, [callback]); // Re-bind whenever callback changes
}
```

**問題**：每次 Render，父組件通常會傳入一個新的箭頭函數 `() => console.log(count)`。這導致 `useEffect` 每次都執行 cleanup 和 setup，頻繁解綁與綁定事件監聽器，效能不佳。
**Problem**: On every render, the parent component usually passes a new arrow function `() => console.log(count)`. This causes `useEffect` to run cleanup and setup every time, frequently unbinding and rebinding the event listener, which is poor for performance.

### 3. Senior Pattern: The "Latest Ref" (useEvent / useLatest)

我們利用 `useRef` 作為一個「可變的容器」，在不觸發 Effect 重新執行的情況下，保持對最新 callback 的引用。

We use `useRef` as a "mutable container" to hold the reference to the latest callback without triggering the Effect to re-run.

```javascript
import { useEffect, useRef, useLayoutEffect } from 'react';

function useEventCallback(fn) {
  const ref = useRef(fn);

  // 1. 每次 Render 都更新 Ref，確保它指向最新的邏輯
  // 1. Update Ref on every render to ensure it points to the latest logic
  // 使用 useLayoutEffect 確保在任何 Effect 執行前 Ref 已更新
  useLayoutEffect(() => {
    ref.current = fn;
  });

  // 2. 回傳一個穩定的函數引用
  // 2. Return a stable function reference
  return useRef((...args) => {
    // 執行當下最新的 fn (Execute the latest fn at call time)
    return (0, ref.current)(...args);
  }).current;
}

// Optimized Usage Hook
function useWindowResize(callback) {
  // 確保 callback 永遠是最新的，但本身引用地址不變
  const stableCallback = useEventCallback(callback);

  useEffect(() => {
    const handler = (e) => stableCallback(e);
    window.addEventListener('resize', handler);
    
    // 這裡不再需要依賴 callback，因為 stableCallback 永遠不變
    // No need to depend on callback here, as stableCallback never changes
    return () => window.removeEventListener('resize', handler);
  }, [stableCallback]); 
}
```

**為何可行**：
**Why it works**:
1.  `ref.current` 的變更不會觸發 re-render。
    Changes to `ref.current` do not trigger a re-render.
2.  `useEffect` 內部的 `handler` 呼叫的是 `stableCallback`，而 `stableCallback` 內部透過 `ref.current` 動態讀取最新的函數。
    The `handler` inside `useEffect` calls `stableCallback`, which dynamically reads the latest function via `ref.current`.
3.  這是在 React 中橋接「Reactive Data Flow」與「Imperative Event Systems」的標準模式。
    This is the standard pattern for bridging "Reactive Data Flow" and "Imperative Event Systems" in React.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 濫用 `useLayoutEffect` (Overusing `useLayoutEffect`)

-   **錯誤 (Mistake)**: 為了避免任何潛在的閃爍，預設全部使用 `useLayoutEffect`。
    Defaulting to `useLayoutEffect` for everything to avoid any potential flickering.
-   **後果 (Consequence)**: 阻塞主執行緒（Main Thread），延遲 First Contentful Paint (FCP)，導致頁面感覺卡頓。
    Blocks the main thread, delays First Contentful Paint (FCP), causing the page to feel sluggish.
-   **修正 (Fix)**: 95% 的情況下應使用 `useEffect`。只有在需要測量 DOM 幾何屬性並立即修改樣式時，才使用 `useLayoutEffect`。
    Use `useEffect` in 95% of cases. Only use `useLayoutEffect` when you need to measure DOM geometry and immediately modify styles.

## 5.2 忽視 Linter 的依賴警告 (Ignoring Linter Dependency Warnings)

-   **錯誤 (Mistake)**: 在 `useEffect` 中使用了某個 prop，但為了不想讓 Effect 重新執行，故意從依賴陣列中省略它（`// eslint-disable-next-line`）。
    Using a prop inside `useEffect` but intentionally omitting it from the dependency array to prevent the Effect from re-running (`// eslint-disable-next-line`).
-   **後果 (Consequence)**: 這是 Stale Closure 的主要來源，會導致極難除錯的邏輯錯誤。
    This is the primary source of Stale Closures, leading to logic bugs that are extremely hard to debug.
-   **修正 (Fix)**: 誠實填寫依賴。如果不想因為該依賴變更而執行 Effect，應該使用 `useRef` 保存該值，或者將邏輯移至 Event Handler 中，而非 Effect 中。
    Be honest with dependencies. If you don't want the Effect to run when that dependency changes, use `useRef` to hold the value, or move the logic into an Event Handler instead of an Effect.

## 5.3 Custom Hook 回傳過多實作細節 (Leaking Implementation Details)

-   **錯誤 (Mistake)**: 直接回傳 `setState` 函數或原始的 `ref` 給 Hook 使用者。
    Directly returning the `setState` function or the raw `ref` to the Hook consumer.
-   **後果 (Consequence)**: 破壞了封裝性，讓 Consumer 可以隨意破壞內部狀態。
    Breaks encapsulation, allowing the Consumer to arbitrarily corrupt internal state.
-   **修正 (Fix)**: 回傳封裝好的 Handler（如 `open`, `close`, `toggle`）而非 `setIsVisible`。
    Return encapsulated Handlers (like `open`, `close`, `toggle`) instead of `setIsVisible`.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

在面試或技術討論中，這些問題能有效鑑別工程師對 React 運行機制的理解深度。

In interviews or technical discussions, these questions effectively gauge an engineer's depth of understanding regarding React's runtime mechanisms.

## Q1: 請解釋 `useEffect` 與 `useLayoutEffect` 的區別，並舉一個必須使用 `useLayoutEffect` 的例子。
## Q1: Explain the difference between `useEffect` and `useLayoutEffect`, and give an example where `useLayoutEffect` is mandatory.

-   **高分回答要點 (Key Points)**:
    -   指出執行時機：Paint 之後 (Async) vs. Paint 之前 (Sync)。
    -   提到對效能的影響（Blocking rendering）。
    -   **範例**：Tooltip 位置計算。如果不使用 `useLayoutEffect`，使用者會先看到 Tooltip 在錯誤位置（0,0），然後瞬間跳到正確位置（Flicker）。

## Q2: 如何實作一個 `useInterval` Hook？為什麼直接在 `useEffect` 中使用 `setInterval` 會有問題？
## Q2: How would you implement a `useInterval` Hook? Why is using `setInterval` directly inside `useEffect` problematic?

-   **高分回答要點 (Key Points)**:
    -   直接使用會遇到 Closure Trap，導致 callback 讀取到的 state 永遠是舊的。
    -   若將 callback 加入依賴，會導致 Timer 頻繁重置，時間不準確。
    -   解決方案：使用 `useRef` 儲存 callback，讓 `setInterval` 只需要設定一次（Saved Callback Pattern）。

## Q3: 什麼情況下你會使用 `useImperativeHandle`？這是否違反了 React 的單向資料流原則？
## Q3: When would you use `useImperativeHandle`? Does this violate React's one-way data flow principle?

-   **高分回答要點 (Key Points)**:
    -   這是 Escape Hatch，確實打破了單向流，但在整合第三方 DOM 庫（如控制 Video 播放、Canvas 繪圖、Focus 管理）時是必要的。
    -   應限制使用範圍，不應用於一般的狀態傳遞。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 記憶錨點 (Key Takeaways)
1.  **Hooks are Snapshots**: 永遠記住 Effect 閉包捕捉的是定義當下的變數值。
2.  **Refs escape Closures**: 使用 `useRef` 來穿透閉包，存取最新的值而不觸發 Render。
3.  **Layout Effects block Paint**: `useLayoutEffect` 是同步的，僅用於 DOM 測量與避免視覺閃爍。
4.  **Logic Extraction**: 使用 Custom Hooks 將邏輯與 UI 分離，實現 Headless UI 架構。
5.  **Honest Dependencies**: 不要欺騙 Linter，用架構手段（如 Refs）解決依賴問題，而不是移除依賴項。

## 後續延伸 (Next Steps)
-   **Performance Optimization**: 學習 `useMemo` 與 `useCallback` 的正確使用時機，以及 React.memo 的配合（對應下一章：效能優化與並發模式）。
-   **Concurrent Features**: 探索 React 18+ 的 `useTransition` 與 `useDeferredValue`，這將改變我們處理渲染優先級的方式。
-   **Library Study**: 閱讀 `react-use` 或 `ahooks` 的原始碼，觀察它們如何處理邊界情況。