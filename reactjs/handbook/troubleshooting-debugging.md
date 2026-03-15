# 除錯工具與故障排除流程 / Troubleshooting & Debugging Workflow

## Mental model｜心智模型

在 React 中進行除錯，與傳統的命令式編程（Imperative Programming）除錯有所不同。你必須將思維從「追蹤程式碼執行的每一行」轉變為「分析狀態快照與渲染週期」。

### 1. UI = f(state) 的逆向工程
React 的核心公式是 $UI = f(state)$。當 UI 出現 Bug 時，問題通常出在：
- **State/Props 錯誤**：輸入資料不正確。
- **Component Logic ($f$) 錯誤**：轉換邏輯有誤。
- **Synchronization 錯誤**：副作用（Effects）與狀態不同步。

除錯的過程就是**逆向工程**：從錯誤的 UI 現象，回推是哪一次 Render Cycle 的 State 異常，或是哪一個 Effect 造成了非預期的副作用。

### 2. 渲染是「快照」而非「連續劇」 (Rendering as Snapshots)
每一次 Render 都是獨立的快照。當你看到變數值「不對」時，通常是因為你正在查看「舊的快照」（Stale Closure）或是「尚未發生的未來」。
- **Debugging Mindset**: 不要只問「現在變數是多少？」，要問「這是**第幾次** Render？這一次 Render 裡的 Scope 是什麼？」

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 善用 React DevTools 的進階功能
不要只把 DevTools 當作查看 DOM 的工具，它是查看 Component Tree 與 State 的顯微鏡。

- **Highlight Updates**: 開啟「Highlight updates when components render」。這是最快發現「非預期渲染」的方法。
- **Filter Components**: 在 DevTools 設定中過濾掉雜訊（如 Context Providers, Styled Components），專注於業務邏輯組件。
- **Inspect Props/State/Hooks**: 直接在樹狀圖中修改 Props 或 State，測試組件對不同資料的反應（Resilience testing）。

### 2. 效能分析：Profiler 優先 (Measure, Don't Guess)
遇到效能問題時，憑直覺優化（Premature Optimization）是禁忌。

- **Record & Analyze**: 使用 Profiler 錄製操作過程。
- **Flamegraph (火焰圖)**: 尋找寬度最寬的 Bar（耗時最長）。灰色代表未渲染，有色代表有渲染。
- **Ranked Chart**: 直接列出該次 Commit 中最耗時的組件。
- **"Why did this render?"**: 在 Profiler 設定中開啟此選項，滑鼠移到組件上會顯示重繪原因（例如：`Props changed: [user]`）。

### 3. 系統性隔離法 (Systematic Isolation)
當組件樹龐大時，使用 **Binary Search Strategy**（二分搜尋法）來定位問題。
- 暫時註解掉一半的 Child Components。
- 如果 Bug 消失，問題在那一半；如果還在，問題在這一半。
- 重複此步驟直到鎖定單一組件。

### 4. Custom Hooks 的除錯支援
對於複雜的 Custom Hooks，使用 `useDebugValue` 來讓內部狀態在 DevTools 中顯示更友善的標籤，而不是顯示為匿名的 `State` 或 `Effect`。

```javascript
function useOnlineStatus() {
  const isOnline = ...;
  // 在 DevTools 顯示 "OnlineStatus: Online"
  useDebugValue(isOnline ? 'Online' : 'Offline');
  return isOnline;
}
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Console.log 散彈槍 (Console Spraying)
- **Bad**: 在 render body 中寫滿 `console.log`。這會因為 React 的 Strict Mode（開發環境執行兩次）或高頻率渲染而產生大量雜訊，甚至導致瀏覽器卡頓。
- **Good**: 使用 `useEffect` 監聽特定變數變化時才 log，或是使用 DevTools 的斷點。

### 2. 忽視依賴陣列警告 (Ignoring Dependency Warnings)
- **Bad**: 看到 ESLint 警告 `react-hooks/exhaustive-deps` 時，直接 disable 規則。這是導致 **Stale Closure**（讀取到舊變數）的頭號原因。
- **Good**: 修正依賴關係。如果依賴導致無限迴圈，通常意味著你的 `useEffect` 邏輯需要拆分，或是需要 `useCallback` 包裹依賴的函式。

### 3. 誤判渲染原因 (Misinterpreting Re-renders)
- **Bad**: 認為「只要用 `memo` 包起來就不會重繪」。
- **Pitfall**: 如果 Props 傳入的是每次都重新產生的 Object 或 Function（且未被 memoize），`React.memo` 完全無效。
- **Fix**: 檢查父層是否傳入了不穩定的 reference。

### 4. 在 Render Phase 執行副作用
- **Bad**: 在 component function body 內直接發送 API request 或修改 DOM。
- **Consequence**: 導致不可預測的行為、無限迴圈或 UI 閃爍。
- **Fix**: 嚴格遵守副作用必須在 `useEffect` 或 Event Handlers 中執行。

---

## Checklists & workflows｜檢查清單與流程

### 🐛 General Bug Investigation Checklist
當功能不如預期時，請依序檢查：

- [ ] **Console Errors**: 是否有紅字錯誤？（React 的錯誤訊息通常很精準）。
- [ ] **DevTools Inspection**:
    - 組件是否真的 Render 了？
    - Props 和 State 的值是否符合預期？
    - Hooks 的順序是否在多次 Render 中保持一致？
- [ ] **Data Flow**:
    - 資料是從哪裡變壞的？（API 回傳？Reducer 處理？Parent 傳入？）
- [ ] **Strict Mode**:
    - 關閉 Strict Mode 後問題是否消失？（如果是，代表你的組件不純粹，有副作用洩漏）。

### 🚀 Performance Tuning Checklist
當畫面卡頓或延遲時：

- [ ] **Build Mode**: 永遠在 **Production Build** 下測試效能（Development mode 慢很多）。
- [ ] **Profiler Check**:
    - 找出渲染時間 > 16ms 的組件。
    - 檢查是否有不必要的渲染（Rendered but DOM didn't change）。
- [ ] **Context Check**: 是否因為 Context Value 變更，導致所有 Consumers 強制重繪？
- [ ] **Reference Stability**:
    - 傳給 Child Component 的 `onClick` 是否有用 `useCallback`？
    - 傳給 Child Component 的 `style={{...}}` 或 `options={[]}` 是否導致 reference 每次都變？

---

## Real-world examples｜實戰案例

### Case 1: The "Infinite Loop" Trap (無限迴圈陷阱)

**情境**：頁面載入後 CPU 飆高，瀏覽器卡死。
**原因**：在 `useEffect` 中設定了 state，但該 state 又是 dependency。

```javascript
// ❌ Anti-pattern: Infinite Loop
useEffect(() => {
  // 每次 count 改變 -> 觸發 effect -> 設定 count -> 觸發 render -> 觸發 effect...
  setCount(count + 1);
}, [count]);

// ✅ Fix: 使用 functional update 或移除依賴（視邏輯而定）
useEffect(() => {
  const timer = setInterval(() => {
    setCount(c => c + 1); // 不需要依賴 count
  }, 1000);
  return () => clearInterval(timer);
}, []);
```

### Case 2: The "Why Did You Render?" (不明原因重繪)

**情境**：一個列表項目 `ListItem` 已經被 `React.memo` 包裹，但在輸入框打字時，列表依然全部重繪，導致打字延遲。

**除錯流程**：
1. 開啟 Profiler，勾選 "Record why each component rendered"。
2. 執行打字操作，停止錄製。
3. 查看 `ListItem`，提示顯示：`Props changed: (onClick)`。

**根因**：父組件在 Render 時每次都產生新的匿名函式。

```javascript
// ❌ Parent Component
function Parent() {
  const [text, setText] = useState('');
  // 每次 Parent render，這個 function 都是新的記憶體位置
  const handleDelete = (id) => { ... };

  return (
    <>
      <input value={text} onChange={e => setText(e.target.value)} />
      <List onItemClick={handleDelete} />
    </>
  );
}

// ✅ Fix: useCallback
const handleDelete = useCallback((id) => { ... }, []);
```

### Case 3: Stale Closure in Event Listeners (過時的閉包)

**情境**：在 `useEffect` 中綁定 `window` 事件，但在事件 callback 中讀取到的 state 永遠是初始值。

**原因**：Closure 在綁定時「捕獲」了當時的變數環境，之後沒有更新。

```javascript
// ❌ Stale Closure
useEffect(() => {
  const handleResize = () => {
    console.log(currentData); // 永遠印出初始值，因為 effect 只跑了一次
  };
  window.addEventListener('resize', handleResize);
  return () => window.removeEventListener('resize', handleResize);
}, []); // 依賴是空的，導致 handleResize 永遠引用第一次 render 的 scope

// ✅ Fix 1: 加依賴 (會導致頻繁綁定/解綁)
// useEffect(..., [currentData]);

// ✅ Fix 2: 使用 Ref (Mutable) 來保持最新值
const dataRef = useRef(currentData);
useEffect(() => { dataRef.current = currentData; }, [currentData]);

useEffect(() => {
  const handleResize = () => {
    console.log(dataRef.current); // 讀取 Ref，永遠是新的
  };
  window.addEventListener('resize', handleResize);
  return () => window.removeEventListener('resize', handleResize);
}, []);
```