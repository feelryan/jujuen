# 渲染效能優化：減少重繪、重排與改善 Core Web Vitals / Rendering Performance Optimization: Reducing Repaints, Reflows, and Improving Core Web Vitals

## Mental model｜心智模型

要掌握渲染效能，必須理解瀏覽器的 **Pixel Pipeline（像素管線）**。當你改變 CSS 時，瀏覽器並不是「直接」畫出結果，而是經過一系列步驟。

To master rendering performance, you must understand the browser's **Pixel Pipeline**. When you change CSS, the browser doesn't just "draw" the result; it goes through a sequence of steps.

### 1. The Pipeline Hierarchy (管線層級)
想像你在裝修房子，成本由高到低分別是：

1.  **Layout (Reflow / 重排)**：**「拆牆與移動隔間」**。
    *   當你改變元素的幾何屬性（`width`, `height`, `left`, `top`, `margin`）時，瀏覽器必須重新計算該元素及其受影響之子元素、兄弟元素在頁面上的位置與大小。這是最昂貴的操作。
    *   *Analogy: Moving walls. Expensive and affects the structural integrity of the whole house.*
2.  **Paint (Repaint / 重繪)**：**「重新粉刷牆壁」**。
    *   當你改變外觀但不改變幾何形狀（`color`, `background`, `box-shadow`）時，瀏覽器需要重新繪製像素，但不需要重新計算位置。成本中等。
    *   *Analogy: Painting walls. Moderate cost, doesn't change the layout.*
3.  **Composite (合成)**：**「用 Photoshop 圖層疊加」**。
    *   瀏覽器將頁面拆分成不同的圖層（Layers）。當你改變 `transform` 或 `opacity` 時，瀏覽器只需在 GPU 中合成這些現有的圖層。這是最快、最省效能的操作。
    *   *Analogy: Stacking layers in Photoshop. Very cheap and handled by the GPU.*

### 2. Core Web Vitals Connection
*   **LCP (Largest Contentful Paint)**：主要受 **Critical CSS** 載入速度與渲染阻塞（Render Blocking）影響。
*   **CLS (Cumulative Layout Shift)**：主要受 **Layout (Reflow)** 影響。如果圖片或廣告在載入後才撐開空間，就會發生位移。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Animation Strategy: Stick to Composite-Only Properties
**動畫策略：堅守合成層屬性**

在製作動畫或轉場時，盡量只使用 `transform` 和 `opacity`。

*   **Do:** Use `transform: translate()` for movement and `transform: scale()` for resizing.
*   **Don't:** Animate `top`, `left`, `width`, `height`, or `margin`.

```css
/* ✅ Efficient: Handled by GPU, no layout recalculation */
.menu.open {
  transform: translateX(0);
  opacity: 1;
}

/* ❌ Expensive: Triggers Layout (Reflow) on every frame */
.menu.open {
  left: 0;
  display: block; /* Cannot animate display, but often toggled causing jumps */
}
```

### 2. Preventing CLS: Reserve Space
**預留空間以防止佈局位移**

瀏覽器在下載完圖片或 Web Fonts 之前不知道它們的大小，這會導致內容「跳動」。

*   **Aspect Ratio:** Always set `width` and `height` attributes on `<img>` or use CSS `aspect-ratio`.
*   **Font Loading:** Use `font-display: optional` or `swap` (with care) to handle text rendering phases.

```css
/* ✅ Modern approach for responsive images/containers */
.card-image {
  width: 100%;
  aspect-ratio: 16 / 9; /* Reserves space immediately */
  object-fit: cover;
}
```

### 3. Optimizing LCP: Critical CSS
**關鍵 CSS 優化**

為了加速 LCP，應將「首屏（Above-the-fold）」所需的 CSS 內聯（Inline）在 HTML `<head>` 中，並延遲載入其餘 CSS。

*   **Pattern:** Extract Critical CSS -> Inline in HTML -> Load full CSS asynchronously.
*   **Tools:** Use tools like `critical`, `penthouse`, or Next.js/Nuxt built-in features.

### 4. Rendering Hints: `content-visibility` & `will-change`
**渲染提示屬性**

*   **`content-visibility: auto`**：告訴瀏覽器「如果這個元素不在螢幕上，就不要花算力去渲染它」。這對長列表（Long lists）或複雜的 Footer 非常有效。
*   **`will-change`**：提前告訴瀏覽器哪個屬性會變動，讓瀏覽器預先分配 GPU 資源。

```css
/* ✅ Great for long feeds or heavy off-screen sections */
.heavy-section {
  content-visibility: auto;
  contain-intrinsic-size: 1000px; /* Estimated height to prevent scrollbar jumping */
}

/* ✅ Use sparingly for elements about to animate */
.modal {
  will-change: transform, opacity;
}
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The `will-change` Abuse
**濫用 `will-change`**

*   **Pitfall:** Applying `will-change: all` or adding it to too many elements.
*   **Consequence:** Excessive memory usage. The browser creates a new layer for each element, consuming GPU memory and potentially crashing mobile browsers.
*   **Correction:** Only apply it to elements that are actively animating or about to animate.

### 2. Layout Thrashing (Forced Synchronous Layout)
**佈局抖動（強制同步佈局）**

雖然這是 JS 行為，但往往源於 CSS 屬性的讀取。當你在一個 Frame 內「先寫入樣式，再讀取佈局屬性（如 `offsetHeight`）」，瀏覽器被迫立即執行 Reflow 以回傳正確數值。

*   **Anti-pattern:**
    ```javascript
    // ❌ Reads and writes interleaved in a loop
    boxes.forEach(box => {
      box.style.width = '100px'; // Write (Invalidates layout)
      console.log(box.offsetWidth); // Read (Forces layout recalculation immediately)
    });
    ```

### 3. Animating `box-shadow`
**對 `box-shadow` 進行動畫**

*   **Pitfall:** Animating `box-shadow` creates heavy paint costs because the shadow needs to be recalculated and repainted on every frame.
*   **Workaround:** Use a pseudo-element (`::after`) with the shadow and animate its `opacity`.

---

## Checklists & workflows｜檢查清單與流程

### Performance Review Checklist (效能審查清單)

- [ ] **CLS Check:** Do all images and video elements have explicit `width`, `height`, or `aspect-ratio`?
- [ ] **CLS Check:** Are ads or dynamic content containers given a fixed `min-height` to prevent collapse?
- [ ] **Animation Check:** Are all continuous animations (loops, transitions) using only `transform` and `opacity`?
- [ ] **LCP Check:** Is the LCP element (e.g., hero image) prioritized? (Not lazy-loaded, possibly preloaded).
- [ ] **Code Review:** Are we using `will-change` only where necessary (and removing it when done)?
- [ ] **Font Loading:** Is `font-display` configured to avoid FOIT (Flash of Invisible Text) causing layout shifts?

### Debugging Workflow (除錯流程)

1.  **Identify:** Use Chrome DevTools **Performance** tab. Look for red triangles (Layout Thrashing) or long green bars (Painting).
2.  **Visualize:** Turn on **Rendering** drawer in DevTools:
    *   Enable "Layout Shift Regions" (to see CLS).
    *   Enable "Paint Flashing" (to see what gets repainted).
3.  **Verify:** Use [CSSTriggers.com](https://csstriggers.com/) to check if the property you are animating triggers Layout, Paint, or just Composite.

---

## Real-world examples｜實戰案例

### Example 1: Optimizing a "Card Hover" Effect
**案例一：優化卡片懸停效果**

**Bad Practice (Triggers Layout & Paint):**
改變 `top` 和 `box-shadow` 會導致重排與重繪，在低階手機上會卡頓。

```css
.card {
  top: 0;
  transition: top 0.3s, box-shadow 0.3s;
}
.card:hover {
  top: -10px; /* ❌ Triggers Layout */
  box-shadow: 0 10px 20px rgba(0,0,0,0.2); /* ❌ Triggers Paint */
}
```

**Best Practice (Composite Only):**
使用 `transform` 移動位置，並用偽元素處理陰影的透明度。

```css
.card {
  transform: translateY(0);
  transition: transform 0.3s;
  position: relative;
}

/* Pre-render the shadow on a pseudo-element */
.card::after {
  content: '';
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  box-shadow: 0 10px 20px rgba(0,0,0,0.2);
  opacity: 0; /* Hidden by default */
  transition: opacity 0.3s;
  z-index: -1;
}

.card:hover {
  transform: translateY(-10px); /* ✅ Composite only */
}

.card:hover::after {
  opacity: 1; /* ✅ Composite only */
}
```

### Example 2: Handling Dynamic Content (CLS)
**案例二：處理動態內容導致的位移**

常見於新聞網站或電商列表，API 資料回來前高度為 0，回來後撐開頁面。

**Before (Unstable):**
```html
<div class="ad-container">
  <!-- Content injected by JS later -->
</div>
```

**After (Stable):**
使用 `min-height` 或 `aspect-ratio` 佔位。

```css
.ad-container {
  min-height: 250px; /* ✅ Reserves space for the standard ad unit */
  background-color: #f0f0f0; /* Optional: Skeleton placeholder color */
  display: flex;
  align-items: center;
  justify-content: center;
}
```

### Example 3: Improving Long List Rendering
**案例三：改善長列表渲染**

當頁面有數千個 DOM 節點時（例如無限捲動的 Feed），渲染成本極高。

```css
/* Apply to the container of each post/item */
.feed-item {
  /* ✅ Skips rendering work for items off-screen */
  content-visibility: auto;
  
  /* ✅ Crucial: Tells browser the approximate size so scrollbar doesn't jump */
  contain-intrinsic-size: 500px; 
}
```