# 1. 前言與學習目標 (Introduction and Learning Goals)

對於資深工程師而言，容器化不再只是關於「如何打包應用程式」，而是關於「如何在多租戶或高風險環境中安全地運行程式碼」。Docker 預設的設定偏向開發便利性而非安全性，這在 Production 環境中是一個巨大的隱患。本章將帶領你從預設配置走向深度防禦（Defense in Depth）。

For senior engineers, containerization is no longer just about "how to package applications," but "how to run code securely in multi-tenant or high-risk environments." Docker's default settings prioritize development convenience over security, which poses a significant risk in production. This chapter guides you from default configurations to Defense in Depth.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **實作最小權限原則 (Implement Least Privilege):** 透過 Dropping Capabilities 與 User Namespaces，確保即使容器被攻破，攻擊者也無法獲得宿主機的 Root 權限。
    **Implement Least Privilege:** Ensure that even if a container is compromised, the attacker cannot gain Root access to the host by using Dropping Capabilities and User Namespaces.
2.  **配置核心級隔離 (Configure Kernel-Level Isolation):** 理解並應用 Seccomp 與 AppArmor/SELinux 設定檔來限制系統呼叫（System Calls）。
    **Configure Kernel-Level Isolation:** Understand and apply Seccomp and AppArmor/SELinux profiles to restrict System Calls.
3.  **建立安全的軟體供應鏈 (Establish a Secure Software Supply Chain):** 整合映像檔弱點掃描（Vulnerability Scanning）與簽章驗證機制至 CI/CD 流程中。
    **Establish a Secure Software Supply Chain:** Integrate image vulnerability scanning and signature verification mechanisms into the CI/CD pipeline.
4.  **區分 Rootless Docker 與 Rootless Containers:** 清楚解釋並實作無 Root 守護進程（Daemon）的運行模式。
    **Distinguish Rootless Docker from Rootless Containers:** Clearly explain and implement the mode of running without a Root daemon.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 容器不是虛擬機 (Containers are Not VMs)
最核心的心智模型差異在於：**VM 虛擬化硬體，容器虛擬化作業系統（核心）**。
The core mental model difference is: **VMs virtualize hardware, while containers virtualize the operating system (kernel).**

-   **VM:** 擁有獨立的 Kernel。攻擊者必須逃逸 Hypervisor 才能影響 Host。
    **VM:** Has an independent Kernel. An attacker must escape the Hypervisor to affect the Host.
-   **Container:** 與 Host 共享 Kernel。如果容器內的行程是 `root`，且沒有適當隔離，它在理論上擁有對 Kernel 的完全存取權。
    **Container:** Shares the Kernel with the Host. If a process inside the container is `root` and not properly isolated, it theoretically has full access to the Kernel.

### 2.2 Linux Capabilities：拆解 Root 的權力 (Breaking Down Root's Power)
在傳統 Linux 中，權限是二元的：或是神一般的 `root`，或是普通使用者。**Capabilities** 將 `root` 的權力拆解成細項（如 `CAP_NET_BIND_SERVICE` 綁定低位 port、`CAP_SYS_TIME` 修改系統時間）。
In traditional Linux, privileges are binary: either god-like `root` or a standard user. **Capabilities** break down `root`'s power into granular items (e.g., `CAP_NET_BIND_SERVICE` to bind low ports, `CAP_SYS_TIME` to modify system time).

**資深觀點：** Docker 預設已經拿掉了一些危險的 Capabilities，但對於高安全性應用，你應該採取「白名單策略」：先 `DROP ALL`，再逐一加回需要的權限。
**Senior Perspective:** Docker drops some dangerous Capabilities by default, but for high-security applications, you should adopt a "whitelist strategy": first `DROP ALL`, then add back only the necessary privileges one by one.

### 2.3 Seccomp & AppArmor：系統呼叫防火牆 (System Call Firewalls)
如果 Capabilities 是限制「你能做什麼（功能）」，Seccomp (Secure Computing Mode) 則是限制「你能怎麼請求核心（系統呼叫）」。
If Capabilities restrict "what you can do (features)," Seccomp (Secure Computing Mode) restricts "how you can ask the kernel (system calls)."

-   **Seccomp:** 定義允許或禁止的 syscalls 列表（例如禁止 `reboot` 或 `swapon`）。
    **Seccomp:** Defines a list of allowed or prohibited syscalls (e.g., blocking `reboot` or `swapon`).
-   **AppArmor/SELinux:** 基於檔案路徑或網路資源的強制存取控制（MAC）。
    **AppArmor/SELinux:** Mandatory Access Control (MAC) based on file paths or network resources.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型分散式系統設計中，容器安全直接影響**合規性 (Compliance)** 與 **多租戶隔離 (Multi-tenant Isolation)**。

In large-scale distributed system design, container security directly impacts **Compliance** and **Multi-tenant Isolation**.

### 3.1 供應鏈安全架構 (Supply Chain Security Architecture)
在 Production 環境，我們不允許開發者直接 `docker push` 到生產用的 Registry。標準流程如下：
In a Production environment, we do not allow developers to directly `docker push` to the production Registry. The standard process is as follows:

1.  **Build:** CI Server 建置映像檔。
    **Build:** CI Server builds the image.
2.  **Scan:** 使用工具（如 Trivy, Clair, Snyk）掃描 OS 套件與應用程式依賴的 CVE。
    **Scan:** Use tools (like Trivy, Clair, Snyk) to scan OS packages and application dependencies for CVEs.
3.  **Sign:** 若掃描通過，使用私鑰對映像檔簽章（Docker Content Trust / Cosign）。
    **Sign:** If the scan passes, sign the image using a private key (Docker Content Trust / Cosign).
4.  **Admit:** Kubernetes Admission Controller 或 Docker Runtime 僅允許拉取「已簽章且來自受信任 Registry」的映像檔。
    **Admit:** Kubernetes Admission Controller or Docker Runtime only allows pulling images that are "signed and from a trusted Registry."

### 3.2 縱深防禦策略 (Defense in Depth Strategy)
這是一個分層的防護網，任一層失效都不應導致全面崩潰：
This is a layered defense network; failure in any single layer should not lead to total collapse:

*   **Layer 1 (Image):** Distroless 或 Minimal Base Image（減少攻擊面）。
    **Layer 1 (Image):** Distroless or Minimal Base Image (reduce attack surface).
*   **Layer 2 (Runtime):** Non-root user, Read-only filesystem。
    **Layer 2 (Runtime):** Non-root user, Read-only filesystem.
*   **Layer 3 (Kernel):** Dropped Capabilities, Seccomp profiles。
    **Layer 3 (Kernel):** Dropped Capabilities, Seccomp profiles.
*   **Layer 4 (Host):** User Namespaces (userns-remap)。
    **Layer 4 (Host):** User Namespaces (userns-remap).

---

# 4. 逐步示例 (Walkthrough / Example)

### 情境：強化一個 Node.js Web 應用 (Scenario: Hardening a Node.js Web Application)
我們將從一個普通的 Dockerfile 進化到一個高安全性的版本。
We will evolve from a standard Dockerfile to a highly secure version.

#### Phase 1: The Naive Approach (不推薦 / Not Recommended)
```dockerfile
FROM node:18
WORKDIR /app
COPY . .
RUN npm install
CMD ["node", "server.js"]
```
**問題 (Issues):**
- 預設以 `root` 執行。
- 包含完整的 OS 工具（shell, curl 等），方便攻擊者橫向移動。
- `node_modules` 可寫入，容易被注入惡意程式碼。

**Issues:**
- Runs as `root` by default.
- Contains full OS tools (shell, curl, etc.), facilitating lateral movement for attackers.
- `node_modules` is writable, making it easy to inject malicious code.

#### Phase 2: Production Hardened (推薦 / Recommended)

這個版本展示了多層防禦機制。
This version demonstrates multi-layered defense mechanisms.

```dockerfile
# Build Stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
# CI 環境中應使用 npm ci 確保版本一致性
# Use npm ci in CI environments to ensure version consistency
RUN npm ci 
COPY . .

# Runtime Stage - 使用 Distroless 或 Alpine
FROM node:18-alpine 

# 1. 建立非 Root 使用者 (Create non-root user)
# Alpine 預設有 'node' 使用者，但顯式建立更佳
# Alpine has a 'node' user by default, but explicit creation is better
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# 2. 僅複製必要檔案 (Copy only necessary files)
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
COPY --from=builder /app/server.js ./

# 3. 切換使用者 (Switch User)
USER appuser

# 4. 啟動應用 (Start Application)
CMD ["node", "server.js"]
```

#### Phase 3: Runtime Security Constraints (執行時安全限制)

僅有 Dockerfile 是不夠的，執行時的參數決定了最終的權限邊界。
The Dockerfile alone is not enough; runtime parameters determine the final privilege boundaries.

```bash
docker run -d \
  --name secure-app \
  \
  # 1. 限制資源以防止 DoS (Limit resources to prevent DoS)
  --memory="512m" \
  --cpus="1.0" \
  \
  # 2. 檔案系統唯讀，防止惡意寫入 (Read-only filesystem prevents malicious writes)
  --read-only \
  # 為需要寫入的目錄掛載 tmpfs (Mount tmpfs for directories requiring write access)
  --tmpfs /tmp \
  \
  # 3. 權限最小化 (Least Privilege)
  --cap-drop=ALL \
  # 僅加回必要的權限 (例如綁定 Port < 1024 需要 NET_BIND_SERVICE，若無則不加)
  # Only add back necessary caps (e.g., NET_BIND_SERVICE for ports < 1024)
  # --cap-add=NET_BIND_SERVICE \
  \
  # 4. 禁止權限提升 (Prevent Privilege Escalation)
  # 防止 setuid binary 改變使用者
  # Prevents setuid binaries from changing the user
  --security-opt=no-new-privileges:true \
  \
  my-secure-image:latest
```

**分析 (Analysis):**
- **`--read-only`**: 攻擊者即使找到 RCE (Remote Code Execution) 漏洞，也無法下載惡意腳本或修改現有程式碼。
- **`--cap-drop=ALL`**: 即使容器內的行程是 root（如果沒設 `USER`），它也無法修改系統時間、載入核心模組或進行原始網路操作。
- **`--security-opt=no-new-privileges:true`**: 這是防止攻擊者利用 `sudo` 或 `suid` 執行檔提升權限的關鍵開關。

**Analysis:**
- **`--read-only`**: Even if an attacker finds an RCE (Remote Code Execution) vulnerability, they cannot download malicious scripts or modify existing code.
- **`--cap-drop=ALL`**: Even if the process inside the container is root (if `USER` wasn't set), it cannot modify system time, load kernel modules, or perform raw network operations.
- **`--security-opt=no-new-privileges:true`**: This is a critical switch to prevent attackers from using `sudo` or `suid` binaries to escalate privileges.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 濫用 `--privileged` (Abusing `--privileged`)
-   **錯誤 (Pitfall):** 為了解決「權限不足」或「無法在容器內跑 Docker (DinD)」的問題，直接加上 `--privileged` 旗標。
    **Pitfall:** Adding the `--privileged` flag directly to solve "insufficient permission" issues or to run Docker-in-Docker (DinD).
-   **為何不好 (Why it's bad):** 這基本上給了容器與 Host 幾乎相同的權限（包括存取所有裝置）。這破壞了容器的所有隔離性。
    **Why it's bad:** This essentially grants the container nearly the same privileges as the Host (including access to all devices). It destroys all container isolation.
-   **替代方案 (Alternative):** 仔細分析需要的 Capability（如 `--cap-add=SYS_ADMIN`）或裝置（`--device`），僅開放需要的項目。
    **Alternative:** Carefully analyze the required Capability (e.g., `--cap-add=SYS_ADMIN`) or device (`--device`), and open only what is necessary.

### 5.2 將 Secrets 烘焙進映像檔 (Baking Secrets into Images)
-   **錯誤 (Pitfall):** `ENV DB_PASSWORD=secret` 寫在 Dockerfile 中。
    **Pitfall:** Writing `ENV DB_PASSWORD=secret` in the Dockerfile.
-   **為何不好 (Why it's bad):** 任何人只要能 pull 你的 image，透過 `docker history` 或 `docker inspect` 就能看到密碼。
    **Why it's bad:** Anyone who can pull your image can see the password via `docker history` or `docker inspect`.
-   **替代方案 (Alternative):** 使用 Docker Secrets (Swarm)、Kubernetes Secrets，或在執行時透過環境變數注入（但不要在 build time 注入）。
    **Alternative:** Use Docker Secrets (Swarm), Kubernetes Secrets, or inject via environment variables at runtime (but never at build time).

### 5.3 忽略 User Namespaces (Ignoring User Namespaces)
-   **錯誤 (Pitfall):** 依賴 `USER 1000` 但未啟用 Daemon 層級的 User Remapping。
    **Pitfall:** Relying on `USER 1000` without enabling Daemon-level User Remapping.
-   **為何不好 (Why it's bad):** 如果攻擊者逃逸出容器，容器內的 UID 1000 對應到 Host 的 UID 1000。如果 Host 的 UID 1000 有特殊權限，攻擊者就繼承了這些權限。
    **Why it's bad:** If an attacker escapes the container, UID 1000 inside corresponds to UID 1000 on the Host. If the Host's UID 1000 has special privileges, the attacker inherits them.
-   **替代方案 (Alternative):** 配置 `/etc/docker/daemon.json` 中的 `userns-remap`，將容器內的 root 映射為 Host 的非特權使用者（如 `nobody`）。
    **Alternative:** Configure `userns-remap` in `/etc/docker/daemon.json` to map the container's root to a non-privileged user on the Host (like `nobody`).

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 如果你需要執行一個必須使用 Root 權限的 Legacy 應用程式，你會如何確保安全性？
**If you need to run a legacy application that requires Root privileges, how would you ensure security?**

*   **高分回答要點 (Key Points for a High Score):**
    *   承認這是不理想的，但若是現實限制，首選 **User Namespaces (userns)**。這樣容器內的 Root 在 Host 上只是普通使用者。
    *   使用 **Capabilities Whitelisting** (`drop ALL`, `add` needed)。
    *   配置嚴格的 **Seccomp profile** 限制可用的 Syscalls。
    *   確保 Host 的 Kernel 是最新的，減少 Kernel Exploit 的風險。

### Q2: 請解釋 Docker 的 `privileged` 模式與 `root` 使用者有什麼區別？
**Explain the difference between Docker's `privileged` mode and the `root` user.**

*   **高分回答要點 (Key Points for a High Score):**
    *   **User:** 容器內的 `root` (UID 0) 預設擁有對容器內資源的控制權，但受限於 Capabilities、Seccomp 和 Namespaces，無法任意操作 Host 核心。
    *   **Privileged Mode:** 是一個特殊的旗標，它會移除 cgroup 限制、停用 Seccomp、賦予所有 Capabilities，並允許存取 Host 的所有裝置（`/dev`）。
    *   結論：`root` 是身分，`privileged` 是安全機制的開關。`root` in container != `root` on host (unless privileged).

### Q3: 在 CI/CD 流程中，你會在哪些階段加入容器安全掃描？為什麼？
**At which stages of the CI/CD pipeline would you include container security scanning? Why?**

*   **高分回答要點 (Key Points for a High Score):**
    *   **Pre-build (IDE/Commit):** 掃描 Dockerfile (Linting) 檢查是否使用 `latest` tag 或包含 secrets。
    *   **Post-build (Registry):** 映像檔建置完成後，掃描 Base OS 和 App Dependencies (SCA)。
    *   **Admission (Cluster):** 在部署到 K8s 前，Admission Controller 驗證映像檔簽章與掃描結果，阻止未經授權的映像檔運行。
    *   **Runtime:** 持續監控運行中的容器行為（如 Falco），偵測異常的 shell 啟動或檔案寫入。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 記憶錨點 (Key Takeaways)
1.  **最小權限 (Least Privilege):** 永遠不要以 Root 運行容器；使用 `USER` 指令。
2.  **核心隔離 (Kernel Isolation):** 善用 `--cap-drop=ALL` 與 `--security-opt=no-new-privileges`。
3.  **唯讀原則 (Immutability):** 生產環境容器應盡可能設定為 Read-only Filesystem。
4.  **供應鏈安全 (Supply Chain):** 映像檔必須經過掃描與簽章才能進入生產環境。
5.  **不信任預設值 (Don't Trust Defaults):** Docker 的預設值是為了易用性，而非安全性。

### 後續延伸 (Next Steps)
*   **Kubernetes Security:** 學習 Pod Security Standards (PSS) 與 Network Policies。這將是單機 Docker 安全概念在叢集層級的延伸。
*   **Runtime Security Tools:** 深入研究 Falco 或 Tetragon，了解如何基於 eBPF 監控容器行為。
*   **Distroless Images:** 實作 Google 的 Distroless 映像檔，極致縮小攻擊面。

下一章，我們將探討 **Docker 網路與服務發現 (Networking and Service Discovery)**，了解容器如何在隔離的網路環境中高效通訊。
In the next chapter, we will explore **Docker Networking and Service Discovery**, understanding how containers communicate efficiently within isolated network environments.