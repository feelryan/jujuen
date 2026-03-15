# 資源限制與效能調校：避免 OOM 與 CPU 爭搶 / Resource Limits & Performance Tuning: Avoiding OOM & CPU Contention

## Mental model｜心智模型

### 1. 容器不是虛擬機，是「被隔離的行程」
**Containers are not VMs; they are "isolated processes".**
不要把 Docker 容器想像成擁有一塊固定硬體的獨立伺服器。容器本質上是 Host OS 上的一個 Process，只是透過 Linux Kernel 的 **Cgroups (Control Groups)** 被貼上了「資源使用上限」的標籤。
- **CPU 是時間片 (Time Slices)**：限制 CPU 並不是減少 CPU 的核心數，而是限制該行程在一段時間內能佔用 CPU 的「時間比例」。
- **Memory 是帳本 (Ledger)**：Kernel 會記帳，一旦超過額度，Kernel 的 **OOM Killer (Out Of Memory Killer)** 就會像保全一樣，直接把該行程「殺掉」以保護系統穩定，而不是讓它變慢。

### 2. 應用程式的「自我感知」落差
**The "Self-Awareness" Gap.**
許多語言的 Runtime（如舊版 Java JVM 或 Node.js）預設會去讀取 Host 的總記憶體，而不是 Cgroups 的限制。
- **情境**：在一台 64GB RAM 的機器上跑一個限制 512MB 的容器。
- **後果**：Java 看到 64GB，於是快樂地開啟了 16GB 的 Heap，結果啟動瞬間就被 Docker (Cgroups) 判定超標而殺掉。這就是所謂的「容器內應用程式對資源限制無感」。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 記憶體限制策略：Hard Limit vs. Soft Limit
**Memory Limits Strategy.**

在 `docker-compose.yml` 或 Kubernetes 中，通常建議設定 **Hard Limit**。

- **Hard Limit (`--memory` / `limits.memory`)**：
  - 這是絕對天花板。超過此值，容器會被 OOM Killed。
  - **Best Practice**：**一定要設定**。這是防止單一容器吃光宿主機資源導致整台機器當機的最後防線。
- **Soft Limit (`--memory-reservation` / `requests.memory`)**：
  - 這是保障值或警告線。當 Host 記憶體緊繃時，Docker 會嘗試將容器壓縮到此數值內。
  - **Best Practice**：設定為應用程式正常運作所需的「最小」記憶體量。

### 2. 語言 Runtime 的資源感知配置
**Runtime Resource Awareness.**

這是避免 OOM 最關鍵的一步。不要寫死數值（如 `-Xmx2g`），而是讓 Runtime 動態適應容器限制。

#### **Java (JVM)**
從 Java 10+ (或 Java 8u191+) 開始，JVM 支援容器感知。
- **Pattern**: 使用百分比設定，預留空間給 Non-Heap (Metaspace, Threads, Overhead)。
- **Command**:
  ```bash
  # 建議設定為 75% 左右，保留 25% 給非 Heap 記憶體
  java -XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0 -jar app.jar
  ```

#### **Node.js**
Node.js v12+ 之後改善了限制，但仍建議明確設定或使用工具。
- **Pattern**: 在啟動指令中參考 Cgroups 記憶體限制。
- **Command**:
  ```bash
  # 使用 --max-old-space-size，通常設定為容器限制的 70-80%
  # 或者在 Dockerfile 中利用 script 動態計算
  node --max-old-space-size=460 index.js # 若容器限制為 512MB
  ```

#### **Go (Golang)**
Go 雖然沒有 VM Overhead，但 `GOMAXPROCS` 預設會抓取 Host 的 CPU 核數。
- **Pattern**: 使用 `automaxprocs` 庫來自動調整。
- **Implementation**:
  ```go
  import _ "go.uber.org/automaxprocs"
  ```

### 3. CPU 限制：Quota vs. Shares
**CPU Limits.**

- **CPU Limit (`--cpus`)**:
  - 設定硬上限（例如 `1.5` 代表最多使用 1.5 顆核心的算力）。
  - **優點**：效能可預測，不會影響鄰居。
  - **缺點**：如果設定太緊，會導致 **CPU Throttling**（節流），造成 API Latency 飆高。
- **CPU Shares (`--cpu-shares`)**:
  - 設定權重（預設 1024）。只有在 CPU 忙碌（爭搶）時才生效。
  - **Best Practice**: 對於延遲敏感（Latency-sensitive）的服務，小心使用過低的 CPU Limit；對於批次處理（Batch jobs），可以使用 Shares 來確保它們只在系統空閒時全速運作。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 誤將 Heap Size 等於 Container Limit
**Setting Heap Size == Container Limit.**
- **錯誤做法**：Docker 限制 1GB，Java 設定 `-Xmx1g`。
- **後果**：必死無疑。因為 Java Process 除了 Heap，還有 Metaspace、Code Cache、Thread Stacks、GC Overhead 等 Native Memory。總量會超過 1GB，導致 OOM Killed。
- **修正**：Heap Size 應約為 Container Limit 的 70% - 80%。

### 2. 忽略 Swap 的影響
**Ignoring Swap.**
- **陷阱**：預設情況下，Docker 可能允許容器使用 Swap。如果應用程式發生 Memory Leak，它可能不會馬上崩潰，而是開始使用 Swap，導致效能極度低落（Thrashing），且難以除錯。
- **建議**：在生產環境中，通常建議關閉 Swap (`--memory-swap` 設為與 `--memory` 相同值)，讓問題儘早暴露（Fail Fast）。

### 3. 盲目信任 `top` 或 `free` 指令
**Trusting `top` inside containers.**
- **陷阱**：在容器內執行 `top` 或 `free -h`，看到的往往是 **Host OS** 的總資源，而不是容器的限制。
- **修正**：使用 `cat /sys/fs/cgroup/memory/memory.limit_in_bytes` 或專門的監控工具（如 cAdvisor, Prometheus node-exporter）。

### 4. 沒有監控 OOM Kill 事件
**No Monitoring on OOM Kills.**
- **現象**：容器偶爾重啟，Log 裡卻沒有任何 Exception。
- **原因**：因為是被 Kernel 殺掉的（SIGKILL），應用程式來不及寫 Log。
- **修正**：檢查 `docker inspect <container_id>` 的 `State.OOMKilled` 欄位，或監控 Host 的 `dmesg`。

---

## Checklists & workflows｜檢查清單與流程

### Deployment Configuration Checklist
- [ ] **Memory Hard Limit**: 是否已為每個容器設定記憶體上限？（防止單點崩潰拖垮全站）
- [ ] **Runtime Configuration**:
    - Java: 是否設定了 `-XX:MaxRAMPercentage`？
    - Node.js: 是否設定了 `--max-old-space-size`？
    - Go: 是否使用了 `automaxprocs`？
- [ ] **Buffer Zone**: 記憶體限制是否預留了 20-30% 的緩衝區給非 Heap 使用？
- [ ] **CPU Strategy**: 
    - Web Server: 是否設定了合理的 CPU Request/Limit 以避免 Throttling？
    - Worker: 是否考慮使用 CPU Shares 降低優先級？

### Troubleshooting OOM Workflow
當容器無故重啟時：

1. **Check Docker State**:
   ```bash
   docker inspect <container_id> --format '{{.State.OOMKilled}}'
   ```
   如果是 `true`，確認是記憶體不足。

2. **Check Exit Code**:
   檢查 Exit Code 是否為 `137` (128 + 9 SIGKILL)。這通常代表被 OOM Killer 處決。

3. **Check Host Logs**:
   ```bash
   dmesg | grep -i "killed process"
   ```
   查看是哪個 Process 被殺，以及當下的記憶體使用狀況。

4. **Analyze Memory Usage**:
   使用 `docker stats` 觀察即時用量，或接入 Prometheus + Grafana 查看歷史趨勢。

---

## Real-world examples｜實戰案例

### Case 1: The "Silent Death" of a Java Microservice
**情境**：一個 Spring Boot 應用程式在流量高峰時會隨機重啟，Application Log 完全沒有 ERROR 紀錄。
**診斷**：
- `docker inspect` 顯示 `OOMKilled: true`。
- `docker-compose.yml` 設定 `mem_limit: 512m`。
- Java 參數未設定，預設 Heap 佔用了大部分空間，加上 Tomcat Threads 增加，直接頂破 512MB。

**解決方案 (`docker-compose.yml`)**：
```yaml
version: '3.8'
services:
  api:
    image: my-java-app
    deploy:
      resources:
        limits:
          memory: 512M  # Docker 限制
          cpus: '1.0'
    environment:
      # 讓 JVM 自動感知並只使用 75% (約 384MB) 作為 Heap，保留 128MB 給 Native Memory
      - JAVA_TOOL_OPTIONS=-XX:MaxRAMPercentage=75.0
```

### Case 2: CPU Throttling Causing Latency Spikes
**情境**：Node.js API 服務平均回應時間很快，但 P99 延遲偶爾會飆高到數秒。
**診斷**：
- 開發者為了省資源，設定了非常嚴格的 CPU Limit: `cpus: '0.2'`。
- 當 Request 進來需要處理 JSON Parsing 時，CPU 瞬間需求超過 0.2 顆核。
- Linux CFS (Completely Fair Scheduler) 強制該行程暫停 (Throttling)，直到下一個週期。

**解決方案**：
- **放寬 Limit**：將 `cpus` 提升至 `1.0` 或移除硬限制。
- **監控 Throttling**：觀察 `container_cpu_cfs_throttled_seconds_total` 指標。
- **修正觀念**：CPU 不像 Memory，暫時超過不會導致 Crash，只會變慢。對於 Latency 敏感的服務，CPU Limit 應設得寬鬆，或僅使用 CPU Request (Shares) 來保障最低算力。