# 效能優化與記憶體管理 / Performance Optimization & Memory Management

## Mental model｜心智模型

要掌握 JavaScript 的效能與記憶體，必須建立兩個核心的心智模型：**「可觸及性圖譜 (Reachability Graph)」** 與 **「主執行緒的過路費 (Main Thread Toll)」**。

### 1. The Reachability Graph (GC 的視角)
不要把記憶體管理想成「手動釋放」，而是要思考「引用關係 (Reference Graph)」。
- **Roots (根)**：全域物件 (Window/Global)、當前 Call Stack 中的變數。
- **Reachability (可觸及性)**：只要從 Roots 出發，透過引用鏈 (Reference Chain) 能連到的物件，Garbage Collector (GC) 就不會回收它。
- **The Mental Shift**：記憶體洩漏 (Memory Leak) 通常不是因為你「忘了刪除」，而是因為你「不小心留了一條線」，讓 GC 誤以為該物件還有用。

### 2. The Main Thread Toll (DOM 與 JS 的橋樑)
- **Engine vs. DOM**：V8 引擎（JS 執行處）與 Rendering Engine（DOM 所在處）是分開的。
- **The Bridge**：每次 JS 操作 DOM，都像是在兩座島之間過橋，需要繳「過路費」。
- **Reflow & Repaint**：最貴的過路費是強迫瀏覽器重新計算版面配置 (Reflow)。若你在一個迴圈中頻繁過橋（讀取佈局 -> 修改樣式 -> 讀取佈局），效能就會崩潰。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 使用 WeakMap/WeakSet 管理關聯數據
當你需要將資料綁定到 DOM 元素或物件上，但不想阻止該物件被回收時，這是最佳解法。
- **Pattern**: `const cache = new WeakMap();`
- **Why**: 當 Key (物件) 被 GC 回收時，WeakMap 中的 Value 也會自動被釋放，避免 Memory Leak。

### 2. 虛擬化長列表 (List Virtualization)
不要渲染使用者看不見的 DOM。
- **Pattern**: 使用 `react-window` 或自行實作 sliding window。
- **Why**: DOM 節點數量直接影響記憶體與 Style Recalculation 的速度。保持 DOM 節點在 1500 個以內是黃金法則。

### 3. 批次 DOM 更新 (Batch DOM Updates)
減少「過橋」次數。
- **Pattern**: 使用 `DocumentFragment` 或現代框架的 Virtual DOM 機制，甚至是 `requestAnimationFrame` 來集中寫入。
- **Concept**: Read 都在一起，Write 都在一起，不要交錯。

### 4. 靜態形狀優化 (Static Shape Optimization / Hidden Classes)
V8 引擎喜歡形狀固定的物件。
- **Good**: 在 Constructor 中一次定義好所有屬性。
- **Bad**: 執行期間隨意 `delete obj.prop` 或動態添加 `obj.newProp`。這會破壞 V8 的 Hidden Class 優化 (Deoptimization)。

```javascript
// ✅ Good Practice
class Point {
  constructor(x, y) {
    this.x = x;
    this.y = y;
  }
}

// ❌ Performance Killer
const p = {};
p.x = 1; // V8 creates hidden class A
p.y = 2; // V8 creates hidden class B
delete p.x; // V8 deoptimizes back to dictionary mode
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Detached DOM Tree" (分離的 DOM 樹)
這是最隱蔽的記憶體洩漏。
- **Scenario**: 你從 `document.body` 移除了一個父節點 `div#parent`，但你的 JS 變數還留著對其子節點 `span#child` 的引用。
- **Consequence**: 雖然父節點不在畫面上了，但因為子節點被引用，且子節點指回父節點，導致**整棵被移除的 DOM 樹**都無法被 GC 回收。

### 2. Accidental Global Variables (意外的全域變數)
- **Code**: `function foo() { bar = "leak"; }` (忘了寫 `const`/`let`)
- **Pitfall**: `bar` 變成 `window.bar`，永遠不會被回收。
- **Fix**: 永遠使用 Strict Mode (`'use strict'`) 或 Linter。

### 3. Layout Thrashing (佈局抖動)
在迴圈中交錯進行「讀取佈局屬性」與「寫入樣式」。
- **Anti-pattern**:
  ```javascript
  // ❌ 瀏覽器被迫在每次迴圈都重新計算 Layout (Reflow)
  elements.forEach(el => {
    const width = el.offsetWidth; // Read
    el.style.width = (width + 10) + 'px'; // Write
  });
  ```
- **Fix**: 先讀完，再寫入。

### 4. Forgotten Timers & Listeners (被遺忘的計時器與監聽器)
- **Scenario**: SPA (Single Page Application) 中，Component 卸載 (Unmount) 時，沒有清除 `setInterval` 或 `window.addEventListener`。
- **Result**: 這些 Callback 函式依然持有 Component 內部的引用 (Closure)，導致整個 Component 無法被回收。

---

## Checklists & workflows｜檢查清單與流程

### Performance Optimization Checklist
- [ ] **DOM 操作最小化**：是否將多次 DOM 寫入合併？是否使用了 `DocumentFragment`？
- [ ] **迴圈優化**：迴圈內是否有 `offsetWidth`, `scrollTop` 等會觸發 Reflow 的屬性讀取？
- [ ] **非同步卸載**：繁重的計算（如圖像處理、大數據排序）是否移至 Web Worker 處理？
- [ ] **Debounce/Throttle**：Scroll 與 Resize 事件是否加上了防抖或節流？

### Memory Leak Investigation Workflow (Chrome DevTools)
當懷疑有 Memory Leak 時，請依此步驟操作：

1.  **開啟無痕模式 (Incognito)**：排除 Chrome Extension 的干擾。
2.  **Performance Monitor**：打開 DevTools 的 Performance Monitor，觀察 CPU 與 JS Heap 大小。如果操作後 Heap 持續上升且 GC 後不下降，即為洩漏徵兆。
3.  **The "3-Snapshot" Technique (三快照法)**：
    -   **Snapshot 1**: 基準狀態 (Base state)。
    -   **Action**: 執行懷疑會洩漏的操作 (例如：打開 Modal 再關閉，重複 5 次)。
    -   **Snapshot 2**: 操作後狀態。
    -   **Action**: 點擊垃圾桶圖示 (Force GC)。
    -   **Snapshot 3**: 最終狀態。
4.  **Comparison**: 比較 Snapshot 3 與 Snapshot 1。
    -   過濾器選擇 "Objects allocated between Snapshot 1 and 2"。
    -   尋找 **Detached DOM elements** 或異常數量的 Object。
    -   查看 **Retainers** (保留者) 欄位，找出是誰（哪個變數或 Closure）抓著它不放。

---

## Real-world examples｜實戰案例

### Case 1: The Closure Trap in Event Handlers
**情境**：一個儀表板頁面，每秒更新數據。

```javascript
// ❌ Problematic Code
function attachHandler() {
  const hugeData = new Array(100000).fill('data'); // 佔用大量記憶體
  
  const button = document.getElementById('btn');
  button.addEventListener('click', () => {
    // 即使這裡只用了 console.log，
    // 某些舊瀏覽器或特定 Scope 實作可能會因為 Closure 
    // 而保留整個 attachHandler 的 Scope，包含 hugeData。
    console.log('Clicked'); 
  });
}
```

**修正**：確保 Event Handler 不會意外捕獲不需要的大型變數，或在不需要時明確設為 `null`。

### Case 2: Virtualizing a Long List
**情境**：電商網站需要顯示 10,000 筆商品列表。直接 `ul.innerHTML` 渲染導致頁面卡死 3 秒。

**解決方案 (Pseudo-code)**：
```javascript
// ✅ Virtualization Strategy
const containerHeight = 800;
const itemHeight = 50;
const visibleCount = Math.ceil(containerHeight / itemHeight);

function onScroll(scrollTop) {
  const startIndex = Math.floor(scrollTop / itemHeight);
  const endIndex = startIndex + visibleCount;
  
  // 只渲染目前視窗可見的 items (+ buffer)
  const visibleItems = allItems.slice(startIndex, endIndex + buffer);
  
  // 使用 transform: translateY 來模擬原本的位置
  renderList(visibleItems, startIndex * itemHeight);
}
```
**結果**：DOM 節點維持在 ~20 個，FPS 穩定在 60，記憶體佔用極低。

### Case 3: Cleaning up in React `useEffect`
**情境**：使用者切換路由後，Console 報錯 "Can't perform a React state update on an unmounted component"，且記憶體飆升。

**原因**：非同步請求完成前，Component 已卸載，但 Callback 仍持有 Component 引用。

```javascript
// ✅ Best Practice
useEffect(() => {
  let isMounted = true;
  
  fetchData().then(data => {
    if (isMounted) {
      setData(data);
    }
  });

  // Cleanup function is CRITICAL
  return () => {
    isMounted = false;
  };
}, []);
```