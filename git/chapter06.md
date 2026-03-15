# Chapter 06: 自動化 Hooks 與 CI/CD 整合
# Chapter 06: Git Hooks and CI/CD Integration

## 1. 前言與學習目標 (Introduction & Learning Objectives)

在資深工程師的職涯中，Git 不僅僅是版本控制工具，更是自動化管線（Pipeline）的起點。本章將探討如何利用 Git Hooks 建立「左移測試（Shift-Left Testing）」機制，在程式碼進入共用儲存庫前攔截錯誤，並將其與 CI/CD 流程無縫接軌。

In the career of a Senior Software Engineer, Git is not just a version control tool but the starting point of automation pipelines. This chapter explores how to leverage Git Hooks to establish "Shift-Left Testing" mechanisms, intercepting errors before code enters the shared repository, and seamlessly integrating them with CI/CD workflows.

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **區分與實作 Hooks**：清楚界定 Client-side 與 Server-side Hooks 的適用場景，並能配置 `pre-commit`、`commit-msg` 等關鍵 Hooks。
    **Distinguish and Implement Hooks**: Clearly define the use cases for Client-side and Server-side Hooks, and configure critical hooks like `pre-commit` and `commit-msg`.
2.  **設計防禦性工作流**：利用 Hooks 自動化檢查程式碼風格（Linting）、機敏資訊（Secrets）與 Commit Message 規範，減少 Code Review 的低級錯誤。
    **Design Defensive Workflows**: Use Hooks to automate checks for code style (Linting), secrets, and Commit Message conventions, reducing trivial errors in Code Reviews.
3.  **整合 CI/CD 策略**：理解本地 Hooks 與遠端 CI Pipeline 的互補關係，避免過度依賴本地檢查導致的安全漏洞或環境不一致。
    **Integrate CI/CD Strategies**: Understand the complementary relationship between local Hooks and remote CI Pipelines, avoiding security gaps or environmental inconsistencies caused by over-reliance on local checks.

---

## 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 事件驅動模型 (Event-Driven Model)

Git Hooks 的運作機制類似於資料庫的 Triggers 或前端框架的 Event Listeners。它們是存放在 `.git/hooks` 目錄下的腳本，當特定的 Git 事件（如 commit, push, merge）發生時，Git 會自動觸發這些腳本。

The mechanism of Git Hooks is similar to database Triggers or Event Listeners in frontend frameworks. They are scripts stored in the `.git/hooks` directory. When specific Git events (such as commit, push, merge) occur, Git automatically triggers these scripts.

### 2.2 Client-side vs. Server-side Hooks

理解這兩者的差異對於設計系統至關重要：

Understanding the difference between these two is crucial for system design:

*   **Client-side Hooks (本地端)**：
    *   **觸發時機 (Trigger)**：發生在開發者的機器上（例如 `pre-commit`, `prepare-commit-msg`, `pre-push`）。
    *   **用途 (Purpose)**：快速回饋、格式化程式碼、防止將顯而易見的錯誤推送到遠端。
    *   **限制 (Limitation)**：開發者可以輕易繞過（使用 `--no-verify`），且 Hooks 腳本本身不會隨 `git clone` 自動安裝（需要額外工具如 `husky` 或 `pre-commit` 框架協助）。
    *   **Client-side Hooks (Local)**:
        *   **Trigger**: Occurs on the developer's machine (e.g., `pre-commit`, `prepare-commit-msg`, `pre-push`).
        *   **Purpose**: Quick feedback, code formatting, preventing obvious errors from being pushed to remote.
        *   **Limitation**: Developers can easily bypass them (using `--no-verify`), and the hook scripts themselves are not automatically installed with `git clone` (requiring tools like `husky` or the `pre-commit` framework).

*   **Server-side Hooks (伺服器端)**：
    *   **觸發時機 (Trigger)**：發生在遠端儲存庫接收推送時（例如 `pre-receive`, `update`, `post-receive`）。
    *   **用途 (Purpose)**：強制執行政策（Policy Enforcement），例如拒絕非 Fast-forward 的推送、強制 Code Review 權限檢查。
    *   **限制 (Limitation)**：在現代 SaaS 平台（GitHub, GitLab, Bitbucket）中，通常不允許用戶直接配置 Shell Script 形式的 Server-side Hooks，而是透過「Branch Protection Rules」或 Webhooks 來實現類似功能。
    *   **Server-side Hooks (Remote)**:
        *   **Trigger**: Occurs when the remote repository receives a push (e.g., `pre-receive`, `update`, `post-receive`).
        *   **Purpose**: Policy Enforcement, such as rejecting non-fast-forward pushes or enforcing Code Review permissions.
        *   **Limitation**: In modern SaaS platforms (GitHub, GitLab, Bitbucket), users are typically not allowed to configure Server-side Hooks as shell scripts directly. Instead, similar functionality is achieved via "Branch Protection Rules" or Webhooks.

---

## 3. 實務場景與系統設計視角 (Real-World & System Design View)

### 3.1 典型系統架構中的角色 (Role in Typical System Architecture)

在一個成熟的 DevOps 體系中，Git Hooks 扮演「第一道防線」的角色。

In a mature DevOps ecosystem, Git Hooks act as the "First Line of Defense".

**流程圖概念 (Flow Concept):**

1.  **Local Dev**: Developer runs `git commit`.
2.  **Filter 1 (Client Hook)**: `pre-commit` runs Linter & Secret Scanning. (Fail fast, save CI cost).
3.  **Push**: Developer runs `git push`.
4.  **Filter 2 (Server Check)**: GitHub/GitLab checks Branch Protection (e.g., requires signed commits).
5.  **CI Pipeline**: Webhook triggers Jenkins/GitHub Actions. Runs heavy tests (Integration/E2E).
6.  **CD**: Deployment.

### 3.2 對可維護性與擴充性的影響 (Impact on Maintainability & Scalability)

*   **降低 CI 成本 (Cost Reduction)**：
    如果一個簡單的語法錯誤（Syntax Error）就能在本地被 `pre-commit` 攔截，就不需要觸發遠端昂貴的 CI Build。這對於數百人團隊來說，能顯著節省雲端運算資源與排隊時間。
    **Cost Reduction**: If a simple syntax error can be intercepted locally by `pre-commit`, there is no need to trigger an expensive remote CI Build. For a team of hundreds, this significantly saves cloud computing resources and queue time.

*   **一致性 (Consistency)**：
    透過工具（如 `husky` for Node.js 或 `pre-commit` for Python/Go）共享 Hooks 配置，確保所有新進工程師的環境都具備相同的檢查標準，減少 "It works on my machine" 的爭議。
    **Consistency**: By sharing Hook configurations via tools (like `husky` for Node.js or `pre-commit` for Python/Go), you ensure that all new engineers have the same check standards, reducing "It works on my machine" disputes.

---

## 4. 逐步示例 (Walkthrough / Example)

### 情境 (Scenario)

你正在帶領一個團隊開發微服務，你發現團隊常犯兩個錯誤：
1.  不小心將 AWS Keys 或 Private Keys Commit 進去。
2.  Commit Message 格式混亂，導致無法自動生成 Changelog。

You are leading a team developing microservices, and you notice the team frequently makes two mistakes:
1. Accidentally committing AWS Keys or Private Keys.
2. Messy Commit Messages, making it impossible to auto-generate Changelogs.

### 解決方案：使用 `pre-commit` 框架 (Solution: Using `pre-commit` framework)

雖然可以手寫 Shell Script，但在企業級專案中，使用 `pre-commit` (Python 編寫的框架，但支援多語言) 是更標準的做法，因為它易於版本控制與共享。

While you can write Shell Scripts manually, using `pre-commit` (a framework written in Python but supporting multiple languages) is the standard practice in enterprise projects because it is easy to version control and share.

#### Step 1: 安裝與配置 (Installation & Configuration)

在專案根目錄建立 `.pre-commit-config.yaml`：
Create `.pre-commit-config.yaml` in the project root:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  # Detect Secrets (防止機敏資料外洩)
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.16.1
    hooks:
      - id: gitleaks

  # Conventional Commits (規範 Commit Message)
  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v2.1.1
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
```

#### Step 2: 啟用 Hooks (Enable Hooks)

開發者只需執行一次安裝指令：
Developers only need to run the installation command once:

```bash
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg
```

#### Step 3: 驗證流程 (Verification Process)

當開發者嘗試 Commit 一個包含 AWS Key 的檔案時：
When a developer tries to commit a file containing an AWS Key:

```bash
$ git add config.json
$ git commit -m "Add config"

# Output:
# Gitleaks........................................................Failed
# - hook id: gitleaks
# - exit code: 1
#
# leaks found: [ ... details of the leak ... ]
```

Commit 會被自動阻擋，開發者必須修正後才能再次提交。
The commit is automatically blocked, and the developer must fix it before committing again.

### 為什麼這在實務中可行？ (Why is this practical?)

*   **宣告式配置 (Declarative Configuration)**：透過 YAML 管理，Code Review 可以審核檢查規則的變更。
*   **版本鎖定 (Version Pinning)**：`rev: v4.4.0` 確保所有團隊成員使用相同版本的檢查工具，避免工具升級導致的不一致。
*   **Declarative Configuration**: Managed via YAML, allowing Code Reviews to audit changes to check rules.
*   **Version Pinning**: `rev: v4.4.0` ensures all team members use the same version of the tools, avoiding inconsistencies caused by tool upgrades.

---

## 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 肥大的 Pre-commit Hooks (Bloated Pre-commit Hooks)

*   **錯誤 (Pitfall)**：在 `pre-commit` 中執行完整的 Unit Tests 或 Integration Tests。
*   **後果 (Consequence)**：Commit 變得非常慢（超過 10 秒開發者就會感到煩躁）。這會導致開發者習慣性使用 `git commit --no-verify` 來跳過檢查，最終讓 Hooks 形同虛設。
*   **最佳實務 (Best Practice)**：Client-side Hooks 應該只做「輕量級」檢查（Linting, Syntax Check, Secret Scanning）。耗時的測試應留給 CI Server。
*   **Pitfall**: Running full Unit Tests or Integration Tests in `pre-commit`.
*   **Consequence**: Commits become very slow (developers get annoyed after 10 seconds). This leads to developers habitually using `git commit --no-verify` to skip checks, rendering Hooks useless.
*   **Best Practice**: Client-side Hooks should only perform "lightweight" checks (Linting, Syntax Check, Secret Scanning). Time-consuming tests should be left to the CI Server.

### 5.2 僅依賴本地檢查 (Relying Only on Local Checks)

*   **錯誤 (Pitfall)**：認為有了 `pre-commit` 就不需要在 CI 中跑 Lint 或 Secret Scan。
*   **後果 (Consequence)**：惡意或粗心的開發者可以繞過本地 Hooks。此外，透過 Web UI (GitHub/GitLab UI) 直接編輯檔案也會繞過本地 Hooks。
*   **最佳實務 (Best Practice)**：**Defense in Depth**。本地 Hooks 是為了加速開發回饋，CI 才是最終的品質守門員（Source of Truth）。CI 必須再次執行所有關鍵檢查。
*   **Pitfall**: Thinking that with `pre-commit`, there's no need to run Lint or Secret Scan in CI.
*   **Consequence**: Malicious or careless developers can bypass local Hooks. Also, editing files directly via Web UI (GitHub/GitLab UI) bypasses local Hooks.
*   **Best Practice**: **Defense in Depth**. Local Hooks are for accelerating development feedback; CI is the final gatekeeper of quality (Source of Truth). CI must re-run all critical checks.

### 5.3 提交特定環境的 Hooks (Committing Environment-Specific Hooks)

*   **錯誤 (Pitfall)**：直接將 `.git/hooks/pre-commit` 檔案 commit 進 repo，且腳本中包含絕對路徑（如 `/Users/alice/bin/node`）。
*   **後果 (Consequence)**：其他開發者（如 Bob）拉取程式碼後無法執行，因為路徑不同或作業系統不同。
*   **最佳實務 (Best Practice)**：使用 `pre-commit` 框架或 `husky`，並確保腳本使用相對路徑或環境變數。
*   **Pitfall**: Directly committing the `.git/hooks/pre-commit` file into the repo, with scripts containing absolute paths (e.g., `/Users/alice/bin/node`).
*   **Consequence**: Other developers (like Bob) cannot execute it after pulling the code due to different paths or operating systems.
*   **Best Practice**: Use frameworks like `pre-commit` or `husky`, and ensure scripts use relative paths or environment variables.

---

## 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 如何在不降低開發速度的前提下，提升 Code Quality？
**How do you improve Code Quality without slowing down development velocity?**

*   **高分回答要點 (Key Points)**：
    *   提到 **Feedback Loop** 的速度：本地 Hooks 提供即時回饋（秒級），CI 提供完整回饋（分級）。
    *   **分層策略**：本地只跑受影響檔案的 Lint (`lint-staged`)，CI 跑全量測試。
    *   **Escape Hatch**：承認有時需要緊急修復，允許 `--no-verify`，但強調 CI 最終會擋下不合規的程式碼。

### Q2: 如果開發者繞過了本地的 Secret Scanning Hook，我們該如何補救？
**If a developer bypasses the local Secret Scanning Hook, how do we remediate?**

*   **高分回答要點 (Key Points)**：
    *   **CI Gate**：CI Pipeline 中必須包含 Secret Scanning，一旦發現立即 Fail build。
    *   **Remediation**：解釋一旦 Secret 進入 git history，單純 `git revert` 是不夠的（因為歷史紀錄還在）。必須使用 `git filter-repo` 或 BFG Repo-Cleaner 清除歷史，或者（更安全的做法）**立即視該 Secret 為已洩漏並進行輪替 (Rotate the secret)**。
    *   **Monitoring**：提及 GitHub Advanced Security 或類似工具的主動掃描。

### Q3: 請比較 `pre-commit` 與 `pre-push` 的適用場景。
**Compare the use cases for `pre-commit` and `pre-push`.**

*   **高分回答要點 (Key Points)**：
    *   `pre-commit`：最快回饋，適合格式化 (Prettier)、簡單 Linting。頻率高，必須極快。
    *   `pre-push`：頻率較低，適合執行輕量級的 Unit Tests 或檢查是否包含大型二進位檔案。這是程式碼離開本地前的最後一道防線。

---

## 7. 小結與後續延伸 (Summary & Next Steps)

### 重點摘要 (Key Takeaways)

1.  **Hooks 是事件驅動的**：它們攔截 Git 操作，是自動化的起點。
2.  **Client-side vs Server-side**：Client-side 為了速度與開發者體驗；Server-side (CI) 為了安全性與一致性。
3.  **不要依賴單一防線**：本地 Hooks 易被繞過，必須與 CI Pipeline 配合形成縱深防禦。
4.  **速度至上**：本地 Hooks 必須快，只檢查 `staged` 的檔案（使用 `lint-staged`），避免拖慢開發節奏。
5.  **工具標準化**：使用 `pre-commit` 或 `husky` 來管理與共享 Hooks 配置，而非手寫 Shell Scripts。

### 後續延伸 (Next Steps)

*   **Advanced Git Internals**：深入了解 `.git` 目錄結構，理解 Hooks 究竟是如何被 Git 核心呼叫的。
*   **Monorepo Tooling**：在大型 Monorepo (如 Nx, Turborepo, Bazel) 中，如何設計 Hooks 只對受影響的專案（Affected Projects）執行檢查，而非全量檢查。
*   **Custom CI Actions**：學習如何撰寫自己的 GitHub Actions 或 GitLab Runners，將複雜的 Server-side 檢查邏輯模組化。