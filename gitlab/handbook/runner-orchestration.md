# Runner 編排策略與資源優化 / Runner Orchestration and Resource Optimization

## Mental model｜心智模型

要掌握 GitLab Runner 的編排，不能只將 Runner 視為「一台安裝了 Agent 的伺服器」，而應該將其視為一個 **「動態的運算資源池 (Dynamic Compute Resource Pool)」**。

在這個模型中，我們關注三個核心維度：

1.  **調度層 (The Dispatcher)**：GitLab Server 負責分發工作，它不關心工作在哪裡跑，只關心標籤 (Tags) 是否匹配。
2.  **執行層 (The Executor)**：這是程式碼實際運行的地方。
    *   **Shell** = 在本機直接跑（裸機），環境是「髒」的 (Stateful)。
    *   **Docker** = 每次都在全新的 Container 跑，環境是「乾淨」的 (Stateless)。
    *   **Kubernetes** = 在 Pod 中跑，具備高度彈性與資源隔離。
3.  **彈性層 (The Elasticity)**：資源如何隨負載伸縮？
    *   **Static**：固定機器，成本固定，響應快，但閒置時浪費。
    *   **Autoscaling**：隨需產生機器 (On-demand/Spot)，成本優化，但有冷啟動時間 (Cold start)。

**核心原則**：
> **"Treat Runners like Cattle, not Pets."**
> 除非有特殊硬體需求（如 iOS Build 需 Mac），否則 Runner 應設計為可隨時銷毀、無狀態且自動擴展的。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Executor Selection Strategy (執行器選擇策略)

在 90% 的場景下，選擇順序應為：**Kubernetes > Docker > Shell**。

*   **Kubernetes Executor**:
    *   **適用場景**：團隊已經在使用 K8s，需要大規模並發 (Concurrency)。
    *   **Best Practice**：為 CI/CD Job 設定明確的 CPU/Memory Request 與 Limit，避免單一 Job 拖垮整個 Cluster Node。使用 `node_selector` 將 CI 負載隔離到特定的 Node Pool。
*   **Docker Executor (Machine/Autoscaling)**:
    *   **適用場景**：尚未導入 K8s，或需要使用 Docker-in-Docker (DinD) 進行複雜構建。
    *   **Best Practice**：配置 `docker-machine` (或其 fork) 搭配 AWS/GCP 的 Spot Instances。
*   **Shell Executor**:
    *   **適用場景**：必須存取底層硬體 (GPU, USB dongles) 或特定 OS (macOS, Windows without container support)。
    *   **Best Practice**：僅用於該特定用途，嚴格限制權限，並定期重置環境。

### 2. Cost Optimization with Spot Instances (競價實例成本優化)

利用雲端供應商的 Spot Instances (AWS) / Preemptible VMs (GCP) 可以節省高達 70-90% 的運算成本。

*   **實作模式**：
    *   使用 `docker-machine` 驅動程式。
    *   設定 `IdleCount` > 0：保留少量「熱機」以應付突發流量，避免第一位開發者等待開機。
    *   設定 `MaxGrowthRate`：防止錯誤配置導致無限開機器燒錢。
    *   **S3/GCS 作為 Cache**：因為機器隨時會消失，必須使用分佈式快取 (Distributed Cache) 儲存 `node_modules` 等依賴，而非依賴本地檔案系統。

### 3. Concurrency Tuning (並發調校)

GitLab Runner 有兩個層級的並發設定，經常被混淆：

*   `concurrent` (Global level): 這台 Runner Host **總共**可以同時跑多少 Jobs。
*   `limit` (Runner level): 特定 token 註冊的 Runner 可以跑多少 Jobs。
*   `request_concurrency`: 向 GitLab Server 請求工作的頻率。

**Pattern**: 在一台強大的 Host 上安裝一個 Runner Service，將 `concurrent` 設為高值 (如 10-50)，然後依賴 Docker/K8s 隔離 Job。不要在同一台機器上啟動 10 個 Runner Process。

### 4. Docker Image Optimization (映像檔優化)

*   **Pre-pulling Images**: 如果你的 CI 頻繁使用某個巨大的 Docker Image，在 Runner 的 `config.toml` 中設定 `pull_policy = ["if-not-present"]` 並定期在 Host 上預先拉取該 Image，可大幅減少網路頻寬與時間。
*   **Custom Build Images**: 不要直接用原始的 `node:16` 或 `maven:3`，建立一個包含所有常用工具 (git, curl, zip) 的自定義 Image，減少在 `before_script` 中 `apt-get install` 的時間。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Stateful Shell" Trap (有狀態 Shell 的陷阱)
*   **Bad Practice**: 使用 Shell Executor，並依賴上一次 Job 留下的檔案（例如 `node_modules`）。
*   **Consequence**: "It works on CI but fails locally" 或者 "It fails on CI but works locally"。當 Runner 數量增加時，Job A 的殘留檔案會汙染 Job B。
*   **Solution**: 始終假設環境是全新的。如果必須用 Shell，請在 `before_script` 執行 `git clean -fdx`。

### 2. Blindly Using Docker-in-Docker (盲目使用 DinD)
*   **Bad Practice**: 為了 build Docker image，無腦開啟 `privileged = true` 並使用 `dind` service。
*   **Consequence**: 安全風險高（Root 權限），且每次都要重新拉取 Layer，速度慢。
*   **Solution**:
    *   考慮使用 **Kaniko** 或 **Buildah** (不需要 privileged 權限)。
    *   若必須用 Docker，考慮掛載 `/var/run/docker.sock` (Socket Binding)，利用 Host 的 Docker Daemon (需注意安全邊界，僅限受信任專案)。

### 3. Ignoring Artifact Management (忽視產物管理)
*   **Bad Practice**: 將巨大的 build output (如 500MB 的 binary 或 `node_modules`) 全部設為 artifacts，且過期時間設為 `never`。
*   **Consequence**: GitLab Server 儲存空間爆炸，備份變慢，Restore 困難。
*   **Solution**:
    *   Artifacts 僅用於「人類需要下載查看」或「傳遞給下一個 Stage」的檔案。
    *   設定合理的 `expire_in` (如 `1 week`)。
    *   中間產物 (Intermediate files) 應使用 Cache 而非 Artifacts。

### 4. Single Point of Failure (單點故障)
*   **Bad Practice**: 整個公司依賴一台手動架設的 "Super Runner"。
*   **Consequence**: 當這台機器磁碟滿了或當機，全公司開發停擺。
*   **Solution**: 至少要有兩台 Runner，或使用 Autoscaling Group。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Choosing the Right Executor
1.  **Do you need to build Docker images?**
    *   Yes -> Use **Docker** (with Kaniko/DinD) or **K8s**.
    *   No -> Next.
2.  **Do you need specific hardware (GPU, MacOS)?**
    *   Yes -> Use **Shell** on dedicated hardware.
    *   No -> Next.
3.  **Do you have an existing K8s cluster?**
    *   Yes -> Use **Kubernetes Executor**.
    *   No -> Use **Docker Executor** on a VM.

### Runner Maintenance Checklist (Monthly)
- [ ] **版本更新**：檢查 Runner version 是否落後 GitLab Server 超過 3 個 minor versions（避免 API 不相容）。
- [ ] **磁碟清理**：執行 `docker system prune` 清理懸空的 images 和 volumes (若未設定自動清理)。
- [ ] **Cache 驗證**：檢查 S3/MinIO Cache bucket 的 Lifecycle rule 是否生效（是否自動刪除舊 Cache）。
- [ ] **Token 輪替**：如果是長期運行的 Runner，檢查 Registration Token 是否需要輪替（GitLab 16.0+ 引入了新的 Token 機制，需關注）。
- [ ] **資源監控**：檢查 Runner Host 的 CPU/Memory 使用率，調整 `concurrent` 上限。

### Autoscaling Configuration Workflow
1.  **Define Base Load**: 觀察平日最低 Job 數量，設定 `IdleCount` (例如 2)。
2.  **Define Peak Load**: 設定 `Limit` 防止費用失控 (例如 20)。
3.  **Set Idle Time**: 設定 `IdleTime` (例如 1800秒)，讓機器跑完 Job 後多活 30 分鐘，以服務後續立即進來的 Job。
4.  **Select Instance Type**: 選擇 CPU/RAM 比例適合 Build 任務的機型 (如 AWS `c5.large` 或 `t3.xlarge`)。

---

## Real-world examples｜實戰案例

### Scenario 1: Cost-Effective Web App CI (AWS + Docker Autoscaling)

這是一個典型的 Web 應用程式 CI 架構，目標是降低成本並應對上班時間的流量高峰。

**config.toml Snippet:**

```toml
concurrent = 20
check_interval = 0

[[runners]]
  name = "aws-autoscaler"
  url = "https://gitlab.com/"
  token = "PROJECT_TOKEN"
  executor = "docker+machine"
  limit = 20
  [runners.docker]
    image = "alpine:latest"
    privileged = true      # For DinD
    disable_cache = true   # Force use of distributed cache
  [runners.cache]
    Type = "s3"
    Shared = true
    [runners.cache.s3]
      ServerAddress = "s3.amazonaws.com"
      BucketName = "gitlab-runner-cache"
      BucketLocation = "us-east-1"
  [runners.machine]
    IdleCount = 2           # Always keep 2 runners ready
    IdleTime = 1800         # Keep alive for 30 mins after job
    MaxGrowthRate = 10      # Don't spin up too fast
    MachineDriver = "amazonec2"
    MachineName = "gitlab-docker-machine-%s"
    MachineOptions = [
      "amazonec2-access-key=...",
      "amazonec2-secret-key=...",
      "amazonec2-region=us-east-1",
      "amazonec2-instance-type=t3.large",
      "amazonec2-request-spot-instance=true", # KEY: Use Spot Instances
      "amazonec2-spot-price=0.03"             # Max price willing to pay
    ]
```

### Scenario 2: iOS Build Farm (Shell Executor on Mac mini)

針對 iOS App 開發，必須使用 macOS 環境。

**Architecture**:
*   3台 Mac mini 連接至辦公室網路。
*   使用 Shell Executor。
*   **關鍵腳本 (`.gitlab-ci.yml`)**:

```yaml
ios-build:
  stage: build
  tags:
    - macos  # 指定跑在 Mac mini 上
    - xcode-14
  script:
    - bundle install --path vendor/bundle  # Local isolation
    - bundle exec fastlane gym
  after_script:
    - rm -rf ~/Library/Developer/Xcode/DerivedData/* # 清理 Xcode 緩存，避免磁碟滿載
```

### Scenario 3: Enterprise Kubernetes Cluster (K8s Executor)

大型企業內部，多個團隊共享一個 K8s Cluster。

**Strategy**:
*   使用 **GitLab Agent for Kubernetes** 安裝 Runner。
*   利用 `config.toml` 中的 `[runners.kubernetes]` 區塊進行資源隔離。

```toml
[runners.kubernetes]
  namespace = "gitlab-runner"
  image = "ubuntu:20.04"
  # 確保 CI Job 不會搶佔關鍵服務資源
  cpu_request = "500m"
  memory_request = "1Gi"
  service_account = "ci-job-runner"
  # 將 CI Job 趕到特定的 Node Pool (例如由 Spot Instances 組成的 Pool)
  [runners.kubernetes.node_selector]
    "k8s.io/lifecycle" = "spot"
    "purpose" = "ci-workload"
```