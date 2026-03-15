# Chapter 06: GitHub Packages & Artifact Management
# 第六章：GitHub Packages 與 Artifact 管理

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

In modern DevOps practices, source code is merely the raw material; the actual deliverables are the **Artifacts** (Docker images, JARs, npm packages). GitHub Packages transforms GitHub from a code warehouse into a comprehensive software supply chain platform. For Senior Engineers, mastering this goes beyond "knowing how to push an image"; it involves designing a secure, efficient, and traceable delivery pipeline.

在現代 DevOps 實踐中，原始碼僅是原料，真正的交付物是 **Artifacts**（如 Docker images, JARs, npm packages）。GitHub Packages 將 GitHub 從單純的程式碼倉庫轉變為完整的軟體供應鏈平台。對於資深工程師而言，掌握這項技能不僅是「知道如何上傳映像檔」，更在於設計一套安全、高效且可追溯的交付流水線。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Design a Unified Registry Strategy**: Integrate GitHub Container Registry (GHCR) and language-specific registries (npm, Maven, NuGet) to replace or augment external services like Docker Hub or Nexus.
    **設計統一的 Registry 策略**：整合 GitHub Container Registry (GHCR) 與特定語言的 Registry（npm, Maven, NuGet），以取代或增強 Docker Hub 或 Nexus 等外部服務。
2.  **Manage Cross-Project Dependencies**: Implement "InnerSource" workflows where internal shared libraries are versioned and consumed securely across different repositories within an organization.
    **管理跨專案相依性**：實作「內部開源（InnerSource）」工作流，確保內部共用函式庫在組織內不同儲存庫間能安全地進行版本控制與引用。
3.  **Enforce Supply Chain Security**: Utilize OIDC and granular permissions (`GITHUB_TOKEN`) to secure artifact publishing, eliminating the need for long-lived Personal Access Tokens (PATs).
    **落實供應鏈安全**：利用 OIDC 與細粒度權限（`GITHUB_TOKEN`）來保護 Artifact 的發布過程，消除對長期有效的個人存取權杖（PATs）之依賴。
4.  **Optimize Storage & Costs**: Configure retention policies to manage artifact lifecycle, preventing storage bloat from CI/CD snapshots.
    **優化儲存與成本**：設定保留策略（Retention Policies）來管理 Artifact 生命週期，防止 CI/CD 快照造成儲存空間膨脹。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 The "Factory vs. Warehouse" Analogy
### 2.1 「工廠 vs. 倉庫」類比

Think of a **GitHub Repository** as the **Factory** where code is assembled. **GitHub Actions** is the **Assembly Line**. **GitHub Packages** is the **Warehouse** where finished goods are stored before distribution.

將 **GitHub Repository** 視為組裝程式碼的 **工廠**。**GitHub Actions** 是 **組裝流水線**。**GitHub Packages** 則是 **倉庫**，用於在分發前儲存製成品。

*   **Source Code**: Mutable, changes frequently (commits).
    **原始碼**：可變的，頻繁變動（commits）。
*   **Artifact**: Immutable, versioned snapshot of the code (e.g., `v1.0.0`). Once published, it should never change (though it can be deleted).
    **Artifact**：不可變的，程式碼的版本化快照（例如 `v1.0.0`）。一旦發布就不應更改（儘管可以被刪除）。

### 2.2 Scope & Visibility: Repository vs. Organization
### 2.2 範圍與可見性：Repository vs. Organization

A common confusion arises between repository-scoped packages and organization-scoped packages.
一個常見的混淆點在於「Repository 範圍」與「Organization 範圍」的套件差異。

*   **Repository-scoped (Legacy/Language specific)**: Often tied strictly to the repo. Permissions mirror the repo's permissions.
    **Repository 範圍（舊版/特定語言）**：通常與 Repo 嚴格綁定。權限鏡像於 Repo 的權限。
*   **Organization-scoped (Container Registry - GHCR)**: The package lives at the Org level (e.g., `ghcr.io/my-org/my-image`). It can be linked to a repo for traceability (Software Bill of Materials), but its permissions can be managed independently. This is crucial for sharing base images across multiple projects.
    **Organization 範圍（Container Registry - GHCR）**：套件存在於組織層級（例如 `ghcr.io/my-org/my-image`）。它可以連結到 Repo 以實現可追溯性（軟體物料清單），但其權限可獨立管理。這對於在多個專案間共用 Base Images 至關重要。

### 2.3 Authentication Model
### 2.3 驗證模型

Unlike external registries (AWS ECR, Docker Hub) that require managing separate secrets, GitHub Packages integrates natively with GitHub's auth.
不同於需要管理獨立 Secret 的外部 Registry（AWS ECR, Docker Hub），GitHub Packages 原生整合了 GitHub 的驗證機制。

*   **CI/CD**: Uses the ephemeral `GITHUB_TOKEN`. No need to rotate secrets.
    **CI/CD**：使用短暫存在的 `GITHUB_TOKEN`。無需輪替 Secret。
*   **Local Dev**: Uses your Personal Access Token (PAT) or GitHub CLI (`gh auth login`).
    **本地開發**：使用你的個人存取權杖（PAT）或 GitHub CLI (`gh auth login`)。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### 3.1 Architecture: The InnerSource Supply Chain
### 3.1 架構：內部開源供應鏈

In a microservices architecture, you often have shared libraries (e.g., `common-auth`, `logger-lib`) used by multiple services.
在微服務架構中，通常會有被多個服務使用的共用函式庫（例如 `common-auth`, `logger-lib`）。

**Flow:**
1.  **Shared Lib Repo**: Developer pushes code -> Action tests & builds -> Publishes `npm`/`maven` package to GitHub Packages.
2.  **Service Repo**: Developer updates dependency version -> Action builds Docker image (pulling the private lib) -> Pushes Docker image to `ghcr.io`.
3.  **Deployment**: Kubernetes/Cloud Run pulls the image from `ghcr.io` using a K8s Secret (docker-registry type) derived from a GitHub PAT or Robot Account.

**流程：**
1.  **共用函式庫 Repo**：開發者推送程式碼 -> Action 測試與建置 -> 發布 `npm`/`maven` 套件至 GitHub Packages。
2.  **服務 Repo**：開發者更新相依版本 -> Action 建置 Docker image（拉取私有函式庫） -> 推送 Docker image 至 `ghcr.io`。
3.  **部署**：Kubernetes/Cloud Run 從 `ghcr.io` 拉取映像檔，使用源自 GitHub PAT 或 Robot Account 的 K8s Secret。

### 3.2 Impact on System Quality
### 3.2 對系統品質的影響

*   **Security (安全性)**:
    *   **Provenance**: You can trace exactly which commit and workflow run produced a specific Docker image.
    *   **Private Access**: No need to expose internal libraries to public registries (npmjs.com) just to share them.
    *   **來源證明**：你可以精確追溯是哪一個 commit 和 workflow run 產生了特定的 Docker image。
    *   **私有存取**：無需為了共用而將內部函式庫暴露在公開 Registry（npmjs.com）。

*   **Maintainability (可維護性)**:
    *   **Versioning**: Forces strict semantic versioning. Services don't break randomly because they depend on a specific immutable version, not a moving branch.
    *   **版本控制**：強制執行嚴格的語意化版本控制。服務不會隨機崩潰，因為它們依賴於特定的不可變版本，而非變動的分支。

*   **Performance (效能)**:
    *   **Network Proximity**: GitHub Actions runners pull from GitHub Packages faster than from external registries, reducing build times.
    *   **網路鄰近性**：GitHub Actions runners 從 GitHub Packages 拉取套件的速度比從外部 Registry 快，從而減少建置時間。

---

## 4. Walkthrough: Publishing & Consuming a Private Package
## 4. 逐步示例：發布與使用私有套件

Let's look at a scenario involving a Node.js shared library and a Dockerized service.
我們來看一個包含 Node.js 共用函式庫與 Docker 化服務的場景。

### Scenario 1: Publishing a Private npm Package
### 場景 1：發布私有 npm 套件

**Objective**: Publish `@my-org/core-utils` so other internal projects can `npm install` it.
**目標**：發布 `@my-org/core-utils`，以便其他內部專案可以執行 `npm install`。

**1. Configuration (`package.json`):**
You must tell npm to point to GitHub's registry, not the public npm registry.
**1. 設定 (`package.json`)：**
你必須告訴 npm 指向 GitHub 的 Registry，而非公開的 npm Registry。

```json
{
  "name": "@my-org/core-utils",
  "version": "1.0.0",
  "publishConfig": {
    "registry": "https://npm.pkg.github.com/"
  },
  "repository": "git://github.com/my-org/core-utils.git"
}
```

**2. GitHub Actions Workflow (`.github/workflows/publish.yml`):**
**2. GitHub Actions 工作流程 (`.github/workflows/publish.yml`)：**

```yaml
name: Publish Package
on:
  release:
    types: [created] # Trigger on GitHub Release creation

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write # Crucial: Allow writing to Packages
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          registry-url: 'https://npm.pkg.github.com'
          scope: '@my-org'
      
      - run: npm ci
      - run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }} 
          # setup-node creates an .npmrc utilizing this env var
```

### Scenario 2: Building & Pushing a Docker Image to GHCR
### 場景 2：建置並推送 Docker Image 至 GHCR

**Objective**: Build a service image and push to `ghcr.io/my-org/my-service`.
**目標**：建置服務映像檔並推送至 `ghcr.io/my-org/my-service`。

**GitHub Actions Workflow:**

```yaml
name: Build and Push Docker Image
on:
  push:
    branches: ['main']

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write # Required to push to GHCR
      
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Log in to the Container registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata (tags, labels) for Docker
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha
            type=ref,event=branch
            type=semver,pattern={{version}}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
```

**Why this is robust (為何這很穩健):**
1.  **Dynamic Metadata**: `docker/metadata-action` automatically generates tags like `main`, `sha-1234567`, and `v1.0.0` based on the git context.
    **動態 Metadata**：`docker/metadata-action` 會根據 git context 自動產生 `main`, `sha-1234567`, 和 `v1.0.0` 等標籤。
2.  **Permissions**: Uses strict `permissions` block.
    **權限**：使用嚴格的 `permissions` 區塊。
3.  **No Long-lived Secrets**: Uses `GITHUB_TOKEN` for auth.
    **無長期 Secret**：使用 `GITHUB_TOKEN` 進行驗證。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 The "Storage Bloat" Trap
### 5.1 「儲存膨脹」陷阱

*   **Anti-pattern**: Pushing a new Docker image tag for *every* commit to `main` without a retention policy.
    **反模式**：針對 `main` 的 *每次* commit 都推送新的 Docker image tag，且沒有設定保留策略。
*   **Consequence**: You hit storage limits quickly, incurring extra costs.
    **後果**：你會迅速達到儲存上限，產生額外費用。
*   **Solution**: Configure **Package Retention Policies** in GitHub settings. For example, keep only the last 10 versions of untagged images, or delete images older than 30 days unless tagged with `release-*`.
    **解法**：在 GitHub 設定中配置 **套件保留策略（Package Retention Policies）**。例如，只保留最後 10 個未標記版本的映像檔，或刪除超過 30 天且未標記 `release-*` 的映像檔。

### 5.2 Local vs. CI Auth Confusion
### 5.2 本地與 CI 驗證混淆

*   **Anti-pattern**: Checking in an `.npmrc` file containing a hardcoded auth token or assuming the developer's environment matches CI.
    **反模式**：將包含硬編碼 auth token 的 `.npmrc` 檔案簽入版控，或假設開發者環境與 CI 一致。
*   **Consequence**: "It works on my machine" but fails in CI, or security leaks.
    **後果**：「在我的機器上可以跑」但在 CI 失敗，或造成安全洩漏。
*   **Solution**: Use env vars in `.npmrc` (`//npm.pkg.github.com/:_authToken=${NODE_AUTH_TOKEN}`) and ensure developers set this var in their shell profile (using a PAT), while CI uses `secrets.GITHUB_TOKEN`.
    **解法**：在 `.npmrc` 中使用環境變數（`//npm.pkg.github.com/:_authToken=${NODE_AUTH_TOKEN}`），並確保開發者在其 Shell 設定檔中設定此變數（使用 PAT），而 CI 則使用 `secrets.GITHUB_TOKEN`。

### 5.3 Mutable "Latest" Tag in Production
### 5.3 在正式環境使用可變的 "Latest" 標籤

*   **Anti-pattern**: Deploying `ghcr.io/org/app:latest` to production.
    **反模式**：部署 `ghcr.io/org/app:latest` 到正式環境。
*   **Consequence**: You don't know exactly which code is running. Rollbacks are difficult because `latest` has been overwritten.
    **後果**：你無法確切知道正在執行哪份程式碼。因為 `latest` 已被覆寫，回滾變得困難。
*   **Solution**: Deploy using immutable tags (e.g., `v1.2.3` or `sha-a1b2c3d`). Use `latest` only for convenience in development.
    **解法**：使用不可變標籤（如 `v1.2.3` 或 `sha-a1b2c3d`）進行部署。`latest` 僅用於開發時的便利。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How would you design a secure artifact workflow for a regulated industry (e.g., Fintech)?
### Q1: 你會如何為受監管產業（如金融科技）設計安全的 Artifact 工作流程？

*   **Key Points**:
    *   **Immutability**: Ensure artifacts cannot be overwritten.
    *   **Signing**: Use **Sigstore / Cosign** to sign container images in the CI pipeline.
    *   **Scanning**: Integrate vulnerability scanning (Trivy or GitHub Advanced Security) *before* pushing to the registry.
    *   **Provenance**: Use GitHub Actions to generate SLSA (Supply-chain Levels for Software Artifacts) provenance to prove the binary came from the expected source code.
*   **高分回答要點**：
    *   **不可變性**：確保 Artifact 無法被覆寫。
    *   **簽章**：在 CI 流水線中使用 **Sigstore / Cosign** 對容器映像檔進行簽章。
    *   **掃描**：在推送到 Registry *之前* 整合漏洞掃描（Trivy 或 GitHub Advanced Security）。
    *   **來源證明**：使用 GitHub Actions 產生 SLSA（軟體 Artifact 供應鏈等級）來源證明，以證明二進位檔來自預期的原始碼。

### Q2: We have a monorepo with 50 microservices. How do we manage Docker images efficiently using GHCR?
### Q2: 我們有一個包含 50 個微服務的 Monorepo。如何使用 GHCR 高效管理 Docker Images？

*   **Key Points**:
    *   **Naming Convention**: Use namespaced images (e.g., `ghcr.io/org/monorepo/service-a`).
    *   **Selective Build**: Use `paths` filter in GitHub Actions to only build and push images for services that actually changed.
    *   **Caching**: Utilize Docker layer caching (using `gha` cache exporter) to speed up builds since many services likely share the same base image layers.
*   **高分回答要點**：
    *   **命名慣例**：使用命名空間化的映像檔（例如 `ghcr.io/org/monorepo/service-a`）。
    *   **選擇性建置**：在 GitHub Actions 中使用 `paths` 過濾器，僅針對實際變更的服務建置並推送映像檔。
    *   **快取**：利用 Docker 層快取（使用 `gha` cache exporter）來加速建置，因為許多服務可能共用相同的 Base Image 層。

### Q3: Compare GitHub Packages vs. Artifactory/Nexus. When would you stick with the latter?
### Q3: 比較 GitHub Packages 與 Artifactory/Nexus。什麼時候你會堅持使用後者？

*   **Key Points**:
    *   **GitHub Packages Pros**: Integrated Auth, zero setup, closer to code.
    *   **Artifactory Pros**: Better support for proxying/caching remote repositories (e.g., caching npmjs.com to avoid rate limits), more granular retention policies, supports legacy formats not on GitHub yet.
    *   **Decision**: If the org is all-in on GitHub, use Packages. If you need a centralized proxy for *all* external dependencies (to firewall off the internet), Artifactory is better.
*   **高分回答要點**：
    *   **GitHub Packages 優點**：整合驗證、零設定、更貼近程式碼。
    *   **Artifactory 優點**：對代理/快取遠端儲存庫有更好的支援（例如快取 npmjs.com 以避免速率限制）、更細粒度的保留策略、支援 GitHub 尚未支援的舊格式。
    *   **決策**：如果組織全面採用 GitHub，使用 Packages。如果你需要一個針對 *所有* 外部相依性的集中式代理（以防火牆隔絕網際網路），Artifactory 較佳。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Summary
### 小結

1.  **Unified Auth**: Access code and packages with a single identity (`GITHUB_TOKEN` / PAT).
    **統一驗證**：使用單一身份（`GITHUB_TOKEN` / PAT）存取程式碼與套件。
2.  **Container First**: `ghcr.io` is the modern standard for GitHub-hosted Docker images, offering org-level visibility.
    **容器優先**：`ghcr.io` 是 GitHub 託管 Docker 映像檔的現代標準，提供組織層級的可見性。
3.  **Security Integration**: Tight coupling with Actions allows for automated provenance and signing, key for secure supply chains.
    **安全整合**：與 Actions 的緊密耦合允許自動化的來源證明與簽章，這對安全供應鏈至關重要。
4.  **Lifecycle Management**: Active management of retention policies is mandatory to control costs.
    **生命週期管理**：主動管理保留策略對於控制成本是強制性的。

### Next Steps
### 後續延伸

*   **Advanced Security**: Study **Sigstore** and **Cosign** to implement image signing within GitHub Actions.
    **進階安全**：研究 **Sigstore** 與 **Cosign**，以在 GitHub Actions 中實作映像檔簽章。
*   **Dependency Management**: Explore **Dependabot** configuration to automatically update the private packages you just published across your repositories.
    **相依性管理**：探索 **Dependabot** 設定，以自動在你的儲存庫間更新你剛剛發布的私有套件。
*   **Next Chapter**: Proceed to **Chapter 07: GitHub Actions Advanced Workflows** (Self-hosted runners & Composite Actions).
    **下一章**：前往 **第七章：GitHub Actions 進階工作流程**（Self-hosted runners 與 Composite Actions）。