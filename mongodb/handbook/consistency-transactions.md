# 一致性模型與交易機制 / Consistency Models & Transactions

## Mental model｜心智模型

在 MongoDB 中處理一致性（Consistency）與交易（Transactions）時，不能直接套用傳統 RDBMS 的思維。你需要建立以下兩個核心的心智模型：

### 1. 可調節的一致性頻譜 (The Spectrum of Tunable Consistency)
不同於傳統關聯式資料庫通常由全域設定決定隔離層級（Isolation Level），MongoDB 允許開發者在 **「每一次操作（Per-operation）」** 的層級上權衡 **延遲（Latency）** 與 **持久性/一致性（Durability/Consistency）**。

想像一個滑動條（Slider）：
- **左端（Fast & Loose）：** `Write Concern: w:1` + `Read Concern: local`。寫入只需 Primary 記憶體確認，讀取不保證資料已持久化。速度極快，但在故障轉移（Failover）時可能遺失資料。
- **右端 (Slow & Safe)：** `Write Concern: w:majority` + `Read Concern: majority` (or `linearizable`)。寫入需多數節點確認，讀取保證不會回滾（Rollback）。速度較慢，但資料絕對安全。

### 2. 原子性的邊界 (The Boundary of Atomicity)
- **Pre-v4.0 思維：** 原子性的邊界是 **單一文件（Single Document）**。Schema 設計必須將所有需要原子更新的欄位嵌入（Embed）在同一個文件中。
- **Post-v4.0 思維：** 原子性的邊界可以擴展到 **跨文件/跨集合（Multi-document/Cross-collection）**。但請記住，**「能用單一文件解決的，就不要用多文件交易」**。MongoDB 的交易機制是為了處理無法透過 Schema 優化解決的場景，而非預設選項。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 關鍵數據預設使用 `w:majority`
對於金融交易、庫存扣減或用戶權限變更，**必須**設定 `Write Concern: { w: "majority" }`。
- **Why:** 這是防止資料在 Primary 節點當機並發生故障轉移（Failover）時發生「回滾（Rollback）」的唯一保證。
- **Pattern:** 在連線字串（Connection String）層級設定預設值，特殊情況（如 Log 寫入）再於程式碼中覆寫為 `w:1`。

### 2. Causal Consistency (因果一致性) 的應用
當使用者執行「寫入後立即讀取（Read-your-own-writes）」的操作時（例如：更新個人簡介後刷新頁面），應使用 **Causal Consistency Session**。
- **How:** MongoDB Driver 預設在 Session 中開啟此功能。確保你的連續操作共用同一個 `ClientSession`。
- **Benefit:** 系統會保證讀取操作發生在寫入操作之後，即使讀取請求被路由到 Secondary 節點。

### 3. 交易重試機制 (Transaction Retry Logic)
MongoDB 的多文件交易可能會遇到 `TransientTransactionError`（例如鎖衝突或選舉發生）。應用層 **必須** 實作重試邏輯。
- **Pattern:** 不要手寫 `while` 迴圈，使用 Driver 提供的 `withTransaction` callback API，它內建了標準的重試機制與錯誤處理。

### 4. 讀寫分離的正確姿勢
如果你為了效能讀取 Secondary (`readPreference: secondary`)，請務必理解你可能會讀到「過期」或「即將回滾」的資料。
- **Best Practice:** 如果業務邏輯不能容忍髒讀（Dirty Reads），請堅持讀取 Primary。若必須讀 Secondary 且要求一致性，需搭配 `Read Concern: majority`，但這會增加 Secondary 的延遲等待。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 把 MongoDB 當作 RDBMS 使用 (The "RDBMS Lift-and-Shift")
- **Anti-pattern:** 在所有寫入操作外層都包上 `startTransaction` / `commitTransaction`。
- **Consequence:** 嚴重效能下降。MongoDB 的交易會產生全域邏輯時鐘（Logical Clock）開銷，並增加 WiredTiger 引擎的壓力。
- **Fix:** 優先優化 Schema 設計（Denormalization/Embedding），僅在真正需要跨 Collection 原子性時才使用交易。

### 2. 長時間運行的交易 (Long-running Transactions)
- **Anti-pattern:** 在交易區塊內進行 HTTP 請求、複雜運算或等待使用者輸入。
- **Consequence:**
  - 鎖定資源過久，阻塞其他操作。
  - **Oplog 壓力：** 未提交的交易會佔用 WiredTiger cache，且 MongoDB 預設交易超時僅為 60 秒。
- **Fix:** 保持交易極短（Short-lived）。準備好所有資料後再開啟交易，寫入完畢立即 Commit。

### 3. 忽略 `w:majority` 的隱性資料遺失
- **Pitfall:** 使用預設的 `w:1` 寫入訂單資料。Primary 收到寫入後立刻崩潰，尚未同步到 Secondary。新選出的 Primary 沒有這筆資料。
- **Result:** 用戶以為訂單成功，但資料庫中該訂單憑空消失。

### 4. DDL 操作混入交易
- **Pitfall:** 嘗試在交易內建立 Index 或建立 Collection。
- **Constraint:** MongoDB 的多文件交易主要支援 CRUD 操作。許多 DDL 操作（如 `createIndex`）在交易中是被禁止的或會導致鎖定問題。應在應用程式啟動時預先建立好 Schema 結構。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Should I use a Transaction? (我需要用交易嗎？)

1. **操作是否涉及多個文件？**
   - No → 使用單文件原子操作 (Standard CRUD)。
   - Yes → 前往步驟 2。
2. **能否透過嵌入 (Embedding) 合併為單一文件？**
   - Yes → 修改 Schema，使用單文件原子操作。
   - No → 前往步驟 3。
3. **業務是否容忍短暫的不一致 (Eventual Consistency)？**
   - Yes → 使用個別寫入，接受極短暫的資料差異。
   - No → **使用 ACID 多文件交易**。

### Implementation Checklist (實作檢查清單)

- [ ] **Write Concern:** 關鍵寫入是否已設定 `w:majority`？
- [ ] **Read Concern:** 交易內的讀取是否設定為 `snapshot` (Driver 通常預設處理)？
- [ ] **Retry Logic:** 是否使用了 Driver 的 `withTransaction` helper 或實作了針對 `TransientTransactionError` 與 `UnknownTransactionCommitResult` 的重試迴圈？
- [ ] **Timeouts:** 交易執行時間是否保證在 60 秒內？
- [ ] **Sharding:** (若使用分片叢集) 交易是否包含分片鍵（Shard Key）以優化路由？
- [ ] **Error Handling:** 是否正確捕捉並處理了 Commit 階段的網路錯誤？

---

## Real-world examples｜實戰案例

### Scenario 1: E-commerce Inventory & Order (電商庫存與訂單)

這是一個典型的 **「無法嵌入」** 場景，因為 `Products` 和 `Orders` 是兩個獨立增長的集合，且必須保持一致。

**Requirement:** 建立訂單時，必須同時扣減庫存。若庫存不足或訂單建立失敗，兩者皆須回滾。

**Pseudo-code (Node.js style):**

```javascript
const session = client.startSession();

// Step 1: Use withTransaction helper for automatic retries
await session.withTransaction(async () => {
  // Step 2: Check inventory with snapshot isolation
  // Important: Pass the 'session' to every operation
  const product = await productsCollection.findOne(
    { _id: productId, stock: { $gte: quantity } },
    { session }
  );

  if (!product) {
    throw new Error("Insufficient stock"); // Aborts transaction automatically
  }

  // Step 3: Decrement stock
  await productsCollection.updateOne(
    { _id: productId },
    { $inc: { stock: -quantity } },
    { session }
  );

  // Step 4: Create order
  await ordersCollection.insertOne(
    {
      productId: productId,
      quantity: quantity,
      status: "pending",
      createdAt: new Date()
    },
    { session }
  );
}, {
  // Step 5: Enforce strict consistency settings
  readPreference: 'primary',
  readConcern: { level: 'snapshot' }, // Consistent view across operations
  writeConcern: { w: 'majority' }     // Durable commit
});

// Step 6: End session
await session.endSession();
```

### Scenario 2: High-Volume Logging (高流量日誌)

**Requirement:** 記錄使用者點擊流（Clickstream），流量極大，允許極少量資料遺失，要求低延遲。

**Configuration:**
- **Write Concern:** `w: 0` (Fire and forget) 或 `w: 1` (Ack by primary only)。
- **Read Concern:** `local` (最快，不檢查多數節點)。
- **Strategy:** 完全不使用 Transaction。利用 `BulkWrite` 批次寫入來提升吞吐量。

### Scenario 3: User Profile Update (讀取自己的寫入)

**Requirement:** 用戶更新頭像後，立即導回首頁，首頁必須顯示新頭像。

**Configuration:**
- **Causal Consistency:**
  ```javascript
  // Client automatically tracks operation time (cluster time)
  const session = client.startSession({ causalConsistency: true });
  
  try {
    await users.updateOne({ _id: uid }, { $set: { avatar: "new.png" } }, { session });
    // The read is causally consistent with the previous write
    const user = await users.findOne({ _id: uid }, { session });
    return user;
  } finally {
    session.endSession();
  }
  ```