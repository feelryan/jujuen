# 非同步與並發實戰模式 / AsyncIO & Concurrency Patterns

## Mental model｜心智模型

理解 Python 的並發（Concurrency）與平行（Parallelism），關鍵在於區分 **Event Loop** 與 **GIL (Global Interpreter Lock)** 的運作方式。

### 1. 單執行緒的協作式多工 (The Single-Threaded Cooperative Multitasking)
想像一位 **餐廳服務生（Event Loop）**：
- **AsyncIO**：服務生只有一個人。他負責點餐、送餐。當客人 A 在看菜單（IO Waiting）時，服務生不會乾等，而是轉身去服務客人 B。只要沒有人霸佔服務生（CPU Blocking），整個餐廳運作就很流暢。
- **Blocking**：如果客人 A 要求服務生留在桌邊陪他讀完整本菜單（同步 IO 或 繁重計算），其他所有客人都會餓死。這就是「阻塞 Event Loop」。

### 2. 決策矩陣 (Concurrency Decision Matrix)
在 Python 中選擇架構時，請依據任務屬性決定：

| 任務類型 (Task Type) | 特徵 (Characteristics) | 推薦方案 (Solution) | 核心模組 (Module) |
| :--- | :--- | :--- | :--- |
| **I/O Bound** (大量等待) | 網路請求、DB 查詢、檔案讀寫 | **AsyncIO** (Coroutines) | `asyncio`, `httpx`, `asyncpg` |
| **CPU Bound** (大量計算) | 影像處理、ML 推論、複雜運算 | **Multiprocessing** (Parallelism) | `multiprocessing`, `ProcessPoolExecutor` |
| **Blocking I/O** (舊式同步庫) | 只能使用同步庫 (如 `requests`) | **Threading** (Preemptive) | `threading`, `ThreadPoolExecutor` |

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 結構化並發 (Structured Concurrency)
自 Python 3.11 起，推薦使用 `TaskGroup` 來管理生命週期，確保所有任務要麼一起完成，要麼一起取消。

```python
import asyncio

async def fetch_data(id):
    # Simulate IO
    await asyncio.sleep(1)
    return f"Data {id}"

async def main():
    # Python 3.11+ 推薦寫法：自動處理異常傳播與取消
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch_data(1))
        task2 = tg.create_task(fetch_data(2))
    
    # 離開 block 後，task1 和 task2 確保已完成
    print(task1.result(), task2.result())
```

### 2. 限制並發數量 (Throttling Concurrency)
不要無限制地發起 `create_task`，這會耗盡 File Descriptors 或被目標 API Ban 掉。使用 `Semaphore`。

```python
sem = asyncio.Semaphore(10)  # 同時最多 10 個連線

async def safe_request(url):
    async with sem:  # 取得 token 才能執行
        return await client.get(url)
```

### 3. 混合 CPU-bound 任務 (Offloading Blocking Code)
絕對不要在 async 函式中直接執行繁重計算。使用 `asyncio.to_thread` (Python 3.9+) 將其丟到 Thread Pool。

```python
import time
import asyncio

def heavy_calculation():
    # 這是同步的阻塞代碼
    time.sleep(2) 
    return "Result"

async def main():
    print("Loop continues running...")
    # 將阻塞任務丟給 Thread 執行，釋放 Event Loop
    result = await asyncio.to_thread(heavy_calculation)
    print(result)
```

### 4. 優雅關閉 (Graceful Shutdown)
在 Container 或 Service 收到 `SIGTERM` 時，必須取消所有 Pending Tasks 並等待清理。

- 接收信號。
- `task.cancel()` 取消任務。
- `await asyncio.gather(..., return_exceptions=True)` 等待清理完成。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Sync" Blocker (同步阻塞陷阱)
最常見的錯誤是在 `async def` 中呼叫同步的 IO 函式。
- ❌ **Bad:** `requests.get(url)` (這會暫停整個 Event Loop，所有併發請求都會卡住)
- ✅ **Good:** `await httpx.get(url)` (釋放控制權，讓 Loop 處理其他任務)

### 2. Fire and Forget (射後不理)
創建了 Task 卻沒有保存 reference，也沒有 await。
- ❌ **Bad:** `asyncio.create_task(background_job())` (如果沒變數接住它，Python GC 可能會在執行途中把它回收；且若發生 Exception 會被靜默吞掉)
- ✅ **Good:** 將 task 加入 `background_tasks` 集合，並綁定 `done_callback` 處理異常。

### 3. Mutable State Race Conditions (非同步下的競態條件)
雖然 Python 是單執行緒，但在 `await` 的前後，全域變數的狀態可能已經被其他 Task 改變了。
- **風險點**：`await` 是一個 "Checkpoint"，這裡會發生 Context Switch。
- **防禦**：如果多個 Coroutine 共享可變狀態（如 Counter），仍需使用 `asyncio.Lock`。

### 4. Over-engineering (過度設計)
對於簡單的 Script 或非高併發場景，強行使用 AsyncIO 只會增加除錯難度與程式碼複雜度。如果你的瓶頸不在 IO 等待，請堅持使用同步程式碼。

---

## Checklists & workflows｜檢查清單與流程

### Decision Workflow: Async vs Sync
1. **瓶頸在哪？**
   - CPU 滿載 -> Multiprocessing
   - 網路/硬碟等待 -> 繼續
2. **依賴庫支援 Async 嗎？**
   - 支援 (如 FastAPI, SQLAlchemy async) -> **使用 AsyncIO**
   - 不支援 (如 Pandas, 舊版 boto3) -> **使用 ThreadPoolExecutor 封裝**

### Code Review Checklist
- [ ] **No Blocking Calls**: 檢查是否有 `time.sleep()`, `requests`, 或繁重的 `for` 迴圈直接寫在 async function 內。
- [ ] **Await Usage**: 所有的 async function call 前面都有 `await` 嗎？（除非是有意為之的 Background Task）。
- [ ] **Timeout Handling**: 所有的網路請求是否都設定了 `timeout`？（避免無限期掛起 Task）。
  - `await asyncio.wait_for(coro, timeout=5.0)`
- [ ] **Exception Handling**: `asyncio.gather` 是否設定了 `return_exceptions` 策略？或者使用了 `TaskGroup`？
- [ ] **Resource Cleanup**: 是否使用了 `async with` (Context Managers) 來管理連線池 (Session) 或資料庫連線？

---

## Real-world examples｜實戰案例

### 案例 1：高併發 API 聚合器 (API Aggregator)
**場景**：前端請求一個 User Profile 頁面，後端需要同時去 User Service, Order Service, Notification Service 抓資料。

```python
import asyncio
import httpx

async def get_user_dashboard(user_id: str):
    async with httpx.AsyncClient() as client:
        # 同時發出三個請求，總耗時等於最慢的那個請求，而非三者之和
        user_task = client.get(f"https://api/users/{user_id}")
        orders_task = client.get(f"https://api/orders/{user_id}")
        notif_task = client.get(f"https://api/notifications/{user_id}")
        
        # 等待全部完成
        responses = await asyncio.gather(user_task, orders_task, notif_task)
        
        # 解包數據
        user_data = responses[0].json()
        orders_data = responses[1].json()
        notif_data = responses[2].json()
        
    return {
        "user": user_data,
        "orders": orders_data,
        "notifications": notif_data
    }
```

### 案例 2：生產者-消費者模式 (Producer-Consumer Queue)
**場景**：爬蟲抓取網址（生產者）並進行資料解析入庫（消費者），利用 Queue 進行緩衝與流量控制。

```python
import asyncio

async def worker(name, queue):
    while True:
        # 從佇列獲取任務
        task_item = await queue.get()
        
        # 處理任務
        print(f"{name} processing {task_item}")
        await asyncio.sleep(0.1) # 模擬 IO
        
        # 通知佇列該任務已完成
        queue.task_done()

async def main():
    queue = asyncio.Queue(maxsize=100)
    
    # 啟動 3 個消費者 worker
    workers = [asyncio.create_task(worker(f"Worker-{i}", queue)) for i in range(3)]
    
    # 生產者放入任務
    for i in range(20):
        await queue.put(f"Item-{i}")
    
    # 等待佇列清空
    await queue.join()
    
    # 取消 worker (因為它們在 while True 中)
    for w in workers:
        w.cancel()

# asyncio.run(main())
```