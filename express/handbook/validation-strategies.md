# 請求驗證與資料淨化策略 / Request Validation & Data Sanitization

## Mental model｜心智模型

在 Express 應用程式中，將請求驗證視為 **「海關檢查站 (Border Control)」** 或 **「無菌室氣鎖 (Airlock)」**。

1.  **Untrusted Zone (外部世界)**：所有的 `req.body`, `req.query`, `req.params` 本質上都是「髒」的、不可信的。它們可能包含惡意腳本、錯誤的資料型別，或是試圖覆蓋資料庫欄位的多餘屬性。
2.  **Trusted Zone (核心邏輯)**：你的 Controller 和 Service 層應該只處理「已消毒」的資料。在 Controller 內部不應再出現 `if (!req.body.email)` 這種防禦性程式碼。
3.  **The Gatekeeper (驗證中介軟體)**：驗證層必須作為 Middleware 存在於 Router 之前。它的職責是 **"Parse, don't just validate"**（解析而不僅是驗證）。這意味著它不僅檢查資料是否正確，還負責將資料轉換（Coercion）為正確的型別（例如將 Query string `"123"` 轉為 Number `123`），並剔除未定義的欄位（Stripping）。

> **Key Concept**: 如果資料沒有通過 Schema 驗證，請求甚至不應該進入 Controller。這就是 **Fail Fast** 原則。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Schema-Based Validation (基於 Schema 的驗證)
不要手寫 `if-else` 檢查。使用宣告式 Schema 庫（如 **Zod** 或 **Joi**）來定義資料形狀。
- **Zod**: 現代首選，對 TypeScript 支援極佳，支援靜態型別推斷。
- **Joi**: 傳統強大，生態系豐富，適合純 JS 專案。

### 2. The Middleware Factory Pattern (中介軟體工廠模式)
建立一個通用的高階函式，接受 Schema 並回傳 Express Middleware。這樣可以保持 Route 定義的整潔。

```typescript
// 概念示意
router.post('/users', validate(createUserSchema), userController.create);
```

### 3. Whitelisting & Stripping (白名單與剔除)
這是防止 **Mass Assignment (批量賦值攻擊)** 的關鍵。
- 攻擊者可能會在 Payload 中偷渡 `isAdmin: true` 或 `balance: 9999`。
- 驗證庫必須設定為「剔除 Schema 中未定義的欄位」(Strip unknown keys)。Zod 預設行為是 strip，Joi 需要設定 `stripUnknown: true`。

### 4. Input Sanitization & Coercion (輸入淨化與型別強制)
- **Trim Strings**: 自動去除字串前後空白，避免 `" user "` 造成資料庫查詢失敗。
- **Type Coercion**: `req.query` 永遠是字串。在驗證層將其轉為數字或布林值，讓 Controller 拿到正確型別。
- **HTML Escaping**: 雖然通常由前端或 View Engine 處理，但在儲存前對特定欄位進行 XSS 防護也是一種策略（但需小心不要破壞資料原始性）。

### 5. Centralized Error Handling (集中式錯誤處理)
驗證失敗時，不應直接 `res.status(400).json(...)`，而是將錯誤傳遞給全域 Error Handler。這樣可以統一錯誤格式（例如 RFC 7807 Problem Details）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Shotgun Parsing (散彈槍式解析)
- **現象**：驗證邏輯散落在程式碼各處。先在 Controller 檢查 email，進到 Service 檢查 password 長度，進到 Database 前又檢查一次。
- **後果**：難以維護，容易漏掉檢查，且無法一眼看出 API 需要什麼參數。

### 2. Trusting the Frontend (信任前端驗證)
- **現象**：後端工程師說「前端已經有做表單驗證了，後端不用太嚴格」。
- **後果**：這是巨大的安全漏洞。任何人都可以用 Postman 或 `curl` 繞過前端直接打 API。**前端驗證是為了 UX，後端驗證是為了 Security。**

### 3. Leaking Implementation Details (洩漏實作細節)
- **現象**：直接將 Zod/Joi 的原始錯誤物件回傳給客戶端。
- **後果**：可能暴露過多資訊，且對終端使用者不友善。應將錯誤轉換為標準化的 `code` 和 `message` 格式。

### 4. Regex Hell (正規表達式地獄)
- **現象**：自己手寫複雜的 Regex 來驗證 Email 或 URL。
- **後果**：容易寫錯導致 ReDoS (Regex Denial of Service) 攻擊。請使用驗證庫內建的 `.email()` 或 `.url()` 方法。

---

## Checklists & workflows｜檢查清單與流程

在開發新的 API Endpoint 時，請遵循以下檢查流程：

### Development Workflow
1.  **Define DTO/Schema**: 先定義輸入資料的 Zod/Joi Schema（包含 Body, Query, Params）。
2.  **Implement Validation Middleware**: 將 Schema 掛載到 Route 上。
3.  **Type Inference (TS only)**: 在 Controller 中使用 `z.infer<typeof Schema>` 來獲得自動型別提示，確保程式碼與驗證邏輯同步。

### Security & Quality Checklist
- [ ] **涵蓋範圍**：是否同時驗證了 `req.body`、`req.query` 和 `req.params`？
- [ ] **未知欄位**：是否已設定剔除未知欄位（Strip Unknown）以防止污染？
- [ ] **資料淨化**：字串欄位是否已 `trim()`？數字字串是否已轉為 `Number`？
- [ ] **長度限制**：字串欄位是否有 `.max()` 限制？（防止 Buffer Overflow 或資料庫錯誤）。
- [ ] **錯誤訊息**：驗證失敗的錯誤訊息是否清晰，且沒有暴露敏感系統資訊？
- [ ] **業務邏輯分離**：Controller 中是否已經移除了所有基礎的資料格式檢查？

---

## Real-world examples｜實戰案例

### Scenario: 使用 Zod 進行通用驗證 (Modern TypeScript Approach)

這是一個在現代 Express 專案中標準的實作模式。

#### 1. 建立通用的驗證 Middleware (`middleware/validateResource.ts`)

```typescript
import { Request, Response, NextFunction } from 'express';
import { AnyZodObject, ZodError } from 'zod';

// Currying function: 接收 Schema，回傳 Middleware
const validate = (schema: AnyZodObject) => 
  async (req: Request, res: Response, next: NextFunction) => {
    try {
      // parseAsync 會執行驗證並進行資料轉換 (Coercion/Trim)
      // 我們驗證 body, query, params 三個部分
      const parsed = await schema.parseAsync({
        body: req.body,
        query: req.query,
        params: req.params,
      });
      
      // 重要：將淨化後的資料寫回 req，確保 Controller 拿到的是乾淨資料
      req.body = parsed.body;
      req.query = parsed.query;
      req.params = parsed.params;
      
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        // 這裡可以轉交給全域 Error Handler，或直接回傳 400
        return res.status(400).json({
          status: 'fail',
          errors: error.errors.map(e => ({
            path: e.path.join('.'),
            message: e.message
          }))
        });
      }
      next(error);
    }
  };

export default validate;
```

#### 2. 定義 Schema (`schemas/user.schema.ts`)

```typescript
import { z } from 'zod';

export const createUserSchema = z.object({
  body: z.object({
    // 驗證並自動去除前後空白
    fullName: z.string().trim().min(2, "Name too short").max(50),
    
    // 內建 Email 格式檢查
    email: z.string().email("Invalid email format"),
    
    // 密碼複雜度要求
    password: z.string().min(8).regex(/[A-Z]/, "Must contain uppercase"),
    
    // 選擇性欄位
    age: z.number().int().positive().optional(),
  }).strict(), // .strict() 拒絕任何未定義的欄位 (防止污染)
});

// 匯出型別供 Controller 使用
export type CreateUserInput = z.infer<typeof createUserSchema>['body'];
```

#### 3. 在 Route 中整合 (`routes/user.routes.ts`)

```typescript
import { Router } from 'express';
import validate from '../middleware/validateResource';
import { createUserSchema } from '../schemas/user.schema';
import { createUserHandler } from '../controllers/user.controller';

const router = Router();

// 請求流程：Request -> Validate Middleware (失敗則 400) -> Controller
router.post('/users', validate(createUserSchema), createUserHandler);

export default router;
```

#### 4. Controller 的實作 (`controllers/user.controller.ts`)

```typescript
import { Request, Response } from 'express';
import { CreateUserInput } from '../schemas/user.schema';

// 使用泛型 Request<{}, {}, CreateUserInput> 讓 req.body 獲得型別提示
export const createUserHandler = (
  req: Request<{}, {}, CreateUserInput>, 
  res: Response
) => {
  // 這裡不需要再檢查 req.body.email 是否存在
  // TypeScript 也知道 req.body 包含什麼欄位
  const { email, fullName } = req.body;
  
  // 執行業務邏輯...
  res.status(201).json({ message: "User created" });
};
```