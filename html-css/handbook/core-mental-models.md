# 核心心智模型：盒模型、層疊上下文與格式化上下文 / Core Mental Models: Box Model, Stacking Contexts, and Formatting Contexts

CSS 的難點往往不在於屬性太多，而在於其背後的渲染邏輯與直覺相悖。本章節將幫助你建立正確的「渲染心智模型」，讓你不再是透過「試誤法」（Trial and Error）來寫 CSS，而是能夠精準預測瀏覽器的行為。

Understanding CSS is not about memorizing properties, but about mastering the rendering logic. This chapter focuses on the mental models required to predict browser behavior accurately, moving you away from "trial and error" coding.

---

## Mental model｜心智模型

### 1. 盒模型是「房地產」，不是「繪畫」 (Real Estate vs. Painting)
不要只把元素看作螢幕上的圖形，要把它看作**佔據空間的容器**。
- **Content**: 實際居住空間。
- **Padding**: 室內牆壁厚度（屬於房子的一部分，會撐大房子）。
- **Border**: 房子的外牆。
- **Margin**: 房子與鄰居之間的法定空地（不屬於房子，但影響位置）。
- **Key Insight**: 瀏覽器計算佈局時，是先算「佔地面積」，再算「繪製內容」。

### 2. 層疊上下文是「圖層資料夾」 (Stacking Contexts are Layer Groups)
`z-index` 並不是一個全域的數值比較（Global Ranking）。
- 想像 Photoshop 的圖層資料夾（Layer Groups）。
- 如果父元素建立了一個新的 Stacking Context（資料夾），那麼子元素的 `z-index` 就像是資料夾內部的順序。
- **Rule**: 如果父資料夾在底層，無論子圖層的 `z-index` 設得多高（例如 `9999`），它永遠無法蓋過位於上層父資料夾中的元素。

### 3. 格式化上下文是「獨立沙箱」 (Formatting Contexts are Sandboxes)
BFC (Block Formatting Context)、FFC (Flex)、GFC (Grid) 就像是建立了獨立的行政區。
- **隔離性 (Isolation)**：沙箱內部的佈局變化（如浮動）不會影響到外部，外部的規則（如 Margin Collapsing）也不一定能穿透進來。
- 這是解決「高度塌陷」與「外距重疊」的根本機制。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 全域重置盒模型 (Universal Box Sizing)
永遠不要使用預設的 `content-box` 進行佈局計算，那違反人類直覺。
Always use `border-box` to ensure `width` includes padding and border.

```css
/* The most important snippet in CSS */
*, *::before, *::after {
  box-sizing: border-box;
}
```

### 2. 使用 `isolation: isolate` 管理層疊 (Managing Stacking Contexts)
當你需要建立一個新的層疊上下文，但不想使用 `position: relative` 或 `z-index` 產生副作用時，使用 `isolation: isolate`。這在建立 Component Library 時特別重要，可以防止內部的 `z-index` 洩漏或被外部干擾。

```css
.card {
  /* Creates a new stacking context without positioning side-effects */
  isolation: isolate; 
}
```

### 3. 系統化管理 Z-Index (Z-Index Scales)
不要使用 magic numbers (`999`, `9999`)。使用 Sass 變數或 CSS Custom Properties 定義層級。

```css
:root {
  --z-negative: -1;
  --z-normal: 1;
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-modal: 300;
  --z-popover: 400;
}
```

### 4. 使用 `display: flow-root` 觸發 BFC
過去我們用 `overflow: hidden` 或 clearfix hack 來包含浮動元素（Clear fix），現在標準的做法是使用 `display: flow-root`。它唯一的用途就是建立一個新的 BFC，且沒有 `overflow` 裁剪內容的副作用。

```css
.container {
  /* Contains floated children and prevents margin collapsing with children */
  display: flow-root; 
}
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 意外的層疊上下文 (Accidental Stacking Contexts)
**Pitfall**: 你以為只有 `z-index` 會影響層級，但其實 `opacity < 1`, `transform`, `filter`, `will-change` 等屬性都會默默地建立新的 Stacking Context。
**Consequence**: 這會導致 `position: fixed` 的元素突然「失效」（變成了相對於該父元素定位，而非 Viewport），或是 `z-index` 比較失效。

### 2. 外距重疊的困惑 (Margin Collapsing Confusion)
**Pitfall**: 垂直方向上，相鄰的 Block 元素 Margin 會合併（取最大值），甚至父子元素的 Margin 也會合併（如果沒有 border/padding 隔開）。
**Anti-pattern**: 為了推開父元素，給子元素加 `margin-top`，結果發現父元素跟著掉下來了（因為 Margin 穿透了）。
**Fix**: 給父元素加 `padding-top: 1px`，或設定 `overflow: hidden` / `display: flow-root` (BFC)。

### 3. 濫用 `z-index: 99999` (Z-Index Wars)
**Pitfall**: 為了解決蓋不住的問題，工程師開始競標 `z-index`。
**Consequence**: 維護惡夢。當你需要一個比 `99999` 更高的元素時，你只能寫 `100000`，最後數字失去意義。

---

## Checklists & workflows｜檢查清單與流程

當遇到佈局錯亂或層級錯誤時，請依序檢查：

### 🛑 Debugging "Why is this element not visible/clickable?" (Z-Index Issues)
- [ ] **檢查父層級**：該元素的父層（或祖先層）是否建立了 Stacking Context？
  - 檢查 `opacity`, `transform`, `filter`, `perspective`, `isolation`, `will-change`。
- [ ] **檢查同層比較**：如果父層建立了 Context，該父層與「你想蓋過的元素」的父層，誰的 `z-index` 更大？
  - *記住：小資料夾裡的國王，打不過大資料夾裡的平民。*
- [ ] **檢查定位**：`z-index` 預設只對 `position` 非 `static` 的元素有效（除非是 Flex/Grid item）。

### 📐 Debugging "Why is the spacing weird?" (Box Model Issues)
- [ ] **檢查 Box Sizing**：是否全域套用了 `box-sizing: border-box`？
- [ ] **檢查 Margin Collapse**：
  - 這是垂直方向的 Block 元素嗎？
  - 父子之間是否有 Border 或 Padding 阻隔？
  - 是否需要觸發 BFC (`display: flow-root`) 來隔離 Margin？
- [ ] **檢查 Line Height**：文字元素的高度往往受到 `line-height` 撐開，而不僅僅是 `font-size`。

---

## Real-world examples｜實戰案例

### Case 1: The "Fixed" Header Trap (Transform vs. Fixed)

**情境**：你做了一個 `position: fixed` 的 Header，原本運作正常。後來為了做進場動畫，你在 `<body>` 或外層容器加了 `transform: translate(...)`。
**災難**：Header 突然不再固定於視窗頂部，而是隨著頁面捲動跑掉了。
**原因**：`transform` 屬性會在該元素上建立新的 Containing Block，導致內部的 `position: fixed` 變成相對於該元素定位，而非 Viewport。
**解法**：避免在包含 `position: fixed` 元素的父層上使用 `transform`。如果必須做動畫，考慮將 Fixed 元素移出該容器，與容器並列。

### Case 2: The "Media Object" Layout (BFC Application)

**情境**：經典的圖文排版（左圖右文）。
**問題**：如果文字太短，圖片高度太高，下方的內容會跑上來被圖片蓋住（浮動溢出）。
**傳統解法**：在容器底部加 `<div style="clear: both"></div>`。
**現代解法 (BFC)**：

```css
.media-object {
  /* 圖片浮動 */
  .img { float: left; margin-right: 10px; }
  
  /* 文字容器觸發 BFC */
  .content {
    display: flow-root; /* 建立 BFC */
    /* 結果：.content 的左邊界會自動避開浮動圖片，
       且 .content 內部的高度計算會包含其子元素，不會塌陷 */
  }
}
```

### Case 3: Tooltip inside a Card with `overflow: hidden`

**情境**：一個卡片元件設定了 `overflow: hidden` (為了圓角裁切圖片)，卡片內有一個按鈕，hover 時會顯示 Tooltip。
**問題**：Tooltip 被卡片的邊緣切掉了。
**原因**：Tooltip 位於卡片的 DOM 結構內，受到卡片 `overflow: hidden` (這也是一種 Formatting Context 邊界) 的限制。
**解法**：
1. **React/Vue Portals**: 將 Tooltip 渲染到 `<body>` 結尾，使其脫離卡片的 DOM 結構與 Stacking Context。
2. **Anchor Positioning API (Modern)**: 使用新的 CSS Anchor Positioning 讓 Tooltip 邏輯上連結按鈕，但渲染層級獨立。