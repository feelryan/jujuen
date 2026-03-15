# 測試策略：行為驅動與 RTL / Testing Strategy: Behavior-Driven & RTL

## Mental model｜心智模型

### 1. 黑箱測試與使用者視角 (The Black Box & User Perspective)
在 React Testing Library (RTL) 的哲學中，測試程式碼應該模擬「使用者」如何與你的應用程式互動，而不是模擬「開發者」如何編寫程式碼。
- **Don't:** 檢查組件內部的 State 變數是否為 `true`，或是某個 method 是否被呼叫。
- **Do:** 檢查畫面上是否出現了特定的文字、按鈕是否可點擊、或是錯誤訊息是否彈出。

想像你在測試一台微波爐：
- **實作細節測試 (Implementation Detail):** 拆開外殼，檢查電路板上的電壓是否為 5V。如果電路設計改了但功能沒變，測試就會失敗（False Negative）。
- **行為驅動測試 (Behavior-Driven):** 按下「加熱」按鈕，檢查食物是否變熱。只要結果正確，內部電路如何重構都不影響測試通過。

### 2. 信心指數 (Confidence Coefficient)
測試的核心價值在於提供信心。
> *"The more your tests resemble the way your software is used, the more confidence they can give you."* — Kent C. Dodds
> (你的測試越像軟體被使用的方式，它們能給你的信心就越多。)

如果測試全過，但使用者無法使用，那測試就是無效的。RTL 強制你寫出能反映真實使用情境的測試。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 優先使用 `getByRole` (Prioritize `getByRole`)
這是 RTL 的黃金法則。`getByRole` 最接近使用者（以及螢幕閱讀器）感知頁面的方式。
- **Best:** `screen.getByRole('button', { name: /submit/i })`
- **Good:** `screen.getByLabelText(/email/i)` (針對表單)
- **Okay:** `screen.getByText(/welcome/i)` (針對非互動元素)
- **Last Resort:** `screen.getByTestId('custom-element')` (僅在無法透過語意選取時使用)

### 2. 使用 `user-event` 取代 `fireEvent` (Use `user-event` over `fireEvent`)
`fireEvent` 只是單純觸發 DOM 事件，而 `user-event` 會模擬瀏覽器的真實行為。
- 例如：當使用者在 input 打字時，`user-event` 會依序觸發 focus, keydown, input, keyup 等事件，這更能抓出真實世界的 bug。

### 3. 避免過度 Mocking (Avoid Over-Mocking)
不要 Mock 你的子組件 (Child Components)，除非它們是極重的第三方套件或尚未實作的功能。
- **Integration over Unit:** 在 React 中，測試父組件連同子組件一起渲染的結果（Integration Test），通常比單獨測試每個小組件更有價值。
- **Mock Boundaries:** 只 Mock 邊界（例如 API 請求、Local Storage、瀏覽器 API），使用 **MSW (Mock Service Worker)** 來攔截網路請求是目前的業界標準。

### 4. 非同步斷言的正確姿勢 (Handling Async Assertions)
React 的狀態更新是非同步的。
- 使用 `findBy...` 來等待元素出現（內建 retry 機制）。
- 使用 `waitFor(() => expect(...))` 來等待特定的斷言通過。
- **Pattern:** `await screen.findByRole('alert')` 優於 `await waitFor(() => screen.getByRole('alert'))`。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 測試實作細節 (Testing Implementation Details)
- **Bad:** 使用 Enzyme 風格的 wrapper 來存取 `wrapper.state('isLoading')`。
- **Bad:** 測試組件內部的 function 名稱。
- **Consequence:** 重構程式碼（Refactoring）時，功能沒壞但測試全紅（Brittle Tests）。

### 2. 濫用 `act(...)` (Abusing `act`)
通常你不需要手動呼叫 `act`。如果你看到 `act` 警告，通常是因為：
- 你在測試結束後還有 State Update（例如未清理的 `useEffect` 或未等待的 Promise）。
- 你使用了 `fireEvent` 而非 `user-event`（`user-event` v14+ 自動包裹了 act）。
- **Fix:** 確保在斷言之前，所有的非同步操作都已經 settle（例如使用 `findBy` 或 `waitFor`）。

### 3. 使用 `querySelector` 或 Class Name (Querying by Class/ID)
- **Bad:** `container.querySelector('.submit-btn')`
- **Why:** CSS class 是為了樣式，不是為了功能。如果設計師改了 class name，測試不該失敗。

### 4. 巢狀的 `waitFor` (Nested `waitFor`)
- **Bad:** 在 `waitFor` callback 裡面做 side effect (如 user click)。
- **Rule:** `waitFor` 裡面只放 **斷言 (Assertion)**。Side effect 應該在 `waitFor` 之前發生。

---

## Checklists & workflows｜檢查清單與流程

### 🧪 測試撰寫決策樹 (Test Authoring Decision Tree)

當你要選取一個元素時，請依序問自己：
1. **Is it interactive?** (按鈕、連結、標題) -> 用 `getByRole`。
2. **Is it a form input?** -> 用 `getByLabelText`。
3. **Is it just text?** -> 用 `getByText`。
4. **Does it have alt text?** (圖片) -> 用 `getByAltText`。
5. **None of the above?** -> 加上 `data-testid` 屬性並用 `getByTestId` (但在 Code Review 時需解釋為何無法使用語意標籤)。

### ✅ PR 自我檢查清單 (PR Checklist)

- [ ] **Accessibility Check:** 我的測試是否使用了 `getByRole`？這能順便驗證 A11y 屬性是否正確。
- [ ] **User Simulation:** 我是否使用了 `userEvent.setup()` 來模擬操作？
- [ ] **Async Handling:** 是否正確使用了 `await screen.findBy...` 來處理載入後的 UI 變化？
- [ ] **No Implementation Leak:** 我是否完全沒有測試 `state`、`props` 或 `class methods`？
- [ ] **Clean Up:** 每個測試案例是否獨立？（Mock 是否在 `afterEach` 重置？）

---

## Real-world examples｜實戰案例

### 情境：非同步資料載入與錯誤處理 (Async Data Fetching & Error Handling)

這是一個標準的「載入使用者列表」測試，涵蓋了 Loading 狀態、API Mocking (MSW)、以及成功/失敗的 UI 驗證。

```javascript
// 假設我們使用 MSW 來 Mock API
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UserList } from './UserList';
import { server } from './mocks/server';
import { rest } from 'msw';

describe('UserList Integration', () => {
  // Setup user-event instance
  const user = userEvent.setup();

  test('renders users after fetching', async () => {
    render(<UserList />);

    // 1. 驗證初始 Loading 狀態 (User Behavior: 看到載入中)
    // 使用 queryBy 因為元素可能稍後消失，或者用 getBy 確保它存在
    expect(screen.getByText(/loading/i)).toBeInTheDocument();

    // 2. 等待非同步資料渲染 (User Behavior: 等待資料出現)
    // findBy 會自動重試直到 timeout，適合非同步
    const userItem = await screen.findByRole('heading', { name: /Alice/i });
    expect(userItem).toBeInTheDocument();

    // 3. 驗證 Loading 消失
    expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
  });

  test('handles server error gracefully', async () => {
    // Override default mock for this specific test
    server.use(
      rest.get('/api/users', (req, res, ctx) => {
        return res(ctx.status(500));
      })
    );

    render(<UserList />);

    // 驗證錯誤訊息出現
    const errorMsg = await screen.findByRole('alert');
    expect(errorMsg).toHaveTextContent(/failed to fetch/i);
    
    // 驗證重試按鈕功能
    const retryBtn = screen.getByRole('button', { name: /retry/i });
    await user.click(retryBtn);
    
    // 再次驗證 loading 出現 (代表重試邏輯有被觸發)
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });
});
```

### 關鍵點解析 (Key Takeaways):
1.  **Role-based Queries:** 使用 `heading`, `button`, `alert` 來選取元素，確保語意正確。
2.  **Async Flow:** 使用 `findBy` 處理 API 回傳的時間差，不使用硬編碼的 `setTimeout`。
3.  **Mocking:** 透過 MSW 控制網路層，讓測試專注於 UI 如何回應資料，而非測試 fetch 本身。