# 1. 前言與學習目標 (Introduction and Learning Objectives)

對於資深工程師而言，Docker 不僅僅是 `docker build` 和 `docker run`。深入理解其底層機制，是解決複雜生產環境問題（如效能瓶頸、安全性漏洞、殭屍行程）的關鍵。本章將揭開容器的「魔術」，還原其作為 Linux Process 的本質。

For senior engineers, Docker is much more than just `docker build` and `docker run`. A deep understanding of its underlying mechanisms is crucial for solving complex production issues (such as performance bottlenecks, security vulnerabilities, and zombie processes). This chapter will unveil the "magic" of containers, restoring them to their essence as Linux Processes.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **解構容器隔離機制**：清楚解釋 Namespaces 如何隔離視圖，Cgroups 如何限制資源，以及 UnionFS 如何優化儲存。
    **Deconstruct container isolation**: Clearly explain how Namespaces isolate views, how Cgroups limit resources, and how UnionFS optimizes storage.
2.  **剖析 Docker 架構演進**：描述 Docker Client、Daemon (dockerd)、containerd 與 runc 之間的呼叫鏈，並理解為何 Kubernetes 棄用 Docker shim。
    **Dissect Docker architecture evolution**: Describe the call chain between Docker Client, Daemon (dockerd), containerd, and runc, and understand why Kubernetes deprecated the Docker shim.
3.  **手動模擬容器**：不依賴 Docker，僅使用 Linux 原生指令（如 `unshare`, `nsenter`）建立一個簡易的隔離環境。
    **Manually simulate a container**: Create a simple isolated environment using only native Linux commands (like `unshare`, `nsenter`) without relying on Docker.
4.  **識別底層效能陷阱**：理解 Copy-on-Write (CoW) 機制對 I/O 密集型應用的影響，並知道如何規避。
    **Identify low-level performance pitfalls**: Understand the impact of the Copy-on-Write (CoW) mechanism on I/O-intensive applications and know how to avoid it.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 容器不存在於 Kernel 中 (Containers Do Not Exist in the Kernel)

在 Linux Kernel 中，並沒有一個名為「Container」的一級物件。容器其實是利用 Kernel 提供的三項技術組合而成的「受限行程」。
In the Linux Kernel, there is no first-class object named "Container." A container is actually a "restricted process" composed of three technologies provided by the Kernel.

*   **Namespaces (隔離視圖 / Isolation of View)**: 決定行程「看得到」什麼。例如 PID Namespace 讓容器以為自己是 PID 1；Network Namespace 讓容器有獨立的 IP。
    **Namespaces**: Determine what a process can "see." For example, the PID Namespace makes the container think it is PID 1; the Network Namespace gives the container an independent IP.
*   **Cgroups (資源限制 / Resource Limiting)**: 決定行程「能使用」多少資源。例如限制 CPU 使用率或記憶體上限。
    **Cgroups**: Determine how much resource a process can "use." For example, limiting CPU usage or memory caps.
*   **UnionFS / OverlayFS (檔案系統 / File System)**: 決定行程「如何存取」檔案。透過分層機制（Layering）與寫入時複製（Copy-on-Write），實現映像檔的高效共用。
    **UnionFS / OverlayFS**: Determine how a process "accesses" files. Through layering and Copy-on-Write (CoW), it achieves efficient sharing of images.

### 2.2 Docker Engine 架構 (Docker Engine Architecture)

現代 Docker 的架構是高度模組化的，這對於理解 Kubernetes 的運作至關重要。
Modern Docker architecture is highly modular, which is essential for understanding how Kubernetes works.

1.  **Docker Daemon (`dockerd`)**: 面向使用者的 API Server，負責處理來自 CLI 的請求，管理 Image、Network 等高階物件。
    **Docker Daemon (`dockerd`)**: The user-facing API Server, responsible for handling requests from the CLI and managing high-level objects like Images and Networks.
2.  **containerd**: 行業標準的容器運行時管理器（Container Runtime Manager）。它負責管理容器的生命週期（Start, Stop, Pause），但不直接建立容器行程。
    **containerd**: The industry-standard Container Runtime Manager. It manages the container lifecycle (Start, Stop, Pause) but does not directly create container processes.
3.  **runc**: 輕量級的 CLI 工具，符合 OCI (Open Container Initiative) 標準。它負責真正地呼叫 Kernel API (Namespaces/Cgroups) 來生成容器。
    **runc**: A lightweight CLI tool compliant with the OCI (Open Container Initiative) standard. It is responsible for actually calling Kernel APIs (Namespaces/Cgroups) to spawn the container.

**心智模型類比 (Mental Model Analogy)**:
*   **VM** 像是獨棟別墅（擁有獨立的地基與結構，即獨立 Kernel）。
*   **Container** 像是共享辦公室中的隔間（Cubicle）。大家共用大樓的水電與結構（Host Kernel），但透過隔板（Namespaces）讓你看不到隔壁的人，並透過管理員（Cgroups）限制你只能用一張桌子。
*   **VM** is like a detached house (with its own foundation and structure, i.e., independent Kernel).
*   **Container** is like a cubicle in a shared office space. Everyone shares the building's utilities and structure (Host Kernel), but partitions (Namespaces) prevent you from seeing your neighbors, and the manager (Cgroups) limits you to using only one desk.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

### 3.1 安全性設計：特權模式的風險 (Security Design: The Risk of Privileged Mode)

在系統設計中，我們常需決定容器的權限。
In system design, we often need to determine container permissions.

*   **場景**: CI/CD Agent 需要在容器內執行 Docker build (Docker-in-Docker)。
*   **Scenario**: A CI/CD Agent needs to execute Docker build inside a container (Docker-in-Docker).
*   **風險**: 開啟 `--privileged` 標誌實際上移除了大部分 Namespaces 與 Cgroups 的限制，並允許容器存取 Host 的所有裝置。這打破了隔離模型。
*   **Risk**: Enabling the `--privileged` flag effectively removes most Namespaces and Cgroups restrictions and allows the container to access all Host devices. This breaks the isolation model.
*   **最佳實踐**: 盡量避免 DIND (Docker-in-Docker)，改用 DOOD (Docker-outside-of-Docker，掛載 `/var/run/docker.sock`)，或使用 rootless 容器技術（如 Kaniko）。
*   **Best Practice**: Avoid DIND (Docker-in-Docker) whenever possible. Instead, use DOOD (Docker-outside-of-Docker, mounting `/var/run/docker.sock`) or use rootless container technologies (like Kaniko).

### 3.2 效能設計：OverlayFS 的 I/O 成本 (Performance Design: I/O Cost of OverlayFS)

*   **場景**: 資料庫（如 PostgreSQL）或高頻寫入的 Log 收集器運行在容器中。
*   **Scenario**: A database (like PostgreSQL) or a high-frequency log collector running in a container.
*   **原理**: 當容器修改一個位於唯讀層（Image Layer）的檔案時，OverlayFS 必須先將該檔案從下層複製到上層（Container Layer），這就是 Copy-on-Write。對於大檔案或頻繁寫入，這會造成顯著的 I/O 延遲。
*   **Mechanism**: When a container modifies a file located in a read-only layer (Image Layer), OverlayFS must first copy that file from the lower layer to the upper layer (Container Layer). This is Copy-on-Write. For large files or frequent writes, this causes significant I/O latency.
*   **設計決策**: **永遠不要**將資料庫的資料檔（Data Directory）放在容器的 Root FS 上。必須使用 **Volumes**（繞過 OverlayFS，直接寫入 Host FS）或綁定掛載（Bind Mounts）。
*   **Design Decision**: **Never** place database data files (Data Directory) on the container's Root FS. You must use **Volumes** (bypassing OverlayFS to write directly to the Host FS) or Bind Mounts.

---

# 4. 逐步示例：不使用 Docker 建立容器 (Walkthrough: Creating a Container Without Docker)

為了證明容器只是 Linux 行程，我們將使用 `unshare` 指令手動建立一個隔離環境。這有助於理解 Docker 底層到底做了什麼。
To prove that a container is just a Linux process, we will use the `unshare` command to manually create an isolated environment. This helps in understanding what Docker actually does under the hood.

### 步驟 1: 準備 Root Filesystem (Step 1: Prepare Root Filesystem)

首先，我們需要一個迷你的檔案系統。我們可以從 Alpine Linux 匯出。
First, we need a mini filesystem. We can export one from Alpine Linux.

```bash
# 在一台安裝了 Docker 的機器上
# On a machine with Docker installed
mkdir rootfs
docker export $(docker create alpine) | tar -C rootfs -xvf -
```

### 步驟 2: 使用 unshare 建立 Namespaces (Step 2: Create Namespaces using unshare)

我們將建立一個新的 PID Namespace 和 Mount Namespace，並將 Shell 切換進去。
We will create a new PID Namespace and Mount Namespace, and switch the shell into it.

```bash
# --mount-proc: 自動掛載 /proc，這對於 ps 指令正常運作至關重要
# --fork: 建立子行程
# --pid: 建立 PID Namespace
# --mount: 建立 Mount Namespace
sudo unshare --mount-proc=rootfs/proc --fork --pid --mount --root=rootfs /bin/sh
```

### 步驟 3: 驗證隔離 (Step 3: Verify Isolation)

現在你在新的 Shell 中。試試看以下指令：
Now you are in the new shell. Try the following commands:

```bash
# 在容器內 / Inside the container
/ # ps aux
PID   USER     TIME  COMMAND
    1 root      0:00 /bin/sh
    2 root      0:00 ps aux
```

**觀察 (Observation)**:
你會發現 PID 1 是 `/bin/sh`。而在 Host 機器上，這個 Shell 的 PID 可能是 12345。這就是 **PID Namespace** 的魔力：行程在容器內看到自己是 Root，但在 Host 上它只是一個普通行程。
You will notice PID 1 is `/bin/sh`. On the Host machine, this shell's PID might be 12345. This is the magic of the **PID Namespace**: the process sees itself as Root inside the container, but on the Host, it is just a normal process.

### 步驟 4: 離開與清理 (Step 4: Exit and Cleanup)

```bash
/ # exit
```

這個簡單的實驗展示了 `runc` 的核心職責：設定 Namespaces 並切換 Root Filesystem (chroot/pivot_root)。
This simple experiment demonstrates the core responsibility of `runc`: setting up Namespaces and switching the Root Filesystem (chroot/pivot_root).

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 忽略 PID 1 的職責 (Ignoring the Responsibilities of PID 1)

*   **錯誤描述**: 在 Dockerfile 中使用 `CMD ["sh", "-c", "java -jar app.jar"]` 或是 Shell script 啟動應用程式，導致應用程式不是 PID 1。
*   **Error Description**: Using `CMD ["sh", "-c", "java -jar app.jar"]` or a shell script to start the application in the Dockerfile, causing the application not to be PID 1.
*   **為何不好**: Linux 中 PID 1 負責回收殭屍行程 (Zombie Reaping) 並處理信號 (Signal Handling, 如 SIGTERM)。如果 PID 1 是 shell，它通常不會轉發信號給子行程，導致 `docker stop` 等待 10 秒後強制殺死 (SIGKILL) 應用，可能造成資料損壞。
*   **Why it's bad**: In Linux, PID 1 is responsible for Zombie Reaping and Signal Handling (e.g., SIGTERM). If PID 1 is a shell, it usually doesn't forward signals to child processes, causing `docker stop` to wait 10 seconds before force-killing (SIGKILL) the app, potentially leading to data corruption.
*   **解決方案**: 使用 `exec` 模式：`CMD ["java", "-jar", "app.jar"]` 或在 Shell script 最後使用 `exec java ...`。或者使用 `tini` 作為 init process (`docker run --init`)。
*   **Solution**: Use `exec` form: `CMD ["java", "-jar", "app.jar"]` or use `exec java ...` at the end of the shell script. Alternatively, use `tini` as the init process (`docker run --init`).

### 5.2 映像檔層級過多與快取失效 (Excessive Image Layers and Cache Invalidation)

*   **錯誤描述**: 在 Dockerfile 中頻繁使用 `RUN` 指令，且將變動頻繁的檔案（如 source code）放在變動不頻繁的依賴安裝（如 `npm install`）之前。
*   **Error Description**: Frequently using `RUN` commands in the Dockerfile, and placing frequently changing files (like source code) before infrequently changing dependency installations (like `npm install`).
*   **為何不好**: 每一層 Layer 都會增加 OverlayFS 的開銷。順序錯誤會導致 Docker Cache 無法有效利用，大幅增加 Build 時間。
*   **Why it's bad**: Each layer adds overhead to OverlayFS. Incorrect ordering prevents effective use of Docker Cache, significantly increasing Build time.
*   **解決方案**: 合併 `RUN` 指令（使用 `&&`），並嚴格遵守「最少變動在前，最多變動在後」的原則。
*   **Solution**: Combine `RUN` commands (using `&&`) and strictly follow the principle of "least frequently changed first, most frequently changed last."

### 5.3 濫用 `:latest` 標籤 (Abusing the `:latest` Tag)

*   **錯誤描述**: 在生產環境部署 yaml 中使用 `image: myapp:latest`。
*   **Error Description**: Using `image: myapp:latest` in production deployment yaml.
*   **為何不好**: `:latest` 是可變的 (Mutable)。回滾 (Rollback) 變得不可能，因為你不知道上一個 `:latest` 到底指向哪個 SHA。此外，Kubernetes 的 ImagePullPolicy 預設行為可能會導致意外更新或不更新。
*   **Why it's bad**: `:latest` is mutable. Rollback becomes impossible because you don't know which SHA the previous `:latest` pointed to. Furthermore, Kubernetes' default ImagePullPolicy might lead to unexpected updates or no updates at all.
*   **解決方案**: 使用具體的版本號（Semantic Versioning）或 SHA hash (e.g., `myapp:v1.2.3` 或 `myapp@sha256:...`)。
*   **Solution**: Use specific semantic versioning or SHA hashes (e.g., `myapp:v1.2.3` or `myapp@sha256:...`).

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 請解釋 `docker run` 執行時，底層發生了什麼事？ (Explain what happens under the hood when `docker run` is executed.)

*   **高分回答要點**:
    *   **Client**: Docker CLI 將請求發送給 Docker Daemon (REST API)。
    *   **Daemon**: `dockerd` 解析請求，檢查 Image 是否存在（若無則 Pull）。
    *   **Runtime Manager**: `dockerd` 呼叫 `containerd`。
    *   **OCI Runtime**: `containerd` 啟動 `containerd-shim`，shim 呼叫 `runc`。
    *   **Kernel**: `runc` 與 Kernel 互動，建立 Namespaces、Cgroups，掛載 Rootfs。
    *   **Process**: 容器行程啟動後，`runc` 退出，由 `shim` 接管行程的 I/O 和生命週期（這讓 `dockerd` 重啟不影響運行中的容器）。
*   **Key Points for High Score**:
    *   **Client**: Docker CLI sends a request to the Docker Daemon (REST API).
    *   **Daemon**: `dockerd` parses the request, checks if the Image exists (Pulls if not).
    *   **Runtime Manager**: `dockerd` calls `containerd`.
    *   **OCI Runtime**: `containerd` starts `containerd-shim`, and the shim calls `runc`.
    *   **Kernel**: `runc` interacts with the Kernel to create Namespaces, Cgroups, and mount Rootfs.
    *   **Process**: After the container process starts, `runc` exits, and the `shim` takes over the process's I/O and lifecycle (this allows `dockerd` to restart without affecting running containers).

### Q2: 虛擬機 (VM) 與容器 (Container) 在隔離性上的根本差異為何？ (What is the fundamental difference in isolation between a VM and a Container?)

*   **高分回答要點**:
    *   **Kernel Sharing**: 容器共享 Host Kernel；VM 擁有獨立的 Guest Kernel。
    *   **Attack Surface**: 容器的攻擊面較大。如果 Kernel 有漏洞，容器可能逃逸 (Escape) 並影響 Host；VM 則有 Hypervisor 作為額外防護層。
    *   **Isolation Level**: VM 是硬體級虛擬化（強隔離）；容器是作業系統級虛擬化（軟隔離）。
*   **Key Points for High Score**:
    *   **Kernel Sharing**: Containers share the Host Kernel; VMs have an independent Guest Kernel.
    *   **Attack Surface**: Containers have a larger attack surface. If the Kernel has a vulnerability, a container might escape and affect the Host; VMs have a Hypervisor as an extra layer of protection.
    *   **Isolation Level**: VM is hardware-level virtualization (strong isolation); Container is OS-level virtualization (soft isolation).

### Q3: 如何除錯一個「啟動後立即退出」的容器？ (How do you debug a container that exits immediately after starting?)

*   **高分回答要點**:
    *   **Logs**: `docker logs <container_id>` 查看 stdout/stderr。
    *   **Inspect**: `docker inspect` 查看 ExitCode 和 State。
    *   **Override Entrypoint**: 使用 `docker run -it --entrypoint /bin/sh <image>` 覆蓋原本的啟動指令，手動進入容器環境嘗試執行 App，檢查環境變數或路徑問題。
    *   **Events**: `docker events` 查看是否有 OOM (Out of Memory) Kill 事件。
*   **Key Points for High Score**:
    *   **Logs**: `docker logs <container_id>` to check stdout/stderr.
    *   **Inspect**: `docker inspect` to check ExitCode and State.
    *   **Override Entrypoint**: Use `docker run -it --entrypoint /bin/sh <image>` to override the original startup command, manually enter the container environment to try running the App, and check for environment variable or path issues.
    *   **Events**: `docker events` to check for OOM (Out of Memory) Kill events.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)

1.  **容器是行程 (Process)**：容器只是被 Namespaces 限制視圖、被 Cgroups 限制資源的 Linux 行程。
    **Containers are Processes**: A container is just a Linux process with its view restricted by Namespaces and resources limited by Cgroups.
2.  **Namespaces = 隔離 (Isolation)**：PID, Network, Mount, User, IPC, UTS。
    **Namespaces = Isolation**: PID, Network, Mount, User, IPC, UTS.
3.  **Cgroups = 限制 (Limits)**：CPU, Memory, Disk I/O。
    **Cgroups = Limits**: CPU, Memory, Disk I/O.
4.  **UnionFS = 分層 (Layers)**：Copy-on-Write 機制優化了儲存，但要注意寫入效能。
    **UnionFS = Layers**: The Copy-on-Write mechanism optimizes storage but requires attention to write performance.
5.  **呼叫鏈 (Call Chain)**：Docker CLI -> dockerd -> containerd -> runc -> Kernel。
    **Call Chain**: Docker CLI -> dockerd -> containerd -> runc -> Kernel.
6.  **PID 1 至關重要**：確保正確處理信號與殭屍行程。
    **PID 1 is Crucial**: Ensure proper handling of signals and zombie processes.

### 後續延伸 (Next Steps)

*   **Networking**: 既然知道 Network Namespace 是隔離的，那麼容器如何與外界通訊？下一章將深入探討 Bridge, Overlay, 與 CNI (Container Network Interface)。
    **Networking**: Now that we know the Network Namespace is isolated, how do containers communicate with the outside world? The next chapter will dive into Bridge, Overlay, and CNI (Container Network Interface).
*   **Kubernetes Internals**: 研究 Kubelet 如何透過 CRI (Container Runtime Interface) 直接呼叫 containerd，繞過 dockerd。
    **Kubernetes Internals**: Study how Kubelet calls containerd directly via CRI (Container Runtime Interface), bypassing dockerd.