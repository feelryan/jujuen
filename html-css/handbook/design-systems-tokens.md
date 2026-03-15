# Design Systems 整合：Design Tokens 與主題管理 / Integrating Design Systems: Design Tokens and Theme Management

## Mental model｜心智模型

在現代 CSS 架構中，我們不再將樣式視為「寫死的數值」（Hardcoded Values），而是視為「資料的引用」（Data References）。

### 1. The Token Tier Structure (分層結構)
理解 Design Tokens 最重要的心智模型是 **「三層架構」**。不要直接將顏色數值綁定到元件上，而是透過中間層來管理語意。

1.  **Primitive Tokens (Global / Option Tokens)**:
    *   **定義**：最底層的原始數值，通常直接對應設計軟體的色票或格線。
    *   **例子**：`--blue-500: #3b82f6`, `--space-4: 1rem`.
    *   **心法**：這是一張「原物料清單」，除了展示色票外，**不應該在 UI 開發中直接使用**。

2.  **Semantic Tokens (Alias / Decision Tokens)**:
    *   **定義**：描述該數值的「用途」與「意圖」，而非它的外觀。這是 Design System 的核心。
    *   **例子**：`--color-action-primary: var(--blue-500)`, `--color-bg-surface: var(--white)`.
    *   **心法**：這是 API 介面層。當我們要實作 Dark Mode 時，我們切換的是這一層的映射關係，而不是去改 Component 的 CSS。

3.  **Component Tokens (Specific Tokens)**:
    *   **定義**：特定元件專用的變數，通常繼承自 Semantic Tokens。
    *   **例子**：`--btn-bg: var(--color-action-primary)`.
    *   **心法**：這層是為了隔離。如果按鈕需要獨立改變樣式而不影響其他使用 Primary Color 的元件，就在這層修改。

### 2. Theming as Context Switching (主題即上下文切換)
CSS Variables (Custom Properties) 具有繼承與 Scope 特性。
*   **Mental Model**: 主題切換本質上是「在不同的 DOM 節點（或屬性）上，重新定義 Semantic Tokens 的值」。
*   瀏覽器會根據當前的 Context (如 `[data-theme="dark"]`) 自動計算出最終的視覺呈現，無需 JavaScript 介入重繪樣式。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Naming Convention: CTI (Category-Type-Item)
採用業界標準的命名慣例（如 Style Dictionary 推薦的 CTI），能大幅降低溝通成本。
*   **Pattern**: `--category-type-item-state`
*   **Example**: `--color-text-primary-hover`
    *   `Category`: color
    *   `Type`: text
    *   `Item`: primary
    *   `State`: hover

### 2. The "Semantic Layer" Implementation (實作語意層)
永遠不要在元件中寫死顏色，也不要直接用 Primitive Tokens。

```css
/* ❌ Bad: 直接使用原始色 */
.button {
  background-color: #3b82f6; 
}

/* ⚠️ Risky: 直接使用 Primitive Token (難以實作 Dark Mode) */
.button {
  background-color: var(--blue-500);
}

/* ✅ Good: 使用 Semantic Token */
.button {
  background-color: var(--color-action-primary);
  color: var(--color-text-on-action);
}
```

### 3. Scoped Theming Strategy (作用域主題策略)
利用 CSS 變數的層疊特性，將主題定義與元件樣式分離。

*   **Global Definition (`:root`)**: 定義 Primitives。
*   **Theme Definition (`[data-theme]`)**: 重新映射 Semantics。

```css
:root {
  /* Primitives */
  --blue-500: #3b82f6;
  --gray-900: #111827;
  --white: #ffffff;
}

[data-theme="light"] {
  /* Semantics Mapping */
  --bg-default: var(--white);
  --text-primary: var(--gray-900);
}

[data-theme="dark"] {
  /* Semantics Mapping */
  --bg-default: var(--gray-900);
  --text-primary: var(--white);
}
```

### 4. Typography as Composite Tokens (複合排版 Token)
文字通常不只有 `font-size`，還包含 `line-height`, `font-weight` 等。
*   **Pattern**: 使用 CSS class 或 mixin 來應用一組 Token，而非單獨應用變數。
*   **Modern Approach**: 如果使用 Tailwind 或 CSS-in-JS，通常會將其打包成一個 text style object。在純 CSS 中，可以定義 Utility Classes：
    ```css
    .text-heading-xl {
      font-family: var(--font-sans);
      font-weight: var(--font-bold);
      font-size: var(--text-3xl);
      line-height: var(--leading-tight);
    }
    ```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Pass-through" Trap (直通陷阱)
*   **Anti-pattern**: 在開發 Dark Mode 時，發現某個元件顏色沒變，檢查後發現它直接用了 `--gray-900` 這種 Primitive Token。
*   **Consequence**: 你必須去修改所有用到該變數的元件 CSS，這違反了 Design System 的初衷。
*   **Fix**: 強制規定 UI 元件只能存取 Semantic 層級的變數。

### 2. Vague Naming (模糊命名)
*   **Anti-pattern**: 命名如 `--main-color`, `--secondary-color`。
*   **Why it fails**: "Main" 是什麼意思？是背景的主色？還是品牌的主色？還是文字的主色？當設計師決定「背景要變黑，但品牌色按鈕保持藍色」時，`--main-color` 就會產生衝突。
*   **Fix**: 使用具體的語意，如 `--bg-page`, `--text-body`, `--brand-primary`。

### 3. Over-tokenization (過度 Token 化)
*   **Anti-pattern**: 為每一個微小的 pixel 差異都建立一個 Token。例如 `--width-card-profile-image: 42px`。
*   **Consequence**: `variables.css` 變得巨大且難以維護，開發者找不到變數乾脆直接寫死數值。
*   **Fix**: 保持 Token 的通用性（如 Spacing Scale `--space-4`, `--space-8`），只有在極度需要一致性的地方（如 Brand Colors）才嚴格限制。

### 4. Ignoring Fallbacks (忽略回退值)
*   **Anti-pattern**: `color: var(--unknown-token);`
*   **Consequence**: 如果變數未定義，瀏覽器不會報錯，而是使用繼承值或預設值（通常是透明或黑色），導致 UI 壞掉且難以除錯。
*   **Fix**: 在關鍵樣式上考慮 fallback，或者確保 Linter 能檢查變數拼寫。

---

## Checklists & workflows｜檢查清單與流程

### Workflow: From Design to CSS
1.  **Define**: 設計師在 Figma 中定義 Primitives 與 Semantics。
2.  **Export**: 透過插件（如 Tokens Studio）導出 JSON。
3.  **Transform**: 使用工具（如 Style Dictionary）將 JSON 轉換為 CSS Variables。
4.  **Consume**: 工程師在專案中引入生成的 CSS 檔案。

### Developer Implementation Checklist
在實作 UI 元件或頁面時，請依序檢查：

- [ ] **Token Tier Check**: 我是否使用了 Semantic Tokens（如 `--text-primary`）而非 Primitive Tokens（如 `--gray-900`）？
- [ ] **Hardcoding Check**: CSS 中是否出現了非 `0` 或非 `%` 的裸露數值（Magic Numbers）？如果有，是否應該替換為 Spacing Token？
- [ ] **Theming Check**: 如果我手動切換 `data-theme="dark"`，這個元件的可讀性（對比度）是否依然正常？
- [ ] **Context Check**: 如果這個元件被放在一個深色背景的容器中（即使全站是 Light Mode），它能透過 CSS 變數繼承正確顯示嗎？
- [ ] **Unit Consistency**: Spacing 是否統一使用 `rem` 或 `px`（依專案規範），沒有混用的情況？

---

## Real-world examples｜實戰案例

### Example 1: Robust Dark Mode Implementation (穩健的深色模式實作)

這是一個標準的 Design Tokens 實作結構，展示如何透過變數層切換主題。

```css
/* 1. Primitives (Global Scope) - The Palette */
:root {
  /* Brand */
  --brand-blue: #2563eb;
  --brand-blue-dark: #1d4ed8;
  
  /* Neutrals */
  --gray-100: #f3f4f6;
  --gray-800: #1f2937;
  --gray-900: #111827;
  --white: #ffffff;
}

/* 2. Semantics (Theme Scope) - The Contract */
/* Default (Light) */
:root, [data-theme="light"] {
  --bg-page: var(--white);
  --bg-surface: var(--gray-100);
  --text-primary: var(--gray-900);
  --text-inverted: var(--white);
  --action-primary: var(--brand-blue);
}

/* Dark Theme */
[data-theme="dark"] {
  --bg-page: var(--gray-900);
  --bg-surface: var(--gray-800);
  --text-primary: var(--white);
  --text-inverted: var(--gray-900); /* 注意這裡的反轉邏輯 */
  --action-primary: var(--brand-blue-dark); /* 調整為適合深色的藍 */
}

/* 3. Usage (Component Scope) - The Implementation */
.card {
  background-color: var(--bg-surface); /* 自動隨主題變換 */
  color: var(--text-primary);
  padding: var(--space-4);
  border-radius: var(--radius-md);
}

.btn-primary {
  background-color: var(--action-primary);
  color: var(--text-inverted);
}
```

### Example 2: Handling Spacing Scales (處理間距系統)

不要隨意寫 `margin: 13px`。建立一個空間系統能讓 UI 更有韻律感。

```css
:root {
  --base-unit: 0.25rem; /* 4px */
  
  --space-1: calc(var(--base-unit) * 1);  /* 4px */
  --space-2: calc(var(--base-unit) * 2);  /* 8px */
  --space-4: calc(var(--base-unit) * 4);  /* 16px */
  --space-8: calc(var(--base-unit) * 8);  /* 32px */
}

/* 實戰應用：Stack Pattern */
.stack > * + * {
  margin-top: var(--space-4); /* 統一間距 */
}
```

### Example 3: Component-Specific Tokens for Isolation (元件層級變數)

當你需要微調特定元件，但不希望影響全域 Semantic Tokens 時。

```css
.alert-box {
  /* 定義 Component Tokens，預設繼承 Semantic Tokens */
  --alert-bg: var(--bg-surface);
  --alert-text: var(--text-primary);
  
  background: var(--alert-bg);
  color: var(--alert-text);
  border: 1px solid currentColor;
}

/* 特殊變體：覆寫 Component Tokens 即可，不用重寫屬性 */
.alert-box.danger {
  --alert-bg: var(--color-danger-bg);
  --alert-text: var(--color-danger-text);
}
```