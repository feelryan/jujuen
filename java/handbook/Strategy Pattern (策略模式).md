# Strategy Pattern（策略模式）

## 使用情境（Scenario）

> **當演算法或業務邏輯需要在「執行時期」動態切換時**

例如：

*   不同計價策略（折扣、會員價、促銷）
*   不同排序 / 過濾方式
*   不同驗證或處理流程

傳統方式會建立很多 `XXXStrategy` 類別，但在 **Java 8+** 中已不再是最佳選擇。

***

# ✅ Best Practice ①：使用 `Enum + Lambda` 取代多個策略類別

> **適合策略數量「有限且固定」的情境**

***

## 📌 範例：訂單價格計算策略

### 傳統（不推薦，僅概念）

```java
class NormalPriceStrategy { ... }
class VipPriceStrategy { ... }
class DiscountPriceStrategy { ... }
```

👉 類別爆炸、樣板程式碼多

***

## ✅ 現代寫法：Enum + Lambda

```java
import java.util.function.Function;

public enum PricingStrategy {

    NORMAL(price -> price),
    VIP(price -> price * 0.8),
    DISCOUNT(price -> price * 0.5);

    private final Function<Double, Double> calculator;

    PricingStrategy(Function<Double, Double> calculator) {
        this.calculator = calculator;
    }

    public double calculate(double price) {
        return calculator.apply(price);
    }
}
```

***

### ✅ 使用端（動態切換策略）

```java
PricingStrategy strategy = PricingStrategy.VIP;

double finalPrice = strategy.calculate(100.0);
System.out.println(finalPrice); // 80.0
```

✅ **重點優點**

*   沒有任何 `ConcreteStrategy` 類別
*   策略集中管理、語意清楚
*   Enum 保證型別安全
*   Lambda 讓邏輯極度精簡

***

# ✅ Best Practice ②：直接傳遞 `Function<T, R>`（最彈性）

> **適合策略需要由外部決定、組合、或測試替換的情境**

***

## 📌 範例：服務接受策略作為參數

```java
import java.util.function.Function;

public class PriceService {

    public double calculate(double price, Function<Double, Double> strategy) {
        return strategy.apply(price);
    }
}
```

***

### ✅ 使用方式（執行期決定策略）

```java
PriceService service = new PriceService();

// VIP strategy
double vipPrice = service.calculate(100.0, p -> p * 0.8);

// Discount strategy
double discountPrice = service.calculate(100.0, p -> p * 0.5);

// Custom strategy
double customPrice = service.calculate(100.0, p -> p - 20);
```

✅ **優點**

*   完全不需要 Strategy 類別或 Enum
*   策略可在 runtime 任意組合
*   非常適合測試與 DI
*   天然支援 Lambda / Method Reference

***

## ✅ 搭配 Method Reference（更乾淨）

```java
public class PriceStrategies {
    public static double vip(double price) {
        return price * 0.8;
    }
}
```

```java
double price =
    service.calculate(100.0, PriceStrategies::vip);
```

***

# 🧠 什麼時候用哪一種？

| 情境           | 建議                 |
| ------------ | ------------------ |
| 策略數量固定、明確    | ✅ Enum + Lambda    |
| 策略來自外部或動態組合  | ✅ `Function<T, R>` |
| 舊式 OO 教學     | ⚠ 傳統 Strategy 類別   |
| 現代 Java 業務邏輯 | ✅ 函數式策略            |

***

# ❌ 為何捨棄傳統 Strategy 類別？

*   類別數量暴增
*   每個類別通常只有一行邏輯
*   Java 8+ 已有標準函數式介面可用
*   增加維護成本，卻沒有對應價值

***

# ✅ 一句話總結（可直接放 handbook）

> **當策略需要在執行期切換時可使用 Strategy Pattern；在 Java 8+ 中，捨棄多個策略類別，改用 `Enum` 搭配 Lambda，或直接傳遞 `Function<T, R>` 等函數式介面，以達成更精簡且彈性的設計。**


直接說即可 👍
