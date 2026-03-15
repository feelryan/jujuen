# 專案架構設計與模組化模式 / Project Architecture & Modular Patterns

## Mental model｜心智模型

在 Node.js 的世界裡，最常見的痛點不是語言本身，而是**缺乏官方強制規範（Unopinionated）**。這是一把雙面刃：它給了你極大的自由，但也容易導致「義大利麵程式碼（Spaghetti Code）」。

要建立穩固的架構，請建立以下的心智模型：

### 1. The Restaurant Analogy (餐廳隱喻)
將你的應用程式想像成一間餐廳，請求（Request）是訂單，回應（Response）是餐點。
- **Router / Controller (服務生)**：負責接收訂單（Request），確認格式正確，然後轉交給廚房。**服務生不應該煮菜**（Controller 不應包含商業邏輯）。
- **Service Layer (廚房/主廚)**：這是核心。主廚根據食譜（商業邏輯）處理食材。主廚不直接去農場採收，而是從冰箱拿（呼叫 Data Layer）。
- **Data Access Layer / DAO (冰箱/倉儲)**：只負責存取資料庫或外部 API。它不在乎這些資料要拿來做什麼菜，只負責準確地拿出來。

### 2. Dependency Direction (依賴方向)
依賴關係應該是**單向流動**的。
- **正確**：Controller -> Service -> Data Layer
- **錯誤**：Data Layer -> Service (循環依賴) 或 Controller 直接操作 SQL。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Three-Layer Architecture (三層式架構)
這是 Node.js 後端（如 Express/Koa/Fastify）最標準的實作模式。

- **Controller Layer (Interface Layer)**
  - **職責**：解析 HTTP 請求、驗證輸入參數 (Validation)、呼叫 Service、回傳 HTTP 狀態碼與 JSON。
  - **Rule**：不可直接存取 DB。
- **Service Layer (Business Logic Layer)**
  - **職責**：執行核心業務規則（如：計算折扣、密碼雜湊、觸發 Email）。
  - **Rule**：不可包含 `req` 或 `res` 物件（保持與 HTTP 傳輸層解耦，方便測試）。
- **Data Access Layer (Repository / DAO)**
  - **職責**：執行 SQL 查詢、ORM 操作、Redis 存取。
  - **Rule**：只回傳純資料物件 (POJO) 或 Model 實例。

### 2. Dependency Injection (DI) & Inversion of Control (IoC)
即使不使用 NestJS 這種強型別框架，在原生 JS/TS 中實作 DI 也是必要的，這能大幅提升可測試性。

- **Manual DI (手動注入)**：
  不要在模組內部直接 `require` 或 `import` 依賴的實例，而是透過 `constructor` 或工廠函式傳入。
  ```javascript
  // Bad: Hard to mock database for testing
  const db = require('./db');
  class UserService {
    create(user) { return db.insert(user); }
  }

  // Good: Dependency Injection
  class UserService {
    constructor(userRepository) {
      this.userRepo = userRepository;
    }
    create(user) { return this.userRepo.insert(user); }
  }
  ```

### 3. Folder Structure: Feature vs. Technical
隨著專案擴大，資料夾結構應從「按技術分層」轉向「按功能模組分層」。

- **Small Project (Technical Role)**:
  ```text
  /controllers
  /services
  /models
  ```
- **Large Project (Domain/Feature Based)**:
  ```text
  /modules
    /users
      user.controller.js
      user.service.js
      user.repository.js
    /orders
      order.controller.js
      ...
  ```
  **Why?** 當你要修改「訂單功能」時，你不需要在三個不同的資料夾跳來跳去。這也更符合 Domain-Driven Design (DDD) 的雛形。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The Fat Controller (肥胖控制器)
這是最常見的反模式。開發者將 SQL 查詢、資料驗證、業務邏輯全部寫在 Route Handler 裡。
- **後果**：無法單元測試（必須啟動 HTTP Server 才能測）、邏輯無法在其他地方重用（例如 WebSocket 或 Cron Job 也想用同樣邏輯時）、程式碼難以閱讀。

### 2. Circular Dependencies (循環依賴)
模組 A 引用 模組 B，模組 B 又引用 模組 A。
- **Node.js 行為**：Node.js 可能會回傳一個尚未完全初始化的空物件 `{}`，導致 `TypeError: x is not a function`。
- **解法**：重構架構，通常代表這兩個模組耦合過深，應提取共用邏輯到第三個模組（如 `common` 或 `shared`），或使用 Dependency Injection 延遲解析。

### 3. God Object / Utils Dumping Ground
建立一個 `utils.js` 或 `helpers.js`，然後把所有不知道放哪裡的函式都丟進去。
- **後果**：這個檔案會變成數千行的巨獸，且依賴關係混亂。
- **解法**：將工具函式分類，如 `date-utils.js`, `string-formatters.js`, `validation-helpers.js`。

### 4. Global State (全域狀態)
使用 `global.myConfig` 或在模組頂層宣告可變變數 (mutable variables) 來共享狀態。
- **後果**：在並發請求下（雖然 Node 是單執行緒，但非同步操作會交錯），請求 A 可能會汙染請求 B 的資料。這也是測試的惡夢。

---

## Checklists & workflows｜檢查清單與流程

在進行 Code Review 或重構時，請使用此清單檢查架構健康度：

### Architecture Health Checklist
- [ ] **Controller 潔癖檢查**：Controller 是否包含任何 SQL 語句或 ORM 查詢？（若有，請移至 Service/DAO）。
- [ ] **HTTP 解耦檢查**：Service 層是否引用了 `express` 的 `req` 或 `res` 物件？（若有，請移除，改為傳遞參數）。
- [ ] **環境變數隔離**：設定檔（Config）是否集中管理？程式碼中是否有 Hard-coded 的 API Key 或 DB URL？
- [ ] **錯誤處理路徑**：是否有統一的 Error Handling Middleware？Service 層是否只拋出 Error 而不是直接回傳 HTTP Response？
- [ ] **依賴注入**：核心業務邏輯是否容易被 Mock？（例如：能否在不連線真實 DB 的情況下測試 Service？）

### Refactoring Workflow: From Spaghetti to Layered
如果你接手一個遺留專案，請依此順序重構：
1.  **Extract Routes**: 將 `app.js` 裡面的路由定義移到 `routes/` 資料夾。
2.  **Extract Controllers**: 將路由 callback 中的邏輯移到 `controllers/`。
3.  **Extract Services**: 辨識 Controller 中的業務邏輯，移到 `services/`。
4.  **Extract Data Access**: 將 SQL/ORM 操作移到 `repositories/` 或 `models/`。

---

## Real-world examples｜實戰案例

### Scenario: User Registration (使用者註冊)

#### ❌ The "Spaghetti" Way (Anti-pattern)
所有邏輯混雜在一起，難以維護。

```javascript
// routes/users.js
const express = require('express');
const router = express.Router();
const db = require('../db'); // Direct DB access

router.post('/register', async (req, res) => {
  try {
    // 1. Validation Logic mixed in
    if (!req.body.email || !req.body.password) {
      return res.status(400).json({ error: 'Missing fields' });
    }

    // 2. Business Logic (Check exists) mixed with DB query
    const existing = await db.query('SELECT * FROM users WHERE email = ?', [req.body.email]);
    if (existing.length > 0) {
      return res.status(409).json({ error: 'User exists' });
    }

    // 3. More Business Logic (Hashing)
    // ... hashing logic ...

    // 4. DB Insert
    await db.query('INSERT INTO users ...');

    res.status(201).json({ success: true });
  } catch (err) {
    res.status(500).json({ error: 'Server error' });
  }
});
```

#### ✅ The "Layered" Way (Best Practice)
職責分離，Service 可被單元測試，Controller 專注於 HTTP。

**1. Controller (`controllers/user.controller.js`)**
```javascript
class UserController {
  constructor(userService) {
    this.userService = userService; // DI
  }

  async register(req, res, next) {
    try {
      const { email, password } = req.body;
      // Controller handles input extraction & simple validation
      if (!email || !password) throw new Error('InvalidInput');

      // Delegate to Service
      const user = await this.userService.registerUser(email, password);

      // Controller handles HTTP response
      res.status(201).json({ data: user });
    } catch (err) {
      next(err); // Pass to global error handler
    }
  }
}
```

**2. Service (`services/user.service.js`)**
```javascript
class UserService {
  constructor(userRepo, emailService) {
    this.userRepo = userRepo;
    this.emailService = emailService;
  }

  async registerUser(email, password) {
    // Pure Business Logic
    const existing = await this.userRepo.findByEmail(email);
    if (existing) throw new Error('UserAlreadyExists');

    const hashedPassword = await this.hashPassword(password);
    const newUser = await this.userRepo.create({ email, password: hashedPassword });

    // Side effect handled in service layer
    await this.emailService.sendWelcomeEmail(email);

    return newUser;
  }
  
  // ... helper methods ...
}
```

**3. Composition Root (`app.js` or `di-container.js`)**
```javascript
// Wiring everything together
const userRepo = new UserRepository(dbConnection);
const emailService = new EmailService(smtpConfig);
const userService = new UserService(userRepo, emailService);
const userController = new UserController(userService);

// Route definition
router.post('/register', (req, res, next) => userController.register(req, res, next));
```