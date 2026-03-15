# 現代語法與 ES Next 最佳實踐 / Modern Syntax & ES Next Best Practices

## Mental model｜心智模型

要掌握現代 JavaScript（ES6+ 及其後的 ES Next 功能），關鍵不在於死記語法糖（Syntactic Sugar），而在於轉變對程式碼「表達力（Expressiveness）」與「安全性（Safety）」的認知。

### 1. 訊噪比 (Signal-to-Noise Ratio)
舊式 JS 充滿了為了「讓程式跑起來」而寫的樣板程式碼（Boilerplate），例如檢查 `undefined`、手動合併物件、或使用中間變數。Modern JS 的核心哲學是**提高訊噪比**——用更少的程式碼表達更清晰的意圖（Intent）。
- **Old Mental Model**: 命令式（Imperative）。告訴機器一步步怎麼做（先檢查 A，再檢查 A.B，如果有才取值）。
- **New Mental Model**: 宣告式（Declarative）。告訴機器你要什麼結構（給我 A 裡面的 B，如果沒有就給預設值）。

### 2. 預設防禦 (Defensive by Default)
現代語法如 Optional Chaining (`?.`) 和 Nullish Coalescing (`??`) 改變了我們處理「缺失資料」的心智模型。我們不再將 `null/undefined` 視為需要層層 `if` 包裹的例外，而是將其視為資料流中的一種自然狀態，透過語法優雅地「折疊（collapse）」或「替補（fallback）」。

### 3. 不可變性優先 (Immutability First)
雖然 JS 本身不是純函數式語言，但 Spread Syntax (`...`) 等特性鼓勵我們以「產生新物件」取代「修改舊物件」。這對於現代前端框架（如 React）或狀態管理至關重要。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Named Parameters with Defaults (具名參數與預設值)
利用解構賦值（Destructuring）模擬其他語言的具名參數。這解決了函式參數順序依賴的問題，並提供了清晰的預設值。

```javascript
// ✅ Best Practice
function createUser({ name, role = 'guest', isActive = true } = {}) {
  // ...logic
}

// 呼叫時不需記憶順序，且可讀性高
createUser({ name: 'Alice', role: 'admin' });
```

### 2. The "Safe Navigation" Pattern (安全導航模式)
結合 Optional Chaining (`?.`) 與 Nullish Coalescing (`??`) 來處理深層巢狀物件與預設值。這是處理 API Response 的標準姿勢。

```javascript
const user = { profile: { settings: { theme: null } } };

// ❌ Old Way: 冗長且容易出錯 (0 或 "" 會被視為 false)
const theme = (user && user.profile && user.profile.settings && user.profile.settings.theme) || 'light';

// ✅ Modern Way: 清晰且精確 (只針對 null/undefined fallback)
const theme = user?.profile?.settings?.theme ?? 'light';
```

### 3. Immutable Object Updates (不可變物件更新)
使用 Spread Syntax (`...`) 來複製並更新物件，而非使用 `Object.assign` 或直接修改屬性。

```javascript
const originalState = { loading: false, data: [] };

// ✅ Best Practice
const newState = {
  ...originalState,
  loading: true, // Override specific property
  timestamp: Date.now() // Add new property
};
```

### 4. Conditional Property Addition (條件式屬性添加)
利用 Spread syntax 的短路特性，優雅地決定是否要將某個屬性加入物件中。

```javascript
const isAdmin = true;
const user = {
  name: 'Bob',
  ...(isAdmin && { role: 'admin', permissions: ['read', 'write'] }),
};
// 如果 isAdmin 為 false，那些屬性根本不會存在於 user 物件中
```

### 5. Array Transformations (陣列轉換)
優先使用 `map`, `filter`, `reduce`, `find` 配合 Arrow Functions，而非 `for` 迴圈。這能減少 Side Effects 並提升可讀性。

```javascript
// ✅ Best Practice
const activeUserNames = users
  .filter(u => u.isActive)
  .map(u => u.name);
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Deep Destructuring" Trap (過度深層解構)
雖然解構很強大，但巢狀解構超過兩層會讓程式碼變得難以閱讀，且如果中間層級缺失，會直接拋出 Error。

```javascript
// ❌ Anti-pattern: 難以閱讀，且若 data 或 user 為 undefined 會 crash
const { data: { user: { address: { city } } } } = response;

// ✅ Better: 分段解構或使用 Optional Chaining
const city = response?.data?.user?.address?.city;
```

### 2. Confusing `||` with `??` (混淆邏輯或與空值合併)
使用 `||` 提供預設值時，會將 `0`, `false`, `""` (空字串) 視為無效值而覆蓋掉。這在處理數值（如索引 0）或布林開關時是常見 Bug 來源。

- **Rule**: 如果你只想防禦 `null` 或 `undefined`，永遠使用 `??`。

### 3. The Shallow Copy Pitfall (淺拷貝陷阱)
Spread Syntax (`...`) 只是**淺拷貝 (Shallow Copy)**。如果物件內部還有巢狀物件，修改新物件的巢狀屬性仍會影響舊物件。

```javascript
const a = { config: { verbose: true } };
const b = { ...a };

b.config.verbose = false; 
// ⚠️ 警告: a.config.verbose 也變成了 false！因為 config 是 reference。
```
*Solution*: 對於深層拷貝，使用 `structuredClone()` (現代瀏覽器/Node) 或 library (如 Lodash `cloneDeep`)。

### 4. Overusing Arrow Functions in Methods (在物件方法濫用箭頭函式)
箭頭函式沒有自己的 `this`。如果你在定義物件方法時使用箭頭函式，`this` 不會指向該物件實例。

```javascript
const counter = {
  count: 0,
  // ❌ Anti-pattern: 這裡的 this 指向 global 或 undefined
  increment: () => { this.count++; }, 
  // ✅ Correct: 使用簡寫語法
  increment() { this.count++; }
};
```

---

## Checklists & workflows｜檢查清單與流程

在 Code Review 或重構時，使用此清單檢查現代語法的適用性：

### Code Cleanliness Checklist
- [ ] **變數宣告**：是否完全避免了 `var`？預設使用 `const`，只有需要重新賦值時才用 `let`？
- [ ] **字串串接**：是否使用了 Template Literals (`` `Hello ${name}` ``) 取代字串 `+` 串接？
- [ ] **屬性存取**：在存取可能為 `undefined` 的巢狀屬性時，是否使用了 `?.`？
- [ ] **預設值**：是否使用了 `??` 來處理預設值，確保不會意外覆蓋 `0` 或 `false`？
- [ ] **物件建構**：是否使用了 Object Property Shorthand (`{ name }` 而非 `{ name: name }`)？

### Refactoring Workflow (Legacy to Modern)
當你遇到一段舊式程式碼時：
1.  **Identify**: 找出所有的 `var` 和 `function` 宣告。
2.  **Convert Scope**: 將 `var` 改為 `const/let`，確保區塊作用域（Block Scope）邏輯正確。
3.  **Simplify Logic**: 尋找 `if (obj && obj.prop)` 模式，替換為 `obj?.prop`。
4.  **Extract Parameters**: 如果函式接收大量參數，考慮重構為接收單一物件並使用解構賦值。
5.  **Clean Up Loops**: 將單純的資料轉換 `for` 迴圈改寫為 `.map()` 或 `.reduce()`。

---

## Real-world examples｜實戰案例

### Scenario 1: Handling Complex API Configuration (處理複雜 API 設定)
在封裝 HTTP Client 時，我們常需要合併「全域設定」、「預設設定」與「單次請求設定」。

```javascript
const defaultHeaders = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
};

function request(url, options = {}) {
  // 1. 解構並給予預設值，避免 options 為 undefined
  const { 
    method = 'GET', 
    headers = {}, 
    body, 
    ...restOptions // 2. 收集其餘參數 (如 timeout, signal)
  } = options;

  // 3. 使用 Spread 合併 Headers，確保使用者傳入的 headers 優先級最高
  const finalConfig = {
    method,
    headers: {
      ...defaultHeaders,
      ...headers, 
      // 若使用者傳入 Authorization，會覆蓋 defaultHeaders 裡的同名屬性
      ...(localStorage.getItem('token') && { 'Authorization': `Bearer ${localStorage.getItem('token')}` })
    },
    // 4. 條件式加入 body (GET 請求不應有 body)
    ...(body && { body: JSON.stringify(body) }),
    ...restOptions
  };

  return fetch(url, finalConfig);
}
```

### Scenario 2: Robust Data Extraction (強健的資料提取)
從後端撈取使用者資料並顯示，資料結構可能不完整。

```javascript
// 假設這是後端回傳的髒資料
const apiResponse = {
  id: 101,
  user: {
    name: 'John Doe',
    preferences: {
      // theme 遺失
      notifications: false
    }
    // contact 遺失
  }
};

// ❌ Risky Code
// const email = apiResponse.user.contact.email; // Crash!
// const theme = apiResponse.user.preferences.theme || 'dark'; // 若 theme 為 false (不想要 theme?) 會被強制轉為 'dark'

// ✅ Modern & Safe Code
const { user } = apiResponse;

const email = user?.contact?.email ?? 'No email provided';
const theme = user?.preferences?.theme ?? 'system-default';
const isNotified = user?.preferences?.notifications ?? true; // 正確保留 false

console.log({ email, theme, isNotified });
// Output: { email: 'No email provided', theme: 'system-default', isNotified: false }
```