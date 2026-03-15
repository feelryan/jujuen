# 核心概念與型別系統心智模型 / Core Concepts & Type System Mental Models

## Mental model｜心智模型

要精通 TypeScript，必須先拋棄來自 Java 或 C# 的「名義型別（Nominal Typing）」思維，轉而擁抱「結構化型別（Structural Typing）」與「集合論（Set Theory）」。

### 1. Types are Sets of Values (型別即集合)
將型別視為「一組可能值的集合」。
- **`never`**：空集合 (Empty set)。沒有任何值屬於此集合。
- **`unknown`**：全集合 (Universal set)。包含所有可能的值。
- **`string | number`**：聯集 (Union)。值可以是字串集合或數字集合中的元素。
- **`A & B`**：交集 (Intersection)。值必須同時滿足 A 的特徵與 B 的特徵。

> **Mental Shift**: 不要想「這個變數是這個類別的實例嗎？」，要想「這個值屬於這個集合嗎？」

### 2. Structural Typing (Duck Typing)
TypeScript 只在乎「長相（Shape）」。如果一個物件具備了介面要求的所有屬性，它就「是」該型別，無論它原本叫什麼名字。
- **相容性規則**：如果集合 A 的屬性包含集合 B 的所有必要屬性，則 A 可以賦值給 B（A 是 B 的子集合/子型別）。

### 3. Type Erasure (型別抹除)
TypeScript 的型別系統完全是「靜態」的。編譯成 JavaScript 後，所有的 Interface、Type Alias、Generic 都會消失。
- **Runtime Reality**: 你不能在執行期檢查 `if (variable instanceof MyInterface)`，因為 `MyInterface` 在執行期根本不存在。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Discriminated Unions (辨識聯集)
這是 TypeScript 中最強大的模式，結合了「集合論」與「執行期檢查」。透過一個共同的字面量屬性（Literal Type）作為標籤（Tag），讓 TS 在縮小範圍（Narrowing）時能精確判斷。

```typescript
// Pattern: Discriminated Union
type UploadState =
  | { status: 'idle' }
  | { status: 'uploading'; progress: number }
  | { status: 'success'; url: string }
  | { status: 'error'; error: Error };

function render(state: UploadState) {
  // TS knows exactly which properties exist in each block
  switch (state.status) {
    case 'uploading':
      return `Loading: ${state.progress}%`; // Safe to access .progress
    case 'success':
      return `Image: ${state.url}`;         // Safe to access .url
    default:
      return '...';
  }
}
```

### 2. Branded Types (名義型別模擬)
當結構化型別過於寬鬆（例如 `UserId` 和 `OrderId` 都是 `string`，容易誤傳）時，可以使用 "Branding" 技巧模擬名義型別。

```typescript
// Pattern: Branded Types
type Brand<K, T> = K & { __brand: T };

type USD = Brand<number, 'USD'>;
type EUR = Brand<number, 'EUR'>;

const usd = 10 as USD;
const eur = 10 as EUR;

// function pay(amount: USD) { ... }
// pay(eur); // Error: Type 'EUR' is not assignable to type 'USD'.
```

### 3. The "Parse, Don't Validate" Pattern
承認 Type Erasure 的事實。在資料進入系統邊界（I/O, API Response）時，使用 Schema Validation Library (如 Zod) 將 `unknown` 轉換為確定的型別，而不是盲目使用 `as` 斷言。

```typescript
import { z } from 'zod';

const UserSchema = z.object({
  id: z.string(),
  email: z.string().email(),
});

// Infer TS type from the runtime validator
type User = z.infer<typeof UserSchema>;

function handleResponse(data: unknown) {
  // Runtime check that guarantees compile-time type
  const user = UserSchema.parse(data); 
  // 'user' is now strictly typed as User
}
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Lying" Assertion (`as`)
過度依賴 `as` 關鍵字。`as` 是告訴編譯器：「閉嘴，我比你更懂」。但通常你是錯的，且這會隱藏執行期錯誤。

- **Bad**: `const user = {} as User;` (你欺騙了編譯器，後續存取屬性可能導致 runtime crash)。
- **Fix**: 定義 Optional 屬性或使用 Builder Pattern。

### 2. Misunderstanding Excess Property Checks
開發者常困惑為什麼「直接傳物件字面量」會報錯，但「傳變數」卻不會。這是 TS 為了防止拼寫錯誤的特殊機制，而非核心型別規則的改變。

```typescript
interface Point { x: number; y: number; }

function draw(p: Point) {}

// Error: Object literal may only specify known properties.
draw({ x: 10, y: 20, z: 30 }); 

const p3d = { x: 10, y: 20, z: 30 };
// OK: Structural typing allows extra properties via variable reference
draw(p3d); 
```

### 3. Enum Misuse
TypeScript 的 `enum` 是少數會產生 runtime code 的功能，且行為有時不符合預期（特別是數值 Enum）。
- **Pitfall**: 數值 Enum 不具備型別安全性（可以賦值任意數字）。
- **Better**: 使用 `Union of Literal Types` (`type Status = 'open' | 'closed'`) 或 `const assertion` 物件。

---

## Checklists & workflows｜檢查清單與流程

在定義型別或處理複雜邏輯時，請使用此清單校準你的心智模型：

### Type Definition Workflow (定義型別時)
- [ ] **Set Check**: 我的型別是否涵蓋了所有可能的狀態？（例如：是否遺漏了 `loading` 或 `error` 狀態？）
- [ ] **Structure Check**: 我是否依賴了 private 屬性或類別名稱？（如果是，請改用 Interface 或 Discriminated Union）。
- [ ] **Branding Check**: 如果我有兩個結構相同但邏輯不同的 Primitive type（如 `Email` vs `String`），是否需要加上 Brand？

### Runtime Boundary Workflow (處理外部資料時)
- [ ] **Erasure Check**: 我是否試圖在執行期使用 `interface` 進行 `instanceof` 檢查？
- [ ] **Validation Check**: 來自 API 的資料是否先經過 Zod/Yup 驗證，還是直接 `as` 轉型？
- [ ] **Narrowing Check**: 在處理 Union Type 時，我是否使用了唯一的 Literal 屬性（Discriminator）來縮小範圍？

---

## Real-world examples｜實戰案例

### Scenario: Payment Gateway Integration
假設你需要整合 Stripe 和 PayPal，它們的資料結構完全不同，但你需要統一處理。

#### ❌ The "Class/Inheritance" Approach (Nominal Thinking)
試圖建立一個 Base Class 並強迫兩者繼承，導致結構僵化且難以處理 API 回傳的純 JSON。

#### ✅ The "Discriminated Union" Approach (Structural/Set Thinking)

```typescript
// 1. Define distinct shapes (Sets)
interface StripePayment {
  method: 'stripe'; // Discriminator
  stripeToken: string;
  currency: string;
}

interface PayPalPayment {
  method: 'paypal'; // Discriminator
  email: string;
  orderId: string;
}

// 2. Define the Union (The set of all valid payments)
type PaymentMethod = StripePayment | PayPalPayment;

// 3. Process with Type Narrowing
function processPayment(payment: PaymentMethod) {
  // At this line, payment is (Stripe U PayPal)
  
  if (payment.method === 'stripe') {
    // TS narrows type to StripePayment automatically
    console.log(`Charging card: ${payment.stripeToken}`);
  } else {
    // TS knows this MUST be PayPalPayment (Set subtraction)
    console.log(`Redirecting to PayPal for: ${payment.email}`);
  }
}

// 4. Testing is easy (Duck Typing)
// No need to instantiate a "Stripe" class, just match the shape.
processPayment({ 
  method: 'stripe', 
  stripeToken: 'tok_123', 
  currency: 'USD' 
});
```

### Key Takeaway
在這個案例中：
1. 我們不在乎物件是「誰產生的」（Class）。
2. 我們只在乎物件「長什麼樣」（Structure）。
3. 我們利用 `method` 欄位作為執行期的標記，連結了編譯期的型別與執行期的邏輯（Bridging Type Erasure）。