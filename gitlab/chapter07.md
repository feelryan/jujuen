# 流水線效能優化與快取策略
# Pipeline Performance Optimization

## 1. 前言與學習目標
## 1. Introduction & Learning Objectives

對於資深工程師而言，CI/CD 流水線的執行速度直接影響開發團隊的「回饋迴圈」（Feedback Loop）。等待 20 分鐘與等待 2 分鐘的 Build 對開發效率有著天壤之別。本章將超越基礎語法，深入探討如何透過快取策略、Docker 映像檔優化與 Artifacts 管理來極大化 GitLab CI 的效能。

For senior engineers, the execution speed of CI/CD pipelines directly impacts the development team's "Feedback Loop." The difference between waiting 20 minutes versus 2 minutes for a build is monumental for development efficiency. This chapter goes beyond basic syntax to explore how to maximize GitLab CI performance through caching strategies, Docker image optimization, and Artifacts management.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **區分並正確使用 Cache 與 Artifacts**：理解兩者在生命週期與用途上的根本差異，避免因誤用導致的儲存浪費或建置失敗。
    **Distinguish and correctly use Cache vs. Artifacts**: Understand the fundamental differences in lifecycle and purpose, avoiding storage waste or build failures caused by misuse.
2.  **實作進階 Docker 快取策略**：利用 Docker Layer Caching、BuildKit 或 Kaniko 在無特權（Rootless）環境下加速容器建置。
    **Implement advanced Docker caching strategies**: Leverage Docker Layer Caching, BuildKit, or Kaniko to accelerate container builds in rootless environments.
3.  **設計分散式快取架構**：在 Autoscaling Runners 環境中配置 S3/MinIO 作為分散式快取後端，確保快取命中率。
    **Design distributed caching architectures**: Configure S3/MinIO as a distributed cache backend in Autoscaling Runners environments to ensure cache hit rates.
4.  **優化大型專案的 DAG（有向無環圖）**：透過 `needs` 與 `dependencies` 關鍵字減少不必要的 Job 等待時間。
    **Optimize DAGs (Directed Acyclic Graphs) for large projects**: Reduce unnecessary job wait times using `needs` and `dependencies` keywords.

---

## 2. 核心觀念與心智模型
## 2. Core Concepts & Mental Model

### 2.1 Cache vs. Artifacts：暫存與交付
### 2.1 Cache vs. Artifacts: Temporary Storage vs. Delivery

這是最常被混淆的概念。請建立以下心智模型：
This is the most commonly confused concept. Establish the following mental model:

-   **Cache（快取）** 是為了 **"加速下一次執行"**。它是盡力而為（Best-effort）的，如果快取遺失，Job 應該要能重新下載或重建依賴，不應導致失敗。它通常用於 `node_modules`, `.m2/repository`, `vendor/` 等依賴套件。
    **Cache** is for **"speeding up the next run."** It is best-effort; if the cache is missing, the job should be able to re-download or rebuild dependencies without failing. It is typically used for `node_modules`, `.m2/repository`, `vendor/`, etc.
-   **Artifacts（產出物）** 是為了 **"傳遞給下一個 Stage"** 或 **"供人類下載"**。它是必要的（Mandatory），如果 Artifact 遺失，依賴它的後續 Job 會失敗。它通常用於編譯後的 Binary、測試報告、生成的靜態網站檔案。
    **Artifacts** are for **"passing to the next stage"** or **"human download."** They are mandatory; if an artifact is missing, subsequent jobs depending on it will fail. They are typically used for compiled binaries, test reports, or generated static site files.

### 2.2 Docker Layer Caching：洋蔥模型
### 2.2 Docker Layer Caching: The Onion Model

Docker 映像檔由唯讀層（Layers）組成。當我們在 CI 中執行 `docker build` 時，如果 Dockerfile 中的指令與之前的建置相同且 context 未變，Docker 會重用快取層。
Docker images consist of read-only layers. When running `docker build` in CI, if the instructions in the Dockerfile match a previous build and the context hasn't changed, Docker reuses the cached layers.

在 GitLab CI 的 ephemeral runners（用完即丟的執行器）環境中，本地 Docker daemon 的快取通常不存在。因此，我們必須依賴 **Registry Caching**（如 `--cache-from`）將快取層拉取下來，這是在雲端原生環境優化的關鍵。
In GitLab CI's ephemeral runners environment, the local Docker daemon cache usually doesn't exist. Therefore, we must rely on **Registry Caching** (e.g., `--cache-from`) to pull cached layers, which is crucial for optimization in cloud-native environments.

---

## 3. 實務場景與系統設計視角
## 3. Real-World & System Design View

### 3.1 分散式快取架構 (Distributed Caching Architecture)
### 3.1 Distributed Caching Architecture

在 Production 等級的 GitLab 環境中，通常會使用 Kubernetes Executor 來動態擴展 Runners。這意味著每個 Job 都在一個全新的 Pod 中執行。
In a production-grade GitLab environment, the Kubernetes Executor is often used to dynamically scale Runners. This means every job runs in a brand-new Pod.

-   **問題**：Pod A 下載了 500MB 的 `node_modules`，但 Pod B（執行下一次 Pipeline）無法存取 Pod A 的檔案系統。
    **Problem**: Pod A downloads 500MB of `node_modules`, but Pod B (running the next pipeline) cannot access Pod A's filesystem.
-   **解法**：配置 GitLab Runner 使用 S3、GCS 或 MinIO 作為分散式快取後端。
    **Solution**: Configure GitLab Runner to use S3, GCS, or MinIO as a distributed cache backend.

**流程視角 (Flow View):**
1.  **Job Start**: Runner 啟動，檢查 `gitlab-ci.yml` 中的 cache key。
    **Job Start**: Runner starts, checks the cache key in `gitlab-ci.yml`.
2.  **Pull Cache**: Runner 從 S3 下載對應的 cache zip 檔並解壓縮到工作目錄。
    **Pull Cache**: Runner downloads the corresponding cache zip file from S3 and extracts it to the working directory.
3.  **Execute**: 執行 build script（如 `npm install`）。若快取命中，此步驟極快。
    **Execute**: Run build scripts (e.g., `npm install`). If cache hits, this step is extremely fast.
4.  **Push Cache**: Job 結束前，若檔案有變更，Runner 將目錄壓縮並上傳回 S3。
    **Push Cache**: Before the job ends, if files changed, the Runner zips the directory and uploads it back to S3.

### 3.2 對 DORA 指標的影響
### 3.2 Impact on DORA Metrics

優化 Pipeline 直接改善 **Lead Time for Changes**（變更前置時間）。如果 CI 需要 1 小時，工程師一天只能部署幾次；如果縮短到 10 分鐘，迭代頻率將大幅提升。同時，減少 Runner 的執行時間也能顯著降低雲端成本（Compute Minutes）。
Optimizing pipelines directly improves **Lead Time for Changes**. If CI takes 1 hour, engineers can only deploy a few times a day; if reduced to 10 minutes, iteration frequency increases drastically. Additionally, reducing Runner execution time significantly lowers cloud costs (Compute Minutes).

---

## 4. 逐步示例：優化 Docker Build 與快取
## 4. Walkthrough / Example: Optimizing Docker Build & Caching

### 情境 (Scenario)
### Scenario

我們有一個 Node.js 應用程式，目前的 Pipeline 每次都需要 15 分鐘：
1. `npm install` 每次都要重新下載 (5 mins)。
2. `docker build` 每次都從頭建置 (10 mins)。

We have a Node.js application where the current pipeline takes 15 minutes every time:
1. `npm install` re-downloads everything (5 mins).
2. `docker build` builds from scratch (10 mins).

### 第一步：優化套件依賴快取
### Step 1: Optimizing Dependency Caching

我們使用 `cache` 關鍵字，並以 `package-lock.json` 的 checksum 作為 key。這樣只有當依賴改變時，才會建立新的快取。
We use the `cache` keyword and use the checksum of `package-lock.json` as the key. This way, a new cache is created only when dependencies change.

```yaml
# .gitlab-ci.yml

variables:
  npm_config_cache: "$CI_PROJECT_DIR/.npm"

build_dependencies:
  image: node:18-alpine
  stage: build
  script:
    - npm ci
  cache:
    key:
      files:
        - package-lock.json
    paths:
      - .npm/
      - node_modules/
    policy: pull-push # Default behavior
```

**為何這樣做？ (Why?)**
使用 `npm ci` 配合 `package-lock.json` 確保安裝版本一致。快取 `.npm` (npm cache) 和 `node_modules` 可以大幅減少網路 I/O。
Using `npm ci` with `package-lock.json` ensures consistent versions. Caching `.npm` (npm cache) and `node_modules` significantly reduces network I/O.

### 第二步：優化 Docker Build (使用 Registry Cache)
### Step 2: Optimizing Docker Build (Using Registry Cache)

在 CI 環境中，我們通常沒有本地快取。我們可以使用 `--cache-from` 指令，告訴 Docker 從 Registry 拉取舊的映像檔作為快取來源。
In a CI environment, we usually don't have a local cache. We can use the `--cache-from` instruction to tell Docker to pull the old image from the Registry as a cache source.

```yaml
docker_build:
  stage: package
  image: docker:24.0.5
  services:
    - docker:24.0.5-dind
  variables:
    IMAGE_TAG: $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG
    LATEST_TAG: $CI_REGISTRY_IMAGE:latest
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    # 嘗試拉取 latest 映像檔作為快取層
    # Attempt to pull the latest image as a cache layer
    - docker pull $LATEST_TAG || true
    - >
      docker build
      --cache-from $LATEST_TAG
      --tag $IMAGE_TAG
      --tag $LATEST_TAG
      .
    - docker push $IMAGE_TAG
    - docker push $LATEST_TAG
```

**進階技巧 (Advanced Tip):**
如果你的 Dockerfile 是多階段建置（Multi-stage build），你需要為每個階段明確指定 `--cache-from`，或者使用更現代的工具如 Docker BuildKit (`docker buildx`)，它支援更細緻的快取匯出（`--cache-to type=inline` 或 `type=registry`）。
If your Dockerfile is a multi-stage build, you need to explicitly specify `--cache-from` for each stage, or use modern tools like Docker BuildKit (`docker buildx`), which supports more granular cache exporting (`--cache-to type=inline` or `type=registry`).

### 第三步：使用 Kaniko (針對 Kubernetes 環境)
### Step 3: Using Kaniko (For Kubernetes Environments)

在許多企業級 K8s 中，基於安全考量禁止使用 Docker-in-Docker (dind) 的特權模式（Privileged mode）。此時 `kaniko` 是最佳替代方案，它不需要 Docker daemon 且自動處理 Layer Caching。
In many enterprise K8s environments, Docker-in-Docker (dind) privileged mode is forbidden for security reasons. In this case, `kaniko` is the best alternative; it doesn't require a Docker daemon and handles Layer Caching automatically.

```yaml
build_image_kaniko:
  stage: package
  image:
    name: gcr.io/kaniko-project/executor:v1.14.0-debug
    entrypoint: [""]
  script:
    - /kaniko/executor
      --context "${CI_PROJECT_DIR}"
      --dockerfile "${CI_PROJECT_DIR}/Dockerfile"
      --destination "${CI_REGISTRY_IMAGE}:${CI_COMMIT_TAG}"
      --cache=true # 啟用快取 Enable caching
      --cache-repo="${CI_REGISTRY_IMAGE}/cache" # 指定快取存放庫 Specify cache repo
```

---

## 5. 常見錯誤與反模式
## 5. Common Pitfalls & Anti-patterns

### 5.1 快取過大導致反效果
### 5.1 Cache Bloat Causing Negative Impact

-   **錯誤 (Pitfall)**: 將所有東西都放入 Cache，導致 cache.zip 超過 1GB。
    **Pitfall**: Putting everything into the Cache, causing cache.zip to exceed 1GB.
-   **後果 (Consequence)**: 下載和解壓縮快取的時間超過了重新安裝依賴的時間。
    **Consequence**: The time to download and extract the cache exceeds the time to reinstall dependencies.
-   **修正 (Fix)**: 只快取必要的依賴目錄（如 `node_modules`），並定期清理過期的 Cache key。排除生成的 binary 或 log 檔。
    **Fix**: Cache only necessary dependency directories (e.g., `node_modules`) and periodically clear expired Cache keys. Exclude generated binaries or log files.

### 5.2 誤用 Artifacts 傳遞依賴
### 5.2 Misusing Artifacts to Pass Dependencies

-   **錯誤 (Pitfall)**: 在 Build Stage 安裝 `node_modules`，然後將其作為 Artifact 傳遞給 Test Stage。
    **Pitfall**: Installing `node_modules` in the Build Stage and passing it as an Artifact to the Test Stage.
-   **後果 (Consequence)**: Artifacts 會被上傳到 GitLab Server 並預設保留很久，這會極快消耗 Server 儲存空間並拖慢上傳/下載速度。
    **Consequence**: Artifacts are uploaded to the GitLab Server and kept for a long time by default, rapidly consuming server storage and slowing down upload/download speeds.
-   **修正 (Fix)**: 使用 Cache 來共享 `node_modules`。Artifacts 僅用於編譯後的結果（如 `dist/` 資料夾或 `.jar` 檔）。
    **Fix**: Use Cache to share `node_modules`. Use Artifacts only for compiled results (e.g., `dist/` folder or `.jar` files).

### 5.3 忽略 Dockerfile 的指令順序
### 5.3 Ignoring Dockerfile Instruction Order

-   **錯誤 (Pitfall)**: 在 `COPY . .` 之後才執行 `RUN npm install`。
    **Pitfall**: Running `RUN npm install` after `COPY . .`.
-   **後果 (Consequence)**: 只要原始碼有任何變動（即使只是改了 README），Docker 就會讓 `npm install` 的快取層失效，導致每次都重新安裝。
    **Consequence**: Any change in the source code (even just changing README) invalidates the `npm install` cache layer, causing a reinstall every time.
-   **修正 (Fix)**: 先 COPY 依賴描述檔 (`package.json`)，安裝依賴，最後才 COPY 原始碼。
    **Fix**: COPY dependency descriptors (`package.json`) first, install dependencies, and then COPY the source code.

---

## 6. 面試與實務問答切入點
## 6. Interview & Discussion Hooks

### Q1: 如何優化一個執行時間過長的 CI/CD Pipeline？
### Q1: How do you optimize a CI/CD pipeline that takes too long to execute?

-   **回答要點 (Key Points)**:
    1.  **分析 (Analyze)**: 使用 GitLab 的 Pipeline 分析圖表找出瓶頸（是下載慢？測試慢？還是 Docker build 慢？）。
    2.  **並行化 (Parallelization)**: 將測試拆分並行執行（Parallel Matrix），調整 DAG 結構讓不相依的 Job 同時跑。
    3.  **快取 (Caching)**: 實作分散式依賴快取與 Docker Layer Caching。
    4.  **精簡 (Slimming)**: 減少 Docker image 大小，使用更輕量的 Base image (Alpine/Distroless)。

### Q2: 請解釋 GitLab CI 中 `cache` 與 `artifacts` 的區別，以及何時使用哪一個？
### Q2: Explain the difference between `cache` and `artifacts` in GitLab CI, and when to use which?

-   **回答要點 (Key Points)**:
    -   **Cache**: 用於加速，跨 Pipeline 有效，非必須（Missing is OK），通常存依賴庫。
    -   **Artifacts**: 用於傳遞資料，Pipeline 內有效（或供下載），必須存在（Missing fails job），通常存建置產物。
    -   **情境**: `node_modules` 用 Cache；`app.jar` 或 `coverage-report.html` 用 Artifacts。

### Q3: 在 Kubernetes Runner 環境下，你會如何處理 Docker Build？
### Q3: How do you handle Docker Builds in a Kubernetes Runner environment?

-   **回答要點 (Key Points)**:
    -   提到 **Docker-in-Docker (dind)** 的安全性問題（需要 Privileged mode）。
    -   推薦使用 **Kaniko** 或 **Buildah** 作為無特權（Rootless）的建置方案。
    -   討論如何配置 Kaniko 的快取參數（`--cache=true`）來利用 Registry 儲存快取層。

---

## 7. 小結與後續延伸
## 7. Summary & Next Steps

### 記憶錨點 (Key Takeaways)
1.  **Cache != Artifacts**: Cache 加速依賴獲取；Artifacts 傳遞建置產出。
2.  **分散式快取 (Distributed Cache)**: 在 Autoscaling 環境中，必須配置 S3/MinIO 才能讓快取生效。
3.  **Docker Layer Caching**: 善用 `--cache-from` 或 BuildKit/Kaniko 快取功能，避免重複建置未變更的層。
4.  **Dockerfile 優化**: 嚴格遵守「依賴安裝在前，原始碼複製在後」的原則。
5.  **DAG 優化**: 使用 `needs: []` 來打破 Stage 的順序限制，讓 Job 儘早開始執行。

### 後續延伸 (Next Steps)
-   **安全性 (Security)**: 學習如何在 Pipeline 中安全地管理 Secrets（整合 HashiCorp Vault）。
-   **GitLab CI for Monorepo**: 研究如何使用 `rules:changes` 僅針對變更的模組執行 Pipeline。
-   **Observability**: 整合 Datadog 或 Prometheus 來監控 Pipeline 的效能趨勢。

下一章將探討 **GitLab CI 的安全性最佳實踐與 Secret Management**。
The next chapter will explore **GitLab CI Security Best Practices and Secret Management**.