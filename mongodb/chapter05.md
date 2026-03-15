# 1. 前言與學習目標 (Introduction & Learning Objectives)

在早期的 MongoDB 版本中，「缺乏多文件交易（Multi-document Transactions）」常被視為其主要弱點。然而，隨著 v4.0 和 v4.2 的發布，MongoDB 已經支援了跨 Replica Set 甚至 Sharded Cluster 的 ACID 交易。對於資深工程師而言，挑戰不再是「能不能做」，而是「該不該做」以及「如何設定一致性級別（Consistency Levels）」。本章將深入探討如何在分散式環境下，透過 Write Concern 與 Read Concern 來權衡資料正確性與系統效能。

In early versions of MongoDB, the lack of multi-document transactions was often cited as a major weakness. However, with the release of v4.0 and v4.2, MongoDB introduced full ACID transaction support across Replica Sets and even Sharded Clusters. For Senior Engineers, the challenge is no longer "is it possible," but "should we do it" and "how to configure consistency levels." This chapter dives deep into balancing data correctness and system performance in a distributed environment using Write Concern and Read Concern.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精準評估交易需求**：分辨何時該依賴 Schema Design（單文件原子性）解決問題，何時必須引入 Multi-document Transactions。
    **Accurately assess transaction needs:** Distinguish when to rely on Schema Design (single-document atomicity) versus when to introduce Multi-document Transactions.
2.  **掌握一致性設定**：理解並應用 `Write Concern` 與 `Read Concern` 來實現強一致性（Strong Consistency）、因果一致性（Causal Consistency）或最終一致性（Eventual Consistency）。
    **Master consistency settings:** Understand and apply `Write Concern` and `Read Concern` to achieve Strong Consistency, Causal Consistency, or Eventual Consistency.
3.  **處理分散式挑戰**：在系統設計面試或實務中，解釋 MongoDB 在 CAP 定理中的位置，以及如何處理髒讀（Dirty Reads）與不可重複讀（Non-repeatable Reads）。
    **Handle distributed challenges:** Explain MongoDB's position in the CAP theorem during system design interviews or practice, and how to handle Dirty Reads and Non-repeatable Reads.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 單文件原子性 vs. 多文件交易 (Single-doc Atomicity vs. Multi-doc Transactions)

MongoDB 的核心哲學是「資料即文件（Data as Document）」。在大多數情況下，一個經過良好設計的 Document 包含了實體所需的所有資訊。MongoDB 保證對**單一文件**的操作（即使是更新多個欄位）是原子的（Atomic）。這與關聯式資料庫（RDBMS）預設依賴交易來串聯多個 Table 的思維不同。

MongoDB's core philosophy is "Data as Document." In most cases, a well-designed Document contains all the information an entity needs. MongoDB guarantees that operations on a **single document** (even updating multiple fields) are atomic. This differs from the RDBMS mindset, which defaults to relying on transactions to link multiple tables.

*   **Mental Model**:
    *   **Single-doc**: 就像把錢放進一個信封並封口。這是一個不可分割的動作，要嘛整個信封交出去，要嘛沒有。
    *   **Multi-doc Transaction**: 就像房屋買賣的託管（Escrow）。你需要同時協調買家付款、賣家交屋、銀行撥款。任何一個環節失敗，整個流程都必須回滾（Rollback）。這需要更高的協調成本（Coordination Cost）。
*   **Mental Model**:
    *   **Single-doc**: Like putting money in an envelope and sealing it. It's an indivisible action; either the whole envelope is delivered, or it isn't.
    *   **Multi-doc Transaction**: Like an escrow in real estate. You need to coordinate the buyer paying, the seller transferring the title, and the bank releasing funds simultaneously. If any part fails, the entire process must rollback. This incurs a higher Coordination Cost.

## 2.2 Write Concern & Read Concern

這是 MongoDB 控制一致性與可用性權衡的兩個旋鈕（Knobs）。

These are the two knobs MongoDB uses to control the trade-off between consistency and availability.

### Write Concern (`w`)
決定寫入操作需要多少個節點確認才算「成功」。
Determines how many nodes must acknowledge a write operation for it to be considered "successful."

*   `w: 1`: 只要 Primary 寫入記憶體即回傳成功。快，但不安全（Primary 崩潰可能掉資料）。
    `w: 1`: Returns success as soon as the Primary writes to memory. Fast, but unsafe (data loss possible if Primary crashes).
*   `w: majority`: 需要大多數節點（Primary + Secondaries）確認寫入 journal。慢，但保證資料不遺失且不會被回滾。
    `w: majority`: Requires a majority of nodes (Primary + Secondaries) to acknowledge writing to the journal. Slower, but guarantees data is durable and won't be rolled back.

### Read Concern
決定讀取操作可以讀到什麼樣狀態的資料。
Determines what state of data a read operation is allowed to see.

*   `local`: 讀取當前節點最新的資料（可能之後會被回滾）。
    `local`: Reads the most recent data on the current node (might be rolled back later).
*   `majority`: 只讀取那些「已被大多數節點確認」的資料。避免髒讀。
    `majority`: Only reads data that has been "acknowledged by a majority of nodes." Prevents dirty reads.
*   `snapshot`: 在交易中使用，保證讀取到特定時間點的一致快照。
    `snapshot`: Used within transactions, guarantees reading a consistent snapshot from a specific point in time.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 系統架構中的角色 (Role in System Architecture)

在微服務架構或大型分散式系統中，MongoDB 常被用作 Operational Data Store。資深工程師必須理解，開啟 ACID 交易並不是免費的午餐。

In microservices architectures or large distributed systems, MongoDB is often used as an Operational Data Store. Senior engineers must understand that enabling ACID transactions is not a free lunch.

*   **效能影響 (Performance Impact)**: 交易會佔用 WiredTiger 引擎的 Cache，並增加鎖競爭（Lock Contention）。如果交易執行時間過長，會導致 oplog 膨脹並影響 Replication Lag。
    **Performance Impact**: Transactions consume WiredTiger engine cache and increase Lock Contention. Long-running transactions can cause oplog bloat and impact Replication Lag.
*   **CAP 定理 (CAP Theorem)**: MongoDB 預設傾向於 CP（在 Partition 時保持一致性，若無法選出 Primary 則拒絕寫入）。使用 `w: majority` 強化了 C（Consistency），但會增加寫入延遲（Latency）。
    **CAP Theorem**: MongoDB defaults towards CP (maintaining Consistency during Partitions; refusing writes if no Primary can be elected). Using `w: majority` reinforces C (Consistency) but increases write Latency.

## 3.2 適用場景 (Use Cases)

1.  **金融帳務 (Financial Ledgers)**: 必須使用 Multi-document Transactions。例如：從帳戶 A 扣款並存入帳戶 B，這兩個 Document 必須同生共死。
    **Financial Ledgers**: Must use Multi-document Transactions. Example: Debiting Account A and crediting Account B; these two documents must succeed or fail together.
2.  **庫存管理 (Inventory Management)**: 高併發下的庫存扣減。雖然可以用原子操作 `$inc`，但若涉及訂單生成與庫存扣減跨不同 Collection，則需交易支援。
    **Inventory Management**: High-concurrency inventory deduction. While atomic `$inc` works, transactions are needed if order generation and inventory deduction span different collections.
3.  **非適用場景 (Anti-Use Cases)**: 日誌記錄、社群媒體按讚、感測器數據。這些場景對一致性要求低，使用 `w: 1` 換取高吞吐量是更好的選擇。
    **Anti-Use Cases**: Logging, social media likes, sensor data. These scenarios have low consistency requirements; using `w: 1` for high throughput is a better choice.

---

# 4. 逐步示例 (Walkthrough / Example)

## 情境：電子商務下單流程 (Scenario: E-commerce Checkout Flow)

我們需要建立一筆訂單（Order），同時扣減庫存（Inventory）。這兩個資料位於不同的 Collection。

We need to create an Order and simultaneously deduct Inventory. These two pieces of data reside in different Collections.

### 4.1 Naive Approach (Without Transactions)

```javascript
// 這是危險的做法 (This is risky)
await db.collection('inventory').updateOne(
  { _id: productId },
  { $inc: { qty: -1 } }
);
// 如果這裡程式崩潰或網路斷線... (If crash or network failure happens here...)
// 庫存扣了，但訂單沒建立 (Inventory deducted, but order not created)
await db.collection('orders').insertOne(orderData);
```

這種寫法在分散式系統中極易導致資料不一致（Data Inconsistency）。
This approach easily leads to Data Inconsistency in distributed systems.

### 4.2 Professional Approach (With ACID Transactions)

我們使用 MongoDB 的 Session 與 Transaction API 來確保原子性。注意我們設定了 `readConcern: snapshot` 與 `writeConcern: majority`。

We use MongoDB's Session and Transaction API to ensure atomicity. Note that we configure `readConcern: snapshot` and `writeConcern: majority`.

```javascript
const client = new MongoClient(uri);
await client.connect();

async function placeOrder(orderData, productId) {
  // 1. 開始一個 Session
  // 1. Start a Session
  const session = client.startSession();

  // 2. 設定交易選項
  // 2. Define transaction options
  const transactionOptions = {
    readPreference: 'primary',
    readConcern: { level: 'snapshot' },
    writeConcern: { w: 'majority' }
  };

  try {
    // 3. 使用 withTransaction Helper (自動處理重試邏輯)
    // 3. Use withTransaction Helper (handles retry logic automatically)
    await session.withTransaction(async () => {
      const inventoryCollection = client.db('shop').collection('inventory');
      const ordersCollection = client.db('shop').collection('orders');

      // 步驟 A: 檢查並扣減庫存
      // Step A: Check and deduct inventory
      const updateResult = await inventoryCollection.updateOne(
        { _id: productId, qty: { $gte: 1 } }, // 確保庫存足夠 (Ensure sufficient stock)
        { $inc: { qty: -1 } },
        { session }
      );

      if (updateResult.modifiedCount === 0) {
        throw new Error("Out of stock or product not found");
      }

      // 步驟 B: 建立訂單
      // Step B: Create order
      await ordersCollection.insertOne(orderData, { session });
      
      console.log("Transaction committed.");
    }, transactionOptions);

  } catch (e) {
    console.error("Transaction aborted due to error:", e);
    throw e;
  } finally {
    await session.endSession();
  }
}
```

### 4.3 關鍵細節 (Key Details)

*   **`withTransaction`**: 這是官方 Driver 提供的 Helper，它會自動處理 `UnknownTransactionCommitResult` 和 `TransientTransactionError` 等暫時性錯誤的重試，這在雲端環境極為重要。
    **`withTransaction`**: This is a helper provided by official drivers. It automatically handles retries for transient errors like `UnknownTransactionCommitResult` and `TransientTransactionError`, which is crucial in cloud environments.
*   **Session 傳遞**: 所有的 DB 操作都必須傳入 `{ session }` 物件，否則該操作會在交易之外執行。
    **Session Passing**: All DB operations must accept the `{ session }` object; otherwise, the operation will execute outside the transaction.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 錯誤：將 MongoDB 當作 RDBMS 使用 (Treating MongoDB like an RDBMS)
*   **描述**: 開發者習慣性地將所有寫入操作都包在 Transaction 中，即使是單一文件的寫入。
    **Description**: Developers habitually wrap all write operations in a Transaction, even for single-document writes.
*   **為何不好**: 交易會帶來顯著的延遲（Latency）與吞吐量（Throughput）懲罰。MongoDB 的單文件操作本身就是原子的，不需要額外的交易開銷。
    **Why it's bad**: Transactions incur significant Latency and Throughput penalties. MongoDB's single-document operations are inherently atomic and do not need the extra transaction overhead.
*   **修正**: 優先考慮 Schema Design（例如 Embedding），僅在確實需要跨多個 Documents 原子性時才使用交易。
    **Fix**: Prioritize Schema Design (e.g., Embedding) and only use transactions when atomicity across multiple Documents is strictly required.

## 5.2 錯誤：長運行交易 (Long-Running Transactions)
*   **描述**: 在交易區塊中執行耗時的運算、外部 API 呼叫或等待使用者輸入。
    **Description**: Performing time-consuming computations, external API calls, or waiting for user input within a transaction block.
*   **為何不好**: MongoDB 的交易有預設 60 秒的超時限制（`transactionLifetimeLimitSeconds`）。長時間持有鎖會阻塞其他操作，並導致 WiredTiger Cache 壓力過大。
    **Why it's bad**: MongoDB transactions have a default 60-second timeout (`transactionLifetimeLimitSeconds`). Holding locks for a long time blocks other operations and puts excessive pressure on the WiredTiger Cache.
*   **修正**: 保持交易邏輯極簡。先在交易外準備好資料，進入交易後只做 DB 讀寫，並盡快 Commit。
    **Fix**: Keep transaction logic minimal. Prepare data outside the transaction, and once inside, only perform DB reads/writes and Commit as quickly as possible.

## 5.3 錯誤：忽略 Write Conflict (Ignoring Write Conflict)
*   **描述**: 在高併發環境下，多個交易試圖修改同一份文件，導致 `WriteConflict` 錯誤，但程式碼沒有重試機制。
    **Description**: In high-concurrency environments, multiple transactions try to modify the same document, causing `WriteConflict` errors, but the code lacks a retry mechanism.
*   **修正**: 務必使用 Driver 提供的 `withTransaction` API 或手動實作重試迴圈。
    **Fix**: Always use the `withTransaction` API provided by the driver or manually implement a retry loop.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: MongoDB 既然是 NoSQL，它支援 ACID 嗎？如果不支援，你們系統如何處理金流？
**Since MongoDB is NoSQL, does it support ACID? If not, how does your system handle financial flows?**

*   **高分回答要點**:
    *   糾正觀念：MongoDB 自 4.0 起支援 Replica Set 交易，4.2 起支援 Sharded Cluster 交易，完全符合 ACID。
    *   實務策略：雖然支援，但我們傾向透過 Schema Design（Embedding）利用單文件原子性來優化效能。
    *   金流處理：對於必須跨帳戶的操作，我們會使用 `withTransaction` 配合 `w: majority` 確保資料不遺失且一致。
*   **Key Points for a High Score**:
    *   Correct the misconception: MongoDB supports Replica Set transactions since 4.0 and Sharded Cluster transactions since 4.2, fully compliant with ACID.
    *   Practical Strategy: While supported, we prefer optimizing performance via Schema Design (Embedding) to leverage single-document atomicity.
    *   Financial Flows: For operations requiring cross-account consistency, we use `withTransaction` combined with `w: majority` to ensure data durability and consistency.

## Q2: 請解釋 `Read Concern: Majority` 與 `Read Concern: Linearizable` 的差異？
**Explain the difference between `Read Concern: Majority` and `Read Concern: Linearizable`.**

*   **高分回答要點**:
    *   `Majority`: 保證讀到的資料已被寫入大多數節點（不會回滾），但不保證是「最新」的（可能讀到舊資料，若該節點尚未同步）。效能較好。
    *   `Linearizable`: 保證讀到絕對最新的資料（Real-time），就像只有一個節點一樣。代價極高，因為讀取時需要去確認所有節點狀態，會嚴重影響讀取延遲。
*   **Key Points for a High Score**:
    *   `Majority`: Guarantees the data read has been written to a majority of nodes (won't rollback), but doesn't guarantee it's the "newest" (might read stale data if the node hasn't synced yet). Better performance.
    *   `Linearizable`: Guarantees reading the absolute latest data (Real-time), as if there were only one node. Extremely high cost, as reading requires confirming status with nodes, severely impacting read latency.

## Q3: 在分散式系統中，如何實現「讀取自己的寫入（Read Your Own Writes）」？
**How do you achieve "Read Your Own Writes" in a distributed system?**

*   **高分回答要點**:
    *   這是「因果一致性（Causal Consistency）」的範疇。
    *   MongoDB 允許 Client 在 Session 中追蹤 `operationTime` 和 `clusterTime`。
    *   透過在 Session 中執行讀寫，MongoDB 會確保讀取操作發生在該 Session 之前的寫入操作之後，即使是在 Secondary 節點讀取。
*   **Key Points for a High Score**:
    *   This falls under "Causal Consistency."
    *   MongoDB allows Clients to track `operationTime` and `clusterTime` within a Session.
    *   By executing reads and writes within a Session, MongoDB ensures the read operation happens logically after the previous write in that Session, even when reading from a Secondary node.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)
1.  **單文件原子性是首選 (Single-doc atomicity is first choice)**: 總是先嘗試透過 Embedding 解決一致性問題，交易是最後手段。
2.  **ACID 交易已成熟 (ACID is mature)**: MongoDB 4.0+ 支援多文件交易，用法類似 SQL 但底層機制不同。
3.  **Write Concern 決定安全性 (Write Concern dictates safety)**: 用 `w: majority` 來防止資料在 Failover 時遺失。
4.  **Read Concern 決定隔離性 (Read Concern dictates isolation)**: 用 `snapshot` 隔離級別來避免髒讀與不可重複讀。
5.  **交易不是效能殺手，錯誤使用才是 (Transactions aren't performance killers, misuse is)**: 避免長交易，善用 `withTransaction` 處理重試。

## 後續延伸 (Next Steps)
*   **進階實作**: 嘗試在 Sharded Cluster 環境下設定交易，觀察效能變化（跨 Shard 交易成本更高）。
    **Advanced Practice**: Try configuring transactions in a Sharded Cluster environment and observe performance changes (Cross-shard transactions are more expensive).
*   **下一章預告**: 深入探討 **Aggregation Pipeline Optimization**，學習如何處理複雜的資料分析查詢而不拖垮資料庫。
    **Next Chapter Preview**: Deep dive into **Aggregation Pipeline Optimization**, learning how to handle complex analytical queries without crashing the database.