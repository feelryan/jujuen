# 除錯與故障排除流程 / Debugging & Troubleshooting Workflow

## Mental model｜心智模型

在資深工程師的眼裡，除錯不僅僅是「修復錯誤」，而是一個**科學化的假設驗證過程（Scientific Method）**與**觀測層級（Observability Layers）**的切換。

### 1. 偵探與醫生 (The Detective & The Doctor)
- **開發階段 (Development)**：你是偵探。你可以隨時暫停時間（Breakpoint），檢查每一個變數的狀態，甚至修改現實（Modify variables at runtime）來驗證假設。這是 **PDB/IPDB** 的領域。
- **生產環境 (Production)**：你是醫生，面對的是正在跑馬拉松的心臟病患。你不能讓心臟停下來檢查（Stop-the-world debugging），你只能使用非侵入式的儀器（MRI/X-Ray）來觀察運作中的系統。這是 **py-spy** 與 **memray** 的領域。

### 2. 觀測光譜 (The Spectrum of Observability)
除錯策略取決於你能承受的「干擾程度（Overhead）」：
- **High Overhead / High Detail**: Step-through Debugging (PDB), Tracing (sys.settrace). 適用於本地重現。
- **Medium Overhead**: Profiling (cProfile), Detailed Logging. 適用於測試環境或特定效能調優。
- **Low Overhead**: Sampling Profiling (py-spy), Metrics. 適用於生產環境即時監控。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 互動式除錯 (Interactive Debugging)
別再只依賴 `print()` 了。在開發環境中，使用 `ipdb` (IPython Debugger) 能大幅提升效率。

- **Use `breakpoint()`**: Python 3.7+ 的內建函式。
  - 設定環境變數 `PYTHONBREAKPOINT=ipdb.set_trace`，程式碼中只需寫 `breakpoint()`，自動呼叫增強版 debugger。
- **Post-mortem Debugging**: 程式崩潰後自動進入除錯模式。
  - 執行指令：`python -m ipdb main.py`
  - 在 code 中：
    ```python
    import sys, ipdb
    try:
        main()
    except Exception:
        ipdb.post_mortem(sys.exc_info()[2])
    ```

### 2. 生產環境效能分析 (Production Profiling with py-spy)
當生產環境 CPU 飆高或程式卡死（Deadlock/Hang）時，**py-spy** 是神器。它是一個 Sampling Profiler，直接讀取 process memory，**不需要修改程式碼，也不會暫停程式執行**。

- **Top View (即時監控)**: 類似 Linux `top` 指令，但顯示的是 Python 函式。
  ```bash
  # 需 sudo 權限
  py-spy top --pid <PID>
  ```
- **Dump Stack (抓取當前堆疊)**: 查看程式「現在」卡在哪一行。
  ```bash
  py-spy dump --pid <PID>
  ```
- **Flamegraph (火焰圖錄製)**: 錄製一段時間並生成火焰圖，分析效能瓶頸。
  ```bash
  py-spy record -o profile.svg --pid <PID> --duration 60
  ```

### 3. 記憶體分析 (Memory Profiling with memray)
Python 的記憶體問題通常分為：記憶體洩漏 (Leak) 與 記憶體膨脹 (Bloat)。`memray` 是目前最推薦的工具，因為它能追蹤 C/C++ extension 的記憶體分配（這是 `tracemalloc` 做不到的）。

- **Live Mode**:
  ```bash
  memray run --live my_script.py
  ```
- **Native Tracking**: 追蹤 NumPy/Pandas 等 C 套件的記憶體。
  ```bash
  memray run --native my_script.py
  ```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Print" Debugging Trap (沈迷於 Print 大法)
- **現象**：在 production code 留下大量的 `print(vars)`。
- **後果**：
  - 污染 stdout/logs，導致真正的錯誤訊息被淹沒。
  - I/O 操作本身很慢，可能改變 Race Condition 的時序（Heisenbug），導致 bug 在除錯時消失。
  - 可能意外洩漏敏感資料（PII/Credentials）到日誌中。

### 2. Attaching PDB in Production (在生產環境掛載 PDB)
- **現象**：試圖在流量進來時使用 `pdb.set_trace()`。
- **後果**：PDB 會暫停整個 Process。對於 Web Server (如 Gunicorn/Uvicorn) 來說，這意味著該 Worker 停止回應請求，導致 Timeout 或 Load Balancer 報錯。
- **修正**：生產環境應使用 `py-spy` 或日誌追蹤，而非暫停式除錯。

### 3. Ignoring C-Extension Leaks (忽視 C 擴充套件洩漏)
- **現象**：只用 Python 內建的 `tracemalloc` 或 `objgraph` 檢查，發現 Python 物件數沒增加，但 RAM 卻一直吃光。
- **原因**：問題出在 C 語言層（如 XML parser, Image library, NumPy）。
- **修正**：必須使用 `memray` 並開啟 `--native` 模式。

---

## Checklists & workflows｜檢查清單與流程

### Scenario A: 程式邏輯錯誤 (Logic Bug)
_適用於開發與測試階段_

- [ ] **重現 (Reproduce)**：能否建立一個 Minimal Reproducible Example (MRE)？
- [ ] **斷點 (Breakpoint)**：在可疑處插入 `breakpoint()`。
- [ ] **檢查狀態 (Inspect)**：
    - 使用 `p variable` 查看變數。
    - 使用 `pp variable` 美化輸出。
    - 使用 `w` (where) 查看 Call Stack。
- [ ] **驗證假設 (Hypothesis)**：在 IPDB 中執行程式碼片段，確認修正邏輯是否正確。

### Scenario B: 生產環境 CPU 飆高或卡死 (High CPU / Hang)
_適用於 Production_

- [ ] **確認 PID**：使用 `ps aux | grep python` 找到目標 Process ID。
- [ ] **非侵入式觀察**：執行 `sudo py-spy top --pid <PID>`。
    - [ ] 是否卡在某個特定的函式？
    - [ ] 是否卡在 `acquire_lock` (Deadlock)？
    - [ ] 是否卡在 I/O 等待？
- [ ] **快照證據**：執行 `py-spy dump --pid <PID>` 保存當下堆疊以供後續分析。
- [ ] **效能錄製**：若非卡死而是變慢，執行 `py-spy record` 生成火焰圖。

### Scenario C: 記憶體洩漏 (Memory Leak)
_適用於 CI/CD 或 Staging_

- [ ] **基準線測試**：確保程式在閒置時記憶體是平穩的。
- [ ] **壓力測試**：使用 `memray run -o output.bin my_script.py` 執行一段高負載操作。
- [ ] **視覺化分析**：
    - `memray flamegraph output.bin`
    - 查看火焰圖中「最寬」且「顏色最深」的區塊。
- [ ] **檢查 Native Code**：如果 Python 堆疊看不出問題，加上 `--native` 重跑一次。

---

## Real-world examples｜實戰案例

### 1. The "Stuck" Background Worker (卡死的背景任務)
**情境**：一個 Celery Worker 處理影像轉檔，偶爾會卡住不動，CPU 使用率 0%，也不報錯。

**除錯流程**：
1. SSH 進入伺服器。
2. 找到卡住的 worker PID。
3. 執行 `sudo py-spy dump --pid 12345`。
4. **發現**：Stack trace 顯示停在 `requests.get(...)` 的 socket read 階段。
5. **根因**：程式碼沒有設定 `timeout`，導致連線掛起無限等待。
6. **解法**：加上 `requests.get(..., timeout=10)`。

### 2. The Slow API Endpoint (龜速的 API)
**情境**：某個 API 查詢回應時間長達 5 秒，但在本地開發時很快。

**除錯流程**：
1. 在 Staging 環境模擬請求。
2. 使用 `py-spy record --pid <PID> --duration 10 -o profile.svg`。
3. 下載並用瀏覽器打開 `profile.svg`。
4. **發現**：火焰圖顯示 80% 的時間花在 `pandas.read_csv()` 上，且是在一個迴圈內被呼叫。
5. **根因**：IO 讀取被錯誤地放在迴圈內，而非預先讀取快取。

### 3. The Invisible Memory Leak (隱形記憶體殺手)
**情境**：服務跑了三天後 OOM (Out of Memory) 重啟，`gc.get_objects()` 看不出異常。

**除錯流程**：
1. 使用 `memray run --native app.py` 啟動服務。
2. 跑一輪壓力測試。
3. 生成報告：`memray flamegraph output.bin`。
4. **發現**：記憶體大量分配在 `lxml.etree` 的 C 函式中。
5. **根因**：XML 解析後未正確釋放 C 層級的 tree 物件（Python GC 有時無法及時回收 C extension 的資源）。
6. **解法**：手動呼叫清理函式或改用更現代的解析庫。