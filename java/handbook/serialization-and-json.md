# 序列化陷阱與 JSON 處理 / Serialization Pitfalls and JSON Processing

## Mental model｜心智模型

序列化是將記憶體中的物件圖 (Object Graph) 轉換為位元組流 (Byte Stream) 或文字 (如 JSON) 的過程，以便於儲存或網路傳輸；反序列化則是其逆過程。
Serialization is the process of converting an in-memory object graph into a byte stream or text (like JSON) for storage or network transmission; deserialization is the reverse process.

在 Java 世界中，你需要建立以下心智模型：
In the Java ecosystem, you need to establish the following mental model:

1. **原生序列化是危險的後門 (Native Serialization is a Dangerous Backdoor)**：實作 `java.io.Serializable` 會繞過類別的建構子 (Constructor)，這意味著你的業務邏輯驗證完全失效。此外，它還帶來了嚴重的反序列化漏洞（如 RCE，遠端程式碼執行）以及脆弱的類別版本相容性問題。
   **Native Serialization is a Dangerous Backdoor**: Implementing `java.io.Serializable` bypasses class constructors, meaning your business logic validation is completely circumvented. Furthermore, it introduces severe deserialization vulnerabilities (like RCE - Remote Code Execution) and fragile class version compatibility issues.
2. **現代序列化是「資料綁定」 (Modern Serialization is "Data Binding")**：現代 Java 開發應將序列化視為資料綁定。我們不再依賴 JVM 底層的魔術，而是使用 Jackson 或 Gson 等框架，透過明確的 DTO (Data Transfer Object) 與 JSON/Protobuf 等中立格式進行對應。
   **Modern Serialization is "Data Binding"**: Modern Java development should treat serialization as data binding. Instead of relying on JVM under-the-hood magic, we use frameworks like Jackson or Gson to map explicit DTOs (Data Transfer Objects) to neutral formats like JSON or Protobuf.
3. **邊界防禦 (Boundary Defense)**：永遠不要信任外部傳入的 JSON 字串。反序列化時，必須限制可實例化的類別型別，避免多型 (Polymorphism) 帶來的安全風險。
   **Boundary Defense**: Never trust incoming JSON strings from external sources. During deserialization, you must restrict the types of classes that can be instantiated to avoid security risks associated with polymorphism.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 將 ObjectMapper 視為 Thread-Safe 的單例 (Treat `ObjectMapper` as a Thread-Safe Singleton)
在 Jackson 中，`ObjectMapper` 的建立成本非常高。一旦配置完成，它是完全執行緒安全的 (Thread-safe)。在真實專案中，應該將其配置為單例 (Singleton) 或交由 Spring 的 IoC 容器管理，並在整個應用程式中共用。
In Jackson, creating an `ObjectMapper` is highly expensive. Once configured, it is completely thread-safe. In real-world projects, it should be configured as a singleton or managed by Spring's IoC container and shared across the entire application.

### 2. 擁抱不可變性與 Java Records (Embrace Immutability and Java Records)
使用 Java 14+ 的 `Record` 作為 DTO。Jackson 完美支援 Record 的反序列化，這強迫資料在反序列化時必須經過 Record 的 Canonical Constructor，從而保證資料的一致性與驗證邏輯的執行。
Use Java 14+ `Record` for DTOs. Jackson perfectly supports deserializing Records, which forces the data to pass through the Record's canonical constructor during deserialization, ensuring data consistency and the execution of validation logic.

### 3. 處理現代日期與時間 API (Handle Modern Date-Time API)
預設情況下，Jackson 無法正確處理 `java.time` (JSR-310) 套件。必須註冊 `JavaTimeModule`，並關閉將日期寫入為時間戳記的預設行為，改用 ISO-8601 標準字串格式。
By default, Jackson cannot handle the `java.time` (JSR-310) package correctly. You must register the `JavaTimeModule` and disable the default behavior of writing dates as timestamps, opting instead for the ISO-8601 standard string format.

### 4. 安全的多型反序列化 (Safe Polymorphic Deserialization)
當需要序列化/反序列化介面或抽象類別時，使用 `@JsonTypeInfo` 和 `@JsonSubTypes` 明確指定允許的子類別，而不是開啟全域的 Default Typing。
When serializing/deserializing interfaces or abstract classes, use `@JsonTypeInfo` and `@JsonSubTypes` to explicitly specify allowed subclasses, rather than enabling global Default Typing.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### ❌ 反模式 1：依賴原生 `java.io.Serializable` 進行快取或持久化 (Relying on Native Serialization for Caching/Persistence)
**問題 (Problem)**：將實作了 `Serializable` 的物件存入 Redis 或資料庫。當類別結構改變（例如新增欄位）且沒有正確維護 `serialVersionUID` 時，會觸發 `InvalidClassException` 導致系統崩潰。
Storing `Serializable` objects in Redis or a database. When the class structure changes (e.g., adding a field) without properly maintaining the `serialVersionUID`, it triggers an `InvalidClassException`, causing the system to crash.
**解法 (Solution)**：快取與持久化一律使用 JSON 或二進位格式 (如 Protobuf/Kryo)。
Always use JSON or binary formats (like Protobuf/Kryo) for caching and persistence.

### ❌ 反模式 2：每次請求都 `new ObjectMapper()` (Creating `new ObjectMapper()` per request)
**問題 (Problem)**：在方法內部實例化 `ObjectMapper`。這會導致嚴重的 CPU 效能損耗與記憶體垃圾產生，因為框架需要重新掃描類別與建立序列化快取。
Instantiating `ObjectMapper` inside a method. This causes severe CPU performance degradation and memory garbage generation because the framework needs to rescan classes and rebuild serialization caches.
**解法 (Solution)**：宣告為 `private static final ObjectMapper MAPPER = new ObjectMapper();` 或注入 Spring 的 `ObjectMapper` Bean。
Declare it as `private static final ObjectMapper MAPPER = new ObjectMapper();` or inject Spring's `ObjectMapper` bean.

### ❌ 反模式 3：未忽略未知屬性 (Failing to Ignore Unknown Properties)
**問題 (Problem)**：當第三方 API 或前端在 JSON 中新增了一個欄位，而你的 DTO 尚未更新時，Jackson 預設會拋出 `UnrecognizedPropertyException`，導致 API 請求失敗。
When a third-party API or frontend adds a new field to the JSON and your DTO hasn't been updated, Jackson throws an `UnrecognizedPropertyException` by default, causing the API request to fail.
**解法 (Solution)**：全域停用 `DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES`。
Globally disable `DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES`.

### ❌ 反模式 4：雙向關聯導致的無限遞迴 (Infinite Recursion from Bidirectional Relationships)
**問題 (Problem)**：JPA 實體 (Entities) 中常見的父子雙向關聯（如 `Order` 包含 `List<Item>`，`Item` 又關聯回 `Order`），在序列化時會觸發 `StackOverflowError`。
Common bidirectional relationships in JPA entities (e.g., `Order` contains `List<Item>`, and `Item` links back to `Order`) will trigger a `StackOverflowError` during serialization.
**解法 (Solution)**：避免直接序列化 JPA Entities，應轉換為 DTO。若必須序列化，使用 `@JsonManagedReference` / `@JsonBackReference` 或 `@JsonIgnore` 切斷迴圈。
Avoid serializing JPA Entities directly; map them to DTOs instead. If you must, use `@JsonManagedReference` / `@JsonBackReference` or `@JsonIgnore` to break the loop.

---

## Checklists & workflows｜檢查清單與流程

### 🛡️ 安全與穩定性檢查 (Security & Stability Checklist)
- [ ] **No Native Serialization**: 專案中是否已禁止使用 `ObjectInputStream` 反序列化不受信任的資料？ (Have you banned `ObjectInputStream` for untrusted data?)
- [ ] **No Default Typing**: Jackson 的 `enableDefaultTyping()` 或 `activateDefaultTyping()` 是否已確認關閉？ (Is Jackson's default typing explicitly disabled to prevent RCE?)
- [ ] **Unknown Properties**: 是否已設定 `FAIL_ON_UNKNOWN_PROPERTIES = false` 以確保向前相容性？ (Is `FAIL_ON_UNKNOWN_PROPERTIES` disabled for forward compatibility?)

### ⚡ 效能檢查 (Performance Checklist)
- [ ] **Singleton Instance**: `ObjectMapper` 或 `Gson` 實例是否為單例且被重複使用？ (Are `ObjectMapper` or `Gson` instances singletons and reused?)
- [ ] **No Pretty Printing in Prod**: 生產環境是否已關閉 JSON 格式化輸出 (`SerializationFeature.INDENT_OUTPUT`) 以節省頻寬與 CPU？ (Is pretty printing disabled in production to save bandwidth and CPU?)

### 🔄 相容性與型別檢查 (Compatibility & Type Checklist)
- [ ] **JSR-310 Module**: 是否已註冊 `JavaTimeModule` 處理 `LocalDate` / `Instant`？ (Is `JavaTimeModule` registered for `LocalDate` / `Instant`?)
- [ ] **Enum Handling**: 列舉 (Enum) 序列化是否使用了 `@JsonValue` 或明確的字串對應，而非依賴脆弱的 `Enum.ordinal()`？ (Are Enums serialized using `@JsonValue` or explicit strings instead of fragile `ordinal()`?)

---

## Real-world examples｜實戰案例

### 案例 1：企業級高可用 ObjectMapper 配置 (Enterprise-Grade ObjectMapper Configuration)

這是在真實專案中，兼顧效能、相容性與現代 Java 特性的 Jackson 配置標準模板。
This is a standard Jackson configuration template used in real-world projects, balancing performance, compatibility, and modern Java features.

```java
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

public class JsonUtils {
    
    // 單例且 Thread-safe 的 ObjectMapper
    // Singleton and thread-safe ObjectMapper
    private static final ObjectMapper MAPPER = new ObjectMapper();

    static {
        // 1. 註冊 Java 8 日期時間模組 (Register Java 8 Date-Time module)
        MAPPER.registerModule(new JavaTimeModule());
        
        // 2. 日期格式化為 ISO-8601 字串，而非時間戳記 (Format dates as ISO-8601 strings, not timestamps)
        MAPPER.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
        
        // 3. 忽略 JSON 中存在但 Java DTO 中沒有的屬性，防止 API 擴充時報錯 
        // (Ignore unknown properties to prevent errors during API expansion)
        MAPPER.disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES);
        
        // 4. 不序列化 Null 值，減少網路頻寬消耗 (Do not serialize null values to save bandwidth)
        MAPPER.setSerializationInclusion(JsonInclude.Include.NON_NULL);
    }

    public static String toJson(Object obj) {
        try {
            return MAPPER.writeValueAsString(obj);
        } catch (Exception e) {
            throw new RuntimeException("JSON serialization failed", e);
        }
    }

    public static <T> T fromJson(String json, Class<T> clazz) {
        try {
            return MAPPER.readValue(json, clazz);
        } catch (Exception e) {
            throw new RuntimeException("JSON deserialization failed", e);
        }
    }
}
```

### 案例 2：結合 Java Record 與 Jackson 進行資料綁定 (Data Binding with Java Records and Jackson)

使用 Record 可以確保反序列化時，依然會執行建構子中的業務驗證邏輯。
Using Records ensures that business validation logic inside the constructor is still executed during deserialization.

```java
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.Objects;

// Java 14+ Record 自動具備不可變性 (Immutability)
public record UserProfile(
    @JsonProperty("user_id") String userId,
    @JsonProperty("email") String email
) {
    // Compact constructor 用於驗證邏輯 (Compact constructor for validation)
    public UserProfile {
        Objects.requireNonNull(userId, "User ID cannot be null");
        if (email == null || !email.contains("@")) {
            throw new IllegalArgumentException("Invalid email format");
        }
    }
}

// 測試反序列化 (Testing Deserialization)
// String json = """{"user_id": "U123", "email": "invalid-email"}""";
// JsonUtils.fromJson(json, UserProfile.class); 
// 將會拋出 IllegalArgumentException (Will throw IllegalArgumentException)
```

### 案例 3：安全的多型 JSON 處理 (Safe Polymorphic JSON Handling)

當 API 需要接收不同類型的事件 (Event) 時，使用 `@JsonTypeInfo` 來安全地處理多型，避免反序列化漏洞。
When an API needs to receive different types of events, use `@JsonTypeInfo` to handle polymorphism safely and avoid deserialization vulnerabilities.

```java
import com.fasterxml.jackson.annotation.JsonSubTypes;
import com.fasterxml.jackson.annotation.JsonTypeInfo;

// 1. 定義型別識別欄位 (Define the type identifier field)
@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME, 
    include = JsonTypeInfo.As.PROPERTY, 
    property = "event_type"
)
// 2. 明確列出允許的子類別，防範 RCE 攻擊 (Explicitly list allowed subclasses to prevent RCE)
@JsonSubTypes({
    @JsonSubTypes.Type(value = ClickEvent.class, name = "CLICK"),
    @JsonSubTypes.Type(value = PurchaseEvent.class, name = "PURCHASE")
})
public interface TrackingEvent {
    // ...
}

public record ClickEvent(String buttonId) implements TrackingEvent {}
public record PurchaseEvent(String orderId, double amount) implements TrackingEvent {}

/*
傳入的 JSON 範例 (Incoming JSON example):
{
  "event_type": "PURCHASE",
  "orderId": "ORD-999",
  "amount": 150.5
}
Jackson 會安全地將其反序列化為 PurchaseEvent 實例。
Jackson will safely deserialize this into a PurchaseEvent instance.
*/
```