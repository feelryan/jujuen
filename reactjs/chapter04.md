# 1. 前言與學習目標 (Introduction & Learning Objectives)

在 React 生態系發展初期，Redux 幾乎是狀態管理的唯一標準答案。然而，隨著 React Hooks 的引入以及對「伺服器狀態（Server State）」與「客戶端狀態（Client State）」邊界認知的成熟，現代 React 應用的狀態架構已發生巨大轉變。

In the early days of the React ecosystem, Redux was almost the default answer for state management. However, with the introduction of React Hooks and a maturing understanding of the boundary between "Server State" and "Client State," the state architecture of modern React applications has shifted significantly.

完成本章後，身為資深工程師，你應該能夠：
By the end of this chapter, as a Senior Engineer, you should be able to:

1.  **精準區分狀態類型**：不再將 API 回傳資料視為單純的 Redux Store 屬性，而是理解 Server State 的快取、過期與同步機制（如 React Query）。
    **Distinguish state types precisely**: Stop treating API response data merely as Redux Store properties, and instead understand the caching, staleness, and synchronization mechanisms of Server State (e.g., React Query).

2.  **評估架構權衡**：能夠根據專案規模與複雜度，在 Context API、Zustand、Redux Toolkit 與 Atomic State (Jotai/Recoil) 之間做出正確的技術選型。
    **Evaluate architectural trade-offs**: Make the right technical choices among Context API, Zustand, Redux Toolkit, and Atomic State (Jotai/Recoil) based on project scale and complexity.

3.  **優化渲染效能**：理解不同狀態管理庫的「變更傳播機制（Change Propagation Mechanism）」，避免因 Context 使用不當導致的無效渲染（Unnecessary Re-renders）。
    **Optimize rendering performance**: Understand the "Change Propagation Mechanism" of different state management libraries to avoid unnecessary re-renders caused by improper use of Context.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 狀態光譜：Server vs. Client State
## 2.1 The State Spectrum: Server vs. Client State

資深工程師應具備的第一個心智模型是將「狀態」視為一個光譜，而非單一巨大的 Store。
The first mental model a Senior Engineer should possess is viewing "state" as a spectrum, rather than a single monolithic Store.

*   **Server State (Remote)**:
    *   **定義**：資料實際上不屬於你的 Client，你只是借用（borrowed）。它由遠端伺服器擁有，可能隨時被其他人更新。
    *   **特性**：非同步（Asynchronous）、需要快取（Cached）、可能過期（Stale）、需要去重（Deduplicated）。
    *   **工具**：TanStack Query (React Query), SWR, Apollo Client.
    *   **Definition**: Data that doesn't actually belong to your Client; you are just borrowing it. It is owned by a remote server and can be updated by others at any time.
    *   **Characteristics**: Asynchronous, Cached, Stale, Deduplicated.
    *   **Tools**: TanStack Query (React Query), SWR, Apollo Client.

*   **Client State (UI/Local)**:
    *   **定義**：完全由瀏覽器當前的 Session 擁有與控制。
    *   **特性**：同步（Synchronous）、通常是暫時的（Ephemeral）。
    *   **分類**：
        *   **Global UI**: Theme, Sidebar open/close, User Session (Zustand, Redux).
        *   **Form State**: Input values, validation (React Hook Form).
        *   **Component State**: `useState`, `useReducer`.
    *   **Definition**: Fully owned and controlled by the browser's current session.
    *   **Characteristics**: Synchronous, usually Ephemeral.
    *   **Classification**:
        *   **Global UI**: Theme, Sidebar open/close, User Session (Zustand, Redux).
        *   **Form State**: Input values, validation (React Hook Form).
        *   **Component State**: `useState`, `useReducer`.

## 2.2 狀態傳播機制：Push vs. Pull (Atomic)
## 2.2 State Propagation Mechanism: Push vs. Pull (Atomic)

理解狀態庫如何通知組件更新至關重要：
Understanding how state libraries notify components to update is crucial:

1.  **Context API (Dependency Injection)**:
    *   當 Provider 的 value 改變時，**所有** 訂閱該 Context 的子組件都會重新渲染（除非使用 `useMemo` 或拆分 Context）。這適合低頻更新（Low-frequency updates），如 Theme 或 User Locale。
    *   When the Provider's value changes, **all** child components subscribed to that Context re-render (unless `useMemo` or Context splitting is used). This fits low-frequency updates like Theme or User Locale.

2.  **External Store (Redux/Zustand)**:
    *   使用 Observer Pattern。組件透過 `selector` 訂閱 Store 的特定切片（Slice）。只有當切片資料改變時，該組件才會渲染。這適合高頻、複雜的互動。
    *   Uses the Observer Pattern. Components subscribe to a specific slice of the Store via a `selector`. The component renders only when that slice changes. This fits high-frequency, complex interactions.

3.  **Atomic State (Recoil/Jotai)**:
    *   由下而上（Bottom-up）的拓撲結構。狀態被拆分為最小單元（Atom），組件直接訂閱 Atom。這在處理圖形編輯器或 Excel 類應用時效能極佳。
    *   Bottom-up topological structure. State is split into minimal units (Atoms), and components subscribe directly to Atoms. This performs excellently for graphics editors or Excel-like applications.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型系統設計中，狀態管理的選擇直接影響**可維護性（Maintainability）**與**效能（Performance）**。

In large-scale system design, the choice of state management directly impacts **Maintainability** and **Performance**.

## 3.1 現代 React 應用的分層架構
## 3.1 Layered Architecture in Modern React Apps

在 Production 環境中，我們不再使用單一的 Redux Store 處理所有事情，而是採用分層策略：
In a Production environment, we no longer use a single Redux Store for everything, but adopt a layered strategy:

1.  **Data Layer (Server State)**:
    *   使用 **React Query** 處理 API 請求。
    *   **優勢**：自動處理 Loading/Error 狀態、Retry 機制、Window Focus Refetching。這大幅減少了 boilerplate code。
    *   Use **React Query** to handle API requests.
    *   **Advantage**: Automatically handles Loading/Error states, Retry mechanisms, and Window Focus Refetching. This significantly reduces boilerplate code.

2.  **Application Layer (Global Client State)**:
    *   使用 **Zustand** 或 **Redux Toolkit**。
    *   僅存放跨頁面共享的 UI 狀態（如：購物車內容、全域 Modal 控制）。
    *   Use **Zustand** or **Redux Toolkit**.
    *   Stores only UI state shared across pages (e.g., Shopping Cart contents, Global Modal controls).

3.  **Feature Layer (Local State)**:
    *   使用 `useState`, `useReducer`, 或 **Context**（僅限該 Feature 範圍內）。
    *   避免將僅屬於某個 Widget 的狀態提升到 Global Store。
    *   Use `useState`, `useReducer`, or **Context** (scoped strictly to that Feature).
    *   Avoid hoisting state that belongs only to a specific Widget into the Global Store.

## 3.2 效能與擴展性考量
## 3.2 Performance & Scalability Considerations

*   **Bundle Size**: Redux + RTK 較重；Zustand 極輕量（~1KB）。對於移動端優先的應用，Zustand 是更好的預設選擇。
    **Bundle Size**: Redux + RTK is heavier; Zustand is extremely lightweight (~1KB). For mobile-first apps, Zustand is a better default choice.
*   **Re-render Storms**: 在大型 Dashboard 中，若將所有 API 資料放入 Context，一次 API 更新可能觸發數百個組件重新渲染。使用 Selectors（Zustand/Redux）可以精確控制渲染範圍。
    **Re-render Storms**: In large Dashboards, putting all API data into Context can trigger hundreds of component re-renders upon a single API update. Using Selectors (Zustand/Redux) allows precise control over the render scope.

---

# 4. 逐步示例 (Walkthrough / Example)

## 場景：儀表板與即時通知
## Scenario: Dashboard with Real-time Notifications

假設我們要構建一個儀表板，包含：
1.  用戶個人資料（很少變動）。
2.  即時通知計數（高頻變動）。
3.  側邊欄摺疊狀態（UI 互動）。

Let's build a dashboard containing:
1.  User Profile (Rarely changes).
2.  Real-time Notification Count (High-frequency changes).
3.  Sidebar Collapse State (UI interaction).

### 4.1 Naive Approach (The Anti-pattern)

將所有東西都塞進一個巨大的 Context。
Stuffing everything into a massive Context.

```tsx
// ❌ Bad Practice: Mixing concerns and causing re-renders
const GlobalContext = createContext(null);

export const GlobalProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [notifications, setNotifications] = useState(0);
  const [isSidebarOpen, setSidebarOpen] = useState(true);

  // Fetching inside provider (Manual effect management)
  useEffect(() => {
    fetch('/api/user').then(u => setUser(u));
  }, []);

  // Whenever 'notifications' updates, components only caring about 'isSidebarOpen' will also re-render!
  const value = { user, notifications, isSidebarOpen, setSidebarOpen };
  
  return <GlobalContext.Provider value={value}>{children}</GlobalContext.Provider>;
};
```

### 4.2 Mature Approach (Separation of Concerns)

我們將狀態拆分為 Server State (React Query) 與 Client State (Zustand)。
We split the state into Server State (React Query) and Client State (Zustand).

#### Step 1: Server State with React Query

```tsx
// ✅ Good: Dedicated Data Fetching & Caching
import { useQuery } from '@tanstack/react-query';

export const useUserProfile = () => {
  return useQuery({
    queryKey: ['user'],
    queryFn: async () => {
      const res = await fetch('/api/user');
      return res.json();
    },
    staleTime: 1000 * 60 * 60, // Data is fresh for 1 hour
  });
};
```

#### Step 2: Client State with Zustand

```tsx
// ✅ Good: Atomic-like store with selectors
import { create } from 'zustand';

interface UIState {
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
  notifications: number;
  setNotifications: (count: number) => void;
}

export const useUIStore = create<UIState>((set) => ({
  isSidebarOpen: true,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  notifications: 0,
  setNotifications: (count) => set({ notifications: count }),
}));
```

#### Step 3: Consumption with Selectors (Performance Optimization)

```tsx
// Component A: Sidebar Toggle Button
const SidebarToggle = () => {
  // Select ONLY what you need. 
  // This component will NOT re-render when 'notifications' changes.
  const toggle = useUIStore((state) => state.toggleSidebar);
  const isOpen = useUIStore((state) => state.isSidebarOpen);
  
  console.log('SidebarToggle Rendered'); 
  return <button onClick={toggle}>{isOpen ? 'Close' : 'Open'}</button>;
};

// Component B: Notification Badge
const Badge = () => {
  const count = useUIStore((state) => state.notifications);
  
  console.log('Badge Rendered');
  return <span>{count}</span>;
};
```

### 分析 (Analysis)
*   **解耦 (Decoupling)**: API 邏輯與 UI 狀態完全分離。
*   **效能 (Performance)**: `SidebarToggle` 不會因為 `notifications` 更新而重新渲染，這在 Context API 中很難簡單達成（需要拆分多個 Context）。
*   **Decoupling**: API logic is completely separated from UI state.
*   **Performance**: `SidebarToggle` does not re-render when `notifications` updates, which is hard to achieve simply with Context API (requires splitting into multiple Contexts).

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 Redux 作為 API 快取 (Redux as API Cache)
*   **錯誤**：手寫 Thunk/Saga 來 fetch 資料，dispatch `FETCH_START`, `FETCH_SUCCESS`，並將資料存入 Redux Store。
*   **問題**：你需要手動處理 race conditions、deduplication、cache invalidation。這增加了大量的 boilerplate 且容易出錯。
*   **修正**：使用 **React Query** 或 **RTK Query**。
*   **Mistake**: Hand-rolling Thunks/Sagas to fetch data, dispatching `FETCH_START`, `FETCH_SUCCESS`, and storing data in Redux Store.
*   **Issue**: You have to manually handle race conditions, deduplication, and cache invalidation. This adds massive boilerplate and is error-prone.
*   **Fix**: Use **React Query** or **RTK Query**.

## 5.2 Context Hell (Context 濫用)
*   **錯誤**：為了避免 Prop Drilling，將所有狀態都放入 Context，導致 Provider 嵌套過深（Provider Wrapper Hell），且造成全域重繪。
*   **問題**：Context 本質上是依賴注入（Dependency Injection）機制，而非高效能的狀態管理工具。
*   **修正**：對於高頻更新狀態，使用 Zustand/Redux；對於靜態配置（Config/Theme），使用 Context。
*   **Mistake**: To avoid Prop Drilling, putting all state into Context, leading to deep Provider nesting (Provider Wrapper Hell) and global re-renders.
*   **Issue**: Context is fundamentally a Dependency Injection mechanism, not a high-performance state management tool.
*   **Fix**: Use Zustand/Redux for high-frequency updates; use Context for static configuration (Config/Theme).

## 5.3 useEffect 同步狀態 (State Syncing via useEffect)
*   **錯誤**：監聽 props 變化，然後在 `useEffect` 中 `setState` 來同步本地狀態。
*   **問題**：這會導致額外的 Render pass（Props update -> Render -> Effect -> State update -> Render）。
*   **修正**：直接在 Render 過程中計算衍生狀態（Derived State），或使用 `key` prop 重置組件狀態。
*   **Mistake**: Listening to props changes and calling `setState` inside `useEffect` to sync local state.
*   **Issue**: This causes an extra Render pass (Props update -> Render -> Effect -> State update -> Render).
*   **Fix**: Calculate Derived State directly during the Render process, or use the `key` prop to reset component state.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 你如何決定何時使用 Context API，何時引入 Redux 或 Zustand？
## Q1: How do you decide when to use Context API versus introducing Redux or Zustand?

*   **高分回答要點**：
    *   **頻率與範圍**：Context 適合低頻更新（Theme, Auth User）與依賴注入。若狀態更新頻繁且被廣泛使用，Context 會導致效能問題。
    *   **選擇器 (Selectors)**：Zustand/Redux 支援 selectors，允許組件只訂閱 Store 的一部分，避免不必要的渲染。Context 無法原生做到這點（除非拆分 Context）。
    *   **除錯與中介軟體**：Redux/Zustand 提供 DevTools 和 Middleware 生態，適合複雜流程控制。
*   **Key Points for High Score**:
    *   **Frequency & Scope**: Context fits low-frequency updates (Theme, Auth User) and Dependency Injection. If state updates frequently and is widely used, Context causes performance issues.
    *   **Selectors**: Zustand/Redux support selectors, allowing components to subscribe only to a slice of the Store, avoiding unnecessary renders. Context cannot do this natively (without splitting Contexts).
    *   **Debugging & Middleware**: Redux/Zustand provide DevTools and Middleware ecosystems, suitable for complex flow control.

## Q2: 為什麼現代 React 開發傾向將 Server State 移出 Global Store？
## Q2: Why does modern React development tend to move Server State out of the Global Store?

*   **高分回答要點**：
    *   **本質不同**：Server State 是非同步且不屬於 Client 的，需要處理 Loading, Error, Stale, Caching, Deduping。
    *   **簡化程式碼**：手動在 Redux 中實作上述邏輯極其繁瑣。React Query 等專用庫將這些複雜性封裝，讓 Global Store 回歸單純的 Client UI 狀態管理。
    *   **樂觀更新 (Optimistic Updates)**：專用庫通常內建對 Optimistic Updates 的支援，提升 UX。
*   **Key Points for High Score**:
    *   **Fundamental Difference**: Server State is asynchronous and doesn't belong to the Client; it requires handling Loading, Error, Stale, Caching, and Deduping.
    *   **Code Simplification**: Manually implementing the above logic in Redux is tedious. Dedicated libraries like React Query encapsulate these complexities, letting the Global Store return to pure Client UI state management.
    *   **Optimistic Updates**: Dedicated libraries usually have built-in support for Optimistic Updates, improving UX.

## Q3: 什麼是 Prop Drilling？除了引入 Context/Store，還有什麼 React 原生解法？
## Q3: What is Prop Drilling? Besides introducing Context/Store, what are the native React solutions?

*   **高分回答要點**：
    *   **定義**：層層傳遞 props 給不需要該 props 的中間組件。
    *   **Component Composition (組合)**：這是常被忽略的解法。透過將子組件作為 `children` 或 prop 傳遞（Slot Pattern），可以避免中間層感知資料。
    *   **範例**：`<Layout user={user} />` 改為 `<Layout><Header user={user} /></Layout>`。
*   **Key Points for High Score**:
    *   **Definition**: Passing props through layers of intermediate components that don't need them.
    *   **Component Composition**: An often overlooked solution. By passing child components as `children` or props (Slot Pattern), intermediate layers can avoid awareness of the data.
    *   **Example**: Change `<Layout user={user} />` to `<Layout><Header user={user} /></Layout>`.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 記憶錨點 (Key Takeaways)
1.  **Server State != Client State**：優先使用 React Query (TanStack Query) 處理 API 資料，不要手動存入 Redux。
2.  **Context is for DI**：Context 適用於依賴注入與低頻靜態資料，不適合高頻動態數據。
3.  **Selectors Save Performance**：使用 Zustand 或 Redux 時，務必使用 Selector 來精確訂閱狀態，防止無效渲染。
4.  **Zustand over Redux**：對於大多數新專案，Zustand 提供了更簡單的 API 與更小的 Bundle size，除非你需要 Redux 強大的 Middleware 生態。
5.  **Component Composition**：在引入任何狀態庫之前，先思考是否能透過組件組合（Composition）解決 Prop Drilling。

## 後續延伸 (Next Steps)
*   **Advanced Performance**: 學習使用 React Profiler 分析 Context 造成的渲染浪費。
*   **Micro-Frontends**: 研究在微前端架構下，不同 App 如何共享或隔離狀態（Global Store vs Isolated Store）。
*   **Next Chapter**: 進入 **Chapter 05: React Performance Optimization (渲染機制與效能優化)**，深入探討 Fiber 架構與 Concurrency。