# 資料管理：保留策略與日誌壓縮 / Data Management: Retention Policies and Log Compaction

## Mental model｜心智模型

要掌握 Kafka 的資料管理，必須打破「Kafka 是一個無限隊列」的幻想，並建立「**基於分段日誌（Segmented Log）的生命週期**」模型。

### 1. 分段（Segments）是管理的最小單位
Kafka **不會** 針對單一條訊息（Message）進行刪除或壓縮。所有的保留策略（Retention Policy）都是作用在 **Log Segment（日誌分段）** 檔案級別上的。
- **寫入時**：資料寫入當前的 `Active Segment`。
- **滾動（Rolling）**：當 `Active Segment` 達到大小上限（`segment.bytes`）或時間上限（`segment.ms`）時，它會被關閉（Closed/Rolled），變成唯讀的舊 Segment，並開啟一個新的 Active Segment。
- **清理時**：只有「已關閉」的 Segments 才會被標記為可清理。

### 2. 兩種截然不同的清理世界觀
你必須根據資料的性質選擇清理策略（`cleanup.policy`）：

| 策略 | 世界觀 | 適用場景 | Mental Image |
| :--- | :--- | :--- | :--- |
| **Delete (Default)** | **事件流 (Stream of Events)**<br>歷史資料隨時間失去價值，只需保留最近 N 天或 N GB。 | Log Aggregation, Metrics, Clickstream | **CCTV 錄影帶**：循環錄影，新帶子覆蓋舊帶子。 |
| **Compact** | **狀態表 (Table of State)**<br>我們只在乎每個 Key 的「最新數值」，舊數值無效。 | User Profile, Product Catalog, CDC (Change Data Capture) | **白板**：同一個位置（Key）只能寫一個值，新的擦掉舊的。 |

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 混合保留策略 (Hybrid Retention)
不要只依賴時間，也不要只依賴大小。
- **Pattern**: 同時設定 `log.retention.hours` (e.g., 7 days) 與 `log.retention.bytes` (e.g., 100GB)。
- **Why**: 避免突發流量（Traffic Spike）撐爆磁碟。當流量暴增時，`bytes` 限制會優先觸發，雖然會縮短資料保留時間（例如從 7 天變 2 天），但能保護 Broker 不會因磁碟滿載而崩潰。

### 2. Log Compaction 與 Tombstone 機制
在 `cleanup.policy=compact` 模式下，如何刪除一個 Key？
- **Pattern**: 發送一條 `Value = null` 的訊息（即 Tombstone）。
- **Config**: 調整 `delete.retention.ms`（預設 24 小時）。這控制 Tombstone 本身保留多久才被物理刪除。
- **Best Practice**: 確保 Consumer 在 `delete.retention.ms` 時間內至少上線消費一次，否則 Consumer 可能會錯過刪除事件，導致本地狀態與 Kafka 不一致（Zombie Data）。

### 3. 分層儲存 (Tiered Storage) 的應用
對於需要長期保存（如 1 年以上）但存取頻率低的資料。
- **Pattern**: 開啟 Tiered Storage（如 KIP-405 或 Confluent Tiered Storage），將熱數據留在 Local Disk (SSD)，冷數據卸載到 S3/GCS (Object Store)。
- **Benefit**: 解耦「運算資源（Broker CPU/RAM）」與「儲存資源」。你可以擁有無限的 Retention 而不需要擴充昂貴的 Broker 節點。

### 4. 針對 Compact Topics 的效能調校
- **Config**: `min.cleanable.dirty.ratio` (預設 0.5)。
- **Trade-off**:
  - 調低（如 0.1）：更頻繁地觸發 Compaction，磁碟空間更省，但 Broker I/O 負載增加。
  - 維持預設（0.5）：只有當 Log 中 50% 是「髒數據（舊值）」時才清理。適合寫入頻繁但 Key 重複率高的場景。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 誤以為訊息會「準時」消失
- **Pitfall**: 設定 `retention.ms=1000` (1秒)，期待訊息 1 秒後立刻釋放空間。
- **Reality**: 訊息必須等到所在的 Segment 被 **滾動（Rolled）** 關閉後，且 Cleaner Thread 掃描到時才會被刪除。如果流量很低，Segment 可能幾天都不會滾動，資料就會一直留著。
- **Fix**: 對於低流量 Topic，需同時調整 `segment.ms` 強制滾動。

### 2. 在 Event Sourcing 場景誤用 Compaction
- **Pitfall**: 將「銀行轉帳紀錄」設為 Compact。
- **Consequence**: Compaction 會刪除同一個帳號（Key）的舊交易紀錄，只保留最後一筆。你會失去帳戶的歷史變動軌跡（Audit Trail）。
- **Rule**: 只有當資料代表「當前狀態（Current State）」時才用 Compact；若代表「歷史事件（History of Events）」請用 Delete。

### 3. Segment Size 設定過大或過小
- **Too Small**: 導致 Broker 打開過多檔案句柄（File Handlers），增加 OS 負載。
- **Too Large**: 導致過期資料無法及時清理（粒度太粗），且在 Consumer 追趕數據（Catch-up）時容易發生突發的網路頻寬佔用。

### 4. 忽略 `__consumer_offsets` 的膨脹
- **Context**: 這是 Kafka 內部的 Compact Topic。
- **Pitfall**: 如果 Consumer Group ID 隨機生成且不斷變化（例如每次部署都換 Group ID），這個 Topic 會無限膨脹，導致 Broker 記憶體不足或載入緩慢。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: 選擇正確的策略

1. **這份資料是「事實流 (Facts)」還是「狀態更新 (Updates)」？**
   - 事實流 (Logs, Tracing, Transactions) -> **Delete**
   - 狀態更新 (User Profile, Table Snapshot) -> **Compact**

2. **如果是 Delete 策略：**
   - [ ] 設定 `log.retention.hours` (時間底線)
   - [ ] 設定 `log.retention.bytes` (空間底線 - **Critical for stability**)
   - [ ] 若需長期保存，是否已啟用 Tiered Storage？

3. **如果是 Compact 策略：**
   - [ ] 確認 Producer 發送的 Key 具有唯一標識性（Non-null keys）。
   - [ ] 確認 `delete.retention.ms` 足夠長，讓所有 Consumer 都有時間處理 Tombstone。
   - [ ] 評估 `min.cleanable.dirty.ratio`，在 I/O 與空間效率間取得平衡。

### Ops Checklist: 上線前檢查

- [ ] **Segment Size**: 確認 `segment.bytes` (預設 1GB) 對於該 Topic 的流量是否合理？（低流量 Topic 建議調小或設定 `segment.ms`）。
- [ ] **Disk Monitoring**: 是否設定了 Disk Usage > 80% 的 Alert？
- [ ] **Compaction Lag**: 對於 Compact Topic，監控 `kafka_log_cleaner_recopy_rate` 與 max lag，確保清理速度跟得上寫入速度。
- [ ] **Key Validation**: 確保 Compact Topic 的 Producer **絕對不會** 發送 `Key=null` 的訊息（除非是業務邏輯錯誤），否則該訊息永遠不會被 Compact，只能等待 `delete` 策略（如果有的話）。

---

## Real-world examples｜實戰案例

### Scenario 1: CDC (Change Data Capture) for Microservices
**場景**：將 MySQL 的 `users` 表同步到 Kafka，供其他服務建立 Local Cache。
- **Config**:
  - `cleanup.policy = compact`
  - `key = user_id`
  - `segment.ms = 10 mins` (為了讓新資料盡快變成可清理狀態，避免 Log 虛胖)
  - `min.cleanable.dirty.ratio = 0.3` (積極清理，保持 Cache 重建速度快)
- **Result**: 新加入的微服務只需從頭讀取該 Topic，即可在短時間內重建完整的 User Table 狀態，而無需讀取所有歷史變更。

### Scenario 2: High-Volume Clickstream Logs
**場景**：網站點擊流，每秒 100k msg，用於即時分析與寫入 Data Lake。
- **Config**:
  - `cleanup.policy = delete`
  - `log.retention.hours = 4` (Kafka 僅作為緩衝區)
  - `log.retention.bytes = 500GB` (防止突發流量塞滿 Disk)
  - `compression.type = zstd` (以 CPU 換取 Disk I/O 與儲存空間)
- **Result**: Kafka 運作得像一個高效的 Pipe，資料快速流過不佔用長期空間，長期儲存交給 S3/HDFS。

### Scenario 3: GDPR "Right to be Forgotten" Implementation
**場景**：使用者要求刪除個資，但資料散落在 Kafka 的多個 Topic 中。
- **Technique**: **Crypto-shredding (加密銷毀)**
- **Implementation**:
  1. 所有敏感資料在寫入 Kafka 前，使用該 User 專屬的 Key 進行加密。
  2. 該 User 的 Encryption Key 儲存在一個外部的 Key Management Service (KMS) 或一個專門的 Compact Topic 中。
  3. 當用戶要求刪除時，只需刪除（丟棄）該 User 的 Encryption Key。
  4. Kafka 中的資料雖然還在（直到 Retention 到期），但已變成無法解密的亂碼（Ciphertext），符合法規上的「無法復原」。