# Chapter 09: Testing Strategies & CI/CD
# 第九章：測試策略與自動化部署

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

For a Senior Software Engineer, testing is not just about writing assertions; it is about designing a **Testable Architecture** and establishing a **Confidence Pipeline**. In the Node.js ecosystem, where dynamic typing can lead to runtime errors, a robust testing strategy is the primary defense against regression. This chapter moves beyond basic syntax to focus on architectural patterns for testing and optimizing the delivery pipeline.

對於資深軟體工程師而言，測試不僅僅是撰寫斷言（assertions），而是關於設計**可測試的架構（Testable Architecture）**並建立**信心流水線（Confidence Pipeline）**。在 Node.js 生態系中，動態型別可能導致執行期錯誤，因此穩健的測試策略是防止回歸（regression）的首要防線。本章將超越基礎語法，專注於測試的架構模式與交付流程的最佳化。

By the end of this chapter, you will be able to:
完成本章後，您將能夠：

1.  **Architect for Testability**: Apply Dependency Injection (DI) and Inversion of Control (IoC) in Node.js to decouple business logic from infrastructure, making Unit Testing trivial and effective.
    **為可測試性架構設計**：在 Node.js 中應用依賴注入（DI）與控制反轉（IoC），將商業邏輯與基礎設施解耦，使單元測試變得輕量且有效。
2.  **Balance the Test Pyramid vs. Trophy**: Decide the optimal ratio of Unit, Integration, and E2E tests for API-centric Node.js services (often favoring Integration tests).
    **平衡測試金字塔與獎盃模型**：針對以 API 為核心的 Node.js 服務，決定單元、整合與 E2E 測試的最佳比例（通常傾向於整合測試）。
3.  **Optimize CI/CD Pipelines**: Implement caching strategies (`node_modules`), multi-stage Docker builds, and parallel execution to reduce feedback loops from minutes to seconds.
    **最佳化 CI/CD 流程**：實作快取策略（`node_modules`）、多階段 Docker 建置與平行執行，將回饋迴圈從數分鐘縮短至數秒。
4.  **Manage Flakiness & External Dependencies**: Use tools like `Testcontainers` or `Nock` to handle databases and third-party APIs reliably without mocking implementation details.
    **管理不穩定性與外部依賴**：使用 `Testcontainers` 或 `Nock` 等工具可靠地處理資料庫與第三方 API，避免過度 Mock 實作細節。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 The Testing Spectrum: Pyramid vs. Trophy
### 2.1 測試光譜：金字塔 vs. 獎盃

Traditionally, the **Test Pyramid** (lots of Unit, fewer Integration, very few E2E) is the standard. However, in modern Node.js microservices, business logic is often thin, functioning mainly as glue between a database and external APIs. Here, the **Testing Trophy** (championed by Kent C. Dodds) is often a better mental model: focusing heavily on **Integration Tests**.

傳統上，**測試金字塔**（大量的單元測試，較少的整合測試，極少的 E2E 測試）是標準。然而，在現代 Node.js 微服務中，商業邏輯通常很薄，主要作為資料庫與外部 API 之間的膠水。在這種情況下，**測試獎盃**（由 Kent C. Dodds 提倡）通常是更好的心智模型：將重心放在**整合測試**上。

*   **Unit Tests**: Verify pure functions or isolated classes. (Fast, precise, but low confidence in wiring).
    **單元測試**：驗證純函式或隔離的類別。（快速、精確，但對組件連接的信心較低）。
*   **Integration Tests**: Verify the interaction between your code and its dependencies (DB, Redis) or between modules. In Node.js, spinning up a real express app and hitting it with `supertest` against a Dockerized DB is the gold standard.
    **整合測試**：驗證程式碼與其依賴（DB, Redis）或模組間的互動。在 Node.js 中，啟動真實的 express 應用程式並使用 `supertest` 針對 Docker 容器化的 DB 進行測試是黃金標準。

### 2.2 Test Doubles: Mocks, Stubs, and Spies
### 2.2 測試替身：Mocks, Stubs 與 Spies

Senior engineers must distinguish between these to avoid "Testing Implementation Details."
資深工程師必須區分這些概念，以避免「測試實作細節」。

*   **Stub**: Provides canned answers to calls made during the test (e.g., forcing `fs.readFile` to return a specific buffer).
    **Stub**：對測試中的呼叫提供預設回應（例如：強制 `fs.readFile` 回傳特定的 buffer）。
*   **Mock**: Expects specific calls to be made (e.g., verifying `sendEmail` was called exactly once with specific arguments). **Overusing Mocks makes refactoring painful.**
    **Mock**：預期特定的呼叫會發生（例如：驗證 `sendEmail` 被呼叫且僅被呼叫一次，並帶有特定參數）。**過度使用 Mock 會讓重構變得痛苦。**
*   **Spy**: Wraps a real function to record its usage without changing its behavior.
    **Spy**：包裝真實函式以記錄其使用情況，但不改變其行為。

### 2.3 CI/CD as a Manufacturing Line
### 2.3 CI/CD 作為生產線

Think of your Node.js application as a product on an assembly line.
將您的 Node.js 應用程式想像成裝配線上的產品。

1.  **Lint/Format**: Quality control (static analysis).
    **Lint/Format**：品質控管（靜態分析）。
2.  **Unit Test**: Component inspection.
    **單元測試**：組件檢查。
3.  **Build**: Assembly (transpilation, bundling, containerization).
    **建置**：組裝（轉譯、打包、容器化）。
4.  **Integration Test**: System functionality check.
    **整合測試**：系統功能檢查。
5.  **Deploy**: Shipping to the customer.
    **部署**：交付給客戶。

**Key Insight**: Fail fast. Don't run E2E tests if the linter fails.
**關鍵洞察**：快速失敗（Fail fast）。如果 Linter 失敗，就不應該執行 E2E 測試。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### 3.1 Design for Testability (Dependency Injection)
### 3.1 為可測試性設計（依賴注入）

In a production Node.js system, tightly coupled code is the enemy of testing. If your controller directly imports a database model or an external API client, you cannot test the controller without triggering side effects.
在生產環境的 Node.js 系統中，緊密耦合的程式碼是測試的大敵。如果您的 Controller 直接 import 資料庫模型或外部 API 客戶端，您就無法在不觸發副作用的情況下測試該 Controller。

**System Design Implication**:
**系統設計意涵**：
Use **Dependency Injection (DI)**. Instead of `import User from './models/User'`, pass the `User` model (or repository) into the service/controller constructor. This allows you to inject a real repository in production and an in-memory mock repository during unit tests.
使用 **依賴注入（DI）**。與其使用 `import User from './models/User'`，不如將 `User` 模型（或 Repository）傳入 Service/Controller 的建構函式中。這允許您在生產環境注入真實的 Repository，而在單元測試時注入記憶體中的 Mock Repository。

### 3.2 Handling External Services in CI
### 3.2 在 CI 中處理外部服務

When your system depends on DynamoDB, Redis, or Stripe:
當您的系統依賴 DynamoDB、Redis 或 Stripe 時：

*   **Naive Approach**: Mock everything. (Risk: Production bugs due to API mismatch).
    **天真做法**：Mock 所有東西。（風險：因 API 不匹配導致生產環境 Bug）。
*   **Senior Approach**:
    **資深做法**：
    *   **Infrastructure**: Use **Testcontainers** or ephemeral Docker services in CI to run real instances of Redis/Postgres.
        **基礎設施**：在 CI 中使用 **Testcontainers** 或臨時的 Docker 服務來執行真實的 Redis/Postgres 實例。
    *   **3rd Party APIs**: Use **Contract Testing** (e.g., Pact) or record/replay tools (e.g., `Polly.js`, `Nock` with recording) to ensure your mocks match reality.
        **第三方 API**：使用 **契約測試**（如 Pact）或錄製/重播工具（如 `Polly.js`、帶錄製功能的 `Nock`）確保您的 Mock 與現實相符。

---

## 4. Walkthrough / Example
## 4. 逐步示例

### Scenario: Testing a Payment Service
### 情境：測試支付服務

We need to test a `processPayment` function that:
1.  Checks user balance in DB.
2.  Calls Stripe API.
3.  Updates DB transaction record.

我們需要測試一個 `processPayment` 函式，它會：
1.  檢查資料庫中的使用者餘額。
2.  呼叫 Stripe API。
3.  更新資料庫交易紀錄。

### Step 1: The "Naive" Implementation (Hard to Test)
### 步驟 1：「天真」的實作（難以測試）

```javascript
// paymentService.js
const db = require('./db'); // Singleton DB connection
const stripe = require('stripe')('sk_test_...');

exports.processPayment = async (userId, amount) => {
  const user = await db.User.findById(userId); // Direct dependency
  if (user.balance < amount) throw new Error('Insufficient funds');
  
  await stripe.charges.create({ amount, currency: 'usd' }); // Direct dependency
  
  user.balance -= amount;
  await user.save();
};
```

**Critique**: To test this, you have to mock `require('stripe')` and `require('./db')`. This is brittle and relies on module caching magic (like `jest.mock`).
**評論**：要測試這段程式碼，你必須 Mock `require('stripe')` 和 `require('./db')`。這很脆弱，且依賴模組快取機制（如 `jest.mock`）。

### Step 2: The "Testable" Implementation (Dependency Injection)
### 步驟 2：「可測試」的實作（依賴注入）

We define dependencies via constructor (or a factory function).
我們透過建構函式（或工廠函式）定義依賴。

```javascript
// paymentService.js
class PaymentService {
  constructor({ userRepo, paymentGateway }) {
    this.userRepo = userRepo;
    this.paymentGateway = paymentGateway;
  }

  async processPayment(userId, amount) {
    const user = await this.userRepo.findById(userId);
    if (user.balance < amount) throw new Error('Insufficient funds');

    // Business Logic: Check logic independent of DB/API implementation
    const chargeResult = await this.paymentGateway.charge(amount, 'usd');
    
    user.balance -= amount;
    await this.userRepo.save(user);
    return chargeResult;
  }
}

module.exports = PaymentService;
```

### Step 3: Unit Test (Logic Verification)
### 步驟 3：單元測試（邏輯驗證）

Here we use stubs/mocks because we only care about the *logic flow*, not the DB connection.
這裡我們使用 Stubs/Mocks，因為我們只在乎**邏輯流程**，而非資料庫連線。

```javascript
// paymentService.test.js
const PaymentService = require('./paymentService');

describe('PaymentService', () => {
  it('should throw error if balance is insufficient', async () => {
    // Arrange: Create simple objects, no heavy libraries needed
    const mockUserRepo = {
      findById: jest.fn().mockResolvedValue({ balance: 50 }),
      save: jest.fn()
    };
    const mockGateway = { charge: jest.fn() };
    
    const service = new PaymentService({ 
      userRepo: mockUserRepo, 
      paymentGateway: mockGateway 
    });

    // Act & Assert
    await expect(service.processPayment('user1', 100))
      .rejects.toThrow('Insufficient funds');
      
    expect(mockGateway.charge).not.toHaveBeenCalled();
  });
});
```

### Step 4: Integration Test (The Real Deal)
### 步驟 4：整合測試（動真格）

This runs against a real DB (spun up via Docker) and a mocked HTTP server for Stripe (using Nock).
這會針對真實的資料庫（透過 Docker 啟動）與 Mock 的 Stripe HTTP 伺服器（使用 Nock）進行測試。

```javascript
// paymentService.integration.test.js
const request = require('supertest');
const app = require('../app'); // Your Express App with real wiring
const nock = require('nock');
const { connect, close, clear } = require('../test-utils/db');

beforeAll(async () => await connect()); // Connect to Test DB
afterEach(async () => await clear());
afterAll(async () => await close());

it('POST /pay performs full transaction', async () => {
  // Arrange: Seed DB
  await request(app).post('/users').send({ id: 'user1', balance: 200 });
  
  // Mock External API (Stripe) only
  const scope = nock('https://api.stripe.com')
    .post('/v1/charges')
    .reply(200, { id: 'ch_123', status: 'succeeded' });

  // Act
  const res = await request(app)
    .post('/pay')
    .send({ userId: 'user1', amount: 100 });

  // Assert
  expect(res.status).toBe(200);
  expect(scope.isDone()).toBe(true); // Verify API was called
  
  // Verify DB state directly
  const user = await request(app).get('/users/user1');
  expect(user.body.balance).toBe(100);
});
```

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 Testing Implementation Details
### 5.1 測試實作細節

*   **Bad**: `expect(userService.getUser).toHaveBeenCalledWith(123)`.
    **壞**：`expect(userService.getUser).toHaveBeenCalledWith(123)`。
*   **Why**: If you refactor `getUser` to take an object `{ id: 123 }` instead, the test breaks even if the feature still works.
    **原因**：如果你重構 `getUser` 改為接收物件 `{ id: 123 }`，即使功能正常，測試也會壞掉。
*   **Good**: Test inputs and outputs (Black Box). `expect(response.body).toEqual(expectedUser)`.
    **好**：測試輸入與輸出（黑箱）。`expect(response.body).toEqual(expectedUser)`。

### 5.2 Dirty Test State (Shared State)
### 5.2 髒測試狀態（共享狀態）

*   **Bad**: Using a global database without cleaning it up between tests. Test A creates a user, Test B expects 0 users and fails.
    **壞**：使用全域資料庫但在測試間未清理。測試 A 建立了一個使用者，測試 B 預期 0 個使用者，結果失敗。
*   **Fix**: Use `beforeEach` / `afterEach` hooks to truncate tables or use database transactions that rollback after each test.
    **修正**：使用 `beforeEach` / `afterEach` 鉤子來清空資料表，或使用資料庫交易（Transaction）並在每個測試後 Rollback。

### 5.3 Ignoring CI/CD Performance
### 5.3 忽視 CI/CD 效能

*   **Bad**: Running `npm install` every time without caching.
    **壞**：每次都執行 `npm install` 而沒有快取。
*   **Fix**: Use `npm ci` (deterministic install based on lockfile) and cache `node_modules` based on `package-lock.json` hash.
    **修正**：使用 `npm ci`（基於 lockfile 的確定性安裝）並根據 `package-lock.json` 的雜湊值快取 `node_modules`。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How do you handle "Flaky Tests" in a CI environment?
### Q1: 你如何在 CI 環境中處理「不穩定測試（Flaky Tests）」？

*   **Key Points**:
    *   **Identification**: Is it timing (race condition), external dependency (network), or shared state?
    *   **Isolation**: Ensure tests don't share DB state or global variables.
    *   **Determinism**: Mock Date/Time (e.g., `jest.useFakeTimers`) and `Math.random` if necessary.
    *   **Retries**: Mention that retries are a temporary band-aid, not a fix. The root cause must be solved.
    *   **關鍵點**：
    *   **識別**：是時序問題（Race condition）、外部依賴（網路）還是共享狀態？
    *   **隔離**：確保測試不共享 DB 狀態或全域變數。
    *   **確定性**：Mock 日期/時間（如 `jest.useFakeTimers`）以及必要時 Mock `Math.random`。
    *   **重試**：提到重試只是暫時的OK繃，不是解法。必須解決根本原因。

### Q2: When would you choose E2E tests over Integration tests?
### Q2: 什麼時候你會選擇 E2E 測試而非整合測試？

*   **Key Points**:
    *   **Cost vs. Value**: E2E are slow and expensive. Use them for "Critical User Journeys" (e.g., Checkout flow, Login).
    *   **Scope**: Integration tests mock the *external* world (Stripe, Twilio). E2E tests might run against a Sandbox environment of those services to verify the contract hasn't changed.
    *   **關鍵點**：
    *   **成本 vs. 價值**：E2E 慢且昂貴。用於「關鍵使用者旅程」（如結帳流程、登入）。
    *   **範圍**：整合測試 Mock **外部**世界（Stripe, Twilio）。E2E 測試可能會針對這些服務的沙盒環境執行，以驗證契約未改變。

### Q3: How do you design a CI pipeline for a Node.js Monorepo?
### Q3: 你如何為 Node.js Monorepo 設計 CI 流程？

*   **Key Points**:
    *   **Affected Graph**: Only run tests for packages that changed (and their dependents). Tools like `Nx` or `Turborepo`.
    *   **Parallelization**: Run independent tests concurrently.
    *   **Artifacts**: Build once, deploy everywhere. Don't rebuild Docker images in different stages.
    *   **關鍵點**：
    *   **受影響圖譜**：只針對變更的套件（及其依賴者）執行測試。使用 `Nx` 或 `Turborepo` 等工具。
    *   **平行化**：並發執行獨立的測試。
    *   **產出物**：一次建置，隨處部署。不要在不同階段重新建置 Docker 映像檔。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Summary
### 小結

1.  **Testable Architecture**: Dependency Injection is key to decoupling Node.js apps for testing.
    **可測試架構**：依賴注入是將 Node.js 應用解耦以利測試的關鍵。
2.  **Testing Strategy**: For backend services, prioritize **Integration Tests** (Controller + DB) over granular Unit Tests.
    **測試策略**：對於後端服務，優先考慮**整合測試**（Controller + DB），而非細碎的單元測試。
3.  **CI Optimization**: Use `npm ci`, cache dependencies, and separate build/test stages to speed up feedback.
    **CI 最佳化**：使用 `npm ci`、快取依賴並分離建置/測試階段以加速回饋。
4.  **External Deps**: Use `Testcontainers` for DBs and `Nock`/`Pact` for APIs. Avoid mocking internals.
    **外部依賴**：DB 使用 `Testcontainers`，API 使用 `Nock`/`Pact`。避免 Mock 內部實作。
5.  **Reliability**: Eliminate shared state to fix flaky tests.
    **可靠性**：消除共享狀態以修復不穩定的測試。

### Next Steps
### 後續延伸

*   **Observability (Chapter 10)**: Once tests pass and code deploys, how do you know it works? Learn about Logging (Winston/Pino), Metrics (Prometheus), and Tracing (OpenTelemetry).
    **可觀測性（第 10 章）**：當測試通過且程式碼部署後，如何知道它運作正常？學習日誌（Winston/Pino）、指標（Prometheus）與追蹤（OpenTelemetry）。
*   **Advanced Performance**: Explore load testing with `k6` or `Artillery` to see how your Node.js app behaves under stress.
    **進階效能**：探索使用 `k6` 或 `Artillery` 進行負載測試，觀察 Node.js 應用在高壓下的表現。