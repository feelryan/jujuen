# Chapter 07: 效能優化與擴展性設計
# Chapter 07: Performance Optimization & Scalability

## 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，Express 的效能優化不僅僅是寫出更快的程式碼，更在於理解 Node.js 的 Runtime 機制，以及如何透過架構設計來突破單執行緒（Single-threaded）的物理限制。本章將超越基礎的 API 開發，深入探討如何在高併發場景下維持系統的低延遲與高吞吐量。

For Senior Engineers, performance optimization in Express is not just about writing faster code; it's about understanding the Node.js Runtime mechanism and how to overcome the physical limitations of being single-threaded through architectural design. This chapter goes beyond basic API development to explore how to maintain low latency and high throughput in high-concurrency scenarios.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **診斷效能瓶頸 (Diagnose Bottlenecks)**：識別 Event Loop Blocking 的徵兆，並使用適當工具分析 API Latency。
    Identify signs of Event Loop Blocking and use appropriate tools to analyze API Latency.
2.  **實作多層次快取 (Implement Multi-Level Caching)**：在 Express 中正確整合 Redis 進行 Cache-Aside 策略，並理解 HTTP Compression 的效益。
    Correctly integrate Redis in Express for Cache-Aside strategies and understand the benefits of HTTP Compression.
3.  **水平擴展應用 (Scale Horizontally)**：利用 Node.js 的 Clustering 模組或 PM2 Process Manager 來充分利用多核心 CPU。
    Utilize Node.js's Clustering module or PM2 Process Manager to fully leverage multi-core CPUs.
4.  **避免常見反模式 (Avoid Common Anti-Patterns)**：理解並修正記憶體洩漏（Memory Leaks）與同步操作（Synchronous Operations）帶來的風險。
    Understand and fix risks associated with Memory Leaks and Synchronous Operations.

---

## 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 Event Loop 與「餐廳服務生」模型
### 2.1 The Event Loop & The "Restaurant Waiter" Model

Express 建立在 Node.js 之上，其核心優勢在於非阻塞 I/O（Non-blocking I/O）。想像一位服務生（Single Thread）服務整間餐廳：
Express is built on Node.js, and its core advantage lies in Non-blocking I/O. Imagine a single waiter (Single Thread) serving an entire restaurant:

-   **正確做法 (Correct Approach)**：服務生點完餐後，將訂單交給廚房（OS Kernel / Worker Pool），然後立即去服務下一桌客人。當菜做好了，廚房通知服務生上菜（Callback/Promise resolution）。
    **Correct Approach**: After taking an order, the waiter hands it to the kitchen (OS Kernel / Worker Pool) and immediately serves the next table. When the food is ready, the kitchen notifies the waiter to serve it (Callback/Promise resolution).
-   **錯誤做法 (Blocking)**：服務生點完餐後，親自進廚房切菜、煮菜（CPU Intensive Task），這期間所有客人都被忽略（Request Timeout）。
    **Blocking**: After taking an order, the waiter goes into the kitchen to chop and cook (CPU Intensive Task), ignoring all other customers during this time (Request Timeout).

**資深觀點**：在 Express 中，任何超過 10ms 的同步運算都應該被視為潛在風險。對於加密（Crypto）、影像處理或大型 JSON 解析，應考慮 Worker Threads 或獨立的微服務。
**Senior Perspective**: In Express, any synchronous operation exceeding 10ms should be viewed as a potential risk. For cryptography, image processing, or large JSON parsing, consider Worker Threads or separate microservices.

### 2.2 垂直擴展 vs. 水平擴展
### 2.2 Vertical vs. Horizontal Scaling

-   **單體限制 (Monolithic Limit)**：預設情況下，Express 實例只運行在一個 CPU 核心上。即使你有一台 64 核心的伺服器，單一 Express Process 也只能利用其中 1/64 的算力。
    **Monolithic Limit**: By default, an Express instance runs on a single CPU core. Even with a 64-core server, a single Express Process can only utilize 1/64th of the computing power.
-   **Clustering / PM2**：透過 Fork 出多個 Processes（通常對應 CPU 核心數），我們可以讓多個 Express 實例共享同一個 Port。這是在不更改程式碼邏輯下，提升吞吐量最快的方式。
    **Clustering / PM2**: By forking multiple processes (usually matching the CPU core count), we allow multiple Express instances to share the same port. This is the fastest way to increase throughput without changing code logic.

---

## 3. 實務場景與系統設計視角 (Real-World & System Design View)

### 3.1 典型的高效能 Express 架構
### 3.1 Typical High-Performance Express Architecture

在 Production 環境中，一個經過優化的 Express 服務通常位於以下架構中：
In a Production environment, an optimized Express service typically sits within the following architecture:

1.  **Load Balancer (Nginx / AWS ALB)**: 處理 SSL Termination，並將流量分發到不同的運算節點（EC2 / K8s Pods）。
    Handles SSL Termination and distributes traffic to different compute nodes (EC2 / K8s Pods).
2.  **Process Manager (PM2)**: 在每個節點內部，PM2 管理著多個 Express Processes（Cluster Mode），負責自動重啟與日誌聚合。
    Inside each node, PM2 manages multiple Express Processes (Cluster Mode), handling auto-restart and log aggregation.
3.  **Express App Layer**:
    -   **Compression Middleware**: 使用 gzip/brotli 壓縮 Response Body，減少網路傳輸時間。
        Uses gzip/brotli to compress Response Body, reducing network transfer time.
    -   **In-Memory / Distributed Cache**: 優先讀取 Redis，減少資料庫負載。
        Prioritizes reading from Redis to reduce database load.
4.  **Data Layer**: Database (PostgreSQL/MongoDB) 與外部服務。
    Database (PostgreSQL/MongoDB) and external services.

### 3.2 對系統屬性的影響
### 3.2 Impact on System Attributes

-   **可擴展性 (Scalability)**：Stateless 的 Express 設計（Session 存於 Redis 而非記憶體）允許我們隨意增加 Server 數量。
    **Scalability**: Stateless Express design (Session stored in Redis, not memory) allows us to add servers at will.
-   **可用性 (Availability)**：使用 Clustering 意味著如果一個 Worker Process 因為未捕獲的異常（Uncaught Exception）崩潰，Master Process 可以立即生成新的 Worker，而不會導致整個服務中斷。
    **Availability**: Using Clustering means if a Worker Process crashes due to an Uncaught Exception, the Master Process can immediately spawn a new Worker without taking down the entire service.

---

## 4. 逐步示例 (Walkthrough / Example)

### 情境：優化一個高流量的產品列表 API
### Scenario: Optimizing a High-Traffic Product List API

假設我們有一個 `/api/v1/products` 端點，回應時間約為 300ms，且在高併發下 CPU 飆升。
Suppose we have an `/api/v1/products` endpoint with a response time of ~300ms, and CPU spikes under high concurrency.

### Step 1: 啟用壓縮 (Enable Compression)

這是最簡單的優化（Low Hanging Fruit）。大型 JSON Payload 會佔用頻寬並增加客戶端下載時間。
This is the lowest hanging fruit. Large JSON payloads consume bandwidth and increase client download time.

```javascript
const express = require('express');
const compression = require('compression');
const app = express();

// Best Practice: Use compression early in the middleware chain
// 最佳實踐：在 Middleware 鏈的早期使用 compression
app.use(compression()); 

app.get('/api/v1/products', async (req, res) => {
  // ... fetch data logic
});
```

### Step 2: 實作 Redis 快取 (Implement Redis Caching)

我們使用 **Cache-Aside** 模式。
We use the **Cache-Aside** pattern.

```javascript
const redis = require('redis');
const client = redis.createClient({ url: process.env.REDIS_URL });
client.connect();

const CACHE_TTL = 60; // seconds

app.get('/api/v1/products', async (req, res) => {
  const cacheKey = 'products:all';

  try {
    // 1. Check Cache
    const cachedData = await client.get(cacheKey);
    if (cachedData) {
      // X-Cache Header helps with debugging
      res.set('X-Cache', 'HIT');
      return res.json(JSON.parse(cachedData));
    }

    // 2. Fetch from DB (Simulated slow operation)
    // 假設這是一個耗時的 DB 查詢
    const products = await database.getProducts(); 

    // 3. Write to Cache
    // Set expiry to prevent stale data persisting forever
    // 設定過期時間以防止過時資料永久存在
    await client.setEx(cacheKey, CACHE_TTL, JSON.stringify(products));

    res.set('X-Cache', 'MISS');
    return res.json(products);

  } catch (error) {
    // Fail-safe: If Redis fails, fall back to DB, don't crash request
    // 故障安全：如果 Redis 失敗，退回到 DB，不要讓請求崩潰
    console.error('Redis error', error);
    const products = await database.getProducts();
    return res.json(products);
  }
});
```

### Step 3: 使用 PM2 進行叢集化 (Clustering with PM2)

在程式碼層面不需要大幅修改，我們主要透過啟動設定來處理。
No major code changes are needed; we handle this primarily through startup configuration.

建立 `ecosystem.config.js`:
Create `ecosystem.config.js`:

```javascript
module.exports = {
  apps: [{
    name: "express-api",
    script: "./server.js",
    instances: "max", // Utilize all CPU cores / 利用所有 CPU 核心
    exec_mode: "cluster", // Enable clustering mode / 啟用叢集模式
    env: {
      NODE_ENV: "development",
    },
    env_production: {
      NODE_ENV: "production",
    }
  }]
}
```

**啟動指令 (Start Command)**:
`pm2 start ecosystem.config.js --env production`

**結果 (Result)**:
如果伺服器有 4 個核心，PM2 會啟動 4 個 Node.js 行程。吞吐量（RPS）理論上可提升接近 4 倍（取決於是否為 CPU Bound）。
If the server has 4 cores, PM2 will start 4 Node.js processes. Throughput (RPS) can theoretically increase by nearly 4x (depending on whether it's CPU Bound).

---

## 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 在主執行緒進行繁重運算 (Heavy Computation on Main Thread)

-   **錯誤 (Mistake)**: 在 Request Handler 中執行 `JSON.parse` 處理極大的字串，或進行複雜的陣列排序。
    Executing `JSON.parse` on massive strings or performing complex array sorting within the Request Handler.
-   **後果 (Consequence)**: Event Loop 被阻塞（Blocked），所有其他進來的請求都被卡住，導致 Latency Spike。
    The Event Loop gets blocked, causing all other incoming requests to hang, leading to Latency Spikes.
-   **修正 (Fix)**: 使用 Stream 處理大數據，或將計算卸載（Offload）到 Worker Threads / 專用微服務。
    Use Streams for large data, or offload computation to Worker Threads / dedicated microservices.

### 5.2 記憶體內快取濫用 (In-Memory Cache Abuse)

-   **錯誤 (Mistake)**: 使用全域變數（如 `const cache = {}`）來儲存大量資料。
    Using global variables (like `const cache = {}`) to store large amounts of data.
-   **後果 (Consequence)**:
    1.  **Memory Leak**: Node.js 預設記憶體限制（約 1.5GB）很快就會耗盡，導致 OOM (Out of Memory) Crash。
        Node.js default memory limit (~1.5GB) is exhausted quickly, leading to OOM Crash.
    2.  **Inconsistency**: 在 Cluster 模式下，每個 Process 的記憶體不共享，導致不同請求拿到不同資料。
        In Cluster mode, memory is not shared between processes, leading to data inconsistency across requests.
-   **修正 (Fix)**: 始終使用外部儲存（Redis/Memcached）進行快取。
    Always use external storage (Redis/Memcached) for caching.

### 5.3 忽略 Keep-Alive 連線 (Ignoring Keep-Alive Connections)

-   **錯誤 (Mistake)**: 每次請求都重新建立 TCP/DB 連線。
    Re-establishing TCP/DB connections for every request.
-   **後果 (Consequence)**: TCP Handshake 開銷巨大。
    Huge overhead from TCP Handshakes.
-   **修正 (Fix)**: 使用 HTTP Keep-Alive Agent，並確保資料庫連線池（Connection Pool）設定正確。
    Use an HTTP Keep-Alive Agent and ensure Database Connection Pools are configured correctly.

---

## 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: Node.js 是單執行緒的，為什麼能處理高併發？如果遇到 CPU 密集型任務該怎麼辦？
### Q1: Node.js is single-threaded. How does it handle high concurrency? What if we encounter CPU-intensive tasks?

-   **高分回答要點 (Key Points)**:
    -   解釋 **Event Loop** 與 **Libuv**：JS 執行是單執行緒，但 I/O 操作（網路、檔案）是由 OS 核心或 Thread Pool 非同步處理的。
        Explain **Event Loop** and **Libuv**: JS execution is single-threaded, but I/O operations (network, file) are handled asynchronously by the OS kernel or Thread Pool.
    -   解釋 **Blocking**：CPU 密集任務會卡住 Event Loop。
        Explain **Blocking**: CPU-intensive tasks block the Event Loop.
    -   **解決方案**：
        1.  **Clustering**: 多行程處理。
            **Clustering**: Multi-process handling.
        2.  **Worker Threads**: Node.js v10+ 的多執行緒支援。
            **Worker Threads**: Multi-threading support in Node.js v10+.
        3.  **Architecture**: 將重運算拆分到獨立的微服務（如 Python/Go 服務）。
            **Architecture**: Offload heavy computation to separate microservices (e.g., Python/Go services).

### Q2: 在 Express 中實作 Caching 時，如何處理「快取雪崩」(Cache Stampede)？
### Q2: When implementing Caching in Express, how do you handle "Cache Stampede"?

-   **高分回答要點 (Key Points)**:
    -   **定義**：當熱門 Key 過期時，大量並發請求同時打向資料庫。
        **Definition**: When a hot key expires, massive concurrent requests hit the database simultaneously.
    -   **策略 1 (Locking)**：第一個請求去 DB 抓資料時，在 Redis 上鎖，其他請求等待。
        **Strategy 1 (Locking)**: The first request fetches from DB and locks Redis; others wait.
    -   **策略 2 (Probabilistic Early Expiration)**：在快取即將過期前，隨機讓部分請求去更新快取。
        **Strategy 2 (Probabilistic Early Expiration)**: Randomly allow some requests to refresh the cache before it actually expires.
    -   **策略 3 (Stale-While-Revalidate)**：先回傳舊資料，背景非同步更新快取。
        **Strategy 3 (Stale-While-Revalidate)**: Return stale data immediately while updating the cache asynchronously in the background.

### Q3: 如何監控 Express 應用程式的效能瓶頸？
### Q3: How do you monitor performance bottlenecks in an Express application?

-   **高分回答要點 (Key Points)**:
    -   **APM Tools**: 使用 New Relic, Datadog 或 OpenTelemetry 追蹤 Transaction Traces。
        **APM Tools**: Use New Relic, Datadog, or OpenTelemetry to track Transaction Traces.
    -   **Event Loop Lag**: 監控 Event Loop 的延遲時間（這是 Node.js 特有的關鍵指標）。
        **Event Loop Lag**: Monitor Event Loop latency (a key metric specific to Node.js).
    -   **Profiling**: 在開發/測試環境使用 Clinic.js 或 Node.js 內建的 `--prof` 進行 CPU Profiling。
        **Profiling**: Use Clinic.js or Node.js built-in `--prof` for CPU Profiling in dev/test environments.

---

## 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)
1.  **Non-blocking is King**: 永遠不要阻塞 Event Loop。將同步操作視為效能殺手。
    **Non-blocking is King**: Never block the Event Loop. Treat synchronous operations as performance killers.
2.  **Cache Aggressively**: 使用 Redis 實作 Cache-Aside 模式是降低 Latency 最有效的手段。
    **Cache Aggressively**: Implementing Cache-Aside with Redis is the most effective way to reduce Latency.
3.  **Scale with Cores**: 使用 PM2 或 Cluster Module 讓 Express 跑滿伺服器的所有 CPU 核心。
    **Scale with Cores**: Use PM2 or Cluster Module to run Express across all server CPU cores.
4.  **Compress Payloads**: 啟用 Gzip/Brotli 壓縮，以極低的 CPU 成本換取網路傳輸速度。
    **Compress Payloads**: Enable Gzip/Brotli compression to trade minimal CPU cost for network speed.
5.  **Stateless Architecture**: 保持應用程式無狀態，以便隨時進行水平擴展。
    **Stateless Architecture**: Keep the application stateless to allow for horizontal scaling at any time.

### 後續延伸 (Next Steps)
-   **Security**: 效能優化後，下一步應關注安全性。閱讀關於 Helmet, Rate Limiting (DDOS protection) 的實作。
    **Security**: After optimization, focus on security. Read about implementing Helmet and Rate Limiting (DDOS protection).
-   **Microservices**: 當單體 Express 應用擴展到極限時，學習如何將其拆分為微服務（使用 gRPC 或 Message Queues 如 RabbitMQ）。
    **Microservices**: When the monolithic Express app reaches its limit, learn how to decompose it into microservices (using gRPC or Message Queues like RabbitMQ).