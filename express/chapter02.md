# Chapter 02: Enterprise Architecture & Layered Patterns
# 第 02 章：企業級架構設計與分層模式

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

Express is famous for its unopinionated nature, allowing developers to structure applications however they see fit. However, for Senior Engineers working on large-scale systems, this freedom often leads to "Spaghetti Code" if not managed with strict architectural patterns. This chapter focuses on transforming a basic Express app into a maintainable, testable, and scalable enterprise-grade system.
Express 以其「不預設立場（unopinionated）」的特性聞名，允許開發者自由決定應用程式的結構。然而，對於開發大規模系統的資深工程師而言，這種自由若缺乏嚴謹的架構模式管理，往往會導致「義大利麵式程式碼（Spaghetti Code）」。本章專注於將基礎的 Express 應用程式轉型為可維護、可測試且可擴展的企業級系統。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Implement the 3-Layer Architecture**: Clearly separate concerns into Controller, Service, and Repository layers.
    **實作三層式架構**：清晰地將關注點分離為 Controller（控制器）、Service（服務）與 Repository（倉儲）層。
2.  **Apply Dependency Injection (DI)**: Decouple components using Constructor Injection without relying heavily on complex frameworks.
    **應用依賴注入（DI）**：使用建構子注入（Constructor Injection）來解耦組件，而不需過度依賴複雜的框架。
3.  **Design for Testability**: Structure your code so that business logic can be unit-tested in isolation from HTTP details and database drivers.
    **為可測試性而設計**：調整程式結構，使得商業邏輯可以在隔離 HTTP 細節與資料庫驅動的情況下進行單元測試。
4.  **Organize Project Structure**: Adopt a scalable directory structure (e.g., component-based or domain-driven) suitable for teams.
    **組織專案結構**：採用適合團隊協作的可擴展目錄結構（如基於組件或領域驅動的結構）。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### The 3-Layer Mental Model (三層架構心智模型)

Think of an Express application like a **High-End Restaurant**:
將 Express 應用程式想像成一家**高級餐廳**：

1.  **Controller (The Waiter)**:
    *   **Role**: Takes the order (Request), validates it, passes it to the kitchen, and brings back the food (Response).
    *   **Rule**: Never cooks the food. Should not contain business logic.
    *   **角色**：負責點餐（Request）、確認需求、將訂單交給廚房，並將餐點送回（Response）。
    *   **規則**：絕對不負責烹飪。不應包含商業邏輯。

2.  **Service (The Chef)**:
    *   **Role**: Knows the recipes (Business Logic). Mixes ingredients, applies rules, and ensures quality.
    *   **Rule**: Doesn't care who the customer is (HTTP agnostic) or where the ingredients come from (DB agnostic, ideally).
    *   **角色**：熟知食譜（商業邏輯）。混合食材、應用規則並確保品質。
    *   **規則**：不在乎顧客是誰（與 HTTP 無關），也不在乎食材具體來自哪裡（理想情況下與 DB 實作細節無關）。

3.  **Repository (The Pantry/Supplier)**:
    *   **Role**: Fetches raw ingredients (Data) from the fridge or supplier (Database).
    *   **Rule**: Doesn't know what the chef will cook. Just provides simple CRUD operations.
    *   **角色**：從冰箱或供應商（資料庫）獲取原始食材（資料）。
    *   **規則**：不知道廚師要煮什麼。僅提供單純的 CRUD 操作。

### Dependency Injection (DI) & Inversion of Control (IoC)
### 依賴注入（DI）與控制反轉（IoC）

In a naive Express app, modules `require` or `import` each other directly. This creates hard dependencies.
在初階的 Express 應用中，模組通常直接 `require` 或 `import` 彼此。這會建立強依賴關係。

*   **Tight Coupling (Bad)**: `AuthService` imports `UserModel` directly. You cannot test `AuthService` without a database connection.
*   **Loose Coupling (Good)**: `AuthService` receives a `userRepository` interface in its constructor.
*   **強耦合（壞）**：`AuthService` 直接匯入 `UserModel`。若沒有資料庫連線，你無法測試 `AuthService`。
*   **鬆耦合（好）**：`AuthService` 在其建構子中接收一個 `userRepository` 介面。

> **Note**: Unlike **NestJS** which has a built-in IoC Container, Express requires you to either wire dependencies manually (Composition Root) or use libraries like `InversifyJS` or `Awilix`. For this chapter, we focus on the pattern, not the library.
> **注意**：不同於 **NestJS** 內建 IoC 容器，Express 需要你手動組裝依賴（Composition Root）或使用 `InversifyJS`、`Awilix` 等函式庫。本章專注於模式本身，而非特定函式庫。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### Why does this matter in Production?
### 這在正式環境為何重要？

1.  **Maintainability & Refactoring (可維護性與重構)**:
    *   When business rules change (e.g., "Users must verify email before login"), you only touch the **Service** layer. The Controller (HTTP status) and Repository (SQL queries) remain untouched.
    *   當商業規則變更（例如：「使用者登入前必須驗證 Email」），你只需修改 **Service** 層。Controller（HTTP 狀態）與 Repository（SQL 查詢）保持不變。

2.  **Framework Agnosticism (框架無關性)**:
    *   If you decide to switch from Express to Fastify, or invoke the logic via a CLI script or Cron Job, your **Service** layer can be reused 100% because it doesn't depend on `req` and `res`.
    *   如果你決定從 Express 轉移到 Fastify，或透過 CLI 腳本、排程任務（Cron Job）呼叫邏輯，你的 **Service** 層可以 100% 重用，因為它不依賴 `req` 和 `res`。

3.  **Testing Strategy (測試策略)**:
    *   **Unit Tests**: Test Services by mocking Repositories. Fast and reliable.
    *   **Integration Tests**: Test Controllers to ensure HTTP wiring is correct.
    *   **單元測試**：透過 Mock Repositories 來測試 Services。快速且可靠。
    *   **整合測試**：測試 Controllers 以確保 HTTP 串接正確。

### Architecture Diagram (Text-based)
### 架構圖（文字描述）

```text
[Client] -> [Routes] -> [Controller] -> [Service] -> [Repository] -> [Database]
                                            |
                                      [External API Adapter]
```

*   **Routes**: Map URLs to Controller methods.
*   **Controller**: Unpacks `req.body`, calls Service, formats `res.json`.
*   **Service**: Contains `if/else`, validation logic, calls Repository.
*   **Repository**: `find`, `save`, `delete` methods wrapping ORM/SQL.

---

## 4. Walkthrough / Example
## 4. 逐步示例

### Scenario: User Registration
### 情境：使用者註冊

We will refactor a "Spaghetti" implementation into a structured one.
我們將把一個「義大利麵式」的實作重構為結構化的版本。

#### ❌ The Naive Approach (Spaghetti Code)
#### ❌ 初階做法（義大利麵程式碼）

Everything is inside the route handler. Hard to test, hard to read.
所有邏輯都在路由處理器中。難以測試，難以閱讀。

```javascript
// routes/user.js
const express = require('express');
const router = express.Router();
const User = require('../models/User'); // Direct Mongoose coupling

router.post('/register', async (req, res) => {
  try {
    // Validation logic mixed with HTTP
    if (!req.body.email || !req.body.password) {
      return res.status(400).json({ message: 'Missing fields' });
    }

    // Business logic: Check existence
    const existing = await User.findOne({ email: req.body.email });
    if (existing) {
      return res.status(409).json({ message: 'User exists' });
    }

    // DB logic mixed with business logic
    const user = new User(req.body);
    await user.save();

    // Side effect: Sending email (often mixed here too)
    // await sendWelcomeEmail(user.email); 

    res.status(201).json(user);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
```

#### ✅ The Mature Approach (Layered + DI)
#### ✅ 成熟做法（分層 + 依賴注入）

We will use **Constructor Injection**.
我們將使用 **建構子注入**。

**1. Repository Layer (Data Access)**
Encapsulates the DB interaction.
封裝資料庫互動。

```javascript
// repositories/UserRepository.js
class UserRepository {
  constructor(model) {
    this.model = model;
  }

  async findByEmail(email) {
    return this.model.findOne({ email });
  }

  async create(userData) {
    return this.model.create(userData);
  }
}
module.exports = UserRepository;
```

**2. Service Layer (Business Logic)**
Pure logic. No `req`, `res`, or direct DB models.
純邏輯。沒有 `req`、`res` 或直接的 DB 模型。

```javascript
// services/UserService.js
class UserService {
  constructor(userRepository) {
    this.userRepository = userRepository;
  }

  async registerUser(payload) {
    // 1. Validate Business Rules
    const existing = await this.userRepository.findByEmail(payload.email);
    if (existing) {
      throw new Error('USER_ALREADY_EXISTS'); // Throw generic errors, not HTTP errors
    }

    // 2. Execute Logic
    const newUser = await this.userRepository.create(payload);
    
    // 3. Return Result
    return newUser;
  }
}
module.exports = UserService;
```

**3. Controller Layer (HTTP Handling)**
Orchestrates the flow.
編排流程。

```javascript
// controllers/UserController.js
class UserController {
  constructor(userService) {
    this.userService = userService;
  }

  // Use arrow function to bind 'this' automatically or bind in constructor
  register = async (req, res, next) => {
    try {
      const result = await this.userService.registerUser(req.body);
      res.status(201).json(result);
    } catch (error) {
      if (error.message === 'USER_ALREADY_EXISTS') {
        return res.status(409).json({ message: 'User already exists' });
      }
      next(error); // Pass to global error handler
    }
  };
}
module.exports = UserController;
```

**4. Composition Root (Wiring it all together)**
This is where the magic happens. Usually in `app.js` or a dedicated `container.js`.
這是關鍵所在。通常在 `app.js` 或專門的 `container.js` 中。

```javascript
// container.js (Dependency Injection Container)
const UserModel = require('./models/User');
const UserRepository = require('./repositories/UserRepository');
const UserService = require('./services/UserService');
const UserController = require('./controllers/UserController');

// Manual Injection
const userRepository = new UserRepository(UserModel);
const userService = new UserService(userRepository);
const userController = new UserController(userService);

module.exports = {
  userController
};

// routes/index.js
const express = require('express');
const { userController } = require('../container');
const router = express.Router();

router.post('/register', userController.register);

module.exports = router;
```

### Project Structure Recommendation
### 專案結構建議

For large projects, group by **Component/Feature** rather than technical role (Controller/Service).
對於大型專案，建議按 **組件/功能** 分組，而不是按技術角色（Controller/Service）分組。

```text
src/
  components/
    users/
      User.model.js
      UserRepository.js
      UserService.js
      UserController.js
      user.routes.js
      user.test.js
    orders/
      ...
  common/
    middleware/
    utils/
  app.js
  server.js
```

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 1. The "Fat Controller"
### 1. 「肥胖控制器」
*   **Mistake**: Keeping validation and simple logic in the controller, only moving complex logic to services.
*   **Why it's bad**: Inconsistent testing. You can't unit test the validation logic without mocking `req`.
*   **Correction**: Controllers should strictly be input/output adapters.
*   **錯誤**：將驗證和簡單邏輯留在 Controller，只將複雜邏輯移至 Service。
*   **壞處**：測試不一致。若不 Mock `req`，你無法單元測試驗證邏輯。
*   **修正**：Controller 應嚴格作為輸入/輸出轉接器。

### 2. Leaking HTTP into Services
### 2. HTTP 細節洩漏至 Service
*   **Mistake**: Passing `req` or `res` into Service methods (e.g., `userService.update(req)`).
*   **Why it's bad**: Your service is now coupled to Express. You cannot reuse it in a WebSocket handler or a background job.
*   **Correction**: Pass only the necessary data (DTOs or plain objects).
*   **錯誤**：將 `req` 或 `res` 傳入 Service 方法（例如 `userService.update(req)`）。
*   **壞處**：你的 Service 現在與 Express 耦合。你無法在 WebSocket 處理器或背景任務中重用它。
*   **修正**：僅傳遞必要的資料（DTO 或純物件）。

### 3. Skipping the Repository Layer
### 3. 跳過 Repository 層
*   **Mistake**: Calling `Mongoose` or `Sequelize` models directly inside the Service.
*   **Why it's bad**: Hard to mock the database for unit tests. Hard to switch databases later.
*   **Correction**: Always wrap DB calls. Even if it's just a one-liner wrapper initially.
*   **錯誤**：在 Service 內直接呼叫 `Mongoose` 或 `Sequelize` 模型。
*   **壞處**：難以在單元測試中 Mock 資料庫。日後難以更換資料庫。
*   **修正**：始終封裝 DB 呼叫。即使最初只是單行程式碼的包裝。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

These questions test a candidate's understanding of *why* we use these patterns, not just *how*.
這些問題測試候選人對 *為什麼* 使用這些模式的理解，而不僅僅是 *如何* 使用。

### Q1: "Why do we need a Repository layer if ORMs like TypeORM or Mongoose already provide an abstraction?"
### Q1：「如果像 TypeORM 或 Mongoose 這樣的 ORM 已經提供了抽象層，為什麼我們還需要 Repository 層？」

*   **Key Points**:
    *   **Decoupling**: ORMs are still external dependencies. If we switch from Mongoose to raw SQL, we shouldn't have to rewrite the Service layer.
    *   **Testing**: Mocking a custom Repository interface is easier and cleaner than mocking complex ORM chain methods (e.g., `find().where().sort().exec()`).
    *   **Domain Language**: Repositories allow us to name methods based on business intent (e.g., `findActiveUsers`) rather than DB syntax.
*   **關鍵點**：
    *   **解耦**：ORM 仍然是外部依賴。如果我們從 Mongoose 切換到原生 SQL，不應重寫 Service 層。
    *   **測試**：Mock 一個自定義的 Repository 介面，比 Mock 複雜的 ORM 鏈式方法（如 `find().where().sort().exec()`）更容易且乾淨。
    *   **領域語言**：Repository 允許我們根據業務意圖命名方法（例如 `findActiveUsers`），而非 DB 語法。

### Q2: "How do you handle Database Transactions across multiple Services or Repositories?"
### Q2：「你如何處理跨多個 Service 或 Repository 的資料庫交易（Transactions）？」

*   **Key Points**:
    *   This is a classic layered architecture challenge.
    *   **Unit of Work (UoW)** pattern: Pass a transaction object (or session) through the service methods to the repositories.
    *   **CLS (Continuation-Local Storage)**: Use libraries like `cls-hooked` or Node's `AsyncLocalStorage` to store the transaction context implicitly, avoiding "prop drilling" the transaction object.
*   **關鍵點**：
    *   這是分層架構的經典挑戰。
    *   **工作單元（UoW）模式**：將交易物件（或 session）透過 Service 方法傳遞給 Repository。
    *   **CLS（Continuation-Local Storage）**：使用 `cls-hooked` 或 Node 的 `AsyncLocalStorage` 隱式儲存交易上下文，避免「屬性鑽取（prop drilling）」傳遞交易物件。

### Q3: "In a circular dependency scenario (Service A needs Service B, and B needs A), how do you resolve it in this architecture?"
### Q3：「在循環依賴的情境下（Service A 需要 Service B，且 B 需要 A），你在這種架構中如何解決？」

*   **Key Points**:
    *   **Refactoring**: Often a sign of bad design. Extract the shared logic into a third Service C.
    *   **Dependency Injection**: If unavoidable, use lazy injection or property injection instead of constructor injection.
    *   **Event Bus**: Decouple them completely by emitting events (e.g., Service A emits `USER_CREATED`, Service B listens).
*   **關鍵點**：
    *   **重構**：通常是設計不良的徵兆。將共享邏輯提取到第三個 Service C。
    *   **依賴注入**：如果無法避免，使用延遲注入（Lazy Injection）或屬性注入，而非建構子注入。
    *   **事件匯流排**：透過發送事件完全解耦（例如：Service A 發送 `USER_CREATED`，Service B 監聽）。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Summary (摘要)
1.  **Separation of Concerns**: Keep Controllers for HTTP, Services for Logic, Repositories for Data.
    **關注點分離**：Controller 負責 HTTP，Service 負責邏輯，Repository 負責資料。
2.  **Dependency Injection**: Inject dependencies via constructors to enable easy testing and swapping.
    **依賴注入**：透過建構子注入依賴，以實現輕鬆測試與替換。
3.  **Testability**: The primary benefit of this architecture is the ability to unit test business logic in isolation.
    **可測試性**：此架構的主要優勢在於能夠隔離並單元測試商業邏輯。
4.  **Project Structure**: Organize by Feature/Component in large apps to prevent a monolithic file structure.
    **專案結構**：在大型應用中按功能/組件組織，以防止單體式檔案結構。

### Next Steps (下一步)
*   **Chapter 03**: **Error Handling & Observability**. Now that we have layers, how do we centralize error handling and ensure we can trace a request through these layers?
*   **Chapter 03**：**錯誤處理與可觀測性**。既然有了分層，我們該如何集中處理錯誤，並確保能追蹤請求穿過這些層級的過程？
*   **Action Item**: Refactor *one* route in your current project to use the Controller-Service-Repository pattern. Write a unit test for that Service.
*   **行動項目**：將你目前專案中的 *一個* 路由重構為 Controller-Service-Repository 模式。並為該 Service 撰寫單元測試。