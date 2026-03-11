# 實戰維運與無停機遷移
# Production Readiness & Zero-downtime Migration

## 1. 前言與學習目標
## 1. Introduction & Learning Objectives

對於資深工程師而言，設計出完美的 Schema 只是工作的一半；另一半則是確保這些設計能在 Production 環境中長期穩定運行，並且在需要變更時，不會造成服務中斷。本章將焦點從「設計」轉向「維運」與「演進」。
For senior engineers, designing the perfect schema is only half the battle; the other half is ensuring these designs run stably in production and can evolve without service interruption. This chapter shifts the focus from "design" to "operations" and "evolution."

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **執行無停機 Schema 遷移（Zero-downtime Schema Migration）**：理解並實作針對海量資料表的 Online Schema Change 策略。
    **Execute Zero-downtime Schema Migration:** Understand and implement Online Schema Change strategies for massive tables.
2.  **設計雙寫遷移模式（Dual-write Migration Pattern）**：在涉及資料模型重構或資料庫拆分時，運用應用層雙寫策略來平滑過渡。
    **Design Dual-write Migration Patterns:** Apply application-level dual-write strategies to smoothly transition during data model refactoring or database splitting.
3.  **建立資料庫可觀測性（Database Observability）**：定義關鍵監控指標（Metrics），並建立慢查詢（Slow Query）分析與優化流程。
    **Establish Database Observability:** Define key monitoring metrics and establish processes for slow query analysis and optimization.

---

## 2. 核心觀念與心智模型
## 2. Core Concepts & Mental Model

### 2.1 心智模型：飛行中更換引擎
### 2.1 Mental Model: Changing the Engine Mid-flight

在開發環境（Dev）修改 DB Schema 就像把車停在車庫裡換輪胎；但在 Production 環境，尤其是高併發系統中，這就像在「飛行中更換引擎」。你不能讓飛機（服務）停下來，也不能讓乘客（使用者）感覺到顛簸。
Modifying a DB schema in a development environment is like changing a tire in a garage; however, in a production environment, especially in high-concurrency systems, it is like "changing the engine mid-flight." You cannot stop the plane (service), nor can you let the passengers (users) feel the turbulence.

### 2.2 鎖與延遲（Locks & Latency）
### 2.2 Locks & Latency

傳統的 `ALTER TABLE` 指令在某些資料庫（如舊版 MySQL）會鎖住整張表（Table Lock），導致所有寫入請求阻塞，進而引發應用程式連線池（Connection Pool）耗盡，造成全站當機。
Traditional `ALTER TABLE` commands in some databases (like older MySQL versions) can lock the entire table, blocking all write requests. This can lead to application connection pool exhaustion and cause a site-wide outage.

*   **Online Schema Change (OSC):** 利用「影子表（Shadow Table）」與「觸發器（Triggers）」或「Binlog 複製」技術，在背景複製資料，最後瞬間切換（Atomic Rename）。
    **Online Schema Change (OSC):** Uses "Shadow Table" and "Triggers" or "Binlog replication" techniques to copy data in the background, followed by an instantaneous switch (Atomic Rename).

### 2.3 雙寫模式（Dual-write Pattern）
### 2.3 Dual-write Pattern

當遷移不僅僅是加欄位，而是涉及邏輯變更（例如：拆分 Table、更換 DB 引擎）時，OSC 工具不足以應付。此時需要應用層介入。
When a migration involves more than just adding a column—such as logic changes (e.g., splitting a table, changing DB engines)—OSC tools are insufficient. Application-level intervention is required.

*   **定義**：應用程式同時寫入「舊資料源」與「新資料源」，以確保兩者資料一致，並透過 Feature Flag 逐步切換讀取流量。
    **Definition:** The application writes to both the "old data source" and the "new data source" simultaneously to ensure data consistency, gradually switching read traffic via Feature Flags.

---

## 3. 實務場景與系統設計視角
## 3. Real-World & System Design View

### 3.1 典型系統架構中的角色
### 3.1 Role in Typical System Architecture

在分散式系統中，API Server 與 Database 之間通常存在著緊密的耦合。
In distributed systems, there is often tight coupling between the API Server and the Database.

*   **Migration Worker / Script:** 負責執行背景資料回填（Backfill）的獨立服務，避免影響主要 API 的效能。
    **Migration Worker / Script:** An independent service responsible for executing background data backfill, avoiding impact on the performance of the main API.
*   **Observability Stack (e.g., Prometheus + Grafana):** 負責監控 DB 的 CPU、IOPS、Replication Lag 以及 Connection Pool 使用率。
    **Observability Stack (e.g., Prometheus + Grafana):** Responsible for monitoring DB CPU, IOPS, Replication Lag, and Connection Pool usage.

### 3.2 對系統品質的影響
### 3.2 Impact on System Quality

*   **Availability (可用性):** 透過無鎖遷移避免維護視窗（Maintenance Window），達成 99.99% 以上的 SLA。
    **Availability:** Avoiding maintenance windows through lock-free migration to achieve 99.99%+ SLA.
*   **Reliability (可靠性):** 雙寫模式提供了「回滾（Rollback）」的安全網。如果新 DB 有問題，只需關閉 Feature Flag 即可切回舊 DB。
    **Reliability:** The dual-write pattern provides a "rollback" safety net. If the new DB has issues, simply toggling the Feature Flag reverts to the old DB.

---

## 4. 逐步示例：應用層雙寫遷移策略
## 4. Walkthrough / Example: Application-Level Dual-Write Strategy

### 背景 (Context)
### Context

假設我們有一個單體資料庫中的 `Orders` 表，資料量已達 5TB。我們決定將 `Orders` 遷移到一個新的 Sharded Database 架構中（或是從 MySQL 遷移到 NoSQL）。我們不能停機。
Suppose we have an `Orders` table in a monolithic database with 5TB of data. We decided to migrate `Orders` to a new Sharded Database architecture (or from MySQL to NoSQL). We cannot afford downtime.

### 遷移五階段 (The 5 Phases of Migration)
### The 5 Phases of Migration

這是一個標準的 **Online Migration Strategy**，適用於大多數複雜的資料重構。
This is a standard **Online Migration Strategy**, applicable to most complex data refactorings.

#### Phase 1: 雙寫（Dual Write）
#### Phase 1: Dual Write

修改應用程式代碼，在寫入舊 DB (Source) 的同時，也寫入新 DB (Target)。
Modify application code to write to the new DB (Target) simultaneously while writing to the old DB (Source).

*   **關鍵點 (Key Point):** 寫入新 DB 失敗不應影響主流程（可透過 `try-catch` 吃掉異常或使用非同步佇列）。
    **Key Point:** Failure to write to the new DB should not affect the main flow (can be handled by `try-catch` or async queues).
*   **讀取 (Read):** 仍然 100% 讀取舊 DB。
    **Read:** Still 100% reading from the old DB.

```typescript
async function createOrder(orderData: Order): Promise<Order> {
  // 1. Write to Old DB (Source of Truth)
  const order = await oldDb.insertOrder(orderData);

  // 2. Dual Write to New DB (Best Effort)
  try {
    if (featureFlags.isEnabled('dual_write_orders')) {
       await newDb.insertOrder(orderData);
    }
  } catch (e) {
    // Log error but don't fail the request
    logger.warn('Dual write failed', e);
  }

  return order;
}
```

#### Phase 2: 歷史資料回填（Backfill）
#### Phase 2: Historical Data Backfill

啟動背景 Worker，將雙寫開始**之前**的歷史資料從舊 DB 複製到新 DB。
Start a background worker to copy historical data from the old DB to the new DB that existed **before** the dual-write started.

*   **挑戰 (Challenge):** 處理資料競爭（Race Conditions）。如果 Backfill 正在覆蓋一筆剛被應用程式更新的資料怎麼辦？
    **Challenge:** Handling Race Conditions. What if the backfill overwrites data that was just updated by the application?
*   **解法 (Solution):** 通常依賴 `updated_at` 時間戳記，或是使用 `INSERT IGNORE` / `UPSERT` 策略，確保新資料不會被舊的歷史資料覆蓋。
    **Solution:** Usually rely on `updated_at` timestamps, or use `INSERT IGNORE` / `UPSERT` strategies to ensure new data isn't overwritten by old historical data.

#### Phase 3: 資料驗證與比較（Validation / Parity Check）
#### Phase 3: Validation / Parity Check

資料回填完成後，開啟「讀取比較（Read Diff）」模式。
After backfill is complete, enable "Read Diff" mode.

*   應用程式同時讀取新舊 DB，比較結果是否一致，但不回傳新 DB 的結果給使用者。
    The application reads from both DBs, compares if the results match, but does not return the new DB's result to the user.
*   修復任何發現的資料不一致。
    Fix any data inconsistencies found.

#### Phase 4: 切換讀取（Switch Reads）
#### Phase 4: Switch Reads

透過 Feature Flag，逐步將讀取流量切換到新 DB（Canary Release）。
Gradually switch read traffic to the new DB via Feature Flags (Canary Release).

*   1% -> 10% -> 50% -> 100%。
    1% -> 10% -> 50% -> 100%.
*   此時，Source of Truth 變更為新 DB。
    At this point, the Source of Truth changes to the new DB.

#### Phase 5: 停止雙寫與清理（Stop Dual Write & Cleanup）
#### Phase 5: Stop Dual Write & Cleanup

確認系統穩定運行一段時間後，停止寫入舊 DB，並移除舊的程式碼路徑。
After confirming the system is stable for a period, stop writing to the old DB and remove the old code paths.

---

## 5. 常見錯誤與反模式
## 5. Common Pitfalls & Anti-patterns

### 5.1 依賴 ORM 的自動遷移
### 5.1 Relying on ORM Auto-migrations

*   **錯誤 (Pitfall):** 在 Production 啟動時讓 ORM（如 Hibernate, TypeORM, Django ORM）自動執行 `sync` 或 `alter table`。
    **Pitfall:** Letting ORM (like Hibernate, TypeORM, Django ORM) automatically execute `sync` or `alter table` upon production startup.
*   **後果 (Consequence):** 對於大表可能導致長時間鎖表，甚至因為多個 Instance 同時啟動而造成 Race Condition。
    **Consequence:** Can cause long table locks on large tables, or even race conditions if multiple instances start simultaneously.
*   **修正 (Correction):** 使用專門的 Migration 工具（如 Flyway, Liquibase），並將 Schema 變更與程式碼部署分離。對於大表，使用 `gh-ost` 或 `pt-online-schema-change`。
    **Correction:** Use dedicated migration tools (like Flyway, Liquibase) and decouple schema changes from code deployment. For large tables, use `gh-ost` or `pt-online-schema-change`.

### 5.2 忽略 Replication Lag
### 5.2 Ignoring Replication Lag

*   **錯誤 (Pitfall):** 在寫入 Primary 後，立即從 Read Replica 讀取資料。
    **Pitfall:** Reading from a Read Replica immediately after writing to the Primary.
*   **後果 (Consequence):** 使用者看到舊資料（Stale Read），導致體驗不佳或邏輯錯誤。
    **Consequence:** Users see stale data, leading to poor experience or logic errors.
*   **修正 (Correction):** 實作「寫後讀（Read-your-writes）」一致性，例如強制剛寫入的使用者在短時間內讀取 Primary，或使用快取層。
    **Correction:** Implement "Read-your-writes" consistency, such as forcing users who just wrote data to read from the Primary for a short time, or using a caching layer.

### 5.3 缺乏慢查詢監控
### 5.3 Lack of Slow Query Monitoring

*   **錯誤 (Pitfall):** 等到 CPU 100% 或服務 Timeout 才發現某個 SQL 語句沒吃到 Index。
    **Pitfall:** Waiting until CPU hits 100% or services timeout to discover a SQL statement missed an index.
*   **修正 (Correction):** 設定 `long_query_time`（例如 1s 或 200ms），並定期 Review 慢查詢日誌（Slow Query Log）。在 CI/CD 階段引入 SQL Linter 或 `EXPLAIN` 檢查。
    **Correction:** Set `long_query_time` (e.g., 1s or 200ms) and regularly review Slow Query Logs. Introduce SQL Linters or `EXPLAIN` checks in the CI/CD pipeline.

---

## 6. 面試與實務問答切入點
## 6. Interview & Discussion Hooks

### Q1: 如何在不鎖表的情況下為一張 10 億行的表新增欄位？
### Q1: How do you add a column to a 1-billion-row table without locking it?

*   **高分回答要點 (Key Points):**
    *   提到直接 `ALTER` 的風險（Table Lock）。
    *   解釋 **Online Schema Change** 原理：建立新表結構 -> 雙寫/觸發器同步增量資料 -> 背景複製歷史資料 -> 原子切換（Atomic Swap）。
    *   提及工具：MySQL 的 `gh-ost`（無 Trigger，基於 Binlog，負載更低）或 `pt-online-schema-change`。
    *   提及 PostgreSQL 的 `CREATE INDEX CONCURRENTLY` 等特性。

### Q2: 我們需要將 User ID 從 Int32 升級為 Int64，這涉及到多個表的外鍵，你會怎麼做？
### Q2: We need to upgrade User ID from Int32 to Int64, involving foreign keys across multiple tables. How would you approach this?

*   **高分回答要點 (Key Points):**
    *   這是一個破壞性變更（Breaking Change），不能簡單 ALTER。
    *   **策略：** 新增一個 `user_id_v2` (Int64) 欄位。
    *   **步驟：** 雙寫（同時寫入 v1 和 v2）-> Backfill 舊資料 -> 切換讀取代碼使用 v2 -> 廢棄 v1。
    *   強調這是一個漫長的過程，需要代碼相容性（Compatibility）。

### Q3: 資料庫 CPU 突然飆高到 100%，你會如何排查？
### Q3: Database CPU suddenly spikes to 100%. How do you troubleshoot?

*   **高分回答要點 (Key Points):**
    *   **止血 (Mitigation):** 是否有剛上線的代碼？考慮 Rollback。是否有異常流量？考慮限流（Rate Limiting）。
    *   **分析 (Analysis):** 查看 `SHOW PROCESSLIST` (MySQL) 或 `pg_stat_activity` (PostgreSQL) 找出當前執行的 Query。
    *   **兇手 (Culprit):** 通常是 Full Table Scan、缺少 Index、或是 N+1 Query 問題。
    *   **長期 (Long-term):** 建立慢查詢監控與警報。

---

## 7. 小結與後續延伸
## 7. Summary & Next Steps

### 記憶錨點 (Key Takeaways)
1.  **Online Schema Change (OSC)** 是處理大表變更的標準手段，避免鎖表導致的停機。
2.  **雙寫模式 (Dual-write Pattern)** 是應用層遷移的核心，包含「雙寫、回填、驗證、切換、清理」五個步驟。
3.  **Feature Flags** 是控制遷移風險的關鍵開關，允許隨時回滾。
4.  **可觀測性 (Observability)** 必須包含慢查詢日誌與連線池監控，這是 Production Ready 的底線。
5.  **Replication Lag** 是讀寫分離架構中常見的陷阱，需在設計 API 時考慮一致性需求。

### 後續延伸 (Next Steps)
*   **進階閱讀:** 研究 `gh-ost` 的架構原理（如何模擬 Replica 讀取 Binlog）。
*   **下一章預告:** 當單機 DB 優化到極致仍無法支撐時，我們需要進入 **Database Sharding & Partitioning**（資料庫分片與分區）。
*   **Next Chapter Preview:** When a single DB is optimized to the limit but still cannot support the load, we need to move into **Database Sharding & Partitioning**.