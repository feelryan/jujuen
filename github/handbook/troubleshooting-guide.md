# 實戰排錯流程與 Checklist / Practical Troubleshooting Guide & Checklist

在 GitHub 生態系中，問題通常發生在三個層面：**Git 本地操作（Local）**、**權限與身份驗證（Auth & Access）**、以及 **自動化與整合（Automation & Integration）**。本章節提供針對這三個層面的系統化排查模型與實戰清單。

## Mental model｜心智模型

要有效排錯，必須建立「分層隔離（Layered Isolation）」的心智模型。當錯誤發生時，請先判斷問題屬於哪一層：

1.  **The State Layer (Git Data)**:
    *   **核心問題**：檔案內容衝突、History 混亂、Reference 遺失。
    *   **思考方式**：Git 是一個 Directed Acyclic Graph (DAG)。所有的衝突本質上都是 DAG 的分岔點無法自動合併。不要把衝突視為「錯誤」，而是「需要人工決策的並行修改」。

2.  **The Gatekeeper Layer (Auth & Permissions)**:
    *   **核心問題**：Permission denied (publickey)、403 Forbidden、SAML SSO 限制。
    *   **思考方式**：GitHub 的權限是「交集」運算。
    *   `最終權限 = (個人帳號權限 + Team 權限) ∩ (Organization SAML 狀態) ∩ (Token Scope)`。
    *   很多時候你「有權限」，但你的「鑰匙（Token/Key）」沒有被授權通過 SSO 閘道。

3.  **The Event Layer (Actions & Webhooks)**:
    *   **核心問題**：CI Pipeline 失敗、Webhook 沒觸發或 Timeout。
    *   **思考方式**：這是一個非同步的事件驅動系統。
    *   **環境差異**：CI Runner 的環境（Environment）≠ 本地開發環境。90% 的 CI 錯誤來自於「隱藏的依賴」或「環境變數缺失」。
    *   **網路邊界**：Webhook 失敗通常是因為防火牆（Firewall）或公開網路不可達（Not Reachable）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 處理複雜 Merge Conflicts (The "Rebase First" Strategy)
在大型協作中，避免直接 `git merge main` 造成混亂的 merge commit。
*   **Pattern**: 使用 `git pull --rebase origin main` 保持歷史乾淨。
*   **Tooling**: 設定 VS Code 或 IntelliJ 作為 `mergetool`。不要嘗試在純文字介面解決複雜衝突。
*   **Strategy**: 如果衝突過於複雜，開啟一個新的分支，將你的更動 cherry-pick 過去，這通常比解衝突更快。

### 2. CI/CD 排錯 (Debug via Context)
不要盲目猜測 CI 失敗原因。
*   **Enable Debug Logging**: 在 Repository Secret 中設定 `ACTIONS_STEP_DEBUG = true`，這會讓 Runner 輸出詳細的執行日誌。
*   **Dump Context**: 在 Workflow 失敗步驟前，增加一個步驟印出 `env` 和 `github` context，檢查變數是否如預期。
*   **Interactive Debugging**: 使用如 `mxschmitt/action-tmate` 這樣的 Action，在 CI 失敗時開啟 SSH session 讓你連進去 Runner 檢查環境。

### 3. 權限驗證 (The "SSH -T" Check)
*   **Pattern**: 遇到 Permission denied，第一步永遠是執行 `ssh -T git@github.com`。這會告訴你 GitHub 認得你是誰（User Identity），以及你是否成功連線。
*   **Scope Check**: 對於 PAT (Personal Access Token) 錯誤，檢查 Token 的 Scopes 是否包含 `repo` 或 `workflow`。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. "Commit Debugging" in CI
*   **Anti-pattern**: 修改一行 code -> Commit "fix ci" -> Push -> 等 5 分鐘 -> 失敗 -> 重複。
*   **Consequence**: Git log 充滿垃圾 commits，且效率極低。
*   **Solution**: 使用本地 Runner 工具（如 `nektos/act`）在本地模擬 GitHub Actions 執行，或使用上述的 Interactive Debugging。

### 2. 忽略 SAML SSO 授權
*   **Anti-pattern**: 加入了公司 Organization，上傳了 SSH Key，但 Clone 私有庫時依然報錯 `Permission denied (publickey)`。
*   **Pitfall**: 企業版 GitHub 通常強制 SAML SSO。你的 SSH Key 或 PAT 必須在 Settings 中點擊 "Configure SSO" 並授權給該 Organization，否則該 Key 對該 Org 無效。

### 3. 暴力解衝突 (The "Theirs" Trap)
*   **Anti-pattern**: 遇到衝突直接使用 `git checkout --theirs .` 或 `git checkout --ours .` 而不檢查內容。
*   **Consequence**: 可能意外覆蓋掉同事的重要邏輯或設定檔（如 `package.json`），導致程式邏輯壞掉但 Git 認為已解決。

### 4. Webhook 本地測試困難
*   **Anti-pattern**: 為了測試 Webhook，不斷部署到 Staging server。
*   **Solution**: 使用 GitHub CLI (`gh webhook forward`) 或 `ngrok` 將 Webhook 轉發到 `localhost` 進行即時除錯。

---

## Checklists & workflows｜檢查清單與流程

### 🛠 Workflow 1: Permission Denied / Auth Issues 排查
當你無法 Clone、Push 或 Pull 時：

- [ ] **Step 1: 身份確認**
    - 執行 `ssh -T git@github.com`。
    - *Pass*: 看到 "Hi <username>! You've successfully authenticated..."
    - *Fail*: 看到 "Permission denied (publickey)" -> 檢查本地 SSH Agent (`ssh-add -l`) 或 Key 是否已上傳 GitHub。
- [ ] **Step 2: 權限範圍 (Scopes & SSO)**
    - 如果是 HTTPS/PAT：Token 是否過期？是否勾選了 `repo` scope？
    - 如果是 Organization Repo：進入 GitHub Settings > SSH and GPG keys > 該 Key 旁是否有 "SSO" 按鈕？點擊並 Authorize。
- [ ] **Step 3: 倉庫權限**
    - 瀏覽器開啟該 Repo URL。看得到嗎？
    - 如果看不到（404），你可能被移出 Team，或 Repo 被刪除/轉移。
- [ ] **Step 4: 協議檢查**
    - 檢查 `.git/config` 中的 remote url。
    - 推薦使用 SSH (`git@github.com:...`) 而非 HTTPS，除非受限於公司防火牆。

### 🐛 Workflow 2: CI/CD Pipeline 莫名失敗排查
當 Local 測試通過，但 GitHub Actions 失敗時：

- [ ] **Step 1: 環境差異檢查**
    - Node/Python/Go 版本是否與 Local 一致？(檢查 `actions/setup-node` 設定)
    - 依賴鎖定檔 (`package-lock.json`, `go.sum`) 是否已提交且一致？
- [ ] **Step 2: Secrets 與變數**
    - 該 Secret 是否存在於正確的環境（Repository secrets vs Environment secrets）？
    - PR 來自 Fork 嗎？(Fork 的 PR 預設讀不到 Secrets，這是安全機制)。
- [ ] **Step 3: 路徑與權限**
    - Script 是否有執行權限 (`chmod +x`)？
    - 是否使用了絕對路徑？(CI Runner 的路徑結構可能不同，請用 `$GITHUB_WORKSPACE`)。
- [ ] **Step 4: 資源限制**
    - 是否遇到 API Rate Limit？
    - 是否超過 Runner 的記憶體或磁碟限制？(查看 Job Summary)。

### 🔀 Workflow 3: 解決頑強的 Merge Conflicts
當 GitHub Web UI 顯示 "This branch has conflicts that must be resolved"：

- [ ] **Step 1: 本地同步**
    - `git checkout main` -> `git pull` (確保 main 是最新的)。
    - `git checkout feature-branch`。
- [ ] **Step 2: 選擇策略**
    - 策略 A (標準): `git merge main`。
    - 策略 B (乾淨歷史): `git rebase main` (推薦，但需小心)。
- [ ] **Step 3: 解決衝突**
    - 打開編輯器，搜尋 `<<<<<<<`。
    - 針對邏輯衝突：與同事溝通。
    - 針對鎖定檔 (`package-lock.json`)：通常直接刪除該檔，解決 `package.json` 衝突後重新 install 生成。
- [ ] **Step 4: 驗證**
    - `npm test` / `make test` 確保解完衝突後程式仍能執行。
- [ ] **Step 5: 完成**
    - Merge: `git add .` -> `git commit` -> `git push`。
    - Rebase: `git add .` -> `git rebase --continue` -> `git push --force-with-lease`。

---

## Real-world examples｜實戰案例

### Case 1: The "Invisible" Secret (CI/CD)
**情境**：開發者在 GitHub Actions 中使用 `${{ secrets.API_KEY }}`，但程式一直報錯 "API Key is empty"。
**排查過程**：
1.  檢查 Settings > Secrets，發現 Key 確實存在。
2.  **關鍵點**：Workflow 是由 `dependabot` 或 Fork 的 PR 觸發的。
3.  **原因**：GitHub 安全機制預設禁止 Fork 的 PR 讀取 Secrets，防止惡意程式碼竊取金鑰。
4.  **解法**：使用 `pull_request_target` 事件（需極度小心安全性），或僅在 Owner 的分支上執行敏感測試。

### Case 2: The SAML SSO Block (Permission)
**情境**：新進資深工程師，剛加入公司 Organization，可以瀏覽 Repo 網頁，但 `git clone` 報錯 `Permission denied (publickey)`。
**排查過程**：
1.  工程師執行 `ssh -T git@github.com`，顯示 "Hi [User]!..." (驗證通過)。
2.  工程師確認已被加入 Team。
3.  **關鍵點**：公司開啟了 SAML SSO Enforcement。
4.  **解法**：工程師前往 User Settings > SSH keys，發現該 Key 旁邊顯示 "SSO not authorized"。點擊 "Authorize" 並通過公司 IDP 登入後，Clone 成功。

### Case 3: The "Ghost" Webhook (Integration)
**情境**：Jenkins 設定了 GitHub Webhook，但 Push code 後 Jenkins 沒反應。
**排查過程**：
1.  進入 GitHub Repo Settings > Webhooks。
2.  看到最近的 Delivery 旁邊有紅色驚嘆號。點開看 Response：`Timed out`。
3.  **關鍵點**：Jenkins 位於公司內網（Intranet），沒有公開 IP。
4.  **解法**：IT 部門需設定防火牆白名單（允許 GitHub IP Range），或使用 `Smee.io` / `ngrok` 類型的 Proxy 服務轉發 Payload。