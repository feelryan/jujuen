# 高可用性與災難復原實戰 / High Availability (HA) & Disaster Recovery (DR)

## Mental model｜心智模型

在設計 AWS 架構時，必須接受一個核心事實：「**Everything fails, all the time** (所有東西隨時都可能壞掉)」。HA 與 DR 並不是為了防止故障發生，而是為了在故障發生時，系統能夠「存活」或「重生」。

### 1. 故障半徑 (Blast Radius) 與隔離層級
不要將 HA 與 DR 混為一談，請依照故障的層級來思考防禦策略：
- **Component Level (Instance/Container)**: 單台機器掛掉。
  - **解法**：Health Checks + Auto Scaling (自動替換)。
- **Zone Level (Availability Zone)**: 整個機房斷電或網路中斷。
  - **解法**：Multi-AZ 架構 (HA 的核心)。
- **Region Level (Geographical)**: 發生地震、大規模光纖切斷或 AWS Region 級別的控制面故障。
  - **解法**：Multi-Region Replication (DR 的核心)。

### 2. RTO 與 RPO 的權衡矩陣
DR 不是開關，而是一個光譜。你必須與業務端（Business Stakeholders）確認以下兩個指標，才能決定技術架構：
- **RPO (Recovery Point Objective)**: 你能容忍遺失多少**資料**？（例如：最多遺失 15 分鐘前的資料）。
- **RTO (Recovery Time Objective)**: 你能容忍系統**停機**多久？（例如：必須在 4 小時內恢復服務）。

> **Mental Shortcut**: RTO/RPO 越接近零，架構越複雜，成本呈指數級上升。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. High Availability (HA) Patterns
HA 的目標是 **Zero Downtime** 或使用者無感知的故障轉移。

- **Stateless Compute (無狀態運算)**:
  - 應用程式層（EC2/Containers/Lambda）不應儲存 Session 或檔案。
  - **實作**：使用 ELB 分發流量至跨多個 AZ 的 Auto Scaling Group。Session 存入 ElastiCache (Redis)，檔案存入 S3。
- **Storage Redundancy (儲存冗餘)**:
  - **RDS/Aurora**: 啟用 `Multi-AZ`。當 Primary DB 故障，AWS 會自動更改 DNS 指向 Standby，應用程式僅需重連。
  - **S3**: 標準 S3 儲存類別預設即為 Multi-AZ (11 個 9 的持久性)。

### 2. Disaster Recovery (DR) Strategies
DR 的目標是跨 Region 的災難復原。依照 RTO/RPO 要求由寬鬆到嚴格分為四種模式：

#### A. Backup and Restore (備份與還原)
- **適用場景**: RTO/RPO > 24小時，成本敏感型專案。
- **實作**: 使用 **AWS Backup** 定期將 EBS Snapshots、RDS Backups 複製到另一個 Region。災難發生時，手動在新 Region 啟動資源。

#### B. Pilot Light (長明燈模式)
- **適用場景**: RTO 數小時，核心資料不能丟，但運算資源可以慢慢開。
- **實作**:
  - **Data**: 在 DR Region 配置 RDS Read Replica 或 DynamoDB Global Tables (資料即時同步)。
  - **Compute**: 應用程式伺服器處於「關閉」或「未部署」狀態，僅保留 IaC 腳本或 AMI。
  - **Trigger**: 災難發生時，將 Read Replica 升級為 Primary，並透過 Auto Scaling 啟動運算資源。

#### C. Warm Standby (暖備援)
- **適用場景**: RTO 分鐘級，業務關鍵系統。
- **實作**:
  - DR Region 擁有一套「縮小版」的完整架構（例如 Production 有 10 台機器，DR 只開 1 台）。
  - 災難發生時，透過 Route 53 切換流量，並迅速 Scale-out DR Region 的機器數量。

#### D. Multi-Region Active-Active (雙活/多活)
- **適用場景**: RTO/RPO ≈ 0，全球級服務，預算無上限。
- **實作**:
  - **Traffic**: Route 53 使用 Latency 或 Geolocation 路由策略，同時將流量打入兩個 Region。
  - **Data**: 使用 DynamoDB Global Tables 或 Aurora Global Database 進行雙向/多向同步。
  - **複雜度**: 極高。需處理資料衝突 (Conflict Resolution) 與等冪性 (Idempotency)。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Region-Specific" Hardcoding (寫死 Region 依賴)
- **Bad Smell**: 程式碼中寫死 `us-east-1` 的 S3 Endpoint 或 ARN。
- **後果**: 當你需要 Failover 到 `us-west-2` 時，程式碼必須重新 Build 和 Deploy，導致 RTO 暴增。
- **修正**: 使用環境變數或 Service Discovery 注入 Region 資訊。

### 2. Ignoring Soft Dependencies (忽略軟依賴)
- **Bad Smell**: 你的 App 在 DR Region 啟動了，但它依賴的第三方授權服務、CI/CD Pipeline 或 Docker Registry 卻只在原 Region 運作。
- **後果**: 系統看似恢復，但無法登入或無法發布緊急修補。
- **修正**: 確保所有依賴服務（包含 Secrets Manager、Parameter Store）都已複製到 DR Region。

### 3. Split-Brain Syndrome (腦裂)
- **Bad Smell**: 在 Active-Active 架構中，網路分區導致兩個 Region 的資料庫同時接受寫入，且無法同步。
- **後果**: 資料永久不一致或遺失。
- **修正**: 實作分散式鎖 (Distributed Locking) 或使用支援 Global Write 的資料庫 (如 DynamoDB Global Tables 的 Last Writer Wins 策略)，並在應用層設計衝突解決機制。

### 4. The "Untested" Backup (薛丁格的備份)
- **Bad Smell**: 設定了自動備份但從未嘗試還原。
- **後果**: 真正災難發生時，才發現備份檔損壞或加密金鑰 (KMS Key) 在 DR Region 無法解密。
- **修正**: 跨 Region 複製 Backup 時，務必連同 KMS Key 一起處理，並定期演練還原。

---

## Checklists & workflows｜檢查清單與流程

### Decision Workflow: Choosing a DR Strategy
1. **定義需求**: 詢問業務方 "如果系統停機 1 小時會損失多少錢？"
2. **評估資料**: 資料庫引擎是否支援 Cross-Region Replication？
3. **選擇模式**:
   - 損失 < 架構成本 $\rightarrow$ **Backup & Restore**
   - 需快速恢復資料但可容忍啟動時間 $\rightarrow$ **Pilot Light**
   - 需快速切換且流量可預測 $\rightarrow$ **Warm Standby**
   - 零停機需求 $\rightarrow$ **Active-Active**

### Pre-Flight Checklist for Production
- [ ] **SPOF Analysis**: 檢查架構中是否有單點故障 (Single Point of Failure)？(e.g., 單一 NAT Gateway, 單一 Bastion Host)。
- [ ] **Multi-AZ Enabled**: 確認 RDS, ElastiCache, ALB, ASG 都已啟用 Multi-AZ。
- [ ] **Backup Policy**: AWS Backup 策略已設定，且包含 Cross-Region Copy。
- [ ] **KMS Strategy**: 用於加密備份的 KMS Key 是否為 Multi-Region Key，或已在 DR Region 建立對應 Key？
- [ ] **Route 53 TTL**: DNS TTL 是否設定得夠短 (e.g., 60s) 以便快速切換？
- [ ] **Service Quotas**: DR Region 的 vCPU Quota 是否足夠支撐 Production 流量？(這常被忽略！)

### Failover Drill (Game Day) Routine
1. **模擬故障**: 關閉 Primary Region 的 RDS 或阻斷特定 AZ 的網路 (使用 AWS FIS)。
2. **觸發切換**: 執行 DR 腳本 (Promote Read Replica, Update DNS)。
3. **驗證服務**: 檢查 DR Region 的應用程式是否能正常讀寫資料。
4. **測量指標**: 紀錄實際 RTO 與 RPO 是否符合預期。
5. **回切 (Failback)**: 演練如何將流量與新數據安全地切回主 Region。

---

## Real-world examples｜實戰案例

### Scenario: Pilot Light for a SaaS Platform
**背景**: 一個 B2B SaaS 平台，主要運行在 `ap-northeast-1` (Tokyo)。
**需求**: RPO < 5 min, RTO < 30 min。
**架構設計**:

1.  **Data Layer**:
    - Primary: Amazon Aurora (MySQL) in Tokyo.
    - DR: 建立一個 **Cross-Region Read Replica** 在 `ap-southeast-1` (Singapore)。
    - S3: 開啟 Cross-Region Replication (CRR) 同步使用者上傳的文件到 Singapore。

2.  **Compute Layer**:
    - Tokyo: 完整的 ASG + ALB + ECS Cluster。
    - Singapore: 僅建立 VPC、Security Groups 和一個 **容量為 0** 的 ASG。ECS Task Definition 與 Container Images 已同步至 Singapore 的 ECR。

3.  **Failover Process (Automation)**:
    - 監控系統偵測到 Tokyo Region 嚴重故障。
    - Ops 團隊執行 `failover-to-sg.sh` 腳本：
        1.  呼叫 RDS API 將 Singapore Replica 升級為 Standalone Cluster。
        2.  更新 Parameter Store 中的 DB Endpoint。
        3.  將 Singapore ASG 的 Desired Capacity 從 0 調整為 10。
        4.  更新 Route 53 DNS Record，將流量權重切換至 Singapore ALB。

### Scenario: Handling "Thundering Herd" after Recovery
**情境**: 當 DR Region 啟動時，瞬間湧入大量積壓的流量，導致剛啟動的系統直接崩潰（Thundering Herd Problem）。
**實戰技巧**:
- **預熱 (Pre-warming)**: 如果使用 ALB，需聯絡 AWS Support 預熱 Load Balancer（針對極大流量）。
- **指數退避 (Exponential Backoff)**: 確保 Client 端 (Mobile App/Frontend) 的重試機制包含 Jitter (隨機延遲)，避免所有客戶端在同一秒發送請求。
- **降級模式 (Degradation)**: 在 DR 模式下，暫時關閉非核心功能（如報表生成、推薦系統），將資源留給核心交易流程。