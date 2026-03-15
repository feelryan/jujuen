# 進階 CI/CD 設計模式與策略 / Advanced CI/CD Design Patterns and Strategies

## Mental model｜心智模型

要掌握 GitLab 的進階 CI/CD，必須從「線性流水線 (Linear Pipeline)」的思維轉變為「圖論與模組化 (Graph & Modularity)」的思維。

### 1. 從「工廠產線」到「交通路網」
- **傳統模式 (Stages)**：像是一條嚴格的工廠組裝線。所有 `Build` 階段的工作完成前，`Test` 階段絕對不會開始。這導致了「短板效應」——最慢的 Job 拖累了整個 Stage 的完成時間。
- **進階模式 (DAG - Directed Acyclic Graph)**：像是交通路網。只要前置條件（Dependency）滿足，車輛（Job）就可以出發，不需要等待其他無關的車輛。這就是 `needs` 關鍵字的核心邏輯。

### 2. 從「單體架構」到「微服務架構」
- **傳統模式 (.gitlab-ci.yml)**：所有的邏輯寫在一個巨大的 YAML 檔中，就像 Monolithic Application，難以維護且牽一髮動全身。
- **進階模式 (Parent-Child & Multi-project)**：將 CI/CD 拆解。
  - **Parent-Child**：像是 Monorepo 內部的模組化，主管（Parent）決定要把工作指派給哪個部門（Child Pipeline）。
  - **Multi-project**：像是微服務間的 API 呼叫，專案 A 完成後，觸發專案 B 進行整合測試或部署。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Monorepo 的「分而治之」模式 (The Divide and Conquer Pattern)
在 Monorepo（單一儲存庫包含多個服務）中，最常見的效能殺手是「改了前端文件，卻跑了後端測試」。

- **Solution**: 結合 `rules:changes` 與 `trigger` (Child Pipelines)。
- **Implementation**:
  - 在 Parent Pipeline 偵測變更檔案的路徑。
  - 僅觸發相關子專案的 Child Pipeline。
  - **Code Snippet**:
    ```yaml
    # .gitlab-ci.yml (Parent)
    trigger_backend:
      stage: triggers
      trigger:
        include: backend/.gitlab-ci.yml
        strategy: depend # 等待子流水線成功才算成功
      rules:
        - changes:
            - backend/**/*
    
    trigger_frontend:
      stage: triggers
      trigger:
        include: frontend/.gitlab-ci.yml
      rules:
        - changes:
            - frontend/**/*
    ```

### 2. 快速通道模式 (The Fast Lane / DAG)
打破 Stage 的順序限制，讓互不依賴的任務並行處理，顯著縮短 Feedback Loop。

- **Use Case**: `Deploy to Staging` 不需要等待 `Linting` 或 `Unit Tests` 全部跑完，只要 `Build` 完成即可（視風險策略而定）。
- **Implementation**: 使用 `needs` 關鍵字。
- **Code Snippet**:
  ```yaml
  build_job:
    stage: build
    script: echo "Building..."

  test_job:
    stage: test
    script: echo "Testing..."
    # 這裡沒有 needs，預設等待 build stage 完成

  deploy_job:
    stage: deploy
    script: echo "Deploying..."
    needs: ["build_job"] # 只要 build_job 完成就立刻開始，無視 test_job 進度
  ```

### 3. 動態流水線生成 (Dynamic Pipeline Generation)
當靜態 YAML 無法滿足需求（例如：根據資料夾動態產生 N 個微服務的測試 Job），可以使用程式碼生成 CI 設定檔。

- **Workflow**:
  1. **Job A**: 執行 Script (Python/Bash)，掃描專案結構，產出 `generated-ci.yml`。
  2. **Job B (Trigger)**: 使用 `trigger: include: artifact` 載入剛生成的 YAML。

### 4. 跨專案依賴鏈 (Cross-Project Dependency Chain)
適用於前後端分離或 Infrastructure-as-Code (IaC) 與應用程式分離的場景。

- **Pattern**: App Repo 建置完成 -> 觸發 Infra Repo (Ansible/Terraform) 進行部署 -> 觸發 E2E Test Repo 進行驗證。
- **Tip**: 善用 `variables` 傳遞版本號或 Image Tag 給下游專案。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 濫用 DAG 導致的「義大利麵依賴」(Spaghetti DAG)
- **Anti-pattern**: 過度使用 `needs`，導致 Job 之間的依賴關係錯綜複雜，難以視覺化與除錯。
- **Consequence**: 當 Pipeline 失敗時，很難追蹤是因為哪個前置 Job 失敗，或是邏輯錯誤。
- **Fix**: 保持 DAG 簡單，僅在「跨 Stage 且有顯著時間優勢」時使用。

### 2. 殭屍流水線 (The Zombie Trigger)
- **Anti-pattern**: 使用 `trigger` 但未設定 `strategy: depend`。
- **Consequence**: Parent Pipeline 觸發 Child 後立刻顯示「綠燈 (Passed)」，但實際上 Child Pipeline 正在跑甚至後來失敗了。這會導致 Merge Request 被錯誤地允許合併。
- **Fix**: 除非是「射後不理 (Fire and forget)」的通知型任務，否則務必加上 `strategy: depend`。

### 3. Artifacts 傳遞失誤 (The Missing Artifact)
- **Anti-pattern**: 在 DAG 模式下，Job B `needs` Job A，但忘記 Job A 和 Job B 可能跑在不同的 Runner 上，或者預設的 Artifact 下載行為被覆蓋。
- **Consequence**: Job B 找不到編譯好的檔案。
- **Fix**: 確保 `needs` 列表中包含產出 Artifact 的 Job，GitLab 會自動處理下載；若跨 Pipeline 則需使用 API 或 Package Registry 中轉。

### 4. 巢狀地獄 (Nested Include Hell)
- **Anti-pattern**: Parent include Child, Child include Grand-child... 層層疊疊超過 3 層。
- **Consequence**: 極難除錯，變數 (Variables) 的優先級繼承規則會變得非常混亂。
- **Fix**: 盡量保持扁平化，最多兩層（Parent -> Child）。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: 該用哪種模式？
在設計新的 Pipeline 架構時，請依序回答以下問題：

1. **是否為單一 Git Repository？**
   - **No** → 使用 **Multi-project Pipelines** (Bridge jobs)。
   - **Yes** → 繼續下一題。
2. **專案內是否包含多個獨立部署的模組（如 Monorepo）？**
   - **Yes** → 使用 **Parent-Child Pipelines** 配合 `rules:changes`。
   - **No** → 繼續下一題。
3. **是否有特定的 Job 執行時間很長，且後續步驟不需等待它？**
   - **Yes** → 在該路徑使用 **DAG (`needs`)**。
   - **No** → 使用標準的 **Stages** 即可（簡單即是美）。

### Implementation Checklist
- [ ] **Scope Check**: 使用 `rules:changes` 確保只有相關的程式碼變更才會觸發對應的 Pipeline。
- [ ] **Dependency Check**: 若使用了 `needs`，確認所有需要的 `artifacts` 來源都已列入。
- [ ] **Blocking Check**: 觸發 Child Pipeline 時，是否加上了 `strategy: depend` 以確保主流程能感知子流程的失敗？
- [ ] **Variable Propagation**: 跨專案觸發時，關鍵變數（如 `CI_COMMIT_TAG`, `IMAGE_TAG`）是否已正確傳遞？
- [ ] **Visualization**: 在 GitLab CI/CD 頁面查看 "Needs" tab 或 Pipeline Graph，確認依賴關係圖符合預期。

---

## Real-world examples｜實戰案例

### Scenario: Full-Stack Monorepo with Selective Testing

**情境**：一個 Repo 包含 `api` (Go), `web` (React), `docs` (Markdown)。
**目標**：
1. 修改 `docs` 時，只跑 Markdown Lint，不跑 Build。
2. 修改 `api` 時，跑 Go Test 並觸發 Integration Test。
3. 修改 `web` 時，跑 React Test。

**`.gitlab-ci.yml` (Root)**:

```yaml
stages:
  - triggers

# 只有文件變更時
docs-pipeline:
  stage: triggers
  trigger:
    include: docs/.gitlab-ci.yml
  rules:
    - changes:
        - docs/**/*

# 後端變更時
api-pipeline:
  stage: triggers
  trigger:
    include: api/.gitlab-ci.yml
    strategy: depend # 必須等待後端測試通過
  rules:
    - changes:
        - api/**/*
    - changes: # 如果共用庫變更，也要跑
        - lib/**/*

# 前端變更時
web-pipeline:
  stage: triggers
  trigger:
    include: web/.gitlab-ci.yml
    strategy: depend
  rules:
    - changes:
        - web/**/*
```

**`api/.gitlab-ci.yml` (Child - Using DAG)**:

```yaml
stages:
  - build
  - test
  - deploy

go-build:
  stage: build
  script: go build -o app ./cmd
  artifacts:
    paths: [app]

unit-test:
  stage: test
  script: go test ./...
  needs: [] # 不需要等待 build，可以平行開始 (假設不需要 binary)

integration-test:
  stage: test
  script: ./run-integration-tests.sh
  needs: ["go-build"] # 需要 build 完的 binary

deploy-dev:
  stage: deploy
  script: ./deploy.sh
  needs: ["go-build", "unit-test"] # Build 好且單元測試過就部署，整合測試可以在背景跑
  environment: dev
```

此案例展示了如何結合 **Parent-Child** 來隔離關注點，並在子流水線中利用 **DAG** 來加速開發者的反饋循環。