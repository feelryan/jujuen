# 效能優化與快取策略指南 / Performance Optimization & Caching Strategy Guide

## Mental model｜心智模型

在 Spring Boot 應用程式中，效能優化通常圍繞著兩個核心資源管理概念：**「資源池化 (Pooling)」** 與 **「資料局部性 (Data Locality)」**。

1.  **資料庫連線是昂貴的租借品 (Database Connections are expensive rentals)**：
    *   建立與關閉資料庫連線極度消耗資源。HikariCP 的角色就像是「計程車排班站」，車子（連線）預先發動好等在那裡。
    *   **關鍵思維**：連線池的大小不是越大越好。過大的池會導致 CPU 在不同連線間頻繁切換 (Context Switching)，反而降低吞吐量。

2.  **快取是借來的時間 (Caching is borrowed time)**：
    *   快取是用「空間換取時間」並犧牲「即時一致性」的策略。
    *   **關鍵思維**：引入快取即引入了複雜度（快取失效、資料不一致）。除非資料庫成為瓶頸且資料允許短暫過期，否則不要過早優化 (Premature Optimization)。
    *   **分層防禦**：
        *   L1: Local Cache (e.g., Caffeine) - 速度極快，但僅限單機，重啟消失。
        *   L2: Distributed Cache (e.g., Redis) - 速度快，跨實例共享，持久化。
        *   L3: Database - 真實資料來源 (Source of Truth)。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. HikariCP 連線池調校 (HikariCP Tuning)

HikariCP 是 Spring Boot 預設且效能極佳的連線池，但預設值通常不適用於生產環境。

*   **固定池大小 (Fixed Pool Size)**：
    *   **Pattern**: 設定 `minimumIdle` 等於 `maximumPoolSize`。
    *   **Why**: 避免連線池在流量波動時動態建立與銷毀連線的開銷。
*   **黃金公式 (The Formula)**：
    *   對於 HDD/SSD 混合儲存的資料庫：`connections = ((core_count * 2) + effective_spindle_count)`
    *   對於全 SSD 或雲端資料庫，通常 `CPU Core * 2` 到 `CPU Core * 4` 之間是甜蜜點。
    *   *實戰經驗：對於一個 4 vCPU 的 DB Server，連線池設為 10-20 往往比設為 100 更快。*

### 2. Redis 快取序列化 (Redis Serialization)

Spring Boot 預設使用 JDK Serialization (`JdkSerializationRedisSerializer`)，這會產生無法閱讀的二進位資料且跨語言相容性差。

*   **Pattern**: 使用 JSON 序列化。
*   **Implementation**: 設定 `RedisTemplate` 使用 `GenericJackson2JsonRedisSerializer` 或 `StringRedisSerializer`。
*   **Why**: 方便 Debug（在 Redis GUI 中可讀），且相容其他語言的服務。

### 3. 快取更新策略 (Cache Invalidation Strategy)

*   **Cache-Aside (Lazy Loading)**：
    *   讀取：先查 Cache，沒有則查 DB 並回寫 Cache。Spring 的 `@Cacheable` 預設即此模式。
    *   寫入：先寫 DB，**然後刪除 (Evict)** Cache，而不是更新 Cache。
    *   **Why**: 「刪除」比「更新」更能保證一致性，避免兩個併發寫入導致 Cache 存了舊值。

### 4. 針對不同業務場景設定 TTL (Time-To-Live)

*   不要對所有快取使用全域統一的過期時間。
*   **Pattern**: 透過自定義 `CacheManager` 或 Redis 設定，區分 `Short-Lived` (如庫存，1分鐘) 與 `Long-Lived` (如商品詳情，1小時) 的快取配置。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Thundering Herd" Problem (快取雪崩/擊穿)
*   **現象**：當一個熱門 Key 過期（或 Redis 當機），成千上萬的請求瞬間穿透到資料庫，導致 DB CPU 飆升甚至當機。
*   **Avoid**:
    *   使用 `sync = true` 屬性在 `@Cacheable` 中（這會加本地鎖）。
    *   實作 Mutex Lock (分散式鎖) 在快取重建邏輯中。
    *   設定 TTL 時加入隨機抖動 (Jitter)，避免大量 Key 同一時間過期。

### 2. 濫用 `@Cacheable` 於複雜物件
*   **現象**：將含有循環參照 (Circular Reference) 或 Lazy Loading 屬性的 Hibernate Entity 直接塞入 Redis。
*   **Consequence**: 序列化失敗 (`StackOverflowError`) 或 `LazyInitializationException`。
*   **Fix**: 永遠只快取 **DTO (Data Transfer Object)**，而非 Entity。

### 3. 忽略 Keyspace 事件與記憶體管理
*   **現象**：Redis 記憶體爆滿，導致 Eviction 策略啟動，隨機刪除資料。
*   **Fix**: 監控 Redis `maxmemory` 設定，並確保設定了合適的 Eviction Policy (如 `volatile-lru` 或 `allkeys-lru`)。

### 4. HikariCP `connectionTimeout` 設定過長
*   **現象**：預設 30秒。當 DB 變慢時，App Server 的執行緒會卡住 30秒等待連線，導致整個 App Server 無回應 (Thread Starvation)。
*   **Fix**: 設定為 `2000ms` - `5000ms`。如果 5秒拿不到連線，快速失敗 (Fail Fast) 比卡死更好。

---

## Checklists & workflows｜檢查清單與流程

### Performance Tuning Checklist (上線前檢核)

- [ ] **HikariCP Config**:
    - [ ] `maximum-pool-size` 是否已根據 DB 核心數計算？(非預設值 10)
    - [ ] `minimum-idle` 是否等於 `maximum-pool-size`？
    - [ ] `connection-timeout` 是否設為合理值 (e.g., 2000ms - 5000ms)？
- [ ] **Redis Config**:
    - [ ] 是否已替換預設的 JDK Serializer 為 JSON Serializer？
    - [ ] 是否為所有 Cache 設定了預設 TTL (避免永久佔用記憶體)？
    - [ ] Key 的命名是否有統一前綴 (Namespace) 以避免衝突？
- [ ] **Code Level**:
    - [ ] `@Cacheable` 的 Key 是否包含所有查詢參數？
    - [ ] 是否在 `@Transactional` 的方法內小心使用 Cache (避免交易未 commit 就回寫 Cache)？
    - [ ] 是否快取的是 DTO 而非 Managed Entities？

### Caching Decision Tree (決策流程)

1.  **資料讀取頻率高嗎？** -> No -> **不快取**。
2.  **資料變更頻率高嗎？** -> Yes -> **不快取** (或極短 TTL)。
3.  **資料一致性要求是「強一致性」嗎？** -> Yes -> **不快取** (直接讀 DB)。
4.  **允許「最終一致性」？** -> Yes -> **使用 Redis (@Cacheable)**。
5.  **單機存取且資料量小？** -> Yes -> **使用 Caffeine (Local Cache)**。

---

## Real-world examples｜實戰案例

### 1. Production-Ready HikariCP Configuration
這是一份適用於大多數中型專案的 `application.yml` 設定（假設 DB 資源有限）：

```yaml
spring:
  datasource:
    hikari:
      # Pool Size: 假設 DB Server 為 4 Core，App 實例數適中
      maximum-pool-size: 10
      minimum-idle: 10
      # Timeout: 快速失敗，避免執行緒堆積
      connection-timeout: 3000 # 3 seconds
      # Lifetime: 比 DB 預設 wait_timeout 短，避免使用已斷開連線
      max-lifetime: 1800000 # 30 minutes
      pool-name: HikariPool-CoreAPI
```

### 2. Spring Cache with Custom TTL & Serialization
配置多個 Cache Manager 或使用自定義配置來處理不同過期時間。

```java
@Configuration
@EnableCaching
public class CacheConfig {

    @Bean
    public RedisCacheConfiguration cacheConfiguration() {
        return RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(60)) // 預設 60 分鐘
            .disableCachingNullValues()
            // 使用 Jackson 序列化 Value，方便閱讀與跨語言
            .serializeValuesWith(RedisSerializationContext.SerializationPair.fromSerializer(new GenericJackson2JsonRedisSerializer()));
    }
    
    // 針對特定 Cache Name 設定不同的 TTL
    @Bean
    public RedisCacheManagerBuilderCustomizer redisCacheManagerBuilderCustomizer() {
        return (builder) -> builder
            .withCacheConfiguration("product_detail",
                RedisCacheConfiguration.defaultCacheConfig().entryTtl(Duration.ofHours(24))) // 商品詳情快取 1 天
            .withCacheConfiguration("otp_code",
                RedisCacheConfiguration.defaultCacheConfig().entryTtl(Duration.ofMinutes(5))); // 驗證碼快取 5 分鐘
    }
}
```

### 3. Correct Usage of Annotations (Cache-Aside Pattern)

```java
@Service
public class ProductService {

    // 讀取：如果 Redis 有 "product_detail::123" 則直接回傳，否則執行方法並存入
    // sync=true 避免擊穿 (Thundering Herd)
    @Cacheable(value = "product_detail", key = "#id", sync = true)
    public ProductDTO getProductById(Long id) {
        return productRepository.findById(id)
                .map(this::convertToDTO)
                .orElseThrow(() -> new ResourceNotFoundException("Product not found"));
    }

    // 寫入/更新：更新 DB 後，直接刪除 Cache，讓下一次讀取重新 fetch
    @Transactional
    @CacheEvict(value = "product_detail", key = "#id")
    public void updateProductPrice(Long id, BigDecimal newPrice) {
        Product product = productRepository.findById(id).orElseThrow();
        product.setPrice(newPrice);
        productRepository.save(product);
    }
}
```