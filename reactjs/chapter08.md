# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，寫出「能跑的程式碼」只是基本功，真正的挑戰在於如何確保應用程式在生產環境（Production）中具備高可用性、安全性與可觀測性。React 雖然在開發體驗上提供了很多便利，但在面對真實世界的網路環境、惡意攻擊與非預期錯誤時，仍需額外的架構設計來支撐。
For a Senior Software Engineer, writing "working code" is merely the baseline. The real challenge lies in ensuring high availability, security, and observability in a production environment. While React offers excellent developer experience, it requires additional architectural design to withstand real-world network conditions, malicious attacks, and unexpected runtime errors.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **設計強健的錯誤處理機制 (Design Robust Error Handling):** 實作階層式的 Error Boundaries，確保單一組件崩潰不會導致整個應用程式白屏（White Screen of Death）。
    Implement hierarchical Error Boundaries to ensure that a single component crash does not lead to a White Screen of Death (WSOD) for the entire application.
2.  **防禦常見安全性漏洞 (Defend Against Security Vulnerabilities):** 深入理解 React 的 XSS 防護機制及其侷限性，並正確處理 `dangerouslySetInnerHTML` 與使用者輸入。
    Deeply understand React's XSS protection mechanisms and their limitations, and correctly handle `dangerouslySetInnerHTML` and user inputs.
3.  **建立可觀測性體系 (Establish Observability):** 整合 Logging 與 Monitoring 工具（如 Sentry, Datadog），並掌握 Source Maps 在生產環境的正確配置策略。
    Integrate Logging and Monitoring tools (e.g., Sentry, Datadog) and master the correct configuration strategy for Source Maps in production.
4.  **應對 Concurrent Mode 的副作用 (Handle Concurrent Mode Side Effects):** 識別並修復在 React Concurrent Features 下可能導致狀態不一致或重複提交的 Race Conditions。
    Identify and fix race conditions that may lead to state inconsistencies or duplicate submissions under React Concurrent Features.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 錯誤邊界作為「防撞區」 (Error Boundaries as "Crumple Zones")

在傳統的命令式編程中，我們習慣用 `try-catch` 包裹邏輯。但在 React 的宣告式渲染樹中，某個子組件在 Render Phase 的錯誤若未被捕獲，會導致整個 React Tree 卸載（Unmount）。
In traditional imperative programming, we are used to wrapping logic with `try-catch`. However, in React's declarative render tree, an uncaptured error in a child component during the Render Phase will cause the entire React Tree to unmount.

**心智模型：** 將 Error Boundary 想像成汽車的「防撞區（Crumple Zone）」。當撞擊（錯誤）發生時，只有局部區域會毀損（顯示 Fallback UI），而駕駛艙（App 的其餘部分）仍保持完整與運作。
**Mental Model:** Think of an Error Boundary as a car's "Crumple Zone." When an impact (error) occurs, only the local area is damaged (showing Fallback UI), while the cabin (the rest of the App) remains intact and functional.

**注意：** Error Boundaries **無法** 捕獲 Event Handlers、非同步程式碼（`setTimeout`, `requestAnimationFrame`）、SSR 錯誤以及 Error Boundary 自身內部的錯誤。這些仍需傳統的 `try-catch` 處理。
**Note:** Error Boundaries **cannot** catch errors in Event Handlers, asynchronous code (`setTimeout`, `requestAnimationFrame`), SSR errors, or errors within the Error Boundary itself. These still require traditional `try-catch` handling.

## 2.2 安全性：預設跳脫與例外 (Security: Default Escaping & Exceptions)

React 在渲染時預設會對內容進行跳脫（Escaping），這防範了大部分的 XSS（跨站腳本攻擊）。然而，資深工程師必須知道「後門」在哪裡。
React escapes content by default during rendering, which prevents most XSS (Cross-Site Scripting) attacks. However, a Senior Engineer must know where the "backdoors" are.

*   **`dangerouslySetInnerHTML`**: 這是 React 顯式告訴你「我知道自己在做危險操作」的 API。
    **`dangerouslySetInnerHTML`**: This is React's API explicitly telling you, "I know I am doing something dangerous."
*   **Props Injection**: 攻擊者可能透過控制 props（如 `<a href={userInput}>`）注入 `javascript:alert(1)`，這是 React 預設防護無法覆蓋的盲點。
    **Props Injection**: Attackers might inject `javascript:alert(1)` by controlling props (e.g., `<a href={userInput}>`), a blind spot not covered by React's default protection.

## 2.3 可觀測性：黑盒與透視 (Observability: Black Box vs. Transparency)

在生產環境中，React App 是一個在使用者瀏覽器中運行的黑盒。當用戶回報「壞掉了」，若沒有遙測數據（Telemetry），你將無從下手。
In production, a React App is a black box running in the user's browser. When a user reports "it's broken," you are helpless without telemetry data.

**核心概念：** 必須將前端視為分散式系統的一個節點。你需要收集：
**Core Concept:** Treat the frontend as a node in a distributed system. You need to collect:
1.  **Context**: 發生錯誤時的 State、Props 與 User Action。
    **Context**: State, Props, and User Action at the time of the error.
2.  **Environment**: 瀏覽器版本、OS、Viewport 大小。
    **Environment**: Browser version, OS, Viewport size.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 系統架構中的容錯設計 (Fault Tolerance in System Architecture)

在大型單頁應用（SPA）設計中，我們通常採用「分層隔離」策略：
In large Single Page Application (SPA) design, we typically adopt a "Layered Isolation" strategy:

1.  **Global Boundary**: 位於 `App` 根部。捕獲災難性錯誤，顯示「系統維護中」或「請重新整理」頁面，避免白屏。
    **Global Boundary**: Located at the `App` root. Catches catastrophic errors, displaying a "System Maintenance" or "Please Refresh" page to avoid WSOD.
2.  **Feature/Page Boundary**: 位於路由（Router）或主要功能區塊層級。例如，側邊欄壞了不應影響主內容區的操作。
    **Feature/Page Boundary**: Located at the Router or main feature block level. For example, a broken sidebar should not affect the operation of the main content area.
3.  **Widget Boundary**: 用於高風險或第三方組件（如複雜的圖表、外部嵌入內容）。
    **Widget Boundary**: Used for high-risk or third-party components (e.g., complex charts, external embedded content).

## 3.2 安全性與 CSP (Security & CSP)

僅依賴 React 的防護是不夠的。在系統設計層面，必須配合 **Content Security Policy (CSP)** HTTP Header。
Relying solely on React's protection is insufficient. At the system design level, it must be paired with **Content Security Policy (CSP)** HTTP Headers.

*   **Strict CSP**: 禁止 `unsafe-inline` 與 `unsafe-eval`。這會影響某些依賴動態 script 的 CSS-in-JS 庫或舊版工具，選型時需考慮。
    **Strict CSP**: Disallow `unsafe-inline` and `unsafe-eval`. This affects certain CSS-in-JS libraries or legacy tools that rely on dynamic scripts; consider this during technology selection.
*   **Sanitization Pipeline**: 所有使用者產生的 HTML 內容（如 Rich Text Editor 輸出）在存入 DB 前或渲染前，必須經過 `DOMPurify` 等庫的清洗。
    **Sanitization Pipeline**: All user-generated HTML content (e.g., Rich Text Editor output) must be sanitized via libraries like `DOMPurify` before being stored in the DB or rendered.

## 3.3 Source Maps 與除錯 (Source Maps & Debugging)

**Trade-off**: Source Maps 對除錯至關重要，但公開完整的 Source Maps 會暴露原始碼結構，甚至包含敏感註解或邏輯。
**Trade-off**: Source Maps are crucial for debugging, but exposing full Source Maps reveals source code structure, potentially including sensitive comments or logic.

**Best Practice**: 在 Build 階段生成 Source Maps，但**不要**部署到公開的 Web Server。而是將其上傳至監控服務（如 Sentry），並在 CI/CD 流程結束後刪除或限制存取。
**Best Practice**: Generate Source Maps during the Build phase, but **do not** deploy them to the public Web Server. Instead, upload them to a monitoring service (like Sentry) and delete or restrict access after the CI/CD pipeline finishes.

---

# 4. 逐步示例 (Walkthrough / Example)

## 案例：構建具備監控與安全防護的 Widget (Building a Monitored & Secure Widget)

### 背景 (Context)
我們有一個顯示使用者評論的組件 `ReviewWidget`。評論內容包含 HTML（由 Markdown 轉換而來）。我們需要確保：
1. 若渲染失敗，不影響頁面其他部分。
2. 渲染失敗時，自動發送報告至監控系統。
3. 防止 XSS 攻擊。

We have a component `ReviewWidget` that displays user reviews. The content contains HTML (converted from Markdown). We need to ensure:
1. If rendering fails, the rest of the page is unaffected.
2. When rendering fails, a report is automatically sent to the monitoring system.
3. XSS attacks are prevented.

### Step 1: 實作可觀測的 Error Boundary (Implementing an Observable Error Boundary)

目前 React 的 Error Boundary 必須是 Class Component。
Currently, React Error Boundaries must be Class Components.

```javascript
import React from 'react';
import * as Sentry from '@sentry/react'; // 假設使用 Sentry

class ObservableErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    // 更新 state 以便下一次渲染顯示 fallback UI
    // Update state so the next render shows the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // 1. Log error to logging service
    console.error("Uncaught error:", error, errorInfo);
    
    // 2. Send context to Sentry
    Sentry.withScope((scope) => {
      scope.setExtras(errorInfo);
      Sentry.captureException(error);
    });
  }

  render() {
    if (this.state.hasError) {
      // 可以接受自定義 Fallback，或使用預設
      // Can accept a custom Fallback, or use a default
      return this.props.fallback || (
        <div className="p-4 border border-red-500 bg-red-50 rounded">
          <h3>Something went wrong.</h3>
          <button onClick={() => window.location.reload()}>Reload</button>
        </div>
      );
    }

    return this.props.children; 
  }
}
```

### Step 2: 安全的 HTML 渲染組件 (Secure HTML Rendering Component)

使用 `dompurify` 來清洗 HTML，防止 XSS。
Use `dompurify` to sanitize HTML and prevent XSS.

```javascript
import DOMPurify from 'dompurify';

const SafeHTML = ({ htmlContent }) => {
  // Config: 禁止 SVG 與 MathML 以減少攻擊面，並強制所有連結開新視窗
  // Config: Forbid SVG and MathML to reduce attack surface, force all links to open in new window
  const sanitizedContent = DOMPurify.sanitize(htmlContent, {
    USE_PROFILES: { html: true },
    FORBID_TAGS: ['style', 'script'],
    ADD_ATTR: ['target'], 
  });
  
  // Hook to ensure links open in new tab securely (noopener noreferrer)
  DOMPurify.addHook('afterSanitizeAttributes', function (node) {
    if ('target' in node) {
      node.setAttribute('target', '_blank');
      node.setAttribute('rel', 'noopener noreferrer');
    }
  });

  return (
    <div 
      className="prose"
      dangerouslySetInnerHTML={{ __html: sanitizedContent }} 
    />
  );
};
```

### Step 3: 整合使用 (Integration)

```javascript
const ReviewWidget = ({ rawMarkdown }) => {
  // 假設 convertMarkdownToHtml 是一個工具函數
  // Assume convertMarkdownToHtml is a utility function
  const html = convertMarkdownToHtml(rawMarkdown);

  return (
    <ObservableErrorBoundary fallback={<div>Review temporarily unavailable</div>}>
      <SafeHTML htmlContent={html} />
    </ObservableErrorBoundary>
  );
};
```

**分析 (Analysis):**
*   **可靠性 (Reliability):** `ObservableErrorBoundary` 隔離了錯誤。
*   **可觀測性 (Observability):** `componentDidCatch` 提供了錯誤堆疊與組件樹資訊給 Sentry。
*   **安全性 (Security):** `DOMPurify` 移除了潛在的惡意腳本，且 `noopener noreferrer` 防止了 Reverse Tabnabbing 攻擊。

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 濫用 Error Boundary (Overusing Error Boundaries)

*   **反模式 (Anti-pattern):** 將每個按鈕或輸入框都包在 Error Boundary 中。
    Wrapping every button or input field in an Error Boundary.
*   **問題 (Why it's bad):** 雖然這極大化了隔離，但會導致 UI 破碎化。當一個按鈕壞掉時，使用者看到的是一個充滿「錯誤圖示」的頁面，且維護成本極高。此外，Error Boundary 會保留舊的 State，有時需要手動重置（Reset）。
    While this maximizes isolation, it leads to UI fragmentation. When a button breaks, the user sees a page full of "error icons," and maintenance becomes costly. Also, Error Boundaries preserve old State, sometimes requiring manual resets.
*   **修正 (Fix):** 遵循「功能區塊（Feature-level）」隔離原則。
    Follow the "Feature-level" isolation principle.

## 5.2 忽略 `javascript:` URI 攻擊 (Ignoring `javascript:` URI Attacks)

*   **反模式 (Anti-pattern):** 直接將使用者輸入放入 `href`。
    Directly placing user input into `href`.
    ```javascript
    <a href={userProfile.website}>My Website</a>
    ```
*   **問題 (Why it's bad):** 如果 `userProfile.website` 是 `javascript: alert(document.cookie)`，點擊即觸發 XSS。React 的自動跳脫**不會**防護屬性值中的協議（Protocol）。
    If `userProfile.website` is `javascript: alert(document.cookie)`, clicking it triggers XSS. React's automatic escaping does **not** protect against protocols in attribute values.
*   **修正 (Fix):** 驗證 URL 協議。
    Validate the URL protocol.
    ```javascript
    const safeHref = userProfile.website.startsWith('http') ? userProfile.website : '#';
    ```

## 5.3 在 Render Phase 產生副作用 (Side Effects in Render Phase)

*   **反模式 (Anti-pattern):** 在 component body 直接發送 log 或修改外部變數。
    Sending logs or modifying external variables directly in the component body.
*   **問題 (Why it's bad):** 在 React Concurrent Mode（或 React 18+ 的 Strict Mode）下，Render 函數可能會被呼叫多次但只 commit 一次。這會導致 Log 數據重複、污染，甚至造成邏輯錯誤。
    In React Concurrent Mode (or React 18+ Strict Mode), the Render function may be invoked multiple times but committed only once. This leads to duplicated logs, pollution, or even logic errors.
*   **修正 (Fix):** 所有的副作用（包含 Logging）都應該放在 `useEffect` 或 Event Handlers 中。
    All side effects (including Logging) should be placed in `useEffect` or Event Handlers.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何在生產環境中處理「白屏」問題，並確保開發團隊能收到通知？
**How do you handle the "White Screen of Death" in production and ensure the dev team is notified?**

*   **高分回答要點 (Key Points):**
    *   解釋 **Error Boundaries** 的運作機制（`componentDidCatch`, `getDerivedStateFromError`）。
    *   區分 **Development** (顯示 overlay) 與 **Production** (顯示 fallback UI) 的行為差異。
    *   提到 **Integration**：如何將錯誤資訊發送到 Sentry/LogRocket。
    *   提到 **Source Maps** 的安全性處理（上傳後刪除公開存取），以便在後台看到可讀的 Stack Trace。

## Q2: React 自動防護 XSS，那我們還需要擔心什麼安全性問題？
**React automatically protects against XSS, so what security issues do we still need to worry about?**

*   **高分回答要點 (Key Points):**
    *   指出 React 防護的邊界：只防護 `textContent`，不防護 `dangerouslySetInnerHTML`。
    *   提到 **Attribute Injection**：如 `href="javascript:..."` 或 `src` 屬性。
    *   提到 **JSON Injection**：如果將 Server 端資料直接注入到 HTML `<script>` 標籤中（SSR 常見），需要做適當的跳脫。
    *   討論 **Supply Chain Attacks**：惡意 npm 套件的問題。

## Q3: 在 Concurrent Features 啟用後，對於錯誤處理或效能監控有什麼影響？
**With Concurrent Features enabled, what is the impact on error handling or performance monitoring?**

*   **高分回答要點 (Key Points):**
    *   **Render vs Commit**: 監控指標不能只看 Render 次數，因為 Render 可被中斷或丟棄。
    *   **Tearing**: 雖然 React 18 有 `useSyncExternalStore`，但在整合外部 Store 時若處理不當，可能會在 UI 呈現不一致的狀態。
    *   **Slow Renders**: Concurrent mode 讓頁面保持響應，但長時間的 render 仍需透過 Profiler API 監控，避免 CPU 佔用過高。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)
1.  **Error Boundaries** 是 React 應用程式的保險絲，必須分層設計（Global vs Feature）。
2.  **安全性** 不能只依賴 React。需額外處理 `dangerouslySetInnerHTML`、URL 協議驗證，並配置 CSP。
3.  **可觀測性** 依賴於結構化的 Logging 與 Source Maps 的正確管理（Private Source Maps）。
4.  **副作用管理** 在 React 18+ 至關重要，嚴禁在 Render Phase 執行 Logging 或 Analytics 呼叫。
5.  **第三方內容** 永遠視為不可信，必須使用 Sanitizer（如 DOMPurify）。

## 後續延伸 (Next Steps)
*   **Advanced Patterns**: 研究 **React Suspense** 與 Error Boundary 的結合，處理非同步資料載入的錯誤狀態。
*   **Next Chapter**: 進入 **Chapter 09: Performance Optimization**，學習如何利用 Profiler API 找出效能瓶頸，並優化 Large List 渲染與 Bundle Size。