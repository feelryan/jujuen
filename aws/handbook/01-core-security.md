# AWS 架構核心與 IAM 安全模型 / Well-Architected Framework & IAM Security Model

## Mental model｜心智模型

在進入 AWS 世界之前，必須重塑對「安全邊界」的認知。

### 1. Identity is the New Perimeter (身分即邊界)
在傳統地端機房，我們依賴防火牆（Firewall）和 VPN 來建立安全邊界。但在 AWS 雲端環境中，資源可能遍布全球，**IAM (Identity and Access Management)** 才是真正的第一道防線。
- **Mental Shift**: 不要只問「這個 IP 能不能連線？」，要問「這個 **Principal (身分)** 是否擁有對該 **Resource (資源)** 執行 **Action (動作)** 的權限，且符合 **Condition (條件)**？」

### 2. The Shared Responsibility Model (責任共擔模型)
這不是法律免責聲明，而是工程邊界劃分。
- **AWS 的責任 (Security of the Cloud)**：AWS 負責實體資料中心、硬體、虛擬化層的網路隔離。你不需要擔心有人拿大錘砸爛你的伺服器。
- **你的責任 (Security in the Cloud)**：你負責作業系統補丁、防火牆設定 (Security Groups)、資料加密，以及最重要的——**誰有權限存取什麼**。
- **關鍵點**：如果你把 S3 Bucket 設為 Public Read 導致資料外洩，這是你的責任，不是 AWS 的漏洞。

### 3. Blast Radius Reduction (爆炸半徑最小化)
將 AWS 帳號視為一個「隔離艙」。
- 不要將 Production (生產環境) 和 Development (開發環境) 放在同一個 AWS Account。
- 使用 **AWS Organizations** 建立多帳號架構，當一個帳號被入侵或發生誤操作時，損害被限制在該帳號內，不會波及整個企業。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Multi-Account Strategy (多帳號策略)
不要試圖在一個 AWS 帳號中用 IAM Policy 和 Tag 來隔離所有環境。
- **Landing Zone**: 使用 AWS Control Tower 或 Terraform 建立標準化的多帳號結構。
- **OU (Organizational Units) Structure**:
  - `Security OU`: 存放 Log Archive 和 Security Tooling (GuardDuty, Security Hub)。
  - `Workload OU`: 依環境區分 `Prod`, `Staging`, `Dev` 帳號。
  - `Sandbox OU`: 給工程師自由實驗的區域，設有嚴格的預算上限。

### 2. Human vs. Machine Access (人類與機器存取分離)
- **Humans (Workforce)**: **嚴禁使用 IAM User + Long-term Access Keys**。
  - **Pattern**: 使用 **IAM Identity Center (舊稱 AWS SSO)**。工程師透過公司 Email/MFA 登入，獲取短期的 Session Token 來操作 AWS Console 或 CLI。
- **Machines (Workloads)**: 使用 **IAM Roles**。
  - **Pattern**: EC2 使用 Instance Profile，Lambda 使用 Execution Role，EKS 使用 IRSA (IAM Roles for Service Accounts)。永遠不要將 Access Key 硬寫在程式碼或 Config 檔中。

### 3. Policy Structure & Conditions (策略結構與條件)
一個成熟的 IAM Policy 必須包含 `Condition` 區塊。
- **Pattern**: 限制存取來源。
  ```json
  "Condition": {
      "IpAddress": { "aws:SourceIp": "203.0.113.0/24" },
      "StringEquals": { "aws:RequestedRegion": "ap-northeast-1" }
  }
  ```
- **Pattern**: 屬性存取控制 (ABAC)。使用 Tags 來控制權限，例如 `Condition: { "StringEquals": { "aws:ResourceTag/Environment": "${aws:PrincipalTag/Environment}" } }`。

### 4. Cross-Account Access via AssumeRole (跨帳號角色扮演)
當 CI/CD Pipeline (位於 Tooling 帳號) 需要部署到 Prod 帳號時：
- 不要在 Prod 帳號建立 IAM User 給 CI/CD 用。
- **Pattern**: 在 Prod 帳號建立一個 Role (e.g., `DeployerRole`)，並設定 Trust Relationship 允許 Tooling 帳號的特定 Role 進行 `sts:AssumeRole`。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Root" User Trap (Root 帳號陷阱)
- **Anti-pattern**: 使用 Root Email 登入 AWS Console 進行日常維運。
- **Risk**: Root 擁有無限權限且無法被 Policy 限制。一旦 Root 憑證外洩，帳號將被徹底綁架（包含刪除你的備份和信用卡盜刷）。
- **Fix**: 註冊完 AWS 帳號後，設定 MFA，鎖進保險箱，只在極端情況（如帳務問題）下使用。

### 2. The "Star" Policy (星號策略)
- **Anti-pattern**: 開發時為了方便，給予 `Action: "*"` 或 `Resource: "*"`。
  - `AdministratorAccess` 給開發者。
  - `s3:*` 給 EC2。
- **Risk**: 這違反了最小權限原則 (Least Privilege)。如果該 EC2 被植入挖礦程式或勒索軟體，攻擊者將擁有整個 S3 的刪除權限。

### 3. Inline Policies Everywhere (隨處可見的內嵌策略)
- **Anti-pattern**: 直接將 Policy 寫死在 User 或 Role 上 (Inline)，而不是建立 Managed Policy。
- **Pitfall**: 難以維護、無法重用、難以進行版本控制與變更追蹤。
- **Fix**: 使用 **Customer Managed Policies**，並透過 IaC (Terraform/CloudFormation) 管理。

### 4. Hardcoded Credentials (硬編碼憑證)
- **Anti-pattern**: 將 `AWS_ACCESS_KEY_ID` 和 `SECRET_ACCESS_KEY` 寫在 `.env` 檔並 commit 到 Git Repo。
- **Consequence**: 這是 AWS 帳號被駭的最常見原因。Bot 會在幾秒鐘內掃描到並開始開啟幾百台 GPU 機器挖礦。
- **Fix**: 使用 `git-secrets` 或 `trufflehog` 掃描 Repo；本地開發使用 `~/.aws/credentials` 或 `aws sso login`。

---

## Checklists & workflows｜檢查清單與流程

### Day 1 Security Checklist (新帳號啟用清單)
- [ ] **Root Account**: 啟用 MFA (硬體 Key 或 Authenticator App)，刪除 Root Access Keys。
- [ ] **CloudTrail**: 確保 CloudTrail 已啟用並將 Log 傳送到獨立的 S3 Bucket (Log Archive)。
- [ ] **Billing**: 設定 AWS Budgets 預算警報 (例如：超過 $10 就寄信通知)，避免意外破產。
- [ ] **GuardDuty**: 在所有 Region 啟用 GuardDuty (威脅偵測)。
- [ ] **IAM**: 刪除預設未使用的 IAM User，設定強密碼策略 (Password Policy)。
- [ ] **S3 Block Public Access**: 在 Account Level 啟用 "Block Public Access" 設定。

### IAM Policy Design Workflow (權限設計流程)
1. **Start Broad (but safe)**: 先使用 AWS Managed Policy (如 `AmazonS3ReadOnlyAccess`) 測試連通性。
2. **Narrow Down**: 使用 **IAM Access Analyzer** 根據實際 CloudTrail 紀錄生成 Policy。
3. **Add Conditions**: 加入 `SourceVpce` (限制只能從 VPC 內存取) 或 `SourceIp`。
4. **Review**: 透過 IaC Code Review 流程確認沒有 `*` 權限。

---

## Real-world examples｜實戰案例

### Scenario: Secure S3 Access for a Web Application
**情境**：一個跑在 EC2 上的 Web App 需要讀寫 S3 Bucket (`my-app-data`) 中的圖片。

#### ❌ Bad Practice (Do NOT do this)
1. 在 IAM Console 建立一個 User `web-app-user`。
2. 給予 `AmazonS3FullAccess` 權限。
3. 產生 Access Key / Secret Key。
4. 將 Key 寫在 EC2 的 `/var/www/html/config.php` 裡。

#### ✅ Best Practice (Do this)
1. **Create Policy**: 建立一個最小權限的 Policy。
   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": ["s3:PutObject", "s3:GetObject"],
               "Resource": "arn:aws:s3:::my-app-data/*"
           }
       ]
   }
   ```
2. **Create Role**: 建立一個 IAM Role `WebAppRole`，將上述 Policy 附加給它。
3. **Trust Policy**: 設定 Trust Relationship 允許 `ec2.amazonaws.com` 扮演此角色。
4. **Instance Profile**: 將此 Role 綁定到 EC2 Instance Profile。
5. **Code**: 程式碼中使用 AWS SDK (boto3, AWS SDK for Java/Node.js)。SDK 會自動從 EC2 Metadata Service 取得暫時性憑證，完全不需要管理 Key。

### Scenario: Cross-Account Deployment (CI/CD)
**情境**：GitHub Actions 需要部署代碼到 AWS `Prod` 帳號。

1. **Identity Provider**: 在 AWS `Prod` 帳號的 IAM 中設定 **OIDC Identity Provider** (指向 `token.actions.githubusercontent.com`)。
2. **IAM Role**: 建立 `GitHubDeployRole`。
3. **Trust Policy**: 設定僅允許特定的 GitHub Repo (`repo:my-org/my-repo:ref:refs/heads/main`) 扮演此 Role。
4. **Workflow**: GitHub Actions 執行時，使用 `aws-actions/configure-aws-credentials` 透過 OIDC 取得短效 Token 進行部署。
   - **優點**: GitHub 裡不需要儲存任何 AWS Secret Key。