# 型別系統與強制轉型陷阱 / Type System & Coercion Pitfalls

JavaScript 的動態型別（Dynamic Typing）與弱型別（Weak Typing）特性是一把雙面刃。它讓開發初期非常靈活，但也因為隱式強制轉型（Implicit Coercion）埋下了許多難以察覺的 Bug。本章節旨在建立正確的型別心智模型，並提供防禦性的編碼策略。

## Mental model｜心智模型

### 1. 變數沒有型別，值才有型別 (Variables don't have types, values do)
在 C# 或 Java 中，你定義一個變數為 `int`，它就永遠是個整數容器。但在 JS 中，變數只是一個「標籤（Label）」，它可以貼在任何型別的「值（Value）」上。
- **思考方式**：不要問「這個變數是什麼型別？」，要問「這個變數目前持有的**值**是什麼型別？」。

### 2. 原始值 vs 參考值 (Primitives vs. References)
這是理解 JS 記憶體運作的核心。
- **Primitives (Immutable / Call by Value)**: `string`, `number`, `boolean`, `null`, `undefined`, `symbol`, `bigint`。
  - 它們像是一張寫了字的紙條。當你把變數 A 賦值給變數 B，你是**影印**了一張新的紙條給 B。修改 B 不會影響 A。
- **References (Mutable / Call by Reference / Sharing)**: `object` (包含 `array`, `function`)。
  - 它們像是房子的地址。當你把變數 A 賦值給變數 B，你是把**地址**抄給了 B。A 和 B 指向同一棟房子，任何一方進去搬動家具（修改屬性），另一方都會看到改變。

### 3. 強制轉型是「過度熱心的助手」 (Coercion is an over-eager assistant)
當你試圖對不同型別進行運算（例如 `'1' + 2`），JS 引擎不會報錯，而是會扮演一個「熱心助手」，猜測你想做什麼並幫你轉換型別。
- **規則**：JS 傾向於將運算元轉換為 `String` 或 `Number`。
- **風險**：這位助手經常猜錯你的意圖（例如把 `null` 當成 `0`，或把 `[]` 當成 `""`）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 顯式轉型優於隱式轉型 (Explicit over Implicit)
永遠不要依賴 JS 的自動轉型，明確地告訴程式碼你要轉成什麼。

```javascript
// ❌ Bad: 依賴隱式轉型
const total = inputPrice + tax; // 如果 inputPrice 是字串 "100"，結果變成 "10010"

// ✅ Good: 顯式轉型
const total = Number(inputPrice) + tax;
// 或者使用更明確的 Parsing (視需求而定)
const total = parseInt(inputPrice, 10) + tax;
```

### 2. 嚴格相等檢查 (Strict Equality)
在 99% 的情況下，使用 `===` (Strict Equality) 而非 `==` (Loose Equality)。
- `==` 會觸發強制轉型，導致 `0 == ''` (true) 或 `false == '0'` (true) 等詭異結果。
- **唯一例外**：檢查 `null` 或 `undefined` 時，有時會用 `if (value == null)` 來同時捕捉這兩者（但現代語法更推薦 `??`）。

### 3. 善用 Nullish Coalescing (`??`) 取代 Logical OR (`||`)
這是現代 JS 最重要的防禦性模式之一。
- `||` 會對所有 **Falsy** 值（包含 `0`, `""`, `false`）生效。
- `??` 只會對 **Nullish** 值（`null`, `undefined`）生效。

```javascript
const config = { timeout: 0 };

// ❌ Bad: 當 timeout 設定為 0 時，會被錯誤覆蓋成 1000
const time = config.timeout || 1000; 

// ✅ Good: 只有當 timeout 是 null/undefined 時才使用預設值
const time = config.timeout ?? 1000; 
```

### 4. 防禦性物件取值 (Optional Chaining)
處理深層巢狀物件或 API 回傳資料時，使用 `?.` 防止 `Cannot read property of undefined`。

```javascript
// ✅ Good
const street = user?.address?.street ?? 'Unknown Street';
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Falsy" Trap with Numbers
在條件判斷中直接使用數字變數是常見的 Bug 來源，特別是當 `0` 是一個有效數值時。

```javascript
const points = 0;

// ❌ Anti-pattern: 0 被視為 false，導致顯示 "No points"
if (points) {
  renderPoints(points);
} else {
  renderEmptyState();
}

// ✅ Fix: 明確檢查型別或數值
if (typeof points === 'number') { ... }
```

### 2. React/Frontend 的 `0` 渲染陷阱
在 JSX 或樣板語言中，使用 `&&` 進行條件渲染時，如果左側運算結果是 `0`，它會被渲染在畫面上，而不是「什麼都不顯示」。

```jsx
// ❌ Pitfall: 如果 items.length 是 0，畫面上會顯示一個數字 "0"
{ items.length && <List items={items} /> }

// ✅ Fix: 確保左側是 Boolean
{ items.length > 0 && <List items={items} /> }
// 或者
{ !!items.length && <List items={items} /> }
```

### 3. `typeof` 的歷史包袱
不要完全信任 `typeof`。
- `typeof null` 回傳 `'object'`（這是 JS 著名的歷史 Bug）。
- `typeof NaN` 回傳 `'number'`（NaN 意指 "Invalid Number"，但它還是 Number 型別）。
- **解法**：檢查 null 請用 `value === null`；檢查 NaN 請用 `Number.isNaN(value)`。

### 4. 意外的物件變異 (Unintended Mutation)
將物件或陣列傳入函式後直接修改，會汙染外部狀態。

```javascript
// ❌ Anti-pattern
function addTag(tags) {
  tags.push('new-tag'); // 修改了原始陣列
  return tags;
}

// ✅ Best Practice: Copy-on-write
function addTag(tags) {
  return [...tags, 'new-tag']; // 回傳新陣列
}
```

---

## Checklists & workflows｜檢查清單與流程

### Code Review Checklist
在審查涉及資料處理的程式碼時，請檢查：

- [ ] **相等性檢查**：是否全面使用 `===`？如果使用了 `==`，是否有註解說明原因？
- [ ] **預設值處理**：使用 `||` 設定預設值時，是否考慮過 `0` 或 `""` (空字串) 是有效值的情況？是否該改用 `??`？
- [ ] **數值運算**：在進行數學運算前，是否已確保所有輸入都是 `Number` 型別？（特別是來自 DOM input 或 URL query params 的值）。
- [ ] **條件渲染**：在 React/Vue 中，`&&` 左側是否可能為 `0`？
- [ ] **物件傳遞**：函式是否修改了傳入的物件參數？如果是，是否應該使用 `{...obj}` 或 `structuredClone` 進行複製？

### 決策樹：如何檢查「空值」？

1. **變數是否為 `null` 或 `undefined`？**
   - 使用 `value == null` (Loose equality) 或 `value === null || value === undefined`。
2. **變數是否為「沒有值」（包含空字串、0、false）？**
   - 使用 `!value` (Falsy check)。
3. **變數是否為陣列且為空？**
   - 使用 `Array.isArray(val) && val.length === 0`。
4. **變數是否為物件且為空（無屬性）？**
   - 使用 `val && Object.keys(val).length === 0`。

---

## Real-world examples｜實戰案例

### Case 1: API 回傳資料的隱式轉型災難
後端回傳 JSON 資料，前端需要加總金額。

```javascript
// API Response: { "price": "100.50", "tax": 5 }
// 注意：price 是字串（常見於為了保持精度的後端設計），tax 是數字

function calculateTotal(data) {
  // 💀 Bug: "100.50" + 5 -> "100.505" (字串串接)
  // 結果不是 105.5，而是字串 "100.505"
  return data.price + data.tax;
}

// 🛡️ Defense:
function calculateTotalSafe(data) {
  // 使用 Number() 或 parseFloat() 確保型別安全
  return Number(data.price) + Number(data.tax);
}
```

### Case 2: 表單輸入驗證 (Form Input Validation)
HTML `<input type="number">` 的 `value` 屬性在 JS 中取得時仍然是 `string`。

```javascript
const ageInput = document.getElementById('age').value; // 假設輸入 18，取得 "18"

// 💀 Pitfall: 嚴格比對失敗
if (ageInput === 18) {
  // 這行永遠不會執行，因為 "18" !== 18
  console.log('You are 18!');
}

// 🛡️ Defense:
if (Number(ageInput) === 18) { ... }
// 或
if (ageInput == 18) { ... } // 雖然可行，但建議顯式轉型比較好維護
```

### Case 3: 陣列參考造成的副作用 (Reference Side-effects)
在 Redux 或 React State 中常見的錯誤。

```javascript
const defaultConfig = { theme: 'dark', retries: 3 };

function updateUserConfig(userConfig) {
  // 💀 Bug: 直接修改了 default object
  // 如果下一個使用者進來，defaultConfig 已經被汙染了
  const config = defaultConfig; 
  config.retries = 5; 
  return { ...config, ...userConfig };
}

// 🛡️ Defense:
function updateUserConfigSafe(userConfig) {
  // 建立新物件，斷開參考
  const config = { ...defaultConfig }; 
  config.retries = 5;
  return { ...config, ...userConfig };
}
```