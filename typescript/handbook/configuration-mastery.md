# TSConfig 配置詳解與環境設定 / TSConfig Mastery & Environment Setup

## Mental model｜心智模型

要掌握 `tsconfig.json`，不能只把它當作一堆雜亂的開關。你需要建立兩個核心維度的心智模型：**「分析維度 (Analysis)」** 與 **「輸出維度 (Emit)」**。

To master `tsconfig.json`, stop treating it as a random bag of switches. You need a mental model based on two core dimensions: **Analysis** and **Emit**.

### 1. The Two Pipelines Model (雙管線模型)
TypeScript 編譯器實際上同時在做兩件事，這兩件事由不同的配置控制：

1.  **Type Checking Pipeline (型別檢查管線)**:
    -   **關注點**: 程式碼的正確性、安全性。
    -   **關鍵參數**: `strict`, `noImplicitAny`, `strictNullChecks`。
    -   **心法**: 這是你的「數位導師」，越嚴格 (Strict)，它教你的越多，執行期錯誤越少。
2.  **Transpilation Pipeline (轉譯管線)**:
    -   **關注點**: 產出的 JavaScript 要長什麼樣子，以及如何被執行環境 (Runtime) 理解。
    -   **關鍵參數**: `target`, `module`, `moduleResolution`, `outDir`。
    -   **心法**: 這是你的「翻譯官」，它必須知道目標讀者是誰 (Browser, Node.js, or Deno)。

### 2. The Module Resolution Map (模組解析地圖)
大多數配置錯誤都源於對「模組 (Module)」的誤解。
-   **`module`**: 決定輸出的 JS 檔案使用什麼語法 (CommonJS `require` vs ESM `import`)。
-   **`moduleResolution`**: 決定 TS 如何**尋找**你 import 的檔案。這必須模擬你的執行環境或打包工具 (Bundler) 的行為。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Use `extends` from the Community (繼承社群標準)
不要從零開始手寫。使用 `@tsconfig/bases` 作為基底，確保你遵循該環境的最佳實踐。

Don't start from scratch. Use `@tsconfig/bases` to ensure you are following the best practices for your target runtime.

```json
// tsconfig.json
{
  // Node 18+ project
  "extends": "@tsconfig/node18/tsconfig.json",
  "compilerOptions": {
    "outDir": "dist",
    "baseUrl": "."
  }
}
```

### 2. Strictness is Non-Negotiable (嚴格模式不可妥協)
對於新專案，**永遠**開啟 `strict: true`。這會同時啟用 `noImplicitAny`, `strictNullChecks`, `strictFunctionTypes` 等關鍵檢查。

-   **Why**: 關閉嚴格模式等於放棄了 TypeScript 50% 的價值。
-   **Migration**: 如果是舊專案遷移，可以使用 `strict: false` 但手動開啟 `strictNullChecks` (這是最有價值的單一設定)。

### 3. Module Configuration Strategy (模組配置策略)
根據你的專案類型選擇正確的組合：

| Project Type | `module` | `moduleResolution` | Note |
| :--- | :--- | :--- | :--- |
| **Modern Frontend (Vite/Webpack)** | `ESNext` | `Bundler` | TS 5.0+ 推薦。讓 TS 知道打包工具會處理 import。 |
| **Node.js (CommonJS)** | `CommonJS` | `Node` (or `Node10`) | 傳統 Node 專案。 |
| **Node.js (ESM)** | `NodeNext` | `NodeNext` | 現代 Node 專案，強制正確的 ESM 副檔名 (.mjs/.js)。 |
| **Library Authoring** | `NodeNext` | `NodeNext` | 確保你的套件能同時支援 CJS 與 ESM 使用者。 |

### 4. Path Mapping for Clean Imports (路徑別名)
使用 `paths` 來避免 `../../../../components` 這種地獄。

```json
"compilerOptions": {
  "baseUrl": "./src",
  "paths": {
    "@core/*": ["core/*"],
    "@utils/*": ["utils/*"]
  }
}
```
**Critical Note**: TS 的 `paths` **只負責型別檢查**，它不會幫你改寫輸出的 JS 檔案路徑。你必須在 Runtime (Node) 或 Bundler (Vite/Webpack) 另外配置 Alias Resolver。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Path Mapping" Trap (路徑映射陷阱)
-   **Bad Pattern**: 在 `tsconfig.json` 設定了 `paths`，但沒有在 Webpack/Vite 或 `tsconfig-paths` (Node) 中做對應設定。
-   **Consequence**: TS 編譯通過 (Type check pass)，但程式一跑就炸開 (Runtime Error: Cannot find module)。
-   **Fix**: 確保 Build tool 的 alias 設定與 TSConfig 同步。

### 2. Ignoring `exclude` (忽略排除清單)
-   **Bad Pattern**: 讓 TS 編譯器去掃描 `node_modules` 或 build output 目錄。
-   **Consequence**: IDE 變慢，記憶體飆升，型別檢查卡頓。
-   **Fix**: 明確設定 `exclude`。
    ```json
    "exclude": ["node_modules", "dist", "coverage"]
    ```

### 3. Misunderstanding `target` vs `lib` (混淆目標與函式庫)
-   **Pitfall**: 以為把 `target` 設為 `ES5` 就不能用 `Promise` 或 `Array.prototype.includes`。
-   **Reality**:
    -   `target`: 決定語法降級 (Syntax Downleveling)，例如 `const` 變 `var`，`() =>` 變 `function`。
    -   `lib`: 告訴 TS 環境中有哪些內建物件 (Objects/APIs) 可用。
-   **Best Practice**: 如果你在舊瀏覽器跑新語法 (靠 Polyfill)，你可以設 `target: ES5` 但 `lib: ["ES2020", "DOM"]`。

### 4. `ts-node` Production Usage (正式環境使用 ts-node)
-   **Anti-pattern**: 在 Production 環境直接使用 `ts-node index.ts`。
-   **Consequence**: 啟動速度慢，記憶體消耗大。
-   **Fix**: Production 應執行編譯後的 JS (`node dist/index.js`)，或使用更快的 runtime 如 `tsx` / `swc` (但在 Production 仍建議預編譯)。

---

## Checklists & workflows｜檢查清單與流程

### Project Setup Checklist (專案初始設定清單)

- [ ] **Base Config**: 是否已繼承 `@tsconfig/bases` 對應的環境設定？
- [ ] **Strict Mode**: `strict` 是否設為 `true`？
- [ ] **Module Strategy**:
    - [ ] 前端專案：`module: ESNext`, `moduleResolution: Bundler`
    - [ ] 後端專案：`module: NodeNext`, `moduleResolution: NodeNext`
- [ ] **Output**: `outDir` 是否設定？`rootDir` 是否正確指向原始碼根目錄？
- [ ] **Scope**: `include` 和 `exclude` 是否精確鎖定原始碼範圍？
- [ ] **Interop**: 是否開啟 `esModuleInterop: true` 以支援 CommonJS 模組的 Default Import？

### Debugging "Cannot find module" (模組解析除錯流程)

1.  **Check Extension**: 檔案真的存在嗎？副檔名 (.ts, .tsx, .d.ts) 正確嗎？
2.  **Check Resolution**: `moduleResolution` 設定為何？
    -   如果是 `NodeNext`，你的 import 路徑是否包含了 `.js` 副檔名？(ESM Requirement)
3.  **Check Paths**: 如果用了 `@/` 開頭的路徑，`paths` 和 `baseUrl` 設定了嗎？
4.  **Check Types**: 該套件是否缺少型別定義？嘗試安裝 `@types/package-name`。

---

## Real-world examples｜實戰案例

### Scenario 1: Modern React App (Vite)
這是目前最主流的前端配置。重點在於將解析工作交給 Bundler，並支援 DOM API。

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    
    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true, // 允許 import .ts (Vite 處理)
    "resolveJsonModule": true,
    "isolatedModules": true, // Vite 使用 esbuild 轉譯，單檔轉譯需要此設定
    "noEmit": true, // Vite 負責打包，TS 只做檢查
    
    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### Scenario 2: Node.js Microservice (ESM)
針對原生支援 ESM 的 Node.js 服務。重點在於 `NodeNext` 的嚴格模組解析。

```json
{
  "extends": "@tsconfig/node18/tsconfig.json",
  "compilerOptions": {
    "rootDir": "src",
    "outDir": "dist",
    
    /* Strict ESM for Node */
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    
    "sourceMap": true, // 方便 Production 除錯
    "declaration": false, // 應用程式通常不需要產 .d.ts
    "removeComments": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "**/*.test.ts"]
}
```

### Scenario 3: Monorepo Library (Turborepo / Nx)
針對大型專案中的共用套件。重點是 `composite` 與 `declaration`。

```json
{
  "extends": "@tsconfig/node18/tsconfig.json",
  "compilerOptions": {
    "composite": true, // 啟用 Project References，加速增量編譯
    "declaration": true, // 必須產出型別定義供其他 package 使用
    "declarationMap": true, // 讓使用者可以 Go to Definition 跳轉回 TS 原始碼
    "sourceMap": true,
    "rootDir": "src",
    "outDir": "dist"
  },
  "include": ["src"]
}
```