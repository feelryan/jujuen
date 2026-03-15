# Chapter 02: Semantic HTML and Accessibility (A11y)
# 第 02 章：語意化 HTML 與無障礙設計 (A11y)

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

For a Senior Software Engineer, HTML is not merely about rendering pixels; it is about structuring data for machines (search engines, screen readers) and ensuring compliance with legal standards (WCAG, ADA). Accessibility (A11y) is often the differentiator between a "working prototype" and a "production-grade enterprise product."
對於資深軟體工程師而言，HTML 不僅僅是為了渲染像素，更是為了讓機器（搜尋引擎、螢幕閱讀器）能結構化地理解資料，並確保產品符合法律標準（如 WCAG、ADA）。無障礙設計（A11y）往往是區分「可運作的原型」與「企業級正式產品」的關鍵分水嶺。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Explain the Accessibility Tree**: Understand how the browser maps the DOM to the Accessibility Tree and how Assistive Technologies (AT) consume it.
    **解釋無障礙樹 (Accessibility Tree)**：理解瀏覽器如何將 DOM 映射為無障礙樹，以及輔助科技 (AT) 如何使用它。
2.  **Master ARIA vs. Native Semantics**: Know precisely when to use ARIA attributes and, more importantly, when *not* to use them (The First Rule of ARIA).
    **掌握 ARIA 與原生語意**：精確知道何時該使用 ARIA 屬性，更重要的是知道何時「不該」使用它們（ARIA 第一條規則）。
3.  **Implement Complex Focus Management**: Handle keyboard navigation in Single Page Applications (SPAs), specifically for Modals, Drawers, and Route changes.
    **實作複雜的焦點管理**：處理單頁應用程式 (SPA) 中的鍵盤導航，特別是針對模態視窗 (Modals)、抽屜 (Drawers) 與路由切換場景。
4.  **Audit for Enterprise Compliance**: Identify common accessibility anti-patterns that pose legal or SEO risks.
    **進行企業級合規審查**：識別可能導致法律風險或 SEO 負面影響的常見無障礙反模式。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 The Accessibility Tree vs. The DOM
### 2.1 無障礙樹 (Accessibility Tree) vs. DOM

**Mental Model**: Think of the **DOM** as the visual blueprint for the rendering engine, while the **Accessibility Tree** is the API for Assistive Technologies (like NVDA, VoiceOver, JAWS).
**心智模型**：將 **DOM** 視為渲染引擎的視覺藍圖，而 **無障礙樹** 則是輔助科技（如 NVDA, VoiceOver, JAWS）的 API 介面。

When a browser parses HTML, it constructs the DOM. Parallel to this, it generates the Accessibility Tree based on the DOM's semantic meaning. Screen readers do not read the screen pixels; they query the Accessibility Tree.
當瀏覽器解析 HTML 時，它會建構 DOM。與此同時，它會根據 DOM 的語意生成無障礙樹。螢幕閱讀器並不是讀取螢幕上的像素，而是查詢這棵無障礙樹。

*   **DOM Node**: `<button>Submit</button>`
*   **A11y Object**: `{ Role: "button", Name: "Submit", State: "focusable" }`

**Key Insight**: If you use a `<div>` styled as a button, it appears in the DOM but may lack the correct `Role` and `State` in the Accessibility Tree, rendering it invisible or confusing to non-visual users.
**關鍵洞察**：如果你使用一個樣式化為按鈕的 `<div>`，它雖然存在於 DOM 中，但在無障礙樹中可能缺乏正確的 `Role`（角色）與 `State`（狀態），導致非視覺使用者無法感知或感到困惑。

### 2.2 Semantics as the "Happy Path"
### 2.2 語意化是「快樂路徑」

Native HTML elements (`<button>`, `<input>`, `<nav>`, `<main>`) come with built-in accessibility features:
原生 HTML 元素（`<button>`, `<input>`, `<nav>`, `<main>`）自帶內建的無障礙功能：

1.  **Role**: Defines what the element is.
    **角色 (Role)**：定義該元素是什麼。
2.  **Name**: Calculated from content or labels.
    **名稱 (Name)**：從內容或標籤計算而來。
3.  **Keyboard Support**: Focus handling and key press listeners (Enter/Space).
    **鍵盤支援**：焦點處理與按鍵監聽（Enter/Space）。

**Analogy**: Using a `<div>` for a button is like implementing a Linked List in JavaScript when you really just needed a native Array. You *can* do it, but you have to manually reimplement all the built-in methods (push, pop, length) and you'll likely introduce bugs.
**類比**：用 `<div>` 來做按鈕，就像是你明明只需要原生的 Array，卻在 JavaScript 中手刻一個 Linked List。你*確實*可以這麼做，但你必須手動重新實作所有內建方法（push, pop, length），而且很可能會引入 Bug。

### 2.3 ARIA (Accessible Rich Internet Applications)
### 2.3 ARIA (可存取富網際網路應用程式)

ARIA attributes (`aria-label`, `role="dialog"`, `aria-expanded`) are meant to bridge the gap when native HTML falls short.
ARIA 屬性（`aria-label`, `role="dialog"`, `aria-expanded`）是用來填補原生 HTML 功能不足時的缺口。

*   **Rule #1 of ARIA**: Don't use ARIA if a native HTML element serves the purpose.
    **ARIA 第一條規則**：如果原生 HTML 元素能達到目的，就不要使用 ARIA。
*   **Rule #2**: Do not change native semantics unless you really have to. (e.g., don't give a `<h3>` a `role="button"`).
    **第二條規則**：除非必要，否則不要改變原生語意。（例如：不要給 `<h3>` 加上 `role="button"`）。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### 3.1 Component Library Architecture
### 3.1 元件庫架構設計

In a large-scale system, individual product engineers should rarely need to worry about low-level ARIA attributes. Instead, A11y should be abstracted into the **Design System / Component Library**.
在大型系統中，個別產品工程師應該很少需要擔心底層的 ARIA 屬性。相反地，A11y 應該被抽象化封裝在 **設計系統 / 元件庫** 中。

*   **Base Components**: The `<Button>`, `<Modal>`, and `<Dropdown>` components in your internal library must handle `aria-expanded`, focus trapping, and keyboard events internally.
    **基礎元件**：你內部函式庫中的 `<Button>`, `<Modal>`, 和 `<Dropdown>` 元件必須在內部處理好 `aria-expanded`、焦點鎖定 (focus trapping) 和鍵盤事件。
*   **Enforcement**: Use linting tools (e.g., `eslint-plugin-jsx-a11y`) in the CI/CD pipeline to block PRs that violate basic A11y rules.
    **強制執行**：在 CI/CD 流程中使用 Lint 工具（如 `eslint-plugin-jsx-a11y`）來阻擋違反基本 A11y 規則的 PR。

### 3.2 SPA Routing & Focus Management
### 3.2 SPA 路由與焦點管理

In a traditional Multi-Page Application (MPA), a page reload resets focus to the top of the `<body>`. In Single Page Applications (React/Vue/Angular), changing the route technically just replaces a DOM fragment.
在傳統的多頁應用程式 (MPA) 中，頁面重新載入會將焦點重置到 `<body>` 頂部。但在單頁應用程式 (SPA) 中，切換路由技術上只是替換了 DOM 片段。

**The Problem**: If a user clicks a link and the content swaps, their focus might be lost (dropped to `body`) or remain on a non-existent element, forcing screen reader users to navigate from the start again.
**問題**：如果使用者點擊連結後內容被替換，他們的焦點可能會遺失（掉回 `body`）或停留在不存在的元素上，迫使螢幕閱讀器使用者必須重新從頭導航。

**The Solution**: The Router or Layout component must programmatically move focus to the new page's main heading (`<h1>`) or a wrapper with `tabindex="-1"` upon navigation.
**解法**：路由器 (Router) 或佈局元件 (Layout) 必須在導航發生時，以程式化方式將焦點移動到新頁面的主標題 (`<h1>`) 或帶有 `tabindex="-1"` 的容器上。

### 3.3 SEO & Machine Readability
### 3.3 SEO 與機器可讀性

Google's crawler (Googlebot) parses the DOM similarly to a screen reader to understand content hierarchy.
Google 的爬蟲 (Googlebot) 解析 DOM 的方式與螢幕閱讀器類似，藉此理解內容層級。

*   **Landmarks**: Using `<header>`, `<main>`, `<aside>`, `<footer>` helps bots distinguish primary content from boilerplate navigation.
    **地標 (Landmarks)**：使用 `<header>`, `<main>`, `<aside>`, `<footer>` 有助於機器人區分主要內容與樣板導航。
*   **Heading Structure**: A logical `h1` -> `h2` -> `h3` hierarchy is crucial for both SEO rankings and screen reader navigation ("skip to next heading").
    **標題結構**：邏輯清晰的 `h1` -> `h2` -> `h3` 層級對於 SEO 排名與螢幕閱讀器導航（「跳至下一個標題」功能）至關重要。

---

## 4. Walkthrough / Example
## 4. 逐步示例

### Scenario: Building an Accessible Custom Toggle
### 場景：建構一個無障礙的客製化切換開關 (Toggle)

**Requirement**: Design a custom "Switch" component that looks like a toggle slider but behaves like a checkbox.
**需求**：設計一個客製化的「開關 (Switch)」元件，外觀像滑動開關，但行為像核取方塊 (Checkbox)。

#### 4.1 Naive Approach (The Anti-Pattern)
#### 4.1 幼稚做法（反模式）

```html
<!-- BAD: Semantic nightmare -->
<div class="toggle-switch" onclick="toggleState()">
  <div class="knob"></div>
  <span class="label">Enable Notifications</span>
</div>
```

**Why it fails**:
**為何失敗**：
1.  **Not Focusable**: Keyboard users cannot Tab to it.
    **無法聚焦**：鍵盤使用者無法 Tab 到這個元素。
2.  **No Role**: Screen readers see "group" or just text, not a "checkbox" or "switch".
    **無角色**：螢幕閱讀器只會看到「群組」或純文字，而不是「核取方塊」或「開關」。
3.  **No State**: Users don't know if it's ON or OFF without seeing the color.
    **無狀態**：使用者若看不到顏色，就不知道它是「開」還是「關」。

#### 4.2 Mature Approach (ARIA Pattern)
#### 4.2 成熟做法（ARIA 模式）

If we cannot use a native `<input type="checkbox">` due to extreme styling constraints (though usually you can using CSS opacity hacks), we build a semantic counterfeit.
如果因為極端的樣式限制而無法使用原生的 `<input type="checkbox">`（雖然通常可以用 CSS 透明度技巧達成），我們需要建構一個語意化的仿製品。

```html
<!-- BETTER: ARIA-enhanced custom control -->
<button
  type="button"
  role="switch"
  aria-checked="false"
  id="notify-switch"
  class="toggle-switch"
  onclick="toggleState(this)"
>
  <span class="knob"></span>
</button>
<label for="notify-switch">Enable Notifications</label>
```

**Analysis**:
**分析**：
*   **Element**: Uses `<button>` to get free keyboard focus and enter/space key handling.
    **元素**：使用 `<button>` 以免費獲得鍵盤焦點與 Enter/Space 鍵處理。
*   **Role**: `role="switch"` tells the AT this is a toggle, not a generic button.
    **角色**：`role="switch"` 告訴輔助科技這是一個開關，而非普通按鈕。
*   **State**: `aria-checked` must be programmatically updated via JS when clicked.
    **狀態**：`aria-checked` 必須在點擊時透過 JS 程式化更新。

#### 4.3 The "Best" Approach (Native + CSS)
#### 4.3 「最佳」做法（原生 + CSS）

The most robust solution uses the native input, ensuring 100% compatibility across devices and browsers without complex JS state management for A11y.
最穩健的解法是使用原生 input，確保在所有裝置與瀏覽器上 100% 相容，且無需為了 A11y 撰寫複雜的 JS 狀態管理。

```html
<!-- BEST: Native input with visual styling -->
<style>
  .sr-only {
    /* Standard pattern to hide element visually but keep it in A11y tree */
    position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
    overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0;
  }
  /* Style the label based on input state */
  input:checked + label .knob { transform: translateX(100%); }
  input:focus + label { outline: 2px solid blue; }
</style>

<input type="checkbox" id="notify-native" class="sr-only">
<label for="notify-native" class="toggle-switch">
  <span class="knob"></span>
  Enable Notifications
</label>
```

**Why this wins**:
**為何勝出**：
*   **Zero JS for Semantics**: The browser handles the state logic.
    **語意無需 JS**：瀏覽器處理狀態邏輯。
*   **Form Submission**: Works natively inside a `<form>`.
    **表單提交**：在 `<form>` 內可原生運作。
*   **Maintainability**: Less code to maintain.
    **可維護性**：程式碼更少，更好維護。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 Positive `tabindex`
### 5.1 正值的 `tabindex`

*   **Anti-pattern**: `<div tabindex="1">...</div>`
    **反模式**：`<div tabindex="1">...</div>`
*   **Issue**: Values greater than 0 force the element to the *front* of the tab order, breaking the natural DOM flow logic. It creates a confusing "jumping" experience for keyboard users.
    **問題**：大於 0 的值會強迫元素排到 Tab 順序的「最前面」，破壞自然的 DOM 順序邏輯。這會為鍵盤使用者創造混亂的「跳躍」體驗。
*   **Fix**: Only use `tabindex="0"` (make focusable in natural order) or `tabindex="-1"` (programmatically focusable, but skipped by Tab key).
    **修正**：只使用 `tabindex="0"`（使其依自然順序可聚焦）或 `tabindex="-1"`（可程式化聚焦，但 Tab 鍵會跳過）。

### 5.2 Clickable Divs without Key Handlers
### 5.2 只有點擊事件的 Div

*   **Anti-pattern**: `<div onClick={submit}>Submit</div>`
    **反模式**：`<div onClick={submit}>Submit</div>`
*   **Issue**: Even if you add `role="button"` and `tabindex="0"`, the `<div>` does not fire the `onClick` event when the user presses Enter or Space.
    **問題**：即使你加了 `role="button"` 和 `tabindex="0"`，當使用者按下 Enter 或 Space 鍵時，`<div>` 依然不會觸發 `onClick` 事件。
*   **Fix**: Use `<button>`, or manually add `onKeyDown` listeners for Enter/Space.
    **修正**：使用 `<button>`，或者手動加入針對 Enter/Space 的 `onKeyDown` 監聽器。

### 5.3 Redundant ARIA
### 5.3 冗餘的 ARIA

*   **Anti-pattern**: `<button role="button">Save</button>` or `<header role="banner">` (in HTML5).
    **反模式**：`<button role="button">Save</button>` 或 `<header role="banner">`（在 HTML5 中）。
*   **Issue**: It adds noise to the code and increases download size without adding value. HTML5 elements already have these implicit roles.
    **問題**：這增加了程式碼雜訊與下載大小，卻未增加價值。HTML5 元素已經具備這些隱含角色。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How do you handle accessibility in a complex Modal/Dialog component?
### Q1: 你如何在複雜的 Modal/Dialog 元件中處理無障礙設計？

*   **Key Points to Cover**:
    **高分回答要點**：
    1.  **Focus Trap**: Focus must be constrained within the modal so pressing Tab doesn't cycle to the background page.
        **焦點鎖定 (Focus Trap)**：焦點必須被限制在模態視窗內，按 Tab 鍵不應跳回背景頁面。
    2.  **Return Focus**: When the modal closes, focus must be restored to the element that opened it (the trigger).
        **歸還焦點**：當模態視窗關閉時，焦點必須歸還給當初打開它的元素（觸發器）。
    3.  **ARIA Roles**: Use `role="dialog"` (or `alertdialog`), `aria-modal="true"`, and `aria-labelledby` pointing to the modal title.
        **ARIA 角色**：使用 `role="dialog"`（或 `alertdialog`）、`aria-modal="true"`，並用 `aria-labelledby` 指向模態視窗標題。
    4.  **Escape Key**: The modal should close on pressing `Esc`.
        **Esc 鍵**：按下 `Esc` 鍵應關閉模態視窗。

### Q2: Explain the difference between `aria-label`, `aria-labelledby`, and `aria-describedby`.
### Q2: 請解釋 `aria-label`、`aria-labelledby` 與 `aria-describedby` 的差異。

*   **Key Points to Cover**:
    **高分回答要點**：
    *   `aria-label`: Provides a string label directly (invisible visually). Used when there is no visible text (e.g., a hamburger menu icon).
        `aria-label`：直接提供字串標籤（視覺不可見）。用於沒有可見文字時（例如漢堡選單圖示）。
    *   `aria-labelledby`: References the ID of another element to use as the label. It takes precedence over `aria-label`. Preferred if visible text exists.
        `aria-labelledby`：引用另一個元素的 ID 作為標籤。優先級高於 `aria-label`。若有可見文字，優先使用此項。
    *   `aria-describedby`: References an element that provides *additional* description (like a tooltip or error message), read after the label and role.
        `aria-describedby`：引用提供「額外」描述的元素（如提示框或錯誤訊息），會在讀完標籤與角色後讀出。

### Q3: How would you audit an existing application for accessibility issues?
### Q3: 你會如何對現有應用程式進行無障礙問題審查？

*   **Key Points to Cover**:
    **高分回答要點**：
    1.  **Automated Tools**: Start with Lighthouse, axe-core, or ARC Toolkit to catch ~30-50% of syntactic errors.
        **自動化工具**：先用 Lighthouse, axe-core 或 ARC Toolkit 抓出約 30-50% 的語法錯誤。
    2.  **Keyboard Navigation**: Manually tab through the site. Can you reach everything? Can you trigger everything? Are focus rings visible?
        **鍵盤導航**：手動用 Tab 鍵瀏覽網站。能到達所有地方嗎？能觸發所有功能嗎？焦點框 (Focus rings) 可見嗎？
    3.  **Screen Reader Testing**: Use NVDA (Windows) or VoiceOver (Mac) to verify the A11y tree structure and announcements.
        **螢幕閱讀器測試**：使用 NVDA (Windows) 或 VoiceOver (Mac) 驗證無障礙樹結構與語音宣告。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Recap (記憶錨點)
*   **DOM != A11y Tree**: Browsers create a separate tree for assistive tech; your job is to ensure this tree is meaningful.
    **DOM 不等於 A11y Tree**：瀏覽器為輔助科技建立了獨立的樹；你的工作是確保這棵樹有意義。
*   **Native First**: Always prefer semantic HTML (`<button>`, `<nav>`) over ARIA. ARIA is a polyfill, not a primary tool.
    **原生優先**：永遠優先使用語意化 HTML（`<button>`, `<nav>`）而非 ARIA。ARIA 是補丁，不是主要工具。
*   **Focus Management**: In SPAs and Modals, you must manually manage where the keyboard focus goes.
    **焦點管理**：在 SPA 與 Modals 中，你必須手動管理鍵盤焦點的去向。
*   **Interactive Elements**: If it clicks, it must be focusable (tabindex) and actionable (Enter/Space).
    **互動元素**：如果它能被點擊，它就必須是可聚焦的 (tabindex) 且可操作的 (Enter/Space)。
*   **Labels**: Every input and button needs a perceptible name (via content, `label`, or `aria-label`).
    **標籤**：每個輸入框與按鈕都需要一個可感知的名稱（透過內容、`label` 或 `aria-label`）。

### Next Steps (下一步)
*   **Practice**: Try to navigate your company's main product using *only* a keyboard. Note down every frustration.
    **實作**：嘗試「只」用鍵盤導航你公司的主要產品。記下每一個令人沮喪的地方。
*   **Deep Dive**: Study **WCAG 2.2 AA** standards to understand the specific contrast and target size requirements.
    **深入研究**：研讀 **WCAG 2.2 AA** 標準，理解具體的對比度與點擊目標大小要求。
*   **Next Chapter**: Proceed to **Chapter 03: CSS Architecture at Scale (BEM, CSS Modules, CSS-in-JS)** to learn how to style these semantic elements maintainably.
    **下一章**：前往 **第 03 章：大規模 CSS 架構 (BEM, CSS Modules, CSS-in-JS)**，學習如何以可維護的方式為這些語意化元素設定樣式。