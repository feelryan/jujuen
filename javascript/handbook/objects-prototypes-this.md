# 物件導向、原型鏈與 this 機制 / OOP, Prototypes & 'this' Binding

在 JavaScript 中，物件導向（OOP）與 `this` 的行為常是資深開發者面試新人的必考題，也是導致 Bug 的常見源頭。本章節不談教科書定義，而是聚焦於如何建立正確的「執行期心智模型」，以及在現代框架（如 React, Vue, Node.js）中如何優雅地處理這些機制。

## Mental model｜心智模型

要掌握 JS 的 OOP，必須打破傳統類別語言（如 Java/C#）的思維。

### 1. 原型鏈是「委派」而非「複製」 (Delegation, not Copying)
在傳統 OOP，實例化（Instantiation）通常意味著將類別的藍圖「複製」一份到物件中。但在 JavaScript 中，物件與其原型之間建立的是一條 **「即時連結（Live Link）」**。
- **Mental Image**：想像一條鐵鍊。當你向物件要一個屬性（`obj.prop`），引擎會先看物件本身有沒有；如果沒有，它會順著鐵鍊往上找（Prototype Chain），直到找到或鐵鍊結束（`null`）。
- **Implication**：如果你在執行期間修改了上游的原型（例如 `Array.prototype`），所有下游的陣列都會受到影響。

### 2. `this` 是由「呼叫位置」決定的 (Call-site matters)
這是最常被誤解的概念。`this` **不是** 在編寫程式碼時決定的（除非是 Arrow Function），而是在 **程式碼執行時** 決定的。
- **核心規則**：問自己「這個函式是**如何**被呼叫的？」，而不是「它在哪裡被宣告？」。
- **優先順序**：
  1. **`new` 綁定**：`new Constructor()` -> `this` 是新建立的物件。
  2. **明確綁定**：`call`, `apply`, `bind` -> `this` 是你指定的物件。
  3. **隱含綁定**：`obj.method()` -> `this` 是 `obj`。
  4. **預設綁定**：直接呼叫 `func()` -> `this` 是全域物件（Strict mode 下是 `undefined`）。

### 3. Arrow Function 的 `this` 是「詞法作用域」 (Lexical Scoping)
箭頭函式沒有自己的 `this`。它會「繼承」外層程式碼區塊的 `this`。這就像是一個變數查找過程，找不到就往外層找。這也是為什麼它在 React Component 或 Callback 中如此好用。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 優先使用 `class` 語法糖 (Prefer `class` syntax)
雖然底層仍是原型，但 `class` 語法提供了更清晰的結構，並防止了常見錯誤（如忘記使用 `new` 呼叫建構子）。
- **Why**：它讓程式碼對來自其他語言的開發者更友善，且現代工具鏈（TypeScript, ESLint）對 `class` 的支援度極佳。

### 2. 方法定義在 Prototype，狀態定義在 Constructor
為了節省記憶體，共用的方法應該放在 `class` 本體中（即 Prototype 上），而每個實例獨有的資料（State）放在 `constructor` 中。

```javascript
class User {
  constructor(name) {
    this.name = name; // 每個實例獨立的狀態
  }
  
  sayHi() { // 所有實例共用同一個 function reference
    console.log(`Hi, I am ${this.name}`);
  }
}
```

### 3. 使用 Arrow Function 解決 Callback 中的 `this` 遺失
在傳遞方法給事件監聽器或非同步函式時，使用 Class Fields 配合 Arrow Function 是現代最乾淨的解法（Auto-binding）。

```javascript
class ButtonHandler {
  constructor() {
    this.count = 0;
  }

  // Best Practice: Class Field with Arrow Function
  handleClick = () => {
    this.count++; // `this` 永遠正確指向 instance
    console.log(this.count);
  }
}
// 使用時： <button onClick={handler.handleClick} />
```

### 4. 組合優於繼承 (Composition over Inheritance)
JavaScript 的繼承鏈過長會導致維護災難（Gorilla / Banana problem）。若需要復用功能，優先考慮 **Composition** 或 **Mixins** 模式，而不是建立深層的 `extends` 階層。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 濫用 `var self = this` (The `self` / `that` hack)
在 ES6 之前，為了在 callback 中存取 `this`，常會看到 `var that = this`。
- **Bad**：增加閱讀負擔，且變數名稱混亂。
- **Fix**：使用 Arrow Function 或 `.bind()`。

### 2. 直接修改原生原型 (Mutating Native Prototypes)
也就是俗稱的 "Monkey Patching"。例如 `Array.prototype.last = function() { ... }`。
- **Risk**：如果未來的 JS 標準推出了同名方法但行為不同，你的程式會崩潰；或是第三方套件互相衝突。
- **Fix**：撰寫獨立的 Utility function（如 lodash 的做法）或繼承原生類別（`class MyArray extends Array`）。

### 3. 在 `constructor` 中定義方法 (Method definitions inside constructor)
除非是為了綁定 `this`（且你沒用 Class Fields），否則不要在 constructor 裡寫 `this.method = function() {}`。
- **Consequence**：每次 `new` 一個物件，都會重新建立一個新的 function 實例，浪費記憶體。

### 4. 誤用 Arrow Function 作為物件方法
```javascript
const obj = {
  value: 10,
  // Pitfall: Arrow function here binds `this` to global/window, not obj
  print: () => console.log(this.value) 
};
obj.print(); // undefined
```
- **Fix**：在 Object Literal 中定義方法時，使用標準函式語法 `print() { ... }`。

---

## Checklists & workflows｜檢查清單與流程

### Debugging `this` Issues (除錯決策樹)
當遇到 `this` 是 `undefined` 或錯誤物件時，請依序檢查：

- [ ] **是否使用了 Arrow Function？**
    - 是：`this` 綁定到定義時的外層 Scope。檢查外層是否正確。
    - 否：進入下一步。
- [ ] **是否使用了 `new` 關鍵字？**
    - 是：`this` 是新建立的實例。
    - 否：進入下一步。
- [ ] **是否使用了 `call`, `apply`, 或 `bind`？**
    - 是：`this` 被明確指定了。
    - 否：進入下一步。
- [ ] **呼叫點是否為 `obj.method()` 形式？**
    - 是：`this` 指向 `obj`。
    - 否（例如 `const f = obj.method; f()`）：`this` 丟失（指向 Global 或 undefined）。**這是最常見的 Bug。**

### Code Review Checklist (程式碼審查清單)
- [ ] 是否避免了深層繼承（超過 2 層繼承通常是壞味道）？
- [ ] 是否在 Class 中使用了 Public Class Fields (Arrow Function) 來處理 Event Handlers？
- [ ] 是否避免了修改原生物件的原型（Array, Object, String）？
- [ ] 在使用 `Object.create(null)` 時，是否意識到該物件沒有 `toString` 或 `hasOwnProperty` 方法？

---

## Real-world examples｜實戰案例

### 1. React/Vue 中的 Event Handler 綁定
這是最經典的 `this` 丟失場景。

```javascript
class Toggle extends React.Component {
  constructor(props) {
    super(props);
    this.state = { isToggleOn: true };
    // 傳統做法 (Verbose)
    // this.handleClick = this.handleClick.bind(this);
  }

  // 現代實戰做法 (Class Fields)
  // 自動綁定 this，且不會放在 Prototype 上，而是作為實例屬性
  handleClick = () => {
    this.setState(prevState => ({
      isToggleOn: !prevState.isToggleOn
    }));
  }

  render() {
    // 如果 handleClick 不是 arrow function 且沒 bind，這裡傳遞後執行時 this 會是 undefined
    return (
      <button onClick={this.handleClick}>
        {this.state.isToggleOn ? 'ON' : 'OFF'}
      </button>
    );
  }
}
```

### 2. API Client 的封裝 (Singleton vs Class)
在設計 API 模組時，我們常面臨要 `export new ApiClient()` (Singleton) 還是 `export class ApiClient`。

```javascript
// pattern: Singleton (適合無狀態或全域設定)
class ApiService {
  constructor() {
    this.baseUrl = process.env.API_URL;
  }
  
  get(endpoint) {
    return fetch(`${this.baseUrl}${endpoint}`);
  }
}
export const api = new ApiService();

// pattern: Dependency Injection (適合測試與複雜依賴)
// 在測試時可以輕鬆替換 mock
export class UserService {
  constructor(apiClient) {
    this.api = apiClient;
  }
  
  getUsers() {
    return this.api.get('/users');
  }
}
```

### 3. 原型鏈查找效能 (Prototype Lookup Performance)
雖然現代引擎優化得很好，但理解原理有助於效能調校。

```javascript
// 假設我們有一個深層繼承
// Animal -> Mammal -> Dog -> Poodle
const myDog = new Poodle();

// 當呼叫 myDog.eat()
// 1. 檢查 myDog 實例本身 -> 無
// 2. 檢查 Poodle.prototype -> 無
// 3. 檢查 Dog.prototype -> 無
// 4. 檢查 Mammal.prototype -> 無
// 5. 檢查 Animal.prototype -> 找到 eat()！

// 實戰啟示：
// 如果是一個極高頻率呼叫的方法（例如遊戲迴圈、大量數據處理），
// 且該方法位於原型鏈很深的位置，理論上會有微小的效能損耗。
// 但更重要的是：深層繼承讓程式碼難以追蹤邏輯（"Where is this method defined?"）。
```