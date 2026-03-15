# Chapter 09: Package Registry and Container Management
# 第 9 章：套件庫與容器映像檔管理

## 1. Introduction and Learning Objectives
## 1. 前言與學習目標

In modern DevOps ecosystems, managing source code is only half the battle; managing the binary artifacts (libraries and container images) derived from that code is equally critical. GitLab provides integrated Package and Container Registries, allowing teams to close the loop on the software supply chain without relying on external services like Nexus, Artifactory, or Docker Hub.
在現代 DevOps 生態系統中，管理原始碼僅是戰役的一半；管理由程式碼衍生出的二進位產物（函式庫與容器映像檔）同樣至關重要。GitLab 提供了整合式的 Package 與 Container Registries，讓團隊能夠在不依賴 Nexus、Artifactory 或 Docker Hub 等外部服務的情況下，完成軟體供應鏈的閉環。

By the end of this chapter, you will be able to:
完成本章後，您將能夠：

1.  **Unify Artifact Management**: Configure and utilize GitLab's Package Registry for language-specific dependencies (NPM, Maven, NuGet, PyPI) and Container Registry for Docker/OCI images.
    **統一產物管理**：配置並使用 GitLab 的 Package Registry 來管理特定語言的相依套件（NPM, Maven, NuGet, PyPI），以及使用 Container Registry 管理 Docker/OCI 映像檔。
2.  **Optimize Storage & Cost**: Design and implement aggressive cleanup policies to manage storage growth, distinguishing between "soft deletion" (untagging) and "hard deletion" (garbage collection).
    **優化儲存與成本**：設計並實作積極的清理策略以管理儲存空間增長，並區分「軟刪除」（移除標籤）與「硬刪除」（垃圾回收）的差異。
3.  **Secure the Supply Chain**: Implement authentication strategies using `CI_JOB_TOKEN` and Deploy Tokens to control access to private artifacts across different projects and pipelines.
    **確保供應鏈安全**：運用 `CI_JOB_TOKEN` 與 Deploy Tokens 實作驗證策略，以控制跨專案與跨 Pipeline 對私有產物的存取權限。
4.  **Troubleshoot Registry Issues**: Diagnose common issues related to image immutability, layer caching, and cross-project dependency resolution.
    **排除 Registry 問題**：診斷與映像檔不可變性、分層快取（Layer Caching）以及跨專案相依性解析相關的常見問題。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 The "Single Source of Truth" for Binaries
### 2.1 二進位檔的「單一真理來源」

Think of the GitLab Registry not just as a storage bucket, but as the **authoritative interface** between your CI (Build) and CD (Deploy) phases.
請將 GitLab Registry 不僅視為一個儲存桶，而是 CI（建置）與 CD（部署）階段之間的**權威介面**。

*   **Source Code (Git Repository):** The recipe.
*   **Artifacts (Registry):** The cooked meal, packaged and ready for consumption.
*   **原始碼 (Git Repository)：** 食譜。
*   **產物 (Registry)：** 烹調好的餐點，已打包並準備好供人享用。

Unlike generic object storage (S3), GitLab Registries understand the *semantics* of versioning (Semantic Versioning for packages, Tags/Digests for containers) and integrate natively with GitLab's permission model.
與一般的物件儲存（S3）不同，GitLab Registries 理解版本的*語意*（套件的語意化版本、容器的 Tags/Digests），並與 GitLab 的權限模型原生整合。

### 2.2 Package Registry vs. Container Registry
### 2.2 套件庫 vs. 容器庫

It is crucial to distinguish between the two subsystems, as they serve different granularities:
區分這兩個子系統至關重要，因為它們服務於不同的顆粒度：

| Feature | Package Registry | Container Registry |
| :--- | :--- | :--- |
| **Primary Unit** | Libraries / Dependencies (jar, tgz, dll, whl) | Docker / OCI Images |
| **Protocol** | Language specific (NPM, Maven, NuGet API) | Docker Registry HTTP API V2 |
| **Use Case** | Sharing code *between* developers/projects | Deploying applications to runtime (K8s, ECS) |
| **Dependency** | Resolved at *Build Time* | Resolved at *Deploy/Run Time* |

| 特性 | Package Registry | Container Registry |
| :--- | :--- | :--- |
| **主要單位** | 函式庫 / 相依套件 (jar, tgz, dll, whl) | Docker / OCI 映像檔 |
| **協定** | 特定語言協定 (NPM, Maven, NuGet API) | Docker Registry HTTP API V2 |
| **使用情境** | 在開發者/專案*之間*共享程式碼 | 將應用程式部署至執行環境 (K8s, ECS) |
| **相依性** | 在*建置時期 (Build Time)* 解析 | 在*部署/執行時期 (Deploy/Run Time)* 解析 |

### 2.3 Scope and Visibility
### 2.3 範圍與可見性

*   **Project-level:** Artifacts are scoped to a specific project. Useful for microservices that own their private libraries.
*   **Group-level:** Artifacts are aggregated from all projects in a group. This is the "Mental Model" for a developer pulling dependencies: "I want to install `@my-company/utils`, I don't care which specific repo built it."
*   **Instance-level:** (Self-managed only) Global visibility.

*   **專案層級：** 產物被限制在特定專案範圍內。適用於擁有私有函式庫的微服務。
*   **群組層級：** 聚合群組內所有專案的產物。這是開發者拉取相依套件時的「心智模型」：「我想要安裝 `@my-company/utils`，我不在乎具體是哪個 repo 建置了它。」
*   **實例層級：**（僅限自管版）全域可見性。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### 3.1 Architecture: The Secure Supply Chain
### 3.1 架構：安全的軟體供應鏈

In a production environment, relying on public registries (npmjs.com, Maven Central, Docker Hub) introduces risks: availability (they go down), security (typosquatting), and rate limiting.
在生產環境中，依賴公開 Registry（npmjs.com, Maven Central, Docker Hub）會帶來風險：可用性（它們可能當機）、安全性（搶註類似網域名稱攻擊）以及速率限制。

**Design Pattern: Proxy and Cache (Dependency Firewall)**
**設計模式：代理與快取（相依性防火牆）**

While GitLab (as of recent versions) is introducing "Dependency Proxy" features, the typical enterprise architecture involves:
雖然 GitLab（在近期版本中）引入了「Dependency Proxy」功能，但典型的企業架構通常包含：

1.  **Internal Libraries:** Published to GitLab Package Registry.
2.  **External Libraries:** Cached via GitLab Dependency Proxy (for Docker) or an external tool (like Nexus/Artifactory) if GitLab's native caching is insufficient for the specific language.
3.  **Build Process:** CI pipelines are configured to pull *only* from the internal registry URL, ensuring no accidental calls to the public internet.

1.  **內部函式庫：** 發布至 GitLab Package Registry。
2.  **外部函式庫：** 透過 GitLab Dependency Proxy（針對 Docker）快取，或若 GitLab 對特定語言的原生快取不足，則使用外部工具（如 Nexus/Artifactory）。
3.  **建置流程：** CI Pipeline 被設定為*僅*從內部 Registry URL 拉取，確保不會意外連線至公開網際網路。

### 3.2 Storage & Performance Considerations
### 3.2 儲存與效能考量

*   **Deduplication:** GitLab Container Registry uses Docker's layer content-addressable storage. If 50 microservices all use the same `alpine:3.18` base layer, that layer is stored only once physically (if using the unified storage driver).
*   **Cost:** Without cleanup policies, registries grow indefinitely. A typical CI pipeline building a 500MB image on every commit can generate Terabytes of waste in months.
*   **重複資料刪除：** GitLab Container Registry 使用 Docker 的分層內容定址儲存（Content-Addressable Storage）。如果 50 個微服務都使用相同的 `alpine:3.18` 基礎層，該層在實體上只會儲存一次（若使用統一儲存驅動）。
*   **成本：** 若無清理策略，Registry 將無限增長。一個典型的 CI Pipeline 若每次 commit 都建置 500MB 的映像檔，幾個月內就能產生數 TB 的浪費。

---

## 4. Walkthrough / Example
## 4. 逐步示例

### 4.1 Scenario: Publishing and Consuming a Private NPM Package
### 4.1 情境：發布並使用私有 NPM 套件

**Goal:** Create a shared UI library (`@techcorp/ui-kit`) and use it in a web application (`webapp-frontend`).
**目標：** 建立一個共享 UI 函式庫（`@techcorp/ui-kit`）並在 Web 應用程式（`webapp-frontend`）中使用它。

#### Step 1: Configure the Library Project (`ui-kit`)
#### 步驟 1：設定函式庫專案（`ui-kit`）

In `package.json`, define the publish configuration.
在 `package.json` 中定義發布設定。

```json
{
  "name": "@techcorp/ui-kit",
  "version": "1.0.0",
  "publishConfig": {
    "@techcorp:registry": "https://gitlab.example.com/api/v4/projects/<PROJECT_ID>/packages/npm/"
  }
}
```

In `.gitlab-ci.yml`, use `CI_JOB_TOKEN` to authenticate.
在 `.gitlab-ci.yml` 中，使用 `CI_JOB_TOKEN` 進行驗證。

```yaml
publish-npm:
  image: node:18
  stage: deploy
  script:
    # Configure npm to use GitLab registry for @techcorp scope
    - npm config set @techcorp:registry https://gitlab.example.com/api/v4/projects/${CI_PROJECT_ID}/packages/npm/
    # Authenticate using the CI job token
    - npm config set -- '//gitlab.example.com/api/v4/projects/${CI_PROJECT_ID}/packages/npm/:_authToken' "${CI_JOB_TOKEN}"
    - npm publish
  only:
    - tags
```

#### Step 2: Consuming in the Client Project (`webapp-frontend`)
#### 步驟 2：在客戶端專案（`webapp-frontend`）中使用

To install this package, the client project needs an `.npmrc` file.
為了安裝此套件，客戶端專案需要一個 `.npmrc` 檔案。

**Local Development (Developer's machine):**
**本地開發（開發者電腦）：**
Developers usually authenticate using a Personal Access Token (PAT).
開發者通常使用個人存取憑證（PAT）進行驗證。

**CI Environment:**
**CI 環境：**
Use `CI_JOB_TOKEN`. Note that the client project must have permission to access the library project (if private).
使用 `CI_JOB_TOKEN`。請注意，客戶端專案必須擁有存取函式庫專案的權限（若為私有專案）。

```bash
# .npmrc in the root of webapp-frontend
@techcorp:registry=https://gitlab.example.com/api/v4/packages/npm/
//gitlab.example.com/api/v4/packages/npm/:_authToken=${CI_JOB_TOKEN}
```
*Note: Using the instance-level or group-level endpoint (`/api/v4/packages/npm/`) allows resolving packages from multiple projects.*
*註：使用實例層級或群組層級的端點（`/api/v4/packages/npm/`）允許解析來自多個專案的套件。*

### 4.2 Scenario: Container Registry Cleanup Policy
### 4.2 情境：容器庫清理策略

**Problem:** Storage costs are spiking. We have thousands of `feature-branch` images that are no longer needed.
**問題：** 儲存成本飆升。我們有數千個不再需要的 `feature-branch` 映像檔。

**Solution:** Configure a Cleanup Policy (Settings -> Packages & Registries -> Cleanup policies).
**解法：** 設定清理策略（Settings -> Packages & Registries -> Cleanup policies）。

**Recommended Policy for Active Projects:**
**針對活躍專案的建議策略：**

*   **Keep these tags:** `latest`, `production`, `v.+` (Regex for semantic versions).
    **保留這些標籤：** `latest`, `production`, `v.+`（語意化版本的正規表示式）。
*   **Keep at least:** 10 tags (Safety net).
    **至少保留：** 10 個標籤（安全網）。
*   **Remove tags older than:** 30 days.
    **移除超過此天數的標籤：** 30 天。
*   **Remove tags matching:** `.*` (Catch-all for feature branches not protected above).
    **移除符合此規則的標籤：** `.*`（捕捉所有未被上述規則保護的功能分支）。

**Technical Detail:**
**技術細節：**
The policy only **untags** images (Soft Delete). The actual disk space is not freed until the **Garbage Collection** runs (usually a scheduled task on the GitLab instance by administrators).
此策略僅會**移除標籤**（軟刪除）。實際的磁碟空間直到**垃圾回收（Garbage Collection）**執行後才會釋放（通常由管理員在 GitLab 實例上設定排程任務）。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 Hardcoding Credentials in Codebase
### 5.1 在程式碼庫中硬編碼憑證

*   **Anti-pattern:** Committing `.npmrc` or `settings.xml` with a raw Personal Access Token (PAT) into the Git repo.
*   **Why it's bad:** Security risk. If the repo leaks, the token leaks. Tokens expire, breaking builds unexpectedly.
*   **Better approach:** Use environment variables (`${CI_JOB_TOKEN}`, `${DEPLOY_TOKEN}`) and inject them at runtime or via CI/CD variables.
*   **反模式：** 將包含原始 Personal Access Token (PAT) 的 `.npmrc` 或 `settings.xml` 提交到 Git repo。
*   **壞處：** 安全風險。若 repo 洩漏，Token 也隨之洩漏。Token 會過期，導致建置意外中斷。
*   **較佳做法：** 使用環境變數（`${CI_JOB_TOKEN}`, `${DEPLOY_TOKEN}`），並在執行時期或透過 CI/CD 變數注入。

### 5.2 The "Latest" Tag Trap
### 5.2 "Latest" 標籤陷阱

*   **Anti-pattern:** Deploying to production using `image: my-app:latest`.
*   **Why it's bad:** Non-deterministic. If you scale up the cluster and a new node pulls `latest`, it might get a different version than the existing nodes if `latest` was updated in the meantime. It also makes rollbacks difficult.
*   **Better approach:** Use specific tags (SHA, SemVer) or the `CI_COMMIT_SHA` as the Docker tag.
*   **反模式：** 使用 `image: my-app:latest` 部署到生產環境。
*   **壞處：** 非決定性。若擴展叢集且新節點拉取 `latest`，如果 `latest` 在此期間被更新，新節點可能會得到與現有節點不同的版本。這也讓 rollback 變得困難。
*   **較佳做法：** 使用特定標籤（SHA, SemVer）或使用 `CI_COMMIT_SHA` 作為 Docker tag。

### 5.3 Ignoring "Orphaned" Layers
### 5.3 忽略「孤兒」層

*   **Anti-pattern:** Deleting tags but never running Garbage Collection (GC).
*   **Why it's bad:** You lose the reference to the image manifest, but the binary blobs (layers) remain on disk/S3. You are paying for storage you can't access.
*   **Better approach:** Ensure the GitLab administrator has configured the Registry Garbage Collector to run in `delete` mode periodically.
*   **反模式：** 刪除標籤但從未執行垃圾回收（GC）。
*   **壞處：** 你失去了指向映像檔清單（Manifest）的參照，但二進位 Blob（層）仍保留在磁碟/S3 上。你在為無法存取的儲存空間付費。
*   **較佳做法：** 確保 GitLab 管理員已設定 Registry Garbage Collector 定期以 `delete` 模式執行。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### 6.1 Design a Multi-Region Registry Strategy
### 6.1 設計多區域 Registry 策略

*   **Question:** "We have a Kubernetes cluster in US-East and another in EU-West. Both need to pull images from our central GitLab Registry. Latency is high, and bandwidth costs are significant. How do you optimize this?"
*   **Key Points:**
    *   **Geo-replication:** If using GitLab Geo (Premium/Ultimate), replicate repositories and registries to secondary sites.
    *   **Pull-through Cache:** Configure a local registry mirror (like Harbor or Docker Registry proxy) inside each K8s cluster that proxies the central GitLab Registry.
    *   **CDN:** Use a CDN in front of the Registry storage backend (if supported/configured).
*   **問題：** 「我們在美東和歐西各有一個 Kubernetes 叢集。兩者都需要從中央 GitLab Registry 拉取映像檔。延遲很高，且頻寬成本顯著。你會如何優化？」
*   **回答要點：**
    *   **地理複製 (Geo-replication)：** 若使用 GitLab Geo (Premium/Ultimate)，將儲存庫與 Registry 複製到次要站點。
    *   **穿透式快取 (Pull-through Cache)：** 在每個 K8s 叢集內部配置本地 Registry 鏡像（如 Harbor 或 Docker Registry proxy），代理中央 GitLab Registry。
    *   **CDN：** 在 Registry 儲存後端前使用 CDN（若支援/已配置）。

### 6.2 Security Scanning and Compliance
### 6.2 安全掃描與合規

*   **Question:** "How do we ensure that no container image with 'Critical' vulnerabilities is ever deployed to production?"
*   **Key Points:**
    *   Enable **Container Scanning** in GitLab CI.
    *   Use **GitLab Operational Container Scanning** (Starboard/Trivy) for running images.
    *   Set up **Merge Request Approvals** based on vulnerability findings (Security Gates).
    *   Discuss the difference between scanning at build time vs. scanning the registry periodically (for new CVEs on old images).
*   **問題：** 「我們如何確保沒有任何帶有『嚴重』漏洞的容器映像檔被部署到生產環境？」
*   **回答要點：**
    *   在 GitLab CI 中啟用 **Container Scanning**。
    *   針對執行中的映像檔使用 **GitLab Operational Container Scanning** (Starboard/Trivy)。
    *   根據漏洞發現設定 **Merge Request Approvals**（安全閘門）。
    *   討論建置時掃描與定期掃描 Registry（針對舊映像檔的新 CVE）之間的差異。

### 6.3 Authentication Scopes
### 6.3 驗證範圍

*   **Question:** "Why does `CI_JOB_TOKEN` sometimes fail when project A tries to pull a package from project B?"
*   **Key Points:**
    *   `CI_JOB_TOKEN` permissions are tied to the user triggering the pipeline OR the project's allowlist (depending on GitLab version/settings).
    *   You may need to explicitly add Project A to Project B's "Job Token Access" allowlist (Settings -> CI/CD -> Token Access).
    *   Alternatively, use a Group Deploy Token for broader access.
*   **問題：** 「為什麼當專案 A 嘗試從專案 B 拉取套件時，`CI_JOB_TOKEN` 有時會失敗？」
*   **回答要點：**
    *   `CI_JOB_TOKEN` 的權限綁定於觸發 Pipeline 的使用者，或專案的允許清單（取決於 GitLab 版本/設定）。
    *   你可能需要明確將專案 A 加入專案 B 的「Job Token Access」允許清單（Settings -> CI/CD -> Token Access）。
    *   或者，使用 Group Deploy Token 以獲得更廣泛的存取權限。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Summary
### 小結

1.  **Integrated Ecosystem**: GitLab Registry eliminates the need for external artifact managers, simplifying authentication and pipeline integration.
    **整合生態系**：GitLab Registry 消除對外部產物管理工具的需求，簡化了驗證與 Pipeline 整合。
2.  **Scope Matters**: Understand the difference between Project, Group, and Instance-level endpoints for resolving dependencies.
    **範圍很重要**：理解專案、群組與實例層級端點在解析相依性時的差異。
3.  **Cleanup is Mandatory**: Without aggressive cleanup policies and garbage collection, registries become a massive cost center.
    **清理是強制的**：若無積極的清理策略與垃圾回收，Registry 將成為巨大的成本中心。
4.  **Security First**: Use `CI_JOB_TOKEN` or Deploy Tokens instead of personal credentials; scan images for vulnerabilities before pushing.
    **安全優先**：使用 `CI_JOB_TOKEN` 或 Deploy Tokens 取代個人憑證；在 push 前掃描映像檔漏洞。
5.  **Immutability**: Prefer specific tags (SHA/SemVer) over `latest` to ensure reproducible deployments.
    **不可變性**：優先使用特定標籤（SHA/SemVer）而非 `latest`，以確保可重現的部署。

### Next Steps
### 後續延伸

*   **Advanced Security**: Proceed to **Chapter 10: DevSecOps & Security Scanning** to learn how to automatically block artifacts with vulnerabilities.
    **進階安全**：前往 **第 10 章：DevSecOps 與安全掃描**，學習如何自動阻擋含有漏洞的產物。
*   **GitLab Geo**: If working in a distributed team, investigate how to replicate registries across regions for faster pulls.
    **GitLab Geo**：若在分散式團隊工作，研究如何跨區域複製 Registry 以加快拉取速度。
*   **Dependency Proxy**: Configure the Dependency Proxy to cache upstream images (like from Docker Hub) to improve reliability and speed.
    **Dependency Proxy**：設定 Dependency Proxy 以快取上游映像檔（如來自 Docker Hub），提升可靠性與速度。