# 遺留系統遷移實戰 / Legacy System Migration Strategies

## Mental Model｜心智模型

在處理遺留系統（Legacy System）遷移時，工程師最常犯的錯誤是將其視為一次性的「拆除重建」工程。正確的心智模型應該是 **「飛行中換引擎」 (Changing the engine while flying)** 或是生物學上的 **「絞殺榕模式」 (Strangler Fig Pattern)**。

### Core Concepts

1.  **資產而非債務 (Asset, not just Debt)**：
    遺留系統雖然技術陳舊，但它包含了經過市場驗證的業務邏輯與價值。遷移的目標是 **提取價值 (Extract Value)**，而非單純的消滅舊程式碼。
2.  **共存是常態 (Coexistence is the Norm)**：
    在 99% 的遷移專案中，新舊系統將會在很長一段時間內（數月甚至數年）並行運作。架構設計必須優先考慮新舊系統間的 **互通性 (Interoperability)** 與 **資料同步 (Data Synchronization)**。
3.  **以業務邊界驅動 (Business-Driven Boundaries)**：
    不要為了技術而拆分（例如：「我們把所有的 SQL 預存程序改成 Java」），而應依據 **Bounded Context (界限上下文)** 來拆分。每次遷移都應該對應到一個獨立的業務領域（Domain）。

---

## Patterns & Best Practices｜常見模式與最佳實務

### 1. The Strangler Fig Pattern (絞殺榕模式)
這是最標準的遷移模式。在遺留系統外圍建立新的微服務，透過攔截請求（Intercepting Requests），逐步將流量導向新服務，直到舊系統萎縮至可以被移除。

*   **實作重點**：需要在系統最前端引入一個 **Facade / API Gateway** 來進行流量路由。
*   **策略**：
    *   **Proxy First**: 先將所有請求通過 Gateway 轉發給 Monolith，確保路徑暢通。
    *   **Route by Feature**: 針對特定 URL (e.g., `/api/orders`) 將流量切換至新服務。

### 2. Database Migration Strategies (資料庫遷移策略)
資料庫的拆分遠比程式碼拆分困難。以下是三種主流策略：

#### A. Shared Database (過渡期共用資料庫)
*   **做法**：新服務暫時連線到舊的 Monolith 資料庫。
*   **適用**：遷移初期，快速驗證業務邏輯。
*   **警告**：這是強耦合，必須設定嚴格的 Deadline 移除，否則會變成 Distributed Monolith。

#### B. Dual Write (雙寫模式)
*   **做法**：應用程式同時寫入「舊資料庫」與「新資料庫」。
*   **流程**：
    1.  **Insert/Update**: 應用層同時寫入 Old DB 與 New DB。
    2.  **Read**: 仍然讀取 Old DB（Source of Truth）。
    3.  **Shadow Mode**: 比較 Old DB 與 New DB 的讀取結果，驗證一致性。
    4.  **Switch Read**: 將讀取切換至 New DB。
    5.  **Stop Write**: 停止寫入 Old DB。
*   **挑戰**：無法保證分散式交易原子性（Atomic）。若寫入舊庫成功、新庫失敗，需有補償機制（Retry queue）。

#### C. Change Data Capture (CDC / 資料變更抓取)
*   **做法**：利用資料庫的 Transaction Log (如 MySQL Binlog, PostgreSQL WAL) 來非同步同步資料。
*   **工具**：Debezium, Kafka Connect。
*   **優勢**：解耦應用層，對效能影響最小，適合高吞吐量系統。
*   **劣勢**：存在些微延遲（Eventual Consistency），需處理「回寫」造成的迴圈問題。

### 3. Anti-Corruption Layer (ACL / 防腐層)
不要讓遺留系統的髒命名（Dirty Naming）或怪異結構污染新服務。
*   **做法**：在新服務與舊系統之間建立一個轉接層（Adapter）。
*   **功能**：將舊系統的 `TBL_USR_01` 轉換為新系統的 `User` 物件。

---

## Anti-patterns & Pitfalls｜反模式與踩雷點

### 1. The Big Bang Rewrite (大霹靂重寫)
*   **現象**：團隊決定停止開發新功能 6 個月，從頭重寫整個系統。
*   **後果**：通常會延期至 12-18 個月，且上線當天因為缺乏真實流量驗證而崩潰，或是業務需求早已變更。
*   **解法**：堅持 **Incremental Migration (增量遷移)**。

### 2. Distributed Monolith (分散式單體)
*   **現象**：拆分了服務，但服務之間透過同步 HTTP 呼叫緊密相連，且共用底層資料表。
*   **後果**：一個服務掛掉，全站掛掉；無法獨立部署。
*   **解法**：確保每個服務擁有獨立的 Database Schema，盡量使用非同步通訊（Messaging）。

### 3. Ignoring "The Long Tail" (忽視長尾資料)
*   **現象**：只遷移了「活躍資料」，忽略了 5 年前的歷史訂單或冷資料。
*   **後果**：當用戶查詢歷史紀錄時系統報錯，或報表數據不一致。
*   **解法**：制定明確的 **Backfill (資料回填)** 策略。

### 4. Refactoring while Migrating (遷移同時重構業務邏輯)
*   **現象**：在搬遷程式碼的同時，順便修改了業務規則（例如：改變折扣計算方式）。
*   **後果**：當出現 Bug 時，無法判斷是「架構遷移導致」還是「業務邏輯修改導致」。
*   **解法**：**Lift and Shift first**。先以相同的邏輯搬遷到新架構，確認穩定後，再進行業務重構。

---

## Checklists & Workflows｜檢查清單與流程

### Decision Tree: Data Synchronization Strategy
- **資料量小且寫入頻率低？** -> 使用 **Dual Write (應用層雙寫)**
- **資料量大、高併發寫入？** -> 使用 **CDC (Debezium + Kafka)**
- **唯讀參考資料 (如郵遞區號)？** -> 使用 **Replication / Cache**

### Migration Workflow Checklist (單一服務遷移流程)

#### Phase 1: Preparation (準備階段)
- [ ] **界定邊界**：明確定義要拆分的 Domain 及其涉及的資料表。
- [ ] **建立 ACL**：在舊系統中建立介面，隔離即將拆分的邏輯。
- [ ] **基礎建設**：新服務的 CI/CD、Log、Monitor 環境已就緒。

#### Phase 2: Data Synchronization (資料同步)
- [ ] **啟動雙寫/CDC**：開始將資料同步到新資料庫。
- [ ] **歷史資料回填 (Backfill)**：將同步開啟前的舊資料搬移至新庫。
- [ ] **一致性驗證**：撰寫腳本比對新舊資料庫的筆數與內容（Checksum）。

#### Phase 3: Dark Launch & Switch (暗佈署與切換)
- [ ] **Shadow Traffic (影子流量)**：將請求複製一份發送給新服務（不回傳結果給用戶），觀察新服務的報錯率與效能。
- [ ] **Canary Release (金絲雀發布)**：將 1% -> 5% -> 20% 的 **讀取 (Read)** 流量切換至新服務。
- [ ] **Full Read Switch**：100% 讀取流量切換至新服務。
- [ ] **Write Switch (若適用)**：將寫入的主控權切換至新服務（舊系統改為呼叫新服務 API）。

#### Phase 4: Cleanup (清理)
- [ ] **Decommission**：移除舊系統中的相關程式碼。
- [ ] **Drop Tables**：備份後，移除舊資料庫中的相關 Table。

---

## Real-world Examples｜實戰案例

### Scenario: Extracting "User Service" from a PHP Monolith

**背景**：一個 10 年歷史的 PHP 單體電商系統，所有資料都在一個巨大的 MySQL `users` 表中，包含登入資訊、地址、積分等。目標是拆分出一個 Go 語言寫的 `User Service` (gRPC)。

#### Step 1: Stop the Bleeding (止血)
在 PHP 程式碼中，找出所有直接 SQL 查詢 `SELECT * FROM users` 的地方，封裝成一個 `UserRepository` Class。這是 PHP 端的 **ACL**。

#### Step 2: Dual Write (雙寫)
修改 PHP 的 `UserRepository::save()` 方法：
```php
function save($user) {
    // 1. Write to local Monolith DB (Source of Truth)
    $this->db->query("UPDATE users SET ...", $user);
    
    // 2. Async Fire-and-forget to new Service (or via Message Queue)
    // 這裡即使失敗也不拋出 Exception，避免影響主流程
    $this->messageQueue->publish("user.updated", $user);
}
```

#### Step 3: Backfill (回填)
撰寫一個 Script，讀取 PHP DB 的 `users` 表，將所有舊用戶資料透過 gRPC 寫入新的 Go User Service 資料庫。

#### Step 4: Verification (驗證)
在 Go Service 中實作一個「比對 API」。PHP 端的 `UserRepository::find()` 在讀取舊庫後，非同步呼叫 Go Service 進行比對。如果資料不一致，發送 Alert 到 Slack。

#### Step 5: Cut Over (切換讀取)
當一致性達到 99.999% 後，修改 PHP 的 `UserRepository::find()`：
```php
function find($id) {
    // Feature Flag 控制切換進度
    if ($this->featureFlag->isEnabled('use_new_user_service')) {
        return $this->grpcClient->getUser($id);
    }
    return $this->db->query("SELECT * FROM users WHERE id = ?", $id);
}
```

#### Step 6: Retire (退役)
確認運行一個月無誤後，移除 PHP 中直接存取 `users` 表的程式碼，`users` 表僅保留作為備份或唯讀用途，最終 Drop 掉。