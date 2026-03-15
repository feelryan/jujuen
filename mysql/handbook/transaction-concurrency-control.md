# 交易並發與鎖機制除錯 | Transactions, Concurrency & Locking Debugging

## Mental model｜心智模型

要掌握 MySQL (InnoDB) 的並發控制，不能只將其視為簡單的「鎖住一行資料」。你需要建立以下兩個核心視角：

### 1. MVCC 是「時光機」 (Git for Data)
InnoDB 使用 **MVCC (Multi-Version Concurrency Control)** 來處理讀寫並發。
- 想像每一行資料都有多個「版本」 (Undo Log)。
- **快照讀 (Snapshot Read)**：普通的 `SELECT` 就像 `git checkout <commit-hash>`，讀取的是交易開始那一刻的資料快照，完全不加鎖，也不會被寫入操作阻塞。
- **當前讀 (Current Read)**：`SELECT ... FOR UPDATE`、`UPDATE`、`DELETE` 則是讀取「最新版本」，並且會加鎖。

### 2. 鎖是加在「索引」上的，不只是資料行
這是最常被誤解的概念。**InnoDB 的鎖是鎖在 Index Record 上，而非實體資料行。**
- **Record Lock**：鎖住索引紀錄本身。
- **Gap Lock**：鎖住索引之間的「間隙」（防止別人插入新資料，導致 Phantom Read）。
- **Next-Key Lock**：Record Lock + Gap Lock。

> **The Mental Shift**: 當你除錯 Deadlock 時，不要只看「他改了哪一行」，要看「他的 `WHERE` 條件掃描了哪些**索引區間**」。如果 `WHERE` 條件沒有走索引，MySQL 會退化成鎖住全表（或是鎖住所有掃描過的行），這就是災難的開始。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 隔離級別的選擇：RR vs. RC
MySQL 預設是 **Repeatable Read (RR)**，但許多高並發系統（如電商秒殺）會選擇 **Read Committed (RC)**。
- **Repeatable Read (RR)**：保證同一交易內讀取一致，但為了防止幻讀 (Phantom Read)，會大量使用 **Gap Lock**。這常是 Deadlock 的元兇。
- **Read Committed (RC)**：只鎖定實際命中的紀錄，**沒有 Gap Lock**。
  - **Best Practice**: 如果你的應用程式能容忍「不可重複讀」（同一個交易內兩次 SELECT 結果不同），且深受 Deadlock 之苦，將隔離級別改為 `READ-COMMITTED` 是一個有效的優化手段。

### 2. 交易範圍最小化 (Keep Transactions Short)
交易持有的鎖，只有在 `COMMIT` 或 `ROLLBACK` 時才會釋放。
- **Pattern**:
  1.  **準備數據**：在交易外完成所有運算、參數驗證。
  2.  **開啟交易**。
  3.  **執行 SQL**：快速執行 Insert/Update。
  4.  **提交交易**。
- **Anti-Pattern**: 在交易內進行 HTTP 請求、複雜運算或檔案 I/O。

### 3. 悲觀鎖與樂觀鎖的選擇
- **悲觀鎖 (Pessimistic Locking)**：`SELECT ... FOR UPDATE`。
  - 適用於：寫入衝突機率高、強一致性要求（如庫存扣減）。
  - **注意**：務必確保 `WHERE` 走唯一索引 (Unique Index)，否則會鎖住範圍。
- **樂觀鎖 (Optimistic Locking)**：使用 `version` 欄位。
  - SQL: `UPDATE table SET val = new_val, ver = ver + 1 WHERE id = ? AND ver = old_ver`
  - 適用於：讀多寫少、衝突機率低的情境。

### 4. 固定順序存取資源 (Canonical Ordering)
Deadlock 最常見的原因是兩個交易以相反順序獲取資源。
- **Pattern**: 總是按照 ID 排序來鎖定資源。
  - ❌ Transaction A: Lock User(1) -> Lock User(2); Transaction B: Lock User(2) -> Lock User(1)
  - ✅ 兩者都強制：Lock User(1) -> Lock User(2)

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 隱式鎖升級 (Lock Escalation via Table Scans)
- **情境**：`UPDATE users SET active = 0 WHERE name = 'Alice';`
- **陷阱**：如果 `name` 欄位**沒有索引**，InnoDB 會掃描全表，並對**每一行**（甚至間隙）加鎖。這會導致整張表無法寫入，直到交易結束。
- **後果**：系統瞬間停擺 (Lock Wait Timeout)。

### 2. 忽略 Gap Lock 的存在 (The "Insert" Deadlock)
- **情境**：在 RR 級別下，兩個交易同時試圖插入同一範圍的數據，或者執行 `SELECT ... FOR UPDATE` 查詢不存在的紀錄。
- **陷阱**：查詢不存在的紀錄會產生 Gap Lock。如果兩個交易都持有同一個 Gap 的 Shared Lock (S-Lock)，然後都想插入數據（需要 X-Lock），就會發生 Deadlock。

### 3. 在交易中呼叫外部服務 (Network Calls inside Transaction)
- **情境**：
  ```python
  with db.transaction():
      user.save()
      email_service.send_welcome_email() # 這是地雷！
  ```
- **陷阱**：如果 Email 服務回應慢（例如 5秒），資料庫連線和鎖就會被佔用 5秒。並發一高，DB 連線池瞬間耗盡。

### 4. 大批次更新 (Massive Batch Updates)
- **情境**：`DELETE FROM logs WHERE created_at < '2023-01-01'` (刪除 100 萬筆)。
- **陷阱**：這會產生巨大的 Undo Log，佔用大量鎖資源，並可能觸發 `max_allowed_packet` 或鎖表。
- **解法**：分批處理 (Chunking)，每次刪除 1000 筆，中間 `sleep` 釋放資源。

---

## Checklists & workflows｜檢查清單與流程

### 🚨 Emergency Troubleshooting Workflow (發生鎖死時)

1.  **查看當前鎖狀態 (MySQL 8.0+)**：
    ```sql
    SELECT * FROM performance_schema.data_locks;
    SELECT * FROM performance_schema.data_lock_waits;
    ```
2.  **查看正在運行的交易**：
    ```sql
    SELECT * FROM information_schema.innodb_trx \G;
    -- 重點看 trx_mysql_thread_id (processlist id) 和 trx_query (正在執行的 SQL)
    ```
3.  **分析最近一次 Deadlock**：
    ```sql
    SHOW ENGINE INNODB STATUS \G;
    -- 搜尋 "LATEST DETECTED DEADLOCK" 區塊
    ```
4.  **緊急處置**：
    - 找到阻塞源頭的 `trx_mysql_thread_id`，執行 `KILL <thread_id>;`。

### ✅ Code Review Checklist (開發階段)

- [ ] **索引檢查**：所有 `UPDATE` 和 `DELETE` 語句的 `WHERE` 條件是否都命中了索引？(Explain 確認 type 不是 ALL)。
- [ ] **交易長度**：交易內部是否只包含必要的 DB 操作？有無外部 API 呼叫或複雜計算？
- [ ] **鎖定順序**：涉及多張表或多行操作時，是否保證了固定的加鎖順序？
- [ ] **隔離級別**：如果業務允許，是否考慮使用 `READ COMMITTED` 來減少 Gap Lock？
- [ ] **For Update 使用**：使用 `SELECT ... FOR UPDATE` 時，是否針對了具體的 Primary Key 或 Unique Key？(避免範圍鎖)。

---

## Real-world examples｜實戰案例

### 案例 1：經典的 "Upsert" Deadlock (Gap Lock 陷阱)

**場景**：高並發下，檢查使用者是否存在，不存在則建立。

**有問題的代碼 (Pseudo-code)**：
```sql
-- Transaction A & B running concurrently in RR isolation
START TRANSACTION;
SELECT * FROM users WHERE email = 'test@example.com' FOR UPDATE;
-- 如果回傳空 (Empty Set)，MySQL 會在 email 索引上加 Gap Lock
-- 此時 A 和 B 都拿到了 Gap S-Lock (共享鎖，允許並存)

INSERT INTO users (email) VALUES ('test@example.com');
-- A 嘗試 Insert，需要 X-Lock (排他鎖)。
-- 但 B 持有 S-Lock，A 必須等待 B 釋放。
-- B 也嘗試 Insert，也需要 X-Lock，但也被 A 的 S-Lock 卡住。
-- BOOM! Deadlock.
COMMIT;
```

**解決方案**：
1.  使用 `INSERT IGNORE` 或 `INSERT ... ON DUPLICATE KEY UPDATE` (原子操作)。
2.  或者，先用普通 `SELECT` (快照讀) 檢查，若無則 `INSERT` (依賴 Unique Index 報錯來處理並發)，捕獲 Duplicate Key Error 後重試。

### 案例 2：遺失的索引導致全表鎖死

**場景**：一個後台排程任務，清理過期訂單。

**SQL**：
```sql
-- `status` 欄位有索引，但 `order_date` 沒有索引
UPDATE orders SET status = 'archived' 
WHERE status = 'closed' AND order_date < '2023-01-01';
```

**問題**：
雖然 `status` 有索引，但如果 `status='closed'` 的資料量很大（例如佔全表 50%），MySQL 優化器可能會放棄使用索引，轉而進行 Clustered Index Scan (全表掃描)。
這會導致**整張表的所有記錄都被加鎖**，前台用戶無法下單，系統呈現假死狀態。

**解決方案**：
1.  為 `(status, order_date)` 建立聯合索引 (Composite Index)。
2.  使用 `LIMIT` 分批更新，避免一次鎖定太多行。
3.  在低峰期執行。

### 案例 3：N+1 查詢與長交易

**場景**：ORM 框架常見錯誤。

```python
# 開啟交易
with transaction():
    orders = Order.objects.filter(status='pending') # SELECT
    for order in orders:
        # 這裡對每一筆訂單進行處理，可能包含複雜邏輯
        process_order(order) 
        order.status = 'processed'
        order.save() # UPDATE
```

**問題**：
如果 `orders` 有 1000 筆，這會變成一個超長交易。鎖定的資源會隨著迴圈進行越來越多，直到最後才釋放。這極易造成 Lock Wait Timeout。

**解決方案**：
將交易範圍縮小到單筆訂單處理，或者使用批量更新 `UPDATE orders SET ... WHERE id IN (...)`，避免在應用層迴圈中長時間持有連線。