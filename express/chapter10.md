# Chapter 10: Modernization: TypeScript Integration & Microservices
# 第 10 章：現代化演進：TypeScript 與微服務轉型

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

For Senior Engineers, "modernizing" an Express application rarely means rewriting it from scratch. It usually involves two parallel tracks: hardening the codebase with static analysis (TypeScript) and decoupling architecture for scalability (Microservices/Serverless). This chapter focuses on the strategic execution of these transitions.
對於資深工程師而言，「現代化」一個 Express 應用程式很少意味著從頭重寫。通常這涉及兩條並行的軌道：透過靜態分析（TypeScript）強化程式碼庫，以及為了擴充性進行架構解耦（微服務/Serverless）。本章專注於這些轉型的策略執行。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Execute Incremental TS Migration**: Apply strategies to migrate a legacy JavaScript Express codebase to TypeScript without halting feature development.
    **執行漸進式 TS 遷移**：應用策略將舊有的 JavaScript Express 程式碼庫遷移至 TypeScript，且不停止功能開發。
2.  **Design Type-Safe Contracts**: Utilize Generics and DTOs (Data Transfer Objects) to enforce strict contracts between Middleware, Controllers, and Services.
    **設計型別安全的合約**：利用泛型（Generics）與 DTOs（資料傳輸物件）在 Middleware、Controller 與 Service 之間強制執行嚴格合約。
3.  **Decompose Monoliths**: Identify "Seams" in a monolithic Express app and extract them into independent microservices or serverless functions using the Strangler Fig pattern.
    **拆解單體架構**：識別單體 Express 應用中的「接縫（Seams）」，並利用絞殺榕模式（Strangler Fig pattern）將其提取為獨立的微服務或 Serverless 函式。
4.  **Adapt for Serverless**: Refactor Express controllers to be runtime-agnostic, allowing deployment on both containers (Docker) and FaaS (AWS Lambda/GCP Cloud Functions).
    **適配 Serverless**：重構 Express controller 使其與執行環境無關，允許同時部署於容器（Docker）與 FaaS（AWS Lambda/GCP Cloud Functions）。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 TypeScript as a Structural Contract
### 2.1 TypeScript 作為結構化合約

In Express, TypeScript is not just about adding types to variables; it's about defining the **shape of data** flowing through the request pipeline.
在 Express 中，TypeScript 不僅僅是為變數加上型別；它是關於定義流經請求管道（request pipeline）的**資料形狀**。

*   **Mental Model**: Think of `req` and `res` not as dynamic buckets, but as strictly typed envelopes. Middleware acts as a "stamp" that guarantees specific properties exist on the envelope for the next handler.
    **心智模型**：不要將 `req` 和 `res` 視為動態的水桶，而應視為嚴格型別的信封。Middleware 就像是一個「戳章」，保證信封上存在特定的屬性，供下一個處理器使用。

*   **Interface vs. Type**:
    *   Use **Interfaces** for defining Request/Response extensions (e.g., `AuthenticatedRequest`) because interfaces support **declaration merging**. This allows different declaration files to augment the `Express.Request` object seamlessly.
    *   Use **Types** (or Zod schemas) for DTOs and validation logic, as they offer better composition features (Unions, Intersections).
    **Interface vs. Type**：
    *   使用 **Interfaces** 定義 Request/Response 的擴充（例如 `AuthenticatedRequest`），因為 interface 支援**宣告合併（declaration merging）**。這允許不同的宣告檔案無縫地擴充 `Express.Request` 物件。
    *   使用 **Types**（或 Zod schema）來定義 DTO 和驗證邏輯，因為它們提供更好的組合特性（聯集、交集）。

### 2.2 The Strangler Fig Pattern (Architecture)
### 2.2 絞殺榕模式（架構）

When moving from Monolith to Microservices, the "Big Bang" rewrite is a recipe for disaster. The Strangler Fig pattern is the standard mental model for risk reduction.
當從單體架構轉向微服務時，「大爆炸式（Big Bang）」重寫通常是災難的配方。絞殺榕模式是降低風險的標準心智模型。

*   **Concept**: You place an API Gateway (or a reverse proxy like Nginx) in front of your legacy Express Monolith. New features are built as separate services. Gradually, old routes in the proxy are pointed to new services, slowly "strangling" the old monolith until it can be decommissioned.
    **概念**：你在舊有的 Express 單體應用前放置一個 API Gateway（或像 Nginx 的反向代理）。新功能被建構為獨立的服務。逐漸地，代理中的舊路由被指向新服務，慢慢地「絞殺」舊單體，直到它可以被退役。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### 3.1 The "Modular Monolith" as a Stepping Stone
### 3.1 「模組化單體」作為墊腳石

Before physically splitting code into separate repos or containers, Senior Engineers often refactor a messy Express app into a **Modular Monolith**.
在物理上將程式碼拆分為獨立的 repo 或容器之前，資深工程師通常會先將混亂的 Express 應用重構為**模組化單體（Modular Monolith）**。

*   **Structure**: Instead of organizing by technical layers (`/controllers`, `/models`, `/routes`), organize by **Domain** (`/orders`, `/users`, `/inventory`).
*   **Benefit**: This creates clear boundaries. If `Orders` module imports directly from `Users` database models, you have tight coupling. Refactoring to communicate via internal interfaces prepares you for the eventual network call when they become microservices.
*   **結構**：不要按技術分層（`/controllers`, `/models`, `/routes`）組織，而是按**領域（Domain）**（`/orders`, `/users`, `/inventory`）組織。
*   **效益**：這建立了清晰的邊界。如果 `Orders` 模組直接匯入 `Users` 的資料庫模型，就代表有緊密耦合。重構為透過內部介面溝通，能為將來變成微服務時的網路呼叫做好準備。

### 3.2 Observability in Distributed Systems
### 3.2 分散式系統中的可觀測性

When you split an Express Monolith into Microservices:
當你將 Express 單體拆分為微服務時：

*   **Logging**: `console.log` is no longer sufficient. You need structured logging (JSON) with a `correlation_id` (or `trace_id`) that propagates across HTTP calls between services.
*   **Tracing**: Implementing OpenTelemetry becomes mandatory to visualize the latency waterfall across services.
*   **日誌**：`console.log` 不再足夠。你需要結構化日誌（JSON），並帶有 `correlation_id`（或 `trace_id`），以便在服務間的 HTTP 呼叫中傳遞。
*   **追蹤**：實作 OpenTelemetry 變得強制性，以便視覺化跨服務的延遲瀑布圖。

---

## 4. Walkthrough / Example
## 4. 逐步示例

### Scenario: Strongly Typed Request & Controller Decoupling
### 場景：強型別請求與 Controller 解耦

We will look at two advanced patterns:
1.  Using TypeScript Generics to strictly type `req.body` and `req.query`.
2.  Decoupling the controller logic to make it "Serverless-ready".
我們將探討兩個進階模式：
1.  使用 TypeScript 泛型來嚴格定義 `req.body` 和 `req.query` 的型別。
2.  解耦 controller 邏輯，使其具備「Serverless 就緒」的特性。

#### Step 1: Defining the Contract (Zod + TypeScript)
#### 步驟 1：定義合約（Zod + TypeScript）

We use `zod` for runtime validation and type inference. This avoids duplicating type definitions.
我們使用 `zod` 進行執行時驗證與型別推導。這避免了重複定義型別。

```typescript
import { z } from 'zod';
import { Request, Response, NextFunction } from 'express';

// 1. Define the Schema
const CreateUserSchema = z.object({
  body: z.object({
    email: z.string().email(),
    role: z.enum(['admin', 'user']),
    metadata: z.record(z.string()).optional()
  }),
  query: z.object({
    dryRun: z.string().transform((val) => val === 'true').optional()
  })
});

// 2. Infer Types from Schema
type CreateUserRequest = z.infer<typeof CreateUserSchema>;

// 3. Generic Controller Type Helper
// This ensures TS checks that we are accessing valid properties on req.body/query
interface TypedRequest<T extends z.ZodType<any, any>> extends Request {
  body: z.infer<T>['body'];
  query: z.infer<T>['query'];
}

// 4. Middleware for Runtime Validation
const validate = (schema: z.ZodType<any, any>) => 
  (req: Request, res: Response, next: NextFunction) => {
    try {
      const parsed = schema.parse({
        body: req.body,
        query: req.query,
        params: req.params,
      });
      // Replace unsafe req data with parsed/transformed data
      req.body = parsed.body;
      req.query = parsed.query;
      next();
    } catch (error) {
      return res.status(400).json(error);
    }
  };
```

#### Step 2: The "Pure" Controller (Serverless Ready)
#### 步驟 2：「純粹」的 Controller（Serverless 就緒）

Instead of locking logic inside an Express handler, write the core logic as a pure function. The Express handler becomes just an adapter.
不要將邏輯鎖死在 Express handler 中，而是將核心邏輯寫成純函式。Express handler 僅僅作為一個適配器（Adapter）。

```typescript
// --- Core Domain Logic (Framework Agnostic) ---
// This can be reused in AWS Lambda, CLI, or Testing without mocking req/res
export const createUserCore = async (
  input: CreateUserRequest['body'], 
  isDryRun: boolean
) => {
  // Database logic here...
  if (isDryRun) return { id: 'simulated-id', status: 'dry-run' };
  return { id: '12345', status: 'created', email: input.email };
};

// --- Express Adapter ---
export const createUserController = async (
  req: TypedRequest<typeof CreateUserSchema>, // Strongly typed req
  res: Response
) => {
  // TS knows req.body.email exists and is a string
  // TS knows req.query.dryRun is a boolean (due to Zod transform)
  const result = await createUserCore(req.body, req.query.dryRun || false);
  res.status(201).json(result);
};

// --- Usage ---
// app.post('/users', validate(CreateUserSchema), createUserController);
```

**Why this matters for Seniors**:
*   **Testability**: You can unit test `createUserCore` without mocking `req` and `res`.
*   **Portability**: If you move to AWS Lambda, you just write a Lambda Adapter that calls `createUserCore`. You don't need to rewrite the business logic.
**這對資深工程師的重要性**：
*   **可測試性**：你可以對 `createUserCore` 進行單元測試，而無需模擬 `req` 和 `res`。
*   **可攜性**：如果你遷移到 AWS Lambda，只需寫一個 Lambda Adapter 來呼叫 `createUserCore`。你不需要重寫商業邏輯。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 The "Any" Trap & Incomplete Types
### 5.1 "Any" 陷阱與不完整的型別

*   **Anti-pattern**: Using `req: any` or `req: Request` (without generics) and then casting properties manually `(req.body as User)`.
*   **Why it's bad**: It defeats the purpose of TypeScript. If the upstream middleware changes the data structure, the compiler won't warn you, leading to runtime crashes.
*   **Solution**: Use Zod/Joi to infer types and enforce them at the runtime boundary (middleware), as shown in the example above.
*   **反模式**：使用 `req: any` 或 `req: Request`（未使用泛型），然後手動轉型 `(req.body as User)`。
*   **為何不好**：這違背了 TypeScript 的初衷。如果上游 middleware 改變了資料結構，編譯器不會警告你，導致執行時崩潰。
*   **解法**：使用 Zod/Joi 推導型別，並在執行時邊界（middleware）強制執行，如上例所示。

### 5.2 Global Namespace Pollution
### 5.2 全域命名空間污染

*   **Anti-pattern**: Overusing `declare global { namespace Express { ... } }` for every small property added to the request object.
*   **Why it's bad**: It makes the `Request` type bloated and ambiguous. A property added by an auth middleware might appear available in a public route where that middleware didn't run.
*   **Solution**: Use **Intersection Types** locally in controllers (e.g., `type AuthRequest = Request & { user: UserEntity }`) for specific routes that require those properties.
*   **反模式**：為每一個加到 request 物件的小屬性過度使用 `declare global { namespace Express { ... } }`。
*   **為何不好**：這會讓 `Request` 型別變得臃腫且模稜兩可。一個由驗證 middleware 加入的屬性，可能會顯示在該 middleware 未執行的公開路由中。
*   **解法**：在需要這些屬性的特定路由 controller 中，使用**交集型別（Intersection Types）**（例如 `type AuthRequest = Request & { user: UserEntity }`）。

### 5.3 Distributed Monolith (The Microservices Trap)
### 5.3 分散式單體（微服務陷阱）

*   **Anti-pattern**: Splitting Express apps into services but sharing the same Database instance or relying on synchronous HTTP calls for every operation.
*   **Why it's bad**: You inherit the complexity of distributed systems (latency, network failure) without the benefits of isolation. If the DB goes down, everything goes down.
*   **Solution**: Each microservice should own its data. Use **Event-Driven Architecture** (RabbitMQ/Kafka/SNS) for inter-service communication instead of deep chains of HTTP calls.
*   **反模式**：將 Express 應用拆分為服務，但共用同一個資料庫實例，或依賴同步 HTTP 呼叫進行每個操作。
*   **為何不好**：你繼承了分散式系統的複雜性（延遲、網路故障），卻沒有獲得隔離的好處。如果資料庫掛掉，所有服務都掛掉。
*   **解法**：每個微服務應擁有自己的資料。使用**事件驅動架構**（RabbitMQ/Kafka/SNS）進行服務間通訊，而非深層的 HTTP 呼叫鏈。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How would you migrate a critical, high-traffic Express monolith to TypeScript without stopping feature work?
### Q1: 你會如何在不停止功能開發的情況下，將一個關鍵、高流量的 Express 單體應用遷移至 TypeScript？

*   **Key Points**:
    *   **Coexistence**: Configure `tsconfig.json` with `allowJs: true`. This allows mixing `.js` and `.ts` files.
    *   **Strategy**: Don't rewrite existing working code immediately. Write **new features** in TS.
    *   **Tactical Refactoring**: Pick "leaf nodes" (utils, helpers) to convert first, then move to models/DTOs, and finally controllers.
    *   **CI/CD**: Ensure the build pipeline supports the hybrid structure.
*   **回答要點**：
    *   **共存**：設定 `tsconfig.json` 中的 `allowJs: true`。這允許混用 `.js` 和 `.ts` 檔案。
    *   **策略**：不要立即重寫現有運作中的程式碼。用 TS 撰寫**新功能**。
    *   **戰術性重構**：選擇「葉節點」（工具函式、helper）優先轉換，接著是 models/DTOs，最後才是 controllers。
    *   **CI/CD**：確保建置流程支援這種混合結構。

### Q2: In a Serverless environment (e.g., Lambda), traditional Express apps suffer from "Cold Starts". How do you mitigate this?
### Q2: 在 Serverless 環境（如 Lambda）中，傳統 Express 應用會遭遇「冷啟動（Cold Starts）」問題。你會如何緩解？

*   **Key Points**:
    *   **Lazy Loading**: Don't initialize database connections or load heavy libraries at the top level (global scope) if they aren't used by every route. Initialize them inside the handler or use lazy getters.
    *   **Bundle Size**: Use tools like `esbuild` or Webpack to tree-shake unused code.
    *   **Architecture**: Instead of deploying the entire Express app as one Lambda (Monolithic Lambda), split it. Use the API Gateway to route to smaller, single-purpose functions (Nano-services) to reduce the initialization overhead.
*   **回答要點**：
    *   **延遲載入**：如果資料庫連線或重型函式庫並非每個路由都會用到，不要在頂層（全域範疇）初始化它們。在 handler 內部初始化或使用 lazy getters。
    *   **打包大小**：使用 `esbuild` 或 Webpack 等工具來 tree-shake（搖樹優化）未使用的程式碼。
    *   **架構**：不要將整個 Express 應用部署為單一個 Lambda（單體 Lambda），應將其拆分。使用 API Gateway 路由至更小、單一用途的函式（奈米服務），以減少初始化開銷。

### Q3: How do you handle code sharing (e.g., Auth Middleware, Error Handling) across multiple Express microservices?
### Q3: 你如何在多個 Express 微服務之間處理程式碼共用（例如驗證 Middleware、錯誤處理）？

*   **Key Points**:
    *   **Private NPM Packages**: Extract common logic into a private library. Versioning becomes critical here (SemVer).
    *   **Sidecar Pattern**: For things like logging or metrics, run a sidecar container instead of embedding logic in the app code.
    *   **Gateway Offloading**: Move authentication (JWT verification) to the API Gateway level so individual services don't need to handle the initial auth handshake, only permission checks.
*   **回答要點**：
    *   **私有 NPM 套件**：將通用邏輯提取為私有函式庫。這裡版本控制（語意化版本 SemVer）變得至關重要。
    *   **Sidecar 模式**：對於日誌或指標等功能，運行 sidecar 容器，而不是將邏輯嵌入應用程式碼中。
    *   **Gateway 卸載**：將驗證（JWT 驗證）移至 API Gateway 層，這樣個別服務就不需要處理初始的驗證握手，只需處理權限檢查。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Key Takeaways (記憶錨點)
*   **TypeScript is a Contract**: Use Generics and Zod to strictly type `req.body` and `req.query`, moving error detection from runtime to compile-time.
    **TypeScript 是合約**：使用泛型和 Zod 嚴格定義 `req.body` 和 `req.query`，將錯誤偵測從執行時移至編譯時。
*   **Logic Decoupling**: Separate business logic from Express `req/res` objects to enable easier testing and migration to Serverless/FaaS.
    **邏輯解耦**：將商業邏輯與 Express `req/res` 物件分離，以利於測試及遷移至 Serverless/FaaS。
*   **Incremental Migration**: Use `allowJs: true` and the Strangler Fig pattern. Avoid "Big Bang" rewrites.
    **漸進式遷移**：使用 `allowJs: true` 和絞殺榕模式。避免「大爆炸式」重寫。
*   **Modular Monolith**: Organize code by Domain, not technical layer, as a precursor to Microservices.
    **模組化單體**：按領域而非技術層組織程式碼，作為微服務的前導。
*   **Observability**: Distributed systems require distributed tracing (OpenTelemetry) and structured logging.
    **可觀測性**：分散式系統需要分散式追蹤（OpenTelemetry）與結構化日誌。

### Next Steps (後續延伸)
*   **gRPC & Protobuf**: Learn how to replace internal HTTP REST calls between Express microservices with gRPC for better performance and stricter contracts.
    **gRPC & Protobuf**：學習如何用 gRPC 取代 Express 微服務內部的 HTTP REST 呼叫，以獲得更好的效能與更嚴格的合約。
*   **GraphQL Integration**: Explore implementing a GraphQL layer (using Apollo Server with Express) as a unified gateway over your new microservices.
    **GraphQL 整合**：探索實作 GraphQL 層（使用 Apollo Server 搭配 Express）作為新微服務之上的統一閘道。
*   **Containerization Deep Dive**: Master multi-stage Docker builds for optimized Node.js/Express production images.
    **容器化深入**：精通多階段 Docker 建置，以優化 Node.js/Express 的生產環境映像檔。