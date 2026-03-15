# 核心設計哲學：API-First 與領域驅動設計 / Core Principles: API-First Design & DDD

## Mental model｜心智模型

在進入實作細節前，我們必須先翻轉「資料庫優先（Database-First）」的傳統思維。

### 1. The "Menu vs. Fridge" Analogy（菜單與冰箱的比喻）
- **Database-First**：就像讓客人直接走進廚房打開冰箱（Database），看有什麼食材就點什麼。這會導致內部實作（Schema）與外部需求（API）強耦合，改動資料庫結構就會弄壞 API。
- **API-First & DDD**：你先設計精美的菜單（API Contract），描述你能提供什麼服務（Business Value）。客人只看菜單點餐，廚房內部如何備料、食材放在哪個冰箱（SQL vs NoSQL），對客人來說是透明的。

### 2. The Interaction Layering（互動分層）
正確的依賴流向應該是：
> **User Needs** $\rightarrow$ **API Contract** $\rightarrow$ **Domain Logic** $\rightarrow$ **Persistence (DB)**

- **API-First** 確保我們解決的是使用者的問題，而不是暴露資料庫的結構。
- **DDD** 確保我們的程式碼邏輯（Domain）反映真實業務規則，而不是單純的資料搬運（CRUD）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Define Contract Before Code (Schema-First Development)
不要等到程式碼寫完才產生 Swagger/OpenAPI 文件。
- **作法**：使用 OpenAPI (Swagger) 或 AsyncAPI 規範先定義好介面。
- **好處**：
  - 前端與後端可以並行開發（利用 Mock Server）。
  - 迫使工程師先思考「資源（Resource）」與「行為（Action）」，而非「資料表（Table）」。

### 2. Intent-Based API Design (意圖導向設計)
API 的命名應反映業務意圖，而非資料庫操作。
- **Bad (CRUD style)**: `PATCH /users/123` with body `{"status": "active"}`
- **Good (Intent style)**: `POST /users/123/activate`
- **為什麼**：後者明確表達了業務含義（Activate），可以在 Domain 層觸發副作用（如發送歡迎信），前者只是單純改欄位。

### 3. Separation of Models (DTO vs. Entity)
嚴格區分 API 層的資料結構與資料庫層的實體。
- **Request/Response DTOs**：針對 API 消費者設計，包含驗證邏輯、UI 友善的格式。
- **Domain Entities**：包含核心業務邏輯與狀態檢查。
- **Persistence Models (ORM)**：對應資料庫表格結構。
- **實務建議**：使用 Mapper（如 AutoMapper, MapStruct 或手寫轉換函數）在層與層之間轉換，**絕不將 ORM Entity 直接回傳給 API**。

### 4. Bounded Contexts (界限上下文)
不要試圖建立一個「大一統」的資料庫模型。
- 在「電商系統」中，`Product` 在「銷售上下文」關注的是價格與描述；在「倉儲上下文」關注的是庫存位置與重量。
- **實務**：API 與 DB 設計應依據 Context 拆分，避免一個巨大的 `Products` 表格包含所有欄位。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Anemic Domain Model" (貧血模型)
- **症狀**：Entity 類別只有 `@Column` 和 Getter/Setter，所有的業務邏輯都散落在 Service 層甚至 Controller 層。
- **後果**：業務規則無法重用，資料狀態容易不一致。
- **修正**：將邏輯推回 Entity。例如 `order.cancel()` 應該在 Order 類別內檢查狀態是否允許取消，而不是在 Service 裡寫 `if (order.status == 'PAID') ...`。

### 2. Leaking Implementation Details (洩漏實作細節)
- **症狀**：API 回傳了 `is_deleted` (軟刪除標記)、`version` (樂觀鎖版本號) 或資料庫特定的 ID 格式，而這些對前端毫無意義。
- **後果**：前端邏輯與後端 DB 設計耦合，後端重構時前端必須跟著改。

### 3. God API / God Table (上帝物件)
- **症狀**：一個 `GET /data` 回傳所有東西，或者一個 `User` 表格有 100 個欄位。
- **後果**：效能低落，維護困難，違反單一職責原則（SRP）。

### 4. CRUD-Driven Development for Complex Business
- **症狀**：不管業務多複雜，API 永遠只有 POST/GET/PUT/DELETE 對應 Create/Read/Update/Delete。
- **風險**：對於簡單的 CMS 系統這沒問題；但對於金融、訂單系統，CRUD 無法表達狀態轉換的限制（例如：訂單出貨後不能直接改地址）。

---

## Checklists & workflows｜檢查清單與流程

### Phase 1: Design & Contract (API-First)
- [ ] **Vocabulary Check**: API URL 和欄位名稱是否使用了「通用語言（Ubiquitous Language）」？（業務人員看得懂嗎？）
- [ ] **Mock Verification**: 在寫任何一行後端程式碼前，前端是否已確認 Mock API 的 JSON 結構符合 UI 需求？
- [ ] **Abstraction Check**: API 是否隱藏了資料庫細節？（例如：沒有暴露 FK column name, 內部狀態碼）。

### Phase 2: Modeling (DDD)
- [ ] **Invariant Check**: 業務規則（Invariants）是否封裝在 Domain Entity 或 Value Object 中？
- [ ] **Boundary Check**: 這個 API 是否跨越了 Bounded Context？（例如：在「使用者資訊 API」中硬塞「最新訂單資訊」，導致耦合）。

### Phase 3: Implementation
- [ ] **Layering Check**: Controller 是否只負責 HTTP 解析與轉換，而不包含業務邏輯？
- [ ] **DTO Check**: 是否確保沒有任何 ORM Entity 類別出現在 Controller 的回傳型別中？

---

## Real-world examples｜實戰案例

### Scenario: Updating a User's Address
#### ❌ Anti-Pattern: Database-Driven (CRUD)

直接把資料庫欄位暴露出來，讓前端決定要改什麼。

**API Definition:**
`PUT /users/{id}`
```json
{
  "address_line1": "New St.",
  "zip_code": "90210",
  "is_verified": true  // 危險：前端不該能直接修改驗證狀態
}
```

**Backend Code (Anemic):**
```python
def update_user(id, data):
    user = db.find(id)
    user.update(data) # 直接把 JSON 倒進 DB，毫無業務防護
    user.save()
```

#### ✅ Best Practice: API-First & DDD

根據業務意圖設計 API，並在 Domain 層保護規則。

**API Definition (Intent-based):**
`POST /users/{id}/relocate` (搬家)
```json
{
  "new_address": {
    "street": "New St.",
    "zip": "90210"
  }
}
```

**Backend Code (Rich Model):**
```python
# Controller
def relocate_user(id, request_dto):
    user = repository.find_by_id(id)
    # 呼叫 Domain Method，而非直接改欄位
    user.relocate_to(request_dto.to_value_object()) 
    repository.save(user)
    return Response.ok()

# Domain Entity
class User:
    def relocate_to(self, new_address):
        if self.status == 'LOCKED':
            raise DomainException("Locked users cannot move.")
        
        self.address = new_address
        self.is_verified = False # 業務規則：搬家後需要重新驗證地址
        self.add_event(UserRelocatedEvent(self.id, new_address)) # 觸發副作用
```

### Key Takeaway
在這個案例中，API-First 讓我們定義了 `relocate` 這個明確的行為，而 DDD 確保了「搬家會導致地址驗證失效」這個業務規則被強制執行，不會因為前端忘記傳送 `is_verified: false` 而導致資料錯誤。