# 1. 前言與學習目標 (Introduction and Learning Objectives)

對於資深工程師而言，Docker 的儲存層不僅僅是關於「如何掛載目錄」，更關乎於理解檔案系統如何在核心層級運作，以及這些機制如何影響 I/O 密集型應用（如資料庫）的效能。本章將深入探討 Docker 的儲存驅動（Storage Drivers）與資料持久化策略。

For senior engineers, the Docker storage layer is not just about "how to mount a directory," but understanding how the file system operates at the kernel level and how these mechanisms impact the performance of I/O-intensive applications (such as databases). This chapter delves into Docker's Storage Drivers and data persistence strategies.

完成本章後，你將能夠：
1.  **剖析 Storage Drivers**：清楚解釋 Overlay2 的運作原理，包含 `lowerdir`、`upperdir`、`merged` 的結構，以及其對磁碟空間的影響。
2.  **掌握 Copy-on-Write (CoW)**：理解 CoW 機制在寫入時的效能損耗，並知道何時該避開它。
3.  **精準選擇持久化策略**：在 System Design 面試或架構設計中，能夠根據場景（開發便利性 vs. 生產環境效能 vs. 安全性）準確選擇 Volumes、Bind Mounts 或 tmpfs。
4.  **優化 I/O 效能**：識別因錯誤使用容器寫入層（Container Writable Layer）而導致的效能瓶頸。

By the end of this chapter, you will be able to:
1.  **Dissect Storage Drivers**: Clearly explain the mechanics of Overlay2, including the structure of `lowerdir`, `upperdir`, and `merged`, and their impact on disk space.
2.  **Master Copy-on-Write (CoW)**: Understand the performance overhead of the CoW mechanism during writes and know when to bypass it.
3.  **Select Persistence Strategies Precisely**: Accurately choose between Volumes, Bind Mounts, or tmpfs based on the scenario (development convenience vs. production performance vs. security) in System Design interviews or architectural designs.
4.  **Optimize I/O Performance**: Identify performance bottlenecks caused by improper use of the Container Writable Layer.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 聯合檔案系統與 Overlay2 (Union File Systems & Overlay2)

**心智模型**：想像你有一疊透明投影片（Layers）。底層的投影片畫著基礎圖案（Image Layers），最上層有一張空白的透明片（Container Layer）。當你從上往下看時，你會看到一張完整的合成圖（Merged View）。如果你在最上層塗改，底層的圖案並不會被破壞，只是被遮擋或疊加了。這就是 Union File System 的基本概念。

**Mental Model**: Imagine you have a stack of transparent overhead slides (Layers). The bottom slides contain the base drawings (Image Layers), and there is a blank transparent sheet on top (Container Layer). When you look down from the top, you see a complete composite image (Merged View). If you draw on the top sheet, the underlying drawings are not destroyed; they are merely obscured or overlaid. This is the basic concept of a Union File System.

在 Linux 核心中，Docker 預設使用 **Overlay2** 驅動。它將檔案系統分為：
*   **LowerDir**:唯讀的映像檔層（Read-only image layers）。
*   **UpperDir**: 可讀寫的容器層（Read-write container layer）。
*   **Merged**: 容器掛載點，使用者看到的統一視圖。
*   **WorkDir**: Overlay2 內部用於準備檔案寫入的中介目錄。

In the Linux kernel, Docker defaults to the **Overlay2** driver. It divides the file system into:
*   **LowerDir**: Read-only image layers.
*   **UpperDir**: Read-write container layer.
*   **Merged**: The container mount point, the unified view seen by the user.
*   **WorkDir**: An internal intermediate directory used by Overlay2 to prepare file writes.

## 2.2 Copy-on-Write (CoW) 機制

**核心定義**：當容器需要修改一個位於 `LowerDir`（映像檔層）的檔案時，Docker 不會直接修改該檔案（因為它是唯讀的）。相反地，它會先將該檔案從 `LowerDir` 複製到 `UpperDir`，然後對副本進行修改。

**Core Definition**: When a container needs to modify a file located in the `LowerDir` (image layer), Docker does not modify that file directly (since it is read-only). Instead, it first copies the file from the `LowerDir` to the `UpperDir`, and then modifies the copy.

**效能影響 (Performance Impact)**：
*   **讀取 (Read)**：效能極高，接近原生速度。
*   **首次寫入 (First Write)**：會有延遲，因為必須先執行 `open()` -> `read()` (from lower) -> `write()` (to upper)。對於大檔案，這個複製過程可能導致顯著的 I/O 等待。
*   **後續寫入 (Subsequent Writes)**：發生在 `UpperDir` 的副本上，速度恢復正常。

**Performance Impact**:
*   **Read**: Extremely high performance, close to native speed.
*   **First Write**: Latency occurs because the system must execute `open()` -> `read()` (from lower) -> `write()` (to upper). For large files, this copy process can cause significant I/O wait.
*   **Subsequent Writes**: Occur on the copy in `UpperDir`, and speed returns to normal.

## 2.3 Volumes vs. Bind Mounts

這兩者都是用來繞過 CoW 機制，直接將資料寫入 Host 檔案系統，但在管理層面上有所不同。

Both are used to bypass the CoW mechanism and write data directly to the Host file system, but they differ in management.

| Feature | Volumes (推薦) | Bind Mounts |
| :--- | :--- | :--- |
| **Location** | Managed by Docker (`/var/lib/docker/volumes/`) | Anywhere on Host OS |
| **Portability** | High (Abstracted from OS paths) | Low (Dependent on Host paths) |
| **Management** | `docker volume` CLI API | Manual OS file management |
| **Performance** | Native (Bypasses Storage Driver) | Native (Bypasses Storage Driver) |
| **Use Case** | DB data, persistent app data | Config files, source code (dev), OS-specific tools |

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 資料庫效能優化 (Database Performance Optimization)

在設計高吞吐量的資料庫容器（如 PostgreSQL 或 MySQL）時，絕對**不能**將資料檔（Data Directory）放在容器的預設寫入層。

When designing high-throughput database containers (such as PostgreSQL or MySQL), you must **never** place the data directory in the container's default writable layer.

**原因 (Reason)**：
資料庫頻繁進行隨機寫入（Random Writes）。若依賴 CoW 機制，每次修改現有 Page 都可能觸發檔案複製，導致 I/O 放大（Write Amplification）與延遲。此外，容器刪除後資料即遺失。

**Reason**:
Databases perform frequent random writes. Relying on the CoW mechanism means every modification to an existing page could trigger a file copy, leading to Write Amplification and latency. Additionally, data is lost when the container is removed.

**最佳實踐 (Best Practice)**：
使用 **Named Volumes** 掛載至 `/var/lib/mysql`（或對應路徑）。這會繞過 Overlay2 驅動，直接使用 Host 的檔案系統效能，且由 Docker 統一管理權限。

**Best Practice**:
Use **Named Volumes** mounted to `/var/lib/mysql` (or the corresponding path). This bypasses the Overlay2 driver, utilizing the Host's native file system performance, with permissions managed uniformly by Docker.

## 3.2 CI/CD Pipeline 中的 Docker-in-Docker

在 Jenkins 或 GitLab CI Runner 中，我們常需要讓容器內的 Agent 能夠執行 Docker 指令。

In Jenkins or GitLab CI Runners, we often need the Agent inside the container to execute Docker commands.

**設計模式 (Design Pattern)**：
與其使用真正的 Docker-in-Docker (DinD) 模式（這需要特權模式且有儲存驅動嵌套問題），通常建議使用 **Bind Mount** 將 Host 的 Docker Socket (`/var/run/docker.sock`) 掛載進容器。

**Design Pattern**:
Instead of using true Docker-in-Docker (DinD) mode (which requires privileged mode and has storage driver nesting issues), it is usually recommended to use a **Bind Mount** to mount the Host's Docker Socket (`/var/run/docker.sock`) into the container.

```bash
docker run -v /var/run/docker.sock:/var/run/docker.sock ...
```

這讓容器內的 Client 直接與 Host 的 Daemon 溝通，避免了 OverlayFS on OverlayFS 的效能與相容性災難。

This allows the Client inside the container to communicate directly with the Daemon on the Host, avoiding the performance and compatibility disaster of OverlayFS on OverlayFS.

## 3.3 日誌管理與 I/O 隔離 (Log Management & I/O Isolation)

**反模式 (Anti-pattern)**：應用程式將大量日誌寫入容器內的檔案（如 `/app/logs/server.log`）。這會導致容器層無限膨脹，並消耗 CoW 資源。

**Anti-pattern**: The application writes massive logs to a file inside the container (e.g., `/app/logs/server.log`). This causes the container layer to grow indefinitely and consumes CoW resources.

**系統設計視角 (System Design View)**：
遵循 **12-Factor App** 原則，將日誌輸出到 `stdout`/`stderr`。Docker Daemon 會捕捉這些串流並透過 Log Driver（如 `json-file`, `awslogs`, `splunk`）處理。這將 I/O 負載從容器儲存層轉移到了 Host 的 Logging 子系統，更易於管理與輪替（Log Rotation）。

**System Design View**:
Follow the **12-Factor App** principles and output logs to `stdout`/`stderr`. The Docker Daemon captures these streams and handles them via a Log Driver (e.g., `json-file`, `awslogs`, `splunk`). This shifts the I/O load from the container storage layer to the Host's logging subsystem, making it easier to manage and rotate.

---

# 4. 逐步示例：深入 Overlay2 與 CoW (Walkthrough: Deep Dive into Overlay2 & CoW)

讓我們透過實際操作來觀察 Overlay2 的結構與 CoW 的行為。

Let's observe the structure of Overlay2 and the behavior of CoW through a practical walkthrough.

### 步驟 1: 啟動容器並尋找儲存路徑 (Step 1: Start Container & Locate Storage)

首先，啟動一個 Ubuntu 容器。

First, start an Ubuntu container.

```bash
docker run -d --name storage-test ubuntu:latest sleep 3600
```

使用 `docker inspect` 查找其在 Host 上的 Overlay2 路徑。

Use `docker inspect` to find its Overlay2 path on the Host.

```bash
docker inspect storage-test | grep GraphDriver -A 7
```

**輸出範例 (Output Example)**:
```json
"GraphDriver": {
    "Data": {
        "LowerDir": "/var/lib/docker/overlay2/l/...",
        "MergedDir": "/var/lib/docker/overlay2/<ID>/merged",
        "UpperDir": "/var/lib/docker/overlay2/<ID>/diff",
        "WorkDir": "/var/lib/docker/overlay2/<ID>/work"
    },
    "Name": "overlay2"
}
```

### 步驟 2: 驗證 CoW 行為 (Step 2: Verify CoW Behavior)

進入 `UpperDir`（即容器的可寫層），目前應該是空的（或僅有少量系統檔）。

Check the `UpperDir` (the container's writable layer); it should be empty (or contain only a few system files) at this moment.

```bash
# 需使用 root 權限查看 /var/lib/docker
sudo ls -F /var/lib/docker/overlay2/<ID>/diff/
```

現在，在容器內修改一個屬於 Image 層的檔案，例如 `/etc/apt/sources.list`。

Now, modify a file inside the container that belongs to the Image layer, such as `/etc/apt/sources.list`.

```bash
docker exec storage-test sh -c "echo '# test' >> /etc/apt/sources.list"
```

再次查看 Host 上的 `UpperDir`。你會發現 `etc/apt/sources.list` 出現了。

Check the `UpperDir` on the Host again. You will see that `etc/apt/sources.list` has appeared.

### 步驟 3: 分析結果 (Analysis)

1.  **Before Write**: `/etc/apt/sources.list` 僅存在於 `LowerDir` (Read-only)。
2.  **On Write**: Docker 核心觸發 CoW，將該檔案從 `LowerDir` 複製到 `UpperDir`。
3.  **After Write**: 容器應用程式讀取該檔案時，OverlayFS 會優先提供 `UpperDir` 中的版本（遮蔽了 `LowerDir` 的版本）。

1.  **Before Write**: `/etc/apt/sources.list` exists only in `LowerDir` (Read-only).
2.  **On Write**: The Docker kernel triggers CoW, copying the file from `LowerDir` to `UpperDir`.
3.  **After Write**: When the container application reads the file, OverlayFS serves the version in `UpperDir` (masking the version in `LowerDir`).

這證明了：如果你在容器內修改了一個 1GB 的檔案，即使只改了 1 byte，這 1GB 的檔案也會被複製到 `UpperDir`，佔用額外的 1GB 空間並產生複製延遲。

This proves: If you modify a 1GB file inside a container, even if you only change 1 byte, the entire 1GB file is copied to `UpperDir`, consuming an additional 1GB of space and incurring copy latency.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 權限地獄：Bind Mounts 與 UID/GID (Permission Hell: Bind Mounts & UID/GID)

**錯誤案例 (Pitfall)**：開發者在 Linux 上使用 Bind Mount 將專案目錄掛載到容器內，結果容器內的應用程式（以 `root` 執行）產生的檔案，在 Host 上變成了 `root` 權限，導致開發者無法編輯或刪除。反之，容器若以非 root (`USER 1000`) 執行，可能無法寫入 Host 的掛載目錄。

**Pitfall**: A developer uses Bind Mount on Linux to mount a project directory into a container. The application inside (running as `root`) creates files that become owned by `root` on the Host, making them uneditable or undeletable by the developer. Conversely, if the container runs as non-root (`USER 1000`), it might fail to write to the mounted directory on the Host.

**解決方案 (Solution)**：
*   **開發環境**：在 `docker run` 時傳遞 `--user $(id -u):$(id -g)`，讓容器內程序以當前 Host 用戶身份執行。
*   **生產環境**：優先使用 Named Volumes，Docker 會自動處理大部分權限問題；或在 Dockerfile 中明確建立用戶並 `chown` 資料夾。

**Solution**:
*   **Dev**: Pass `--user $(id -u):$(id -g)` during `docker run` to execute the container process as the current Host user.
*   **Prod**: Prefer Named Volumes, as Docker handles most permission issues automatically; or explicitly create a user and `chown` directories in the Dockerfile.

## 5.2 忽略容器大小增長 (Ignoring Container Size Growth)

**錯誤案例 (Pitfall)**：監控系統顯示磁碟空間不足，排查發現 `/var/lib/docker/overlay2` 佔用巨大。原因是應用程式在容器內執行 `apt-get update` 或下載臨時大檔卻未清理，這些變更都留在了可寫層。

**Pitfall**: Monitoring shows disk space running low. Investigation reveals `/var/lib/docker/overlay2` is consuming massive space. The cause is applications running `apt-get update` or downloading large temporary files inside the container without cleaning up, leaving these changes in the writable layer.

**解決方案 (Solution)**：
*   使用 `docker system df -v` 定期檢查容器大小。
*   確保 Dockerfile 中的安裝指令與清理指令在**同一個 RUN** 中執行（例如 `apt-get install -y pkg && rm -rf /var/lib/apt/lists/*`），避免檔案被提交到 Image Layer。
*   臨時檔案應寫入 `tmpfs` 掛載點（`--tmpfs /tmp`），而非容器層。

**Solution**:
*   Use `docker system df -v` to regularly check container sizes.
*   Ensure installation and cleanup commands in the Dockerfile run in the **same RUN instruction** (e.g., `apt-get install -y pkg && rm -rf /var/lib/apt/lists/*`) to prevent files from being committed to an Image Layer.
*   Temporary files should be written to a `tmpfs` mount (`--tmpfs /tmp`) instead of the container layer.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 解釋為什麼在 Docker 中運行資料庫，不建議直接使用容器內部儲存？
**Explain why it is not recommended to use container internal storage directly when running a database in Docker.**

*   **高分回答要點 (Key Points)**：
    1.  **CoW Overhead**：資料庫涉及大量隨機寫入，若修改映像檔層的既有檔案，會觸發 CoW 導致 I/O 延遲。
    2.  **Persistence**：容器生命週期短暫，刪除容器等於刪除資料（Ephemeral）。
    3.  **Throughput**：Storage Drivers (如 Overlay2) 相比直接存取 Host FS (Volumes) 有額外的檔案系統開銷。
    4.  **Solution**：應使用 Docker Volumes 或 Bind Mounts 來繞過 Storage Driver。

*   **Key Points**:
    1.  **CoW Overhead**: Databases involve heavy random writes. Modifying existing files in image layers triggers CoW, causing I/O latency.
    2.  **Persistence**: Containers are ephemeral; removing a container deletes its data.
    3.  **Throughput**: Storage Drivers (like Overlay2) introduce additional file system overhead compared to direct Host FS access (Volumes).
    4.  **Solution**: Should use Docker Volumes or Bind Mounts to bypass the Storage Driver.

## Q2: Volumes 和 Bind Mounts 在底層實作上有何不同？你會如何選擇？
**What is the difference between Volumes and Bind Mounts in underlying implementation? How do you choose between them?**

*   **高分回答要點 (Key Points)**：
    1.  **實作 (Implementation)**：兩者本質都是 Linux 的 `mount --bind`，將 Host 目錄掛載到 Container namespace。
    2.  **管理 (Management)**：Volumes 由 Docker 在特定路徑（`/var/lib/docker/volumes`）管理，與 Host OS 結構解耦；Bind Mounts 依賴 Host 絕對路徑。
    3.  **選擇 (Selection)**：
        *   **Volumes**: 用於資料庫、跨容器共享資料、生產環境（更好的移植性與備份機制）。
        *   **Bind Mounts**: 用於開發環境（掛載 source code 實現 hot reload）、掛載 Host 系統檔（如 `/etc/localtime` 或 `docker.sock`）。

*   **Key Points**:
    1.  **Implementation**: Both are essentially Linux `mount --bind`, mapping a Host directory into the Container namespace.
    2.  **Management**: Volumes are managed by Docker in a specific path (`/var/lib/docker/volumes`), decoupled from the Host OS structure; Bind Mounts rely on absolute Host paths.
    3.  **Selection**:
        *   **Volumes**: For databases, sharing data between containers, production environments (better portability and backup mechanisms).
        *   **Bind Mounts**: For development (mounting source code for hot reload), mounting Host system files (like `/etc/localtime` or `docker.sock`).

## Q3: 什麼是 OverlayFS 的 inode exhaustion 問題？
**What is the inode exhaustion problem in OverlayFS?**

*   **高分回答要點 (Key Points)**：
    1.  Docker 映像檔與容器層包含大量小檔案時，可能會耗盡 Host 檔案系統的 inode，即使磁碟空間（Block）仍有剩餘。
    2.  每個容器有自己的 `UpperDir`，若大量容器同時運行且各自產生大量小檔案，inode 消耗速度極快。
    3.  解決方案：定期 `docker system prune`，或為 `/var/lib/docker` 配置獨立的分割區並格式化為支援高 inode 數量的設定（如 `mkfs.ext4 -i`）。

*   **Key Points**:
    1.  When Docker images and container layers contain massive amounts of small files, they can exhaust the Host file system's inodes, even if disk space (Blocks) remains.
    2.  Each container has its own `UpperDir`. If many containers run simultaneously and generate many small files, inodes are consumed rapidly.
    3.  Solution: Regularly run `docker system prune`, or configure a separate partition for `/var/lib/docker` formatted with high inode count settings (e.g., `mkfs.ext4 -i`).

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)
1.  **Storage Drivers (Overlay2)**：透過 `LowerDir` (RO) 與 `UpperDir` (RW) 的堆疊來呈現統一視圖。
2.  **Copy-on-Write (CoW)**：修改映像檔層檔案時，必須先複製到容器層。這會導致首次寫入延遲與空間消耗。
3.  **Data Persistence**：生產環境資料庫務必使用 **Volumes**，避開 CoW 並確保資料持久性。
4.  **Bind Mounts**：適合開發環境（程式碼同步）或特殊系統需求（Docker Socket），但需注意權限問題。
5.  **Tmpfs**：適合存儲敏感資訊（Secrets）或高頻讀寫的臨時資料，完全不寫入磁碟。

1.  **Storage Drivers (Overlay2)**: Present a unified view by stacking `LowerDir` (RO) and `UpperDir` (RW).
2.  **Copy-on-Write (CoW)**: Modifying a file in the image layer requires copying it to the container layer first. This causes first-write latency and space consumption.
3.  **Data Persistence**: Production databases must use **Volumes** to bypass CoW and ensure data persistence.
4.  **Bind Mounts**: Suitable for development (code sync) or specific system needs (Docker Socket), but beware of permission issues.
5.  **Tmpfs**: Ideal for storing sensitive info (Secrets) or high-frequency temporary data, never writing to disk.

## 後續延伸 (Next Steps)
*   **下一章 (Chapter 05)**：**Docker 網路模型 (Networking Model)**。既然資料已經落地，接下來我們將探討容器如何透過 Bridge、Host、Overlay 網路進行通訊，以及 Service Discovery 的基礎。
*   **延伸閱讀**：研究 Docker 的 `dm` (Device Mapper) 驅動與 `overlay2` 的歷史差異，以及在 Kubernetes 中 CSI (Container Storage Interface) 如何抽象化底層儲存。

*   **Next Chapter (Chapter 05)**: **Docker Networking Model**. Now that data is persisted, we will explore how containers communicate via Bridge, Host, and Overlay networks, and the basics of Service Discovery.
*   **Further Reading**: Research the historical differences between Docker's `dm` (Device Mapper) driver and `overlay2`, and how CSI (Container Storage Interface) in Kubernetes abstracts underlying storage.