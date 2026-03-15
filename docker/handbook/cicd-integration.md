# CI/CD 整合策略：構建、標籤與發佈 / CI/CD Integration Strategy: Build, Tag, and Publish

## Mental model｜心智模型

在設計容器化的 CI/CD 流水線時，最核心的心智模型是 **「不可變產物」 (Immutable Artifact)** 與 **「一次構建，到處運行」 (Build Once, Run Anywhere)**。

傳統的部署模式可能是在不同環境（Dev, Staging, Prod）分別拉取程式碼並重新編譯或設定；但在 Docker 的世界裡，CI 的產出物（Artifact）就是 Docker Image。

1.  **工廠流水線隱喻 (The Factory Assembly Line)**：
    *   **CI (Continuous Integration)** 是工廠的組裝線。它的職責是將原始碼、依賴項打包成一個密封的箱子（Docker Image）。
    *   **Registry** 是倉庫。箱子一旦封箱（Build & Push），就不應該再被打開修改。
    *   **CD (Continuous Deployment)** 是物流配送。它負責將同一個箱子運送到不同的目的地（環境）。你不會因為目的地是「生產環境」就拆開箱子重新組裝，你只會更換箱子外面的「配送標籤」（環境變數與配置）。

2.  **信任鏈 (Chain of Trust)**：
    *   每一個 Image 必須能回溯到唯一的 Git Commit。
    *   如果 Image 在 Staging 測試通過，部署到 Production 的必須是 **同一個 Image ID**（或 Digest），而不僅僅是同一個 Git Tag 重新構建的版本。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 標籤策略：SHA 與 SemVer 的組合拳 (Tagging Strategy)
不要只依賴 `latest` 標籤。一個健壯的策略通常包含以下幾種標籤的組合：

*   **Immutable Identifier (不可變標識)**: 使用 Git Commit SHA（短碼，如 `a1b2c3d`）作為主要的 Image Tag。這是 CI 內部追蹤與回滾的黃金標準。
*   **Semantic Versioning (語意化版本)**: 當發佈 Release 時，加上 `v1.0.1`、`v1.0`、`v1` 等標籤。這是給人類和外部系統看的。
*   **Rolling Tags (滾動標籤)**: 僅在特定情境使用，如 `main` 或 `nightly`，代表該分支的最新狀態，但不應用於生產環境部署設定檔中。

### 2. 快取優化 (CI Caching)
CI Runner 通常是無狀態的，每次重新拉取 Base Image 和安裝依賴非常耗時。
*   **Registry Cache**: 使用 `--cache-from` 指令，嘗試從 Registry 拉取舊的 Image 作為快取來源。
*   **BuildKit**: 啟用 Docker BuildKit (`DOCKER_BUILDKIT=1`)，它支援更高效的並行構建與快取掛載 (`--mount=type=cache`)。

### 3. 映像檔掃描 (Image Scanning)
將安全性檢查左移 (Shift Left)。在 Push 到 Registry 之前或之後立即執行掃描。
*   使用工具如 **Trivy** 或 **Grype** 掃描 OS 套件與應用程式依賴的 CVE (Common Vulnerabilities and Exposures)。
*   設定閥值 (Threshold)：例如，只有當出現 `CRITICAL` 漏洞時才中斷 Pipeline，`MEDIUM` 則僅發出警告。

### 4. 多架構構建 (Multi-arch Builds)
隨著 ARM 架構（如 AWS Graviton, Apple Silicon）普及，單一架構 Image 已不足夠。
*   使用 `docker buildx` 構建多架構 Image (amd64, arm64) 並推送到同一個 Tag 下。這能確保開發人員（可能用 Mac M1/M2）與生產環境（可能用 Linux x86）體驗一致。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Latest" Trap (濫用 latest 標籤)
*   **反模式**：在 Kubernetes Deployment yaml 或 docker-compose 中指定 `image: my-app:latest`。
*   **後果**：你不知道生產環境到底跑的是哪個版本。當需要回滾 (Rollback) 時，你無法精確回到上一個狀態，因為 `latest` 是可變的指針。
*   **修正**：部署時使用具體的 `SHA` tag 或 `v1.2.3` tag。

### 2. Rebuilding for Environments (為不同環境重構建)
*   **反模式**：CI 流程中有 `build-dev`、`build-staging`、`build-prod` 等步驟，分別將環境變數打包進 Image。
*   **後果**：違反「不可變產物」原則。你在 Staging 測過的 Image 與 Prod 的 Image 本質上是不同的二進位檔案，可能導致 "It works in staging but fails in prod"。
*   **修正**：構建一次，通過環境變數 (Env Vars) 或 ConfigMap 在運行時注入配置。

### 3. Leaking Secrets in Layers (在層中洩漏機密)
*   **反模式**：`COPY .env .` 或在 `RUN` 指令中使用 `export API_KEY=...`。
*   **後果**：即使你在後面的 Layer 刪除了該檔案，駭客仍可透過 `docker history` 或檢視 Layer 內容找回機密。
*   **修正**：使用 Docker 的 `--secret` mount 功能，確保機密不被寫入 Image Layer。

### 4. Ignoring .dockerignore (忽略上下文優化)
*   **反模式**：執行 `COPY . .` 時將 `.git` 目錄、`node_modules`、測試報告或本地臨時檔案全部複製進去。
*   **後果**：Image 體積膨脹，CI 上傳時間變長，且增加安全風險。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Tagging Logic
在 CI Script 中決定如何標記 Image 的決策樹：

1.  **Is this a Pull Request?**
    *   Yes -> Tag with `pr-{number}` (Optional, for preview environments).
2.  **Is this a push to Main/Master?**
    *   Yes -> Tag with `git-sha` (Required).
    *   Yes -> Tag with `edge` or `main` (Optional, for dev env).
3.  **Is this a Git Tag (Release)?**
    *   Yes -> Tag with `git-sha` (Required).
    *   Yes -> Tag with `v1.2.3` (SemVer).
    *   Yes -> Tag with `latest` (Optional, but use with caution).

### CI Pipeline Checklist
在合併 CI 設定檔前，請檢查以下項目：

- [ ] **Linting**: 是否加入了 Dockerfile Linter (如 `hadolint`)？
- [ ] **Context Control**: 是否設定了 `.dockerignore` 排除非必要檔案？
- [ ] **Deterministic Tag**: 是否為每次構建產生了唯一的 Tag (Git SHA)？
- [ ] **Security Scan**: 是否整合了漏洞掃描步驟 (Trivy/Clair)？
- [ ] **No Secrets**: 是否確認沒有將 `ARG` 或 `ENV` 用於傳遞敏感資訊？
- [ ] **Clean Up**: CI Runner 是否有定期清理舊 Image 的機制（避免磁碟爆滿）？

---

## Real-world examples｜實戰案例

### 案例：GitHub Actions Workflow (簡化版)

這是一個展示「構建、快取、標籤、掃描、發佈」的標準流程。

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ "main" ]
    tags: [ "v*.*.*" ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      # 1. 設定 Docker Buildx (為了快取與多架構)
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      # 2. 登入 Registry
      - name: Log into registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      # 3. 提取 Metadata (自動產生 tags: main, sha-xxxx, v1.0.0)
      - name: Extract Docker metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=sha,format=long

      # 4. 構建並匯出到本地 Docker (為了掃描)
      - name: Build and export to Docker
        uses: docker/build-push-action@v4
        with:
          context: .
          load: true # 不 Push，先 load 到本地 daemon
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:test
          cache-from: type=gha # GitHub Actions Cache
          cache-to: type=gha,mode=max

      # 5. 安全掃描 (Trivy)
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: '${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:test'
          format: 'table'
          exit-code: '1' # 發現嚴重漏洞則失敗
          ignore-unfixed: true
          vuln-type: 'os,library'
          severity: 'CRITICAL,HIGH'

      # 6. 真正的 Push (如果掃描通過)
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### 實戰技巧：The "Promote" Pattern

在更嚴謹的企業環境中，Image 不會直接 Push 到 Production Registry。

1.  **CI Build**: 構建 Image -> Push 到 `dev-registry`。
2.  **CD Dev**: 部署到 Dev 環境。
3.  **CD Staging**: 測試通過後，**Retag** 該 Image (不重新構建) -> Push 到 `staging-registry`。
4.  **CD Prod**: Staging 驗收後，**Retag** 該 Image -> Push 到 `prod-registry`。

```bash
# Promotion Script 範例 (Pseudo-code)
SOURCE_IMAGE="dev-registry.com/app:sha-a1b2c3d"
TARGET_IMAGE="prod-registry.com/app:v1.0.0"

# 拉取、重新標籤、推送 (無需重新 build)
docker pull $SOURCE_IMAGE
docker tag $SOURCE_IMAGE $TARGET_IMAGE
docker push $TARGET_IMAGE
```

這種模式確保了你在生產環境運行的 bits (二進位資料) 與你在測試環境驗證過的 bits 絕對一致。