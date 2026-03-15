# GitLab 核心運作機制與心智模型 / Core Mental Models and Operational Mechanisms

本章節旨在建立正確的 GitLab 運作心智模型。許多 CI/CD 或權限管理的錯誤，往往源自於對「繼承機制」、「流水線狀態機」或「資源生命週期」的誤解。掌握這些模型，能讓你從「寫 Script」進階到「設計系統」。

---

## Mental model｜心智模型

### 1. The Inheritance Tree: Group vs. Project
**繼承樹模型：群組與專案**

將 GitLab 的結構想像成一個 **Linux 檔案系統**，但具備更強的屬性繼承能力：
*   **Group (Folder)**: 管理邊界。它是權限 (Members)、變數 (Variables)、標籤 (Labels) 與 Runner 的容器。
*   **Project (File)**: 執行單元。它是程式碼 (Repository)、流水線 (Pipeline) 與 Issue 的實際載體。

> **Key Insight**: 變數與權限是 **由上而下 (Cascading)** 流動的。在 Root Group 設定的 CI/CD 變數，預設會被所有子專案繼承。這對於管理 AWS Keys 或 Docker Registry 憑證至關重要。

### 2. The Event-Driven State Machine: CI/CD
**事件驅動狀態機：CI/CD 流水線**

不要將 `.gitlab-ci.yml` 視為單純的 Shell Script 集合，它是一個 **事件驅動的狀態機 (Event-Driven State Machine)**。
*   **Trigger (Event)**: 每個 Pipeline 都是由特定事件觸發的（如 `push`, `merge_request`, `schedule`, `api`）。
*   **Filter (Rules)**: 系統會根據 `rules` 決定哪些 Job 應該進入這個狀態機。
*   **Flow (DAG vs. Stages)**: 傳統模式是同步的 Stages（所有 Test 跑完才跑 Deploy）；現代模式是有向無環圖 (DAG)，只要相依性 (`needs`) 滿足，Job 就會立即執行。

### 3. Ephemeral vs. Persistent: Artifacts & Cache
**短暫與持久：產物與快取**

這是最常被混淆的概念，請用以下模型區分：
*   **Cache (快取)**: 為了 **加速**。屬於「盡力而為 (Best-effort)」的儲存，Runner 之間不一定共享，隨時可能消失也不應影響建置成功率 (e.g., `node_modules`, `.m2`).
*   **Artifacts (產物)**: 為了 **傳遞** 與 **封存**。屬於「保證存在」的儲存，用於 Job 之間傳遞資料 (Build -> Test) 或供人類下載 (APK, JAR)。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 階層式變數管理 (Hierarchical Variable Management)
不要在每個 Project 裡重複設定 `AWS_ACCESS_KEY_ID`。
*   **Pattern**:
    *   **Instance/Root Group Level**: 設定全域通用的設定（如 Proxy, Internal Registry URL）。
    *   **Sub-group Level (e.g., Backend Team)**: 設定該團隊共用的 Deploy Keys 或 Cloud Credentials。
    *   **Project Level**: 僅設定該專案特有的變數（如 `APP_VERSION`）。
*   **Why**: 減少維護成本，並降低金鑰洩漏風險（越少地方設定越好）。

### 2. DAG (Directed Acyclic Graph) over Stages
儘量使用 `needs` 關鍵字來打破 `stages` 的同步阻塞。
*   **Pattern**:
    ```yaml
    build_a:
      stage: build
    test_a:
      stage: test
      needs: ["build_a"] # 不需等待 build_b 完成即可開始
    ```
*   **Why**: 加速回饋循環。如果 `build_b` 很慢，不應該卡住 `test_a` 的執行。

### 3. Merge Request Pipelines (Detached Pipelines)
優先使用 Merge Request Pipelines 而非 Branch Pipelines。
*   **Pattern**: 在 `rules` 中明確指定 `if: $CI_PIPELINE_SOURCE == 'merge_request_event'`。
*   **Why**:
    *   避免重複執行（Push 到 Branch 同時開 MR，預設會跑兩條 Pipeline）。
    *   可以使用 "Merged Results Pipelines"（模擬 Merge 後的結果進行測試，確保 Main branch 永遠是綠的）。

### 4. Artifacts 最小化策略
*   **Pattern**: 明確設定 `expire_in`，並嚴格限制 `paths`。
    ```yaml
    artifacts:
      paths: ["dist/"] # 只保留編譯結果，不要保留整個 repo
      expire_in: 1 week # 預設短期保留
      when: always
    ```
*   **Why**: 避免 GitLab Server 儲存空間爆炸。Git Object (Repo) 的增長通常緩慢，但 Artifacts 的增長是指數級的。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "God Group" (扁平化地獄)
*   **Anti-pattern**: 將所有專案都直接放在頂層 Group 下，或是完全不使用 Sub-groups。
*   **Consequence**: 當公司擴張，需要區分 "SRE Team" 與 "Frontend Team" 的權限時，必須逐一修改數百個專案的 Members 設定。

### 2. Cache as Artifacts (誤用快取傳遞資料)
*   **Anti-pattern**: 試圖用 `cache` 在 Build Job 和 Deploy Job 之間傳遞編譯好的 Binary 檔。
*   **Consequence**: 隨機失敗。如果 Build Job 和 Deploy Job 被調度到不同的 Runner（或 Docker 容器重建），Cache 可能為空，導致部署失敗。**Job 間傳遞資料必須用 Artifacts。**

### 3. Hardcoded Secrets in `.gitlab-ci.yml`
*   **Anti-pattern**: `script: - docker login -u user -p password ...`
*   **Consequence**: 即使是 Private Repo，這也是極大的安全漏洞。Git 歷史紀錄是永久的。**必須使用 CI/CD Variables (Masked & Protected)。**

### 4. Overusing `dependencies: []`
*   **Anti-pattern**: 忘記在不需要前一階段產物的 Job（如 Linter）設定 `dependencies: []`。
*   **Consequence**: 預設情況下，GitLab 會下載前一階段 **所有** Job 的 Artifacts。這會浪費大量的頻寬與 I/O 時間。

---

## Checklists & workflows｜檢查清單與流程

### Project Initialization Checklist (新專案設定檢核)
- [ ] **Visibility**: 確認專案可見性 (Private/Internal/Public) 符合資安規範。
- [ ] **Inheritance**: 檢查 Group 層級的變數是否正確繼承，是否有變數名稱衝突 (Precedence: Project > Group > Instance)。
- [ ] **Runners**: 確認專案已啟用正確的 Shared Runners 或特定的 Group Runners (Tags)。
- [ ] **Cleanup Policy**: 啟用 "Settings -> CI/CD -> Artifacts" 的自動清理策略，避免儲存空間溢出。

### Pipeline Debugging Workflow (流水線除錯流程)
當 Pipeline 沒有如預期觸發或執行時：
1.  **Check Syntax**: 使用 CI Lint 工具檢查語法錯誤。
2.  **Check Rules**:
    *   變數 `$CI_PIPELINE_SOURCE` 是什麼？(push, web, merge_request_event?)
    *   是否使用了 `changes` 但 Git 偵測不到變更？
3.  **Check Tags**: Job 設定的 `tags` 是否有對應的 Runner 在線上 (Online)？
4.  **Check Permissions**: 執行 Job 的 User (Triggerer) 是否有權限存取該環境或變數 (Protected Branches/Variables)？

---

## Real-world examples｜實戰案例

### Scenario: Microservices Monorepo with Group-Level Governance
**場景：微服務 Monorepo 與群組級治理**

假設你正在管理一個包含 3 個微服務的系統。

#### 1. Group Structure (結構設計)
```text
my-company (Root Group)
├── devops-tools (Project) -> 存放共用的 CI Templates
├── backend (Sub-group) -> 設定變數: AWS_ROLE_ARN
│   ├── user-service (Project)
│   ├── payment-service (Project)
│   └── inventory-service (Project)
└── frontend (Sub-group)
```

#### 2. CI/CD Configuration (核心配置)
在 `user-service/.gitlab-ci.yml` 中，我們引用共用模板並覆寫部分行為：

```yaml
include:
  - project: 'my-company/devops-tools'
    file: '/templates/microservice-base.yml'

variables:
  SERVICE_NAME: "user-service"

# 實踐 DAG 模式
test:unit:
  stage: test
  script: npm run test

build:image:
  stage: build
  script: docker build -t $REGISTRY/$SERVICE_NAME:$CI_COMMIT_SHA .
  # 這裡不需要等待 test:unit 完成，除非你有政策要求
  
deploy:staging:
  stage: deploy
  needs: ["build:image", "test:unit"] # 明確依賴：Image 建好且測試通過才部署
  script: ./deploy_script.sh
  environment: staging
```

#### 3. Operational Insight (運作洞察)
*   **變數繼承**: `deploy:staging` Job 執行時，會自動讀取 `backend` Group 設定的 `AWS_ROLE_ARN` 來進行部署驗證。
*   **Artifacts**: `build:image` 不需要產出 Artifacts (因為 Image 推送到 Registry 了)，但 `test:unit` 產出了 JUnit XML Report (Artifacts) 供 GitLab UI 顯示測試報告。
*   **Cache**: `npm install` 的結果被放在 Cache 中，加速下一次 Pipeline，但不會傳遞給 `deploy:staging`。