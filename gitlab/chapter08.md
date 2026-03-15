# 1. 前言與學習目標 (Introduction & Learning Objectives)

在數十人甚至數百人的工程團隊中，單純依賴開發者的自律來維持程式碼品質與分支穩定性是不切實際的。作為資深工程師，你需要將「人治」轉化為「法治」，利用工具自動化執行 Code Review 政策與合併流程。本章將探討如何利用 GitLab 的進階治理功能，解決大規模協作中的瓶頸。

In an engineering team of dozens or even hundreds, relying solely on developer discipline to maintain code quality and branch stability is impractical. As a Senior Engineer, you need to transition from "governance by people" to "governance by code," leveraging tools to automate Code Review policies and merge processes. This chapter explores how to use GitLab's advanced governance features to solve bottlenecks in large-scale collaboration.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **實作精細的權責劃分 (Implement Granular Ownership):** 利用 `CODEOWNERS` 檔案在 Monorepo 或大型專案中自動指派 Reviewers，確保正確的人審核正確的模組。
    Use the `CODEOWNERS` file to automatically assign Reviewers in Monorepos or large projects, ensuring the right people review the right modules.
2.  **解決高併發合併衝突 (Resolve High-Concurrency Merge Conflicts):** 理解並配置 **Merge Trains**，消除「邏輯衝突」導致的 CI 綠燈但合併後壞掉 (Broken Master) 的問題。
    Understand and configure **Merge Trains** to eliminate "semantic conflicts" that cause "Broken Master" scenarios where CI passes individually but fails after merging.
3.  **設計合規的審核流程 (Design Compliant Approval Workflows):** 運用 **Approval Rules** 建立符合 SOC2 或 ISO 標準的 Segregation of Duties (職責分離) 機制。
    Apply **Approval Rules** to establish Segregation of Duties mechanisms compliant with SOC2 or ISO standards.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 CODEOWNERS：程式碼的地契 (The Deed to the Code)

將 `CODEOWNERS` 想像成真實世界的「土地分區使用管制」。在一個大型城市（Monorepo）中，不同的區域（Directories/Files）由不同的委員會（Teams/Users）管轄。
Think of `CODEOWNERS` as "Zoning Laws" in the real world. In a large city (Monorepo), different zones (Directories/Files) are governed by different committees (Teams/Users).

-   **定義 (Definition):** 一個受版控的檔案，定義了誰對路徑下的程式碼負有責任。
    A version-controlled file that defines who is responsible for the code under specific paths.
-   **強制性 (Enforcement):** 它可以與 Protected Branches 結合，強制要求 Owner 必須核准才能合併，而不僅僅是建議。
    It can be combined with Protected Branches to mandate approval from the Owner before merging, rather than just serving as a suggestion.

## 2.2 Approval Rules：政策引擎 (The Policy Engine)

如果 `CODEOWNERS` 是指定「誰」負責，那麼 Approval Rules 就是定義「規則」本身。
If `CODEOWNERS` specifies "who" is responsible, Approval Rules define the "rules" themselves.

-   **多維度閘門 (Multi-dimensional Gates):** 你可以設定多個規則並行，例如：「需要 1 位資深工程師」且「需要 1 位資安人員」。
    You can set multiple parallel rules, such as: "Requires 1 Senior Engineer" AND "Requires 1 Security Engineer."
-   **與 GitHub 的差異 (Difference from GitHub):** GitLab 的 Approval Rules 允許更細緻的「非 Code Owner」規則設定，例如針對特定分支或弱點掃描結果 (Vulnerability-Check) 自動觸發的規則。
    GitLab's Approval Rules allow for more granular "non-Code Owner" rule settings, such as rules automatically triggered for specific branches or vulnerability scan results.

## 2.3 Merge Trains：序列化交易 (Serialized Transactions)

在高頻率提交的團隊中，常見的痛點是：Feature A 的 CI 通過，Feature B 的 CI 也通過，但 A 和 B 合併在一起後系統卻崩潰了。這是因為 CI 通常是基於「當前主幹」跑的，而不是「預測合併後的狀態」。
In high-velocity teams, a common pain point is: Feature A's CI passes, Feature B's CI passes, but when A and B are merged together, the system crashes. This is because CI usually runs against the "current master," not the "predicted post-merge state."

-   **心智模型 (Mental Model):** 將 Merge Trains 視為資料庫的 **序列化交易 (Serializable Transaction)** 或單線道的火車。
    View Merge Trains as a **Serializable Transaction** in a database or a single-track railway.
-   **運作原理 (Mechanism):** GitLab 會將待合併的 MR 排隊，並在臨時的合併結果上執行 Pipeline。如果 MR 1、MR 2、MR 3 同時在隊列中，MR 3 的測試環境是 `Master + MR 1 + MR 2 + MR 3`。
    GitLab queues the MRs waiting to be merged and runs pipelines on the temporary merge results. If MR 1, MR 2, and MR 3 are in the queue, MR 3's test environment is `Master + MR 1 + MR 2 + MR 3`.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 系統架構中的角色 (Role in System Architecture)

在微服務或大型單體架構的 CI/CD 流程中，GitLab 的這些功能位於 **Continuous Integration (CI)** 與 **Continuous Deployment (CD)** 的交界處，充當 **Quality Gate (品質閘門)**。

In the CI/CD pipeline of microservices or large monolithic architectures, these GitLab features sit at the intersection of **Continuous Integration (CI)** and **Continuous Deployment (CD)**, acting as a **Quality Gate**.

-   **可維護性 (Maintainability):** `CODEOWNERS` 防止了「隨意修改核心共用庫」的行為，強迫變更必須經過架構師或核心團隊的審視。
    `CODEOWNERS` prevents "arbitrary changes to core shared libraries," forcing changes to be reviewed by architects or the core team.
-   **安全性 (Security):** Approval Rules 實作了「四眼原則 (Four-eyes principle)」，防止惡意程式碼或錯誤配置（如 Terraform 修改 IAM 權限）被單人合入。
    Approval Rules implement the "Four-eyes principle," preventing malicious code or misconfigurations (like Terraform modifying IAM permissions) from being merged by a single person.
-   **擴充性 (Scalability):** Merge Trains 讓數百名開發者可以同時提交程式碼，而無需手動處理 "Please rebase your branch" 的循環惡夢。
    Merge Trains allow hundreds of developers to submit code simultaneously without manually dealing with the "Please rebase your branch" nightmare loop.

## 3.2 典型流程 (Typical Workflow)

1.  **Developer** 提交 MR。
2.  **GitLab** 根據 `CODEOWNERS` 自動指派 Reviewers（例如 Backend Team 和 Security Team）。
3.  **Approval Rules** 檢查是否滿足條件（例如：Security Team 必須核准，且 Code Coverage 未下降）。
4.  **Developer** 點擊 "Merge to Train"。
5.  **GitLab** 將 MR 加入火車，依序與前車合併並執行 Pipeline。
6.  若成功，自動合併至 Master；若失敗，踢出火車並通知開發者。

---

# 4. 逐步示例 (Walkthrough / Example)

## 情境 (Scenario)

假設你正在維護一個 **Fintech Monorepo**，結構如下：
Assume you are maintaining a **Fintech Monorepo** with the following structure:

-   `/backend` (Go services)
-   `/frontend` (React apps)
-   `/infrastructure` (Terraform)
-   `/lib/crypto` (Shared cryptography library - Critical!)

目標：保護關鍵路徑，並加速日常開發合併。
Goal: Protect critical paths and accelerate daily development merges.

## Step 1: 設定 CODEOWNERS (Configuring CODEOWNERS)

在專案根目錄或 `.gitlab/` 下建立 `CODEOWNERS` 檔案。
Create a `CODEOWNERS` file in the project root or under `.gitlab/`.

```plaintext
# .gitlab/CODEOWNERS

# Section 1: Default Owners
# 任何未被特定規則覆蓋的檔案，預設由 Engineering Leads 負責
# Any file not covered by specific rules defaults to Engineering Leads
* @org/engineering-leads

# Section 2: Backend
# Backend 團隊負責所有 go 檔案
# Backend team owns all go files
/backend/ @org/backend-team
*.go @org/backend-team

# Section 3: Critical Infrastructure (Requires strict approval)
# 基礎設施變更需要 DevOps 團隊
# Infrastructure changes require the DevOps team
/infrastructure/ @org/devops-team

# Section 4: Security Critical
# 加密庫必須由 Security 團隊審核，且這是強制性的
# Crypto library must be reviewed by the Security team, and this is mandatory
[Security]
/lib/crypto/ @org/security-team
```

*註：`[Security]` 是 GitLab 的 Section 功能，允許在 MR Widget 中分組顯示 Approval 狀態。*
*Note: `[Security]` is a GitLab Section feature, allowing approval status to be grouped in the MR Widget.*

## Step 2: 設定 Approval Rules (Setting Approval Rules)

在 GitLab UI (`Settings` -> `Merge requests` -> `Merge request approvals`) 設定：
Configure in GitLab UI (`Settings` -> `Merge requests` -> `Merge request approvals`):

1.  **Rule Name:** `Security Check`
2.  **Target Branch:** `main` (or `production`)
3.  **Approvers:** Select specific security engineers or the group `@org/security-team`.
4.  **Approvals required:** `1` (or more).
5.  **Vulnerability-Check:** 開啟此內建規則，當掃描出 High/Critical 漏洞時，強制要求安全團隊核准。
    Enable this built-in rule to mandate security team approval when High/Critical vulnerabilities are detected.

## Step 3: 啟用 Merge Trains (Enabling Merge Trains)

Merge Trains 依賴於 **Merge Request Pipelines** (在合併結果上跑的 Pipeline)。
Merge Trains rely on **Merge Request Pipelines** (Pipelines running on the merge result).

1.  **UI 設定:** `Settings` -> `Merge requests` -> `Merge options` -> 勾選 `Enable merge trains`。
    **UI Setting:** `Settings` -> `Merge requests` -> `Merge options` -> Check `Enable merge trains`.

2.  **CI 配置 (`.gitlab-ci.yml`):** 確保你的 Pipeline 邏輯能區分一般 MR 和 Merge Train。
    **CI Configuration (`.gitlab-ci.yml`):** Ensure your Pipeline logic distinguishes between standard MRs and Merge Trains.

```yaml
workflow:
  rules:
    # 針對 Merge Train 執行 Pipeline
    # Run pipeline for Merge Train
    - if: '$CI_MERGE_REQUEST_EVENT_TYPE == "merge_train"'
    # 針對一般 Merge Request 執行 Pipeline
    # Run pipeline for standard Merge Request
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'

stages:
  - build
  - test
  - compliance

test_backend:
  stage: test
  script:
    - go test ./...
  # 這裡不需要特別過濾，因為 workflow 已經控制了何時觸發
  # No special filtering needed here as workflow controls when to trigger

compliance_check:
  stage: compliance
  script:
    - ./scripts/check-compliance.sh
  rules:
    # 只在 Merge Train (即將合入 Master 前) 執行昂貴的合規檢查
    # Run expensive compliance checks only on Merge Train (right before merging to Master)
    - if: '$CI_MERGE_REQUEST_EVENT_TYPE == "merge_train"'
```

**為何這樣做可行？**
Merge Train 確保了當你的 MR 真正合入主幹時，它是基於「未來的主幹狀態」通過測試的。如果前面的 MR 失敗，你的 MR 會自動重新排隊（Re-queued）並基於新的狀態重新測試。
**Why this works:**
Merge Trains ensure that when your MR is actually merged into the main branch, it has passed tests based on the "future state of the main branch." If a preceding MR fails, your MR is automatically re-queued and re-tested based on the new state.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 濫用 CODEOWNERS 導致雜訊 (Overusing CODEOWNERS Causing Noise)

-   **錯誤 (Mistake):** 將 `@all-developers` 設為根目錄 `*` 的 Owner。
    Setting `@all-developers` as the Owner of the root directory `*`.
-   **後果 (Consequence):** 每一個 MR 都會通知所有人，導致 "Notification Fatigue"（通知疲勞），大家開始忽略審核請求。
    Every MR notifies everyone, leading to "Notification Fatigue," causing people to ignore review requests.
-   **修正 (Fix):** 保持 `CODEOWNERS` 的顆粒度。只對關鍵路徑設定強制 Owner，其他路徑使用選用性的 Approval Rules 或依賴團隊默契。
    Keep `CODEOWNERS` granular. Set mandatory Owners only for critical paths; use optional Approval Rules or team conventions for other paths.

## 5.2 忽略「語意衝突」 (Ignoring "Semantic Conflicts")

-   **錯誤 (Mistake):** 認為 Git 沒有回報 Merge Conflict 就代表安全，因此不使用 Merge Trains 或 Merge Result Pipelines。
    Assuming that if Git reports no Merge Conflict, it is safe, and thus not using Merge Trains or Merge Result Pipelines.
-   **後果 (Consequence):** 開發者 A 改了函數簽名 (Signature)，開發者 B 在另一個檔案呼叫了舊的簽名。兩者都能獨立通過 CI，合入後 Master 壞掉。
    Developer A changes a function signature; Developer B calls the old signature in another file. Both pass CI independently, but Master breaks after merging.
-   **修正 (Fix):** 對於高頻率協作專案，務必啟用 Merge Trains 或至少啟用 "Merge result pipelines"。
    For high-velocity projects, strictly enable Merge Trains or at least "Merge result pipelines."

## 5.3 審核瓶頸 (Approval Bottlenecks)

-   **錯誤 (Mistake):** 設定了嚴格的 Approval Rules (例如：必須由 CTO 核准)，但只有一個人有權限。
    Setting strict Approval Rules (e.g., must be approved by CTO) but only one person has the permission.
-   **後果 (Consequence):** 該人員休假或忙碌時，整個團隊的部署停擺。
    When that person is on leave or busy, the entire team's deployment halts.
-   **修正 (Fix):** 總是使用 **Group** 作為 Approver (例如 `@backend-leads`) 而非個人，並設定備援機制。
    Always use a **Group** as the Approver (e.g., `@backend-leads`) instead of individuals, and establish redundancy mechanisms.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何在數百人的 Monorepo 中防止 "Broken Master"？
**How do you prevent "Broken Master" in a Monorepo with hundreds of developers?**

-   **高分回答要點 (Key Points):**
    -   指出 Git Merge Conflict 與 Semantic Conflict 的區別。
    -   解釋 **Merge Trains** 的運作原理（序列化測試）。
    -   提及 **Merge Result Pipelines** 的必要性（在合併後的狀態跑測試）。
    -   討論 Trade-off：Merge Trains 會增加 CI 資源消耗與等待時間，需配合並行處理 (Parallelism) 或自動取消策略優化。

## Q2: 我們的系統需要符合 SOC2 合規，你會如何在 GitLab 中實作？
**Our system needs to be SOC2 compliant. How would you implement this in GitLab?**

-   **高分回答要點 (Key Points):**
    -   關鍵詞：**Segregation of Duties (職責分離)**。
    -   實作：使用 **Protected Branches** 禁止直接 Push 到 production 分支。
    -   實作：使用 **Approval Rules** 強制要求至少一人（非作者本人）核准。
    -   實作：使用 **CODEOWNERS** 確保特定敏感目錄（如 IAM 配置）由特定團隊審核。
    -   Audit Trail：GitLab 的 Merge Request 紀錄即為審計軌跡。

## Q3: 團隊抱怨 Code Review 等太久，你會如何利用工具改善？
**The team complains that Code Review takes too long. How would you use tools to improve this?**

-   **高分回答要點 (Key Points):**
    -   分析瓶頸：是找不到人 Review，還是 Review 過程太長？
    -   利用 **CODEOWNERS** 自動指派，減少「尋找 Reviewer」的時間。
    -   利用 **GitLab Duo (AI)** 或自動化腳本先進行初步 Review (Linting, Static Analysis)，減少人工 Review 的低級錯誤負擔。
    -   設定 **Approval Rules** 的 "Remove all approvals when new commits are pushed" 選項需謹慎，避免非邏輯性的小修改導致重新排隊。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)

1.  **CODEOWNERS** 是程式碼庫的法律，定義了誰擁有什麼，並可強制執行審核權。
    **CODEOWNERS** is the law of the codebase, defining who owns what and enforcing review authority.
2.  **Approval Rules** 提供了多維度的品質閘門，是滿足安全合規（SOC2/ISO）的關鍵工具。
    **Approval Rules** provide multi-dimensional quality gates and are key tools for meeting security compliance (SOC2/ISO).
3.  **Merge Trains** 解決了高併發開發下的邏輯衝突問題，將合併流程從「樂觀鎖」轉為「序列化交易」，確保 Master 永遠是綠燈。
    **Merge Trains** solve semantic conflicts in high-concurrency development, shifting the merge process from "optimistic locking" to "serialized transactions," ensuring Master is always green.
4.  良好的治理配置應當是「無感」但「有效」的，避免過度干擾開發者的日常工作流。
    Good governance configuration should be "seamless" yet "effective," avoiding excessive interference with the developer's daily workflow.

## 下一步 (Next Steps)

-   **延伸閱讀:** 研究 GitLab 的 **Compliance Frameworks**，了解如何將上述規則打包成範本，強制套用到組織內的所有專案。
    **Further Reading:** Research GitLab's **Compliance Frameworks** to understand how to package the above rules into templates and enforce them across all projects in the organization.
-   **實作練習:** 在一個測試專案中設定 Merge Train，並嘗試製造一個「邏輯衝突」（A 改名，B 呼叫舊名），觀察 Merge Train 如何攔截此錯誤。
    **Hands-on Practice:** Set up a Merge Train in a test project and try to create a "semantic conflict" (A renames, B calls old name) to observe how the Merge Train intercepts this error.
-   **下一章預告:** 我們將探討 **GitLab CI/CD 的進階優化 (Advanced CI/CD Optimization)**，包括 DAG (Directed Acyclic Graph) Pipelines 與 Dynamic Child Pipelines。
    **Next Chapter:** We will explore **Advanced CI/CD Optimization**, including DAG (Directed Acyclic Graph) Pipelines and Dynamic Child Pipelines.