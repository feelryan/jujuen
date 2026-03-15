# 常見反模式與壞味道 / Common Anti-Patterns & Code Smells

在 React 開發中，許多「壞味道」並非導致程式崩潰的直接錯誤，而是導致維護成本指數上升、效能低落或資料流難以追蹤的架構缺陷。本章節專注於識別這些模式，並提供重構的具體路徑。

In React development, "code smells" are often architectural flaws that lead to high maintenance costs, poor performance, or untraceable data flows, rather than immediate crashes. This chapter focuses on identifying these patterns and providing concrete refactoring paths.

---

## Mental model｜心智模型

### 1. 宣告式 vs. 命令式思維 (Declarative vs. Imperative)
許多反模式源於試圖在 React 的宣告式模型中強行套用命令式邏輯。
- **正確心智**：UI 是狀態的純函數映射 (`UI = f(State)`)。你不需要「告訴」React 去更新什麼，你只需要改變狀態，React 會處理剩下的事。
- **錯誤心智**：當 A 發生時，手動去修改 B，再觸發 C。這通常會導致 `useEffect` 連鎖反應。

### 2. 資料流向的純粹性 (Purity of Data Flow)
React 的資料流應該像瀑布一樣單向流動。
- **反模式**：像是在瀑布中間裝馬達試圖把水打回去（雙向綁定、過度的 Parent callback），或是把水管接得太長（Prop Drilling）。
- **目標**：讓資料來源（Source of Truth）單一化，並讓衍生資料（Derived State）即時計算，而非同步儲存。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 衍生狀態計算 (Derived State Calculation)
永遠不要將「可以透過現有 props 或 state 計算出來的值」存入另一個 state。

**Good:**
```javascript
function Cart({ items }) {
  // ✅ 直接計算，每次 render 時都會執行
  // Calculate directly; runs on every render
  const total = items.reduce((sum, item) => sum + item.price, 0); 
  
  return <div>Total: {total}</div>;
}
```

**Bad:**
```javascript
function Cart({ items }) {
  const [total, setTotal] = useState(0);

  // ❌ 冗餘且容易不同步
  // Redundant and prone to desynchronization
  useEffect(() => {
    setTotal(items.reduce((sum, item) => sum + item.price, 0));
  }, [items]);

  return <div>Total: {total}</div>;
}
```

### 2. 組件組合 (Component Composition)
解決 Prop Drilling 最優雅的方式通常不是 Context，而是改變組件的結構。利用 `children` 或 Render Props 將組件「提升」到擁有資料的層級。

**Pattern:** `Lift Content Up`
如果不希望中間層組件知道它傳遞了什麼，就將具體的子組件作為 `props` 傳入。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The `useEffect` Chain (Effect 連鎖反應)
這是現代 React 最常見的壞味道。一個 Effect 更新狀態，觸發另一個 Effect，再更新另一個狀態。這會導致 Race Conditions 和極難除錯的流程。

- **識別方式**：你發現需要畫一張流程圖才能解釋資料怎麼從 A 變到 B 再變到 C。
- **解決方案**：將邏輯移入 Event Handlers 或使用 Derived State。

### 2. Prop Drilling (屬性鑽探)
將資料穿過多層不需要該資料的中間組件。
- **後果**：中間組件變得脆弱，重構困難，且容易造成不必要的 re-render。
- **解決方案**：
  1. **Composition (優先)**：傳遞組件而非資料 (Pass components, not data)。
  2. **Context API**：適用於全域設定 (Theme, User, Locale)。
  3. **Server State Tools** (React Query/SWR)：直接在需要的組件層級獲取資料，跳過傳遞。

### 3. God Components (上帝組件)
一個檔案超過 300-500 行，包含大量的 `useState`、`useEffect` 和複雜的 JSX。
- **特徵**：通常包含多個不相關的業務邏輯（例如同時處理表單驗證、資料獲取和 UI 動畫）。
- **解決方案**：
  - **Custom Hooks**：將邏輯抽離 (e.g., `useFormLogic`, `useDataFetching`)。
  - **Sub-components**：將 UI 拆分。

### 4. Defining Components Inside Components (在組件內定義組件)
這是一個嚴重的效能與 UX 殺手。

**Bad:**
```javascript
function Parent() {
  // ❌ 每次 Parent render 時，Child 都會被視為一個全新的組件函數
  // Every time Parent renders, Child is treated as a brand new component function
  function Child() { 
    return <div>I will lose focus and state on every parent render</div>;
  }

  return <Child />;
}
```
- **後果**：React 會在每次父組件渲染時 Unmount 再 Remount 子組件。Input 會失去焦點 (focus)，內部 State 會重置。
- **修正**：將 `Child` 移到 `Parent` 外部。

### 5. Side Effects in Render (渲染過程中的副作用)
在組件主體（Render phase）中直接修改 DOM、變更 ref 或呼叫 API。

**Bad:**
```javascript
function BadComponent({ data }) {
  // ❌ 絕對禁止：在 render 過程中執行副作用
  // Strictly forbidden: Side effects during render
  document.title = data.title; 
  saveToLocalStorage(data); 

  return <div>...</div>;
}
```
- **修正**：移至 `useEffect` 或 Event Handlers。

---

## Checklists & workflows｜檢查清單與流程

在 Code Review 或重構時，請使用此清單檢查組件健康度：

### State & Effects 審查
- [ ] **是否有多餘的 State？** 能否透過 props 或其他 state 計算得出？如果是，刪除該 state。
- [ ] **是否濫用 `useEffect`？** 這個 Effect 是為了「同步資料」嗎？如果是，嘗試改為 Derived State 或 Event Handler。
- [ ] **Effect 依賴是否誠實？** `dependency array` 是否包含了所有用到的變數？如果使用了 `eslint-disable-line`，通常代表邏輯有問題。

### Component Structure 審查
- [ ] **是否有 Prop Drilling？** 資料是否穿過了 3 層以上的中間層？考慮使用 Composition 或 Context。
- [ ] **組件定義位置？** 是否有任何組件是在另一個組件內部定義的？請移到外部。
- [ ] **職責單一性？** 組件是否同時處理「資料獲取」和「複雜 UI 呈現」？考慮拆分為 Container/Presentational 或使用 Custom Hooks。

### Performance & Safety
- [ ] **Object/Array 參考穩定性？** 傳遞給 `memo` 子組件或 `useEffect` 的物件/陣列是否每次 render 都重新建立？(考慮 `useMemo`)。
- [ ] **Render 純粹性？** 確保函數主體沒有直接修改外部變數或 DOM。

---

## Real-world examples｜實戰案例

### Case 1: 避免 Effect Chaining (表單連動)

**情境**：使用者選擇「國家」後，自動選擇該國家的第一個「城市」。

**❌ Anti-Pattern (Imperative / Effect-based):**
這會導致兩次 Render（一次改國家，Effect 觸發後改城市）。
```javascript
function LocationForm() {
  const [country, setCountry] = useState('US');
  const [city, setCity] = useState('NY');

  // 當 country 改變時，命令式地去修改 city
  useEffect(() => {
    setCity(getCapital(country));
  }, [country]);

  return (
    <select onChange={e => setCountry(e.target.value)} value={country} />
    // ...
  );
}
```

**✅ Best Practice (Event-driven / Co-location):**
將邏輯放在觸發變化的源頭（Event Handler）。這只會導致一次 Render（React 18+ 自動批次處理）。
```javascript
function LocationForm() {
  const [country, setCountry] = useState('US');
  const [city, setCity] = useState('NY');

  const handleCountryChange = (e) => {
    const newCountry = e.target.value;
    setCountry(newCountry);
    // 在同一個事件中處理相關邏輯
    // Handle related logic in the same event
    setCity(getCapital(newCountry)); 
  };

  return (
    <select onChange={handleCountryChange} value={country} />
    // ...
  );
}
```

### Case 2: 解決 Prop Drilling (Layout Wrapper)

**情境**：一個 `Dashboard` 頁面需要將 `user` 資料傳遞給深層的 `Avatar`。

**❌ Anti-Pattern (Drilling):**
`Header` 和 `Nav` 不需要知道 `user` 是什麼，卻被迫傳遞它。
```javascript
<Dashboard user={user} />
  -> <Header user={user} />
     -> <Nav user={user} />
        -> <Avatar user={user} /> // 終於到了
```

**✅ Best Practice (Composition):**
將 `Avatar` 在最上層就組裝好，透過 `props` 傳遞下去。
```javascript
function Dashboard({ user }) {
  // 這裡直接傳遞組件，而非資料
  // Pass the component, not the data
  return (
    <Header 
      navSlot={<Nav avatarSlot={<Avatar user={user} />} />} 
    />
  );
}

// Header 只需要負責佈局
function Header({ navSlot }) {
  return <header>{navSlot}</header>;
}
```