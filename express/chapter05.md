# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，Express 不僅僅是一個路由框架，更是資料流（Data Flow）的協調者。在處理高併發或大數據量的場景時，單純的 `await db.query()` 往往是效能瓶頸與記憶體洩漏的元兇。本章將深入探討如何優雅地管理資料庫連線與資料流。

For senior engineers, Express is not just a routing framework but an orchestrator of data flow. In high-concurrency or large-dataset scenarios, a simple `await db.query()` is often the culprit behind performance bottlenecks and memory leaks. This chapter delves into elegantly managing database connections and data streams.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精準控制連線池（Connection Pooling）：** 理解如何配置與監控 DB Pool Size，避免 "Connection Exhaustion" 與 "Thundering Herd" 問題。
    **Precisely control Connection Pooling:** Understand how to configure and monitor DB Pool Size to avoid "Connection Exhaustion" and "Thundering Herd" problems.
2.  **實作強健的交易機制（Robust Transactions）：** 在非同步環境（Async/Await）中正確管理 ACID 交易，確保在錯誤發生時能正確 Rollback 並釋放連線資源。
    **Implement Robust Transactions:** Correctly manage ACID transactions in an asynchronous environment (Async/Await), ensuring proper Rollback and resource release upon errors.
3.  **利用 Streams 處理海量資料（Handle Massive Data with Streams）：** 使用 Node.js Streams 實現 ETL（Extract, Transform, Load）風格的 API 回應，解決大檔案上傳與匯出的記憶體溢位（OOM）風險。
    **Handle Massive Data with Streams:** Use Node.js Streams to implement ETL-style API responses, solving Out-of-Memory (OOM) risks during large file uploads and exports.
4.  **掌握背壓機制（Master Backpressure）：** 理解並處理 Stream 的背壓，防止快速的資料來源壓垮慢速的客戶端。
    **Master Backpressure:** Understand and handle stream backpressure to prevent fast data sources from overwhelming slow clients.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 連線池與多工處理 (Connection Pooling & Multiplexing)

**心智模型：** 想像資料庫連線池是一個「計程車排班站」。
**Mental Model:** Imagine the database connection pool as a "taxi dispatch station."

Express 伺服器收到成千上萬個請求（乘客），但資料庫只能同時處理有限的連線（計程車）。如果每個請求都嘗試建立一個新的 TCP 連線（買一台新車），系統會因握手開銷（Handshake overhead）而崩潰。連線池維護一組已建立的連線，請求必須「借用（Checkout）」連線，用完後「歸還（Release）」。

The Express server receives thousands of requests (passengers), but the database can only handle a limited number of concurrent connections (taxis). If every request tries to establish a new TCP connection (buying a new car), the system will collapse due to handshake overhead. The connection pool maintains a set of established connections; requests must "checkout" a connection and "release" it when done.

**關鍵差異：**
*   **Stateless Query:** 可以直接使用 Pool 的輔助方法（如 `pool.query()`），它會自動借用並歸還。
*   **Stateful Transaction:** 必須顯式地借出同一個 Client 實例（`pool.connect()`），在該實例上執行 `BEGIN`, `COMMIT`, `ROLLBACK`，最後手動歸還。這是資深工程師常犯錯的地方。

**Key Distinction:**
*   **Stateless Query:** Can use the Pool helper directly (e.g., `pool.query()`), which automatically checks out and releases.
*   **Stateful Transaction:** Must explicitly checkout the *same* Client instance (`pool.connect()`), execute `BEGIN`, `COMMIT`, `ROLLBACK` on that instance, and manually release it. This is a common pitfall for engineers.

## 2.2 Streams 與背壓 (Streams & Backpressure)

**心智模型：** 想像水管系統（Piping System）。
**Mental Model:** Imagine a water piping system.

傳統的 `fs.readFile` 或 `db.query` 就像是用水桶裝水：必須把水桶裝滿（載入記憶體）才能倒給使用者。Streams 則是接水管：水（資料）一滴一滴流過，不需要巨大的水桶。

Traditional `fs.readFile` or `db.query` is like using a bucket: you must fill the bucket (load into memory) before pouring it for the user. Streams are like pipes: water (data) flows drop by drop, requiring no massive bucket.

**背壓（Backpressure）：** 當出水管（Client 網速）比進水管（DB 讀取速度）慢時，水管會積水。Node.js 的 `pipe()` 機制會自動偵測這種情況，暫停 DB 讀取，直到 Client 消化完緩衝區的資料。

**Backpressure:** When the drain pipe (Client network speed) is slower than the inlet pipe (DB read speed), water builds up. Node.js's `pipe()` mechanism automatically detects this, pausing the DB read until the Client consumes the buffered data.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 典型架構中的角色 (Role in Typical Architecture)

在 Production 環境中，Express 通常位於 Load Balancer 之後，資料庫之前。

In a production environment, Express typically sits behind a Load Balancer and in front of the Database.

*   **無狀態層（Stateless Layer）：** Express 實例可以水平擴展（Scale Out）。
*   **資源限制（Resource Constraints）：** 雖然 Express 可以擴展，但資料庫的連線數是硬限制（Hard Limit）。
    *   如果你有 10 個 Express Pods，每個 Pod 的 Pool Size 設為 50，那麼 DB 必須承受 500 個併發連線。
    *   **設計決策：** Pool Size 的設定必須經過計算：`Pool Size = (Total DB Connections / Number of Instances) * Safety Factor`。

*   **Stateless Layer:** Express instances can scale out.
*   **Resource Constraints:** While Express scales, database connections are a hard limit.
    *   If you have 10 Express Pods, and each Pod has a Pool Size of 50, the DB must withstand 500 concurrent connections.
    *   **Design Decision:** Pool Size configuration must be calculated: `Pool Size = (Total DB Connections / Number of Instances) * Safety Factor`.

## 3.2 可觀測性與安全性 (Observability & Security)

*   **Slow Query Logging:** 在 Express 中介軟體或 DB Driver 層級攔截超過閾值的查詢。
*   **Timeouts:** 永遠不要讓查詢無限期執行。設定 `statement_timeout` (Postgres) 或 Driver 層級的 timeout，防止單一請求卡死 Event Loop 或佔用連線。
*   **Memory Impact:** 使用 Stream 處理 CSV 匯出或大 JSON 回應，是防止 Node.js 發生 `Heap Out of Memory` 崩潰的標準解法。

*   **Slow Query Logging:** Intercept queries exceeding thresholds at the Express middleware or DB Driver level.
*   **Timeouts:** Never let a query run indefinitely. Set `statement_timeout` (Postgres) or Driver-level timeouts to prevent a single request from blocking the Event Loop or holding a connection.
*   **Memory Impact:** Using Streams for CSV exports or large JSON responses is the standard solution to prevent Node.js `Heap Out of Memory` crashes.

---

# 4. 逐步示例 (Walkthrough / Example)

以下範例使用 `pg` (node-postgres) 驅動，這是 Node.js 生態系中最底層且高效的 PostgreSQL 客戶端，許多 ORM (TypeORM, Prisma, MikroORM) 底層皆基於此。

The following examples use the `pg` (node-postgres) driver, the most low-level and efficient PostgreSQL client in the Node.js ecosystem, upon which many ORMs (TypeORM, Prisma, MikroORM) are built.

## 4.1 範例一：強健的交易管理 (Robust Transaction Management)

**情境：** 使用者轉帳，需要扣除 A 帳戶餘額並增加 B 帳戶餘額。這兩個操作必須是原子的（Atomic）。

**Scenario:** User transfer. Deduct balance from Account A and add to Account B. These two operations must be atomic.

```javascript
import { Pool } from 'pg';

const pool = new Pool({
  max: 20, // Max clients in the pool
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

export const transferFunds = async (fromId, toId, amount) => {
  // 1. Checkout a dedicated client from the pool
  // 注意：不能直接用 pool.query，因為我們需要跨多個查詢維持同一個 session
  const client = await pool.connect();

  try {
    // 2. Start Transaction
    await client.query('BEGIN');

    // 3. Operation A: Deduct
    const resA = await client.query(
      'UPDATE accounts SET balance = balance - $1 WHERE id = $2 RETURNING balance',
      [amount, fromId]
    );
    
    if (resA.rows.length === 0) throw new Error('Account not found');
    if (resA.rows[0].balance < 0) throw new Error('Insufficient funds');

    // 4. Operation B: Add
    await client.query(
      'UPDATE accounts SET balance = balance + $1 WHERE id = $2',
      [amount, toId]
    );

    // 5. Commit Transaction
    await client.query('COMMIT');
    return { success: true };

  } catch (e) {
    // 6. Rollback on Error
    await client.query('ROLLBACK');
    console.error('Transaction Failed:', e);
    throw e; // Re-throw for Express error handler
  } finally {
    // 7. CRITICAL: Release client back to the pool
    // 如果忘記這行，連線將永遠被佔用，最終導致服務不可用
    client.release();
  }
};
```

**為何這樣做可行？**
*   `pool.connect()` 確保我們拿到一個獨佔的連線。
*   `try/catch/finally` 確保無論成功或失敗，連線都會被釋放（Release）。這是最關鍵的一步。

**Why this works:**
*   `pool.connect()` ensures we get an exclusive connection.
*   `try/catch/finally` ensures the connection is released regardless of success or failure. This is the most critical step.

## 4.2 範例二：高效能資料流匯出 (High-Performance Data Streaming)

**情境：** 管理員需要下載包含 100 萬筆交易紀錄的 CSV 報表。
**Scenario:** An admin needs to download a CSV report containing 1 million transaction records.

**Naive Approach (Bad):**
`const rows = await db.query('SELECT * ...');` -> Load 1GB into RAM -> `res.json(rows)`.
這會導致 Server 記憶體暴增，甚至 Crash。

**Streaming Approach (Good):**
使用 `pg-query-stream` 配合 Node.js Pipeline。

```javascript
import QueryStream from 'pg-query-stream';
import { pipeline } from 'stream/promises'; // Node 15+
import { Transform } from 'stream';

// Express Handler
app.get('/api/reports/transactions', async (req, res) => {
  const client = await pool.connect();
  
  try {
    // 1. Setup the query stream
    // batchSize controls how many rows are kept in memory at once
    const query = new QueryStream('SELECT * FROM transactions', [], { batchSize: 100 });
    const dbStream = client.query(query);

    // 2. Transform Stream: Object to CSV String
    const jsonToCsv = new Transform({
      writableObjectMode: true, // Input is Object (DB Row)
      readableObjectMode: false, // Output is String/Buffer
      transform(row, encoding, callback) {
        // Simple CSV formatting (in production, use a library like 'csv-stringify')
        const csvLine = `${row.id},${row.amount},${row.date}\n`;
        callback(null, csvLine);
      }
    });

    // 3. Set Headers for Download
    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', 'attachment; filename="transactions.csv"');

    // 4. Pipeline: DB -> Transform -> Response
    // pipeline handles error propagation and cleanup automatically
    await pipeline(
      dbStream,
      jsonToCsv,
      res
    );

  } catch (err) {
    console.error('Streaming failed', err);
    // Note: If headers are already sent, you can't send a JSON error response here.
    // You might need to destroy the stream.
    if (!res.headersSent) res.status(500).send('Export failed');
  } finally {
    client.release(); // Always release!
  }
});
```

**技術亮點 (Technical Highlights):**
*   **Backpressure:** 如果使用者下載速度慢，`res` (Writable Stream) 會發訊號給 `jsonToCsv`，進而傳遞給 `dbStream`，資料庫游標（Cursor）會暫停讀取。
*   **Memory Efficiency:** 記憶體中同時只會有 `batchSize` (100) 筆資料，而非 100 萬筆。

**Technical Highlights:**
*   **Backpressure:** If the user's download speed is slow, `res` (Writable Stream) signals `jsonToCsv`, which propagates to `dbStream`, causing the database cursor to pause reading.
*   **Memory Efficiency:** Only `batchSize` (100) records exist in memory at any time, not 1 million.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 殭屍連線 (The Zombie Client)

**錯誤描述：** 在 `try/catch` 中處理了錯誤，但忘記在 `finally` 區塊中呼叫 `client.release()`，或者在 `catch` 中直接 `return` 而跳過了釋放邏輯。
**後果：** 連線池很快被耗盡，新的請求會無限期等待連線（Pending），導致服務停擺。

**Description:** Handling errors in `try/catch` but forgetting to call `client.release()` in the `finally` block, or returning directly inside `catch`, skipping the release logic.
**Consequence:** The connection pool is quickly exhausted; new requests wait indefinitely (Pending), causing service outage.

## 5.2 巢狀交易地獄 (Nested Transaction Hell)

**錯誤描述：** 在一個已經開啟交易的函數中，呼叫另一個也會開啟交易的函數（`BEGIN` 內包 `BEGIN`）。
**修正：** 大多數 SQL 資料庫不支援真正的巢狀交易（Nested Transactions），通常需要使用 `SAVEPOINT`。較佳的實務是將「業務邏輯」與「交易邊界」分離，由最上層的 Controller 或 Service 決定交易範圍。

**Description:** Calling a function that starts a transaction inside another function that has already started one (`BEGIN` inside `BEGIN`).
**Fix:** Most SQL databases don't support true Nested Transactions; `SAVEPOINT` is usually required. A better practice is to separate "Business Logic" from "Transaction Boundaries," letting the top-level Controller or Service define the transaction scope.

## 5.3 忽略 Stream 的錯誤處理 (Ignoring Stream Errors)

**錯誤描述：** 使用 `.pipe()` 而非 `pipeline()`，且沒有監聽 `error` 事件。
**後果：** 如果 Stream 中途斷開（例如 DB 連線中斷），Node.js process 可能會因為 Unhandled Exception 而崩潰。`pipeline` (Node 10+) 或 `stream.finished` 是更安全的選擇。

**Description:** Using `.pipe()` instead of `pipeline()` without listening to `error` events.
**Consequence:** If the stream breaks midway (e.g., DB connection drops), the Node.js process might crash due to an Unhandled Exception. `pipeline` (Node 10+) or `stream.finished` are safer choices.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何決定 Express 應用程式中 DB Connection Pool 的大小？
**How do you determine the DB Connection Pool size in an Express application?**

*   **高分回答要點：**
    *   **不是越大越好：** DB 的 CPU/IO 是瓶頸。過多的連線會導致 Context Switching 高於實際執行查詢的時間。
    *   **公式參考：** PostgreSQL 建議 `((Core_count * 2) + effective_spindle_count)`。
    *   **分散式考量：** 必須除以 Express 的實例（Instance/Pod）數量。例如 DB 上限 100 連線，有 10 個 Pods，則每個 Pod 的 Pool Size 不應超過 10。
    *   **監控：** 提到使用 Prometheus/Grafana 監控 `pool_active_connections` 與 `pool_waiting_count`。

*   **Key Points:**
    *   **Bigger is not better:** DB CPU/IO is the bottleneck. Too many connections cause Context Switching to outweigh actual query time.
    *   **Formula:** PostgreSQL suggests `((Core_count * 2) + effective_spindle_count)`.
    *   **Distributed Context:** Must divide by the number of Express instances/pods. E.g., DB limit 100, 10 Pods => Max Pool Size 10 per Pod.
    *   **Monitoring:** Mention using Prometheus/Grafana to monitor `pool_active_connections` and `pool_waiting_count`.

## Q2: 在 Node.js 中，為什麼我們需要 Stream？直接讀檔案或查詢 DB 有什麼問題？
**Why do we need Streams in Node.js? What's wrong with reading files or querying DBs directly?**

*   **高分回答要點：**
    *   **記憶體空間複雜度：** 直接讀取是 O(N)（N=資料大小），Stream 是 O(1)（固定 Buffer 大小）。
    *   **延遲（Latency）：** Stream 可以「首字節優先（Time to First Byte）」回應，使用者不用等整個檔案生成完就能開始下載。
    *   **背壓（Backpressure）：** 解釋生產者與消費者速度不一致時，Stream 如何協調以避免緩衝區溢位。

*   **Key Points:**
    *   **Memory Space Complexity:** Direct read is O(N) (N=data size), Stream is O(1) (fixed Buffer size).
    *   **Latency:** Streams allow "Time to First Byte" response; users don't wait for the full file generation to start downloading.
    *   **Backpressure:** Explain how Streams coordinate when producer and consumer speeds differ to avoid buffer overflow.

## Q3: 如果在交易執行到一半時，Node.js 伺服器崩潰（Crash）了，資料庫會發生什麼事？
**If the Node.js server crashes halfway through a transaction, what happens to the database?**

*   **高分回答要點：**
    *   **TCP 連線中斷：** DB 會偵測到客戶端連線斷開。
    *   **自動 Rollback：** 大多數關聯式資料庫（Postgres, MySQL）會將未 COMMIT 的交易視為失敗，並自動執行 Rollback。
    *   **鎖的釋放：** 崩潰時，該連線持有的 Row Locks 會被資料庫釋放，避免 Deadlock。
    *   **應用層一致性：** 提到這雖然保證了 DB 一致性，但客戶端可能收到 500 錯誤，需要有重試機制（Idempotency）來處理不確定狀態。

*   **Key Points:**
    *   **TCP Disconnect:** The DB detects the client connection drop.
    *   **Auto Rollback:** Most RDBMS (Postgres, MySQL) treat uncommitted transactions as failed and automatically Rollback.
    *   **Lock Release:** Row Locks held by the connection are released by the DB upon crash, preventing Deadlocks.
    *   **App-Layer Consistency:** Mention that while DB consistency is preserved, the client receives a 500 error, requiring retry mechanisms (Idempotency) to handle the indeterminate state.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)
1.  **Pool Size Calculation:** 連線池大小應根據 DB 負載能力與 Application 實例數量反推，而非隨意設定。
2.  **Client Release:** 在手動管理交易（`pool.connect()`）時，務必在 `finally` 區塊釋放 Client，這是防止記憶體洩漏與連線耗盡的鐵律。
3.  **Streams for Scale:** 對於大於記憶體限制的資料操作（匯出、上傳），一律使用 Streams（`pipeline`）。
4.  **Backpressure Awareness:** 理解 `pipe()` 如何自動處理讀寫速度差異，保護系統不被流量沖垮。
5.  **ACID in Async:** 在 Node.js 非同步環境下，確保交易操作都在同一個 Client 實例上序列執行。

## 後續延伸 (Next Steps)
*   **進階章節：** 探索 **Message Queues (RabbitMQ/Kafka)** 與 Express 的整合，將耗時的資料庫寫入操作非同步化。
*   **安全性：** 研究 SQL Injection 的防禦（雖然 Parameterized Query 已涵蓋大部分，但動態 SQL 仍有風險）。
*   **ORM Performance:** 深入研究 TypeORM 或 Prisma 在底層如何處理 Connection Pool，以及如何優化 N+1 問題。

*   **Advanced Chapter:** Explore integrating **Message Queues (RabbitMQ/Kafka)** with Express to offload time-consuming DB write operations.
*   **Security:** Study SQL Injection defense (while Parameterized Query covers most, dynamic SQL remains risky).
*   **ORM Performance:** Deep dive into how TypeORM or Prisma handles Connection Pools under the hood and how to optimize N+1 problems.