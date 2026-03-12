# Chapter 04: 並行與平行程式設計 (Concurrency & Parallelism Patterns)

## 1. 前言與學習目標 (Introduction & Learning Goals)

在 Python 的高階面試與系統設計中，「如何處理並發」往往是決定勝負的關鍵。由於 Python 獨特的 GIL（Global Interpreter Lock）機制，盲目地使用 Threading 往往無法帶來預期的效能提升，甚至可能因 Context Switch 而變慢。

In high-level Python interviews and system design, "how to handle concurrency" is often a make-or-break topic. Due to Python's unique GIL (Global Interpreter Lock) mechanism, blindly using Threading often fails to deliver expected performance gains and can even degrade performance due to context switching overhead.

完成本章後，身為資深工程師的你應該能夠：

By the end of this chapter, as a Senior Engineer, you should be able to:

1.  **精準判斷模型選擇**：在 `asyncio`、`threading` 與 `multiprocessing` 之間，根據 I/O bound 或 CPU bound 的特性做出正確的架構決策。
    **Accurately select the model**: Make the correct architectural decision between `asyncio`, `threading`, and `multiprocessing` based on whether the task is I/O bound or CPU bound.
2.  **理解 GIL 的本質與限制**：清楚解釋 GIL 如何影響多執行緒效能，以及如何透過 C-Extensions 或 Multiprocessing 繞過它。
    **Understand the essence and limits of the GIL**: Clearly explain how the GIL impacts multi-threaded performance and how to bypass it using C-Extensions or Multiprocessing.
3.  **混合模式實作**：在 Asyncio 的 Event Loop 中正確整合 Blocking I/O 或 CPU 密集型任務（使用 `run_in_executor`）。
    **Implement hybrid patterns**: Correctly integrate Blocking I/O or CPU-intensive tasks within an Asyncio Event Loop (using `run_in_executor`).
4.  **處理 Race Conditions**：在並行環境中識別非原子操作（Non-atomic operations），並使用適當的鎖（Locks/Semaphores）保護共享資源。
    **Handle Race Conditions**: Identify non-atomic operations in concurrent environments and protect shared resources using appropriate synchronization primitives (Locks/Semaphores).

---

## 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 並行 (Concurrency) vs. 平行 (Parallelism)
**直覺類比 (Analogy)**：
- **Concurrency (並行)**：就像一個廚師（CPU 核心）同時處理切菜、煮湯和烤箱裡的派。廚師在這些任務間快速切換（Context Switching），或者在等待烤箱（I/O）時去切菜。同一時間點，廚師的手只能做一件事。
- **Parallelism (平行)**：就像廚房裡有三個廚師（多核 CPU），一個人切菜，一個人煮湯，一個人顧烤箱。他們是真的在「同時」工作。

**Concurrency**: Like a single chef (CPU core) handling chopping, boiling soup, and baking a pie. The chef switches rapidly between tasks (Context Switching) or chops veggies while waiting for the oven (I/O). At any exact moment, the chef is doing only one thing.
**Parallelism**: Like having three chefs (Multi-core CPU) in the kitchen: one chops, one boils, one bakes. They are truly working "at the same time."

### 2.2 Python 的 GIL (Global Interpreter Lock)
Python（CPython 實作）的記憶體管理不是 Thread-safe 的。為了防止多個 Thread 同時修改 Python 物件導致崩潰，引入了 GIL。

Python's (CPython implementation) memory management is not thread-safe. To prevent multiple threads from modifying Python objects simultaneously and causing crashes, the GIL was introduced.

- **影響 (Impact)**：在任何一個時間點，只有一個 Thread 能持有 GIL 並執行 Python Bytecode。這意味著 Python 的多執行緒無法利用多核 CPU 來加速 **CPU Bound** 的任務。
- **例外 (Exceptions)**：當執行 I/O 操作（網路請求、磁碟讀寫）或某些釋放 GIL 的 C 擴充套件（如 NumPy 矩陣運算）時，GIL 會被釋放，此時多執行緒是有意義的。

- **Impact**: At any given moment, only one thread can hold the GIL and execute Python Bytecode. This means Python threads cannot leverage multi-core CPUs to accelerate **CPU Bound** tasks.
- **Exceptions**: The GIL is released during I/O operations (network requests, disk I/O) or within certain C-extensions that explicitly release it (like NumPy matrix operations), making multi-threading useful in these cases.

### 2.3 三種模式的決策矩陣 (Decision Matrix)

| Feature | Asyncio (Coroutines) | Threading | Multiprocessing |
| :--- | :--- | :--- | :--- |
| **Paradigm** | Cooperative Multitasking (協作式) | Preemptive Multitasking (搶佔式) | Parallelism (平行處理) |
| **Memory** | Shared (Single Process) | Shared (Single Process) | Isolated (Separate Processes) |
| **Switching Cost** | Very Low (Function calls) | Medium (OS Context Switch) | High (Pickling/IPC overhead) |
| **Best For** | **High Concurrency I/O** (Web Servers, Websockets) | **Blocking I/O** (Legacy DB drivers, File I/O) | **CPU Bound** (Data Processing, ML) |

---

## 3. 實務場景與系統設計視角 (Real-World & System Design View)

### 3.1 高並發 Web 服務 (High Concurrency Web Services)
在現代 Microservices 架構中，服務通常是 I/O 密集的（呼叫其他 API、查詢 DB）。
In modern Microservices architectures, services are typically I/O intensive (calling other APIs, querying DBs).

- **架構選擇**：使用 **Asyncio** (FastAPI/Sanic/Tornado)。
- **原因**：一個 Thread 可以處理數千個連線。相比 Threading 模型（如 Flask + Gunicorn threads），Asyncio 節省了大量的記憶體與 Context Switch 開銷。
- **System Design 考量**：若服務中包含少量 CPU 密集運算（如圖片縮放、JWT 驗證），必須小心不要阻塞 Event Loop。

- **Choice**: Use **Asyncio** (FastAPI/Sanic/Tornado).
- **Reason**: A single thread can handle thousands of connections. Compared to the Threading model (e.g., Flask + Gunicorn threads), Asyncio saves significant memory and context switching overhead.
- **System Design Consideration**: If the service includes minor CPU-intensive tasks (e.g., image resizing, JWT verification), you must be careful not to block the Event Loop.

### 3.2 數據處理與背景任務 (Data Processing & Background Tasks)
當需要處理大量數據運算、影像辨識或複雜邏輯時。
When handling heavy data computation, image recognition, or complex logic.

- **架構選擇**：使用 **Multiprocessing** (Celery with `prefork` pool / Dask)。
- **原因**：唯有透過多 Process 才能繞過 GIL，吃滿多核 CPU 的算力。
- **Trade-off**：Process 間的通訊（IPC）成本較高，且每個 Process 都有獨立的記憶體空間，需注意記憶體總消耗。

- **Choice**: Use **Multiprocessing** (Celery with `prefork` pool / Dask).
- **Reason**: Only multi-processing can bypass the GIL and fully utilize multi-core CPU power.
- **Trade-off**: Inter-Process Communication (IPC) is costly, and since each process has its own memory space, total memory consumption must be monitored.

---

## 4. 逐步示例 (Walkthrough / Example)

### 案例：混合型爬蟲與數據處理 (Hybrid Crawler & Data Processing)
**情境 (Scenario)**：我們需要從 100 個 URL 下載資料（I/O Bound），然後對下載的 JSON 進行複雜的數據清洗與轉換（CPU Bound）。

**Scenario**: We need to download data from 100 URLs (I/O Bound) and then perform complex data cleaning and transformation on the downloaded JSON (CPU Bound).

#### 4.1 錯誤的嘗試：純 Asyncio 處理 CPU 任務 (The Wrong Way)
如果在 `async def` 中直接執行 CPU 密集運算，會導致 Event Loop 停擺，所有其他的網路請求都會被卡住。

If you execute CPU-intensive calculations directly inside an `async def`, the Event Loop will halt, and all other network requests will be blocked.

#### 4.2 成熟的解法：Asyncio + ProcessPoolExecutor (The Mature Solution)
我們使用 `asyncio` 處理 HTTP 請求，並將 CPU 運算卸載（Offload）到 `ProcessPoolExecutor`。

We use `asyncio` to handle HTTP requests and offload CPU computations to a `ProcessPoolExecutor`.

```python
import asyncio
import time
import concurrent.futures
from typing import List, Dict

# 模擬 CPU 密集型任務 (Simulate CPU-bound task)
# 注意：此函數不能是 async，且最好是純函數以利 Pickling
def heavy_computation(data: str) -> Dict:
    # Simulate heavy work (e.g., parsing huge JSON, encryption)
    count = 0
    for _ in range(5_000_000):
        count += 1
    return {"data": data, "result": count}

# 模擬 I/O 密集型任務 (Simulate I/O-bound task)
async def fetch_url(url: str) -> str:
    # In real world, use aiohttp or httpx
    await asyncio.sleep(0.1) # Simulate network latency
    return f"content_of_{url}"

async def process_url(url: str, pool: concurrent.futures.ProcessPoolExecutor):
    # 1. Non-blocking I/O
    content = await fetch_url(url)
    
    # 2. Offload CPU work to a separate process
    # run_in_executor(Executor, func, *args)
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(pool, heavy_computation, content)
    return result

async def main():
    urls = [f"url_{i}" for i in range(20)]
    
    # 建立 Process Pool，數量通常設為 CPU 核心數
    # Create Process Pool, size usually set to CPU core count
    with concurrent.futures.ProcessPoolExecutor() as pool:
        tasks = [process_url(url, pool) for url in urls]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        print(f"Processed {len(results)} items in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    # Windows/macOS 下 Multiprocessing 需要此保護
    # Multiprocessing on Windows/macOS requires this guard
    asyncio.run(main())
```

**為何這樣做可行 (Why this works)**：
- `fetch_url` 釋放控制權給 Event Loop，允許同時發出多個請求。
- `run_in_executor` 將 `heavy_computation` 丟給另一個 Process 執行，主 Thread 的 Event Loop 繼續處理其他 I/O，互不阻塞。

- `fetch_url` yields control to the Event Loop, allowing multiple requests to be fired concurrently.
- `run_in_executor` throws `heavy_computation` to another Process. The main thread's Event Loop continues handling other I/O without blocking.

---

## 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 在 Async 函式中呼叫 Blocking Library
**錯誤 (Pitfall)**：在 `async def` 中使用 `requests.get()` 或 `time.sleep()`。
**後果 (Consequence)**：整個 Event Loop 被暫停，這比同步程式還慘，因為你引入了 async 的複雜度卻得到單執行緒的效能。
**修正 (Fix)**：使用 `aiohttp` / `httpx`，或者若必須使用舊套件，請用 `loop.run_in_executor(ThreadPoolExecutor, ...)` 包裝。

**Pitfall**: Using `requests.get()` or `time.sleep()` inside an `async def`.
**Consequence**: The entire Event Loop is paused. This is worse than synchronous code because you introduced async complexity but got single-threaded performance.
**Fix**: Use `aiohttp` / `httpx`, or if you must use legacy packages, wrap them with `loop.run_in_executor(ThreadPoolExecutor, ...)`.

### 5.2 誤以為 Python 的 `+=` 是 Thread-safe 的
**錯誤 (Pitfall)**：在多執行緒環境下共享變數並直接修改。
**程式碼 (Code)**：
```python
# Not thread-safe!
counter = 0
def increment():
    global counter
    counter += 1 
```
**原因 (Reason)**：`counter += 1` 在 Bytecode 層級分為三個步驟：讀取 (LOAD)、加法 (ADD)、寫回 (STORE)。執行緒可能在 ADD 之後、STORE 之前被切換掉 (Race Condition)。
**修正 (Fix)**：使用 `threading.Lock()` 或 `atomic` 類別。

**Pitfall**: Sharing and modifying variables directly in a multi-threaded environment.
**Reason**: `counter += 1` compiles to three bytecode steps: LOAD, ADD, STORE. A thread context switch can occur after ADD but before STORE (Race Condition).
**Fix**: Use `threading.Lock()` or atomic classes.

### 5.3 忽略 Multiprocessing 的序列化成本 (Pickling Overhead)
**錯誤 (Pitfall)**：傳遞巨大的物件（如 1GB 的 DataFrame）給子 Process。
**後果 (Consequence)**：序列化 (Pickling) 與反序列化 (Unpickling) 的時間可能超過平行運算節省的時間。
**修正 (Fix)**：使用 Shared Memory (Python 3.8+ `multiprocessing.shared_memory`)，或傳遞資料的路徑/ID 讓子 Process 自行讀取。

**Pitfall**: Passing huge objects (e.g., a 1GB DataFrame) to child processes.
**Consequence**: The time spent on Pickling and Unpickling might exceed the time saved by parallel computation.
**Fix**: Use Shared Memory (Python 3.8+ `multiprocessing.shared_memory`), or pass data paths/IDs and let child processes load the data themselves.

---

## 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 請解釋 Python GIL 對系統設計的影響，以及你如何在專案中克服它？
**Explain the impact of the Python GIL on system design and how you overcome it in projects.**

*   **高分回答要點 (Key Points)**：
    *   明確指出 GIL 是一個 Mutex，保護 CPython 內部的記憶體管理，導致同一時間只能有一個 Thread 執行 Bytecode。
    *   區分 **I/O Bound** (GIL 會釋放，Threading 有效) 與 **CPU Bound** (GIL 鎖住，Threading 無效)。
    *   提出解法：使用 `multiprocessing`、使用 C-extension (如 NumPy 內部釋放 GIL)、或將運算密集的 Microservice 改用 Go/Rust/C++ 撰寫。

*   **Key Points**:
    *   Clearly state that the GIL is a Mutex protecting CPython's internal memory management, allowing only one thread to execute bytecode at a time.
    *   Distinguish between **I/O Bound** (GIL is released, Threading works) and **CPU Bound** (GIL locks, Threading fails).
    *   Propose solutions: Use `multiprocessing`, use C-extensions (like NumPy which releases GIL internally), or rewrite compute-heavy Microservices in Go/Rust/C++.

### Q2: 什麼時候你應該選擇 `asyncio` 而不是 `threading`？反之亦然？
**When should you choose `asyncio` over `threading`, and vice versa?**

*   **高分回答要點 (Key Points)**：
    *   **Asyncio**：適用於極高並發的 I/O (C10K 問題)，例如 Websocket Server、Gateway。優點是記憶體佔用低，沒有 Race Condition (因為是單執行緒協作)，但除錯較難，且不能有 Blocking code。
    *   **Threading**：適用於依賴 Blocking I/O 的舊程式庫 (如 `psycopg2` 同步模式)、或簡單的並行任務。優點是程式模型簡單（線性），OS 自動排程。

*   **Key Points**:
    *   **Asyncio**: Best for extremely high concurrency I/O (C10K problem), e.g., Websocket Servers, Gateways. Pros: Low memory footprint, no Race Conditions (single-threaded cooperative), but harder to debug and zero tolerance for blocking code.
    *   **Threading**: Best for legacy libraries relying on Blocking I/O (e.g., synchronous `psycopg2`) or simple concurrent tasks. Pros: Simple programming model (linear), OS handles scheduling.

### Q3: 在 Asyncio 系統中，如果有一個第三方套件只有同步 (Synchronous) API，你會怎麼處理？
**In an Asyncio system, how do you handle a third-party package that only has a Synchronous API?**

*   **高分回答要點 (Key Points)**：
    *   絕對不能直接呼叫，會 Block 住 Event Loop。
    *   使用 `loop.run_in_executor(None, func, args)` 將其放入預設的 `ThreadPoolExecutor` 中執行。
    *   如果是 CPU 密集的同步函式，則應傳入 `ProcessPoolExecutor`。

*   **Key Points**:
    *   Never call it directly; it will block the Event Loop.
    *   Use `loop.run_in_executor(None, func, args)` to run it in the default `ThreadPoolExecutor`.
    *   If it is a CPU-intensive synchronous function, pass a `ProcessPoolExecutor` instead.

---

## 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)
1.  **GIL 限制**：Python 多執行緒無法平行處理 CPU 任務，僅適用於 I/O 任務。
2.  **Asyncio 優勢**：單執行緒、協作式多工，適合高並發網路 I/O，但對 Blocking code 零容忍。
3.  **Multiprocessing**：繞過 GIL 的唯一純 Python 手段，適合 CPU 密集任務，但需注意 IPC 與記憶體開銷。
4.  **Race Conditions**：即使有 GIL，Python 的操作（如 `+=`）仍非原子性，共享資源需加鎖。
5.  **Executor Pattern**：熟練使用 `run_in_executor` 是橋接 Async 與 Sync 世界的關鍵技能。

### 後續延伸 (Next Steps)
-   **Profiling**: 學習使用 `cProfile`, `py-spy` 或 `viztracer` 來分析並行程式的效能瓶頸（將在 Chapter 05 介紹）。
-   **Advanced Asyncio**: 研究 `asyncio.Queue` (Producer-Consumer pattern) 與 `TaskGroup` (Python 3.11+ 的結構化並發)。
-   **Distributed Tasks**: 從單機 Multiprocessing 延伸到分散式任務佇列 (Celery, RQ, Dramatiq)。