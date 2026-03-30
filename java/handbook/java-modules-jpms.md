# Java 模組化系統 (JPMS) 實務與取捨 / Java Platform Module System (JPMS) Practices and Trade-offs

## Mental model｜心智模型

在傳統的 Java 世界裡，Classpath 就像是一個沒有隔間的大型倉庫（大雜燴）。只要類別是 `public`，專案內的任何程式碼都可以隨意存取它，這導致了「內部實作細節被意外依賴」以及「Jar Hell（依賴衝突）」等問題。
In the traditional Java world, the Classpath is like a giant, undivided warehouse (a melting pot). As long as a class is `public`, any code in the project can access it. This leads to issues like "internal implementation details being accidentally relied upon" and "Jar Hell" (dependency conflicts).

**JPMS (Project Jigsaw) 的核心心智模型是「套件級別的防火牆 (Package-level Firewall)」與「明確的依賴圖 (Explicit Dependency Graph)」。**
**The core mental model of JPMS (Project Jigsaw) is a "Package-level Firewall" and an "Explicit Dependency Graph".**

- **封裝性 (Strong Encapsulation)**：在模組化系統中，`public` 不再代表「所有人可見」。只有在 `module-info.java` 中明確 `exports`（匯出）的套件，才能被其他模組看到。
  **Strong Encapsulation**: In the module system, `public` no longer means "visible to everyone." Only packages explicitly `exports`ed in `module-info.java` are visible to other modules.
- **明確依賴 (Reliable Configuration)**：你必須明確宣告你需要哪些模組（`requires`）。JVM 在啟動時會驗證依賴圖，如果缺少模組，程式會直接拒絕啟動（Fail-fast），而不是在執行到一半時拋出 `ClassNotFoundException`。
  **Reliable Configuration**: You must explicitly declare which modules you need (`requires`). The JVM verifies the dependency graph at startup; if a module is missing, it refuses to start (Fail-fast) instead of throwing a `ClassNotFoundException` halfway through execution.

**取捨 (The Trade-off)**：JPMS 帶來了極高的安全性和架構清晰度，但也帶來了極高的遷移成本。對於底層函式庫 (Libraries) 作者來說，JPMS 是必備武器；但對於一般企業級應用（如 Spring Boot 微服務），強行導入 JPMS 的成本往往大於效益，除非你的目標是使用 `jlink` 打造極小化的自訂 JRE。
**The Trade-off**: JPMS brings extremely high security and architectural clarity, but also a very high migration cost. For low-level library authors, JPMS is a must-have weapon; however, for typical enterprise applications (like Spring Boot microservices), the cost of forcing JPMS often outweighs the benefits, unless your goal is to build a minimal custom JRE using `jlink`.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 函式庫開發者的「由下而上」策略 / Bottom-Up Strategy for Library Developers
如果你在開發共用函式庫 (Shared Libraries)，強烈建議提供 `module-info.java`。這能保護你的內部實作（例如 `com.yourlib.internal`）不被外部濫用。
If you are developing shared libraries, it is highly recommended to provide a `module-info.java`. This protects your internal implementations (e.g., `com.yourlib.internal`) from being abused by external users.
- **實務做法 / Practice**: 將 API 介面與實作分離。只 `exports` 包含介面與 DTO 的套件。
  Separate API interfaces from implementations. Only `exports` packages containing interfaces and DTOs.

### 2. 利用 `jlink` 打造微型容器映像檔 / Leveraging `jlink` for Micro Container Images
對於雲端原生 (Cloud-Native) 應用，JPMS 最大的商業價值在於 `jlink`。你可以打包出一個只包含應用程式所需 JDK 模組的自訂 JRE，大幅降低 Docker Image 大小與記憶體佔用。
For cloud-native applications, the biggest business value of JPMS lies in `jlink`. You can bundle a custom JRE containing only the JDK modules your application needs, drastically reducing Docker Image size and memory footprint.
- **實務做法 / Practice**: 即使你的專案依賴了尚未模組化的舊 Jar 包，你仍然可以透過 `jdeps` 分析出專案依賴的 JDK 模組，然後用 `jlink` 裁減 JRE，而應用程式本身依然跑在傳統的 Classpath 上。
  Even if your project relies on non-modularized legacy Jars, you can still use `jdeps` to analyze the required JDK modules, then use `jlink` to strip down the JRE, while running the application itself on the traditional Classpath.

### 3. 使用 `ServiceLoader` 實現鬆耦合 / Decoupling with `ServiceLoader`
JPMS 深度整合了 SPI (Service Provider Interface) 機制。透過 `uses` 和 `provides` 關鍵字，模組可以在不知道具體實作類別的情況下，動態載入服務。
JPMS deeply integrates the SPI (Service Provider Interface) mechanism. Using the `uses` and `provides` keywords, modules can dynamically load services without knowing the concrete implementation classes.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 分裂套件 (Split Packages)
- **踩雷點 / Pitfall**: 在兩個不同的模組（或 Jar 檔）中，存在完全相同的套件名稱（例如 `com.example.utils`）。JPMS 嚴格禁止分裂套件，這會導致編譯或啟動失敗。
  Having the exact same package name (e.g., `com.example.utils`) in two different modules (or Jars). JPMS strictly forbids split packages, which will cause compilation or startup failures.
- **解決方案 / Solution**: 在設計模組時，確保每個模組擁有獨佔的根套件命名空間（例如 `com.example.moduleA.utils` 與 `com.example.moduleB.utils`）。
  When designing modules, ensure each module has an exclusive root package namespace.

### 2. 忘記開放反射權限 (Forgetting to `opens` for Reflection)
- **踩雷點 / Pitfall**: 現代 Java 框架（如 Spring, Hibernate, Jackson, Mockito）重度依賴 Reflection (反射) 來實例化私有類別或讀取私有欄位。如果你的模組只使用了 `exports`，這些框架在執行時會拋出 `InaccessibleObjectException`。
  Modern Java frameworks (like Spring, Hibernate, Jackson, Mockito) heavily rely on Reflection to instantiate private classes or read private fields. If your module only uses `exports`, these frameworks will throw `InaccessibleObjectException` at runtime.
- **解決方案 / Solution**: 使用 `opens` 關鍵字將特定套件開放給特定框架，或者使用 `open module` 開放整個模組的反射權限。
  Use the `opens` keyword to open specific packages to specific frameworks, or use `open module` to open the entire module for reflection.

### 3. 濫用 `requires transitive` (Abusing `requires transitive`)
- **踩雷點 / Pitfall**: 為了貪圖方便，把所有依賴都宣告為 `requires transitive`，導致依賴關係如病毒般蔓延，破壞了模組化的初衷。
  For convenience, declaring all dependencies as `requires transitive`, causing dependencies to spread like a virus and destroying the original purpose of modularization.
- **解決方案 / Solution**: 只有當你的模組 API（例如 public 方法的回傳型別）直接暴露了另一個模組的型別時，才使用 `requires transitive`。否則，請使用單純的 `requires`。
  Only use `requires transitive` when your module's API (e.g., return types of public methods) directly exposes types from another module. Otherwise, use a simple `requires`.

---

## Checklists & workflows｜檢查清單與流程

### 決策樹：我應該在專案中導入 JPMS 嗎？ / Decision Tree: Should I adopt JPMS?

- [ ] **這是一個供他人使用的 Library 嗎？ (Is this a shared Library?)**
  - 👉 **Yes**: 強烈建議加入 `module-info.java`。 (Highly recommended to add `module-info.java`.)
- [ ] **這是一個 Spring Boot / 企業級 Web 應用嗎？ (Is this a Spring Boot / Enterprise Web App?)**
  - 👉 **Yes**: 評估依賴。如果依賴了大量老舊、未模組化的第三方庫，**建議保持現狀（使用 Classpath）**，避免陷入依賴地獄。 (Evaluate dependencies. If relying on many legacy, non-modular third-party libraries, **it's recommended to stay on the Classpath** to avoid dependency hell.)
- [ ] **你需要極致的啟動速度、極小的 Docker Image 嗎？ (Do you need extreme startup speed and a tiny Docker Image?)**
  - 👉 **Yes**: 考慮使用 `jlink` 裁減 JRE，或進一步轉向 GraalVM Native Image。 (Consider using `jlink` to tailor the JRE, or move towards GraalVM Native Image.)

### 模組化遷移檢查清單 / Modularization Migration Checklist

- [ ] **依賴盤點 (Dependency Audit)**: 執行 `jdeps --module-path <libs> -s <your-jar>` 檢查現有依賴是否相容。 / Run `jdeps` to check if existing dependencies are compatible.
- [ ] **消除分裂套件 (Eliminate Split Packages)**: 確保專案內沒有跨模組的同名套件。 / Ensure no identically named packages exist across modules.
- [ ] **定義 API 邊界 (Define API Boundaries)**: 決定哪些套件該 `exports`，哪些該隱藏。 / Decide which packages to `exports` and which to hide.
- [ ] **處理反射 (Handle Reflection)**: 針對 JPA Entities、JSON DTOs 或 Spring Controllers，在 `module-info.java` 中加入 `opens`。 / Add `opens` in `module-info.java` for JPA Entities, JSON DTOs, or Spring Controllers.

---

## Real-world examples｜實戰案例

以下是一個典型的「介面與實作分離」的真實專案結構，展示如何利用 JPMS 隱藏實作細節，並透過 ServiceLoader 進行解耦。
Below is a typical real-world project structure demonstrating "separation of interface and implementation," showing how to use JPMS to hide implementation details and decouple via ServiceLoader.

### 專案結構 / Project Structure
```text
payment-system/
 ├── payment.api/          (模組 A: 定義介面 / Defines interfaces)
 ├── payment.stripe/       (模組 B: Stripe 實作 / Stripe implementation)
 └── payment.app/          (模組 C: 消費者應用 / Consumer application)
```

### 1. API 模組 (`payment.api/module-info.java`)
只匯出介面，不包含任何實作。
Exports only the interface, containing no implementation.
```java
module payment.api {
    // 讓其他模組可以看到 PaymentProcessor 介面
    // Allows other modules to see the PaymentProcessor interface
    exports com.example.payment.api;
}
```

### 2. 實作模組 (`payment.stripe/module-info.java`)
依賴 API 模組，但**不匯出**自己的實作套件，而是透過 `provides` 註冊服務。
Requires the API module, but **does not export** its own implementation package. Instead, it registers the service via `provides`.
```java
module payment.stripe {
    requires payment.api;
    
    // 依賴第三方 HTTP 客戶端 (假設為自動模組或已模組化)
    // Requires a third-party HTTP client
    requires java.net.http; 

    // 關鍵：不 exports com.example.payment.stripe.impl
    // 而是宣告提供 PaymentProcessor 的實作
    // Key: Do not export the impl package.
    // Instead, declare that it provides the PaymentProcessor implementation.
    provides com.example.payment.api.PaymentProcessor 
        with com.example.payment.stripe.impl.StripePaymentProcessor;
}
```

### 3. 應用程式模組 (`payment.app/module-info.java`)
宣告需要使用該服務，並開放反射權限給依賴注入框架（如 Spring）。
Declares the use of the service and opens reflection access for DI frameworks (like Spring).
```java
module payment.app {
    requires payment.api;
    
    // 宣告會透過 ServiceLoader 尋找此介面的實作
    // Declares that it will look for implementations of this interface via ServiceLoader
    uses com.example.payment.api.PaymentProcessor;

    // 如果使用 Spring Boot，需要開放套件給 Spring 進行反射與依賴注入
    // If using Spring Boot, open the package to Spring for reflection and DI
    requires spring.context;
    opens com.example.payment.app to spring.core, spring.beans, spring.context;
}
```

### 4. 應用程式呼叫端 / Application Caller
在程式碼中，我們完全看不到 `StripePaymentProcessor` 這個類別，達到了完美的解耦。
In the code, we cannot see the `StripePaymentProcessor` class at all, achieving perfect decoupling.
```java
// 在 payment.app 模組中 / Inside payment.app module
import com.example.payment.api.PaymentProcessor;
import java.util.ServiceLoader;

public class App {
    public static void main(String[] args) {
        // 透過 ServiceLoader 動態載入實作 (JPMS 會根據 module-info 自動匹配)
        // Dynamically load implementations via ServiceLoader (JPMS matches automatically based on module-info)
        Iterable<PaymentProcessor> processors = ServiceLoader.load(PaymentProcessor.class);
        
        for (PaymentProcessor processor : processors) {
            processor.process(100.0); // 執行 Stripe 實作 / Executes Stripe implementation
        }
    }
}
```