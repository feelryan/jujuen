# 泛型設計模式與約束技巧 / Generics Design Patterns & Constraints

## Mental model｜心智模型

要掌握泛型（Generics），請放棄將它視為「高深莫測的語法」，轉而將其視為 **「型別系統中的函式參數」**。

1.  **型別的變數 (Variables for Types)**：
    一般函式接收「值」作為參數，回傳一個「值」；泛型則是接收「型別」作為參數，回傳一個新的「型別」或約束後的結構。
    *   `function(value)` $\rightarrow$ 處理邏輯 $\rightarrow$ `returnValue`
    *   `type<T>` $\rightarrow$ 結構定義 $\rightarrow$ `SpecificType`

2.  **延遲綁定 (Lazy Binding)**：
    泛型允許你定義一個「模具（Mold）」，但暫時不決定注入什麼材質。直到你真正呼叫該函式或實例化類別的那一刻（Call site），型別才被鎖定。這讓你的程式碼在撰寫時保持彈性（Flexible），在執行前保持安全（Safe）。

3.  **合約與邊界 (Contracts & Boundaries)**：
    單純的 `<T>` 是危險的，因為它代表「任何東西」。
    *   **Constraints (`extends`)** 是你對這個模具的「規格要求」（例如：這個模具只能裝「有 `.length` 屬性的東西」）。
    *   **Inference (推斷)** 是 TypeScript 的自動化機制，它嘗試根據你傳入的「值」來猜測 `T` 是什麼，讓你不用每次都手寫 `<string>`。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 約束優先 (Constrain your Generics)
不要只寫 `<T>`，除非你真的接受任何型別。使用 `extends` 來縮小範圍，這樣你在函式內部才能安全地存取屬性。

```typescript
// ❌ Too loose: TS doesn't know if T has an .id
function getIds<T>(items: T[]) {
  return items.map(item => item.id); // Error: Property 'id' does not exist on type 'T'.
}

// ✅ Constrained: We guarantee T has an id
interface HasId {
  id: string | number;
}

function getIds<T extends HasId>(items: T[]): (string | number)[] {
  return items.map(item => item.id);
}
```

### 2. 利用推斷減少冗餘 (Leverage Inference)
設計泛型 API 時，目標是讓使用者 **「感覺不到泛型的存在」**。

```typescript
// ❌ Bad DX: User must specify T manually
function wrap<T>(value: T): { data: T } {
  return { data: value };
}
wrap<string>("hello"); // Verbose

// ✅ Good DX: TS infers T from the argument
wrap("hello"); // TS knows T is "hello" (literal) or string
```

### 3. 泛型預設值 (Generic Defaults)
為泛型提供預設值，可以讓進階使用者有覆寫的空間，同時不增加一般使用者的負擔。常用於 React Props 或 API Response wrapper。

```typescript
// TData defaults to 'any' or 'unknown' if not provided,
// but allows strict typing when needed.
interface ApiResponse<TData = unknown, TError = Error> {
  data: TData;
  error: TError | null;
  status: number;
}

// Usage 1: Simple
const simpleRes: ApiResponse = { data: "ok", error: null, status: 200 };

// Usage 2: Strict
interface User { name: string }
const userRes: ApiResponse<User> = { data: { name: "Alice" }, error: null, status: 200 };
```

### 4. 關聯多個泛型 (Correlating Multiple Generics)
當你需要確保兩個參數之間有某種關係（例如：第二個參數是第一個參數的 key）時，這是最強大的模式。

```typescript
// K is constrained to be a key of T
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

const user = { name: "Alice", age: 30 };
const age = getProperty(user, "age"); // Type is number
const fail = getProperty(user, "email"); // Error: Argument of type '"email"' is not assignable...
```

### 5. 建構者模式與流式 API (Builder Pattern & Fluent APIs)
利用泛型來追蹤狀態變化，這在建立複雜物件或 SQL Query Builder 時非常有用。

```typescript
class RequestBuilder<TBody = never> {
  private body?: TBody;

  setBody<B>(body: B): RequestBuilder<B> {
    const next = new RequestBuilder<B>();
    next.body = body;
    return next;
  }

  // Only allow send if body is set (not never)
  send(this: RequestBuilder<Exclude<TBody, never>>) {
    console.log("Sending:", this.body);
  }
}

new RequestBuilder()
  .setBody({ id: 1 }) // Returns RequestBuilder<{id: number}>
  .send(); // OK

new RequestBuilder().send(); // Error: Property 'body' is missing... (conceptually)
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 為了泛型而泛型 (Unnecessary Generics)
如果你的泛型 `T` 沒有用來關聯「參數與回傳值」或「參數與參數」，那你可能不需要泛型。

```typescript
// ❌ Anti-pattern: T is not related to input, cannot be inferred
function log<T>(): void {
  console.log("something");
}
// User must call log<string>() - pointless.

// ❌ Anti-pattern: Just use specific types
function print<T extends string>(val: T) {
  console.log(val);
}
// Better: function print(val: string) { ... }
```

### 2. 泛型污染 (The "Any" Generic)
使用 `extends any` 或是沒有適當約束，導致內部邏輯必須使用大量 Type Assertion (`as`)。

*   **後果**：失去了 TypeScript 的保護，程式碼內部充滿了 `any`，只有外部看起來是強型別。
*   **修正**：盡可能精確定義 `extends` 介面。

### 3. 過度巢狀的泛型 (Generic Hell)
當你看到 `<T, U, V, W extends keyof V>` 這種程式碼時，通常意味著抽象化過度。
*   **徵兆**：同事看不懂你的函式簽章 (Signature)。
*   **修正**：將多個參數合併為一個設定物件型別，或簡化設計。

### 4. 忽略 `unknown` 的安全性
在泛型中，預設值使用 `any` (`T = any`) 是懶惰的做法。
*   **建議**：使用 `T = unknown`，強迫使用者在使用前進行型別檢查 (Type Narrowing)。

---

## Checklists & workflows｜檢查清單與流程

在引入泛型之前，請通過以下決策樹：

### Decision Tree: Do I need a Generic?
1.  **這個函式/類別是否需要處理多種資料型別？**
    *   No $\rightarrow$ 使用具體型別 (Specific Types)。
    *   Yes $\rightarrow$ 繼續。
2.  **輸入的型別與輸出的型別是否有關聯？** (例如：輸入 A 輸出 A，或輸入 A 輸出 Wrap<A>)
    *   No $\rightarrow$ 考慮使用 `any` 或 `unknown`，或者 Union Types。
    *   Yes $\rightarrow$ 使用泛型。
3.  **TS 能否自動推斷出這個泛型？**
    *   No $\rightarrow$ 重新設計參數順序，或考慮是否設計過度。
    *   Yes $\rightarrow$ Good to go.

### Implementation Checklist
- [ ] **命名規範**：單字母 `T`, `U`, `K` 用於簡單場景；具體名稱 `TData`, `TResponse`, `TProps` 用於複雜場景。
- [ ] **約束檢查**：是否使用了 `extends` 來限制 `T` 的範圍？避免 `T` 變成 `any`。
- [ ] **預設值**：是否需要提供 `T = ...` 來改善 DX？
- [ ] **推斷測試**：呼叫函式時，是否可以省略 `<Type>`？如果不行，API 設計可能不夠友善。
- [ ] **巢狀深度**：泛型層級是否超過 2 層？如果是，考慮提取出中間層的 `type` 定義。

---

## Real-world examples｜實戰案例

### 1. 型別安全的 API 客戶端 (Type-Safe API Client)
這是最常見的泛型應用場景。我們建立一個 wrapper，讓呼叫者決定回傳的資料結構。

```typescript
interface ApiConfig {
  url: string;
  method: 'GET' | 'POST';
}

// TResponse allows the caller to define the shape of the data
async function request<TResponse>(config: ApiConfig): Promise<TResponse> {
  const response = await fetch(config.url, { method: config.method });
  if (!response.ok) throw new Error('Network error');
  // In real world, you might want runtime validation here (e.g., Zod)
  return response.json() as Promise<TResponse>;
}

// Usage
interface UserProfile {
  id: string;
  name: string;
}

// Clean usage: type is injected here
const user = await request<UserProfile>({
  url: '/api/user/1',
  method: 'GET'
});

console.log(user.name); // TS knows this is a string
```

### 2. 強型別表單處理 (Strictly Typed Form Handler)
確保表單的 `initialValues` 和 `onSubmit` 處理的資料結構一致。

```typescript
interface FormProps<TValues> {
  initialValues: TValues;
  onSubmit: (values: TValues) => void;
  // Render prop pattern
  children: (values: TValues, handleChange: (key: keyof TValues, val: any) => void) => React.ReactNode;
}

// Generic Component Function
function Form<TValues extends object>(props: FormProps<TValues>) {
  // ... implementation logic
  return null; // placeholder
}

// Usage
// TS infers TValues as { username: string; age: number }
<Form
  initialValues={{ username: "admin", age: 18 }}
  onSubmit={(values) => {
    // values is strictly typed
    console.log(values.username.toUpperCase());
  }}
>
  {(values, handleChange) => (
    <div>
       {/* Type-safe field access */}
      <input
        value={values.username}
        onChange={e => handleChange("username", e.target.value)}
      />
    </div>
  )}
</Form>
```

### 3. Utility: 提取物件部分屬性 (Pick with Autocomplete)
TypeScript 內建的 `Pick` 很好用，但我們可以封裝一個 helper function 來處理陣列過濾。

```typescript
// Constraint: T must be an object
// Constraint: K must be keys of T
function pick<T extends object, K extends keyof T>(obj: T, keys: K[]): Pick<T, K> {
  const result = {} as Pick<T, K>;
  keys.forEach(key => {
    result[key] = obj[key];
  });
  return result;
}

const laptop = { model: "MacBook", year: 2022, os: "macOS", stock: 10 };

// TS provides autocomplete for "model" and "stock"
// Return type is strictly { model: string; stock: number }
const inventoryInfo = pick(laptop, ["model", "stock"]);
```