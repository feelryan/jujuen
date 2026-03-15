# Chapter 04: DevSecOps 與供應鏈安全
# Chapter 04: DevSecOps & Supply Chain Security

## 1. 前言與學習目標
## 1. Introduction & Learning Objectives

在現代軟體工程中，安全性不再是資安團隊在部署前才介入的「守門員」，而是滲透到開發生命週期每一環節的「責任」。對於資深工程師而言，掌握 GitHub 的 DevSecOps 工具鏈不僅是為了修補漏洞，更是為了建立一套自動化、可審計且低摩擦的合規流程。

In modern software engineering, security is no longer a "gatekeeper" that steps in only before deployment; it is a shared responsibility embedded in every stage of the development lifecycle. For Senior Engineers, mastering GitHub's DevSecOps toolchain is not just about patching vulnerabilities, but about establishing an automated, auditable, and low-friction compliance workflow.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **實作無金鑰認證（Keyless Authentication）：** 利用 OpenID Connect (OIDC) 取代長效的 Cloud Credentials，強化 CI/CD 對接 AWS/GCP/Azure 的安全性。
    **Implement Keyless Authentication:** Use OpenID Connect (OIDC) to replace long-lived Cloud Credentials, hardening the security of CI/CD pipelines connecting to AWS/GCP/Azure.
2.  **自動化依賴管理與漏洞修復：** 配置 Dependabot 進行依賴更新與安全警示，並理解如何處理傳遞性依賴（Transitive Dependencies）的風險。
    **Automate Dependency Management & Remediation:** Configure Dependabot for dependency updates and security alerts, and understand how to mitigate risks from transitive dependencies.
3.  **整合靜態應用程式安全測試（SAST）：** 部署 CodeQL 於 GitHub Actions 中，將程式碼視為數據進行查詢，以在 Code Review 階段攔截邏輯漏洞。
    **Integrate Static Application Security Testing (SAST):** Deploy CodeQL within GitHub Actions to treat code as data, intercepting logical vulnerabilities during the Code Review phase.
4.  **防禦憑證洩漏（Secret Leaks）：** 啟用 Secret Scanning 與 Push Protection，防止 API Key 與 Token 進入版本控制系統。
    **Prevent Secret Leaks:** Enable Secret Scanning and Push Protection to stop API Keys and Tokens from entering the version control system.

---

## 2. 核心觀念與心智模型
## 2. Core Concepts & Mental Model

### 2.1 供應鏈安全：從「鎖門」到「檢查建材」
### 2.1 Supply Chain Security: From "Locking the Door" to "Inspecting Materials"

傳統資安專注於防火牆與權限控管（鎖門），而供應鏈安全關注的是你的軟體是由什麼組成的（建材）。現代應用程式 80-90% 的程式碼來自開源依賴包。
Traditional security focuses on firewalls and access control (locking the door), whereas supply chain security focuses on what your software is composed of (the materials). In modern applications, 80-90% of the code comes from open-source dependencies.

*   **心智模型：** 把你的專案想像成一家餐廳。
    *   **App Sec:** 確保廚房乾淨、沒有老鼠（CodeQL, Secret Scanning）。
    *   **Supply Chain Sec:** 確保供應商送來的食材沒有過期或被下毒（Dependabot, Dependency Graph）。
*   **Mental Model:** Imagine your project as a restaurant.
    *   **App Sec:** Ensuring the kitchen is clean and pest-free (CodeQL, Secret Scanning).
    *   **Supply Chain Sec:** Ensuring the ingredients delivered by suppliers are not expired or poisoned (Dependabot, Dependency Graph).

### 2.2 CodeQL：程式碼即數據 (Code as Data)
### 2.2 CodeQL: Code as Data

CodeQL 是 GitHub Advanced Security 的核心引擎。不同於傳統的 RegEx 掃描，CodeQL 會建立程式碼的語意資料庫（Database），包含語法樹（AST）與控制流圖（CFG）。
CodeQL is the core engine of GitHub Advanced Security. Unlike traditional RegEx-based scanning, CodeQL builds a semantic database of your code, including the Abstract Syntax Tree (AST) and Control Flow Graph (CFG).

*   **定義：** 你撰寫類似 SQL 的查詢語句來尋找漏洞模式（例如：「尋找所有未經消毒就進入 SQL 執行的使用者輸入」）。
*   **Definition:** You write SQL-like queries to find vulnerability patterns (e.g., "Find all user inputs that reach a SQL execution without sanitization").

### 2.3 OIDC (OpenID Connect)：短期信任取代長期憑證
### 2.3 OIDC (OpenID Connect): Short-lived Trust vs. Long-lived Credentials

在 CI/CD 中，最危險的資產往往是儲存在 GitHub Secrets 中的 `AWS_ACCESS_KEY_ID`。OIDC 允許 GitHub Actions 向雲端供應商換取一個「短效 Token」。
In CI/CD, the most dangerous assets are often the `AWS_ACCESS_KEY_ID` stored in GitHub Secrets. OIDC allows GitHub Actions to exchange a token for a "short-lived token" from the cloud provider.

*   **類比：**
    *   **Secrets:** 給清潔工一把你家大門的備用鑰匙，並祈禱他不會弄丟（長期風險）。
    *   **OIDC:** 清潔工到達時，警衛核對身份後，給他一張只能用一小時的門禁卡（最小權限）。
*   **Analogy:**
    *   **Secrets:** Giving the cleaner a spare key to your house and praying they don't lose it (long-term risk).
    *   **OIDC:** When the cleaner arrives, the guard verifies their identity and issues a key card valid for only one hour (least privilege).

---

## 3. 實務場景與系統設計視角
## 3. Real-World & System Design View

### 3.1 企業級 DevSecOps 管道架構
### 3.1 Enterprise DevSecOps Pipeline Architecture

在大型組織中，DevSecOps 必須是強制性且自動化的。以下是一個標準的設計模式：
In large organizations, DevSecOps must be mandatory and automated. The following is a standard design pattern:

1.  **Pre-Commit / IDE:** 使用 GitHub Copilot 或 IDE 插件進行輕量級掃描。
    **Pre-Commit / IDE:** Use GitHub Copilot or IDE plugins for lightweight scanning.
2.  **Pull Request (The Gate):**
    *   **Secret Scanning:** 阻止含有金鑰的 commit 推送（Push Protection）。
    *   **SAST (CodeQL):** 分析變更的程式碼，若發現 High/Critical 漏洞則 Block Merge。
    *   **Dependency Review:** 檢查新引入的套件是否含有已知漏洞或授權問題。
3.  **Deploy (OIDC):** Action Runner 使用 OIDC 取得 AWS/GCP 權限進行部署，無需管理 Key Rotation。
    **Deploy (OIDC):** Action Runner uses OIDC to obtain AWS/GCP permissions for deployment, eliminating the need for Key Rotation management.
4.  **Post-Deploy / Monitor:** 持續監控依賴圖（Dependency Graph），當舊依賴爆出新 CVE 時觸發 Dependabot Alert。
    **Post-Deploy / Monitor:** Continuously monitor the Dependency Graph; trigger Dependabot Alerts when new CVEs are discovered in old dependencies.

### 3.2 對系統品質的影響
### 3.2 Impact on System Quality

*   **可維護性 (Maintainability):** 自動化的依賴更新（Dependabot）雖然會產生噪音，但能避免「相依性地獄（Dependency Hell）」，防止技術債累積到無法升級的地步。
    **Maintainability:** Automated dependency updates (Dependabot), while noisy, prevent "Dependency Hell" and stop technical debt from accumulating to a point where upgrades become impossible.
*   **安全性 (Security):** 顯著降低憑證洩漏風險（透過 OIDC）與供應鏈攻擊面。
    **Security:** Significantly reduces the risk of credential leakage (via OIDC) and the supply chain attack surface.
*   **開發速度 (Velocity):** 雖然增加了檢查環節，但「左移（Shift Left）」將修復成本降至最低。在 PR 階段修復漏洞比在 Production 修復快 100 倍。
    **Velocity:** Although checks are added, "Shift Left" minimizes remediation costs. Fixing a vulnerability during the PR phase is 100x faster than fixing it in Production.

---

## 4. 逐步示例：OIDC 整合與 CodeQL 實戰
## 4. Walkthrough / Example: OIDC Integration & CodeQL in Action

### 案例背景
### Scenario Background

假設我們有一個 Node.js 後端服務，部署在 AWS Lambda 上。我們希望移除 GitHub Secrets 中的 AWS Keys，並確保沒有 SQL Injection 漏洞進入主分支。
Assume we have a Node.js backend service deployed on AWS Lambda. We want to remove AWS Keys from GitHub Secrets and ensure no SQL Injection vulnerabilities enter the main branch.

### 步驟 1：配置 AWS OIDC 信任 (Infrastructure as Code)
### Step 1: Configure AWS OIDC Trust (Infrastructure as Code)

首先，我們需要在 AWS 端信任 GitHub 的 OIDC Provider。這通常透過 Terraform 完成。
First, we need to trust GitHub's OIDC Provider on the AWS side. This is typically done via Terraform.

```hcl
# AWS IAM Role for GitHub Actions
resource "aws_iam_role" "github_actions" {
  name = "github-actions-deploy-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRoleWithWebIdentity"
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::${var.aws_account_id}:oidc-provider/token.actions.githubusercontent.com"
        }
        Condition = {
          StringLike = {
            # 安全關鍵：限制只能由特定 Repo 的特定 Branch 觸發
            # Critical Security: Restrict to specific Repo and Branch
            "token.actions.githubusercontent.com:sub": "repo:my-org/my-repo:ref:refs/heads/main"
          }
          StringEquals = {
            "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
          }
        }
      }
    ]
  })
}
```

### 步驟 2：GitHub Actions Workflow (OIDC + CodeQL)
### Step 2: GitHub Actions Workflow (OIDC + CodeQL)

建立 `.github/workflows/secure-deploy.yml`。
Create `.github/workflows/secure-deploy.yml`.

```yaml
name: Secure Build & Deploy

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

permissions:
  id-token: write   # Required for requesting the OIDC JWT
  contents: read    # Required for actions/checkout
  security-events: write # Required for uploading CodeQL results

jobs:
  security-scan:
    name: CodeQL Analysis
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with:
          languages: javascript

      # 如果是編譯語言（如 Java/C++），這裡需要執行 build command
      # If compiled language (Java/C++), run build command here

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v3
        with:
          category: "/language:javascript"

  deploy:
    name: Deploy to AWS
    needs: security-scan
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Configure AWS Credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-actions-deploy-role
          aws-region: us-east-1
          # 不需要 AWS_ACCESS_KEY_ID 或 SECRET_ACCESS_KEY
          # No AWS_ACCESS_KEY_ID or SECRET_ACCESS_KEY needed

      - name: Deploy Lambda
        run: |
          aws lambda update-function-code --function-name my-function --zip-file fileb://function.zip
```

### 為何這個做法可行？
### Why this works?

1.  **OIDC:** GitHub Actions 簽發一個 JWT，AWS 驗證該 JWT 的簽名與 `sub` (Subject) 欄位。若匹配，AWS 回傳臨時憑證。這消除了長期憑證洩漏的風險。
    **OIDC:** GitHub Actions issues a JWT; AWS verifies the signature and the `sub` (Subject) field. If they match, AWS returns temporary credentials. This eliminates the risk of long-lived credential leakage.
2.  **CodeQL:** 在部署前強制執行掃描。若掃描失敗（發現漏洞），`deploy` job 根本不會執行（因為 `needs: security-scan`）。
    **CodeQL:** Enforces scanning before deployment. If the scan fails (vulnerabilities found), the `deploy` job will not run at all (due to `needs: security-scan`).

---

## 5. 常見錯誤與反模式
## 5. Common Pitfalls & Anti-patterns

### 5.1 OIDC 權限過寬 (Over-privileged OIDC Subject)
### 5.1 Over-privileged OIDC Subject

*   **錯誤：** 在 AWS Condition 中設定 `repo:my-org/my-repo:*`，允許該 Repo 的任何分支、任何 PR 都能取得 AWS Admin 權限。
    **Mistake:** Setting `repo:my-org/my-repo:*` in the AWS Condition, allowing any branch or PR in that repo to assume AWS Admin privileges.
*   **後果：** 惡意員工或被盜帳號者可以開一個分支，修改 Workflow 印出 AWS 敏感資料或破壞基礎設施。
    **Consequence:** A malicious insider or compromised account can create a branch, modify the workflow to print AWS sensitive data, or destroy infrastructure.
*   **修正：** 嚴格限制 `sub` 為 `repo:my-org/my-repo:ref:refs/heads/main` 或特定 Environment。
    **Fix:** Strictly limit the `sub` to `repo:my-org/my-repo:ref:refs/heads/main` or a specific Environment.

### 5.2 警報疲勞 (Alert Fatigue)
### 5.2 Alert Fatigue

*   **錯誤：** 開啟所有 Dependabot 警報，但不設定過濾或自動合併規則。面對 500+ 個 Low/Moderate 警報，團隊選擇直接忽略。
    **Mistake:** Enabling all Dependabot alerts without filtering or auto-merge rules. Facing 500+ Low/Moderate alerts, the team chooses to ignore them entirely.
*   **修正：**
    1.  設定 Dependabot Grouped Updates（將多個更新合併為一個 PR）。
    2.  利用 GitHub Actions 自動 Approve & Merge 通過測試的 Minor/Patch 更新。
    3.  專注於 High/Critical 警報。
    **Fix:**
    1.  Configure Dependabot Grouped Updates (combine multiple updates into one PR).
    2.  Use GitHub Actions to auto-approve & merge Minor/Patch updates that pass tests.
    3.  Focus on High/Critical alerts.

### 5.3 僅掃描 HEAD 而忽略歷史 (Scanning HEAD only, ignoring History)
### 5.3 Scanning HEAD only, ignoring History

*   **錯誤：** 認為開啟 Secret Scanning 後就安全了，但歷史 commit 中仍包含舊的 AWS Key。
    **Mistake:** Thinking you are safe after enabling Secret Scanning, while historical commits still contain old AWS Keys.
*   **修正：** 攻擊者會 clone 整個 repo 挖掘歷史。必須使用 `BFG Repo-Cleaner` 或 `git-filter-repo` 重寫 git history，並**立即輪替（Rotate）** 該洩漏的憑證。
    **Fix:** Attackers clone the entire repo to mine history. You must use `BFG Repo-Cleaner` or `git-filter-repo` to rewrite git history and **immediately rotate** the leaked credentials.

---

## 6. 面試與實務問答切入點
## 6. Interview & Discussion Hooks

### Q1: 如果在大型單體系統（Monolith）中導入 CodeQL，發現有 5000 個既有警報，你會如何處理？
### Q1: If you introduce CodeQL to a large Monolith and find 5,000 existing alerts, how would you handle it?

*   **高分回答要點：**
    *   **Baseline (基準線):** 不要試圖一次修完。設定目前的狀態為 Baseline。
    *   **Stop the Bleeding (止血):** 設定 Quality Gate，只阻擋「新引入」的漏洞（New issues only）。
    *   **Triage (分流):** 依據 Severity (Critical/High) 與 Exploitability (是否對外暴露) 排定修復優先級。
    *   **Key Points:**
        *   **Baseline:** Don't try to fix everything at once. Set the current state as the baseline.
        *   **Stop the Bleeding:** Set a Quality Gate to block only "newly introduced" vulnerabilities.
        *   **Triage:** Prioritize fixes based on Severity (Critical/High) and Exploitability (is it exposed publicly?).

### Q2: 請解釋 OIDC Token Exchange 的流程，以及它為何比儲存 Secrets 更安全？
### Q2: Explain the OIDC Token Exchange process and why it is safer than storing Secrets.

*   **高分回答要點：**
    *   **流程:** GitHub (IdP) 簽發 JWT -> Cloud Provider (Relying Party) 驗證簽名與 Claims (sub, aud) -> Cloud Provider 回傳短期 Access Token。
    *   **安全性:** 避免了 Long-lived credentials 的儲存與輪替問題（Key Rotation）。即便 GitHub 被駭，攻擊者也無法獲得能長期訪問雲端的金鑰。
    *   **Key Points:**
        *   **Process:** GitHub (IdP) signs a JWT -> Cloud Provider (Relying Party) verifies signature and claims (sub, aud) -> Cloud Provider returns a short-lived Access Token.
        *   **Security:** Avoids storage and rotation issues of long-lived credentials. Even if GitHub is compromised, attackers cannot gain long-term access keys to the cloud.

### Q3: 我們如何防範「依賴混淆攻擊 (Dependency Confusion Attack)」？
### Q3: How do we prevent "Dependency Confusion Attacks"?

*   **高分回答要點：**
    *   **定義:** 攻擊者在公開 Registry (npm/pypi) 上發布與公司內部私有套件同名但版號更高的惡意套件。
    *   **防禦:** 在 Package Manager 配置中（如 `.npmrc`）明確指定 Scope (@myorg) 對應的 Registry URL。
    *   **GitHub 角色:** 使用 GitHub Packages 並設定權限，確保內部依賴優先於公開來源。
    *   **Key Points:**
        *   **Definition:** Attackers publish malicious packages on public registries (npm/pypi) with the same name as internal private packages but higher version numbers.
        *   **Defense:** Explicitly specify the Registry URL for Scopes (@myorg) in package manager configurations (e.g., `.npmrc`).
        *   **GitHub Role:** Use GitHub Packages with proper permissions to ensure internal dependencies take precedence over public sources.

---

## 7. 小結與後續延伸
## 7. Summary & Next Steps

### 記憶錨點
### Key Takeaways

1.  **Shift Left:** 安全檢查應在 PR 階段自動執行，而非部署前。
    **Shift Left:** Security checks should run automatically during the PR phase, not before deployment.
2.  **OIDC is King:** 停止在 GitHub Secrets 中儲存 AWS/GCP 的靜態金鑰。
    **OIDC is King:** Stop storing static AWS/GCP keys in GitHub Secrets.
3.  **Code as Data:** CodeQL 透過語意查詢分析代碼邏輯，比單純的 RegEx 更準確。
    **Code as Data:** CodeQL analyzes code logic via semantic queries, offering higher accuracy than simple RegEx.
4.  **Supply Chain:** 依賴管理（Dependabot）與依賴審查（Dependency Review）是防範供應鏈攻擊的關鍵。
    **Supply Chain:** Dependency management (Dependabot) and Dependency Review are critical for preventing supply chain attacks.
5.  **Push Protection:** 在金鑰離開開發者電腦的那一刻就進行攔截。
    **Push Protection:** Intercept keys the moment they leave the developer's machine.

### 後續延伸 (Next Steps)
### Next Steps

*   **Advanced GitHub Actions:** 學習 Self-hosted Runners 的安全隔離與 Scaling 策略（Chapter 05）。
    **Advanced GitHub Actions:** Learn about security isolation and scaling strategies for Self-hosted Runners (Chapter 05).
*   **Custom CodeQL Queries:** 嘗試為特定業務邏輯編寫自定義的 CodeQL 查詢（例如：強制特定的 Log 格式）。
    **Custom CodeQL Queries:** Try writing custom CodeQL queries for specific business logic (e.g., enforcing specific logging formats).
*   **SBOM (Software Bill of Materials):** 研究如何從 GitHub 自動生成 SBOM 並整合至合規報告中。
    **SBOM (Software Bill of Materials):** Research how to automatically generate SBOMs from GitHub and integrate them into compliance reports.