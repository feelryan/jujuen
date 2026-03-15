# 1. 前言與學習目標 (Introduction and Learning Objectives)

對於資深工程師而言，GitHub Actions 不僅僅是一個執行 `npm test` 的腳本執行器，而是現代化軟體交付供應鏈（Software Delivery Supply Chain）的核心骨幹。本章旨在協助你從「撰寫腳本」的思維，轉變為「架構 CI/CD 系統」的思維。

For senior engineers, GitHub Actions is more than just a script runner for `npm test`; it is the backbone of the modern software delivery supply chain. This chapter aims to shift your mindset from "scripting" to "architecting CI/CD systems."

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **設計高併發測試策略 (Design High-Concurrency Testing Strategies)**：利用 Matrix Builds 與並行處理（Parallelism）大幅縮短 Feedback Loop。
2.  **優化構建效能與成本 (Optimize Build Performance & Cost)**：實作進階 Caching 策略與依賴管理，並理解何時該引入 Self-hosted Runners。
3.  **模組化 Pipeline 架構 (Modularize Pipeline Architecture)**：使用 Reusable Workflows 與 Composite Actions 來解決 "YAML Hell" 問題，提升可維護性。
4.  **確保生產環境穩定性 (Ensure Production Stability)**：透過 Concurrency Control 與 Environment Protection Rules 管理部署風險。

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 事件驅動的短暫容器 (Event-Driven Ephemeral Containers)

與傳統 Jenkins Server（通常是 Stateful、長期運行的寵物伺服器）不同，GitHub Actions 的心智模型應建立在 **"Ephemeral"（短暫/無狀態）** 與 **"Event-Driven"（事件驅動）** 之上。

Unlike traditional Jenkins Servers (often stateful, long-running pet servers), the mental model for GitHub Actions should be built on being **"Ephemeral" (stateless)** and **"Event-Driven"**.

-   **Event (Trigger):** 這是啟動 Pipeline 的信號（如 `push`, `pull_request`, `workflow_dispatch`）。
-   **Runner:** 這是無狀態的計算單元。每次 Job 啟動時，你得到的是一個全新的環境（除非使用 Self-hosted 且未清除 workspace，但不建議依賴此行為）。
-   **Implication:** 因為環境是全新的，所以 **Caching（快取）** 不是「選配」，而是效能優化的「標配」。

## 2.2 工作流程拓撲 (Workflow Topology)

將你的 Pipeline 視為一個 **DAG (Directed Acyclic Graph，有向無環圖)**。

View your pipeline as a **DAG (Directed Acyclic Graph)**.

-   **Jobs:** 圖中的節點（Nodes）。預設情況下並行執行（Parallel execution）。
-   **Needs:** 定義邊（Edges）與依賴關係。例如 `deploy` job 依賴於 `build` 與 `test` jobs 成功完成。
-   **Matrix:** 節點的動態扇出（Fan-out）。單一 Job 定義可在執行時擴展為多個並行 Job。

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型分散式系統或 Monorepo 架構中，CI/CD 的設計直接影響開發效率（Developer Experience, DX）與營運成本。

In large-scale distributed systems or Monorepo architectures, CI/CD design directly impacts Developer Experience (DX) and operational costs.

## 3.1 架構決策：GitHub-hosted vs. Self-hosted Runners

| Feature | GitHub-hosted Runners | Self-hosted Runners (e.g., K8s ARC) |
| :--- | :--- | :--- |
| **Maintenance** | Zero (Managed by GitHub) | High (OS patching, scaling, security) |
| **Security** | Isolated VMs (High isolation) | Network access to internal VPC/DBs |
| **Performance** | Standard specs (2-core to 64-core) | Customizable (GPU, High-Memory, Persistent SSD) |
| **Cost** | Per minute billing | Infrastructure cost + Management overhead |

**System Design Tip:**
在系統設計面試或實務中，若需存取私有網路資源（如 AWS VPC 內的 RDS 進行整合測試），或需要特殊的硬體（如 ML 模型訓練需 GPU），**Self-hosted Runners** 是標準答案。對於一般的 Lint/Unit Test，GitHub-hosted 則因維護成本低而勝出。

In system design interviews or practice, if access to private network resources (like RDS in AWS VPC for integration tests) or specialized hardware (like GPUs for ML training) is required, **Self-hosted Runners** are the standard answer. For general Lint/Unit Tests, GitHub-hosted wins due to low maintenance overhead.

## 3.2 企業級 Pipeline 架構 (Enterprise Pipeline Architecture)

一個成熟的 Pipeline 設計通常包含三層：

A mature pipeline design typically consists of three layers:

1.  **Trigger Layer:** 過濾事件（如 `paths-ignore`），避免修改 README 文件也觸發部署。
2.  **Integration Layer (CI):** 高度並行化。使用 Matrix 測試不同版本，利用 Cache 加速 `npm install` 或 `docker build`。
3.  **Deployment Layer (CD):** 序列化執行。使用 `concurrency` 確保部署順序，使用 OIDC (OpenID Connect) 取代長期 Access Keys 進行雲端驗證。

---

# 4. 逐步示例 (Walkthrough / Example)

## 情境 (Scenario)

我們有一個 Node.js 微服務，需要：
1. 在 Node 18 和 20 上運行測試。
2. 僅在 `main` 分支合併後，構建 Docker Image 並推送到 AWS ECR。
3. 確保同一分支的舊構建自動取消，避免資源浪費。

We have a Node.js microservice that needs to:
1. Run tests on Node 18 and 20.
2. Build a Docker image and push to AWS ECR only after merging to the `main` branch.
3. Ensure old builds on the same branch are automatically cancelled to save resources.

## 架構化實作 (Architected Implementation)

```yaml
name: Production CI/CD

# 1. Event Triggers & Path Filtering
# 避免非程式碼更動觸發昂貴的 Pipeline
on:
  push:
    branches: [ "main" ]
    paths-ignore: [ "**.md", "docs/**" ]
  pull_request:
    branches: [ "main" ]

# 2. Concurrency Control
# 如果開發者連續 push 兩次，第一次的 build 會被自動取消
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  # 3. Matrix Testing Strategy
  test:
    name: Test on Node ${{ matrix.node-version }}
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false # 其中一個版本失敗不影響其他版本繼續跑完
      matrix:
        node-version: [18.x, 20.x]

    steps:
      - uses: actions/checkout@v4
      
      # 4. Advanced Caching
      # setup-node 內建了 cache 功能，比手動寫 actions/cache 更簡潔
      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm' # 自動處理 package-lock.json hash

      - name: Install Dependencies
        run: npm ci # 使用 ci 而非 install，確保 deterministic build

      - name: Run Tests
        run: npm test

  # 5. Deployment (Conditional & Sequential)
  build-and-deploy:
    needs: test # 必須等測試通過
    if: github.ref == 'refs/heads/main' # 只在 main 分支執行
    runs-on: ubuntu-latest
    permissions:
      id-token: write # 必要：為了 OIDC 驗證
      contents: read

    steps:
      - uses: actions/checkout@v4

      # 6. Security: OIDC Authentication (No Long-lived Keys)
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActionRole
          aws-region: us-east-1

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build, tag, and push image to Amazon ECR
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: my-app
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
```

### 關鍵設計解析 (Key Design Analysis)
-   **Concurrency Group:** 解決了資源浪費問題。在大型團隊中，這能節省顯著的 GitHub Actions 分鐘數。
-   **Matrix `fail-fast: false`:** 在收集測試數據時很有用。即使 Node 18 失敗，我們仍想知道 Node 20 是否通過，以便判斷是語法兼容性問題還是邏輯錯誤。
-   **OIDC (OpenID Connect):** 這是資深工程師必須掌握的安全實踐。我們不再將 `AWS_ACCESS_KEY_ID` 存放在 GitHub Secrets 中，而是讓 GitHub 透過 JWT Token 與 AWS IAM 交換臨時權限。

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 濫用 Cache 或 Key 設計不良 (Cache Abuse or Poor Key Design)
-   **Anti-pattern:** 使用過於寬泛的 Cache Key（如僅用 `os` 作為 key），導致依賴更新後，CI 仍然拉取舊的 `node_modules`。
-   **Correction:** Cache Key 必須包含依賴鎖定檔案的 Hash。
    -   ❌ `key: ${{ runner.os }}-node-modules`
    -   ✅ `key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}`

## 5.2 忽視 Reusable Workflows (Ignoring Reusable Workflows)
-   **Anti-pattern:** 在 10 個微服務的 Repo 中複製貼上相同的 deploy 邏輯。當需要更新 AWS 認證方式時，必須修改 10 個地方。
-   **Correction:** 建立一個中心化的 `infrastructure` repo，定義 `workflow_call`，讓所有微服務引用標準化的部署流程。這符合 **DRY (Don't Repeat Yourself)** 原則。

## 5.3 在 CI 中依賴外部不穩定資源 (Depending on Flaky External Resources)
-   **Anti-pattern:** 在測試步驟中直接呼叫外部 API（如 Stripe Sandbox 或第三方 Weather API）。
-   **Correction:** 使用 **Mocking** 或 **Service Virtualization**。CI 環境應該是密封且確定性的（Hermetic and Deterministic）。外部網路波動不應導致 Deployment 失敗。

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

這些問題可用於面試候選人，或在團隊內部進行架構審查。

These questions can be used to interview candidates or conduct architecture reviews within the team.

## Q1: 如何優化一個執行時間超過 30 分鐘的 CI Pipeline？
**How would you optimize a CI pipeline that takes over 30 minutes to run?**

-   **Key Points:**
    1.  **Parallelism:** 檢查是否有可以並行執行的 Job（如 Lint, Unit Test, Build）。
    2.  **Caching:** 確認 `node_modules`、Docker Layers 是否有效被 Cache。
    3.  **Test Splitting:** 使用 Matrix 或 Sharding 將大型測試套件（Test Suite）拆分到多個機器上同時跑。
    4.  **Artifacts:** 避免在 Job 之間傳遞過大的 Artifacts（上傳/下載非常耗時）。

## Q2: 在高度管制的環境（如金融業）使用 GitHub Actions，你會如何設計安全性？
**How would you design security for GitHub Actions in a highly regulated environment (e.g., Finance)?**

-   **Key Points:**
    1.  **Self-hosted Runners:** 確保程式碼不離開私有網路，且 Runner 是短暫的（Ephemeral）或定期重置。
    2.  **OIDC:** 嚴格禁止長期憑證（Long-lived credentials）。
    3.  **Environment Protection Rules:** 強制要求 Manual Approval（人工審核）才能部署到 Production。
    4.  **Pinned Actions:** 引用第三方 Action 時使用 Commit SHA 而非 Tag（如 `uses: actions/checkout@a1b2c3d`），防止供應鏈攻擊。

## Q3: 比較 GitHub Actions 與 Jenkins，你會在什麼情況下選擇 Jenkins？
**Compare GitHub Actions with Jenkins. When would you choose Jenkins?**

-   **Key Points:**
    -   雖然 GitHub Actions 是現代首選，但 Jenkins 在以下場景仍有優勢：
        1.  極度複雜的 Legacy Pipeline，依賴大量的 Groovy Scripting。
        2.  完全地端（On-premise）環境，無法連線到 GitHub Cloud。
        3.  需要極細粒度的權限控制（Per-job permission），雖然 GitHub 也在改進此點。
    -   *資深觀點：* 大多數新專案應首選 GitHub Actions 以降低維護成本。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 記憶錨點 (Key Takeaways)
1.  **Event-Driven:** 理解 GitHub Actions 是基於事件觸發的短暫容器環境。
2.  **Matrix & Concurrency:** 利用 Matrix 進行扇出測試，利用 Concurrency 節省成本。
3.  **Caching Strategy:** 正確的 Cache Key 是效能優化的關鍵。
4.  **Security First:** 使用 OIDC 取代 Secrets，使用 SHA Pinning 防止供應鏈攻擊。
5.  **Reusability:** 善用 Composite Actions 和 Reusable Workflows 進行標準化治理。

## 後續延伸 (Next Steps)
-   **Advanced:** 研究 **Custom Docker Actions**，當你需要封裝複雜的工具鏈（Toolchain）時，這是比 Composite Actions 更強大的選擇。
-   **Observability:** 探索如何將 GitHub Actions 的 Metrics（執行時間、失敗率）匯出到 Datadog 或 Prometheus，建立 CI/CD 的可觀測性儀表板。
-   **Next Chapter:** 進入 **Chapter 03: Security & Supply Chain**，深入探討 CodeQL、Dependabot 與 SBOM (Software Bill of Materials)。