# 常見陷阱與反模式 / Common Pitfalls & Anti-patterns

## Mental model｜心智模型

在探討 TypeScript 的反模式時，我們必須建立一個核心觀念：**TypeScript 是為了「描述」執行期的行為，而不是「改變」它。**

大多數的陷阱（Pitfalls）都源於以下兩種錯誤的心智模型：
1.  **過度依賴 TypeScript 的魔法**：誤以為 TS 的語法（如 Enums 或 Class）會自動產生優化過的 JS，卻忽略了它們帶來的執行期負擔（Runtime Overhead）。
2.  **為了便利而對編譯器撒謊**：使用 `any` 或 `as` 強制過關。這就像是關掉煙霧偵測器來解決火災警報，雖然當下安靜了，但風險（Runtime Error）依然存在。

**The "Soundness" Spectrum (型別健全度光譜):**
將你的程式碼視為位於光譜上：
- **Unsound (不健全)**: 到處是 `any`、`as`，編譯器無法保證型別安全。
- **Sound (健全)**: 透過 Type Guards、Discriminated Unions 和 `unknown` 確保每一行程式碼在執行前都經過驗證。

避免反模式的目標，就是盡量將程式碼往 **Sound** 的方向移動。

---

## Patterns & best practices｜常見模式與最佳實務

在真實專案中，我們推薦用以下模式來替代常見的陷阱：

### 1. 用 `Union Types` + `as const` 取代 `Enums`
TypeScript 的 `enum` 是少數會產生執行期程式碼（Runtime Code）的功能之一，且 Numeric Enums 存在 Reverse Mapping 問題，String Enums 則是 Nominal Typing（名義型別），與 TS 的 Structural Typing（結構化型別）格格不入。

**Best Practice:** 使用 Object Literal 配合 `as const`。

```typescript
// ✅ Recommended Pattern
const UserRole = {
  Admin: 'ADMIN',
  User: 'USER',
  Guest: 'GUEST',
} as const;

type UserRole = typeof UserRole[keyof typeof UserRole]; // 'ADMIN' | 'USER' | 'GUEST'
```

### 2. 用 `unknown` 取代 `any`
`any` 是放棄治療，`unknown` 則是「我知道它是某個東西，但我現在還不確定，使用前我會檢查」。

**Best Practice:** 當無法確定輸入型別時，標註為 `unknown`，並強制要求使用 Type Guard (型別防衛) 或 Zod 等驗證庫。

```typescript
// ✅ Recommended Pattern
function processInput(input: unknown) {
  if (typeof input === 'string') {
    console.log(input.toUpperCase()); // Safe
  } else {
    throw new Error("Expected string");
  }
}
```

### 3. 優先使用 POJO (Plain Old JavaScript Object) + Interface，而非 Class
除非你在使用高度依賴 OOP 的框架（如 NestJS, Angular），否則在 React/Vue 或純邏輯層中，過度使用 Class 會增加 bundle size 且難以序列化（Serialization）。

**Best Practice:** 定義資料的 `interface` 或 `type`，並撰寫純函式（Pure Functions）來操作這些資料。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The `any` Contagion (Any 的傳染性)
`any` 具有病毒般的傳染性。一旦一個變數被宣告為 `any`，任何由它衍生出的變數、函式回傳值都會變成 `any`，導致型別系統在該區塊完全失效。

*   **Bad:** `const data: any = JSON.parse(str); const id = data.id; // id is any`
*   **Consequence:** 失去了 IDE 的自動補全與重構保護，Bug 潛伏到 Production 才爆炸。

### 2. Type Assertion Abuse (濫用 `as`)
使用 `as` (Type Assertion) 是在告訴編譯器：「閉嘴，我比你更懂」。這通常是謊言。

*   **Bad:**
    ```typescript
    type User = { name: string; age: number };
    // ❌ Runtime Error waiting to happen: missing properties
    const user = {} as User;
    console.log(user.name.toUpperCase()); // Crash! user.name is undefined
    ```
*   **Pitfall:** 當你重構 `User` 型別時，`as User` 的地方不會報錯，導致資料結構與型別定義脫鉤。

### 3. The `Function` and `{}` Types
*   **Bad:** 使用 `Function` 型別。它接受任何參數並回傳 `any`。
*   **Bad:** 使用 `{}` 型別。這並不代表「空物件」，而是代表「除了 null/undefined 以外的任何非 null 值」（例如 `42` 也可以賦值給 `{}`）。
*   **Fix:** 使用具體的 `() => void` 或 `Record<string, never>` (空物件)。

### 4. Blindly Trusting API Responses
直接給 API 回傳值加上型別，而不做執行期驗證。

*   **Bad:** `const user = await fetch('/api/user').then(r => r.json()) as User;`
*   **Risk:** 後端改了欄位名，前端編譯通過，但執行期掛掉。這屬於 **System Boundaries** 的問題。

---

## Checklists & workflows｜檢查清單與流程

### Code Review Checklist (程式碼審查清單)

- [ ] **No Explicit `any`**: 是否使用了 `any`？能否改用 `unknown` 或泛型？
- [ ] **Assertion Justification**: 所有的 `as` 斷言是否有註解說明原因？（例如：處理 DOM API 或無法推導的第三方庫）。
- [ ] **Enum Check**: 是否引入了新的 `enum`？若是，是否有理由不使用 Union Types？
- [ ] **Strict Null Checks**: 是否有地方繞過了 null check（例如使用 `!` 非空斷言運算子）？
- [ ] **Boundary Validation**: 在接收外部資料（API, LocalStorage, User Input）時，是否有使用 Zod/Yup 或 Type Guards 進行驗證，而不僅僅是 `as`？

### Refactoring Workflow: Removing `any` (移除 Any 的重構流程)

當接手一個充滿 `any` 的遺留專案時：

1.  **Enable Strict Mode (Gradually):** 先在 `tsconfig.json` 開啟 `noImplicitAny: true`。
2.  **Trace the Source:** 找到 `any` 最早出現的地方（通常是 API 回傳或第三方庫）。
3.  **Apply `unknown`:** 將該處改為 `unknown`。
4.  **Fix Errors with Narrowing:** 跟隨編譯器的紅色波浪線，在下游使用 `typeof`, `instanceof`, 或 Custom Type Guards (`is`) 來收窄型別。
5.  **Use Generics:** 如果函式是為了處理多種型別，改用泛型 `<T>` 而非 `any`。

---

## Real-world examples｜實戰案例

### Case 1: The Enum Bundle Bloat (Enum 的體積膨脹)

**Anti-pattern (TypeScript):**
```typescript
enum Status {
  Pending,
  Active,
  Disabled
}
// 看起來很簡潔，但編譯出的 JS 包含了一個 IIFE (Immediately Invoked Function Expression)
// 且無法被 Tree-shaken (如果沒被使用也可能殘留)。
```

**Refactored (Best Practice):**
```typescript
const Status = {
  Pending: 0,
  Active: 1,
  Disabled: 2
} as const;

type Status = typeof Status[keyof typeof Status]; // 0 | 1 | 2

// 編譯後的 JS 只是單純的物件，甚至在編譯階段直接被替換成常數（如果使用 const enum，但 const enum 也有坑）。
// 這種寫法對 Bundler 最友善。
```

### Case 2: The "Lying" Assertion (說謊的斷言)

**Scenario:** 你正在寫一個表單提交功能。

**Anti-pattern:**
```typescript
interface FormData {
  username: string;
  email: string;
}

// ❌ 危險：初始化時為了騙過編譯器使用了 as
const formData = {} as FormData;

// ... 假設中間漏掉了 email 的賦值 ...
formData.username = "Alice";

submit(formData); // 送出 { username: "Alice" }，後端預期 email 存在，導致報錯。
```

**Refactored (Best Practice):**
```typescript
// ✅ 使用 Partial 或是正確的初始化
const formData: Partial<FormData> = {};

// 或者，強制完整初始化
const formData: FormData = {
  username: "",
  email: ""
};
```

### Case 3: The `any` Virus in Libraries (函式庫中的 Any 病毒)

**Scenario:** 使用第三方庫沒有型別定義。

**Anti-pattern:**
```typescript
import * as lib from 'legacy-lib';
const result: any = lib.complexCalculation(); 

// ❌ 病毒擴散
const metrics = result.metrics; // any
const score = metrics.average;  // any
// 完全沒有型別檢查，拼錯字也不會發現
console.log(score.toFixxd(2)); // Runtime Crash
```

**Refactored (Best Practice):**
```typescript
// ✅ 在邊界定義型別
interface CalculationResult {
  metrics: {
    average: number;
  }
}

// 使用 Type Assertion 在源頭阻斷 (或是寫一個 .d.ts 檔案)
const result = lib.complexCalculation() as CalculationResult;

const metrics = result.metrics; // Typed
const score = metrics.average;  // number
// console.log(score.toFixxd(2)); // Compile Error: Property 'toFixxd' does not exist.
```