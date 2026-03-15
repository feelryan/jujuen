# 系統邊界與執行期驗證 / System Boundaries & Runtime Validation

在 TypeScript 開發中，最危險的地方往往不是邏輯複雜的演算法內部，而是系統與外部世界接觸的「邊界」。本章節將探討如何處理 API 回傳值、使用者輸入與 JSON 檔案，並介紹如何利用 `unknown` 與 Schema Validation（如 Zod）來構建堅固的防禦工事。

## Mental model｜心智模型

### 1. 靜態型別 vs. 動態資料 (The Static vs. Dynamic Gap)
TypeScript 的型別檢查僅存在於 **編譯時期 (Compile-time)**。一旦程式碼被編譯成 JavaScript 並在瀏覽器或 Node.js 中執行，所有的型別標記都會消失。
- **誤區**：認為定義了 `interface User`，API 回傳的 JSON 就會自動變成那個形狀。
- **現實**：外部輸入（I/O）在執行期是「薛丁格的資料」，在未經檢查前，它可能是任何東西。

### 2. 信任邊界 (The Trust Boundary)
將你的應用程式想像成一座城堡：
- **城堡內部 (Trusted Zone)**：這是你的 TypeScript 程式碼，型別系統在此處提供 100% 的保證。
- **城堡外部 (Untrusted Zone)**：API、LocalStorage、URL 參數、使用者表單。這裡充滿了混亂。
- **城門 (The Gate)**：這是本章的重點。你不能讓外部資料直接「傳送」進城堡，必須在城門口設立「檢疫站」（Runtime Validation）。

### 3. Parse, don't validate (解析而非僅驗證)
這是一個重要的思維轉換（源自 Alexis King 的文章）：
- **Validate**：檢查輸入是否符合規則，如果符合，就繼續使用該輸入（通常還需配合 Type Assertion）。
- **Parse**：檢查輸入是否符合規則，如果符合，**回傳一個全新的、帶有正確型別的資料結構**；如果不符合，拋出錯誤。
- **結論**：在 TypeScript 中，我們應該追求 **Parsing**，將 `unknown` 的輸入轉化為具體的 `Type`。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 預設使用 `unknown` 而非 `any`
當你無法確定外部資料的形狀時，**永遠不要使用 `any`**。
- `any`：告訴編譯器「閉嘴，我知道我在做什麼」（通常你不知道），它會像病毒一樣傳播，關閉沿途所有的型別檢查。
- `unknown`：告訴編譯器「這是一個未知的東西，在我檢查它之前，不准讓我對它做任何操作」。

```typescript
// ❌ Bad: 放棄治療
const data: any = JSON.parse(jsonString);
console.log(data.user.id); // Runtime Error if structure is wrong

// ✅ Good: 強迫檢查
const data: unknown = JSON.parse(jsonString);
// console.log(data.user.id); // Error: Object is of type 'unknown'.

if (isUser(data)) {
  console.log(data.user.id); // Safe now
}
```

### 2. 使用 Schema Validation Libraries (Zod / io-ts)
手寫 Type Guards (`if (typeof data === 'object' && data !== null && 'id' in data...)`) 非常繁瑣且容易出錯。現代 TS 專案的標準做法是使用 Schema 庫，其中 **Zod** 是目前的業界首選。

**Pattern: Single Source of Truth (單一真理來源)**
不要分開定義 `interface` 和驗證邏輯，而是從 Schema 推導型別。

```typescript
import { z } from "zod";

// 1. 定義 Runtime Schema
const UserSchema = z.object({
  id: z.string().uuid(),
  username: z.string().min(3),
  email: z.string().email(),
  role: z.enum(["admin", "user", "guest"]),
  preferences: z.object({
    theme: z.string().optional(),
  }).optional(),
});

// 2. 自動推導 TypeScript 型別 (Compile-time)
// 不需要手寫 interface User { ... }
type User = z.infer<typeof UserSchema>;

// 3. 在邊界處使用 (Runtime)
function handleApiResponse(payload: unknown): User {
  // parse 會在失敗時 throw error，safeParse 則回傳 result object
  return UserSchema.parse(payload); 
}
```

### 3. 處理 "Excess Properties" (多餘屬性)
API 可能會回傳比你預期更多的欄位。
- **Strip (預設)**：Zod 預設會移除 Schema 中未定義的欄位。這通常是好的，避免污染內部狀態。
- **Passthrough**：保留未定義欄位。
- **Strict**：如果有未定義欄位則報錯。

### 4. 轉換層 (Transformation Layer)
有時 API 的格式（如 `snake_case` 或字串形式的日期）不適合前端使用。利用 Schema 進行轉換。

```typescript
const ApiUserSchema = z.object({
  created_at: z.string(), // API 給的是字串
}).transform((data) => ({
  createdAt: new Date(data.created_at), // 轉成 Date 物件並改為 camelCase
}));
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Blind Cast" (盲目斷言)
這是最常見也最致命的反模式。
```typescript
// ❌ DANGEROUS
// 你在對編譯器說謊。如果 API 改了，你的程式會在執行期崩潰，
// 但 TS 編譯器卻顯示一切正常。
const user = await response.json() as User; 
```

### 2. 信任部分資料
```typescript
// ❌ Bad
function processData(input: any) {
  if (input.type === 'success') {
    // 假設 payload 結構正確，但其實沒驗證 payload
    handleSuccess(input.payload); 
  }
}
```

### 3. 在 UI 元件內部驗證
不要在 React Component 或業務邏輯深處做 `z.parse()`。驗證應該發生在 **Data Fetching Layer** (e.g., API client, React Query 的 `select` 函數, 或 Redux middleware)。一旦資料進入應用程式狀態 (State)，它應該已經是「乾淨」且「有型別」的。

### 4. 忽略錯誤處理
Schema Validation 失敗時會拋出錯誤。如果沒有適當的 `try-catch` 或 Error Boundary，使用者會看到白屏。
- **建議**：將驗證錯誤轉換為使用者友善的訊息（例如：「伺服器回傳格式錯誤，請聯繫客服」）。

---

## Checklists & workflows｜檢查清單與流程

在整合外部 API 或處理使用者輸入時，請使用此清單：

### Decision Tree: Handling External Data
1. **資料來源是哪裡？**
   - 內部模組引用 -> 使用 TypeScript 靜態型別。
   - 外部 (API/DB/File/Form) -> 進入步驟 2。
2. **我有這個資料的 Schema 嗎？**
   - 沒有 -> 定義 Zod Schema。
   - 有 -> 確保 Schema 與型別定義同步 (使用 `z.infer`)。
3. **資料進入點在哪裡？**
   - API Client -> 在 `fetch` 後立即 Parse。
   - Form -> 在 `onSubmit` 時 Parse。
4. **如何處理驗證失敗？**
   - Log 錯誤細節 (這通常代表後端 API 變更或 Bug)。
   - 顯示通用錯誤訊息給使用者。
   - **絕對不要** 使用 `as` 強制轉型來繞過錯誤。

### Code Review Checklist
- [ ] 所有的 `fetch` 或 API 呼叫結果是否都經過 Schema 驗證？
- [ ] 程式碼中是否出現了 `as User` 或 `<User>response` 的斷言？(應該被標記為需要修改)
- [ ] 是否使用了 `unknown` 來標註尚未驗證的輸入？
- [ ] Zod Schema 是否包含了必要的 `.optional()` 或 `.nullable()` 處理？

---

## Real-world examples｜實戰案例

### 案例 1：安全的 API Client (Secure API Client)

這是一個封裝良好的 API 請求模式，確保回傳值絕對符合預期。

```typescript
import { z } from "zod";

// 定義預期的回應結構
const UserProfileSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
  isActive: z.boolean().default(true), // 處理後端可能漏給的情況
});

type UserProfile = z.infer<typeof UserProfileSchema>;

class ApiClient {
  async getUser(userId: string): Promise<UserProfile> {
    const response = await fetch(`/api/users/${userId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const rawData: unknown = await response.json();

    // 關鍵步驟：驗證與解析
    // 如果後端亂改欄位，這裡會噴錯，保護下游程式碼
    const result = UserProfileSchema.safeParse(rawData);

    if (!result.success) {
      console.error("API Contract Breach:", result.error.format());
      throw new Error("Received invalid user data from server");
    }

    // result.data 的型別是 UserProfile，不是 any
    return result.data;
  }
}
```

### 案例 2：環境變數配置 (Environment Configuration)

環境變數是另一個常見的邊界。你以為 `process.env.DB_HOST` 一定有值，但往往在部署時才發現漏了。

```typescript
import { z } from "zod";

const EnvSchema = z.object({
  NODE_ENV: z.enum(["development", "production", "test"]),
  API_URL: z.string().url(),
  PORT: z.string().transform(Number).default("3000"), // 字串轉數字
  SECRET_KEY: z.string().min(16),
});

// 建立一個 Config 單例
function loadConfig() {
  const result = EnvSchema.safeParse(process.env);

  if (!result.success) {
    console.error("❌ Invalid environment variables:", result.error.format());
    process.exit(1); // 啟動失敗，直接退出，不要讓程式在錯誤設定下執行
  }

  return result.data;
}

export const config = loadConfig();
// 使用時： config.PORT (number), config.API_URL (string)
```