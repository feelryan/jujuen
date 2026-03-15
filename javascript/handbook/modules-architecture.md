# 模組化設計與架構決策 / Modular Design & Architecture Decisions

在 JavaScript 的演進史中，模組系統是變動最劇烈、也最容易造成架構混亂的領域。從早期的 IIFE、AMD/UMD，到 Node.js 的 CommonJS (CJS)，再到標準化的 ES Modules (ESM)。本章節不談歷史課，而是聚焦於**現代專案的架構決策**：如何選擇模組格式、如何利用模組特性實作 Singleton 或 Factory 模式，以及如何避免常見的耦合陷阱。

---

## Mental model｜心智模型

### 1. 靜態圖譜 vs. 動態載入 (Static Graph vs. Dynamic Loading)
理解 ESM 與 CJS 最核心的差異在於**解析時機**。
- **ESM (ES Modules)**：建立的是**靜態相依圖譜 (Static Dependency Graph)**。在程式碼執行前，Import/Export 的關係就已經確定。這使得 Tree-shaking（移除未使用的程式碼）成為可能。想像成**電路板佈線**，通電前線路已接好。
- **CJS (CommonJS)**：是**動態執行**的。`require()` 是一個函式，可以在 `if` 判斷式中呼叫。想像成**去圖書館借書**，你需要時才去櫃檯拿，且拿回來的是一份影本。

### 2. Live Bindings vs. Copied Values
這是最常被忽視的行為差異：
- **ESM 是 Live Bindings (活體綁定)**：當模組 A 匯出一個變數，模組 B 匯入它，B 拿到的是**參考 (Reference)**。如果 A 修改了該變數，B 會讀到新值。
- **CJS 是 Copied Values (數值拷貝)**：當模組 A `module.exports` 一個物件，模組 B `require` 進來時，通常是拿到該物件的**快取拷貝**（除非匯出的是 mutable object 且你修改其屬性，但基本型別是斷開的）。

### 3. 模組即單例 (Module as Singleton)
在 Node.js 與瀏覽器中，模組在第一次被載入後會被**快取 (Cached)**。這意味著，如果你在模組頂層 `new` 一個實例並匯出，所有匯入該檔案的地方都會拿到**同一個實例**。這是 JavaScript 中最自然的 Singleton 實作方式。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 優先採用 ESM (ES Modules First)
除非維護極舊的 Node.js 專案，否則新專案應全面採用 ESM。
- **Why**: 瀏覽器原生支援、支援 Tree-shaking、更好的靜態分析工具支援 (Linting, TypeScript)。
- **How**: 在 `package.json` 設定 `"type": "module"` 或使用 `.mjs` 副檔名。

### 2. Named Exports over Default Exports
在架構決策上，**具名匯出 (Named Exports)** 優於 **預設匯出 (Default Exports)**。
- **重構友善 (Refactoring)**：IDE 可以準確地重新命名所有引用。
- **強制一致性 (Consistency)**：匯入者無法隨意命名變數（例如將 `User` class 匯入並命名為 `Customer`），減少認知負擔。
- **Tree-shaking**：具名匯出讓 Bundler 更容易識別哪些部分未被使用。

### 3. The "Module Singleton" Pattern
利用模組快取機制來管理全域狀態或連線，而非傳統 OOP 的 Singleton Class。

```javascript
// db.js
import { Database } from './DatabaseClass.js';

// 這裡執行初始化，所有 import 此檔案者共用此實例
export const db = new Database(process.env.DB_URL); 
```

### 4. The "Factory Function" Pattern (Dependency Injection)
為了提升**可測試性 (Testability)**，避免直接匯出實例（Side-effects），改為匯出工廠函式。這允許在單元測試中注入 Mock 依賴。

```javascript
// logger.js
export const createLogger = (config) => {
  return new Logger(config); // 每次呼叫產生新實例
};
```

### 5. Barrel Files (Index Exports)
使用 `index.js` (或 `index.ts`) 來聚合資料夾內的模組，對外提供統一介面。
- **優點**：封裝內部結構，外部只需 `import { A, B } from './features'`。
- **注意**：大型專案中過度使用 Barrel files 可能導致 Bundle size 增加（如果 Tree-shaking 設定不當）或循環依賴問題。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Dual Package" Hazard
同時發布支援 CJS 與 ESM 的套件時極易出錯。
- **問題**：使用者可能在同一個專案中，透過不同路徑同時載入了 CJS 版與 ESM 版的同一個套件。
- **後果**：`instanceof` 檢查失敗（因為是兩個不同的 Class 定義）、Singleton 狀態不同步（兩份快取）。
- **解法**：盡量只發布 ESM，或使用工具（如 `tupos`, `bunjee`）小心處理 conditional exports。

### 2. Circular Dependencies (循環依賴)
模組 A 引用 B，B 又引用 A。
- **在 CJS 中**：通常會導致其中一方拿到 `{}` (空物件)，因為 `exports` 尚未完成賦值。
- **在 ESM 中**：由於 Hoisting 和 Live Bindings，有時可以運作，但若存取時機過早（在模組頂層直接執行），仍會拋出 `ReferenceError`。
- **解法**：萃取共用邏輯到第三個模組 C，讓 A 和 B 都依賴 C。

### 3. Importing for Side Effects
僅為了執行模組內的程式碼而 import，卻不使用匯出值。
- **Bad**: `import './init-db.js';` (隱晦地修改了全域狀態或執行了連線)。
- **Better**: 匯出初始化函式並顯式呼叫。 `import { initDb } from './db.js'; initDb();`

### 4. Mutable Exports (修改匯出值)
雖然 ESM 允許 Live Bindings，但**不要從模組外部**嘗試修改匯入的變數。
```javascript
import { config } from './config.js';
config = {}; // Error: Assignment to constant variable.
```
即便匯出的是物件（Mutable），修改其屬性也是一種 Code Smell，因為這隱藏了狀態變更的來源。

---

## Checklists & workflows｜檢查清單與流程

### Architecture Decision: Starting a New Module
在建立新模組或功能時，請依序思考：

- [ ] **Format**: 專案是否已全面設定為 ESM (`"type": "module"`)？
- [ ] **State**: 這個模組需要保存狀態嗎？
  - [ ] **Yes (Global/Shared)**: 匯出已初始化的實例 (Singleton Pattern)。
  - [ ] **Yes (Isolated)**: 匯出 Class 或 Factory Function。
  - [ ] **No**: 匯出純函式 (Pure Functions)。
- [ ] **Exports**:
  - [ ] 是否使用了 **Named Exports** 而非 Default Export？
  - [ ] 是否建立了 `index.js` (Barrel) 來隱藏內部實作細節？
- [ ] **Dependencies**:
  - [ ] 是否產生了循環依賴？(使用 `madge` 等工具檢查)。
  - [ ] 是否依賴了帶有 Side Effects 的模組？

### Code Review Checklist
- [ ] 檢查是否混用了 `require` 與 `import` (除非在 migration 過渡期)。
- [ ] 檢查是否有 `import * as obj`，這可能會影響 Tree-shaking 效率，除非真的需要所有屬性。
- [ ] 確保沒有在模組頂層進行昂貴的運算（如同步讀檔、建立重型連線），這會拖慢應用程式啟動速度。

---

## Real-world examples｜實戰案例

### Case 1: Database Connection (Singleton vs. Factory)

**❌ Anti-pattern: Implicit Side Effect**
載入檔案時就連線，難以測試，且無法處理連線失敗重試。

```javascript
// db-bad.js
import mongoose from 'mongoose';
// Side effect: Happens immediately on import
mongoose.connect(process.env.MONGO_URI); 
export default mongoose;
```

**✅ Best Practice: Explicit Initialization (Singleton via Module)**
延遲連線，但保持單例。

```javascript
// db-good.js
import { MongoClient } from 'mongodb';

const client = new MongoClient(process.env.MONGO_URI);
let dbInstance = null;

// 匯出連線函式，讓呼叫者決定何時連線
export async function connectDB() {
  if (!dbInstance) {
    await client.connect();
    dbInstance = client.db('my_app');
  }
  return dbInstance;
}

// 也可以匯出 client 供關閉連線使用
export { client };
```

### Case 2: Handling Circular Dependencies

**❌ The Problem**

```javascript
// User.js
import { getPostsForUser } from './Post.js'; // Circular
export class User {
  getPosts() { return getPostsForUser(this.id); }
}

// Post.js
import { User } from './User.js'; // Circular
export function getPostsForUser(userId) {
  // ... logic using User class to format response
  return new User(data);
}
```

**✅ The Fix: Dependency Injection or Shared Interface**
不直接互相引用，而是透過參數傳遞或提取共用型別。

```javascript
// Post.js
// 移除對 User.js 的 import
export function getPostsForUser(userId, UserClassConstructor) {
  // 透過參數注入 User 類別，打破依賴
  return new UserClassConstructor(data);
}

// main.js (Controller)
import { User } from './User.js';
import { getPostsForUser } from './Post.js';

// 在組裝層(Composition Root)將它們結合
const posts = getPostsForUser(user.id, User);
```

### Case 3: Tree-shaking Friendly Exports

**❌ Hard to Tree-shake**
將所有工具函式包成一個大物件匯出。Bundler 很難知道你只用了其中一個。

```javascript
// utils.js
export default {
  formatDate: (date) => { /* ... */ },
  validateEmail: (email) => { /* ... */ },
  // ... 50 other functions
};

// app.js
import utils from './utils.js';
utils.formatDate(new Date()); // 整個 utils 物件都會被打包進去
```

**✅ Tree-shakeable**
獨立匯出。

```javascript
// utils.js
export const formatDate = (date) => { /* ... */ };
export const validateEmail = (email) => { /* ... */ };

// app.js
import { formatDate } from './utils.js'; 
// 只有 formatDate 會被打包，validateEmail 會被丟棄
```