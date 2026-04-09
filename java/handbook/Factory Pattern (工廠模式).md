
# Factory Pattern（工廠模式）

## 使用情境（Scenario）

> **當你需要將「物件建立的邏輯」與「物件使用的邏輯」解耦時**

也就是：

*   使用端 **不需要知道** 實際是哪個實作類別
*   需要 **集中管理建立邏輯**
*   未來新增型別時，不希望影響使用端程式碼

***

# ✅ 做法一：使用「介面 Static Method」作為簡單工廠（Simple Factory）

## 1️⃣ 定義介面（含 static factory method）

```java
public interface Notification {

    void send(String message);

    // ✅ Java 8+ Interface Static Method 作為簡單工廠
    static Notification of(String type) {
        switch (type) {
            case "EMAIL":
                return new EmailNotification();
            case "SMS":
                return new SmsNotification();
            default:
                throw new IllegalArgumentException("Unknown notification type: " + type);
        }
    }
}
```

***

## 2️⃣ 實作類別

```java
public class EmailNotification implements Notification {
    @Override
    public void send(String message) {
        System.out.println("Send EMAIL: " + message);
    }
}
```

```java
public class SmsNotification implements Notification {
    @Override
    public void send(String message) {
        System.out.println("Send SMS: " + message);
    }
}
```

***

## 3️⃣ 使用端（完全不知道實作類）

```java
Notification notification = Notification.of("EMAIL");
notification.send("Hello Ryan");
```

✅ **重點**

*   使用端**只依賴介面**
*   建立邏輯集中在介面中
*   不需要額外的 `XXXFactory` 類別

***

## ✅ 為什麼這是 Best Practice？

| 傳統寫法                      | Java 8+ 寫法                 |
| ------------------------- | -------------------------- |
| `new EmailNotification()` | `Notification.of("EMAIL")` |
| 額外 Factory 類              | 介面本身提供                     |
| 分散建立邏輯                    | 集中於抽象層                     |

***

# ✅ 做法二：使用 `Supplier<T>` 進行「動態建立」（取代傳統 Factory 介面）

> 當型別不是寫死的，而是：

*   需註冊
*   需動態擴充
*   需由 DI / 設定檔 / Map 控制

👉 **改用 `Supplier<T>`**

***

## 1️⃣ 建立 Supplier Registry

```java
import java.util.Map;
import java.util.function.Supplier;

public class NotificationFactory {

    private static final Map<String, Supplier<Notification>> REGISTRY =
            Map.of(
                "EMAIL", EmailNotification::new,
                "SMS", SmsNotification::new
            );

    public static Notification create(String type) {
        Supplier<Notification> supplier = REGISTRY.get(type);
        if (supplier == null) {
            throw new IllegalArgumentException("Unknown notification type: " + type);
        }
        return supplier.get();
    }
}
```

***

## 2️⃣ 使用方式

```java
Notification notification =
        NotificationFactory.create("SMS");

notification.send("Factory with Supplier");
```

***

## ✅ 為什麼用 `Supplier<T>`，不用傳統 Factory 介面？

### ❌ 傳統寫法（不推薦）

```java
public interface NotificationFactory {
    Notification create();
}
```

問題：

*   為了「只回傳一個物件」卻多一個介面
*   無法善用 Lambda / Method Reference
*   Java 8+ 已有標準功能介面

***

### ✅ 現代 Java 寫法（推薦）

```java
Supplier<Notification> supplier = EmailNotification::new;
Notification notification = supplier.get();
```

✅ 好處：

*   不需自訂介面
*   天然支援 Lambda
*   容易存入 Map
*   容易測試與替換

***

# ✅ 真實專案常見用法（DI friendly）

```java
public class AlertService {

    private final Supplier<Notification> notificationSupplier;

    public AlertService(Supplier<Notification> notificationSupplier) {
        this.notificationSupplier = notificationSupplier;
    }

    public void alert(String msg) {
        notificationSupplier.get().send(msg);
    }
}
```

使用時注入：

```java
AlertService service =
        new AlertService(EmailNotification::new);

service.alert("Dependency Injection ready");
```

***

# 🧠 設計總結（對應你的原文）

> ✅ **需要解耦建立與使用 → Factory Pattern**  
> ✅ **簡單工廠 → Interface static method**  
> ✅ **動態工廠 → `Supplier<T>`，不要自訂 Factory 介面**

***

## ✅ 一句話版本（可直接放 handbook）

> **在 Java 8+ 中，可使用介面的 static method 作為簡單工廠；若需要動態建立物件，使用 `Supplier<T>` 函數式介面取代傳統 Factory 介面，以降低樣板程式碼並提升彈性。**



直接說你要哪個即可 👍
