# 領域驅動設計與型別建模 / Domain Modeling with Types

這不僅僅是關於如何寫出「正確」的 TypeScript，而是關於如何利用型別系統來**捕捉業務邏輯**。目標是達成 **"Make illegal states unrepresentable"**（讓非法狀態無法被表達）——如果一段程式碼在業務邏輯上是不合理的，它在編譯階段就不應該通過。

---

## Mental model｜心智模型

### 1. 型別即集合 (Types as Sets)
不要將型別視為單純的「資料驗證器」，請將其視為**所有可能值的集合**。
- `string` 是無限多個字串的集合。
- `boolean` 是 `{true, false}` 的集合。
- 領域建模的過程，就是透過 `Union` (聯集) 與 `Intersection` (交集) 來縮小這個集合，直到它精確地吻合你的業務規則。

### 2. 讓編譯器成為領域專家 (Compiler as Domain Expert)
在傳統開發中，業務邏輯通常隱藏在 `if/else` 的執行期檢查中。在 TypeScript 中，我們將這些邏輯上移至型別定義。
- **Bad Model**: 允許 `isLoading: false` 且 `error: null` 且 `data: null` 同時發生（這是一個業務上不存在的狀態）。
- **Good Model**: 定義明確的狀態機，編譯器會強迫你處理每一種可能的業務情境。

### 3. Parse, don't validate
這是一個核心思維轉變。與其在函式內部不斷驗證輸入（Validate），不如在系統邊界將輸入解析（Parse）成一個受信任的型別。一旦資料進入了你的領域核心，它就應該已經是「被證明為正確」的型別結構。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Discriminated Unions (Tagged Unions)｜可辨識聯合
這是 TypeScript 領域建模最強大的工具。透過一個共同的欄位（通常是 `kind`, `type`, 或 `status`）來區分不同的業務狀態。

```typescript
// ✅ Pattern: 明確區分狀態，消除非法組合
type NetworkRequest<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error };

// 使用時，TS 會自動推斷上下文
function render(request: NetworkRequest<User>) {
  switch (request.status) {
    case 'idle':
      return <Placeholder />;
    case 'loading':
      return <Spinner />;
    case 'success':
      // 在這裡，TS 知道 data 必定存在
      return <UserProfile user={request.data} />;
    case 'error':
      return <ErrorMessage error={request.error} />;
  }
}
```

### 2. Branded Types (Opaque Types)｜品牌型別
防止「基本型別迷戀」(Primitive Obsession)。即使 `UserId` 和 `OrderId` 底層都是 `string`，它們也不應該混用。

```typescript
// ✅ Pattern: 使用虛擬屬性創造 "Nominal Typing" 效果
type Brand<K, T> = K & { readonly __brand: T };

type UserId = Brand<string, 'UserId'>;
type OrderId = Brand<string, 'OrderId'>;
type Email = Brand<string, 'Email'>;

// 驗證函式 (Factory / Type Guard)
function parseEmail(input: string): Email {
  if (!input.includes('@')) throw new Error("Invalid email");
  return input as Email;
}

function processOrder(orderId: OrderId, userId: UserId) { /* ... */ }

const uid = 'user_123' as UserId;
const oid = 'order_abc' as OrderId;

// processOrder(uid, oid); // ❌ Error: Argument of type 'UserId' is not assignable to parameter of type 'OrderId'.
processOrder(oid, uid); // ✅ OK
```

### 3. Exhaustiveness Checking｜窮盡性檢查
利用 `never` 型別確保你在 `switch` 或 `if` 語句中處理了所有可能的案例。當你新增一個業務狀態時，這個模式會讓編譯器報錯，提醒你更新邏輯。

```typescript
function assertNever(x: never): never {
  throw new Error("Unexpected object: " + x);
}

function handleStatus(s: NetworkRequest<any>) {
  switch (s.status) {
    case 'idle': /*...*/ break;
    case 'loading': /*...*/ break;
    case 'success': /*...*/ break;
    // 如果忘記寫 case 'error'，下面這行會報錯，因為 s 此時不是 never
    default: assertNever(s);
  }
}
```

### 4. Result Type Pattern｜結果型別模式
取代 `throw` 例外，將錯誤視為領域模型的一部分。這強迫呼叫者必須處理失敗的情況。

```typescript
type Result<T, E = Error> =
  | { success: true; value: T }
  | { success: false; error: E };

function divide(a: number, b: number): Result<number, string> {
  if (b === 0) return { success: false, error: "Cannot divide by zero" };
  return { success: true, value: a / b };
}
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Bag of Optionals" (選用屬性大禮包)
這是最常見的反模式。試圖用一個包含大量 `?` (optional) 屬性的物件來表達多種狀態。

*   **❌ Anti-pattern**:
    ```typescript
    interface State {
      isLoading: boolean;
      data?: User;
      error?: string;
    }
    // 問題：isLoading: false, data: undefined, error: undefined 是什麼狀態？
    // 問題：isLoading: true, data: User, error: string 是什麼狀態？
    ```
*   **後果**: 你必須在 UI 層寫大量的 `if (data && !error)` 防禦性程式碼，且容易遺漏邊界情況。

### 2. Primitive Obsession (基本型別迷戀)
在函式簽章中大量使用 `string` 或 `number`，導致參數順序錯誤時編譯器無法抓出。

*   **❌ Anti-pattern**:
    ```typescript
    function transferMoney(from: string, to: string, amount: number) { ... }
    // 容易寫成 transferMoney(to, from, amount)
    ```

### 3. Boolean Flags Explosion (布林值爆炸)
當你發現一個物件有多個布林值旗標（`isAdmin`, `isEditor`, `canDelete`...），且這些旗標之間有依賴關係時，這通常意味著你需要一個 Union Type 或更明確的權限模型，而不是一堆布林值。

---

## Checklists & workflows｜檢查清單與流程

在設計新的功能模組或資料結構時，請依序執行以下步驟：

### Modeling Workflow
1.  **列舉狀態**：用紙筆列出該功能所有可能的業務狀態（例如：Draft, Published, Archived）。
2.  **識別資料**：每個狀態下，哪些資料是**必須**存在的？哪些資料是該狀態**獨有**的？
3.  **定義 Union**：使用 Discriminated Union 將上述分析轉化為程式碼。
4.  **實作建構子/工廠**：建立 helper functions 來產生這些狀態，確保只有合法的狀態能被建立。

### Code Review Checklist
- [ ] **互斥性檢查**：是否有多個布林值（如 `isLoading`, `isError`）可以同時為真，但在業務邏輯上不應該同時發生？如果是，請改用 Discriminated Union。
- [ ] **ID 區分**：函式是否接受多個相同型別的 ID（如 `userId` 和 `groupId` 都是 string）？如果是，是否使用了 Branded Types 區分？
- [ ] **窮盡性檢查**：在處理狀態變化的 `switch` 語句中，是否使用了 `assertNever` 或類似機制，確保未來新增狀態時會報錯？
- [ ] **非法狀態不可達**：是否能建構出一個不合理的物件（例如「已付款」的訂單卻沒有「付款時間」）？型別定義應阻止這種情況。

---

## Real-world examples｜實戰案例

### 案例：支付處理系統 (Payment Processing)

#### ❌ Before: 鬆散的型別定義
```typescript
interface Payment {
  id: string;
  amount: number;
  status: 'pending' | 'success' | 'failed';
  processedAt?: Date; // 只有 success/failed 才有，但型別允許 pending 時也有
  failureReason?: string; // 只有 failed 才有
  transactionId?: string; // 只有 success 才有
}

// 開發者必須記得：如果是 success，transactionId 一定有值...
const printReceipt = (p: Payment) => {
  if (p.status === 'success') {
    // 這裡 p.transactionId 仍然是 string | undefined，需要手動斷言或檢查
    console.log(p.transactionId!.toUpperCase()); 
  }
}
```

#### ✅ After: 精確的領域建模
```typescript
// 定義 Brand
type PaymentId = Brand<string, 'PaymentId'>;
type TransactionId = Brand<string, 'TransactionId'>;

// 定義各個狀態的形狀
interface PaymentBase {
  id: PaymentId;
  amount: number;
  createdAt: Date;
}

interface PendingPayment extends PaymentBase {
  status: 'pending';
}

interface SuccessPayment extends PaymentBase {
  status: 'success';
  processedAt: Date;
  transactionId: TransactionId; // 必填
}

interface FailedPayment extends PaymentBase {
  status: 'failed';
  processedAt: Date;
  failureReason: string; // 必填
}

// 組合
type Payment = PendingPayment | SuccessPayment | FailedPayment;

// 使用
const printReceipt = (p: Payment) => {
  if (p.status === 'success') {
    // TS 自動推斷 p 為 SuccessPayment
    // p.transactionId 是 TransactionId (string)，且不為 undefined
    console.log(p.transactionId); 
    
    // console.log(p.failureReason); // ❌ Error: Property 'failureReason' does not exist on type 'SuccessPayment'.
  }
}
```

這個重構帶來的價值：
1.  **自動補全 (Autocomplete)**：當你檢查 `status === 'failed'` 後，IDE 只會提示 `failureReason`，不會提示 `transactionId`。
2.  **重構安全性**：如果你決定移除 `failed` 狀態，所有相關的程式碼都會立即報錯。
3.  **文件化**：新進工程師看一眼型別定義，就知道「成功的付款一定有 Transaction ID」。