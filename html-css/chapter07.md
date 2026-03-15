# 1. 前言與學習目標 (Introduction and Learning Objectives)

在資深工程師的層級，CSS 不再只是關於如何置中一個 `div`，而是關於如何建立一套可擴展、可維護的視覺語言架構。本章將探討如何從工程角度構建 Design System，特別是透過 Design Tokens 來解耦設計決策與程式碼實作。

At the senior engineer level, CSS is no longer just about centering a `div`; it is about architecting a scalable and maintainable visual language. This chapter explores how to build a Design System from an engineering perspective, specifically focusing on Design Tokens to decouple design decisions from code implementation.

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **設計多層級 Token 架構**：區分 Primitive Tokens（原始）、Semantic Tokens（語意）與 Component Tokens（元件），並解釋其對維護性的影響。
    **Design a multi-tiered Token Architecture**: Distinguish between Primitive, Semantic, and Component tokens, and explain their impact on maintainability.
2.  **實作自動化主題切換 (Theming)**：利用 CSS Custom Properties (Variables) 實作高效的 Dark Mode 或多品牌主題，無需依賴繁重的 JavaScript 邏輯。
    **Implement automated Theming**: Use CSS Custom Properties (Variables) to implement efficient Dark Mode or multi-brand themes without relying on heavy JavaScript logic.
3.  **建立跨平台樣式來源 (Source of Truth)**：理解如何透過 JSON 或 YAML 定義樣式，並透過工具（如 Style Dictionary）分發至 Web, iOS, 與 Android。
    **Establish a cross-platform Source of Truth**: Understand how to define styles via JSON or YAML and distribute them to Web, iOS, and Android using tools like Style Dictionary.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 Design Tokens：設計的 API (The API of Design)

**直覺類比**：
想像你正在寫一個大型後端系統。你不會在每一行程式碼中硬寫資料庫連線字串（Hardcoding），而是會將其放入環境變數或設定檔中。Design Tokens 就是 UI 的「環境變數」。

**Intuitive Analogy**:
Imagine you are writing a large backend system. You wouldn't hardcode the database connection string in every line of code; instead, you would place it in environment variables or a configuration file. Design Tokens are the "environment variables" of the UI.

**正規定義**：
Design Tokens 是儲存視覺設計原子（如顏色、字體大小、間距、動畫時間）的與平台無關的變數。它們充當設計工具（如 Figma）與開發實作之間的協議層。

**Formal Definition**:
Design Tokens are platform-agnostic variables that store visual design atoms (such as colors, font sizes, spacing, animation timing). They act as a contract layer between design tools (like Figma) and development implementation.

## 2.2 Token 的三層架構 (The Three-Tier Token Architecture)

為了確保擴充性，資深工程師通常採用三層架構，而非扁平結構：

To ensure scalability, senior engineers typically adopt a three-tier architecture rather than a flat structure:

1.  **Primitive Tokens (Global / Base)**:
    *   代表原始值。例如：`blue-500: #1fb6ff`。
    *   **用途**：定義調色盤，不帶有任何使用情境的意涵。
    *   **Represents raw values**. E.g., `blue-500: #1fb6ff`.
    *   **Usage**: Defines the palette without any contextual meaning.

2.  **Semantic Tokens (Alias / Abstract)**:
    *   代表用途。例如：`color-primary-action: {blue-500}`。
    *   **用途**：這是最重要的一層。當你需要將品牌色從藍色改為紅色時，只需修改這裡的映射，而無需修改 Primitive。
    *   **Represents intent**. E.g., `color-primary-action: {blue-500}`.
    *   **Usage**: This is the most critical layer. When you need to change the brand color from blue to red, you only update the mapping here, not the Primitive.

3.  **Component Tokens (Specific)**:
    *   代表特定元件的屬性。例如：`button-bg-color: {color-primary-action}`。
    *   **用途**：針對特定元件的微調，通常繼承自 Semantic Tokens。
    *   **Represents specific component properties**. E.g., `button-bg-color: {color-primary-action}`.
    *   **Usage**: For specific component tweaks, usually inheriting from Semantic Tokens.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 DesignOps 與 CI/CD 整合 (DesignOps and CI/CD Integration)

在大型組織中，Design System 是一個獨立的產品。我們通常會建立一個 pipeline 來自動化樣式的發布：

In large organizations, the Design System is a standalone product. We usually build a pipeline to automate style distribution:

1.  **Design Source**: 設計師在 Figma 中更新 Tokens。
    **Design Source**: Designers update Tokens in Figma.
2.  **Extraction**: 透過 Figma API 或 Plugin 將 Tokens 匯出為 JSON 檔案。
    **Extraction**: Tokens are exported as JSON files via Figma API or Plugins.
3.  **Transformation (Style Dictionary)**: CI/CD 流程執行轉換腳本，將 JSON 轉譯為：
    *   Web: CSS Custom Properties (`:root { --color: ... }`) 或 SCSS 變數。
    *   iOS: Swift Structs / Color Assets。
    *   Android: XML Resources / Jetpack Compose Objects。
    **Transformation (Style Dictionary)**: The CI/CD process runs transformation scripts to translate JSON into:
    *   Web: CSS Custom Properties (`:root { --color: ... }`) or SCSS variables.
    *   iOS: Swift Structs / Color Assets.
    *   Android: XML Resources / Jetpack Compose Objects.
4.  **Consumption**: 各個前端專案透過 npm package 引入這些生成的檔案。
    **Consumption**: Frontend projects import these generated files via npm packages.

## 3.2 對可維護性的影響 (Impact on Maintainability)

如果不使用這套系統，當公司決定進行 Rebranding（更換品牌色）時，工程師需要全域搜尋取代 hex codes，這極易出錯且耗時。使用 Semantic Tokens 後，這變成了一個 Config Change，可以在幾分鐘內完成並部署。

Without this system, when a company decides to Rebrand (change brand colors), engineers have to global search-and-replace hex codes, which is error-prone and time-consuming. With Semantic Tokens, this becomes a Config Change that can be completed and deployed in minutes.

---

# 4. 逐步示例：實作支援 Dark Mode 的 Token 系統 (Walkthrough: Implementing a Dark Mode Ready Token System)

我們將演示如何從 JSON 定義到 CSS 實作，並處理 Dark Mode。

We will demonstrate how to go from JSON definition to CSS implementation, handling Dark Mode.

### Step 1: 定義 Token JSON (Defining the Token JSON)

這是我們的 Source of Truth。注意我們如何區分 `primitive` 和 `semantic`。

This is our Source of Truth. Notice how we distinguish between `primitive` and `semantic`.

```json
// tokens.json
{
  "color": {
    "primitive": {
      "blue": { "500": { "value": "#3b82f6" } },
      "gray": {
        "100": { "value": "#f3f4f6" },
        "900": { "value": "#111827" }
      }
    },
    "semantic": {
      "bg": {
        "default": {
          "light": "{color.primitive.gray.100}",
          "dark": "{color.primitive.gray.900}"
        }
      },
      "text": {
        "primary": {
          "light": "{color.primitive.gray.900}",
          "dark": "{color.primitive.gray.100}"
        }
      },
      "action": {
        "primary": { "value": "{color.primitive.blue.500}" }
      }
    }
  }
}
```

### Step 2: 轉換為 CSS Custom Properties (Transforming to CSS Custom Properties)

在建置階段（Build time），我們將上述 JSON 轉換為 CSS。關鍵在於將 `light` 和 `dark` 分開處理。

During build time, we transform the JSON above into CSS. The key is to handle `light` and `dark` separately.

```css
/* generated-tokens.css */

/* 1. Primitives (Global scope) */
:root {
  --color-primitive-blue-500: #3b82f6;
  --color-primitive-gray-100: #f3f4f6;
  --color-primitive-gray-900: #111827;
}

/* 2. Semantic - Default Theme (Light) */
:root, [data-theme="light"] {
  --color-bg-default: var(--color-primitive-gray-100);
  --color-text-primary: var(--color-primitive-gray-900);
  --color-action-primary: var(--color-primitive-blue-500);
}

/* 3. Semantic - Dark Theme Override */
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg-default: var(--color-primitive-gray-900);
    --color-text-primary: var(--color-primitive-gray-100);
  }
}

[data-theme="dark"] {
  --color-bg-default: var(--color-primitive-gray-900);
  --color-text-primary: var(--color-primitive-gray-100);
}
```

### Step 3: 在元件中使用 (Usage in Components)

工程師在開發時，**永遠只使用 Semantic Tokens**，不直接使用 Primitives 或 Hex codes。

Engineers should **always use Semantic Tokens** during development, never Primitives or Hex codes directly.

```css
/* button.css */
.btn-primary {
  /* GOOD: Uses semantic meaning */
  background-color: var(--color-action-primary);
  color: var(--color-text-primary);
  
  /* BAD: Uses specific color value (Hard to rebrand) */
  /* background-color: var(--color-primitive-blue-500); */
  
  /* WORST: Hardcoded value */
  /* background-color: #3b82f6; */
}

.card {
  /* Automatically switches in dark mode because --color-bg-default changes value */
  background-color: var(--color-bg-default); 
  color: var(--color-text-primary);
}
```

### 為何這個做法可行？ (Why this works?)

1.  **O(1) 複雜度的主題切換**：瀏覽器原生處理 CSS 變數的替換，不需要 JavaScript 遍歷 DOM 來更改 class，效能極佳。
    **O(1) Complexity Theme Switching**: The browser natively handles CSS variable substitution. No JavaScript is needed to traverse the DOM to change classes, resulting in excellent performance.
2.  **關注點分離**：元件開發者只關心「這是背景色」，而不關心「現在是深色還是淺色」。
    **Separation of Concerns**: Component developers only care that "this is a background color," not "whether it is currently dark or light mode."

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 跳過語意層 (Skipping the Semantic Layer)

**錯誤描述**：直接在元件中使用 Primitive Tokens，例如 `color: var(--blue-500)`。
**為何不好**：這導致了「隱性耦合」。如果你想把主要按鈕改成紫色，你必須搜尋所有用到 `--blue-500` 的地方，但有些 `--blue-500` 可能是用於連結或邊框，不應該被改變。
**修正**：始終定義如 `--color-action-primary` 的語意變數。

**Description**: Using Primitive Tokens directly in components, e.g., `color: var(--blue-500)`.
**Why it's bad**: This creates "implicit coupling." If you want to change the primary button to purple, you have to search for all usages of `--blue-500`, but some `--blue-500` might be used for links or borders and shouldn't be changed.
**Fix**: Always define semantic variables like `--color-action-primary`.

## 5.2 Token 命名過於特定或過於籠統 (Naming Tokens Too Specifically or Too Broadly)

**錯誤描述**：
*   過於特定：`--color-sidebar-bottom-border` (導致 Token 爆炸，難以重用)。
*   過於籠統：`--color-blue` (這只是 Primitive 的別名，沒有語意)。

**Description**:
*   Too specific: `--color-sidebar-bottom-border` (Leads to token explosion, hard to reuse).
*   Too broad: `--color-blue` (Just an alias for Primitive, no semantics).

**較佳方案**：
使用 CTI (Category-Type-Item) 結構，例如 `color-border-subtle` 或 `spacing-padding-m`。這提供了足夠的語意但保持了一定的通用性。

**Better Approach**:
Use the CTI (Category-Type-Item) structure, e.g., `color-border-subtle` or `spacing-padding-m`. This provides enough semantics while maintaining reusability.

## 5.3 忽略字體排印的複雜性 (Ignoring Typography Complexity)

**錯誤描述**：只定義 `font-size` tokens。
**為何不好**：字體通常需要成套定義（Size, Line-height, Weight, Letter-spacing）。單獨混合使用容易導致視覺不協調。
**修正**：使用 CSS `mixin` (Sass) 或定義複合 class (Utility classes) 來封裝一組 Typography Token，例如 `.text-heading-xl`。

**Description**: Only defining `font-size` tokens.
**Why it's bad**: Typography usually needs to be defined as a set (Size, Line-height, Weight, Letter-spacing). Mixing them individually often leads to visual inconsistency.
**Fix**: Use CSS `mixin` (Sass) or define composite classes (Utility classes) to encapsulate a set of Typography Tokens, e.g., `.text-heading-xl`.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何在不造成 Breaking Change 的情況下重構 Design System 的色票？
**How would you refactor the color palette of a Design System without causing a Breaking Change?**

*   **高分回答要點**：
    *   強調 **Semantic Layer** 的重要性：如果現有程式碼都依賴 Semantic Tokens，我們只需更改 Token 對應的 Primitive Value。
    *   **Deprecation Strategy**：如果必須更改 Token 名稱，應保留舊名稱作為新名稱的 alias，並在 build time 發出警告，設定一個 sunset period（日落期）。
    *   **Visual Regression Testing**：提及使用工具（如 Percy, Chromatic）在 CI 階段自動比對重構前後的截圖。

*   **Key Points**:
    *   Emphasize the **Semantic Layer**: If existing code relies on Semantic Tokens, we only need to update the Primitive Value mapping.
    *   **Deprecation Strategy**: If token names must change, keep the old name as an alias to the new one, emit warnings at build time, and set a sunset period.
    *   **Visual Regression Testing**: Mention using tools (like Percy, Chromatic) to automatically compare screenshots before and after refactoring in CI.

## Q2: 你會如何設計支援 White-labeling (多租戶換膚) 的架構？
**How would you design an architecture to support White-labeling (Multi-tenant theming)?**

*   **高分回答要點**：
    *   **CSS Variables scope**：解釋如何透過在 `<body>` 或特定容器上切換 `data-theme="tenant-a"` 來重新定義 CSS 變數的值。
    *   **動態載入**：對於差異極大的主題，可以考慮動態 fetch 對應租戶的 CSS 檔案（CSS chunk），而非將所有租戶樣式打包在同一個檔案中（減少 bundle size）。
    *   **Fallback 機制**：如果租戶未定義某個變數，系統應回退到預設主題的值。

*   **Key Points**:
    *   **CSS Variables scope**: Explain how to redefine CSS variable values by toggling `data-theme="tenant-a"` on the `<body>` or a specific container.
    *   **Dynamic Loading**: For vastly different themes, consider dynamically fetching the tenant's CSS file (CSS chunk) instead of bundling all tenant styles together (reducing bundle size).
    *   **Fallback Mechanism**: If a tenant hasn't defined a variable, the system should fall back to the default theme values.

## Q3: CSS-in-JS (如 Styled Components) 與 CSS Variables 在 Design Tokens 實作上有何優劣？
**What are the pros and cons of CSS-in-JS (e.g., Styled Components) vs. CSS Variables for implementing Design Tokens?**

*   **高分回答要點**：
    *   **CSS Variables**：
        *   優點：Runtime 效能極佳（瀏覽器原生），易於除錯（DevTools 可見），跨框架通用。
        *   缺點：型別檢查（Type Safety）較弱（除非搭配 TS 工具）。
    *   **CSS-in-JS (Interpolation)**：
        *   優點：強型別支援，Dead Code Elimination。
        *   缺點：Runtime overhead（需要 JS 計算樣式並注入），SSR 設定較繁瑣。
    *   **結論**：現代趨勢是「混合使用」——使用 CSS Variables 儲存 Tokens（為了動態主題與效能），使用 CSS-in-JS 或 Utility Classes 管理元件結構。

*   **Key Points**:
    *   **CSS Variables**:
        *   Pros: Excellent runtime performance (browser native), easy debugging (visible in DevTools), framework agnostic.
        *   Cons: Weaker Type Safety (unless paired with TS tools).
    *   **CSS-in-JS (Interpolation)**:
        *   Pros: Strong typing support, Dead Code Elimination.
        *   Cons: Runtime overhead (JS needs to calculate and inject styles), complex SSR setup.
    *   **Conclusion**: The modern trend is "Hybrid" — use CSS Variables for Tokens (for dynamic theming and performance), and use CSS-in-JS or Utility Classes for component structure.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)
1.  **Token 三層架構**：Primitive (Raw) -> Semantic (Context) -> Component (Specific)。嚴格遵守此依賴鏈。
2.  **CSS Custom Properties** 是實作動態主題（Theming）與 Design Tokens 的最佳原生機制。
3.  **Source of Truth**：將設計決策從 CSS 檔案移至與平台無關的 JSON/YAML 檔案中，透過 Build Script 分發。
4.  **避免 Magic Values**：在 Production code 中不應出現 Hex code 或 pixel values，全部應由 Tokens 取代。
5.  **DesignOps**：建立自動化流程，讓設計師的 Figma 變更可以同步到程式碼庫。

## 後續延伸 (Next Steps)
*   **進階實作**：研究 **Style Dictionary** 的自定義 transform 與 format，實作自動生成 TypeScript definitions (`.d.ts`) 以獲得 CSS 變數的自動補全 (Autocomplete)。
*   **下一章預告**：探討 **CSS Architecture & Layout Patterns** (BEM, Utility-first, CUBE CSS)，學習如何組織那些使用 Tokens 的 CSS 規則。

*   **Advanced Implementation**: Research **Style Dictionary** custom transforms and formats to automatically generate TypeScript definitions (`.d.ts`) for CSS variable autocomplete.
*   **Next Chapter**: Explore **CSS Architecture & Layout Patterns** (BEM, Utility-first, CUBE CSS) to learn how to organize the CSS rules that consume these Tokens.