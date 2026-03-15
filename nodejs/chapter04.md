# Chapter 04: Enterprise Application Architecture
# 第四章：企業級應用架構設計

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

Node.js is unopinionated by design, which is both its greatest strength and its most dangerous trap. For junior developers, the freedom to write everything in a single file is convenient. For senior engineers, however, the lack of a standardized structure often leads to "Spaghetti Code" that is impossible to test or maintain. This chapter focuses on structuring Node.js applications for longevity and scale.
Node.js 的設計哲學是不預設立場（Unopinionated），這既是它最大的優勢，也是最危險的陷阱。對於初階開發者來說，將所有邏輯寫在單一檔案中非常方便；但對於資深工程師而言，缺乏標準結構往往導致難以測試與維護的「義大利麵程式碼（Spaghetti Code）」。本章將專注於如何架構能長久運作且具備擴展性的 Node.js 應用程式。

By the end of this chapter, you will be able to:
完成本章後，您將能夠：

1.  **Implement Layered Architecture**: Decouple your application into Controller, Service, and Data Access layers to separate concerns effectively.
    **實作分層架構**：將應用程式解耦為控制器（Controller）、服務（Service）與資料存取（Data Access）層，有效分離關注點。
2.  **Master Dependency Injection (DI)**: Understand the "Inversion of Control" principle and apply DI (manually or via containers) to enhance testability.
    **掌握依賴注入（DI）**：理解「控制反轉（IoC）」原則，並應用 DI（手動或透過容器）來提升可測試性。
3.  **Apply Clean Architecture Principles**: Structure code so that business logic is independent of frameworks, databases, and external agencies.
    **應用 Clean Architecture 原則**：組織程式碼結構，使業務邏輯獨立於框架、資料庫與外部代理之外。
4.  **Refactor Legacy Codebases**: Identify "Fat Controllers" and "Leaky Abstractions" and refactor them into maintainable patterns.
    **重構遺留代碼庫**：識別「肥大的控制器（Fat Controllers）」與「洩漏的抽象（Leaky Abstractions）」，並將其重構為可維護的模式。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### The Mental Model: The Restaurant Kitchen
### 心智模型：餐廳廚房

Imagine a professional restaurant.
想像一間專業餐廳。

-   **Controller (The Waiter)**: Takes the order (HTTP Request), validates format, passes it to the kitchen, and delivers the food (HTTP Response). The waiter doesn't cook.
    **Controller（服務生）**：接收訂單（HTTP Request）、驗證格式、傳遞給廚房，並送上食物（HTTP Response）。服務生不負責烹飪。
-   **Service Layer (The Chef)**: Receives the order, follows the recipe (Business Logic), combines ingredients, and ensures quality. The chef doesn't care who the customer is or how the ingredients were farmed.
    **Service Layer（主廚）**：接收訂單、依照食譜（業務邏輯）烹調、組合食材並確保品質。主廚不在乎顧客是誰，也不管食材是如何種植的。
-   **Data Access / Repository (The Supplier/Fridge)**: Provides the raw ingredients (Data). It hides the complexity of whether the tomato came from a local farm (SQL) or an import (NoSQL).
    **Data Access / Repository（供應商/冰箱）**：提供原始食材（資料）。它隱藏了番茄是來自在地農場（SQL）還是進口（NoSQL）的複雜性。

### Key Definitions
### 關鍵定義

1.  **Separation of Concerns (SoC)**:
    Each module should have one, and only one, reason to change. If you change the database, the Controller shouldn't break.
    **關注點分離 (SoC)**：每個模組應該只有一個，且僅有一個改變的理由。如果你更換資料庫，Controller 不應該因此壞掉。

2.  **Dependency Injection (DI) & Inversion of Control (IoC)**:
    Instead of a Service creating its own Database connection (`const db = require('./db')`), the connection is "injected" into the Service. This allows you to swap the real DB with a Mock DB during testing.
    **依賴注入 (DI) 與控制反轉 (IoC)**：Service 不應自行建立資料庫連線（`const db = require('./db')`），而是將連線「注入」到 Service 中。這讓你在測試時可以輕易將真實 DB 替換為 Mock DB。

3.  **Clean Architecture (The Onion)**:
    The golden rule is the **Dependency Rule**: Source code dependencies can only point inwards. Nothing in an inner circle (Entities/Use Cases) can know anything at all about something in an outer circle (DB, Web, UI).
    **Clean Architecture（洋蔥架構）**：黃金準則是**依賴原則**：原始碼的依賴關係只能指向內部。內圈（實體/使用案例）中的任何東西都不能知道外圈（資料庫、Web、UI）的任何資訊。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### Role in Production Systems
### 在生產環境系統中的角色

In a large-scale distributed system or microservices architecture, strict internal architecture of a Node.js service is crucial for **Maintainability** and **Observability**.
在大型分散式系統或微服務架構中，Node.js 服務嚴謹的內部架構對於**可維護性**與**可觀測性**至關重要。

-   **Maintainability**: When a business rule changes (e.g., "Users under 18 cannot register"), you know exactly where to look (Service Layer). You don't hunt through route handlers.
    **可維護性**：當業務規則改變時（例如：「未滿 18 歲使用者不能註冊」），你明確知道該去哪裡找（Service 層），而不需要在路由處理器中大海撈針。
-   **Testability**: You can write Unit Tests for your business logic without spinning up a Docker container for MongoDB or Redis. This speeds up CI/CD pipelines significantly.
    **可測試性**：你可以針對業務邏輯撰寫單元測試，而無需啟動 MongoDB 或 Redis 的 Docker 容器。這能顯著加速 CI/CD 流程。
-   **Flexibility**: Moving from a monolithic Express app to Serverless (AWS Lambda)? If your logic is decoupled from the HTTP framework (Express/Fastify), the migration is mostly copy-pasting the Service layer.
    **靈活性**：想從單體 Express 應用遷移到 Serverless (AWS Lambda)？如果你的邏輯與 HTTP 框架（Express/Fastify）解耦，遷移工作大部分只是複製貼上 Service 層。

### Architecture Flow
### 架構流程

A typical request flow in a production Node.js service:
生產環境 Node.js 服務的典型請求流程：

`Request` -> **Router** -> **Middleware** (Auth/Validation) -> **Controller** (DTO parsing) -> **Service** (Business Logic) -> **Repository** (ORM/Query Builder) -> `Database`

`請求` -> **路由** -> **中介軟體** (驗證/校驗) -> **控制器** (DTO 解析) -> **服務** (業務邏輯) -> **儲存庫** (ORM/查詢建構器) -> `資料庫`

---

## 4. Walkthrough / Example
## 4. 逐步示例

### Scenario: User Registration
### 場景：使用者註冊

We need to register a user. The logic involves:
1.  Validating input.
2.  Checking if the email exists.
3.  Hashing the password.
4.  Saving to DB.
5.  Sending a welcome email.

我們需要註冊一位使用者。邏輯包含：
1.  驗證輸入。
2.  檢查 Email 是否存在。
3.  雜湊（Hash）密碼。
4.  存入資料庫。
5.  發送歡迎信。

### Level 1: The Naive Approach (The Anti-Pattern)
### Level 1：天真的做法（反模式）

This is typical "Tutorial Code". Everything is in the route handler.
這是典型的「教學範例程式碼」。所有東西都在路由處理器裡。

```javascript
// routes/user.js
const express = require('express');
const router = express.Router();
const db = require('../models'); // Direct DB dependency
const bcrypt = require('bcrypt');
const mailer = require('../utils/mailer'); // Direct Mailer dependency

router.post('/register', async (req, res) => {
  try {
    // 1. Validation mixed with logic
    if (!req.body.email || !req.body.password) {
      return res.status(400).send('Missing fields');
    }

    // 2. Direct DB calls in controller
    const existing = await db.User.findOne({ where: { email: req.body.email } });
    if (existing) {
      return res.status(409).send('User exists');
    }

    // 3. Business logic (hashing) mixed in
    const hashedPassword = await bcrypt.hash(req.body.password, 10);

    const user = await db.User.create({
      email: req.body.email,
      password: hashedPassword
    });

    // 4. Side effect (Email) tightly coupled
    await mailer.sendWelcome(user.email);

    res.status(201).json(user);
  } catch (err) {
    res.status(500).send(err.message);
  }
});

module.exports = router;
```

**Why this fails at scale:**
*   **Hard to Test**: To test this, you must mock `req`, `res`, `db`, and `mailer`.
*   **No Reusability**: If you want to create a user from a CLI script or a cron job, you can't reuse this logic because it's tied to `req` and `res`.

**為何這在規模化時會失敗：**
*   **難以測試**：要測試這段程式，你必須 mock `req`、`res`、`db` 和 `mailer`。
*   **無法重用**：如果你想從 CLI 腳本或排程任務建立使用者，你無法重用這段邏輯，因為它綁死在 `req` 和 `res` 上。

---

### Level 2: Layered Architecture with Dependency Injection
### Level 2：具備依賴注入的分層架構

Let's refactor using Classes and Manual Dependency Injection.
讓我們使用類別（Classes）與手動依賴注入來重構。

#### 1. Repository Layer (Data Access)
#### 1. Repository 層（資料存取）

Encapsulates DB operations.
封裝資料庫操作。

```javascript
// repositories/UserRepository.js
class UserRepository {
  constructor(dbModel) {
    this.model = dbModel;
  }

  async findByEmail(email) {
    return this.model.findOne({ where: { email } });
  }

  async create(userData) {
    return this.model.create(userData);
  }
}
module.exports = UserRepository;
```

#### 2. Service Layer (Business Logic)
#### 2. Service 層（業務邏輯）

Pure business logic. No `req`, no `res`. Notice we inject dependencies in the constructor.
純業務邏輯。沒有 `req`，沒有 `res`。注意我們在建構子中注入依賴。

```javascript
// services/UserService.js
class UserService {
  constructor(userRepository, mailerService) {
    this.userRepo = userRepository;
    this.mailer = mailerService;
  }

  async registerUser(email, password) {
    const existing = await this.userRepo.findByEmail(email);
    if (existing) {
      throw new Error('USER_ALREADY_EXISTS'); // Throw generic errors, not HTTP errors
    }

    // Logic: Password hashing belongs here or in a domain entity
    const hashedPassword = await this.hashPassword(password); 
    
    const newUser = await this.userRepo.create({ email, password: hashedPassword });
    
    await this.mailer.sendWelcome(email);
    return newUser;
  }

  async hashPassword(password) {
    // Implementation details...
    return 'hashed_' + password; 
  }
}
module.exports = UserService;
```

#### 3. Controller Layer (HTTP Interface)
#### 3. Controller 層（HTTP 介面）

Handles HTTP status codes and parsing.
處理 HTTP 狀態碼與解析。

```javascript
// controllers/UserController.js
class UserController {
  constructor(userService) {
    this.userService = userService;
  }

  async register(req, res, next) {
    try {
      const { email, password } = req.body;
      const user = await this.userService.registerUser(email, password);
      res.status(201).json(user);
    } catch (error) {
      if (error.message === 'USER_ALREADY_EXISTS') {
        return res.status(409).json({ error: 'User already exists' });
      }
      next(error);
    }
  }
}
module.exports = UserController;
```

#### 4. Wiring it up (Composition Root)
#### 4. 組合依賴（Composition Root）

This is where we connect the dots. In frameworks like NestJS, this is handled by the framework. In vanilla Node/Express, we do it at the app entry point.
這是我們連接所有點的地方。在 NestJS 等框架中，這由框架處理。在原生 Node/Express 中，我們在應用程式入口點處理。

```javascript
// app.js (Composition Root)
const db = require('./models');
const mailer = require('./utils/mailer');

// Inject dependencies manually
const userRepo = new UserRepository(db.User);
const userService = new UserService(userRepo, mailer);
const userController = new UserController(userService);

// Bind the method to the instance context
app.post('/register', (req, res, next) => userController.register(req, res, next));
```

**Why this is better:**
*   **Testing**: You can test `UserService` by passing a fake `userRepo` that returns predefined data. No database required.
*   **Separation**: The Controller handles HTTP (409 vs 201). The Service handles Logic (Hashing, Email flow).

**為何這樣更好：**
*   **測試**：你可以透過傳入一個回傳預定義資料的假 `userRepo` 來測試 `UserService`。完全不需要資料庫。
*   **分離**：Controller 處理 HTTP（409 vs 201）。Service 處理邏輯（雜湊、Email 流程）。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 1. The "Fat Controller"
### 1. 「肥大的控制器」
**Description**: Keeping validation, business logic, and response formatting all inside the controller function.
**Why it's bad**: Violates Single Responsibility Principle (SRP). Hard to read, impossible to unit test logic in isolation.
**Solution**: Move logic to Service, validation to Middleware (e.g., Joi/Zod), and data access to Repository.
**描述**：將驗證、業務邏輯和回應格式化全部保留在控制器函式中。
**壞處**：違反單一職責原則 (SRP)。難以閱讀，無法獨立對邏輯進行單元測試。
**解法**：將邏輯移至 Service，驗證移至 Middleware（如 Joi/Zod），資料存取移至 Repository。

### 2. Leaky Abstractions (Passing `req` to Service)
### 2. 洩漏的抽象（將 `req` 傳入 Service）
**Description**: `userService.createUser(req)`
**Why it's bad**: The Service layer now knows about HTTP. You cannot reuse this service for a WebSocket handler or a Cron job without mocking a fake `req` object.
**Solution**: Pass explicit arguments (`email`, `password`) or a DTO (Data Transfer Object).
**描述**：`userService.createUser(req)`
**壞處**：Service 層現在知道 HTTP 的存在。你無法在 WebSocket 處理器或 Cron Job 中重用此服務，除非你 mock 一個假的 `req` 物件。
**解法**：傳遞明確的參數（`email`, `password`）或 DTO（資料傳輸物件）。

### 3. Tight Coupling with Singletons
### 3. 與單例模式的緊密耦合
**Description**: `const db = require('./db')` inside `UserService.js`.
**Why it's bad**: You cannot swap the database implementation for testing. You are stuck with the global state.
**Solution**: Use Dependency Injection (as shown in the walkthrough).
**描述**：在 `UserService.js` 內部直接 `const db = require('./db')`。
**壞處**：你無法為了測試而替換資料庫實作。你被全域狀態綁架了。
**解法**：使用依賴注入（如逐步示例所示）。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How do you handle "Circular Dependencies" in a layered Node.js architecture?
### Q1: 在分層的 Node.js 架構中，你如何處理「循環依賴」？

*   **Context**: Service A needs Service B, and Service B needs Service A.
*   **Key Points**:
    *   Acknowledge this is usually a design flaw (Tight Coupling).
    *   **Solution 1**: Refactor. Extract the shared logic into a third Service C.
    *   **Solution 2**: Use Event-Driven Architecture. Service A emits an event, Service B listens to it (decoupling execution).
    *   **Solution 3 (Last resort)**: Use lazy injection or `module.exports` mutation (messy).
*   **情境**：Service A 需要 Service B，而 Service B 又需要 Service A。
*   **回答要點**：
    *   承認這通常是設計缺陷（緊密耦合）。
    *   **解法 1**：重構。將共用邏輯提取到第三個 Service C。
    *   **解法 2**：使用事件驅動架構。Service A 發出事件，Service B 監聽該事件（解耦執行）。
    *   **解法 3（下策）**：使用延遲注入（Lazy injection）或修改 `module.exports`（很髒）。

### Q2: Why use a Repository pattern if I'm using an ORM (like Mongoose or Sequelize)?
### Q2: 如果我已經在使用 ORM（如 Mongoose 或 Sequelize），為什麼還需要 Repository 模式？

*   **Key Points**:
    *   **Abstraction**: ORMs change (e.g., migrating from Mongoose v5 to v6, or switching to TypeORM). A Repository acts as an adapter/boundary.
    *   **Testing**: Mocking a Repository method (`findUser`) is easier and cleaner than mocking complex ORM query chains (`User.find().where().limit().exec()`).
    *   **Domain Language**: Repositories allow method names that speak business language (`findActiveUsers`) rather than SQL language (`where status = 'active'`).
*   **回答要點**：
    *   **抽象化**：ORM 會變（例如從 Mongoose v5 升級到 v6，或換成 TypeORM）。Repository 充當適配器/邊界。
    *   **測試**：Mock 一個 Repository 方法（`findUser`）比 Mock 複雜的 ORM 查詢鏈（`User.find().where().limit().exec()`）更容易且乾淨。
    *   **領域語言**：Repository 允許使用具備業務意義的方法名稱（`findActiveUsers`），而非 SQL 語法（`where status = 'active'`）。

### Q3: Explain how Dependency Injection aids in Unit Testing versus Integration Testing.
### Q3: 請解釋依賴注入如何協助單元測試與整合測試。

*   **Key Points**:
    *   **Unit Testing**: DI allows injecting *Mocks/Stubs* (e.g., an in-memory DB array) into the Service. This makes tests run in milliseconds and isolates the logic.
    *   **Integration Testing**: DI allows injecting the *Real* DB connection (or a test DB connection) to verify the actual data flow.
    *   Without DI, you are forced to do Integration Testing for everything, which is slow and brittle.
*   **回答要點**：
    *   **單元測試**：DI 允許將 *Mocks/Stubs*（例如記憶體中的陣列 DB）注入到 Service 中。這讓測試在毫秒內完成並隔離邏輯。
    *   **整合測試**：DI 允許注入*真實*的 DB 連線（或測試用的 DB 連線）以驗證實際資料流。
    *   沒有 DI，你將被迫對所有東西進行整合測試，這既緩慢又脆弱。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Summary
### 小結

1.  **Layer Your App**: Always separate Controller (HTTP), Service (Logic), and Repository (Data).
    **分層你的應用**：永遠分離 Controller（HTTP）、Service（邏輯）與 Repository（資料）。
2.  **Inject Dependencies**: Avoid `require`ing models directly in services. Inject them to enable testing and loose coupling.
    **注入依賴**：避免在 Service 中直接 `require` 模型。透過注入來實現測試與鬆散耦合。
3.  **Keep Controllers Skinny**: Controllers should only parse requests and send responses. Logic belongs in Services.
    **保持 Controller 輕量**：Controller 只應解析請求與發送回應。邏輯屬於 Service。
4.  **Isolate Domain Logic**: Your business rules should not depend on Express, Fastify, or Mongoose directly.
    **隔離領域邏輯**：你的業務規則不應直接依賴 Express、Fastify 或 Mongoose。

### Next Steps
### 後續延伸

*   **Study**: Look into **NestJS**. It is a framework that enforces these patterns (Modules, DI, Controllers, Services) out of the box. Even if you don't use it, understanding its structure will make you a better Node.js architect.
    **學習**：研究 **NestJS**。它是一個開箱即強制執行這些模式（模組、DI、控制器、服務）的框架。即使你不使用它，理解它的結構也能讓你成為更好的 Node.js 架構師。
*   **Practice**: Take an existing "spaghetti" project and refactor *one* route to use the Controller-Service-Repository pattern.
    **實作**：拿一個現有的「義大利麵」專案，並重構*一個*路由以使用 Controller-Service-Repository 模式。
*   **Next Chapter**: Proceed to **Performance Optimization & Event Loop**, where we explore how to ensure your beautifully architected app runs efficiently under load.
    **下一章**：前往 **效能優化與 Event Loop**，我們將探討如何確保你設計精良的應用程式在高負載下高效運作。