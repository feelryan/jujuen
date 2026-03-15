# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，CSS 最令人沮喪的往往不是「寫不出樣式」，而是「無法預測樣式為何生效（或不生效）」。在大型專案或微前端（Micro-frontend）架構中，樣式衝突（Style Conflicts）與權重戰爭（Specificity Wars）是維護性的殺手。本章將超越基礎的選擇器教學，深入瀏覽器的渲染決策機制。

For senior engineers, the most frustrating aspect of CSS is often not "how to write styles," but "predicting why a style applies (or doesn't)." In large-scale projects or Micro-frontend architectures, Style Conflicts and Specificity Wars are killers of maintainability. This chapter moves beyond basic selectors to dive deep into the browser's rendering decision mechanism.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精準計算與控制權重（Master Specificity & Control）**：不再依賴 `!important` 解決衝突，而是理解 `(ID, Class, Type)` 三元組計算邏輯。
    **Master Specificity & Control**: Stop relying on `!important` to resolve conflicts; instead, understand the `(ID, Class, Type)` tuple calculation logic.
2.  **運用 `@layer` 架構 CSS（Architect CSS with `@layer`）**：使用 Cascade Layers 徹底解決第三方套件與專案代碼之間的優先級問題。
    **Architect CSS with `@layer`**: Use Cascade Layers to definitively solve priority issues between third-party packages and project code.
3.  **設計基於 CSS Variables 的動態主題系統（Design Dynamic Theming with CSS Variables）**：利用 Custom Properties 的繼承特性與作用域，實作高效能的 Dark Mode 或多租戶主題（Multi-tenant Theming）。
    **Design Dynamic Theming with CSS Variables**: Leverage the inheritance and scoping of Custom Properties to implement high-performance Dark Mode or Multi-tenant Theming.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 現代層疊演算法 (The Modern Cascade Algorithm)

很多工程師認為 CSS 的優先級只看「權重（Specificity）」，這是一個過時的心智模型。現代瀏覽器的層疊（Cascade）決策順序如下：

Many engineers believe CSS priority is determined solely by "Specificity," which is an outdated mental model. The modern browser Cascade decision order is as follows:

1.  **來源與重要性 (Origin & Importance)**：`Transition` > `!important` (User Agent/User/Author) > `Animation` > Normal Styles.
2.  **上下文 (Context / Layers)**：`@layer` 定義的順序（後者贏）。
    **Context / Layers**: The order defined in `@layer` (last one wins).
3.  **權重 (Specificity)**：Inline styles > ID > Class/Attribute/Pseudo-class > Type/Pseudo-element.
4.  **出現順序 (Order of Appearance)**：原始碼中較晚出現的贏（若上述條件皆相同）。
    **Order of Appearance**: The one that appears later in the source code wins (if all above conditions are equal).

> **Key Insight**: `@layer` 的引入改變了遊戲規則。位於較高優先級 Layer 的樣式，即使權重較低（例如只有一個 tag selector），也會覆蓋較低優先級 Layer 中權重極高（例如 ID selector）的樣式。
>
> **Key Insight**: The introduction of `@layer` changes the game. Styles in a higher-priority Layer, even with lower specificity (e.g., a single tag selector), will override styles in a lower-priority Layer with extremely high specificity (e.g., an ID selector).

## 2.2 CSS 變數的作用域與繼承 (Scope & Inheritance of CSS Variables)

CSS Custom Properties (`--variable-name`) 不僅僅是字串替換（如 Sass 變數），它們是**動態的**且**受 DOM 結構影響的**。

CSS Custom Properties (`--variable-name`) are not just string replacements (like Sass variables); they are **dynamic** and **influenced by the DOM structure**.

-   **Lexical Scoping**：變數在宣告的選擇器及其子元素中有效。
    **Lexical Scoping**: Variables are valid within the declared selector and its children.
-   **Dynamic Evaluation**：當變數值改變（例如透過 JS 或 Media Query），依賴該變數的所有屬性會即時重繪。
    **Dynamic Evaluation**: When a variable's value changes (e.g., via JS or Media Query), all properties relying on that variable repaint instantly.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 Design Systems 與 Design Tokens

在大型系統設計中，我們不再直接寫死 hex color 或 pixel 值。我們定義 **Design Tokens**（設計變數），並透過 CSS Variables 注入到 `:root` 或特定容器中。

In large-scale system design, we no longer hardcode hex colors or pixel values. We define **Design Tokens** and inject them via CSS Variables into `:root` or specific containers.

-   **Global Level**: `:root { --color-primary: #007bff; }` (App-wide theme)
-   **Component Level**: `.card { --card-bg: var(--color-surface); }` (Local abstraction)

這允許我們在不增加 bundle size 的情況下，支援多品牌（White-labeling）或深色模式。

This allows us to support White-labeling or Dark Mode without increasing bundle size.

## 3.2 第三方整合與微前端 (Third-party Integration & Micro-frontends)

當你的應用程式需要嵌入第三方 Widget，或者你的團隊負責開發被嵌入的 Widget 時，樣式污染是常見風險。

When your application needs to embed a third-party Widget, or your team develops a Widget to be embedded, style contamination is a common risk.

-   **Legacy Approach**: 使用 BEM 命名法 (`.my-widget__button`) 或 CSS-in-JS 生成 hash class 避免衝突。
    **Legacy Approach**: Use BEM naming (`.my-widget__button`) or CSS-in-JS generated hash classes to avoid conflicts.
-   **Modern Approach**: 將整個 Widget 的 CSS 包在一個 `@layer widget` 中，並確保宿主環境（Host App）的樣式在更高優先級的 Layer。
    **Modern Approach**: Wrap the entire Widget's CSS in a `@layer widget` and ensure the Host App's styles are in a higher-priority Layer.

---

# 4. 逐步示例 (Walkthrough / Example)

## 情境：解決遺留代碼與新 UI 的衝突 (Scenario: Resolving Conflicts between Legacy Code and New UI)

假設你有一個遺留的全域樣式表 `legacy.css`，裡面充滿了高權重的選擇器。現在你需要引入一個新的 Design System，但不想使用 `!important` 到處覆蓋。

Suppose you have a legacy global stylesheet `legacy.css` full of high-specificity selectors. You now need to introduce a new Design System but don't want to use `!important` everywhere to override.

### 步驟 1：問題分析 (Step 1: Problem Analysis)

```css
/* legacy.css */
#content .sidebar button.active {
  background-color: red; /* Specificity: (1, 2, 1) - Very High! */
  color: white;
}

/* new-design-system.css */
.btn-primary {
  background-color: blue; /* Specificity: (0, 1, 0) - Too Low */
  color: white;
}
```

在傳統做法中，你必須將 `.btn-primary` 的權重人為提高（例如加上 `#content` 前綴），這導致了惡性循環。

In the traditional approach, you would have to artificially increase the specificity of `.btn-primary` (e.g., adding the `#content` prefix), leading to a vicious cycle.

### 步驟 2：引入 `@layer` (Step 2: Introducing `@layer`)

我們可以定義層級順序，明確告訴瀏覽器：無論權重如何，「新系統」優先於「舊系統」。

We can define the layer order, explicitly telling the browser: regardless of specificity, the "New System" takes precedence over the "Legacy System".

```css
/* main.css - Entry Point */

/* Define the order of precedence: first is lowest, last is highest */
@layer legacy, new-system;

/* Import legacy styles into the 'legacy' layer */
@import url('legacy.css') layer(legacy);

/* Import new styles into the 'new-system' layer */
@import url('new-design-system.css') layer(new-system);
```

### 步驟 3：實作與驗證 (Step 3: Implementation & Verification)

現在，即使 `legacy.css` 中的選擇器權重是 `(1, 2, 1)`，而 `new-design-system.css` 中的選擇器權重僅是 `(0, 1, 0)`，瀏覽器也會優先採用 `new-system` layer 的樣式。

Now, even if the selector specificity in `legacy.css` is `(1, 2, 1)` and the selector in `new-design-system.css` is only `(0, 1, 0)`, the browser will prioritize the style from the `new-system` layer.

### 步驟 4：結合 CSS Variables 進行主題切換 (Step 4: Combining with CSS Variables for Theming)

```css
@layer new-system {
  :root {
    --btn-bg: #007bff;
    --btn-text: #ffffff;
  }

  [data-theme="dark"] {
    --btn-bg: #375a7f;
    --btn-text: #e0e0e0;
  }

  .btn-primary {
    /* Decoupled from specific values */
    background-color: var(--btn-bg);
    color: var(--btn-text);
    padding: 0.5rem 1rem;
  }
}
```

**Why this works**:
1.  **Isolation**: `legacy` 層無法干擾 `new-system` 層（除非使用 `!important`，這會穿透 Layer，但這是另一回事）。
    **Isolation**: The `legacy` layer cannot interfere with the `new-system` layer (unless `!important` is used, which pierces Layers, but that's a separate issue).
2.  **Maintainability**: 新代碼不需要知道舊代碼的權重結構。
    **Maintainability**: New code doesn't need to know the specificity structure of the old code.
3.  **Flexibility**: 變數允許在 Runtime 切換主題，無需重新加載 CSS。
    **Flexibility**: Variables allow runtime theme switching without reloading CSS.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 濫用 `!important` 進行架構控制 (Misusing `!important` for Architectural Control)

-   **Anti-pattern**: 在 Utility Class（如 Tailwind 風格的自製類別）中全面加上 `!important` 以確保它們總是生效。
    **Anti-pattern**: Adding `!important` globally to Utility Classes (like custom Tailwind-style classes) to ensure they always apply.
-   **Why it's bad**: 這破壞了 Cascade 的自然流動，使得無法在特定狀態（如 `:hover` 或 Media Query）下覆蓋這些樣式。
    **Why it's bad**: This breaks the natural flow of the Cascade, making it impossible to override these styles in specific states (like `:hover` or Media Queries).
-   **Better Approach**: 使用 `@layer utilities { ... }` 並將該 Layer 置於最高優先級。
    **Better Approach**: Use `@layer utilities { ... }` and place that Layer at the highest priority.

## 5.2 在 `:root` 定義所有變數 (Defining All Variables in `:root`)

-   **Anti-pattern**: 將所有組件的局部變數都定義在全域 `:root` 中。
    **Anti-pattern**: Defining all local component variables in the global `:root`.
-   **Why it's bad**: 污染全域命名空間，且增加了瀏覽器計算樣式的負擔（因為 `:root` 變數變更會觸發全頁重繪檢查）。
    **Why it's bad**: Pollutes the global namespace and increases the browser's style calculation burden (since changing `:root` variables triggers a full-page repaint check).
-   **Better Approach**: 僅將真正的全域 Tokens（顏色、間距）放在 `:root`，組件特定的變數應定義在組件 Scope 內。
    **Better Approach**: Only put true global Tokens (colors, spacing) in `:root`; component-specific variables should be defined within the component's scope.

## 5.3 忽略 Layer 的順序依賴 (Ignoring Layer Order Dependency)

-   **Pitfall**: 在多個文件中分散定義 `@layer` 名稱，導致載入順序不確定。
    **Pitfall**: Defining `@layer` names scattered across multiple files, leading to indeterminate loading order.
-   **Solution**: 在入口 CSS 檔案的最頂端，統一宣告 Layer 的順序（例如 `@layer reset, base, components, utilities;`）。
    **Solution**: Explicitly declare the Layer order at the very top of the entry CSS file (e.g., `@layer reset, base, components, utilities;`).

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 請解釋 CSS Specificity 的計算方式，以及 `@layer` 如何影響這個計算？
**Explain how CSS Specificity is calculated, and how `@layer` affects this calculation.**

-   **Key Points**:
    -   解釋 (ID, Class, Element) 三元組模型（例如 `0-1-0`）。
    -   提及 Inline styles 的特殊地位。
    -   **關鍵點**：指出 `@layer` 的優先級高於 Specificity。如果 Layer A > Layer B，則 Layer A 中的 `div` (0-0-1) 會贏過 Layer B 中的 `#id` (1-0-0)。
    -   **Key Points**: Explain the (ID, Class, Element) tuple model. Mention the special status of Inline styles. **Crucial**: Point out that `@layer` precedence is higher than Specificity. If Layer A > Layer B, a `div` (0-0-1) in Layer A beats an `#id` (1-0-0) in Layer B.

## Q2: 如何在不使用 JavaScript 的情況下，實作高效能的 Dark Mode？
**How would you implement high-performance Dark Mode without using JavaScript?**

-   **Key Points**:
    -   使用 CSS Custom Properties 定義語意化顏色（如 `--bg-primary` 而非 `--white`）。
    -   利用 `prefers-color-scheme` media query 自動適應系統設定。
    -   利用 CSS 變數的繼承特性，只需改變根節點的變數值，無需切換 CSS 檔案（避免 FOUC - Flash of Unstyled Content）。
    -   **Key Points**: Use CSS Custom Properties to define semantic colors (e.g., `--bg-primary` instead of `--white`). Leverage the `prefers-color-scheme` media query. Use variable inheritance to update values at the root, avoiding CSS file swaps (preventing FOUC).

## Q3: 在大型專案中，你會如何架構 CSS 以避免樣式衝突？
**In a large-scale project, how would you architect CSS to avoid style conflicts?**

-   **Key Points**:
    -   使用 **ITCSS (Inverted Triangle CSS)** 概念或類似的分層結構。
    -   現代做法：明確定義 `@layer` (Reset, Framework, Components, Utilities)。
    -   使用命名約定（如 BEM）或是 CSS Modules / Scoped CSS 來隔離組件樣式。
    -   **Key Points**: Use **ITCSS** concepts or similar layering structures. Modern approach: Explicitly define `@layer`. Use naming conventions (like BEM) or CSS Modules / Scoped CSS to isolate component styles.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)

1.  **Cascade Order**: Importance > Origin > **Layer** > Specificity > Order. 牢記 Layer 在 Specificity 之前。
    **Cascade Order**: Importance > Origin > **Layer** > Specificity > Order. Remember that Layer comes before Specificity.
2.  **Specificity Tuple**: `(ID, Class, Tag)`。Inline style 權重極高，但輸給 `!important`。
    **Specificity Tuple**: `(ID, Class, Tag)`. Inline styles are very high weight but lose to `!important`.
3.  **CSS Variables**: 是執行時期的動態屬性，遵循 DOM 繼承結構，是現代主題系統的基石。
    **CSS Variables**: Runtime dynamic properties that follow the DOM inheritance structure; the cornerstone of modern theming systems.
4.  **@layer**: 是管理大型專案樣式優先級的最佳工具，能有效隔離第三方樣式與遺留代碼。
    **@layer**: The best tool for managing style priority in large projects, effectively isolating third-party styles and legacy code.

## 後續延伸 (Next Steps)

-   **下一章 (Next Chapter)**: 深入 **Layout Systems (Flexbox & Grid)**。既然掌握了樣式如何「生效」，接下來要掌握樣式如何「排版」。
    **Next Chapter**: Dive into **Layout Systems (Flexbox & Grid)**. Now that you control how styles "apply," next is controlling how they "layout."
-   **延伸閱讀 (Further Reading)**: 研究 `CSS Container Queries` (`@container`)，這結合了 Scope 概念，允許組件根據「容器大小」而非「視窗大小」進行響應，是 Component-Driven Design 的下一步。
    **Further Reading**: Research `CSS Container Queries` (`@container`). This combines Scope concepts, allowing components to respond based on "container size" rather than "viewport size," the next step in Component-Driven Design.