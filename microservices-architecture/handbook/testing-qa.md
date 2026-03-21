# 測試策略與契約測試 / Testing Strategies & Contract Testing

## Mental model｜心智模型

在微服務架構中，傳統的測試思維（特別是依賴大量 End-to-End 測試）會導致 CI/CD 管道極度緩慢且脆弱。我們需要將思維從「驗證整個系統」轉變為「驗證邊界與契約」。

### 1. The Shift: From Monolith to Distributed Boundaries
**轉變：從單體到分散式邊界**

- **Monolith Mindset**: "I need to deploy everything to a staging environment to see if it works." (我需要把所有東西部署到 Staging 環境才能知道它能不能跑。)
- **Microservices Mindset**: "I need to verify that my service behaves correctly in isolation and respects the contracts with its neighbors." (我需要驗證我的服務在隔離狀態下運作正常，且遵守與鄰居的契約。)

### 2. The Testing Pyramid Reimagined
**重新構想的測試金字塔**

在微服務中，金字塔的中層（Integration/Contract）變得至關重要，而頂層（E2E）必須被嚴格壓縮。

- **Unit Tests (單元測試)**: 驗證服務內部的商業邏輯 (Business Logic)。不涉及網路 I/O。
- **Contract Tests (契約測試)**: 驗證服務之間的「溝通協議」是否一致。這是微服務測試的核心。
- **Component/Integration Tests (組件/整合測試)**: 驗證服務與其基礎設施（DB, Cache）或 Mock 外部服務的互動。
- **End-to-End Tests (端對端測試)**: 僅用於驗證關鍵路徑 (Critical Paths)，數量極少，目的是確認系統「接線」正確，而非驗證邏輯。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Consumer-Driven Contract Testing (CDCT)
**消費者驅動契約測試**

這是解決微服務整合地獄的黃金標準。不要等到部署後才發現 API 欄位改了。

- **Concept**: 消費者 (Consumer) 定義他們需要的 API 格式（即 "Contract"），提供者 (Provider) 在 CI 階段驗證是否符合這些需求。
- **Tooling**: **Pact**, Spring Cloud Contract.
- **Why**: 它允許 Provider 自由重構內部代碼，只要不破壞 Contract，就不會影響 Consumer。
- **Practice**:
    - Consumer 撰寫單元測試生成 Contract (JSON 檔)。
    - Contract 上傳至 Broker (如 Pact Broker)。
    - Provider 的 CI pipeline 下載 Contract 並針對自身 API 執行驗證。

### 2. Service Virtualization & Mocking
**服務虛擬化與模擬**

在測試單一微服務時，永遠不要依賴真實的外部微服務。

- **Pattern**: 使用 **WireMock** 或 **Mountebank** 來模擬下游服務的回應。
- **Best Practice**: 確保你的 Mocks 與真實服務的行為一致（這就是 CDCT 發揮作用的地方：用 Contract 來生成 Mocks）。

### 3. Testing in Production (TiP) & Canary Analysis
**生產環境測試與金絲雀分析**

由於 E2E 測試很難覆蓋所有分散式場景，部分驗證責任需轉移到部署階段。

- **Synthetic Monitoring**: 定期在生產環境運行模擬使用者行為的輕量級腳本，確保核心功能活著。
- **Canary Release**: 新版本只開放給 1% 流量，觀察錯誤率與延遲，若有問題自動回滾。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "E2E Obsession" (The Testing Ice-Cream Cone)
**E2E 迷思（冰淇淋甜筒狀測試）**

- **Symptoms**: 團隊花費大量時間維護 Selenium/Cypress 腳本，CI 跑一次要 1 小時，且經常因為網路抖動或測試資料髒掉而失敗 (Flaky tests)。
- **Consequence**: 開發者不再信任測試結果，部署恐懼症增加。
- **Solution**: 刪除不穩定的 E2E，改用契約測試覆蓋交互邏輯。

### 2. Shared Test Databases
**共用測試資料庫**

- **Bad Practice**: 多個微服務在測試環境連接同一個實體資料庫，或者多個開發者共用一個 Staging DB。
- **Consequence**: 測試資料互相踩踏 (Data Collision)，無法平行執行測試。
- **Solution**: 使用 **Testcontainers** 在測試執行時動態啟動 Docker 化的獨立資料庫，測完即丟。

### 3. Testing Implementation Details
**測試實作細節**

- **Bad Practice**: 測試程式碼過度依賴內部的 class 結構或 private methods。
- **Consequence**: 每次重構 (Refactoring) 即使邏輯沒變，測試也會紅，導致重構成本過高。
- **Solution**: 測試應針對 Public API (Controller/Service Interface) 的行為與回傳值。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Where to test?
**決策樹：該在哪裡測？**

1. **是單一類別或函數的邏輯嗎？** -> **Unit Test**
2. **涉及資料庫查詢或外部 API 呼叫嗎？** -> **Integration/Component Test** (使用 Testcontainers 或 WireMock)
3. **涉及兩個服務之間的 API 格式約定嗎？** -> **Contract Test** (Pact)
4. **是使用者的核心關鍵路徑（如：結帳流程）嗎？** -> **E2E Test** (極少量)

### Workflow: Implementing CDCT (Pact)
**流程：實作消費者驅動契約**

- [ ] **Step 1 (Consumer)**: 在 Consumer 端撰寫單元測試，定義預期的 Request/Response。
- [ ] **Step 2 (Consumer)**: 執行測試，生成 Pact JSON 檔案。
- [ ] **Step 3 (Consumer)**: 將 Pact 檔案發布到 Pact Broker (帶上版本號)。
- [ ] **Step 4 (Provider)**: Provider 的 CI 觸發，從 Broker 拉取最新的 Pact 檔案。
- [ ] **Step 5 (Provider)**: 執行驗證測試（Pact 框架會自動發送 Request 給 Provider 並驗證 Response）。
- [ ] **Step 6 (Provider)**: 若驗證通過，標記該版本的契約為 "Verified"。

### Operational Checklist
**維運檢查清單**

- [ ] **Isolation**: 所有的單元與整合測試是否都能在沒有網路的情況下執行？(除了 E2E)
- [ ] **Speed**: 提交 PR 後，測試回饋迴圈 (Feedback Loop) 是否在 10 分鐘內？
- [ ] **Data Management**: 測試是否負責建立並清理自己的資料？(不依賴預先存在的資料)
- [ ] **Flakiness**: 是否有被標記為 `@Ignore` 或經常隨機失敗的測試？(有的話，立即修復或刪除)

---

## Real-world examples｜實戰案例

### Scenario: Order Service calls Inventory Service
**場景：訂單服務呼叫庫存服務**

假設 `Order Service` 需要呼叫 `Inventory Service` 的 `GET /inventory/{id}` 來確認庫存。

#### 1. The Contract (Pact JSON Fragment)
這是 Consumer (Order Service) 產生的契約，描述它「期望」看到的樣子。

```json
{
  "consumer": { "name": "OrderService" },
  "provider": { "name": "InventoryService" },
  "interactions": [
    {
      "description": "a request for inventory details",
      "request": {
        "method": "GET",
        "path": "/inventory/123"
      },
      "response": {
        "status": 200,
        "headers": { "Content-Type": "application/json" },
        "body": {
          "sku": "123",
          "quantity": 10,
          "status": "IN_STOCK"
        }
      }
    }
  ]
}
```

#### 2. Provider Verification (Java/Spring Boot Example)
`Inventory Service` 不需要啟動真實的 Controller，只需掛載測試環境並驗證契約。

```java
@Provider("InventoryService")
@PactFolder("pacts") // Or fetch from Pact Broker
public class InventoryProviderTest {

    @MockBean
    private InventoryRepository repository; // Mock the DB layer

    @TestTemplate
    @ExtendWith(PactVerificationInvocationContextProvider.class)
    void pactVerificationTestTemplate(PactVerificationContext context) {
        context.verifyInteraction();
    }

    @BeforeEach
    void before(PactVerificationContext context) {
        // Setup state: 當 Consumer 請求 ID 123 時，Mock DB 回傳對應資料
        when(repository.findById("123")).thenReturn(
            new InventoryItem("123", 10, InventoryStatus.IN_STOCK)
        );
        context.setTarget(new HttpTestTarget("localhost", 8080));
    }
}
```

#### 3. Why this saves you? (為什麼這能救你一命？)
如果 `Inventory Service` 的開發者決定將 `quantity` 欄位改名為 `qty`：
1. **沒有契約測試時**：`Inventory Service` 單元測試通過（因為它內部改了一致），部署上線。`Order Service` 呼叫失敗，生產環境炸裂。
2. **有契約測試時**：`Inventory Service` 在 CI 階段執行 `pactVerificationTestTemplate`，發現 Consumer 預期的是 `quantity` 但實際回傳 `qty`。**Build Failed**。開發者必須要麼回滾修改，要麼通知 Consumer 團隊升級。