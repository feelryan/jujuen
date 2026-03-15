# 效能優化與記憶體管理清單 / Performance Optimization & Memory Checklist

## Mental model｜心智模型

在 Python 中進行效能優化，必須先建立正確的認知：**Python 是為了開發者效率（Developer Productivity）而生，而非機器執行效率（Machine Efficiency）。**

因此，優化的核心策略並非「把每一行 Python 寫得像 C 一樣快」，而是「找出瓶頸，並將繁重的工作交給底層（C/Rust）或更合適的架構」。

### 1. The Optimization Pyramid (優化金字塔)
不要一開始就跳進 C-Extensions。請遵循以下路徑：
1.  **演算法與資料結構 (Algorithms & Data Structures)**：$O(N^2)$ 改為 $O(N)$ 或 $O(1)$ 是最巨大的優化。
2.  **善用內建功能 (Built-ins & Standard Library)**：Python 的 `list`, `dict`, `set` 是高度優化的 C 實作。
3.  **向量化運算 (Vectorization)**：使用 NumPy/Pandas 將迴圈推向 C 層級。
4.  **編譯與擴展 (Compilation/Extensions)**：使用 Cython, PyO3 (Rust), 或 PyPy/JIT。

### 2. Memory Management Reality (記憶體管理真相)
-   **Reference Counting (引用計數)**：這是 Python 記憶體管理的主力。當物件的引用歸零，記憶體立即釋放。
-   **Garbage Collection (垃圾回收)**：僅用於處理「循環引用 (Reference Cycles)」。
-   **Everything is an Object**：一個簡單的整數 `x = 1` 在 Python 中也是一個完整的 PyObject struct，這意味著巨大的 Memory Overhead。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Lazy Evaluation with Generators (惰性求值)
處理大量資料時，避免一次性將所有資料載入記憶體。
-   **Pattern**: 使用 `yield` 關鍵字或 Generator Expressions `(x for x in data)`。
-   **Benefit**: 記憶體使用量從 $O(N)$ 降為 $O(1)$。

```python
# Bad: Loads 1GB file into RAM
def process_file(path):
    lines = []
    with open(path) as f:
        for line in f:
            lines.append(line.upper())
    return lines

# Good: Stream processing
def process_file_lazy(path):
    with open(path) as f:
        for line in f:
            yield line.upper()
```

### 2. Using `__slots__` for High-Volume Objects
如果你需要建立數百萬個小型物件（例如：Pixels, TradeTicks, Nodes），標準的 `__dict__` 字典儲存屬性會消耗大量記憶體。
-   **Pattern**: 在 class 定義中加入 `__slots__`。
-   **Benefit**: 禁止動態屬性建立，移除每個實例的 `__dict__`，節省約 40-50% 記憶體。

```python
class Point:
    __slots__ = ('x', 'y')  # Fixed memory layout
    def __init__(self, x, y):
        self.x = x
        self.y = y
```

### 3. Fast Lookups with Sets and Dicts
-   **Pattern**: 檢查元素是否存在（Membership testing）時，永遠使用 `set` 或 `dict`，不要用 `list`。
-   **Why**: List 是 $O(N)$，Set/Dict 是 $O(1)$（平均情況）。

### 4. Caching Results (Memoization)
對於重複計算且結果相同的函數（Pure Functions），使用快取。
-   **Tool**: `functools.lru_cache`。

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation(param):
    # ... heavy calculation ...
    return result
```

### 5. String Concatenation
-   **Pattern**: 使用 `''.join(list_of_strings)` 而非在迴圈中使用 `+=`。
-   **Why**: String 是不可變的（Immutable）。`+=` 會在每次迭代時建立新的字串物件並複製內容，導致 $O(N^2)$ 的複雜度。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Premature Optimization (過早優化)
-   **Pitfall**: 在沒有 Profiling 數據的情況下，為了「感覺比較快」而寫出難以閱讀的程式碼。
-   **Correction**: **Make it work, make it right, make it fast.** 先寫出可讀的程式碼，遇到效能問題再用 Profiler 找瓶頸。

### 2. The Global Variable Trap (全域變數陷阱)
-   **Pitfall**: 在 Module 層級宣告大型 `list` 或 `dict` 作為快取，卻沒有清理機制。
-   **Consequence**: 這些物件的 Reference Count 永遠不會歸零，導致記憶體洩漏（Memory Leak），直到 Process 結束。

### 3. Blocking the GIL with CPU-bound Threads
-   **Pitfall**: 使用 `threading` 模組來加速 CPU 密集的運算（如影像處理、矩陣運算）。
-   **Reality**: Python 的 GIL (Global Interpreter Lock) 限制同一時間只有一個 Thread 能執行 Python Bytecode。多執行緒在 CPU bound 任務中反而因為 Context Switch 而變慢。
-   **Fix**: 使用 `multiprocessing` 或 C-extensions (NumPy 釋放 GIL)。

### 4. Mutable Default Arguments as Memory Leaks
-   **Pitfall**: `def func(data=[])`。
-   **Consequence**: 該 `list` 在函數定義時就建立了，並且一直駐留在記憶體中。如果不斷往裡面 append 資料，它會無限膨脹。

---

## Checklists & workflows｜檢查清單與流程

### Performance Tuning Workflow (優化標準作業程序)

1.  **Establish Baseline (建立基準)**：寫好 Reproducible 的測試案例。
2.  **Profile (分析)**：使用工具找出熱點（Hotspots）。
    -   *CPU*: `cProfile`, `py-spy`, `line_profiler`
    -   *Memory*: `tracemalloc`, `memory_profiler`
3.  **Optimize (優化)**：針對瓶頸修改程式碼。
4.  **Verify (驗證)**：確保邏輯正確且效能確實提升。

### Optimization Checklist (優化檢核表)

- [ ] **演算法檢查**：是否在大數據集上使用了 $O(N^2)$ 的巢狀迴圈？能否改為 $O(N)$？
- [ ] **I/O 檢查**：瓶頸是在 CPU 運算還是在等待 I/O（網路/硬碟）？如果是 I/O，是否已改用 AsyncIO 或 Threading？
- [ ] **迴圈檢查**：迴圈內部是否重複執行了不必要的屬性存取或計算？（將不變量移出迴圈）。
- [ ] **資料結構**：是否在 List 中頻繁搜尋？（改用 Set）。是否在 List 前端頻繁插入？（改用 `collections.deque`）。
- [ ] **向量化**：如果是數值運算，是否已嘗試 NumPy？

### Memory Leak Hunting Checklist (記憶體洩漏排查)

- [ ] **Global Objects**：檢查是否有全域變數（Global/Module level）持續增長。
- [ ] **Closures/Decorators**：檢查閉包是否意外捕捉了大型物件。
- [ ] **C-Extensions**：使用的第三方 C 擴展庫是否有已知的 Leak？
- [ ] **Tracemalloc**：使用 `tracemalloc` 比較兩個時間點的 Snapshot，找出增量最大的物件。

---

## Real-world examples｜實戰案例

### Example 1: Debugging Memory Leak with `tracemalloc`
這是一個典型的記憶體除錯腳本樣板。

```python
import tracemalloc

def run_suspect_code():
    # 模擬記憶體洩漏：全域變數不斷增加
    global_store = []
    for i in range(10000):
        global_store.append("x" * 1000)

def main():
    tracemalloc.start()
    
    # Snapshot 1: Before execution
    snapshot1 = tracemalloc.take_snapshot()
    
    run_suspect_code()
    
    # Snapshot 2: After execution
    snapshot2 = tracemalloc.take_snapshot()
    
    # 比較差異
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    
    print("[ Top 3 Memory Hogs ]")
    for stat in top_stats[:3]:
        print(stat)
        
if __name__ == "__main__":
    main()
```

### Example 2: Optimizing Membership Testing
在處理黑名單過濾或大量 ID 比對時的效能差異。

```python
import time

# 假設有 100 萬個 ID
large_dataset = list(range(1000000))
search_targets = range(999000, 1000000)

# Anti-pattern: List lookup O(N)
# Total complexity: O(M * N) where M is targets, N is dataset
start = time.time()
found = 0
for target in search_targets:
    if target in large_dataset: # Slow!
        found += 1
print(f"List lookup time: {time.time() - start:.4f}s")

# Best Practice: Set lookup O(1)
# Total complexity: O(M * 1) + O(N) for set creation
start = time.time()
large_set = set(large_dataset) # One-time cost
found = 0
for target in search_targets:
    if target in large_set: # Fast!
        found += 1
print(f"Set lookup time: {time.time() - start:.4f}s")
```

### Example 3: Profiling with `cProfile` (Command Line)
不要猜測哪裡慢，直接測量。

```bash
# 直接在終端機執行，依照 cumulative time (累積時間) 排序
python -m cProfile -s cumtime your_script.py
```

**解讀輸出：**
-   `ncalls`: 呼叫次數。如果某個簡單函數被呼叫了數億次，這就是優化點（Inline 或減少呼叫）。
-   `tottime`: 函數內部實際執行的時間（不含子函數）。如果這裡很高，表示該函數本身的演算法需要優化。
-   `cumtime`: 包含子函數的總執行時間。通常先看這裡找出最慢的路徑。