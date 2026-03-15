# 1. 前言與學習目標 (Introduction and Learning Objectives)

對於資深工程師而言，建置效能（Build Performance）不僅僅是節省幾秒鐘的問題，它直接影響開發者的生產力（Developer Velocity）、CI/CD 的基礎設施成本，以及產品交付的迭代週期。本章將超越基礎的指令操作，深入探討 Maven 與 Gradle 的內部執行模型。

For senior engineers, Build Performance is not just about saving a few seconds; it directly impacts Developer Velocity, CI/CD infrastructure costs, and the iteration cycle of product delivery. This chapter moves beyond basic commands to explore the internal execution models of Maven and Gradle.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精準診斷瓶頸 (Diagnose Bottlenecks):** 使用 Gradle Build Scan 或 Maven Profiler 等工具，量化並定位建置過程中的效能殺手。
    **Diagnose Bottlenecks:** Use tools like Gradle Build Scan or Maven Profiler to quantify and pinpoint performance killers in the build process.
2.  **實作進階快取策略 (Implement Advanced Caching):** 正確配置 Local 與 Remote Build Cache，理解 Cache Miss 的根本原因並解決之（特別是針對非確定性任務）。
    **Implement Advanced Caching:** Correctly configure Local and Remote Build Cache, understand the root causes of Cache Misses, and resolve them (especially for non-deterministic tasks).
3.  **優化執行模型 (Optimize Execution Model):** 熟練運用 Parallel Execution（平行執行）與 Daemon 機制，並理解其對記憶體與 CPU 的資源競爭影響。
    **Optimize Execution Model:** Skillfully apply Parallel Execution and Daemon mechanisms, understanding their impact on memory and CPU resource contention.
4.  **區分工具特性 (Distinguish Tool Capabilities):** 清楚解釋 Maven 與 Gradle 在 Incremental Build（增量建置）上的架構差異，以及如何在 Maven 中引入類似 Gradle 的效能特性（如 `mvnd`）。
    **Distinguish Tool Capabilities:** Clearly explain the architectural differences between Maven and Gradle regarding Incremental Builds, and how to introduce Gradle-like performance features into Maven (e.g., via `mvnd`).

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

要優化建置，必須先理解建置工具如何看待「工作」。
To optimize a build, one must first understand how the build tool views "work".

### 2.1 增量建置與輸入/輸出追蹤 (Incremental Builds & I/O Tracking)

**直覺類比 (Analogy):**
想像你在編寫一個複雜的數學函式。如果輸入參數（x, y）與上次計算時完全相同，你不需要重新計算，直接查表回傳上次的結果即可（Memoization）。建置工具也是如此，只是它的「輸入」是原始碼與依賴，「輸出」是 Compiled Classes 或 JARs。

**Analogy:**
Imagine you are writing a complex mathematical function. If the input parameters (x, y) are exactly the same as the last calculation, you don't need to recalculate; you just look up and return the previous result (Memoization). Build tools work similarly, but their "inputs" are source code and dependencies, and "outputs" are Compiled Classes or JARs.

**正規定義 (Formal Definition):**
- **Incremental Build:** 只有在 Task 的 Inputs（如 `.java` 檔案、依賴版本）或 Outputs（如 `build/` 目錄）發生變化時，才執行該 Task。否則標記為 `UP-TO-DATE`。
- **Fingerprinting (Hashing):** Gradle/Maven 會對所有 Inputs 進行雜湊運算（Hash）。這是判斷變更的依據。

**Incremental Build:** A task is executed only if its Inputs (e.g., `.java` files, dependency versions) or Outputs (e.g., `build/` directory) have changed. Otherwise, it is marked as `UP-TO-DATE`.
**Fingerprinting (Hashing):** Gradle/Maven computes hashes for all Inputs. This is the basis for determining changes.

### 2.2 建置快取 (Build Cache: Local vs. Remote)

**概念差異 (Conceptual Difference):**
- **Incremental Build** 僅限於「同一個 Workspace、上一次的建置」。如果你執行 `clean`，增量優化就失效了。
- **Build Cache** 則更進一步。它將 Task 的結果儲存起來（Key 是 Inputs 的 Hash）。即使你 `clean` 了專案，或者在另一台機器上（Remote Cache），只要 Inputs Hash 相同，就能直接下載結果，跳過編譯。

**Conceptual Difference:**
- **Incremental Build** is limited to the "same workspace, previous build". If you run `clean`, the incremental optimization is lost.
- **Build Cache** goes further. It stores the results of tasks (Keyed by the Hash of Inputs). Even if you `clean` the project, or are on a different machine (Remote Cache), as long as the Inputs Hash matches, the result can be downloaded directly, skipping compilation.

### 2.3 守護行程 (The Daemon)

**心智模型 (Mental Model):**
JVM 需要「熱身」。JIT (Just-In-Time) Compiler 需要時間來優化 bytecode。
Gradle Daemon 或 Maven Daemon (`mvnd`) 是一個長駐背景的 Process。它不僅避免了每次啟動 JVM 的開銷，更重要的是它保持了 JIT 的優化狀態（Warm JVM）。

**Mental Model:**
The JVM needs "warming up". The JIT (Just-In-Time) Compiler takes time to optimize bytecode.
The Gradle Daemon or Maven Daemon (`mvnd`) is a long-lived background process. It not only avoids the overhead of JVM startup each time but, more importantly, maintains the JIT optimized state (Warm JVM).

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型分散式團隊或微服務架構中，建置優化是 DevOps 策略的關鍵一環。
In large distributed teams or microservices architectures, build optimization is a critical component of DevOps strategy.

### 3.1 CI/CD Pipeline 架構 (CI/CD Pipeline Architecture)

在 Production 級別的 CI 系統中，我們通常會部署 **Remote Build Cache Node**。

In a production-grade CI system, we typically deploy a **Remote Build Cache Node**.

*   **Developer (Local):** 讀取 Remote Cache，寫入 Local Cache。開發者 A 編譯過的底層 Library，開發者 B 可以直接拉取 cache，無需重新編譯。
    **Developer (Local):** Reads from Remote Cache, writes to Local Cache. A low-level library compiled by Developer A can be pulled from cache by Developer B without recompilation.
*   **CI Server (Jenkins/GitLab/GitHub Actions):**
    *   **Pull Request Builds:** 讀取 Remote Cache（加速驗證），通常設定為不寫入（避免污染）。
    *   **Master/Main Branch Builds:** 讀取並**寫入** Remote Cache（作為黃金標準）。
    *   **Ephemeral Agents:** 由於 CI Agent 通常是短暫存在的（容器化），Local Cache 效益低，Remote Cache 是加速關鍵。

*   **CI Server (Jenkins/GitLab/GitHub Actions):**
    *   **Pull Request Builds:** Read from Remote Cache (accelerate validation), usually configured not to write (avoid pollution).
    *   **Master/Main Branch Builds:** Read and **write** to Remote Cache (as the gold standard).
    *   **Ephemeral Agents:** Since CI agents are often ephemeral (containerized), Local Cache has low utility; Remote Cache is the key to acceleration.

### 3.2 Maven vs. Gradle 在實務上的選擇 (Practical Choice: Maven vs. Gradle)

*   **Gradle:** 原生支援 Build Cache 與 Daemon，且對 Incremental Build 的粒度控制極佳。在大型 Monorepo 中，Gradle 通常能提供比 Maven 快 2-10 倍的效能。
    **Gradle:** Natively supports Build Cache and Daemon, with excellent granularity control for Incremental Builds. In large Monorepos, Gradle often provides 2-10x better performance than Maven.
*   **Maven:** 傳統上較慢。但現代 Maven 專案應引入 **Maven Build Cache Extension** 與 **mvnd (Maven Daemon)** 來縮小差距。
    **Maven:** Traditionally slower. However, modern Maven projects should introduce the **Maven Build Cache Extension** and **mvnd (Maven Daemon)** to close the gap.

---

# 4. 逐步示例 (Walkthrough / Example)

假設我們有一個包含 50 個子模組（Submodules）的 Java Monorepo，目前的 CI 建置時間為 20 分鐘。目標是將其縮短至 5 分鐘以內。

Assume we have a Java Monorepo with 50 submodules. The current CI build time is 20 minutes. The goal is to reduce it to under 5 minutes.

### Step 1: 建立基準線與分析 (Baseline & Profiling)

首先，我們不能憑感覺優化。

First, we cannot optimize based on intuition.

**Gradle:**
```bash
./gradlew build --scan
```
這會產生一個網頁報告，顯示每個 Task 的執行時間、Cache Miss 的原因以及依賴下載時間。

This generates a web report showing execution time per Task, reasons for Cache Misses, and dependency download times.

**Maven:**
```bash
# 使用 Maven Profiler 或簡單的時間戳記
mvn clean install -Dmaven.profiler.enabled=true
# 或者使用 mvnd
mvnd clean install
```

### Step 2: 啟用平行執行 (Enable Parallel Execution)

大多數 CI Server 都有多核心 CPU，但預設建置可能是單執行緒的。

Most CI servers have multi-core CPUs, but the default build might be single-threaded.

**Gradle (`gradle.properties`):**
```properties
# 啟用平行執行
org.gradle.parallel=true
# 根據 CPU 核心數自動配置 Worker 數量
org.gradle.workers.max=4 
```

**Maven (`.mvn/maven.config` or Command Line):**
```bash
# -T 1C 代表每個 CPU 核心分配一個 Thread
mvn clean install -T 1C
```
*注意：平行執行可能會導致並發問題（Race Conditions）或記憶體不足（OOM），需監控 Heap Size。*
*Note: Parallel execution can lead to Race Conditions or Out Of Memory (OOM) errors; monitor Heap Size.*

### Step 3: 配置遠端快取 (Configure Remote Cache) - Gradle 範例

這是效能提升最大的步驟。假設我們使用一個 HTTP 後端作為 Cache Node (例如 Gradle Enterprise 或自架 Nginx/Artifactory)。

This is the step with the biggest performance gain. Assume we use an HTTP backend as a Cache Node (e.g., Gradle Enterprise or self-hosted Nginx/Artifactory).

**`settings.gradle`:**

```groovy
buildCache {
    local {
        enabled = true
    }
    remote(HttpBuildCache) {
        url = 'https://build-cache.mycompany.com/cache/'
        push = isCiServer() // 只有 CI Server (Main Branch) 允許寫入
        credentials {
            username = System.getenv('CACHE_USER')
            password = System.getenv('CACHE_PASSWORD')
        }
    }
}

boolean isCiServer() {
    return System.getenv('CI') != null
}
```

### Step 4: 解決 Cache Miss (Debugging Cache Misses)

如果配置了 Cache 但命中率（Hit Rate）很低，通常是因為「非確定性輸入（Non-deterministic Inputs）」。

If Cache is configured but the Hit Rate is low, it is usually due to "Non-deterministic Inputs".

**常見兇手 (Common Culprit):** 在 Build 過程中動態生成包含「當前時間戳」的檔案。
**Common Culprit:** Dynamically generating files containing the "current timestamp" during the build.

```java
// Anti-pattern in build.gradle
task generateVersionInfo {
    doLast {
        // 每次執行都會產生不同的檔案內容，導致後續 Task 的 Input Hash 改變，Cache 失效
        // Every run produces different file content, changing Input Hash for subsequent tasks, invalidating Cache
        new File(buildDir, "version.txt").text = "Build Time: " + new Date()
    }
}
```

**修正 (Fix):** 移除時間戳，或將時間戳視為不影響快取的屬性（如果工具支援），或者僅在 Release 階段加入時間戳。
**Fix:** Remove the timestamp, treat the timestamp as a property that doesn't affect caching (if supported), or only add timestamps during the Release phase.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 絕對路徑污染 (Absolute Path Pollution)
**錯誤描述:** 編譯產物或配置中包含了機器的絕對路徑（例如 `/Users/alice/project/...` vs `/home/jenkins/agent/project/...`）。
**為何不好:** 這會導致 Inputs Hash 在不同機器上不一致，使 Remote Cache 完全失效（Relocatability issue）。
**最佳實踐:** 確保所有路徑都是相對路徑。Gradle 預設會處理這點，但在自定義 Task 或 Maven 配置中需特別小心。

**Description:** Build artifacts or configurations contain absolute paths of the machine.
**Why it's bad:** This causes Input Hashes to differ across machines, rendering Remote Cache completely ineffective (Relocatability issue).
**Best Practice:** Ensure all paths are relative. Gradle handles this by default, but extra care is needed in custom Tasks or Maven configurations.

### 5.2 過度平行化導致的 OOM (OOM caused by Over-Parallelization)
**錯誤描述:** 在 8 核心機器上設定 `-T 8` 或 `workers.max=8`，但每個 Worker 需要 2GB RAM，而機器只有 8GB RAM。
**為何不好:** 導致頻繁 GC 或 Crash，反而比單執行緒更慢。
**最佳實踐:** 平衡 CPU 核心數與可用記憶體。通常保留 1-2 個核心給系統，並限制 Heap Size (`-Xmx`)。

**Description:** Setting `-T 8` or `workers.max=8` on an 8-core machine, but each Worker needs 2GB RAM while the machine only has 8GB.
**Why it's bad:** Causes frequent GC or crashes, making it slower than single-threaded builds.
**Best Practice:** Balance CPU cores with available memory. Usually reserve 1-2 cores for the system and limit Heap Size (`-Xmx`).

### 5.3 忽略 `clean` 的代價 (Ignoring the cost of `clean`)
**錯誤描述:** 在 CI script 中習慣性地執行 `mvn clean install` 或 `./gradlew clean build`。
**為何不好:** `clean` 會刪除所有增量建置的成果。如果有良好的 Build Cache 機制，`clean` 是可以接受的；但若沒有 Cache，這是在浪費資源。
**最佳實踐:** 信任構建工具的增量機制。在 CI 上，如果使用 Ephemeral Agents，`clean` 是隱含的（因為環境是新的）；但在本地開發，應避免頻繁 `clean`。

**Description:** Habitually running `mvn clean install` or `./gradlew clean build` in CI scripts.
**Why it's bad:** `clean` deletes all incremental build results. If a good Build Cache mechanism exists, `clean` is acceptable; otherwise, it's a waste of resources.
**Best Practice:** Trust the build tool's incremental mechanism. On CI, if using Ephemeral Agents, `clean` is implicit (fresh environment); but in local development, avoid frequent `clean`.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 你如何診斷並優化一個執行緩慢的 CI Pipeline？
**How do you diagnose and optimize a slow CI Pipeline?**

**高分回答要點 (Key Points for a High Score):**
1.  **Measure First:** 提到使用 Profiling 工具（Gradle Build Scan / Maven Profiler）建立基準線，而不是猜測。
2.  **Identify Bottlenecks:** 區分是「依賴下載慢」（Network/Proxy issue）、「測試執行慢」（Flaky tests/Integration tests）還是「編譯慢」（CPU bound）。
3.  **Apply Layers:** 依序提出解決方案：
    -   硬體層：增加 CPU/RAM。
    -   配置層：開啟 Parallel Execution、Daemon。
    -   架構層：實作 Remote Build Cache。
    -   代碼層：模組化（Modularization）以增加平行度與 Cache 命中率。

### Q2: 請解釋 Gradle/Maven 的 Build Cache 原理，以及什麼情況下會導致 Cache Miss？
**Explain the principles of Gradle/Maven Build Cache, and what causes a Cache Miss?**

**高分回答要點 (Key Points for a High Score):**
1.  **Input Fingerprinting:** 解釋 Hash 機制（Inputs -> Hash Key -> Output Value）。
2.  **Relocatability:** 強調路徑無關性（Path independence）的重要性。
3.  **Volatile Inputs:** 舉例說明時間戳、隨機數、絕對路徑、環境變數如何破壞 Cache Key 的一致性。
4.  **Debugging:** 提到如何比較兩個 Build 的 Fingerprint 來找出差異（例如 Gradle 的 `Compare Builds` 功能）。

### Q3: 在微服務架構下，共用 Library 的版本管理與建置效能如何權衡？
**In a microservices architecture, how do you trade off version management of shared libraries against build performance?**

**高分回答要點 (Key Points for a High Score):**
1.  **SNAPSHOT vs. Release:** 頻繁使用 SNAPSHOT 會導致 Gradle/Maven 強制檢查更新（ `--refresh-dependencies`），拖慢建置並破壞 Cache 穩定性。
2.  **Bill of Materials (BOM):** 使用 BOM 統一管理版本，減少 Dependency Resolution 的複雜度。
3.  **Monorepo vs. Polyrepo:** 討論 Monorepo 配合 Build Cache 可以讓修改 Shared Lib 後的影響範圍測試更快，但需要更強的工具支援（如 Gradle/Bazel）。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)
1.  **Incremental Build** 靠的是檢查 Input/Output 的變化；**Build Cache** 靠的是 Input Hash 的全域查找。
2.  **Remote Cache** 是 CI/CD 效能優化的聖杯，能讓乾淨的環境也能享受之前的編譯成果。
3.  **Parallel Execution** 需配合記憶體管理，避免 OOM。
4.  **Daemon** 必須保持開啟（在 CI 環境中需特別配置）以利用 JIT 優化。
5.  **Non-deterministic Tasks**（如寫入時間戳）是 Cache 的最大敵人。

### 後續延伸 (Next Steps)
-   **進階依賴管理 (Advanced Dependency Management):** 學習如何處理 Dependency Hell、Resolution Strategy 以及 BOM 的設計（對應 Chapter 05）。
-   **Custom Plugins:** 當標準配置無法滿足需求時，如何撰寫高效能的 Custom Plugin，並確保其對 Cache 友善。
-   **Bazel:** 如果 Maven/Gradle 達到極限，探索 Google 的 Bazel 建置系統如何處理超大規模的 Monorepo 建置。