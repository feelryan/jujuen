# 現代化 Express：TypeScript 整合 / Modern Express with TypeScript

## Mental model｜心智模型

要在 Express 中順暢地使用 TypeScript，必須理解 **「動態管道 vs 靜態合約」（Dynamic Pipeline vs Static Contract）** 的衝突與調和。

1.  **Request 是一本護照（Passport Analogy）**：
    *   **Express (JS view)**：Request 物件像是一本護照，Middleware 是關卡。經過一個關卡（例如 `authMiddleware`），護照上就被蓋了一個章（例如 `req.user = { id: 1 }`）。JS 允許隨時隨地蓋章。
    *   **TypeScript (TS view)**：TS 是一個嚴格的檢查員，它在程式執行前就要知道護照上有哪些欄位。如果原始的 `Request` 介面沒有 `user` 欄位，TS 就會報錯，即使你心裡知道執行時它一定會有。
    *   **The Bridge**：你需要透過 **Declaration Merging（宣告合併）** 或 **Generics（泛型）** 來告訴 TS：「這本護照在這個專案中，會有這些額外的欄位」。

2.  **型別流動方向（Type Flow Direction）**：
    *   不要手寫 TS Interface 然後去驗證資料。
    *   **正確流向**：Runtime Validator (e.g., Zod/Joi) -> Infer TS Type -> Controller -> Response。
    *   這確保了「執行時的驗證邏輯」與「編譯時的型別檢查」永遠同步。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 全域擴充 Request 型別 (Global Type Augmentation)
對於所有 Request 都可能存在的屬性（如 `req.user`, `req.tenantId`），使用 Declaration Merging 擴充 Express 的全域定義。

*   **Why**: 避免在每個 Handler 都要寫 `(req as AuthenticatedRequest)` 這種轉型。
*   **How**: 建立 `src/types/express.d.ts`。

### 2. Controller 的泛型應用 (Typed Controllers)
對於特定 Endpoint 的輸入（Params, Query, Body），不要擴充全域 Request，而是使用 Express 的 Generic。

*   **Pattern**: `Request<Params, ResBody, ReqBody, ReqQuery>`
*   **Practice**: 結合 `zod` 的 `z.infer` 來自動生成這些型別。

### 3. Zod 作為單一真理來源 (Single Source of Truth)
不要分開維護 Swagger 文件、Joi 驗證與 TS Interface。使用 Zod 定義 Schema，然後導出 TS Type，並透過 middleware 進行 runtime 驗證。

### 4. 錯誤處理的型別安全
確保 Error Handler 中能正確區分 `AppError` (Operational) 與 `Error` (Programmatic)。在 TypeScript 中，`catch(e)` 的 `e` 預設是 `unknown` 或 `any`，務必使用 Type Guard (`instanceof`) 來限縮型別。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 濫用 `any` 或 `as` (The `any` cast)
*   **Bad**: `(req as any).user.id` 或 `const user = req.body as User;`
*   **Why**: 這完全繞過了型別檢查。如果 `req.body` 結構改變，TS 不會報錯，但 Runtime 會炸開。
*   **Fix**: 使用 Zod/Yup 進行 parse，成功後才將資料交給 Controller。

### 2. 過度繼承 Request 介面 (Interface Explosion)
*   **Bad**: 為每個 Controller 建立 `interface LoginRequest extends Request`, `interface ProductRequest extends Request`...
*   **Why**: 造成程式碼冗餘且難以維護。
*   **Fix**: 使用 Express 內建的 Generics `Request<P, Res, Body, Q>`。

### 3. 忽略 `tsconfig.json` 的嚴格模式
*   **Bad**: `strict: false` 或 `noImplicitAny: false`。
*   **Why**: 在寬鬆模式下寫 Express + TS，得到的只是「寫起來比較麻煩的 JavaScript」，卻沒有享受到型別安全的紅利。

### 4. 在 Middleware 中修改 `res.locals` 卻沒有型別定義
*   **Pitfall**: 很多人知道擴充 `req`，卻忘了 `res.locals` 也是傳遞資料的重要管道。
*   **Fix**: 同樣可以透過 Declaration Merging 擴充 `Locals` 介面。

---

## Checklists & workflows｜檢查清單與流程

### Project Setup Checklist
- [ ] 安裝必要的 Type Definitions：`npm i -D @types/express @types/node`。
- [ ] 設定 `tsconfig.json`：確保 `"esModuleInterop": true` 和 `"strict": true`。
- [ ] 建立型別定義資料夾：`src/types/` 或 `src/@types/`。
- [ ] 選擇 Runtime Validation Library：推薦 `zod` (因其 TS 整合性最佳)。

### Development Workflow (New Endpoint)
1.  **Define Schema**: 使用 Zod 定義 `bodySchema`, `querySchema`, `paramsSchema`。
2.  **Infer Types**: 從 Schema 導出 TS 型別 (`type CreateUserBody = z.infer<typeof bodySchema>`)。
3.  **Implement Controller**: 使用 `Request<Params, Res, Body, Query>` 簽名。
4.  **Attach Middleware**: 在 Route 中掛載 `validate(schema)` middleware。

### Migration Checklist (JS to TS)
- [ ] **Step 1**: 將 `.js` 改為 `.ts`，允許 `noImplicitAny: false` (暫時)。
- [ ] **Step 2**: 修正 `require` 為 `import`。
- [ ] **Step 3**: 為 Middleware 的 `req`, `res`, `next` 加上型別註記。
- [ ] **Step 4**: 處理 `req.body` 的型別（引入 Zod）。
- [ ] **Step 5**: 開啟 `strict: true` 並修復所有紅字。

---

## Real-world examples｜實戰案例

### 1. Global Type Augmentation (處理 User Session)

這解決了「Middleware 驗證過後，Controller 卻讀不到 `req.user`」的經典問題。

```typescript
// src/types/express.d.ts
import { UserRole } from '../constants';

// 必須是一個 module 才能進行 augmentation
export {};

declare global {
  namespace Express {
    interface Request {
      // 這裡定義所有 middleware 可能掛載的屬性
      user?: {
        id: string;
        role: UserRole;
        email: string;
      };
      requestId: string;
    }
  }
}
```

### 2. Strongly Typed Controller with Zod

這展示了如何將 Runtime 驗證與 Compile-time 型別完美結合。

```typescript
// src/controllers/user.controller.ts
import { Request, Response, NextFunction } from 'express';
import { z } from 'zod';

// 1. 定義 Schema (Runtime Validation)
const createUserSchema = z.object({
  body: z.object({
    email: z.string().email(),
    password: z.string().min(8),
    age: z.number().optional()
  }),
  query: z.object({
    dryRun: z.string().transform((val) => val === 'true').optional()
  })
});

// 2. 推導型別 (Compile-time Type)
type CreateUserSchema = z.infer<typeof createUserSchema>;
type CreateUserBody = CreateUserSchema['body'];
type CreateUserQuery = CreateUserSchema['query'];

// 3. 實作 Controller
// Request<Params, ResBody, ReqBody, ReqQuery>
export const createUser = async (
  req: Request<{}, any, CreateUserBody, CreateUserQuery>,
  res: Response,
  next: NextFunction
) => {
  // 這裡 req.body.email 會自動提示，且型別為 string
  // req.query.dryRun 型別為 boolean | undefined
  
  const { email, password } = req.body; 
  
  if (req.query.dryRun) {
    return res.json({ message: "Dry run success", email });
  }

  // ... 呼叫 Service 層
  res.status(201).json({ id: "123", email });
};
```

### 3. Generic Validation Middleware

一個通用的 Middleware，確保進入 Controller 的資料一定符合 Schema。

```typescript
// src/middlewares/validate.ts
import { Request, Response, NextFunction } from 'express';
import { AnyZodObject, ZodError } from 'zod';

export const validate = (schema: AnyZodObject) => 
  async (req: Request, res: Response, next: NextFunction) => {
    try {
      // parseAsync 會驗證並轉換資料 (例如 string -> number)
      const parsed = await schema.parseAsync({
        body: req.body,
        query: req.query,
        params: req.params,
      });
      
      // 將淨化後的資料寫回 req，確保 Controller 拿到的是乾淨的資料
      req.body = parsed.body;
      req.query = parsed.query;
      req.params = parsed.params;
      
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        return res.status(400).json({ errors: error.errors });
      }
      next(error);
    }
  };
```