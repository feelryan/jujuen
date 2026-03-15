# 系統遷移與第三方整合 / System Migration and Third-party Integration

## Mental model｜心智模型

在進行 GitLab 的遷移與整合時，核心思維必須從「工具替換」轉變為「架構重構」與「事件驅動整合」。

### 1. 從「寵物」到「牲畜」 (Pet vs. Cattle)
*   **Legacy (Jenkins):** 傳統 Jenkins Server 往往被視為「寵物」，充滿了手動安裝的 Plugins、全域設定與累積多年的狀態 (Stateful)。
*   **GitLab CI:** GitLab Runner 與 Job 應被視為「牲畜」，是無狀態 (Stateless)、短暫 (Ephemeral) 且基於容器化 (Docker-based) 的。
*   **遷移關鍵：** 不要試圖在 GitLab CI 中「複製」Jenkins 的環境；而是將環境封裝進 Docker Image，讓 Pipeline 定義檔 (YAML) 成為唯一的真理來源 (Source of Truth)。

### 2. 宣告式 vs. 指令式 (Declarative vs. Imperative)
*   **Jenkinsfile (Scripted):** 傾向於寫 Groovy 腳本，邏輯複雜且難以閱讀。
*   **GitLab CI (.yml):** 嚴格的宣告式語法。你告訴 GitLab **「想要什麼狀態」** (例如：`needs`, `rules`, `artifacts`)，而不是寫腳本去控制 **「如何達到」**。

### 3. 事件匯流排 (The Event Bus)
*   將 GitLab 視為開發流程的 **Event Source**。
*   **Integration:** 所有的整合（Jira, Slack, Custom Webhooks）都是對 GitLab 事件（Push, Merge Request, Pipeline Failure）的訂閱與反應。這是一個「事件驅動 (Event-driven)」的生態系，而非單向的通知。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 遷移策略：絞殺榕模式 (Strangler Fig Pattern)
不要嘗試一次性的大霹靂 (Big Bang) 遷移。
*   **雙軌並行 (Parallel Run):** 在保留舊 CI 系統的同時，針對新功能或非關鍵路徑啟用 GitLab CI。
*   **觸發器橋接:** 在過渡期，可以使用 GitLab CI 的 `trigger` 功能去呼叫舊的 Jenkins Job，逐步將邏輯搬移過來。

### 2. Jenkins to GitLab CI 轉換模式
*   **Plugin 替代方案:** 盤點 Jenkins Plugins，大多數功能應由 **Docker Image** 或 **CLI Tools** 取代。
    *   *Example:* 透過 Maven Plugin 建置 $\rightarrow$ 使用 `image: maven:3.8` 直接執行 `mvn clean package`。
*   **Shared Libraries $\rightarrow$ CI Templates:** 將 Jenkins Shared Libraries 的共用邏輯轉換為 GitLab 的 `include: component` 或 `include: project` (CI Templates)。

### 3. GitHub Actions to GitLab CI 對照
*   **Steps vs. Script:** GHA 的 `steps` 通常對應 GitLab 的 `script` 區塊。
*   **Actions vs. Includes/Images:** GHA 的 Marketplace Actions 在 GitLab 中通常對應為「引用一個包含該工具的 Docker Image」或是「Include 一個封裝好的 Template」。

### 4. Jira & Project Management Integration
*   **Smart Commits:** 強制開發者在 Commit Message 中包含 Ticket ID (e.g., `JIRA-123`)。
*   **Transition Automation:** 設定 GitLab 在 Merge Request 合併後，自動將 Jira Ticket 狀態轉為 `Done` 或 `Ready for QA`。
*   **Visibility:** 在 Jira Ticket 中顯示 Build Status 與 Deployment Environment，讓 PM 能掌握進度。

### 5. ChatOps & Notifications (Slack/Teams)
*   **Signal over Noise:** 不要將所有 Pipeline 成功/失敗都推送到同一個大群組。
*   **Scoped Notifications:**
    *   `master` 分支失敗 $\rightarrow$ 推送至 Team Channel (緊急)。
    *   Feature 分支失敗 $\rightarrow$ 僅通知 Commit 作者 (透過 Email 或 Slack DM)。
*   **Interactive Notifications:** 使用 Slack App 整合，允許直接在 Slack 上點擊 "Approve Deployment"。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Shell Script Wrapper" (Shell 腳本包裝紙)
*   **Bad Practice:** 在 `.gitlab-ci.yml` 中只寫一行 `./run_all_logic.sh`，然後把所有邏輯（建置、測試、部署）都塞在那個 Shell Script 裡。
*   **Consequence:** 失去了 GitLab 的視覺化階段 (Stages)、並行執行 (Parallel execution)、快取 (Caching) 與錯誤重試 (Retry) 的能力。CI 變成了黑盒子。

### 2. Hardcoded Secrets (硬編碼憑證)
*   **Bad Practice:** 在遷移過程中，為了方便直接將 AWS Key 或 DB Password 寫在 YAML 或 Dockerfile 中。
*   **Correction:** 必須使用 GitLab CI/CD Variables (Masked & Protected) 或整合 HashiCorp Vault。

### 3. Ignoring Artifact Passing (忽略產物傳遞)
*   **Pitfall:** 在 Jenkins 中，Workspace 是保留的；但在 GitLab 中，每個 Job 預設是乾淨的環境。
*   **Consequence:** 下一個 Stage 找不到上一個 Stage 編譯好的檔案。
*   **Fix:** 明確定義 `artifacts` (paths) 與 `dependencies` (needs)。

### 4. Webhook Security Holes (Webhook 安全漏洞)
*   **Pitfall:** 開放 Webhook 接收外部觸發，但沒有驗證 `Secret Token`。
*   **Risk:** 任何人只要知道 URL 就能觸發你的 Pipeline 或部署流程。

---

## Checklists & workflows｜檢查清單與流程

### Migration Checklist (遷移檢查清單)

- [ ] **Inventory Audit (資產盤點):** 列出所有現存 Jenkins Jobs/GHA Workflows 及其依賴的 Plugins。
- [ ] **Secret Mapping (憑證對應):** 將舊系統的 Credentials 逐一建立為 GitLab CI/CD Variables。
- [ ] **Containerization (容器化):** 確認所有建置工具 (Java, Node, Python versions) 都有對應的 Docker Images。
- [ ] **Pipeline Translation (流程轉換):**
    - [ ] `Jenkins Stage` $\rightarrow$ `GitLab Stage`
    - [ ] `Jenkins Agent` $\rightarrow$ `GitLab Runner Tags` / `Image`
    - [ ] `Post Build Actions` $\rightarrow$ `artifacts` / `cache`
- [ ] **Parallel Validation (並行驗證):** 同時運行新舊 Pipeline，比對產出物 (Artifacts) 的 Hash 值是否一致。

### Integration Decision Tree (整合決策樹)

1.  **需要雙向同步嗎？ (Two-way sync?)**
    *   *Yes:* 使用官方 Integration (Jira, Slack App)。
    *   *No (One-way trigger):* 使用 Webhooks。
2.  **觸發源頭是什麼？**
    *   *Code Push/Merge:* 使用 GitLab Push Events Webhook。
    *   *External System Update:* 使用 GitLab API (`POST /projects/:id/trigger/pipeline`)。
3.  **安全性要求？**
    *   *High:* 設定 Webhook Secret Token + IP Whitelist。

---

## Real-world examples｜實戰案例

### Example 1: Jenkinsfile to .gitlab-ci.yml Translation

**Scenario:** 一個簡單的 Java Maven 專案遷移。

**Legacy (Jenkinsfile):**
```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('Test') {
            steps {
                sh 'mvn test'
            }
        }
    }
}
```

**Modern (GitLab CI):**
```yaml
# 使用 Docker Image 取代 agent 設定
image: maven:3.8-openjdk-11

stages:
  - build
  - test

variables:
  MAVEN_OPTS: "-Dmaven.repo.local=.m2/repository"

cache:
  paths:
    - .m2/repository

build_job:
  stage: build
  script:
    - mvn clean package -DskipTests
  artifacts:
    paths:
      - target/*.jar
    expire_in: 1 week

test_job:
  stage: test
  needs: ["build_job"] # 優化：明確依賴關係
  script:
    - mvn test
```
*Key Changes:* 引入了 `image`, `cache` (加速), `artifacts` (傳遞 Jar 檔), 與 `needs` (DAG 執行)。

### Example 2: Jira Integration Workflow

**Goal:** 當程式碼合併到 `main` 分支並部署到 Production 後，自動關閉 Jira Issue。

1.  **Configuration:** 在 GitLab `Settings > Integrations > Jira` 中填入 Jira URL 與 Auth Token。
2.  **Developer Action:**
    *   Commit message: `feat: add login page (Closes JIRA-456)`
3.  **GitLab Pipeline:**
    *   Pipeline 執行成功。
    *   GitLab 偵測到 `Closes JIRA-456` 關鍵字。
    *   GitLab 透過 API 在 Jira 上將 `JIRA-456` 加上 Comment: *"Deployed to Production in pipeline #12345"* 並將狀態移動至 **Done**。

### Example 3: Triggering GitLab Pipeline from External Webhook

**Scenario:** 當 CMS 系統 (Content Management System) 內容更新時，觸發 GitLab CI 重新建置靜態網站 (SSG)。

**Setup:**
1.  在 GitLab 專案設定 `Settings > CI/CD > Pipeline triggers`，新增一個 Token (e.g., `cms-trigger-token`).
2.  在 CMS 系統設定 Webhook URL:
    `https://gitlab.example.com/api/v4/projects/123/trigger/pipeline?token=cms-trigger-token&ref=main`

**Payload Handling (.gitlab-ci.yml):**
```yaml
deploy_cms_content:
  stage: deploy
  rules:
    - if: '$CI_PIPELINE_SOURCE == "trigger"' # 只在 API 觸發時執行
  script:
    - echo "CMS content updated. Rebuilding site..."
    - npm run build
    - npm run deploy
```