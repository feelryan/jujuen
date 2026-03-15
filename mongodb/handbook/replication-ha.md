# 複製集與高可用性架構 / Replication & High Availability

## Mental model｜心智模型

在深入設定之前，必須先建立正確的 Replica Set 運作心智模型。MongoDB 的複製機制並非單純的「檔案備份」，而是一個 **基於操作日誌（Operation Log）的非同步串流系統**。

### 1. The Journaling Stream (Oplog)
想像 Primary 節點是一位正在寫日記的作者。所有的寫入操作（Insert, Update, Delete）首先被記錄在 `oplog`（Operation Log）中。Secondary 節點則是訂閱者，它們不斷地從 Primary 的 `oplog` 尾端讀取新的條目，並在自己的資料庫上重放（Replay）這些操作。
*   **關鍵點**：複製是 **非同步（Asynchronous）** 的。Primary 寫入成功與 Secondary 複製完成之間存在時間差，這個時間差稱為 **Replication Lag**。

### 2. The Democracy (Election & Quorum)
Replica Set 是一個民主體系。節點之間透過心跳（Heartbeats）互相監控。當 Primary 失聯時，剩下的節點會發起選舉。
*   **關鍵點**：選舉成功的條件是獲得「大多數（Majority）」節點的投票。因此，Replica Set 的節點總數通常建議為 **奇數**，以避免票數相同導致無法選出 Leader（Split-brain 僵局）。
*   **Majority 定義**：`N/2 + 1`。例如 3 個節點的叢集，需要 2 票才能成為 Primary。

### 3. Consistency vs. Availability Trade-off
在高可用性架構中，你必須在「資料絕對不掉（Consistency）」與「服務隨時可用（Availability）」之間做取捨。
*   **預設行為**：MongoDB 預設傾向 Availability。Primary 寫入成功即回傳，不等待 Secondary。如果 Primary 在複製前崩潰，資料可能會在 Failover 過程中回滾（Rollback）並遺失。
*   **強一致性模式**：透過 `Write Concern` (`w: "majority"`) 強制要求資料寫入大多數節點才算成功，犧牲部分寫入延遲來換取資料耐久性（Durability）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Architecture Patterns: PSS over PSA
**PSS (Primary-Secondary-Secondary)** 是生產環境的黃金標準。
*   **PSS**：三個完整的資料節點。具備高可用性與資料冗餘。
*   **PSA (Primary-Secondary-Arbiter)**：兩個資料節點加一個仲裁者（Arbiter）。
    *   *Why avoid Arbiter?* Arbiter 不存資料。如果 Primary 掛了，Secondary 成為新的 Primary，此時叢集只剩下一份資料副本。若此時該節點硬體故障，資料將永久遺失。且使用 `w: "majority"` 在 PSA 架構下容易因單點故障導致寫入阻塞。

### 2. Write Concern Strategy
不要在應用程式層級寫死 Write Concern，應根據業務場景動態調整，或設定 Connection String 層級的預設值。
*   **關鍵交易（金流、訂單）**：務必使用 `{ w: "majority", j: true }`。確保資料已寫入大多數節點的磁碟 Journal，防止斷電或 Failover 導致資料回滾。
*   **一般日誌/緩存**：可使用 `{ w: 1 }`，追求效能。

### 3. Read Preference for Isolation, Not Scaling
許多開發者誤以為將讀取流量導向 Secondary (`readPreference: secondary`) 是為了「提升讀取效能」。這通常是錯誤的起手式。
*   **正確用法**：將繁重的分析型查詢（Analytics/Reporting）導向一個專用的、設定為 `hidden: true` 的 Secondary 節點，避免影響 Primary 的線上服務效能。
*   **線上服務**：預設應讀取 Primary (`primary`) 以確保強一致性。若能容忍讀到舊資料（Eventual Consistency），才考慮 `primaryPreferred` 或 `secondaryPreferred`。

### 4. Priority Configuration
利用 `priority` 設定來控制誰該當 Primary。
*   將硬體較強、位於主機房的節點設為 `priority: 2`。
*   將異地備援（DR）節點設為 `priority: 0`（永遠不當 Primary，除非手動介入），防止因為網路波動導致 Primary 飄移到遠端機房，增加整體延遲。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Even Number" Trap (偶數節點陷阱)
*   **情境**：部署了 2 個或 4 個節點。
*   **後果**：當網路分割（Network Partition）發生時，兩邊都無法湊齊大多數票數，導致整個叢集變成唯讀（Read-only）或無法選出 Primary。
*   **修正**：永遠保持投票節點為奇數。如果預算有限，才考慮加 Arbiter（但請回顧 PSS vs PSA 的權衡）。

### 2. Ignoring Oplog Size (Oplog 視窗過小)
*   **情境**：Oplog 大小設得太小（預設通常是磁碟的 5%）。
*   **後果**：如果一個 Secondary 停機維護時間超過了 Oplog 覆蓋一輪的時間（Oplog Window），該節點重新上線後將無法同步，狀態會變成 `RECOVERING` 且無法恢復，必須重新做 Initial Sync（非常耗時）。
*   **修正**：監控 `Oplog Window` 時間。確保它至少能容納 24 小時以上的寫入量，以便有足夠時間處理故障或維護。

### 3. Blindly Reading from Secondaries
*   **情境**：為了分擔流量，將使用者 Profile 讀取設為 `secondary`。
*   **後果**：使用者更新了個人資料，重新整理頁面卻看到舊資料（因為 Replication Lag）。這會造成極差的使用者體驗與 Bug 回報。
*   **修正**：對於「寫後即讀（Read-your-writes）」的場景，必須讀取 Primary。

### 4. Rollback Data Loss
*   **情境**：Primary 接受了寫入 (`w: 1`) 後立刻崩潰，資料還沒傳給 Secondary。Secondary 選舉成為新 Primary。舊 Primary 恢復後，發現自己的那筆資料與新 Primary 衝突。
*   **後果**：MongoDB 會執行 **Rollback**，將衝突資料刪除並寫入 `rollback` 目錄下的 BSON 檔。如果不手動檢查該目錄，資料就默默消失了。
*   **修正**：使用 `w: "majority"` 可從根本避免此問題。

---

## Checklists & workflows｜檢查清單與流程

### Deployment & Configuration Checklist
- [ ] **拓撲檢查**：節點總數是否為奇數？（建議 3, 5, 7）
- [ ] **Oplog 容量**：已評估寫入吞吐量，並設定足夠大的 Oplog Size（建議至少容納 24-48 小時）。
- [ ] **安全性**：是否已啟用 `keyFile` 或 x.509 認證進行節點間通訊加密？
- [ ] **Write Concern**：關鍵程式碼路徑是否已實作 `w: "majority"`？
- [ ] **Read Preference**：是否明確定義讀取策略？（避免預設值造成的意外行為）
- [ ] **Time Synchronization**：所有節點是否已設定 NTP 同步時間？（時間偏移會導致選舉異常）。

### Rolling Upgrade Workflow (零停機維護流程)
當需要升級 MongoDB 版本或修補 OS 時，請遵循此順序：
1.  **備份**：確保最近有可用的備份。
2.  **升級 Secondaries**：
    *   逐一停止 Secondary 服務。
    *   執行升級/維護。
    *   重啟並等待狀態變回 `SECONDARY` 且 Lag 追上。
3.  **升級 Primary**：
    *   在 Shell 執行 `rs.stepDown()` 強制 Primary 降級為 Secondary（觸發選舉，新 Primary 接手）。
    *   原 Primary 變為 Secondary 後，執行升級/維護。
    *   重啟並等待同步。
4.  **驗證**：確認 `rs.status()` 所有節點皆健康。

---

## Real-world examples｜實戰案例

### Case 1: The "Ghost" Order (Rollback Scenario)
**情境**：電商平台在大促期間，資料庫負載極高。某次 Primary 突然斷電重啟。維運團隊發現有幾筆訂單在 Application Log 顯示「建立成功」，但在資料庫裡卻找不到。
**原因**：
1. App 送出訂單，使用預設 `w: 1`。
2. Primary 寫入記憶體/Journal 後回傳 OK。
3. 在 Oplog 複製到 Secondary 之前，Primary 斷電。
4. Secondary 選舉成為新 Primary（此時它沒有那幾筆訂單）。
5. 舊 Primary 復活，發現自己比新 Primary 多了幾筆資料，於是觸發 Rollback，將訂單移至 rollback 資料夾。
**解決方案**：
將訂單寫入改為 `{ w: "majority", wtimeout: 5000 }`。雖然延遲增加了 10-20ms，但保證了訂單不會憑空消失。

### Case 2: Analytics Blocking Production
**情境**：每週一早上 9 點，系統回應速度變慢，Primary CPU 飆高。
**調查**：發現行銷團隊的報表程式在週一執行全表掃描（Full Collection Scan）的聚合運算。雖然他們連線字串設了 `readPreference=secondary`，但因為該 Secondary 負載過重，導致它停止從 Primary 複製資料（Stop Pulling Oplog）。
**連鎖反應**：
當 Secondary 停止複製，Primary 的 Cache 無法有效清除（因為 MongoDB 需要保留某些資料以供複製），導致 Primary 的 Cache Pressure 升高，進而影響寫入效能。
**解決方案**：
建立一個專屬節點：
```javascript
cfg = rs.conf();
cfg.members[3].priority = 0;
cfg.members[3].hidden = true; // 對應用程式隱藏，不參與選舉，不服務一般讀取
cfg.members[3].tags = { "workload": "analytics" };
rs.reconfig(cfg);
```
報表程式指定讀取這個 Hidden Node，徹底隔離負載。

### Case 3: The "Forever Recovering" Node
**情境**：一個 500GB 的資料庫，Oplog 設為 10GB。某個 Secondary 硬體故障，修復花了 6 小時。重新加入叢集後，狀態一直顯示 `RECOVERING`，最後報錯停止。
**原因**：系統每小時產生 2GB 的 Oplog。6 小時產生了 12GB。Oplog 是一個固定大小的 Ring Buffer，舊紀錄已被覆蓋。Secondary 需要的同步點（Sync Source）已經在 Primary 的 Oplog 中找不到了。
**解決方案**：
必須刪除該節點的 `dbPath` 資料，重新進行 **Initial Sync**（全量複製），這在 500GB 資料量下可能耗時數小時甚至數天，期間叢集可用性降低。
**預防**：
調整 Oplog 大小至 50GB+，確保能容納至少 24 小時的寫入量。