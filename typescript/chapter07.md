# 1. 前言與學習目標 (Introduction & Learning Goals)

作為資深工程師，你可能面臨過將大型 JavaScript 遺留系統（Legacy System）遷移至 TypeScript 的挑戰。這不僅是語法上的轉換，更是一場涉及建置流程、團隊協作規範與長期維護性的工程治理。本章將超越單純的語法教學，專注於「如何安全、有效地落地 TypeScript」。

As a Senior Engineer, you have likely faced the challenge of migrating large legacy JavaScript systems to TypeScript. This is not merely a syntactic conversion; it is an engineering governance task involving build processes, team collaboration standards, and long-term maintainability. This chapter moves beyond basic syntax to focus on "how to safely and effectively implement TypeScript."

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **制定漸進式遷移策略 (Formulate a Progressive Migration Strategy)**：拒絕「Big Bang」重寫，學會如何設定 `allowJs` 與 `checkJs` 讓 JS 與 TS 共存，並依據業務價值排定遷移優先順序。
    **Formulate a Progressive Migration Strategy**: Reject "Big Bang" rewrites; learn how to configure `allowJs` and `checkJs` to allow JS and TS coexistence, and prioritize migration based on business value.

2.  **配置企業級 Linting 與 CI 流程 (Configure Enterprise-grade Linting & CI Pipelines)**：整合 ESLint、Prettier 與 Husky，並在 CI/CD 階段設定嚴格的 Type Check 閘門（Gatekeeper）。
    **Configure Enterprise-grade Linting & CI Pipelines**: Integrate ESLint, Prettier, and Husky, and establish strict Type Check gatekeepers within the CI/CD stage.

3.  **管理團隊協作規範 (Manage Team Collaboration Governance)**：定義專案的 `tsconfig` 嚴格程度（Strictness），並建立 Code Review 中關於型別設計的標準（例如：何時允許使用 `any`，何時必須定義 Interface）。
    **Manage Team Collaboration Governance**: Define the project's `tsconfig` strictness and establish Code Review standards regarding type design (e.g., when `any` is permissible vs. when Interfaces are mandatory).

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 遷移的光譜 (The Migration Spectrum)

許多工程師誤以為遷移是二元對立的（全 JS vs 全 TS）。實際上，遷移是一個「光譜」。
Many engineers mistakenly believe migration is binary (all JS vs. all TS). In reality, migration is a "spectrum."

*   **Level 0 (Loose)**: 純 JavaScript，無型別檢查。
    **Level 0 (Loose)**: Pure JavaScript, no type checking.
*   **Level 1 (Coexistence)**: TS 編譯器處理 JS 檔案 (`allowJs: true`)，但不強制檢查。
    **Level 1 (Coexistence)**: TS compiler handles JS files (`allowJs: true`) but enforces no checks.
*   **Level 2 (Soft Check)**: 對 JS 檔案進行基本推斷檢查 (`checkJs: true`)，類似於加強版的 Linter。
    **Level 2 (Soft Check)**: Basic inference checks on JS files (`checkJs: true`), similar to a supercharged Linter.
*   **Level 3 (Strict TS)**: 全面 TS 檔案，開啟 `strict: true`，禁止隱式 `any`。
    **Level 3 (Strict TS)**: Full TS files, `strict: true` enabled, implicit `any` forbidden.

**心智模型**：將遷移視為「裝修房子且同時住在裡面」。你不能一次拆掉所有支柱（Big Bang Rewrite），必須逐個房間進行（Module-by-Module），並確保水電（Build Pipeline）在過程中保持運作。
**Mental Model**: View migration as "renovating a house while living in it." You cannot tear down all pillars at once (Big Bang Rewrite); you must proceed room by room (Module-by-Module) and ensure utilities (Build Pipeline) remain functional throughout the process.

## 2.2 嚴格模式的層次 (Layers of Strictness)

TypeScript 的 `strict` flag 實際上是一組 flag 的集合。資深工程師應理解如何拆解它們以分階段導入。
TypeScript's `strict` flag is actually a collection of flags. Senior engineers should understand how to decompose them for phased adoption.

*   `noImplicitAny`: 最重要的防線，防止變數退化為 `any`。
    `noImplicitAny`: The most critical defense line, preventing variables from degenerating into `any`.
*   `strictNullChecks`: 防止 `undefined` is not an object 錯誤的核心。通常是遷移中最痛苦但也最有價值的一步。
    `strictNullChecks`: The core protection against `undefined` is not an object errors. Often the most painful but valuable step in migration.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 系統架構中的角色 (Role in System Architecture)

在微服務或大型單體架構中，TypeScript 的遷移策略直接影響「開發速度」與「系統穩定性」的權衡。
In microservices or large monolith architectures, TypeScript migration strategies directly impact the trade-off between "development velocity" and "system stability."

*   **邊界合約 (Boundary Contracts)**：優先遷移 API 層（DTOs）與資料庫模型。這能為系統建立「型別防護網」，即使內部邏輯仍是 JS，外部介面已受控。
    **Boundary Contracts**: Prioritize migrating the API layer (DTOs) and database models. This establishes a "type safety net" for the system; even if internal logic remains JS, external interfaces are controlled.
*   **共用函式庫 (Shared Libraries)**：若團隊維護內部的 npm packages，這些必須優先遷移並提供 `.d.ts`，否則所有依賴它的服務都無法享受 TS 的紅利。
    **Shared Libraries**: If the team maintains internal npm packages, these must be migrated first and provide `.d.ts` files; otherwise, all dependent services cannot reap the benefits of TS.

## 3.2 CI/CD 整合 (CI/CD Integration)

在系統設計視角下，TypeScript 不僅是開發工具，更是 CI 流程中的靜態分析環節。
From a system design perspective, TypeScript is not just a development tool but a static analysis step in the CI pipeline.

*   **Type Check 作為 Blocking Step**：在 Build 之前執行 `tsc --noEmit`。如果型別檢查失敗，禁止部署。
    **Type Check as a Blocking Step**: Execute `tsc --noEmit` before the Build step. If type checking fails, deployment is forbidden.
*   **增量檢查 (Incremental Checks)**：對於巨型專案，使用 Project References 或 `tsc --incremental` 來縮短 CI 時間。
    **Incremental Checks**: For massive projects, use Project References or `tsc --incremental` to reduce CI time.

---

# 4. 逐步示例 (Walkthrough / Example)

## 場景：遷移一個核心 JS 模組 (Scenario: Migrating a Core JS Module)

假設我們有一個處理使用者訂單的 `orderService.js`，目標是將其遷移為 TS，並加入嚴格檢查。
Suppose we have an `orderService.js` handling user orders. The goal is to migrate it to TS and enforce strict checks.

### Step 1: 調整 tsconfig.json (Adjust tsconfig.json)

首先，確保專案允許 JS 與 TS 共存。
First, ensure the project allows JS and TS coexistence.

```json
// tsconfig.json
{
  "compilerOptions": {
    "outDir": "./dist",
    "allowJs": true,          // 允許編譯 JS 檔案 (Allow compiling JS files)
    "checkJs": false,         // 暫不檢查 JS 內容 (Do not check JS content yet)
    "strict": false,          // 先關閉嚴格模式 (Disable strict mode initially)
    "noImplicitAny": false,   // 允許隱式 any (Allow implicit any)
    "module": "commonjs",
    "target": "es6"
  },
  "include": ["src/**/*"]
}
```

### Step 2: 重新命名與初步修復 (Rename and Initial Fix)

將 `orderService.js` 改名為 `orderService.ts`。此時你會看到大量的紅色波浪線（Errors）。
Rename `orderService.js` to `orderService.ts`. You will immediately see a sea of red squiggly lines (Errors).

*   **策略 (Strategy)**：不要試圖一次修復所有邏輯錯誤。先用 `any` 或 `// @ts-ignore` 壓制錯誤，確保編譯通過。這聽起來反直覺，但這是為了保持「可部署狀態」。
    **Strategy**: Do not attempt to fix all logic errors at once. Suppress errors with `any` or `// @ts-ignore` first to ensure compilation passes. This sounds counter-intuitive, but it is to maintain a "deployable state."

```typescript
// src/orderService.ts

// 暫時定義一個 loose 的 interface (Temporarily define a loose interface)
interface Order {
  id: string;
  items: any[]; // TODO: Define Item type later
  total: number;
  [key: string]: any; // 允許額外屬性，避免遷移初期的 friction (Allow extra props to avoid friction during early migration)
}

export function processOrder(order: Order) {
  // ... logic
  // 如果有無法解決的型別錯誤：
  // @ts-expect-error: Legacy code relying on weird behavior
  const legacyData = order.someUndefinedProp; 
}
```

### Step 3: 逐步收緊與定義型別 (Tighten and Define Types)

現在檔案已經是 `.ts`，我們可以開始移除 `any` 並定義真實結構。
Now that the file is `.ts`, we can start removing `any` and defining real structures.

```typescript
// src/types/Order.ts
export interface OrderItem {
  productId: string;
  quantity: number;
  price: number;
}

export interface Order {
  id: string;
  items: OrderItem[];
  total: number;
  status: 'PENDING' | 'PAID' | 'SHIPPED'; // 使用 Union Types 替代字串 (Use Union Types instead of strings)
}
```

### Step 4: 啟用嚴格模式 (Enable Strict Mode)

當大部分檔案都遷移完成後，目標是開啟 `strict: true`。如果專案太大，可以使用 `strict: true` 但在特定檔案頂部加入 `// @ts-nocheck` 作為過渡。
Once most files are migrated, the goal is to enable `strict: true`. If the project is too large, enable `strict: true` globally but add `// @ts-nocheck` at the top of specific files as a transition.

**進階技巧 (Pro Tip)**: 使用 `tsc-strict` 或類似工具，只針對 git staged files 進行嚴格檢查，防止新程式碼品質退化。
**Pro Tip**: Use `tsc-strict` or similar tools to perform strict checks only on git staged files, preventing degradation of new code quality.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 永遠存在的 `any` (The Eternal `any`)

*   **錯誤 (Pitfall)**：為了快速過編譯，將所有參數設為 `any`，並且事後不再回頭修正。
    **Pitfall**: Setting all parameters to `any` just to pass compilation quickly, and never looking back to fix them.
*   **後果 (Consequence)**：你失去了 TypeScript 90% 的價值，且給團隊一種「我們已經在用 TS」的虛假安全感。
    **Consequence**: You lose 90% of TypeScript's value and give the team a false sense of security that "we are using TS."
*   **修正 (Fix)**：使用 `unknown` 替代 `any`，迫使開發者在使用變數前進行型別檢查（Type Narrowing）；或者設定 ESLint 規則 `@typescript-eslint/no-explicit-any` 為 `warn` 或 `error`。
    **Fix**: Use `unknown` instead of `any`, forcing developers to perform Type Narrowing before using the variable; or set the ESLint rule `@typescript-eslint/no-explicit-any` to `warn` or `error`.

## 5.2 忽略 Runtime Validation (Ignoring Runtime Validation)

*   **錯誤 (Pitfall)**：認為 TypeScript 的 Interface 能在執行期驗證 API 回傳的資料。
    **Pitfall**: Believing that TypeScript Interfaces can validate data returned from APIs at runtime.
*   **後果 (Consequence)**：TS 僅在編譯期存在。如果後端 API 變更，前端 TS 程式碼不會報錯，但會在執行期崩潰。
    **Consequence**: TS only exists at compile time. If the backend API changes, the frontend TS code won't complain, but it will crash at runtime.
*   **修正 (Fix)**：結合 `zod` 或 `io-ts` 等 Schema Validation 函式庫，在邊界層進行執行期驗證，並自動推導出 TS 型別。
    **Fix**: Combine with Schema Validation libraries like `zod` or `io-ts` to perform runtime validation at the boundary layer and automatically infer TS types.

## 5.3 過度複雜的型別體操 (Over-Engineering Types)

*   **錯誤 (Pitfall)**：在遷移初期就試圖寫出完美的 Generic Utility Types，導致程式碼難以閱讀。
    **Pitfall**: Trying to write perfect Generic Utility Types early in the migration, making the code unreadable.
*   **修正 (Fix)**：KISS (Keep It Simple, Stupid)。先寫重複的 Interface，待模式清晰後再重構為 Generics。可讀性 > 炫技。
    **Fix**: KISS (Keep It Simple, Stupid). Write repetitive Interfaces first, and refactor into Generics once patterns become clear. Readability > Showing off.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## 6.1 如何在不暫停業務開發的情況下遷移百萬行程式碼？
**How do you migrate a million lines of code without halting business development?**

*   **回答要點 (Key Points)**：
    *   **增量策略 (Incremental Strategy)**：強調 `allowJs` 配置。
    *   **高價值優先 (High Value First)**：優先遷移核心模組、共用 Utilities 或變動頻率高的檔案。
    *   **自動化 (Automation)**：提及使用 `ts-migrate` (Airbnb) 或類似腳本自動生成初步型別。
    *   **防守 (Defense)**：設定 CI 檢查，確保新程式碼必須是 TS 且通過嚴格檢查（Ratchet mechanism）。

## 6.2 團隊成員對 TypeScript 熟練度不一，如何推行？
**Team members have varying levels of TypeScript proficiency. How do you roll it out?**

*   **回答要點 (Key Points)**：
    *   **工具輔助 (Tooling)**：配置 ESLint 與 Prettier，讓機器當壞人（let the machine be the bad cop）。
    *   **Code Review 指南 (Review Guidelines)**：制定明確的 Checklist（例如：DTO 必須有 Interface）。
    *   **配對程式設計 (Pair Programming)**：資深帶資淺，特別是在處理複雜泛型時。
    *   **漸進式嚴格度 (Progressive Strictness)**：初期允許 `any`，但需標註 `TODO`，並安排 Tech Debt Sprint 清理。

## 6.3 什麼時候你應該選擇 **不** 遷移某些檔案？
**When should you choose NOT to migrate certain files?**

*   **回答要點 (Key Points)**：
    *   **即將廢棄 (Deprecation)**：如果該模組計畫在 3 個月內重寫或移除。
    *   **極低變動率 (Low Churn)**：如果是 5 年前寫好且極其穩定的 Helper function，且沒有依賴外部型別，遷移的 ROI 極低。
    *   **測試覆蓋率極低 (Low Test Coverage)**：在沒有測試保護下強行重構型別極易引入 Regression，應先補測試再遷移。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)

1.  **遷移是旅程而非開關 (Migration is a journey, not a switch)**：善用 `allowJs` 和 `checkJs` 進行平滑過渡。
2.  **嚴格模式分層導入 (Layered Strictness)**：先求有（編譯通過），再求好（`noImplicitAny`），最後求完美（`strictNullChecks`）。
3.  **邊界防禦 (Boundary Defense)**：優先為 API 回傳值與第三方套件定義型別，這是 ROI 最高的投資。
4.  **CI 是守門員 (CI is the Gatekeeper)**：沒有自動化檢查的規範只是建議，必須在 Pipeline 中強制執行 `tsc` 與 `eslint`。
5.  **文化重於工具 (Culture over Tooling)**：遷移成功的關鍵在於團隊共識，而非僅僅是 `tsconfig.json` 的設定。

## 後續延伸 (Next Steps)

*   **進階型別 (Advanced Types)**：當基礎遷移完成後，學習 `chapter08` 的 Conditional Types 與 Mapped Types 來減少重複程式碼。
    **Advanced Types**: Once basic migration is complete, study `chapter08` on Conditional Types and Mapped Types to reduce code duplication.
*   **效能優化 (Performance Optimization)**：研究如何優化 `tsc` 編譯速度，例如使用 Project References 或轉向 `esbuild`/`swc` 進行轉譯（Transpilation）。
    **Performance Optimization**: Research how to optimize `tsc` compilation speed, such as using Project References or switching to `esbuild`/`swc` for transpilation.