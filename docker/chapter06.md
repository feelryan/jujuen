# Chapter 06: Resource Limits and Performance Tuning
# 第六章：資源限制與效能調校

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

For Senior Engineers, running a container is easy; ensuring it runs reliably under load without starving other processes is the real challenge. In production environments, especially within orchestration platforms like Kubernetes, improper resource configuration is the root cause of the "Noisy Neighbor" problem and unexpected OOM (Out of Memory) kills. This chapter focuses on the Linux Cgroups mechanism underlying Docker and how to tune the kernel for high-concurrency scenarios.

對於資深工程師而言，執行一個容器很容易；但要確保它在高負載下可靠運行，且不會耗盡資源導致其他程序飢餓，才是真正的挑戰。在生產環境中，特別是在 Kubernetes 這類編排平台內，不當的資源配置是導致「吵雜鄰居（Noisy Neighbor）」問題與意外 OOM（Out of Memory）崩潰的主因。本章將深入探討 Docker 底層的 Linux Cgroups 機制，以及如何針對高併發場景進行 Kernel 調校。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Master CPU & Memory Constraints**: Differentiate between soft limits (shares) and hard limits (quotas), and know when to use CPU pinning (`cpuset`).
    **掌握 CPU 與記憶體限制**：區分軟限制（shares）與硬限制（quotas）的差異，並知道何時使用 CPU 綁核（`cpuset`）。
2.  **Diagnose OOM Kills**: Understand the Linux OOM Killer's behavior, interpret Exit Code 137, and configure applications (like JVM) to respect container limits.
    **診斷 OOM Kills**：理解 Linux OOM Killer 的行為，解讀 Exit Code 137，並配置應用程式（如 JVM）以遵循容器限制。
3.  **Tune Kernel Parameters**: Use `--sysctl` and `ulimit` to optimize network stack performance (e.g., `somaxconn`) for high-throughput services.
    **調校 Kernel 參數**：使用 `--sysctl` 與 `ulimit` 來優化高吞吐量服務的網路堆疊效能（例如 `somaxconn`）。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 Cgroups: The Resource Police
### 2.1 Cgroups：資源警察

The mental model for Docker resource limits is **Linux Control Groups (cgroups)**. While Namespaces provide isolation (what you can *see*), Cgroups provide accounting and limiting (what you can *use*).
Docker 資源限制的心智模型建立在 **Linux Control Groups (cgroups)** 之上。Namespaces 提供了隔離（你能*看見*什麼），而 Cgroups 則提供了計量與限制（你能*使用*什麼）。

*   **CPU Shares (Soft Limit)**: Think of this as "stock shares" in a company. It only matters when there is contention. If the CPU is idle, a container with low shares can use 100%. If busy, time is distributed proportionally.
    **CPU Shares（軟限制）**：將其想像為公司的「股權」。這只有在資源競爭時才重要。如果 CPU 閒置，低權重的容器也可以使用 100% 資源；如果忙碌，時間則按比例分配。
*   **CPU Quota (Hard Limit)**: Think of this as a speed governor. Even if the host is idle, the container cannot exceed this limit. It creates "throttling."
    **CPU Quota（硬限制）**：將其想像為限速器。即使主機閒置，容器也無法超過此限制。這會造成「節流（throttling）」。
*   **Memory Limit**: A hard wall. If you hit it, the kernel invokes the OOM Killer. Unlike CPU throttling (which just slows you down), memory exhaustion kills the process.
    **記憶體限制**：這是一堵硬牆。如果你撞上它，Kernel 就會召喚 OOM Killer。與 CPU 節流（只是讓你變慢）不同，記憶體耗盡會直接殺死程序。

### 2.2 The OOM Killer Mechanism
### 2.2 OOM Killer 機制

When a container exceeds its `--memory` limit, the Linux Kernel must reclaim memory. It scores processes based on usage and kills the one with the highest score (usually the main application in the container).
當容器超過其 `--memory` 限制時，Linux Kernel 必須回收記憶體。它會根據使用量對程序進行評分，並殺死分數最高的程序（通常是容器內的主應用程式）。

> **Key Insight**: Docker does not kill your process; the Linux Kernel does. Docker merely reports the aftermath (Exit Code 137 = 128 + 9 SIGKILL).
> **關鍵洞察**：並不是 Docker 殺死了你的程序，而是 Linux Kernel。Docker 只是回報了結果（Exit Code 137 = 128 + 9 SIGKILL）。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### 3.1 Quality of Service (QoS) in Orchestration
### 3.1 編排系統中的服務品質 (QoS)

In System Design, we classify services by criticality. Docker resource limits are the building blocks for Kubernetes QoS classes:
在系統設計中，我們根據關鍵性對服務進行分類。Docker 資源限制是 Kubernetes QoS 類別的基石：

*   **Guaranteed**: `limit` equals `request` (CPU & Memory). The container gets dedicated resources and is the last to be evicted.
    **Guaranteed**：`limit` 等於 `request`（CPU 與記憶體）。容器獲得專用資源，且是最後一個被驅逐的。
*   **Burstable**: `limit` > `request`. The container can burst into unused resources but risks throttling or eviction if the node is under pressure.
    **Burstable**：`limit` 大於 `request`。容器可以突發使用未被佔用的資源，但在節點壓力大時面臨被節流或驅逐的風險。
*   **BestEffort**: No limits set. These are the first to die when resources are scarce.
    **BestEffort**：未設定限制。當資源稀缺時，這些容器會最先被犧牲。

### 3.2 High Concurrency & Kernel Tuning
### 3.2 高併發與 Kernel 調校

For high-throughput systems (e.g., API Gateways, Push Notification Services), default Docker settings are insufficient.
對於高吞吐量系統（例如 API Gateway、推播服務），Docker 的預設設定是不夠的。

*   **File Descriptors**: Every TCP connection is a file. The default `ulimit -n` might be too low (often 1024).
    **檔案描述符**：每個 TCP 連線都是一個檔案。預設的 `ulimit -n` 可能太低（通常是 1024）。
*   **Network Stack**: Parameters like `net.core.somaxconn` (backlog size) determine how many pending connections can queue up. If the queue fills, new requests are dropped (Connection Refused) before your app even sees them.
    **網路堆疊**：諸如 `net.core.somaxconn`（backlog 大小）等參數決定了有多少等待中的連線可以排隊。如果佇列滿了，新的請求在你的應用程式看到之前就會被丟棄（Connection Refused）。

---

## 4. Walkthrough / Example
## 4. 逐步示例

### Scenario: Tuning a Java Microservice & Nginx Gateway
### 情境：調校 Java 微服務與 Nginx Gateway

We have a Java Spring Boot application (memory-intensive) behind an Nginx reverse proxy (high concurrency).
我們有一個 Java Spring Boot 應用程式（記憶體密集型），位於 Nginx 反向代理（高併發）之後。

#### Step 1: Memory Limits & Java Heap
#### 步驟 1：記憶體限制與 Java Heap

**Naive Approach**: Just set `--memory="512m"`.
**天真做法**：直接設定 `--memory="512m"`。
*Result*: The JVM might try to allocate a heap larger than 512MB because it sees the *host's* total memory, leading to an immediate OOM kill on startup.
*結果*：JVM 可能會嘗試分配大於 512MB 的 Heap，因為它看到的是*主機*的總記憶體，導致啟動時立即發生 OOM 崩潰。

**Better Approach**:
**較佳做法**：

```bash
# Docker command
docker run -d \
  --name java-app \
  --memory="512m" \
  --memory-swap="512m" \  # Disable swap usage effectively (limit == swap limit)
  -e JAVA_OPTS="-XX:MaxRAMPercentage=75.0" \
  my-java-image
```

*   **Explanation**: We limit the container to 512MB. We use `-XX:MaxRAMPercentage` (available in modern JDKs) to tell the JVM to calculate heap size based on the *container limit*, not the host RAM.
    **解釋**：我們將容器限制在 512MB。我們使用 `-XX:MaxRAMPercentage`（現代 JDK 支援）告訴 JVM 根據*容器限制*而非主機 RAM 來計算 Heap 大小。

#### Step 2: CPU Pinning for Latency Sensitive Tasks
#### 步驟 2：針對延遲敏感任務的 CPU 綁核

**Problem**: The Java app experiences "Stop-the-World" GC pauses that vary wildly because the container keeps jumping between different CPU cores (context switching).
**問題**：Java 應用程式經歷了波動劇烈的「Stop-the-World」GC 暫停，因為容器不斷在不同的 CPU 核心之間跳轉（Context Switching）。

**Solution**: Use `cpuset` to pin the container to specific cores.
**解法**：使用 `cpuset` 將容器固定在特定核心上。

```bash
docker run -d \
  --name java-app-pinned \
  --cpuset-cpus="0-1" \  # Bind to Core 0 and Core 1 only
  --memory="512m" \
  my-java-image
```

*   **Trade-off**: This reduces context switching and improves cache locality (L1/L2 cache), but requires careful management of core allocation across the cluster to avoid fragmentation.
    **權衡**：這減少了 Context Switching 並改善了快取局部性（L1/L2 Cache），但需要仔細管理叢集中的核心分配以避免碎片化。

#### Step 3: Kernel Tuning for Nginx (High Concurrency)
#### 步驟 3：針對 Nginx 的 Kernel 調校（高併發）

**Problem**: Under load testing (10k req/sec), Nginx starts dropping connections, but CPU/Memory are fine.
**問題**：在負載測試下（10k req/sec），Nginx 開始丟棄連線，但 CPU/記憶體都很正常。

**Diagnosis**: The default `somaxconn` (socket listen backlog) is often 128.
**診斷**：預設的 `somaxconn`（Socket 監聽佇列）通常是 128。

**Solution**: Tune sysctl and ulimits.
**解法**：調校 sysctl 與 ulimits。

```bash
docker run -d \
  --name nginx-high-perf \
  --sysctl net.core.somaxconn=1024 \
  --ulimit nofile=65535:65535 \
  -p 80:80 \
  nginx
```

*   `--sysctl net.core.somaxconn=1024`: Increases the backlog queue.
    `--sysctl net.core.somaxconn=1024`：增加 backlog 佇列。
*   `--ulimit nofile=65535`: Allows Nginx to open more file descriptors (connections).
    `--ulimit nofile=65535`：允許 Nginx 開啟更多檔案描述符（連線）。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 Misunderstanding CPU Shares vs. Quotas
### 5.1 誤解 CPU Shares 與 Quotas

*   **Anti-pattern**: Relying solely on `--cpu-shares` (or `-c`) expecting a hard limit.
    **反模式**：僅依賴 `--cpu-shares`（或 `-c`）並期望它是一個硬限制。
*   **Why it's bad**: If the host is idle, your container can consume 100% CPU, potentially masking performance issues that will only appear when the node becomes busy.
    **為何不好**：如果主機閒置，你的容器可能會消耗 100% CPU，這可能會掩蓋效能問題，這些問題只有在節點變忙時才會顯現。
*   **Correction**: Use `--cpus` (which sets quotas) for predictable performance profiles, especially in multi-tenant environments.
    **修正**：使用 `--cpus`（設定 quotas）以獲得可預測的效能表現，特別是在多租戶環境中。

### 5.2 Unbounded Swap
### 5.2 無限制的 Swap

*   **Anti-pattern**: Setting memory limit but leaving swap unlimited (default behavior in some versions).
    **反模式**：設定了記憶體限制但未限制 Swap（某些版本的預設行為）。
*   **Why it's bad**: When the container hits the RAM limit, it starts swapping to disk. The application doesn't crash, but performance degrades drastically (latency spikes). This "zombie" state is often harder to debug than a crash.
    **為何不好**：當容器達到 RAM 限制時，它開始 Swap 到硬碟。應用程式不會崩潰，但效能會急劇下降（延遲飆升）。這種「殭屍」狀態通常比直接崩潰更難除錯。
*   **Correction**: Set `--memory-swap` equal to `--memory` to disable swap for that container.
    **修正**：將 `--memory-swap` 設定為等於 `--memory`，以停用該容器的 Swap。

### 5.3 Using Privileged Mode for Sysctl
### 5.3 為了 Sysctl 使用特權模式

*   **Anti-pattern**: Using `--privileged` just to change a network parameter.
    **反模式**：僅為了更改一個網路參數就使用 `--privileged`。
*   **Why it's bad**: It grants root capabilities to the container, breaking security isolation.
    **為何不好**：這賦予了容器 Root 能力，破壞了安全隔離。
*   **Correction**: Use `--sysctl` for namespaced parameters. For non-namespaced parameters, configure them on the host (carefully).
    **修正**：對於有命名空間隔離的參數，使用 `--sysctl`。對於非命名空間參數，請（小心地）在主機上配置。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How do you debug a container that randomly restarts with no logs?
### Q1: 你如何除錯一個隨機重啟且沒有 Log 的容器？

*   **Key Points**:
    *   Suspect OOM Killer immediately.
    *   Check `docker inspect <container_id>` for `State.ExitCode` (137) and `State.OOMKilled` (true).
    *   Check host kernel logs (`dmesg` or `/var/log/syslog`) for "Out of memory: Kill process".
    *   **Discussion**: Differentiate between application crash (stack trace in logs) vs. kernel kill (silence).
*   **關鍵要點**：
    *   立即懷疑 OOM Killer。
    *   檢查 `docker inspect <container_id>` 中的 `State.ExitCode` (137) 與 `State.OOMKilled` (true)。
    *   檢查主機 Kernel Log（`dmesg` 或 `/var/log/syslog`）是否有 "Out of memory: Kill process"。
    *   **討論**：區分應用程式崩潰（Log 中有 Stack Trace）與 Kernel 殺死程序（靜默）的差異。

### Q2: Explain the difference between `--cpus=0.5` and `--cpu-shares=512`. Which one would you use for a background batch job vs. a user-facing API?
### Q2: 解釋 `--cpus=0.5` 與 `--cpu-shares=512` 的差異。對於背景批次任務與使用者面向的 API，你會分別使用哪一個？

*   **Key Points**:
    *   `--cpus=0.5` is a hard limit (Quota). The container gets 50% of a core every period (usually 100ms). Good for **predictability** and capacity planning.
    *   `--cpu-shares=512` is a soft weight. If CPU is free, it can use 100%. Good for **utilization**.
    *   **Strategy**: Use Quotas (limits) for the API to ensure consistent latency (avoid noisy neighbors). Use Shares for the batch job to scavenge unused cycles without blocking critical work.
*   **關鍵要點**：
    *   `--cpus=0.5` 是硬限制（Quota）。容器在每個週期（通常 100ms）獲得 50% 的核心時間。適合**可預測性**與容量規劃。
    *   `--cpu-shares=512` 是軟權重。如果 CPU 空閒，它可以使用 100%。適合**利用率**。
    *   **策略**：對 API 使用 Quotas（限制）以確保一致的延遲（避免吵雜鄰居）。對批次任務使用 Shares 以在不阻礙關鍵工作的情況下利用剩餘運算週期。

### Q3: Why does setting `ulimit` inside a Dockerfile often fail, and how do you handle it in production?
### Q3: 為什麼在 Dockerfile 中設定 `ulimit` 經常失敗，你在生產環境中如何處理？

*   **Key Points**:
    *   `ulimit` is a runtime configuration, not a build-time artifact. Docker builds inherit limits from the Docker daemon default.
    *   Using `RUN ulimit -n 65535` in Dockerfile only affects that specific layer/shell, not the final container runtime.
    *   **Solution**: Must be set at runtime via `--ulimit` flag, `docker-compose.yml`, or Container Runtime Interface (CRI) settings in Kubernetes.
*   **關鍵要點**：
    *   `ulimit` 是執行時配置，而非建置時產物。Docker 建置過程繼承 Docker daemon 的預設限制。
    *   在 Dockerfile 中使用 `RUN ulimit -n 65535` 只會影響該特定層/Shell，不會影響最終容器執行時。
    *   **解法**：必須在執行時透過 `--ulimit` 旗標、`docker-compose.yml` 或 Kubernetes 中的 CRI 設定來配置。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Recap (記憶錨點)
### 重點回顧

1.  **Cgroups** are the mechanism for resource limiting; **Namespaces** are for isolation.
    **Cgroups** 是資源限制的機制；**Namespaces** 是隔離的機制。
2.  **Exit Code 137** almost always means OOM Killed (`kill -9`). Check `dmesg`.
    **Exit Code 137** 幾乎總是代表 OOM Killed (`kill -9`)。請檢查 `dmesg`。
3.  **CPU Shares** are relative weights (opportunistic); **CPU Quotas** (`--cpus`) are absolute limits (throttling).
    **CPU Shares** 是相對權重（機會主義）；**CPU Quotas** (`--cpus`) 是絕對限制（節流）。
4.  **Swap** can hide memory pressure and cause latency spikes. Disable it (`--memory-swap == --memory`) for predictable performance.
    **Swap** 會隱藏記憶體壓力並導致延遲飆升。為了可預測的效能，請停用它（`--memory-swap == --memory`）。
5.  **Kernel Tuning** (`sysctl`, `ulimit`) is essential for high-concurrency apps to avoid connection drops.
    **Kernel 調校**（`sysctl`, `ulimit`）對於避免高併發應用程式的連線丟棄至關重要。

### Next Steps
### 後續延伸

*   **Deep Dive**: Learn how to visualize these metrics using **Prometheus + cAdvisor**.
    **深入研究**：學習如何使用 **Prometheus + cAdvisor** 視覺化這些指標。
*   **Next Chapter**: Proceed to **Container Security & Capabilities** (Chapter 07), where we will discuss how to run containers without `root` and manage Linux Capabilities (e.g., `NET_ADMIN`) securely.
    **下一章**：進入 **容器安全與權限（Container Security & Capabilities）**（第七章），我們將討論如何在非 `root` 情況下執行容器，並安全地管理 Linux Capabilities（如 `NET_ADMIN`）。