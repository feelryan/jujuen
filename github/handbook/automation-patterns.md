# 自動化設計模式與最佳實踐 / Automation Design Patterns & Best Practices

## Mental model｜心智模型

在深入 GitHub Actions 的具體語法之前，我們需要建立一個關於「自動化架構」的正確心智模型。許多工程師將 CI/CD 視為「一長串的 Shell Script」，這導致了難以維護的 `main.yaml` 巨石（Monolith）。

高效的自動化設計應具備以下特質：

1.  **模組化 (Modularity as Lego Blocks)**：
    將流程拆解為可重用的單元。不要把所有邏輯寫在一個 workflow 檔案中。
    *   **Composite Actions** 是你的「自定義指令」或「函數」（Function），處理**步驟（Steps）**層級的封裝。
    *   **Reusable Workflows** 是你的「流程模版」或「類別」（Class），處理**作業（Jobs）**層級的封裝。

2.  **宣告式矩陣 (Declarative Matrix)**：
    不要寫迴圈（Loop），而是定義維度（Dimensions）。讓 GitHub 的調度器幫你處理並行（Parallelism）與組合爆炸。

3.  **依賴反轉 (Inversion of Control)**：
    工作流應定義「它需要什麼（Inputs/Secrets）」，而不是硬編碼「它從哪裡拿」。這讓同一個 Workflow 可以輕易地在 Dev、Staging、Prod 環境間切換。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. The "Centralized Pipeline" Pattern (Reusable Workflows)
**適用場景：** 多個微服務（Microservices）或儲存庫共用相同的 CI/CD 標準。

不要在每個 Repo 裡複製貼上相同的 Build/Test 邏輯。建立一個專門的 `infrastructure` 或 `.github` 儲存庫，存放通用的 Workflow。

*   **實作重點**：
    *   使用 `on: workflow_call` 定義輸入參數（Inputs）與密鑰（Secrets）。
    *   呼叫端只需提供變數，無需關心實作細節。
    *   利用 `secrets: inherit` 簡化密鑰傳遞，或顯式傳遞以落實最小權限原則。

```yaml
# 呼叫端 (Caller) - repo-a/.github/workflows/ci.yml
jobs:
  build-and-test:
    uses: my-org/infra-workflows/.github/workflows/standard-node-ci.yml@v1
    with:
      node-version: '18'
    secrets: inherit # 或指定特定 secret
```

### 2. The "Setup Action" Pattern (Composite Actions)
**適用場景：** 幾乎每個 Job 都要重複的前置作業（如：Checkout + Setup Node + Cache + Auth）。

將重複的 5-10 行 setup 步驟封裝成一個 Composite Action。這能讓主 Workflow 的業務邏輯更加清晰。

*   **實作重點**：
    *   封裝繁瑣的 Cache Key 計算邏輯。
    *   統一處理 Private Registry 的認證。

```yaml
# action.yml (Composite Action)
name: 'Setup Node & Cache'
runs:
  using: "composite"
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
        cache: 'npm'
    - run: npm ci
      shell: bash # Composite Action 必須指定 shell
```

### 3. The "Dynamic Matrix" Pattern (Job Sharding)
**適用場景：** Monorepo 測試、大型測試套件的分片執行（Sharding）。

當靜態的 `strategy: matrix` 無法滿足需求時（例如：只想測試有變動的 Packages），可以先用一個 Job 計算出需要的矩陣，再傳給下一個 Job。

*   **實作重點**：
    *   Job A：分析變更，輸出 JSON 格式的陣列（例如 `['pkg-a', 'pkg-c']`）。
    *   Job B：使用 `${{ fromJson(needs.jobA.outputs.matrix) }}` 作為矩陣來源。

### 4. Path Filtering & Concurrency Control
**適用場景：** 節省資源與避免無效構建。

*   **Path Filtering**：使用 `paths` 或 `paths-ignore` 確保修改 `README.md` 不會觸發後端部署。
*   **Concurrency**：確保同一個 PR 的舊 Commit 自動取消執行，節省 Action Minutes。

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Hidden Logic" Trap (過度使用 Composite Actions)
*   **反模式**：試圖在 Composite Action (`action.yml`) 裡面寫複雜的 `if-else` 邏輯。
*   **後果**：Composite Actions 不支援 `steps.if` 的完整功能，導致必須寫醜陋的 Shell Script 邏輯 (`run: if [ "$VAR" == "true" ]; then ... fi`)，難以除錯且跨平台相容性差。
*   **修正**：如果邏輯太複雜，請改寫成 JavaScript Action 或將其提升至 Workflow 層級處理。

### 2. The "Untagged Reference" Risk (不鎖定版本)
*   **反模式**：引用 Action 時使用 `@main` 或 `@master`（例如 `uses: actions/checkout@main`）。
*   **後果**：上游更新若包含 Breaking Change，你的 CI 會突然全線崩潰。
*   **修正**：生產環境務必使用具體版本號（`@v2.1.0`）或 Commit SHA。對於內部信任的 Reusable Workflows，至少鎖定 Major Version（`@v1`）。

### 3. Hardcoded Secrets in Workflows
*   **反模式**：直接在 YAML 檔案中寫死 Token 或密碼，或者使用 Base64 編碼但仍放在 Code 裡。
*   **後果**：資安洩漏。一旦 Commit 進入 Git History，就必須視為已洩漏並撤銷。
*   **修正**：嚴格使用 `${{ secrets.MY_SECRET }}`。

### 4. Matrix Explosion (矩陣爆炸)
*   **反模式**：定義了過多維度（OS x Node Version x Browser x Database），導致一次 Commit 觸發 100+ 個 Jobs。
*   **後果**：耗盡 GitHub Actions 免費額度或預算，且排隊時間過長。
*   **修正**：使用 `include` 僅加入必要的組合，或使用 `exclude` 排除無效組合（例如 Windows + iOS build）。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: 如何選擇封裝方式？

1.  **我需要重用的是「一系列步驟 (Steps)」還是「整個作業 (Job)」？**
    *   步驟 -> **Composite Action**
    *   作業 -> **Reusable Workflow**
2.  **我是否需要使用 Secrets？**
    *   是，且希望由呼叫者控制 -> **Reusable Workflow** (支援 `secrets: inherit`)
    *   是，但作為參數傳入 -> **Composite Action** (必須透過 `inputs` 傳入，不能直接存取 `secrets` context)
3.  **我是否需要在多個 Repo 間共用？**
    *   是 -> 建立獨立的 `.github` 公共儲存庫並發布 Release Tag。

### Workflow Code Review Checklist

- [ ] **觸發條件優化**：是否設定了 `paths-ignore` 以避免修改文件觸發部署？
- [ ] **資源管理**：是否設定了 `concurrency` 以取消過時的構建？
- [ ] **權限最小化**：是否在 Job 層級明確定義了 `permissions`（例如 `contents: read`, `id-token: write`）？
- [ ] **版本鎖定**：所有的 `uses` 是否都指定了 Tag 或 SHA？
- [ ] **Timeout 設定**：是否為每個 Job 設定了 `timeout-minutes` 以防止卡死的 Job 耗盡額度？
- [ ] **機密處理**：是否確保沒有在 Log 中印出 Secrets（注意 `set -x` 或除錯輸出的內容）？

---

## Real-world examples｜實戰案例

### Example 1: The "Golden Path" Deployment (Reusable Workflow)

這是一個標準化的部署流程，強制執行 Lint、Test，並根據環境變數決定部署目標。

```yaml
# .github/workflows/deploy-template.yml
name: Reusable Deployment
on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
      artifact-name:
        required: true
        type: string
    secrets:
      AWS_ROLE_ARN:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }} # 使用 GitHub Environments 保護
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: ${{ inputs.artifact-name }}
      
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: us-east-1
          
      - name: Deploy
        run: ./deploy-script.sh
```

### Example 2: Monorepo Smart Matrix Strategy

假設你有一個 Monorepo 包含 `frontend`, `backend`, `worker`。此模式僅針對有變動的服務執行測試。

```yaml
# .github/workflows/ci.yml
jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set-matrix.outputs.matrix }}
    steps:
      - uses: actions/checkout@v4
      - id: set-matrix
        run: |
          # 這裡可以使用 `dorny/paths-filter` 或自定義腳本
          # 假設輸出為 JSON string: ["frontend", "backend"]
          CHANGES=$(./scripts/detect-changes.sh)
          echo "matrix=$CHANGES" >> $GITHUB_OUTPUT

  test:
    needs: detect-changes
    if: ${{ needs.detect-changes.outputs.matrix != '[]' }}
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: ${{ fromJson(needs.detect-changes.outputs.matrix) }}
    steps:
      - uses: actions/checkout@v4
      - name: Test ${{ matrix.service }}
        run: cd ${{ matrix.service }} && npm test
```