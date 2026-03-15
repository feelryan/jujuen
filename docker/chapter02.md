# Chapter 02: Advanced Image Building and Optimization
# 第 02 章：高效能映像檔建置與最佳化

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

In a production environment, a Docker image is more than just a packaging format; it is the fundamental unit of deployment. For a Senior Engineer, optimizing images is not merely about saving disk space—it directly impacts **deployment latency (scaling speed)**, **security posture (attack surface)**, and **CI/CD efficiency**.

在正式生產環境中，Docker 映像檔不僅僅是一種打包格式，它是部署的基本單位。對於資深工程師而言，最佳化映像檔不僅是為了節省磁碟空間，更直接影響 **部署延遲（擴展速度）**、**安全性態勢（攻擊面）** 以及 **CI/CD 的效率**。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Master Multi-stage Builds:** Decouple the build environment from the runtime environment to produce minimal artifacts.
    **掌握多階段建置（Multi-stage Builds）：** 將建置環境與執行環境解耦，產出極小化的交付物。
2.  **Leverage Layer Caching Strategy:** Design `Dockerfile` instructions to maximize cache hit rates, drastically reducing build times.
    **運用層快取策略（Layer Caching Strategy）：** 設計 `Dockerfile` 指令以最大化快取命中率，大幅縮短建置時間。
3.  **Implement Distroless/Scratch Patterns:** Utilize minimal base images to remove non-essential binaries (like shells), enhancing security.
    **實作 Distroless/Scratch 模式：** 使用最小化基底映像檔移除不必要的二進位檔（如 Shell），提升安全性。
4.  **Optimize Build Context:** Understand how the Docker daemon receives context and how to optimize it using `.dockerignore`.
    **最佳化建置上下文（Build Context）：** 理解 Docker daemon 如何接收上下文，並使用 `.dockerignore` 進行最佳化。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 The Layered Architecture & Copy-on-Write (CoW)
### 2.1 分層架構與寫入時複製（CoW）

**Mental Model:** Think of a Docker image as a stack of transparent overhead projector sheets (layers). Each instruction (`RUN`, `COPY`, `ADD`) creates a new sheet. When you look from the top down, you see the combined result. If a file is modified in a higher layer, it "covers up" the version in the lower layer, but the lower layer's weight (size) still exists in the final artifact.

**心智模型：** 將 Docker 映像檔想像成一疊透明投影片（Layers）。每一個指令（`RUN`、`COPY`、`ADD`）都會產生一張新的投影片。當你從上往下看時，看到的是疊加後的結果。如果上層修改了某個檔案，它會「遮蓋」住下層的版本，但下層的重量（大小）依然存在於最終產物中。

**Key Takeaway:** Deleting a file in a subsequent layer (e.g., `RUN rm -rf ...`) does **not** reduce the image size; it merely hides the file. To actually reduce size, creation and deletion must happen in the *same* layer.

**關鍵重點：** 在後續的層中刪除檔案（例如 `RUN rm -rf ...`）**不會** 減少映像檔的大小，它只是隱藏了該檔案。要真正減少大小，建立與刪除必須發生在 *同一層* 中。

### 2.2 The Build Context
### 2.2 建置上下文

**Mental Model:** When you run `docker build .`, the CLI does not build the image locally. Instead, it packages the current directory (the context) into a tarball and uploads it to the Docker Daemon (which might be remote).

**心智模型：** 當你執行 `docker build .` 時，CLI 並非在本地直接建置映像檔。相反地，它會將當前目錄（上下文）打包成一個 tarball 並上傳給 Docker Daemon（這可能是遠端的）。

**Implication:** Including `.git` folders, `node_modules`, or large temp files in your context slows down the build start time significantly.

**影響：** 如果在上下文中包含 `.git` 資料夾、`node_modules` 或大型暫存檔，將顯著拖慢建置的啟動時間。

### 2.3 Base Image Hierarchy: OS vs. Slim vs. Distroless
### 2.3 基底映像檔階層：OS vs. Slim vs. Distroless

*   **Full OS (e.g., `ubuntu`, `debian`):** Contains a full package manager, shell, and common utilities. Useful for debugging but heavy and insecure.
*   **Slim (e.g., `debian:slim`):** Stripped down but still has a shell and package manager. A good middle ground.
*   **Alpine (e.g., `node:alpine`):** Uses `musl libc` instead of `glibc`. Extremely small (5MB base), but can cause compatibility issues with C-extensions (e.g., Python numpy, Node gyp).
*   **Distroless (Google):** Contains *only* the application and its runtime dependencies. No shell, no package manager. Maximum security.

*   **完整 OS（如 `ubuntu`, `debian`）：** 包含完整的套件管理員、Shell 和常用工具。便於除錯，但體積大且較不安全。
*   **Slim（如 `debian:slim`）：** 經過精簡，但仍保留 Shell 和套件管理員。不錯的中庸之道。
*   **Alpine（如 `node:alpine`）：** 使用 `musl libc` 取代 `glibc`。極小（基底約 5MB），但可能導致 C 擴充套件（如 Python numpy, Node gyp）的相容性問題。
*   **Distroless（Google）：** *僅* 包含應用程式及其執行時期依賴。沒有 Shell，沒有套件管理員。安全性最高。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### 3.1 Impact on Horizontal Scaling (HPA)
### 3.1 對水平擴展（HPA）的影響

In a Kubernetes environment, when traffic spikes, the Horizontal Pod Autoscaler (HPA) requests new pods. The total time to serve traffic is:
`T_ready = T_schedule + T_pull_image + T_container_start + T_readiness_probe`

在 Kubernetes 環境中，當流量激增時，水平 Pod 自動擴展器（HPA）會請求新的 Pod。服務流量所需的總時間為：
`T_ready = T_schedule + T_pull_image + T_container_start + T_readiness_probe`

For a 1GB image, `T_pull_image` can take 30-60 seconds on a fresh node. For a 50MB image, it takes seconds. **Image optimization is a latency optimization for your system's elasticity.**

對於 1GB 的映像檔，在全新的節點上 `T_pull_image` 可能需要 30-60 秒。而對於 50MB 的映像檔，僅需數秒。**映像檔最佳化即是對系統彈性（Elasticity）的延遲最佳化。**

### 3.2 Security & Compliance
### 3.2 安全性與合規性

In Big Tech, security teams scan images for CVEs (Common Vulnerabilities and Exposures).
*   **Attack Surface:** A full OS image has thousands of packages (curl, wget, netcat) that attackers can use for "Living off the Land" attacks if they compromise your container.
*   **Maintenance:** Fewer libraries mean fewer CVE alerts to patch.

在大型科技公司，資安團隊會掃描映像檔中的 CVE（通用漏洞揭露）。
*   **攻擊面：** 完整的 OS 映像檔包含數千個套件（curl, wget, netcat），如果容器被攻陷，攻擊者可利用這些工具進行「寄生攻擊（Living off the Land）」。
*   **維護成本：** 函式庫越少，意味著需要修補的 CVE 警報越少。

---

## 4. Walkthrough: Optimizing a Node.js Application
## 4. 逐步示例：最佳化 Node.js 應用程式

Let's optimize a typical Node.js API service.
讓我們來最佳化一個典型的 Node.js API 服務。

### Phase 1: The Naive Approach (Anti-pattern)
### 第一階段：天真的做法（反模式）

```dockerfile
# Bad Practice
FROM node:18

# Copying everything first invalidates cache for subsequent steps whenever code changes
COPY . /app
WORKDIR /app

# Installing dependencies every time code changes
RUN npm install
RUN npm run build

CMD ["npm", "start"]
```

**Issues:**
1.  **Cache Busting:** Changing one line of code invalidates the `COPY . /app` layer, forcing `npm install` to run again. Slow builds.
2.  **Size:** Includes devDependencies (like TypeScript, test runners) in production.
3.  **Security:** Runs as `root` by default.

**問題：**
1.  **快取失效：** 修改一行程式碼就會使 `COPY . /app` 層失效，強迫 `npm install` 重新執行。建置緩慢。
2.  **體積：** 在生產環境中包含了開發依賴（devDependencies，如 TypeScript、測試執行器）。
3.  **安全性：** 預設以 `root` 身份執行。

### Phase 2: Layer Caching & Multi-stage Build (Production Ready)
### 第二階段：層快取與多階段建置（生產就緒）

We separate the "Builder" (needs compilers, python, dev deps) from the "Runner" (needs only runtime deps).

我們將「建置者」（需要編譯器、Python、開發依賴）與「執行者」（僅需執行時期依賴）分開。

```dockerfile
# Stage 1: Builder
# Use explicit version SHA for immutability (optional but recommended)
FROM node:18-alpine AS builder

WORKDIR /app

# Optimization: Copy package files FIRST to leverage cache
# Only if package.json changes will 'npm ci' re-run
COPY package*.json ./

# 'npm ci' is faster and more reliable than 'npm install' for CI
RUN npm ci

# Copy source code AFTER installing dependencies
COPY . .

# Build the application (e.g., TypeScript to JS)
RUN npm run build

# Prune dev dependencies to prepare for the final stage
RUN npm prune --production

# Stage 2: Runner
# Use a smaller base image or Distroless
FROM gcr.io/distroless/nodejs18-debian11 AS runner

WORKDIR /app

# Copy only necessary files from the builder stage
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

# Distroless images don't have a shell, so we use vector form CMD
CMD ["dist/main.js"]
```

### Analysis of Phase 2
### 第二階段分析

1.  **Layer Caching:**
    *   `COPY package*.json ./` is separate. If you change your source code (`src/index.ts`) but not your dependencies, Docker reuses the cached `npm ci` layer. Build time drops from minutes to seconds.
2.  **Multi-stage:**
    *   The final image does not contain the TypeScript compiler, source code (if only `dist` is needed), or cache folders.
3.  **Distroless:**
    *   The final image has no shell (`/bin/sh`). Even if an attacker finds an RCE (Remote Code Execution) vulnerability, they cannot easily pop a shell to explore the system.

1.  **層快取：**
    *   `COPY package*.json ./` 被獨立出來。如果你修改了原始碼 (`src/index.ts`) 但沒改依賴，Docker 會重用 `npm ci` 的快取層。建置時間從數分鐘降至數秒。
2.  **多階段：**
    *   最終映像檔不包含 TypeScript 編譯器、原始碼（若只需要 `dist`）或快取資料夾。
3.  **Distroless：**
    *   最終映像檔沒有 Shell (`/bin/sh`)。即使攻擊者發現了 RCE（遠端程式碼執行）漏洞，他們也難以開啟 Shell 來探索系統。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 The "Chaining" Mistake
### 5.1 「指令串接」的錯誤

**Anti-pattern:**
```dockerfile
RUN apt-get update
RUN apt-get install -y vim
RUN rm -rf /var/lib/apt/lists/*
```

**Why it's bad:** Each `RUN` creates a layer. The files deleted in layer 3 are still present in layer 2. The image size is not reduced.

**為何不好：** 每個 `RUN` 都會建立一層。在第 3 層刪除的檔案仍然存在於第 2 層中。映像檔大小並未減少。

**Solution:** Chain commands in a single layer.
**解法：** 在單一層中串接指令。

```dockerfile
RUN apt-get update && \
    apt-get install -y vim && \
    rm -rf /var/lib/apt/lists/*
```

### 5.2 Leaking Secrets in Build Args
### 5.2 在 Build Args 中洩漏機密

**Anti-pattern:**
`ARG GITHUB_TOKEN`
`RUN git clone https://$GITHUB_TOKEN@github.com/org/repo.git`

**Why it's bad:** Build arguments and command history are persisted in the image metadata. Anyone with the image can see the token via `docker history`.

**為何不好：** 建置參數與指令歷史紀錄會被持久化在映像檔的中繼資料中。任何擁有該映像檔的人都可以透過 `docker history` 看到該 Token。

**Solution:** Use Docker BuildKit secrets (`--mount=type=secret`).
**解法：** 使用 Docker BuildKit secrets (`--mount=type=secret`)。

### 5.3 Ignoring `.dockerignore`
### 5.3 忽略 `.dockerignore`

**Anti-pattern:** Not having a `.dockerignore` file.

**Why it's bad:** Docker uploads the *entire* directory to the daemon context. If you have a 2GB `tmp/` folder or local `.git` history, the build takes forever to start ("Sending build context to Docker daemon...").

**為何不好：** Docker 會將 *整個* 目錄上傳至 Daemon 上下文。如果你有一個 2GB 的 `tmp/` 資料夾或本地 `.git` 歷史紀錄，建置啟動將會非常久（顯示 "Sending build context to Docker daemon..."）。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How would you optimize a CI pipeline where the Docker build step is the bottleneck?
### Q1: 如果 Docker 建置步驟是 CI Pipeline 的瓶頸，你會如何最佳化？

**Key Points for a Senior Answer:**
*   **Layer Caching:** Ensure `package.json` / `go.mod` is copied and installed *before* source code.
*   **Registry Caching:** Use `--cache-from` (or BuildKit's `type=registry`) to pull previous layers from the registry so the CI runner doesn't start from scratch every time.
*   **Context Optimization:** Check `.dockerignore` to ensure we aren't uploading unnecessary files.
*   **Base Image:** Switch to smaller base images (Alpine) to reduce network transfer time.

**資深回答要點：**
*   **層快取：** 確保 `package.json` / `go.mod` 在原始碼 *之前* 被複製並安裝。
*   **Registry 快取：** 使用 `--cache-from`（或 BuildKit 的 `type=registry`）從 Registry 拉取先前的層，避免 CI Runner 每次都從頭開始。
*   **上下文最佳化：** 檢查 `.dockerignore` 確保沒有上傳不必要的檔案。
*   **基底映像檔：** 切換至較小的基底映像檔（Alpine）以減少網路傳輸時間。

### Q2: Why might you choose `debian:slim` over `alpine` for a Python or Node.js application?
### Q2: 為什麼在 Python 或 Node.js 應用程式中，你可能會選擇 `debian:slim` 而非 `alpine`？

**Key Points:**
*   **Libc Compatibility:** Alpine uses `musl libc`, while most binaries are compiled for `glibc` (used by Debian/Ubuntu).
*   **Build Time:** Installing Python wheels (e.g., numpy, pandas) on Alpine often requires compiling from source because pre-compiled wheels aren't compatible with musl. This drastically increases build time and complexity.
*   **Debugging:** Sometimes the subtle differences in DNS resolution or threading between musl and glibc cause production bugs that are hard to reproduce.

**關鍵要點：**
*   **Libc 相容性：** Alpine 使用 `musl libc`，而大多數二進位檔是針對 `glibc`（Debian/Ubuntu 使用）編譯的。
*   **建置時間：** 在 Alpine 上安裝 Python wheels（如 numpy, pandas）通常需要從原始碼編譯，因為預編譯的 wheels 與 musl 不相容。這會大幅增加建置時間與複雜度。
*   **除錯：** 有時 musl 與 glibc 在 DNS 解析或執行緒處理上的細微差異，會導致難以重現的生產環境 Bug。

### Q3: Explain the security benefits of "Distroless" images.
### Q3: 解釋 "Distroless" 映像檔的安全性優勢。

**Key Points:**
*   **Minimal Attack Surface:** No shell, no package manager (apt/apk), no curl/wget.
*   **Exploit Mitigation:** Even if an attacker exploits an application vulnerability (like Log4Shell), they cannot easily download a payload or open a reverse shell because the tools simply aren't there.
*   **Compliance:** Fewer components mean fewer CVE scans to triage.

**關鍵要點：**
*   **最小攻擊面：** 沒有 Shell，沒有套件管理員（apt/apk），沒有 curl/wget。
*   **漏洞利用緩解：** 即使攻擊者利用應用程式漏洞（如 Log4Shell），他們也難以下載惡意負載或開啟反向 Shell，因為工具根本不存在。
*   **合規性：** 元件越少，意味著需要篩選的 CVE 掃描結果越少。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Summary
### 小結
1.  **Order Matters:** Always copy dependency definitions (`package.json`) and install them *before* copying source code to maximize **Layer Caching**.
    **順序很重要：** 務必先複製依賴定義檔（`package.json`）並安裝，*再* 複製原始碼，以最大化 **層快取**。
2.  **Multi-stage is Mandatory:** Separate build tools from runtime artifacts. Never ship compilers to production.
    **多階段是必須的：** 將建置工具與執行產物分開。絕不要將編譯器發布到生產環境。
3.  **One Layer for Cleanup:** If you install and remove files, do it in the same `RUN` instruction (chained with `&&`).
    **單層清理：** 如果你安裝並移除檔案，請在同一個 `RUN` 指令中完成（用 `&&` 串接）。
4.  **Distroless for Security:** Use Distroless images to remove the OS shell, reducing the blast radius of security breaches.
    **Distroless 提升安全：** 使用 Distroless 映像檔移除 OS Shell，降低安全漏洞的爆炸半徑。
5.  **Context Hygiene:** Use `.dockerignore` to keep the build context small and fast.
    **上下文衛生：** 使用 `.dockerignore` 保持建置上下文輕量且快速。

### Next Steps
### 後續延伸
*   **Container Orchestration:** Now that you have optimized images, how do you manage them at scale? (Next Chapter: Kubernetes Basics).
    **容器編排：** 既然有了最佳化的映像檔，如何大規模管理它們？（下一章：Kubernetes 基礎）。
*   **Image Signing:** Explore **Docker Content Trust** or **Cosign** to ensure only signed, verified images run in your cluster.
    **映像檔簽章：** 探索 **Docker Content Trust** 或 **Cosign**，確保叢集中只執行經過簽章驗證的映像檔。