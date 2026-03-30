# JVM 架構與類別載入機制 (Classloading) / JVM Architecture and Classloading

## Mental model｜心智模型

**將 JVM 視為應用程式的專屬作業系統 / Treat the JVM as a dedicated OS for your application**

在實戰中，我們不需要死背 JVM 規範，但必須建立精確的心智模型：JVM 就像一個微型作業系統，負責分配記憶體（Memory Areas）與載入執行檔（Classloading）。
In practice, you don't need to memorize the JVM specification, but you must build an accurate mental model: the JVM is like a micro-operating system responsible for allocating memory (Memory Areas) and loading executables (Classloading).

1. **記憶體劃分 (Memory Architecture):**
   - **Heap (堆積):** 這是「共享的資料倉庫」。所有物件實例都在這裡建立與消亡，這是 Garbage Collection (GC) 的主要戰場。
     *Heap is the "shared data warehouse". All object instances are born and die here; this is the main battlefield for Garbage Collection (GC).*
   - **Thread Stack (執行緒堆疊):** 這是「個人的工作台」。每個執行緒獨享，存放區域變數與方法呼叫進度。StackOverflowError 通常是因為遞迴太深，而不是記憶體不夠。
     *Stack is the "personal workbench". Exclusive to each thread, storing local variables and method call frames. `StackOverflowError` usually means recursion went too deep, not a lack of overall memory.*
   - **Metaspace (元空間):** 這是「設計圖檔案室」。存放類別定義 (Class metadata)、方法資訊等。它使用 Native Memory，如果動態生成太多類別（如大量使用 CGLib/反射），會導致這裡爆滿。
     *Metaspace is the "blueprint archive". It stores class definitions and method info. It uses Native Memory. If you dynamically generate too many classes (e.g., heavy use of CGLib/reflection), this area will overflow.*

2. **雙親委派模型 (Parent-Delegation Model):**
   - 想像這是一個「有事優先找老闆」的企業層級架構。當你需要載入一個類別時，ClassLoader 會先問它的 Parent 能不能載入。只有當 Parent 找不到時，自己才會嘗試載入。
     *Imagine a corporate hierarchy where "always ask the boss first" is the rule. When a class needs to be loaded, the ClassLoader asks its Parent first. It only tries to load the class itself if the Parent cannot find it.*
   - **為什麼要這樣？(Why?)** 為了安全與唯一性。確保核心類別（如 `java.lang.String`）永遠由 Bootstrap ClassLoader 載入，防止駭客偽造核心 API。
     *For security and uniqueness. It ensures core classes (like `java.lang.String`) are always loaded by the Bootstrap ClassLoader, preventing hackers from spoofing core APIs.*

---

## Patterns & best practices｜常見模式與最佳實務

- **使用 Thread Context ClassLoader (TCCL) 解決 SPI 困境 / Use TCCL to solve the SPI dilemma**
  Java 核心 API（如 JDBC `java.sql.DriverManager`）由 Bootstrap ClassLoader 載入，但具體的資料庫驅動程式（如 MySQL Driver）存在於使用者的 Classpath 中。Bootstrap 看不到使用者的 Classpath。最佳實務是透過 `Thread.currentThread().getContextClassLoader()` 來「反向」獲取應用程式層級的類別。
  *Core Java APIs (like JDBC) are loaded by the Bootstrap ClassLoader, but specific drivers (like MySQL Driver) are in the user's classpath, which Bootstrap cannot see. The best practice is to use `Thread.currentThread().getContextClassLoader()` to "reversely" access application-level classes.*

- **自訂 ClassLoader 實現模組隔離 / Custom ClassLoaders for Module Isolation**
  在開發外掛系統 (Plugin systems) 或 Web 容器 (如 Tomcat) 時，不同的外掛可能依賴同一個套件的不同版本（例如 Guava 18 與 Guava 30）。最佳做法是為每個外掛實例化一個獨立的 Custom ClassLoader，打破雙親委派，優先從外掛目錄載入類別，實現依賴隔離。
  *When developing plugin systems or Web containers (like Tomcat), different plugins might depend on different versions of the same library (e.g., Guava 18 vs. 30). The best practice is to instantiate a separate Custom ClassLoader for each plugin, breaking parent delegation to load classes from the plugin directory first, achieving dependency isolation.*

- **明確限制 Metaspace 大小 / Explicitly limit Metaspace size**
  在容器化 (Docker/K8s) 環境中，永遠要設定 `-XX:MaxMetaspaceSize`。預設情況下 Metaspace 是無上限的，如果發生 ClassLoader 洩漏，會吃光機器的實體記憶體，導致整個容器被 OOM Killer 砍掉。
  *In containerized environments (Docker/K8s), always set `-XX:MaxMetaspaceSize`. By default, Metaspace is unbounded. If a ClassLoader leak occurs, it will consume all physical memory, causing the OOM Killer to terminate the entire container.*

---

## Anti-patterns & pitfalls｜反模式與踩雷點

- **混淆 ClassNotFoundException 與 NoClassDefFoundError / Confusing CNFE and NCDFE**
  - **`ClassNotFoundException`**: 這是一個 `Exception`。通常發生在執行期使用反射 (`Class.forName()`) 動態載入類別，但 Classpath 裡真的沒有這個類別。
    *This is an `Exception`. It usually happens during runtime dynamic loading (e.g., `Class.forName()`), and the class is genuinely missing from the Classpath.*
  - **`NoClassDefFoundError`**: 這是一個 `Error`（致命錯誤）。代表編譯時這個類別還在，但執行期 JVM 試圖連結 (Link) 該類別時卻找不到了（通常是因為依賴衝突、或是靜態初始化區塊 `static {}` 拋出異常導致類別初始化失敗）。
    *This is an `Error` (fatal). It means the class was present during compilation, but when the JVM tried to link it at runtime, it was gone (usually due to dependency conflicts, or a static initializer block `static {}` throwing an exception causing initialization to fail).*

- **ClassLoader 導致的記憶體洩漏 (Metaspace OOM) / ClassLoader-induced Memory Leaks**
  在熱部署 (Hot-deploy) 場景中，如果應用程式被卸載，但某個長生命週期的物件（如 ThreadLocal 或靜態變數）仍然持有對舊版類別實例的參照，這會導致該類別的 ClassLoader 無法被 GC 回收。最終 Metaspace 會被塞滿舊版本的類別定義。
  *In hot-deploy scenarios, if an app is undeployed but a long-lived object (like ThreadLocal or static variables) still holds a reference to an instance of an old class, the ClassLoader for that class cannot be garbage collected. Eventually, Metaspace fills up with old class definitions.*

- **強行覆寫 java.* 套件 / Forcibly overriding `java.*` packages**
  新手有時會嘗試自己寫一個 `java.lang.String` 來做測試。由於雙親委派機制，JVM 永遠會載入官方的 String。如果你寫自訂 ClassLoader 強行載入，JVM 會拋出 `SecurityException: Prohibited package name`。
  *Juniors sometimes try to write their own `java.lang.String` for testing. Due to parent delegation, the JVM will always load the official String. If you write a custom ClassLoader to force it, the JVM will throw a `SecurityException: Prohibited package name`.*

---

## Checklists & workflows｜檢查清單與流程

當遇到類別載入或 JVM 記憶體異常時，請依照以下流程排查：
When encountering classloading or JVM memory anomalies, follow this workflow:

- [ ] **確認異常類型 (Identify the Exception):**
  - 是 `OutOfMemoryError: Java heap space` 還是 `OutOfMemoryError: Metaspace`？（前者查程式碼邏輯/大物件，後者查反射/動態代理/熱部署）。
    *Is it Heap space or Metaspace? (For Heap, check code logic/large objects; for Metaspace, check reflection/dynamic proxies/hot-deployments).*
- [ ] **排查 NoClassDefFoundError (Troubleshoot NCDFE):**
  - 檢查 Maven/Gradle 依賴樹 (`mvn dependency:tree`)，是否有同一個 Library 的多個版本衝突 (Dependency Hell)？
    *Check the dependency tree. Are there multiple conflicting versions of the same library?*
  - 檢查該類別是否有複雜的 `static` 變數初始化，且初始化過程中可能拋出隱藏的異常？
    *Does the class have complex `static` variable initialization that might be throwing hidden exceptions?*
- [ ] **檢查 ClassLoader 隔離 (Check ClassLoader Isolation):**
  - 如果在 Tomcat/Spring Boot 等容器中發生 `ClassCastException`（A 不能轉型為 A），檢查這兩個 A 是否由不同的 ClassLoader 載入？（在 JVM 中，類別的唯一識別是 `ClassLoader + ClassName`）。
    *If `ClassCastException` occurs (A cannot be cast to A), were they loaded by different ClassLoaders? (In the JVM, a class's unique identity is `ClassLoader + ClassName`).*
- [ ] **檢查啟動參數 (Review Startup Flags):**
  - 是否配置了 `-XX:+HeapDumpOnOutOfMemoryError`？這在實戰中是必須的，能讓你在 OOM 發生後留下證據 (Heap Dump)。
    *Is `-XX:+HeapDumpOnOutOfMemoryError` configured? This is mandatory in production to leave evidence (Heap Dump) after an OOM.*

---

## Real-world examples｜實戰案例

### 案例 1：破壞雙親委派機制來實現外掛隔離 / Breaking Parent Delegation for Plugin Isolation

在標準的雙親委派中，我們會覆寫 `findClass()`。但如果我們要讓外掛的 JAR 檔優先於系統的 JAR 檔（例如 Tomcat 的 WebAppClassLoader），我們必須覆寫 `loadClass()` 的邏輯。
*In standard parent delegation, we override `findClass()`. But if we want plugin JARs to take precedence over system JARs (like Tomcat's WebAppClassLoader), we must override the `loadClass()` logic.*

```java
public class PluginClassLoader extends URLClassLoader {
    
    public PluginClassLoader(URL[] urls, ClassLoader parent) {
        super(urls, parent);
    }

    @Override
    public Class<?> loadClass(String name, boolean resolve) throws ClassNotFoundException {
        synchronized (getClassLoadingLock(name)) {
            // 1. 檢查是否已經載入過 / Check if already loaded
            Class<?> c = findLoadedClass(name);
            if (c == null) {
                try {
                    // 2. 破壞雙親委派：先嘗試從外掛自己的路徑找 (核心類別除外)
                    // Break delegation: Try to find it locally first (except core classes)
                    if (!name.startsWith("java.") && !name.startsWith("javax.")) {
                        c = findClass(name);
                    }
                } catch (ClassNotFoundException e) {
                    // 本地找不到，才交給 Parent (Fallback to parent)
                    c = super.loadClass(name, resolve);
                }
            }
            if (resolve) {
                resolveClass(c);
            }
            return c;
        }
    }
}
```
*實戰意義：這段程式碼展示了如何讓外掛擁有自己版本的依賴庫，而不會與主程式或其他外掛發生衝突。*
*Practical takeaway: This code demonstrates how to allow a plugin to have its own versions of dependencies without conflicting with the host application or other plugins.*

### 案例 2：Thread Context ClassLoader (TCCL) 解決 SPI 載入失敗 / TCCL solving SPI loading failure

當你在開發一個基礎框架，需要實例化使用者提供的類別時，直接使用 `Class.forName()` 會失敗，因為框架的 ClassLoader 看不到使用者的程式碼。
*When developing a foundational framework that needs to instantiate user-provided classes, using `Class.forName()` directly will fail because the framework's ClassLoader cannot see the user's code.*

```java
// 反模式 (Anti-pattern): 在框架程式碼中直接載入
// Framework ClassLoader tries to load user class -> ClassNotFoundException
Class<?> userStrategy = Class.forName("com.myapp.CustomStrategy"); 

// 最佳實務 (Best Practice): 使用 TCCL
// Use the Thread Context ClassLoader provided by the application environment
ClassLoader tccl = Thread.currentThread().getContextClassLoader();
Class<?> userStrategy = Class.forName("com.myapp.CustomStrategy", true, tccl);
Object instance = userStrategy.getDeclaredConstructor().newInstance();
```
*實戰意義：Spring 框架底層大量使用了 TCCL 來掃描與載入開發者寫的 `@Component` 與 `@Service`。*
*Practical takeaway: The Spring framework heavily uses TCCL under the hood to scan and load developer-written `@Component` and `@Service` classes.*