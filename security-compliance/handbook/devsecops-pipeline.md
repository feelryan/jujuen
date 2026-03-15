# DevSecOps 流程與供應鏈安全 / DevSecOps Pipeline & Supply Chain Security

## Mental model｜心智模型

### 1. From Gatekeeper to Guardrails (從守門員到護欄)
傳統資安是「守門員（Gatekeeper）」，在軟體發布前進行耗時的人工審查，往往成為瓶頸。DevSecOps 的核心是將資安轉化為「護欄（Guardrails）」。
- **Guardrails** 是自動化的，它們存在於 CI/CD 流程中。
- 如果程式碼違反安全規則（如包含憑證、依賴已知漏洞套件），流水線會自動失敗，就像工廠產線上的自動退料機制。
- 目標是讓開發者在寫程式的當下（Commit 或 PR 階段）就能修正問題，而不是在部署前一刻才被資安團隊擋下。

### 2. The Supply Chain Confidence (供應鏈信任鏈)
現代軟體 80% 以上由開源組件構成。你的程式碼只是冰山一角，水面下是龐大的依賴樹（Dependency Tree）。
- **SCA (Software Composition Analysis)** 是你的「進貨檢驗」。你必須知道你的供應商（Open Source Libraries）是否送來了壞掉的零件。
- **SBOM (Software Bill of Materials)** 是你的「成份標示表」。當發生類似 Log4j 的事件時，你不需要掃描程式碼，而是查詢 SBOM 就能在幾秒鐘內知道哪些服務受影響。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Layered Defense in Pipeline (流水線分層防禦)
不要試圖在一個階段做完所有掃描。應根據速度與反饋迴圈（Feedback Loop）分層實施：

*   **Pre-commit / IDE 階段 (最快)**：
    *   **Secrets Detection**: 防止 AWS Key、Database Password 被 commit 進 git history。一旦進入 git，就視為已洩漏。
    *   **Linting**: 基礎語法安全檢查。
*   **CI / Build 階段 (數分鐘)**：
    *   **SCA (Software Composition Analysis)**: 檢查 `package.json`, `go.mod`, `pom.xml` 中的依賴套件是否有 CVE 漏洞。
    *   **SAST (Static Application Security Testing)**: 掃描原始碼中的 SQL Injection, XSS 等邏輯漏洞。
    *   **IaC Scanning**: 檢查 Terraform/K8s YAML 是否有配置錯誤（如 S3 bucket public access）。
*   **CD / Artifact 階段 (較慢)**：
    *   **Container Scanning**: 掃描 Docker Base Image 的 OS 層級漏洞。
    *   **DAST (Dynamic Application Security Testing)**: 對執行中的應用程式進行黑箱攻擊測試（通常在 Staging 環境）。

### 2. Automated Dependency Management (自動化依賴管理)
不要依賴人工定期升級套件。
*   使用 **Dependabot** 或 **Renovate**。當依賴套件有新版本或修復了安全漏洞時，機器人會自動發送 Pull Request。
*   **Pattern**: 設定自動合併（Auto-merge）規則給 Patch version 或低風險更新，將開發者的精力集中在 Major version 的變更審查。

### 3. SBOM & Artifact Signing (軟體物料清單與簽章)
為了防範供應鏈攻擊（如駭客篡改了你的 Build Server 或依賴包）：
*   **Generate SBOM**: 在 Build 過程中生成 CycloneDX 或 SPDX 格式的 SBOM。
*   **Sign Artifacts**: 使用 **Sigstore / Cosign** 對你的 Docker Image 或 Binary 進行數位簽章。
*   **Verify**: 在 Kubernetes Cluster 或部署環境中，使用 Policy Controller (如 Kyverno 或 OPA Gatekeeper) 驗證簽章，確保只部署經過授權且未被篡改的 Image。

### 4. Baseline & Triage Strategy (基線與分流策略)
剛引入 DevSecOps 工具時，通常會產生數百個「漏洞」。
*   **Establish a Baseline**: 將既有的舊漏洞標記為 "Backlog" 或 "Technical Debt"，不要讓它們阻擋 Pipeline（除非是 Critical）。
*   **Stop the Bleeding**: 設定 Pipeline 規則為「**No New Critical/High Vulnerabilities**」。確保新的程式碼是乾淨的，舊債慢慢還。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Wall of Red" (紅燈牆效應)
*   **Bad Practice**: 一口氣開啟所有 SAST/SCA 規則，導致 CI Pipeline 跑出 500 個錯誤並失敗。
*   **Consequence**: 開發團隊會感到麻痺，認為資安工具只是在阻礙工作，最終會想辦法繞過（Bypass）檢查。
*   **Fix**: 從「僅監控（Audit Mode）」開始，調整誤報（False Positives），只針對高信心度、高風險的問題阻擋 Pipeline。

### 2. Scanning Secrets in CI only (只在 CI 掃描機密)
*   **Bad Practice**: 在 GitHub Actions 或 Jenkins 中掃描 Secrets。
*   **Pitfall**: 當 CI 報錯時，Secret 已經存在於 Git Commit History 中了。你必須重寫 Git History (Force Push) 並輪替該金鑰。
*   **Fix**: 強制推行 **Pre-commit hooks** (如 `pre-commit` framework 搭配 `gitleaks` 或 `trufflehog`)，在 `git commit` 按下的瞬間就阻擋。

### 3. Blindly Trusting Public Images (盲目信任公開映像檔)
*   **Bad Practice**: Dockerfile 使用 `FROM node:latest` 或 `FROM python:3.9` 而不進行掃描或鎖定 hash。
*   **Pitfall**: 上游映像檔可能被植入惡意軟體，或包含數千個已知漏洞。
*   **Fix**: 使用 **Distroless** 或 **Alpine** 等最小化映像檔，並鎖定 SHA256 Hash (`FROM node@sha256:...`)，且定期掃描 Base Image。

### 4. Blocking Deployments for Low Risks (因低風險阻擋部署)
*   **Bad Practice**: 因為一個 Low/Info 等級的漏洞（例如某個不影響功能的 regex 效能問題）而讓整個 Release 失敗。
*   **Consequence**: 業務交付延遲，資安團隊失去信任。
*   **Fix**: 設定明確的 **Quality Gate**。例如：只阻擋 Critical & High，Medium 設定 SLA（如 30 天內修復），Low 僅紀錄。

---

## Checklists & workflows｜檢查清單與流程

### Pipeline Integration Checklist (整合檢核表)

- [ ] **Pre-commit Stage**:
  - [ ] 已配置 `pre-commit` hook。
  - [ ] 整合 Secrets Scanner (e.g., Gitleaks, TruffleHog)。
  - [ ] 整合基礎 Linter (e.g., ESLint, GolangCI-Lint)。
- [ ] **Build Stage (CI)**:
  - [ ] **SCA**: 已整合依賴掃描工具 (e.g., Snyk, Trivy, OWASP Dependency-Check)。
  - [ ] **SAST**: 已針對主要語言配置靜態分析 (e.g., SonarQube, CodeQL)。
  - [ ] **IaC**: 若有 Terraform/K8s 檔，已整合 Checkov 或 Tfsec。
- [ ] **Artifact Stage**:
  - [ ] **Container Scan**: 建置完 Docker Image 後立即掃描 (e.g., Trivy, Grype)。
  - [ ] **SBOM**: 產出 SBOM 檔案 (CycloneDX/SPDX) 並隨 Artifact 封存。
  - [ ] **Signing**: 使用私鑰或 OIDC (Sigstore) 對 Artifact 簽章。
- [ ] **Policy & Gate**:
  - [ ] 設定 Quality Gate：Critical 漏洞直接 Fail Build。
  - [ ] 設定例外排除機制 (Vulnerability Exception Process)，避免誤報卡死流程。

### Vulnerability Remediation Workflow (漏洞修復流程)

1.  **Discovery**: Pipeline 偵測到新漏洞。
2.  **Triage (分流)**:
    *   是 False Positive (誤報)? -> 標記為 Ignore/Won't Fix 並附上原因 -> **Close**。
    *   是 True Positive 但不影響當前環境 (Not Exploitable)? -> 標記並設定 Review Date -> **Monitor**。
    *   是 True Positive 且高風險? -> **Create Ticket** (Jira/GitHub Issue)。
3.  **Remediation**:
    *   **Patch**: 升級套件版本 (優先選擇)。
    *   **Mitigate**: 如果無法升級，實施補償性控制 (如 WAF 規則、關閉特定功能)。
4.  **Verification**: 重新執行 Pipeline，確認漏洞消失。

---

## Real-world examples｜實戰案例

### Example 1: GitHub Actions with Trivy (Container & SCA Scan)

這是一個實際可用的 GitHub Actions 片段，展示如何在 Build 過程中掃描 Docker Image 並生成 SBOM。

```yaml
name: DevSecOps Build

on: [push]

jobs:
  build-secure:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Build Docker Image
        run: docker build -t myapp:${{ github.sha }} .

      # 1. 掃描 Docker Image 漏洞 (Container Security)
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'myapp:${{ github.sha }}'
          format: 'table'
          exit-code: '1'          # 發現漏洞時讓 Pipeline 失敗
          ignore-unfixed: true    # 忽略尚未有修補程式的漏洞
          vuln-type: 'os,library'
          severity: 'CRITICAL,HIGH' # 只阻擋高風險以上

      # 2. 生成 SBOM (Supply Chain Security)
      - name: Generate SBOM
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'myapp:${{ github.sha }}'
          format: 'cyclonedx'
          output: 'sbom.json'

      - name: Upload SBOM
        uses: actions/upload-artifact@v3
        with:
          name: sbom
          path: sbom.json
```

### Example 2: Handling the "Log4j" Scenario (SCA Value)

**情境**：週五下午爆發 Log4j (Log4Shell) 漏洞。
*   **沒有 DevSecOps 的團隊**：
    *   緊急召集所有開發者。
    *   人工檢查幾百個 Repo 的 `pom.xml` 或 `build.gradle`。
    *   不確定編譯後的 jar 包裡是否藏有遞歸依賴 (Transitive Dependency) 的 Log4j。
    *   耗時：3-5 天排查與修復。
*   **有 DevSecOps/SBOM 的團隊**：
    *   資安官使用 Dependency Track 或類似工具查詢集中管理的 SBOM 資料庫。
    *   搜尋 `log4j-core` 版本 `< 2.15.0`。
    *   系統立即列出受影響的 5 個微服務。
    *   自動觸發 Dependabot/Renovate 發送 PR 升級版本。
    *   耗時：1 小時內定位，當天完成修復與部署。

### Example 3: Pre-commit Configuration (Preventing Secrets Leak)

`.pre-commit-config.yaml` 配置範例，開發者在本地 `git commit` 時就會執行。

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.16.1
    hooks:
      - id: gitleaks
        # 掃描當前 commit 是否包含 AWS Key, Private Key, API Tokens
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: check-merge-conflict
      - id: detect-private-key
```