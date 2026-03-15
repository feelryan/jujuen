# Chapter 09: 大型應用程式架構演進 (Large-Scale Architecture & Micro-frontends)

## 1. 前言與學習目標 (Introduction & Learning Objectives)

隨著前端應用程式的規模擴大與團隊人數增長，單純的 Component Composition 已不足以解決開發效率與部署瓶頸的問題。本章將視角從「程式碼實作」提升至「架構設計」，探討如何管理大規模 React 應用。

As frontend applications scale in size and team numbers grow, simple Component Composition is no longer sufficient to solve development efficiency and deployment bottlenecks. This chapter elevates the perspective from "code implementation" to "architectural design," exploring how to manage large-scale React applications.

完成本章後，你應該能夠：
After completing this chapter, you should be able to:

1.  **評估與實作 Monorepo 策略**：理解 Nx、Turborepo 等工具如何優化大型專案的建置與依賴管理。
    **Evaluate and implement Monorepo strategies**: Understand how tools like Nx and Turborepo optimize build and dependency management for large projects.
2.  **掌握 Micro-frontends 核心技術**：使用 Webpack 5 Module Federation 實作微前端架構，解決團隊間的獨立部署問題。
    **Master core Micro-frontends technologies**: Implement micro-frontend architecture using Webpack 5 Module Federation to solve independent deployment issues across teams.
3.  **設計 Legacy Code 遷移路徑**：運用 Strangler Fig Pattern（絞殺榕模式）將舊有的 Monolith 逐步重構為現代化 React 架構。
    **Design migration paths for Legacy Code**: Apply the Strangler Fig Pattern to gradually refactor legacy monoliths into modern React architectures.

---

## 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 Monorepo vs. Polyrepo

**直覺類比 (Analogy)**：
想像一家大型製造廠。**Polyrepo** 就像是每個部門（輪胎、引擎、底盤）都在不同的城市，擁有獨立的倉庫與工具，協作時需要透過物流（npm publish）運送零件，更新緩慢且版本易衝突。**Monorepo** 則像是所有部門都在同一個巨大的園區內，雖然各自獨立運作，但共享基礎設施（Linting, Testing, CI pipeline）與零件庫，變更可以原子化（Atomic）地同步生效。

**Intuitive Analogy**:
Imagine a large manufacturing plant. **Polyrepo** is like having each department (tires, engine, chassis) in different cities with independent warehouses and tools; collaboration requires shipping parts via logistics (npm publish), which is slow and prone to version conflicts. **Monorepo** is like having all departments within the same massive campus; while they operate independently, they share infrastructure (Linting, Testing, CI pipeline) and parts inventory, allowing changes to take effect atomically.

**正規定義 (Formal Definition)**：
Monorepo 是一種將多個專案（Projects/Packages）存儲在單一 Version Control System (VCS) Repository 中的策略。它不等於 Monolith；Monorepo 可以包含多個獨立部署的應用程式。

**Formal Definition**:
Monorepo is a strategy of storing multiple projects (Projects/Packages) in a single Version Control System (VCS) Repository. It is not equivalent to a Monolith; a Monorepo can contain multiple independently deployable applications.

### 2.2 Micro-frontends & Module Federation

**核心概念 (Core Concept)**：
微前端將後端 Microservices 的概念引入前端。它允許將一個大型前端應用拆分為多個垂直切片（Vertical Slices），每個切片由不同團隊維護、使用不同技術堆疊（雖不建議混用，但技術上可行），並能獨立部署。

**Core Concept**:
Micro-frontends bring the backend Microservices concept to the frontend. It allows splitting a large frontend application into multiple vertical slices, where each slice is maintained by a different team, can use a different tech stack (though mixing is discouraged, it is technically possible), and can be deployed independently.

**Module Federation (Webpack 5)**：
這是實現微前端的關鍵技術。它允許 JavaScript 應用程式在**執行時 (Runtime)** 動態載入另一個應用程式的程式碼，並共享依賴（如 React, Lodash），避免重複下載。

**Module Federation (Webpack 5)**:
This is the key technology enabling micro-frontends. It allows a JavaScript application to dynamically load code from another application at **runtime** and share dependencies (like React, Lodash) to avoid duplicate downloads.

---

## 3. 實務場景與系統設計視角 (Real-World & System Design View)

### 3.1 典型架構角色 (Typical Architecture Roles)

在一個基於 Module Federation 的系統中，通常包含兩種角色：
In a system based on Module Federation, there are typically two roles:

1.  **Host (Shell / Container)**：負責應用程式的骨架、導航（Routing）、全域狀態（Authentication）以及載入 Remote 模組。
    **Host (Shell / Container)**: Responsible for the application skeleton, navigation (Routing), global state (Authentication), and loading Remote modules.
2.  **Remote (Micro-app)**：獨立的功能模組（如：結帳流程、使用者儀表板），可以作為獨立 App 運行，也可以被 Host 載入。
    **Remote (Micro-app)**: Independent functional modules (e.g., Checkout Flow, User Dashboard) that can run as standalone apps or be loaded by the Host.

### 3.2 對系統屬性的影響 (Impact on System Attributes)

*   **可維護性 (Maintainability)**：
    *   *Pros*: 程式碼庫邊界清晰，團隊權責分明。
    *   *Cons*: 跨應用程式的整合測試（Integration Testing）變得複雜。
    *   *Pros*: Clear codebase boundaries and distinct team responsibilities.
    *   *Cons*: Integration testing across applications becomes complex.

*   **部署與 CI/CD (Deployment & CI/CD)**：
    *   *Pros*: 獨立部署。修改「結帳頁」不需要重新構建整個「首頁」。
    *   *Cons*: 需要更複雜的 CI/CD 協調，確保 Remote 更新後 Host 不會崩潰（Contract Testing）。
    *   *Pros*: Independent deployment. Modifying the "Checkout Page" doesn't require rebuilding the entire "Home Page".
    *   *Cons*: Requires more complex CI/CD coordination to ensure Remote updates don't crash the Host (Contract Testing).

*   **效能 (Performance)**：
    *   *Pros*: 按需載入（Lazy Loading）是預設行為。
    *   *Cons*: 若依賴共享配置錯誤，可能導致重複下載 React 核心庫，造成 Bundle Bloat。
    *   *Pros*: Lazy loading is the default behavior.
    *   *Cons*: Incorrect shared dependency configuration can lead to downloading React core libraries multiple times, causing Bundle Bloat.

---

## 4. 逐步示例 (Walkthrough / Example)

### 案例：從單體應用拆分出「Dashboard」模組
### Scenario: Extracting a "Dashboard" module from a Monolithic App

假設我們有一個電商平台（Host），希望將賣家後台（Dashboard）拆分給另一個團隊獨立開發。

Suppose we have an E-commerce platform (Host) and want to split the Seller Dashboard (Dashboard) for another team to develop independently.

#### Step 1: 配置 Remote (Dashboard App)
#### Step 1: Configure Remote (Dashboard App)

在 Dashboard 專案的 `webpack.config.js` 中使用 `ModuleFederationPlugin`。
Use `ModuleFederationPlugin` in the `webpack.config.js` of the Dashboard project.

```javascript
// dashboard/webpack.config.js
const { ModuleFederationPlugin } = require('webpack').container;
const deps = require('./package.json').dependencies;

module.exports = {
  // ... other webpack config
  plugins: [
    new ModuleFederationPlugin({
      name: 'dashboardApp', // Unique name for the remote
      filename: 'remoteEntry.js', // The manifest file name
      exposes: {
        // Expose the main component
        './DashboardWidget': './src/components/DashboardWidget',
        './AnalyticsPage': './src/pages/Analytics',
      },
      shared: {
        ...deps,
        react: {
          singleton: true, // Critical: Only one copy of React
          requiredVersion: deps.react,
        },
        'react-dom': {
          singleton: true,
          requiredVersion: deps['react-dom'],
        },
      },
    }),
  ],
};
```

#### Step 2: 配置 Host (Main App)
#### Step 2: Configure Host (Main App)

在主應用程式中註冊 Remote。
Register the Remote in the main application.

```javascript
// host/webpack.config.js
const { ModuleFederationPlugin } = require('webpack').container;
const deps = require('./package.json').dependencies;

module.exports = {
  // ...
  plugins: [
    new ModuleFederationPlugin({
      name: 'hostApp',
      remotes: {
        // format: 'remoteName@url/remoteEntry.js'
        dashboard: 'dashboardApp@http://localhost:3001/remoteEntry.js',
      },
      shared: {
        ...deps,
        react: { singleton: true, requiredVersion: deps.react },
        'react-dom': { singleton: true, requiredVersion: deps['react-dom'] },
      },
    }),
  ],
};
```

#### Step 3: 在 Host 中使用 Remote Component
#### Step 3: Consume Remote Component in Host

使用 `React.lazy` 與 `Suspense` 進行非同步載入。
Use `React.lazy` and `Suspense` for asynchronous loading.

```javascript
// host/src/App.js
import React, { Suspense } from 'react';

// Dynamic import matching the 'remotes' key and 'exposes' key
const RemoteDashboard = React.lazy(() => import('dashboard/DashboardWidget'));

const App = () => {
  return (
    <div>
      <h1>Main Application Shell</h1>
      <div style={{ border: '1px solid red', padding: '20px' }}>
        <Suspense fallback={<div>Loading Dashboard...</div>}>
          <RemoteDashboard userRole="admin" />
        </Suspense>
      </div>
    </div>
  );
};

export default App;
```

#### 關鍵思考 (Critical Thinking)
為什麼這在實務中可行？因為 `remoteEntry.js` 是一個輕量的 manifest 檔案，Host 載入它後，才知道去哪裡抓取 `DashboardWidget` 的實際 chunk。如果 Host 已經載入了 React 18，且 Remote 也要求 React 18，Webpack 會協調雙方使用 Host 已有的 React 實例，節省頻寬並維持 Context 一致性。

Why is this viable in practice? Because `remoteEntry.js` is a lightweight manifest file. After the Host loads it, it knows where to fetch the actual chunk for `DashboardWidget`. If the Host has already loaded React 18 and the Remote also requires React 18, Webpack coordinates both to use the Host's existing React instance, saving bandwidth and maintaining Context consistency.

---

## 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 Singleton 依賴配置錯誤 (Misconfigured Singleton Dependencies)

*   **錯誤案例 (Pitfall)**：未將 `react` 與 `react-dom` 設為 `singleton: true`。
*   **後果 (Consequence)**：瀏覽器會下載兩份 React。這不僅浪費頻寬，更會導致著名的錯誤：`Error: Invalid hook call. Hooks can only be called inside of the body of a function component.` 這是因為 Hooks 依賴於全域的 React Dispatcher，多個 React 實例會導致 Dispatcher 錯亂。
*   **解決方案 (Solution)**：務必在 `shared` 配置中明確標示 `singleton: true`。

*   **Pitfall**: Failing to set `react` and `react-dom` as `singleton: true`.
*   **Consequence**: The browser downloads two copies of React. This not only wastes bandwidth but leads to the infamous error: `Error: Invalid hook call. Hooks can only be called inside of the body of a function component.` This is because Hooks rely on a global React Dispatcher, and multiple React instances confuse the Dispatcher.
*   **Solution**: Always explicitly mark `singleton: true` in the `shared` configuration.

### 5.2 過度拆分 (Over-fragmentation / Micro-components)

*   **錯誤案例 (Pitfall)**：將每個 Button、Dropdown 都做成一個 Micro-frontend。
*   **後果 (Consequence)**：網路請求爆炸（Network Waterfall），開發體驗極差（DX suffers），版本管理地獄。
*   **解決方案 (Solution)**：Micro-frontends 應該以「業務領域（Domain）」或「頁面（Page）」為邊界，而非 UI 元件。UI 元件應透過 Shared NPM Library 管理。

*   **Pitfall**: Turning every Button or Dropdown into a Micro-frontend.
*   **Consequence**: Explosion of network requests (Network Waterfall), poor developer experience (DX suffers), and version management hell.
*   **Solution**: Micro-frontends should be bounded by "Business Domains" or "Pages," not UI components. UI components should be managed via a Shared NPM Library.

### 5.3 樣式污染 (CSS Pollution)

*   **錯誤案例 (Pitfall)**：Remote App 使用全域 CSS (e.g., `body { font-size: 14px }`)。
*   **後果 (Consequence)**：當 Remote 被載入 Host 時，會覆蓋 Host 的樣式，導致整個網站版面崩壞。
*   **解決方案 (Solution)**：強制使用 CSS Modules、Styled Components 或 Shadow DOM 來確保樣式隔離（Style Isolation）。

*   **Pitfall**: Remote App uses global CSS (e.g., `body { font-size: 14px }`).
*   **Consequence**: When the Remote is loaded into the Host, it overrides the Host's styles, breaking the layout of the entire site.
*   **Solution**: Enforce the use of CSS Modules, Styled Components, or Shadow DOM to ensure Style Isolation.

---

## 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 你會如何決定何時引入 Micro-frontends 架構？
### Q1: How do you decide when to introduce a Micro-frontend architecture?

*   **高分回答要點 (Key Points)**：
    *   **組織結構 (Organizational Structure)**：康威定律（Conway's Law）。當團隊規模大到無法有效溝通，需要解耦部署流程時。
    *   **部署頻率 (Deployment Frequency)**：不同模組的發布週期差異巨大（例如：行銷活動頁 vs. 核心結帳頁）。
    *   **反對理由 (Counter-arguments)**：如果專案規模小、團隊少於 10 人，引入微前端只會增加無謂的複雜度（Over-engineering）。Monorepo 可能是更好的過渡方案。

*   **Key Points**:
    *   **Organizational Structure**: Conway's Law. When the team size is too large for effective communication and deployment processes need decoupling.
    *   **Deployment Frequency**: Vastly different release cycles for different modules (e.g., Marketing Campaign pages vs. Core Checkout pages).
    *   **Counter-arguments**: If the project is small or the team is under 10 people, introducing micro-frontends adds unnecessary complexity (Over-engineering). A Monorepo might be a better transition solution.

### Q2: 在微前端架構下，如何處理跨應用程式的通訊與狀態共享？
### Q2: How do you handle cross-application communication and state sharing in a micro-frontend architecture?

*   **高分回答要點 (Key Points)**：
    *   **避免過度耦合 (Avoid Tight Coupling)**：盡量減少共享狀態。
    *   **URL as Source of Truth**：透過 Query Params 傳遞簡單狀態。
    *   **Custom Events / Pub-Sub**：使用瀏覽器原生的 `CustomEvent` 或輕量的 Event Bus 進行鬆散耦合通訊。
    *   **Global Store (慎用)**：雖然可以將 Redux/Zustand store expose 出去，但這會造成強依賴，違反微前端獨立部署的初衷。

*   **Key Points**:
    *   **Avoid Tight Coupling**: Minimize shared state as much as possible.
    *   **URL as Source of Truth**: Pass simple state via Query Params.
    *   **Custom Events / Pub-Sub**: Use browser-native `CustomEvent` or a lightweight Event Bus for loosely coupled communication.
    *   **Global Store (Use with Caution)**: While you can expose a Redux/Zustand store, this creates strong dependencies, violating the principle of independent deployment in micro-frontends.

### Q3: 如何在 Legacy System (e.g., jQuery/AngularJS) 中逐步遷移到 React？
### Q3: How do you gradually migrate a Legacy System (e.g., jQuery/AngularJS) to React?

*   **高分回答要點 (Key Points)**：
    *   **Strangler Fig Pattern**：不直接重寫，而是在舊系統旁建立新系統，逐步攔截流量。
    *   **實作細節**：使用 Module Federation 或簡單的 `ReactDOM.render` 將 React Widget 掛載到舊版 HTML 的特定 `div` 上。
    *   **Nginx/Routing 層級**：在 Load Balancer 層級將特定路徑（如 `/new-feature`）導向新的 React App。

*   **Key Points**:
    *   **Strangler Fig Pattern**: Don't rewrite directly; build a new system alongside the old one and gradually intercept traffic.
    *   **Implementation Details**: Use Module Federation or simple `ReactDOM.render` to mount React Widgets onto specific `div`s in the legacy HTML.
    *   **Nginx/Routing Level**: Redirect specific paths (e.g., `/new-feature`) to the new React App at the Load Balancer level.

---

## 7. 小結與後續延伸 (Summary & Next Steps)

### 重點回顧 (Key Takeaways)

1.  **Monorepo (Nx/Turborepo)** 解決了多專案的程式碼共享與建置效率問題，是大型團隊的基礎建設。
2.  **Module Federation** 允許在 Runtime 動態載入模組，是現代微前端架構的主流實作。
3.  **Shared Dependencies** 的配置至關重要，特別是 React 的 `singleton` 設定，否則會導致 Hook 錯誤。
4.  **獨立部署 (Independent Deployment)** 是微前端的核心價值，架構設計應以此為目標，避免過度耦合。
5.  **Strangler Fig Pattern** 是處理 Legacy Code 遷移最穩健的策略。

### 後續延伸 (Next Steps)

*   **進階效能優化**：研究如何在微前端架構下實作 **Server-Side Rendering (SSR)** (e.g., Next.js with Module Federation)。
*   **Design System**：如何構建一個跨團隊、跨微前端的 Design System Component Library。
*   **Observability**：在分散式前端架構中，如何追蹤錯誤（Sentry, Datadog）與效能監控。

*   **Advanced Performance Optimization**: Research how to implement **Server-Side Rendering (SSR)** in a micro-frontend architecture (e.g., Next.js with Module Federation).
*   **Design System**: How to build a Design System Component Library that works across teams and micro-frontends.
*   **Observability**: How to track errors (Sentry, Datadog) and monitor performance in a distributed frontend architecture.