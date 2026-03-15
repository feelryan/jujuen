# 渲染效能優化與 Core Web Vitals
# Rendering Performance and Core Web Vitals

## 1. 前言與學習目標
## 1. Introduction and Learning Objectives

對於資深工程師而言，HTML 與 CSS 不僅僅是關於佈局與視覺還原，更關乎瀏覽器的渲染機制（Rendering Pipeline）與使用者體驗的核心指標。在高效能需求的應用（如電商首頁、即時儀表板）中，錯誤的 CSS 寫法可能導致 Main Thread 阻塞，進而影響 SEO 排名與轉換率。

For senior engineers, HTML and CSS are not just about layout and visual fidelity; they are deeply tied to the browser's Rendering Pipeline and core user experience metrics. In high-performance applications (such as e-commerce landing pages or real-time dashboards), poor CSS practices can block the Main Thread, negatively impacting SEO rankings and conversion rates.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **深入理解渲染管線（Rendering Pipeline）：** 區分 Reflow（重排）、Repaint（重繪）與 Composite（合成）的差異，並能透過 Chrome DevTools 診斷效能瓶頸。
    **Deeply understand the Rendering Pipeline:** Distinguish between Reflow, Repaint, and Composite, and diagnose performance bottlenecks using Chrome DevTools.
2.  **掌握 Core Web Vitals 優化策略：** 針對 LCP（載入速度）、CLS（視覺穩定性）與 INP（互動延遲）實施具體的 HTML/CSS 優化方案。
    **Master Core Web Vitals optimization strategies:** Implement specific HTML/CSS optimizations for LCP (loading speed), CLS (visual stability), and INP (interaction latency).
3.  **運用現代資源載入技術：** 正確使用 `preload`、`lazy loading`、`content-visibility` 與 GPU 加速技巧來提升頁面回應速度。
    **Apply modern resource loading techniques:** Correctly use `preload`, `lazy loading`, `content-visibility`, and GPU acceleration techniques to improve page responsiveness.

---

## 2. 核心觀念與心智模型
## 2. Core Concepts & Mental Model

### 2.1 像素管線 (The Pixel Pipeline)
### 2.1 The Pixel Pipeline

要優化渲染，必須建立「像素管線」的心智模型。瀏覽器將 HTML/CSS 轉換為螢幕像素的過程大致如下：
To optimize rendering, you must build a mental model of the "Pixel Pipeline." The process by which a browser converts HTML/CSS into pixels on the screen is roughly as follows:

1.  **JavaScript / Style:** 處理 DOM 修改或 CSS 計算。
    **JavaScript / Style:** Handling DOM modifications or CSS calculations.
2.  **Layout (Reflow):** 計算每個元素在螢幕上的幾何位置與大小。這是最昂貴的操作。
    **Layout (Reflow):** Calculating the geometric position and size of each element on the screen. This is the most expensive operation.
3.  **Paint (Repaint):** 填充像素（顏色、陰影、邊框）。
    **Paint (Repaint):** Filling in pixels (colors, shadows, borders).
4.  **Composite:** 將不同的圖層（Layers）在 GPU 中合成並顯示。這是最高效的操作。
    **Composite:** Synthesizing different layers in the GPU for display. This is the most efficient operation.

> **Key Takeaway:** 資深工程師的目標是盡可能讓動畫與互動僅觸發 **Composite** 階段，避免觸發 Layout。
> **Key Takeaway:** The goal for a senior engineer is to ensure animations and interactions trigger only the **Composite** phase, avoiding Layout whenever possible.

### 2.2 Core Web Vitals (CWV)
### 2.2 Core Web Vitals (CWV)

Google 定義的三大核心指標，直接影響 SEO 與使用者體驗：
The three core metrics defined by Google, directly impacting SEO and user experience:

*   **LCP (Largest Contentful Paint):** 視窗內最大內容（通常是 Hero Image 或 H1）渲染完成的時間。目標：< 2.5s。
    **LCP (Largest Contentful Paint):** The time it takes for the largest content element in the viewport (usually a Hero Image or H1) to render. Target: < 2.5s.
*   **CLS (Cumulative Layout Shift):** 頁面載入期間元素意外位移的總和。目標：< 0.1。
    **CLS (Cumulative Layout Shift):** The sum of unexpected layout shifts during page load. Target: < 0.1.
*   **INP (Interaction to Next Paint):** 點擊或鍵盤輸入後，瀏覽器繪製下一幀的延遲時間（取代了舊的 FID）。目標：< 200ms。
    **INP (Interaction to Next Paint):** The latency after a click or keyboard input before the browser paints the next frame (replacing the older FID). Target: < 200ms.

---

## 3. 實務場景與系統設計視角
## 3. Real-World & System Design View

### 3.1 系統架構中的渲染策略
### 3.1 Rendering Strategies in System Architecture

在系統設計面試或架構規劃中，HTML/CSS 的效能優化通常與「內容傳遞策略」綁定：
In system design interviews or architecture planning, HTML/CSS performance optimization is often tied to "content delivery strategies":

*   **Critical Rendering Path (關鍵渲染路徑):**
    為了優化 LCP，我們需要將「首屏渲染所需的 CSS」內聯（Inline Critical CSS）在 HTML `<head>` 中，並延遲載入非關鍵 CSS。這減少了 Render-blocking resources。
    To optimize LCP, we need to inline the "CSS required for first-screen rendering" (Inline Critical CSS) within the HTML `<head>` and defer non-critical CSS. This reduces render-blocking resources.

*   **Image Optimization Strategy (圖片優化策略):**
    系統應自動生成多種格式（WebP/AVIF）與尺寸（`srcset`），並由 CDN 根據 User-Agent 分發。這直接影響 LCP 與頻寬成本。
    The system should automatically generate multiple formats (WebP/AVIF) and sizes (`srcset`), distributed by CDN based on User-Agent. This directly impacts LCP and bandwidth costs.

### 3.2 可觀測性 (Observability)
### 3.2 Observability

在 Production 環境，單靠 Lighthouse 是不夠的。資深工程師會整合 RUM (Real User Monitoring) 工具（如 Sentry, Datadog 或 Google CrUX report）來監控真實使用者的 CWV 數據。
In a production environment, relying solely on Lighthouse is insufficient. Senior engineers integrate RUM (Real User Monitoring) tools (like Sentry, Datadog, or Google CrUX report) to monitor real-world CWV data.

---

## 4. 逐步示例：優化一個新聞列表頁
## 4. Walkthrough: Optimizing a News Feed

### 情境 (Scenario)
### Scenario

我們有一個新聞列表頁面，包含大量的圖片卡片。目前面臨的問題：
1.  **LCP 差:** 首屏圖片載入慢。
2.  **CLS 高:** 圖片載入後會推擠文字，導致頁面跳動。
3.  **Jank (卡頓):** 滑鼠 Hover 卡片時的放大效果不流暢。

We have a news feed page containing numerous image cards. Current issues:
1.  **Poor LCP:** First-screen images load slowly.
2.  **High CLS:** Images push text around after loading, causing layout shifts.
3.  **Jank:** The zoom effect when hovering over cards is stuttery.

### 步驟 1: 解決 CLS (Fixing CLS)
### Step 1: Fixing CLS

**問題:** `<img>` 標籤未指定尺寸，瀏覽器在圖片下載前不知道其高度。
**Problem:** The `<img>` tag lacks dimensions, so the browser doesn't know the height before the image downloads.

**Naive Approach:** 不設定 `width/height`，依賴 CSS `width: 100%`。
**Naive Approach:** Not setting `width/height`, relying on CSS `width: 100%`.

**Solution:** 使用 `aspect-ratio` 或明確設定 HTML 屬性。
**Solution:** Use `aspect-ratio` or explicitly set HTML attributes.

```html
<!-- Better: Browser reserves space immediately -->
<img 
  src="hero.jpg" 
  width="800" 
  height="600" 
  alt="News Hero" 
  style="width: 100%; height: auto; aspect-ratio: 4/3;"
>
```

### 步驟 2: 優化 LCP 與資源載入 (Optimizing LCP & Resource Loading)
### Step 2: Optimizing LCP & Resource Loading

**問題:** 所有圖片同時載入，搶佔頻寬；LCP 圖片優先級不夠高。
**Problem:** All images load simultaneously, competing for bandwidth; the LCP image lacks priority.

**Solution:**
1.  對首屏 LCP 圖片使用 `fetchpriority="high"`。
2.  對非首屏圖片使用 `loading="lazy"`。
3.  使用 `preload` 提示。

**Solution:**
1.  Use `fetchpriority="high"` for the LCP image above the fold.
2.  Use `loading="lazy"` for images below the fold.
3.  Use `preload` hints.

```html
<head>
  <!-- Preload LCP image (Advanced) -->
  <link rel="preload" as="image" href="hero.jpg" fetchpriority="high">
</head>

<body>
  <!-- LCP Element -->
  <img src="hero.jpg" fetchpriority="high" alt="Hero">

  <!-- Below the fold content -->
  <img src="story-2.jpg" loading="lazy" alt="Story 2">
  <img src="story-3.jpg" loading="lazy" alt="Story 3">
</body>
```

### 步驟 3: 高效能動畫 (High Performance Animations)
### Step 3: High Performance Animations

**問題:** 使用 `width`, `height`, `top`, `left` 進行動畫，觸發 Layout (Reflow)。
**Problem:** Animating `width`, `height`, `top`, `left` triggers Layout (Reflow).

**Solution:** 僅對 `transform` 和 `opacity` 進行動畫，並使用 `will-change` 提示瀏覽器提升圖層（Promote Layer）。
**Solution:** Only animate `transform` and `opacity`, and use `will-change` to hint the browser to promote the layer.

```css
/* Anti-pattern: Triggers Layout */
.card:hover {
  top: -10px; /* Expensive! */
  box-shadow: 0 10px 20px rgba(0,0,0,0.2); /* Expensive repaint */
}

/* Optimized: Triggers Composite only */
.card {
  transition: transform 0.3s ease, opacity 0.3s ease;
  /* Hint for GPU rasterization */
  will-change: transform; 
}

.card:hover {
  transform: translateY(-10px) scale(1.02);
}
```

---

## 5. 常見錯誤與反模式
## 5. Common Pitfalls & Anti-patterns

### 5.1 濫用 `will-change`
### 5.1 Overusing `will-change`

*   **錯誤 (Pitfall):** 對大量元素使用 `* { will-change: transform; }` 或在長列表中對每個項目使用。
    **Pitfall:** Using `* { will-change: transform; }` or applying it to every item in a long list.
*   **後果 (Consequence):** 每個 `will-change` 都會強制瀏覽器建立新的 Compositor Layer，這會消耗大量 GPU 記憶體（VRAM），導致行動裝置崩潰或反而變慢。
    **Consequence:** Every `will-change` forces the browser to create a new Compositor Layer, consuming significant GPU memory (VRAM), which can crash mobile devices or paradoxically slow things down.
*   **修正 (Fix):** 僅在即將發生動畫的元素上使用，或透過 JavaScript 動態添加/移除。
    **Fix:** Use it only on elements that are about to animate, or dynamically add/remove it via JavaScript.

### 5.2 `@import` in CSS
### 5.2 `@import` in CSS

*   **錯誤 (Pitfall):** 在 CSS 檔案中使用 `@import url('other.css');`。
    **Pitfall:** Using `@import url('other.css');` inside a CSS file.
*   **後果 (Consequence):** 導致序列化請求（Serial Request Chain）。瀏覽器必須先下載並解析完父 CSS，才知道要去下載子 CSS，嚴重阻塞渲染。
    **Consequence:** Causes a Serial Request Chain. The browser must download and parse the parent CSS before it knows to download the child CSS, severely blocking rendering.
*   **修正 (Fix):** 在 HTML 中使用多個 `<link rel="stylesheet">` 標籤，讓瀏覽器並行下載。
    **Fix:** Use multiple `<link rel="stylesheet">` tags in HTML to allow parallel downloads.

### 5.3 忽略字體載入造成的 CLS
### 5.3 Ignoring CLS caused by Font Loading

*   **錯誤 (Pitfall):** 使用 Web Fonts 但未設定 `font-display`。
    **Pitfall:** Using Web Fonts without setting `font-display`.
*   **後果 (Consequence):** 發生 FOIT (Flash of Invisible Text) 或 FOUT (Flash of Unstyled Text)。當字體載入完成替換 fallback 字體時，文字寬度改變導致佈局位移（CLS）。
    **Consequence:** Occurs FOIT (Flash of Invisible Text) or FOUT (Flash of Unstyled Text). When the font loads and replaces the fallback font, text width changes cause layout shifts (CLS).
*   **修正 (Fix):** 使用 `font-display: swap` 或 `optional`，並盡量匹配 fallback 字體的 metrics (line-height, letter-spacing)。
    **Fix:** Use `font-display: swap` or `optional`, and try to match the metrics (line-height, letter-spacing) of the fallback font.

---

## 6. 面試與實務問答切入點
## 6. Interview & Discussion Hooks

### Q1: 如果一個頁面的 LCP 超過 4 秒，你會如何系統性地分析並優化？
### Q1: If a page has an LCP of over 4 seconds, how would you systematically analyze and optimize it?

*   **高分回答要點 (Key Points):**
    *   **識別 LCP 元素:** 使用 DevTools Performance 面板確認哪個元素觸發了 LCP。
    *   **分析四個階段:** Time to First Byte (TTFB), Resource Load Delay, Resource Load Time, Element Render Delay。
    *   **提出對策:**
        *   如果是 TTFB 慢 -> 優化 CDN、Cache 或 Server 響應。
        *   如果是 Load Delay -> 使用 `preload` 或 `fetchpriority="high"`。
        *   如果是 Render Delay -> 移除 Render-blocking JavaScript/CSS，確保字體快速載入。

### Q2: 解釋 `content-visibility: auto` 的作用及其適用場景。
### Q2: Explain the purpose of `content-visibility: auto` and its use cases.

*   **高分回答要點 (Key Points):**
    *   它允許瀏覽器跳過「視窗外（off-screen）」內容的渲染工作（Layout & Paint），直到使用者捲動到該區域。
    *   這類似於圖片的 lazy loading，但是針對整個 DOM 子樹。
    *   **適用場景:** 長列表、無限捲動頁面、複雜的 Footer。
    *   **注意:** 需搭配 `contain-intrinsic-size` 設定佔位高度，以避免捲動條跳動。

### Q3: 為什麼 CSS 動畫通常比 JavaScript 動畫（如 jQuery `animate`）效能更好？
### Q3: Why are CSS animations generally more performant than JavaScript animations (like jQuery `animate`)?

*   **高分回答要點 (Key Points):**
    *   **Main Thread vs Compositor Thread:** JS 執行在 Main Thread，容易被其他腳本阻塞。CSS 動畫（特別是 transform/opacity）可以卸載到 Compositor Thread 處理。
    *   **GPU 加速:** CSS 能更輕易地觸發硬體加速。
    *   **瀏覽器優化:** 瀏覽器可以優化 CSS 動畫的幀率，甚至在分頁不可見時暫停以省電。

---

## 7. 小結與後續延伸
## 7. Summary & Next Steps

### 重點摘要 (Key Takeaways)
1.  **Pixel Pipeline:** 牢記 JavaScript -> Style -> Layout -> Paint -> Composite。優化的核心是減少 Layout 與 Paint。
2.  **Core Web Vitals:** LCP 關注載入速度，CLS 關注穩定性，INP 關注互動延遲。
3.  **GPU Layers:** 使用 `transform` 和 `opacity` 進行動畫，利用 `will-change` 進行適度提示，避開 Main Thread。
4.  **Resource Hints:** 善用 `preload`、`lazy`、`fetchpriority` 來控制瀏覽器的資源載入優先級。
5.  **Layout Stability:** 總是為圖片和影片保留空間（Aspect Ratio），避免佈局位移。

### 後續延伸 (Next Steps)
*   **Advanced Layouts:** 深入研究 CSS Grid 與 Subgrid 的效能影響（Chapter 07）。
*   **Accessibility (A11y):** 效能優化不應犧牲可訪問性，例如 `content-visibility` 對螢幕閱讀器的影響。
*   **Web Workers:** 學習如何將繁重的 JS 計算移出 Main Thread，進一步優化 INP。