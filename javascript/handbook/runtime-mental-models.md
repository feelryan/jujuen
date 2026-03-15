# 執行環境與核心心智模型 / Runtime & Core Mental Models

## Mental model｜心智模型

要掌握 JavaScript 的執行行為，不能只看程式碼的「物理位置」，而必須在腦中建立 JS 引擎如何解析與執行程式碼的動態模型。

### 1. The "Creation & Execution" Two-Pass System (雙階段系統)
JavaScript 並不是讀一行執行一行。在進入任何一個 Execution Context (執行環境) 前，引擎會先進行「建立階段 (Creation Phase)」。
*   **Phase 1: Creation (Parsing/Hoisting):** 引擎掃描程式碼，為變數和函式保留記憶體空間。這就是 **Hoisting (提升)** 的本質。
    *   `var` 被設為 `undefined`。
    *   `function` 宣告被完整放入記憶體。
    *   `let` / `const` 被保留但未初始化 (進入 TDZ - Temporal Dead Zone)。
*   **Phase 2: Execution:** 引擎再次從頭執行程式碼，逐行賦值與呼叫函式。

### 2. The Call Stack (呼叫堆疊)
將 Call Stack 想像成一疊盤子。
*   JavaScript 是 **Single Threaded (單執行緒)** 的，一次只能處理一個盤子。
*   當函式被呼叫，一個新的 Execution Context (盤子) 被疊上去。
*   當函式執行完畢 (return)，盤子被拿走 (Pop)。
*   **關鍵點：** 如果堆疊頂端的函式卡住 (例如無窮迴圈或龐大運算)，整個瀏覽器/Runtime 就會凍結 (Blocking)。

### 3. Scope Chain as "Tinted Windows" (作用域鏈)
Scope Chain 是基於 **Lexical Scoping (詞法作用域)**，意即「變數的可見性取決於程式碼寫在哪裡，而不是在哪裡被呼叫」。
*   想像成單向透視玻璃：內部函式可以看到外部函式的變數 (Look up)，但外部函式看不到內部的 (Cannot look down)。
*   當引擎找不到變數時，它會沿著 Scope Chain 往外層找，直到 Global Scope。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 模擬私有變數 (Encapsulation via Closures)
雖然 ES6 引入了 `class` 和 `#privateFields`，但在 Functional Programming 或 React Hooks 中，利用 Closure (閉包) 來封裝狀態仍是核心模式。

```javascript
// Pattern: Factory Function with Closure
const createCounter = () => {
  let count = 0; // Private variable via closure scope
  return {
    increment: () => ++count,
    getValue: () => count
  };
};

const counter = createCounter();
console.log(counter.count); // undefined (無法直接存取)
console.log(counter.increment()); // 1 (透過公開介面存取)
```

### 2. 避免全域污染 (IIFE & Modules)
在現代開發中，應預設使用 ES Modules (`import`/`export`)，這會自動為檔案建立獨立的 Scope。若在舊環境或 Script Tag 中，使用 IIFE (Immediately Invoked Function Expression) 來隔離作用域。

```javascript
// Legacy Pattern: IIFE to create a fresh scope
(function() {
  var localConfig = 'secret';
  window.app = { init: () => console.log(localConfig) };
})();
```

### 3. 使用 Block Scope 取代 Function Scope
全面使用 `const` 與 `let`。這讓變數的生命週期與開發者的視覺直覺 (大括號 `{}`) 一致，減少 Hoisting 帶來的認知負擔。

*   **Best Practice:** 預設使用 `const`。
*   **Best Practice:** 只有當變數確實需要被重新賦值時，才使用 `let`。
*   **Best Practice:** 永遠不要使用 `var`。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The Stale Closure Trap (過時的閉包)
這是 React Hooks (`useEffect`, `useCallback`) 開發中最常見的 Bug。當閉包「記住」了舊的變數參考，而外部狀態已經更新時發生。

```javascript
// ❌ Anti-pattern
function Watcher() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    // 這個 setInterval 閉包只捕捉到了第一次 render 時的 count (0)
    const id = setInterval(() => {
      console.log(`Count is: ${count}`); 
    }, 1000);
    return () => clearInterval(id);
  }, []); // Empty dependency array causes the closure to never update
}
```

### 2. Variable Shadowing (變數遮蔽)
在內層作用域宣告與外層同名的變數。這雖然合法，但會切斷 Scope Chain 的存取能力，並造成極大的維護混淆。

```javascript
let userId = 123;

function updateUser(userId) { // ❌ Shadowing: 這裡的 userId 遮蔽了全域的 userId
  // 開發者可能以為他在改全域變數，其實只是改了參數
  userId = 456; 
}
```

### 3. Relying on Hoisting (依賴提升)
雖然 Function Declaration Hoisting 有時很方便 (可以把 helper function 寫在檔案底部)，但依賴 `var` 的 Hoisting 是壞習慣。

```javascript
// ❌ Anti-pattern: 使用變數前未宣告
console.log(status); // undefined (不會報錯，但邏輯通常是錯的)
var status = 'active';
```

### 4. Stack Overflow (遞迴過深)
在沒有 Tail Call Optimization (TCO) 的環境下（大多數 JS 引擎），過深的遞迴會爆掉 Call Stack。

*   **Pitfall:** 處理大型樹狀結構或陣列時使用遞迴。
*   **Solution:** 改用迴圈 (Iteration) 或 Trampoline pattern。

---

## Checklists & workflows｜檢查清單與流程

### Debugging Scope Issues (除錯流程)
當遇到變數為 `undefined` 或值不如預期時：

- [ ] **檢查宣告關鍵字**：是否意外使用了 `var` 導致變數洩漏或 Hoisting 行為異常？
- [ ] **檢查 Scope Chain**：在出錯的那一行，往上看最近的 `{}`。該變數是在這個區塊內宣告的，還是上層？
- [ ] **檢查 Shadowing**：是否在參數或內層 `const/let` 中使用了重複的變數名稱？
- [ ] **檢查 Closure 依賴 (React 特有)**：如果是 Hook 內的邏輯，Dependency Array 是否遺漏了該變數，導致閉包捕捉到舊值？

### Code Review Checklist (審查清單)
- [ ] **No Global Leaks**：確保沒有變數被掛載到 `window` 或 `global` 上（除非是刻意的 Config）。
- [ ] **Block Scoping**：確認沒有使用 `var`。
- [ ] **TDZ Awareness**：確認變數在使用前已經被定義（即使 `let/const` 有 TDZ 保護，邏輯上也應先定義後使用）。
- [ ] **Recursion Safety**：如果有遞迴函式，是否有明確的 Base Case？是否考慮了最大深度？

---

## Real-world examples｜實戰案例

### 1. 非同步迴圈中的 Scope 陷阱 (The Loop Problem)

這是一個經典的面試題，但在處理 API 請求或計時器時經常發生。

**問題情境：**
我們想依序印出 0, 1, 2。

```javascript
// ❌ 錯誤示範 (使用 var)
for (var i = 0; i < 3; i++) {
  setTimeout(() => {
    console.log(i); // 結果：3, 3, 3
  }, 100);
}
// 原因：var 是 function scope，三個 callback 共享同一個變數 i 的參考。
// 當 setTimeout 執行時，迴圈早已結束，i 變成了 3。
```

**解決方案 (使用 Block Scope)：**

```javascript
// ✅ 正確示範 (使用 let)
for (let i = 0; i < 3; i++) {
  // 每次迴圈迭代，都會建立一個新的 Lexical Environment
  // 閉包捕捉的是該次迭代獨立的 i
  setTimeout(() => {
    console.log(i); // 結果：0, 1, 2
  }, 100);
}
```

### 2. Middleware Composition (Koa/Express 執行模型)

後端框架的 Middleware 機制是理解 Call Stack 與 Execution Context 的絕佳案例。這通常被稱為 "Onion Model" (洋蔥模型)。

```javascript
// 簡化的 Middleware 執行模型
const middleware1 = async (next) => {
  console.log('1. Start');
  await next(); // -> 暫停目前的 Context，將控制權交給下一個 middleware (Push to Stack)
  console.log('4. End'); // -> 當下一個 middleware pop 出來後，回到這裡繼續執行
};

const middleware2 = async (next) => {
  console.log('2. Start');
  await next(); 
  console.log('3. End');
};

// 執行順序：1. Start -> 2. Start -> 3. End -> 4. End
// 這展示了 Call Stack 的 LIFO (Last In, First Out) 特性。
```

### 3. 記憶體洩漏 (Memory Leak via Closure)

在 Single Page Application (SPA) 中，不當的閉包會導致 DOM 節點無法被 Garbage Collection 回收。

```javascript
function attachHandler() {
  const hugeData = new Array(1000000).fill('data');
  const element = document.getElementById('button');
  
  // 這個 Event Listener 形成了一個閉包
  element.addEventListener('click', () => {
    // 即使這裡只用了 hugeData.length
    // 某些舊引擎或特定情況下，整個 hugeData 可能被保留在記憶體中
    console.log(hugeData.length);
  });
}

// 修正：在元件卸載或不需要時，務必 removeEventListener
// 否則 element 活著 -> listener 活著 -> closure 活著 -> hugeData 永遠不被釋放
```