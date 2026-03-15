# 編譯效能與大型專案架構 / Compiler Performance & Monorepo Architecture

## Mental model｜心智模型

在處理 TypeScript 的效能問題時，我們需要將 `tsc` (TypeScript Compiler) 的運作想像成兩個獨立的維度：**「語法轉譯 (Transpilation)」** 與 **「型別檢查 (Type Checking)」**，並理解它是如何建立 **「依賴圖 (Dependency Graph)」** 的。

### 1. The "Graph Resolver" Model (依賴圖解析模型)
不要只把 `tsc` 當作一個編譯器，它本質上是一個 **靜態分析引擎**。
- **Monolithic Mode (單體模式)**：在傳統模式下，TS 必須一次性載入所有檔案，建立一個巨大的 AST (Abstract Syntax Tree)。只要改動一個底層檔案，可能會觸發全域的重新計算。
- **Project References (專案參照)**：這是 TS 處理大型架構的核心。將巨大的專案切分成數個小的「子專案 (Sub-projects)」。每個子專案就像一個獨立的 Library，擁有自己的邊界。當子專案 A 編譯完後，會產出 `.d.ts` 和 `.tsbuildinfo`；依賴它的專案 B 只需讀取 A 的 `.d.ts` (Declaration Maps)，而不需要重新解析 A 的原始碼。

### 2. The "Incremental Cache" (增量快取)
TS 的編譯效能優化極度依賴 **快取機制**。
- `.tsbuildinfo` 檔案是編譯器的記憶體。它記錄了上次編譯的檔案雜湊值 (Hash) 與依賴關係。
- 當你執行 `tsc --build` 時，TS 會比對磁碟上的檔案與 `.tsbuildinfo`，只重新編譯那些「真正受影響」的部分，而非整個專案。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 使用 Project References 拆分架構 (Splitting with Project References)
這是大型專案 (Monorepo) 的標準配備。不要讓一個 `tsconfig.json` 包含數千個檔案。

*   **實作方式**：
    *   將程式碼依功能拆分為 `packages/shared`, `packages/core`, `apps/frontend` 等。
    *   每個資料夾都有自己的 `tsconfig.json`。
    *   被引用的專案必須設定 `"composite": true`。
    *   引用者使用 `"references": [{ "path": "../shared" }]`。

### 2. 分離轉譯與檢查 (Separating Transpilation & Checking)
在現代開發流程中，`tsc` 通常太慢而不適合做「轉譯 (Emit)」。

*   **Pattern**：
    *   **Transpilation (Emit)**：使用 Rust/Go 寫成的工具（如 `swc`, `esbuild`, 或 Vite 內建的 rollup）來將 TS 轉為 JS。這些工具速度極快，但通常**不檢查型別**。
    *   **Type Checking**：使用 `tsc --noEmit` 僅進行型別檢查，通常在 CI/CD 或開發時的背景執行。
    *   **優點**：開發伺服器 (Dev Server) 啟動極快，同時保有型別安全性。

### 3. 配置優化 (Configuration Tuning)
針對 `tsconfig.json` 的關鍵優化設定：

*   `"incremental": true`：啟用增量編譯，產出 `.tsbuildinfo`。
*   `"skipLibCheck": true`：跳過 `.d.ts` 宣告檔案的型別檢查（通常是 `node_modules` 裡的）。這能大幅節省時間，因為我們假設第三方套件的型別是正確的。
*   `"exclude": ["node_modules", "dist", "**/*.spec.ts"]`：明確排除不需要編譯的檔案。

### 4. 嚴格控制 Barrel Files (Controlling Barrel Files)
Barrel Files (即只有 `export * from ...` 的 `index.ts`) 雖然方便引用，但對編譯器是負擔。

*   **Best Practice**：
    *   避免在專案根目錄放一個巨大的 `index.ts` 導出所有東西。
    *   如果必須使用，請確保工具鏈支援 Tree-shaking，並考慮在內部開發時直接引用具體路徑（雖然這犧牲了封裝性，但在超大型專案中常是必要的權衡）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Include All" Trap (全域包含陷阱)
最常見的效能殺手是在根目錄的 `tsconfig.json` 中寫了 `include: ["**/*"]`，卻沒有設定正確的 `exclude`。這會導致 TS 試圖編譯 `node_modules`、build artifacts 甚至 coverage 報告。

### 2. Circular Dependencies in Monorepos (循環依賴)
在使用 Project References 時，**絕對不允許**循環依賴（A 引用 B，B 引用 A）。
*   **後果**：`tsc --build` 會直接報錯或卡住。
*   **解法**：提取公共邏輯到第三個專案 C，讓 A 和 B 都引用 C。

### 3. Ignoring "Composite" Mode Constraints (忽略 Composite 限制)
當開啟 `"composite": true` 時，TS 強制要求程式碼必須能被獨立編譯。
*   **常見錯誤**：未顯式宣告回傳型別，導致 TS 必須推斷（Inference），這在跨專案引用時會造成效能瓶頸或錯誤。
*   **解法**：在公開 API (Public API) 上顯式標註型別。

### 4. Global Type Pollution (全域型別污染)
過度使用 `declare global` 或在沒有 `import/export` 的檔案中定義型別。
*   **後果**：當全域型別變更時，TS 必須重新檢查專案中的**所有**檔案，因為它無法確定哪些檔案依賴於這個全域變數。

---

## Checklists & workflows｜檢查清單與流程

### Performance Debugging Workflow (效能排查流程)

當你覺得 `tsc` 變慢時，請執行以下步驟：

- [ ] **Step 1: 診斷數據**
    執行 `tsc --extendedDiagnostics`。
    - 檢查 `File count`：是否編譯了預期外的檔案（如 `node_modules`）？
    - 檢查 `Check time` vs `I/O time`：是型別計算慢還是檔案讀取慢？
- [ ] **Step 2: 產生追蹤檔**
    執行 `tsc --generateTrace trace_output_dir`。
    - 使用 `@typescript/analyze-trace` 或將結果拖入 `chrome://tracing` 分析。
    - 找出是哪個檔案或哪個複雜型別（如遞迴型別）佔用了最多時間。
- [ ] **Step 3: 檢查配置**
    - [ ] 確認 `skipLibCheck` 為 `true`。
    - [ ] 確認 `incremental` 為 `true`。
    - [ ] 確認 `exclude` 正確排除了 build output 目錄。

### Monorepo Setup Checklist (大型專案設定清單)

- [ ] **Root Config**: 根目錄 `tsconfig.json` 應該幾乎是空的，只包含 `files: []` 和 `references: [...]`。
- [ ] **Base Config**: 建立一個 `tsconfig.base.json` 存放共用的 compilerOptions。
- [ ] **Leaf Configs**: 每個 package 繼承 base config，並設定 `"composite": true`。
- [ ] **Explicit Imports**: 確保 package 之間的引用是透過 `package.json` 的定義或 TS path mapping，而不是相對路徑 `../../`。

---

## Real-world examples｜實戰案例

### Scenario: A Monorepo with Frontend, Backend, and Shared Types

假設一個專案結構如下：
```text
/my-monorepo
  /packages
    /ui-lib       (Shared React components)
    /core-utils   (Shared logic)
  /apps
    /web-client   (Next.js app)
    /api-server   (NestJS app)
  tsconfig.json   (Root)
  tsconfig.base.json
```

#### 1. Root `tsconfig.json` (Solution Mode)
這只是一個入口，不做任何實際編譯。

```json
{
  "files": [],
  "references": [
    { "path": "./packages/ui-lib" },
    { "path": "./packages/core-utils" },
    { "path": "./apps/web-client" },
    { "path": "./apps/api-server" }
  ]
}
```

#### 2. Shared Library `packages/core-utils/tsconfig.json`
這是被依賴的底層模組。

```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "composite": true,        // 關鍵：允許被引用
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src"]
}
```

#### 3. Application `apps/web-client/tsconfig.json`
這是終端應用，引用了上面的 library。

```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "noEmit": true,          // Webpack/Next.js 會處理 emit，這裡只做檢查
    "paths": {
      "@my-org/core-utils": ["../../packages/core-utils/src"] 
      // 注意：在 Project References 模式下，通常建議指向 source
      // 但需配合 bundler 設定，或者指向 dist (d.ts)
    }
  },
  "references": [
    { "path": "../../packages/core-utils" },
    { "path": "../../packages/ui-lib" }
  ],
  "include": ["src"]
}
```

### Debugging Output Example

當你執行 `tsc --extendedDiagnostics` 時，你會看到類似這樣的輸出。注意 **Files** 和 **Total time**。

```text
Files:              500
Lines:              45000
Nodes:              180000
...
I/O Read time:      0.15s
I/O Write time:     0.02s
Parse time:         0.45s
Bind time:          0.20s
Check time:         1.50s  <-- 如果這裡異常高，代表有複雜型別運算
Total time:         2.32s
```

**Insight**: 如果 `Files` 數量高達 10,000+ 但你的專案只有 500 個檔案，代表你意外包含了 `node_modules`，請立即檢查 `exclude` 設定。