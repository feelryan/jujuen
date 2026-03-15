# 函式編程與閉包實戰 / Functional Patterns & Closures

## Mental model｜心智模型

在 JavaScript 中採用函式編程（Functional Programming, FP）並非要追求學術上的純粹性（如 Haskell），而是為了**提升程式碼的可預測性與可測試性**。

### 1. 函式即資料 (Functions as Data)
將函式視為「一等公民（First-class citizen）」。你可以像傳遞物件或字串一樣，將函式傳入另一個函式，或從函式中回傳一個新函式。這構成了 Higher-Order Functions (HOF) 的基礎。

### 2. 閉包是「背包」 (Closures as a Backpack)
不要只把閉包想成「函式內的函式」。試著這樣想像：
當一個函式被建立時，它會背上一個隱形的**背包（Backpack/Closure Scope）**。
- 這個背包裡裝著該函式**定義時**所在的環境變數。
- 無論這個函式被傳遞到哪裡執行，它永遠隨身攜帶這個背包。
- **記憶體影響**：只要函式還活著（被引用），背包裡的內容就不會被 Garbage Collection (GC) 回收。

### 3. 純函式是「轉換器」 (Pure Functions as Converters)
純函式就像數學公式 `y = f(x)` 或工廠流水線上的封閉機器：
- **Input -> Output**：相同的輸入永遠產生相同的輸出。
- **No Side Effects**：不修改外部變數、不修改輸入參數、不發送網路請求（除非該請求被封裝為一種 Effect）。
- **Immutable**：資料流動時，產生新的資料結構，而不是修改舊的。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Higher-Order Functions (HOF) for Cross-Cutting Concerns
利用 HOF 來封裝與業務邏輯無關的「切面」邏輯，例如錯誤處理、權限檢查或 Logging。

```javascript
// Pattern: Wrapping logic without touching the core function
const withErrorHandling = (fn) => async (...args) => {
  try {
    return await fn(...args);
  } catch (error) {
    console.error(`Error in ${fn.name}:`, error);
    // 統一的錯誤回傳格式或重試機制
    return null;
  }
};

const fetchUserData = async (id) => { /* ... */ };
const safeFetchUser = withErrorHandling(fetchUserData);
```

### 2. Partial Application & Currying for Configuration
使用閉包來「預先配置」函式參數。這在設定 API 客戶端或 Logger 時非常有用。

```javascript
// Pattern: Pre-configure arguments
const createLogger = (namespace) => (message) => {
  console.log(`[${namespace}] ${message}`);
};

const authLogger = createLogger('AUTH');
const dbLogger = createLogger('DB');

authLogger('User logged in'); // [AUTH] User logged in
```

### 3. Memoization (Caching via Closure)
利用閉包的記憶特性，將昂貴的計算結果快取起來。

```javascript
const memoize = (fn) => {
  const cache = new Map(); // "Backpack" holding the cache
  return (...args) => {
    const key = JSON.stringify(args); // 簡易 key 生成
    if (cache.has(key)) return cache.get(key);
    
    const result = fn(...args);
    cache.set(key, result);
    return result;
  };
};
```

### 4. Composition over Chaining
雖然 Method Chaining (如 `arr.map().filter()`) 很常見，但在處理獨立函式時，使用 `compose` 或 `pipe` 能讓資料流更清晰。

```javascript
// f(g(x)) -> pipe(g, f)(x)
const pipe = (...fns) => (x) => fns.reduce((v, f) => f(v), x);

const getPrice = (item) => item.price;
const applyTax = (price) => price * 1.05;
const formatCurrency = (amount) => `$${amount.toFixed(2)}`;

const getItemFinalPrice = pipe(getPrice, applyTax, formatCurrency);
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Stale Closure" Trap (過時的閉包)
這是 React Hooks (`useEffect`, `useCallback`) 或任何非同步回呼中最常見的 Bug。閉包「記住」的是**建立當下**的變數值，而不是最新的值。

- **Bad:** 在 Event Listener 或 Timer 中引用了舊的變數，導致邏輯錯誤。
- **Fix:** 使用 `useRef` (React) 或確保在變數更新時重新建立閉包。

### 2. Accidental Memory Leaks (意外的記憶體洩漏)
因為閉包會保留整個 Scope，如果不小心在閉包內引用了巨大的物件（如 DOM 節點或大型 Array），即使該物件在其他地方已無用，它仍無法被 GC。

```javascript
function attachHandler() {
  const hugeData = new Array(1000000).fill('data'); // 佔用大量記憶體
  const element = document.getElementById('button');
  
  element.addEventListener('click', () => {
    // 即使這裡只用了 hugeData.length，
    // 某些舊 JS 引擎可能會保留整個 hugeData (視 Scope 實作而定)
    // 現代引擎通常有優化，但若直接引用 hugeData 則必定保留
    console.log(hugeData.length); 
  });
}
```

### 3. Impure Functions in `map`/`filter`
在陣列方法中執行 Side Effects（如修改外部變數、DOM 操作）是危險的，這會讓 `map` 失去「映射」的語意，變成難以追蹤的 `forEach`。

- **Anti-pattern:** `items.map(item => { total += item.price; return item; })`
- **Fix:** 使用 `reduce` 計算總和，保持 `map` 純粹用於轉換。

### 4. Over-Currying (過度柯里化)
將所有函式都寫成 `a => b => c => d` 格式會大幅降低程式碼的可讀性，且在 JavaScript 中會造成額外的 Function call overhead。除非有明確的 Composition 需求，否則適度使用 Partial Application 即可。

---

## Checklists & workflows｜檢查清單與流程

在進行 Code Review 或重構時，請使用此清單檢查函式編程的品質：

### Function Purity Checklist
- [ ] **Input/Output**: 函式是否依賴外部全域變數？（應避免）
- [ ] **Mutation**: 函式是否修改了傳入的參數（Arguments Mutation）？（應使用 Spread operator 或 `structuredClone` 複製）
- [ ] **Side Effects**: 函式內部是否有 API 呼叫、DOM 修改？若有，是否已隔離到特定的 Layer？

### Closure & Memory Checklist
- [ ] **Lifecycle**: 這個閉包的生命週期多長？它是否綁定在全域事件（如 `window` event）上但未被移除？
- [ ] **Scope Size**: 閉包內部是否引用了不必要的大型物件？
- [ ] **Staleness**: 在非同步操作中，閉包捕獲的變數值是否可能是舊的？

### Refactoring Workflow (Imperative to Functional)
1. **Identify Loops**: 找到 `for` 或 `while` 迴圈。
2. **Classify Intent**:
   - 轉換資料？ -> `map`
   - 篩選資料？ -> `filter`
   - 聚合單一值？ -> `reduce`
   - 執行動作？ -> `forEach` (Side effect)
3. **Extract Logic**: 將迴圈內的邏輯提取為獨立的小函式（Pure Functions）。
4. **Compose**: 組合這些小函式來完成任務。

---

## Real-world examples｜實戰案例

### Case 1: API Request Builder (Closure & Currying)
在微服務架構中，我們常需要對不同的 Service 建立請求，利用閉包鎖定 Base URL 與 Auth Token。

```javascript
const createApiClient = (baseUrl) => (token) => async (endpoint, options = {}) => {
  const url = `${baseUrl}${endpoint}`;
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
    ...options.headers
  };

  const response = await fetch(url, { ...options, headers });
  return response.json();
};

// Usage
const userService = createApiClient('https://user-service.api')(currentUserToken);
const paymentService = createApiClient('https://payment.api')(currentUserToken);

// 實際呼叫時只需關心 endpoint
const profile = await userService('/profile');
```

### Case 2: React `useEffect` Stale Closure (The Pitfall)
這是一個經典的實戰陷阱。

```javascript
function Counter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      // ❌ STALE CLOSURE: 這裡的 count 永遠是 0 (閉包建立當下的值)
      console.log(`Count is: ${count}`); 
      
      // 若使用 setCount(count + 1) 也會導致計數器卡在 1
    }, 1000);

    return () => clearInterval(timer);
  }, []); // Empty dependency array means effect runs once

  // ✅ Fix: 使用 Functional Update 或將 count 加入依賴
  // setCount(prev => prev + 1);
}
```

### Case 3: Once Function (Utility Pattern)
確保某個初始化邏輯或昂貴操作只執行一次（Singleton pattern via Closure）。

```javascript
const once = (fn) => {
  let hasRun = false;
  let result;
  
  return (...args) => {
    if (!hasRun) {
      result = fn(...args);
      hasRun = true;
      // Optional: fn = null; // 釋放原始函式記憶體
    }
    return result;
  };
};

const initializeDatabase = once(() => {
  console.log('Connecting to DB...');
  return { connection: 'Active' };
});

initializeDatabase(); // "Connecting to DB..."
initializeDatabase(); // Returns cached result, no log
```