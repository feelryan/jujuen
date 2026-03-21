# 資料治理：Schema Registry 與版本演進 / Data Governance: Schema Registry and Evolution

## Mental model｜心智模型

在 Kafka 的世界裡，Broker 對數據內容一無所知（agnostic），它只負責搬運 Byte Array。如果生產者（Producer）和消費者（Consumer）對 Byte Array 的結構（Schema）理解不一致，就會導致災難性的「反序列化失敗」或數據錯亂。

Schema Registry 的核心心智模型是 **「合約中心化與 ID 參照」（Centralized Contract & ID Reference）**：

1.  **解耦數據與定義 (Decoupling Data from Definition)**：
    不要將冗長的 Schema 定義（例如 JSON 欄位說明）隨每一條訊息發送。相反地，Producer 將 Schema 註冊到 Registry，獲得一個唯一的 `Schema ID`（通常是 4 bytes 的整數）。
2.  **線路格式 (Wire Format)**：
    實際傳輸的 Payload 變成了：`[Magic Byte] + [Schema ID] + [Serialized Data]`。
3.  **動態解析 (Dynamic Resolution)**：
    Consumer 讀到 `Schema ID` 後，若本地快取沒有，則向 Registry 查詢該 ID 對應的 Schema，再用它來還原數據。

這就像是外交護照：你不需要把你的出生證明和詳細個資寫在臉上，你只需要出示一本護照（帶有 ID），海關（Consumer）透過查驗系統（Registry）就能知道如何處理你。

> **The Core Concept:** Treat Schema Registry as the "Source of Truth" for API contracts between decoupled services. It transforms an implicit agreement into an explicit, version-controlled dependency.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 選擇正確的序列化格式 (Choosing the Right Serialization Format)
雖然 JSON 易讀，但在高吞吐量場景下，請優先選擇 **Avro** 或 **Protobuf**。
- **Avro**: Kafka 生態系的頭等公民。支援豐富的 Schema Evolution 規則。適合大數據分析與 Hadoop 生態整合。
- **Protobuf**: Google 的標準，型別系統嚴謹，程式碼生成（Code Generation）支援度極佳。適合微服務間的高效通訊。

### 2. Subject Naming Strategy 的選擇 (Subject Naming Strategies)
Schema 在 Registry 中是以 "Subject" 為單位管理的。選擇正確的命名策略至關重要：
- **TopicNameStrategy (Default)**: Subject 名稱為 `<topic>-value`。
  - *Pros:* 簡單直觀，強制一個 Topic 只有一種 Schema，便於治理。
  - *Cons:* 無法在同一個 Topic 混用不同類型的 Event。
- **RecordNameStrategy**: Subject 名稱為 `<FullyQualifiedClassName>`。
  - *Pros:* 允許在同一 Topic 放入多種 Event 類型。
  - *Cons:* Consumer 必須知道如何處理多種型別，增加了複雜度與耦合。
- **TopicRecordNameStrategy**: 結合上述兩者。
  - *Best Practice:* 90% 的情況下，請堅持使用 **`TopicNameStrategy`**。單一 Topic 單一職責（Single Responsibility）通常是更好的架構選擇。

### 3. 相容性模式設定 (Compatibility Modes)
這決定了 Schema 演進的規則：
- **BACKWARD (Default)**: 新的 Schema 可以被舊的 Consumer 讀取。
  - *場景:* 當你無法同時升級所有 Consumer 時（最常見）。這意味著你只能「新增欄位（並給予預設值）」或「刪除欄位」。
- **FORWARD**: 舊的 Schema 可以被新的 Consumer 讀取。
  - *場景:* 當你必須先升級 Producer，再慢慢升級 Consumer 時（較少見）。
- **FULL**: 向前向後都相容。
  - *場景:* 最安全的模式，允許 Producer 和 Consumer 任意順序升級，但對 Schema 修改的限制最嚴格。

### 4. CI/CD 階段的 Schema 驗證 (Schema Validation in CI/CD)
不要等到 Runtime 才發現 Schema 不相容。
- 使用 Maven/Gradle plugin (e.g., `kafka-schema-registry-maven-plugin`) 在 Build 階段檢查相容性。
- **Pattern**: 本地定義 `.avsc` -> CI 檢查 `test-compatibility` -> CD 執行 `register` -> 部署應用程式。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 隨意更改欄位名稱 (Renaming Fields in Avro)
- **Pitfall**: 在 Avro 中，欄位名稱是 Schema 的一部分。如果你將 `user_id` 改名為 `uid`，這被視為「刪除舊欄位並新增新欄位」。
- **Consequence**: 如果沒有設定 `default` 值，這會破壞 **BACKWARD** 相容性，導致 Consumer 炸裂。
- **Solution**: 使用 Avro 的 `aliases` 功能來處理更名，或者永遠只新增欄位。

### 2. 依賴 GenericRecord 而非具體類別 (Using GenericRecord over SpecificRecord)
- **Pitfall**: 開發者為了省事，不生成 Java POJO，直接使用類似 Map 的 `GenericRecord`。
- **Consequence**: 失去了型別安全（Type Safety），重構困難，且 IDE 無法提供自動完成，容易寫出 Bug。
- **Solution**: 總是使用 Code Generator 生成強型別的類別（SpecificRecord）。

### 3. 混合使用 Schema Registry 與 Raw Json (Mixing Registry and Raw JSON)
- **Pitfall**: Producer 使用 Avro Serializer，但某個 Consumer 試圖用 String Deserializer 讀取並手動 Parse JSON。
- **Consequence**: Consumer 會讀到亂碼（包含 Magic Byte 和 Schema ID），導致解析錯誤。
- **Solution**: 確保全鏈路都使用相容的 SerDe (Serializer/Deserializer)。

### 4. 忽略 Schema Registry 的高可用性 (Ignoring Registry HA)
- **Pitfall**: 認為 Registry 只是「存設定檔的地方」，掛了也沒關係。
- **Consequence**: 雖然 Client 端有 Cache，但若 Cache 失效或有新 Schema 產生，Registry 當機將導致 Producer 無法發送訊息（無法取得 ID）或 Consumer 無法消費（無法取得 Schema）。

---

## Checklists & workflows｜檢查清單與流程

### Schema Evolution Workflow (開發流程)
- [ ] **定義 (Define)**: 修改 `.avsc` 或 `.proto` 檔案。
- [ ] **規範 (Rules)**:
    - [ ] 新增欄位是否有 `default` 值？（為了 Backward Compatibility）
    - [ ] 是否避免了修改現有欄位的型別？
    - [ ] 是否避免了重新命名必要欄位？
- [ ] **驗證 (Validate)**: 在 Local 或 CI 環境執行 `mvn schema-registry:test-compatibility`。
- [ ] **發布 (Publish)**: 在部署應用程式前，或應用程式啟動時自動註冊 Schema。

### Production Readiness Checklist (生產環境檢查)
- [ ] **Mode**: 確認 Subject 的相容性模式已明確設定（建議 `BACKWARD` 或 `FULL`）。
- [ ] **Security**: Schema Registry 是否有配置 Authentication (Basic Auth/mTLS)？
- [ ] **HA**: Schema Registry 是否為 Cluster 模式（背後通常依賴 Kafka topic `_schemas`）？
- [ ] **Caching**: Client 端的 `cached.schema.registry.capacity` 是否足夠（預設 1000 通常足夠，但在超多 Schema 場景需注意）？

---

## Real-world examples｜實戰案例

### 案例：電商訂單系統的演進 (E-commerce Order Evolution)

假設我們有一個 `orders` topic，使用 Avro 格式。

#### Phase 1: 初始上線
Schema V1 定義如下：
```json
{
  "type": "record",
  "name": "Order",
  "fields": [
    {"name": "order_id", "type": "string"},
    {"name": "amount", "type": "double"}
  ]
}
```
Producer 發送數據，Consumer 正常消費。

#### Phase 2: 業務需求變更 (新增「折扣碼」)
業務方要求新增 `discount_code`。開發者修改 Schema 為 V2：

**錯誤做法 (Bad Practice)**:
```json
{"name": "discount_code", "type": "string"} // 缺少 default 值
```
*後果*: 舊的數據（V1）沒有這個欄位，當 Consumer 升級到 V2 Schema 並試圖讀取 V1 數據時，會因為找不到欄位且沒有預設值而拋出 Exception。

**正確做法 (Best Practice - Backward Compatible)**:
```json
{
  "name": "discount_code", 
  "type": ["null", "string"], 
  "default": null 
}
```
*結果*:
1. Producer 升級使用 V2 Schema 發送新訂單。
2. 尚未升級的 Consumer (持有 V1 Schema) 讀取 V2 數據時，會自動忽略 `discount_code`（Avro 特性）。
3. 升級後的 Consumer (持有 V2 Schema) 讀取 V1 舊數據時，會自動將 `discount_code` 填為 `null`。
4. **系統平滑過渡，無需停機。**

#### Phase 3: 故障排除 (Troubleshooting)
某天 Consumer 報錯：`org.apache.kafka.common.errors.SerializationException: Unknown magic byte!`

**診斷步驟**:
1. 檢查 Producer 是否意外切換成了 `StringSerializer` 或 `JsonSerializer`，導致沒有寫入 Schema Registry 規定的 5-byte header。
2. 檢查 Consumer 是否連錯了 Schema Registry URL（例如連到了 Dev 環境的 Registry，導致找不到 ID）。
3. 驗證 Topic 內是否混入了髒數據（非 Avro 格式的訊息）。