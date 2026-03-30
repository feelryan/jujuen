# 現代日期與時間 API 實戰 / Modern Date-Time API in Practice

## Mental model｜心智模型

在處理日期與時間時，最常見的錯誤來自於混淆了「機器時間」與「人類時間」。`java.time` 套件（JSR-310）的核心設計理念就是將這兩者嚴格區分。
The most common mistakes in date and time handling stem from confusing "Machine Time" with "Human Time". The core design philosophy of the `java.time` package (JSR-310) is to strictly separate the two.

1. **Machine Time (機器時間) - `Instant`**
   - 它是時間線上的一個絕對點（自 1970-01-01T00:00:00Z 以來的奈秒數）。它**沒有時區概念**，全宇宙統一。
   - It represents an absolute point on the timeline (nanoseconds since the Unix epoch). It has **no concept of timezones** and is universally consistent.
   - **Use case:** 記錄日誌 (Logging)、資料庫的建立/更新時間 (Audit timestamps)、計算經過時間。

2. **Human Time (人類時間) - `LocalDateTime` / `ZonedDateTime` / `OffsetDateTime`**
   - **`LocalDateTime`**: 只是日曆上的一個字串（例如「2023年10月1日早上9點」）。在沒有附加上時區之前，它**不代表任何具體的時間點**。
   - **`LocalDateTime`**: Just a string on a calendar (e.g., "Oct 1, 2023, 9:00 AM"). Without a timezone, it **does not represent a specific moment in time**.
   - **`OffsetDateTime`**: 帶有與 UTC 的固定偏移量（如 `+08:00`）。適合用於 API 傳輸與資料庫儲存。
   - **`OffsetDateTime`**: Includes a fixed offset from UTC (e.g., `+08:00`). Ideal for API payloads and database storage.
   - **`ZonedDateTime`**: 包含了完整的時區規則（如 `Europe/Paris`），能處理日光節約時間 (DST, Daylight Saving Time) 的複雜變化。
   - **`ZonedDateTime`**: Contains full timezone rules (e.g., `Europe/Paris`), capable of handling the complexities of Daylight Saving Time (DST).

---

## Patterns & best practices｜常見模式與最佳實務

- **Store UTC, Display Local (儲存 UTC，顯示在地時間)**
  - 系統內部（資料庫、後端邏輯、API 傳輸）永遠使用 UTC（`Instant` 或 `OffsetDateTime`）。只有在最邊緣的 UI 層或產生報表時，才轉換為使用者的當地時間。
  - Always use UTC (`Instant` or `OffsetDateTime`) internally (databases, backend logic, API transfers). Only convert to the user's local time at the very edge (UI layer or report generation).

- **Use `Clock` for Dependency Injection (使用 `Clock` 進行依賴注入)**
  - 永遠不要在商業邏輯中直接呼叫 `LocalDateTime.now()`，這會讓程式碼無法進行單元測試。請注入 `java.time.Clock`。
  - Never call `LocalDateTime.now()` directly in business logic, as it makes the code untestable. Inject `java.time.Clock` instead.

- **Prefer `OffsetDateTime` over `ZonedDateTime` for APIs and DBs (API 與資料庫優先使用 `OffsetDateTime`)**
  - 資料庫與 JSON 序列化（如 ISO-8601）對固定偏移量 (`+08:00`) 的支援度遠好於具體時區字串 (`Asia/Taipei`)。將 `ZonedDateTime` 留在需要計算 DST 的商業邏輯層。
  - Databases and JSON serialization (like ISO-8601) support fixed offsets (`+08:00`) much better than specific timezone strings (`Asia/Taipei`). Keep `ZonedDateTime` in the business logic layer where DST calculations are needed.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

- **Anti-pattern: Using `LocalDateTime` to represent an exact moment (使用 `LocalDateTime` 來代表精確時間)**
  - **後果 (Consequence)**: 如果你的伺服器從台北搬到倫敦，或者部署在雲端（預設為 UTC），所有時間都會錯亂。
  - **修正 (Fix)**: 如果你要記錄「事件發生的當下」，請使用 `Instant.now()`。

- **Pitfall: Implicit System Timezone (隱式依賴系統時區)**
  - **錯誤寫法 (Wrong)**: `LocalDate.now()` 或 `ZonedDateTime.now()`。這會依賴 JVM 的預設時區。
  - **正確寫法 (Right)**: `LocalDate.now(ZoneId.of("UTC"))` 或 `LocalDate.now(clock)`。永遠明確指定時區。

- **Pitfall: DST Arithmetic Errors (日光節約時間的計算錯誤)**
  - 在有 DST 的時區（如紐約），「加一天」和「加 24 小時」是不一樣的！
  - In DST-observing zones (like New York), "adding 1 day" and "adding 24 hours" are NOT the same!
  - `zonedDateTime.plusDays(1)`: 保持相同的當地時間（例如 10:00 還是 10:00），底層的絕對時間可能會增加 23 或 25 小時。
  - `zonedDateTime.plusHours(24)`: 絕對時間精準增加 24 小時，但當地時間可能會因為跨越 DST 轉換點而變成 09:00 或 11:00。

---

## Checklists & workflows｜檢查清單與流程

- [ ] **Database Mapping (資料庫映射)**: 我已經確認資料庫欄位類型正確。例如 PostgreSQL 使用 `TIMESTAMP WITH TIME ZONE`，並在 Java 實體中使用 `OffsetDateTime`。 / I have verified DB column types. e.g., using `TIMESTAMP WITH TIME ZONE` in PostgreSQL mapped to `OffsetDateTime` in Java.
- [ ] **JSON Serialization (JSON 序列化)**: 我已經在 Jackson 中註冊了 `JavaTimeModule`，並且禁用了 `WRITE_DATES_AS_TIMESTAMPS`，確保時間以 ISO-8601 字串格式輸出。 / I have registered `JavaTimeModule` in Jackson and disabled `WRITE_DATES_AS_TIMESTAMPS` to ensure ISO-8601 string output.
- [ ] **Testability (可測試性)**: 所有的 `now()` 呼叫都是透過注入的 `Clock` 實例取得，且單元測試中使用了 `Clock.fixed()`。 / All `now()` calls use an injected `Clock` instance, and `Clock.fixed()` is used in unit tests.
- [ ] **Legacy Code Boundaries (遺留程式碼邊界)**: 當必須與舊 API 互動時，我使用了 `Date.from(instant)` 和 `date.toInstant()` 進行轉換，而不是在系統中混用新舊 API。 / When interacting with legacy APIs, I use `Date.from(instant)` and `date.toInstant()` for conversion, avoiding mixing old and new APIs in the system.

---

## Real-world examples｜實戰案例

### 1. Testable Time Service / 可測試的時間服務

使用 `Clock` 讓時間依賴變得可控。
Using `Clock` to make time dependencies controllable.

```java
import java.time.Clock;
import java.time.Instant;
import org.springframework.stereotype.Service;

@Service
public class OrderService {
    
    private final Clock clock;

    // 透過建構子注入 Clock / Inject Clock via constructor
    public OrderService(Clock clock) {
        this.clock = clock;
    }

    public Order createOrder() {
        Order order = new Order();
        // 永遠不要用 Instant.now()，改用 Instant.now(clock)
        // Never use Instant.now() directly, use Instant.now(clock)
        order.setCreatedAt(Instant.now(clock));
        return order;
    }
}

// --- Unit Test ---
// 測試時可以凍結時間 / Freeze time during testing
Clock fixedClock = Clock.fixed(
    Instant.parse("2023-10-01T10:00:00Z"), 
    ZoneId.of("UTC")
);
OrderService service = new OrderService(fixedClock);
```

### 2. Handling Future Events with DST / 處理跨時區與 DST 的未來事件

假設一個紐約的使用者要預約下個月的會議，你必須儲存 `ZonedDateTime` 的資訊，以防 DST 規則變更。
Suppose a user in New York schedules a meeting for next month. You must handle timezone rules carefully in case of DST transitions.

```java
import java.time.*;

public class MeetingScheduler {
    
    public void scheduleMeeting(LocalDateTime localMeetingTime, ZoneId userZone) {
        // 1. 將使用者的本地時間與其時區結合 (處理 DST)
        // 1. Combine local time with user's zone (handles DST)
        ZonedDateTime zdt = ZonedDateTime.of(localMeetingTime, userZone);
        
        // 2. 轉換為 Instant 以便存入資料庫 (機器時間)
        // 2. Convert to Instant for database storage (Machine time)
        Instant dbTimestamp = zdt.toInstant();
        
        // 3. 儲存時，同時保留原始時區，以便未來重新計算
        // 3. Save the original ZoneId as well, in case we need to recalculate
        String dbZone = userZone.getId(); 
        
        saveToDatabase(dbTimestamp, dbZone);
    }
}
```

### 3. Spring Boot / Jackson Configuration / Spring Boot 與 Jackson 配置

確保 API 輸出標準的 ISO-8601 格式，而不是難以閱讀的陣列或時間戳記。
Ensure APIs output standard ISO-8601 formats instead of unreadable arrays or timestamps.

```java
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class JacksonConfig {

    @Bean
    public ObjectMapper objectMapper() {
        ObjectMapper mapper = new ObjectMapper();
        // 註冊 java.time 模組 / Register java.time module
        mapper.registerModule(new JavaTimeModule());
        // 關閉將時間寫為 Timestamp (數字) 的預設行為，強制輸出 ISO-8601 字串
        // Disable writing dates as timestamps to force ISO-8601 string output
        mapper.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
        return mapper;
    }
}

// Output example: "2023-10-25T14:30:00+08:00"
```