# 函式庫開發與型別定義發布 / Library Authoring & Declaration Files

## Mental model｜心智模型

### 1. The "Contract" Perspective (契約觀點)
作為函式庫作者，你交付的不僅是執行期的 JavaScript 程式碼，還有一份編譯期的「法律契約」——即 `.d.ts` 檔案。
- **Runtime (JS):** 負責邏輯正確性與效能。
- **Compile-time (DTS):** 負責開發者體驗 (DX) 與 API 邊界防護。
這兩者必須保持同步。如果 JS 允許某種行為但 TS 禁止（或反之），這就是「違約」。

### 2. Public vs. Internal Surface (公開與內部表面)
將你的型別視為一座冰山：
- **Public API:** 使用者可以直接 import 或透過函式回傳值接觸到的型別。這些必須有明確的命名、穩定的結構，且不應依賴使用者未安裝的第三方型別。
- **Internal Details:** 實作細節、Helper types。這些應該被封裝，避免洩漏到 `.d.ts` 中，以免造成使用者的編譯錯誤（例如：`Exported variable has or is using name 'X' from external module`）。

### 3. The Dependency Triangle (依賴三角關係)
在 `package.json` 中管理依賴時，必須區分三種角色：
- **Implementation Dependency:** 僅在 JS 執行時需要（放在 `dependencies`）。
- **Type Dependency:** 在 `.d.ts` 中被公開引用（必須放在 `dependencies`，否則使用者會報錯）。
- **Development Dependency:** 僅在開發/測試/構建時需要（放在 `devDependencies`）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Modern Packaging with `exports`
現代函式庫應優先支援 `package.json` 的 `exports` 欄位，以精確控制模組解析策略，同時支援 ESM 與 CJS。

```json
// package.json pattern
{
  "name": "my-lib",
  "type": "module",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.js",
      "require": "./dist/index.cjs"
    }
  },
  "main": "./dist/index.cjs",
  "module": "./dist/index.js",
  "types": "./dist/index.d.ts"
}
```
> **Note:** `"types"` 條件必須放在最前面（或非常前面），因為 TypeScript 解析器會尋找第一個符合的條件，若先匹配到沒有型別定義的欄位可能會停止搜尋。

### 2. Bundling Declaration Files (DTS Bundling)
不要直接發布 `tsc` 編譯出來的散亂 `.d.ts` 檔案結構。使用工具將型別定義「打包」成單一入口檔案。
- **Tools:** `tsup` (基於 esbuild), `rollup-plugin-dts`, `api-extractor` (Microsoft).
- **Benefit:** 加速使用者的編譯時間，隱藏內部目錄結構，避免使用者 import 到深層路徑 (`import ... from 'lib/dist/utils/helper'`)。

### 3. Explicit Return Types for Public API
雖然 TS 有強大的推斷能力，但對於 Library 的公開 API，**請務必顯式標註回傳型別**。
- 防止意外修改內部實作導致公開 API 的型別改變（Breaking Change）。
- 加速編譯器處理（不需要深入函式內容推斷）。

```typescript
// Good
export function calculate(a: number, b: number): number {
  return a + b;
}

// Bad (Risk of accidental change)
export function calculate(a: number, b: number) {
  return a + b; 
}
```

### 4. TSDoc & Comments
你的註解就是使用者的 IDE 提示。善用 TSDoc 標準 (`@param`, `@returns`, `@example`, `@deprecated`)。

```typescript
/**
 * Parses the user input string.
 * 
 * @param input - The raw string from user
 * @returns The parsed object
 * @throws {ValidationError} If input is malformed
 * 
 * @example
 * const result = parse("data");
 */
export function parse(input: string): Result { ... }
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Phantom Dependency" (幽靈依賴)
如果在你的 `.d.ts` 中使用了某個第三方型別（例如 `import { Request } from 'express'`），但你將 `express` 或 `@types/express` 放在 `devDependencies` 中。
- **後果:** 使用者安裝你的函式庫後，編譯會報錯，因為他們的 `node_modules` 裡沒有那個型別包。
- **修正:** 如果型別出現在公開 API，該型別包必須在 `dependencies` (或 `peerDependencies`)。

### 2. `const enum` in Libraries
盡量避免在函式庫中 `export const enum`。
- **原因:** `const enum` 預設會被編譯器內聯 (inline) 數值。如果使用者的編譯設定是 `isolatedModules` (如使用 Babel, esbuild, Vite 開發時)，或者你修改了 enum 數值但使用者沒有重新編譯他們的程式碼，會導致執行期錯誤或數值不一致。
- **建議:** 使用一般 `enum` 或 `Union Types` (`type Status = 'open' | 'closed'`)。

### 3. Global Augmentation Pollution (全域污染)
除非你的函式庫本身就是 Polyfill 或全域工具，否則嚴禁在頂層使用 `declare global` 或修改 `Window` / `String.prototype`。
- **風險:** 這會破壞使用者的環境，且難以除錯。
- **替代:** 使用 Module Augmentation，讓使用者顯式地導入並擴充。

### 4. Publishing Source `.ts` Files
不要將 `.ts` 原始碼發布給使用者直接引用（除非是特定生態系如 Deno）。
- **原因:** 使用者的 `tsconfig.json` 設定可能與你不同（例如 `strict` 模式），這會導致你的程式碼在他們的專案中報錯。始終發布編譯後的 `.js` + `.d.ts`。

---

## Checklists & workflows｜檢查清單與流程

### Pre-publish Checklist
在執行 `npm publish` 之前，請務必通過以下檢查：

- [ ] **Are The Types Wrong? (attw):** 使用 `attw` 工具檢查 package exports 是否正確配置，確保 ESM/CJS 使用者都能正確解析型別。
  - `npx @are-the-types-wrong/cli --pack .`
- [ ] **Publint:** 檢查 `package.json` 格式與檔案是否存在。
  - `npx publint`
- [ ] **Type Tests:** 是否撰寫了型別測試？（不僅測試邏輯，還要測試型別是否如預期報錯或通過）。
  - 工具推薦：`tsd` 或 `tstyche`。
- [ ] **Clean Dist:** 確保發布目錄中沒有包含原始碼、測試檔或無用的 config 檔。
- [ ] **SemVer Check:** 如果修改了 Public Interface 的型別（例如把 `string` 改成 `string | number`），這是否構成 Breaking Change？

### Decision Tree: Where to put `@types/foo`?

1.  **Is `foo` used in your library's implementation?**
    *   No -> Remove it.
    *   Yes -> Go to 2.
2.  **Does `foo`'s types appear in your generated `.d.ts` file?**
    *   (e.g., used in function arguments, return types, or exported interfaces)
    *   **Yes** -> Put `@types/foo` in **`dependencies`**.
    *   **No** (It's completely internal) -> Put `@types/foo` in **`devDependencies`**.

---

## Real-world examples｜實戰案例

### 1. The "Dual Package" Setup (tsup configuration)
這是一個使用 `tsup` 同時打包 ESM 與 CJS 並生成單一 `.d.ts` 的標準配置。

**tsup.config.ts:**
```typescript
import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['cjs', 'esm'], // 輸出兩種格式
  dts: true,              // 自動生成並打包 .d.ts
  splitting: false,
  sourcemap: true,
  clean: true,
  // 排除 peerDependencies 避免打包進去
  external: ['react', 'react-dom'], 
});
```

### 2. Handling "Exported variable has or is using name..."
當你匯出一個函式，但該函式回傳的型別沒有被匯出時，TS 會報錯。

**Problem:**
```typescript
// src/internal.ts
class SecretConfig { ... } // Not exported

// src/index.ts
import { SecretConfig } from './internal';

// Error: Return type of 'createConfig' is not exported
export function createConfig() {
  return new SecretConfig();
}
```

**Solution:**
要麼匯出該型別，要麼定義一個公開的介面 (Interface)。

```typescript
// src/index.ts
export interface PublicConfig {
  apiKey: string;
  // 只暴露公開屬性
}

class SecretConfig implements PublicConfig { ... }

// 明確標註回傳型別為公開介面
export function createConfig(): PublicConfig {
  return new SecretConfig();
}
```

### 3. Testing Types (using `tsd`)
確保你的型別限制如預期運作。

**index.test-d.ts:**
```typescript
import { expectType, expectError } from 'tsd';
import { myLibFunc } from '.';

// 驗證回傳型別是否正確
expectType<string>(myLibFunc(123));

// 驗證錯誤參數是否被 TS 捕捉
expectError(myLibFunc('invalid-arg'));
```