# Profiling 工具與可觀測性實戰 / Profiling Tools and Observability in Practice

## Mental model｜心智模型

在進行效能優化時，工程師常犯的最大錯誤是「憑直覺猜測瓶頸」。Profiling 與可觀測性（Observability）是將系統從「黑箱」轉變為「白箱」的過程。

建立以下三個層次的心智模型，有助於選擇正確的工具：

1.  **宏觀監控 (Macro - Metrics): "Is it healthy?"**
    *   **儀表板 (Dashboard)**：類似汽車儀表板。告訴你速度 (Throughput)、轉速 (CPU Usage)、油量 (Memory)。
    *   *用途*：發現異常趨勢，觸發警報。
2.  **請求追蹤 (Flow - Tracing): "Where did the time go?"**
    *   **分散式追蹤 (Distributed Tracing)**：類似包裹追蹤單。告訴你一個請求經過了哪些服務、資料庫，以及在每個節點停留了多久。
    *   *用途*：定位延遲發生在哪個元件（是 DB 慢，還是 API 慢？）。
3.  **微觀剖析 (Micro - Profiling): "Why is it slow?"**
    *   **剖析器 (Profiler)**：類似顯微鏡或 MRI。深入單一 Process 內部，查看 CPU 週期花在哪行程式碼、記憶體被誰佔用。
    *   *用途*：找出具體的程式碼熱點 (Hotspots) 或記憶體洩漏 (Leaks)。

> **The "Zoom-In" Strategy**: 不要一開始就跑 CPU Profiler。正確的流程通常是：
> **Alert (Metrics)** ➔ **Locate Component (Tracing)** ➔ **Fix Code (Profiling)**。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Flame Graphs (火焰圖) 的解讀與應用
火焰圖是 Profiling 的標準視覺化工具。
- **X 軸 (寬度)**：代表佔用的資源總量（如 CPU 時間或記憶體大小）。**越寬代表越消耗資源**。
- **Y 軸 (高度)**：代表呼叫堆疊 (Call Stack) 的深度。
- **Pattern**: 尋找 **"Plateaus" (平頂山)**。如果某個函數在圖形頂端且非常寬，表示它正在執行且沒有呼叫其他函數（On-CPU），這就是優化的首要目標。

### 2. 關聯性 ID 注入 (Correlation ID Injection)
為了讓 Logs 與 Traces 能互相參照，必須實作 Log Correlation。
- **做法**：在所有的 Log 輸出中自動注入 `TraceID` 和 `SpanID`。
- **效益**：當你在 Grafana/Kibana 看到一行錯誤 Log 時，可以直接複製 `TraceID` 跳轉到 Jaeger/Tempo 查看當時的完整請求路徑。

### 3. Continuous Profiling (持續性剖析)
不要等到出事才去 Production 掛 Profiler。
- **Pattern**: 使用 Pyroscope 或 Parca 等工具，以低採樣率（Low Overhead）在生產環境持續收集 Profile 數據。
- **效益**：可以進行 "Time Travel" 分析，比較「昨天正常時」與「今天異常時」的火焰圖差異 (Diff View)。

### 4. 區分 Wall Time 與 CPU Time
- **CPU Time Profiling**: 僅記錄程式碼在 CPU 上執行的時間。適用於計算密集型 (Computation-heavy) 任務。
- **Wall Time (Off-CPU) Profiling**: 記錄包含等待 I/O、鎖 (Lock)、網路請求的時間。適用於高延遲但低 CPU 使用率的場景。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Observer Effect" (觀察者效應)
- **誤區**：在生產環境開啟高頻率的 Profiling 或 Verbose Logging。
- **後果**：Profiling 工具本身消耗了 20% 的 CPU，導致服務更慢，甚至 Crash。
- **修正**：使用採樣 (Sampling) Profiler，並確保 Overhead 控制在 1-2% 以內。

### 2. 忽略 GC (Garbage Collection) 的影響
- **誤區**：看到 CPU 飆高，只專注優化演算法，卻忽略了記憶體分配。
- **後果**：程式碼邏輯很快，但產生大量短暫物件，導致 Runtime 頻繁 GC，GC 佔用了大半 CPU 時間。
- **修正**：查看 Profiler 中的 `runtime.gc` 或類似函數的佔比；優化 Allocation (記憶體分配) 而非僅優化 Execution。

### 3. 只有平均值，沒有 P99
- **誤區**：只看平均延遲 (Average Latency)。
- **後果**：平均 200ms 看起來很健康，但其實有 1% 的請求卡了 10 秒 (Long-tail latency)，導致重要客戶流失。
- **修正**：永遠觀測 P95, P99, P999 延遲指標。

### 4. 在開發環境做效能測試
- **誤區**：在筆電上跑 Profiler，認為結果等同於 Production。
- **後果**：硬體架構、網路延遲、資料量級完全不同，優化了錯誤的瓶頸。
- **修正**：盡可能在 Staging 環境模擬真實流量，或使用 Continuous Profiling 在 Production 採樣。

---

## Checklists & workflows｜檢查清單與流程

### 排查工作流 (Troubleshooting Workflow)

1.  **確認現象 (Symptom)**: 是 CPU 飽和？記憶體洩漏？還是單純延遲高但資源閒置？
2.  **縮小範圍 (Narrow Down)**: 使用 Distributed Tracing 找出是哪個 Service 或 DB Query 慢。
3.  **採集數據 (Capture)**:
    *   如果是 CPU 高：抓取 CPU Profile (30-60秒)。
    *   如果是 Memory 洩漏：抓取 Heap Profile (當下與一段時間後做 Diff)。
    *   如果是卡住不動：抓取 Goroutine/Thread Dump 或 Off-CPU Profile。
4.  **分析熱點 (Analyze)**: 生成 Flame Graph，尋找最寬的 "Plateaus"。
5.  **驗證修復 (Verify)**: 部署修正後，比較新舊 Flame Graph 與 P99 Latency。

### Readiness Checklist

- [ ] **Debug Symbols**: 生產環境的 Binary 是否保留了符號表（或有分開儲存），否則 Profiler 只能看到十六進位地址，無法對應函數名。
- [ ] **Access Control**: 開發者是否有權限在 Production (或受控的 Staging) 執行 Profiling 工具？
- [ ] **Tracing Coverage**: 關鍵路徑（HTTP, gRPC, DB, Cache, Message Queue）是否都已埋點？
- [ ] **Sampling Rate**: Tracing 和 Profiling 的採樣率是否設定得當（既能捕捉問題，又不影響效能）？
- [ ] **Logs Correlation**: Log 格式中是否包含 `trace_id`？

---

## Real-world examples｜實戰案例

### 案例一：JSON 序列化導致的 CPU 飆升
**情境**：一個 Go 寫的 API Gateway 在高流量時 CPU 飆升至 90%，導致 Auto-scaling 頻繁觸發。
**分析**：
1.  查看 Metrics，發現流量與 CPU 成正比，無 I/O 等待。
2.  開啟 CPU Profiler 採樣 30 秒。
3.  生成 Flame Graph，發現 40% 的寬度被 `encoding/json.Marshal` 及其反射 (Reflection) 邏輯佔據。
**解決**：將標準庫 `encoding/json` 替換為高效能的第三方庫（如 `json-iterator` 或 `sonic`），或針對特定熱點結構手寫 Marshal 方法。
**結果**：CPU 使用率下降至 40%。

### 案例二：分散式系統中的「幽靈」延遲
**情境**：使用者回報「偶爾」存檔需要 5 秒，但 API Server 的 Log 顯示處理時間只有 50ms。
**分析**：
1.  這是一個典型的黑箱問題，單看 API Server 無法解釋。
2.  查看 Distributed Tracing (Jaeger)。
3.  發現 Trace 中有一段長達 4.9 秒的空白 (Gap)，發生在 API Server 呼叫 Database 之前。
4.  進一步檢查該 Span 的 Tags 與 Infrastructure Metrics。
**發現**：原來是 Database Connection Pool 滿了，應用程式在等待獲取連線 (Wait for connection)。這段時間不算在 DB Query 時間，也不算在 App 邏輯執行時間。
**解決**：調整 Connection Pool 大小，並增加 Connection Wait Time 的監控指標。

### 案例三：記憶體洩漏 (The Sawtooth vs. The Ramp)
**情境**：Java 服務每隔兩天就會 OOM (Out of Memory) 重啟。
**分析**：
1.  觀察 Memory Metrics。正常的圖形應該是鋸齒狀 (Sawtooth)——記憶體上升，GC 後下降回基線。
2.  此案例的圖形是階梯狀 (Staircase) 或斜坡狀 (Ramp)——每次 GC 後，記憶體低點 (Baseline) 都比上次高。
3.  使用 Heap Dump 分析工具 (如 MAT 或 JProfiler)。
**發現**：一個 `static HashMap` 被用來做本地快取，但沒有實作過期淘汰機制 (TTL) 或最大容量限制。
**解決**：改用 Guava Cache 或 Caffeine，並設定 `expireAfterWrite`。