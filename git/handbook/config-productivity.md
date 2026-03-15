# 高效環境配置與 Alias 技巧 / Configuration and Productivity Aliases

## Mental model｜心智模型

要掌握 Git 的配置，必須建立 **「層級化覆蓋（Cascading Overrides）」** 的心智模型。Git 的設定並非扁平的，而是像 CSS 或環境變數一樣具有優先級。

1.  **System (`--system`)**: 機器層級，影響這台電腦上所有使用者（極少修改）。
2.  **Global (`--global`)**: 使用者層級，這是你的「個人背包」，裝著你習慣的編輯器、Alias 和預設行為。
3.  **Local (`--local`)**: 專案層級（存於 `.git/config`），這是該專案的「特定規則」，優先級最高。

**Alias（別名）** 的本質則是 **「認知負載的壓縮（Cognitive Compression）」**。它不僅僅是為了少打幾個字，而是將一連串複雜的參數（例如畫出漂亮的 commit graph）封裝成一個語義化的指令，讓你專注於「我要看線圖」這個意圖，而不是回憶參數。

> **Key Takeaway:** Always configure defaults globally, but override specific project needs locally. Treat aliases as your personal command-line interface design.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 基礎配置黃金標準 (The Golden Standard of Basic Config)
在任何新環境中，這是你應該優先執行的設定，確保操作的一致性與安全性。

```bash
# 設定身份
git config --global user.name "Your Name"
git config --global user.email "you@example.com"

# 現代化預設值
git config --global init.defaultBranch main        # 避免 master/main 混亂
git config --global pull.rebase true               # 保持歷史線乾淨，避免無意義的 merge commit
git config --global core.editor "code --wait"      # 使用 VS Code 作為編輯器 (或 vim/nano)
git config --global help.autocorrect 1             # 自動修正打錯的指令 (1 = 0.1秒後執行)
```

### 2. 實戰 Alias 設計模式 (Productivity Aliases)
不要只建立 `co` = `checkout` 這種簡單縮寫，應針對 **「高頻查詢」** 與 **「安全操作」** 設計 Alias。

*   **視覺化日誌 (The Visualizer):**
    ```bash
    # 顯示漂亮的彩色分支圖，包含 hash、時間、作者與訊息
    git config --global alias.lg "log --graph --abbrev-commit --decorate --format=format:'%C(bold blue)%h%C(reset) - %C(bold green)(%ar)%C(reset) %C(white)%s%C(reset) %C(dim white)- %an%C(reset)%C(auto)%d%C(reset)' --all"
    ```
*   **狀態快照 (The Quick Status):**
    ```bash
    # 極簡狀態顯示，去除廢話
    git config --global alias.s "status -sb"
    ```
*   **安全防護 (The Safety Net):**
    ```bash
    # 避免誤用 git push -f，強制使用 lease 模式（若遠端有新變更則失敗）
    git config --global alias.pf "push --force-with-lease"
    ```
*   **清理工具 (The Cleaner):**
    ```bash
    # 刪除所有已經合併到 master/main 的本地分支
    git config --global alias.trim "!git branch --merged | grep -v '*' | xargs -n 1 git branch -d"
    ```

### 3. 使用 `includeIf` 管理多重身份 (Context-Aware Configuration)
資深工程師常同時處理「公司專案」與「開源/個人專案」。與其每次手動切換 `user.email`，不如使用 `includeIf` 自動切換。

在 `~/.gitconfig` (Global) 中：
```ini
[user]
    name = Default Name
    email = personal@gmail.com

[includeIf "gitdir:~/work/"]
    path = ~/work/.gitconfig
```
在 `~/work/.gitconfig` 中：
```ini
[user]
    email = professional@company.com
```
這樣只要你在 `~/work/` 目錄下操作，Git 會自動使用公司 Email。

### 4. 提升 Diff 可讀性 (Enhanced Diff Tooling)
原生的 Git diff 閱讀困難。建議整合 `delta` 或 `diff-so-fancy`。
*   **Pattern:** 安裝 `delta` (Rust 編寫的語法高亮工具) 並配置為 default pager。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 跨平台換行符號地獄 (The CRLF/LF Hell)
*   **Anti-pattern:** 團隊成員混合使用 Windows 和 macOS/Linux，且未設定 `core.autocrlf`，導致 commit 充滿了僅僅是換行符號的變更。
*   **Solution:**
    *   Windows: `git config --global core.autocrlf true` (Checkout Windows style, Commit Unix style)
    *   Mac/Linux: `git config --global core.autocrlf input` (Checkout as-is, Commit Unix style)
    *   **Best Practice:** 在專案根目錄加入 `.gitattributes` 強制定義：`* text=auto eol=lf`。

### 2. 過度依賴複雜 Alias (Over-Aliasing)
*   **Pitfall:** 定義了像 `git deploy-prod` 這樣隱藏了 10 個步驟的 alias。
*   **Consequence:** 當 alias 失效或換了機器，你完全忘記原本的指令流程；且新人無法透過閱讀指令學習。
*   **Correction:** 複雜流程應寫成 script (e.g., `./scripts/deploy.sh`) 並納入版控，而非藏在個人的 git config 中。

### 3. 將敏感資訊寫入 Config (Secrets in Config)
*   **Anti-pattern:** 將 Access Token 或密碼直接寫在 URL 中，如 `git remote add origin https://user:password@github.com...`。
*   **Risk:** `git remote -v` 或不小心分享 dotfiles 時會洩漏憑證。
*   **Solution:** 使用 Git Credential Helper (`git config --global credential.helper store` 或系統原生的 keychain)。

---

## Checklists & workflows｜檢查清單與流程

### 新環境/新機器設置清單 (New Environment Setup)
- [ ] **Identity Check**: 確認 `user.name` 與 `user.email` 正確。
- [ ] **Editor Setup**: 確認 `core.editor` 已設為你熟悉的編輯器（避免卡在 Vim 無法退出）。
- [ ] **Line Endings**: 根據作業系統設定 `core.autocrlf`。
- [ ] **Credential Helper**: 確保不用每次 push 都輸入密碼。
- [ ] **Aliases Import**: 匯入常用的 aliases（建議將 dotfiles 託管於 GitHub）。

### 專案層級配置檢查 (Project-Level Config Audit)
- [ ] **User Override**: 是否需要針對此專案使用不同的 Email？(檢查 `.git/config`)
- [ ] **Ignored Files**: `.gitignore` 是否運作正常？(使用 `git check-ignore -v <file>` 測試)
- [ ] **Hooks Path**: 專案是否使用 Husky 或自定義 hooks？(檢查 `core.hooksPath`)

---

## Real-world examples｜實戰案例

### 案例一：解決「為什麼我的 Diff 這麼難看？」
**情境**：你在 Code Review 時，發現 Git 的 diff 輸出一片紅綠，難以辨識具體改了哪個單字，且縮排混亂。

**解決方案**：引入 `delta` 並配置 Git config。

```ini
# ~/.gitconfig
[core]
    pager = delta

[interactive]
    diffFilter = delta --color-only

[delta]
    navigate = true    # 使用 n/N 在 diff 區塊間跳轉
    line-numbers = true
    side-by-side = true # 左右對照模式，類似 GitHub PR 介面
```
**結果**：終端機內的 Diff 變成了語法高亮、左右對照的介面，大幅提升 Review 效率。

### 案例二：緊急修復時的「時光機」Alias
**情境**：你正在 feature branch 上寫了一堆爛 code，突然需要切回 main 修復一個緊急 bug，但你不想 commit 現在的髒 code，也不想手動 stash。

**Alias 設計**：
```bash
# Save current work to a temp branch and switch to main
git config --global alias.save-switch "!f() { git checkout -b temp-backup-$(date +%s); git commit -am 'WIP backup'; git checkout main; }; f"
```
**使用**：執行 `git save-switch`。
**效果**：自動開一個帶時間戳的備份分支並 commit 所有變更，然後切回 main。修復完後，你可以決定要 merge 那個備份分支還是 cherry-pick。

### 案例三：Git Blame 的忽略干擾
**情境**：專案剛進行了一次全域的 Prettier/Eslint 格式化。現在使用 `git blame` 查看某行程式碼是誰寫的時，全部顯示為 "Format Fix" 的那次 commit，失去了歷史意義。

**配置技巧**：
1. 建立一個紀錄格式化 commit hash 的檔案 `.git-blame-ignore-revs`。
2. 設定 Git 忽略這些 commits：
   ```bash
   git config --local blame.ignoreRevsFile .git-blame-ignore-revs
   ```
**結果**：`git blame` 會自動跳過格式化 commit，顯示該行程式碼「真正的」修改者與時間。