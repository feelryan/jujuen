# 測試策略與程式碼品質
# Testing Strategy & Code Quality

## 1. 前言與學習目標
## 1. Introduction & Learning Objectives

對於資深工程師而言，測試不僅僅是為了追求程式碼覆蓋率（Code Coverage），更是為了確保重構時的信心與系統的長期可維護性。本章將超越基礎的 `jest` 語法，深入探討現代 React 生態系中的測試哲學。
For senior engineers, testing is not just about chasing code coverage metrics; it is about ensuring confidence during refactoring and maintaining long-term system stability. This chapter moves beyond basic `jest` syntax to explore the testing philosophy in the modern React ecosystem.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **掌握行為驅動測試（Behavior-Driven Testing）：** 理解為何 React Testing Library (RTL) 取代了 Enzyme，並學會如何測試「使用者行為」而非「實作細節」。
    **Master Behavior-Driven Testing:** Understand why React Testing Library (RTL) superseded Enzyme, and learn how to test "user behavior" rather than "implementation details."
2.  **設計穩健的 Mocking 策略：** 使用 Mock Service Worker (MSW) 在網路層級攔截請求，避免脆弱的 API mocking，並建立更貼近真實環境的整合測試。
    **Design Robust Mocking Strategies:** Use Mock Service Worker (MSW) to intercept requests at the network layer, avoiding brittle API mocking and creating integration tests that closely mimic real environments.
3.  **整合 Accessibility (a11y) 於測試流程：** 利用 `jest-axe` 與 RTL 的 `getByRole` 查詢優先原則，將無障礙設計視為程式碼品質的一環。
    **Integrate Accessibility (a11y) into Testing:** Leverage `jest-axe` and RTL's `getByRole` query priority to treat accessibility as an integral part of code quality.
4.  **優化測試金字塔（Testing Pyramid）：** 在前端領域中，理解為何「測試獎盃（Testing Trophy）」模型通常比傳統金字塔更有效。
    **Optimize the Testing Pyramid:** Understand why the "Testing Trophy" model is often more effective than the traditional pyramid in the frontend domain.

---

## 2. 核心觀念與心智模型
## 2. Core Concepts & Mental Model

### 2.1 測試獎盃 vs. 測試金字塔
### 2.1 The Testing Trophy vs. The Testing Pyramid

傳統後端開發常推崇「測試金字塔」（大量 Unit Tests，少量 E2E）。但在 React 前端開發中，Kent C. Dodds 提出的「測試獎盃（Testing Trophy）」更為適用。
Traditional backend development often advocates the "Testing Pyramid" (heavy on Unit Tests, light on E2E). However, in React frontend development, the "Testing Trophy" model proposed by Kent C. Dodds is often more applicable.

-   **心智模型：** 想像你在驗證一台車。單元測試是檢查「螺絲是否鎖緊」；整合測試是檢查「引擎啟動時輪子是否會轉」；E2E 是「實際開上路」。在 UI 開發中，元件之間的互動（整合）往往比單一函式的邏輯更易出錯且更具價值。
-   **Mental Model:** Imagine validating a car. Unit tests check if "the screws are tight"; integration tests check if "the wheels turn when the engine starts"; E2E is "driving on the road." In UI development, the interaction between components (integration) is often more error-prone and valuable than the logic of a single function.

### 2.2 實作細節 vs. 使用者行為
### 2.2 Implementation Details vs. User Behavior

這是 React Testing Library (RTL) 的核心哲學。
This is the core philosophy of React Testing Library (RTL).

-   **實作細節 (Implementation Details):** 測試元件內部的 `state` 名稱、方法的名稱，或是特定的 CSS class。這些東西改變時（重構），使用者介面可能看起來一樣，但測試卻會失敗（False Negative）。
-   **Implementation Details:** Testing internal `state` names, method names, or specific CSS classes. When these change (refactoring), the UI might look the same, but tests fail (False Negative).
-   **使用者行為 (User Behavior):** 測試使用者看得到的東西（文字、按鈕）以及互動方式（點擊、輸入）。
-   **User Behavior:** Testing what the user sees (text, buttons) and how they interact (clicks, inputs).

### 2.3 網路層 Mocking (Network Level Mocking)
### 2.3 Network Level Mocking

-   **傳統做法：** Mock `axios.get` 或 `window.fetch`。這導致測試與特定的請求函式庫耦合。
-   **Traditional Approach:** Mocking `axios.get` or `window.fetch`. This couples tests to specific request libraries.
-   **現代做法 (MSW):** 使用 Service Worker 在網路層攔截請求。你的元件程式碼完全不知道它被 Mock 了，這提供了最高級別的信心。
-   **Modern Approach (MSW):** Using Service Workers to intercept requests at the network layer. Your component code has no idea it's being mocked, providing the highest level of confidence.

---

## 3. 實務場景與系統設計視角
## 3. Real-World & System Design View

### 3.1 CI/CD Pipeline 中的角色
### 3.1 Role in CI/CD Pipeline

在大型系統設計中，測試策略直接影響部署頻率與穩定性。
In large-scale system design, testing strategy directly impacts deployment frequency and stability.

-   **Unit/Integration (Jest/Vitest + RTL):** 執行速度快，應在每次 Commit 或 PR 時執行。它們負責守門（Gatekeeping），防止邏輯回歸。
-   **Unit/Integration (Jest/Vitest + RTL):** Fast execution; should run on every Commit or PR. They act as gatekeepers to prevent logic regression.
-   **E2E (Playwright/Cypress):** 執行成本高且較慢。通常安排在 Merge 後的 Staging 環境，或作為 Nightly Build 的一部分，專注於 Happy Path 與關鍵商業流程。
-   **E2E (Playwright/Cypress):** High cost and slow execution. Usually scheduled in the Staging environment after Merge, or as part of a Nightly Build, focusing on Happy Paths and critical business flows.

### 3.2 可維護性與重構
### 3.2 Maintainability & Refactoring

資深工程師在設計元件庫或複雜頁面時，會優先考慮「可測試性」。
Senior engineers prioritize "testability" when designing component libraries or complex pages.

-   **Dependency Injection (DI):** 雖然 React 不像 Angular 強調 DI，但在測試時，透過 `Context` 或 `Props` 注入依賴（如 API Client、Logger），能讓測試更容易隔離環境。
-   **Dependency Injection (DI):** While React emphasizes DI less than Angular, injecting dependencies (like API Clients, Loggers) via `Context` or `Props` makes it easier to isolate environments during testing.
-   **Accessibility as a Contract:** 將 a11y 視為系統設計的一部分。如果測試依賴 `getByRole('button', { name: 'Submit' })`，這不僅測試了功能，也保證了螢幕閱讀器使用者能存取該功能。
-   **Accessibility as a Contract:** Treat a11y as part of the system design. If a test relies on `getByRole('button', { name: 'Submit' })`, it not only tests functionality but also ensures screen reader accessibility.

---

## 4. 逐步示例：非同步資料載入與 MSW
## 4. Walkthrough: Async Data Fetching with MSW

我們將示範如何測試一個「使用者列表」元件，該元件會從 API 撈取資料並處理 Loading 與 Error 狀態。
We will demonstrate how to test a "User List" component that fetches data from an API and handles Loading and Error states.

### 4.1 待測試元件 (The Component)
### 4.1 The Component under Test

```tsx
// UserList.tsx
import React, { useEffect, useState } from 'react';

export const UserList = () => {
  const [users, setUsers] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetch('/api/users')
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch');
        return res.json();
      })
      .then((data) => setUsers(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div role="status">Loading...</div>;
  if (error) return <div role="alert">{error}</div>;

  return (
    <ul>
      {users.map((user: any) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
};
```

### 4.2 設置 Mock Service Worker (MSW)
### 4.2 Setting up Mock Service Worker (MSW)

不要 Mock `fetch`，而是定義網路攔截規則。
Do not mock `fetch`; instead, define network interception rules.

```ts
// mocks/handlers.ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/users', () => {
    return HttpResponse.json([
      { id: 1, name: 'Alice' },
      { id: 2, name: 'Bob' },
    ]);
  }),
];
```

### 4.3 編寫測試 (Writing the Test)
### 4.3 Writing the Test

這是一個標準的資深級測試寫法：關注狀態變化與使用者可見內容。
This is a standard senior-level test approach: focusing on state transitions and user-visible content.

```tsx
// UserList.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { UserList } from './UserList';
import { server } from './mocks/server'; // MSW server setup
import { http, HttpResponse } from 'msw';

// 確保測試前後重置 handlers
// Ensure handlers are reset before/after tests
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test('renders users after successful fetch', async () => {
  render(<UserList />);

  // 1. 驗證 Loading 狀態 (User Behavior)
  // 1. Verify Loading state (User Behavior)
  expect(screen.getByRole('status')).toHaveTextContent(/loading/i);

  // 2. 等待資料載入完成
  // 2. Wait for data loading to complete
  // findByRole is async and waits for the element to appear (default 1000ms)
  const userItem = await screen.findByText('Alice');
  expect(userItem).toBeInTheDocument();
  expect(screen.getByText('Bob')).toBeInTheDocument();

  // 3. 確保 Loading 消失
  // 3. Ensure Loading disappears
  expect(screen.queryByRole('status')).not.toBeInTheDocument();
});

test('handles server error gracefully', async () => {
  // Override handler specifically for this test
  server.use(
    http.get('/api/users', () => {
      return new HttpResponse(null, { status: 500 });
    })
  );

  render(<UserList />);

  // 驗證 Error 訊息 (Accessibility: role="alert" is crucial)
  // Verify Error message (Accessibility: role="alert" is crucial)
  const alert = await screen.findByRole('alert');
  expect(alert).toHaveTextContent(/failed to fetch/i);
});
```

### 4.4 為什麼這樣做更好？
### 4.4 Why is this better?

1.  **Resilience:** 如果我們將 `fetch` 換成 `axios` 或 `react-query`，測試**完全不需要修改**。
    **Resilience:** If we switch `fetch` to `axios` or `react-query`, the tests require **zero changes**.
2.  **Accessibility:** 使用 `getByRole('status')` 和 `getByRole('alert')` 強制我們在程式碼中使用正確的語意標籤，提升了產品品質。
    **Accessibility:** Using `getByRole('status')` and `getByRole('alert')` forces us to use correct semantic HTML tags in the code, improving product quality.
3.  **Simplicity:** 沒有複雜的 `jest.spyOn` 或 `mockImplementation`，程式碼閱讀起來就像使用者的操作劇本。
    **Simplicity:** No complex `jest.spyOn` or `mockImplementation`; the code reads like a user interaction script.

---

## 5. 常見錯誤與反模式
## 5. Common Pitfalls & Anti-patterns

### 5.1 濫用 `act(...)`
### 5.1 Misusing `act(...)`

-   **錯誤：** 手動將所有渲染邏輯包裹在 `act()` 中。
-   **Pitfall:** Manually wrapping all render logic in `act()`.
-   **原因：** RTL 的 helper (如 `render`, `userEvent`) 內部已經整合了 `act`。如果你看到 `act` 警告，通常是因為你在測試中觸發了狀態更新但沒有 `await` 它（例如，沒有等待 Promise resolve）。
-   **Why:** RTL helpers (like `render`, `userEvent`) already integrate `act`. If you see `act` warnings, it's usually because you triggered a state update in the test but didn't `await` it (e.g., not waiting for a Promise to resolve).
-   **修正：** 使用 `waitFor` 或 `findBy*` 查詢來等待 UI 穩定。
-   **Fix:** Use `waitFor` or `findBy*` queries to wait for the UI to stabilize.

### 5.2 過度使用 `getByTestId`
### 5.2 Overusing `getByTestId`

-   **錯誤：** 到處加 `data-testid="submit-btn"`。
-   **Pitfall:** Adding `data-testid="submit-btn"` everywhere.
-   **原因：** 這是一個逃生艙（Escape Hatch）。它無法保證使用者能找到按鈕，也無法驗證按鈕是否可被輔助科技存取。
-   **Why:** This is an escape hatch. It doesn't guarantee the user can find the button, nor does it verify the button is accessible to assistive technology.
-   **修正：** 優先順序應為：`getByRole` > `getByLabelText` > `getByPlaceholderText` > `getByText` > `getByTestId`。
-   **Fix:** Priority should be: `getByRole` > `getByLabelText` > `getByPlaceholderText` > `getByText` > `getByTestId`.

### 5.3 淺層渲染 (Shallow Rendering)
### 5.3 Shallow Rendering

-   **錯誤：** 堅持只渲染 Parent Component，Mock 所有 Child Components。
-   **Pitfall:** Insisting on rendering only the Parent Component and mocking all Child Components.
-   **原因：** 這在 Enzyme 時代很流行，但它隱藏了整合問題。如果 Child Component 的 props 介面改了，Parent 的測試仍然會通過，但在 Production 會崩潰。
-   **Why:** Popular in the Enzyme era, but it hides integration issues. If a Child Component's props interface changes, the Parent's test still passes, but it crashes in Production.
-   **修正：** 盡量進行完整渲染（Full Rendering）。如果 Child 太重，才考慮針對性 Mock。
-   **Fix:** Prefer Full Rendering. Only consider targeted mocking if the Child is excessively heavy.

---

## 6. 面試與實務問答切入點
## 6. Interview & Discussion Hooks

### Q1: 你如何處理 React 應用中的「Flaky Tests（不穩定測試）」？
### Q1: How do you handle "Flaky Tests" in a React application?

-   **高分回答要點：**
    *   **識別原因：** 大多數 flaky tests 來自於非同步操作處理不當（例如固定的 `setTimeout` vs 動態的 `waitFor`）或測試間的狀態污染。
    *   **隔離性：** 強調在 `afterEach` 清理 Mock 和 DOM（RTL 自動處理 DOM 清理，但 Global state/MSW 需要手動重置）。
    *   **確定性：** 使用 Mock Data（如 MSW）而非真實 API，確保數據一致性。
    *   **CI 策略：** 設定重試機制（Retries）作為短期解法，但必須標記並修復根本原因。

### Q2: 為什麼我們應該優先使用 `getByRole` 而不是 `getByTestId` 或 CSS Selector？
### Q2: Why should we prioritize `getByRole` over `getByTestId` or CSS Selectors?

-   **高分回答要點：**
    *   **模擬使用者：** 使用者（及螢幕閱讀器）是透過角色（按鈕、標題）和名稱來識別元素，而非 HTML 結構或 ID。
    *   **隱式 A11y 測試：** 如果 `getByRole('button', { name: 'Save' })` 失敗，意味著你的應用程式對視障使用者來說可能是不可用的。這將 Accessibility 測試左移（Shift Left）到了開發階段。
    *   **抗脆性（Resilience）：** CSS class 經常變動，但語意化標籤（Semantic HTML）相對穩定。

### Q3: 在大型專案中，你會如何架構測試的 Providers (Redux, Router, Theme)？
### Q3: How do you structure test Providers (Redux, Router, Theme) in a large project?

-   **高分回答要點：**
    *   **Custom Render：** 建立一個自定義的 `render` 函式（wrapper），將所有必要的 Global Providers (Redux Store, ThemeProvider, IntlProvider) 封裝進去。
    *   **Override 能力：** 該 wrapper 應允許測試案例傳入特定的 initial state 或 mock store，以便測試特定情境。
    *   **避免重複：** 不要讓每個測試檔案都重複寫 `<Provider store={store}>...</Provider>`。

---

## 7. 小結與後續延伸
## 7. Summary & Next Steps

### 重點回顧
### Key Takeaways

1.  **信心優先：** 測試的目的是為了讓你敢於在週五下午部署程式碼。
2.  **RTL 哲學：** 測試使用者行為，而非實作細節。如果重構程式碼導致測試失敗（但功能正常），那就是個壞測試。
3.  **MSW 是標準：** 在網路層級攔截請求是現代前端測試的最佳實踐，解耦了 HTTP Client 實作。
4.  **A11y 即品質：** 善用 `getByRole` 與 `jest-axe`，讓無障礙設計成為開發流程的自然產物。
5.  **整合測試 > 單元測試：** 在 UI 開發中，元件間的協作往往比單一函式的運算更重要。

### 後續延伸
### Next Steps

-   **進階：** 學習如何使用 **Playwright** 進行跨瀏覽器的 E2E 測試，並與 RTL 的單元測試策略互補。
-   **效能：** 下一章將探討 **React 效能優化 (Performance Optimization)**，了解如何測量渲染效能以及如何避免不必要的 Re-renders。