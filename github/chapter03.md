# 1. 前言與學習目標 (Introduction & Learning Objectives)

在資深工程師的日常工作中，CI/CD 流程往往隨著專案增長而變得臃腫且難以維護。如果你發現自己在多個 Repository 之間複製貼上相同的 YAML 設定，或者你的 Workflow 充斥著長達數百行的 Shell Script，那麼你需要將「軟體工程」的原則（如 DRY、模組化、單元測試）引入 GitHub Actions。

In the daily routine of a Senior Engineer, CI/CD pipelines often become bloated and unmaintainable as projects grow. If you find yourself copy-pasting the same YAML configurations across multiple repositories, or if your workflows are cluttered with hundreds of lines of Shell Scripts, you need to introduce "Software Engineering" principles (like DRY, modularization, unit testing) into GitHub Actions.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精準選擇模組化策略**：清楚區分 **Composite Actions** 與 **Reusable Workflows** 的適用場景與限制。
    **Select the right modularization strategy**: Clearly distinguish the use cases and limitations between **Composite Actions** and **Reusable Workflows**.
2.  **開發高品質 Custom Action**：使用 TypeScript 與 `@actions/toolkit` 開發具備型別安全、易於測試且高效能的 Action，取代脆弱的 Shell Script。
    **Develop high-quality Custom Actions**: Use TypeScript and `@actions/toolkit` to build type-safe, testable, and high-performance Actions, replacing fragile Shell Scripts.
3.  **掌握發布與版本控制**：理解 Action 的版本管理策略（SemVer、Mutable Tags vs. Immutable SHAs）及其對供應鏈安全的影響。
    **Master publishing and versioning**: Understand versioning strategies for Actions (SemVer, Mutable Tags vs. Immutable SHAs) and their impact on supply chain security.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 三種抽象層次 (Three Levels of Abstraction)

我們可以將 GitHub Action 的擴充方式類比為程式語言中的不同封裝層級：
We can analogize GitHub Action extensions to different encapsulation levels in programming languages:

1.  **Composite Actions (複合動作)**
    *   **類比 (Analogy)**：Private Helper Function / Mixin。
    *   **定義 (Definition)**：將多個 `steps` 封裝成一個單一的 Action。它在呼叫者的 Job context 中執行，沒有獨立的環境。
    *   **適用 (Use Case)**：封裝重複的 Shell 指令（如設定特定的 build arguments、複雜的 git 操作）。

2.  **Reusable Workflows (可重用工作流程)**
    *   **類比 (Analogy)**：Base Class / Abstract Factory / Shared Library。
    *   **定義 (Definition)**：定義完整的 Workflow（包含 Trigger、Job、Environment），可被其他 Workflow 呼叫。它擁有較強的隔離性。
    *   **適用 (Use Case)**：標準化整個 CI/CD 流程（例如：全公司統一的 Java Build & Scan 流程）。

3.  **Custom Actions (JavaScript/Docker)**
    *   **類比 (Analogy)**：External Binary / Plugin。
    *   **定義 (Definition)**：使用 Node.js 或 Docker 容器執行的獨立程式邏輯。
    *   **適用 (Use Case)**：需要複雜邏輯（迴圈、API 互動）、需要特定 OS 套件、或需要極高執行效能時。

## 2.2 JavaScript vs. Docker Actions

| 特性 (Feature) | JavaScript / TypeScript Action | Docker Action |
| :--- | :--- | :--- |
| **執行環境 (Environment)** | 直接在 Runner 的主機 OS 上執行 (Bare metal)。 | 在 Runner 啟動的 Docker Container 內執行。 |
| **啟動速度 (Speed)** | **極快** (Fast)。只需下載 source code 即可執行。 | **較慢** (Slower)。需 Pull image 並啟動 Container。 |
| **跨平台 (Cross-platform)** | 支援 Linux, macOS, Windows (只要有 Node.js)。 | 僅支援 Linux Runner。 |
| **依賴管理 (Dependencies)** | 需打包 `node_modules` (通常用 `ncc` 編譯成單檔)。 | 依賴全部打包在 Docker Image 中，環境一致性最高。 |

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 Platform Engineering 的治理架構 (Governance in Platform Engineering)

在大型組織（50+ 微服務）中，讓每個團隊各自維護 CI/CD YAML 是反模式（Anti-pattern）。Platform Team 通常會設計一個 **Centralized Action Repository**。

In large organizations (50+ microservices), letting every team maintain their own CI/CD YAML is an anti-pattern. Platform Teams usually design a **Centralized Action Repository**.

*   **架構 (Architecture)**：
    *   建立一個名為 `org-actions` 的 Repo。
    *   內含標準化的 Reusable Workflows（如 `build-deploy-k8s.yml`）與通用的 Composite Actions（如 `setup-corporate-proxy`）。
*   **優勢 (Benefits)**：
    *   **Security Compliance**：可以在 Reusable Workflow 中強制加入 Security Scan (SAST/DAST)，應用程式團隊無法繞過。
    *   **Maintainability**：當雲端憑證輪替或部署邏輯變更時，只需更新中央 Repo，所有下游專案自動生效（若使用 Floating Tag）。

## 3.2 效能與成本考量 (Performance & Cost Considerations)

*   **Docker Action 的冷啟動**：如果你的 Action 只需要執行幾秒鐘（例如傳送 Slack 通知），使用 Docker Action 可能會因為 `docker pull` 導致執行時間翻倍。此時應優先選擇 TypeScript Action。
*   **頻寬成本**：頻繁下載大型 Docker Image 會消耗 GitHub Actions 的頻寬配額（如果是 Self-hosted Runner 則消耗內網頻寬）。

*   **Docker Action Cold Start**: If your Action only runs for a few seconds (e.g., sending a Slack notification), using a Docker Action might double the execution time due to `docker pull`. In this case, TypeScript Action should be preferred.
*   **Bandwidth Cost**: Frequent pulling of large Docker Images consumes GitHub Actions bandwidth quotas (or internal network bandwidth for Self-hosted Runners).

---

# 4. 逐步示例：從 Shell 到 TypeScript Action (Walkthrough: From Shell to TypeScript Action)

## 情境 (Scenario)

我們需要一個步驟，檢查 Pull Request 的標題是否符合 Conventional Commits 規範，若不符合則在 PR 上留言並 Fail build。

We need a step to check if a Pull Request title adheres to Conventional Commits. If not, comment on the PR and fail the build.

### Phase 1: Naive Approach (Inline Shell)

最直覺的做法是直接寫 Shell Script。
The most intuitive approach is writing a Shell Script directly.

```yaml
- name: Check PR Title
  if: github.event_name == 'pull_request'
  run: |
    TITLE="${{ github.event.pull_request.title }}"
    REGEX="^(feat|fix|docs|style|refactor|perf|test|chore)(\(.+\))?: .+"
    if [[ ! "$TITLE" =~ $REGEX ]]; then
      echo "Error: Invalid PR title"
      # 這裡還需要複雜的 curl 指令來呼叫 GitHub API 留言...
      exit 1
    fi
```

**缺點 (Drawbacks)**：難以閱讀、難以重用、呼叫 GitHub API 撰寫 `curl` 非常痛苦且容易出錯（Escaping issues）。
**Drawbacks**: Hard to read, hard to reuse, and calling GitHub API via `curl` is painful and error-prone (Escaping issues).

### Phase 2: Professional Approach (TypeScript Action)

我們將其轉寫為 TypeScript Action。這讓我們可以使用 `@actions/core` 處理輸入輸出，用 `@actions/github` 處理 API。

We convert this into a TypeScript Action. This allows us to use `@actions/core` for inputs/outputs and `@actions/github` for API interactions.

**1. 初始化專案 (Initialize Project)**

```bash
npm init -y
npm install @actions/core @actions/github
npm install -D typescript @types/node @vercel/ncc
```
*(註：`ncc` 用於將所有依賴打包成單一 JS 檔)*
*(Note: `ncc` is used to bundle all dependencies into a single JS file)*

**2. 定義 Metadata (`action.yml`)**

```yaml
name: 'Conventional Commit Checker'
description: 'Checks PR title and comments if invalid'
inputs:
  github-token:
    description: 'GitHub Token'
    required: true
  pr-title:
    description: 'Title of the PR'
    required: true
runs:
  using: 'node20'
  main: 'dist/index.js'
```

**3. 實作邏輯 (`src/index.ts`)**

```typescript
import * as core from '@actions/core';
import * as github from '@actions/github';

async function run() {
  try {
    const token = core.getInput('github-token');
    const title = core.getInput('pr-title');
    
    // Regex for Conventional Commits
    const regex = /^(feat|fix|docs|style|refactor|perf|test|chore)(\(.+\))?: .+/;
    
    if (!regex.test(title)) {
      const octokit = github.getOctokit(token);
      const context = github.context;
      
      if (context.payload.pull_request) {
        await octokit.rest.issues.createComment({
          ...context.repo,
          issue_number: context.payload.pull_request.number,
          body: "❌ **PR Title Error**: Please follow Conventional Commits (e.g., `feat: add new login`)."
        });
      }
      core.setFailed('PR Title does not match conventional commit format.');
    } else {
      core.info('✅ PR Title is valid.');
    }
  } catch (error) {
    if (error instanceof Error) core.setFailed(error.message);
  }
}

run();
```

**4. 打包與發布 (Bundle & Publish)**

```bash
npx ncc build src/index.js -o dist
git add dist/index.js action.yml
git commit -m "feat: initial release"
git tag -a v1.0.0 -m "v1.0.0"
git push origin v1.0.0
```

**為何這是 Senior 等級的做法？ (Why is this Senior level?)**
*   **Robustness**: 使用官方 SDK 處理 API 認證與重試機制。
*   **Testability**: 可以針對 TypeScript 函數編寫 Unit Test (Jest)。
*   **Distribution**: 打包後的 `dist/index.js` 不需使用者安裝 `npm install` 即可執行。

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 忽略 `node_modules` 或未打包 (Ignoring `node_modules` or Not Bundling)

*   **錯誤 (Mistake)**：在 `action.yml` 中指定 `main: index.js`，但沒有提交 `node_modules`，或者期待 Runner 執行 `npm install`。
*   **後果 (Consequence)**：Action 執行失敗，因為 Runner 環境沒有依賴套件。若在 Runtime 執行 `npm install`，會大幅拖慢速度且可能因網路問題失敗。
*   **修正 (Fix)**：始終使用 `ncc` 或 `esbuild` 將程式碼與依賴打包成單一檔案（如 `dist/index.js`）並提交到 Repo。

## 5.2 濫用 Reusable Workflows 導致僵化 (Overusing Reusable Workflows causing Rigidity)

*   **錯誤 (Mistake)**：建立一個包含所有可能步驟的「上帝 Workflow」，並透過數十個 `if: ${{ inputs.do_x }}` 來控制。
*   **後果 (Consequence)**：維護困難，呼叫者難以理解參數組合。
*   **修正 (Fix)**：保持 Reusable Workflow 的單一職責（Single Responsibility）。例如將 `Build` 和 `Deploy` 拆分為不同的 Reusable Workflows，讓呼叫者自行組裝。

## 5.3 使用 Mutable Tags (v1) 進行生產環境部署 (Using Mutable Tags for Production)

*   **錯誤 (Mistake)**：`uses: my-org/security-scan@v1`。
*   **後果 (Consequence)**：如果維護者強制更新了 `v1` tag 且引入了 Bug 或惡意程式碼，你的 Pipeline 會無預警崩潰或被駭（Supply Chain Attack）。
*   **修正 (Fix)**：在高度敏感的環境，應使用 Commit SHA 鎖定版本：`uses: my-org/security-scan@a1b2c3d... # v1.0.1`。並搭配 Dependabot 自動更新 SHA。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 請比較 Composite Action 與 Reusable Workflow 的架構差異與選擇依據。
**Compare the architectural differences and selection criteria between Composite Actions and Reusable Workflows.**

*   **高分回答要點 (Key Points)**：
    *   **Scope**：Composite 是一連串的 Steps（在同一個 Job/Runner 內）；Reusable 是一連串的 Jobs（可以跨 Runner）。
    *   **Secrets**：Reusable Workflow 像是一個被呼叫的函數，需要明確傳遞 Secrets (`secrets: inherit` 或明確列出)；Composite Action 直接存取當前 Job 的 env，但無法定義自己的 Secrets。
    *   **Use Case**：如果只是要封裝 "Setup Java & Maven"，用 Composite。如果要封裝 "Build -> Test -> Upload Artifact" 完整流程，用 Reusable。

## Q2: 如何確保 Custom Action 的安全性與可維護性？
**How do you ensure the security and maintainability of Custom Actions?**

*   **高分回答要點 (Key Points)**：
    *   **Dependency Locking**：使用 `package-lock.json` 並定期掃描依賴漏洞 (Dependabot)。
    *   **Bundling**：提交編譯後的 `dist` 檔，避免 Runtime 下載依賴。
    *   **Pinning**：建議使用者使用 SHA hash 引用 Action。
    *   **Testing**：實作 Unit Test (Jest) 測試邏輯，並建立一個 Self-Test Workflow 在每次 Push 時驗證 Action 本身功能正常。

## Q3: 在設計一個供全公司使用的 Action 時，你會如何處理版本控制？
**How would you handle versioning when designing an Action for company-wide use?**

*   **高分回答要點 (Key Points)**：
    *   遵循 **Semantic Versioning (SemVer)**。
    *   維護 **Major Version Tag** (如 `v1`)：這是一個 "Floating Tag"，指向最新的 `v1.x.x`。方便使用者自動接收非破壞性更新。
    *   發布流程：當發布 `v1.2.0` 時，CI Script 應自動將 `v1` tag 移動到 `v1.2.0` 的 commit 上。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)

1.  **DRY your CI/CD**：使用 **Composite Actions** 封裝重複步驟，使用 **Reusable Workflows** 標準化流程。
2.  **TypeScript over Shell**：對於複雜邏輯，優先使用 **TypeScript Action**，它提供型別安全、更好的 API 整合與測試能力。
3.  **Docker for Consistency**：當依賴特定 OS 工具或環境時，使用 **Docker Action**，但需注意冷啟動時間。
4.  **Bundling is Mandatory**：JavaScript Action 必須打包 (`ncc`/`esbuild`) 依賴，確保執行環境獨立性。
5.  **Security via Pinning**：在生產環境中，優先鎖定 Action 的 **Commit SHA** 以防範供應鏈攻擊。

## 後續延伸 (Next Steps)

*   **Self-Hosted Runners & Scaling**：學習如何管理自建 Runner，以及如何使用 Kubernetes (ARC - Actions Runner Controller) 進行動態擴縮 (Chapter 04)。
*   **Advanced Security**：深入研究 OpenID Connect (OIDC) 與雲端供應商（AWS/GCP）的無金鑰整合，取代長效型 Secret。