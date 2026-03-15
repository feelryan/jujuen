# 生態系整合與原生模組 / Ecosystem Integration & Native Modules

在 Node.js 的世界裡，JavaScript 解決了 95% 的 I/O 密集型問題，但剩下的 5%——通常是極度 CPU 密集 (CPU-intensive) 或需要底層系統存取 (Low-level system access) 的場景——則需要跨越邊界，整合 C++、Rust 或 WebAssembly。本章節探討如何安全、高效地進行這種整合。

---

## Mental model｜心智模型

### 1. The Manager and The Specialist (經理與專家)
將 Node.js (V8 Engine) 想像成一位**經理**，擅長調度、溝通與處理 I/O 事件；而 Native Modules (C++/Rust Addons) 則是**專門領域的專家**（如影像處理、加密運算）。
- **Expensive Context Switch**：經理與專家之間的溝通（JS to C++ boundary crossing）是有成本的。你不會為了計算 `1 + 1` 去請教專家，你只會在需要處理百萬級別矩陣運算時才將任務外包。
- **Blocking Risk**：如果專家在經理的辦公室（Main Thread）裡進行長時間運算，經理就無法接聽電話（處理其他請求）。必須將專家移至獨立的工作間（libuv Thread Pool 或 Worker Threads）。

### 2. The Three Tiers of Integration (整合的三個層次)
在決定如何整合時，應依據需求選擇層次：
1.  **FFI (Foreign Function Interface)**：最快實作，效能稍差。直接呼叫動態連結庫 (.dll/.so)。適合簡單調用現有 C library。
2.  **WebAssembly (Wasm)**：最安全，可攜性最高。在沙盒中執行，接近原生速度。適合純運算邏輯（如壓縮、編碼），不依賴 OS 特性。
3.  **Node-API (N-API)**：最強大，ABI 穩定。直接與 V8/Node 互動。適合需要極致效能或操作 OS 底層 API（如驅動程式溝通）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Prefer N-API (Node-API) over NAN
**永遠優先選擇 Node-API (前稱 N-API)。**
- **Legacy (NAN/V8 direct)**：舊式寫法依賴 V8 版本，Node.js 升級時需要重新編譯，甚至修改 C++ 程式碼。
- **Modern (Node-API)**：提供 ABI Stability（二進位介面穩定性）。編譯一次，可以在不同版本的 Node.js 上執行，無需重新編譯。這對於維護 Library 至關重要。

### 2. The "Hybrid" Module Pattern (混合模組模式)
不要用 C++ 寫整個應用程式。
- **JS for Interface**：用 JavaScript 處理參數驗證、預設值、Promise 包裝與錯誤處理流程。
- **Native for Core Logic**：C++ 僅負責最核心的運算或系統呼叫。
- **Benefit**：降低 C++ 程式碼複雜度，減少 Segfault 風險，並讓 API 對 JS 開發者更友善。

### 3. Asynchronous Work via `libuv` (非同步處理)
如果 Native 函式執行時間超過 1ms，**絕對不要**在 Main Thread 上同步執行。
- 使用 `napi_create_async_work` 或相關 wrapper（如 `Napi::AsyncWorker`）。
- 這會將工作丟給 `libuv` 的 thread pool，待完成後再透過 callback 或 Promise 回到 Main Thread。

### 4. Rust with `napi-rs` (現代化選擇)
在 2024+ 的專案中，**Rust** 是比 C++ 更佳的選擇。
- 使用 **`napi-rs`** 或 **`neon`**。
- **Memory Safety**：Rust 的 Borrow checker 能在編譯期防止 Buffer Overflows 和 Memory Leaks，這是寫 Node.js Addons 最常見的崩潰原因。
- **Tooling**：Cargo 的依賴管理遠勝於 C++ 的手動管理。

### 5. Prebuild Distribution (預編譯發布)
不要讓使用者的 `npm install` 觸發編譯（`node-gyp rebuild`）。這需要使用者安裝 Python、Make、GCC/MSVC，極易失敗。
- 使用 **`prebuildify`** 或 **`node-pre-gyp`**。
- 在 CI/CD 階段針對常見 OS (Windows/Linux/macOS) 和架構 (x64/arm64) 預先編譯好 `.node` 檔，發布時直接下載。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Chatty" Interface (過度頻繁的邊界跨越)
- **Anti-pattern**：在 JS 迴圈中呼叫 Native 函式 100 萬次，每次只做一點點加法。
- **Consequence**：跨越 JS/C++ 邊界的開銷（Overhead）比運算本身還大，導致效能比純 JS 還慢。
- **Solution**：**Batching**。將整個陣列或 Buffer 傳入 Native 層，在 C++/Rust 內部跑迴圈。

### 2. Blocking the Event Loop (阻塞事件迴圈)
- **Anti-pattern**：在 C++ Addon 中執行 `sleep()` 或長時間的 CPU 運算，卻沒有使用 AsyncWorker。
- **Consequence**：整個 Node.js process 凍結，無法處理任何網路請求或 Timer。
- **Detection**：使用 `perf` 或 Node.js 的 `--prof` 查看 Event Loop 延遲。

### 3. Memory Mismanagement (記憶體管理失誤)
- **Anti-pattern**：在 C++ 中 `new` 了物件卻忘記 `delete`，或者錯誤地持有 V8 物件的參照（Persistent handles）導致 GC 無法回收。
- **Consequence**：Memory Leak，最終導致 OOM (Out of Memory) Crash。
- **Solution**：使用 Smart Pointers (`std::unique_ptr`, `std::shared_ptr`) 或 Rust。

### 4. Ignoring `Buffer` Ownership (忽略 Buffer 所有權)
- **Pitfall**：將 JS Buffer 的指標傳給 C++ 進行非同步寫入，但在 C++ 完成前，JS 端已經讓該 Buffer 被 GC 回收。
- **Consequence**：Use-after-free，導致 Segfault (Segmentation Fault) 程式直接崩潰。
- **Solution**：在非同步操作期間，Native 端必須建立對該 Buffer 的 `Napi::Reference` 以防止 GC。

---

## Checklists & workflows｜檢查清單與流程

### Decision Workflow: Do I need a Native Module?
1.  **Is it pure computation?**
    - Yes -> Can specific algorithms be optimized in JS? -> No -> **Try WebAssembly**.
2.  **Do I need existing C/C++ libraries?**
    - Yes -> **Use Node-API (N-API)**.
3.  **Do I need system-level access (drivers, OS API)?**
    - Yes -> **Use Node-API (N-API)**.
4.  **Is performance critical and JS is the bottleneck?**
    - Yes -> **Use Rust (`napi-rs`) or C++ (N-API)**.

### Implementation Checklist
- [ ] **Technology Selection**: 優先考慮 Rust (`napi-rs`)，其次是 C++ (`node-addon-api`)，純運算考慮 Wasm。
- [ ] **Async Design**: 確保所有耗時操作都實作為非同步 (Return Promise)。
- [ ] **Error Handling**: C++ 端的 Exception 必須被捕獲並轉換為 JS Error 拋出，否則會導致 Crash。
- [ ] **Memory Safety**: 檢查所有 `malloc/new` 是否有對應釋放，或使用 RAII 模式。
- [ ] **Thread Safety**: 確保 Native 程式碼是 Thread-safe 的（如果使用了全域變數）。

### Production Readiness Checklist
- [ ] **Prebuilds**: 設定 GitHub Actions / CI 自動編譯並上傳 binaries。
- [ ] **Fallback**: 如果預編譯檔下載失敗，是否有 fallback 機制（如嘗試本地編譯或降級回純 JS 實作）？
- [ ] **Memory Leak Testing**: 使用 `valgrind` (Linux) 或 Instruments (macOS) 針對 Addon 進行壓力測試。
- [ ] **Cross-Platform**: 驗證在 Windows, Linux (glibc/musl), macOS (Intel/Apple Silicon) 上皆可執行。

---

## Real-world examples｜實戰案例

### Example 1: High-Performance Image Processing (Sharp)
`sharp` 是 Node.js 生態系中最著名的原生模組案例。
- **Problem**: 使用純 JS 處理大圖片（Resize/Crop）速度慢且記憶體消耗巨大。
- **Solution**:
    - 使用 **C++** 綁定高效能的 `libvips` library。
    - 利用 **Node-API** 進行整合。
    - 實作 **Stream API**，讓圖片資料流過 C++ 層處理，無需將整張圖載入 V8 Heap。
    - **Trade-off**: 安裝時需要下載平台特定的 binary，偶爾會因環境問題導致安裝失敗。

### Example 2: CPU-bound Crypto (Bcrypt / Argon2)
密碼雜湊（Hashing）被設計為故意消耗 CPU 資源以抵抗暴力破解。
- **Pattern**:
    - **Main Thread**: 接收請求，驗證參數。
    - **Worker Pool (libuv)**: C++ Addon 將 Hashing 任務丟到背景執行緒。
    - **Main Thread**: 繼續處理其他 HTTP 請求。
    - **Callback**: Hashing 完成，通知 Main Thread 回傳結果。
- **Why**: 如果在 JS 主執行緒做 `bcrypt.hashSync`，伺服器吞吐量（RPS）會瞬間掉到個位數。

### Example 3: Rust Integration with `napi-rs`
現代專案中，將複雜演算法移至 Rust。

```rust
// src/lib.rs (Rust)
use napi_derive::napi;

#[napi]
pub fn fibonacci(n: u32) -> u32 {
  match n {
    1 | 2 => 1,
    _ => fibonacci(n - 1) + fibonacci(n - 2),
  }
}
```

```javascript
// index.js (Node.js)
const { fibonacci } = require('./index.node');

// 呼叫起來就像普通 JS 函式，但執行的是編譯過的機械碼
console.log(fibonacci(40)); 
```
- **優勢**: 開發體驗極佳，自動產生 `.d.ts` 型別定義，且無需擔心 C++ 的記憶體錯誤。