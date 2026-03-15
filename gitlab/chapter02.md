# 1. 前言與學習目標 (Introduction & Learning Objectives)

在初階的 GitLab CI/CD 中，我們通常依賴線性的 `stages`（如 build -> test -> deploy）來管理流程。然而，隨著專案規模擴大（例如 Monorepo 架構）或微服務數量的增加，單純的線性流程會導致嚴重的效能瓶頸與維護困難。本章旨在打破「線性執行」的限制，引入更靈活的圖論概念與動態生成技術。

In entry-level GitLab CI/CD, we typically rely on linear `stages` (e.g., build -> test -> deploy) to manage workflows. However, as projects scale (e.g., Monorepo architectures) or the number of microservices increases, simple linear flows lead to severe performance bottlenecks and maintenance challenges. This chapter aims to break the "linear execution" constraint, introducing flexible graph theory concepts and dynamic generation techniques.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **實作 DAG (Directed Acyclic Graph) 流水線**：利用 `needs` 關鍵字打破 stage 的順序依賴，顯著縮短 pipeline 執行時間。
    **Implement DAG (Directed Acyclic Graph) Pipelines**: Use the `needs` keyword to break stage ordering dependencies, significantly reducing pipeline execution time.
2.  **設計 Dynamic Child Pipelines**：針對 Monorepo 或複雜專案，動態生成並觸發子流水線，實現「只測試/部署有變更的服務」。
    **Design Dynamic Child Pipelines**: Dynamically generate and trigger child pipelines for Monorepos or complex projects, achieving "test/deploy only changed services."
3.  **精通 `rules` 邏輯**：取代舊式的 `only/except`，使用進階邏輯控制 job 的執行條件（如變更檢測、變數判斷）。
    **Master `rules` Logic**: Replace legacy `only/except` with advanced logic to control job execution conditions (e.g., change detection, variable evaluation).
4.  **優化流水線架構**：從系統設計角度，將 CI/CD 視為可擴展的自動化系統，而非單純的腳本堆疊。
    **Optimize Pipeline Architecture**: From a system design perspective, treat CI/CD as a scalable automation system rather than a mere stack of scripts.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 從「接力賽」到「甘特圖」 (From Relay Race to Gantt Chart)

**線性模型 (Linear Model - `stages`)**：
傳統 GitLab CI 就像大隊接力。`test` stage 必須等 `build` stage 的**所有** jobs 跑完才能開始。即使 Frontend 的測試不依賴 Backend 的建置，它還是得等。這造成了不必要的等待時間（Idle time）。

**Linear Model (`stages`)**:
Traditional GitLab CI is like a relay race. The `test` stage must wait for **all** jobs in the `build` stage to finish before starting. Even if Frontend tests don't depend on the Backend build, they still have to wait. This creates unnecessary idle time.

**DAG 模型 (DAG Model - `needs`)**：
DAG 就像建築工地的甘特圖（Gantt Chart）。只要「依賴的前置任務」完成了，下一個任務就可以馬上開始，無視 stage 的邊界。這將流水線的總執行時間從「各 stage 最慢 job 之和」壓縮為「最長關鍵路徑（Critical Path）的時間」。

**DAG Model (`needs`)**:
DAG is like a construction site Gantt Chart. As soon as the "dependent prerequisite tasks" are complete, the next task can start immediately, ignoring stage boundaries. This compresses the total pipeline execution time from "the sum of the slowest jobs in each stage" to "the time of the longest Critical Path."

### 2.2 父子流水線與動態生成 (Parent-Child & Dynamic Pipelines)

**靜態子流水線 (Static Child Pipelines)**：
將巨大的 `.gitlab-ci.yml` 拆解成多個小的 YAML 檔，由主流水線透過 `trigger` 呼叫。這類似於將 Monolithic Code 拆解為模組，主要解決**可讀性**與**維護性**問題。

**Static Child Pipelines**:
Breaking a massive `.gitlab-ci.yml` into smaller YAML files, called by the main pipeline via `trigger`. This is akin to refactoring Monolithic Code into modules, primarily solving **readability** and **maintainability** issues.

**動態子流水線 (Dynamic Child Pipelines)**：
這是更進階的技巧。CI 不再讀取預先寫好的 YAML，而是先執行一個腳本（Generator），根據當前的 Git commit 內容（例如：改了哪些資料夾？），**即時生成**一份 YAML 設定檔，然後觸發它。這賦予了 CI/CD 極高的靈活性。

**Dynamic Child Pipelines**:
This is a more advanced technique. Instead of reading a pre-written YAML, the CI first runs a script (Generator) that **generates** a YAML configuration on the fly based on the current Git commit (e.g., which folders changed?), and then triggers it. This grants the CI/CD extreme flexibility.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在 Big Tech 的實務環境中，我們通常面對的是 Monorepo 或是高度相依的微服務架構。

In Big Tech real-world environments, we typically deal with Monorepos or highly interdependent microservices architectures.

### 3.1 Monorepo 的 CI/CD 挑戰 (The Monorepo CI/CD Challenge)

假設你維護一個儲存庫，內含 `frontend` (React), `backend-api` (Go), 和 `data-pipeline` (Python)。
Imagine you maintain a repository containing `frontend` (React), `backend-api` (Go), and `data-pipeline` (Python).

-   **Naive Approach**: 每次 commit 都執行所有服務的 build 和 test。
    *   *後果*：資源浪費巨大，開發者等待時間過長（Feedback Loop 慢）。
-   **System Design Approach**: 實作 Change Detection (變更偵測)。
    *   *架構*：
        1.  **Orchestrator Job**: 比較 `HEAD` 與 `main` 分支的差異。
        2.  **Decision Logic**: 如果只有 `frontend/` 變更，則只生成前端的 CI YAML。
        3.  **Execution**: 觸發生成的 Child Pipeline。

-   **Naive Approach**: Run build and test for all services on every commit.
    *   *Consequence*: Massive resource waste, excessive developer wait time (slow Feedback Loop).
-   **System Design Approach**: Implement Change Detection.
    *   *Architecture*:
        1.  **Orchestrator Job**: Compare differences between `HEAD` and `main` branch.
        2.  **Decision Logic**: If only `frontend/` changed, generate CI YAML only for the frontend.
        3.  **Execution**: Trigger the generated Child Pipeline.

### 3.2 可觀測性與除錯 (Observability & Debugging)

使用 DAG 和 Child Pipelines 會增加邏輯複雜度。GitLab 提供了 "Pipeline Graph" 和 "Dependent Jobs" 視圖。在設計時，必須確保依賴關係清晰，避免產生「義大利麵式依賴（Spaghetti Dependencies）」，否則當 pipeline 失敗時，很難追溯根因。

Using DAG and Child Pipelines increases logic complexity. GitLab provides "Pipeline Graph" and "Dependent Jobs" views. When designing, you must ensure dependencies are clear to avoid "Spaghetti Dependencies," otherwise tracing the root cause when a pipeline fails becomes difficult.

---

# 4. 逐步示例 (Walkthrough / Example)

### 案例背景 (Scenario)
我們有一個專案，包含一個核心服務 `core-svc` 和一個文件目錄 `docs`。
目標：
1. 修改 `docs` 時，只跑 Markdown lint，不跑程式碼編譯。
2. 修改 `core-svc` 時，跑編譯與測試。
3. 編譯與測試需使用 DAG 加速（測試不需等 Lint 完成）。

### Scenario
We have a project containing a core service `core-svc` and a documentation directory `docs`.
Goals:
1. When `docs` is modified, run only Markdown lint, not code compilation.
2. When `core-svc` is modified, run compilation and tests.
3. Compilation and tests should use DAG for speed (tests don't need to wait for Lint).

### 步驟 1: 定義 Dynamic Config Generator (Step 1: Define Dynamic Config Generator)

首先，我們需要一個腳本來生成 CI 設定檔。這裡用簡單的 Shell script 模擬，實務上可用 Python/JS。

First, we need a script to generate the CI config. Here we use a simple Shell script for simulation; in practice, Python/JS is often used.

```bash
# generate-ci-config.sh
echo "Generating CI config..."

# 初始化 YAML
# Initialize YAML
cat <<EOF > generated-config.yml
stages:
  - build
  - test
EOF

# 檢查 core-svc 是否有變更
# Check if core-svc has changes
if git diff --name-only HEAD~1 | grep "^core-svc/"; then
  cat <<EOF >> generated-config.yml

build_core:
  stage: build
  script: echo "Building Core Service..."

test_core:
  stage: test
  needs: ["build_core"]  # DAG: 只依賴 build_core，不依賴 stage
  script: echo "Testing Core Service..."
EOF
fi

# 檢查 docs 是否有變更
# Check if docs has changes
if git diff --name-only HEAD~1 | grep "^docs/"; then
  cat <<EOF >> generated-config.yml

lint_docs:
  stage: build
  script: echo "Linting Docs..."
EOF
fi
```

### 步驟 2: 設定主流水線 (Step 2: Configure Main Pipeline)

在 `.gitlab-ci.yml` 中，我們設定一個 job 來執行上述腳本，並將生成的檔案宣告為 artifact，隨後觸發它。

In `.gitlab-ci.yml`, we configure a job to run the script above, declare the generated file as an artifact, and then trigger it.

```yaml
# .gitlab-ci.yml
stages:
  - setup
  - triggers

generate-config:
  stage: setup
  image: alpine:latest
  before_script:
    - apk add git
  script:
    - chmod +x generate-ci-config.sh
    - ./generate-ci-config.sh
  artifacts:
    paths:
      - generated-config.yml

trigger-dynamic-pipeline:
  stage: triggers
  needs: ["generate-config"]
  trigger:
    include:
      - artifact: generated-config.yml
        job: generate-config
    strategy: depend # 等待子流水線完成並回傳狀態 (Wait for child pipeline to finish and return status)
```

### 為什麼這樣做比較好？ (Why is this better?)

1.  **精準執行 (Precision)**：修改文件不會觸發耗時的編譯。
    **Precision**: Modifying documentation doesn't trigger time-consuming compilation.
2.  **DAG 加速 (DAG Speed)**：在生成的 `generated-config.yml` 中，`test_core` 使用 `needs: ["build_core"]`。這意味著即便我們有其他並行的 build jobs，`test_core` 也只會等待它需要的那個 job，而不是等待整個 `build` stage 結束。
    **DAG Speed**: In the `generated-config.yml`, `test_core` uses `needs: ["build_core"]`. This means even if we have other parallel build jobs, `test_core` only waits for the specific job it needs, not the end of the entire `build` stage.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 濫用 `needs` 導致的「義大利麵 DAG」 (Spaghetti DAGs from Overusing `needs`)

**錯誤 (Mistake)**：
為了極致效能，給每個 job 都加上複雜的 `needs` 依賴，導致依賴線圖錯綜複雜。
For extreme performance, adding complex `needs` dependencies to every job, resulting in a tangled dependency graph.

**後果 (Consequence)**：
維護者無法理解 job 的執行順序。如果中間某個 job 失敗，重試機制可能變得不可預測。
Maintainers cannot understand the execution order of jobs. If an intermediate job fails, retry mechanisms might become unpredictable.

**建議 (Advice)**：
保持 DAG 簡單。通常只在跨 Stage 且有明確 Artifact 依賴時使用 `needs`。同 Stage 的 jobs 應保持獨立。
Keep the DAG simple. Usually, only use `needs` when crossing Stages with explicit Artifact dependencies. Jobs within the same Stage should remain independent.

### 5.2 忽略 `workflow:rules` 導致的重複流水線 (Duplicate Pipelines from Ignoring `workflow:rules`)

**錯誤 (Mistake)**：
沒有設定全域的 `workflow:rules`。
Not configuring global `workflow:rules`.

**後果 (Consequence)**：
當你推播一個 commit 到分支，並同時開啟了 Merge Request 時，GitLab 會觸發兩條流水線（Branch pipeline 和 MR pipeline）。這浪費了一倍的資源。
When you push a commit to a branch and also have an open Merge Request, GitLab triggers two pipelines (Branch pipeline and MR pipeline). This wastes double the resources.

**修正 (Fix)**：

```yaml
workflow:
  rules:
    - if: $CI_MERGE_REQUEST_ID
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    # 避免 Branch pipeline 在有 MR 時重複執行
    # Avoid Branch pipeline running duplicate when MR exists
    - if: $CI_OPEN_MERGE_REQUESTS
      when: never
    - if: $CI_COMMIT_BRANCH
```

### 5.3 子流水線 Artifact 傳遞失敗 (Failed Artifact Passing in Child Pipelines)

**錯誤 (Mistake)**：
期望 Parent Pipeline 的 artifacts 自動出現在 Child Pipeline 中，或者反之。
Expecting Parent Pipeline artifacts to automatically appear in the Child Pipeline, or vice versa.

**觀念 (Concept)**：
Parent 和 Child 是隔離的環境。必須明確定義 artifact 的傳遞。
Parent and Child are isolated environments. You must explicitly define artifact passing.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 如何優化一個執行時間超過 40 分鐘的 CI Pipeline？
**How would you optimize a CI Pipeline that takes over 40 minutes to run?**

*   **高分回答要點 (Key Points)**：
    1.  **分析 (Analysis)**：先看 Critical Path，找出瓶頸（是 Build 慢還是 Test 慢？）。
    2.  **DAG**：使用 `needs` 打破 Stage 邊界，讓無依賴的測試提早開始。
    3.  **Caching**：確保 `node_modules` 或編譯緩存有效利用（分散式緩存）。
    4.  **Parallelization**：使用 `parallel: matrix` 切分測試集（Test Sharding）。
    5.  **Selective Execution**：導入 Dynamic Child Pipelines，只跑有變更的部分。

### Q2: `rules` 和 `only/except` 有什麼不同？為什麼現在推薦用 `rules`？
**What is the difference between `rules` and `only/except`? Why is `rules` recommended now?**

*   **高分回答要點 (Key Points)**：
    1.  **邏輯能力**：`rules` 支援複雜的 `if` 邏輯運算（AND/OR/Regex），`only/except` 只是簡單的列表匹配。
    2.  **優先級**：`rules` 是按順序評估（First match wins），這讓邏輯控制更精確。
    3.  **整合性**：`rules` 可以同時控制 job 是否加入 pipeline (`when`) 以及變數設定 (`variables`)，功能更強大。
    4.  `only/except` 已被 GitLab 視為不建議使用（Deprecated/Legacy in spirit）。

### Q3: 在微服務架構下，如何設計 CI 以確保服務間的兼容性？
**In a microservices architecture, how do you design CI to ensure compatibility between services?**

*   **高分回答要點 (Key Points)**：
    1.  **Downstream Triggers**：當 Shared Library 更新時，觸發所有依賴它的服務的 CI（Multi-project pipelines）。
    2.  **Contract Testing**：在 CI 中加入 Consumer-Driven Contract (CDC) 測試（如 Pact）。
    3.  **Integration Environment**：使用 Dynamic Environments 部署臨時環境進行整合測試。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)
1.  **DAG (`needs`)** 是縮短 Critical Path 的利器，打破了 Stage 的同步等待。
2.  **Dynamic Child Pipelines** 讓 CI 設定檔可以由程式碼生成，是處理 Monorepo 的最佳實踐。
3.  **`rules`** 提供了比 `only/except` 更強大的邏輯控制，應作為預設選擇。
4.  **Change Detection** 是節省雲端成本與開發時間的關鍵策略。
5.  **`workflow:rules`** 必須設定，以避免 Branch/MR 雙重觸發造成的資源浪費。

### 後續延伸 (Next Steps)
*   **Next Chapter**: **GitLab Runner 進階配置與自動擴展 (Advanced Runner Configuration & Autoscaling)**。
    *   學習如何配置 Kubernetes Executor。
    *   實作 Spot Instances 以降低 CI 成本。
*   **Action Item**: 檢視你目前的專案，找出一個執行最慢的 Pipeline，嘗試用 `needs` 重構它，並測量優化前後的時間差異。