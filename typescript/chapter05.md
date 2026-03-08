# 1. 前言與學習目標 (Introduction & Learning Objectives)

在資深工程師的職涯中，隨著專案規模擴大，TypeScript 的編譯速度（Compilation Speed）與開發者體驗（DX）往往成為團隊的瓶頸。當 CI/CD 需要跑 20 分鐘，或者 IDE 的 IntelliSense 延遲數秒才出現，這就不再只是語法問題，而是架構問題。本章將探討如何透過架構設計來解決這些擴展性挑戰。

In the career of a Senior Software Engineer, as project scale increases, TypeScript compilation speed and Developer Experience (DX) often become bottlenecks for the team. When CI/CD pipelines take 20 minutes to run, or IDE IntelliSense lags for seconds, this ceases to be a syntax issue and becomes an architectural one. This chapter explores how to solve these scalability challenges through architectural design.

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **實作 Project References**：將巨大的單體 TS 專案拆解為多個獨立編譯單元，利用 Incremental Build 提升效能。
    **Implement Project References**: Break down massive monolithic TS projects into independent compilation units, leveraging Incremental Builds to boost performance.
2.  **配置 Monorepo 工具鏈**：整合 TypeScript 與現代 Monorepo 工具（如 Turborepo 或 Nx），實現 Build Caching 與並行執行。
    **Configure Monorepo Tooling**: Integrate TypeScript with modern Monorepo tools (like Turborepo or Nx) to achieve Build Caching and parallel execution.
3.  **診斷與優化編譯效能**：識別導致 `tsc` 變慢的元兇（如 Barrel Files、複雜遞迴型別），並應用最佳化策略。
    **Diagnose and Optimize Compilation Performance**: Identify culprits slowing down `tsc` (such as Barrel Files, complex recursive types) and apply optimization strategies.
4.  **設計可擴展的 `tsconfig` 繼承結構**：建立標準化的設定檔階層，確保團隊規範一致且易於維護。
    **Design Scalable `tsconfig` Inheritance**: Establish a standardized configuration hierarchy to ensure team consistency and maintainability.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 編譯器即資料庫 (The Compiler as a Database)

許多人將 TypeScript 編譯器視為單純的「翻譯機」（Transpiler），將 TS 轉為 JS。但在大型專案中，你應該將其視為一個**語意圖資料庫（Semantic Graph Database）**。

Many view the TypeScript compiler simply as a "Transpiler" that converts TS to JS. However, in large projects, you should view it as a **Semantic Graph Database**.

*   **Mental Model**: 當你修改一行程式碼，TS 需要遍歷依賴圖（Dependency Graph）來檢查型別安全性。如果整個專案是一個巨大的圖（Monolith），每次查詢（型別檢查）的成本極高。
*   **Mental Model**: When you change a line of code, TS needs to traverse the Dependency Graph to check for type safety. If the entire project is one giant graph (Monolith), the cost of every query (type check) is extremely high.

### 2.2 Project References: 專案的微服務化 (Project References: Microservices for Your Codebase)

TypeScript 3.0 引入的 Project References 允許你將程式碼庫切分為多個較小的邏輯區塊。這就像是將單體應用（Monolith）拆分為微服務（Microservices），每個部分有自己的邊界與介面。

Introduced in TypeScript 3.0, Project References allow you to slice your codebase into smaller logical chunks. This is akin to breaking a Monolith application into Microservices, where each part has its own boundaries and interfaces.

*   **Isolation**: 每個子專案（Project）有自己的 `tsconfig.json`，且只能存取它明確宣告依賴的其他專案。
    **Isolation**: Each sub-project has its own `tsconfig.json` and can only access other projects it explicitly declares as dependencies.
*   **Incremental Builds**: 修改底層 Library 時，只有相依的上層 App 需要重新檢查，而非整個世界。
    **Incremental Builds**: When modifying a low-level Library, only the dependent upper-level Apps need re-checking, not the entire world.

### 2.3 Monorepo Orchestrators vs. TypeScript Compiler

釐清職責邊界至關重要：
Clarifying the boundaries of responsibility is crucial:

*   **TypeScript (`tsc -b`)**: 負責理解程式碼之間的依賴關係，並執行型別檢查與程式碼生成。它知道「型別正確性」。
    **TypeScript (`tsc -b`)**: Responsible for understanding code dependencies, performing type checking, and code generation. It knows "Type Correctness".
*   **Orchestrators (Nx, Turborepo)**: 負責任務調度（Task Scheduling）與快取（Caching）。它知道「這個任務以前跑過嗎？檔案有變更嗎？」。
    **Orchestrators (Nx, Turborepo)**: Responsible for Task Scheduling and Caching. It knows "Has this task run before? Have files changed?".

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在 Big Tech 環境中，我們通常維護著數百萬行程式碼的 Monorepo。如果缺乏適當的架構，開發效率會急劇下降。

In Big Tech environments, we often maintain Monorepos with millions of lines of code. Without proper architecture, development efficiency plummets.

### 3.1 典型系統架構 (Typical System Architecture)

一個標準的 TypeScript Monorepo 結構通常如下：
A standard TypeScript Monorepo structure typically looks like this:

```text
root/
├── apps/
│   ├── web-dashboard (Next.js)
│   ├── mobile-app (React Native)
│   └── api-server (NestJS/Express)
├── packages/
│   ├── ui-kit (Shared Components)
│   ├── core-utils (Date, Currency logic)
│   ├── api-client (Generated SDKs)
│   └── tsconfig/ (Shared Configs)
├── package.json
├── turbo.json (or nx.json)
└── tsconfig.json (Root Reference)
```

### 3.2 對系統品質的影響 (Impact on System Quality)

1.  **可維護性 (Maintainability)**:
    *   強制執行模組邊界。例如，`core-utils` 不應該依賴 `ui-kit`。Project References 會在編譯層級直接報錯，防止架構腐化。
    *   Enforces module boundaries. For example, `core-utils` should not depend on `ui-kit`. Project References will error at the compilation level, preventing architectural rot.

2.  **CI/CD 效能 (CI/CD Performance)**:
    *   透過 Remote Caching（如 Turborepo Remote Cache），如果某個 PR 只改了 `web-dashboard`，CI 系統會直接從快取拉取 `ui-kit` 和 `api-server` 的建置結果，將建置時間從 15 分鐘縮短至 2 分鐘。
    *   Through Remote Caching (e.g., Turborepo Remote Cache), if a PR only changes `web-dashboard`, the CI system pulls build artifacts for `ui-kit` and `api-server` directly from the cache, reducing build time from 15 minutes to 2 minutes.

3.  **開發者體驗 (DX)**:
    *   IDE 回應速度更快，因為 Language Server 只需要處理當前 context 相關的專案，而非載入整個 Monorepo。
    *   Faster IDE response times, as the Language Server only needs to process projects relevant to the current context, rather than loading the entire Monorepo.

---

# 4. 逐步示例 (Walkthrough / Example)

### 情境：從單體配置遷移至 Project References
### Scenario: Migrating from Monolithic Config to Project References

假設我們有一個簡單的 Monorepo，包含一個 `app` 和一個 `shared` library。目前的 `tsconfig.json` 包含了所有檔案，導致修改 `shared` 會觸發全量檢查。

Assume we have a simple Monorepo containing one `app` and one `shared` library. The current `tsconfig.json` includes all files, causing changes in `shared` to trigger a full check.

#### Step 1: 建立基礎配置 (Create Base Configurations)

首先，抽離通用的設定到 `packages/tsconfig/base.json`。
First, extract common settings to `packages/tsconfig/base.json`.

```json
// packages/tsconfig/base.json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "CommonJS",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "composite": true, // 關鍵：啟用 Project References 支援
    "declaration": true, // 必須產生 .d.ts 供引用者使用
    "declarationMap": true
  }
}
```

*   **Note**: `composite: true` 是啟用 Project References 的核心，它強制 TypeScript 產生構建資訊（`.tsbuildinfo`），以便進行增量編譯。
*   **Note**: `composite: true` is the core of enabling Project References; it forces TypeScript to generate build information (`.tsbuildinfo`) for incremental compilation.

#### Step 2: 配置 Shared Library (Configure Shared Library)

在 `packages/shared/tsconfig.json` 中繼承基礎設定。
Inherit the base settings in `packages/shared/tsconfig.json`.

```json
// packages/shared/tsconfig.json
{
  "extends": "../tsconfig/base.json",
  "compilerOptions": {
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"]
}
```

#### Step 3: 配置 App 並引用 Library (Configure App and Reference Library)

這是最關鍵的一步。App 不再直接 import source code，而是透過 `references` 告訴 TS 它依賴 `shared` 專案。
This is the most critical step. The App no longer imports source code directly but uses `references` to tell TS it depends on the `shared` project.

```json
// apps/web/tsconfig.json
{
  "extends": "../../packages/tsconfig/base.json",
  "compilerOptions": {
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"],
  "references": [
    { "path": "../../packages/shared" }
  ]
}
```

#### Step 4: 根目錄聚合 (Root Aggregation)

根目錄的 `tsconfig.json` 變成一個空的協調者。
The root `tsconfig.json` becomes an empty coordinator.

```json
// tsconfig.json (Root)
{
  "files": [],
  "references": [
    { "path": "./packages/shared" },
    { "path": "./apps/web" }
  ]
}
```

#### Step 5: 執行構建 (Execute Build)

現在，我們使用 build mode (`-b`) 來執行編譯。
Now, we use build mode (`-b`) to execute compilation.

```bash
tsc -b --verbose
```

*   **Result**: TS 會先檢查 `shared`。如果 `shared` 沒變，它會直接使用快取的 `.d.ts`，然後只編譯 `web`。這將複雜度從 O(Total Code) 降低到 O(Affected Code)。
*   **Result**: TS checks `shared` first. If `shared` hasn't changed, it uses the cached `.d.ts` and only compiles `web`. This reduces complexity from O(Total Code) to O(Affected Code).

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 Barrel Files 的濫用 (The Abuse of Barrel Files)

*   **Anti-pattern**: 在 `index.ts` 中 `export * from './everything'`。
    **Anti-pattern**: Doing `export * from './everything'` in `index.ts`.
*   **Why it's bad**:
    1.  **效能 (Performance)**: 當你 import 這個 package 的任何一個小函式，TS 編譯器和 Bundler (如 Webpack) 往往需要解析該 Barrel File 導出的*所有*檔案，導致記憶體暴增和編譯變慢。
        **Performance**: When you import a single tiny function from this package, the TS compiler and Bundler (like Webpack) often need to resolve *all* files exported by that Barrel File, causing memory spikes and slow compilation.
    2.  **循環依賴 (Circular Dependencies)**: 這是造成 "Runtime undefined" 錯誤的常見元兇。
        **Circular Dependencies**: This is a common culprit for "Runtime undefined" errors.
*   **Solution**: 盡量明確 export，或者將大型 package 拆分為多個 entry points (例如 `import { ... } from '@ui/button'` 而非 `from '@ui'`)。

### 5.2 忽略 `exclude` 設定 (Ignoring `exclude` Configuration)

*   **Pitfall**: 沒有正確排除 `node_modules` 或建置產物目錄（如 `dist`, `build`）。
    **Pitfall**: Failing to correctly exclude `node_modules` or build artifact directories (like `dist`, `build`).
*   **Consequence**: TS 會嘗試解析並監控這些資料夾中的檔案，這在大型專案中是災難性的效能殺手。
    **Consequence**: TS attempts to parse and watch files in these directories, which is a catastrophic performance killer in large projects.
*   **Fix**: 始終在 `tsconfig.json` 中明確設定 `"exclude": ["node_modules", "dist"]`。

### 5.3 複雜的遞迴型別 (Complex Recursive Types)

*   **Pitfall**: 撰寫深層嵌套的 Conditional Types 或遞迴型別來進行物件轉換。
    **Pitfall**: Writing deeply nested Conditional Types or recursive types for object transformation.
*   **Why**: TS 編譯器有遞迴深度限制，且這類計算是指數級的。它會拖慢 IDE 的 IntelliSense。
    **Why**: The TS compiler has recursion depth limits, and such computations are exponential. It slows down IDE IntelliSense.
*   **Fix**: 使用 Interface 擴展代替複雜的 Intersection Types (`&`)，並利用 `interface` 的快取特性（Interface 在 TS 內部有較好的快取機制）。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 請解釋 TypeScript 的 Project References 解決了什麼問題？與單純的 `import` 有何不同？
### Q1: Explain what problem TypeScript Project References solve. How is it different from simple `import`?

*   **高分回答要點 (Key Points)**:
    *   **邏輯邊界 (Logical Boundaries)**: 強制依賴方向，防止架構混亂（如 utils 依賴 UI）。
    *   **效能 (Performance)**: 允許 **Incremental Builds**。`tsc -b` 可以跳過未變更的專案，直接使用 `.d.ts`，而非重新解析源碼。
    *   **記憶體 (Memory)**: 編譯器不需要一次將所有源碼載入記憶體，而是分塊處理。

### Q2: 在大型 Monorepo 中，你會如何優化 CI/CD 的 TypeScript 檢查時間？
### Q2: How would you optimize TypeScript check times in a CI/CD pipeline for a large Monorepo?

*   **高分回答要點 (Key Points)**:
    *   **工具層 (Tooling)**: 使用 Nx 或 Turborepo 進行 **Affected Build**（只構建受影響的專案）。
    *   **快取層 (Caching)**: 實作 Remote Caching，跨機器共享構建產物（`.tsbuildinfo`, `.d.ts`）。
    *   **配置層 (Config)**: 使用 `skipLibCheck: true` 忽略 `node_modules` 的型別檢查（假設依賴庫是正確的）。
    *   **硬體層 (Hardware)**: 垂直擴展 CI Runner 的記憶體，避免 OOM (Out of Memory) 導致的 Crash 重試。

### Q3: 什麼是 "Type Instantiation" 造成的效能瓶頸？如何偵測？
### Q3: What is a performance bottleneck caused by "Type Instantiation"? How do you detect it?

*   **高分回答要點 (Key Points)**:
    *   這發生在 TS 嘗試計算複雜型別（如大型 Union 或遞迴 Conditional Types）時。
    *   **偵測**: 使用 `tsc --generateTrace trace` 並載入 `chrome://tracing` 或使用 `@typescript/analyze-trace` 工具來視覺化編譯過程，找出耗時最長的型別。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)

1.  **Compiler as a Graph**: TS 編譯器處理的是依賴圖，優化效能就是優化圖的遍歷。
2.  **Project References**: 是大型專案的標準配置，提供**封裝 (Encapsulation)** 與 **增量編譯 (Incremental Builds)**。
3.  **Monorepo Tooling**: `tsc` 負責型別，Turborepo/Nx 負責調度與快取。兩者結合才能達到最佳效能。
4.  **Config Hierarchy**: 透過 `extends` 建立可維護的 `tsconfig` 繼承樹。
5.  **Avoid Barrel Files**: 減少不必要的重新導出（Re-exports），以減輕編譯器與 Bundler 的負擔。

### 後續延伸 (Next Steps)

*   **Advanced Type Manipulation**: 在優化了架構後，下一章將深入探討如何撰寫高效且強大的型別工具（Utility Types），同時避免效能陷阱。
*   **Custom Transformers**: 研究如何使用 TS Compiler API 撰寫自定義轉換器（如 `ts-patch`），在編譯期進行程式碼生成或優化。