# 測試策略與品質保證 / Testing Strategies & Quality Assurance

## Mental model｜心智模型

在 Node.js 的環境中，測試不僅僅是驗證程式碼的正確性，更是**對非同步行為與邊界副作用（Side Effects）的控制權管理**。

### 1. The Testing Trophy vs. The Pyramid (測試獎盃 vs. 金字塔)
傳統的測試金字塔強調大量的單元測試（Unit Tests）。但在 Node.js 後端開發（特別是 Microservices 或 API 服務）中，**整合測試（Integration Tests）** 往往能提供更高的 ROI（投資報酬率）。
- **Unit Tests**: 驗證單一函式或類別的邏輯。想像你在檢查「這根水管是否漏水」。
- **Integration Tests**: 驗證模組間的互動（例如 API Route -> Controller -> Service -> DB）。想像你在檢查「水管接起來後，水是否能順利流過且壓力正常」。
- **Mental Shift**: 不要過度執著於 Mock 所有依賴。對於 Database 或 Cache，使用 Docker 啟動真實的實例通常比 Mock SQL 查詢更有價值且維護成本更低。

### 2. Control Time & I/O (控制時間與 I/O)
Node.js 是 I/O 密集的。測試的核心挑戰在於如何將「不確定的 I/O」轉化為「確定性的輸入輸出」。
- **Mocking**: 是為了隔離外部不穩定因素（如第三方 API、Email 發送），而不是為了隔離你自己的程式碼邏輯。
- **Async/Await**: 測試程式碼本身就是非同步的。測試框架（如 Jest/Mocha）需要知道「什麼時候結束」。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. The "AAA" Pattern with Async (非同步的 AAA 模式)
所有的測試案例都應遵循 **Arrange（準備） -> Act（執行） -> Assert（斷言）** 的結構。在 Node.js 中，`Act` 階段通常涉及 `await`。

```javascript
test('should create a user and return 201 status', async () => {
  // Arrange: 準備資料與 Mock
  const userData = { name: 'Alice', email: 'alice@example.com' };
  emailService.sendWelcomeEmail.mockResolvedValue(true); // Mock 外部依賴

  // Act: 執行邏輯 (await is crucial here)
  const response = await request(app).post('/users').send(userData);

  // Assert: 驗證結果與副作用
  expect(response.status).toBe(201);
  expect(response.body.id).toBeDefined();
  expect(emailService.sendWelcomeEmail).toHaveBeenCalledWith(userData.email);
});
```

### 2. Dependency Injection for Testability (依賴注入以利測試)
Node.js 的模組系統（CommonJS/ESM）容易導致硬編碼依賴（Hard-coded dependencies）。為了方便 Mocking，應使用依賴注入（DI）或工廠模式。

- **Bad (Hard to mock):**
  ```javascript
  // userService.js
  const db = require('./db'); // 直接 require，測試時難以替換
  exports.createUser = async (user) => { ... }
  ```
- **Good (Easy to mock):**
  ```javascript
  // userService.js
  module.exports = (db) => ({ // 透過參數注入依賴
    createUser: async (user) => { ... }
  });
  ```

### 3. Integration Testing with `supertest` (使用 supertest 進行整合測試)
不要只測試 Controller 的函式，直接測試 HTTP 層。這能確保 Middleware、Route parsing 和 Error handling 都正常運作。

- 啟動一個 ephemeral (短暫的) server 實例，而不是連到 production server。
- 配合 Docker (如 `testcontainers`) 啟動真實的 Database 進行測試，測試結束後銷毀資料。

### 4. Mocking Boundaries, Not Internals (Mock 邊界，而非內部細節)
- **Mock 什麼？** 網路請求（Axios, Fetch）、檔案系統寫入、隨機數生成、時間（Date.now）。
- **不 Mock 什麼？** 你的 Service 呼叫你的 Utility function、資料庫（如果可以用 Docker 跑真實的）、純邏輯運算。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Sleep" Hack (使用 setTimeout 等待)
這是最常見的 Flaky Test（不穩定測試）來源。
- **Anti-pattern:** `await new Promise(r => setTimeout(r, 1000))` // 等待 DB 寫入
- **Solution:** 總是 await 該操作的 Promise，或者使用測試框架提供的 `waitFor` / `poll` 機制，甚至 Mock Timer。

### 2. Leaking State Between Tests (測試間狀態洩漏)
Node.js 的 `require` 會快取模組，全域變數或 Singleton 可能在測試間殘留狀態。
- **後果:** 單獨跑測試 A 通過，但跑全部測試時 A 失敗（因為 B 修改了共用狀態）。
- **Fix:** 使用 `beforeEach` 和 `afterEach` 徹底重置 Mock 和 Database 資料（例如 `TRUNCATE` tables）。

### 3. Testing Implementation Details (測試實作細節)
- **Anti-pattern:** 測試「某個 private method 被呼叫了」。
- **Why bad:** 當你重構程式碼（Refactor）但不改變行為時，測試卻壞了。這會讓你討厭寫測試。
- **Fix:** 測試「公開介面的回傳值」或「公開可觀察的副作用（如 DB 變更）」。

### 4. Unhandled Promise Rejections in Tests
如果測試中忘了 `await` 一個會拋出錯誤的 Promise，測試可能會顯示 Pass（假陽性），或者在測試結束後才報錯。
- **Fix:** 確保 linter 開啟 `await-thenable` 規則，並在測試框架設定中捕捉未處理的 Rejection。

---

## Checklists & workflows｜檢查清單與流程

在提交程式碼或進行 Code Review 時，請使用此清單：

### Pre-commit / Writing Tests Checklist
- [ ] **Isolation (隔離性)**: 測試是否依賴外部真實 API？如果是，請改用 Mock (如 `nock` 或 `jest.mock`)。
- [ ] **Async Correctness (非同步正確性)**: 所有的 Promise 是否都有 `await` 或 `return`？避免使用 callback style 的 `done()` 除非必要。
- [ ] **Teardown (清理)**: 測試結束後，是否清理了 Database 髒資料或還原了 `jest.spyOn`？
- [ ] **Coverage (覆蓋率)**: 是否覆蓋了 Happy Path (成功路徑) 與 Edge Cases (錯誤處理、空值、網路超時)？
- [ ] **Determinism (確定性)**: 多次執行測試，結果是否一致？（注意 `Date.now()` 或 `Math.random()` 的 Mock）。

### Testing Workflow Decision Tree
1. **是純邏輯運算嗎？** (e.g., 資料格式轉換) -> **Unit Test** (不需要 Mock)。
2. **涉及資料庫讀寫嗎？** -> **Integration Test** (連接 Test DB，不 Mock SQL)。
3. **涉及第三方 API 呼叫嗎？** -> **Unit/Integration Test** (必須 Mock HTTP 請求，使用 `nock` 或 `msw`)。
4. **涉及複雜的非同步流程 (Event Emitter/Queues)？** -> **Integration Test** (驗證最終狀態，而非中間過程)。

---

## Real-world examples｜實戰案例

### Example 1: Testing an Async Service with External Dependency (Unit Test)
情境：`PaymentService` 呼叫外部 Stripe API。我們不希望測試時真的扣款。

```javascript
// payment.service.js
class PaymentService {
  constructor(paymentProvider) {
    this.provider = paymentProvider;
  }

  async process(orderId, amount) {
    try {
      const result = await this.provider.charge(amount);
      return { success: true, txId: result.id };
    } catch (error) {
      return { success: false, reason: 'Declined' };
    }
  }
}

// payment.service.test.js
const PaymentService = require('./payment.service');

describe('PaymentService', () => {
  let mockProvider;
  let service;

  beforeEach(() => {
    // Setup: 建立 Mock 物件
    mockProvider = {
      charge: jest.fn()
    };
    service = new PaymentService(mockProvider);
  });

  it('should return success when provider charges successfully', async () => {
    // Arrange: 定義 Mock 行為
    mockProvider.charge.mockResolvedValue({ id: 'tx_123' });

    // Act
    const result = await service.process('order_1', 100);

    // Assert
    expect(result).toEqual({ success: true, txId: 'tx_123' });
    expect(mockProvider.charge).toHaveBeenCalledWith(100);
  });

  it('should handle errors gracefully', async () => {
    // Arrange: 模擬失敗
    mockProvider.charge.mockRejectedValue(new Error('Insufficient funds'));

    // Act
    const result = await service.process('order_1', 100);

    // Assert
    expect(result).toEqual({ success: false, reason: 'Declined' });
  });
});
```

### Example 2: API Integration Testing (整合測試)
情境：測試一個 Express API，包含真實的 DB 操作（假設使用 Jest + Supertest）。

```javascript
// user.routes.test.js
const request = require('supertest');
const app = require('../app'); // 你的 Express App
const db = require('../db');   // 你的 DB 連線實例

describe('POST /api/users', () => {
  // 測試前連線 DB，測試後斷開
  beforeAll(async () => await db.connect());
  afterAll(async () => await db.disconnect());
  
  // 每個測試前清空 User 表，確保獨立性
  beforeEach(async () => await db.User.deleteMany({}));

  it('should create a user and save to DB', async () => {
    const payload = { username: 'john_doe', email: 'john@test.com' };

    // Act: 發送真實 HTTP 請求
    const res = await request(app)
      .post('/api/users')
      .send(payload)
      .expect(201); // Supertest 內建斷言

    // Assert: 檢查 Response
    expect(res.body.id).toBeDefined();
    expect(res.body.username).toBe('john_doe');

    // Assert: 檢查 Database 真實狀態 (Side Effect)
    const userInDb = await db.User.findOne({ email: 'john@test.com' });
    expect(userInDb).toBeTruthy();
    expect(userInDb.username).toBe('john_doe');
  });
});
```