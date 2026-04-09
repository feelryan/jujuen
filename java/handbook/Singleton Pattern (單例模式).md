
# Singleton Pattern（單例模式）

## 使用情境（Scenario）

> **確保系統中某個類別在整個應用程式生命週期中只會存在一個實例**  
> 常見例子：
>
> *   全域設定（Configuration）
> *   系統層級服務（如 Feature Toggle、ID Generator）
> *   基礎資源管理器

***

# ✅ Best Practice ①：優先交給 Spring IoC 管理（最推薦）

> **除非你在寫底層函式庫，否則不要自己寫 Singleton**

### 為什麼？

*   Spring 預設 `@Component` 就是 **Singleton Scope**
*   支援 DI、AOP、測試、生命週期管理
*   避免手寫 Singleton 的各種陷阱

***

## ✅ 範例：使用 Spring 管理單例

```java
import org.springframework.stereotype.Component;

@Component
public class AppConfig {

    public String getAppName() {
        return "JuJuEn System";
    }
}
```

### 使用端（無須關心 Singleton）

```java
import org.springframework.stereotype.Service;

@Service
public class StartupService {

    private final AppConfig appConfig;

    public StartupService(AppConfig appConfig) {
        this.appConfig = appConfig;
    }

    public void start() {
        System.out.println(appConfig.getAppName());
    }
}
```

✅ **重點**

*   沒有 `getInstance()`
*   沒有 `static`
*   Singleton 由 **框架負責**

***

# ✅ Best Practice ②：必須手動實作時 → 使用 `enum`（最安全）

> 適用情境：
>
> *   非 Spring 環境
> *   底層函式庫
> *   不可依賴 IoC container

***

## ✅ 範例：Enum Singleton（官方推薦）

```java
public enum GlobalConfig {

    INSTANCE;

    private String appName = "JuJuEn System";

    public String getAppName() {
        return appName;
    }

    public void setAppName(String appName) {
        this.appName = appName;
    }
}
```

### 使用方式

```java
String name = GlobalConfig.INSTANCE.getAppName();
```

***

## ✅ 為什麼 Enum 是「最佳解」？

Enum Singleton 天然保證：

| 問題              | Enum 是否解決 |
| --------------- | --------- |
| 執行緒安全           | ✅         |
| 防 Reflection 攻擊 | ✅         |
| 防反序列化破壞         | ✅         |
| 實作簡單            | ✅         |

✅ **這是《Effective Java》作者 Joshua Bloch 明確推薦的做法**

***

# ⚠ 常見但不推薦：Classic Singleton（了解即可）

> **以下範例不建議使用，但常在舊系統看到**

```java
public class BadSingleton {

    private static final BadSingleton INSTANCE = new BadSingleton();

    private BadSingleton() {
    }

    public static BadSingleton getInstance() {
        return INSTANCE;
    }
}
```

### 問題點

*   可被 Reflection 破解
*   序列化可能產生新實例
*   不利測試（mock 困難）
*   與現代 DI 架構不相容

👉 **除非你非常清楚後果，否則不要用**

***

# 🧠 如何選擇？（實戰對照）

| 使用情境                 | 建議               |
| -------------------- | ---------------- |
| Spring / Spring Boot | ✅ `@Component`   |
| 函式庫 / 非 IoC          | ✅ `enum`         |
| 新專案                  | ✅ 避免手寫 Singleton |
| 舊系統維護                | ⚠ 僅理解即可          |

***

# ✅ 一句話總結（可直接放 handbook）

> **Singleton 模式用於確保系統中僅有一個實例；在現代應用中，優先交由 Spring IoC 管理。若必須手動實作，使用 `enum` 是最安全、可防止反射與序列化問題的實作方式。**


直接說一聲即可 👍
