
# 1️⃣ Builder Pattern（建造者模式）

## 使用情境（Why）

當你遇到以下情況時，**Builder Pattern 非常適合**：

*   ✅ 物件有 **超過 4 個以上屬性**
*   ✅ 有些屬性是 **選填（optional）**
*   ✅ 不希望使用多個重載建構子（constructor explosion）
*   ✅ 希望建立 **不可變（Immutable）物件**

***

## ✅ 做法一：Static Inner Class Builder（經典但仍推薦）

### 📌 範例：不可變的 `User` 物件

```java
public class User {

    // 必填欄位
    private final String id;
    private final String name;

    // 選填欄位
    private final int age;
    private final String email;
    private final String address;

    private User(Builder builder) {
        this.id = builder.id;
        this.name = builder.name;
        this.age = builder.age;
        this.email = builder.email;
        this.address = builder.address;
    }

    // ✅ 靜態內部 Builder
    public static class Builder {
        private final String id;
        private final String name;

        private int age = 0;
        private String email;
        private String address;

        public Builder(String id, String name) {
            this.id = id;
            this.name = name;
        }

        public Builder age(int age) {
            this.age = age;
            return this;
        }

        public Builder email(String email) {
            this.email = email;
            return this;
        }

        public Builder address(String address) {
            this.address = address;
            return this;
        }

        public User build() {
            return new User(this);
        }
    }
}
```

### ✅ 使用方式

```java
User user = new User.Builder("u123", "Ryan")
        .age(30)
        .email("ryan@example.com")
        .build();
```

### ✅ 優點說明

*   ✔ 可清楚區分 **必填 vs 選填**
*   ✔ 物件建立後完全不可變
*   ✔ 方法鏈（Fluent API）可讀性極佳
*   ✔ 避免一堆 constructor overload

***

## ✅ 做法二：使用 Lombok 的 `@Builder`（最常見於現代專案）

如果你的專案允許使用 Lombok，**這是最省事、最普遍的做法**。

### 📌 範例

```java
import lombok.Builder;
import lombok.Value;

@Value
@Builder
public class User {
    String id;
    String name;
    Integer age;
    String email;
    String address;
}
```

### ✅ 使用方式

```java
User user = User.builder()
        .id("u123")
        .name("Ryan")
        .age(30)
        .email("ryan@example.com")
        .build();
```

### ✅ 為什麼是 Best Practice

*   幾乎 **0 樣板程式碼**
*   自動產生：
    *   Builder
    *   private constructor
    *   getter
*   常見於 **Spring / 微服務 / DTO**

⚠ 注意：  
Lombok 產生的程式碼在原始碼中「看不到」，團隊需有共識。

***

## 2️⃣ 現代 Java 建議：如果只是資料載體，優先使用 `record`

> ✅ **Java 16+ 引入 `record`，是 data carrier 的首選**

### 📌 適合情境

*   ✅ 僅用來承載資料（DTO / VO / API request/response）
*   ✅ 不需要複雜建構流程
*   ✅ 天然不可變

***

### 📌 範例：使用 `record` + compact constructor

```java
public record User(
        String id,
        String name,
        Integer age,
        String email,
        String address
) {
    // ✅ Compact constructor
    public User {
        if (id == null || name == null) {
            throw new IllegalArgumentException("id and name are required");
        }
    }
}
```

### ✅ 使用方式

```java
User user = new User(
        "u123",
        "Ryan",
        30,
        "ryan@example.com",
        null
);
```

### ✅ 為什麼優先考慮 record？

*   ✔ 天然 immutable
*   ✔ 自動產生 `constructor / getters / equals / hashCode / toString`
*   ✔ 極度精簡、語意清楚
*   ✔ 非常適合現代 Java 架構

***

## 🧠 怎麼選？一張心智對照表

| 情境               | 建議                 |
| ---------------- | ------------------ |
| 屬性多 + 有選填 + 建立複雜 | ✅ Builder Pattern  |
| 專案使用 Lombok      | ✅ `@Builder`       |
| 純資料載體（DTO/VO）    | ✅ `record`         |
| 需要不可變            | ✅ Builder 或 record |

***

## ✅ 一句話總結

> **當物件屬性多且部分為選填，或需要不可變物件時，使用 Builder Pattern。可用靜態內部類別或 Lombok 的 `@Builder`；在現代 Java 中，若只是資料載體，優先選擇 `record` 搭配精簡建構子。**


只要說一聲 👍
