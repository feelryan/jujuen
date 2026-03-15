# CSS 架構設計：可維護性、命名慣例與模組化 / CSS Architecture: Maintainability, Naming Conventions, and Modularity

## Mental model｜心智模型

在撰寫 CSS 時，初學者往往將其視為「為 HTML 元素上色」的過程，但在資深工程師眼中，CSS 架構設計本質上是 **依賴管理（Dependency Management）** 與 **作用域控制（Scope Control）**。

要建立可擴展（Scalable）的 CSS 架構，你需要轉變以下心智模型：

1.  **CSS as an API (CSS 即介面)**：
    將 CSS class 視為元件的公開介面（Public API）。當你寫下 `.btn-primary` 時，你正在定義一個合約。架構設計的目標是確保這個合約是**可預測的（Predictable）**且**穩定的（Stable）**。

2.  **The Specificity Graph (特異性圖譜)**：
    健康的 CSS 架構，其特異性（Specificity）應該是平緩的。理想情況下，特異性不應隨著專案增長而螺旋上升。
    *   **Bad Model**: 為了覆蓋舊樣式，不斷疊加 ID 或 `!important`（特異性競賽）。
    *   **Good Model**: 保持低特異性（主要使用單一 Class），讓樣式由「定義順序」而非「權重」決定。

3.  **Append-Only vs. Refactorable (唯增長 vs. 可重構)**：
    糟糕的架構會導致工程師不敢刪除舊程式碼，只能不斷新增（Append-only CSS），導致檔案無限膨脹。好的架構能讓你明確知道：「刪除這行 CSS，只會影響這個元件，不會炸掉全站。」

---

## Patterns & best practices｜常見模式與最佳實務

在真實的大型專案中，我們通常混合使用以下模式來解決特定問題：

### 1. 命名慣例：BEM (Block, Element, Modifier)
儘管現代框架盛行，BEM 仍是理解 CSS 模組化的基石。它的核心價值不在於長長的 class 名稱，而在於**扁平化特異性**與**解耦結構**。

*   **Block**: 獨立的元件（如 `.card`）。
*   **Element**: 元件的子部分，依賴於 Block（如 `.card__title`）。
*   **Modifier**: 狀態或變體（如 `.card--featured`）。

> **Why it works**: 它移除了對 HTML 結構的依賴（不使用 `.card h2`），讓你可以隨意移動 HTML 標籤而不破壞樣式。

### 2. 架構組織：ITCSS (Inverted Triangle CSS)
這解決了「CSS 檔案該如何排序」的問題。將 CSS 分層，從最通用到最具體，確保 Cascade（層疊）運作正常。

1.  **Settings**: 變數、Design Tokens（不產出 CSS）。
2.  **Tools**: Mixins、Functions（不產出 CSS）。
3.  **Generic**: Reset、Normalize。
4.  **Elements**: 未帶 class 的 HTML 標籤樣式（h1, a, p）。
5.  **Objects**: OOCSS 模式，無外觀的佈局骨架（如 `.container`, `.grid`）。
6.  **Components**: 具體的 UI 元件（`.btn`, `.card`）。
7.  **Trumps / Utilities**: `!important`、Helper classes（`.text-center`, `.hidden`）。

### 3. Utility-First (Tailwind CSS)
現代開發的主流模式。不再撰寫語意化的 CSS class，而是組合單一功能的 Utility classes。

*   **Trade-off**: HTML 變得雜亂，但 CSS 檔案大小停止增長（Logarithmic growth）。
*   **Best Practice**: 嚴格限制自定義 CSS（Arbitrary values），強制使用 Design Tokens（`bg-blue-500` 而非 `bg-[#123456]`）以維持一致性。

### 4. Scoped CSS (CSS Modules / CSS-in-JS)
透過工具自動生成唯一的 hash class name（如 `.Button_button__1x2a`），從根本上解決 Global Scope 污染問題。這在 React/Vue 生態系中是標準配置。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Parent-Child" Dependency (過度依賴父層)
```css
/* Bad: 依賴 HTML 結構，且特異性高 */
.sidebar .nav ul li a { color: blue; }

/* Good: 獨立元件，低特異性 */
.nav-link { color: blue; }
```
**後果**：當你把導覽列移出 Sidebar 時，樣式失效；或者你想在 Sidebar 放別的連結時，樣式被意外污染。

### 2. Premature Abstraction (過早抽象化)
看到兩個按鈕有一樣的 `padding` 就急著提取一個 `.shared-padding` class。
**後果**：當設計變更，其中一個按鈕需要不同 padding 時，你陷入了維護地獄。
**原則**：**Duplication is far cheaper than the wrong abstraction.**（重複程式碼比錯誤的抽象成本更低。）

### 3. Magic Numbers (魔術數字)
```css
.modal {
  z-index: 9999; /* 祈禱它在最上面 */
  top: 37px;     /* 剛好對齊某個特定 header 高度 */
}
```
**後果**：脆弱的佈局。只要 Header 高度一變，佈局就壞了。
**解法**：使用 Design Tokens 或 CSS Variables 計算；建立統一的 z-index 管理系統（如 Sass map）。

### 4. Using ID for Styling (使用 ID 進行樣式設定)
**後果**：ID 的特異性無限大，導致你必須使用 `!important` 或更多 ID 來覆蓋它，引發特異性戰爭。

---

## Checklists & workflows｜檢查清單與流程

在進行 Code Review 或重構 CSS 時，請使用此清單：

### Architecture Decision Tree (架構決策樹)
- [ ] **專案規模？**
    - 小型/行銷頁面 -> Utility-first (Tailwind) 或單純 CSS。
    - 大型應用程式 -> CSS Modules / Styled Components (Component-based)。
    - 舊專案維護 -> BEM + ITCSS。
- [ ] **是否需要支援多主題 (Dark Mode/Theming)？**
    - 是 -> 必須優先定義 CSS Variables (Design Tokens)。

### Code Quality Checklist (代碼品質檢查)
- [ ] **Specificity Check**: 是否使用了 ID 選擇器？是否使用了超過 2 層的巢狀（Nesting）？（理想應為 1 層）。
- [ ] **Scope Leak**: 修改這個 class 是否會影響到我不預期的頁面？（若不確定，應考慮改名或增加 BEM Modifier）。
- [ ] **Token Usage**: 所有的顏色、間距、字體大小是否都使用了變數（Variables/Tokens），而非 Hard-coded 數值？
- [ ] **Z-Index**: 新增的 `z-index` 是否符合專案的全域規範？
- [ ] **Undo Styles**: 是否寫了大量的 `unset` 或 `initial` 來抵消之前的樣式？（這代表架構順序有誤或繼承了不該繼承的東西）。

---

## Real-world examples｜實戰案例

### Case 1: Refactoring Legacy CSS (重構遺留代碼)

**情境**：一個老舊專案，CSS 檔案長達 5000 行，充滿了 `.wrapper div p { ... }` 這種寫法。

**Bad Practice (直接覆蓋)**:
```css
/* 在檔案最下方新增 */
.wrapper div p.special-text {
  color: red !important; /* 放棄治療 */
}
```

**Refactoring Workflow (使用 BEM + ITCSS)**:
1.  **Identify**: 找出該段 HTML，加上新的 BEM class。
    ```html
    <div class="wrapper">
      <div>
        <p class="card__text">Content...</p> <!-- 新增 class -->
      </div>
    </div>
    ```
2.  **Isolate**: 建立新的 CSS 規則，確保特異性夠低但能生效。
3.  **Deprecate**: 標記舊的 CSS 為待刪除，或使用工具（如 PurgeCSS）分析未使用的樣式。

### Case 2: The "Card" Component (BEM vs. Tailwind)

**Requirement**: 一個帶有圖片、標題和「購買」按鈕的卡片。

**Approach A: BEM (Semantic & Readable)**
```html
<article class="product-card product-card--featured">
  <img class="product-card__image" src="..." />
  <div class="product-card__body">
    <h2 class="product-card__title">Item Name</h2>
    <button class="btn btn--primary">Buy</button>
  </div>
</article>
```
*優點*：HTML 乾淨，語意明確，適合團隊習慣寫 SCSS 的情境。

**Approach B: Utility-first / Tailwind (Rapid Development)**
```html
<article class="border rounded-lg shadow-md p-4 bg-white hover:shadow-xl transition">
  <img class="w-full h-48 object-cover rounded" src="..." />
  <div class="mt-4">
    <h2 class="text-lg font-bold text-gray-900">Item Name</h2>
    <button class="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
      Buy
    </button>
  </div>
</article>
```
*優點*：開發速度極快，不用切換檔案，保證樣式一致性（不會出現 `13px` 的 padding）。
*實戰技巧*：如果 `button` 的 class 組合太長且重複使用，應使用框架的元件封裝（如 React Component）或 `@apply`（謹慎使用）來抽象化。