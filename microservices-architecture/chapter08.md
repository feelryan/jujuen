# Chapter 08: Testing Strategies & Chaos Engineering
# 第八章：測試策略與混沌工程

## 1. 前言與學習目標 (Introduction & Learning Objectives)

在微服務架構中，傳統的測試金字塔（Testing Pyramid）往往會因為服務間複雜的相依性而崩塌。單純依賴 End-to-End (E2E) 測試會導致部署管線緩慢且極不穩定（Flaky）。本章將探討如何透過契約測試（Consumer-Driven Contracts, CDC）來解耦服務間的測試，並引入混沌工程（Chaos Engineering）來驗證系統在不可預測故障下的韌性。

In microservices architecture, the traditional Testing Pyramid often crumbles due to complex inter-service dependencies. Relying solely on End-to-End (E2E) tests leads to slow and highly flaky deployment pipelines. This chapter explores how to decouple service testing using Consumer-Driven Contracts (CDC) and introduces Chaos Engineering to validate system resilience under unpredictable failures.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **區分並實作 CDC**：理解為何在微服務中「契約測試」比傳統整合測試更具優勢，並能解釋 Pact 等工具的工作原理。
    **Distinguish and implement CDC**: Understand why "Contract Testing" is superior to traditional integration testing in microservices and explain how tools like Pact work.
2.  **優化測試策略**：學會如何減少昂貴的 E2E 測試，改採「測試替身（Test Doubles）」與「契約驗證」相結合的策略。
    **Optimize testing strategy**: Learn how to reduce expensive E2E tests by adopting a strategy combining "Test Doubles" and "Contract Verification."
3.  **設計混沌實驗**：掌握混沌工程的核心原則（Blast Radius, Steady State），並能設計一個安全的實驗來驗證 Circuit Breaker 或 Retry 機制的有效性。
    **Design chaos experiments**: Master the core principles of Chaos Engineering (Blast Radius, Steady State) and design a safe experiment to validate the effectiveness of Circuit Breakers or Retry mechanisms.

---

## 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 測試金字塔的變形 (The Shift in Testing Pyramid)

在單體架構（Monolith）中，我們習慣啟動整個應用程式進行整合測試。但在微服務中，若要測試服務 A，可能需要啟動服務 B、C、D 以及它們的資料庫，這被稱為「整合測試地獄」。

In a monolithic architecture, we are used to spinning up the entire application for integration testing. However, in microservices, testing Service A might require spinning up Services B, C, D, and their databases, a situation known as "Integration Testing Hell."

*   **Mental Model**: 將微服務測試視為**拼圖（Jigsaw Puzzle）**。你不需要把整幅拼圖拼好才能確認兩塊拼圖是否吻合；你只需要檢查它們的**邊緣（介面/契約）**是否匹配。
    **Mental Model**: Treat microservices testing like a **Jigsaw Puzzle**. You don't need to assemble the entire puzzle to verify if two pieces fit; you only need to check if their **edges (interfaces/contracts)** match.

### 2.2 消費者驅動契約 (Consumer-Driven Contracts, CDC)

CDC 是一種測試模式，由「消費者（Consumer）」定義它需要從「提供者（Provider）」那裡獲得什麼（包含 Request 格式與預期的 Response）。這些需求被打包成一份「契約（Contract/Pact）」。

CDC is a testing pattern where the "Consumer" defines what it needs from the "Provider" (including the Request format and the expected Response). These requirements are packaged into a "Contract" (or Pact).

*   **Consumer Side**: 針對 Mock Provider 撰寫單元測試，生成契約檔。
    **Consumer Side**: Write unit tests against a Mock Provider to generate the contract file.
*   **Provider Side**: 讀取契約檔，並重播（Replay）請求來驗證自己是否符合契約。
    **Provider Side**: Read the contract file and replay the requests to verify if it complies with the contract.
*   **Analogy**: 想像你去餐廳點餐（API Call）。你不需要進廚房看廚師怎麼做菜（Internal Logic），你只需要確認菜單上的照片（Contract）與端上來的菜（Response）是一致的。
    **Analogy**: Imagine ordering food at a restaurant (API Call). You don't need to go into the kitchen to see how the chef cooks (Internal Logic); you just need to verify that the photo on the menu (Contract) matches the dish served (Response).

### 2.3 混沌工程 (Chaos Engineering)

混沌工程並非單純的「搞破壞」，而是一種**實驗學科**。它的目標是在生產環境或類生產環境中，主動注入故障，以發現系統中的脆弱點。

Chaos Engineering is not simply "breaking things"; it is an **experimental discipline**. Its goal is to proactively inject faults in production or production-like environments to uncover vulnerabilities in the system.

*   **Core Principle**: 它是疫苗，不是毒藥。透過注入少量且受控的故障（如延遲、封包遺失），訓練系統產生抗體（自動復原、降級）。
    **Core Principle**: It is a vaccine, not a poison. By injecting small, controlled faults (e.g., latency, packet loss), the system is trained to develop antibodies (auto-recovery, degradation).

---

## 3. 實務場景與系統設計視角 (Real-World & System Design View)

### 3.1 解耦部署管線 (Decoupling Deployment Pipelines)

在 System Design 面試或實務中，常見的挑戰是：「如果 Service B 更新了 API，如何確保不會弄壞依賴它的 Service A？」

In System Design interviews or practice, a common challenge is: "If Service B updates its API, how do we ensure it doesn't break Service A which depends on it?"

*   **Without CDC**: Service B 的團隊必須跑完整的 E2E 測試，或者口頭詢問 Service A 團隊。這導致部署恐懼與延遲。
    **Without CDC**: Service B's team must run full E2E tests or verbally ask Service A's team. This leads to deployment fear and delays.
*   **With CDC**: Service B 在 CI/CD Pipeline 中自動執行契約驗證。只要通過驗證，即便 API 內部邏輯大改，甚至新增了欄位（只要不刪除 Service A 需要的舊欄位），都能安心部署。
    **With CDC**: Service B automatically runs contract verification in the CI/CD Pipeline. As long as it passes, even if the internal logic changes significantly or new fields are added (provided old fields needed by Service A are not removed), deployment is safe.

### 3.2 驗證非功能性需求 (Verifying Non-Functional Requirements)

混沌工程在系統設計中主要用於驗證 **Availability（可用性）** 與 **Partition Tolerance（分區容錯性）**。

Chaos Engineering is primarily used in system design to verify **Availability** and **Partition Tolerance**.

*   **Scenario**: 你設計了一個帶有 Circuit Breaker 的 Payment Service。
    **Scenario**: You designed a Payment Service with a Circuit Breaker.
*   **The Gap**: 在單元測試中，你 Mock 了失敗，Circuit Breaker 運作正常。但在真實網路延遲下，Thread Pool 是否會先被耗盡？Timeout 設定是否過長導致雪崩？
    **The Gap**: In unit tests, you mocked the failure, and the Circuit Breaker worked. But under real network latency, will the Thread Pool be exhausted first? Is the Timeout setting too long, causing a cascading failure?
*   **The Fix**: 使用 Chaos Mesh 或 Gremlin 注入 2000ms 的網路延遲，觀察 Grafana 儀表板，確認 Circuit Breaker 是否在預期時間內開啟，且系統是否正確切換到 Fallback 邏輯。
    **The Fix**: Use Chaos Mesh or Gremlin to inject 2000ms of network latency, monitor the Grafana dashboard, and confirm if the Circuit Breaker opens within the expected time and if the system correctly switches to Fallback logic.

---

## 4. 逐步示例 (Walkthrough / Example)

### 4.1 實作 CDC (Consumer-Driven Contracts)

假設我們有兩個服務：`OrderService` (Consumer) 和 `UserService` (Provider)。`OrderService` 需要透過 `GET /users/{id}` 獲取使用者地址。

Let's assume we have two services: `OrderService` (Consumer) and `UserService` (Provider). `OrderService` needs to fetch user addresses via `GET /users/{id}`.

#### Step 1: Consumer 定義期望 (Consumer Defines Expectations)

在 `OrderService` 的測試程式碼中，我們使用 Pact SDK 定義契約。

In `OrderService`'s test code, we use the Pact SDK to define the contract.

```javascript
// Pseudo-code using Pact JS conceptual model
const interaction = {
  state: "User 123 exists",
  uponReceiving: "A request for user 123",
  withRequest: {
    method: "GET",
    path: "/users/123",
    headers: { "Accept": "application/json" }
  },
  willRespondWith: {
    status: 200,
    body: {
      id: "123",
      // We only care about address here. 
      // Even if UserService returns 'age', we don't put it in contract if we don't use it.
      address: Matchers.string("123 Main St") 
    }
  }
};

// Run this test -> Generates "order-service-user-service.json" (The Pact File)
```

#### Step 2: 分享契約 (Share the Contract)

Pact 檔案通常會上傳到一個中央伺服器（Pact Broker）。

The Pact file is usually uploaded to a central server (Pact Broker).

#### Step 3: Provider 驗證契約 (Provider Verifies Contract)

在 `UserService` 的 CI 流程中，它會下載契約並執行驗證。

In `UserService`'s CI process, it downloads the contract and runs verification.

```java
// Pseudo-code for Provider Test
@PactFolder("pacts") // Or fetch from Broker
public class UserServiceProviderTest {

    @TestTemplate
    @ExtendWith(PactVerificationInvocationContextProvider.class)
    void pactVerificationTestTemplate(PactVerificationContext context) {
        context.verifyInteraction();
    }

    @State("User 123 exists")
    public void toUser123Exists() {
        // Setup DB or Mock to ensure user 123 is actually there
        userRepository.save(new User("123", "123 Main St"));
    }
}
```

**為何這可行？**：這保證了 `UserService` 的任何變更，如果破壞了 `OrderService` 的使用方式（例如把 `address` 改名為 `addr`），CI 會直接失敗，阻止部署。

**Why this works?**: This guarantees that any change in `UserService` that breaks `OrderService`'s usage (e.g., renaming `address` to `addr`) will cause the CI to fail immediately, blocking deployment.

### 4.2 混沌實驗設計 (Designing a Chaos Experiment)

**目標 (Goal)**: 驗證當 DB CPU 飆高時，API 是否能優雅降級（Graceful Degradation）。
**Target**: Verify if the API can gracefully degrade when DB CPU spikes.

1.  **定義穩態 (Define Steady State)**:
    *   正常情況下，API 延遲 < 200ms，錯誤率 < 0.1%。
    *   Normally, API latency < 200ms, error rate < 0.1%.
2.  **提出假設 (Hypothesis)**:
    *   如果 DB CPU 達到 90%，API 延遲會增加，但 Read Replica 應該能分擔流量，或者 Cache 應該能擋住部分請求，錯誤率不應超過 2%。
    *   If DB CPU hits 90%, API latency will increase, but Read Replicas should share the load, or Cache should serve requests; error rate should not exceed 2%.
3.  **執行實驗 (Run Experiment)**:
    *   使用工具（如 AWS FIS 或 Chaos Mesh）對 DB 容器注入 CPU Stress。
    *   Use tools (like AWS FIS or Chaos Mesh) to inject CPU Stress into the DB container.
4.  **觀察與學習 (Observe & Learn)**:
    *   如果錯誤率飆升到 50%，代表 Connection Pool 設定不當或 Cache 失效。
    *   If the error rate spikes to 50%, it indicates improper Connection Pool settings or Cache failure.

---

## 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 過度依賴 E2E 測試 (Over-reliance on E2E Tests)

*   **Anti-pattern**: 試圖在 CI 環境中啟動所有 50+ 個微服務來跑測試。
    **Anti-pattern**: Trying to spin up all 50+ microservices in the CI environment to run tests.
*   **Why it's bad**: 環境極不穩定（Flaky），執行時間長（數小時），導致開發者不願頻繁提交程式碼。
    **Why it's bad**: The environment is highly flaky, execution takes hours, leading to developers being reluctant to commit code frequently.
*   **Solution**: 將 80% 的 E2E 測試替換為 CDC 和單元測試。僅保留極少數關鍵路徑（Critical Path）的 E2E 測試（如「使用者結帳」流程）。
    **Solution**: Replace 80% of E2E tests with CDC and unit tests. Keep only a very few Critical Path E2E tests (e.g., "User Checkout" flow).

### 5.2 在契約測試中驗證業務邏輯 (Testing Business Logic in Contracts)

*   **Anti-pattern**: Consumer 在契約中要求：「如果我送出金額 100，回傳的稅金必須是 5」。
    **Anti-pattern**: Consumer requires in the contract: "If I send amount 100, the returned tax must be 5."
*   **Why it's bad**: 這是 Provider 的內部邏輯測試，不該由 Consumer 決定。契約應專注於 **Schema（結構）** 與 **Interaction（互動方式）**。
    **Why it's bad**: This is an internal logic test for the Provider and should not be dictated by the Consumer. Contracts should focus on **Schema** and **Interaction**.
*   **Solution**: 契約只驗證：「如果我送出金額 100，回傳的結構包含 `tax` 欄位且為數字」。
    **Solution**: The contract only verifies: "If I send amount 100, the returned structure contains a `tax` field which is a number."

### 5.3 缺乏觀測性的混沌工程 (Chaos without Observability)

*   **Anti-pattern**: 在沒有完善監控的情況下進行混沌測試。
    **Anti-pattern**: Conducting chaos testing without comprehensive monitoring.
*   **Why it's bad**: 系統壞了你不知道原因，甚至不知道它壞了。這不是實驗，這是玩火。
    **Why it's bad**: You won't know why the system broke, or even *that* it broke. This isn't experimentation; it's playing with fire.
*   **Solution**: 先建立 Logs, Metrics, Tracing，確認能看到系統的「心跳」，再開始注入故障。
    **Solution**: Establish Logs, Metrics, and Tracing first to ensure you can see the system's "heartbeat" before injecting faults.

---

## 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 如何在微服務架構中處理「跨服務的整合測試」？
**How do you handle "cross-service integration testing" in a microservices architecture?**

*   **Key Points**:
    *   承認 E2E 的成本與不穩定性。
    *   提出 **Testing Pyramid** 的轉變：Unit > Contract (CDC) > Component > E2E。
    *   解釋 **CDC** 如何讓 Consumer 與 Provider 解耦開發。
    *   提及使用 **Service Virtualization** (如 WireMock) 來隔離依賴。

### Q2: 什麼時候應該引入混沌工程？是在開發初期還是上線後？
**When should Chaos Engineering be introduced? Early in development or after launch?**

*   **Key Points**:
    *   **Shift Left**: 可以在開發環境（Staging）早期引入，例如自動化的「斷網測試」。
    *   **Prerequisites**: 強調必須先有足夠的**可觀測性（Observability）**和**自動化恢復能力**。
    *   **Blast Radius**: 在 Production 執行時，必須控制影響範圍（例如只針對 1% 的非關鍵用戶）。

### Q3: Mocking 和 Contract Testing 有什麼不同？
**What is the difference between Mocking and Contract Testing?**

*   **Key Points**:
    *   **Mocking**: 是 Consumer 自己的假設（Assumption）。如果 Provider 改了 API，Mock 不會報錯，但上線會炸。
    *   **Contract Testing**: 驗證了 Mock 的假設是否真實。它確保 Consumer 的 Mock 與 Provider 的實際行為保持同步。
    *   **Phrase**: "Mocks can lie; Contracts are verified lies." (Mock 會說謊；契約是經過驗證的謊言。)

---

## 7. 小結與後續延伸 (Summary & Next Steps)

### 重點回顧 (Key Takeaways)

1.  **放棄全量 E2E**：在微服務中，試圖複製完整生產環境進行測試是不切實際的。
    **Abandon full E2E**: In microservices, trying to replicate the full production environment for testing is impractical.
2.  **擁抱 CDC**：使用 Pact 等工具建立 Consumer 與 Provider 間的契約，確保 API 變更的安全性。
    **Embrace CDC**: Use tools like Pact to establish contracts between Consumers and Providers, ensuring the safety of API changes.
3.  **契約非邏輯**：契約測試關注的是「溝通格式（Schema）」而非「業務邏輯（Business Logic）」。
    **Contracts != Logic**: Contract tests focus on "Communication Schema," not "Business Logic."
4.  **混沌即實驗**：混沌工程是為了驗證系統的韌性（Resilience），必須包含「穩態假設」與「控制變因」。
    **Chaos is Experimentation**: Chaos Engineering validates system resilience and must include "Steady State Hypotheses" and "Controlled Variables."
5.  **觀測先行**：沒有可觀測性，就沒有混沌工程。
    **Observability First**: No observability, no Chaos Engineering.

### 後續延伸 (Next Steps)

*   **Study**: 深入研究 **Service Mesh (Istio/Linkerd)** 如何透過 Fault Injection 功能來簡化混沌實驗。
    **Study**: Deep dive into how **Service Mesh (Istio/Linkerd)** simplifies chaos experiments via Fault Injection features.
*   **Practice**: 在你的 CI Pipeline 中加入一個簡單的 Pact 驗證步驟。
    **Practice**: Add a simple Pact verification step to your CI Pipeline.
*   **Next Chapter**: 進入 **Chapter 09: Security & Identity (OAuth2, OIDC, mTLS)**，探討如何在這些測試策略之上，確保微服務的安全性。
    **Next Chapter**: Move on to **Chapter 09: Security & Identity (OAuth2, OIDC, mTLS)** to explore how to secure microservices on top of these testing strategies.