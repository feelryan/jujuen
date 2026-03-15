# 除錯與故障排除流程：Sanitizers 與 Core Dump 分析 / Debugging & Troubleshooting: Sanitizers & Core Dump Analysis

## Mental model｜心智模型

在 C++ 的世界裡，除錯不僅僅是「找出錯誤的邏輯」，更多時候是在進行「數位鑑識（Digital Forensics）」。由於 C++ 允許直接操作記憶體，許多錯誤（如 Buffer Overflow, Use-after-free）會導致 **Undefined Behavior (UB)**，這意味著程式當下可能不會崩潰，而是默默地破壞數據，直到很久之後才在完全無關的地方爆炸。

建立高效除錯流程的心智模型應包含以下三個層次：

1.  **顯微鏡模式 (Instrumentation)**：不要依賴肉眼 Code Review 或 `std::cout` 來猜測記憶體錯誤。使用 **Sanitizers (ASan, TSan, UBSan)** 將程式碼「武裝」起來，讓隱形的記憶體錯誤在發生瞬間就「大聲尖叫（Crash with report）」。
2.  **時光機模式 (Post-mortem Analysis)**：當程式在生產環境崩潰時，你無法重現現場。**Core Dump** 就是案發現場的凍結快照。你需要學會如何從這堆二進位資料中，還原出當時的 Call Stack 和變數狀態。
3.  **互動偵查 (Interactive Debugging)**：使用 GDB/LLDB 不只是為了設斷點（Breakpoint），更是為了探索狀態。你是在與執行中的 Process 對話，詢問它「現在誰持有這個鎖？」或「這個指標指向的記憶體內容是什麼？」。

> **The Golden Rule**: Make the invisible visible. Don't guess; instrument and measure.
> **黃金法則**：讓不可見的錯誤現形。不要猜測；使用工具檢測與測量。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 現代除錯標準配備：Sanitizers
在 GDB 介入之前，先讓編譯器幫你找 Bug。這是現代 C++ 開發的標準流程。

*   **AddressSanitizer (ASan)**: 檢測 Out-of-bounds, Use-after-free, Double-free, Memory leaks。
    *   *Flags*: `-fsanitize=address -g`
    *   *Best Practice*: 在 CI/CD Pipeline 中，務必有一個 Build 是開啟 ASan 的。
*   **UndefinedBehaviorSanitizer (UBSan)**: 檢測整數溢位、空指標解引用、對齊錯誤等。
    *   *Flags*: `-fsanitize=undefined -g`
    *   *Best Practice*: 通常與 ASan 一起使用。
*   **ThreadSanitizer (TSan)**: 檢測 Data Races。
    *   *Flags*: `-fsanitize=thread -g`
    *   *Note*: TSan 與 ASan 互斥，不能同時開啟。

### 2. 建置組態的選擇 (Build Configurations)
除錯不僅僅是 Debug mode 的事。

*   **Debug (`-O0 -g`)**: 最適合開發階段，變數未被優化，邏輯線性，適合 GDB 單步執行。
*   **RelWithDebInfo (`-O2 -g` or `-O3 -g`)**: **這是生產環境的最佳實踐**。你既需要優化後的效能，也需要在崩潰時能透過 Core Dump 看到符號（Symbols）。
    *   *Pattern*: 編譯時保留 debug info，但在發布時將符號檔（`.debug` 或 `.dSYM`）分離出來存檔，Binary 本身 strip 掉符號以減小體積。

### 3. Core Dump 管理策略
*   **啟用 Core Dump**: 確保系統層級 `ulimit -c unlimited` 已設定。
*   **自動化收集**: 在 Linux 環境常配合 `systemd-coredump` 或自定義腳本將 Core file 集中管理。

### 4. Valgrind 的定位
雖然 ASan 速度快（~2x overhead）且是編譯期注入，但 **Valgrind (Memcheck)** 不需要重新編譯即可運作（~20x overhead）。
*   *Use Case*: 當你沒有原始碼、無法重新編譯，或者懷疑是第三方 Library 導致的記憶體問題時，Valgrind 是最後防線。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. "Printf Debugging" for Memory Issues (用印日誌解記憶體問題)
*   **Bad**: 遇到 Segmentation Fault 時，試圖在每一行加 `printf("here\n")`。
*   **Why**: 記憶體錯誤往往是「海森堡蟲（Heisenbug）」。加入 `printf` 會改變記憶體佈局（Memory Layout）或執行時序，導致 Bug 暫時消失或轉移位置，浪費數小時。
*   **Fix**: 直接上 ASan 或 GDB。

### 2. 忽略 UBSan 的警告
*   **Bad**: 看到 UBSan 報錯 "signed integer overflow"，但程式沒崩潰，所以選擇忽略。
*   **Why**: 編譯器會假設 UB 永遠不會發生，並據此進行激進優化（例如直接刪除該段程式碼）。今天沒崩潰只是運氣好，明天換個編譯器版本可能就炸了。

### 3. 在優化過的代碼中迷失 (Debugging Optimized Code)
*   **Pitfall**: 在 `-O3` 優化下使用 GDB，發現程式碼「亂跳」或變數顯示 `<optimized out>`。
*   **Why**: 編譯器進行了指令重排（Instruction Reordering）或暫存器分配。
*   **Mitigation**: 如果必須 Debug Release build，專注於 Call Stack 和全域狀態，不要過度糾結於區域變數的單步追蹤。

### 4. 混用不相容的 Sanitizers
*   **Pitfall**: 試圖同時開啟 `-fsanitize=address` 和 `-fsanitize=thread`。
*   **Result**: 編譯失敗或執行期錯誤。這兩者都需要大幅修改記憶體存取邏輯，彼此衝突。

---

## Checklists & workflows｜檢查清單與流程

### 流程一：崩潰處理標準程序 (The Crash Workflow)

當程式發生 Segfault 或莫名崩潰時：

1.  **重現 (Reproduce)**
    - [ ] 是否有穩定的重現步驟？
    - [ ] 是否能在本地環境重現？

2.  **檢測 (Sanitize)**
    - [ ] **Recompile with ASan/UBSan**: `CXXFLAGS="-fsanitize=address,undefined -g -O1"`
    - [ ] **Run**: 執行程式，觀察 ASan 的紅色報錯輸出。通常它會精確指出哪一行分配了記憶體，哪一行非法存取了它。

3.  **分析 (Analyze)**
    - [ ] 如果 ASan 沒抓到，改用 **GDB/LLDB**。
    - [ ] `gdb ./my_app` -> `run` -> 等待崩潰 -> `bt` (Backtrace)。
    - [ ] 檢查 `frame X` 中的變數狀態。

### 流程二：死鎖與卡頓排查 (The Deadlock/Stuck Workflow)

當程式「卡住」不動時：

1.  **掛載 (Attach)**
    - [ ] 找到 Process ID (PID)。
    - [ ] `gdb -p <PID>`

2.  **全執行緒檢視 (Thread Inspection)**
    - [ ] (GDB) `info threads`：查看所有執行緒。
    - [ ] (GDB) `thread apply all bt`：**這是大絕招**，一次印出所有執行緒的堆疊。
    - [ ] 尋找是否有兩個執行緒互相等待對方的 Mutex（經典死鎖），或者所有 Worker thread 都在等待空的 Queue。

3.  **並行檢測 (Concurrency Check)**
    - [ ] 如果懷疑是 Data Race（偶發性崩潰或數據錯誤），**Recompile with TSan**: `-fsanitize=thread -g`。

### 流程三：Core Dump 分析 (Post-mortem)

當你拿到一個 `core` 檔案時：

- [ ] **準備環境**: 確保你有產生該 Core dump 的 **完全一致的 Binary** 和 **Debug Symbols**。
- [ ] **載入 GDB**: `gdb <path_to_binary> <path_to_core_dump>`
- [ ] **還原現場**:
    - `bt full`: 查看完整堆疊與區域變數。
    - `list`: 查看崩潰點附近的程式碼。
    - `info registers`: 查看暫存器（進階，用於查看指標是否被破壞）。

---

## Real-world examples｜實戰案例

### Case 1: The "Use-After-Free" caught by ASan

**Scenario**: 一個網路服務在處理完 Request 後偶爾會崩潰。
**Code (Simplified)**:
```cpp
std::string* processRequest() {
    std::string* data = new std::string("payload");
    // ... logic ...
    delete data; // 釋放記憶體
    return data; // 錯誤：回傳了懸空指標 (Dangling Pointer)
}

void handler() {
    std::string* str = processRequest();
    std::cout << *str << std::endl; // Use-after-free
}
```

**Without ASan**: 程式可能印出亂碼，可能崩潰，也可能看起來完全正常（最糟的情況）。
**With ASan Output**:
```text
=================================================================
==12345==ERROR: AddressSanitizer: heap-use-after-free on address 0x602000000010 ...
READ of size 32 at 0x602000000010 thread T0
    #0 0x401234 in handler() /path/to/main.cpp:10
    ...
0x602000000010 is located 0 bytes inside of 32-byte region ...
freed by thread T0 here:
    #0 0x7f... in operator delete(void*) ...
    #1 0x401180 in processRequest() /path/to/main.cpp:5
    ...
previously allocated by thread T0 here:
    #0 0x7f... in operator new(unsigned long) ...
    #1 0x401150 in processRequest() /path/to/main.cpp:3
```
**解析**: ASan 不僅告訴你哪裡讀取錯誤（READ），還告訴你這塊記憶體是**哪裡釋放的**（freed by...）以及**哪裡分配的**（allocated by...）。這直接指出了生命週期管理的邏輯錯誤。

### Case 2: Debugging a Deadlock with GDB

**Scenario**: 伺服器不再回應請求，CPU 使用率為 0%。
**Action**:
1. `gdb -p 12345` (Attach to process)
2. `(gdb) thread apply all bt`

**Output Analysis**:
```text
Thread 2 (Thread 0x7...):
#0  __lll_lock_wait ...
#1  0x... in pthread_mutex_lock ...
#2  0x... in DataManager::update() at data.cpp:45  <-- Waiting for Mutex A
#3  ...

Thread 1 (Thread 0x7...):
#0  __lll_lock_wait ...
#1  0x... in pthread_mutex_lock ...
#2  0x... in NetworkHandler::process() at net.cpp:88 <-- Waiting for Mutex B
```
**解析**: 透過 `bt` 發現 Thread 2 持有 B 等 A，Thread 1 持有 A 等 B。這是一眼就能看出的經典死鎖。解決方案是統一鎖的獲取順序（Lock Ordering）或使用 `std::scoped_lock` (C++17) 同時鎖定。

### Case 3: Iterator Invalidation

**Scenario**: 遍歷 `std::vector` 並刪除元素時崩潰。
**Anti-pattern Code**:
```cpp
std::vector<int> vec = {1, 2, 3, 4};
for (auto it = vec.begin(); it != vec.end(); ++it) {
    if (*it % 2 == 0) {
        vec.erase(it); // 錯誤：erase 會使當前 it 失效，下一次 ++it 是 UB
    }
}
```
**Fix (Idiomatic C++)**:
使用 Erase-Remove idiom 或 C++20 `std::erase_if`。
```cpp
// C++20
std::erase_if(vec, [](int x) { return x % 2 == 0; });
```
**Debugging**: 這種錯誤在 Debug mode (MSVC STL / libstdc++ debug mode) 通常會有 assertion failed，但在 Release mode 會變成隨機崩潰。開啟 `-D_GLIBCXX_DEBUG` (GCC) 或 `-D_LIBCPP_DEBUG` (Clang) 可以讓標準庫幫你檢查迭代器有效性。