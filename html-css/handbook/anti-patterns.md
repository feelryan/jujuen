# 常見反模式與陷阱：避免維護惡夢 / Common Anti-Patterns and Pitfalls: Avoiding Maintenance Nightmares

## Mental model｜心智模型

在探討反模式之前，我們必須建立一個核心觀念：**CSS 的本質是「流動」與「繼承」，而非「固定」與「覆蓋」。**

許多維護惡夢（Maintenance Nightmares）源於開發者試圖將網頁視為一張靜態的畫布（Canvas），而非一個動態的媒體。當你發現自己在與瀏覽器的預設行為「打架」時，通常就已經踏入了反模式的領域。

### 脆弱性 vs. 韌性 (Fragility vs. Resilience)

- **脆弱的 CSS (Fragile CSS)**：依賴精確的數值、特定的 DOM 結構或強制的權重覆蓋。只要內容變更、字體載入失敗或螢幕尺寸微調，版面就會崩壞。
- **有韌性的 CSS (Resilient CSS)**：依賴相對關係、語意化結構與自然流動。它能優雅地處理內容溢出（Overflow）或未預期的視窗尺寸。

**The "Debt" Metaphor:**
每一次使用 `!important` 解決樣式衝突，或是寫下一個 `margin-top: -15px` 來微調位置，你都在欠下「技術債」。這些債務會在下一次重構或新增功能時，以指數級的複雜度要求償還。

---

## Patterns & best practices｜常見模式與最佳實務

要消除反模式，必須用正確的模式來替換。以下是針對常見問題的解法：

### 1. 管理權重而非強制覆蓋 (Managing Specificity instead of Forcing)

不要使用 `!important` 來贏得權重戰爭，應建立合理的權重分層。

- **Pattern**: 使用 **BEM (Block Element Modifier)** 或 **CSS Layers (`@layer`)**。
- **Why**: 讓樣式優先級由「架構」決定，而不是由「選擇器的長度」決定。

```css
/* Bad: Trying to override by nesting or !important */
.header .nav ul li a { color: blue; }
a.active { color: red !important; }

/* Good: Low specificity, clear intent (BEM) */
.nav__link { color: blue; }
.nav__link--active { color: red; }
```

### 2. 依賴關係而非魔術數字 (Relationships over Magic Numbers)

避免使用無法解釋的具體數值（Magic Numbers）來排版。

- **Pattern**: 使用 Flexbox/Grid 的對齊功能，或相對單位 (`em`, `rem`, `%`, `ch`)。
- **Why**: `margin-left: 17px` 可能在你的螢幕上剛好置中，但在別人的螢幕上就是歪的。

```css
/* Bad: Magic Number alignment */
.icon {
  position: absolute;
  top: 12px; /* Why 12? What if font size changes? */
  left: 50%;
  margin-left: -10px;
}

/* Good: Contextual alignment */
.button {
  display: inline-flex;
  align-items: center; /* Vertically centered regardless of height */
  justify-content: center;
  gap: 0.5em; /* Space relative to font size */
}
```

### 3. 語意化結構而非 Div Soup (Semantic HTML over Div Soup)

不要為了樣式而增加無意義的 HTML 標籤。

- **Pattern**: 使用 `::before` / `::after` 偽元素進行裝飾，使用 Grid/Flex 減少 wrapper。
- **Why**: 過深的 DOM 樹會影響渲染效能（Reflow cost），且嚴重損害可訪問性（Accessibility）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

以下是四個最致命的 CSS 反模式，請在 Code Review 時嚴格把關。

### 1. The `!important` Addiction (`!important` 成癮症)

濫用 `!important` 會打破 CSS 的 Cascade（層疊）機制，導致後續維護者必須使用更強的 `!important` 來覆蓋，形成惡性循環。

- **識別方式**：在非 Utility class (如 `.u-hidden`) 中看到 `!important`。
- **後果**：無法透過正常的 CSS 選擇器修改樣式，導致樣式表變得不可預測。
- **例外**：
  - **Utility Classes**: `.text-center { text-align: center !important; }` 是可接受的，因為它們的目的是不可變的原子樣式。
  - **Email Templates**: 由於 Email client 的相容性極差，不得不為之。

### 2. Magic Numbers (魔術數字)

魔術數字是指那些「剛好能用」但「不知為何」的數值。

- **常見跡象**：
  - `top: 37px;` (為什麼不是 40 或 50？)
  - `width: 96%;` (為了避開某些 padding？)
  - `z-index: 9999;` (試圖蓋過一切)
- **風險**：當字體大小改變、內容變長或更換字型時，佈局立即破裂。

### 3. Div Soup (Div 湯 / 標籤巢狀地獄)

為了實現某個視覺效果，過度包裹 `<div>`。

```html
<!-- The "Div Soup" Anti-pattern -->
<div class="card-wrapper">
  <div class="card-inner">
    <div class="card-content">
      <div class="card-text">
        Hello
      </div>
    </div>
  </div>
</div>
```

- **修正**：現代 CSS (Flex/Grid) 通常允許我們移除 30-50% 的結構性標籤。
- **陷阱**：許多前端框架（Frameworks）的元件庫容易導致此問題，需謹慎使用。

### 4. Absolute Positioning for Layout (濫用絕對定位排版)

試圖用 `position: absolute` 來建構主要的頁面佈局（如 Sidebar 或 Header），而不是用於小範圍的裝飾或 Overlay。

- **問題**：絕對定位的元素脫離了文檔流（Document Flow）。父元素無法感知其高度，導致內容重疊（Overlapping）或父容器塌陷（Collapse）。
- **正確做法**：主要佈局應使用 Grid 或 Flexbox；`absolute` 僅用於 Dropdown、Tooltip、Badge 或 Modal。

---

## Checklists & workflows｜檢查清單與流程

在提交 PR 或進行 Code Review 時，請使用此清單自我檢查。

### Code Review Checklist

- [ ] **No `!important` outside utilities**: 是否在非工具類別中使用了 `!important`？如果是，能否透過提高選擇器權重或改變 CSS 順序來解決？
- [ ] **No Magic Numbers**: 是否存在無法解釋的像素值（如 `top: 13px`）？能否改用 `flex`, `grid` 或相對單位？
- [ ] **Z-index Management**: 是否使用了 `z-index: 9999`？是否建立了 Stacking Context 或使用 CSS 變數管理層級（如 `var(--z-modal)`）？
- [ ] **Structure Check**: 是否為了排版引入了超過 2 層的純 `div` 包裹？能否使用 `::before/::after` 或 `grid` 簡化？
- [ ] **Flow Check**: 如果刪除某個元素的內容，容器會塌陷嗎？如果內容增加一倍，版面會壞掉嗎？（測試韌性）
- [ ] **Fixed Dimensions**: 是否對含有文字的容器設定了固定高度（`height: 300px`）？應改用 `min-height` 以容納動態內容。

### Debugging Decision Tree (當樣式不如預期時)

1. **是權重問題嗎？** -> 檢查 DevTools 中的樣式是否被劃掉。 -> *Action: 調整選擇器或使用 `@layer`。*
2. **是盒模型問題嗎？** -> 檢查是否有未預期的 `padding` 或 `border` 撐開了寬度。 -> *Action: 確保 `box-sizing: border-box`。*
3. **是定位問題嗎？** -> 元素是否脫離了文檔流（Absolute/Fixed）？ -> *Action: 檢查父層是否有 `position: relative`。*
4. **是堆疊問題嗎？** -> `z-index` 無效？ -> *Action: 檢查是否建立了新的 Stacking Context (如 `opacity < 1`, `transform`, `filter`)。*

---

## Real-world examples｜實戰案例

### Case 1: The "Un-centerable" Modal (絕對定位陷阱)

**Anti-pattern (Fragile):**
開發者試圖用絕對定位和負邊距來置中一個彈窗。這在內容高度改變時會失效。

```css
/* ❌ Bad */
.modal {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 400px;
  height: 300px; /* Fixed height is dangerous */
  margin-top: -150px; /* Magic number dependent on height */
  margin-left: -200px;
}
```

**Best Practice (Resilient):**
使用 `transform` 或 Flexbox，無需知道具體尺寸。

```css
/* ✅ Better (Transform) */
.modal {
  position: absolute; /* or fixed */
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%); /* Dynamic based on own size */
  max-width: 90vw; /* Responsive safety */
  max-height: 90vh;
  overflow: auto;
}

/* ✅ Best (Flexbox/Grid on container) */
.modal-overlay {
  display: grid;
  place-items: center; /* The modern way to center anything */
  position: fixed;
  inset: 0;
}
```

### Case 2: The Specificity War (權重戰爭)

**Anti-pattern:**
為了覆蓋 Sidebar 的樣式，寫出了極長的選擇器。

```css
/* ❌ Bad: Hard to override later */
body #main-container .sidebar ul li a.active {
  color: red;
}
```

**Best Practice:**
降低權重，使用 Class。

```css
/* ✅ Good */
.sidebar-link--active {
  color: red;
}
```

### Case 3: Responsive Breakage (固定寬度陷阱)

**Anti-pattern:**
設定固定寬度導致在手機上出現橫向捲軸。

```css
/* ❌ Bad */
.container {
  width: 1200px;
  margin: 0 auto;
}
```

**Best Practice:**
使用最大寬度。

```css
/* ✅ Good */
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem; /* Prevent touching edges on mobile */
}
```