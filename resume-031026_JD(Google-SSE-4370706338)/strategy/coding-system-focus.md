# 程式測驗策略：演算法與腳本能力 / Coding Strategy: Algorithms & Scripting

## Why this matters｜為什麼這個主題重要

對於 **Diagnostics, Tools, Google Cloud** 這個職位而言，面試官對程式能力的期待與一般的 Web Application Engineer 有顯著不同。

1.  **Nature of the Job (工作本質)**:
    *   **JD 關鍵字**：`System programming`、`interacts with hardware`、`diagnostic tools`、`Linux`。
    *   這意味著你寫的程式碼通常是用來**解析日誌 (Log Parsing)**、**自動化硬體測試 (Test Automation)**、或是**處理大量系統訊號 (Signal Processing)**。
    *   相比於複雜的 Dynamic Programming，面試官更看重你處理 **字串 (Strings)**、**檔案 I/O (File I/O)**、**正規表達式 (Regex)** 與 **並發 (Concurrency)** 的能力。

2.  **The "Scripting" Interview Round (腳本能力面試)**:
    *   Google 的 SRE 或 Infra 相關職位常有一輪專門針對 "Scripting/Practical Coding" 的面試。
    *   若你只準備標準 LeetCode 演算法，可能會在被要求「讀取一個 50GB 的 Log 檔並統計錯誤率」時，因為試圖將檔案全部載入記憶體 (Memory Limit Exceeded) 或忘記如何處理 File Stream 而失敗。

3.  **Ryan's Gap (你的現狀與缺口)**:
    *   你的履歷強項在於 **Java/Spring Boot/Web App**。這類開發通常依賴框架處理底層 I/O。
    *   此職位需要展示你具備 **"Closer to Metal"** 的思維：如何高效使用 Python 或 C++ 進行系統層級的操作，而不僅僅是呼叫 API。

---

## Step‑by‑step strategy｜具體行動步驟

建議在 1–4 週內執行以下計畫，將重點從「解題」轉向「解決系統問題」。

### Week 1: Language Selection & Standard Libraries (語言與標準庫)
*   **Action**: 決定面試主要語言。雖然你會 Java，但針對 Tools/Infra 職位，強烈建議使用 **Python** (速度快、字串處理強) 或 **C++** (JD 明確提到，且適合系統底層)。
    *   *若選 Python*：需精通 `sys`, `os`, `re`, `collections`, `heapq`。
    *   *若選 C++*：需精通 STL (`vector`, `map`, `unordered_map`, `string` manipulation)。
*   **Drill**: 每天花 30 分鐘練習不查文件寫出 File Reader 和 Regex matcher。

### Week 2: High-Yield Topics for Diagnostics (高投報率題型)
針對 "Diagnostics & Tools" 的場景，優先練習以下類型的題目（LeetCode 對應標籤）：
1.  **String Manipulation & Parsing**: 字串處理是 Log 分析的核心。
    *   *Focus*: String split, Regex matching, Anagrams, Palindromes.
2.  **Hash Maps & Sets**: 快速查找錯誤碼、去重 (De-duplication)。
3.  **Intervals (區間問題)**: 處理時間序列 Log、排程任務 (Scheduling)。
    *   *Focus*: Merge Intervals, Insert Interval.
4.  **Topological Sort (拓撲排序)**: 處理安裝依賴 (Dependency Resolution)、編譯順序。

### Week 3: System Interaction & Scalability (系統交互與擴展性)
*   **Scenario Practice**: 練習處理「無法一次放入記憶體」的資料。
    *   *題目*: "How to find the top 10 error messages in a 1TB log file?"
    *   *策略*: 使用 **Streaming (Line-by-line processing)** + **Min-Heap**。
*   **Concurrency**: 複習基本的 Thread/Process 概念。
    *   *題目*: "Design a thread-safe logger" 或 "Producer-Consumer problem"。

### Week 4: Mock & Speed (模擬與速度)
*   **Mock Interview**: 找人模擬面試，特別要求對方出「實務應用題」而非純演算法題。
*   **Constraint Check**: 在寫每一行 code 前，先大聲說出你的 Time Complexity 和 Space Complexity。

---

## Examples & templates｜範例與句型

在面試中，你可以使用以下「模板」來展現你對系統程式設計的熟悉度。

### 1. The "Log Parsing" Template (Python Example)
當遇到處理大量文字資料的問題時，展現你對 **Memory Efficiency** 的重視：

```python
import re
from collections import defaultdict

# Pattern: Don't read whole file at once. Use a generator/iterator.
def process_large_log(file_path):
    error_pattern = re.compile(r"ERROR: (\d+)")
    counts = defaultdict(int)
    
    try:
        # Signal: You know how to handle file resources safely
        with open(file_path, 'r') as f:
            for line in f:  # Signal: Line-by-line processing for O(1) memory
                match = error_pattern.search(line)
                if match:
                    error_code = match.group(1)
                    counts[error_code] += 1
    except FileNotFoundError:
        return None # Signal: Error handling
        
    return counts
```

### 2. The "Dependency Resolution" Template (Graph/DFS)
當遇到 "Build Order" 或 "Task Scheduling" 問題時（常見於 Tools 開發）：

```python
# Signal: You understand directed graphs for system dependencies
def build_order(tasks, dependencies):
    graph = {t: [] for t in tasks}
    for u, v in dependencies:
        graph[u].append(v)
    
    visited = set()
    path = set()
    order = []
    
    def dfs(node):
        if node in path: return False # Cycle detected (Circular dependency)
        if node in visited: return True
        
        path.add(node)
        for neighbor in graph[node]:
            if not dfs(neighbor): return False
        
        path.remove(node)
        visited.add(node)
        order.append(node)
        return True
```

### 3. Clarifying Questions (釐清問題的句型)
*   "Is the input fitting in memory, or should I treat it as a stream?" (資料量是否大到需要串流處理？)
*   "Are we running this on a single machine or a distributed system?" (單機還是分散式？這決定了是否用 MapReduce 思維)
*   "Do we need to handle unicode characters or just ASCII?" (針對 Log parsing 很重要)

---

## Signals for interviewers｜要讓面試官看到的訊號

若你照著上述策略準備，面試官會在你的表現中捕捉到以下 **Positive Signals**：

1.  **System Awareness (系統意識)**:
    *   你主動考慮了記憶體限制 (Memory Constraints) 和 I/O 成本，而不僅僅是演算法的 Big O。
    *   *Signal*: "Since this is a diagnostic tool running on a production server, we should minimize CPU usage to avoid affecting the main service."

2.  **Robustness (強健性)**:
    *   你的程式碼考慮了「檔案不存在」、「權限不足」、「Log 格式損壞」等邊界情況。這是 Tooling Engineer 的核心素養。

3.  **Tooling Mindset (工具思維)**:
    *   你傾向於寫出可重用 (Reusable)、模組化 (Modular) 的腳本，而不是一次性的 Spaghetti code。

4.  **Linux/OS Proficiency (Linux 熟練度)**:
    *   在解釋解法時，能提及 OS 概念（例如：Buffer size, File Descriptors, Pipes）。

---

## Common pitfalls｜常見錯誤與避免方式

1.  **Pitfall: Over-Engineering (過度設計)**
    *   *錯誤*: 寫一個簡單的 Log Parser，卻定義了 5 個 Class 和 Factory Pattern。
    *   *修正*: 針對 Scripting 題目，**Keep it simple**。函式 (Functions) 通常比類別 (Classes) 更適合快速解決問題。

2.  **Pitfall: Ignoring Library Power (忽視標準庫)**
    *   *錯誤*: 自己手寫一個 Sort 演算法或 Hash Map 實作。
    *   *修正*: Google 允許並鼓勵使用標準庫 (Standard Library)。展現你熟悉 `heapq.nlargest` 或 `collections.Counter` 能大幅加分。

3.  **Pitfall: Silent Coding (悶頭寫 Code)**
    *   *錯誤*: 拿到題目後沈默 10 分鐘狂寫。
    *   *修正*: **Think out loud**. 特別是在做系統工具設計時，解釋你的權衡 (Trade-off) 至關重要（例如：「我選擇犧牲一點空間來換取更快的查詢速度...」）。

---

## Checklist｜檢查清單

- [ ] **Language**: 我已選定 Python 或 C++ 作為主要面試語言，並熟悉其 File I/O 與 Regex 語法。
- [ ] **Basics**: 我能不查文件手寫出 BFS, DFS, Binary Search, Merge Sort。
- [ ] **Data Structures**: 我熟悉 Hash Map, Stack, Queue, Heap (Priority Queue) 的應用場景。
- [ ] **Tooling Specifics**: 我練習過至少 3 題 Log Parsing / String Manipulation 的題目。
- [ ] **System Limits**: 我習慣在解題前詢問 Input Size，並根據記憶體限制調整解法。
- [ ] **Mock**: 我已進行過至少一次模擬面試，並練習邊寫邊解釋 (Vocalization)。