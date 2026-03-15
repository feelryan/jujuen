# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，CSS 佈局不再只是關於「如何把元素置中」，而是關於如何建立可維護、可預測且高效能的 UI 架構。在現代 Web 開發中，我們必須從依賴 Viewport 的全域響應式設計，轉向以元件為中心的模組化設計。

For senior engineers, CSS layout is no longer just about "how to center an element," but about building UI architectures that are maintainable, predictable, and performant. In modern web development, we must shift from global viewport-dependent responsive design to component-centric modular design.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精準決策佈局模型**：從「內容優先（Content-first）」與「佈局優先（Layout-first）」的角度，區分 Flexbox 與 Grid 的最佳適用場景。
    **Decide layout models precisely**: Distinguish the best use cases for Flexbox versus Grid based on "Content-first" vs. "Layout-first" perspectives.
2.  **掌握二維佈局策略**：利用 CSS Grid 解決複雜的儀表板（Dashboard）與應用程式介面排版，減少不必要的 DOM 巢狀結構。
    **Master 2D layout strategies**: Use CSS Grid to solve complex dashboard and application interface layouts, reducing unnecessary DOM nesting.
3.  **實作真正的模組化設計**：運用 Container Queries (`@container`) 解耦元件與頁面寬度的依賴，使其在 Micro-frontends 或 Design Systems 中具備高度可移植性。
    **Implement true modular design**: Leverage Container Queries (`@container`) to decouple components from page width dependencies, making them highly portable in Micro-frontends or Design Systems.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 Flexbox vs. Grid：一維流與二維網格 (1D Stream vs. 2D Mesh)

**Flexbox (Flexible Box Layout)** 的心智模型是「流（Stream）」。它專注於**一維**空間（行或列）中的分佈。它的核心邏輯是 **Content-out**（由內容決定尺寸）：容器會根據子元素的大小與剩餘空間來計算佈局。

The mental model for **Flexbox (Flexible Box Layout)** is a "Stream." It focuses on distribution within a **one-dimensional** space (row or column). Its core logic is **Content-out**: the container calculates the layout based on the size of its children and the available remaining space.

**CSS Grid** 的心智模型是「藍圖（Blueprint）」。它專注於**二維**空間（同時控制行與列）。它的核心邏輯是 **Layout-in**（由佈局決定尺寸）：我們先定義好網格軌道（Tracks），然後將元素放入其中。

The mental model for **CSS Grid** is a "Blueprint." It focuses on **two-dimensional** space (controlling both rows and columns simultaneously). Its core logic is **Layout-in**: we define the grid tracks first, and then place elements into them.

> **資深觀點 (Senior Insight)**：
> 如果你發現自己在 Flexbox 中使用了固定的 `width` 或 `calc()` 來強制換行以模擬網格，你應該切換到 Grid。如果你在 Grid 中只用了一行或一列，且依賴內容撐開寬度，你可能只需要 Flexbox。
>
> **Senior Insight**:
> If you find yourself using fixed `width` or `calc()` in Flexbox to force wrapping and simulate a grid, you should switch to Grid. If you are using Grid for a single row or column and relying on content to dictate width, you likely just need Flexbox.

## 2.2 Container Queries：元件的自我意識 (Self-Awareness of Components)

傳統的 Media Queries (`@media`) 查詢的是**瀏覽器視窗（Viewport）**的屬性。這導致元件缺乏獨立性：一個卡片元件在側邊欄（窄）與主內容區（寬）需要不同的樣式，但 Media Queries 無法感知其父容器的寬度。

Traditional Media Queries (`@media`) query the properties of the **browser viewport**. This leads to a lack of component independence: a card component needs different styles when in a sidebar (narrow) versus the main content area (wide), but Media Queries cannot perceive the width of the parent container.

**Container Queries (`@container`)** 讓元件查詢其**最近的容器**狀態。這改變了響應式設計的心智模型：從「頁面如何適應螢幕」轉變為「元件如何適應其容器」。

**Container Queries (`@container`)** allow a component to query the state of its **nearest container**. This shifts the mental model of responsive design: from "how the page adapts to the screen" to "how the component adapts to its container."

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型系統與 Design Systems 的架構設計中，佈局選擇直接影響**可維護性 (Maintainability)** 與 **累積佈局位移 (CLS, Cumulative Layout Shift)**。

In the architectural design of large-scale systems and Design Systems, layout choices directly impact **Maintainability** and **Cumulative Layout Shift (CLS)**.

## 3.1 Design Systems 與 Micro-frontends (Design Systems & Micro-frontends)

在微前端架構中，團隊 A 開發的 Widget 可能被嵌入到團隊 B 的 Dashboard 中。團隊 A 無法預知 Widget 會被放在多寬的容器裡。

In a micro-frontend architecture, a Widget developed by Team A might be embedded into a Dashboard owned by Team B. Team A cannot predict the width of the container where the Widget will be placed.

*   **Legacy Approach**: 使用 JS 監聽 `ResizeObserver` 並動態切換 class。這會增加 JS 執行時間並可能導致閃爍。
*   **Modern Approach**: 使用 Container Queries。CSS 引擎原生處理，效能極佳，且實現了真正的「一次編寫，隨處運行」。

*   **Legacy Approach**: Using JS to listen to `ResizeObserver` and dynamically toggling classes. This increases JS execution time and can cause flickering.
*   **Modern Approach**: Using Container Queries. Handled natively by the CSS engine, it offers excellent performance and achieves true "write once, run anywhere."

## 3.2 複雜 B2B 儀表板 (Complex B2B Dashboards)

對於像 AWS Console 或 Google Cloud Console 這類高密度資訊的介面：

For high-density information interfaces like AWS Console or Google Cloud Console:

*   **Grid 的優勢**：可以定義明確的區域（Areas），例如 Sidebar, Header, Main, Footer。當需要調整佈局（例如將 Sidebar 移到底部）時，只需修改 Grid Template，而無需更動 HTML 結構。這極大地降低了重構成本。
*   **Grid Advantage**: You can define explicit Areas (e.g., Sidebar, Header, Main, Footer). When layout adjustments are needed (e.g., moving the Sidebar to the bottom), you only modify the Grid Template without touching the HTML structure. This significantly reduces refactoring costs.

## 3.3 效能考量 (Performance Considerations)

*   **Layout Thrashing**: 過度巢狀的 Flexbox（Flex inside Flex inside Flex）會增加瀏覽器 Layout 計算的複雜度。Grid 允許扁平化的 HTML 結構，減少 DOM 深度。
*   **Layout Thrashing**: Excessively nested Flexbox (Flex inside Flex inside Flex) increases the complexity of the browser's Layout calculation. Grid allows for a flatter HTML structure, reducing DOM depth.
*   **CLS**: Grid 允許開發者預先定義軌道尺寸（例如 `grid-template-columns: 200px 1fr`）。即使內容尚未載入（如圖片），空間也已被保留，這有助於優化 Core Web Vitals 中的 CLS 分數。
*   **CLS**: Grid allows developers to pre-define track sizes (e.g., `grid-template-columns: 200px 1fr`). Even if content (like images) hasn't loaded yet, the space is reserved, which helps optimize the CLS score in Core Web Vitals.

---

# 4. 逐步示例 (Walkthrough / Example)

## 案例：自適應產品卡片 (Scenario: Adaptive Product Card)

**背景**：我們需要設計一個 `ProductCard` 元件。它在手機上是垂直堆疊，在桌機列表中是水平排列，但在桌機的側邊欄（窄空間）中又必須變回垂直堆疊。

**Context**: We need to design a `ProductCard` component. It stacks vertically on mobile, arranges horizontally in a desktop list, but must switch back to a vertical stack when placed in a desktop sidebar (narrow space).

### 4.1 Naive Solution: Media Queries

```css
/* Anti-pattern for reusable components */
.card {
  display: flex;
  flex-direction: column;
}

@media (min-width: 768px) {
  .card {
    flex-direction: row; /* Switch to horizontal on desktop */
  }
}

/* Problem: If this card is in a narrow sidebar on desktop, 
   it will still try to be horizontal, breaking the layout. */
```

**問題**：這種做法假設「螢幕寬 = 容器寬」。當卡片被放入側邊欄時，螢幕雖寬，但可用空間很窄，佈局會崩壞。

**Problem**: This approach assumes "screen width = container width." When the card is placed in a sidebar, the screen is wide, but the available space is narrow, causing the layout to break.

### 4.2 Modern Solution: Container Queries + Grid

我們將使用 Container Queries 來根據父容器寬度調整佈局，並結合 Grid 來處理內部排版。

We will use Container Queries to adjust layout based on parent container width, combined with Grid for internal structuring.

**Step 1: 定義容器 (Define the Container)**

首先，外層容器必須被標記為 Query Container。

First, the outer wrapper must be marked as a Query Container.

```css
.card-container {
  /* Define this element as a container for size queries */
  container-type: inline-size; 
  container-name: card-wrapper;
}
```

**Step 2: 實作響應式卡片 (Implement the Responsive Card)**

```css
.card {
  display: grid;
  /* Default: Mobile-first / Narrow view (Vertical stack) */
  grid-template-columns: 1fr; 
  gap: 1rem;
  border: 1px solid #ddd;
  padding: 1rem;
}

.card__image {
  width: 100%;
  aspect-ratio: 16/9;
  object-fit: cover;
}

/* When the container is wider than 400px */
@container card-wrapper (min-width: 400px) {
  .card {
    /* Switch to Horizontal layout */
    grid-template-columns: 150px 1fr; 
    align-items: center;
  }
  
  .card__image {
    height: 100%; /* Match height of content */
    aspect-ratio: auto;
  }
}
```

### 4.3 為何這是最佳解？ (Why is this the best solution?)

1.  **Decoupling**: `.card` 完全不關心 Viewport 是多少。它只關心自己有多少空間。
    **Decoupling**: The `.card` doesn't care about the Viewport at all. It only cares about how much space it has.
2.  **Reusability**: 你可以將此卡片放入 Grid 的主區域（寬）、Flexbox 的側邊欄（窄），甚至 Modal 中，它都能完美呈現。
    **Reusability**: You can place this card in a Grid main area (wide), a Flexbox sidebar (narrow), or even a Modal, and it will render perfectly.
3.  **Grid Power**: 使用 `grid-template-columns: 150px 1fr` 比 Flexbox 更穩定，因為圖片寬度被嚴格限制為 150px，不會因為圖片載入延遲而導致內容跳動。
    **Grid Power**: Using `grid-template-columns: 150px 1fr` is more stable than Flexbox because the image width is strictly constrained to 150px, preventing content jumps due to image loading delays.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 濫用 Flexbox 處理二維佈局 (Misusing Flexbox for 2D Layouts)

*   **錯誤 (Pitfall)**: 使用 `flex-wrap: wrap` 並配合 `width: 33%` 或 `margin` 來模擬網格。
    **Pitfall**: Using `flex-wrap: wrap` combined with `width: 33%` or `margin` to simulate a grid.
*   **後果 (Consequence)**: 最後一行的元素對齊會很痛苦（例如最後一行只有兩個元素時，它們可能無法與上方對齊，或者間距計算困難）。
    **Consequence**: Aligning elements in the last row becomes painful (e.g., if the last row has only two elements, they might not align with the rows above, or gap calculations become difficult).
*   **修正 (Fix)**: 使用 CSS Grid (`grid-template-columns: repeat(auto-fill, minmax(200px, 1fr))`)。這能自動處理響應式換行且保持嚴格對齊。
    **Fix**: Use CSS Grid (`grid-template-columns: repeat(auto-fill, minmax(200px, 1fr))`). This automatically handles responsive wrapping while maintaining strict alignment.

## 5.2 忽略視覺順序與 DOM 順序的不一致 (Ignoring Visual vs. DOM Order Mismatch)

*   **錯誤 (Pitfall)**: 過度使用 `order` 屬性（Flexbox/Grid）或 `grid-template-areas` 來大幅改變視覺佈局，導致視覺順序與 HTML DOM 順序脫節。
    **Pitfall**: Overusing the `order` property (Flexbox/Grid) or `grid-template-areas` to drastically change the visual layout, causing a disconnect between visual order and HTML DOM order.
*   **後果 (Consequence)**: 嚴重破壞無障礙體驗（Accessibility）。螢幕閱讀器（Screen Readers）是依據 DOM 順序朗讀，鍵盤導航（Tab 鍵）也是依據 DOM 順序。使用者視覺上看到焦點跳來跳去。
    **Consequence**: Severely harms Accessibility. Screen Readers read based on DOM order, and keyboard navigation (Tab key) also follows DOM order. Users will see the focus jumping around erratically.
*   **修正 (Fix)**: 盡量保持 DOM 結構與視覺邏輯一致。僅在微調（如將圖片移到文字右側）時使用 `order`，避免用於重大的邏輯重排。
    **Fix**: Keep the DOM structure consistent with the visual logic as much as possible. Use `order` only for minor adjustments (like moving an image to the right of text), avoiding it for major logical reordering.

## 5.3 在 Grid 中使用絕對單位導致溢出 (Using Absolute Units in Grid Causing Overflow)

*   **錯誤 (Pitfall)**: 定義 `grid-template-columns: 300px 1fr`，但在小螢幕上容器小於 300px。
    **Pitfall**: Defining `grid-template-columns: 300px 1fr`, but the container is smaller than 300px on small screens.
*   **後果 (Consequence)**: 觸發水平捲軸，破壞佈局。
    **Consequence**: Triggers a horizontal scrollbar, breaking the layout.
*   **修正 (Fix)**: 使用 `minmax()` 或媒體查詢/容器查詢。例如 `minmax(0, 1fr)` 或 `minmax(200px, 1fr)` 配合 wrap。**特別注意**：`minmax(0, 1fr)` 是解決 Grid item 內容溢出（blowout）問題的常見技巧（預設是 `min-content`）。
    **Fix**: Use `minmax()` or media/container queries. For example, `minmax(0, 1fr)` or `minmax(200px, 1fr)` with wrapping. **Note**: `minmax(0, 1fr)` is a common trick to solve Grid item content blowout issues (default is `min-content`).

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

這些問題旨在測試候選人對現代 CSS 架構的深度理解，而非單純的語法記憶。

These questions are designed to test a candidate's deep understanding of modern CSS architecture, rather than simple syntax memorization.

## 6.1 決策 Grid 與 Flexbox (Deciding between Grid and Flexbox)

**Q: "在設計一個複雜的頁面佈局時，你如何決定何時使用 Grid，何時使用 Flexbox？請舉例說明。"**
**Q: "When designing a complex page layout, how do you decide when to use Grid and when to use Flexbox? Please provide examples."**

*   **高分回答要點 (Key Points)**:
    *   **維度 (Dimensions)**: Flexbox 是一維（1D），Grid 是二維（2D）。
    *   **控制權 (Control)**: Grid 是 "Layout-in"（父層控制子層位置），Flexbox 是 "Content-out"（子層大小影響排列）。
    *   **重疊 (Overlap)**: Grid 允許元素輕易重疊（Layering），Flexbox 較難做到。
    *   **實例**: 整個頁面的 Skeleton（Header/Sidebar/Main）用 Grid；導航列（Navbar）內部的按鈕排列用 Flexbox。

## 6.2 實作 Design System 的響應式策略 (Responsive Strategy for Design Systems)

**Q: "我們正在建立一套供多個產品線使用的 Design System。你會如何設計元件的響應式行為，以確保它們在不同寬度的容器中都能正常顯示？"**
**Q: "We are building a Design System for multiple product lines. How would you design the responsive behavior of components to ensure they render correctly in containers of varying widths?"**

*   **高分回答要點 (Key Points)**:
    *   指出 Media Queries 的侷限性（依賴 Viewport）。
    *   提出 **Container Queries** 作為核心解決方案。
    *   討論 Fallback 策略（對於不支援舊瀏覽器的處理，雖在現代已較少見）。
    *   強調元件應具備 "Fluidity"（流動性），使用相對單位（%, fr, rem）而非固定像素。

## 6.3 佈局造成的效能問題 (Performance Issues Caused by Layout)

**Q: "CSS 佈局方式會如何影響瀏覽器的 Rendering Performance？什麼是 CLS，Grid 和 Flexbox 對此有何影響？"**
**Q: "How do CSS layout methods affect browser Rendering Performance? What is CLS, and how do Grid and Flexbox impact it?"**

*   **高分回答要點 (Key Points)**:
    *   解釋 Reflow (Layout) 與 Repaint。
    *   **CLS (Cumulative Layout Shift)**: 說明 Grid 如何透過預留空間（Explicit Tracks）來減少 CLS。
    *   Flexbox 若未設定寬度，圖片載入後撐開容器會導致 Shift。
    *   避免在動畫中使用會觸發 Layout 的屬性（如 `width`, `left`），應使用 `transform`。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 本章重點 (Key Takeaways)

1.  **Flexbox** 適用於**一維**內容流（Content-out），適合元件內部的微觀佈局（Micro-layout）。
    **Flexbox** is for **1D** content streams (Content-out), suitable for micro-layouts within components.
2.  **Grid** 適用於**二維**結構（Layout-in），適合頁面整體的宏觀佈局（Macro-layout）與複雜對齊。
    **Grid** is for **2D** structures (Layout-in), suitable for macro-layouts of the page and complex alignment.
3.  **Container Queries** 是現代模組化設計的關鍵，它讓元件響應其**容器**而非螢幕，實現真正的可重用性。
    **Container Queries** are key to modern modular design, allowing components to respond to their **container** rather than the screen, achieving true reusability.
4.  在系統設計層面，選擇正確的佈局模型能顯著降低 DOM 複雜度並提升 **Core Web Vitals (CLS)** 分數。
    At the system design level, choosing the right layout model can significantly reduce DOM complexity and improve **Core Web Vitals (CLS)** scores.
5.  注意 **Accessibility**，切勿讓視覺順序與 DOM 順序嚴重脫節。
    Pay attention to **Accessibility**; never let the visual order become severely disconnected from the DOM order.

## 後續延伸 (Next Steps)

*   **進階實作**: 嘗試重構一個舊專案的 Media Queries 為 Container Queries。
    **Advanced Practice**: Try refactoring the Media Queries of a legacy project into Container Queries.
*   **下一章預告**: 深入探討 **CSS Architecture & Scalability**（BEM, CSS Modules, CSS-in-JS, Tailwind），學習如何在大型團隊中管理 CSS 命名空間與樣式衝突。
    **Next Chapter Preview**: Dive deep into **CSS Architecture & Scalability** (BEM, CSS Modules, CSS-in-JS, Tailwind), learning how to manage CSS namespaces and style conflicts in large teams.