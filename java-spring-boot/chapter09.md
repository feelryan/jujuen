# Chapter 09: 可觀測性與生產環境維運
# Chapter 09: Observability & Production Readiness

## 1. 前言與學習目標 (Introduction & Learning Objectives)

在現代微服務架構與雲原生環境中，「程式碼能跑」只是起點。資深工程師的價值在於能夠構建「可被理解、可被除錯、可被量化」的系統。本章將超越基礎的 `System.out.println` 或簡單的 Health Check，深入探討如何利用 Spring Boot 生態系構建生產級的可觀測性（Observability）。

In modern microservices architectures and cloud-native environments, "code that works" is just the starting point. The value of a Senior Engineer lies in building systems that are "understandable, debuggable, and quantifiable." This chapter moves beyond basic `System.out.println` or simple Health Checks, diving deep into building production-grade Observability using the Spring Boot ecosystem.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **掌握 Micrometer 的核心抽象**：理解如何利用 Micrometer 作為「度量的 SLF4J」，並正確處理維度（Tags）與基數（Cardinality）問題。
    **Master Micrometer Core Abstractions**: Understand how to use Micrometer as "SLF4J for metrics" and correctly handle dimensionality (Tags) and Cardinality issues.
2.  **實作分散式追蹤（Distributed Tracing）**：在 Spring Boot 3.x 中使用 Micrometer Tracing (取代 Spring Cloud Sleuth) 實現跨服務的請求追蹤與 Log 關聯。
    **Implement Distributed Tracing**: Use Micrometer Tracing (replacing Spring Cloud Sleuth) in Spring Boot 3.x to achieve cross-service request tracing and log correlation.
3.  **區分 Liveness 與 Readiness**：正確配置 Kubernetes Probes，避免因錯誤的健康檢查導致服務頻繁重啟或流量黑洞。
    **Distinguish Liveness from Readiness**: Correctly configure Kubernetes Probes to avoid frequent restarts or traffic blackholes caused by incorrect health checks.
4.  **建立黃金訊號監控（Golden Signals）**：利用 Prometheus 與 Grafana 視覺化延遲（Latency）、流量（Traffic）、錯誤（Errors）與飽和度（Saturation）。
    **Establish Golden Signal Monitoring**: Visualize Latency, Traffic, Errors, and Saturation using Prometheus and Grafana.

---

## 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 可觀測性的三大支柱 (The Three Pillars of Observability)

對於資深工程師而言，必須清楚區分 Metrics、Logs 與 Traces 的用途與成本結構。
For senior engineers, it is crucial to distinguish the purpose and cost structure of Metrics, Logs, and Traces.

1.  **Metrics (度量)**：
    *   **定義**：可聚合的數值資料（如：過去 1 分鐘的平均回應時間）。
    *   **特性**：成本低，適合宏觀趨勢分析，但缺乏單一請求的細節。
    *   **Spring 對應**：Micrometer, Spring Boot Actuator.
    *   **Definition**: Aggregatable numerical data (e.g., average response time over the last minute).
    *   **Characteristics**: Low cost, suitable for macro trend analysis, but lacks details of individual requests.
    *   **Spring Mapping**: Micrometer, Spring Boot Actuator.

2.  **Logs (日誌)**：
    *   **定義**：離散的事件紀錄（如：User X failed to login due to bad password）。
    *   **特性**：成本高（儲存與檢索），包含豐富細節，適合事後分析。
    *   **Spring 對應**：SLF4J, Logback/Log4j2.
    *   **Definition**: Discrete event records (e.g., User X failed to login due to bad password).
    *   **Characteristics**: High cost (storage and retrieval), rich in detail, suitable for post-mortem analysis.
    *   **Spring Mapping**: SLF4J, Logback/Log4j2.

3.  **Traces (追蹤)**：
    *   **定義**：請求在分散式系統中的傳播路徑（如：Service A -> Service B -> DB）。
    *   **特性**：提供請求的因果關係與時間分佈，解決微服務中的「不知誰慢」問題。
    *   **Spring 對應**：Micrometer Tracing (Brave/OpenTelemetry).
    *   **Definition**: The propagation path of a request through a distributed system (e.g., Service A -> Service B -> DB).
    *   **Characteristics**: Provides causality and timing distribution of requests, solving the "don't know who is slow" problem in microservices.
    *   **Spring Mapping**: Micrometer Tracing (Brave/OpenTelemetry).

### 2.2 Micrometer：度量的外觀模式 (Micrometer: The Facade Pattern for Metrics)

就像 SLF4J 是 Logging 的標準介面，**Micrometer 是 Java 應用程式 Metrics 的標準介面**。
Just as SLF4J is the standard interface for Logging, **Micrometer is the standard interface for Metrics in Java applications**.

*   **Mental Model**: 你不需要針對 Prometheus 寫程式碼，你針對 `MeterRegistry` 寫程式碼。Spring Boot 會根據 classpath 自動注入適當的實作（如 `PrometheusMeterRegistry`）。
*   **Mental Model**: You don't write code for Prometheus; you write code against `MeterRegistry`. Spring Boot automatically injects the appropriate implementation (e.g., `PrometheusMeterRegistry`) based on the classpath.

### 2.3 Spring Boot 3.x 的變革 (Changes in Spring Boot 3.x)

Spring Cloud Sleuth 專案已停止維護，其核心功能已移入 **Micrometer Tracing**。這是一個重要的轉變，意味著 Metrics 與 Tracing 現在統一在 Micrometer 傘下，使得 API 與配置更加一致。
The Spring Cloud Sleuth project is no longer maintained, and its core functionality has moved into **Micrometer Tracing**. This is a significant shift, meaning Metrics and Tracing are now unified under the Micrometer umbrella, making APIs and configurations more consistent.

---

## 3. 實務場景與系統設計視角 (Real-World & System Design View)

### 3.1 生產環境架構 (Production Architecture)

在典型的 Big Tech 環境中，Spring Boot 應用程式的可觀測性架構通常如下：
In a typical Big Tech environment, the observability architecture for a Spring Boot application usually looks like this:

1.  **Application Side**:
    *   Spring Boot Actuator 暴露 `/actuator/prometheus` 端點（Pull Model）。
    *   Micrometer Tracing 產生 Trace ID 與 Span ID，並注入 MDC (Mapped Diagnostic Context) 以便 Log 關聯。
    *   Logs 非同步寫入 stdout (容器化標準) 或本地檔案。

2.  **Infrastructure Side**:
    *   **Metrics**: Prometheus Server 定期 scrape 應用程式的端點。
    *   **Logs**: Fluentd/Promtail 作為 Sidecar 或 DaemonSet 收集 stdout，轉送至 Elasticsearch/Loki。
    *   **Traces**: OpenTelemetry Collector 接收 Trace 資料，轉送至 Jaeger/Tempo/Zipkin。

### 3.2 Liveness vs. Readiness 的設計權衡 (Design Trade-offs: Liveness vs. Readiness)

這是系統設計面試與實務中常見的考點。
This is a common topic in system design interviews and practice.

*   **Liveness (存活探針)**：
    *   **意義**：App 是否崩潰？是否需要重啟？
    *   **實作**：通常只檢查 Process 是否還在，或者死鎖檢測。**千萬不要檢查 DB 連線**。如果 DB 掛了，重啟 App 沒用，只會造成級聯故障（Cascading Failure）。
    *   **Meaning**: Has the app crashed? Does it need a restart?
    *   **Implementation**: Usually just checks if the process exists or detects deadlocks. **Never check DB connections**. If the DB is down, restarting the app won't help and will only cause cascading failures.

*   **Readiness (就緒探針)**：
    *   **意義**：App 是否準備好接收流量？
    *   **實作**：檢查 DB、Cache、依賴服務是否可用。如果失敗，Load Balancer 會停止派發流量給該實例，但不會重啟它。
    *   **Meaning**: Is the app ready to accept traffic?
    *   **Implementation**: Checks if DB, Cache, and dependent services are available. If it fails, the Load Balancer stops sending traffic to this instance, but does not restart it.

---

## 4. 逐步示例 (Walkthrough / Example)

### 情境：監控訂單處理服務的效能 (Scenario: Monitoring Order Processing Performance)

我們需要監控 `OrderService.createOrder()` 方法的執行時間，並按「訂單類型」與「結果（成功/失敗）」進行分類統計。同時，我們需要確保 Log 中包含 Trace ID 以便排錯。
We need to monitor the execution time of the `OrderService.createOrder()` method, categorized by "order type" and "result (success/failure)". Additionally, we need to ensure Logs contain Trace IDs for debugging.

#### 步驟 1: 引入依賴 (Step 1: Dependencies)

在 Spring Boot 3.x (Maven) 中：
In Spring Boot 3.x (Maven):

```xml
<dependencies>
    <!-- Actuator for Metrics endpoints -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-actuator</artifactId>
    </dependency>
    <!-- Micrometer implementation for Prometheus -->
    <dependency>
        <groupId>io.micrometer</groupId>
        <artifactId>micrometer-registry-prometheus</artifactId>
    </dependency>
    <!-- Micrometer Tracing with Brave (or OpenTelemetry) -->
    <dependency>
        <groupId>io.micrometer</groupId>
        <artifactId>micrometer-tracing-bridge-brave</artifactId>
    </dependency>
</dependencies>
```

#### 步驟 2: 程式化埋點 (Step 2: Programmatic Instrumentation)

雖然 `@Timed` 註解很方便，但在複雜邏輯中，程式化方式（Programmatic）更靈活，特別是動態 Tag。
While the `@Timed` annotation is convenient, the programmatic approach is more flexible for complex logic, especially for dynamic Tags.

```java
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import io.micrometer.core.instrument.Tag;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.concurrent.TimeUnit;

@Service
public class OrderService {

    private static final Logger log = LoggerFactory.getLogger(OrderService.class);
    private final MeterRegistry meterRegistry;

    public OrderService(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
    }

    public void createOrder(String orderType) {
        long start = System.nanoTime();
        String outcome = "SUCCESS";
        
        try {
            log.info("Starting order creation for type: {}", orderType);
            // Simulate business logic
            processOrder(orderType); 
        } catch (Exception e) {
            outcome = "ERROR";
            log.error("Order creation failed", e);
            throw e;
        } finally {
            // Record the metric
            // Metric Name: order.creation.time
            // Tags: type=VIP, outcome=SUCCESS
            Timer.builder("order.creation.time")
                .description("Time taken to create an order")
                .tags(List.of(
                    Tag.of("type", orderType),
                    Tag.of("outcome", outcome)
                ))
                .register(meterRegistry)
                .record(System.nanoTime() - start, TimeUnit.NANOSECONDS);
        }
    }

    private void processOrder(String type) throws InterruptedException {
        Thread.sleep(100); // Simulate work
    }
}
```

#### 步驟 3: Log 關聯設定 (Step 3: Log Correlation Configuration)

在 `application.properties` 中設定 Log 格式，使其包含 Trace ID。
Configure the Log format in `application.properties` to include the Trace ID.

```properties
# Spring Boot 3.x default format usually includes tracing info if present
# But to be explicit:
logging.pattern.level=%5p [${spring.application.name:},%X{traceId:-},%X{spanId:-}]
```

**結果 (Outcome)**：
當 API 被呼叫時，Log 會顯示如下：
When the API is called, the Log will look like this:

```text
INFO [order-service,65b8e9f2d12e34a1,65b8e9f2d12e34a1] : Starting order creation for type: VIP
```

這允許你在 Kibana/Splunk 中搜尋 `traceId=65b8e9f2d12e34a1`，一次拉出該請求跨越所有微服務的所有 Log。
This allows you to search for `traceId=65b8e9f2d12e34a1` in Kibana/Splunk and pull up all logs for that request across all microservices at once.

---

## 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 基數爆炸 (Cardinality Explosion)

這是 Metrics 系統中最致命的錯誤。
This is the most fatal error in Metrics systems.

*   **錯誤案例**：將 `userId`、`email` 或 `orderId` 作為 Metric 的 Tag。
    `Tag.of("userId", userId)`
*   **後果**：Prometheus 是時間序列資料庫（TSDB），它會為每一組 Tag 組合建立一個新的時間序列。如果 Tag 的值是無限的（Unbounded），記憶體會迅速耗盡，導致監控系統崩潰。
*   **正確做法**：Tag 必須是有限集合（Bounded Set），如 `region`, `status`, `error_code`, `user_tier` (VIP/Regular)。
*   **Error Case**: Using `userId`, `email`, or `orderId` as a Metric Tag.
*   **Consequence**: Prometheus is a Time Series Database (TSDB); it creates a new time series for every unique combination of Tags. If the Tag values are unbounded, memory will be exhausted rapidly, crashing the monitoring system.
*   **Correct Approach**: Tags must be a Bounded Set, such as `region`, `status`, `error_code`, `user_tier`.

### 5.2 過度依賴 `@Timed` (Over-reliance on `@Timed`)

*   **問題**：`@Timed` 只能監控方法的進入與退出。它無法捕捉方法 *內部* 的分支邏輯或特定區塊的效能，也難以動態添加基於執行結果的 Tag（如 `exception_type`）。
*   **建議**：對於關鍵路徑，使用 `Timer.builder()` 手動埋點。
*   **Issue**: `@Timed` only monitors method entry and exit. It cannot capture performance of specific blocks *inside* the method or branching logic, and it's hard to dynamically add Tags based on execution results (e.g., `exception_type`).
*   **Recommendation**: Use `Timer.builder()` for manual instrumentation on critical paths.

### 5.3 忽略採樣率 (Ignoring Sampling Rate)

*   **問題**：在分散式追蹤中，如果將 Sampling Rate 設為 1.0 (100%)，對於高流量系統會產生巨大的儲存與網路成本。
*   **建議**：在生產環境設定合理的採樣率（如 0.01 或 0.1），或使用「基於頭部的採樣」（Head-based sampling）與自適應採樣。
*   **Issue**: In distributed tracing, setting the Sampling Rate to 1.0 (100%) incurs massive storage and network costs for high-traffic systems.
*   **Recommendation**: Set a reasonable sampling rate in production (e.g., 0.01 or 0.1), or use Head-based sampling and adaptive sampling.

---

## 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 你如何設計一個高併發系統的監控指標，以避免對主流程造成效能影響？
**How do you design monitoring metrics for a high-concurrency system to avoid performance impact on the main flow?**

*   **高分回答要點**：
    *   **非同步與緩衝**：說明 Metrics 收集通常發生在記憶體中（如 Micrometer 的 RingBuffer），並由獨立執行緒非同步推播或被拉取，不會阻塞請求處理。
    *   **基數控制**：強調避免 High Cardinality Tags。
    *   **直方圖（Histograms）成本**：提到 Percentile (P99, P95) 計算的成本，以及 Client-side 計算 vs Server-side (Prometheus Histogram) 計算的權衡。

### Q2: 當系統出現 "Latency Spike" 時，你如何利用可觀測性工具定位根因？
**When the system experiences a "Latency Spike", how do you use observability tools to pinpoint the root cause?**

*   **高分回答要點**：
    *   **由廣入微**：先看 Metrics (Grafana) 確認是哪個 Service、哪個 Endpoint 變慢。
    *   **關聯分析**：利用該時間段的 Trace ID，去 Tracing 系統 (Jaeger) 看 Waterfall 圖，找出是 DB 慢、外部 API 慢還是 CPU 密集運算慢。
    *   **日誌佐證**：利用 Trace ID 搜尋 Logs，查看是否有 Exception 或異常邏輯分支。

### Q3: Spring Boot Actuator 的安全性如何考量？
**How do you consider the security of Spring Boot Actuator?**

*   **高分回答要點**：
    *   **網路隔離**：Actuator 端點不應暴露給 Public Internet。通常設定在不同的 Port（`management.server.port`）並僅允許內網或監控伺服器存取。
    *   **細粒度權限**：使用 Spring Security 限制對 `/env`, `/heapdump`, `/threaddump` 等敏感端點的存取，因為它們可能洩露環境變數（包含密碼）或記憶體資料。

---

## 7. 小結與後續延伸 (Summary & Next Steps)

### 重點回顧 (Key Takeaways)

1.  **Micrometer is Key**：它是 Metrics 的 Facade，掌握它就能適配各種監控後端。
2.  **Cardinality Matters**：永遠不要將無限增長的 ID 放進 Tag 中。
3.  **Trace ID Propagation**：確保 Log 中包含 Trace ID 是微服務除錯的基石。
4.  **Health Check Strategy**：Liveness 檢查 Process，Readiness 檢查依賴，不可混用。
5.  **Spring Boot 3.x**：注意 Sleuth 到 Micrometer Tracing 的遷移。

### 後續延伸 (Next Steps)

*   **Advanced**: 研究 **OpenTelemetry (OTel)** Java Agent 自動埋點與手動埋點的混合使用。
*   **Next Chapter**: 進入 **Chapter 10: Performance Tuning & JVM Internals**，學習如何解讀這些 Metrics 並進行 JVM 調校。