# 成本優化與 FinOps 實踐 / Cost Optimization & FinOps Practices

## Mental model｜心智模型

### 1. 雲端帳單是架構決策的副作用
**Cloud bill is a side effect of architectural decisions.**
不要將成本視為每個月底由財務部門處理的「行政事務」，而應視為工程師在設計系統時的「非功能性需求 (Non-functional Requirement)」。如同效能 (Performance) 與安全性 (Security)，成本 (Cost) 必須在寫下第一行程式碼前就被考慮。

### 2. 從 CapEx 轉向 OpEx 的思維
**Shift from CapEx (Capital Expenditure) to OpEx (Operational Expenditure).**
在地端機房，資源是「沈沒成本 (Sunk Cost)」，機器買了閒置也是浪費；在 AWS，資源是「水電費」，不用時關閉才是常態。
- **Visibility (可視性)**：你無法優化你看不到的東西。Tagging 是 FinOps 的基礎建設。
- **Accountability (當責性)**：開發團隊應該對自己服務的成本負責，而不是由維運團隊 (Ops) 概括承受。

### 3. 單位經濟學 (Unit Economics)
不要只看「總成本是否增加」，而要看「每筆交易/每個用戶的成本是否合理」。如果你的 AWS 帳單增加 50%，但業務量成長了 200%，這其實是成功的 FinOps。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 採購模型的「千層蛋糕」策略 (The Layered Purchasing Strategy)
針對運算資源 (EC2, Fargate, Lambda)，應採用分層採購策略：
- **底層 (Base Load)**：針對 24/7 運行的穩定負載，購買 **Compute Savings Plans**（比 Reserved Instances 更靈活）。目標覆蓋率約 70-80%。
- **中層 (Predictable Spikes)**：針對可預測的週期性負載（如早九晚五），使用 **Auto Scaling Group** 搭配 **Scheduled Scaling**。
- **頂層 (Stateless/Fault-tolerant)**：針對批次處理、CI/CD Agents 或可容忍中斷的服務，使用 **Spot Instances**（最高可省 90%）。
- **溢出 (Unpredictable)**：僅針對突發流量使用 **On-Demand**。

### 2. 強制標籤策略 (Enforced Tagging Strategy)
沒有標籤的資源就是「孤兒資源」。
- **實作方式**：使用 AWS Organizations 的 **Tag Policies** 或 IaC (Terraform/CDK) 強制執行。
- **必備標籤**：
  - `CostCenter`: 誰付錢？
  - `Environment`: `prod`, `staging`, `dev`。
  - `Service`: 微服務名稱。
  - `Owner`: 聯絡人。

### 3. 儲存分級與生命週期 (Storage Tiering & Lifecycle)
- **S3**：啟用 **S3 Intelligent-Tiering**。這是最簡單的「設定後不理 (Set-and-forget)」優化方式，它會自動將不常存取的物件移至低成本層級。
- **EBS**：
  - 將所有 `gp2` 磁碟區升級為 `gp3`。`gp3` 成本更低且效能基準更好（不依賴 burst balance）。
  - 刪除未掛載 (Unattached) 的 EBS Volumes。

### 4. 數據傳輸優化 (Data Transfer Optimization)
AWS 的流量費用往往是隱形殺手。
- **VPC Endpoints**：存取 S3/DynamoDB 時，使用 Gateway Endpoints 避免流量繞經 NAT Gateway（NAT Gateway 每 GB 都要收費）。
- **Availability Zones**：盡量保持流量在同一 AZ 內。跨 AZ 傳輸是有費用的。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. NAT Gateway 陷阱 (The NAT Gateway Trap)
**現象**：帳單中 `EC2-Other` 類別異常高。
**原因**：大量的 Lambda 或 EC2 在私有子網 (Private Subnet) 透過 NAT Gateway 下載 Docker Image 或上傳大量數據到 S3。
**解法**：使用 VPC Endpoints (Gateway type for S3/DynamoDB is free; Interface type costs money but is cheaper than NAT for high throughput)。

### 2. 過早購買承諾 (Premature Commitment)
**現象**：專案初期就購買 3 年全額預付的 RI 或 Savings Plans。
**後果**：架構重構（例如從 EC2 轉向 Serverless，或更換 Instance Family）時，預購的容量變成浪費。
**建議**：先用 On-Demand 跑 1-3 個月，確定基準線 (Baseline) 後再購買 Savings Plans。

### 3. 殭屍資源 (Zombie Resources)
**現象**：開發環境充滿了遺留的資源。
- **未釋放的 Elastic IP (EIP)**：EIP 如果沒綁定正在執行的實例，AWS 會收費。
- **老舊 Snapshots**：自動備份腳本沒有設定過期刪除，導致數年的 EBS Snapshots 累積。
- **閒置的 Load Balancers**：沒有 Target 的 ELB 依然會按小時計費。

### 4. CloudWatch Logs 暴漲
**現象**：Log 費用超過了運算費用。
**原因**：開啟了過於詳細的 Debug level logs，且沒有設定 Retention Policy（預設是永久保存）。
**解法**：設定 Log Group 的 Retention（如 14 天），並將長期歸檔導出至 S3 Glacier。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Compute Pricing Strategy
1. **Is it stateful? (是否有狀態)**
   - Yes -> On-Demand or Savings Plans.
   - No -> Go to step 2.
2. **Can it handle interruption? (能否容忍中斷)**
   - Yes -> **Spot Instances**.
   - No -> Go to step 3.
3. **Is the usage steady 24/7? (是否全天候穩定運行)**
   - Yes -> **Savings Plans (Compute)**.
   - No -> **On-Demand** (controlled by Auto Scaling).

### Monthly FinOps Checklist
- [ ] **Review Cost Anomalies**: 檢查 AWS Cost Anomaly Detection 的警報。
- [ ] **Rightsizing**: 查看 AWS Compute Optimizer 建議，縮減過度配置的 EC2/RDS。
- [ ] **Savings Plans Coverage**: 覆蓋率是否低於 70%？是否需要加購？
- [ ] **Unused Resources**:
    - [ ] 刪除 Unattached EBS Volumes。
    - [ ] 釋放 Unassociated Elastic IPs。
    - [ ] 刪除 Idle Load Balancers。
    - [ ] 清理 Old Snapshots / AMI。
- [ ] **Storage Check**: 確認 S3 Bucket 是否啟用了 Lifecycle Policy 或 Intelligent-Tiering。
- [ ] **Database**: 檢查 RDS 是否有閒置連接，非生產環境是否在非工作時間關閉。

---

## Real-world examples｜實戰案例

### Case 1: The "Dev Environment" Waste
**情境**：開發團隊有 20 台 EC2 用於測試，每個月帳單居高不下，但工程師只有平日 10:00-19:00 會用到。
**解決方案**：
實作 **AWS Instance Scheduler** (或自製 Lambda + EventBridge)。
- 設定 Tag `Schedule: OfficeHours`。
- 自動在平日 19:00 關機，平日 09:00 開機。
- **結果**：每週運行時間從 168 小時降至 50 小時，成本節省約 **70%**。

### Case 2: Spot Instances for Batch Processing
**情境**：一家數據分析公司需要處理大量的影像轉檔，原本使用 On-Demand `c5.2xlarge`，成本極高。
**解決方案**：
- 將轉檔程式容器化 (Dockerized)。
- 使用 **AWS Batch** 或 **EKS** 搭配 **Spot Fleet**。
- 設定 `MixedInstancesPolicy`，允許使用多種 Instance Types (如 `c5.2xlarge`, `c5a.2xlarge`, `m5.2xlarge`) 以分散 Spot Pool 耗盡的風險。
- **結果**：成本降低 **60-80%**，且因為 Spot 便宜，可以開更多機器並行處理，反而縮短了作業時間。

### Case 3: The "Cross-AZ" Data Transfer Surprise
**情境**：Web Server (AZ-a) 頻繁呼叫 Database (AZ-b)，產生巨額 "Data Transfer Regional" 費用。
**解決方案**：
- 架構調整：確保應用程式優先連線到「同一 AZ」的 Read Replica。
- 若無法避免跨 AZ (如 High Availability 需求)，評估是否該流量真的需要即時同步，或可改用 S3 + Batch 處理（S3 內部流量較便宜）。
- **結果**：透過調整連線字串與讀寫分離策略，消除了大部分跨 AZ 流量費用。