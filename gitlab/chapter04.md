# 1. 前言與學習目標 (Introduction and Learning Objectives)

在資深工程師的職涯中，DevSecOps 不僅僅是安裝幾個掃描工具，而是關於如何建立「自動化的信任機制」。本章將探討如何利用 GitLab 的內建安全功能與外部密鑰管理系統（如 HashiCorp Vault），在不犧牲開發速度的前提下，實現 Shift-left（左移）安全防護。

In the career of a Senior Software Engineer, DevSecOps is not just about installing a few scanners; it is about building an "automated trust mechanism." This chapter explores how to leverage GitLab's built-in security features and external secret management systems (like HashiCorp Vault) to implement Shift-left security without sacrificing development velocity.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **整合全方位掃描**：在 CI Pipeline 中正確配置 SAST、DAST、相依性掃描（Dependency Scanning）與容器掃描（Container Scanning）。
    **Integrate Comprehensive Scanning**: Correctly configure SAST, DAST, Dependency Scanning, and Container Scanning within the CI Pipeline.
2.  **實作進階密鑰管理**：捨棄靜態 CI 變數，改用 GitLab OIDC (OpenID Connect) 與 HashiCorp Vault 進行動態密鑰存取。
    **Implement Advanced Secret Management**: Move away from static CI variables and utilize GitLab OIDC (OpenID Connect) with HashiCorp Vault for dynamic secret access.
3.  **設計合規策略**：利用 GitLab 的 Security Policies 與 Compliance Frameworks，強制執行組織級別的安全規範。
    **Design Compliance Strategies**: Enforce organization-level security standards using GitLab's Security Policies and Compliance Frameworks.
4.  **平衡速度與安全**：理解如何處理誤報（False Positives）與設定阻擋規則（Blocking Rules），避免安全掃描成為開發瓶頸。
    **Balance Speed and Security**: Understand how to handle false positives and configure blocking rules to prevent security scans from becoming development bottlenecks.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 Shift-Left Security (安全左移)

**直覺類比**：
想像你在蓋房子。傳統的安全檢查就像是房子蓋好後，檢查員才來敲牆壁看有沒有空心（Penetration Testing）。Shift-left 則像是在畫設計圖（Code Review）和選磚塊（Dependency Scanning）時，就已經在檢查結構強度。

**Intuitive Analogy**:
Imagine building a house. Traditional security checks are like an inspector checking for hollow walls only after the house is finished (Penetration Testing). Shift-left is like checking structural integrity while drawing the blueprints (Code Review) and selecting the bricks (Dependency Scanning).

**正規定義**：
將安全測試從軟體開發生命週期（SDLC）的末端（測試/部署階段）移動到早期階段（編碼/建置階段）。在 GitLab 中，這意味著每個 Merge Request (MR) 都會觸發微型的安全審計。

**Formal Definition**:
Moving security testing from the end of the Software Development Life Cycle (SDLC) (testing/deployment phase) to the early stages (coding/build phase). In GitLab, this means every Merge Request (MR) triggers a micro-security audit.

### 2.2 The Security Triad in CI/CD (CI/CD 中的安全鐵三角)

1.  **Code Security (SAST & Secrets Detection)**:
    *   檢查原始碼中的邏輯漏洞（如 SQL Injection）與意外提交的憑證。
    *   Checks source code for logical vulnerabilities (e.g., SQL Injection) and accidentally committed credentials.
2.  **Supply Chain Security (Dependency & Container Scanning)**:
    *   檢查你引用的第三方套件（如 npm, maven）與 Base Image 是否有已知的 CVE。
    *   Checks third-party packages (e.g., npm, maven) and Base Images for known CVEs.
3.  **Runtime Security (DAST & Environment Protection)**:
    *   對運行中的應用程式進行攻擊模擬，並保護部署環境的存取權限。
    *   Simulates attacks on the running application and protects access to deployment environments.

### 2.3 Static vs. Dynamic Secrets (靜態與動態密鑰)

*   **Static (CI Variables)**: 就像把備用鑰匙藏在門墊下。雖然方便，但如果有人翻開門墊（擁有 Maintainer 權限），鑰匙就洩漏了，且更換鑰匙很麻煩。
    **Static (CI Variables)**: Like hiding a spare key under the doormat. Convenient, but if someone lifts the mat (has Maintainer access), the key is compromised, and rotating it is a hassle.
*   **Dynamic (Vault + OIDC)**: 就像旅館的房卡。你憑身分證（GitLab CI Job JWT）去櫃檯（Vault）換取一張只能用一小時的房卡。
    **Dynamic (Vault + OIDC)**: Like a hotel key card. You exchange your ID (GitLab CI Job JWT) at the front desk (Vault) for a card that only works for one hour.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型企業或受監管產業（金融、醫療）的系統設計中，GitLab 的 DevSecOps 扮演著「守門員」與「審計員」的雙重角色。

In large enterprises or regulated industries (FinTech, HealthTech), GitLab's DevSecOps plays the dual role of "Gatekeeper" and "Auditor."

### 3.1 典型架構流程 (Typical Architecture Flow)

1.  **Developer Commit**: 開發者提交程式碼。
    **Developer Commit**: Developer commits code.
2.  **Pre-build Scan**: 在建置 Artifact 之前，先執行 Secret Detection 與 SAST。若發現私鑰洩漏，立即中斷 Pipeline。
    **Pre-build Scan**: Before building the artifact, execute Secret Detection and SAST. If a private key leak is detected, fail the pipeline immediately.
3.  **Build & Container Scan**: 建置 Docker Image，並掃描 Image 層級的漏洞（如 OS 套件過舊）。
    **Build & Container Scan**: Build the Docker Image and scan for image-level vulnerabilities (e.g., outdated OS packages).
4.  **Secret Injection (Vault)**: 部署階段，GitLab Runner 使用 JWT 向 Vault 請求短效期的 AWS/GCP 憑證或 Database 密碼。
    **Secret Injection (Vault)**: During deployment, the GitLab Runner uses a JWT to request short-lived AWS/GCP credentials or Database passwords from Vault.
5.  **Review App DAST**: 部署到臨時環境（Review App），執行 DAST 掃描。
    **Review App DAST**: Deploy to a temporary environment (Review App) and execute DAST scans.
6.  **Security Dashboard**: 所有發現的漏洞彙整至 GitLab Security Dashboard，供資安團隊審核。
    **Security Dashboard**: All detected vulnerabilities are aggregated in the GitLab Security Dashboard for the security team to review.

### 3.2 對系統屬性的影響 (Impact on System Attributes)

*   **可維護性 (Maintainability)**: 自動化依賴更新（如 Renovate 或 GitLab Dependency Scanning）減少了技術債累積。
    **Maintainability**: Automated dependency updates (like Renovate or GitLab Dependency Scanning) reduce technical debt accumulation.
*   **安全性 (Security)**: 縮小攻擊面。動態密鑰消除了長期憑證洩漏的風險。
    **Security**: Reduces the attack surface. Dynamic secrets eliminate the risk of long-term credential leakage.
*   **開發速度 (Velocity)**: 初期會因為修復漏洞而變慢，但長期來看，避免了 Release 前夕的「資安總體檢」導致的延期。
    **Velocity**: Initially slower due to vulnerability remediation, but in the long run, it prevents delays caused by "security audits" right before release.

---

# 4. 逐步示例 (Walkthrough / Example)

本節將示範如何將一個普通的 Pipeline 升級為具備 DevSecOps 與 Vault 整合的企業級 Pipeline。

This section demonstrates how to upgrade a standard pipeline to an enterprise-grade pipeline with DevSecOps and Vault integration.

### 4.1 基礎場景 (Basic Scenario)

假設我們有一個 Node.js 微服務，原本的 `.gitlab-ci.yml` 只是簡單的 Build 與 Test，並且將 Database 密碼存在 GitLab CI/CD Variables 中（這是常見的反模式）。

Assume we have a Node.js microservice. The original `.gitlab-ci.yml` only performs simple Build and Test steps, and stores the Database password in GitLab CI/CD Variables (a common anti-pattern).

### 4.2 步驟一：引入 GitLab 安全模板 (Step 1: Including GitLab Security Templates)

GitLab 提供了 "Auto DevOps" 的組件，我們可以透過 `include` 快速啟用。

GitLab provides "Auto DevOps" components that we can quickly enable via `include`.

```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

# 引入標準安全掃描模板
# Include standard security scanning templates
include:
  - template: Security/SAST.gitlab-ci.yml
  - template: Security/Secret-Detection.gitlab-ci.yml
  - template: Security/Dependency-Scanning.gitlab-ci.yml
  - template: Security/Container-Scanning.gitlab-ci.yml

# 覆寫 SAST 設定 (可選)
# Override SAST settings (Optional)
sast:
  variables:
    SEARCH_MAX_DEPTH: 4
  stage: test
```

**思考 (Thinking)**: 這樣做雖然簡單，但可能會產生大量雜訊（Noise）。實務上，我們通常會在 GitLab UI 的 "Security Configuration" 中調整規則，或者透過 `.sast-ignore` 檔案排除測試資料夾。

**Thinking**: While simple, this can generate a lot of noise. In practice, we usually tune rules in the GitLab UI's "Security Configuration" or exclude test folders via a `.sast-ignore` file.

### 4.3 步驟二：整合 HashiCorp Vault (Step 2: Integrating HashiCorp Vault)

這是資深工程師必須掌握的重點：**無憑證驗證 (Keyless Authentication)**。

This is a key focus for senior engineers: **Keyless Authentication**.

**前提 (Prerequisites)**:
1.  Vault 已配置 JWT Auth Method。
2.  Vault 中有一個 Role 綁定到特定的 GitLab Project/Branch。

**Prerequisites**:
1.  Vault is configured with the JWT Auth Method.
2.  A Role in Vault is bound to the specific GitLab Project/Branch.

**Pipeline 配置 (Pipeline Configuration)**:

```yaml
deploy_prod:
  stage: deploy
  image: hashicorp/vault:latest
  # 宣告需要 OIDC Token
  # Declare the need for an OIDC Token
  id_tokens:
    VAULT_ID_TOKEN:
      aud: https://vault.example.com
  variables:
    VAULT_ADDR: "https://vault.example.com"
    VAULT_ROLE: "my-project-prod-role"
  script:
    # 1. 使用 GitLab 簽發的 JWT 登入 Vault
    # 1. Login to Vault using the JWT signed by GitLab
    - export VAULT_TOKEN=$(vault write -field=token auth/jwt/login role=$VAULT_ROLE jwt=$VAULT_ID_TOKEN)
    
    # 2. 讀取動態密鑰 (例如 AWS Key 或 DB Password)
    # 2. Read dynamic secrets (e.g., AWS Key or DB Password)
    - export DB_PASS=$(vault kv get -field=password secret/my-app/prod/db)
    
    # 3. 執行部署 (此處僅為示範)
    # 3. Execute deployment (Demo only)
    - echo "Deploying with secure DB password..."
    - ./deploy_script.sh --password $DB_PASS
```

**為何這樣做可行？ (Why this works?)**
GitLab 為每個 Job 簽發一個 JWT (`VAULT_ID_TOKEN`)，其中包含 `project_id`, `ref` (branch), `user_login` 等 claim。Vault 驗證簽名並檢查 claim 是否符合 Role 定義。如果符合，就發給 Runner 一個短效期的 Vault Token。**整個過程沒有任何長效密碼存在 GitLab 中。**

GitLab issues a JWT (`VAULT_ID_TOKEN`) for each job, containing claims like `project_id`, `ref` (branch), `user_login`. Vault verifies the signature and checks if the claims match the Role definition. If they match, it issues a short-lived Vault Token to the Runner. **No long-lived secrets exist in GitLab throughout this process.**

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 警報疲勞 (Alert Fatigue)
*   **錯誤 (Pitfall)**: 一次開啟所有掃描器，並將所有嚴重等級（Low to Critical）都設為 Pipeline 失敗條件。
    **Pitfall**: Enabling all scanners at once and setting all severity levels (Low to Critical) to fail the pipeline.
*   **後果 (Consequence)**: 開發者被數百個 "Low severity" 警告淹沒，最終選擇忽略所有安全報告，或者直接 disable 掃描 job。
    **Consequence**: Developers are overwhelmed by hundreds of "Low severity" warnings, eventually choosing to ignore all security reports or disable scanning jobs entirely.
*   **修正 (Correction)**: 採用「逐步加強」策略。初期只阻擋 "Critical" 漏洞，並專注於修復新產生的漏洞（New Vulnerabilities），對於既有的舊債（Backlog）則另案處理。

### 5.2 誤用 CI/CD 變數儲存敏感資料 (Misusing CI/CD Variables for Secrets)
*   **錯誤 (Pitfall)**: 將 Production Database 密碼存在 GitLab CI/CD Variables，並未勾選 "Masked" 或 "Protected"。
    **Pitfall**: Storing Production Database passwords in GitLab CI/CD Variables without checking "Masked" or "Protected".
*   **後果 (Consequence)**: 任何有權限修改 `.gitlab-ci.yml` 的開發者都可以寫一個 `echo $DB_PASS` 的 job 把密碼印出來。
    **Consequence**: Any developer with permission to modify `.gitlab-ci.yml` can write a job with `echo $DB_PASS` to print the password.
*   **修正 (Correction)**: 使用 Vault/AWS Secrets Manager 整合。若必須使用 CI 變數，務必設定 "Protected"（僅在 Protected Branch/Tag 可用）與 "Masked"（在 Log 中隱藏）。

### 5.3 在 Production 執行破壞性 DAST (Destructive DAST in Production)
*   **錯誤 (Pitfall)**: 直接對 Production URL 執行 DAST 全掃描。
    **Pitfall**: Running a full DAST scan directly against the Production URL.
*   **後果 (Consequence)**: DAST 工具可能會填寫大量垃圾表單，甚至觸發刪除操作（如果爬蟲爬到了 Delete 連結），導致資料汙染或服務中斷。
    **Consequence**: DAST tools might fill out massive amounts of junk forms or even trigger delete operations (if the crawler finds Delete links), causing data pollution or service disruption.
*   **修正 (Correction)**: 僅在 Review App 或 Staging 環境執行 DAST。若必須掃描 Prod，請使用唯讀帳號或排除危險路徑。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 如何在「開發速度」與「安全性」之間取得平衡？
**How do you balance "Development Velocity" and "Security"?**

*   **高分回答要點 (Key Points)**:
    *   **Shift Left**: 越早發現修復成本越低。
    *   **Baseline & Policy**: 設定基準線，只阻擋「新增」的漏洞，不讓舊債阻礙新功能上線。
    *   **Async Scanning**: 對於耗時的 DAST，可以安排在 Nightly Build 或非同步 Pipeline 中執行，不阻擋每個 Commit 的即時回饋。
    *   **Auto-remediation**: 利用 Dependabot 或 Renovate 自動建立修復漏洞的 MR。

### Q2: 請解釋 GitLab CI 與 Vault 整合的 OIDC 流程，相比於使用 Access Token 有何優勢？
**Explain the OIDC flow between GitLab CI and Vault. What are the advantages over using Access Tokens?**

*   **高分回答要點 (Key Points)**:
    *   **Mechanism**: 描述 JWT 的簽發（GitLab）、傳遞（Runner）、驗證（Vault）與權限交換（Token）流程。
    *   **Secret Zero Problem**: 解決了「保護密鑰的密鑰」問題。不需要在 GitLab 預埋任何長效 Token。
    *   **Granularity**: 可以基於 Branch、Tag 甚至特定的 Job ID 來限制權限（Bound Claims）。
    *   **Rotation**: 憑證是短效且動態生成的，無需人工輪替。

### Q3: 什麼是 Compliance Pipeline (合規管線)？它解決了什麼問題？
**What is a Compliance Pipeline? What problem does it solve?**

*   **高分回答要點 (Key Points)**:
    *   **Problem**: 在大型組織中，個別團隊可能會為了趕進度而移除安全掃描 Job。
    *   **Solution**: Compliance Pipeline (或 Scan Execution Policies) 允許資安團隊定義一組「強制執行」的 Job。
    *   **Implementation**: 這些 Job 會在專案原本的 `.gitlab-ci.yml` 之前或之後強制執行，開發者無法繞過或覆寫。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 7.1 記憶錨點 (Key Takeaways)
1.  **Shift-Left**: 安全不是最後的關卡，而是貫穿開發流程的持續回饋。
2.  **Layers of Security**: 結合 SAST (Code), Dependency Scanning (Supply Chain), Container Scanning (Infra), 與 DAST (Runtime)。
3.  **Vault Integration**: 使用 `id_tokens` 與 JWT 實現無憑證驗證 (Keyless Auth)，徹底移除靜態密鑰。
4.  **Policy as Code**: 使用 GitLab Security Policies 強制執行合規要求，防止人為疏忽。
5.  **Noise Management**: 正確管理誤報與 Baseline，避免警報疲勞導致安全機制失效。

### 7.2 後續延伸 (Next Steps)
*   **進階實作**: 研究如何撰寫自定義的 SAST 規則 (使用 Semgrep) 來捕捉公司特定的錯誤模式。
    **Advanced Implementation**: Research how to write custom SAST rules (using Semgrep) to catch company-specific error patterns.
*   **下一章預告 (Chapter 05)**: **GitLab Observability & Monitoring**。學習如何監控 Pipeline 效能、整合 Prometheus/Grafana，以及追蹤 Deployment 的健康狀態。
    **Next Chapter Preview (Chapter 05)**: **GitLab Observability & Monitoring**. Learn how to monitor Pipeline performance, integrate Prometheus/Grafana, and track Deployment health.