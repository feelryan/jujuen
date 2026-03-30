# 現代 HTTP Client 與網路通訊 / Modern HTTP Client and Networking

## Mental model｜心智模型

Java 11 引入的 `java.net.http.HttpClient` 是一個現代化、非阻塞且支援 HTTP/2 的內建網路客戶端。在真實專案中，請拋棄老舊的 `HttpURLConnection`，並將新的 `HttpClient` 視為你的首選。
Introduced in Java 11, `java.net.http.HttpClient` is a modern, non-blocking, HTTP/2-capable built-in network client. In real-world projects, discard the legacy `HttpURLConnection` and treat the new `HttpClient` as your default choice.

要掌握這個 API，請建立以下的心智模型：
To master this API, build the following mental model:

1. **`HttpClient` 是連線池管理者 (The Connection Pool Manager)**：它不僅僅是一個發送器，它內部維護了 TCP 連線池、執行緒池與 SSL 上下文。它是**執行緒安全 (Thread-safe)** 且設計為**被重複使用 (Reusable)** 的。
2. **`HttpRequest` 是不可變的定義 (The Immutable Definition)**：使用 Builder 模式建立。一旦建立，它就是不可變的（Immutable），這意味著同一個 Request 實例可以被多次發送。
3. **`HttpResponse` 與 `BodyHandler` (The Result and the Handler)**：`HttpClient` 不會預設將整個回應載入記憶體。你必須提供一個 `BodyHandler` 來告訴它如何處理位元組流（例如轉成字串、存成檔案或作為 InputStream 串流處理）。
4. **非同步基於 `CompletableFuture` (Async is CompletableFuture-based)**：所有的非同步操作 (`sendAsync`) 都回傳 `CompletableFuture<HttpResponse>`，讓你完美整合現代 Java 的非同步程式設計模式。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 共用單一 HttpClient 實例 / Reuse a Singleton HttpClient
永遠不要在每次發送請求時建立新的 `HttpClient`。你應該在應用程式啟動時配置好一個共用的 Client 實例（例如宣告為 `static final` 或註冊為 Spring Bean）。
Never create a new `HttpClient` for every request. You should configure a shared Client instance at application startup (e.g., declared as `static final` or registered as a Spring Bean).

### 2. 全面設定超時機制 / Comprehensive Timeout Configuration
網路是不可靠的。你必須在兩個層級設定超時：**連線超時 (Connect Timeout)** 與 **請求超時 (Request Timeout)**。
The network is unreliable. You must set timeouts at two levels: **Connect Timeout** (on the Client) and **Request Timeout** (on the Request).

### 3. 根據 Payload 大小選擇 BodyHandler / Choose BodyHandler based on Payload Size
- 小型 JSON/Text：使用 `BodyHandlers.ofString()`。
- 下載大型檔案：使用 `BodyHandlers.ofFile()`，直接將串流寫入磁碟，避免 OOM (Out of Memory)。
- 串流處理：使用 `BodyHandlers.ofInputStream()`。
- Small JSON/Text: Use `BodyHandlers.ofString()`.
- Large file downloads: Use `BodyHandlers.ofFile()` to stream directly to disk and avoid OOM.
- Stream processing: Use `BodyHandlers.ofInputStream()`.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### ❌ 忽略 HTTP 狀態碼 (Ignoring HTTP Status Codes)
**問題 (The Problem)**：與某些高階函式庫不同，當伺服器回傳 `404 Not Found` 或 `500 Internal Server Error` 時，`HttpClient` **不會拋出異常 (Does NOT throw exceptions)**。它會正常回傳一個 `HttpResponse`。
**後果 (Consequence)**：如果你直接呼叫 `response.body()` 而不檢查狀態碼，你的程式可能會解析錯誤的 HTML 錯誤頁面，導致 `JsonParseException`。
**解法 (Solution)**：永遠在處理 Body 之前檢查 `response.statusCode()`。

### ❌ 每次請求都建立新的 HttpClient (Creating a new HttpClient per request)
**問題 (The Problem)**：在方法內部 `HttpClient.newHttpClient()`。
**後果 (Consequence)**：這會導致連線池無法被重複使用，產生大量的短命 TCP 連線（TIME_WAIT 狀態），最終耗盡系統的 Socket 資源（Port exhaustion）。

### ❌ 在非同步回呼中執行阻塞操作 (Blocking inside async callbacks)
**問題 (The Problem)**：在 `client.sendAsync(...).thenApply(resp -> doHeavyDbQuery(resp))` 中執行耗時的 I/O 或 CPU 密集操作。
**後果 (Consequence)**：這會阻塞 `HttpClient` 內部的執行緒池，導致後續的網路請求全部卡住。
**解法 (Solution)**：如果要在回呼中執行阻塞操作，請使用 `.thenApplyAsync(..., customExecutor)` 將任務轉移到你自己的執行緒池。

---

## Checklists & workflows｜檢查清單與流程

在發佈使用 `HttpClient` 的程式碼前，請確認：
Before shipping code that uses `HttpClient`, verify the following:

- [ ] **Singleton Check**: `HttpClient` 實例是否被宣告為單例並重複使用？ (Is the `HttpClient` instance a singleton and reused?)
- [ ] **Timeout Check**: 是否在 `HttpClient.Builder` 設定了 `connectTimeout`？是否在 `HttpRequest.Builder` 設定了 `timeout`？ (Are both connect and request timeouts configured?)
- [ ] **Status Code Check**: 程式碼是否明確驗證了 `response.statusCode() >= 200 && response.statusCode() < 300`？ (Is the status code explicitly validated?)
- [ ] **Memory Check**: 如果預期回應的 Body 很大（例如超過數 MB），是否使用了 `ofFile` 或 `ofInputStream` 而不是 `ofString`？ (Are you avoiding `ofString` for large payloads to prevent OOM?)
- [ ] **Thread Check (Async only)**: 是否確保了 `CompletableFuture` 的鏈式呼叫中沒有 Thread-blocking 的操作？ (Are you sure there are no blocking operations within the async chain?)

---

## Real-world examples｜實戰案例

以下是一個真實世界中常見的非同步 JSON API 請求範例，包含了超時控制、狀態碼檢查與 JSON 解析（搭配 Jackson）。
Below is a common real-world example of an asynchronous JSON API request, including timeout control, status code checking, and JSON parsing (using Jackson).

```java
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.concurrent.CompletableFuture;
import com.fasterxml.jackson.databind.ObjectMapper;

public class ApiClient {

    // 1. 共用 HttpClient 實例 (Reuse HttpClient instance)
    // 設定 10 秒連線超時，並優先使用 HTTP/2 (Set 10s connect timeout, prefer HTTP/2)
    private static final HttpClient HTTP_CLIENT = HttpClient.newBuilder()
            .version(HttpClient.Version.HTTP_2)
            .connectTimeout(Duration.ofSeconds(10))
            .build();

    private static final ObjectMapper JSON_MAPPER = new ObjectMapper();

    /**
     * 非同步獲取使用者資料 (Fetch user data asynchronously)
     */
    public CompletableFuture<User> fetchUserAsync(String userId) {
        // 2. 建立不可變的 HttpRequest (Create immutable HttpRequest)
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("https://api.example.com/users/" + userId))
                .header("Accept", "application/json")
                .timeout(Duration.ofSeconds(5)) // 請求超時 (Request timeout)
                .GET()
                .build();

        // 3. 發送非同步請求 (Send async request)
        return HTTP_CLIENT.sendAsync(request, HttpResponse.BodyHandlers.ofString())
                .thenApply(this::verifyResponse) // 4. 檢查狀態碼 (Check status code)
                .thenApply(HttpResponse::body)
                .thenApply(this::parseUserJson); // 5. 解析 JSON (Parse JSON)
    }

    /**
     * 驗證 HTTP 狀態碼 (Verify HTTP status code)
     */
    private HttpResponse<String> verifyResponse(HttpResponse<String> response) {
        int statusCode = response.statusCode();
        if (statusCode >= 200 && statusCode < 300) {
            return response;
        }
        // 遇到 4xx 或 5xx 時主動拋出異常 (Explicitly throw exception on 4xx/5xx)
        throw new RuntimeException("API Request failed with status: " + statusCode 
                                   + ", body: " + response.body());
    }

    /**
     * 將 JSON 字串轉為 Java 物件 (Convert JSON string to Java object)
     */
    private User parseUserJson(String jsonBody) {
        try {
            return JSON_MAPPER.readValue(jsonBody, User.class);
        } catch (Exception e) {
            throw new RuntimeException("Failed to parse JSON response", e);
        }
    }
    
    // Dummy Record for example
    public record User(String id, String name, String email) {}
}
```

### WebSocket 實戰補充 / WebSocket Quick Note
`HttpClient` 也內建了對 WebSocket 的支援。你可以透過 `HttpClient.newWebSocketBuilder()` 來建立長連線。
`HttpClient` also has built-in support for WebSockets. You can establish persistent connections using `HttpClient.newWebSocketBuilder()`.

```java
// 建立 WebSocket 連線 (Establish WebSocket connection)
CompletableFuture<WebSocket> wsFuture = HTTP_CLIENT.newWebSocketBuilder()
    .buildAsync(URI.create("wss://chat.example.com"), new WebSocket.Listener() {
        @Override
        public void onOpen(WebSocket webSocket) {
            System.out.println("Connected!");
            webSocket.request(1); // 請求接收 1 則訊息 (Request 1 message)
        }

        @Override
        public CompletionStage<?> onText(WebSocket webSocket, CharSequence data, boolean last) {
            System.out.println("Received: " + data);
            webSocket.request(1); // 處理完後請求下一則 (Request next after processing)
            return null;
        }
    });
```
*注意：WebSocket Listener 是基於 Reactive Streams 規範（Backpressure），你必須手動呼叫 `webSocket.request(n)` 來告訴 Client 你準備好接收多少筆後續訊息。*
*Note: The WebSocket Listener is based on Reactive Streams (Backpressure). You must manually call `webSocket.request(n)` to tell the Client how many subsequent messages you are ready to receive.*