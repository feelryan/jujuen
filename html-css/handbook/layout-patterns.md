# 實戰佈局模式：從置中對齊到響應式網格 / Practical Layout Patterns: From Centering to Responsive Grids

## Mental model｜心智模型

在現代 CSS 佈局中，最關鍵的心智轉變是從「像素推移 (Pixel Pushing)」轉向「定義約束與關係 (Defining Constraints & Relationships)」。網頁不是一張固定的 PDF，而是一種流動的媒介。

To master modern CSS layout, the critical mental shift is moving from "Pixel Pushing" to "Defining Constraints & Relationships." The web is not a fixed PDF; it is a fluid medium.

### 1. 1D vs. 2D Context (Flexbox vs. Grid)
- **Flexbox (1D - One Dimensional):** 想像成一串珠子或一條流動的線。它關注的是**內容流向 (Flow)**。當你需要讓元素在「一條軸線」上排列（即使它們換行了，本質上還是線性的延伸）時使用。
  - *Analogy:* Like a string of beads. Focuses on **content flow**. Use it when elements need to align along a single axis.
- **Grid (2D - Two Dimensional):** 想像成一張藍圖或棋盤。它關注的是**區域劃分 (Placement)**。當你需要同時控制行與列，或者需要精確地將元素放置在特定區域時使用。
  - *Analogy:* Like a blueprint or chessboard. Focuses on **area placement**. Use it when you need to control both rows and columns simultaneously.

### 2. Intrinsic Web Design (內在網頁設計)
不再總是依賴 Media Queries (`@media`) 來改變佈局，而是利用 CSS 的內在能力（如 `flex-wrap`, `minmax`, `auto-fit`）讓佈局根據可用空間自動適應。
Instead of relying solely on Media Queries to change layouts, leverage the intrinsic capabilities of CSS (like `flex-wrap`, `minmax`, `auto-fit`) to let the layout adapt automatically based on available space.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. The Super Center (終極置中)
這是面試必考題，也是最常用的模式。不再需要 `transform` 或負 margin 的 hack。

The classic interview question and the most used pattern. No more `transform` or negative margin hacks.

```css
/* Grid Approach (Most concise) */
.center-container {
  display: grid;
  place-items: center; /* Shorthand for align-items & justify-items */
  min-height: 100vh;
}

/* Flexbox Approach (Better if you need to control individual children later) */
.center-container-flex {
  display: flex;
  justify-content: center;
  align-items: center;
}
```

### 2. The RAM Pattern (Responsive Auto-fit Minmax)
不需要 Media Queries 就能實現響應式卡片網格。這是 Grid 最強大的實戰應用之一。
Responsive card grids without Media Queries. This is one of the most powerful real-world applications of CSS Grid.

- **R**epeat: 重複軌道。
- **A**uto-fit: 自動填滿剩餘空間（如果卡片不夠多，不會留下巨大空白）。
- **M**inmax: 定義最小寬度與最大彈性。

```css
.card-grid {
  display: grid;
  gap: 1rem;
  /* 只要空間允許，每列至少 250px，剩餘空間平分 (1fr) */
  /* As long as space permits, columns are at least 250px, splitting remaining space (1fr) */
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
}
```

### 3. The Holy Grail (Grid Areas)
傳統的 Header-Sidebar-Content-Footer 佈局。使用 `grid-template-areas` 讓 CSS 程式碼像 ASCII Art 一樣直觀，極易維護。
The classic layout. Using `grid-template-areas` makes your CSS look like ASCII art, making it incredibly intuitive and maintainable.

```css
.app-shell {
  display: grid;
  grid-template-columns: 250px 1fr; /* Sidebar fixed, content fluid */
  grid-template-rows: auto 1fr auto; /* Header/Footer auto, content fills space */
  grid-template-areas: 
    "header header"
    "sidebar content"
    "footer footer";
  min-height: 100vh;
}

.header { grid-area: header; }
.sidebar { grid-area: sidebar; }
/* ... etc */

@media (max-width: 768px) {
  .app-shell {
    grid-template-columns: 1fr;
    grid-template-areas: 
      "header"
      "content"
      "sidebar"
      "footer";
  }
}
```

### 4. The Sidebar Layout (With Flexbox)
當側邊欄寬度固定，主內容自適應時，Flexbox 依然是一個輕量級的好選擇。
When the sidebar is fixed width and the main content is adaptive, Flexbox remains a lightweight and solid choice.

```css
.sidebar-layout {
  display: flex;
  flex-wrap: wrap; /* Allows stacking on mobile */
  gap: 1rem;
}

.sidebar {
  flex-basis: 20rem; /* Target width */
  flex-grow: 1;      /* Grow to fill if needed */
}

.content {
  flex-basis: 0;
  flex-grow: 999;    /* Dominates the space calculation */
  min-width: 50%;    /* Breakpoint trigger: wraps when container is narrow */
}
```

### 5. The Stack (Vertical Rhythm)
避免在每個元件上寫 `margin-bottom`。使用父層容器控制垂直間距。
Avoid writing `margin-bottom` on every component. Use the parent container to control vertical spacing.

```css
.stack {
  display: flex;
  flex-direction: column;
  gap: 1.5rem; /* Consistent spacing between all children */
}
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Magic Numbers & Fixed Dimensions (魔術數字與固定尺寸)
- **Anti-pattern:** `width: 960px;` or `height: 400px;`
- **Why:** 這是破壞響應式設計的元兇。內容溢出或在小螢幕上出現橫向卷軸。
- **Fix:** 使用 `max-width`, `min-height`, `fr` 單位或百分比。讓內容決定高度，讓容器限制最大寬度。
- **Fix:** Use `max-width`, `min-height`, `fr` units, or percentages. Let content dictate height; let containers constrain max width.

### 2. Margin for Layout (用 Margin 做佈局)
- **Anti-pattern:** 使用 `margin-left: 20px` 來推擠元素以達到排列效果。
- **Why:** Margin 應該只用於元素間的「推擠」，而不是「定位」。這會導致佈局脆弱，一旦內容變動就會崩壞。
- **Fix:** 使用 Flexbox/Grid 的 `gap`, `justify-content`, `align-items`。

### 3. Absolute Positioning Everything (濫用絕對定位)
- **Anti-pattern:** 使用 `position: absolute` 來排版整個頁面的區塊。
- **Why:** 這將元素移出了文檔流 (Document Flow)，導致父容器塌陷 (collapse)，且無法自動適應內容高度。
- **Fix:** 僅在需要「重疊」或「脫離流」的微小 UI（如 Badge, Modal close button）使用 Absolute。

### 4. Flexbox for 2D Grids (強行用 Flexbox 做二維網格)
- **Anti-pattern:** 在 Flexbox 容器上使用 `width: 33%` 並期待它完美對齊最後一行的卡片（特別是當最後一行只有一個元素時，它不會對齊左邊，而是置中或分散）。
- **Why:** Flexbox 不知道「列 (Row)」的概念，它只知道換行。
- **Fix:** 這種情況請直接使用 CSS Grid。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Flexbox or Grid?
在開始寫 code 之前，請先問自己：

1. **我需要控制單一維度（行或列）還是雙維度？**
   - 單一維度 (1D) → **Flexbox** (e.g., Navbar, Tag list, Breadcrumbs)
   - 雙維度 (2D) → **Grid** (e.g., Photo gallery, Dashboard layout, Page skeleton)
2. **我是「內容優先」還是「佈局優先」？**
   - 讓內容決定大小 → **Flexbox**
   - 嚴格限制佈局區域大小 → **Grid**

### Implementation Checklist
- [ ] **Overflow Safety:** 當內容文字變長（例如切換成德文）時，佈局會崩壞嗎？是否設定了 `min-width: 0` 來防止 Flex/Grid item 撐爆容器？
- [ ] **Scrollbars:** 是否意外出現了橫向卷軸？（檢查 `100vw` 是否造成了問題，通常 `100%` 更安全）。
- [ ] **Gap Management:** 是否使用了 `gap` 屬性而不是在子元素上寫 `margin`？
- [ ] **Semantic Structure:** 佈局是否依賴了過多的 `<div>` 嵌套？能否利用 Grid 的特性減少 HTML 結構？
- [ ] **Mobile First:** 預設樣式是否能在手機上正常顯示（通常是 `block` 或 `flex-column`），再透過 `min-width` media query 加入複雜佈局？

---

## Real-world examples｜實戰案例

### Example 1: The "Split Screen" Login Page (Grid)
常見的登入頁面：左側是滿版圖片，右側是置中的登入表單。
A common login page: Full-height image on the left, centered login form on the right.

```css
.login-page {
  display: grid;
  /* Mobile: 1 col, Desktop: 2 cols (image takes 55%, form takes rest) */
  grid-template-columns: 1fr; 
  min-height: 100vh;
}

.branding-image {
  display: none; /* Hidden on mobile */
  background: url('hero.jpg') center/cover;
}

.login-form-container {
  display: grid;
  place-items: center; /* Center the form content */
  padding: 2rem;
}

@media (min-width: 768px) {
  .login-page {
    grid-template-columns: 55fr 45fr; /* Using fr for ratio */
  }
  .branding-image {
    display: block;
  }
}
```

### Example 2: Navigation Bar with "Auto" Margin (Flexbox)
經典導航列：Logo 在左，選單在右。
Classic Navbar: Logo on the left, links on the right.

```css
.navbar {
  display: flex;
  align-items: center; /* Vertically center */
  gap: 1rem;
  padding: 1rem;
}

.logo {
  font-weight: bold;
}

.nav-links {
  /* This is the magic trick */
  /* margin-left: auto pushes this element to the far right */
  margin-left: auto; 
  
  display: flex;
  gap: 1rem;
}
```

### Example 3: Imbalanced Grid (Magazine Layout)
模擬雜誌排版，第一篇文章特別大，其餘較小。
Simulating a magazine layout where the first article is featured, and others are smaller.

```css
.news-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

/* The first item spans 2 columns and 2 rows */
.news-card:first-child {
  grid-column: span 2;
  grid-row: span 2;
}

/* Fallback for smaller screens to prevent overflow */
@media (max-width: 650px) {
  .news-card:first-child {
    grid-column: span 1;
    grid-row: span 1;
  }
}
```