# 儲存效能優化與資料模式 / Storage Performance Optimization & Data Patterns

## Mental model｜心智模型

在 Azure 上設計儲存架構時，不要只把儲存視為「靜態的硬碟」，而應將其視為一條 **「流量管道 (Pipeline)」**。效能問題通常不是因為「空間不夠」，而是因為「管道太窄」或「流速限制」。

### 1. The Bottleneck Funnel (瓶頸漏斗)
系統的總體效能受限於鏈路中 **最低** 的限制值。
$$Total Performance = \min(VM\_Limit, Disk\_Limit, Network\_Bandwidth)$$
*   **Disk Limit**: 單顆磁碟的物理限制 (IOPS/Throughput)。
*   **VM Limit**: 虛擬機器本身的 IO吞吐量限制 (這常被忽略，導致買了昂貴的 Disk 卻跑不出效能)。
*   **App Limit**: 應用程式的並發數 (Concurrency) 與封包大小 (Block size)。

### 2. The CAP Theorem & PACELC (分散式權衡)
對於資料庫 (如 Cosmos DB, Azure SQL Hyperscale)：
*   在網路分區 (Partition) 發生時，你必須在 **可用性 (Availability)** 與 **一致性 (Consistency)** 之間做選擇。
*   即使沒有網路分區，你也要在 **延遲 (Latency)** 與 **一致性 (Consistency)** 之間做權衡。
*   *Mental Shift:* 從「我要最強的一致性」轉變為「我的業務邏輯能容忍多大的資料延遲？」

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Disk Storage: IOPS & Throughput Tuning
針對 I/O 密集型應用 (如 SQL Server on VM, Kafka)：

*   **Disk Striping (RAID 0)**:
    *   **Pattern**: 當單顆 Premium SSD (e.g., P30: 5,000 IOPS) 無法滿足需求，且 Ultra Disk 太貴時，將多顆 P30 透過 OS 層級 (LVM/Storage Spaces) 組成 RAID 0。
    *   **Benefit**: IOPS 與 Throughput 線性疊加，且成本通常低於單顆高階 Disk。
*   **Read-Only Caching**:
    *   **Pattern**: 對於讀多寫少的 workload (如 Web Server, Reporting DB)，開啟 Host Caching (Read-only)。
    *   **Benefit**: 讀取請求會由 VM 本地的 SSD 快取處理，不消耗遠端 Disk 的 IOPS 配額。

### 2. Blob Storage: High Performance & Cost Efficiency
*   **Prefix Randomization (Partitioning)**:
    *   **Pattern**: Azure Blob Storage 後端會根據檔名 (Key) 進行分區。如果大量檔案以相同字串開頭 (如 `2023-10-25-log-...`)，會導致單一分區熱點 (Hotspot)。
    *   **Best Practice**: 在檔名前加上 Hash 或 GUID (e.g., `3a1f-2023-10-25-log...`) 以分散負載。
*   **Lifecycle Management Policy**:
    *   **Pattern**: 設定自動化規則：`Hot` (7天) -> `Cool` (30天) -> `Archive` (365天) -> `Delete`。
    *   **Benefit**: 大幅降低長期儲存成本，無需撰寫額外 script。

### 3. Database Sharding & Consistency
*   **Sharding Strategy (Cosmos DB / SQL)**:
    *   **Pattern**: 選擇 Partition Key 時，尋找 **高基數 (High Cardinality)** 且 **查詢頻率均勻** 的屬性。
    *   **Example**: 多租戶系統中，若單一租戶資料量巨大，用 `TenantId` 做 Key 會導致 "Jumbo Partition"；此時應考慮 `TenantId_UserId` 或 `TenantId_Date` (Composite Key)。
*   **Consistency Tuning**:
    *   **Pattern**: 預設不要無腦選 Strong Consistency。
    *   **Session Consistency**: 大多數 Web App 的甜蜜點（使用者能讀到自己剛寫入的資料，效能優於 Strong）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "VM Throttling" Trap (VM 頻寬陷阱)
*   **Anti-pattern**: 在一台 `Standard_D2s_v3` (Max 3,200 IOPS) 上掛載一顆 `P30` (5,000 IOPS) 磁碟。
*   **Consequence**: 你的 Disk 永遠跑不滿，因為被 VM 本身的限制掐住了。這是在浪費錢。
*   **Fix**: 升級 VM 系列 (如 L-series 或 E-series) 或檢查 VM 的 "Uncached Disk Throughput" 規格。

### 2. The "Append Blob" Contention (追加寫入競爭)
*   **Anti-pattern**: 多個執行緒或多個 client 同時嘗試對同一個 Append Blob 進行寫入。
*   **Consequence**: 發生 `412 Precondition Failed` 或高延遲重試。
*   **Fix**: 每個 Writer 寫入自己的 Blob，後續再透過 ETL 流程合併；或改用 Event Hubs 作為緩衝。

### 3. Cross-Partition Queries (跨分區查詢)
*   **Anti-pattern**: 在 Cosmos DB 中，查詢條件未包含 Partition Key (例如 Key 是 `UserId`，但你用 `WHERE City = 'Taipei'` 查詢)。
*   **Consequence**: 資料庫必須掃描所有分區 (Fan-out)，消耗大量 RU (Request Units) 且延遲極高。
*   **Fix**: 重新設計 Data Model，或使用 "Materialized View" pattern 複製一份以 `City` 為 Key 的資料。

---

## Checklists & workflows｜檢查清單與流程

### Storage Selection Workflow (儲存選型決策)
1.  **資料結構為何？**
    *   Structured (SQL) -> Azure SQL / PostgreSQL
    *   Semi-structured (JSON) -> Cosmos DB
    *   Unstructured (Files/Media) -> Blob Storage
2.  **效能需求 (IOPS/Latency)？**
    *   Sub-millisecond latency -> Ultra Disk / Premium SSD v2 / Redis Cache
    *   General Purpose -> Premium SSD / Standard SSD
3.  **存取模式？**
    *   Random R/W -> Managed Disk / Cosmos DB
    *   Sequential Append -> Append Blob / Event Hubs

### Performance Tuning Checklist (效能調優檢核表)
- [ ] **Check VM Limits**: 確認 VM 的 Max IOPS/Throughput 是否大於所有掛載 Disk 的總和。
- [ ] **Check Disk Type**: 資料庫 Log 檔 (Write intensive) 是否使用了 Premium SSD 或 Ultra Disk？
- [ ] **Caching Strategy**: OS Disk 和 Read-heavy Data Disk 是否開啟了 `Read-only` Host Caching？(注意：Write-heavy disk 應設為 `None`)。
- [ ] **Network Latency**: 是否使用了 Proximity Placement Groups (PPG) 來讓運算與儲存物理距離更近？
- [ ] **Throttling Metrics**: 檢查 Azure Monitor 中的 `Throttling Percentage` 指標，確認是 Disk 還是 VM 在限流。
- [ ] **Block Size**: 應用程式的 I/O Block Size 是否過小？(e.g., 4KB I/O 會導致高 IOPS 但低 Throughput；64KB+ 通常較佳)。

---

## Real-world examples｜實戰案例

### Scenario 1: High-Performance SQL Server on Azure VM
**情境**: 一個金融交易系統，發現 SQL Server 寫入延遲很高，但 CPU 使用率很低。
*   **診斷**:
    *   使用了 `Standard_D8s_v3` VM。
    *   資料碟使用單顆 `P30` (5000 IOPS, 200 MB/s)。
    *   監控顯示 Disk Queue Length 持續飆高。
*   **解決方案 (Action)**:
    1.  **Storage Spaces (Striping)**: 新增第二顆 `P30`，在 OS 內做 Striping。理論上限變為 10,000 IOPS / 400 MB/s。
    2.  **VM Bottleneck Check**: `Standard_D8s_v3` 的上限是 12,800 IOPS / 192 MB/s (Cached) 或 **12,800 IOPS / 192 MB/s (Uncached)**。
    3.  **發現問題**: 雖然 IOPS 足夠，但 VM 的 Throughput 上限只有 192 MB/s，而兩顆 P30 需要 400 MB/s。VM 成為瓶頸。
    4.  **最終調整**: 將 VM 升級為 `Standard_E8bds_v5` (專為儲存優化的系列)，或調整 Block Size 以降低 Throughput 需求。

### Scenario 2: E-commerce Product Catalog (Cosmos DB)
**情境**: 電商網站在「黑色星期五」流量大增，Cosmos DB 頻繁出現 `429 Too Many Requests`，且擴充 RU 後效果不彰。
*   **診斷**:
    *   Partition Key 設定為 `Category` (產品類別)。
    *   大部分流量都集中在 `Category = 'Electronics'` (熱門商品)。
    *   這造成了 **Hot Partition (熱分區)**，該分區的物理資源耗盡，而其他分區 (如 `Books`) 卻閒置。
*   **解決方案 (Action)**:
    *   **Refactor**: 更改 Partition Key 為 `ProductId` (極高基數) 或 `Category_SubCategory_Hash` (合成鍵)。
    *   **V2 Design**: 使用 `ProductId` 作為 Key 以確保寫入均勻分佈；針對「查詢特定類別」的需求，使用 Azure Cognitive Search 或 Cosmos DB 的 Materialized View pattern 來解決讀取問題。