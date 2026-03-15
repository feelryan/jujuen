# 渲染效能優化與 Memoization / Rendering Performance & Memoization

## Mental model｜心智模型

在深入優化之前，必須建立正確的 React 渲染心智模型。許多效能問題源於對「React 何時以及為何重新渲染」的誤解。

### 1. 渲染不等於 DOM 更新 (Render $\neq$ Commit)
React 的運作分為兩個階段：
- **Render Phase (渲染階段)**：React 呼叫你的組件函式，計算出 Virtual DOM tree。
- **Commit Phase (提交階段)**：React 比較新舊 Virtual DOM (Diffing)，並將差異應用到真實 DOM 上。

**關鍵觀念**：組件 Re-render 是很常見且廉價的。只有當 Diffing 發現差異並觸發 DOM 操作時，成本才高。我們優化的目標通常是 **「避免不必要的 Render Phase 計算」**，或者是 **「當 Render 計算成本過高時進行快取」**。

### 2. 預設行為：連鎖反應 (The Default Chain Reaction)
React 的預設行為是：**當父組件 Re-render 時，其所有子組件也會無條件 Re-render**（除非使用了 `React.memo`）。
這與 Props 是否改變無關。這是一個遞迴過程。

### 3. 穩定性原則 (Stability Principle)
Memoization (`useMemo`, `useCallback`, `React.memo`) 的核心在於 **「維持參照恆定 (Referential Stability)」**。
- 如果你傳給子組件的 Props（物件或函式）在每次父組件 Render 時都是新的記憶體位址，那麼子組件的 `React.memo` 就會失效。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 優先使用結構優化 (Structure over Memoization)
在撒上 `useMemo` 之前，先檢查是否能透過重構解決。

- **State Colocation (狀態下移)**：如果只有頁面的一小部分需要更新（例如 Input 欄位），將 State 移到該特定組件內，避免觸發整頁 Re-render。
- **Component Composition (組件組合)**：利用 `children` prop 將昂貴的組件傳遞下去。
  ```jsx
  // ❌ Bad: ColorPicker 更新會導致 ExpensiveTree Re-render
  <div style={{ color }}>
    <ColorPicker onChange={setColor} />
    <ExpensiveTree />
  </div>

  // ✅ Good: ExpensiveTree 作為 prop 傳遞，React 知道它沒變，不會 Re-render
  <ColorPickerWrapper>
    <ExpensiveTree />
  </ColorPickerWrapper>
  ```

### 2. 正確使用 `React.memo`
僅在以下情況使用 `React.memo` 包裹組件：
- 該組件渲染成本高（包含大量運算或複雜 DOM 結構）。
- 該組件經常在 Props 未變動的情況下被父組件強制 Re-render。
- **重要**：確保傳入的 Props 是 Primitive type 或具有穩定的 Reference。

### 3. `useMemo` 與 `useCallback` 的黃金法則
不要為了「預防」而到處使用。它們本身也有執行成本。
- **useMemo**：
  1. 用於快取昂貴計算（例如：過濾/排序大型陣列）。
  2. 用於確保物件/陣列的 Reference 穩定，以作為 `useEffect` 的依賴或傳給 `memo` 的子組件。
- **useCallback**：
  1. 唯一用途：確保函式 Reference 穩定，以傳給 `memo` 的子組件或作為 Hooks 依賴。

### 4. 列表虛擬化 (Virtualization / Windowing)
當需要渲染長列表（數百或數千筆資料）時，DOM 節點數量是效能殺手。
- 使用 `react-window` 或 `react-virtuoso`。
- 僅渲染使用者「可視範圍」內的項目。

### 5. Code Splitting & Lazy Loading
減少初始 Bundle Size，加快 First Contentful Paint (FCP)。
- 使用 `React.lazy` 和 `Suspense` 針對 Route 層級或大型 Modal/Widget 進行拆分。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 虛假的 Memoization (The Broken Memo)
這是最常見的錯誤。使用了 `React.memo`，但 Props 卻是不穩定的。

```jsx
// ❌ Anti-pattern
const Parent = () => {
  // 每次 render 都會產生新的 inline object 和 inline function
  return <MemoizedChild style={{ color: 'red' }} onClick={() => {}} />;
};
```
**後果**：`MemoizedChild` 每次都會比較 Props，發現不同，然後 Re-render。你付出了比較的成本，卻沒得到快取的好處（Double penalty）。

### 2. 到處使用 `useMemo` (Premature Optimization)
對簡單的計算（如 `a + b` 或簡單的 `map`）使用 `useMemo`。
**後果**：記憶體佔用增加，程式碼複雜度上升，且 React 內部的依賴檢查可能比你的計算還慢。

### 3. Context Hell 導致的全域更新
將頻繁變動的資料（如 User typing input）放入 Context，且該 Context 被大量組件訂閱。
**後果**：打一個字，整個 App 的消費者組件都 Re-render。
**解法**：分割 Context，或使用 Recoil/Zustand 等支援 Atomic updates 的狀態管理庫。

### 4. 在 Render Scope 內定義組件
```jsx
const Parent = () => {
  // ❌ 絕對禁止：每次 Parent render，Child 都是一個「全新的組件定義」
  const Child = () => <div>...</div>;
  return <Child />;
};
```
**後果**：React 會完全卸載舊的 Child 並掛載新的，導致狀態遺失和極差的效能。

---

## Checklists & workflows｜檢查清單與流程

在決定優化之前，請遵循此流程：

### Optimization Workflow
1. **Measure First (先測量)**：使用 React DevTools Profiler 錄製操作。
2. **Identify Bottlenecks (找瓶頸)**：找出標示為黃色/紅色的組件，或渲染時間過長的 commit。
3. **Analyze "Why did this render?" (分析原因)**：在 Profiler 中查看組件 Re-render 的原因（Hooks changed, Parent rendered, etc.）。

### Decision Checklist
- [ ] **是否真的慢？** 使用者能感覺到延遲嗎？（< 16ms 通常不需要優化）。
- [ ] **是否可以下移 State？** 將變動隔離在葉節點組件。
- [ ] **是否可以使用 Composition？** 透過 `children` prop 傳遞靜態內容。
- [ ] **Context 是否過大？** 是否需要拆分 Context 以隔離變動？
- [ ] **列表是否過長？** 超過 50-100 個複雜項目？考慮 Virtualization。
- [ ] **使用 `React.memo` 前的檢查：**
    - [ ] 組件是否經常在 Props 不變時 Re-render？
    - [ ] 傳入的 Props 是否包含不穩定的 Object/Array/Function？
    - [ ] 如果有，是否已正確使用 `useMemo`/`useCallback` 包裹父層變數？

---

## Real-world examples｜實戰案例

### Case 1: 表格篩選器的效能陷阱 (The Filter List Trap)

**情境**：一個包含複雜篩選器和大型資料表格的頁面。每次在篩選器輸入文字，表格都會卡頓。

**問題代碼 (Pseudo-code)**：
```jsx
function Dashboard() {
  const [filters, setFilters] = useState({});
  const [data, setData] = useState(largeData);

  // ❌ 每次 Dashboard render，getFilteredData 都會重新執行
  // 即使只是切換了一個無關的 UI tab
  const visibleData = getFilteredData(data, filters); 

  return (
    <>
      <Filters onChange={setFilters} />
      <DataTable items={visibleData} /> {/* DataTable 即使 memo 也會更新，因為 items 參照變了 */}
    </>
  );
}
```

**優化方案**：
```jsx
function Dashboard() {
  const [filters, setFilters] = useState({});
  const [data, setData] = useState(largeData);

  // ✅ 1. 使用 useMemo 快取昂貴計算
  const visibleData = useMemo(() => {
    return getFilteredData(data, filters);
  }, [data, filters]); // 只有資料或篩選條件變動才重算

  // ✅ 2. 確保傳給子組件的 callback 穩定
  const handleFilterChange = useCallback((newFilters) => {
    setFilters(newFilters);
  }, []);

  return (
    <>
      <Filters onChange={handleFilterChange} />
      <DataTable items={visibleData} />
    </>
  );
}
// 假設 DataTable 和 Filters 已經被 React.memo 包裹
```

### Case 2: 巨型表單的輸入延遲 (Laggy Large Form)

**情境**：一個很長的設定頁面，包含數十個區塊。使用者在最上方的「專案名稱」輸入時感到明顯延遲。

**診斷**：`ProjectNameInput` 的 `onChange` 更新了最上層的 `FormState`，導致下方所有 `HeavySection` 全部 Re-render。

**優化方案 (Composition)**：
不要把所有 State 都放在頂層，或者利用 Composition 隔離渲染。

```jsx
// ✅ 優化前：所有東西都在一起
// <FormContainer> -> updates state -> re-renders <HeavySection />

// ✅ 優化後：隔離變動
const FormContainer = () => {
  return (
    <Layout>
      <Header>
        {/* 只有 ProjectNameInput 會因為自己的 state 變動而 render */}
        <ProjectNameInput /> 
      </Header>
      <Body>
        {/* 這些靜態組件不會受到 Header 輸入的影響 */}
        <HeavySectionA />
        <HeavySectionB />
      </Body>
    </Layout>
  );
};
```
如果必須共享 State，考慮使用 `Context` + `React.memo`，或是將 `HeavySection` 包裹在 `React.memo` 中，並確保傳遞給它的 props 都是穩定的。