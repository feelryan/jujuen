# 安全性與團隊協作規範 / Security and Collaboration Governance

在軟體工程中，Git 不僅僅是程式碼的時光機，它更是一份**具有法律效力的合約（Legal Contract）**與**團隊溝通的公共帳本（Public Ledger）**。本章節將探討如何確保這份帳本的真實性（Security）、整潔度（Hygiene）與可讀性（Governance）。

## Mental model｜心智模型

要掌握 Git 的安全性與協作規範，你需要建立以下兩個核心觀念：

### 1. 信任鏈（Chain of Trust）
Git 的分散式特性意味著任何人都可以設定 `user.name` 為 "Linus Torvalds" 並提交程式碼。
*   **身分驗證（Identity Verification）**：就像銀行支票需要簽名一樣，Commit 簽章（Signing）是證明「這段程式碼真的是由持有私鑰的人（你）所寫」的唯一方式。
*   **不可否認性（Non-repudiation）**：當 Commit 被簽署後，作者無法否認該提交，這對於稽核與溯源至關重要。

### 2. 污染隔離區（Contamination Containment）
Git 倉庫（Repository）應該被視為一個「無塵室」。
*   **敏感資訊是輻射汙染**：一旦 API Key 或密碼進入 Commit History（即使後來被刪除），整個倉庫就被「汙染」了。因為 Git 的歷史是永久儲存的，唯一的解法是重寫歷史（極高成本）並立即作廢該密鑰。
*   **雜訊過濾**：`.gitignore` 是你的空氣過濾網，它的職責是區分「原始碼（Source）」與「生成物（Artifacts）」以及「環境配置（Local Config）」。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 採用 SSH 簽署 Commit (Modern Commit Signing)
過去 GPG 設定繁瑣，現在 Git 支援使用 SSH Key 進行簽章，這是目前最推薦的實務。

*   **Why**: 復用現有的 SSH Key（用於 GitHub/GitLab 認證），設定簡單，且同樣能獲得 "Verified" 標章。
*   **How**:
    ```bash
    git config --global gpg.format ssh
    git config --global user.signingkey ~/.ssh/id_ed25519.pub
    git config --global commit.gpgsign true
    ```

### 2. 多層級 `.gitignore` 策略 (Tiered Ignore Strategy)
不要把所有規則都塞在專案的 `.gitignore`。

*   **Global (`~/.gitignore_global`)**: 放與**開發者個人工具**相關的檔案（如 `.DS_Store`, `Thumbs.db`, `.vscode/`, `.idea/`）。這是你的個人衛生習慣，不應污染團隊專案。
*   **Repository (`.gitignore`)**: 放與**專案建置**相關的檔案（如 `node_modules/`, `dist/`, `*.log`, `.env`）。這是團隊共識。
*   **Explicit Whitelisting (白名單模式)**: 對於配置檔較多的專案，採用「先忽略所有，再允許特定」的模式更安全：
    ```gitignore
    # Ignore everything
    *
    # Re-include specific folders
    !src/
    !package.json
    ```

### 3. 強制性 Conventional Commits
團隊應採用 [Conventional Commits](https://www.conventionalcommits.org/) 規範，這不僅是為了好看，更是為了**自動化**。

*   **Format**: `<type>(<scope>): <subject>`
*   **Automation**: 透過標準化格式，CI/CD 可以自動生成 Changelog 並決定 Semantic Versioning 的版號（例如 `fix` 觸發 patch，`feat` 觸發 minor）。

### 4. Pre-commit Hooks 作為最後防線
依賴人類記憶是不靠譜的，使用工具（如 `husky` + `lint-staged`）在 commit 發生前攔截。

*   **Secret Scanning**: 整合 `gitleaks` 或 `talisman` 阻擋疑似密鑰的字串提交。
*   **Linting**: 確保提交的程式碼符合風格規範。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 鴕鳥心態的資安處理 (The Ostrich Algorithm)
*   **Bad**: 不小心 commit 了 AWS Key，心想「我趕快刪掉再 push 一個新的 commit 就好了」。
*   **Reality**: 駭客機器人會掃描所有公開（甚至私有）Repo 的**歷史紀錄**。只要 key 曾經存在於任一 commit 中，它就已經外洩。
*   **Fix**: 必須立即作廢（Rotate）該 Key，並使用 `git filter-repo` 或 BFG 清洗歷史（如果專案還未被廣泛 clone）。

### 2. 混合身分的混亂 (Identity Crisis)
*   **Bad**: 在公司專案使用私人 Email (`cute_boy_99@gmail.com`)，或在開源專案暴露公司內部 Email。
*   **Fix**: 使用 Git 的 Conditional Configuration 自動切換身分。
    ```gitconfig
    # ~/.gitconfig
    [includeIf "gitdir:~/work/"]
        path = .gitconfig-work
    [includeIf "gitdir:~/personal/"]
        path = .gitconfig-personal
    ```

### 3. 無意義的 Commit Message (The "WIP" Curse)
*   **Bad**: 連續提交 `fix`, `update`, `wip`, `temp`, `oops`。
*   **Consequence**: Code Review 變得不可能，`git blame` 失去除錯價值，無法自動生成 Changelog。

### 4. 將 `.env` 加入版控
*   **Bad**: 為了方便隊友設定環境，把含有真實密碼的 `.env` 檔案 commit 上去。
*   **Fix**: Commit `.env.example` (僅含 key 名稱與假資料)，真實 `.env` 永遠列入 `.gitignore`。

---

## Checklists & workflows｜檢查清單與流程

### Setup Checklist (Onboarding)
- [ ] **設定全域忽略檔**：建立 `~/.gitignore_global` 並加入 OS/IDE 產生的垃圾檔。
- [ ] **設定 SSH 簽章**：配置 `user.signingkey` 並在 GitHub/GitLab 上傳公鑰以啟用 Verified 標章。
- [ ] **設定身分隔離**：確認 `user.email` 在工作目錄與個人目錄正確切換。

### Pre-Commit Checklist (Daily)
- [ ] **檢查暫存區 (Staging Area)**：使用 `git diff --cached` 快速瀏覽即將提交的變更，確認沒有誤加入的設定檔或密鑰。
- [ ] **撰寫規範訊息**：訊息是否符合 `type: description` 格式？是否解釋了 "Why" 而不僅是 "What"？
- [ ] **原子化提交 (Atomic Commits)**：這個 commit 是否只做了一件事？如果 CI 失敗，是否容易 revert？

### Emergency Workflow: Secret Leakage (緊急應變)
當發現敏感資訊已 push 到遠端：
1.  **立刻作廢 (Revoke)** 該憑證/密鑰（这是最重要的一步）。
2.  通知團隊暫停 Pull/Push。
3.  使用 `git filter-repo` 移除歷史中的檔案：
    ```bash
    pip install git-filter-repo
    git filter-repo --path path/to/secret_file --invert-paths
    ```
4.  強制推送：`git push origin --force --all`。
5.  通知團隊重新 clone 或重置本地分支。

---

## Real-world examples｜實戰案例

### 1. 團隊 Commit Message 規範範本
這是一個真實團隊在 `CONTRIBUTING.md` 中定義的規範，結合了 Emoji 與 Conventional Commits 以提升可讀性：

| Type | Emoji | Description | Example |
| :--- | :---: | :--- | :--- |
| `feat` | ✨ | 新增功能 | `feat(auth): add google sso login support` |
| `fix` | 🐛 | 修復 Bug | `fix(cart): resolve calculation error on discount` |
| `docs` | 📝 | 文件變更 | `docs: update API endpoint usage in README` |
| `chore`| 🔧 | 建置/工具變更 | `chore(deps): upgrade react to v18` |
| `refactor`| ♻️ | 重構 (無功能變更) | `refactor(utils): simplify date parsing logic` |

### 2. 自動化阻擋敏感資訊 (Husky + Gitleaks)
在 `package.json` 專案中設定自動檢查：

```json
// package.json
{
  "scripts": {
    "prepare": "husky install"
  },
  "devDependencies": {
    "husky": "^8.0.0"
  }
}
```

```bash
# .husky/pre-commit
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# 1. Check for secrets (using a dockerized gitleaks or local binary)
gitleaks detect --source . --verbose --redact

# 2. Check commit message format
npx commitlint --edit "$1"
```

### 3. 處理 "被追蹤的" 忽略檔案
**情境**：你把 `config.js` 加入了 `.gitignore`，但每次修改它，Git 還是會顯示變更。
**原因**：該檔案已經被 commit 過了，`.gitignore` 只對「未追蹤（Untracked）」的檔案有效。
**解法**：
```bash
# 1. 從 Git 索引中移除（保留實體檔案）
git rm --cached config.js

# 2. 確保 .gitignore 中有 config.js
echo "config.js" >> .gitignore

# 3. 提交變更
git commit -m "chore: stop tracking config.js"
```