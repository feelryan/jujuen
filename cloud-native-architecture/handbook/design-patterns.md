# 關鍵雲原生設計模式 / Key Cloud-Native Design Patterns

## Mental model｜心智模型

在雲原生架構中，我們必須打破「一個應用程式 = 一個行程 (Process)」的舊有觀念。Kubernetes 的原子單位是 **Pod**，而 Pod 是一組容器的集合。這意味著我們可以將「業務邏輯」與「基礎設施關注點」解耦到不同的容器中，但它們共享同一個網路與儲存空間。

**核心思維：進程外的裝飾者模式 (Out-of-Process Decorator Pattern)**

想像你的應用程式是飛機的「駕駛員 (Pilot)」，他的職責是專心飛行（處理業務邏輯）。
- **Sidecar/Adapter/Ambassador** 就像是「副駕駛」或「隨機工程師」。
- 他們負責導航、通訊加密、監控引擎數據、轉換訊號。
- **關鍵點**：駕駛員不需要知道副駕駛是用什麼語言溝通的，也不需要知道引擎監控的細節。駕駛員只管飛，副駕駛負責讓飛行符合規範。

In Cloud-Native architecture, we must break the mental model of "One Application = One Process." The atomic unit in Kubernetes is the **Pod**, which is a collection of containers. This allows us to decouple "Business Logic" from "Infrastructure Concerns" into separate containers that share the same network and storage.

**Core Concept: Out-of-Process Decorator Pattern**
Think of your application as the **Pilot** (Business Logic).
- **Sidecar/Adapter/Ambassador** are the **Co-pilots** or **Flight Engineers**.
- They handle navigation, encryption (mTLS), metrics monitoring, and signal translation.
- **Key Takeaway**: The Pilot doesn't need to know how the Co-pilot communicates or monitors the engine. The Pilot flies; the Co-pilot ensures the flight meets infrastructure standards.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Sidecar Pattern (邊車模式)
**The Helper / 輔助者**
這是最通用的模式。輔助容器與主應用容器一同部署，擴充主應用的功能而不改變其程式碼。

- **Use Cases (何時使用):**
  - **Service Mesh (Istio/Linkerd):** 負責 mTLS、流量控制、重試機制。
  - **Log Shipping (Fluentd/Filebeat):** 應用程式只管寫 log 到 stdout 或檔案，Sidecar 負責蒐集並轉送到 ELK/Splunk。
  - **Configuration Watcher:** 監控 ConfigMap 變更並觸發應用程式熱重載 (Hot Reload)。
- **Best Practice:** 保持 Sidecar 輕量且單一職責。確保資源限制 (Resource Limits) 設定正確，避免 Sidecar 搶佔主應用資源。

### 2. Ambassador Pattern (大使模式)
**The Proxy / 代理人**
代表應用程式向外部發送請求，處理連線複雜度。它像是應用程式的「出站代理 (Outbound Proxy)」。

- **Use Cases (何時使用):**
  - **Legacy Protocol Adaptation:** 應用程式只懂 HTTP，但目標資料庫需要複雜的 TCP 握手或舊式驗證。
  - **Circuit Breaking / Retries:** 在應用程式發出請求前，由 Ambassador 處理斷路邏輯（如果語言層級的 library 不支援）。
  - **Database Sharding:** 應用程式連線到 localhost，Ambassador 負責決定路由到哪個 Shard。
- **Best Practice:** 將與外部系統的整合邏輯（如 Auth、Routing）封裝在 Ambassador 中，讓開發者在本地測試時只需 mock 這個代理。

### 3. Adapter Pattern (轉接器模式)
**The Normalizer / 標準化者**
將應用程式的輸出轉換為外部系統期望的統一格式。

- **Use Cases (何時使用):**
  - **Monitoring:** 應用程式輸出自定義格式的 metrics，Adapter 將其轉換為 Prometheus 格式 (/metrics)。
  - **Logging Standardization:** 將不同 legacy 系統的異質 log 格式轉換為統一的 JSON 結構。
- **Best Practice:** 當你無法修改原始碼（例如使用第三方閉源軟體）但必須符合公司的監控標準時，這是首選方案。

### 4. Operator Pattern (操作者模式)
**The Automated Ops / 自動化維運**
這不是一個容器模式，而是一種軟體架構。它將「人類維運者的知識」編碼為軟體（Controller + CRD）。

- **Use Cases (何時使用):**
  - **Complex Stateful Apps:** 資料庫 (PostgreSQL, Kafka, Redis) 的備份、還原、故障轉移 (Failover)。
  - **Lifecycle Management:** 複雜的升級流程（先升級 Slave，再切換 Master，再升級舊 Master）。
- **Best Practice:**
  - **不要濫用 (Don't Overuse):** 如果 Helm Chart 或 Kustomize 就能解決部署問題，不要寫 Operator。
  - **Level of Maturity:** 優先使用社群維護良好的 Operator (如 Prometheus Operator, Strimzi for Kafka)，避免自造輪子。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "God Sidecar" (萬能邊車)
- **Problem:** 將 Logging, Monitoring, Proxy, Auth 全部塞進同一個巨大的 Sidecar 容器。
- **Consequence:** 導致 Sidecar 比主應用還吃資源，且難以維護與升級。
- **Solution:** 拆分為多個專職的 Sidecars，或將通用功能下沈到 Node Level (DaemonSet)。

### 2. Resource Blindness (資源盲區)
- **Problem:** 忽略 Sidecar 的資源消耗。
- **Consequence:** 假設一個 Sidecar 吃 100MB RAM，當你有 1000 個 Pods 時，你就浪費了 100GB 的記憶體在 Sidecar 上。
- **Solution:** 嚴格設定 Sidecar 的 `resources.requests` 與 `limits`。

### 3. Startup Race Conditions (啟動競態條件)
- **Problem:** 主應用程式 (Main Container) 比 Sidecar (如 Istio Proxy) 先啟動，導致應用程式一啟動就嘗試連網失敗。
- **Consequence:** Pod 陷入 CrashLoopBackOff 或初始化錯誤。
- **Solution:** 使用 Kubernetes 1.28+ 的 SidecarContainers feature，或在應用程式啟動腳本中加入 `wait-for-sidecar` 的邏輯。

### 4. Operator Over-Engineering (過度工程化的 Operator)
- **Problem:** 為一個無狀態 (Stateless) 的 Web App 寫了一個 Operator。
- **Consequence:** 增加了巨大的維護成本，卻沒有帶來自動化價值。
- **Solution:** 無狀態應用請使用 Deployment + Service + Ingress。Operator 留給有狀態 (Stateful) 或極度複雜的應用。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Which pattern should I use?
當你需要擴充現有容器功能時：

- [ ] **Is it a complex operational task (backup, failover)?**
    - Yes -> **Operator Pattern**
    - No -> Continue below.
- [ ] **Do I need to standardize output (logs/metrics) without changing code?**
    - Yes -> **Adapter Pattern**
- [ ] **Do I need to handle outbound connectivity (proxy, auth) for the app?**
    - Yes -> **Ambassador Pattern**
- [ ] **Do I need to enhance the app with cross-cutting concerns (mTLS, tracing)?**
    - Yes -> **Sidecar Pattern**

### Implementation Checklist (實作檢查清單)

- [ ] **Lifecycle Order:** 確認 Sidecar 與主容器的啟動與關閉順序是否已處理（例如：主應用結束後，Sidecar 是否能自動退出？）。
- [ ] **Resource Budget:** 是否已計算 Sidecar 的 CPU/Memory overhead 並納入 Capacity Planning？
- [ ] **Security Context:** Sidecar 是否需要特權 (Privileged)？盡量避免，並遵循最小權限原則。
- [ ] **Health Checks:** Sidecar 是否有獨立的 Liveness/Readiness Probe？如果 Sidecar 掛了，Pod 是否應該被視為不健康？
- [ ] **Shared Volume:** 如果 Sidecar 需要讀取主應用的 Log 或 Config，是否已正確掛載 `emptyDir` 或 `ConfigMap`？

---

## Real-world examples｜實戰案例

### Scenario 1: Legacy Banking App Modernization (Sidecar + Ambassador)
**情境：** 一個老舊的 Java 銀行核心系統，只支援 HTTP 且無法修改程式碼加入 mTLS，但資安規範要求服務間通訊必須加密。此外，它需要連線到一個新的外部 API，該 API 需要 OAuth2 Token 交換。

**Solution:**
1.  **Sidecar (Istio/Envoy):** 部署 Envoy Sidecar 攔截所有進出流量。Envoy 負責將 HTTP 流量封裝在 mTLS 中與其他服務溝通。Java App 完全不知情。
2.  **Ambassador (Auth Proxy):** 在同一個 Pod 中部署一個輕量的 Auth Proxy。Java App 發送請求給 `localhost:8080`，Ambassador 接收請求，向 Auth Server 換取 Token，將 Token 注入 Header，再轉發給外部 API。

```yaml
# Conceptual Pod Definition
apiVersion: v1
kind: Pod
metadata:
  name: legacy-banking-app
spec:
  containers:
  - name: main-app
    image: legacy-java:v1.0
    env:
    - name: EXTERNAL_API_URL
      value: "http://localhost:8080" # Points to Ambassador

  - name: auth-ambassador
    image: auth-proxy:latest
    ports:
    - containerPort: 8080
    # Logic: Receive req -> Get OAuth Token -> Forward to Real External API

  - name: istio-proxy # Injected automatically usually
    image: envoy:latest
    # Logic: mTLS handling
```

### Scenario 2: Unified Monitoring for Polyglot Microservices (Adapter)
**情境：** 團隊有多種語言寫的微服務（Node.js, Python, Go, Java）。監控系統統一使用 Prometheus。Go 和 Java 很容易整合 Prometheus SDK，但 Node.js 舊專案輸出的 metrics 格式是自定義的 JSON，難以修改。

**Solution:**
- 使用 **Adapter Pattern**。
- 為 Node.js 服務掛載一個 `metrics-adapter` 容器。
- Adapter 定期打 Node.js 的 `localhost:3000/stats` (JSON)，轉換成 Prometheus 格式，並暴露在 `0.0.0.0:9090/metrics` 供 Prometheus Server 抓取。

### Scenario 3: Managing PostgreSQL on Kubernetes (Operator)
**情境：** 需要在 K8s 上運行 PostgreSQL Cluster，包含 Primary-Replica 架構、自動備份到 S3、以及當 Primary 掛掉時自動選主。

**Solution:**
- **不要** 使用 StatefulSet + Sidecar 手刻 Script。
- **使用** `Postgres Operator` (如 Zalando 或 CloudNativePG)。
- **Why?** 故障轉移涉及複雜的狀態判斷（誰的 WAL log 最也新？），這是 Operator 封裝的「維運知識」最強大的地方。

```yaml
# With Operator, you declare intent, not steps.
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-example
spec:
  instances: 3
  storage:
    size: 10Gi
  backup:
    barmanObjectStore:
      destinationPath: s3://my-bucket/backups
      # The Operator handles the cron jobs, WAL archiving, and recovery logic.
```