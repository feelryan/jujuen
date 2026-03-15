# 1. 前言與學習目標 (Introduction & Learning Objectives)

作為資深工程師，版控不僅僅是執行 `git commit` 或 `git merge`，而是關於如何設計一套能支撐數百人同時協作、確保程式碼品質並維持高頻率部署的機制。本章將超越基礎操作，深入探討適合現代雲端原生開發的策略。

As a Senior Engineer, version control is not just about executing `git commit` or `git merge`; it is about designing a mechanism that supports collaboration among hundreds of engineers, ensures code quality, and maintains high-frequency deployment. This chapter goes beyond basic operations to delve into strategies suitable for modern cloud-native development.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **評估與選擇分支模型 (Evaluate & Select Branching Models)**：能夠根據團隊規模與發布頻率，清晰論述 Trunk-based Development 與 GitFlow 的優劣與適用場景。
    Clearly articulate the trade-offs and use cases of Trunk-based Development vs. GitFlow based on team size and release frequency.
2.  **掌握 Monorepo 治理策略 (Master Monorepo Governance)**：理解在 GitHub 中管理 Monorepo 的挑戰（如 CI 效能、權限控制），並提出相應的解決方案（如 CODEOWNERS、Path filtering）。
    Understand the challenges of managing a Monorepo in GitHub (e.g., CI performance, permission control) and propose solutions (e.g., CODEOWNERS, Path filtering).
3.  **實作進階整合機制 (Implement Advanced Integration Mechanisms)**：理解並能夠配置 GitHub Merge Queue 以解決高併發合併時的語意衝突（Semantic Conflicts）。
    Understand and configure GitHub Merge Queue to resolve semantic conflicts during high-concurrency merges.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

在深入技術細節前，我們需要建立幾個關於大規模協作的心智模型。
Before diving into technical details, we need to establish a few mental models regarding large-scale collaboration.

### 2.1 整合債務 (Integration Debt)

**概念**：分支存活的時間越長，與主幹（Mainline）的差異就越大，合併時的痛苦指數呈指數級上升。這被稱為「整合債務」。
**Concept**: The longer a branch lives, the more it diverges from the Mainline, and the pain of merging increases exponentially. This is known as "Integration Debt".

*   **GitFlow**：傾向於延遲整合（Late Integration），累積較高的整合債務，適合發布週期長、版號嚴謹的傳統軟體（如 Desktop Apps）。
    **GitFlow**: Tends towards Late Integration, accumulating higher integration debt. Suitable for traditional software with long release cycles and strict versioning (e.g., Desktop Apps).
*   **Trunk-based Development (TBD)**：強調持續整合（Continuous Integration），將債務分攤到每天的微小合併中。這是 FAANG 等高績效團隊的標準配備。
    **Trunk-based Development (TBD)**: Emphasizes Continuous Integration, amortizing the debt into daily micro-merges. This is the standard for high-performance teams like FAANG.

### 2.2 邏輯衝突 vs. 語意衝突 (Logical vs. Semantic Conflicts)

**概念**：Git 只能偵測「邏輯衝突」（同一行程式碼被修改）。但在大型系統中，更危險的是「語意衝突」。
**Concept**: Git can only detect "Logical Conflicts" (modifications to the same line of code). However, in large systems, "Semantic Conflicts" are more dangerous.

*   **情境**：PR A 修改了函數 `foo()` 的簽名；PR B 呼叫了舊的 `foo()`。兩者分別通過 CI，但合併後主幹會壞掉（Build Broken）。
    **Scenario**: PR A changes the signature of function `foo()`; PR B calls the old `foo()`. Both pass CI individually, but the mainline breaks after merging.
*   **解法**：這就是 **GitHub Merge Queue** 存在的意義——在合併前預先模擬合併後的狀態進行測試。
    **Solution**: This is why **GitHub Merge Queue** exists—to pre-simulate the merged state for testing before the actual merge.

### 2.3 Monorepo vs. Polyrepo

這不是二元對立，而是關於「依賴管理」的權衡。
This is not a binary choice but a trade-off regarding "dependency management".

*   **Polyrepo**：依賴管理發生在 `package.json` 或 `go.mod` 版本號層級。
    **Polyrepo**: Dependency management happens at the version level (e.g., `package.json` or `go.mod`).
*   **Monorepo**：依賴管理發生在原始碼（Source Code）層級。所有專案共享同一版本的 library，強迫原子性升級（Atomic Upgrades）。
    **Monorepo**: Dependency management happens at the Source Code level. All projects share the same library version, forcing Atomic Upgrades.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在系統設計面試或架構規劃中，版控策略直接影響系統的 **Deployability (可部署性)** 與 **Reliability (可靠性)**。
In system design interviews or architecture planning, version control strategies directly impact the system's **Deployability** and **Reliability**.

### 3.1 微服務架構下的版控選擇 (Version Control in Microservices)

假設你正在設計一個由 50 個微服務組成的電商平台：
Suppose you are designing an e-commerce platform consisting of 50 microservices:

*   **Polyrepo Approach**:
    *   **優點 (Pros)**：服務間強隔離，權限控制簡單，CI 速度快（只跑當前 repo）。
    *   **缺點 (Cons)**：跨服務的重構（如升級共用的 Logging Library）極其痛苦，需要協調 50 個 PR。
    *   **GitHub Feature**: 使用 **GitHub Apps** 或 **Submodules** (不推薦) 來協調。

*   **Monorepo Approach (Recommended for cohesive teams)**:
    *   **優點 (Pros)**：原子性提交（一次 PR 修改 API 定義與所有 Consumer），程式碼可視性高。
    *   **缺點 (Cons)**：CI 複雜度高，需要精細的 **Code Owners** 設定。
    *   **GitHub Feature**: 必須搭配 **Path Filters** (在 Actions 中) 與 **CODEOWNERS** 檔案來確保只有相關團隊能審核特定目錄。

### 3.2 Branch Protection Rules 作為合規閘門 (Compliance Gate)

在 Production 環境中，GitHub 的 Branch Protection Rules 是資安合規的第一道防線：
In a Production environment, GitHub's Branch Protection Rules are the first line of defense for security compliance:

1.  **Require pull request reviews before merging**: 強制至少 1-2 人 Review，防止惡意程式碼。
    Enforce at least 1-2 reviews to prevent malicious code.
2.  **Require status checks to pass**: 確保 CI (Unit Test, Lint, Security Scan) 全綠才能合併。
    Ensure CI (Unit Test, Lint, Security Scan) is all green before merging.
3.  **Require signed commits**: 防止身分偽造。
    Prevent identity spoofing.

---

# 4. 逐步示例 (Walkthrough / Example)

本節將展示如何從一個不穩定的 CI 流程，演進到使用 GitHub Merge Queue 的高可靠流程。
This section demonstrates the evolution from an unstable CI process to a highly reliable process using GitHub Merge Queue.

### 4.1 問題背景 (Scenario)

一個擁有 100 位工程師的團隊使用 Trunk-based Development。每天約有 50 個 PR 合併進 `main`。
A team of 100 engineers uses Trunk-based Development. About 50 PRs are merged into `main` daily.

**痛點 (Pain Point)**：
雖然每個 PR 都通過了 CI，但 `main` 分支經常壞掉（Broken Trunk）。原因是工程師 A 和 B 的 PR 在 CI 執行期間是並行的，互不知道對方的變更，導致「語意衝突」。
Although every PR passes CI, the `main` branch frequently breaks. The reason is that PRs from Engineer A and B run in parallel during CI, unaware of each other's changes, leading to "semantic conflicts".

### 4.2 解決方案演進 (Solution Evolution)

#### Phase 1: Naive Approach (Require Up-to-date Branch)
在 GitHub 設定中勾選 "Require branches to be up to date before merging"。
Check "Require branches to be up to date before merging" in GitHub settings.

*   **結果**: 當 A 合併後，B 的 PR 變為 outdated，必須 rebase 並重跑 CI。
    **Result**: When A merges, B's PR becomes outdated and must be rebased and CI re-run.
*   **缺點**: 在高併發下會造成 "Merge Train Contention"（搶火車）。每個人都在排隊重跑 CI，導致合併時間從分鐘級變成小時級。
    **Drawback**: Creates "Merge Train Contention" under high concurrency. Everyone queues to re-run CI, turning merge times from minutes to hours.

#### Phase 2: GitHub Merge Queue (The Advanced Solution)
啟用 GitHub 的 Merge Queue 功能。這是一種伺服器端的排隊機制。
Enable GitHub's Merge Queue feature. This is a server-side queuing mechanism.

**運作流程 (Workflow)**:
1.  工程師點擊 "Merge when ready" (加入 Queue)。
    Engineers click "Merge when ready" (Join Queue).
2.  GitHub 建立一個臨時分支（如 `gh-readonly-queue/main/...`）。
    GitHub creates a temporary branch (e.g., `gh-readonly-queue/main/...`).
3.  此分支包含：`Current Main` + `PR A` + `PR B` (Batching)。
    This branch contains: `Current Main` + `PR A` + `PR B` (Batching).
4.  CI 針對這個「預測的未來狀態」進行測試。
    CI runs tests against this "predicted future state".
5.  若通過，A 和 B 一起合併；若失敗，系統會二分搜尋法（Bisect）找出是誰壞了 build，將其踢出 Queue。
    If passed, A and B merge together; if failed, the system uses bisection to find the culprit and kicks them out of the Queue.

### 4.3 設定範例 (Configuration Example)

雖然這是 UI 設定，但理解其背後的邏輯至關重要。

```yaml
# .github/workflows/ci.yml
name: CI
on:
  pull_request:
  merge_group:  # 關鍵：必須監聽 merge_group 事件
    types: [checks_requested]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Tests
        run: npm test
```

**關鍵點 (Key Takeaway)**:
你的 CI workflow 必須能夠被 `merge_group` 事件觸發。這讓 GitHub Actions 知道它正在為 Queue 中的臨時合併狀態執行測試，而不僅僅是單一 PR。
Your CI workflow must be triggerable by the `merge_group` event. This tells GitHub Actions it is running tests for the temporary merged state in the Queue, not just a single PR.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 長壽命的功能分支 (Long-Lived Feature Branches)

*   **錯誤描述**: 開發一個功能持續 2 週，期間沒有合併回 main，也沒有 pull main 的更新。
    **Description**: Developing a feature for 2 weeks without merging back to main, nor pulling updates from main.
*   **為何不好**: 這是 CI 的反義詞。合併時會變成「大爆炸（Big Bang Merge）」，Code Review 變得不可能（因為變更太大），且容易隱藏 Bug。
    **Why it's bad**: This is the antithesis of CI. Merging becomes a "Big Bang Merge", Code Review becomes impossible (too many changes), and bugs are easily hidden.
*   **替代方案**: 使用 **Feature Flags**。將未完成的程式碼合併進 main，但在 Production 環境中關閉該功能。
    **Alternative**: Use **Feature Flags**. Merge incomplete code into main, but disable the feature in the Production environment.

### 5.2 誤用 GitFlow 於持續部署環境 (Misusing GitFlow in CD Environments)

*   **錯誤描述**: 在需要每天部署多次的 SaaS 產品中使用完整的 GitFlow（develop, release, master, hotfix 分支）。
    **Description**: Using full GitFlow (develop, release, master, hotfix branches) for a SaaS product that requires multiple deployments per day.
*   **為何不好**: 分支切換與合併的儀式感（Ceremony）太重，阻礙了部署速度。GitFlow 是為了「發布版本軟體」設計的，而非「持續交付服務」。
    **Why it's bad**: The ceremony of branch switching and merging is too heavy, hindering deployment speed. GitFlow was designed for "released software", not "continuously delivered services".
*   **替代方案**: 轉向 Trunk-based Development，並利用 Tag 來標記發布點，而非長期維護多個分支。
    **Alternative**: Switch to Trunk-based Development and use Tags to mark release points instead of maintaining multiple long-term branches.

### 5.3 忽略 Monorepo 的構建隔離 (Ignoring Build Isolation in Monorepo)

*   **錯誤描述**: 在 Monorepo 中，改了一行 README，卻觸發了所有微服務的 Build & Test。
    **Description**: In a Monorepo, changing a single line in README triggers Build & Test for all microservices.
*   **為何不好**: 浪費計算資源，且大幅增加開發者的等待時間（Feedback Loop 變長）。
    **Why it's bad**: Wastes compute resources and significantly increases developer wait time (longer Feedback Loop).
*   **替代方案**: 使用 GitHub Actions 的 `paths` 過濾器，或引入 Bazel/Turborepo/Nx 等智慧構建工具來計算依賴圖（Dependency Graph）。
    **Alternative**: Use GitHub Actions `paths` filters, or introduce smart build tools like Bazel/Turborepo/Nx to calculate the Dependency Graph.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 你會如何為一個快速成長的團隊（從 10 人到 100 人）設計分支策略？
**How would you design a branching strategy for a rapidly growing team (from 10 to 100 people)?**

*   **高分回答要點 (Key Points)**:
    *   **演進視角**: 初期可能隨意，但隨著規模擴大，必須轉向 Trunk-based 以減少合併衝突。
    *   **工具支撐**: 提到引入 Merge Queue 來解決併發問題。
    *   **文化轉變**: 強調 Feature Flags 的重要性，將「部署 (Deployment)」與「發布 (Release)」解耦。
    *   **DevEx**: 關注開發者體驗，確保 CI 時間控制在 10-15 分鐘內。

### Q2: 在 Monorepo 中，如何處理 Code Ownership 與權限控制？
**In a Monorepo, how do you handle Code Ownership and permission control?**

*   **高分回答要點 (Key Points)**:
    *   **CODEOWNERS**: 詳細解釋 GitHub 的 `CODEOWNERS` 檔案機制，如何將特定目錄綁定到特定 GitHub Team。
    *   **Branch Protection**: 說明如何設定 "Require review from Code Owners"，強制相關領域專家審核。
    *   **最小權限原則**: 雖然都在一個 repo，但可以透過目錄級別的權限控管（雖然 Git 原生不支援，但 GitHub 平台層支援 Review 閘門）。

### Q3: 什麼時候你不應該使用 Trunk-based Development？
**When should you NOT use Trunk-based Development?**

*   **高分回答要點 (Key Points)**:
    *   **開源專案 (Open Source)**: 貢獻者互不信任，Fork & Pull Request 模型更適合。
    *   **高監管環境 (Highly Regulated)**: 如醫療或航太軟體，需要極其嚴格的 Release 分支審計，且發布頻率極低。
    *   **Legacy 系統**: 缺乏自動化測試的舊系統。沒有測試保護的 Trunk-based Development 是災難。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 重點回顧 (Key Takeaways)

1.  **Trunk-based Development** 是現代高績效團隊的首選，它依賴 **Feature Flags** 來解耦部署與發布。
    **Trunk-based Development** is the preferred choice for modern high-performance teams, relying on **Feature Flags** to decouple deployment from release.
2.  **Integration Debt** 隨時間指數增長，頻繁合併（CI）是降低風險的唯一途徑。
    **Integration Debt** grows exponentially with time; frequent merging (CI) is the only way to mitigate risk.
3.  **GitHub Merge Queue** 解決了高併發下的「語意衝突」與「排隊重跑 CI」的問題。
    **GitHub Merge Queue** solves "semantic conflicts" and "CI re-run queuing" problems under high concurrency.
4.  **Monorepo** 需要額外的工具（如 CODEOWNERS, Build Systems）來維持可擴展性。
    **Monorepo** requires additional tooling (e.g., CODEOWNERS, Build Systems) to maintain scalability.

### 後續延伸 (Next Steps)

*   **實作**: 在你的 GitHub Repo 中設定一個簡單的 `CODEOWNERS` 檔案與 Branch Protection Rule。
    **Action**: Configure a simple `CODEOWNERS` file and Branch Protection Rule in your GitHub Repo.
*   **閱讀**: 研究 Google 或 Meta 的 Monorepo 工程部落格，了解他們如何處理數十億行程式碼的版控。
    **Read**: Research Google or Meta's engineering blogs on Monorepo to understand how they handle version control for billions of lines of code.
*   **下一章預告**: 我們將探討 **GitHub Actions & Workflow Automation**，學習如何將這些策略轉化為自動化的 Pipeline。
    **Next Chapter**: We will explore **GitHub Actions & Workflow Automation**, learning how to translate these strategies into automated pipelines.