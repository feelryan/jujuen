# 自動化整合：Hooks 與 CI/CD / Automation Integration: Hooks and CI/CD

## Mental model｜心智模型

### 1. Git 作為事件驅動系統 (Git as an Event-Driven System)
不要只把 Git 當作檔案儲存庫，請將其視為一個會發送訊號的**事件發射器 (Event Emitter)**。
當你執行 `git commit`、`git push` 或 `git merge` 時，Git 內部會觸發一系列的生命週期事件。Hooks 就是監聽這些事件的攔截器 (Interceptors)。

*   **Local Hooks (客戶端)**：發生在你的機器上。它們是第一道防線，負責「快速檢查」與「格式化」。
    *   *Analogy*: 就像機場的登機櫃台檢查，確認你有護照 (Linting passed) 和機票 (Message format correct) 才能進入管制區。
*   **Server-side Hooks / CI (伺服器端)**：發生在遠端倉庫或 CI Server 上。它們是最終防線，負責「完整測試」與「整合建置」。
    *   *Analogy*: 就像海關與安檢，進行徹底的全身掃描 (Unit Tests, E2E Tests, Security Scan)。

### 2. 左移測試 (Shift Left Testing)
自動化的核心哲學是 **"Fail Fast"**。
如果在 CI 階段才發現簡單的語法錯誤 (Syntax Error) 或格式問題，會浪費數分鐘的排隊與執行時間。透過 Pre-commit hooks，我們將錯誤發現的時間點盡可能向左（開發早期）移動，實現秒級的反饋迴圈。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 僅檢查暫存區檔案 (Lint Staged Files Only)
這是最關鍵的效能模式。不要在 `pre-commit` 時檢查整個專案的所有檔案。
*   **Why**: 隨著專案變大，全量檢查會導致 commit 耗時過長，開發者會因此習慣使用 `--no-verify` 跳過檢查。
*   **How**: 使用 `lint-staged` (Node.js 生態) 或 `pre-commit` (Python 生態) 框架，只針對 `git diff --cached` (即將被 commit 的檔案) 執行 Linter 和 Formatter。

### 2. 規範化提交訊息 (Enforce Conventional Commits)
使用 `commit-msg` hook 來檢查提交訊息格式。
*   **Standard**: 採用 [Conventional Commits](https://www.conventionalcommits.org/) (e.g., `feat: add login`, `fix: handle null pointer`).
*   **Benefit**: 這不僅是為了好看，而是為了後續 CI/CD 的自動化——自動生成 Changelog、自動決定 Semantic Versioning (Major/Minor/Patch) 的版號升級。

### 3. 共享 Hooks 配置 (Shared Configuration as Code)
不要讓開發者手動將 script 複製到 `.git/hooks/` 目錄下（因為該目錄不會被版控）。
*   **Pattern**: 使用工具將 Hooks 定義在版控檔案中 (如 `.pre-commit-config.yaml` 或 `package.json`)，並在 `npm install` 或專案初始化時自動安裝到 `.git/hooks/`。
*   **Tools**: `Husky` (JS/TS), `pre-commit` (Multi-language), `Lefthook` (Go/Polyglot).

### 4. CI 中的 Git 最佳化 (Git Optimization in CI)
在 CI Pipeline 中拉取程式碼時，應注意效率與完整性的平衡。
*   **Shallow Clone**: 對於一般的 Build/Test job，使用 `git fetch --depth=1` 以節省時間與頻寬。
*   **Full History**: 對於需要分析歷史 (如 `git blame` 檢查、自動生成 Changelog) 的 job，則需要完整的歷史記錄或特定的 depth。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 在 Pre-commit 中執行繁重測試 (Heavy Tests in Pre-commit)
*   **Anti-pattern**: 在 `pre-commit` hook 中執行完整的單元測試或整合測試。
*   **Consequence**: Commit 過程超過 5-10 秒，開發者體驗極差，最終導致團隊全面棄用 Hooks。
*   **Solution**: Local Hooks 只做 Linting、Formatting 和極輕量的 Static Analysis。重型測試留給 CI。

### 2. 本地獨有的 Hook 邏輯 (Local-only Logic)
*   **Anti-pattern**: 依賴本地 Hook 修改程式碼（如自動 fix lint error），但在 CI 上沒有對應的檢查。
*   **Risk**: 如果開發者使用 `git commit --no-verify` 或使用 GUI 工具跳過了 Hook，爛程式碼就會溜進 Main branch。
*   **Solution**: **Defense in Depth (縱深防禦)**。Local Hook 是為了方便開發者，CI 才是唯一的真理標準。CI 必須再次執行 Lint Check (且設為 fail on error)。

### 3. CI 迴圈地獄 (The CI Loop of Death)
*   **Anti-pattern**: CI Pipeline 檢測到格式錯誤 -> 自動修正 -> `git commit` & `git push` -> 再次觸發 CI -> 無限循環。
*   **Solution**:
    1.  在 CI 推送的 commit message 中加入 `[skip ci]` 或 `[ci skip]`。
    2.  更好的是：CI 僅負責檢查並失敗 (Fail)，要求開發者在本地修正後再推。

### 4. 忽略跨平台相容性 (Ignoring Cross-platform Compatibility)
*   **Pitfall**: 寫了一個 Shell script hook，在 macOS/Linux 上跑得很順，但在 Windows (PowerShell/CMD) 上直接炸開。
*   **Solution**: 盡量使用跨平台的 Hook 執行器 (如 Husky, pre-commit)，或確保 script 使用通用的 `#!/bin/sh` 且避免依賴特定 OS 的指令。

---

## Checklists & workflows｜檢查清單與流程

### Workflow: The Automated Quality Gate
1.  **Stage**: 開發者執行 `git add`。
2.  **Pre-commit**: 觸發 Hook -> 執行 `lint-staged` -> 自動格式化 (Prettier) -> 靜態檢查 (ESLint/Ruff)。
    *   *Pass*: 進入下一步。
    *   *Fail*: 阻擋 Commit，顯示錯誤訊息。
3.  **Commit Msg**: 觸發 `commit-msg` Hook -> 檢查訊息格式 (Conventional Commits)。
4.  **Push**: 開發者執行 `git push` (可選：觸發 `pre-push` 執行輕量單元測試)。
5.  **CI Pipeline**: 伺服器接收 -> Build -> Full Test Suite -> Security Scan。

### Decision Checklist: 設定 Hooks 前的自我檢視

- [ ] **執行時間檢查**：這個 Hook 的執行時間是否控制在 3-5 秒內？
- [ ] **範圍檢查**：是否只針對 `staged` 的檔案執行，而不是全專案掃描？
- [ ] **冪等性 (Idempotency)**：重複執行 Hook 是否會產生相同的結果（不會因為重複執行而把程式碼改壞）？
- [ ] **環境一致性**：新加入的成員執行 `npm install` (或對應指令) 後，Hooks 是否會自動設定完成？
- [ ] **逃生門意識**：團隊成員是否知道在緊急修復 (Hotfix) 時如何使用 `--no-verify`？
- [ ] **CI 兜底**：本地 Hook 檢查的項目，CI 上是否也有對應的檢查步驟？

---

## Real-world examples｜實戰案例

### 1. JavaScript/TypeScript 專案標準配置 (Husky + lint-staged)

這是目前前端與 Node.js 專案最標準的配置。

**`.husky/pre-commit`** (Shell script):
```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

npx lint-staged
```

**`package.json`**:
```json
{
  "scripts": {
    "prepare": "husky install"
  },
  "lint-staged": {
    "**/*.{js,jsx,ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "**/*.{json,md,yml}": [
      "prettier --write"
    ]
  }
}
```
*解說：當開發者 commit 時，系統會自動修復 ESLint 錯誤並美化格式，然後將修改後的檔案自動 add 回去，確保 commit 進去的程式碼是乾淨的。*

### 2. Python/Polyglot 專案配置 (pre-commit framework)

適用於 Python、Terraform、Go 等多語言混合專案。

**`.pre-commit-config.yaml`**:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files # 防止意外 commit 大檔案

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.0.272
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
```
*解說：這會自動幫你移除行尾空白、確保檔案結尾有換行，並使用 Ruff 進行極速的 Python linting。*

### 3. GitHub Actions CI 中的 Git 操作

在 CI 中自動發布版本並推回 Tag。

**`.github/workflows/release.yml`**:
```yaml
steps:
  - name: Checkout
    uses: actions/checkout@v3
    with:
      fetch-depth: 0 # 重要：為了計算版本號，需要完整歷史
      token: ${{ secrets.GH_TOKEN }} # 需要有寫入權限的 Token

  - name: Semantic Release
    run: npx semantic-release
    env:
      GITHUB_TOKEN: ${{ secrets.GH_TOKEN }}
```

### 4. 防止意外 Push 到 Main 分支 (Pre-push Hook)

雖然應該在 Server 端設定 Branch Protection Rules，但在本地端多一層保護也是好的。

**`.husky/pre-push`**:
```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

branch="$(git symbolic-ref HEAD 2>/dev/null)"

if [ "$branch" = "refs/heads/main" ]; then
  echo "🛑 Stop! Direct push to main is not allowed."
  echo "👉 Please create a PR."
  exit 1
fi
```