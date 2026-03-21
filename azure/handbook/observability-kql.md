# 可觀測性與 KQL 實戰 / Observability & KQL in Practice

## Mental model｜心智模型

在 Azure 的世界中，可觀測性（Observability）不僅僅是「收集 Log」，而是一個從**訊號採集**到**洞察行動**的完整資料管道（Data Pipeline）。要精通此領域，你需要建立以下的心智模型：

### 1. The Three Pillars in Azure Context (Azure 脈絡下的三大支柱)
- **Metrics (指標)**：數值型資料，輕量且即時。用於回答「系統現在是否健康？」(e.g., CPU %, Request Count)。在 Azure 中主要由 `Azure Monitor Metrics` 處理。
- **Logs (日誌)**：文本或結構化資料，詳細但成本較高。用於回答「為什麼發生這個錯誤？」(e.g., Exception Stack Trace)。這是 `Log Analytics Workspace` 與 `KQL` 的主戰場。
- **Traces (追蹤)**：請求在分散式系統中的流動路徑。用於回答「哪個微服務拖慢了請求？」(e.g., End-to-End Transaction)。主要由 `Application Insights` 實現。

### 2. The KQL Pipeline (KQL 處理流)
將 KQL 視為 SQL 與 Unix Pipe (`|`) 的結合體。
- **Input**: 一個巨大的資料表（如 `AppRequests` 或 `Heartbeat`）。
- **Pipe (`|`)**: 資料流動的方向，每一層過濾或轉換後的結果，傳給下一層。
- **Output**: 最終的圖表、警報觸發條件或診斷結果。

> **Key Takeaway**: 不要把 Log Analytics 當作靜態的檔案儲存，請將其視為一個**唯讀的、針對時間序列優化的大數據資料庫**。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Workspace Strategy: Centralize vs. Segregate
**集中化策略（Centralized）是多數情況下的最佳解。**
- **Pattern**: 盡量將同一 Region、同一環境（如 Production）的資源 Log 送往同一個 Log Analytics Workspace。
- **Why**: KQL 跨 Workspace 查詢（Cross-workspace query）雖然可行但語法繁瑣且效能較差。集中化讓你能輕鬆關聯（Join）基礎設施（VM）與應用程式（App Service）的 Log。

### 2. Structured Logging & Custom Dimensions
**結構化日誌是 KQL 的靈魂。**
- **Pattern**: 在程式碼中不要只寫 `Log.Error("Order 123 failed")`，而要使用結構化屬性。
- **Practice**: 將關鍵商業資訊（OrderID, UserID, TenantID）放入 `CustomDimensions`。
- **KQL Benefit**: 你可以直接查詢 `| where tostring(CustomDimensions.TenantID) == "T001"`，而不是用低效的 `| where Message contains "T001"`。

### 3. The "Let" Statement for Readability
**使用 `let` 提升查詢可讀性與重用性。**
- **Pattern**: 將複雜的時間範圍、常數或子查詢定義在最上方。
```kusto
let timeRange = 24h;
let errorThreshold = 5;
AppRequests
| where TimeGenerated > ago(timeRange)
| where Success == false
| count
```

### 4. Dynamic Alerting (動態警報)
- **Pattern**: 避免使用靜態閾值（例如 CPU > 80%），改用 Azure Monitor 的動態閾值（Dynamic Thresholds）。
- **Why**: 系統負載有週期性（例如週一早上流量大），動態閾值能利用 ML 自動適應基線，減少誤報（False Positives）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Search *" Trap (盲目搜索陷阱)
- **Anti-pattern**: 使用 `search "error"` 或 `search *` 開頭。
- **Consequence**: 極度消耗效能且掃描成本高昂。這會掃描 Workspace 內**所有**資料表的所有欄位。
- **Fix**: 永遠先指定 Table，再指定時間。
  - ✅ `AppTraces | where TimeGenerated > ago(1h) | where Message has "error"`

### 2. Ignoring Retention Costs (忽視保留成本)
- **Anti-pattern**: 將所有 Log 保留 730 天，且包含大量 Debug 層級資訊。
- **Consequence**: 儲存成本可能比運算資源還貴。
- **Fix**:
  - 設定適當的 Retention Policy（一般 Production 30-90 天）。
  - 使用 **Data Collection Rules (DCR)** 在 Log 進入 Workspace 前過濾掉不必要的 Verbose Log。

### 3. Client-Side Sampling Overkill (過度採樣)
- **Anti-pattern**: 在 Application Insights 開啟 100% 的採樣率（Sampling），即使在高流量系統中。
- **Consequence**: Log 爆量導致成本失控，或觸發 Daily Cap 導致監控中斷。
- **Fix**: 使用 Adaptive Sampling，讓系統自動保留統計顯著的樣本，同時保留失敗請求（Failed Requests）的完整細節。

### 4. Parsing at Query Time (查詢時解析)
- **Anti-pattern**: 依賴 `parse_json()` 或 `extract()` 在查詢時處理非結構化字串。
- **Consequence**: 查詢速度極慢。
- **Fix**: 盡量在寫入時（Log Ingestion）就結構化資料。如果必須解析，請在查詢的前段先過濾資料量。

---

## Checklists & workflows｜檢查清單與流程

### Troubleshooting Workflow (故障排除標準流程)

1. **Scope & Time (範圍與時間)**
   - [ ] 確定問題發生的時間區間（UTC vs Local Time）。
   - [ ] 鎖定受影響的 Resource 或 Service。
2. **High-Level Metrics (高層指標)**
   - [ ] 檢查 `AppRequests` 的 `Duration` (P95/P99) 與 `Success == false` 的比例。
   - [ ] 檢查 `Perf` (CPU/Memory) 是否有異常峰值。
3. **Drill Down with KQL (深入挖掘)**
   - [ ] 使用 `AppExceptions` 查看具體錯誤堆疊。
   - [ ] 使用 `AppDependencies` 檢查是否是下游服務（SQL, Redis, External API）變慢。
4. **Correlation (關聯分析)**
   - [ ] 複製 `OperationId`，查詢該次 Transaction 的所有 Log (`union * | where OperationId == "..."`)。

### Cost Optimization Checklist (成本優化檢核)

- [ ] **Usage Analysis**: 執行 KQL 查詢 `Usage | summarize Sum=sum(Quantity) by DataType` 找出最佔空間的資料表。
- [ ] **Retention Policy**: 確認 Workspace 的資料保留天數是否符合合規需求，避免過長。
- [ ] **Commitment Tiers**: 若每日 Log 量大於 100GB，檢查是否已啟用 Commitment Tiers 以獲得折扣。
- [ ] **Diagnostic Settings**: 檢查 Azure Resources (如 SQL, KeyVault) 的診斷設定，是否只勾選了需要的 Log Category。

---

## Real-world examples｜實戰案例

### Example 1: Performance Bottleneck Analysis (效能瓶頸分析)
**情境**：使用者回報 API 回應變慢，你需要找出是程式碼慢還是資料庫慢。

```kusto
// 結合 Request 與 Dependency 分析
let start = ago(1h);
AppRequests
| where TimeGenerated > start
| where Success == true
| where Duration > 1000 // 找出超過 1秒 的請求
| project TimeGenerated, OperationId, RequestName = Name, RequestDuration = Duration
| join kind=inner (
    AppDependencies
    | where TimeGenerated > start
    | where Duration > 500 // 下游依賴超過 0.5秒
    | project OperationId, DependencyType, Target, DependencyDuration = Duration
) on OperationId
| project TimeGenerated, RequestName, RequestDuration, DependencyType, Target, DependencyDuration
| order by RequestDuration desc
```
*說明：這段 KQL 幫你直接抓出「慢的請求」中，具體是「哪個下游服務」拖慢了速度。*

### Example 2: Who Deleted the Resource? (審計追蹤)
**情境**：某個 VM 突然消失了，需要找出是誰執行的刪除操作。

```kusto
AzureActivity
| where TimeGenerated > ago(7d)
| where OperationNameValue endswith "delete" 
| where ActivityStatusValue == "Success"
| project TimeGenerated, Caller, OperationNameValue, ResourceId, ResourceGroup
| order by TimeGenerated desc
```
*說明：利用 `AzureActivity` 表查詢管理層面的操作紀錄。*

### Example 3: Log Volume Cost Analysis (日誌成本分析)
**情境**：Log Analytics 帳單暴增，需要找出罪魁禍首。

```kusto
Usage
| where TimeGenerated > ago(24h)
| summarize DataSizeMB = sum(Quantity) by DataType
| extend CostEstimation = DataSizeMB * 0.0023 // 假設費率，僅供參考
| order by DataSizeMB desc
| render piechart 
```
*說明：快速視覺化哪種類型的 Log (DataType) 佔用了最多容量。*

### Example 4: Intelligent Alert Logic (智慧警報邏輯)
**情境**：每 5 分鐘檢查一次，如果過去 5 分鐘內的錯誤率超過 10%，且請求總數大於 50 才報警（避免流量低時的誤報）。

```kusto
let timeWindow = 5m;
AppRequests
| where TimeGenerated > ago(timeWindow)
| summarize 
    TotalRequests = count(), 
    FailedRequests = countif(Success == false)
| extend FailureRate = 100.0 * FailedRequests / TotalRequests
| where TotalRequests > 50 and FailureRate > 10
```
*說明：這是一個高品質的警報查詢，過濾了雜訊（低流量時的波動）。*