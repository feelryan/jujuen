# 1. 前言與學習目標 (Introduction & Learning Goals)

作為資深工程師，我們不再只是撰寫 UI 元件，更多時候我們是在做「架構決策」。在現代 React 生態系中，渲染模式（Rendering Patterns）的選擇直接決定了系統的效能（Performance）、SEO 表現、基礎設施成本（Infrastructure Cost）以及使用者體驗（UX）。

As senior engineers, we are no longer just writing UI components; more often, we are making "architectural decisions." In the modern React ecosystem, the choice of Rendering Patterns directly dictates system Performance, SEO results, Infrastructure Cost, and User Experience (UX).

完成本章後，你將能夠：

1.  **精準評估架構權衡（Evaluate Architectural Trade-offs）：** 在 CSR、SSR、SSG、ISR 與 RSC 之間，根據業務需求（如資料即時性 vs. 載入速度）做出最佳選擇。
2.  **掌握 React Server Components (RSC)：** 理解 RSC 與傳統 SSR 的本質區別，以及它如何解決 "Waterfall Request" 與 Bundle Size 問題。
3.  **應用於系統設計面試（Apply to System Design Interviews）：** 在設計如 News Feed、E-commerce 或 Dashboard 系統時，能提出混合式渲染策略並解釋其對 CDN 與 Database 的影響。
4.  **理解 Streaming 架構：** 明白如何利用 Streaming SSR 優化 TTFB (Time to First Byte) 並提升感知效能。

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

要掌握渲染模式，我們需要建立一個關於「運算發生在哪裡（Where computation happens）」與「資料何時準備好（When data is ready）」的心智模型。

To master rendering patterns, we need to establish a mental model regarding "Where computation happens" and "When data is ready."

### 2.1 渲染光譜 (The Rendering Spectrum)

我們可以將渲染視為一個光譜，從完全在客戶端到完全在伺服器端：

We can view rendering as a spectrum, ranging from purely client-side to purely server-side:

1.  **CSR (Client-Side Rendering):**
    *   **定義：** 瀏覽器下載空的 HTML 與巨大的 JS bundle，然後在客戶端執行 React 構建 DOM。
    *   **類比：** 像是收到一盒 IKEA 傢俱組件（JS），客人（Browser）必須自己組裝才能使用。
    *   **Definition:** The browser downloads an empty HTML and a large JS bundle, then executes React on the client to build the DOM.
    *   **Analogy:** Like receiving a box of IKEA furniture parts (JS); the guest (Browser) must assemble it themselves before use.

2.  **SSR (Server-Side Rendering):**
    *   **定義：** 伺服器在 `request time` 產生完整的 HTML。瀏覽器先顯示內容，隨後 JS 下載並執行 Hydration（注水）使頁面可互動。
    *   **類比：** 像是收到已經組裝好的傢俱，但上面的抽屜（互動功能）要等潤滑油乾了（Hydration）才能拉開。
    *   **Definition:** The server generates full HTML at `request time`. The browser displays content first, then JS downloads and performs Hydration to make the page interactive.
    *   **Analogy:** Like receiving pre-assembled furniture, but the drawers (interactive features) can only be opened after the lubricant dries (Hydration).

3.  **SSG (Static Site Generation) / ISR (Incremental Static Regeneration):**
    *   **定義：** 在 `build time` (SSG) 或背景排程 (ISR) 產生 HTML。
    *   **類比：** 工廠大量生產好的型錄，直接發送給所有人，內容是固定的（直到下次印刷）。
    *   **Definition:** HTML is generated at `build time` (SSG) or via background scheduling (ISR).
    *   **Analogy:** Mass-produced catalogs sent directly to everyone; the content is fixed (until the next print run).

4.  **RSC (React Server Components):**
    *   **定義：** 元件邏輯**僅**在伺服器執行，回傳序列化格式（Serialized Format）給 Client，不包含該元件的 library code。
    *   **差異：** SSR 回傳 HTML；RSC 回傳「UI 的描述數據」。RSC 可以與 Client Components 混合使用。
    *   **Definition:** Component logic executes **only** on the server, returning a Serialized Format to the Client, excluding the component's library code.
    *   **Distinction:** SSR returns HTML; RSC returns "data describing the UI." RSC can be intermixed with Client Components.

### 2.2 關鍵指標對照 (Key Metrics Comparison)

| Pattern | TTFB (Time to First Byte) | FCP (First Contentful Paint) | TTI (Time to Interactive) | SEO | Server Cost |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CSR** | Fast (Static HTML) | Slow (Wait for JS) | Slow | Poor | Low (CDN) |
| **SSR** | Slow (Server Logic) | Fast | Moderate (Wait for Hydration) | Excellent | High |
| **SSG** | Fastest | Fastest | Fast | Excellent | Lowest |
| **RSC** | Moderate | Fast | Fast (Less JS to hydrate) | Excellent | Moderate |

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在系統設計面試或架構規劃中，單純討論 React 語法是不夠的。我們必須將視角拉高到 **Infrastructure** 層級。

In system design interviews or architectural planning, discussing React syntax alone is insufficient. We must elevate our perspective to the **Infrastructure** level.

### 3.1 混合架構策略 (Hybrid Architecture Strategy)

現代大型應用（如 Next.js App Router）通常採用混合模式。

Modern large-scale applications (like Next.js App Router) often adopt a hybrid model.

*   **Marketing / Landing Pages:** 使用 **SSG** 或 **ISR**。這些頁面讀多寫少，需要極致的載入速度與 SEO。內容存放在 CDN 邊緣節點（Edge）。
*   **User Dashboard / Settings:** 使用 **CSR** 或 **RSC**。這些是高度私有、動態的內容，SEO 不重要，重點是互動性。
*   **Product Listing / News Feed:** 使用 **SSR** 搭配 **Streaming**。需要 SEO 且資料變動頻繁，利用 Streaming 讓使用者先看到 Header/Skeleton，不用等 Database 查詢全部完成。

*   **Marketing / Landing Pages:** Use **SSG** or **ISR**. These are read-heavy, write-rarely pages requiring extreme load speed and SEO. Content lives on CDN Edge nodes.
*   **User Dashboard / Settings:** Use **CSR** or **RSC**. These are highly private, dynamic contents where SEO is irrelevant, and interactivity is key.
*   **Product Listing / News Feed:** Use **SSR** with **Streaming**. Requires SEO and data changes frequently. Streaming allows users to see Header/Skeleton first without waiting for all Database queries to finish.

### 3.2 RSC 對系統設計的影響 (Impact of RSC on System Design)

引入 React Server Components 後，系統邊界發生了變化：

With the introduction of React Server Components, system boundaries have shifted:

1.  **Backend for Frontend (BFF) 的消融：** 傳統上我們可能需要一個 API Gateway 或 BFF 來聚合資料給前端。使用 RSC，Server Components 本身就充當了 BFF 的角色，直接在 Server 存取 DB 或 Microservices。
2.  **Data Fetching 移至 Server：** 解決了 CSR 常見的 "Network Waterfall" 問題。瀏覽器不再需要發送多個 API 請求（User -> Posts -> Comments），而是一個 RSC 請求就回傳組裝好的 UI 樹。
3.  **Bundle Size 優化：** 龐大的日期處理庫（如 `moment.js` 或 `date-fns`）如果在 RSC 中使用，不會被打包進 Client Bundle，顯著降低 TTI。

1.  **Dissolution of Backend for Frontend (BFF):** Traditionally, we might need an API Gateway or BFF to aggregate data for the frontend. With RSC, Server Components themselves act as the BFF, accessing DBs or Microservices directly on the server.
2.  **Data Fetching moves to Server:** Solves the common "Network Waterfall" in CSR. The browser no longer needs to send multiple API requests (User -> Posts -> Comments); instead, a single RSC request returns the assembled UI tree.
3.  **Bundle Size Optimization:** Heavy libraries (like `moment.js` or `date-fns`), if used in RSC, are not bundled into the Client Bundle, significantly reducing TTI.

---

# 4. 逐步示例 (Walkthrough / Example)

讓我們以設計一個 **「高流量電商產品頁面 (High-Traffic E-commerce Product Page)」** 為例，探討從 Naive 到 Mature 的演進。

Let's use the design of a **"High-Traffic E-commerce Product Page"** as an example to explore the evolution from Naive to Mature solutions.

### 4.1 階段一：純 CSR (The Naive Approach)

```javascript
// ProductPage.jsx (Client Component)
function ProductPage({ id }) {
  const [product, setProduct] = useState(null);
  
  useEffect(() => {
    // Fetch data after component mounts
    fetch(`/api/products/${id}`).then(data => setProduct(data));
  }, [id]);

  if (!product) return <Spinner />;
  return <div>{product.name}</div>;
}
```

*   **問題 (Issues):**
    *   SEO 差（爬蟲可能只看到 Spinner）。
    *   Waterfall：下載 JS -> 執行 JS -> 發送 API -> 等待回應 -> 渲染。
    *   **Issues:** Poor SEO (crawlers might only see the Spinner). Waterfall: Download JS -> Execute JS -> Send API -> Wait for response -> Render.

### 4.2 階段二：SSR (Standard SSR)

將資料獲取移至 `getServerSideProps` (Next.js Pages Router) 或 `async` Component (App Router)。

Move data fetching to `getServerSideProps` (Next.js Pages Router) or an `async` Component (App Router).

*   **改善 (Improvements):** SEO 解決了，FCP 變快。
*   **新瓶頸 (New Bottleneck):** 如果 Database 回應慢（例如庫存查詢耗時 2秒），使用者會看到白畫面 2秒（TTFB 延遲）。Server 負載隨流量線性增加。
*   **Improvements:** SEO solved, FCP is faster.
*   **New Bottleneck:** If the Database is slow (e.g., inventory check takes 2s), the user sees a white screen for 2s (TTFB latency). Server load increases linearly with traffic.

### 4.3 階段三：RSC + Streaming + ISR (The Mature Solution)

這是資深工程師應採用的架構。我們將頁面拆解：

This is the architecture a senior engineer should adopt. We decompose the page:

1.  **靜態資訊 (Static Info):** 產品名稱、描述、圖片。使用 **ISR** (快取 1 分鐘)。
2.  **動態資訊 (Dynamic Info):** 個人化推薦、即時庫存、購物車狀態。使用 **RSC with Streaming**。

```tsx
// app/product/[id]/page.tsx (Server Component by default)
import { Suspense } from 'react';
import { getProductDetails } from '@/lib/db';
import Reviews from '@/components/Reviews';
import AddToCart from '@/components/AddToCart'; // Client Component

// 1. Static/Cached Data (ISR-like behavior via fetch cache)
async function ProductDetails({ id }) {
  const product = await getProductDetails(id); 
  return (
    <article>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      {/* 3. Client Component for interactivity */}
      <AddToCart productId={id} /> 
    </article>
  );
}

export default async function Page({ params }) {
  return (
    <div className="product-layout">
      {/* Main content loads fast (cached) */}
      <ProductDetails id={params.id} />

      {/* 2. Streaming: Slow data doesn't block the whole page */}
      <Suspense fallback={<div className="shimmer">Loading Reviews...</div>}>
        <Reviews productId={params.id} />
      </Suspense>
    </div>
  );
}
```

*   **架構分析 (Architecture Analysis):**
    *   **TTFB:** 極快，因為 `ProductDetails` 可以被 Cache。
    *   **Streaming:** `Reviews` 查詢較慢，但不會阻塞 `ProductDetails` 的 HTML 傳輸。使用者先看到產品，評論區顯示 Loading 骨架屏。
    *   **Interaction:** `AddToCart` 是唯一的 Client Component，保持 JS bundle 最小。
    *   **TTFB:** Extremely fast because `ProductDetails` can be cached.
    *   **Streaming:** `Reviews` query is slow but doesn't block the HTML transmission of `ProductDetails`. Users see the product first; the reviews section shows a loading skeleton.
    *   **Interaction:** `AddToCart` is the only Client Component, keeping the JS bundle minimal.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 濫用 "use client" (Overusing "use client")

*   **錯誤 (Mistake):** 在 Page 的最頂層直接加上 `"use client"`，導致整個路由及其子元件全部變成 Client Rendering。
*   **後果 (Consequence):** 失去了 RSC 帶來的 Bundle Size 優勢與 Server Data Fetching 優勢。
*   **修正 (Fix):** 將 Client Component 推向樹的末端（Leaf nodes）。只在需要 `useState`, `useEffect` 或瀏覽器事件的地方使用它。
*   **Mistake:** Adding `"use client"` at the very top of the Page, causing the entire route and its children to become Client Rendered.
*   **Consequence:** Losing the Bundle Size benefits and Server Data Fetching advantages of RSC.
*   **Fix:** Push Client Components to the leaf nodes of the tree. Only use it where `useState`, `useEffect`, or browser events are needed.

### 5.2 忽略 Hydration Mismatch (Ignoring Hydration Mismatch)

*   **錯誤 (Mistake):** 在 Render 過程中使用隨機數（`Math.random()`）或時間（`new Date()`）導致 Server HTML 與 Client 初次 Render 不一致。
*   **後果 (Consequence):** React 會丟棄 Server HTML 並重新渲染，導致效能懲罰與畫面閃爍。
*   **修正 (Fix):** 確保 Server 與 Client 的初始輸出一致。若需依賴瀏覽器特定數據（如 `window.innerWidth`），請在 `useEffect` 中執行。
*   **Mistake:** Using random numbers (`Math.random()`) or time (`new Date()`) during render, causing inconsistency between Server HTML and Client initial render.
*   **Consequence:** React discards the Server HTML and re-renders, causing performance penalties and layout shift.
*   **Fix:** Ensure initial output matches between Server and Client. If browser-specific data (like `window.innerWidth`) is needed, execute it inside `useEffect`.

### 5.3 瀑布式請求 (Waterfall Requests in Components)

*   **錯誤 (Mistake):** 在巢狀元件中各自 `await` 資料，沒有使用 `Promise.all` 或並行 Data Fetching。
*   **後果 (Consequence):** 總載入時間 = Component A 時間 + Component B 時間。
*   **修正 (Fix):** 在 Parent 層級並行 Fetch 資料，或是利用 RSC 的非阻塞特性（但需注意 `await` 的順序）。
*   **Mistake:** Nested components each `await`ing data without using `Promise.all` or parallel Data Fetching.
*   **Consequence:** Total load time = Component A time + Component B time.
*   **Fix:** Fetch data in parallel at the Parent level, or leverage RSC's non-blocking nature (while being mindful of `await` order).

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 在設計一個類似 Twitter/X 的 Feed 系統時，你會如何選擇渲染模式？
**How would you choose the rendering pattern when designing a Feed system like Twitter/X?**

*   **高分回答要點 (Key Points):**
    *   **App Shell:** 使用 SSR 或 SSG 快速渲染外框（Sidebar, Header）。
    *   **Feed Content:** 這是高度動態且無限滾動的。
        *   **Initial Load:** 可以用 SSR 帶出前 10 則貼文（為了 FCP）。
        *   **Pagination:** 後續載入必須是 CSR（Client-side fetching）。
    *   **RSC 應用:** 如果使用 Next.js，可以用 RSC 獲取初始 Feed，並利用 Server Action 處理「按讚/轉推」，減少 Client JS 邏輯。
    *   **Cache:** Feed 本身很難 Cache（每人不同），但個別 Tweet 元件可以做 Fragment Caching（如果架構支援）。

### Q2: 請解釋 RSC (React Server Components) 與 SSR 的區別，以及它們如何共存？
**Please explain the difference between RSC and SSR, and how they coexist.**

*   **高分回答要點 (Key Points):**
    *   **Output:** SSR 輸出 HTML；RSC 輸出特殊的 JSON-like 序列化格式。
    *   **Execution:** SSR 的元件代碼最終會發送到瀏覽器進行 Hydration；RSC 的代碼**永遠**留在 Server（除非它引用了 Client Component）。
    *   **Coexistence:** 它們是互補的。在 Next.js 中，RSC 先在 Server 執行產生 Virtual DOM 結構，然後這個結構被傳遞給 SSR 引擎產生 HTML。瀏覽器收到 HTML 後，再根據 RSC 的指示進行 Hydration（只針對 Client Component 部分）。

### Q3: 什麼是 Streaming SSR？它解決了什麼問題？
**What is Streaming SSR? What problem does it solve?**

*   **高分回答要點 (Key Points):**
    *   **Problem:** 傳統 SSR 是 "All or Nothing"。Server 必須等所有 API 回來才能送出 HTML。
    *   **Solution:** 利用 HTTP 的 Chunked Transfer Encoding。React 可以先送出靜態 Shell，遇到需要長時間 Fetch 的部分（包在 `<Suspense>` 裡），先送一個 Placeholder。等資料好了，再送出剩下的 HTML script 把 Placeholder 替換掉。
    *   **Benefit:** 顯著降低 TTFB，提升使用者的感知速度。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)

1.  **CSR** 適合高互動、SEO 不敏感的 Dashboard；**SSG/ISR** 適合內容靜態的行銷頁面；**SSR/RSC** 適合動態且需 SEO 的應用。
2.  **RSC (React Server Components)** 是將後端邏輯與前端 UI 融合的架構變革，能顯著減少 Bundle Size 並消除 Client-side Waterfalls。
3.  **Streaming** 是現代 SSR 的標配，它解耦了「慢資料」與「快頁面」的依賴關係。
4.  **Hydration** 是 SSR 的成本所在，盡量減少 Client Components 的數量與大小。
5.  系統設計時，將 **Caching** 策略（CDN vs Server Cache）與渲染模式一併考慮。

### 後續延伸 (Next Steps)

*   **實作：** 使用 Next.js App Router 重構一個既有的 CSR 頁面，體驗 RSC 與 Streaming 的實作細節。
*   **閱讀：** 深入研究 React 18+ 的 `Suspense` 機制與 Concurrent Features。
*   **下一章預告：** **Chapter 07: State Management Patterns (Context, Redux, Zustand, Server State)** — 探討在 RSC 架構下，狀態管理如何從 Client Global Store 轉向 Server State (React Query / Server Actions)。