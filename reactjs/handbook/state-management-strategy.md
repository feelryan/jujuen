# 狀態管理架構決策 / State Management Architecture & Strategy

## Mental model｜心智模型

在現代 React 開發中，狀態（State）不再是一個單一的巨石（Monolith）。最關鍵的心智模型轉變是將狀態視為**不同生命週期與擁有權的集合**。

In modern React development, State is no longer a monolith. The critical mental shift is to view state as a collection of data with **different lifecycles and ownership**.

### 1. The Separation of Concerns: Server vs. Client
最根本的區分在於資料的「來源」與「控制權」：
- **Server State (伺服器狀態)**: 資料實際上屬於伺服器，前端只是一個「快照（Snapshot）」。它具有非同步、可能過期（Stale）、且由多人共享的特性。
- **Client State (客戶端狀態)**: 前端擁有完全控制權的資料，通常是同步的。例如：UI 的開合狀態、輸入框內容、目前的 Theme。

### 2. The Proximity Principle (就近原則)
狀態應該盡可能靠近使用它的地方。
- **Local**: 只有這個組件在乎。
- **Lifted**: 只有幾個兄弟組件在乎（提升到共同父層）。
- **Global**: 整個 App 都在乎。

### 3. URL as State (URL 即狀態)
這常被忽略。如果使用者重新整理頁面後，狀態應該保留（如搜尋關鍵字、分頁、篩選條件），那麼 URL 才是這個狀態的 Source of Truth，而不是 Store。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Server State Management (React Query / SWR)
不要再用 Redux 存取 API 資料。手動處理 loading, error, caching, deduping 非常痛苦且容易出錯。
- **Pattern**: 使用 `useQuery` 處理讀取，`useMutation` 處理寫入。
- **Benefit**: 自動處理快取失效（Invalidation）與背景更新（Refetch on focus）。
- **Rule**: Server State 應該被視為一個 Cache，而不是 Global Store。

### 2. Atomic State for High-Frequency Updates (Zustand / Jotai)
當你需要跨組件共享狀態，且該狀態更新頻率很高（例如：拖拉操作、畫布縮放、即時儀表板）時，Context API 會導致嚴重的效能問題（因為所有 Consumer 都會重繪）。
- **Pattern**: 使用 Zustand 或 Jotai 建立外部 Store。
- **Benefit**: 透過 Selector 機制 (`useStore(state => state.value)`)，只有真正依賴該數值的組件會重繪。

### 3. Context for Dependency Injection & Low-Velocity Data
Context 最適合用於「很少改變」的全域設定，或是「複合組件（Compound Components）」之間的通訊。
- **Pattern**: Theme, User Auth Info, Toast Notification Config.
- **Best Practice**: 將 Context 分拆。不要把所有東西塞進一個 `AppContext`。使用 `useContext` 搭配 `useReducer` 可以模擬輕量級的 Redux，但要注意效能。

### 4. URL Params for Shareable State
- **Pattern**: 將篩選器（Filters）、排序（Sort）、分頁（Pagination）狀態同步到 URL Search Params。
- **Tool**: `react-router-dom` 的 `useSearchParams` 或 Next.js 的 `useRouter`。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Syncing State" Trap (狀態同步陷阱)
試圖將 Server State 複製一份到 Client State (useState/Redux) 中，然後用 `useEffect` 保持同步。
- **Bad**: `useEffect(() => { setLocalData(serverData) }, [serverData])`
- **Consequence**: 造成兩次 Render，且容易產生資料不一致（Source of Truth 衝突）。
- **Fix**: 直接在 Render 期間使用 Server Data，或使用 Derived State (計算屬性)。

### 2. Overusing Context for Everything (濫用 Context)
將 Context 當作全能的 State Manager。
- **Pitfall**: 當 Context Value 是一個大物件時，只要物件中任何一個屬性改變，**所有**使用該 Context 的組件都會 Re-render，即使它們只用到了沒變的屬性。
- **Fix**: Split Contexts (將讀與寫分開，或將不同領域分開)，或改用 Zustand 等支援 Selector 的庫。

### 3. Prop Drilling Madness (屬性鑽孔)
將 props 往下傳遞超過 3-4 層。
- **Fix**: 使用 Component Composition (將組件作為 `children` 傳遞)，這樣中間層就不需要知道 props 的存在；或者使用 Context/Store。

### 4. Premature Optimization with Redux (過早引入 Redux)
在專案初期就引入 Redux Toolkit，結果發現 90% 的資料都是 Server State，剩下的 10% 用 `useState` 就夠了。
- **Advice**: Start simple. Only add complexity when pain points arise.

---

## Checklists & workflows｜檢查清單與流程

在決定要把狀態放在哪裡時，請使用此決策樹（Decision Tree）：

### Decision Tree: Where should this state live?

1.  **Is this data from the Server?** (API response)
    -   [Yes] -> **React Query / SWR / Apollo** (Do not put in Redux/Context).
    -   [No] -> Go to step 2.

2.  **Should the state persist on page reload or be shareable via link?** (URL)
    -   [Yes] -> **URL Search Params / Route Params**.
    -   [No] -> Go to step 3.

3.  **Is the state used by only one component?**
    -   [Yes] -> **Local State (`useState` / `useReducer`)**.
    -   [No] -> Go to step 4.

4.  **Is the state used by a few sibling components?**
    -   [Yes] -> **Lift State Up** (Move `useState` to common parent) or **Component Composition**.
    -   [No] -> Go to step 5.

5.  **Is the state Global (app-wide)?**
    -   **Low Frequency** (Theme, Auth, Language) -> **React Context**.
    -   **High Frequency / Complex Logic** (Data visualization, Complex Forms, Interactive UI) -> **Zustand / Redux Toolkit / Jotai**.

### Implementation Checklist
- [ ] 我是否區分了 Server State 與 Client State？
- [ ] 我是否避免了在 `useEffect` 中同步狀態？
- [ ] 如果使用 Context，我是否確認過 Re-render 的影響範圍？
- [ ] 我的篩選條件（Filters）是否可以透過複製貼上 URL 來分享？
- [ ] 我是否移除了不必要的 Global State，將狀態保持在最小必要範圍（Co-location）？

---

## Real-world examples｜實戰案例

### Scenario A: E-commerce Dashboard (電商後台)

這是一個典型的混合場景，我們來拆解它的狀態分佈：

1.  **User Profile & Permissions**:
    -   **Strategy**: `Context API` (or a lightweight auth store).
    -   **Reason**: 登入後很少改變，全域都需要知道使用者權限。

2.  **Product List (Table Data)**:
    -   **Strategy**: `React Query`.
    -   **Reason**: 這是 Server State。需要快取、分頁、Loading 狀態。
    -   *Code Snippet*: `const { data, isLoading } = useQuery(['products', page], fetchProducts)`

3.  **Table Search & Filters**:
    -   **Strategy**: `URL Search Params`.
    -   **Reason**: 使用者重新整理後，應該停留在原本的篩選結果；方便分享連結給同事。

4.  **Add Product Modal (Open/Close)**:
    -   **Strategy**: `Local State (useState)` or `Zustand` (if triggered from far away).
    -   **Reason**: UI 狀態，不需要持久化。

### Scenario B: Complex Multi-step Form (複雜分步表單)

例如：保險申請流程或購物車結帳。

1.  **Form Data (跨步驟共享)**:
    -   **Strategy**: `Zustand` or `Redux Toolkit`.
    -   **Reason**: 
        -   資料需要在組件卸載（Unmount）後保留（切換步驟時組件會消失）。
        -   Context 效能較差，且邏輯容易與 UI 耦合。
        -   外部 Store 可以更方便地將驗證邏輯（Validation Logic）抽離 UI。

2.  **Draft Saving (自動儲存草稿)**:
    -   **Strategy**: `React Query mutation` + `debounce`.
    -   **Reason**: 將 Store 中的資料定期同步回 Server。

```javascript
// Pseudo-code: Zustand Store for Form
import { create } from 'zustand'

const useFormStore = create((set) => ({
  step: 1,
  formData: { name: '', email: '', plan: 'basic' },
  setField: (field, value) => set((state) => ({ 
    formData: { ...state.formData, [field]: value } 
  })),
  nextStep: () => set((state) => ({ step: state.step + 1 })),
}))

// Component
function Step1() {
  // Selector prevents re-renders if 'step' changes but 'formData' doesn't
  const name = useFormStore((state) => state.formData.name)
  const setField = useFormStore((state) => state.setField)
  
  return <input value={name} onChange={e => setField('name', e.target.value)} />
}
```