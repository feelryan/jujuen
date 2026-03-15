# 1. 前言與學習目標 (Introduction and Learning Objectives)

對於資深工程師而言，Docker 不僅僅是一個打包工具，它是連接「本地開發環境（Inner Loop）」與「自動化交付流水線（Outer Loop）」的關鍵橋樑。本章將探討如何利用 Docker 優化開發體驗，並在 CI/CD 環節中實現高效、安全且可重現的構建流程。

For senior engineers, Docker is more than just a packaging tool; it is the critical bridge connecting the "Inner Loop" (local development) and the "Outer Loop" (automated delivery pipeline). This chapter explores how to leverage Docker to optimize the developer experience and achieve efficient, secure, and reproducible build processes within CI/CD workflows.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **設計高效率的本地開發環境**：利用 Docker Compose 協調微服務與依賴服務（如 DB, Cache），解決 "It works on my machine" 的問題。
    **Design efficient local development environments:** Use Docker Compose to orchestrate microservices and dependent services (e.g., DB, Cache), solving the "It works on my machine" problem.
2.  **優化 CI Pipeline 構建速度**：掌握 Docker BuildKit 的進階快取策略（Inline Cache, Registry Cache），顯著減少 CI 等待時間。
    **Optimize CI pipeline build speeds:** Master advanced Docker BuildKit caching strategies (Inline Cache, Registry Cache) to significantly reduce CI wait times.
3.  **實作可重現的整合測試**：使用 Testcontainers 或類似模式，在測試程式碼中動態管理容器生命週期，確保測試環境的隔離性與一致性。
    **Implement reproducible integration tests:** Use Testcontainers or similar patterns to dynamically manage container lifecycles within test code, ensuring test environment isolation and consistency.
4.  **識別 CI/CD 中的 Docker 安全風險**：理解 Docker-in-Docker (DinD) 與 Docker-outside-of-Docker (DooD) 的差異與權限隱憂。
    **Identify Docker security risks in CI/CD:** Understand the differences and privilege concerns between Docker-in-Docker (DinD) and Docker-outside-of-Docker (DooD).

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 開發內迴圈與外迴圈 (The Inner and Outer Loops)

在心智模型中，我們將軟體交付分為兩個迴圈。Docker 的作用是確保這兩個迴圈的環境「同構（Isomorphic）」。
In our mental model, software delivery is divided into two loops. Docker's role is to ensure these two environments are "isomorphic."

*   **Inner Loop (Local Dev)**: 重點在於**快速反饋**。工程師修改程式碼，容器熱重載（Hot Reload），並連接到本地運行的資料庫容器。
    **Inner Loop (Local Dev):** Focuses on **fast feedback**. Engineers modify code, containers hot-reload, and connect to locally running database containers.
*   **Outer Loop (CI/CD)**: 重點在於**可靠性與自動化**。代碼推送到 Repo，觸發全新的容器構建、測試與掃描。
    **Outer Loop (CI/CD):** Focuses on **reliability and automation**. Code is pushed to the repo, triggering fresh container builds, tests, and scans.

**關鍵差異 (Key Difference)**：本地環境通常是「有狀態的（Stateful）」（保留 DB 數據以方便除錯），而 CI 環境必須是「無狀態的（Stateless）」（每次測試都應從乾淨的環境開始）。
**Key Difference:** Local environments are typically "stateful" (retaining DB data for debugging), whereas CI environments must be "stateless" (every test run should start from a clean slate).

## 2.2 構建上下文與快取層 (Build Context and Caching Layers)

在 CI 環境中，最常見的效能瓶頸是「重複下載依賴」與「重複構建」。
In CI environments, the most common performance bottlenecks are "re-downloading dependencies" and "re-building."

*   **Local Docker Daemon**: 本地有持久化的 Cache，第二次構建極快。
    **Local Docker Daemon:** Has a persistent cache, making subsequent builds extremely fast.
*   **CI Runners**: 通常是 Ephemeral（短暫的），每次都從零開始。因此，必須明確指示 Docker 從遠端 Registry 拉取舊的 Layers 作為快取來源（`--cache-from`）。
    **CI Runners:** Usually ephemeral, starting from scratch every time. Therefore, you must explicitly instruct Docker to pull old layers from a remote registry as a cache source (`--cache-from`).

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 微服務開發環境編排 (Microservices Orchestration for Dev)

在大型系統中，一個服務可能依賴 PostgreSQL, Redis, Kafka 以及其他 3 個內部微服務。
In large-scale systems, a service might depend on PostgreSQL, Redis, Kafka, and 3 other internal microservices.

*   **Naive Approach**: 要求每個開發者在自己的筆電上安裝這些軟體。這會導致版本衝突與配置地獄。
    **Naive Approach:** Require every developer to install these software packages on their laptops. This leads to version conflicts and configuration hell.
*   **Senior Approach**: 維護一個 `docker-compose.dev.yml`。
    **Senior Approach:** Maintain a `docker-compose.dev.yml`.
    *   **Infrastructure as Code**: 定義所有依賴服務的版本。
    *   **Networking**: 自動處理服務間的 DNS 解析（例如 app 連接 `postgres:5432`）。
    *   **Volume Mapping**: 將本地源代碼掛載進容器，實現即時修改即時生效。

## 3.2 CI Pipeline 設計：Shift Left Testing

在系統設計面試或實務架構中，我們希望儘早發現錯誤。
In system design interviews or practical architecture, we want to catch errors as early as possible.

*   **Unit Tests**: 在容器構建過程的 `RUN` 階段執行？還是構建完映像檔後執行？
    **Unit Tests:** Should they run during the `RUN` stage of the build? Or after the image is built?
    *   *Best Practice*: 多階段構建（Multi-stage build）中，可以在中間層執行單元測試。如果測試失敗，構建直接失敗，不會產出最終 Image。
    *   *Best Practice*: In multi-stage builds, run unit tests in an intermediate layer. If tests fail, the build fails immediately, and no final image is produced.

*   **Integration Tests**: 需要真實的資料庫。
    **Integration Tests:** Require a real database.
    *   使用 Docker Compose 在 CI Runner 中啟動整套環境，執行測試後銷毀。
    *   Use Docker Compose to spin up the full environment in the CI Runner, run tests, then tear it down.

---

# 4. 逐步示例 (Walkthrough / Example)

## 4.1 優化 CI 構建速度：BuildKit 與遠端快取 (Optimizing CI Build Speed: BuildKit & Remote Cache)

**場景 (Scenario)**：
一個 Node.js 應用程式，`npm install` 需要 3 分鐘。在 GitHub Actions 或 Jenkins 上，每次 Commit 都會重新執行安裝，浪費大量時間與運算資源。

A Node.js application where `npm install` takes 3 minutes. On GitHub Actions or Jenkins, every commit triggers a re-installation, wasting significant time and compute resources.

**解決方案 (Solution)**：
使用 Docker BuildKit 的 `--cache-from` 與 `--cache-to` 功能，將快取層推送到 Container Registry。

Use Docker BuildKit's `--cache-from` and `--cache-to` features to push cache layers to the Container Registry.

**Dockerfile (Optimized for Caching):**

```dockerfile
# syntax=docker/dockerfile:1
FROM node:18-alpine AS base
WORKDIR /app
COPY package*.json ./

FROM base AS deps
# 使用 cache mount 加速本地與 CI 的依賴安裝
# Use cache mount to speed up dependency installation locally and in CI
RUN --mount=type=cache,target=/root/.npm \
    npm ci

FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=deps /app/node_modules ./node_modules
CMD ["node", "dist/main.js"]
```

**CI Pipeline Command (Conceptual):**

```bash
# 啟用 BuildKit
export DOCKER_BUILDKIT=1

# 建置並推送到 Registry，同時處理快取
# Build and push to Registry, handling cache simultaneously
docker build \
  --tag my-registry.com/my-app:latest \
  --cache-from type=registry,ref=my-registry.com/my-app:build-cache \
  --cache-to type=registry,ref=my-registry.com/my-app:build-cache,mode=max \
  .
```

**解析 (Analysis)**：
*   `mode=max`：指示 Docker 快取所有中間層（Intermediate Layers），不僅僅是最終層。這對於多階段構建至關重要。
    `mode=max`: Instructs Docker to cache all intermediate layers, not just the final one. This is crucial for multi-stage builds.
*   `type=registry`：將快取層直接存儲在 Docker Registry 中，這樣即使 CI Runner 被銷毀，下一次構建也能拉取快取。
    `type=registry`: Stores cache layers directly in the Docker Registry, so even if the CI Runner is destroyed, the next build can pull the cache.

## 4.2 使用 Testcontainers 進行整合測試 (Integration Testing with Testcontainers)

**場景 (Scenario)**：
你需要測試一段依賴 Redis 的程式碼。使用 Mock 可能無法模擬 Redis 的真實行為（如過期策略）。

You need to test code that depends on Redis. Using Mocks might not simulate Redis's real behavior (e.g., eviction policies).

**Java/Kotlin Example (Conceptual):**

```kotlin
@Testcontainers
class RedisIntegrationTest {

    // 定義一個 Redis 容器，測試開始時啟動，結束時自動銷毀
    // Define a Redis container, starts when test begins, destroyed automatically when ends
    @Container
    val redis = GenericContainer(DockerImageName.parse("redis:7.0"))
        .withExposedPorts(6379)

    @Test
    fun testRedisInsert() {
        // 動態獲取映射後的 Host 與 Port
        // Dynamically get the mapped Host and Port
        val host = redis.host
        val port = redis.getMappedPort(6379)
        
        val client = RedisClient(host, port)
        client.set("key", "value")
        assert(client.get("key") == "value")
    }
}
```

**為何這是資深做法？ (Why is this Senior level?)**
*   **程式碼即基礎設施 (Infrastructure as Code)**：測試環境的定義就在測試代碼中，不需要外部腳本準備環境。
    **Infrastructure as Code:** The test environment definition lives within the test code, requiring no external scripts to prep the environment.
*   **隨機端口 (Random Ports)**：避免了並行測試時的端口衝突（Port Conflict）。
    **Random Ports:** Avoids port conflicts during parallel testing.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 在 CI 中掛載 Host Volume (Mounting Host Volumes in CI)

*   **錯誤 (Pitfall)**：在 CI 的 `docker run` 指令中使用 `-v $(pwd):/app`。
    **Pitfall:** Using `-v $(pwd):/app` in CI `docker run` commands.
*   **原因 (Why)**：
    1.  如果 CI 使用的是遠端 Docker Daemon (Docker-outside-of-Docker)，`$(pwd)` 指的是 Daemon 所在的機器路徑，而不是 CI Runner 的路徑，導致掛載空目錄。
        If CI uses a remote Docker Daemon (Docker-outside-of-Docker), `$(pwd)` refers to the path on the Daemon's machine, not the CI Runner, resulting in mounting an empty directory.
    2.  破壞了構建的可重現性，依賴於 Runner 的文件系統狀態。
        It breaks build reproducibility, relying on the Runner's filesystem state.
*   **修正 (Fix)**：在 CI 中應優先使用 `COPY` 指令將代碼打入映像檔，或使用專門的 CI Artifacts 機制。
    **Fix:** Prefer using `COPY` instructions to bake code into the image in CI, or use specialized CI Artifact mechanisms.

## 5.2 濫用 Docker-in-Docker (DinD) 與權限問題 (Misusing DinD and Privilege Issues)

*   **錯誤 (Pitfall)**：為了在 CI 中構建 Docker Image，將 CI 容器設為 `privileged` 並運行另一個 Docker Daemon。
    **Pitfall:** Running the CI container as `privileged` and starting another Docker Daemon inside it just to build Docker images.
*   **原因 (Why)**：
    1.  **安全性**：Privileged 模式允許容器存取宿主機的所有設備，有極大的安全隱患。
        **Security:** Privileged mode allows the container to access all host devices, posing a massive security risk.
    2.  **效能**：文件系統層疊（OverlayFS on OverlayFS）會導致嚴重的 I/O 效能下降。
        **Performance:** Filesystem layering (OverlayFS on OverlayFS) causes severe I/O performance degradation.
*   **修正 (Fix)**：使用 **Docker Socket Binding (DooD)**，即 `-v /var/run/docker.sock:/var/run/docker.sock`，讓 CI 容器使用宿主機的 Daemon。或者使用 **Kaniko** 等無需 Daemon 的構建工具。
    **Fix:** Use **Docker Socket Binding (DooD)**, i.e., `-v /var/run/docker.sock:/var/run/docker.sock`, letting the CI container use the host's Daemon. Or use daemonless build tools like **Kaniko**.

## 5.3 忽略 `.dockerignore` (Ignoring .dockerignore)

*   **錯誤 (Pitfall)**：直接 `COPY . .` 而沒有配置 `.dockerignore`。
    **Pitfall:** Doing `COPY . .` without configuring `.dockerignore`.
*   **後果 (Consequence)**：將 `.git` 文件夾（可能很大）、`node_modules`（架構可能不相容）、敏感的 `.env` 文件全部複製進映像檔。導致構建緩慢且不安全。
    **Consequence:** Copies the `.git` folder (potentially huge), `node_modules` (architecture mismatch), and sensitive `.env` files into the image. Results in slow and insecure builds.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## 6.1 CI/CD 中的快取優化 (Cache Optimization in CI/CD)

*   **問題**：「我們的 CI Pipeline 每次構建都要花 15 分鐘，大部分時間都在安裝依賴。你會如何利用 Docker 優化？」
    **Question:** "Our CI pipeline takes 15 minutes per build, mostly installing dependencies. How would you optimize this using Docker?"
*   **高分回答要點 (Key Points)**：
    *   提及 **Layer Caching** 原理（依賴變更頻率低，應放在底層）。
    *   解釋 **Multi-stage builds** 如何分離構建依賴與執行環境。
    *   關鍵：提到 **Remote Caching (`--cache-from`)**，因為 CI Runner 通常是無狀態的，本地快取無效。
    *   加分：提及 **BuildKit** 的並行構建能力。

## 6.2 容器化測試策略 (Containerized Testing Strategy)

*   **問題**：「在微服務架構下，你如何在本地開發環境與 CI 環境中處理資料庫依賴？」
    **Question:** "In a microservices architecture, how do you handle database dependencies in both local dev and CI environments?"
*   **高分回答要點 (Key Points)**：
    *   **Local**: 使用 Docker Compose 啟動 DB，並掛載 volume 持久化數據以便除錯。
    *   **CI**: 強調環境隔離。使用 `Testcontainers` 或在 CI 腳本中啟動 ephemeral 容器（`Service Containers`）。
    *   討論 **Schema Migration**：測試前如何自動應用 Migration 腳本。

## 6.3 安全性與權限 (Security & Privileges)

*   **問題**：「為什麼在 CI 中掛載 `/var/run/docker.sock` 被認為有風險？有什麼替代方案？」
    **Question:** "Why is mounting `/var/run/docker.sock` in CI considered risky? What are the alternatives?"
*   **高分回答要點 (Key Points)**：
    *   解釋這等於給了容器 `root` 權限控制宿主機。
    *   替代方案：使用 **Kaniko** 或 **Buildah** 進行無 Daemon 構建（Daemonless Build）。
    *   或者使用隔離性更強的 Runtime (如 gVisor, Kata Containers) 但這通常超出一般 CI 範疇。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 小結 (Summary)

1.  **Docker Compose** 是本地開發環境的標準配置，能有效模擬生產環境依賴。
    **Docker Compose** is the standard for local development, effectively simulating production dependencies.
2.  **CI 環境的無狀態性** 要求我們顯式地管理快取（`--cache-from`, `--cache-to`）以提升效能。
    **The stateless nature of CI environments** requires us to explicitly manage caching (`--cache-from`, `--cache-to`) to improve performance.
3.  **BuildKit** 是現代 Docker 構建的核心，務必啟用並善用其並行與快取特性。
    **BuildKit** is the core of modern Docker builds; always enable it and leverage its parallelism and caching features.
4.  **Testcontainers** 提供了程式碼級別的整合測試環境管理，優於外部腳本編排。
    **Testcontainers** provides code-level integration test environment management, superior to external script orchestration.
5.  **安全性**：避免在 CI 中濫用 Privileged 模式，謹慎處理 Docker Socket 的掛載。
    **Security:** Avoid abusing Privileged mode in CI and handle Docker Socket mounting with caution.

## 後續延伸 (Next Steps)

*   **下一章 (Chapter 08)**：將進入 **Container Orchestration (Kubernetes)**。從單機的 Docker Compose 轉向跨節點的集群管理。
    **Next Chapter (Chapter 08):** Moving into **Container Orchestration (Kubernetes)**. Transitioning from single-host Docker Compose to cross-node cluster management.
*   **延伸閱讀**：研究 **Kaniko**，了解如何在 Kubernetes 集群中安全地構建 Docker Image（無需 Docker Daemon）。
    **Further Reading:** Research **Kaniko** to understand how to securely build Docker images inside a Kubernetes cluster (without a Docker Daemon).