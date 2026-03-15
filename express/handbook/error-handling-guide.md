# 錯誤處理實戰指南 / Error Handling Best Practices

在 Express 開發中，錯誤處理（Error Handling）往往是區分「玩具專案」與「生產級應用」的分水嶺。一個健壯的錯誤處理機制不僅能防止伺服器崩潰，還能確保客戶端收到一致的錯誤格式，並協助開發者快速定位問題。

本章節將帶你建立一套可擴展、安全且易於維護的全域錯誤處理機制。

---

## Mental model｜心智模型

要掌握 Express 的錯誤處理，你需要建立以下兩個核心觀念：

### 1. 錯誤處理的「軌道切換」 (The Track Switch)
想像 Express 的 Middleware 堆疊是一條由上而下的水流。
- **正常流程 (Happy Path)**：請求順著 `next()` 一路向下流動。
- **錯誤流程 (Error Path)**：一旦呼叫 `next(err)`（帶參數）或 `throw new Error()`，Express 會立即跳過所有標準 Middleware，直接尋找並跳轉到定義了 4 個參數的 **Error Handling Middleware** `(err, req, res, next)`。

### 2. 錯誤分類矩陣 (The Classification Matrix)
並非所有錯誤都是一樣的。在處理錯誤前，必須先分類：

| 類型 | 定義 | 範例 | 處理策略 |
| :--- | :--- | :--- | :--- |
| **Operational Errors**<br>(操作型錯誤) | 預期內的情況，非程式 bug。通常由使用者輸入或系統限制引起。 | 無效的輸入 (400)、找不到資源 (404)、資料庫連線逾時、權限不足 (403)。 | 回傳適當的 HTTP Status Code 與錯誤訊息給客戶端。**不需要**重啟伺服器。 |
| **Programmer Errors**<br>(程式型錯誤) | 程式碼本身的 Bug。代表程式進入了未知的損壞狀態。 | 讀取 undefined 的屬性、語法錯誤、傳遞錯誤參數給函數。 | 記錄詳細日誌，**讓 Process Crash 並重啟** (由 PM2 或 Docker 處理)，因為應用程式狀態已不可信。 |

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 集中式全域錯誤處理 (Centralized Global Error Handler)
不要在每個 Controller 裡寫 `res.status(500).send(...)`。所有的錯誤都應該流向最後一個 Middleware 進行統一處理。這確保了錯誤格式的一致性（例如：永遠回傳 JSON）。

### 2. 使用自定義錯誤類別 (Custom Error Classes)
建立一個繼承自 `Error` 的 `AppError` 類別，用來攜帶 HTTP Status Code 和 Operational 標記。

```javascript
// utils/AppError.js
class AppError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.statusCode = statusCode;
    this.status = `${statusCode}`.startsWith('4') ? 'fail' : 'error';
    this.isOperational = true; // 標記為可預期的操作型錯誤

    Error.captureStackTrace(this, this.constructor);
  }
}
module.exports = AppError;
```

### 3. Async/Await 的錯誤捕獲 (Handling Async Errors)
在 Express v4 中，Async 函數內的錯誤若沒有 `catch`，不會自動傳遞給 `next()`，會導致請求掛起 (Hang) 或 Unhandled Rejection。
**最佳解法**：使用 Higher-Order Function 包裝器（Wrapper），而非在每個 Controller 寫 `try-catch`。

> **註**：Express v5 (beta) 已原生支援 Async 錯誤捕獲，但在 v4 普及前，Wrapper 仍是標準做法。

### 4. 環境隔離策略 (Environment Separation)
- **Development**：回傳完整的 `stack trace` 與錯誤細節，方便除錯。
- **Production**：隱藏 `stack trace`，只回傳通用的錯誤訊息（如 "Something went wrong"），避免洩露系統架構與路徑資訊（Security）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 吞噬錯誤 (Swallowing Errors)
最危險的做法。這會導致請求無限期掛起（Client 端轉圈圈），且伺服器端沒有任何紀錄。

```javascript
// ❌ Anti-pattern
try {
  await someService();
} catch (err) {
  console.log('Error happened'); // 只有 log，沒有 next(err) 也沒有 res.send
  // Request hangs forever...
}
```

### 2. 拋出字串而非 Error 物件 (Throwing Strings)
```javascript
// ❌ Anti-pattern
throw "User not found"; 
```
這樣做會丟失 Stack Trace，導致你無法追蹤錯誤發生的檔案與行數。永遠使用 `new Error()` 或 `new AppError()`。

### 3. 200 OK 的錯誤回應 (The "200 OK" Error)
有些 API 設計會在發生錯誤時回傳 HTTP 200，但在 Body 裡寫 `{ "error": true }`。這破壞了 REST 語意，並導致監控工具（如 New Relic, Datadog）無法正確統計錯誤率。

### 4. 在 Header 送出後處理錯誤 (Headers Already Sent)
如果在 `res.send()` 之後又呼叫 `next(err)`，Express 預設的錯誤處理器會崩潰。確保錯誤處理發生在回應發送之前，或者在 Global Handler 中檢查 `res.headersSent`。

---

## Checklists & workflows｜檢查清單與流程

在 Code Review 或部署前，請檢查以下項目：

- [ ] **全域處理器位置**：Global Error Handler 是否放在 `app.js` 的 **最後一個** `app.use`？（必須在所有路由之後）。
- [ ] **參數數量**：Global Error Handler 是否明確定義了 4 個參數 `(err, req, res, next)`？少一個都會被視為普通 Middleware。
- [ ] **Async 防護**：所有的 Async Controller 是否都使用了 `catchAsync` 包裝器，或有完整的 try-catch 區塊？
- [ ] **未處理的 Rejection**：是否有監聽 `process.on('unhandledRejection')` 與 `process.on('uncaughtException')` 作為最後一道防線？
- [ ] **安全性檢查**：確認生產環境 (NODE_ENV=production) **絕對沒有** 回傳 `err.stack` 給客戶端。
- [ ] **404 處理**：是否在 Global Error Handler 之前，有一個處理「未定義路由」的 Middleware？

### 錯誤處理決策樹 (Decision Tree)

1. **錯誤發生**
2. **是 Operational Error (如 404, Validation Error)?**
   - YES -> 封裝成 `AppError`，傳遞給 `next()`。
   - NO (Unknown Error) -> 記錄詳細 Log，封裝成 500 Generic Error，傳遞給 `next()`。
3. **進入 Global Error Handler**
   - **是 Development 環境?** -> 回傳 JSON `{ status, error, message, stack }`。
   - **是 Production 環境?**
     - `err.isOperational` 為 true? -> 回傳 `{ status, message }`。
     - `err.isOperational` 為 false? -> Log Error (給開發者看)，回傳 "Something went wrong" (給使用者看)。

---

## Real-world examples｜實戰案例

### 1. Async Wrapper (取代 try-catch)

這是讓 Controller 程式碼保持乾淨的關鍵工具。

```javascript
// utils/catchAsync.js
// 接收一個 async 函數，回傳一個新的函數
// 該新函數執行原函數，並自動 catch 錯誤傳給 next
module.exports = fn => {
  return (req, res, next) => {
    fn(req, res, next).catch(next);
  };
};

// 使用方式 (Controller)
const catchAsync = require('../utils/catchAsync');

exports.getUser = catchAsync(async (req, res, next) => {
  const user = await User.findById(req.params.id);
  
  if (!user) {
    // 使用自定義錯誤，自動跳到 Error Handler
    return next(new AppError('No user found with that ID', 404));
  }

  res.status(200).json({ status: 'success', data: { user } });
});
```

### 2. Production-Ready Global Error Handler

這是一個符合標準的 `app.js` 錯誤處理配置。

```javascript
// controllers/errorController.js

const sendErrorDev = (err, res) => {
  res.status(err.statusCode).json({
    status: err.status,
    error: err,
    message: err.message,
    stack: err.stack
  });
};

const sendErrorProd = (err, res) => {
  // Operational, trusted error: send message to client
  if (err.isOperational) {
    res.status(err.statusCode).json({
      status: err.status,
      message: err.message
    });
  } else {
    // Programming or other unknown error: don't leak details
    // 1) Log error
    console.error('ERROR 💥', err);

    // 2) Send generic message
    res.status(500).json({
      status: 'error',
      message: 'Something went very wrong!'
    });
  }
};

module.exports = (err, req, res, next) => {
  err.statusCode = err.statusCode || 500;
  err.status = err.status || 'error';

  if (process.env.NODE_ENV === 'development') {
    sendErrorDev(err, res);
  } else if (process.env.NODE_ENV === 'production') {
    // 可以在這裡處理特定的 DB 錯誤（如 CastError, DuplicateFields）並轉換為 AppError
    let error = { ...err }; 
    error.message = err.message;
    
    sendErrorProd(error, res);
  }
};
```

### 3. 最後一道防線 (Entry Point)

在 `server.js` (啟動檔) 中處理那些沒有被 Express 捕捉到的錯誤。

```javascript
// server.js

// 處理同步程式碼的 Uncaught Exception (如: console.log(x) where x is not defined)
process.on('uncaughtException', err => {
  console.log('UNCAUGHT EXCEPTION! 💥 Shutting down...');
  console.log(err.name, err.message);
  process.exit(1); // 必須重啟
});

const app = require('./app');
const server = app.listen(port, () => { ... });

// 處理 Async 的 Unhandled Rejection (如: DB 連線失敗)
process.on('unhandledRejection', err => {
  console.log('UNHANDLED REJECTION! 💥 Shutting down...');
  console.log(err.name, err.message);
  // 優雅關閉 Server 後再退出
  server.close(() => {
    process.exit(1);
  });
});
```