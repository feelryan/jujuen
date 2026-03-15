# 資料流與副作用處理 / Data Fetching & Side Effects Handling

## Mental model｜心智模型

在 React 中處理資料流與副作用（Side Effects），核心觀念不在於「如何在組件內發送請求」，而在於**「如何將外部資料狀態同步（Synchronize）到 UI 上」**。

### 1. External Store Synchronization (外部狀態同步)
不要將 Server Data 視為單純的 Component State。Server Data 是「借來的」，它屬於遠端伺服器。你的前端只是該資料的一個 **Cache（快照）**。
- **Old Mindset**: `componentDidMount` -> `fetch` -> `setState`.
- **New Mindset**: UI 訂閱了一個外部資料源（Cache）。當 Cache 更新或過期時，UI 自動重繪。這就是為什麼 React Query / SWR / Apollo Client 等工具成為標準的原因。

### 2. Fetch-on-Render vs. Render-as-you-Fetch
- **Fetch-on-Render (Waterfall)**: 組件渲染 -> 發現需要資料 -> 發送請求 -> 等待 -> 渲染子組件 -> 子組件發現需要資料 -> 發送請求...（這是效能殺手）。
- **Render-as-you-Fetch (Concurrent/Suspense)**: 在開始渲染之前（或同時）就開始抓取資料。讓資料與 UI 載入並行發生。

### 3. The Lifecycle of an Effect
副作用（Effect）的生命週期與組件的 Mount/Unmount 不完全相同。Effect 的重點在於**依賴項（Dependencies）的變化**。
- 每次依賴改變，舊的 Effect 必須被「清理（Cleanup）」，新的 Effect 才能執行。這對於防止 **Race Conditions** 至關重要。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 使用專門的 Server State Library
在 90% 的 SPA 場景中，**不要**在 `useEffect` 中手寫 `fetch`。
- **Pattern**: 使用 React Query (TanStack Query) 或 SWR。
- **Why**: 它們自動處理了 Caching, Deduping (重複請求去重), Revalidation on focus, Retry logic, 以及最重要的 Race Condition 處理。

```javascript
// ✅ Best Practice: Using a library
const { data, error, isLoading } = useQuery({
  queryKey: ['user', id],
  queryFn: () => fetchUser(id),
});
```

### 2. AbortController for Race Conditions
如果你必須手寫 `useEffect` 或在事件處理器中打 API，務必實作 Cancellation。
- **Scenario**: 使用者快速切換 Tab A 和 Tab B。Tab A 的請求較慢，Tab B 較快。若無取消機制，Tab A 的結果可能會覆蓋 Tab B 的畫面（Stale Data overwriting Fresh Data）。

```javascript
// ✅ Pattern: Handling Race Conditions manually
useEffect(() => {
  const controller = new AbortController();
  
  async function fetchData() {
    try {
      const response = await fetch(url, { signal: controller.signal });
      const data = await response.json();
      setData(data);
    } catch (e) {
      if (e.name !== 'AbortError') handleError(e);
    }
  }

  fetchData();
  
  // Cleanup function runs before next effect or on unmount
  return () => controller.abort();
}, [url]);
```

### 3. Hoisting Data Requirements (提升資料需求)
為了避免 Waterfall，盡量將資料獲取邏輯提升到路由層級（Route Level）或父層容器。
- **Modern Approach**: 使用 Next.js Server Components 或 Remix `loader`，在伺服器端就並行處理好資料。
- **SPA Approach**: 在父層使用 `Promise.all` 獲取所有子組件需要的資料，再透過 Context 或 Props 傳遞。

### 4. Optimistic UI (樂觀更新)
不要等待 Server 回應才更新 UI。先假設成功，失敗再回滾（Rollback）。
- **Use Case**: 按讚、加入購物車、Todo List 打勾。
- **Implementation**: 更新 Local Cache -> 發送 Request -> 若 Error 則 Revert Cache。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Fetch inside useEffect" Waterfall
最常見的效能殺手。
- **Bad**: Parent Component fetch -> Render -> Child Component fetch -> Render.
- **Consequence**: 使用者看到載入轉圈圈，消失後，裡面又出現一個轉圈圈。載入時間是所有請求時間的**總和**，而非**最大值**。

### 2. Ignoring the Cleanup Function
- **Bad**: 在 `useEffect` 中訂閱事件或發送請求，但沒有 return cleanup function。
- **Consequence**: Memory leaks，或者在快速操作時出現 "Can't perform a React state update on an unmounted component" 警告（雖然 React 18 優化了這點，但邏輯上仍是錯誤）。

### 3. Derived State in useEffect
- **Bad**: 使用 `useEffect` 來觀察 `data` 變化，然後 `setFilteredData`。
- **Consequence**: 導致額外的 Render Cycle。
- **Fix**: 直接在 Render 過程中計算 Derived State，配合 `useMemo` 優化。

```javascript
// ❌ Anti-pattern
useEffect(() => {
  setFiltered(items.filter(i => i.active));
}, [items]);

// ✅ Correct
const filtered = useMemo(() => items.filter(i => i.active), [items]);
```

### 4. Prop Drilling Fetch Callbacks
- **Bad**: 將 `refetch` 函數傳遞過多層級。
- **Fix**: 使用 React Context 或 Server State Library 的 `useQueryClient` / `mutate` 在任何組件中直接觸發更新。

---

## Checklists & workflows｜檢查清單與流程

在實作資料流功能時，請依序檢查以下項目：

### Development Checklist
- [ ] **Race Condition Check**: 如果我快速觸發兩次請求（例如切換分頁），舊的請求是否會被取消，或者舊的結果是否會被忽略？
- [ ] **Waterfall Check**: 我的組件樹中，是否有「父層載入完 -> 子層才開始載入」的狀況？能否並行處理？
- [ ] **Loading State**: 是否處理了 `isLoading` 狀態？是否有 Skeleton Screen 或 Spinner？
- [ ] **Error Handling**: 請求失敗時，UI 是白屏還是有 Error Boundary / Toast 提示？
- [ ] **Empty State**: 如果資料回來是空的（Empty Array），UI 顯示是否正常？
- [ ] **Strict Mode**: 在 React Strict Mode（開發模式）下，Effect 會執行兩次，我的邏輯是否能承受？（例如：是否發送了重複的 Analytics 事件？）

### Decision Tree: Where to fetch?
1. **是 Next.js / Remix 等現代框架？**
   - -> 使用 Server Components / Loaders (Backend-for-Frontend pattern)。
2. **是傳統 SPA (Create React App / Vite)？**
   - **全域需要的資料 (User Profile)？** -> 初始化時 fetch 並存入 Context/Store。
   - **頁面專屬資料？** -> 使用 React Query / SWR 在 Page Component 層級 fetch。
   - **極小、不需 Cache 的一次性資料？** -> `useEffect` + `AbortController` (但在 2024 年建議還是用 Library)。

---

## Real-world examples｜實戰案例

### Case 1: 解決 Search Input 的 Race Condition 與 Debounce

這是一個經典面試題與實務難題：使用者輸入 "React"，API 可能依序發送 "R", "Re", "Rea"... 但 "R" 的回應可能比 "Rea" 晚到。

```javascript
function SearchResults({ query }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    let ignore = false; // Flag to handle race condition
    
    async function fetchData() {
      // 模擬 API
      const result = await searchAPI(query);
      if (!ignore) {
        setData(result);
      }
    }

    fetchData();

    return () => {
      ignore = true; // Cleanup: 標記舊的請求結果為「無效」
    };
  }, [query]);

  // ... render logic
}
```
*註：實務上建議配合 `useDebounce` 減少請求次數。*

### Case 2: 消除 Waterfall (Parallel Fetching)

**Before (Waterfall):**
```javascript
// UserProfile.js
const { user } = useUser(); // Takes 200ms
if (!user) return <Spinner />;
return <UserPosts userId={user.id} />; // Starts only after user is loaded
```

**After (Parallel / Prefetching):**
```javascript
// Page.js
// 同時發起請求，利用 Library 的 key 機制
const userQuery = useQuery({ queryKey: ['user'], queryFn: fetchUser });
const postsQuery = useQuery({ 
  queryKey: ['posts', userId], 
  queryFn: fetchPosts,
  enabled: !!userQuery.data // Dependent query, 但如果是已知 ID 則可移除 enabled 並行
});

if (userQuery.isLoading) return <Spinner />;

// 或者在 Router 層級使用 loader (React Router 6.4+ / Next.js)
// loader: async () => {
//   const [user, posts] = await Promise.all([fetchUser(), fetchPosts()]);
//   return { user, posts };
// }
```

### Case 3: Suspense for Data Fetching (Modern Pattern)

在 React 18+ 與 Next.js 中，我們不再手動處理 `isLoading`，而是用 Suspense 邊界。

```javascript
import { Suspense } from 'react';

export default function Dashboard() {
  return (
    <div className="layout">
      <Nav />
      {/* 只要 UserProfile 或 RecentActivity 還在讀取，就顯示 Skeleton */}
      <Suspense fallback={<DashboardSkeleton />}>
        <UserProfile />
        <RecentActivity />
      </Suspense>
    </div>
  );
}
```
*這種模式將「讀取狀態」與「組件邏輯」解耦，讓 UI 程式碼更乾淨，且避免了畫面因各個組件先後載入而產生的 Layout Shift (CLS)。*