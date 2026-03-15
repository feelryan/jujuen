# 常見反模式與開發陷阱 / Common Anti-patterns & Pitfalls

在 Express 開發中，靈活性是雙面刃。由於框架本身對架構沒有強制規定（Unopinionated），開發者很容易寫出難以維護的「義大利麵程式碼（Spaghetti Code）」。本章節將盤點那些讓資深工程師皺眉的常見錯誤，並提供重構與預防的具體策略。

---

## Mental model｜心智模型

要避免反模式，首先要建立正確的 Express 運作心智模型：**「流水線（Pipeline）」而非「單一腳本（Monolithic Script）」**。

### 1. The Request Pipeline (請求流水線)
不要把一個 Route Handler 視為一個獨立的程式進入點，而應視為流水線中的一個環節。
- **錯誤觀念**：請求進來 -> 在 Controller 裡寫完所有邏輯 (DB, Validation, Business Logic) -> 回傳。
- **正確觀念**：請求進來 -> Middleware (驗證/淨化) -> Controller (分派任務) -> Service (商業邏輯) -> Repository (資料存取) -> 回傳。

### 2. The Async Flow (非同步流)
Express 4.x (目前主流) 的核心是基於 Callback 的，對 Promise 的支援並不原生（直到 Express 5）。
- **陷阱**：在 `async` 函數中拋出錯誤，若沒有 `catch` 並傳遞給 `next()`，請求會「掛起（Hang）」直到超時，因為 Express 捕捉不到這個異常。

---

## Patterns & best practices｜常見模式與最佳實務

在深入反模式之前，先確立什麼是「好」的模式。

### 1. Thin Controller, Fat Service (瘦控制器，胖服務)
Controller 應該只負責 HTTP 相關的事務（解析 Request、呼叫 Service、回傳 Response）。所有的商業邏輯（如：計算折扣、檢查庫存）應移至 Service Layer。

### 2. Centralized Error Handling (集中式錯誤處理)
不要在每個 Route 裡寫 `res.status(500).send('Error')`。應該將錯誤透過 `next(err)` 傳遞給全域的 Error Handling Middleware。

### 3. Explicit Returns (明確的回傳)
發送 Response 時，習慣加上 `return`，例如 `return res.json(...)`。這不是為了回傳值給 Express，而是為了**終止函數執行**，避免後續程式碼繼續跑而導致 "Headers already sent" 錯誤。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

以下是 Code Review 中最常被標記的嚴重錯誤：

### 1. The "God" Controller (全能控制器)
將所有邏輯寫在 Route Handler 中。

- **❌ Bad Practice:**
  ```javascript
  app.post('/register', async (req, res) => {
    // 1. Validate manually
    if (!req.body.email) return res.status(400).send('Email required');
    
    // 2. Direct DB access in controller
    const user = await db.query('SELECT * FROM users WHERE email = ?', [req.body.email]);
    if (user) return res.status(400).send('User exists');
    
    // 3. Business logic mixed with HTTP
    const hash = crypto.createHash('sha256').update(req.body.password).digest('hex');
    
    // 4. More DB access
    await db.query('INSERT INTO users ...');
    
    res.json({ success: true });
  });
  ```
- **後果**：難以測試、程式碼重複、難以閱讀。

### 2. The "Hanging" Request (被遺忘的 Promise)
在 Express 4 中使用 `async/await` 但忘記 `try/catch`。

- **❌ Bad Practice:**
  ```javascript
  app.get('/data', async (req, res) => {
    const data = await db.getData(); // 如果這裡 throw error
    res.json(data);
  }); 
  // Express 4 捕捉不到 async error，Client 端會一直轉圈圈直到 timeout。
  ```
- **✅ Fix:** 使用 `try/catch` 包裹並呼叫 `next(err)`，或使用 `express-async-handler`。

### 3. "Headers Already Sent" (重複發送回應)
在發送回應後，程式碼繼續執行並試圖再次發送回應。

- **❌ Bad Practice:**
  ```javascript
  app.get('/user/:id', (req, res) => {
    if (!req.params.id) {
      res.status(400).send('ID missing'); // 這裡發送了，但沒有 return
    }
    // 程式繼續往下跑
    res.send('User Data'); // 💥 Error: Can't set headers after they are sent.
  });
  ```

### 4. Global State Mutation (全域變數污染)
在模組層級宣告變數來儲存請求資料。

- **❌ Bad Practice:**
  ```javascript
  let currentUser; // 😱 全域變數！

  app.get('/login', (req, res) => {
    currentUser = req.body.username; // 如果同時有兩個 User 登入，資料會互相覆蓋（Race Condition）
    // ...
  });
  ```
- **✅ Fix:** 使用 `res.locals` 或將資料透過函數參數傳遞。

### 5. Callback Hell (回呼地獄)
雖然現代 JS 已有 Async/Await，但維護舊專案時常看到深層巢狀結構。

- **❌ Bad Practice:**
  ```javascript
  fs.readFile('file.txt', (err, data) => {
    if(err) res.send(err);
    db.query('...', (err, result) => {
      if(err) res.send(err);
      request('http://...', (err, response) => {
        res.send('Done');
      })
    })
  })
  ```

---

## Checklists & workflows｜檢查清單與流程

在提交 PR 或進行 Code Review 時，請使用此清單自我檢查：

### 🛡 Code Review Checklist
- [ ] **Controller Slimness**: Controller 是否只包含 HTTP 邏輯？商業邏輯是否已移至 Service？
- [ ] **Async Safety**: 所有的 `async` Route Handler 是否都有 `try/catch` 或是使用了 Wrapper (如 `express-async-handler`)？
- [ ] **Return on Response**: 所有的 `res.send/json` 前面是否都有 `return` 關鍵字？(除非是函數的最後一行)
- [ ] **No Global State**: 確保沒有在 `module.exports` 外層定義變數來暫存 Request 相關資料。
- [ ] **Status Codes**: 錯誤處理是否回傳了正確的 HTTP Status Code (4xx vs 5xx) 而不僅僅是 200 OK 帶著錯誤訊息？
- [ ] **Security**: 是否在生產環境中隱藏了 Error Stack Trace (`NODE_ENV === 'production'`)？

### 🚦 Decision Tree: Where does this code go?
當你寫下一段程式碼時，請依此判斷放置位置：
1. **它是用來驗證輸入格式嗎？** -> `Middleware` (e.g., Joi/Zod)
2. **它涉及資料庫查詢或複雜運算嗎？** -> `Service`
3. **它只是負責決定回傳 JSON 還是 HTML？** -> `Controller`
4. **它是通用的錯誤處理？** -> `Error Handling Middleware`

---

## Real-world examples｜實戰案例

### 案例：重構一個脆弱的 User Profile API

#### 🔴 Before (Anti-pattern)
這段程式碼包含了：God Controller、未處理的 Promise、潛在的 Header sent 錯誤。

```javascript
// routes/user.js
const User = require('../models/user');

router.get('/:id', async (req, res) => {
  // 1. Logic in Controller
  if (req.params.id === 'admin') {
     res.status(403).json({ error: 'Cannot query admin' });
     // 2. Missing return: Code continues execution!
  }

  // 3. Unhandled Promise Rejection risk (in Express 4)
  const user = await User.findById(req.params.id);
  
  if (!user) {
    // 4. Inconsistent response structure
    return res.send('User not found'); 
  }

  // 5. Business logic leaking
  const userData = user.toObject();
  delete userData.password;
  delete userData.__v;

  res.json(userData);
});
```

#### 🟢 After (Best Practice)
重構後：職責分離、安全、可讀。

```javascript
// 1. Middleware for validation
const validateUserId = (req, res, next) => {
  if (req.params.id === 'admin') {
    return res.status(403).json({ error: 'Access denied' });
  }
  next();
};

// 2. Service for logic & data access
// services/userService.js
const getUserProfile = async (id) => {
  const user = await User.findById(id).lean(); // use lean() for performance
  if (!user) throw new Error('USER_NOT_FOUND');
  
  const { password, __v, ...profile } = user;
  return profile;
};

// 3. Controller handles HTTP only
// controllers/userController.js
const asyncHandler = require('express-async-handler'); // Wrapper for safety

const getUser = asyncHandler(async (req, res) => {
  const userProfile = await userService.getUserProfile(req.params.id);
  res.json(userProfile);
});

// 4. Centralized Error Handling (in app.js)
// app.use((err, req, res, next) => {
//   if (err.message === 'USER_NOT_FOUND') return res.status(404).json(...);
//   res.status(500).json(...);
// });

// Route definition
router.get('/:id', validateUserId, getUser);
```