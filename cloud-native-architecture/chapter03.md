# Chapter 03: Container Design Patterns & Kubernetes Primitives
# 第 3 章：容器設計模式與 Kubernetes 原語

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

In modern Cloud-Native environments, simply containerizing an application is rarely enough. To build resilient, observable, and scalable systems, Senior Engineers must master how containers interact within a Pod and how Kubernetes primitives orchestrate these workloads. This chapter moves beyond basic `docker run` concepts to architectural patterns and production-grade configurations.
在現代雲原生環境中，僅僅將應用程式容器化通常是不夠的。為了構建具備彈性、可觀測性與可擴充性的系統，資深工程師必須掌握容器如何在 Pod 內互動，以及 Kubernetes 原語（Primitives）如何編排這些工作負載。本章將超越基礎的 `docker run` 概念，深入探討架構模式與生產級配置。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Implement Multi-Container Patterns**: Distinguish between and implement Sidecar, Ambassador, and Adapter patterns to decouple auxiliary logic from business logic.
    **實作多容器模式**：區分並實作 Sidecar、Ambassador 與 Adapter 模式，將輔助邏輯與業務邏輯解耦。
2.  **Optimize Workload Selection**: Choose the correct Kubernetes primitive (Deployment vs. StatefulSet vs. DaemonSet) based on application state requirements and identity stability.
    **優化工作負載選擇**：根據應用程式的狀態需求與身分穩定性，選擇正確的 Kubernetes 原語（Deployment vs. StatefulSet vs. DaemonSet）。
3.  **Master Resource Management**: Configure `requests` and `limits` to control Quality of Service (QoS) classes, preventing "Noisy Neighbor" issues and ensuring predictable performance.
    **掌握資源管理**：配置 `requests` 與 `limits` 以控制服務品質（QoS）等級，防止「吵鬧鄰居（Noisy Neighbor）」問題並確保可預測的效能。
4.  **Handle Lifecycle Events**: Design containers that gracefully handle startup (Probes) and shutdown (SIGTERM/PreStop hooks) sequences.
    **處理生命週期事件**：設計能夠優雅處理啟動（Probes）與關閉（SIGTERM/PreStop hooks）序列的容器。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 The Pod as a "Logical Host"
### 2.1 Pod 作為「邏輯主機」

**Mental Model**: Think of a Kubernetes Pod not as a single process, but as a traditional Virtual Machine or a "Logical Host."
**心智模型**：不要將 Kubernetes Pod 視為單一進程，而應將其視為傳統的虛擬機或「邏輯主機」。

*   **Shared Context**: Containers within the same Pod share the same Network Namespace (same IP, same localhost) and can share IPC and Storage Volumes.
    **共享情境**：同一個 Pod 內的容器共享相同的網路命名空間（相同的 IP、相同的 localhost），並且可以共享 IPC 與儲存卷（Volumes）。
*   **Implication**: This allows tightly coupled processes to communicate efficiently via `localhost` or shared files, forming the basis of container design patterns.
    **意涵**：這允許緊密耦合的進程透過 `localhost` 或共享檔案高效通訊，構成了容器設計模式的基礎。

### 2.2 Container Design Patterns
### 2.2 容器設計模式

These patterns address the separation of concerns by placing auxiliary tasks in separate containers within the same Pod.
這些模式透過將輔助任務放置在同一個 Pod 內的不同容器中，來解決關注點分離的問題。

1.  **Sidecar Pattern**: Extends and enhances the main container functionality (e.g., log shipping, configuration reloading, proxying).
    **Sidecar 模式**：擴充並增強主容器的功能（例如：日誌傳送、配置熱加載、代理）。
2.  **Ambassador Pattern**: Acts as a proxy to the outside world. The main application connects to `localhost`, and the Ambassador handles the complexity of connecting to external clusters or databases.
    **Ambassador 模式**：作為通往外部世界的代理。主應用程式連線至 `localhost`，而 Ambassador 負責處理連線至外部叢集或資料庫的複雜性。
3.  **Adapter Pattern**: Standardizes output. It transforms the heterogeneous monitoring metrics or logs of the main application into a unified format expected by the monitoring system.
    **Adapter 模式**：標準化輸出。它將主應用程式異質的監控指標或日誌，轉換為監控系統所預期的統一格式。

### 2.3 Workload Primitives: Deployment vs. StatefulSet
### 2.3 工作負載原語：Deployment vs. StatefulSet

*   **Deployment**: Treats Pods as ephemeral "cattle." Pods are interchangeable, have random hashes in their names, and no persistent identity. Ideal for stateless microservices.
    **Deployment**：將 Pod 視為短暫的「家畜（cattle）」。Pod 是可替換的，名稱中包含隨機雜湊，且沒有持久的身分。非常適合無狀態微服務。
*   **StatefulSet**: Treats Pods as "pets." Each Pod has a sticky identity (ordinal index like `web-0`, `web-1`), stable network ID, and persistent storage binding. Essential for databases or distributed stores (e.g., Kafka, Cassandra).
    **StatefulSet**：將 Pod 視為「寵物（pets）」。每個 Pod 都有固定的身分（序號索引，如 `web-0`、`web-1`）、穩定的網路 ID 以及持久的儲存綁定。對於資料庫或分散式儲存（如 Kafka、Cassandra）至關重要。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### 3.1 Service Mesh Implementation (Sidecar)
### 3.1 服務網格實作（Sidecar）

In a production Service Mesh (like Istio or Linkerd), the Sidecar pattern is ubiquitous. An Envoy proxy is injected into every Pod.
在生產環境的服務網格（如 Istio 或 Linkerd）中，Sidecar 模式無處不在。Envoy 代理會被注入到每個 Pod 中。

*   **Role**: The application code talks to the local Sidecar via loopback. The Sidecar handles mTLS, circuit breaking, retries, and tracing.
    **角色**：應用程式碼透過 loopback 與本地 Sidecar 通訊。Sidecar 負責處理 mTLS、斷路器（Circuit Breaking）、重試與追蹤。
*   **System Design Benefit**: Developers focus on business logic without implementing complex network resilience libraries in every language (Java, Go, Node.js).
    **系統設計效益**：開發者專注於業務邏輯，無需在每種語言（Java、Go、Node.js）中實作複雜的網路韌性函式庫。

### 3.2 Legacy App Modernization (Adapter/Ambassador)
### 3.2 舊有應用程式現代化（Adapter/Ambassador）

Consider a legacy application that only logs to a local file and expects a local MySQL connection.
考慮一個舊有應用程式，它只能將日誌記錄到本地檔案，並且預期連線至本地 MySQL。

*   **Adapter Usage**: A log-shipper container (e.g., Fluent Bit) reads the shared file volume and pushes logs to Elasticsearch. The legacy app remains unchanged.
    **Adapter 用法**：日誌傳送容器（例如 Fluent Bit）讀取共享檔案卷，並將日誌推送到 Elasticsearch。舊有應用程式保持不變。
*   **Ambassador Usage**: An Ambassador container listens on `localhost:3306` and proxies traffic to a remote, sharded MySQL cluster. The legacy app thinks it's talking to a local DB.
    **Ambassador 用法**：Ambassador 容器在 `localhost:3306` 監聽，並將流量代理到遠端的分片 MySQL 叢集。舊有應用程式以為它正在與本地資料庫通訊。

### 3.3 High Availability & Rolling Updates
### 3.3 高可用性與滾動更新

Kubernetes Deployments enable zero-downtime deployments via Rolling Updates.
Kubernetes Deployments 透過滾動更新（Rolling Updates）實現零停機部署。

*   **Mechanism**: K8s spins up a new ReplicaSet, waits for the Readiness Probe to pass, and then terminates old Pods.
    **機制**：K8s 啟動一個新的 ReplicaSet，等待 Readiness Probe 通過，然後終止舊的 Pod。
*   **Design Consideration**: You must implement `readinessProbe` (is the app ready to serve traffic?) and `livenessProbe` (is the app dead and needs a restart?) correctly to prevent traffic from hitting unready pods or restarting healthy pods during high load.
    **設計考量**：你必須正確實作 `readinessProbe`（應用程式是否準備好接收流量？）與 `livenessProbe`（應用程式是否已死當並需要重啟？），以防止流量打到未就緒的 Pod，或在高負載期間重啟健康的 Pod。

---

## 4. Walkthrough: Implementing a Sidecar for Log Shipping
## 4. 逐步示例：實作日誌傳送的 Sidecar

### Scenario
### 情境

We have a legacy Java application that writes logs to `/var/log/app.log`. We cannot modify the source code to send logs to standard output (stdout), which is the Kubernetes standard for log collection.
我們有一個舊有的 Java 應用程式，它將日誌寫入 `/var/log/app.log`。我們無法修改原始碼將日誌發送到標準輸出（stdout），而 stdout 是 Kubernetes 收集日誌的標準方式。

### Step 1: Define the Shared Volume
### 步驟 1：定義共享卷

We need an `emptyDir` volume that exists as long as the Pod is running. Both containers will mount this.
我們需要一個 `emptyDir` 卷，只要 Pod 在運行它就存在。兩個容器都將掛載此卷。

### Step 2: Configure the Main Container
### 步驟 2：配置主容器

The main app writes to the mounted path.
主應用程式寫入掛載的路徑。

### Step 3: Configure the Sidecar Container
### 步驟 3：配置 Sidecar 容器

The sidecar runs a simple command (like `tail -f`) to stream the file content to its own stdout.
Sidecar 執行一個簡單的指令（如 `tail -f`）將檔案內容串流到它自己的 stdout。

### Implementation (YAML)
### 實作 (YAML)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: legacy-app-with-sidecar
spec:
  volumes:
  - name: log-volume
    emptyDir: {}  # Lifecycle tied to the Pod

  containers:
  # 1. Main Application Container
  - name: app-container
    image: my-legacy-java-app:1.0
    volumeMounts:
    - name: log-volume
      mountPath: /var/log
    # Simulating app writing to file
    command: ["/bin/sh", "-c"]
    args: ["while true; do echo $(date) - App Running >> /var/log/app.log; sleep 1; done"]

  # 2. Sidecar Container (Adapter Pattern variant)
  - name: log-sidecar
    image: busybox
    volumeMounts:
    - name: log-volume
      mountPath: /var/log
    # Streams file to stdout, which K8s collects
    command: ["/bin/sh", "-c"]
    args: ["tail -n+1 -f /var/log/app.log"]
```

### Why this works?
### 為何這行得通？

*   **Decoupling**: The app doesn't know about logging infrastructure. The sidecar handles the adaptation.
    **解耦**：應用程式不知道日誌基礎設施的存在。Sidecar 負責適配。
*   **Observability**: `kubectl logs legacy-app-with-sidecar -c log-sidecar` now shows the logs, and cluster-level agents (like Fluentd daemonsets) can pick this up automatically.
    **可觀測性**：`kubectl logs legacy-app-with-sidecar -c log-sidecar` 現在可以顯示日誌，且叢集層級的代理（如 Fluentd daemonsets）可以自動收集這些日誌。

### Resource Management Deep Dive: QoS Classes
### 資源管理深入探討：QoS 等級

When defining these containers, setting resources is critical.
在定義這些容器時，設定資源至關重要。

*   **Guaranteed**: `requests` == `limits` (for CPU and Memory). The Pod is top priority and least likely to be evicted.
    **Guaranteed**：`requests` == `limits`（針對 CPU 和記憶體）。該 Pod 具有最高優先級，最不可能被驅逐。
*   **Burstable**: `requests` < `limits`. The Pod gets a guaranteed baseline but can burst. If the node is under pressure, these are evicted after BestEffort pods.
    **Burstable**：`requests` < `limits`。Pod 獲得保證的基準資源但可以突發使用。如果節點面臨壓力，這些 Pod 會在 BestEffort Pod 之後被驅逐。
*   **BestEffort**: No requests or limits set. These are the first to be killed when the node runs out of resources. **Avoid this in production.**
    **BestEffort**：未設定 requests 或 limits。當節點資源耗盡時，這些是第一個被殺掉的。**在生產環境中應避免此設定。**

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 The "Latest" Tag Trap
### 5.1 "Latest" 標籤陷阱

*   **Anti-pattern**: Using `image: my-app:latest` in Deployments.
    **反模式**：在 Deployments 中使用 `image: my-app:latest`。
*   **Why it's bad**: It breaks immutability. You cannot rollback reliably because `latest` changes over time. It also confuses Kubernetes caching logic (imagePullPolicy).
    **為何不好**：這破壞了不可變性（Immutability）。你無法可靠地回滾，因為 `latest` 會隨時間改變。這也會混淆 Kubernetes 的快取邏輯（imagePullPolicy）。
*   **Solution**: Use specific version tags (e.g., `v1.2.3`) or SHA digests.
    **解決方案**：使用特定的版本標籤（例如 `v1.2.3`）或 SHA 摘要。

### 5.2 Ignoring Graceful Shutdown
### 5.2 忽略優雅關閉

*   **Anti-pattern**: Application receives `SIGTERM` and immediately cuts connections, dropping in-flight requests.
    **反模式**：應用程式收到 `SIGTERM` 後立即切斷連線，丟棄處理中的請求。
*   **Why it's bad**: Causes 5xx errors during rolling updates.
    **為何不好**：在滾動更新期間導致 5xx 錯誤。
*   **Solution**: Handle `SIGTERM` in code to stop accepting new requests but finish processing current ones. Use `preStop` hook to sleep for a few seconds to allow K8s networking (iptables/IPVS) to propagate the endpoint removal before the app shuts down.
    **解決方案**：在程式碼中處理 `SIGTERM`，停止接收新請求但完成當前請求的處理。使用 `preStop` hook 睡眠幾秒鐘，讓 K8s 網路（iptables/IPVS）在應用程式關閉前傳播端點移除的資訊。

### 5.3 CPU Limits Throttling
### 5.3 CPU 限制導致的節流

*   **Anti-pattern**: Setting CPU limits too tight on latency-sensitive Java/Go apps.
    **反模式**：對延遲敏感的 Java/Go 應用程式設定過於嚴格的 CPU 限制。
*   **Why it's bad**: Kubernetes uses CFS (Completely Fair Scheduler) quotas. If a container uses its quota in the first 100ms of a period, it gets throttled for the rest, causing high tail latency (P99).
    **為何不好**：Kubernetes 使用 CFS（完全公平排程器）配額。如果容器在週期的前 100ms 用完了配額，它將在剩餘時間內被節流，導致高尾部延遲（P99）。
*   **Solution**: Be generous with CPU limits or remove them entirely (relying only on requests) if the kernel version handles CPU bursting poorly, while keeping Memory limits strict to prevent OOM.
    **解決方案**：如果核心版本處理 CPU 突發的效果不佳，請寬鬆設定 CPU 限制或完全移除（僅依賴 requests），同時保持嚴格的記憶體限制以防止 OOM。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: Design a highly available deployment for a stateful application (e.g., a custom sharded DB).
### Q1: 為有狀態應用程式（例如自定義分片資料庫）設計高可用部署。

*   **Key Points**:
    *   Must use **StatefulSet** for stable network identity (`db-0`, `db-1`).
    *   Use **Headless Service** to allow direct addressing of pods (no load balancing IP).
    *   **PersistentVolumeClaims (PVC)** templates ensuring data survives pod restarts.
    *   Handling **Pod Disruption Budgets (PDB)** to ensure quorum during cluster upgrades.
*   **關鍵要點**：
    *   必須使用 **StatefulSet** 以獲得穩定的網路身分（`db-0`, `db-1`）。
    *   使用 **Headless Service** 允許直接定址 Pod（無負載平衡 IP）。
    *   **PersistentVolumeClaims (PVC)** 模板確保資料在 Pod 重啟後留存。
    *   處理 **Pod Disruption Budgets (PDB)** 以確保叢集升級期間的法定人數（Quorum）。

### Q2: How would you debug a Pod that is stuck in `CrashLoopBackOff`?
### Q2: 你會如何除錯一個卡在 `CrashLoopBackOff` 狀態的 Pod？

*   **Key Points**:
    *   Check `kubectl logs` (previous instance via `-p` flag if it died quickly).
    *   Check `kubectl describe pod` for events (OOMKilled, Liveness Probe failure, Mount error).
    *   Check exit codes (1 = app error, 137 = OOM/SIGKILL).
    *   Verify configuration (ConfigMap/Secret) mounting issues.
*   **關鍵要點**：
    *   檢查 `kubectl logs`（如果死得很快，使用 `-p` 旗標查看前一個實例）。
    *   檢查 `kubectl describe pod` 查看事件（OOMKilled、Liveness Probe 失敗、掛載錯誤）。
    *   檢查退出代碼（1 = 應用程式錯誤，137 = OOM/SIGKILL）。
    *   驗證配置（ConfigMap/Secret）掛載問題。

### Q3: Explain the difference between Sidecar and DaemonSet. When to use which?
### Q3: 解釋 Sidecar 與 DaemonSet 的差異。何時使用哪一個？

*   **Key Points**:
    *   **Sidecar**: 1:1 relationship with the app container. Runs inside the *same* Pod. Used for app-specific logic (proxy to specific DB, log parsing for this app).
    *   **DaemonSet**: 1:Node relationship. Runs one Pod per Node. Used for node-level infrastructure (CNI plugin, node log collector like Fluentd, monitoring agent).
*   **關鍵要點**：
    *   **Sidecar**：與應用程式容器是 1:1 關係。在*同一個* Pod 內運行。用於特定於應用程式的邏輯（特定資料庫的代理、此應用程式的日誌解析）。
    *   **DaemonSet**：與節點是 1:Node 關係。每個節點運行一個 Pod。用於節點層級的基礎設施（CNI 外掛、節點日誌收集器如 Fluentd、監控代理）。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Key Takeaways (記憶錨點)
### 重點摘要

1.  **Pod is the Atom**: Containers in a Pod share `localhost` and volumes. This enables tightly coupled patterns.
    **Pod 是原子單位**：Pod 中的容器共享 `localhost` 和卷。這實現了緊密耦合的模式。
2.  **Sidecar/Ambassador/Adapter**: Use these patterns to keep business logic clean and offload infrastructure concerns (networking, logging, monitoring).
    **Sidecar/Ambassador/Adapter**：使用這些模式保持業務邏輯乾淨，並卸載基礎設施關注點（網路、日誌、監控）。
3.  **Deployment vs. StatefulSet**: Use Deployments for stateless apps (cattle); StatefulSets for stateful apps needing stable identity (pets).
    **Deployment vs. StatefulSet**：無狀態應用程式使用 Deployments（家畜）；需要穩定身分的有狀態應用程式使用 StatefulSets（寵物）。
4.  **Resource Limits**: Always define requests/limits. Prefer **Guaranteed** or **Burstable** QoS for production critical paths.
    **資源限制**：務必定義 requests/limits。生產關鍵路徑優先選擇 **Guaranteed** 或 **Burstable** QoS。
5.  **Lifecycle Hooks**: Implement `readinessProbe` for traffic safety and `preStop` hooks for graceful termination.
    **生命週期 Hooks**：實作 `readinessProbe` 以確保流量安全，並實作 `preStop` hooks 以實現優雅終止。

### Next Steps
### 後續延伸

*   **Networking Deep Dive**: Now that you understand the Pod, explore how Pods communicate across nodes (CNI, Services, Ingress).
    **網路深入探討**：既然你已了解 Pod，接下來探索 Pod 如何跨節點通訊（CNI、Services、Ingress）。
*   **Advanced Scheduling**: Look into Taints, Tolerations, and Affinity to control exactly where your Pods land.
    **進階排程**：研究 Taints、Tolerations 與 Affinity，以精確控制 Pod 的落點。
*   **Next Chapter**: We will move to **Chapter 04: Service Discovery & Mesh Architecture**.
    **下一章**：我們將進入 **第 4 章：服務發現與網格架構**。