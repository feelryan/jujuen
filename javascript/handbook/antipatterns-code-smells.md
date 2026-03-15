# 常見反模式與程式碼異味 / Common Anti-patterns & Code Smells

## Mental model｜心智模型

在 JavaScript 的世界裡，語言給予了開發者極大的自由度（動態型別、原型繼承、全域變數），但這份自由往往是混亂的根源。理解程式碼異味（Code Smells）的核心心智模型並非「這段程式碼跑不動」，而是 **「這段程式碼增加了不必要的認知負荷（Cognitive Load）」**。

### 1. 破窗效應 (Broken Windows Theory)
反模式通常不是 Bug，程式碼當下是可以運作的。但它們像是建築物打破的窗戶，暗示著「這裡沒人管，可以隨便寫」。一個全域變數會引來更多全域變數，最終導致系統無法維護。

### 2. 可預測性 vs. 聰明 (Predictability vs. Cleverness)
JavaScript 允許很多「聰明」的寫法（例如依賴隱式轉型、Monkey Patching 原生物件）。但在工程團隊中，**可預測性 > 聰明**。好的程式碼應該像無聊的小說，看到開頭就能猜到結尾，而不是充滿驚喜（副作用）。

### 3. 債務利息 (Technical Debt Interest)
每一個反模式都是一筆債務。Callback Hell 的利息是「難以除錯與擴充」；Global State 的利息是「單元測試困難」。重構就是償還本金，停止支付高額利息。

---

## Patterns & best practices｜常見模式與最佳實務

要消除異味，我們需要用已被驗證的模式來替換舊習慣。

### 1. Guard Clauses (衛兵語句) 取代巢狀結構
不要把主邏輯包在層層的 `if-else` 中。儘早 return，讓主流程保持在最外層。

```javascript
// Bad: Arrow Code / Pyramid of Doom
function processUser(user) {
  if (user) {
    if (user.isActive) {
      if (user.hasCredit) {
        // ... logic
      }
    }
  }
}

// Good: Guard Clauses
function processUser(user) {
  if (!user) return;
  if (!user.isActive) return;
  if (!user.hasCredit) return;
  
  // ... logic (flat and clean)
}
```

### 2. Immutability (不可變性) 取代狀態變異
JavaScript 的物件與陣列是傳參考（Pass by reference）。直接修改（Mutate）會導致資料流難以追蹤，特別是在 React 等現代框架中。

*   **Pattern:** 使用 Spread Operator (`...`) 或 Array Methods (`map`, `filter`, `reduce`) 產生新資料，而非修改舊資料。

### 3. Dependency Injection (依賴注入) 取代全域依賴
函式不應直接存取全域變數或單例（Singleton），應透過參數傳入依賴。這讓函式變為 **Pure Function (純函式)**，極易測試。

### 4. Async/Await 取代 Promise Chain / Callbacks
雖然 Promise 解決了 Callback Hell，但過長的 `.then()` 鏈仍然難讀。`async/await` 讓非同步程式碼讀起來像同步程式碼，且 `try/catch` 錯誤處理更直觀。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Global Namespace Pollution (全域變數污染)
*   **徵兆**：變數直接宣告在最外層，或掛載在 `window` / `global` 物件上。
*   **後果**：命名衝突、資料被意外覆寫、難以追蹤是誰改了變數。
*   **解法**：使用 Module (ESM)、IIFE (舊專案)、Closure 封裝變數。

### 2. The Explicit Promise Construction Antipattern
*   **徵兆**：明明已經有 Promise API，卻還用 `new Promise()` 包一層。
*   **後果**：喪失了 Promise 自動傳遞錯誤的能力，程式碼變得冗長。

```javascript
// Bad
function getData() {
  return new Promise((resolve, reject) => {
    fetch('/api').then(res => resolve(res)).catch(err => reject(err));
  });
}

// Good
function getData() {
  return fetch('/api');
}
```

### 3. Magic Numbers & Strings (魔術數字與字串)
*   **徵兆**：程式碼中充斥著 `if (status === 2)` 或 `if (role === 'admin')`。
*   **後果**：沒人知道 `2` 代表什麼，修改時容易漏改。
*   **解法**：提取為 `const STATUS_COMPLETED = 2` 或 Enum 物件。

### 4. Shadowing (變數遮蔽)
*   **徵兆**：內層作用域宣告了與外層同名的變數。
*   **後果**：開發者以為在改外層變數，其實改到了內層（或反之），造成極難察覺的 Bug。

### 5. God Object / God Function
*   **徵兆**：一個檔案超過 500 行，或一個函式做了「驗證 + 資料抓取 + UI 渲染 + 錯誤回報」。
*   **解法**：單一職責原則 (SRP)。拆分邏輯為獨立的小函式。

---

## Checklists & workflows｜檢查清單與流程

在 Code Review 或重構時，請使用此清單進行檢查。

### Code Review Checklist
- [ ] **Scope Check**: 是否有變數宣告在不必要的全域或過大的作用域中？
- [ ] **Mutation Check**: 函式是否修改了傳入的參數（Side Effects）？如果是，是否有必要？
- [ ] **Complexity Check**: 是否有超過 3 層的巢狀縮排？能否用 Guard Clauses 攤平？
- [ ] **Naming Check**: 變數名稱是否能自解釋？是否消滅了 Magic Numbers？
- [ ] **Async Check**: 是否混用了 Callback、Promise Chain 與 Async/Await？（應統一風格，優先使用 Async/Await）。
- [ ] **Error Handling**: 所有的 Promise 是否都有 `.catch` 或在 `try/catch` 區塊中？是否只是 `console.log` 而未做處理？

### Refactoring Workflow (重構流程)
1.  **Cover**: 確保要重構的程式碼有測試覆蓋（哪怕是簡單的整合測試）。
2.  **Lint**: 執行 ESLint，修復自動偵測到的風格問題。
3.  **Extract**: 將長函式中的邏輯區塊提取為獨立的小函式（Extract Function）。
4.  **Simplify**: 將巢狀條件句改為 Guard Clauses。
5.  **Isolate**: 移除對外部變數的依賴，改為參數傳遞。
6.  **Verify**: 執行測試確保功能未變。

---

## Real-world examples｜實戰案例

### Case 1: The "Mutating State" Trap (狀態變異陷阱)

**Anti-pattern (Bad):**
直接修改原始陣列，導致依賴該資料的其他元件（如 React Component）無法偵測變更，或產生副作用。

```javascript
const cart = [{ id: 1, price: 100 }, { id: 2, price: 200 }];

function applyDiscount(cartItems) {
  // 錯誤：直接修改了傳入的物件參考
  for (let i = 0; i < cartItems.length; i++) {
    cartItems[i].price = cartItems[i].price * 0.9;
  }
}

applyDiscount(cart); 
// 原本的 cart 被改掉了，這是一個隱晦的副作用 (Side Effect)
```

**Best Practice (Good):**
回傳新陣列與新物件，保持原始資料純淨。

```javascript
function applyDiscount(cartItems) {
  // 正確：使用 map 產生新陣列，並展開物件產生新參考
  return cartItems.map(item => ({
    ...item,
    price: item.price * 0.9
  }));
}

const newCart = applyDiscount(cart);
// cart 保持原樣，newCart 是打折後的結果
```

### Case 2: Callback Hell to Async/Await

**Anti-pattern (Bad):**
典型的「波動拳」縮排，錯誤處理分散且困難。

```javascript
function loginUser(email, password, callback) {
  getUser(email, (err, user) => {
    if (err) return callback(err);
    checkPassword(user, password, (err, isMatch) => {
      if (err) return callback(err);
      if (isMatch) {
        getToken(user, (err, token) => {
          if (err) return callback(err);
          callback(null, token);
        });
      }
    });
  });
}
```

**Best Practice (Good):**
邏輯扁平化，錯誤處理集中。

```javascript
async function loginUser(email, password) {
  try {
    const user = await getUser(email);
    const isMatch = await checkPassword(user, password);
    
    if (!isMatch) {
      throw new Error('Invalid password');
    }
    
    const token = await getToken(user);
    return token;
  } catch (err) {
    // 集中處理所有步驟的錯誤
    console.error('Login failed', err);
    throw err;
  }
}
```