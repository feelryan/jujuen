# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，撰寫 `Jenkinsfile` 不僅僅是將 Shell script 搬進 Groovy 檔案中，而是關於如何設計可維護、可擴展且高效的自動化流程。本章將超越基礎語法，深入探討 Pipeline as Code 的進階模式。
For senior engineers, writing a `Jenkinsfile` is not just about moving shell scripts into a Groovy file; it is about designing maintainable, scalable, and efficient automation workflows. This chapter moves beyond basic syntax to explore advanced patterns in Pipeline as Code.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精準選擇 Pipeline 類型**：深刻理解 Declarative 與 Scripted Pipeline 的底層差異，並在適當場景做出正確的架構決策。
    **Select the Right Pipeline Type:** Deeply understand the underlying differences between Declarative and Scripted Pipelines and make the right architectural decisions for specific scenarios.
2.  **優化執行效率**：運用 Parallel execution 與 Matrix builds 大幅縮短 Build cycle time，提升開發團隊的 Feedback loop 速度。
    **Optimize Execution Efficiency:** Utilize Parallel execution and Matrix builds to significantly reduce build cycle time, accelerating the feedback loop for development teams.
3.  **處理複雜控制流**：在 Declarative 結構中優雅地嵌入命令式邏輯（Imperative logic），並妥善處理錯誤與重試機制。
    **Handle Complex Control Flows:** Elegantly embed imperative logic within Declarative structures and properly handle errors and retry mechanisms.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## Declarative vs. Scripted: 結構 vs. 彈性 (Structure vs. Flexibility)

**心智模型 (Mental Model)**：
將 **Declarative Pipeline** 想像成填寫一份「嚴格的申請表格」（如 YAML/JSON），你告訴 Jenkins *你想要什麼狀態*（What），Jenkins 負責驗證格式並執行。將 **Scripted Pipeline** 想像成在寫一段「Groovy 程式碼」（How），你擁有完整的控制權，可以寫迴圈、定義變數、甚至修改底層物件，但也更容易寫出難以維護的 Spaghetti code。
**Mental Model:**
Think of **Declarative Pipeline** as filling out a "strict application form" (like YAML/JSON). You tell Jenkins *what state you want*, and Jenkins validates the schema and executes it. Think of **Scripted Pipeline** as writing "raw Groovy code" (How). You have full control—loops, variable definitions, even modifying underlying objects—but it's also easier to write unmaintainable spaghetti code.

**關鍵差異 (Key Differences)**：

*   **Declarative**: 語法更嚴格，提供更好的語法檢查與視覺化（Blue Ocean 支援度佳）。它允許透過 `script` 區塊這個「逃生門」來執行任意 Groovy 程式碼。
    **Declarative**: Stricter syntax, providing better linting and visualization (great Blue Ocean support). It allows an "escape hatch" via the `script` block to execute arbitrary Groovy code.
*   **Scripted**: 基於 Groovy CPS (Continuation Passing Style) 執行。適合極度複雜、需要動態生成 Stage 或高度客製化邏輯的場景。
    **Scripted**: Based on Groovy CPS (Continuation Passing Style). Suitable for extremely complex scenarios requiring dynamic stage generation or highly customized logic.

## Matrix Builds & Parallelism (矩陣建置與平行化)

**類比 (Analogy)**：
*   **Parallel**: 就像多執行緒（Multi-threading）。你有多個獨立的任務（如前端 Build、後端 Build、靜態掃描），可以同時進行以節省時間。
    **Parallel**: Like multi-threading. You have multiple independent tasks (e.g., Frontend Build, Backend Build, Static Analysis) that can run simultaneously to save time.
*   **Matrix**: 就像笛卡兒積（Cartesian Product）。你需要驗證 `(OS: Linux, Windows) x (Node: 14, 16, 18)` 的所有組合。手寫 6 個 Stage 是愚蠢的，Matrix 讓 Jenkins 自動生成這些組合。
    **Matrix**: Like a Cartesian Product. You need to verify all combinations of `(OS: Linux, Windows) x (Node: 14, 16, 18)`. Writing 6 stages manually is foolish; Matrix allows Jenkins to generate these combinations automatically.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型分散式系統或 Microservices 架構中，Jenkins Pipeline 的設計直接影響 **DORA Metrics** 中的「變更前置時間」（Lead Time for Changes）。
In large-scale distributed systems or Microservices architectures, the design of the Jenkins Pipeline directly impacts the "Lead Time for Changes" in **DORA Metrics**.

## 典型應用場景 (Typical Scenarios)

1.  **Monorepo 的條件式建置 (Conditional Builds in Monorepo)**：
    在一個巨大的 Monorepo 中，如果只修改了 Service A 的程式碼，Pipeline 應該聰明到只跑 Service A 的測試與部署，而不是重跑整個世界。這需要結合 `when` 指令與 `changeset` 檢查。
    **Conditional Builds in Monorepo:**
    In a massive Monorepo, if only Service A's code is modified, the Pipeline should be smart enough to run tests and deployment only for Service A, not rebuild the whole world. This requires combining the `when` directive with `changeset` checks.

2.  **跨平台相容性測試 (Cross-Platform Compatibility Testing)**：
    對於開發 SDK 或 Library 的團隊，必須確保程式碼在不同環境（JDK 8/11/17 或 Python 3.8/3.9/3.10）下皆能運作。Matrix build 是此場景的標準解法。
    **Cross-Platform Compatibility Testing:**
    For teams developing SDKs or Libraries, ensuring code works across different environments (JDK 8/11/17 or Python 3.8/3.9/3.10) is mandatory. Matrix builds are the standard solution here.

3.  **資源隔離與成本控制 (Resource Isolation & Cost Control)**：
    透過在不同 Stage 指定不同的 `agent`（例如：編譯用高 CPU 機器，部署用輕量容器），可以優化雲端資源成本與並發量。
    **Resource Isolation & Cost Control:**
    By specifying different `agent`s for different stages (e.g., high-CPU machines for compilation, lightweight containers for deployment), you can optimize cloud resource costs and concurrency.

---

# 4. 逐步示例 (Walkthrough / Example)

## 場景：高效能的多環境驗證 Pipeline (Scenario: High-Performance Multi-Environment Verification Pipeline)

**目標**：我們要建立一個 Pipeline，它能夠平行執行單元測試與 Lint check，並且針對核心邏輯進行多版本的矩陣測試。如果任何一個平行步驟失敗，應盡快終止以節省資源（Fail Fast）。
**Goal**: We want to build a pipeline that executes unit tests and lint checks in parallel, and performs matrix testing on multiple versions for the core logic. If any parallel step fails, it should terminate as soon as possible to save resources (Fail Fast).

### 程式碼實作 (Code Implementation)

```groovy
pipeline {
    agent none // 不在根層級分配 agent，節省 master/executor 資源
               // Do not allocate agent at root level to save master/executor resources

    options {
        timeout(time: 1, unit: 'HOURS') // 防止掛死
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        stage('Setup') {
            agent { label 'linux-small' }
            steps {
                checkout scm
                sh 'echo "Initializing build environment..."'
                // 可以在此 stash 原始碼，供後續 stage 使用
                // Can stash source code here for subsequent stages
                stash includes: '**', name: 'source-code'
            }
        }

        stage('Quality Checks') {
            // 平行執行獨立任務
            // Execute independent tasks in parallel
            parallel {
                stage('Lint') {
                    agent { label 'linux-small' }
                    steps {
                        unstash 'source-code'
                        sh './run-linter.sh'
                    }
                }
                stage('Security Scan') {
                    agent { label 'linux-medium' }
                    steps {
                        unstash 'source-code'
                        sh './run-sast.sh'
                    }
                }
            }
        }

        stage('Matrix Test') {
            // 矩陣策略：針對不同 Node 版本進行測試
            // Matrix Strategy: Test against different Node versions
            matrix {
                axes {
                    axis {
                        name 'NODE_VERSION'
                        values '14', '16', '18'
                    }
                    axis {
                        name 'BROWSER'
                        values 'chrome', 'firefox'
                    }
                }
                excludes {
                    // 排除不支援的組合 (例如 Node 14 不跑 Chrome)
                    // Exclude unsupported combinations
                    exclude {
                        axis {
                            name 'NODE_VERSION'
                            values '14'
                        }
                        axis {
                            name 'BROWSER'
                            values 'chrome'
                        }
                    }
                }
                stages {
                    stage('Test Execution') {
                        agent {
                            docker {
                                image "node:${NODE_VERSION}"
                                label 'docker-node'
                            }
                        }
                        steps {
                            unstash 'source-code'
                            echo "Testing with Node ${NODE_VERSION} on ${BROWSER}"
                            // 模擬測試指令
                            // Simulate test command
                            sh "echo 'Running tests...'" 
                        }
                    }
                }
            }
        }
        
        stage('Deploy') {
            // 僅在 master 分支且測試通過後執行
            // Execute only on master branch and after tests pass
            when {
                branch 'master'
            }
            agent { label 'deploy-node' }
            steps {
                script {
                    // 使用 script block 處理複雜邏輯
                    // Use script block for complex logic
                    def releaseVersion = sh(returnStdout: true, script: 'git describe --tags').trim()
                    if (releaseVersion) {
                        echo "Deploying version: ${releaseVersion}"
                        // sh "./deploy.sh ${releaseVersion}"
                    } else {
                        error "No tag found, skipping deployment."
                    }
                }
            }
        }
    }

    post {
        always {
            // 清理 workspace，避免硬碟塞滿
            // Clean workspace to avoid disk fill-up
            cleanWs()
        }
        failure {
            echo "Pipeline failed! Sending notification..."
            // slackSend ...
        }
    }
}
```

### 關鍵設計解析 (Key Design Analysis)

1.  **`agent none`**: 這是資深工程師的習慣。避免在整個 Pipeline 佔用一個 Executor，而是讓每個 Stage 根據需求動態申請 Agent。
    **`agent none`**: This is a senior engineer's habit. Avoids holding an Executor for the entire Pipeline; instead, lets each Stage dynamically request an Agent as needed.
2.  **`stash` / `unstash`**: 在平行或矩陣執行中，不同的 Stage 可能跑在不同的實體機器或容器上。`stash` 確保了程式碼或 Artifacts 的一致性傳遞。
    **`stash` / `unstash`**: In parallel or matrix execution, different stages might run on different physical machines or containers. `stash` ensures consistent transfer of code or artifacts.
3.  **Matrix `excludes`**: 實務上並非所有組合都有意義。使用 `excludes` 可以修剪矩陣，節省運算資源。
    **Matrix `excludes`**: In practice, not all combinations make sense. Using `excludes` trims the matrix, saving computational resources.
4.  **`script` block**: 在 Declarative Pipeline 中，當你需要將 Shell 執行的結果賦值給變數（如 `git describe`）並進行條件判斷時，`script` 區塊是必要的橋樑。
    **`script` block**: In Declarative Pipeline, when you need to assign the result of a Shell execution to a variable (like `git describe`) and perform conditional logic, the `script` block is a necessary bridge.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 1. 在 `script` 區塊中寫過多邏輯 (Too Much Logic in `script` Block)
*   **錯誤 (Pitfall)**: 把 `Jenkinsfile` 當作 Shell script 的替代品，在 `script` 區塊內寫了幾百行的 Groovy 邏輯。
    **Pitfall**: Treating `Jenkinsfile` as a replacement for Shell scripts, writing hundreds of lines of Groovy logic inside `script` blocks.
*   **影響 (Impact)**: 難以閱讀、難以在本機測試、無法重用。
    **Impact**: Hard to read, hard to test locally, impossible to reuse.
*   **解法 (Solution)**: 將複雜邏輯封裝進 **Shared Libraries** 或外部的 Shell/Python scripts，Pipeline 只負責調度（Orchestration）。
    **Solution**: Encapsulate complex logic into **Shared Libraries** or external Shell/Python scripts; the Pipeline should only handle orchestration.

## 2. 忽略 `failFast` (Ignoring `failFast`)
*   **錯誤 (Pitfall)**: 在 `parallel` 區塊中，如果不設定 `failFast: true`，即使第一個分支一分鐘就失敗了，Jenkins 仍會等待其他跑了 30 分鐘的分支結束才回報失敗。
    **Pitfall**: In a `parallel` block, if `failFast: true` is not set, Jenkins will wait for other branches (that might run for 30 mins) to finish even if the first branch fails in 1 minute.
*   **解法 (Solution)**: 在 `parallel` 階段加入 `failFast true` (注意：語法視 Jenkins 版本略有不同，通常在 options 或 stage 設定)。
    **Solution**: Add `failFast true` in the `parallel` stage (Note: syntax varies slightly by Jenkins version, usually in options or stage settings).

## 3. 濫用 `input` 步驟阻塞 Executor (Blocking Executors with `input`)
*   **錯誤 (Pitfall)**: 在 `agent` 區塊內部使用 `input` 等待人工審核。這會導致該 Agent (Executor) 在等待期間一直被佔用，造成資源浪費與佇列阻塞。
    **Pitfall**: Using `input` inside an `agent` block to wait for manual approval. This causes the Agent (Executor) to be held during the wait, leading to resource waste and queue blocking.
*   **解法 (Solution)**: 將 `input` 放在 `agent none` 的區塊或 `stage` 的最上層（進入 `agent` 之前）。
    **Solution**: Place `input` in an `agent none` block or at the top level of the `stage` (before entering `agent`).

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 你會如何決定使用 Declarative 還是 Scripted Pipeline？
**How do you decide between Declarative and Scripted Pipeline?**

*   **高分回答要點 (Key Points)**:
    *   **預設首選 (Default)**: 90% 的情況應使用 **Declarative**。它易讀、易維護、有語法檢查，且與 Blue Ocean 整合最好。
    *   **例外情況 (Exception)**: 當流程需要極度動態的行為（例如：根據 API 回傳的 JSON 動態生成 50 個並行的 Stage，且每個 Stage 邏輯完全不同）時，**Scripted** 提供的 Groovy 程式化能力才是唯一解。
    *   **混合模式 (Hybrid)**: 在 Declarative 中使用 Shared Library（通常是用 Scripted 語法寫的）是最佳實踐，兼顧結構與彈性。

## Q2: 如何優化一個執行時間過長的 CI Pipeline？
**How do you optimize a CI Pipeline that takes too long to execute?**

*   **高分回答要點 (Key Points)**:
    *   **平行化 (Parallelism)**: 識別無相依性的步驟（Lint, Unit Test, Build Docker Image）並行處理。
    *   **快取 (Caching)**: 善用 Docker layer caching 或依賴套件快取（如 Maven/NPM cache），避免每次重新下載。
    *   **資源垂直擴展 (Vertical Scaling)**: 檢查是否因 Agent 資源不足（CPU/RAM）導致編譯緩慢。
    *   **精準測試 (Test Impact Analysis)**: 只跑受程式碼變更影響的測試（需配合工具或腳本）。

## Q3: 在 Pipeline 中如何安全地處理 Credentials？
**How do you safely handle Credentials in a Pipeline?**

*   **高分回答要點 (Key Points)**:
    *   絕對不要將 Secrets 硬編碼（Hardcode）在 Jenkinsfile。
    *   使用 Jenkins Credentials Binding plugin (`withCredentials`) 將 Secrets 注入為環境變數。
    *   確保在 Shell script 中使用 `set +x` 避免 Secrets 在 log 中被印出（雖然 Jenkins 會嘗試 mask，但不要冒險）。
    *   考慮使用外部 Secret Manager (如 HashiCorp Vault, AWS Secrets Manager) 動態獲取。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 記憶錨點 (Key Takeaways)
1.  **Declarative First**: 優先使用 Declarative Pipeline，將複雜邏輯推入 Shared Libraries。
2.  **Parallel & Matrix**: 這是縮短 Feedback loop 的兩大神器，務必掌握。
3.  **Agent None**: 在 Pipeline 根層級使用 `agent none`，實現精細的資源控制。
4.  **Fail Fast**: 在平行處理中設定快速失敗，節省雲端成本與開發者時間。
5.  **Script Block**: 它是 Declarative 通往 Groovy 強大功能的橋樑，但要謹慎使用，避免邏輯洩漏。

## 後續延伸 (Next Steps)
*   **下一章 (Chapter 03)**: 將深入探討 **Jenkins Shared Libraries**。我們將學習如何將本章提到的複雜邏輯抽象化，建立可供全公司數百個專案共用的標準化 Pipeline 模組。
    **Next Chapter (Chapter 03):** We will dive deep into **Jenkins Shared Libraries**. We will learn how to abstract the complex logic mentioned in this chapter to build standardized Pipeline modules reusable across hundreds of projects in the company.