# Chapter 06: Library Authoring & Declaration Files
# 第六章：函式庫開發與發布

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

As a Senior Engineer, you are often tasked with extracting shared logic into internal libraries or maintaining public SDKs. Writing code that works is only half the battle; ensuring the library provides a seamless Developer Experience (DX) through robust typing and correct module resolution is what distinguishes a senior-level contribution.
身為資深工程師，您經常需要將共用邏輯抽離為內部函式庫，或是維護對外的 SDK。撰寫能運作的程式碼只是成功的一半；確保該函式庫透過穩健的型別定義與正確的模組解析（Module Resolution）來提供無縫的開發者體驗（DX），才是區分資深貢獻者的關鍵。

By the end of this chapter, you will be able to:
完成本章後，您將能夠：

1.  **Master Declaration Files (`.d.ts`)**: Manually author and auto-generate declaration files to expose clean APIs while hiding implementation details.
    **精通宣告檔 (`.d.ts`)**：手動撰寫與自動產生宣告檔，以暴露乾淨的 API 介面，同時隱藏實作細節。
2.  **Configure Modern Module Resolution**: Correctly set up `package.json` "exports" maps to support both CommonJS (CJS) and ES Modules (ESM) consumers.
    **配置現代模組解析**：正確設定 `package.json` 中的 "exports" 對應，以同時支援 CommonJS (CJS) 與 ES Modules (ESM) 的使用者。
3.  **Handle Untyped Dependencies**: Use **Module Augmentation** and **Ambient Declarations** to provide types for third-party libraries that lack them.
    **處理無型別依賴**：使用 **Module Augmentation** 與 **Ambient Declarations** 為缺乏型別的第三方套件補上型別定義。
4.  **Design Library-Grade APIs**: Apply generics and constraints to create flexible, type-safe APIs that infer types correctly for the consumer.
    **設計函式庫等級的 API**：應用泛型與約束條件，設計出既靈活又具備型別安全，且能為使用者正確推斷型別的 API。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 The "Dual Worlds" Model: Runtime vs. Type System
### 2.1 「雙重世界」模型：執行時期 vs. 型別系統

When authoring a library, you are essentially shipping two products: the JavaScript (runtime logic) and the Declaration Files (type contract).
在開發函式庫時，您本質上是在交付兩個產品：JavaScript（執行邏輯）與宣告檔（型別合約）。

*   **Runtime (JS/MJS/CJS):** The actual building. It executes logic, handles errors, and processes data.
    **執行時期 (JS/MJS/CJS)**：實際的建築物。它執行邏輯、處理錯誤並運算資料。
*   **Type System (`.d.ts`):** The blueprint. It tells the consumer's IDE what functions exist, what arguments they take, and what they return, without needing to parse the actual code.
    **型別系統 (`.d.ts`)**：藍圖。它告訴使用者的 IDE 存在哪些函式、接受哪些參數以及回傳什麼，而無需解析實際的程式碼。

**Key Insight:** A library can be runtime-perfect but "type-broken" if the `.d.ts` files are missing or incorrect. Conversely, you can have perfect types that map to non-existent runtime code (a common issue with ambient declarations).
**關鍵洞察**：如果 `.d.ts` 檔案遺失或錯誤，一個函式庫可能在執行時期完美運作，但在「型別層面」卻是損壞的。反之，您也可能擁有完美的型別，卻對應到不存在的執行程式碼（這是 ambient declarations 常見的問題）。

### 2.2 Package Exports & Module Resolution
### 2.2 套件匯出與模組解析

Historically, `main` in `package.json` was enough. In the modern ecosystem, the `exports` field is the source of truth. It acts as a router for your package.
歷史上，`package.json` 中的 `main` 欄位就足夠了。但在現代生態系中，`exports` 欄位才是唯一真理。它充當了您套件的路由器。

*   **Encapsulation:** It prevents consumers from importing internal files (e.g., `import ... from 'pkg/internal/utils'`) unless explicitly exposed.
    **封裝**：它防止使用者匯入內部檔案（例如 `import ... from 'pkg/internal/utils'`），除非您明確暴露它們。
*   **Conditional Exports:** It serves different files depending on whether the consumer is using `require()` (CJS) or `import` (ESM), or even based on the environment (Node vs. Browser).
    **條件式匯出**：它根據使用者是使用 `require()` (CJS) 還是 `import` (ESM)，甚至根據環境（Node vs. Browser）來提供不同的檔案。

### 2.3 Ambient Declarations (`declare`)
### 2.3 Ambient Declarations (`declare`)

The `declare` keyword tells TypeScript: "Trust me, this variable/module exists at runtime, here is its shape." This is used when:
`declare` 關鍵字告訴 TypeScript：「相信我，這個變數/模組在執行時期是存在的，這是它的形狀。」這通常用於：

1.  Typing global variables (e.g., `window.myAnalytics`).
    為全域變數定義型別（例如 `window.myAnalytics`）。
2.  Creating types for a module that doesn't have its own types (`declare module 'untyped-lib'`).
    為沒有型別的模組建立型別（`declare module 'untyped-lib'`）。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### 3.1 The Role in Micro-frontends / Monorepos
### 3.1 在微前端 / Monorepos 中的角色

In a large-scale architecture (e.g., Nx monorepo or Lerna), shared libraries are the backbone.
在大規模架構中（例如 Nx monorepo 或 Lerna），共用函式庫是骨幹。

*   **Contract Enforcement:** The `.d.ts` files act as a strict contract between teams. If Team A changes a shared UI component's props, Team B's build should fail immediately in CI/CD, preventing runtime crashes in production.
    **合約執行**：`.d.ts` 檔案充當團隊之間的嚴格合約。如果 A 團隊更改了共用 UI 元件的 props，B 團隊的建置應該在 CI/CD 中立即失敗，從而防止正式環境中的執行崩潰。
*   **Build Performance:** TypeScript's `project references` and incremental builds rely heavily on declaration files. If your library exposes complex inferred types (instead of explicit types), it can significantly slow down the type-checking phase for all consumers.
    **建置效能**：TypeScript 的 `project references` 和增量建置高度依賴宣告檔。如果您的函式庫暴露了複雜的推斷型別（而非明確型別），可能會顯著拖慢所有使用者的型別檢查階段。

### 3.2 Security & Supply Chain
### 3.2 安全性與供應鏈

While TypeScript is a compile-time tool, proper library authoring mitigates supply chain risks.
雖然 TypeScript 是編譯時期的工具，但適當的函式庫開發方式能減輕供應鏈風險。

*   **Anti-pattern:** Publishing `src/` directly to npm.
    **反模式**：直接將 `src/` 發布到 npm。
*   **Best Practice:** Publish only compiled artifacts (`dist/`) and declaration files. This reduces the attack surface (no dev dependencies or test files in the production package) and ensures reproducible builds for consumers.
    **最佳實踐**：只發布編譯後的產物（`dist/`）和宣告檔。這減少了攻擊面（正式套件中沒有開發依賴或測試檔案），並確保使用者的建置結果可重現。

---

## 4. Walkthrough / Example
## 4. 逐步示例

### Scenario: Creating a Dual-Mode (CJS/ESM) Utility Library
### 情境：建立一個雙模式 (CJS/ESM) 的工具函式庫

We are building a library `@sys/logger` that needs to work in legacy Node.js services (CommonJS) and modern Frontend apps (ESM). We also need to use a third-party library `legacy-color-lib` that has no types.
我們要建立一個函式庫 `@sys/logger`，它需要能在舊版 Node.js 服務 (CommonJS) 和現代前端應用程式 (ESM) 中運作。我們還需要使用一個沒有型別的第三方套件 `legacy-color-lib`。

### Step 1: Handling the Untyped Dependency
### 步驟 1：處理無型別依賴

Create a file `src/types/legacy-color-lib.d.ts` to "shim" the missing types.
建立一個檔案 `src/types/legacy-color-lib.d.ts` 來「墊片（shim）」缺失的型別。

```typescript
// src/types/legacy-color-lib.d.ts

// Declare the module so TS knows it exists
// 宣告模組，讓 TS 知道它的存在
declare module 'legacy-color-lib' {
  export function colorize(text: string, color: string): string;
  export const version: string;
}
```

*Note: Ensure this file is included in your `tsconfig.json`'s `include` array.*
*注意：確保此檔案包含在 `tsconfig.json` 的 `include` 陣列中。*

### Step 2: The Library Code (Generics for Flexibility)
### 步驟 2：函式庫程式碼（利用泛型增加彈性）

We want a logger that allows custom metadata but enforces structure.
我們想要一個允許自訂 metadata 但強制結構化的 logger。

```typescript
// src/index.ts
import { colorize } from 'legacy-color-lib';

export interface LogEntry<TMeta = Record<string, unknown>> {
  level: 'info' | 'error';
  message: string;
  meta?: TMeta;
  timestamp: Date;
}

// Generic allows the consumer to define their own metadata shape
// 泛型允許使用者定義自己的 metadata 形狀
export class Logger<TGlobalMeta = {}> {
  constructor(private context: string) {}

  log<TLocalMeta = {}>(
    message: string, 
    meta?: TGlobalMeta & TLocalMeta
  ): LogEntry<TGlobalMeta & TLocalMeta> {
    const entry = {
      level: 'info' as const,
      message: colorize(message, 'blue'),
      meta,
      timestamp: new Date(),
    };
    
    console.log(`[${this.context}]`, entry);
    return entry;
  }
}
```

### Step 3: Configuring `tsconfig.json` for Libraries
### 步驟 3：為函式庫配置 `tsconfig.json`

Key settings for libraries: `declaration`, `declarationMap`, and `moduleResolution`.
函式庫的關鍵設定：`declaration`、`declarationMap` 與 `moduleResolution`。

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "NodeNext", // Critical for modern dual-emit support
    "moduleResolution": "NodeNext",
    "declaration": true, // Generate .d.ts
    "declarationMap": true, // Allow consumers to "Go to Definition" into your src
    "outDir": "./dist",
    "strict": true,
    "esModuleInterop": true
  },
  "include": ["src/**/*"]
}
```

### Step 4: The `package.json` Exports Strategy
### 步驟 4：`package.json` 的匯出策略

This is where the magic happens for supporting both CJS and ESM.
這是支援 CJS 與 ESM 的魔法所在。

```jsonc
// package.json
{
  "name": "@sys/logger",
  "version": "1.0.0",
  // Fallback for very old tools
  "main": "./dist/index.js", 
  "types": "./dist/index.d.ts",
  
  // Modern entry point
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.mjs", // ESM entry
      "require": "./dist/index.js"  // CJS entry
    }
  },
  "files": [
    "dist"
  ]
}
```

*Note: You would typically use a build tool like `tsup`, `rollup`, or `esbuild` to actually generate the `.mjs` and `.js` files from your TypeScript source.*
*注意：您通常會使用 `tsup`、`rollup` 或 `esbuild` 等建置工具，從您的 TypeScript 原始碼實際產生 `.mjs` 和 `.js` 檔案。*

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 The "Private Type Leak"
### 5.1 「私有型別洩漏」

**Error:** You use a type in an exported function, but you don't export the type itself.
**錯誤**：您在匯出的函式中使用了某個型別，但沒有匯出該型別本身。

```typescript
// BAD
interface InternalConfig { apiKey: string } // Not exported

export function init(config: InternalConfig) { /* ... */ }
```

**Why it's bad:** Consumers cannot create variables of type `InternalConfig` to pass into your function. They have to rely on inference or ugly utility types like `Parameters<typeof init>[0]`.
**為何不好**：使用者無法建立 `InternalConfig` 型別的變數來傳入您的函式。他們必須依賴推斷，或是使用像 `Parameters<typeof init>[0]` 這樣醜陋的工具型別。

**Fix:** Export any type that appears in your public API signature.
**修正**：匯出任何出現在您公開 API 簽章中的型別。

### 5.2 Global Pollution with `declare global`
### 5.2 使用 `declare global` 造成全域污染

**Error:** Modifying global interfaces (like `Window` or `Express.Request`) inside a library intended for general use.
**錯誤**：在旨在通用的函式庫中修改全域介面（如 `Window` 或 `Express.Request`）。

```typescript
// BAD (in a library)
declare global {
  interface Window {
    myLibLoaded: boolean;
  }
}
```

**Why it's bad:** If two libraries do this, they might conflict. It forces a global state on the consumer.
**為何不好**：如果有兩個函式庫都這樣做，它們可能會衝突。這強迫使用者接受全域狀態。

**Fix:** Only use module augmentation if the *primary purpose* of the library is to plugin/extend a specific framework (e.g., a specific Express middleware). Otherwise, keep state encapsulated.
**修正**：只有當函式庫的「主要目的」是外掛/擴充特定框架（例如特定的 Express middleware）時，才使用 module augmentation。否則，請保持狀態封裝。

### 5.3 Ignoring `exports` Encapsulation
### 5.3 忽略 `exports` 封裝

**Error:** Assuming users will only import what you documented.
**錯誤**：假設使用者只會匯入您文件所寫的內容。

**Why it's bad:** Users might `import { helper } from 'my-lib/dist/internal/helper'`. If you refactor your folder structure, you break their code.
**為何不好**：使用者可能會 `import { helper } from 'my-lib/dist/internal/helper'`。如果您重構資料夾結構，就會破壞他們的程式碼。

**Fix:** Use `package.json` "exports" to explicitly block access to internal paths.
**修正**：使用 `package.json` 的 "exports" 明確阻擋對內部路徑的存取。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: Handling Breaking Changes in Types
### Q1: 處理型別的破壞性變更

**Question:** "We need to change the type of a property in our library's configuration object from `string` to `string | number`. Is this a breaking change? What about the reverse?"
**問題**：「我們需要將函式庫設定物件中某個屬性的型別從 `string` 改為 `string | number`。這是破壞性變更嗎？反過來呢？」

**High-scoring Answer:**
**高分回答**：
*   **Widening (string -> string | number):** Usually **non-breaking** for *input* parameters (consumers can still pass a string). However, it *is* a breaking change if this type is a *return* value (consumers expecting only a string will now break).
    **放寬 (string -> string | number)**：對於「輸入」參數通常是**非破壞性**的（使用者仍然可以傳入字串）。然而，如果此型別是「回傳」值，這*就是*破壞性變更（原本預期只會收到字串的使用者程式碼會壞掉）。
*   **Narrowing (string | number -> string):** Definitely a **breaking change** for inputs (consumers passing numbers will fail).
    **限縮 (string | number -> string)**：對於輸入絕對是**破壞性變更**（傳入數字的使用者會失敗）。
*   **Strategy:** Discuss Semantic Versioning (SemVer) strictly applied to types.
    **策略**：討論嚴格應用於型別的語意化版本控制 (SemVer)。

### Q2: The "Missing Types" Problem
### Q2: 「缺失型別」問題

**Question:** "You are using a critical 3rd-party library that doesn't have `@types/package` and is written in plain JS. How do you integrate it into a strict TypeScript project?"
**問題**：「你正在使用一個關鍵的第三方套件，它沒有 `@types/package` 且是用純 JS 寫的。你會如何將它整合進嚴格的 TypeScript 專案？」

**High-scoring Answer:**
**高分回答**：
1.  **Short-term:** Create a `*.d.ts` file with `declare module 'package-name';` (implicit any) to unblock the build.
    **短期**：建立一個 `*.d.ts` 檔並寫入 `declare module 'package-name';`（隱式 any）以解鎖建置。
2.  **Mid-term:** Flesh out the declaration file with specific types for the functions actually used (Progressive Typing).
    **中期**：為實際使用到的函式補上具體的型別定義（漸進式型別化）。
3.  **Long-term:** Contribute the types to `DefinitelyTyped` or open a PR to the original repo to include types.
    **長期**：將型別貢獻給 `DefinitelyTyped`，或發 PR 給原始儲存庫以包含型別。

### Q3: Library Performance
### Q3: 函式庫效能

**Question:** "How can a library's type definitions affect the compilation speed of the consumer's project?"
**問題**：「函式庫的型別定義如何影響使用者專案的編譯速度？」

**High-scoring Answer:**
**高分回答**：
*   Mention **Type Inference vs. Explicit Types**. If a library forces the compiler to re-calculate complex conditional types or deep recursive types on every build, it slows down `tsc`.
    提到 **型別推斷 vs. 明確型別**。如果函式庫強迫編譯器在每次建置時重新計算複雜的條件型別或深層遞迴型別，會拖慢 `tsc`。
*   Solution: Use `import type` to avoid runtime overhead, and simplify exported types where possible (e.g., flattening interfaces).
    解法：使用 `import type` 避免執行時期負擔，並盡可能簡化匯出的型別（例如扁平化介面）。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Key Takeaways (記憶錨點)
### 重點摘要

1.  **Exports Map is King**: Use `package.json` "exports" to control entry points and support CJS/ESM dual modes securely.
    **Exports Map 為王**：使用 `package.json` "exports" 來控制進入點，並安全地支援 CJS/ESM 雙模式。
2.  **Declaration Files are Contracts**: Treat `.d.ts` files as a public API contract. Changes here require SemVer consideration.
    **宣告檔即合約**：將 `.d.ts` 檔案視為公開 API 合約。此處的變更需要考慮語意化版本 (SemVer)。
3.  **Ambient Modules (`declare module`)**: Your escape hatch for untyped dependencies. Use it wisely.
    **Ambient Modules (`declare module`)**：處理無型別依賴的逃生艙。請明智地使用。
4.  **No Private Leaks**: Always export types used in public function signatures.
    **無私有洩漏**：務必匯出公開函式簽章中使用的型別。
5.  **Generics for Consumers**: Use Generics in library APIs to let consumers inject their own types (e.g., payload schemas) while maintaining type safety.
    **為使用者設計泛型**：在函式庫 API 中使用泛型，讓使用者在保持型別安全的同時注入自己的型別（例如 payload schemas）。

### Next Steps (後續延伸)
### 下一步

*   **Advanced Types**: Now that you know how to *ship* types, learn how to write complex ones using **Conditional Types**, **Mapped Types**, and **Template Literal Types** to make your library even more powerful (Chapter 07).
    **進階型別**：既然您已知道如何*發布*型別，接下來學習如何使用 **條件型別 (Conditional Types)**、**映射型別 (Mapped Types)** 和 **樣板字面值型別 (Template Literal Types)** 來撰寫複雜型別，讓您的函式庫更強大（第 07 章）。
*   **Tooling**: Explore `tsup` or `api-extractor` (by Microsoft) to bundle your `.d.ts` files into a single file, cleaning up your distribution folder.
    **工具**：探索 `tsup` 或 `api-extractor`（Microsoft 出品），將您的 `.d.ts` 檔案打包成單一檔案，讓您的發布資料夾更整潔。