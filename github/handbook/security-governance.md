# 安全性配置與治理機制 / Security Configuration & Governance

在這個章節中，我們將探討如何利用 GitHub 的原生功能來構建「自動化防護網」。安全性不應是開發流程中的阻礙（Blocker），而應該是讓開發者能安心加速的護欄（Guardrails）。我們將重點放在 **供應鏈安全**、**身份驗證現代化** 以及 **程式碼所有權治理**。

In this chapter, we explore how to leverage GitHub's native features to build an "automated safety net." Security should not be a blocker in the development process, but rather guardrails that allow developers to accelerate with confidence. We focus on **Supply Chain Security**, **Modern Authentication**, and **Code Ownership Governance**.

---

## Mental model｜心智模型

### 1. 縱深防禦與左移 (Defense in Depth & Shift Left)
不要依賴單一關卡（例如上線前的資安掃描）。GitHub 的治理模型應建立在 **"Shift Left"** 的概念上：
- **Pre-commit**: 防止 Secret 被寫入（IDE plugins, pre-commit hooks）。
- **Pull Request**: 自動化依賴掃描（Dependabot）、程式碼掃描（CodeQL）、以及強制的人員審核（CODEOWNERS）。
- **CI/CD**: 使用短效憑證（OIDC）而非長效金鑰。

### 2. 治理即程式碼 (Governance as Code)
將規則寫在 Repo 中，而不是隱藏在 Setting UI 裡。
- `CODEOWNERS` 定義了誰對這段程式碼負責。
- `.github/workflows` 定義了部署權限與流程。
- `dependabot.yml` 定義了依賴更新的策略。
這確保了治理規則本身也是可被版控、可被審查的 (Versioned & Reviewed)。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 採用 OIDC 取代長效型 Secrets (OIDC over Long-lived Secrets)
這是現代 CI/CD 最重要的安全升級。不要再將 AWS `ACCESS_KEY` 或 GCP `JSON Key` 存入 GitHub Secrets。
- **Pattern**: 使用 **OpenID Connect (OIDC)**。
- **Benefit**: GitHub Actions 在執行時會向雲端供應商（AWS/Azure/GCP）換取「短效 Token」。Job 結束後 Token 即失效，無需輪替金鑰 (Key Rotation)，也無洩漏風險。

### 2. 精細化的 CODEOWNERS 策略 (Granular CODEOWNERS)
不要只把 `CODEOWNERS` 當作「誰該被 Tag」的清單，它應該是 **Branch Protection** 的一部分。
- **Pattern**: 設定 Branch Protection Rule 為 `Require review from Code Owners`。
- **Best Practice**:
    - 避免指定個人（`@john`），應指定團隊（`@org/backend-team`），以避免單點依賴 (Bus Factor)。
    - 針對敏感檔案（如 `.github/workflows/`, `terraform/`）設定更嚴格的 Owner（如 `@org/security-team`）。

### 3. 自動化依賴管理與降噪 (Automated Dependency Management & Noise Reduction)
開啟 Dependabot 是第一步，但如何不被通知淹沒才是關鍵。
- **Pattern**: 使用 `groups` 功能將多個更新合併為一個 PR。
- **Pattern**: 針對 Patch/Minor 版本更新設定自動合併（需配合完整的測試覆蓋率）。

### 4. 強制簽署提交 (Enforce Signed Commits)
確保程式碼確實來自聲稱的開發者，防止身分冒用。
- **Pattern**: 開發者設定 GPG 或 SSH 簽署，並在 Branch Protection 中開啟 `Require signed commits`。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Admin Override" Trap (管理員權限濫用)
- **Anti-pattern**: 資深工程師或 Tech Lead 因為擁有 Admin 權限，習慣性勾選 "Bypass branch protections" 來強行 Merge PR。
- **Risk**: 這破壞了治理的可追溯性，且往往是 Incident 發生的主因。Admin 權限應用於緊急修復 (Hotfix)，而非日常流程。

### 2. Secret Sprawl in Test Data (測試資料中的敏感資訊)
- **Anti-pattern**: 認為「這只是測試用的假 API Key」而將其 Commit 進 Repo。
- **Risk**: Secret Scanning 工具通常無法分辨真假 Key，這會導致大量的 False Positives，造成警報疲勞 (Alert Fatigue)，最終導致真正的洩漏被忽略。

### 3. Dependabot Fatigue (Dependabot 疲勞)
- **Anti-pattern**: 開啟了 Dependabot 但沒有配置過濾策略，導致每週一早上有 50 個 Dependency PRs，團隊最終選擇無視或直接關閉功能。
- **Correction**: 設定 `open-pull-requests-limit`，並優先處理 `severity: high` 或 `critical` 的更新。

### 4. Broad Scoped PATs (權限過寬的個人存取權杖)
- **Anti-pattern**: 為了方便，在 CI/CD Script 中使用個人的 Personal Access Token (PAT) 且勾選了 `repo` (Full control) 權限。
- **Risk**: 一旦該 Token 洩漏，攻擊者擁有該使用者的全部權限。應改用 **GitHub App Token** 或 **Fine-grained PATs**。

---

## Checklists & workflows｜檢查清單與流程

### New Repository Security Checklist (新儲存庫安全檢查清單)

- [ ] **Branch Protection**:
    - [ ] Main/Master 分支禁止直接 Push。
    - [ ] 需要至少 1 人 Approve (建議 2 人)。
    - [ ] 開啟 `Require review from Code Owners`。
    - [ ] 開啟 `Require status checks to pass` (CI 必須綠燈)。
- [ ] **Secrets Management**:
    - [ ] 確認沒有 Hardcoded secrets。
    - [ ] 開啟 **Secret scanning** (Settings -> Code security and analysis)。
    - [ ] 設定 **Push protection** (主動阻擋包含 Secret 的 Push)。
- [ ] **Governance**:
    - [ ] 根目錄建立 `CODEOWNERS` 檔案。
    - [ ] 設定 `.github/dependabot.yml`。
- [ ] **CI/CD Identity**:
    - [ ] 移除所有長效 Cloud Credentials。
    - [ ] 配置 OIDC Trust Relationship。

### Secret Leak Response Workflow (金鑰洩漏應變流程)

1.  **Revoke**: 立即在服務供應商端（如 AWS Console）撤銷該金鑰。**不要先刪除 GitHub 上的程式碼**（因為歷史紀錄還在）。
2.  **Rotate**: 產生新金鑰（或切換至 OIDC）。
3.  **Rewrite History (Optional)**: 如果是私有 Repo 且洩漏範圍小，使用 `git filter-repo` 或 BFG Repo-Cleaner 清除歷史紀錄。如果是公開 Repo，假設金鑰已被爬蟲抓取。
4.  **Audit**: 檢查該金鑰在洩漏期間的 Access Logs，確認是否有異常存取。

---

## Real-world examples｜實戰案例

### 1. OIDC Integration (GitHub Actions to AWS)
這是目前連接雲端最推薦的配置，完全不需要管理 Secret。

**AWS Trust Policy (Terraform snippet):**
```hcl
# 允許 GitHub Actions 扮演這個 IAM Role
data "aws_iam_policy_document" "github_oidc" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = ["arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      # 限制只有特定 Repo 和 Branch 能使用此 Role
      values   = ["repo:my-org/my-repo:ref:refs/heads/main"]
    }
  }
}
```

**GitHub Action Workflow:**
```yaml
permissions:
  id-token: write # 必須開啟此權限以獲取 OIDC Token
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/my-github-actions-role
          aws-region: us-east-1
      # 接下來的 AWS CLI 指令會自動擁有該 Role 的權限
      - run: aws s3 ls
```

### 2. Structured CODEOWNERS
展示如何區分架構職責與安全職責。

```text
# .github/CODEOWNERS

# Default: 全體資深工程師兜底
*       @my-org/senior-engineers

# Frontend 團隊負責 UI 相關
/src/ui/          @my-org/frontend-team
/package.json     @my-org/frontend-team

# Backend 團隊負責 API 與資料庫
/src/api/         @my-org/backend-team
/db/migrations/   @my-org/backend-team

# Security/DevOps 團隊嚴格控管基礎設施與 CI 設定
# 這些檔案的變更必須經過 Security Team 核准
/.github/         @my-org/security-team
/terraform/       @my-org/sre-team @my-org/security-team
```

### 3. Dependabot Grouping Strategy
減少 PR 噪音的配置範例。

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    # 將所有 production dependencies 的更新合併為一個 PR
    groups:
      production-dependencies:
        patterns:
          - "*"
        exclude-patterns:
          - "*@dev"
    # 開發依賴另外分組
    groups:
      dev-dependencies:
        patterns:
          - "*@dev"
```