# 現場面試：進階編碼能力 / Onsite: Advanced Coding & DSA | Onsite: Advanced Coding & DSA

## 1. 目標與範圍 | Goal & Scope
- **展示演算法熟練度**：證明你能解決中等到困難程度的演算法問題（如圖論、動態規劃、陣列操作）。｜**Demonstrate Algorithmic Proficiency**: Prove you can solve medium-to-hard algorithmic problems (e.g., Graphs, DP, Array manipulation).
- **產出高品質程式碼**：撰寫可讀性高、變數命名清晰且模組化的程式碼，而非僅僅是「能跑就好」的腳本。｜**Produce Production-Quality Code**: Write readable, clearly named, and modular code, not just "working" scripts.
- **溝通解題思路**：在編寫程式碼前，先與面試官討論多種解法並分析時間與空間複雜度。｜**Communicate Thought Process**: Discuss multiple approaches and analyze time/space complexity before writing code.
- **處理邊緣情況**：主動識別並處理極端輸入（如空值、超大數據、非法字元），展現資深工程師的嚴謹度。｜**Handle Edge Cases**: Proactively identify and handle extreme inputs (e.g., nulls, massive data, illegal characters), showing senior-level rigor.

## 2. 簡短開場稿 | Opening Script
*(Coding 面試通常直接切入正題，但若有簡單自我介紹環節，請保持極簡。｜Coding interviews usually jump straight in, but if there's a quick intro, keep it minimal.)*

- **你好，我是 Ryan。我有超過 15 年的軟體開發經驗，目前在 Innova Solutions 擔任資深工程師，專注於雲端原生醫療影像平台的後端開發與系統優化。**
  **Hi, I'm Ryan. I have over 15 years of software development experience. I'm currently a Senior Software Engineer at Innova Solutions, focusing on backend development and system optimization for a cloud-native medical imaging platform.**

- **我熟悉的語言是 Java 和 Python，今天我會使用 [選擇你的強項語言，如 Java] 來進行解題。**
  **My primary languages are Java and Python. I will be using [Java/Python] for the coding exercises today.**

## 3. 關鍵故事與成就 | Key Stories & Achievements
*(雖然這是 Coding 環節，但在解釋「為什麼這樣寫」或「優化經驗」時，可引用過往專案作為佐證。｜While this is a coding section, reference past projects when explaining "why you code this way" or "optimization experience".)*

- **搜尋引擎優化 (Hiveel/USTOSHOP)｜Search Engine Optimization (Hiveel/USTOSHOP)**
  - **情境**：需要處理數百萬筆產品/車輛資料的快速檢索與多欄位查詢。｜**Context**: Needed to handle fast retrieval and multi-field queries for millions of product/vehicle records.
  - **關聯**：這讓我對**雜湊表 (Hash Maps)**、**樹狀結構 (Trees)** 與**索引 (Indexing)** 的底層邏輯非常熟悉，這有助於我在面試中快速決定資料結構。｜**Relevance**: This made me very familiar with the underlying logic of **Hash Maps**, **Trees**, and **Indexing**, helping me quickly decide on data structures during interviews.

- **醫療影像自動化流程 (Innova Solutions)｜Medical Imaging Automation (Innova Solutions)**
  - **情境**：開發 "Push2Pacs" 自動化動作與排程審計報告，需處理大量併發事件。｜**Context**: Developed "Push2Pacs" automatic actions and scheduled audit reports, requiring handling of high-concurrency events.
  - **關聯**：這強化了我在**佇列 (Queues)** 管理與**批次處理 (Batch Processing)** 邏輯上的實作能力，特別是在處理非同步任務時。｜**Relevance**: This strengthened my implementation skills in **Queue** management and **Batch Processing** logic, especially when dealing with asynchronous tasks.

- **國家級警報系統 (Chunghwa Telecom)｜National Emergency Alert System (Chunghwa Telecom)**
  - **情境**：設計 e-SAV 雲端平台與緊急訊息警報，需確保極高的可靠度與低延遲。｜**Context**: Designed the e-SAV cloud platform and Emergency Message Alert system, requiring extreme reliability and low latency.
  - **關聯**：這涉及大規模系統的**圖論 (Graph)** 概念（如網路節點傳播）與**字串處理 (String Manipulation)**（訊息格式解析），這是我解決複雜邏輯問題的基礎。｜**Relevance**: This involved **Graph** concepts (network node propagation) and **String Manipulation** (message parsing) for large-scale systems, forming my foundation for solving complex logic problems.

## 4. 常見追問與應對 | Likely Follow‑ups & Responses

- **Q: 這段程式碼的時間複雜度與空間複雜度是多少？｜Q: What is the time and space complexity of this code?**
  - **A (Java/General)**: 目前解法使用了雙層迴圈，時間複雜度是 O(N^2)。如果我們使用 HashMap 來快取已訪問的元素，可以優化到 O(N)，但空間複雜度會從 O(1) 增加到 O(N)。｜**A**: The current approach uses a nested loop, so it's O(N^2). If we use a HashMap to cache visited elements, we can optimize time to O(N), but space complexity will increase from O(1) to O(N).

- **Q: 如果輸入資料量大到記憶體裝不下（Out of Memory），你會怎麼修改？｜Q: How would you modify this if the input data is too large to fit in memory?**
  - **A (System/Data focus)**: 我會採用外部排序 (External Sort) 或串流處理 (Stream Processing)。我們可以分批讀取資料，處理後寫入暫存檔，最後再合併結果。這與我在處理大型醫療影像數據時的邏輯類似。｜**A**: I would use External Sorting or Stream Processing. We can read data in chunks, process/sort them, write to temporary files, and then merge the results. This is similar to how I handle large medical imaging datasets.

- **Q: 這段程式碼在多執行緒環境下安全嗎？｜Q: Is this code thread-safe?**
  - **A (Java focus)**: 目前使用的 `ArrayList` (或 `HashMap`) 不是執行緒安全的。若需並發存取，我會改用 `ConcurrentHashMap` 或在關鍵區段加上 `synchronized` 鎖，但要注意效能影響。｜**A**: The current `ArrayList` (or `HashMap`) is not thread-safe. For concurrent access, I would switch to `ConcurrentHashMap` or apply `synchronized` blocks to critical sections, though I'd need to be mindful of performance impacts.

## 5. 技術深挖提示（針對 Google Cloud/Diagnostics） | Technical Deep‑Dive Prompts (Google Cloud/Diagnostics Focus)
*(由於 JD 強調 "Diagnostics", "System Programming", "Hardware interaction"，演算法題目可能會有相關包裝。｜Since the JD emphasizes "Diagnostics", "System Programming", and "Hardware interaction", coding problems might be flavored accordingly.)*

- **依賴關係解析 (Dependency Resolution)**
  - **題目類型**：給定一組服務或硬體元件及其依賴關係，決定啟動順序或偵測循環依賴。｜**Prompt**: Given a set of services or hardware components and their dependencies, determine the boot order or detect circular dependencies.
  - **核心演算法**：拓撲排序 (Topological Sort)、DFS/BFS (偵測環)。｜**Core Algo**: Topological Sort, DFS/BFS (Cycle detection).

- **日誌分析與字串處理 (Log Parsing & String Manipulation)**
  - **題目類型**：從海量伺服器日誌中找出錯誤模式，或實作一個簡單的 grep/parser。｜**Prompt**: Find error patterns in massive server logs, or implement a simple grep/parser.
  - **核心演算法**：滑動視窗 (Sliding Window)、字串搜尋 (KMP/Rabin-Karp)、正規表達式實作。｜**Core Algo**: Sliding Window, String Search (KMP/Rabin-Karp), Regex implementation logic.

- **網格與連通性 (Grid & Connectivity)**
  - **題目類型**：在資料中心機架（Grid）中，計算故障伺服器的群聚區域或最短修復路徑。｜**Prompt**: In a data center rack layout (Grid), calculate clusters of failed servers or the shortest path for repair.
  - **核心演算法**：BFS/DFS (島嶼問題變體)、Union-Find。｜**Core Algo**: BFS/DFS (Number of Islands variant), Union-Find.

## 6. 常見陷阱與糾正 | Pitfalls & Corrections

- **陷阱：急著寫程式碼｜Pitfall: Jumping into code too fast.**
  - **糾正**：請花前 5 分鐘釐清需求。問清楚輸入範圍、是否會有負數、是否會有重複值。｜**Correction**: Spend the first 5 minutes clarifying requirements. Ask about input range, negative numbers, or duplicates.
  - *話術/Script*: "Before I start coding, I'd like to clarify a few constraints. Can the input array be empty? Are the elements distinct?"

- **陷阱：變數命名過於隨意｜Pitfall: Using sloppy variable names.**
  - **糾正**：避免使用 `a`, `b`, `temp`。使用具業務意義的命名，如 `serverIndex`, `packetQueue`, `maxLatency`。這對於資深職位尤為重要。｜**Correction**: Avoid `a`, `b`, `temp`. Use meaningful names like `serverIndex`, `packetQueue`, `maxLatency`. This is crucial for senior roles.

- **陷阱：忽略測試案例｜Pitfall: Ignoring test cases.**
  - **糾正**：寫完程式碼後，不要等面試官開口，主動用一個簡單案例「人肉跑一遍 (Dry Run)」你的程式碼，檢查邏輯漏洞。｜**Correction**: After coding, don't wait for the interviewer. Proactively "dry run" your code with a simple case to catch logic bugs.

## 7. 收尾與反問 | Closing & Questions for Interviewer

- **Recap**:
  - **剛才我們討論了使用 [演算法名稱] 來解決這個問題，並優化了空間複雜度。考慮到 Google Cloud 的規模，如果要處理 PB 級數據，我會進一步考慮分散式處理的架構。**
  - **We discussed using [Algorithm Name] to solve this, optimizing for space complexity. Considering Google Cloud's scale, if dealing with PB-level data, I would further consider a distributed processing architecture.**

- **Questions**:
  - **在這個職位負責的 Diagnostics Tools 中，你們最常遇到的效能瓶頸是在 CPU 計算還是在 I/O 吞吐量？**
    **In the Diagnostics Tools this role covers, are the most common performance bottlenecks usually in CPU computation or I/O throughput?**
  - **團隊對於程式碼品質與發布速度之間的權衡標準是什麼？特別是在處理硬體相關軟體時。**
    **How does the team balance code quality vs. release velocity, especially when dealing with hardware-interacting software?**