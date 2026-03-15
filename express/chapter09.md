# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，測試不僅僅是為了追求程式碼覆蓋率（Code Coverage），更是為了建立「重構的信心」與「部署的速度」。在 Express 生態系中，由於框架本身的靈活性（unopinionated），缺乏統一的測試標準往往導致專案隨著規模擴大而變得難以維護。本章將超越基礎的斷言（Assertion），深入探討如何構建可擴展的測試策略。

For senior engineers, testing is not just about chasing code coverage metrics; it is about building "confidence in refactoring" and "velocity in deployment." In the Express ecosystem, due to the framework's unopinionated nature, the lack of a unified testing standard often leads to projects becoming unmaintainable as they scale. This chapter goes beyond basic assertions to explore how to architect scalable testing strategies.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **設計分層測試策略**：理解何時使用單元測試（Unit Test），何時使用 Supertest 進行整合測試（Integration Test），以及如何平衡兩者的成本與效益。
    **Design a layered testing strategy**: Understand when to use Unit Tests versus Integration Tests with Supertest, and how to balance the cost-benefit ratio of both.
2.  **掌握依賴隔離技術**：在不使用複雜 DI 框架的情況下，有效地 Mock 資料庫與第三方 API（如 AWS SDK、Stripe），避免測試環境的不穩定。
    **Master dependency isolation techniques**: Effectively mock databases and third-party APIs (e.g., AWS SDK, Stripe) without complex DI frameworks to avoid flaky test environments.
3.  **優化 CI/CD 流程中的測試品質**：解決測試污染（Test Pollution）與間歇性失敗（Flaky Tests）問題，確保自動化流程的可靠性。
    **Optimize test quality in CI/CD pipelines**: Resolve test pollution and flaky tests to ensure the reliability of automation workflows.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 測試金字塔 vs. 測試獎盃 (The Testing Pyramid vs. The Testing Trophy)

傳統觀點強調「測試金字塔」（大量單元測試，少量整合測試）。然而，在 Express 後端開發中，**「測試獎盃」（Testing Trophy）** 模型往往更具實務價值。Express 應用通常是「膠水程式碼」（Glue Code），負責將 Request 轉發給 Controller、Service 與 Database。如果只測單一函數，往往無法抓出 Middleware 順序錯誤或 DB 查詢語法錯誤。

Traditional views emphasize the "Testing Pyramid" (heavy on unit tests, light on integration). However, in Express backend development, the **"Testing Trophy"** model is often more practical. Express applications are typically "glue code," responsible for routing requests to Controllers, Services, and Databases. Testing individual functions in isolation often fails to catch middleware ordering issues or DB query syntax errors.

-   **Unit Tests**: 專注於純邏輯（Business Logic），例如計算折扣、資料格式轉換。不涉及 I/O。
    **Unit Tests**: Focus on pure business logic, such as calculating discounts or data transformation. No I/O involved.
-   **Integration Tests (Supertest)**: 這是 Express 測試的核心。模擬 HTTP 請求穿過 Router、Middleware 到達 Controller，並驗證回應。這是 ROI（投資報酬率）最高的部分。
    **Integration Tests (Supertest)**: The core of Express testing. Simulates HTTP requests passing through Routers and Middleware to Controllers, verifying the response. This yields the highest ROI.

## 2.2 依賴注入與 Mocking (Dependency Injection vs. Mocking)

在 Java (Spring) 或 NestJS 中，依賴注入（DI）是標準配備，測試時替換實作很容易。但在原生 Express 中，模組通常是直接 `require` 或 `import` 的。

In Java (Spring) or NestJS, Dependency Injection (DI) is standard, making implementation swapping easy during tests. However, in native Express, modules are usually directly `require`-d or `import`-ed.

-   **Jest Module Mocking**: 透過攔截 `require` 系統來替換模組。這是 Express 專案中最常見的做法，雖然方便，但容易造成測試與實作細節的強耦合。
    **Jest Module Mocking**: Replaces modules by intercepting the `require` system. This is the most common practice in Express projects; while convenient, it can lead to tight coupling between tests and implementation details.
-   **Manual DI**: 在 Controller 初始化時傳入 Service/DB 實例。這需要改變程式碼結構，但能讓測試更乾淨且不依賴特定測試框架的黑魔法。
    **Manual DI**: Passing Service/DB instances when initializing Controllers. This requires structural code changes but results in cleaner tests that don't rely on test framework "black magic."

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 測試資料庫策略 (Database Strategy in Testing)

在系統設計面試或實務架構中，如何處理資料庫測試是一個關鍵決策點。

In system design interviews or real-world architecture, handling database tests is a critical decision point.

1.  **In-Memory DB (e.g., SQLite, MongoMemoryServer)**:
    -   *Pros*: 速度快，無須外部依賴。
    -   *Cons*: 行為與 Production DB（如 PostgreSQL, MongoDB Atlas）不完全一致，可能漏掉特定語法錯誤。
2.  **Dockerized DB (Testcontainers)**:
    -   *Pros*: 真實環境模擬（Real environment simulation），可靠性高。
    -   *Cons*: 啟動較慢，資源消耗大。
    -   *Senior Choice*: 對於關鍵路徑（Critical Path），資深工程師傾向使用 **Dockerized DB** 配合良好的 Setup/Teardown 策略，以確保 SQL/Query 正確性。

## 3.2 外部服務隔離 (Isolating External Services)

當你的 Express App 依賴 Stripe (金流)、SendGrid (郵件) 或 AWS S3 時，絕對不能在測試中真的呼叫這些 API。

When your Express App depends on Stripe (Payments), SendGrid (Email), or AWS S3, you must never actually call these APIs during tests.

-   **Nock / MSW (Mock Service Worker)**: 在 HTTP 層級攔截請求。這比 Mock 程式碼中的 function 更貼近真實情況，因為它驗證了你的 HTTP Client 配置（Headers, Timeouts）是否正確。
    **Nock / MSW (Mock Service Worker)**: Intercepts requests at the HTTP level. This is closer to reality than mocking functions in code because it verifies your HTTP Client configuration (Headers, Timeouts).

---

# 4. 逐步示例 (Walkthrough / Example)

我們將示範如何測試一個「用戶註冊 API」，包含 Middleware 驗證、Service 邏輯與外部依賴 Mocking。

We will demonstrate how to test a "User Registration API," including Middleware validation, Service logic, and external dependency mocking.

### 4.1 架構準備：分離 App 與 Server (Separating App and Server)

這是最重要的一步。為了讓 `supertest` 正常運作且不佔用 Port，必須將 `app` 定義與 `server.listen` 分開。

This is the most important step. For `supertest` to work correctly without port conflicts, you must separate the `app` definition from `server.listen`.

**`app.js`**
```javascript
const express = require('express');
const userRoutes = require('./routes/userRoutes');
const app = express();

app.use(express.json());
app.use('/api/users', userRoutes);

module.exports = app; // Export app for testing
```

**`server.js`**
```javascript
const app = require('./app');
const port = process.env.PORT || 3000;

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
```

### 4.2 整合測試實作 (Integration Test Implementation)

假設我們使用 Jest 與 Supertest。場景：註冊成功後，應寫入 DB 並發送歡迎信。

Assume we use Jest and Supertest. Scenario: After successful registration, write to DB and send a welcome email.

**`tests/integration/user.test.js`**

```javascript
const request = require('supertest');
const app = require('../../src/app');
const emailService = require('../../src/services/emailService');
const db = require('../../src/db'); // Assume a DB abstraction

// 1. Mock 外部依賴 (Mock External Dependencies)
// 使用 Jest Mock 攔截 emailService，避免真實發信
// Use Jest Mock to intercept emailService, preventing real emails
jest.mock('../../src/services/emailService');

describe('POST /api/users/register', () => {
  
  // 2. Setup & Teardown (資料庫清理)
  // 確保每個測試都在乾淨的狀態下運行
  // Ensure each test runs in a clean state
  beforeAll(async () => {
    await db.connect();
  });

  afterEach(async () => {
    await db.clearDatabase();
    jest.clearAllMocks(); // 重置 Mock 計數器 (Reset mock counters)
  });

  afterAll(async () => {
    await db.disconnect();
  });

  it('should register a user and send a welcome email', async () => {
    // Arrange
    const userData = { email: 'test@example.com', password: 'Password123!' };
    emailService.sendWelcomeEmail.mockResolvedValue(true); // Stub response

    // Act
    const response = await request(app)
      .post('/api/users/register')
      .send(userData);

    // Assert - HTTP Response
    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty('id');
    expect(response.body.email).toBe(userData.email);

    // Assert - Side Effects (Mock Verification)
    expect(emailService.sendWelcomeEmail).toHaveBeenCalledTimes(1);
    expect(emailService.sendWelcomeEmail).toHaveBeenCalledWith(userData.email);
    
    // Assert - Database State (Optional but recommended for critical paths)
    const userInDb = await db.findUserByEmail(userData.email);
    expect(userInDb).toBeTruthy();
  });

  it('should return 400 if email is invalid', async () => {
    const response = await request(app)
      .post('/api/users/register')
      .send({ email: 'invalid-email', password: '123' });

    expect(response.status).toBe(400);
    // 確保在錯誤情況下不會發送 Email
    // Ensure email is not sent in error cases
    expect(emailService.sendWelcomeEmail).not.toHaveBeenCalled();
  });
});
```

### 4.3 為什麼這樣做可行？ (Why this works?)

1.  **真實路由測試**：我們測試了 Express 的 Router、Body Parser 和 Controller 邏輯，而不僅僅是單一函數。
    **Real Routing Test**: We tested Express's Router, Body Parser, and Controller logic, not just a single function.
2.  **邊界隔離**：DB 是真實的（或 Docker 模擬的），但 Email Service 是 Mock 的。這符合「控制不可控因素（External APIs），驗證持久化狀態（DB）」的原則。
    **Boundary Isolation**: The DB is real (or Docker simulated), but the Email Service is mocked. This aligns with the principle of "controlling the uncontrollable (External APIs) while verifying persistence state (DB)."

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 測試實作細節 (Testing Implementation Details)

-   **錯誤 (Bad)**: 測試 Controller 內部是否呼叫了 `validateEmail` 私有函數。
    **Mistake**: Testing if the Controller internally called a private `validateEmail` function.
-   **後果 (Consequence)**: 重構程式碼（例如將驗證邏輯移至 Middleware）時，即使功能正常，測試也會失敗（False Positive）。
    **Consequence**: When refactoring code (e.g., moving validation logic to Middleware), tests fail even if the functionality remains correct (False Positive).
-   **修正 (Fix)**: 測試公開介面（Public Interface），即 HTTP Request 與 Response。
    **Fix**: Test the public interface, i.e., the HTTP Request and Response.

## 5.2 全域狀態污染 (Global State Pollution)

-   **錯誤 (Bad)**: 在測試 A 中修改了 DB 資料，但沒有在測試結束後清理，導致測試 B 失敗。
    **Mistake**: Modifying DB data in Test A but failing to clean it up, causing Test B to fail.
-   **修正 (Fix)**: 使用 `beforeEach` / `afterEach` 進行 Transaction Rollback 或 Table Truncate。
    **Fix**: Use `beforeEach` / `afterEach` to perform Transaction Rollbacks or Table Truncation.

## 5.3 過度 Mocking (Over-Mocking)

-   **錯誤 (Bad)**: Mock 了資料庫層（ORM），Mock 了 Service 層，Mock 了所有東西。
    **Mistake**: Mocking the Database layer (ORM), mocking the Service layer, mocking everything.
-   **後果 (Consequence)**: 測試通過了，但實際上 SQL 語法是錯的，或者欄位名稱根本對不上。你的測試變成了在測試「Mock 的設定」而非程式碼本身。
    **Consequence**: Tests pass, but the SQL syntax is actually wrong, or column names don't match. Your tests become about testing "the Mock configuration" rather than the code itself.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

這些問題能展現你對測試策略的深度理解。

These questions demonstrate your deep understanding of testing strategies.

## Q1: 你如何在 CI/CD 流程中處理不穩定的測試（Flaky Tests）？
**How do you handle flaky tests in a CI/CD pipeline?**

-   **高分回答要點**:
    -   **識別 (Identify)**: 使用 `jest --retry` 或 CI 報告找出非確定性失敗。
    -   **隔離 (Isolate)**: 檢查是否依賴了外部網路（應使用 Nock/Mock）、是否有 Race Condition（Promise 未正確 await）、或是有殘留的 DB 狀態。
    -   **策略 (Strategy)**: 不要只是重試（Retry）。如果是時間相關問題，使用 Fake Timers。如果是 DB 問題，確保 Transaction 隔離。

## Q2: 在 Express 專案中，你會選擇 TDD (Test Driven Development) 還是 BDD (Behavior Driven Development)？
**In an Express project, would you choose TDD or BDD?**

-   **高分回答要點**:
    -   不拘泥於術語，重點是**測試的層級**。
    -   對於複雜的演算法（如定價引擎），我會用 TDD（Unit Test 先行）。
    -   對於 API 開發，我傾向類似 BDD 的整合測試優先（Integration Test First）：先寫 Supertest 定義 API 的輸入輸出（Contract），再實作 Controller。這能確保 API 設計符合需求。

## Q3: 如何測試依賴於第三方 Webhook 的邏輯（例如 Stripe Payment Success）？
**How do you test logic depending on 3rd-party Webhooks (e.g., Stripe Payment Success)?**

-   **高分回答要點**:
    -   **驗證簽章 (Signature Verification)**: 測試必須涵蓋簽章驗證邏輯，確保安全性。
    -   **模擬 Payload**: 從官方文件複製真實的 JSON Payload 進行測試。
    -   **本地觸發**: 在開發環境使用 CLI 工具（如 Stripe CLI）轉發事件到 localhost；在 CI 中則直接對 Webhook Endpoint 發送構造好的 HTTP 請求。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 本章重點 (Key Takeaways)
1.  **Integration over Unit**: 在 Express API 中，使用 Supertest 進行整合測試通常比單元測試更有價值。
2.  **App vs Server**: 務必將 `app.js` 與 `server.js` 分離，以便測試框架掛載。
3.  **Clean State**: 嚴格執行 DB 清理與 Mock 重置，避免測試污染。
4.  **Mock Boundaries**: Mock 外部 I/O（Email, 3rd Party API），但盡量保留內部 I/O（Database）以確保整合正確性。
5.  **Test Public Interface**: 測試輸入（Request）與輸出（Response/DB State），而非實作細節。

## 後續延伸 (Next Steps)
-   **Chapter 10: Performance Optimization & Security**: 既然我們有了測試作為安全網，下一章將探討如何優化 Express 的效能（Caching, Gzip, Event Loop Lag）並加固安全性（Helmet, Rate Limiting），並透過 Load Testing（如 k6）來驗證優化成果。