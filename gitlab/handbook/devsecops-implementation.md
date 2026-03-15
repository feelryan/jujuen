# DevSecOps 實戰：掃描與合規 / DevSecOps Implementation: Scanning and Compliance

## Mental model｜心智模型

在 GitLab CI/CD 中實踐 DevSecOps，不應被視為「在最後階段加一道鎖」，而應視為 **「在流水線中內建感測器 (Sensors)」**。

傳統的資安審查往往發生在部署前夕（Gatekeeper model），這導致修復成本極高。GitLab 的核心模型是 **Shift Left（左移）**，將資安掃描整合進每一次的 Merge Request (MR)。

1.  **The MR is the Firewall**: Merge Request 是防止漏洞進入 `main` 分支的防火牆。所有的掃描（SAST, Secret Detection, Dependency Scanning）都應在 MR pipeline 中執行。
2.  **Delta Analysis (差異分析)**: 開發者只關心「我這段程式碼引入了什麼新漏洞」。GitLab 的 MR Security Widget 專注於顯示 "New Vulnerabilities"，而非整個專案的歷史債務，這對於維持開發速度至關重要。
3.  **Policy as Code**: 合規性規則（如：禁止 High Severity 漏洞合併）應定義在程式碼或策略設定中，而非依賴人為記憶。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Layered Scanning Strategy (分層掃描策略)
不要試圖在一個 Job 裡做完所有事。利用 GitLab 的 Template 機制進行分層：
*   **Static Analysis (SAST/Secret/Lint)**: 執行速度快，應在每個 MR 必跑。
*   **Dependency Scanning**: 檢查第三方套件漏洞 (SCA)。
*   **Container Scanning**: 建置 Docker image 後立即掃描 (Trivy/Clair)。
*   **Dynamic Analysis (DAST)**: 速度慢，通常安排在 Review App 部署後，或僅在特定 Schedule/Release 分支執行。

### 2. Secret Management via OIDC (使用 OIDC 管理機敏資訊)
**不要** 再將長效型的 AWS Keys 或 Database Passwords 存放在 GitLab CI/CD Variables 中。
*   **Pattern**: 使用 GitLab 的 `id_tokens` (OpenID Connect) 與 HashiCorp Vault、AWS 或 GCP 整合。
*   **Benefit**: GitLab CI Job 會生成一個短效的 JWT Token，向 Vault/Cloud Provider 交換暫時性憑證。沒有長效 Key，就沒有 Key 洩漏的風險。

### 3. Security Gates with Approval Rules (基於規則的審核)
不要直接讓 Pipeline 失敗（Fail the pipeline），這會阻斷開發者的測試流程。
*   **Best Practice**: 設定 **Scan Result Policies (Security Policy)**。
*   **Logic**: 當掃描發現 `Critical` 或 `High` 等級的漏洞時，Pipeline 依然可以是綠燈 (Passed)，但 **Merge Button 會被鎖住**，並強制要求 Security Team 的成員進行 Approval。這平衡了開發體驗 (DX) 與安全性。

### 4. Auto-Fix and Remediation
利用 GitLab 的自動修復建議。對於依賴項更新（Dependency Scanning），GitLab 可以自動產生修復的 MR（類似 Dependabot），這能大幅降低維護負擔。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Fail Everything" Trap (所有漏洞都導致失敗)
*   **Anti-pattern**: 設定只要掃描出任何 Low/Info 等級漏洞或 False Positive，Pipeline 就直接 Failed。
*   **Consequence**: 開發者會產生 "Alert Fatigue" (告警疲勞)，開始想辦法繞過掃描，或者直接忽略資安報告。
*   **Solution**: 僅針對 Critical/High 進行阻擋，並建立處理 False Positive 的流程（Dismissal workflow）。

### 2. Hardcoded Secrets in CI Config (在設定檔中寫死密鑰)
*   **Anti-pattern**: `script: - deploy --token "my-secret-token"` 寫在 `.gitlab-ci.yml`。
*   **Risk**: 即使是 Private Repo，這也違反了資安原則，且無法輪替 (Rotate)。
*   **Fix**: 使用 Vault (OIDC) 或至少使用 Masked CI/CD Variables。

### 3. Scanning Only on Master/Main (只在主分支掃描)
*   **Anti-pattern**: 為了節省 CI 分鐘數，只在 `main` 分支跑 SAST。
*   **Consequence**: 當發現漏洞時，程式碼已經合併了。這時修復通常需要另外開 Ticket、排程，往往不了了之。
*   **Fix**: 掃描必須發生在 Feature Branch (MR) 階段。

### 4. Ignoring the "Needs" Keyword (忽略依賴優化)
*   **Anti-pattern**: 讓掃描 Job 等待 Build Job 完成才開始，導致 Pipeline 時間過長。
*   **Fix**: SAST/Secret Detection 通常不需要 Build Artifacts（除了 Java/C# 等編譯語言），應使用 `needs: []` 讓它們在 Pipeline 啟動時立即並行執行。

---

## Checklists & workflows｜檢查清單與流程

### Pipeline Setup Checklist
- [ ] **Include Templates**: 是否已引用 GitLab 官方維護的 SAST/Dependency Scanning/Secret Detection 模板？
- [ ] **OIDC Configured**: 是否已配置 `id_tokens` 以連接 Vault 或 Cloud Provider (AWS/GCP/Azure)？
- [ ] **Artifact Handling**: 掃描報告 (JSON) 是否正確輸出為 Artifacts，以便 Security Dashboard 讀取？
- [ ] **Optimization**: 是否對純文件修改 (Documentation changes) 略過掃描 Job？

### Security Gate Configuration
- [ ] **Scan Result Policy**: 是否已設定 Policy，當發現 Critical 漏洞時，強制要求資安人員 Approval？
- [ ] **License Check**: 是否設定了禁止合併的 License 類型（如 AGPL 等，視公司政策而定）？

### Vulnerability Management Workflow
1.  **Triage (檢視)**: 開發者在 MR Widget 看到漏洞。
2.  **Verify (驗證)**: 確認是否為 False Positive。
    *   如果是：在 GitLab 介面上點擊 "Dismiss" 並填寫理由。
    *   如果否：修正程式碼。
3.  **Approve (核准)**: 若無法立即修復但業務緊急，由 Security Team 審核後在 MR 進行 Override Approval。
4.  **Merge (合併)**: 確認無新增 Critical 漏洞後合併。

---

## Real-world examples｜實戰案例

### 1. The "Standard" DevSecOps Include (標準引用範例)
這是最快速啟用掃描的方式，利用 GitLab Auto DevOps 的模板，但手動控制引用。

```yaml
# .gitlab-ci.yml
include:
  - template: Security/SAST.gitlab-ci.yml
  - template: Security/Secret-Detection.gitlab-ci.yml
  - template: Security/Dependency-Scanning.gitlab-ci.yml
  - template: Security/Container-Scanning.gitlab-ci.yml

variables:
  # 調整掃描等級，避免過多雜訊
  SECURE_LOG_LEVEL: "info"
  # 啟用實驗性功能或特定分析器
  SAST_EXPERIMENTAL_FEATURES: "true"

# 優化：讓 SAST 不需等待 Build 階段，盡早執行
sast:
  stage: test
  needs: []
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

### 2. Vault Integration via OIDC (無密鑰整合)
這是現代化 Secret Management 的標準做法，完全不需在 GitLab 儲存靜態密鑰。

```yaml
# .gitlab-ci.yml
job_using_vault:
  stage: deploy
  image: hashicorp/vault:latest
  id_tokens:
    VAULT_ID_TOKEN:
      aud: https://vault.example.com  # 對應 Vault 的設定
  secrets:
    DATABASE_PASSWORD:
      vault: secret/data/production/db/password@key # 從 Vault 路徑讀取
      file: false # 設為環境變數
  script:
    - echo "Authenticating with Vault using OIDC..."
    - export VAULT_ADDR=https://vault.example.com
    - export VAULT_TOKEN="$(vault write -field=token auth/jwt/login role=my-gitlab-role jwt=$VAULT_ID_TOKEN)"
    - echo "Deploying with DB Password..." # DATABASE_PASSWORD is now available
```

### 3. Scan Result Policy (Security Approval Rule)
雖然這通常在 UI 設定 (Security & Compliance > Policies)，但背後的 YAML 邏輯如下：

```yaml
# .gitlab/security-policies/policy.yml (示意)
type: scan_result_policy
name: "Critical Vulnerability Check"
description: "Require Security Team approval for Critical vulnerabilities"
enabled: true
rules:
  - type: scan_finding
    scanners: [sast, dependency_scanning, container_scanning]
    vulnerabilities_allowed: 0
    severity_levels: [critical]
    branch_type: protected
actions:
  - type: require_approval
    approvals_required: 1
    user_approvers: ["security-lead"]
    group_approvers: ["sec-ops-team"]
```