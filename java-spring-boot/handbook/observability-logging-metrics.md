# 可觀測性實戰：日誌、指標與追蹤 / Observability in Action: Logging, Metrics & Tracing

## Mental model｜心智模型

在現代 Spring Boot 微服務架構中，**可觀測性 (Observability)** 並不僅僅是「寫 Log」。你應該將其視為系統的「醫療儀表板」與「病歷記錄」。

我們通常透過 **三大支柱 (The Three Pillars)** 來構建這個模型：

1.  **Metrics (指標) - "Is it healthy?"**
    *   **概念**：聚合的數值資料。告訴你系統的「趨勢」與「現狀」。
    *   **類比**：汽車儀表板上的時速表、水溫計。
    *   **用途**：觸發警報 (Alerting)。例如：CPU 使用率 > 80%、HTTP 500 錯誤率突增。
2.  **Logging (日誌) - "What happened?"**
    *   **概念**：離散的事件紀錄。告訴你特定時間點發生的「細節」。
    *   **類比**：飛機的黑盒子或航海日誌。
    *   **用途**：除錯 (Debugging) 與根本原因分析 (RCA)。
3.  **Tracing (追蹤) - "Where did it happen?"**
    *   **概念**：請求在分散式系統中的傳播路徑。將 Metrics 與 Logs 串聯起來的「線索」。
    *   **類比**：包裹的物流追蹤單號，顯示包裹經過了哪些轉運站。
    *   **用途**：效能瓶頸分析、定位故障發生的具體服務。

**關鍵思維轉變**：
從 Spring Boot 3 開始，透過 **Micrometer Observation API**，這三者不再是獨立的 API，而是統一的行為。一個 `@Observed` 或 `Observation` 動作，應同時產生 Metrics (計時/計數) 與 Trace (Span)，並在 Log 中自動帶入 Correlation ID。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 結構化日誌 (Structured Logging)
不要再依賴 Regex 去解析純文字 Log。
*   **Pattern**: 使用 JSON 格式輸出 Log (e.g., Logstash Logback Encoder)。
*   **Why**: 讓 Log 系統 (ELK, Datadog, Loki) 能自動索引欄位，支援像 SQL 一樣的查詢 (e.g., `level="ERROR" AND orderId="123"`).
*   **Implementation**: 在 `logback-spring.xml` 中配置 `LogstashEncoder`。

### 2. 上下文注入 (MDC & Correlation ID)
Log 必須包含「是誰、在哪、做什麼」。
*   **Pattern**: 利用 SLF4J 的 **MDC (Mapped Diagnostic Context)**。
*   **Trace ID**: 確保 Spring Boot Actuator 與 Micrometer Tracing 已啟用，它會自動將 `traceId` 與 `spanId` 注入 MDC。
*   **Custom Context**: 在 Filter 或 Interceptor 層，將 `userId`, `tenantId`, `requestId` 放入 MDC。
*   **Result**: 每一行 Log 都會自動帶上 `[traceId=..., spanId=...]`，讓你能瞬間過濾出單次請求的所有 Log。

### 3. 指標維度化 (Dimensional Metrics)
*   **Pattern**: 使用 **Tags (Labels)** 而不是階層式命名。
*   **Bad**: `metrics.http.status.500.count`
*   **Good**: `http.server.requests` (name) + `status=500`, `uri=/api/orders`, `method=POST` (tags).
*   **Why**: 允許聚合查詢。你可以問「所有 API 的 500 錯誤總和」或「特定 API 的錯誤率」。

### 4. 黃金訊號 (The Four Golden Signals)
設計 Dashboard 時，優先關注以下四類指標：
1.  **Latency**: 請求處理時間 (P95, P99)。
2.  **Traffic**: 流量 (RPS)。
3.  **Errors**: 錯誤率 (HTTP 5xx, Exception count)。
4.  **Saturation**: 飽和度 (Thread pool usage, Memory usage, DB connection pool)。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 基數爆炸 (Cardinality Explosion) 💥
這是使用 Micrometer 最常見的災難性錯誤。
*   **Anti-pattern**: 將「無限增長」的值放入 Metrics 的 Tag 中。
    *   ❌ `registry.counter("orders", "orderId", order.getId())`
    *   ❌ `registry.timer("http.requests", "url", "/api/users/12345")` (未正規化的 URL)
*   **Consequence**: 每個唯一的 Tag 值都會產生一個新的 Time Series。如果放入 User ID 或 UUID，會導致 Prometheus/Datadog 記憶體爆掉或帳單爆炸。
*   **Fix**: Tag 只能是「有限集合」 (e.g., `status`, `region`, `paymentMethod`)。

### 2. Log and Throw (重複紀錄)
*   **Anti-pattern**: 在 catch block 中紀錄 error log，然後又把 exception 拋出去。
*   **Consequence**: 同一個錯誤在 Log 中出現多次，干擾排查，且浪費 I/O。
*   **Fix**: 要嘛處理 (Log and Consume)，要嘛拋出 (Throw only)，由最上層的 Global Exception Handler 統一紀錄。

### 3. 同步寫入 Log 阻塞主執行緒
*   **Anti-pattern**: 在高併發系統中使用預設的 Console Appender 或同步 File Appender。
*   **Consequence**: Disk I/O 變慢會直接卡死 Request processing thread。
*   **Fix**: 使用 **AsyncAppender** (Logback) 讓 Log 寫入非同步化。

### 4. 斷鏈的 Trace (Broken Traces)
*   **Anti-pattern**: 在程式中手動 `new Thread()` 或使用未受 Spring 管理的 Thread Pool。
*   **Consequence**: MDC 和 Trace Context 無法傳遞到子執行緒，導致 Log 中的 Trace ID 消失或斷開。
*   **Fix**: 使用 Spring 的 `ThreadPoolTaskExecutor` 並確保它被 Micrometer Tracing 裝飾 (Spring Boot 自動配置通常會處理，但自定義 Bean 時需注意)。

---

## Checklists & workflows｜檢查清單與流程

### Implementation Checklist (實作檢核)

- [ ] **Log Format**: 生產環境是否已啟用 JSON 格式日誌？
- [ ] **Correlation ID**: 請求是否包含 `traceId` 與 `spanId`？跨服務呼叫 (Feign/RestTemplate) 是否有正確傳遞 Header (B3 或 W3C)？
- [ ] **Async Logging**: 是否已配置 `AsyncAppender` 避免 I/O 阻塞？
- [ ] **PII Masking**: 日誌中是否已針對敏感個資 (Email, Credit Card) 進行脫敏處理？
- [ ] **Metrics Cardinality**: 檢查所有自定義 Metrics 的 Tag，確保沒有高基數資料 (UUID, Timestamp)。
- [ ] **Global Error Handling**: 是否有全域異常處理機制，確保所有未捕獲異常都能被記錄且包含 Stack Trace？

### Troubleshooting Workflow (除錯流程)

1.  **Alerting**: 收到警報 (e.g., "Order Service Latency P99 > 2s")。
2.  **Metrics Analysis**: 查看 Dashboard，確認是整體變慢還是特定 Instance/Endpoint 變慢。
3.  **Tracing**:
    *   在 Tracing 系統 (Zipkin/Jaeger/Tempo) 搜尋慢請求。
    *   查看 Waterfall 圖，找出耗時最長的 Span (是 DB 慢？還是外部 API 慢？)。
    *   複製該請求的 `Trace ID`。
4.  **Log Correlation**:
    *   在 Log 系統中搜尋 `traceId="<copied_id>"`。
    *   查看該次請求的所有 Log，定位具體錯誤訊息或邏輯分支。

---

## Real-world examples｜實戰案例

### 1. Spring Boot 3 配置範例 (Logback + Micrometer)

**`logback-spring.xml` (簡化版 - 生產環境 JSON)**

```xml
<configuration>
    <appender name="JSON_CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder class="net.logstash.logback.encoder.LogstashEncoder">
            <!-- 自動包含 MDC 中的 traceId, spanId -->
            <includeMdcKeyName>traceId</includeMdcKeyName>
            <includeMdcKeyName>spanId</includeMdcKeyName>
        </encoder>
    </appender>
    
    <!-- 非同步包裝 -->
    <appender name="ASYNC_JSON" class="ch.qos.logback.classic.AsyncAppender">
        <appender-ref ref="JSON_CONSOLE" />
        <queueSize>512</queueSize>
        <discardingThreshold>0</discardingThreshold>
    </appender>

    <root level="INFO">
        <appender-ref ref="ASYNC_JSON" />
    </root>
</configuration>
```

### 2. 自定義 Metrics 與 Observation (Service Layer)

在 Spring Boot 3 中，推薦使用 `Observation API` 來同時處理 Metrics 和 Tracing。

```java
@Service
@RequiredArgsConstructor
public class PaymentService {

    private final ObservationRegistry observationRegistry;
    private final MeterRegistry meterRegistry; // 用於純數值統計

    public void processPayment(String orderId, String paymentMethod) {
        // 1. 使用 Observation 記錄執行時間與 Trace
        // 這會自動產生一個 Timer metric: "payment.process"
        // 並產生一個 Span，且在 Scope 內的 Log 會帶有 traceId
        Observation.createNotStarted("payment.process", observationRegistry)
                .lowCardinalityKeyValue("paymentMethod", paymentMethod) // Tag: 有限集合
                .highCardinalityKeyValue("orderId", orderId)            // Tag: 僅用於 Tracing，不進 Metrics (避免基數爆炸)
                .observe(() -> {
                    log.info("Starting payment processing"); // Log 會自動帶有 traceId
                    
                    // 模擬商業邏輯
                    executePaymentLogic();
                    
                    // 2. 使用 Counter 記錄業務次數 (純 Metric)
                    meterRegistry.counter("payment.success", "method", paymentMethod).increment();
                });
    }

    private void executePaymentLogic() {
        // ... logic
    }
}
```

### 3. 常見 Log 輸出對比

**Bad (Text, No Context):**
```text
2023-10-27 10:00:01 ERROR Payment failed for order 12345: Connection timeout
```

**Good (JSON, Structured, Correlated):**
```json
{
  "@timestamp": "2023-10-27T10:00:01.123Z",
  "level": "ERROR",
  "message": "Payment failed",
  "logger_name": "com.example.PaymentService",
  "traceId": "653b8e...a1", 
  "spanId": "b2c...99",
  "orderId": "12345",
  "error_type": "java.net.SocketTimeoutException",
  "stack_trace": "..."
}
```
*註：透過 JSON 結構，我們可以輕鬆統計「過去一小時有多少 SocketTimeoutException」，這在純文字 Log 中很難做到。*