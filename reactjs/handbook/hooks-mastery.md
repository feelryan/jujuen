# Hooks 實戰機制與陷阱 / Hooks Mastery: Mechanics & Pitfalls

## Mental model｜心智模型

在精通 Hooks 之前，必須先修正對 React 運作機制的認知。從 Class Components 轉移到 Hooks 並不僅是語法糖的改變，而是思維模式從「生命週期（Lifecycle）」轉向「同步（Synchronization）」與「快照（Snapshot）」的過程。

### 1. 渲染即快照 (Rendering as a Snapshot)
每一次的 Render 都有它自己獨立的 Props、State 與 Event Handlers。
- **Closure is King**: Component 函數內的變數（包含 props 和 state）在該次渲染中是「常數」。
- `useEffect` 也是該次渲染的一部分，它「捕獲」了該次渲染時的變數狀態。
- **Mental Shift**: 不要去想「當這個變數改變時，執行那個函數」，而是要想「在這次渲染中，這個 Effect 依賴了哪些值」。

### 2. 同步而非生命週期 (Synchronization, not Lifecycle)
`useEffect` 的設計初衷不是為了模擬 `componentDidMount` 或 `componentDidUpdate`，而是為了讓 Component 的狀態與外部系統（DOM、Network、Subscription）保持**同步**。
- **Question**: "How do I sync my component with this external data source?"
- **Not**: "How do I run this code only once?"

### 3. 依賴陣列是誠實的聲明 (Dependency Array is a Statement of Fact)
Dependency Array (`deps`) 不是讓你控制 Effect 何時執行的「開關」，而是告訴 React 你的 Effect 依賴了哪些 Scope 內的變數。
- **Rule**: 如果你的 Effect 用到了某個變數，它就必須在 `deps` 裡。
- **Consequence**: 如果你對 React 說謊（遺漏依賴），就會導致 **Stale Closures**（閉包過期），讀取到舊的資料。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 優先使用 Derived State (衍生狀態)
最常見的錯誤是用 `useEffect` 來觀察 A 的變化並設定 B。這會導致額外的 Render pass。
- **Bad Pattern**:
  ```javascript
  const [firstName, setFirstName] = useState('John');
  const [lastName, setLastName] = useState('Doe');
  const [fullName, setFullName] = useState('');

  useEffect(() => {
    setFullName(`${firstName} ${lastName}`); // 觸發第二次 Render
  }, [firstName, lastName]);
  ```
- **Best Practice**: 直接在 Render 過程中計算。
  ```javascript
  const fullName = `${firstName} ${lastName}`; // 零額外成本，自動更新
  ```

### 2. Event Handlers vs. Effects
區分「使用者行為」與「同步行為」。
- 如果邏輯是因為**使用者點擊**而觸發（例如送出表單、導航），請寫在 Event Handler 中。
- 如果邏輯是因為**狀態改變**而必須發生（例如連線 Socket、同步 Document Title），請寫在 `useEffect` 中。

### 3. Functional State Updates
當 Effect 依賴於當前的 State 來計算下一個 State 時，使用 Functional Update 可以移除對該 State 的依賴，避免不必要的 Effect 重新執行。
- **Pattern**: `setCount(c => c + 1)` instead of `setCount(count + 1)`.

### 4. Ref 作為「逃生艙」 (Refs as Escape Hatches)
當你需要讀取最新值但**不想**觸發 Effect 重新執行時（例如 Event Listener 或 Timer），使用 `useRef` 來保存最新狀態。
- **Use Case**: 在 `useEffect` 的 cleanup function 或非同步 callback 中讀取最新的 props/state。

### 5. Custom Hooks 封裝原則
不要只為了「共用」而寫 Custom Hook，要為了「隱藏複雜度」與「語意化」而寫。
- **原則**: Custom Hook 應該封裝副作用（Effects）與狀態邏輯，並暴露出乾淨的 API（Data & Methods）。
- **命名**: 必須以 `use` 開頭，這不僅是慣例，更是 Linter 檢查 Rules of Hooks 的依據。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The Stale Closure Trap (過期閉包陷阱)
這是 Hooks 最險惡的坑。當你為了「不想讓 Effect 跑太多次」而故意在 `deps` 中遺漏變數時，Effect 內部的 Closure 會鎖住定義當下的變數值，永遠不會更新。

### 2. Object/Function Dependencies (不穩定的依賴)
將物件或函數放入 `deps` 卻沒有用 `useMemo` 或 `useCallback` 包裹。
- **後果**: 每次 Render 都會產生新的 reference，導致 `useEffect` 每次都執行，甚至引發無限迴圈（如果 Effect 內部又更新了 State）。
- **Fix**: 對依賴的物件做 Memoization，或將物件移出 Component 外部（如果是靜態常數）。

### 3. Race Conditions in Data Fetching
在 `useEffect` 中發送請求，但沒有處理「請求返回順序」或「Component Unmount」。
- **Pitfall**: 快速切換 ID，舊的請求比新的請求晚回來，導致 UI 顯示錯誤的資料。
- **Fix**: 使用 `AbortController` 或 `isMounted` flag pattern。

### 4. Over-optimization with useMemo/useCallback
不要預設所有東西都包 `useMemo`。
- **代價**: Memoization 本身有記憶體與比較運算的成本。
- **時機**: 只有當該變數被用作 `useEffect` 的依賴，或是傳遞給被 `React.memo` 包裹的子組件時，才需要使用。

---

## Checklists & workflows｜檢查清單與流程

在 Code Review 或提交程式碼前，請依照此清單檢查 Hooks 的使用：

### Dependency Integrity Check
- [ ] **ESLint 是否通過？** 絕對不要使用 `// eslint-disable-next-line react-hooks/exhaustive-deps`，除非你完全理解自己在做什麼（通常你不需要）。
- [ ] **依賴是否穩定？** `deps` 裡的物件或函數是否在每次 Render 時都會變更 Reference？如果是，請使用 `useMemo`/`useCallback`。

### Effect Logic Check
- [ ] **這是副作用嗎？** 這段邏輯是為了「同步」還是「響應使用者操作」？如果是後者，移到 Event Handler。
- [ ] **是否造成瀑布流渲染？** 是否在 Effect 裡設定 State，而該 State 又能直接由 Props 計算得出？
- [ ] **Cleanup 是否完善？** 如果建立了訂閱（Subscription）、計時器（Timer）或監聽器（Listener），是否有回傳 cleanup function？

### Custom Hook Design
- [ ] **抽象層級是否一致？** Hook 是否隱藏了實作細節（如 `useEffect`），只暴露業務邏輯所需的資料與操作？
- [ ] **是否處理了 Loading/Error 狀態？** 非同步操作的 Hook 應回傳 `{ data, loading, error }` 結構。

---

## Real-world examples｜實戰案例

### Case 1: 修正 setInterval 的 Stale Closure

**❌ 錯誤寫法 (The Bug)**
```javascript
function Timer() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      console.log(count); // 永遠印出 0，因為 Closure 捕獲了第一次 render 的 count
      setCount(count + 1); // 永遠設定為 0 + 1
    }, 1000);
    return () => clearInterval(id);
  }, []); // 謊報依賴：其實依賴了 count，但為了不想重設 timer 而省略
}
```

**✅ 正確寫法 A: Functional Update (推薦)**
```javascript
  useEffect(() => {
    const id = setInterval(() => {
      setCount(c => c + 1); // 不依賴外部 count 變數
    }, 1000);
    return () => clearInterval(id);
  }, []); // 安全的空依賴
```

**✅ 正確寫法 B: The Ref Pattern (進階)**
當你需要讀取最新 state 但不想重啟 Effect (例如 Event Listener)：
```javascript
  const savedCallback = useRef(callback);

  // 1. 每次 render 都更新 ref
  useEffect(() => {
    savedCallback.current = callback;
  });

  // 2. Effect 只跑一次，但讀取的是 ref (mutable)
  useEffect(() => {
    function tick() {
      savedCallback.current();
    }
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);
```

### Case 2: 處理 Data Fetching Race Condition

**❌ 潛在 Bug**
```javascript
useEffect(() => {
  fetch(`/api/user/${id}`).then(data => setUser(data));
}, [id]);
// 如果 id 從 1 變 2，但請求 1 比請求 2 晚回來，UI 會顯示 id=2 的標題但 id=1 的資料。
```

**✅ 正確寫法: Cleanup Flag**
```javascript
useEffect(() => {
  let ignore = false;

  async function fetchData() {
    const result = await fetch(`/api/user/${id}`);
    if (!ignore) {
      setUser(result);
    }
  }

  fetchData();

  return () => {
    ignore = true; // Cleanup function runs before the next effect or unmount
  };
}, [id]);
```