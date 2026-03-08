# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，TypeScript 不僅僅是 JavaScript 的型別檢查工具，更是一種「領域建模（Domain Modeling）」語言。本章的目標是協助你從「寫出會過的型別」進階到「寫出能表達業務邏輯的型別」。

For senior engineers, TypeScript is not just a type-checker for JavaScript; it is a language for "Domain Modeling." The goal of this chapter is to help you advance from "writing types that pass" to "writing types that express business logic."

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **讓非法狀態無法被表示（Make Illegal States Unrepresentable）**：利用 Discriminated Unions 消除「屬性大雜燴（Bag of Optionals）」造成的邏輯漏洞。
    **Make Illegal States Unrepresentable**: Eliminate logic loopholes caused by the "Bag of Optionals" anti-pattern using Discriminated Unions.
2.  **模擬名義型別系統（Simulate Nominal Typing）**：使用 Branded Types (Opaque Types) 防止基本型別（如 `string` 或 `number`）在不同業務含義間混用（例如防止將 `UserId` 誤傳給 `OrderId`）。
    **Simulate Nominal Typing**: Use Branded Types (Opaque Types) to prevent primitive types (like `string` or `number`) from being mixed up across different business contexts (e.g., preventing a `UserId` from being passed as an `OrderId`).
3.  **實作編譯期狀態機（Implement Compile-time State Machines）**：在編譯階段就能攔截無效的狀態轉換，而非等到執行期才拋出錯誤。
    **Implement Compile-time State Machines**: Catch invalid state transitions during the compilation phase, rather than waiting for runtime errors.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 結構化型別 vs. 名義化型別 (Structural vs. Nominal Typing)

TypeScript 預設採用**結構化型別系統（Structural Typing）**，也就是「鴨子型別（Duck Typing）」：如果它走起來像鴨子、叫起來像鴨子，那它就是鴨子。這在整合不同來源的 JSON 資料時非常方便，但在嚴謹的領域建模中可能導致危險。

TypeScript defaults to a **Structural Typing system**, also known as "Duck Typing": if it walks like a duck and quacks like a duck, it is a duck. This is convenient for integrating JSON data from various sources but can be dangerous in strict domain modeling.

相對地，Java 或 C# 採用**名義化型別系統（Nominal Typing）**，即使兩個類別結構完全相同，只要名稱不同，它們就是不同的型別。在 TypeScript 中，我們透過 **Branded Types** 來模擬這種行為，為型別打上「標籤」。

In contrast, Java or C# uses a **Nominal Typing system**, where even if two classes have the exact same structure, they are different types if their names differ. In TypeScript, we simulate this behavior using **Branded Types** to "tag" our types.

### 2.2 代數資料型別 (Algebraic Data Types - ADT)

在領域建模中，我們常使用 **Discriminated Unions（可辨識聯合）** 來實作 ADT 中的 "Sum Type"。心智模型應該是：一個物件在同一時間只能是多種特定形狀中的**一種**，並且由一個共同的欄位（Discriminant）決定它是哪一種。

In domain modeling, we often use **Discriminated Unions** to implement "Sum Types" in ADT. The mental model should be: an object can only be **one** of several specific shapes at a time, and a common field (the Discriminant) determines which one it is.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

### 3.1 支付與訂單系統 (Payment & Order Systems)

在處理金流時，狀態的正確性至關重要。一個「已付款」的訂單必須包含 `paymentId`，而「待付款」的訂單絕對不該有這個欄位。

When handling payments, state correctness is critical. A "Paid" order must contain a `paymentId`, whereas a "Pending" order absolutely should not have this field.

-   **Naive Design**: 使用單一 `Order` 介面，所有欄位都是 Optional (`paymentId?: string`)。這導致程式碼充滿 `if (order.paymentId)` 的檢查，且容易遺漏。
-   **Domain Modeling Design**: 定義 `PendingOrder` 與 `PaidOrder`，透過 `status` 欄位區分。存取 `PaidOrder` 時，TypeScript 知道 `paymentId` 必定存在。

-   **Naive Design**: Using a single `Order` interface where all fields are optional (`paymentId?: string`). This leads to code littered with `if (order.paymentId)` checks and is prone to oversight.
-   **Domain Modeling Design**: Defining `PendingOrder` and `PaidOrder`, distinguished by a `status` field. When accessing `PaidOrder`, TypeScript knows `paymentId` must exist.

### 3.2 安全性與 ID 混淆 (Security & ID Confusion)

在微服務架構或大型單體中，資料庫的主鍵通常都是 UUID 字串或整數。

In microservices architectures or large monoliths, database primary keys are usually UUID strings or integers.

-   **Risk**: 函數 `getUser(id: string)` 可能意外接收到一個 `ProductId` 字串。這類錯誤在 Code Review 時極難發現，可能導致嚴重的資料錯亂或權限繞過（IDOR）。
-   **Solution**: 使用 Branded Types 強制區分 `UserId` 與 `ProductId`。

-   **Risk**: A function `getUser(id: string)` might accidentally receive a `ProductId` string. Such errors are extremely hard to spot during Code Review and can lead to severe data corruption or privilege escalation (IDOR).
-   **Solution**: Use Branded Types to enforce the distinction between `UserId` and `ProductId`.

---

# 4. 逐步示例 (Walkthrough / Example)

### 案例：訂單狀態機建模 (Scenario: Order State Machine Modeling)

#### 4.1 初階做法：屬性大雜燴 (The Naive Approach: Bag of Optionals)

這是最常見的反模式。我們試圖用一個介面涵蓋所有可能。

This is the most common anti-pattern. We try to cover all possibilities with a single interface.

```typescript
// ❌ Bad Practice
interface Order {
  id: string;
  status: 'pending' | 'paid' | 'shipped' | 'failed';
  amount: number;
  paymentId?: string; // Only exists if paid
  trackingNumber?: string; // Only exists if shipped
  errorReason?: string; // Only exists if failed
}

function processOrder(order: Order) {
  if (order.status === 'shipped') {
    // We have to manually check or use non-null assertion (!)
    // TypeScript doesn't know trackingNumber exists for sure.
    console.log(order.trackingNumber!.toUpperCase()); 
  }
}
```

**問題 (Problem)**：
我們可以建立一個 `status: 'pending'` 但卻有 `shippedDate` 的物件。這是一個「非法狀態」，但型別系統允許它發生。

We can create an object with `status: 'pending'` that also has a `shippedDate`. This is an "illegal state," yet the type system permits it.

#### 4.2 進階做法：Discriminated Unions (The Mature Approach)

我們將狀態拆解，並利用 `kind` (或 `status`) 作為辨識欄位。

We decompose the state and use `kind` (or `status`) as the discriminant field.

```typescript
// ✅ Better Practice

// 1. Define Branded Types for IDs
type OrderId = string & { readonly __brand: unique symbol };
type PaymentId = string & { readonly __brand: unique symbol };

// Helper to create branded types (casting is necessary here)
const createOrderId = (id: string) => id as OrderId;

// 2. Define distinct states
interface BaseOrder {
  id: OrderId;
  amount: number;
  createdAt: Date;
}

interface PendingOrder extends BaseOrder {
  status: 'pending';
}

interface PaidOrder extends BaseOrder {
  status: 'paid';
  paymentId: PaymentId; // Mandatory
  paidAt: Date;
}

interface ShippedOrder extends BaseOrder {
  status: 'shipped';
  paymentId: PaymentId;
  trackingNumber: string; // Mandatory
  shippedAt: Date;
}

interface FailedOrder extends BaseOrder {
  status: 'failed';
  errorReason: string; // Mandatory
}

// 3. The Union Type
type Order = PendingOrder | PaidOrder | ShippedOrder | FailedOrder;

// 4. Usage with Type Narrowing
function printOrderInfo(order: Order) {
  switch (order.status) {
    case 'pending':
      console.log(`Waiting for payment: ${order.amount}`);
      // order.paymentId; // Error: Property 'paymentId' does not exist on type 'PendingOrder'.
      break;
    case 'paid':
      console.log(`Paid via ${order.paymentId}`);
      break;
    case 'shipped':
      console.log(`Shipped: ${order.trackingNumber}`);
      break;
    case 'failed':
      console.log(`Failed: ${order.errorReason}`);
      break;
    default:
      // Exhaustiveness checking: ensures all cases are handled
      const _exhaustiveCheck: never = order;
      throw new Error(`Unhandled order status: ${JSON.stringify(_exhaustiveCheck)}`);
  }
}
```

**優勢 (Advantages)**：
1.  **型別安全 (Type Safety)**：在 `case 'pending'` 中存取 `paymentId` 會導致編譯錯誤。
2.  **完整性檢查 (Exhaustiveness Checking)**：如果未來新增了 `RefundedOrder` 但忘記在 `switch` 中處理，`default` 區塊的 `never` 指派會導致編譯失敗。

1.  **Type Safety**: Accessing `paymentId` inside `case 'pending'` results in a compilation error.
2.  **Exhaustiveness Checking**: If a `RefundedOrder` is added in the future but we forget to handle it in the `switch`, the `never` assignment in the `default` block will cause the build to fail.

#### 4.3 狀態轉換函數 (State Transition Functions)

我們可以定義函數來強制執行狀態轉換邏輯。

We can define functions to enforce state transition logic.

```typescript
// Only a PendingOrder can become a PaidOrder
function payOrder(order: PendingOrder, paymentId: PaymentId): PaidOrder {
  return {
    ...order,
    status: 'paid',
    paymentId,
    paidAt: new Date(),
  };
}

// Usage
// const shippedOrder = ...;
// payOrder(shippedOrder, ...); // Error: Argument of type 'ShippedOrder' is not assignable to parameter of type 'PendingOrder'.
```

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 過度依賴 `as` 斷言 (Overusing `as` Assertions)

**錯誤描述**：開發者為了快速通過編譯，在 API 回傳處直接使用 `response as Order`，而沒有進行執行期驗證。

**Description**: Developers directly use `response as Order` at API return points to bypass compilation errors quickly, without performing runtime validation.

**為何不好**：TypeScript 的型別在執行期會消失。如果後端回傳的資料結構改變（例如 `status` 變成了 `STATUS`），程式會在執行期崩潰，且錯誤訊息難以除錯。

**Why it's bad**: TypeScript types are erased at runtime. If the backend data structure changes (e.g., `status` becomes `STATUS`), the program will crash at runtime with cryptic error messages.

**替代方案**：使用 Zod, io-ts 或 TypeBox 等庫在 I/O 邊界進行 Schema Validation，並從 Schema 推導出 TS 型別。

**Alternative**: Use libraries like Zod, io-ts, or TypeBox to perform Schema Validation at I/O boundaries and infer TS types from the schema.

### 5.2 濫用 `any` 或 `unknown` 而不進行 Type Guard (Abusing `any` or `unknown` without Type Guards)

**錯誤描述**：在處理複雜聯合型別時，因為懶得寫 Type Guard 函數，直接轉型成 `any` 來存取屬性。

**Description**: When handling complex union types, casting directly to `any` to access properties out of laziness to write Type Guard functions.

**替代方案**：撰寫 User-Defined Type Guards (`isPaidOrder(o): o is PaidOrder`)。

**Alternative**: Write User-Defined Type Guards (`isPaidOrder(o): o is PaidOrder`).

### 5.3 忽略 `never` 型別的用途 (Ignoring the `never` type)

**錯誤描述**：在 `switch` 或 `if/else` 鏈的結尾沒有處理 `never`，導致新增業務狀態時，舊的程式碼默默地忽略了新狀態。

**Description**: Not handling `never` at the end of a `switch` or `if/else` chain, causing legacy code to silently ignore new states when business logic expands.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 請解釋如何在 TypeScript 中實現「讓非法狀態無法被表示」？
**How would you implement "Make Illegal States Unrepresentable" in TypeScript?**

*   **高分回答要點 (Key Points)**：
    *   解釋 **Discriminated Unions** 的概念。
    *   對比 "Bag of Optionals" (所有欄位都可選) 的缺點。
    *   舉例說明如何透過型別限縮 (Narrowing) 來確保在特定狀態下只能存取特定欄位。

### Q2: 什麼是 Branded Types (或 Opaque Types)？在什麼場景下你會使用它？
**What are Branded Types (or Opaque Types)? In what scenarios would you use them?**

*   **高分回答要點 (Key Points)**：
    *   說明 TypeScript 是結構化型別 (Structural)，Branded Types 用來模擬名義化型別 (Nominal)。
    *   實作方式：`Type & { readonly __brand: unique symbol }`。
    *   場景：防止 `UserId` 與 `OrderId` 混用，或區分 `SanitizedHtmlString` 與 `UnsafeString` 以增強安全性。

### Q3: 當系統需要新增一個狀態（例如 `Refunded`）時，你如何確保所有相關的程式碼都已經處理了這個新狀態？
**When the system needs to add a new state (e.g., `Refunded`), how do you ensure all relevant code handles this new state?**

*   **高分回答要點 (Key Points)**：
    *   提及 **Exhaustiveness Checking**。
    *   展示如何使用 `never` 型別在 `switch` 的 `default` 分支中觸發編譯錯誤。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)

1.  **Discriminated Unions** 是領域建模的核心工具，用來取代充滿 Optional 屬性的單一大介面。
2.  **Discriminant (Tag)** 欄位是型別限縮（Narrowing）的關鍵。
3.  **Branded Types** 為基本型別提供語意保護，防止參數傳遞錯誤。
4.  利用 **Exhaustiveness Checking** (`never` type) 確保未來的重構安全性。
5.  型別是用來描述**業務邏輯**的，而不僅僅是描述資料結構。

### 後續延伸 (Next Steps)

*   **Advanced Generics**: 學習如何撰寫 Generic Utilities 來自動轉換這些 Discriminated Unions（例如提取特定狀態的型別）。
*   **Runtime Validation**: 研究 **Zod** 或 **Valibot**，將這些編譯期的型別定義與執行期的資料驗證結合（Single Source of Truth）。
*   **Functional Programming**: 探索 `fp-ts` 或 `Effect`，進一步使用 `Either` 或 `Option` 型別來處理錯誤與空值，取代 `null` 與 `throw`。