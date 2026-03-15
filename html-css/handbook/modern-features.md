# 現代 CSS 特性：Container Queries、Layers 與 :has() / Modern CSS Features: Container Queries, Layers, and :has()

## Mental model｜心智模型

要掌握這些現代特性，你需要調整對 CSS 運作方式的根本認知。這不僅僅是新語法，而是對「響應式」、「權重」與「選擇器邏輯」的典範轉移。

To master these modern features, you need to shift your fundamental understanding of how CSS works. These aren't just new syntax; they are paradigm shifts in "Responsiveness", "Specificity", and "Selector Logic".

### 1. Container Queries: 從「頁面感知」轉向「自我感知」
**From "Page-Aware" to "Self-Aware"**

- **Old Model (Media Queries):** 元件問：「現在視窗 (Viewport) 有多寬？」這導致了依賴全域上下文的脆弱元件。
- **New Model (Container Queries):** 元件問：「**我的容器**給了我多少空間？」
- **核心概念**：將響應式邏輯封裝在元件內部。一個 Card 元件無論被放在 Sidebar (窄) 還是 Main Content (寬)，都能自動切換佈局，而不需要外部的 class 修改。

### 2. Cascade Layers: 從「駭客式權重戰」轉向「分層架構」
**From "Specificity Wars" to "Layered Architecture"**

- **Old Model:** 為了覆蓋樣式，我們依賴更長的選擇器 (e.g., `.nav .item.active`) 或 `!important`。這是一場軍備競賽。
- **New Model:** 想像 Photoshop 的圖層。上層圖層的樣式永遠覆蓋下層，**無論下層的選擇器權重有多高**。
- **核心概念**：權重管理變成了「架構決策」，而非「語法技巧」。你可以明確定義 `Framework` 層與 `Custom` 層的優先級。

### 3. :has(): CSS 的「If/Then」邏輯
**The "If/Then" Logic of CSS**

- **Old Model:** CSS 是由上而下的瀑布流。你只能根據父層選取子層，無法回頭影響父層或兄弟層。
- **New Model:** `:has()` 讓 CSS 具備了「向後看 (Lookahead)」的能力。
- **核心概念**：把它當作 **Conditional Styling**。如果元件包含 X 狀態，則改變元件的外觀。這消除了許多原本需要 JavaScript toggle class 的場景。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 元件級別響應式 (Component-Level Responsiveness)

不要再為每個元件寫 Media Queries。建立一個標準的 Container Query 模式。

**Pattern: The "Fluid Switch" / 流體切換模式**

```css
/* 定義容器 */
.card-container {
  container-type: inline-size;
  container-name: card;
}

/* 元件樣式 */
.card {
  display: flex;
  flex-direction: column;
}

/* 當容器寬度大於 400px 時，切換為水平佈局 */
@container card (min-width: 400px) {
  .card {
    flex-direction: row;
    align-items: center;
  }
}
```

### 2. 3rd Party Reset Strategy (第三方套件重置策略)

使用 `@layer` 來管理第三方 CSS (如 Bootstrap, Tailwind 插件) 與你自己的 Reset/Base 樣式，確保你的 Override 永遠有效且不需要高權重。

**Best Practice: Layer Ordering / 圖層順序定義**

```css
/* 在 CSS 檔案最頂端定義順序 */
@layer reset, framework, components, utilities;

/* 導入第三方庫到較低優先級的層 */
@import url('bootstrap.css') layer(framework);

/* 你的重置樣式 */
@layer reset {
  * { box-sizing: border-box; }
}

/* 你的元件樣式 - 即使選擇器權重低，也能覆蓋 framework */
@layer components {
  .btn-primary {
    background: blue; /* Wins over Bootstrap's .btn-primary */
  }
}
```

### 3. 狀態驅動樣式 (State-Driven Styling with :has)

使用 `:has()` 來處理複雜的 UI 互動反饋，減少對 JS 的依賴。

**Pattern: Interactive Form Validation / 互動式表單驗證**

```css
/* 當 Group 內的 input 有效且非空時，為 Label 加上打勾圖示 */
.form-group:has(input:valid:not(:placeholder-shown)) label::after {
  content: '✓';
  color: green;
}

/* 當 Group 內的 input 有錯誤時，將整個 Group 變紅 */
.form-group:has(input:invalid) {
  border-color: red;
  animation: shake 0.3s;
}
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 濫用 Container Queries 於全域佈局
**Overusing CQ for Global Layouts**
- **Anti-pattern:** 在最外層的 `<body>` 或 `<main>` 設定 `container-type` 來取代所有的 Media Queries。
- **Why:** Container Queries 有微小的效能成本，且對於「視窗級別」的變更（如切換 Mobile/Desktop 導覽列），Media Queries 仍然是語意上更正確且效能更好的選擇。
- **Correction:** 宏觀佈局 (Macro Layout) 用 Media Queries；微觀元件 (Micro Components) 用 Container Queries。

### 2. 忘記 Unlayered Styles 的優先權
**Forgetting Unlayered Styles Priority**
- **Pitfall:** 認為定義了 `@layer` 就能控制一切，卻發現某些沒寫在 layer 裡的舊 CSS 依然覆蓋了你的設定。
- **Rule:** **未分層的樣式 (Unlayered Styles) 擁有最高優先級**。這設計是為了讓舊代碼在漸進式遷移時不會壞掉。
- **Fix:** 盡快將所有樣式歸類到 Layers 中，或者確保你的 Override 寫在 Unlayered 區域（但不建議長期這樣做）。

### 3. :has() 的效能陷阱
**Performance Risks with :has()**
- **Pitfall:** 寫出過於寬泛的查詢，例如 `body:has(.active)`。
- **Why:** 這會迫使瀏覽器在任何 `.active` 變動時重新評估整個 `body` 的樣式，可能導致 Style Recalculation 變慢。
- **Fix:** 盡量縮小 `:has()` 的作用範圍，例如 `.card:has(.checkbox:checked)`。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: 該用哪種 Query?
- **Q1: 這個樣式變化是因為「視窗大小」改變了嗎？(e.g., 手機版隱藏側欄)**
  - Yes -> Use **Media Query**.
- **Q2: 這個樣式變化是因為元件被放在「不同寬度的區塊」中嗎？(e.g., Card 在側欄 vs 主內容)**
  - Yes -> Use **Container Query**.

### Workflow: 導入 Cascade Layers 到現有專案
1. **Audit:** 盤點專案中的 CSS 來源（Reset, Frameworks, Design System, Custom Styles）。
2. **Define:** 在入口文件 (e.g., `main.css`) 頂部定義 Layer 順序：
   `@layer reset, base, theme, components, utilities, overrides;`
3. **Migrate (Low Risk):** 先將 Reset 和第三方庫移入對應 Layer。
4. **Migrate (High Risk):** 逐步將 Custom Components 移入 Layer。
   *注意：移入 Layer 後權重會降低，需檢查是否被 Unlayered Styles 覆蓋。*

### Checklist: 實作檢查
- [ ] **Container Context:** 確保使用 CQ 的元件，其父層或祖先層已設定 `container-type` (通常是 `inline-size`)。
- [ ] **Fallback:** 針對不支援 `:has()` 或 `@container` 的舊瀏覽器，是否有提供基礎樣式 (Progressive Enhancement)？
- [ ] **Layer Order:** 檢查 `@layer` 聲明是否在任何 `@import` 或樣式規則之前。
- [ ] **Scoping:** `:has()` 的選擇器是否足夠具體，避免全頁重繪？

---

## Real-world examples｜實戰案例

### Scenario 1: The "Smart" Article Component (Container Queries)
**情境**：一個新聞卡片元件。在首頁列表中它是窄卡片（圖上文下）；在精選文章區塊它是寬卡片（左圖右文）；在側邊欄推薦中它是極簡模式（無圖）。

```css
.article-card-wrapper {
  container-type: inline-size;
}

.article-card {
  display: grid;
  gap: 1rem;
  /* Default: Minimal (Sidebar) */
  grid-template-columns: 1fr;
}

.article-image { display: none; }

/* Mid-size: Standard Card */
@container (min-width: 300px) {
  .article-image { display: block; height: 200px; object-fit: cover; }
}

/* Large-size: Featured Layout */
@container (min-width: 600px) {
  .article-card {
    grid-template-columns: 2fr 3fr; /* Left Image, Right Content */
    align-items: center;
  }
  .article-image { height: 100%; }
}
```

### Scenario 2: Legacy Project Rescue (Layers)
**情境**：你需要維護一個充滿 `!important` 的舊專案，並且需要引入一個新的 Design System，但不想被舊樣式干擾。

```css
/* main.css */
@layer legacy, new-system;

/* 將舊的 CSS 全部丟進 legacy 層 */
@import url('old-spaghetti-code.css') layer(legacy);

/* 你的新系統在 new-system 層 */
@layer new-system {
  .button {
    background: var(--primary-color);
    /* 不需要 !important，因為 new-system 層級高於 legacy */
  }
}
```

### Scenario 3: Pure CSS Modal Logic (:has)
**情境**：防止 Modal 開啟時背景捲動，以往需要 JS 在 `body` 上 toggle `overflow: hidden`。現在可以用 CSS 解決。

```css
/* 當任何地方有一個開啟的 modal (假設是用 open attribute) */
body:has(dialog[open]),
body:has(.modal.is-open) {
  overflow: hidden;
  padding-right: var(--scrollbar-width); /* 防止佈局跳動 */
}
```