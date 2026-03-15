# 專案結構與分層架構設計 / Project Structure & Layered Architecture

## Mental model｜心智模型

Express 是一個 "Unopinionated"（不預設立場）的框架，這意味著它給你極大的自由，但也容易導致混亂。要建立可維護的 Express 應用，最有效的心智模型是將應用程式視為 **「餐廳運作流程」 (The Restaurant Analogy)**。

請想像你的後端 API 是一間餐廳：

1.  **Routes (The Host / 接待員)**:
    *   負責將請求（客人）引導到正確的桌號（API Endpoint）。
    *   **原則**：只做路徑對應，不處理任何邏輯。
2.  **Controllers (The Waiter / 服務生)**:
    *   負責接收訂單（解析 `req`）、將訂單交給廚房（呼叫 Service）、並將做好的菜端給客人（回傳 `res`）。
    *   **原則**：服務生不應該在桌邊煮菜。Controller 僅處理 HTTP 介面溝通，不包含業務邏輯。
3.  **Services (The Chef / 廚師)**:
    *   負責實際的烹飪（業務邏輯）。例如：計算價格、檢查庫存、混合食材。
    *   **原則**：廚師不關心是哪位服務生送單來的，也不直接面對客人。Service 應與 HTTP 無關（不應出現 `req` 或 `res` 物件）。
4.  **Data Access Layer / Models (The Pantry & Supplier / 食材庫與供應商)**:
    *   負責從倉庫拿取原料（資料庫查詢 SQL/ORM）。
    *   **原則**：只管存取資料，不過問這筆資料要拿來做什麼菜。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. The Standard Layered Structure (標準分層結構)

在真實專案中，請避免將所有程式碼塞在 `app.js` 或 `routes/` 中。推薦採用以下目錄結構：

```text
src/
├── app.js               # App entry point (setup middleware, db connection)
├── server.js            # Server entry point (port listening)
├── config/              # Environment variables & configuration
├── api/                 # Interface Layer
│   ├── routes/          # Route definitions (URL mapping)
│   ├── controllers/     # Request handling, validation, response
│   └── middlewares/     # Express middlewares (auth, logging)
├── services/            # Business Logic Layer (The "Brain")
├── models/              # Data Access Layer (Schema definitions, SQL queries)
├── utils/               # Helper functions (date formatting, math)
├── jobs/                # Cron jobs or background tasks
└── loaders/             # Startup scripts (dependency injection setup)
```

### 2. Separation of Concerns (關注點分離)

*   **Controller Pattern**:
    *   Controller 應該是 **"Skinny" (瘦的)**。
    *   它只做三件事：驗證輸入 (Validate Input)、呼叫服務 (Call Service)、回傳結果 (Send Response)。
    *   所有錯誤處理應透過 `next(err)` 傳遞給 Global Error Handler。

*   **Service Pattern**:
    *   Service 包含 **"Business Rules" (業務規則)**。
    *   例如：「註冊時密碼必須雜湊」、「轉帳時餘額不能為負」。
    *   Service 方法應回傳純資料（Objects/Promises），而不是 HTTP Response。
    *   這使得 Service 可以被重複使用（例如被 CLI 工具或 Cron Job 呼叫），也更容易進行單元測試。

### 3. Configuration Management (配置管理)

*   永遠不要將 API Key、Database URL 硬編碼 (Hardcode) 在程式碼中。
*   使用 `dotenv` 載入 `.env` 檔案。
*   建立一個集中式的 `config/index.js` 來匯出環境變數，並在該處進行驗證（例如：若缺少 `DB_URL` 則啟動失敗）。

### 4. Dependency Injection (依賴注入 - 進階)

*   為了提升測試性，不要在 Service 內部直接 `require` Model。
*   可以透過 Constructor Injection 或簡單的 Function Parameter Injection 將 Model 傳入 Service。這讓你在寫 Unit Test 時可以輕鬆 Mock 資料庫層。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Fat Controllers (肥胖的控制器)
這是最常見的錯誤。將 SQL 查詢、資料運算、第三方 API 呼叫全部寫在 `router.get('/', (req, res) => { ... })` callback 中。
*   **後果**：難以閱讀、難以測試、程式碼無法重用。

### 2. The "Utils" Dump (工具函式垃圾場)
建立一個巨大的 `utils.js` 檔案，裡面塞滿了毫不相關的函式（從資料庫連線到字串處理）。
*   **修正**：依功能拆分，例如 `utils/logger.js`, `utils/date-helper.js`。

### 3. Logic in Routes (路由中的邏輯)
在 `routes/index.js` 裡面直接寫邏輯，而不是導向 Controller。
*   **後果**：路由檔變得冗長，無法一目了然看到 API 的結構。

### 4. Circular Dependencies (循環依賴)
Service A 引用 Service B，Service B 又引用 Service A。
*   **後果**：Node.js 啟動時可能崩潰或導致未定義行為。
*   **修正**：重新設計架構，提取共用邏輯到第三個 Service 或 Utils，或使用 Event Emitter 解耦。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Where does this code go? (這段程式碼該放哪？)

當你寫下一行程式碼時，請依序問自己：

1.  **它是否直接操作 `req` 或 `res` 物件？**
    *   Yes -> **Controller** (或 Middleware)。
    *   No -> 繼續。
2.  **它是否涉及資料庫查詢 (SQL/Mongoose)？**
    *   Yes -> **Model / Data Access Layer**。
    *   No -> 繼續。
3.  **它是否包含業務規則（例如：檢查權限、計算折扣、流程控制）？**
    *   Yes -> **Service**。
    *   No -> 繼續。
4.  **它是否是通用的輔助功能（例如：格式化日期、生成隨機字串）？**
    *   Yes -> **Utils**。

### Refactoring Checklist (重構檢查表)

- [ ] **Routes**: 路由檔案中是否只包含 URL 定義與 Middleware 綁定？(不應有 `function(req, res) { ... }` 的實作細節)。
- [ ] **Controllers**: 是否移除了所有的 SQL/DB 查詢語句？
- [ ] **Services**: 是否完全移除了 `req` 和 `res` 物件？Service 是否會拋出標準 Error 而不是直接回傳 HTTP Status Code？
- [ ] **Config**: 專案中是否還有 Hardcoded 的密鑰或路徑？

---

## Real-world examples｜實戰案例

### Scenario: User Registration (使用者註冊)

#### ❌ Bad Practice (All in one place)

```javascript
// routes/users.js
router.post('/register', async (req, res) => {
  // Validation logic mixed in
  if (!req.body.email) return res.status(400).send('Email required');
  
  // Business logic & DB logic mixed in
  const userExists = await db.query('SELECT * FROM users WHERE email = ?', [req.body.email]);
  if (userExists.length > 0) return res.status(409).send('User exists');
  
  const hashedPassword = await bcrypt.hash(req.body.password, 10);
  await db.query('INSERT INTO users ...', [req.body.email, hashedPassword]);
  
  res.status(201).send('Created');
});
```

#### ✅ Good Practice (Layered Architecture)

**1. Route Layer (`routes/user.js`)**
*只負責定義路徑與串接 Controller。*

```javascript
const { Router } = require('express');
const UserController = require('../controllers/userController');
const router = Router();

router.post('/register', UserController.register);

module.exports = router;
```

**2. Controller Layer (`controllers/userController.js`)**
*處理 HTTP 輸入輸出。*

```javascript
const UserService = require('../services/userService');

class UserController {
  async register(req, res, next) {
    try {
      const { email, password } = req.body;
      // 呼叫 Service，不關心 Service 如何實作
      const user = await UserService.signUp(email, password); 
      return res.status(201).json({ user });
    } catch (e) {
      // 將錯誤交給 Error Handling Middleware
      return next(e); 
    }
  }
}
module.exports = new UserController();
```

**3. Service Layer (`services/userService.js`)**
*純粹的業務邏輯，可測試，無 HTTP 依賴。*

```javascript
const UserModel = require('../models/userModel');
const bcrypt = require('bcrypt');

class UserService {
  async signUp(email, password) {
    // 檢查業務規則
    const userRecord = await UserModel.findByEmail(email);
    if (userRecord) {
      throw new Error('User already exists'); // 這裡拋出錯誤，由 Controller 捕獲
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    
    // 呼叫資料層
    return await UserModel.create(email, hashedPassword);
  }
}
module.exports = new UserService();
```