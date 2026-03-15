# 安全性、錯誤處理與 A11y / Security, Error Handling & Accessibility

這不是「行有餘力才做」的選修課，而是區分「玩具專案」與「生產級應用」的關鍵分水嶺。React 雖然在安全性上提供了預設防護，但錯誤處理與無障礙性 (Accessibility/A11y) 仍高度依賴開發者的自覺與架構設計。

## Mental model｜心智模型

### 1. 安全性：免疫系統 vs. 開放傷口
React 的 JSX 預設會對所有插入的變數進行 Escaping（轉義），這就像人體的**免疫系統**，自動過濾掉大部分的 XSS 攻擊。
然而，當你使用 `dangerouslySetInnerHTML` 時，等同於在皮膚上劃開一道**開放傷口**，繞過了 React 的防護機制。如果沒有經過消毒（Sanitization），細菌（惡意腳本）就會長驅直入。

### 2. 錯誤處理：防撞潰縮區 (Crumple Zones)
不要試圖讓應用程式「永遠不發生錯誤」，而是要設計良好的**潰縮區**。
在汽車設計中，潰縮區是為了在撞擊時吸收能量，保護乘客艙。在 React 中，**Error Boundaries** 就是潰縮區。當某個組件（例如一個複雜的圖表）崩潰時，它應該只影響該區塊（顯示「無法載入圖表」），而不是讓整台車（整個 SPA 頁面）爆炸變成白屏 (White Screen of Death)。

### 3. A11y：路緣坡 (Curb Cuts)
無障礙設計常被誤解為「只為盲人設計」。請想像人行道的**路緣坡**：它最初是為了輪椅使用者設計的，但推嬰兒車的父母、拉行李箱的旅客、送貨員都深受其惠。
語意化的 HTML 與鍵盤導航支援，不僅幫助螢幕閱讀器使用者，也能提升 SEO、讓 Power User 操作更順手，並使程式碼更具可讀性。

---

## Patterns & best practices｜常見模式與最佳實務

### Security Patterns

1.  **Sanitize before `dangerouslySetInnerHTML`**
    永遠假設後端傳來的 HTML 字串是不安全的。使用 `DOMPurify` 進行清洗。
    ```jsx
    import DOMPurify from 'dompurify';

    const SafeContent = ({ htmlContent }) => {
      // ✅ Best Practice: Sanitize content before rendering
      const cleanHtml = DOMPurify.sanitize(htmlContent);
      return <div dangerouslySetInnerHTML={{ __html: cleanHtml }} />;
    };
    ```

2.  **Safe Links (Rel="noopener noreferrer")**
    當使用 `target="_blank"` 開啟外部連結時，務必加上 `rel="noopener noreferrer"`，防止新分頁透過 `window.opener` 操控原頁面（Reverse Tabnabbing）。

### Error Handling Patterns

1.  **Component-Level Error Boundaries**
    使用 `react-error-boundary` 函式庫（比手寫 Class Component 更現代化）來包裹易碎的組件。
    ```jsx
    import { ErrorBoundary } from 'react-error-boundary';

    function ErrorFallback({ error, resetErrorBoundary }) {
      return (
        <div role="alert">
          <p>Something went wrong:</p>
          <pre>{error.message}</pre>
          <button onClick={resetErrorBoundary}>Try again</button>
        </div>
      );
    }

    // ✅ Usage: Wrap specific features, not just the root
    <ErrorBoundary FallbackComponent={ErrorFallback} onReset={() => { /* reset state */ }}>
      <ComplexWidget />
    </ErrorBoundary>
    ```

2.  **Handling Async Errors in Hooks**
    Error Boundaries **無法** 捕捉 Event Handlers 或 `useEffect` 中的非同步錯誤。你需要手動 Catch 並傳遞給 Boundary。
    ```jsx
    import { useErrorBoundary } from 'react-error-boundary';

    function MyComponent() {
      const { showBoundary } = useErrorBoundary();

      useEffect(() => {
        fetchData().catch((error) => {
          // ✅ Manually trigger the nearest Error Boundary
          showBoundary(error);
        });
      }, []);
      
      return <div>...</div>;
    }
    ```

### Accessibility (A11y) Patterns

1.  **Semantic HTML First**
    不要用 `<div onClick={...}>` 來製作按鈕。
    *   **Button**: 用於執行動作（送出、打開 Modal）。使用 `<button type="button">`。
    *   **Link**: 用於導航（換頁）。使用 `<a>` 或 `<Link>`。

2.  **Visually Hidden for Screen Readers**
    有些按鈕只有 icon（例如 🔍），視覺上不需要文字，但螢幕閱讀器需要。
    ```jsx
    // ✅ Pattern: Accessible Icon Button
    <button type="button" className="icon-btn">
      <span className="sr-only">Search</span> {/* CSS class to hide visually but keep for screen readers */}
      <SearchIcon aria-hidden="true" />
    </button>
    ```

3.  **Focus Management**
    當打開 Modal 時，焦點應該鎖定在 Modal 內；關閉後，焦點應回到原本觸發按鈕上。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 🚫 Security Pitfalls
*   **直接渲染 User Input**：永遠不要把 URL 參數或 User Input 直接放入 `href` 或 `src` 屬性中，這可能導致 `javascript:` 偽協議攻擊。
    *   *Bad:* `<a href={userInput}>Click me</a>` (如果 userInput 是 `javascript:alert(1)`)
*   **依賴 Client-side Validation**：前端驗證只是為了 UX，後端必須再次驗證所有數據。前端防護可以輕易被 `curl` 或 Postman 繞過。

### 🚫 Error Handling Pitfalls
*   **全域只有一個 Error Boundary**：如果在 App 根目錄只有一個 Boundary，任何小錯誤都會導致整個應用程式崩潰並顯示錯誤頁面，使用者體驗極差。
*   **Swallowing Errors**：在 `catch` 區塊中什麼都不做，或者只 `console.log` 而不通知使用者或監控系統（如 Sentry）。這會讓 Bug 難以追蹤。

### 🚫 A11y Pitfalls
*   **`outline: none`**：在 CSS 中全域移除 focus ring (`*:focus { outline: none; }`)。這會讓鍵盤使用者完全迷失方向。如果覺得預設醜，請用 `box-shadow` 自訂樣式，但**絕不能移除**。
*   **濫用 ARIA**：`No ARIA is better than bad ARIA`。如果你用了正確的 HTML5 標籤（如 `<button>`），通常不需要 `role="button"`。只有在迫不得已使用非語意標籤時才加上 ARIA。

---

## Checklists & workflows｜檢查清單與流程

在 Code Review 或發布前，請對照以下清單：

### Security Checklist
- [ ] **No `dangerouslySetInnerHTML`**：除非絕對必要且已使用 `DOMPurify` 清洗。
- [ ] **Dependencies Audit**：執行 `npm audit` 確保沒有高風險依賴。
- [ ] **Sensitive Data**：確保沒有將 API Keys、Secrets 或 PII（個人識別資訊）寫死在前端程式碼或存入 LocalStorage。
- [ ] **Links**：所有 `target="_blank"` 的連結都加上了 `rel="noopener noreferrer"`。

### Error Handling Checklist
- [ ] **Boundaries Strategy**：關鍵功能區塊（Widgets, Page Content）是否有獨立的 Error Boundary？
- [ ] **Fallback UI**：錯誤畫面是否提供「重試 (Retry)」按鈕？
- [ ] **Async Errors**：`useEffect` 和 Event Handlers 中的 Promise 是否有 `.catch()` 處理？
- [ ] **Logging**：錯誤是否已串接至監控服務（如 Sentry, LogRocket）？

### A11y Checklist
- [ ] **Keyboard Navigation**：拋開滑鼠，只用 `Tab`、`Enter`、`Space`、`Esc` 能否順利操作整個功能？
- [ ] **Semantic Elements**：按鈕是 `<button>`，連結是 `<a>`，輸入框有對應的 `<label>`。
- [ ] **Alt Text**：所有圖片都有 `alt` 屬性（裝飾性圖片設為 `alt=""`）。
- [ ] **Contrast**：文字與背景對比度是否符合 WCAG AA 標準（可用 Chrome DevTools 檢查）。
- [ ] **Linter**：專案是否已啟用 `eslint-plugin-jsx-a11y` 並修正所有警告？

---

## Real-world examples｜實戰案例

### 案例 1：優雅降級的 Dashboard (Error Handling)

**情境**：一個儀表板頁面包含三個區塊：使用者資訊、銷售圖表、最新通知。
**問題**：銷售圖表的 API 掛了，回傳 500。
**錯誤做法**：沒有 Error Boundary，導致整個 Dashboard 白屏，使用者連「最新通知」都看不到。
**正確做法**：

```jsx
// Dashboard.jsx
const Dashboard = () => {
  return (
    <main>
      <UserProfile />
      
      {/* 只有圖表區塊會顯示錯誤訊息，其他部分正常運作 */}
      <ErrorBoundary 
        FallbackComponent={ChartErrorFallback}
        onReset={() => reloadChartData()}
      >
        <SalesChart />
      </ErrorBoundary>

      <Notifications />
    </main>
  );
};
```

### 案例 2：自定義 Modal 的 A11y 實作

**情境**：設計一個自定義的彈出視窗。
**A11y 需求實作**：
1.  **Role**：外層 `div` 設為 `role="dialog"` 和 `aria-modal="true"`。
2.  **Label**：加上 `aria-labelledby="modal-title"` 指向標題 ID。
3.  **Focus Trap**：當 Modal 開啟時，按 `Tab` 鍵焦點只能在 Modal 內循環，不能跑到背景頁面（通常使用 `react-focus-lock`）。
4.  **Escape to Close**：監聽 `keydown` 事件，按 `Esc` 觸發關閉。
5.  **Restore Focus**：關閉時，焦點自動回到「開啟 Modal」的那個按鈕上。

### 案例 3：防範 XSS 的 Markdown 渲染器

**情境**：部落格系統允許使用者輸入 Markdown。
**風險**：使用者輸入 `[Click me](javascript:stealCookies())`。
**解決方案**：

```jsx
import { marked } from 'marked';
import DOMPurify from 'dompurify';

const MarkdownRenderer = ({ content }) => {
  // 1. Convert Markdown to HTML
  const rawHtml = marked.parse(content);
  
  // 2. Sanitize HTML (移除 script tags, onclick handlers, javascript: hrefs)
  const cleanHtml = DOMPurify.sanitize(rawHtml);

  // 3. Render safely
  return <div dangerouslySetInnerHTML={{ __html: cleanHtml }} />;
};
```