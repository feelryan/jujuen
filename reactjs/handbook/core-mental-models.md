# 核心心智模型：渲染週期與不可變性 / Core Mental Models: Render Cycle & Immutability

## Mental model｜心智模型

要精通 React，必須放棄「命令式（Imperative）」修改 UI 的習慣，轉而擁抱「聲明式（Declarative）」與「快照（Snapshot）」思維。

### 1. UI = f(state) 與 渲染快照 (The Render Snapshot)
React 組件在每次渲染時，就像是當下狀態的一張**快照（Snapshot）**。
- **Render is not "Live":** 組件函數內的 `props` 和 `state` 在該次渲染中是**常數**。
- **Event Handlers belong to the render:** 即使是 `onClick` 函數，它捕捉到的也是該次渲染時的 state 值（Closure）。
- **Mental Shift:** 不要問「現在變數變成什麼了？」，要問「在這次渲染的快照中，變數是什麼？」。

### 2. 渲染階段 vs. 提交階段 (Render Phase vs. Commit Phase)
React 的更新流程分為兩個截然不同的階段，理解這點對於處理副作用（Side Effects）至關重要：
1.  **Render Phase (The "Calculation"):**
    - React 呼叫你的組件函數。
    - 比較新舊 Virtual DOM (Reconciliation)。
    - **特徵：** 純粹計算 (Pure calculation)，可能會被暫停、中止或重複執行。**絕對禁止在此階段產生副作用（如 API call, DOM 操作）。**
2.  **Commit Phase (The "Application"):**
    - React 實際操作 DOM（插入、更新、刪除）。
    - 執行 `useLayoutEffect` 與 `useEffect`。
    - **特徵：** 這裡才是 UI 真正改變與副作用發生的地方。

### 3. 不可變性與參考相等性 (Immutability & Reference Equality)
React 如何知道何時該重新渲染？它依賴 `Object.is()` 進行**淺層比較 (Shallow Comparison)**。
- **The Trigger:** 只有當 `prevProp !== nextProp` 或 `prevState !== nextState`（記憶體位址改變）時，React 才會認定資料已變更。
- **Mutation is invisible:** 如果你直接修改物件內容 (`obj.name = 'new'`) 但保留原物件參考，React 會認為「什麼都沒變」，進而不觸發渲染。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 衍生狀態模式 (Derived State Pattern)
最常見的錯誤是透過 `useEffect` 來同步兩個 state。最佳實務是在 Render 過程中直接計算。

- **Bad (Syncing state):**
  ```javascript
  const [items, setItems] = useState([...]);
  const [count, setCount] = useState(0);

  useEffect(() => {
    setCount(items.length); // 觸發額外的 Render
  }, [items]);
  ```
- **Good (Derived state):**
  ```javascript
  const [items, setItems] = useState([...]);
  const count = items.length; // 在 Render 階段直接計算，零成本，無額外 Render
  ```

### 2. 狀態更新函數 (Functional State Updates)
當新的 state 依賴於舊的 state 時，始終使用 callback 形式。這能確保你拿到的是最新的「待處理狀態」，而非當前閉包中的舊快照。

- **Pattern:**
  ```javascript
  // 安全的做法，特別是在非同步操作或多次更新中
  setCount(prev => prev + 1);
  ```

### 3. 強制重置模式 (Key Reset Pattern)
利用 `key` 屬性的變化來告訴 React：「這是一個全新的組件，請銷毀舊的並重新掛載（Remount）」，而不是嘗試更新它。這在重置表單或動畫時非常有用。

- **Pattern:**
  ```javascript
  // 當 userId 改變時，Profile 組件會完全重置（state 歸零，useEffect 重新執行）
  <Profile key={userId} userId={userId} />
  ```

### 4. 巢狀物件的不可變更新 (Immutable Updates for Nested Objects)
對於深層物件，必須複製每一層被修改的路徑。

- **Pattern (Spread syntax):**
  ```javascript
  setUser(prev => ({
    ...prev,
    preferences: {
      ...prev.preferences,
      theme: 'dark' // 只有這一層和其父層的 reference 改變
    }
  }));
  ```
- **Pattern (Immer):** 在複雜狀態下，建議使用 `useImmer` 或 Redux Toolkit，它允許你寫出 Mutable 的語法但產出 Immutable 的結果。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 直接突變狀態 (Direct State Mutation)
這是 React 新手最致命的錯誤。直接修改陣列或物件，React 的 Diff 演算法會因為 Reference 沒變而忽略更新。

- **Anti-pattern:**
  ```javascript
  const handleAdd = () => {
    users.push(newUser); // ❌ 修改了原陣列
    setUsers(users);     // ❌ Reference 相同，React 不會重新渲染
  };
  ```
- **Fix:** `setUsers([...users, newUser]);`

### 2. 期待 State 立即改變 (Expecting Immediate State Updates)
忘記 State 更新是「非同步」且基於「快照」的。

- **Anti-pattern:**
  ```javascript
  const handleClick = () => {
    setCount(count + 1);
    console.log(count); // ❌ 這裡印出的仍然是舊的 count (0)，而非 1
    someApiCall(count); // ❌ 送出的是舊值
  };
  ```
- **Fix:** 使用 `useEffect` 監聽變化，或在 event handler 中直接使用計算後的值傳給 API。

### 3. Props 到 State 的不必要複製 (Mirroring Props in State)
將 props 複製給 state 初始值，導致後續 props 更新時，state 卻「卡」在舊值。

- **Anti-pattern:**
  ```javascript
  function EmailInput({ email }) {
    const [value, setValue] = useState(email); // ❌ 只有第一次 render 會讀取 email
    // 如果父層改變了 email prop，這裡的 value 不會更新
    return <input value={value} onChange={...} />;
  }
  ```
- **Fix:** 直接使用 props，或者如果需要編輯，配合 `key` 屬性重置組件，或使用 `useEffect` 同步（但優先考慮 Key Reset）。

---

## Checklists & workflows｜檢查清單與流程

在處理渲染問題或狀態邏輯時，請使用此清單：

### 🛑 Debugging: 為什麼沒有重新渲染？ (Why didn't it re-render?)
- [ ] 我是否使用了 `.push()`, `.splice()` 或直接賦值 `obj.x = y`？(檢查 Immutability)
- [ ] 我是否回傳了相同的 Reference？(例如 `return state` 在 reducer 中)
- [ ] 組件是否被 `React.memo` 包裹，且 props 包含了一個每次 render 都重新建立的 function 或 object？

### 🛑 Debugging: 為什麼渲染次數過多？ (Why too many re-renders?)
- [ ] 我是否在 Render Phase (函數本體) 裡設定了 State？(這會導致無限迴圈)
- [ ] 我是否在 `useEffect` 中依賴了一個物件/陣列，但沒有用 `useMemo` 固定它？(導致 Effect 頻繁觸發)
- [ ] 我是否可以改用 **Derived State** 而不是 `useEffect` + `setState`？

### ✅ Design: 狀態設計決策
- [ ] **Can I calculate it?** 如果可以從現有的 props 或 state 計算出來，**絕對不要**把它變成新的 state。
- [ ] **Is it UI state or Server state?** 如果是 Server data，考慮使用 React Query / SWR，而不是手動 `useEffect` fetch。

---

## Real-world examples｜實戰案例

### 案例一：購物車數量的「快照陷阱」
在一個「加入購物車」的功能中，如果使用者快速點擊，閉包陷阱會導致數量計算錯誤。

```javascript
// ❌ Buggy Version
// 如果使用者在一秒內點擊三次，count 只會加 1，因為三次點擊時的 count 都是 0
const handleAdd = () => {
  setTimeout(() => {
    setCount(count + 1); 
  }, 1000);
};

// ✅ Correct Version
// 使用 Functional Update 確保拿到的是最新的 pending state
const handleAdd = () => {
  setTimeout(() => {
    setCount(prevCount => prevCount + 1);
  }, 1000);
};
```

### 案例二：過濾列表的 Derived State
不需要為了「搜尋過濾」創建一個 `filteredList` state。

```javascript
// ❌ Anti-pattern: Redundant State & Effect
const [search, setSearch] = useState('');
const [list, setList] = useState(allData);
const [filtered, setFiltered] = useState(allData);

useEffect(() => {
  setFiltered(list.filter(i => i.includes(search)));
}, [search, list]); // 容易漏掉 dependency，且多一次 render pass

// ✅ Best Practice: Derived State
const [search, setSearch] = useState('');
const [list, setList] = useState(allData);

// 在 Render 過程中直接計算
// 如果計算昂貴，才包上 useMemo
const filtered = useMemo(() => {
  return list.filter(i => i.includes(search));
}, [list, search]);
```

### 案例三：利用 Key 重置表單
當使用者切換不同的 `userId` 編輯資料時，你需要清除表單內的髒資料。

```javascript
function UserProfileEditor({ userId }) {
  // ❌ 這種寫法很痛苦，需要 useEffect 監聽 userId 來 reset state
  const [name, setName] = useState('');
  useEffect(() => setName(''), [userId]); 
  
  // ...
}

// ✅ Parent Component
// 當 userId 改變，React 會移除舊的 Editor，掛載一個全新的 Editor
// State 自動初始化，無需手動 reset
function App() {
  return <UserProfileEditor key={userId} userId={userId} />;
}
```