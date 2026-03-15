# 錯誤排查與除錯指南 / Troubleshooting & Debugging Guide

## Mental model｜心智模型

### 1. The Compiler is a Pessimistic Detective
**編譯器是一位悲觀的偵探**

當 TypeScript 報錯時，不要將其視為「程式碼壞了」，而應視為「偵探發現了供詞（型別定義）與證據（實際代碼）之間的不一致」。
TS 的錯誤訊息通常是層狀的（Layered）：
1.  **Top Level**: 總體判決（例如：Type A is not assignable to Type B）。
2.  **Middle Level**: 推導過程（因為 A 的屬性 `x` 是 string，但 B 需要 number）。
3.  **Bottom Level**: 根本原因（Root Cause）。

**Key Insight**: 在閱讀錯誤訊息時，**從下往上讀（Read from bottom to top）**。最底層的訊息通常最接近問題的核心，而最上層的訊息往往只是副作用。

### 2. Type Debugging vs. Runtime Debugging
**型別除錯 vs. 執行期除錯**

- **Runtime Debugging**: 使用 `console.log` 或 debugger 觀察變數的**值（Value）**。
- **Type Debugging**: 使用 IDE 的 Hover 功能、中間型別（Intermediate Types）或型別工具來觀察**型別的結構（Structure）**。

你不能用 `console.log` 來印出型別，你需要用「型別層面的 `console.log`」（例如 Hover 或特製的 Utility Types）來「看見」編譯器當下推斷出的結果。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. The `Prettify` Helper
**使用 `Prettify` 展開複雜型別**

當型別經過多次 `Pick`, `Omit`, `Partial` 或 Intersection (`&`) 操作後，VS Code 的 Hover 往往只會顯示 `A & B & C`，讓人看不清最終結構。使用 `Prettify` 強制展開型別。

```typescript
// 把這個工具型別加入你的專案或 snippet
type Prettify<T> = {
  [K in keyof T]: T[K];
} & {};

// Usage / 用法
type ComplexUser = Partial<User> & { role: string } & Timestamp;

// Hovering over `ReadableUser` will show the full object structure
// 滑鼠懸停在 ReadableUser 上，會看到展開後的完整物件結構，而非 A & B
type ReadableUser = Prettify<ComplexUser>;
```

### 2. Isolate with Intermediate Types
**使用中間型別隔離問題**

當一個巨大的表達式報錯時，不要試圖一次修好。將其拆解為多個 `type` 定義，找出是哪一步驟開始推斷錯誤（Type Inference Divergence）。

```typescript
// ❌ Hard to debug / 難以除錯
const result = complexFunction(param1, { ...config, nested: { ... } });

// ✅ Easier to debug / 易於除錯
type ConfigType = typeof config; // Check this
type NestedType = typeof config.nested; // Check this
// 透過拆解，確認傳入參數的型別是否如你預期
const arg2: ExpectedType = { ...config, nested: { ... } }; 
const result = complexFunction(param1, arg2);
```

### 3. Type Testing with `tsd` or `expect-type`
**使用工具進行型別測試**

不要只依賴「編譯通過」。對於複雜的 Utility Types 或函式庫作者，應該撰寫「型別測試」。這能確保當你升級 TS 版本或重構時，型別推斷邏輯沒有壞掉。

```typescript
import { expectType, expectNotType } from 'tsd'; // or 'expect-type'

// 假設你有一個 camelCase 轉換工具
declare function toCamelCase<S extends string>(s: S): CamelCase<S>;

// Test Case: 驗證型別推斷是否正確
expectType<"fooBar">(toCamelCase("foo_bar"));
expectNotType<string>(toCamelCase("foo_bar")); // 確保它不是寬泛的 string
```

### 4. The "Hover & Check" Technique
**懸停檢查法**

在寫出複雜邏輯前，先寫變數。
- 寫 `const x = ...`
- 滑鼠移上去看 TS 推斷 `x` 是什麼。
- 如果出現 `any` 或 `unknown`，立即停止並修復。不要讓 `any` 擴散到後面的程式碼。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Any" Silencer
**使用 `as any` 讓錯誤閉嘴**

- **Anti-pattern**: 遇到看不懂的錯誤，直接 `as any`。
- **Consequence**: 你關閉了該變數的所有型別檢查，這通常是 Bug 的溫床。
- **Better approach**: 如果真的解不出來，使用 `as unknown as TargetType`，這至少標記了這是一個不安全的轉型（Unsafe Cast），或者使用 `@ts-expect-error` 並加上註解說明原因。

### 2. Ignoring "Union Distribution"
**忽略聯合型別的分配律**

- **Pitfall**: 當你對 `A | B` 進行操作時，錯誤訊息可能會變得非常巨大且難以閱讀。
- **Diagnosis**: 檢查錯誤訊息中是否包含 `Type 'A' is not assignable to type 'Target'` AND `Type 'B' is not assignable...`。這意味著 TS 正在嘗試將 Union 的每一個成員都拿去匹配。
- **Fix**: 先縮小範圍（Narrowing）再進行操作。

### 3. Misreading "Could be undefined"
**誤讀「可能是 undefined」**

- **Pitfall**: 錯誤訊息顯示 `Object is possibly 'undefined'.`
- **Bad Fix**: 到處加 `!` (Non-null assertion)。
- **Better Fix**: 使用 Optional Chaining (`?.`) 或 Nullish Coalescing (`??`)，或者在邏輯前方加上 `if (!obj) return;` (Type Guard)。

---

## Checklists & workflows｜檢查清單與流程

### Debugging Workflow: The "Divide and Conquer"
**除錯流程：分而治之**

當你面對一個巨大的紅色波浪線時：

1.  **Read the Bottom**: 捲動錯誤訊息到最底部。
    - *是屬性缺失嗎？* (`Property 'id' is missing...`)
    - *是型別不匹配嗎？* (`Type 'string' is not assignable to 'number'`)
2.  **Simplify**: 註解掉大部分程式碼，只留下報錯的那一行。
3.  **Explicit Type Check**: 建立一個臨時變數，顯式標註你**期望**的型別。
    ```typescript
    // Debugging line
    const _debug: ExpectedType = suspiciousVariable;
    ```
4.  **Inspect Inference**: 滑鼠懸停在 `suspiciousVariable` 上，看 TS 認為它是什麼。
5.  **Compare**: 比較 `ExpectedType` 與 TS 推斷出的型別差異。

### Troubleshooting Checklist
**排查清單**

- [ ] **檢查拼寫 (Typos)**: 屬性名稱是否拼錯？（JS/TS 最常見錯誤）。
- [ ] **檢查 `undefined` / `null`**: 是否忘記處理可選屬性（Optional Properties）？
- [ ] **檢查 Union Types**: 是否傳入了 `string | number` 但函式只接受 `string`？
- [ ] **檢查泛型約束 (Constraints)**: 泛型 `T` 是否滿足 `extends SomeShape`？
- [ ] **檢查 Library 定義**: 第三方套件的 `@types` 版本是否與實作版本不一致？
- [ ] **重啟 TS Server**: 有時候 IDE 會卡住。(`Cmd/Ctrl + Shift + P` -> `TypeScript: Restart TS Server`)。

---

## Real-world examples｜實戰案例

### Case 1: Debugging a React Component Prop Mismatch
**案例：React 元件屬性不匹配**

**情境**: 你傳遞了 props 給一個元件，但出現了長達 20 行的錯誤訊息。

```typescript
// Component Definition
interface ButtonProps {
  variant: 'primary' | 'secondary';
  onClick: (e: React.MouseEvent) => void;
  children: React.ReactNode;
}
const Button = (props: ButtonProps) => { /* ... */ };

// ❌ Error Usage
// Error: Type '{ variant: string; onClick: () => void; children: string; }' 
// is not assignable to type 'ButtonProps'.
// Types of property 'variant' are incompatible...
<Button variant="danger" onClick={() => {}}>Click me</Button>
```

**Troubleshooting Steps**:
1.  **讀底部訊息**: `Type '"danger"' is not assignable to type '"primary" | "secondary"'`.
2.  **分析**: 雖然 `danger` 是字串，但它不在允許的 Literal Union 中。
3.  **修復**: 修改 `variant` 或擴充 `ButtonProps`。

### Case 2: The "Vanishing" Type (Widening)
**案例：消失的 Literal Type (型別寬化)**

**情境**: 你定義了一個常數物件，但在傳遞時報錯，說 `string` 不能指派給 `'GET' | 'POST'`。

```typescript
const requestConfig = {
  url: '/api/user',
  method: 'GET' // TS infers this as 'string', not 'GET'
};

function fetchApi(url: string, method: 'GET' | 'POST') { /* ... */ }

// ❌ Error: Argument of type 'string' is not assignable to parameter of type '"GET" | "POST"'.
fetchApi(requestConfig.url, requestConfig.method);
```

**Diagnosis**: TS 預設會將物件屬性推斷為較寬的型別（Widening），因為物件是可變的（Mutable），TS 認為你隨時可能把 `method` 改成別的字串。

**Solution**:
```typescript
// Fix 1: As const assertion (Recommended)
const requestConfig = {
  url: '/api/user',
  method: 'GET'
} as const; // Locks all properties to their literal values

// Fix 2: Inline definition
fetchApi('/api/user', 'GET');
```

### Case 3: Using `ExpectType` for Library Development
**案例：開發工具函式庫時的測試**

**情境**: 你寫了一個 `DeepPartial` 工具型別，你想確保它能正確處理巢狀結構。

```typescript
import { expectType } from 'tsd';

type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

interface User {
  id: number;
  profile: {
    name: string;
    address: {
      city: string;
    }
  }
}

// 實際測試程式碼 (不會被編譯到 runtime，但在開發時會檢查)
const partialUser = {} as DeepPartial<User>;

// 驗證第一層
expectType<number | undefined>(partialUser.id);

// 驗證巢狀層
expectType<string | undefined>(partialUser.profile?.address?.city);

// 驗證不應該存在的屬性 (報錯即成功)
// @ts-expect-error
partialUser.profile.age; 
```