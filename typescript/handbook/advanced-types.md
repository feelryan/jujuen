# 進階型別操作與型別體操 / Advanced Types & Type Gymnastics

## Mental model｜心智模型

在進入「型別體操（Type Gymnastics）」之前，必須先轉變對 TypeScript 的認知。不要僅將型別視為靜態的標籤（Labels），而應視為**可運算的函式（Computable Functions）**。

### 1. 型別即函式 (Types as Functions)
在 Runtime 世界，我們寫函式處理資料：`f(data) -> new_data`。
在 Type 世界，我們寫泛型處理型別：`TypeF<T> -> NewType`。

- **Input**: 泛型參數（Generics `T`, `K`, `U`）。
- **Logic**: 條件判斷（`extends ? :`）、迭代（Mapped Types）、推斷（`infer`）。
- **Output**: 產生一個全新的型別結構。

### 2. 集合論視角 (Set Theory Perspective)
進階型別操作的核心在於對「集合」的變形與篩選：
- **Union (`|`)**: 聯集。
- **Intersection (`&`)**: 交集。
- **`extends`**: 判斷是否為子集（Subset）。
- **`never`**: 空集合（Empty Set），在 Conditional Types 中常用來「移除」不符合條件的項目。

### 3. 單一真值來源 (Single Source of Truth)
型別體操的終極目標不是炫技，而是為了維護 **SSOT**。當你的資料結構（如 API Response 或 Config Object）改變時，所有依賴的衍生型別（Derived Types）應該自動更新，無需手動修改多處。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 利用 Conditional Types 進行邏輯判斷
這是型別系統中的 `if/else`。最常見的模式是用來篩選 Union Type。

```typescript
// Pattern: Distributive Conditional Types
// 作用：從 Union 中移除 null 和 undefined
type NonNullable<T> = T extends null | undefined ? never : T;

// 實戰：根據權限 flag 切換型別
type Response<T, IsAdmin extends boolean> = IsAdmin extends true 
  ? { data: T; adminMetadata: string } 
  : { data: T };
```

### 2. 使用 `infer` 進行解構與提取 (Unwrapping)
當你需要從一個複雜型別中「挖出」內部的某個型別時，`infer` 是唯一解。

```typescript
// Pattern: Unwrapping Promises or Array types
type UnpackPromise<T> = T extends Promise<infer U> ? U : T;
type UnpackArray<T> = T extends (infer U)[] ? U : T;

// 實戰：自動提取函式回傳值的型別（不用手寫 Return Type）
// 類似內建的 ReturnType<T>
type MyReturnType<T> = T extends (...args: any[]) => infer R ? R : never;
```

### 3. Mapped Types 與 Key Remapping (`as`)
這是型別系統中的 `.map()`。不僅可以遍歷 key，還能利用 `as` 語法重命名 key。

```typescript
// Pattern: 修改屬性修飾符 (Modifiers)
type Mutable<T> = {
  -readonly [P in keyof T]: T[P]; // 移除 readonly
};

// Pattern: Key Remapping (TS 4.1+)
// 實戰：為所有屬性加上 getter 前綴
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K]
};

interface User { name: string; age: number; }
type UserGetters = Getters<User>; 
// 結果: { getName: () => string; getAge: () => number; }
```

### 4. Template Literal Types (字串模板型別)
將字串操作帶入型別系統，常用於處理 CSS class names、Event names 或 API routes。

```typescript
type Color = "red" | "blue";
type Size = "small" | "large";

// 自動產生組合字串
type StyleClass = `${Color}-${Size}`; 
// "red-small" | "red-large" | "blue-small" | "blue-large"
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Write-only Types (唯寫型別)
**現象**：寫出了極度複雜、嵌套十層的型別，只有作者當下看得懂，一個月後連自己都無法維護。
**解法**：
- 將複雜邏輯拆解成多個小的 Utility Types。
- 加上註解說明這個型別的「輸入」與「預期輸出」。
- 如果邏輯太過複雜，考慮是否過度設計（Over-engineering），有時簡單的 Interface 繼承比自動推導更好維護。

### 2. 濫用 `any` 中斷推導鏈
**現象**：在型別體操的中間步驟使用了 `any`，導致後續所有推導都變成 `any`，失去了型別安全。
**解法**：
- 盡量使用 `unknown` 替代 `any`。
- 使用泛型約束（Constraints），例如 `T extends Record<string, unknown>`。

### 3. 忽略遞迴深度限制 (Recursion Limits)
**現象**：使用遞迴型別處理深層物件（如 DeepPartial）或長 Tuple 時，出現 `Type instantiation is excessively deep and possibly infinite` 錯誤。
**解法**：
- TS 對遞迴深度有限制（通常約 50 層）。
- 避免對過於巨大的資料結構進行全量的遞迴型別運算。
- 嘗試改寫為非遞迴版本，或限制遞迴深度。

### 4. 分發特性陷阱 (Distributive Conditional Types Gotcha)
**現象**：當泛型 `T` 是 Union Type 時，`T extends U ? X : Y` 會對 Union 的每個成員單獨運算再合併，這有時不是預期的行為。
**解法**：
- 如果要關閉分發特性，將泛型用 tuple 包起來：`[T] extends [U] ? X : Y`。

---

## Checklists & workflows｜檢查清單與流程

在撰寫複雜工具型別時，請遵循以下決策流程：

### Workflow: Utility Type Construction

1.  **定義目標 (Define Goal)**:
    - 輸入是什麼？（例如：一個物件型別）
    - 輸出是什麼？（例如：所有 key 變成 optional 且 value 變成 string）
2.  **拆解步驟 (Break Down)**:
    - 是否需要遍歷 Key？ -> Use **Mapped Types**.
    - 是否需要條件判斷？ -> Use **Conditional Types**.
    - 是否需要提取內部型別？ -> Use **infer**.
    - 是否需要字串重組？ -> Use **Template Literal Types**.
3.  **實作與驗證 (Implement & Verify)**:
    - 先寫一個簡單的 Test Case。
    - 逐步組合邏輯。
4.  **邊界測試 (Edge Cases)**:
    - 傳入 `any`、`never`、`unknown` 會發生什麼事？
    - 傳入 Union Type 時是否正確分發？

### Checklist

- [ ] **可讀性**：變數名稱（`T`, `K`, `U`）是否符合慣例？複雜邏輯是否有註解？
- [ ] **約束力**：泛型是否有適當的 `extends` 約束？（例如 `T extends string` 防止傳入數字）。
- [ ] **分發性**：是否正確處理了 Union Type 的分發行為（需要分發還是禁止分發）？
- [ ] **效能**：是否在大物件上使用了過深的遞迴？IDE 的型別提示是否變得很慢？
- [ ] **除錯**：是否使用了 `Expand<T>` 之類的工具型別來展開結果，確認計算出的型別符合預期？

---

## Real-world examples｜實戰案例

### 1. 類型安全的 API Response 提取器
後端回傳的資料通常包在標準結構中，我們希望直接拿到 `data` 的型別。

```typescript
interface ApiResponse<TData> {
  code: number;
  message: string;
  data: TData;
  timestamp: number;
}

// 假設我們有一個 API 函式
declare function getUser(): Promise<ApiResponse<{ id: number; name: string }>>;

// Utility: 提取 Promise 內部的 ApiResponse 中的 data 型別
type ExtractApiData<Func> = Func extends (...args: any[]) => Promise<ApiResponse<infer Data>> 
  ? Data 
  : never;

// Usage
type UserData = ExtractApiData<typeof getUser>; 
// Result: { id: number; name: string }
// 即使 API 回傳結構改變，UserData 也會自動更新
```

### 2. 智慧型路徑參數 (Typed Route Params)
在前端路由或 i18n 工具中，根據字串模板自動推斷需要的參數。

```typescript
// 解析路徑字串，提取 :param
type ExtractParams<Path extends string> = 
  Path extends `${infer Start}:${infer Param}/${infer Rest}`
    ? { [K in Param | keyof ExtractParams<`/${Rest}`>]: string }
    : Path extends `${infer Start}:${infer Param}`
      ? { [K in Param]: string }
      : {};

// Usage
type MyPath = "/users/:userId/posts/:postId";
type Params = ExtractParams<MyPath>;
// Result: { userId: string; postId: string }

// 實際應用函數
function navigate<P extends string>(path: P, params: ExtractParams<P>) { 
  // ... implementation
}

// TS 會報錯，因為缺了 postId
// navigate("/users/:userId/posts/:postId", { userId: "123" }); 
```

### 3. 嚴格的物件部分更新 (Strict Update Object)
當我們要更新一個物件時，不僅要是 Partial，還不能包含原本不存在的 key。雖然 `Partial<T>` 可以做到，但它允許 `undefined` 賦值，有時我們希望更精確。

```typescript
// 允許部分更新，但禁止明確寫入 undefined (視業務需求而定)
// 並且利用 Exact Optional Property Types (tsconfig 設定)
type ExactPartial<T> = {
  [K in keyof T]?: T[K];
};

// 進階：DeepPartial (處理巢狀物件更新)
type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

interface Config {
  theme: {
    color: string;
    mode: 'dark' | 'light';
  };
  retries: number;
}

const updateConfig = (config: DeepPartial<Config>) => { /*...*/ };

updateConfig({ 
  theme: { mode: 'dark' } // Valid
});
```

### 4. 除錯工具型別 (Debugging Helper)
在開發複雜型別時，VS Code 有時只會顯示 `TypeA & TypeB`，看不出最終結果。這個工具型別強迫 TS 計算並展開最終結構。

```typescript
// 強制展開型別定義，讓 Hover 提示更清晰
export type Expand<T> = T extends infer O ? { [K in keyof O]: O[K] } : never;

// 處理深層展開
export type ExpandDeep<T> = T extends object 
  ? T extends infer O ? { [K in keyof O]: ExpandDeep<O[K]> } : never 
  : T;
```