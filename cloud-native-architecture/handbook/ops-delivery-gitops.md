# 現代化交付：GitOps 與漸進式部署 / Modern Delivery: GitOps & Progressive Deployment

## Mental model｜心智模型

在傳統的 CI/CD 思維中，部署往往被視為一個「動作（Action）」或「腳本（Script）」，例如 Jenkins 執行 `kubectl apply`。但在雲原生架構下，我們必須轉變心智模型：**部署不是動作，而是狀態的收斂（Convergence of State）。**

### 1. 宣告式狀態與控制迴圈 (Declarative State & Control Loop)
GitOps 的核心並非只是「把 YAML 放在 Git 裡」，而是利用 Kubernetes 的 **Reconciliation Loop (調和迴圈)** 機制。
- **Desired State (期望狀態)**：儲存在 Git 中的 Manifests (Helm/Kustomize)，這是唯一的真理來源 (Single Source of Truth)。
- **Actual State (實際狀態)**：Cluster 中正在運行的 Pods/Services。
- **The Operator**：GitOps Agent (如 ArgoCD, Flux) 不斷比對兩者。一旦發現差異 (Drift)，便自動將實際狀態修正為期望狀態。

### 2. CI 與 CD 的職責分離 (Decoupling CI and CD)
- **CI (Continuous Integration)**：負責產出 **不可變的 Artifact (Immutable Artifacts)**，例如 Docker Image。CI 的終點是 Image Registry，而不是生產環境。
- **CD (Continuous Delivery)**：負責監測 Git Config 的變化，並將 Artifact 應用到環境中。CD 是 Pull-based (從 Cluster 內部拉取設定)，而非傳統的 Push-based (外部 Server 擁有 Cluster Admin 權限)。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 儲存庫策略：應用程式碼與配置分離 (App Code vs. Config Code)
不要將 Kubernetes Manifests 直接放在應用程式原始碼的 Repo 中。
- **Pattern**: **Separate Repositories**
    - `app-repo`: 包含原始碼、Dockerfile、Unit Tests。CI Pipeline 成功後會 Build Image 並 Push 到 Registry。
    - `config-repo` (GitOps Repo): 包含 Helm Charts、Kustomize files。CI Pipeline (或自動化工具) 會更新此處的 Image Tag。
- **Why**: 避免無限迴圈 (Commit 觸發 Build，Build 更新 YAML 觸發 Commit...)，且能更清晰地管理 Access Control (開發者不一定需要 Prod Config 的寫入權限)。

### 2. 漸進式部署策略 (Progressive Deployment Strategies)
不要直接做 "Big Bang" 更新，利用 Traffic Splitting 降低風險。

- **Blue-Green Deployment (藍綠部署)**
    - **適用場景**：不兼容的 API 變更、需要瞬間切換流量。
    - **機制**：同時運行 v1 (Blue) 與 v2 (Green) 全量資源。測試通過後，Load Balancer/Service 瞬間切換指向。
    - **代價**：資源消耗加倍 (Double Resource Usage)。

- **Canary Deployment (金絲雀部署)**
    - **適用場景**：大部分日常功能更新。
    - **機制**：先導入少量流量 (e.g., 5%) 給新版本，觀察指標 (Error Rate, Latency)。若正常則逐步增加 (Step: 5% -> 20% -> 50% -> 100%)。
    - **關鍵**：必須結合 **Automated Analysis** (如 Prometheus Metrics)，而非人工盯著 Dashboard。

### 3. 環境管理：Kustomize vs. Helm
- **Kustomize (Overlay Pattern)**：適合差異不大的環境。透過 `base` 與 `overlays/dev`, `overlays/prod` 進行 Patch。優點是可讀性高，無 Template 複雜度。
- **Helm (Template Pattern)**：適合需要封裝成產品分發，或環境差異極大需要複雜邏輯判斷時。建議使用 `Helm + Kustomize` 混合模式 (Helm 產生 Base，Kustomize 進行最後微調)。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "ClickOps" Trap (手動修改叢集)
- **Anti-pattern**: 工程師為了緊急修復，直接使用 `kubectl edit` 或 Dashboard 修改線上的 Deployment。
- **Consequence**: Git 中的狀態與 Cluster 狀態脫鉤 (Configuration Drift)。下一次 GitOps Sync 時，手動修改會被無情覆蓋，導致問題重現。
- **Fix**: 嚴格禁止寫入權限，所有變更必須走 Git Commit。緊急情況可使用 "Hotfix Branch" 流程。

### 2. Secrets in Plain Text (明文金鑰)
- **Anti-pattern**: 將 `Secret` yaml 直接 commit 到 Git。
- **Consequence**: 安全漏洞。即使刪除 commit 紀錄也難以清除。
- **Fix**: 使用 **Sealed Secrets** (將加密後的 Secret 存入 Git，只有 Cluster 內的 Controller 能解密) 或 **External Secrets Operator** (從 AWS Secrets Manager / HashiCorp Vault 同步)。

### 3. Ignoring Database Schema Changes (忽略資料庫遷移)
- **Anti-pattern**: 應用程式 rollback 了，但資料庫 schema 已經變更 (不向下相容)，導致舊版程式崩潰。
- **Fix**: 資料庫變更必須遵循 **N-1 Compatibility** 原則。
    - Step 1: DB Schema 變更 (新增欄位，不刪除舊欄位)。
    - Step 2: 部署新版 App (使用新欄位)。
    - Step 3: (確認穩定後) 清理舊欄位。

### 4. Over-reliance on "Latest" Tag
- **Anti-pattern**: Image tag 使用 `latest`。
- **Consequence**: 無法回滾 (Rollback)，因為 Git 紀錄沒有變化 (都是 latest)，且無法確定當下運行的是哪個版本。
- **Fix**: 使用 Semantic Versioning (`v1.0.1`) 或 Git SHA (`sha-a1b2c3d`)。

---

## Checklists & workflows｜檢查清單與流程

### Deployment Workflow (GitOps + Canary)

1.  **Dev**: 開發者 Push Code 到 `app-repo`。
2.  **CI**: Build Docker Image -> Push to Registry -> 觸發 `config-repo` 更新 (修改 Image Tag)。
3.  **CD (GitOps)**: ArgoCD 偵測到 `config-repo` 變更 -> Sync 到 Cluster。
4.  **Rollout Controller**:
    - 啟動 Canary Pods。
    - 調整 Service Mesh / Ingress 流量 (e.g., 5%)。
    - **Analysis**: 查詢 Prometheus (Success Rate > 99%? Latency < 500ms?)。
    - **Decision**: 通過 -> 增加流量；失敗 -> 自動 Rollback。

### Pre-flight Checklist (部署前檢查)

- [ ] **Immutability**: Docker Image Tag 是否唯一且固定？(非 `latest`)
- [ ] **Observability**: Canary Analysis 所需的 Metrics (如 HTTP 5xx rate) 是否已在 Prometheus 中有數據？
- [ ] **Liveness/Readiness**: 新版本的 Health Check Probe 是否配置正確？(避免流量打入還沒 Ready 的 Pod)
- [ ] **Resource Limits**: 是否設定了合理的 Request/Limit？(避免新版本 Memory Leak 拖垮節點)
- [ ] **Database**: 是否有 Schema Change？是否相容於舊版程式碼？

### Troubleshooting Checklist (部署失敗時)

- [ ] **GitOps Status**: ArgoCD/Flux 顯示狀態為何？(OutOfSync? SyncFailed?)
- [ ] **Rollout Status**: `kubectl argo rollouts get rollout <name>` 顯示在哪個 Step 失敗？
- [ ] **Events**: `kubectl get events` 是否有 ImagePullBackOff 或 PreStopHook 失敗？
- [ ] **Logs**: 新版 Pod 的 Log 是否有 Application Startup Error？

---

## Real-world examples｜實戰案例

### Scenario: Argo Rollouts with AnalysisTemplate
這是一個典型的漸進式部署設定，定義了如何進行 Canary 發布以及如何判斷「成功」。

#### 1. AnalysisTemplate (定義成功的標準)
這是「評分卡」，告訴 Controller 什麼叫做「正常的服務」。

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  args:
  - name: service-name
  metrics:
  - name: success-rate
    interval: 1m
    successCondition: result[0] >= 0.99
    failureLimit: 3
    provider:
      prometheus:
        address: http://prometheus.monitoring:9090
        query: |
          sum(rate(http_request_duration_seconds_count{job="kubernetes-pods", status!~"5.*", service="{{args.service-name}}"}[1m])) 
          / 
          sum(rate(http_request_duration_seconds_count{job="kubernetes-pods", service="{{args.service-name}}"}[1m]))
```

#### 2. Rollout Object (定義部署策略)
取代原本的 `Deployment` 物件。

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: payment-service
spec:
  replicas: 10
  strategy:
    canary:
      # 引用上面的 AnalysisTemplate
      analysis:
        templates:
        - templateName: success-rate
          args:
          - name: service-name
            value: payment-service-canary
      steps:
      - setWeight: 20
      - pause: {duration: 1h}  # 暫停一小時觀察，同時 Analysis 會持續在背景跑
      - setWeight: 50
      - pause: {duration: 10m}
      - setWeight: 100
  template:
    spec:
      containers:
      - name: payment
        image: my-registry/payment:v2.0.1
```

### Case Study: 自動化回滾 (Automated Rollback)
**情境**：某次更新引入了一個 Memory Leak，導致服務運行 30 分鐘後 Latency 飆升。
**過程**：
1. Rollout 執行到 `setWeight: 20`，初期 HTTP 200 OK，Analysis 通過。
2. 進入 `pause: {duration: 1h}` 階段。
3. 第 35 分鐘，Prometheus 偵測到 P99 Latency 超過閾值，且 Error Rate 上升。
4. `AnalysisTemplate` 返回失敗 (Failure)。
5. Argo Rollouts 立即終止 Canary Pods，將流量切回 Stable (舊版) Pods。
6. 開發團隊收到 Slack 通知：「Deployment Failed & Rolled Back」，線上用戶幾乎無感。