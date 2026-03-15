# 常見反模式與陷阱 / Common Anti-patterns & Pitfalls

在 GitHub 的使用旅程中，團隊往往會因為習慣於舊有的版控思維，或是為了求快而忽略安全與自動化架構，導致陷入「技術債」的泥沼。本章節將解析那些「看起來能動，但實際上正在慢性毒害專案」的反模式，並提供修正路徑。

---

## Mental model｜心智模型

要識別反模式，首先要建立正確的 GitHub 協作心智模型：

1.  **流動性優於囤積 (Flow over Hoarding)**：
    *   GitHub 的核心價值在於「流動」。任何阻礙代碼流動的行為（如長壽命分支、巨型 PR）都是反模式。想像一條高速公路，囤積代碼就像是把車停在路中間，導致後方回堵（Merge Conflict）。
2.  **最小權限原則 (Principle of Least Privilege)**：
    *   無論是人員的 Access Token 還是 CI/CD 的 `GITHUB_TOKEN`，預設都應該是「無權限」，而非「全開」。
3.  **配置即代碼 (Configuration as Code)**：
    *   如果你手動在 UI 上點擊設定（例如 Branch Protection Rules），而沒有紀錄或 Terraform 化，這就是不可靠的。

---

## Patterns & best practices｜常見模式與最佳實務

在深入反模式之前，先快速對齊什麼是「健康」的模式：

*   **Trunk-Based Development (or Short-lived Branches)**：分支壽命不超過 2 天，頻繁合併回 Main/Master。
*   **Secrets Management Strategy**：使用 OIDC (OpenID Connect) 連接雲端供應商，完全避免長期 Key 存在 GitHub Actions 中。
*   **Modular Workflows**：將重複的 CI 邏輯抽取為 **Composite Actions** 或 **Reusable Workflows**。
*   **Codeowners & Branch Protection**：強制實施 Code Review 與 Status Check，無人能直接 Push 到生產分支。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 分支與協作反模式 (Workflow & Collaboration)

#### ❌ The "Long-Lived" Feature Branch (長壽命分支)
*   **現象**：一個分支開發了兩週甚至一個月，累積了數十個 Commits。
*   **後果**：
    *   **Merge Hell**：合併時產生大量衝突，修復衝突的風險極高。
    *   **Feedback Delay**：CI 測試太晚執行，發現 Bug 時上下文已遺失。
*   **修正**：使用 Feature Flags (Toggle) 技術，將未完成的功能合併進主幹，但對使用者隱藏。

#### ❌ The "Big Bang" PR (巨型 PR)
*   **現象**：一個 PR 包含 `+5000 / -3000` 行變更，涉及多個模組。
*   **後果**：
    *   **Rubber Stamping**：Reviewer 無法消化，只能盲目按 Approve。
    *   **Blocker**：只要其中一個小功能有 Bug，整個 PR 都被卡住無法上線。
*   **修正**：原子化提交 (Atomic Commits)，一個 PR 只做一件事。

### 2. 安全性反模式 (Security)

#### ❌ Secrets in Codebase (將機密寫入代碼)
*   **現象**：開發者為了方便，將 API Key、Database Password 寫在 `.env` 或程式碼中並 Push。
*   **後果**：即使後來刪除了該檔案，Git History 中依然存在。駭客利用爬蟲秒級掃描公開與私有庫。
*   **修正**：
    *   使用 `git-secrets` 或 GitHub Advanced Security 的 Secret Scanning。
    *   若已洩漏，**必須**視為該 Key 已遭竊，立即 Rotate (更換) Key，並使用 `git filter-repo` 清洗歷史（不建議僅用 `git revert`）。

#### ❌ Over-permissive PATs (權限過大的個人存取權杖)
*   **現象**：在 CI/CD 或腳本中使用開發者的 Personal Access Token (PAT)，且勾選了 `repo` (Full control) 權限。
*   **後果**：若 Token 洩漏，攻擊者可控制所有儲存庫。且當該員工離職，所有自動化流程瞬間癱瘓。
*   **修正**：
    *   優先使用 **GitHub Apps** 進行機器對機器的驗證。
    *   若必須用 Token，使用 **Fine-grained PATs** 限制特定 Repo 與權限範圍。

### 3. 自動化反模式 (GitHub Actions)

#### ❌ The "God Workflow" (上帝工作流)
*   **現象**：一個 `.github/workflows/main.yml` 檔案長達 1000 行，包含 Build, Test, Deploy, Notification 所有邏輯。
*   **後果**：難以閱讀、難以除錯、無法複用。
*   **修正**：拆分為多個 Jobs，並將通用邏輯提取為 **Composite Actions** (`action.yml`)。

#### ❌ Unpinned 3rd-party Actions (未鎖定版本的第三方 Actions)
*   **現象**：使用 `uses: actions/checkout@v3` 或 `uses: owner/action@master`。
*   **後果**：這是一種供應鏈攻擊風險。若作者的 Tag 被覆蓋或 Master 分支被植入惡意代碼，你的 CI 就會執行惡意腳本。
*   **修正**：使用 Commit SHA 鎖定版本，例如 `uses: actions/checkout@a12b3c... # v3.0.0`，並搭配 Dependabot 自動更新。

---

## Checklists & workflows｜檢查清單與流程

在進行 Code Review 或設定新 Repository 時，請使用此清單進行「健康檢查」。

### ✅ Repository Setup & Security Checklist
- [ ] **Branch Protection**：Main/Master 分支是否已啟用保護？（Require PR, Require Status Checks）。
- [ ] **Secret Scanning**：是否已啟用 GitHub 的 Secret Scanning 功能？
- [ ] **Least Privilege**：檢查 Settings > Actions > General，`GITHUB_TOKEN` 權限是否設為 "Read and write permissions"？（建議預設改為 Read-only，在 YAML 中視需要提升）。
- [ ] **CODEOWNERS**：重要目錄是否設定了自動指派 Reviewer？

### ✅ Workflow & CI/CD Checklist
- [ ] **Timeout Setting**：每個 Job 是否都有設定 `timeout-minutes`？（防止卡死導致吃光 Action Minutes）。
- [ ] **Caching**：是否使用了 `actions/cache` 來快取 `node_modules` 或 build artifacts？
- [ ] **Concurrency Group**：是否設定了 `concurrency` 以避免同一個 PR 的舊 Commit 仍在跑 CI 浪費資源？
- [ ] **Hardcoded Values**：YAML 中是否有寫死的版本號或環境變數？（應移至 Repository Variables）。

---

## Real-world examples｜實戰案例

### Case 1: The "Accidental Secret Leak" Cleanup
**情境**：開發者小明不小心把 AWS `ACCESS_KEY_ID` 隨著 `config.json` push 到了公開的 GitHub Repo。

**錯誤處置 (Anti-pattern)**：
1.  小明驚慌失措。
2.  在本地刪除該行代碼。
3.  `git commit -m "remove secret"` 然後 `git push`。
4.  **結果**：駭客翻閱 Commit History 依然找得到 Key，且 AWS 帳單已經爆了。

**正確處置 (Best Practice)**：
1.  **立即撤銷 (Revoke)** 該 AWS Key（這是最重要的第一步）。
2.  檢查 CloudTrail 確認是否有異常存取。
3.  使用工具清洗 Git 歷史（如果 Repo 必須保留）：
    ```bash
    # 安裝 git-filter-repo (Python tool)
    pip install git-filter-repo

    # 強制移除歷史中的敏感檔案
    git filter-repo --path config.json --invert-paths
    
    # 強制推送到遠端 (需暫時關閉 Branch Protection)
    git push origin --force --all
    ```
4.  通知團隊成員重新 Clone Repo（因為 History Hash 已變更）。

### Case 2: Refactoring the "God Workflow"
**情境**：CI 腳本中有大量重複的 Setup 步驟（安裝 Node, 設定 NPM Registry, Auth）。

**Anti-pattern (Copy-Paste)**:
```yaml
# 每個 Job 都重複這段
jobs:
  test:
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 16
      - run: echo "//registry.npmjs.org/:_authToken=${NPM_TOKEN}" > .npmrc
      - run: npm ci
      - run: npm test
  build:
    steps:
      - uses: actions/checkout@v3
      # ... 重複上述 5 行 ...
```

**Best Practice (Composite Action)**:
建立 `.github/actions/setup-node-env/action.yml`:
```yaml
name: 'Setup Node Env'
description: 'Checkout and setup node with caching'
runs:
  using: "composite"
  steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-node@v3
      with:
        node-version: 16
        cache: 'npm'
    - run: npm ci
      shell: bash
```

主 Workflow 簡化為:
```yaml
jobs:
  test:
    steps:
      - uses: ./.github/actions/setup-node-env
      - run: npm test
```