# 流水線效能調校與快取優化 / Pipeline Performance Tuning and Caching Optimization

## Mental model｜心智模型

在優化 GitLab CI/CD 效能時，我們必須建立兩個核心的心智模型：**「快取與產物的職責分離」** 以及 **「層級化加速策略」**。

### 1. Cache vs. Artifacts: The "Speed vs. Reliability" Trade-off
很多效能問題源於混淆了 Cache（快取）與 Artifacts（產物）：
- **Cache (快取)**：是為了 **加速 (Speed)**。它是「可有可無」的（Disposable）。如果快取遺失，流水線應該要能重新下載或建置，只是變慢而已。快取通常用於依賴套件（如 `node_modules`, `.m2`）。
- **Artifacts (產物)**：是為了 **傳遞 (Reliability)**。它是 Job 產出的結果（如編譯後的 Binary, Jar, Dist folder），必須準確地傳遞給下一個 Stage。

### 2. The Hierarchy of Optimization (優化層級)
不要一開始就鑽進微小的程式碼優化，應依照以下順序檢視瓶頸：
1.  **Network I/O**: 下載 Image、上傳/下載 Cache 與 Artifacts 的時間（通常是最大殺手）。
2.  **Scheduling**: Job 等待 Runner 的時間，以及 Job 之間的相依性阻塞（Blocking）。
3.  **Compute**: 實際編譯或測試運行的 CPU/RAM 效率。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Distributed Caching with S3/MinIO (分散式快取)
在 Kubernetes 或 Autoscaling Runner 環境下，Local Cache 幾乎無效（因為每次 Job 都在全新的 Pod/VM 跑）。
- **Pattern**: 設定 Runner 使用 S3 或 MinIO 作為 Shared Cache Server。
- **Why**: 確保 Runner A 下載的依賴，Runner B 下次執行時可以直接取用，大幅減少對外網（如 npm registry, Maven Central）的頻寬消耗。

### 2. Docker Layer Caching (DLC) Strategies
建置 Docker Image 時，善用 Docker 的分層機制。
- **Use `--cache-from`**: 在 CI 中，先 `docker pull` 上一次成功的 Image，並在 build 時加上 `--cache-from` 參數。這能讓 Docker 重用未變更的 Layers（如 OS base, 安裝好的系統套件）。
- **Multi-stage Builds**: 在 Dockerfile 中使用多階段建置，確保最終 Image 只包含執行所需的最小檔案，減少 push/pull 時間。

### 3. Smart Cache Keys (智慧快取鍵)
不要只用全域的 Key，應根據依賴定義檔產生 Key。
- **Pattern**:
  ```yaml
  cache:
    key:
      files:
        - package-lock.json  # 或 yarn.lock, go.sum, pom.xml
    paths:
      - node_modules/
  ```
- **Benefit**: 當依賴檔案沒變時，直接命中快取；變更時自動產生新快取，避免髒數據污染。

### 4. Directed Acyclic Graph (DAG) Optimization
打破傳統 Stage 的序列限制。
- **Pattern**: 使用 `needs` 關鍵字取代預設的 Stage 依賴。
- **Example**: `Test` Job 不需要等待 `Build` Job 完成，除非它真的需要 Build 的產物。如果 `Lint` 和 `Unit Test` 彼此無關，它們應該同時開始，而不受限於 Stage 順序。

### 5. Artifacts Slimming (產物瘦身)
- **Exclude**: 使用 `exclude` 排除不必要的暫存檔（如 `.git`, `node_modules`）。
- **Expiry**: 設定 `expire_in`（如 `1 hr` 或 `1 day`）。大多數 Artifacts 只需要存活到 Deploy 結束即可，無需永久佔用儲存空間。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Monster Cache" (巨型快取)
- **Anti-pattern**: 快取了整個專案目錄，或者快取了比重新下載還慢的超大資料夾。
- **Consequence**: `Restoring cache` 和 `Saving cache` 的時間超過了實際 Build 的時間。
- **Fix**: 只快取下載昂貴的依賴（Dependencies），不要快取編譯產物（Build outputs）。

### 2. Using Cache for Passing Data (誤用快取傳遞資料)
- **Anti-pattern**: 在 Build Job 把編譯好的執行檔放入 Cache，試圖在 Deploy Job 讀取。
- **Consequence**: 由於 Cache 不保證一定存在（可能被清除、可能跨 Runner 未同步），導致 Deploy 隨機失敗。
- **Fix**: 跨 Job 傳遞檔案必須使用 **Artifacts**。

### 3. Ignoring Docker Context (忽略 Docker Context)
- **Anti-pattern**: 執行 `docker build .` 時，目錄下包含數 GB 的 Artifacts 或 `node_modules`。
- **Consequence**: Docker Daemon 需要將整個 Context 複製進去，導致 Build 初始化極慢。
- **Fix**: 設定 `.dockerignore` 排除非必要檔案。

### 4. "Latest" Tag Addiction (過度依賴 Latest Tag)
- **Anti-pattern**: CI/CD 中依賴 `node:latest` 或 `docker:latest`。
- **Consequence**: 每次執行都需要重新 pull image（如果 image pull policy 設為 always），且版本不一致可能導致難以除錯的效能回退。

---

## Checklists & workflows｜檢查清單與流程

### Pipeline Performance Audit Workflow (效能審計流程)

當你發現流水線變慢時，請依照此流程檢查：

- [ ] **Step 1: Analyze Job Duration (分析耗時)**
    - 點開 Job Log，查看時間戳記。
    - 是卡在 `Downloading artifacts`？ `Restoring cache`？ 還是實際的 `Script` 執行？
- [ ] **Step 2: Verify Cache Hit Rate (驗證快取命中)**
    - 檢查 Log 中是否有 `Successfully extracted cache`。
    - 如果每次都顯示 `Creating cache` 且 Key 相同，代表 Cache 太大超時或上傳失敗。
- [ ] **Step 3: Inspect Artifact Size (檢查產物大小)**
    - 瀏覽 Job 頁面的 "Job artifacts"，檢查大小是否合理（例如：一個簡單的 Go App 不該有 500MB 的 Artifacts）。
- [ ] **Step 4: Review Docker Layering (檢視 Docker 分層)**
    - 檢查 Docker build log，確認是否每次都在 `RUN apt-get install` 重新下載系統套件？如果是，代表 Layer Caching 失效。
- [ ] **Step 5: Check Runner Saturation (檢查 Runner 負載)**
    - 是否因為 Runner 數量不足導致 Job 處於 `Pending` 狀態過久？

---

## Real-world examples｜實戰案例

### Example 1: Optimized Node.js Pipeline
展示如何結合 `cache:key:files` 與 `needs` 來優化。

```yaml
stages:
  - prepare
  - build
  - test

# 定義全域快取策略
cache:
  key:
    files:
      - package-lock.json
  paths:
    - node_modules/
  policy: pull  # 預設只讀取，只有特定 Job 負責寫入

install_deps:
  stage: prepare
  script:
    - npm ci
  cache:
    key:
      files:
        - package-lock.json
    paths:
      - node_modules/
    policy: pull-push # 只有這裡會更新快取

lint:
  stage: test
  needs: ["install_deps"] # 只要依賴裝好就跑，不用等 build
  script:
    - npm run lint

build_app:
  stage: build
  needs: ["install_deps"]
  script:
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 hour # 節省空間
```

### Example 2: Docker Layer Caching with Registry
利用既有的 Registry 作為快取來源，避免重複建置 Base Layers。

```yaml
build_image:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  variables:
    IMAGE_TAG: $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG
    LATEST_TAG: $CI_REGISTRY_IMAGE:latest
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    # 嘗試拉取上次的 Image 作為快取來源
    - docker pull $LATEST_TAG || true
    # 使用 --cache-from 加速
    - docker build --cache-from $LATEST_TAG -t $IMAGE_TAG -t $LATEST_TAG .
    - docker push $IMAGE_TAG
    - docker push $LATEST_TAG
```

### Example 3: Distributed Caching Config (config.toml)
這是 Runner 管理者需要設定的部分，啟用 S3/MinIO 分散式快取。

```toml
# /etc/gitlab-runner/config.toml

[[runners]]
  name = "aws-autoscaling-runner"
  executor = "docker+machine"
  [runners.cache]
    Type = "s3"
    Shared = true
    [runners.cache.s3]
      ServerAddress = "s3.amazonaws.com"
      AccessKey = "ACCESS_KEY"
      SecretKey = "SECRET_KEY"
      BucketName = "gitlab-runner-cache"
      BucketLocation = "us-east-1"
```