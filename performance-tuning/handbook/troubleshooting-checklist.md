# 實戰排查流程與 Checklist / Troubleshooting Workflow and Checklist

這不是一份教你如何優化程式碼的指南，這是一份當你的 PagerDuty 響起、客戶在抱怨、老闆在背後盯著你看時的 **「急診室手冊」**。

This is not a guide on how to optimize code. This is an **"Emergency Room Handbook"** for when PagerDuty is firing, customers are complaining, and your boss is breathing down your neck.

---

## Mental model｜心智模型

在處理效能事故（Performance Incident）時，最核心的心智模型是 **「急診室分流」（ER Triage）** 與 **「分層剝洋蔥」（Layered Peeling）**。

### 1. Mitigation First, Root Cause Second (先止血，再找病因)
在事故當下，首要目標是 **恢復服務（Restore Service）**，而不是找到完美的根本原因（Root Cause Analysis, RCA）。
- **Mitigation (止血)**: 重啟、回滾（Rollback）、擴容（Scale-out）、降級（Degrade/Circuit Break）。
- **Resolution (治療)**: 修復 Bug、優化 SQL、調整架構。
- **Rule of Thumb**: 如果 10 分鐘內無法定位問題，優先考慮止血措施（如 Rollback）。

### 2. The "What Changed?" Heuristic (變更啟發法)
絕大多數的效能突發問題都源自於系統的某種「變更」。
- **Code Change**: 剛發佈了新版本？
- **Config Change**: 修改了 DB 參數或 Feature Flag？
- **Traffic Change**: 行銷活動導致流量暴衝？
- **Environment Change**: 雲端供應商底層網路抖動？

### 3. Top-Down vs. Bottom-Up (由上而下 vs. 由下而上)
- **Top-Down (推薦)**: 從 User Experience (Latency/Errors) -> Load Balancer -> App Server -> Database。這能幫你快速縮小範圍（是全站慢還是只有某個 API 慢？）。
- **Bottom-Up**: 直接看 CPU、Memory。這容易陷入細節（CPU 高不代表它是問題根源，可能是受害者）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. The "Binary Search" Isolation (二分搜尋隔離法)
不要試圖一次檢查所有東西。利用架構邊界進行二分法定位：
- **Web vs. App vs. DB**: 請求是在進 App 前就慢（LB/Network），還是在 App 內部慢，還是卡在 DB？
- **Region/Zone**: 是所有區域都慢，還是只有 `us-east-1` 慢？
- **Endpoint**: 是所有 API 都慢，還是只有 `/checkout` 慢？

### 2. Correlation with Time (時間相關性分析)
將所有指標（Metrics）與「事件」對齊時間軸。
- 疊加 Deployment Marker（部署標記）到監控儀表板上。
- 檢查 Log 中錯誤率飆升的確切時間點，是否吻合 Cron Job 的啟動時間？

### 3. Resource Saturation Check (資源飽和度檢查 - USE Method)
對於每一個資源（CPU, Memory, Disk, Network），檢查：
- **Utilization**: 使用率多高？（e.g., CPU 90%）
- **Saturation**: 有多少任務在排隊？（e.g., Load Average > CPU Cores, Kafka Lag）
- **Errors**: 有沒有硬體或系統層級錯誤？（e.g., OOM Kill, Network Dropped Packets）

### 4. Snapshotting (保留現場)
在重啟或回滾前，務必保留現場證據，否則事後無法 RCA。
- **Thread Dump**: Java/Go process 卡死時必備。
- **Heap Dump**: 懷疑 Memory Leak 時。
- **Top/Ps Output**: 記錄當下最耗資源的 Process。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Shotgun Debugging (散彈槍除錯)
**Anti-pattern**: 同時修改 3 個參數、擴容機器、並回滾程式碼。
**Consequence**: 服務恢復了，但你永遠不知道是哪個動作修好的，下次發生時依然無解；或者更糟，引入了新的副作用。
**Fix**: 一次只做一個變更（One change at a time），觀察反饋。

### 2. Tunnel Vision on "The Usual Suspects" (慣性思維)
**Anti-pattern**: 「上次慢是因為資料庫索引沒加，這次一定也是！」於是花了 30 分鐘檢查 DB，結果發現是 DNS 解析問題。
**Consequence**: 浪費寶貴的黃金救援時間。
**Fix**: 遵循標準 Checklist，不要跳過基礎檢查（如網路連線、磁碟空間）。

### 3. Ignoring "Steal Time" or "I/O Wait" (忽視隱性等待)
**Anti-pattern**: 看到 CPU User Usage 只有 20%，就認為 CPU 沒問題，卻忽略了應用程式回應極慢。
**Consequence**: 在雲端環境（AWS/GCP）或高 I/O 場景下，CPU 可能正忙著「等待」被分配時間片（Steal Time）或等待磁碟（I/O Wait）。

### 4. Premature Optimization during Outage (事故中過早優化)
**Anti-pattern**: 發現某個 SQL 跑得慢，試圖在 Production 環境線上 Rewrite SQL 或重構程式碼。
**Consequence**: 壓力下容易寫出 Bug，導致二次故障。
**Fix**: 先透過限流（Rate Limiting）或關閉功能（Feature Toggle）來緩解，事後再優化程式碼。

---

## Checklists & workflows｜檢查清單與流程

這是一份建議列印出來或放在 Wiki 首頁的 War Room Checklist。

### Phase 1: Triage & Mitigation (0-10 mins) - 先止血
- [ ] **Impact Assessment**: 影響範圍是全站癱瘓 (P0) 還是部分功能慢 (P1)？
- [ ] **Recent Changes**: 過去 1 小時內有無部署 (Deploy) 或設定變更 (Config Change)？
    - [ ] *Yes*: **立即執行 Rollback**。不要猶豫，先回滾再查。
- [ ] **Health Check**: Load Balancer / Gateway 是否健康？
    - [ ] *No*: 檢查網路、DNS、CDN 狀態。
- [ ] **Resource Exhaustion**: 是否有明顯的資源耗盡？
    - [ ] CPU / Memory 飆升至 100%？ -> 考慮重啟 (Restart) 或 擴容 (Scale Out)。
    - [ ] Disk Full？ -> 清理 Log 或擴容磁碟。

### Phase 2: Isolation & Analysis (10-30 mins) - 定位瓶頸
如果 Phase 1 沒解決，進入深層排查：

#### A. Application Layer (應用層)
- [ ] **Error Logs**: 檢查 Application Log 是否有大量 `ERROR` / `FATAL` / `Exception`。
- [ ] **Thread/Connection Pool**:
    - [ ] DB Connection Pool 是否滿了 (Leaked connections)？
    - [ ] Worker Thread Pool 是否滿了 (Blocked threads)？
- [ ] **GC / Runtime**: (Java/Go/Node) 是否發生頻繁的 Full GC 或 Stop-the-world？

#### B. Database Layer (資料庫層)
- [ ] **Slow Query**: 檢查當下是否有執行時間極長的 Query (Long running transactions)？
    - [ ] *Action*: 殺掉 (Kill) 卡住的 Query。
- [ ] **Locks**: 是否有 Deadlock 或 Metadata Lock 等待？
- [ ] **Connections**: 連線數是否暴增（可能來自 Cache 失效後的穿透）？

#### C. Infrastructure Layer (基礎設施層)
- [ ] **Network**: 內網延遲 (Internal Latency) 是否增加？Packet Loss？
- [ ] **Neighbors**: (公有雲) 是否受到 Noisy Neighbor 影響 (Check Steal Time)？

### Phase 3: Resolution & Recovery (Post-Incident)
- [ ] **Root Cause**: 確認根本原因（是 Code, Config, 還是 Capacity？）。
- [ ] **Fix**: 應用永久性修復（Patch, Indexing, Architecture Change）。
- [ ] **Post-Mortem**: 撰寫事故報告，更新此 Checklist。

---

## Real-world examples｜實戰案例

### Scenario 1: The "Cache Stampede" (快取雪崩/擊穿)
**症狀 (Symptoms)**:
- 流量正常，但資料庫 CPU 突然飆升至 100%。
- 應用程式回應時間極長，大量 Timeout。
- Redis/Memcached 剛重啟，或某個熱點 Key 剛過期。

**排查 (Diagnosis)**:
- 檢查 DB 連線數：暴增。
- 檢查 Cache Hit Rate：驟降。

**處置 (Action)**:
1. **緊急**: 開啟限流 (Rate Limiting) 或降級頁面，保護 DB 不被打死。
2. **修復**: 實作 "Mutex Lock" (只讓一個 Request 去回填 Cache) 或 "Soft Expiry" (邏輯過期，背景更新)。

### Scenario 2: The "Bad Deployment" (壞掉的部署)
**症狀 (Symptoms)**:
- 部署完成後 5 分鐘內，Error Rate (HTTP 5xx) 飆升。
- Latency 分佈出現雙峰 (Bimodal distribution)：舊機器快，新機器慢。

**排查 (Diagnosis)**:
- 比較新舊版本的 Metrics。
- 檢查新版 Log 是否有 Config 讀取錯誤或 NullPointer。

**處置 (Action)**:
1. **緊急**: **Rollback**。不要嘗試在線上 Debug 新版程式碼。
2. **事後**: 檢查 CI/CD 的 Smoke Test 覆蓋率。

### Scenario 3: The "Connection Leak" (連線洩漏)
**症狀 (Symptoms)**:
- 系統運行數天後逐漸變慢，重啟後恢復正常，但過幾天又變慢。
- 錯誤訊息出現 `ConnectionPoolTimeoutException` 或 `Too many connections`。

**排查 (Diagnosis)**:
- 監控 Connection Pool 的 `Active Connections` 指標，呈現階梯式上升且不下降。
- 檢查程式碼中是否有 `try-catch` 區塊忘記在 `finally` 中釋放資源。

**處置 (Action)**:
1. **緊急**: 重啟服務 (Restart) 釋放連線。
2. **修復**: Code Review 確保資源關閉，或設定 Connection Max Lifetime 強制回收。