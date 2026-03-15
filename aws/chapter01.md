# 1. 前言與學習目標 (Introduction & Learning Objectives)

作為資深工程師，你可能已經熟練地啟動 EC2 或配置 RDS。然而，在 System Design 面試或大規模生產環境中，挑戰往往不在於「如何使用服務」，而在於「如何正確地組合服務」以滿足安全性、成本與可靠性的權衡。本章將帶你超越單一服務的操作，進入架構師的視角。

As a Senior Engineer, you are likely proficient in launching EC2 instances or configuring RDS. However, in System Design interviews or large-scale production environments, the challenge lies not in "how to use a service," but in "how to orchestrate services correctly" to balance security, cost, and reliability. This chapter takes you beyond individual service operations into the architect's perspective.

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **內化 Well-Architected Framework**：不只是背誦六大支柱，而是能根據業務需求（如 Fintech 重視安全、Startup 重視速度）進行架構取捨（Trade-offs）。
    **Internalize the Well-Architected Framework**: Go beyond memorizing the six pillars; learn to make architectural trade-offs based on business needs (e.g., Fintech prioritizing security vs. Startups prioritizing speed).
2.  **掌握 IAM 決策邏輯**：精確解釋 IAM Policy、Resource Policy、Permissions Boundary 與 SCP（Service Control Policy）的優先順序與評估流程。
    **Master IAM Evaluation Logic**: Accurately explain the precedence and evaluation flow of IAM Policies, Resource Policies, Permissions Boundaries, and SCPs (Service Control Policies).
3.  **設計多帳號策略（Multi-Account Strategy）**：理解為何單一帳號是反模式（Anti-pattern），並能設計基於 AWS Organizations 的隔離架構以限制爆炸半徑（Blast Radius）。
    **Design Multi-Account Strategy**: Understand why a single account is an anti-pattern and be able to design an isolation architecture based on AWS Organizations to limit the blast radius.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 AWS Well-Architected Framework：架構的六邊形戰士
## 2.1 AWS Well-Architected Framework: The Hexagonal Warrior of Architecture

不要將 Well-Architected Framework 視為一份靜態的檢查清單，請將其視為一個**平衡計分卡（Balanced Scorecard）**。在系統設計中，你通常無法同時滿足所有支柱，資深工程師的價值在於決定「現在該犧牲哪一個」。

Do not view the Well-Architected Framework as a static checklist; treat it as a **Balanced Scorecard**. In system design, you often cannot satisfy all pillars simultaneously. The value of a Senior Engineer lies in deciding "which one to sacrifice for now."

1.  **Operational Excellence（卓越營運）**: Infrastructure as Code (IaC), Observability, CI/CD.
2.  **Security（安全性）**: Identity, Data protection, Incident response.
3.  **Reliability（可靠性）**: Fault tolerance, Recovery planning, Self-healing.
4.  **Performance Efficiency（效能效率）**: Right-sizing, Serverless, Latency optimization.
5.  **Cost Optimization（成本優化）**: Spot instances, Reserved Instances, Analyzing spend.
6.  **Sustainability（永續性）**: Minimizing environmental impact, Hardware utilization.

## 2.2 IAM 評估邏輯：漏斗模型
## 2.2 IAM Evaluation Logic: The Funnel Model

許多工程師對 IAM 的理解僅停留在「給予權限」。在資深層級，你需要理解 AWS 如何決定「拒絕」或「允許」。請建立以下心智模型：

Many engineers understand IAM only as "granting permissions." At a senior level, you need to understand how AWS decides to "Deny" or "Allow." Establish the following mental model:

**決策流程 (Decision Flow):**
1.  **Explicit Deny（顯式拒絕）**: 這是最高優先級。如果在任何適用的 Policy（包含 SCP）中看到 `Deny`，請求立即被拒絕。
    **Explicit Deny**: This is the highest priority. If a `Deny` is found in any applicable policy (including SCPs), the request is immediately rejected.
2.  **SCP / Permissions Boundary（邊界檢查）**: 如果沒有顯式拒絕，系統會檢查是否在組織規範的邊界內。
    **SCP / Permissions Boundary**: If there is no explicit deny, the system checks if the request falls within the boundaries defined by the organization.
3.  **Explicit Allow（顯式允許）**: 必須至少有一個 Policy 明確寫著 `Allow`。
    **Explicit Allow**: There must be at least one policy that explicitly states `Allow`.
4.  **Implicit Deny（隱式拒絕）**: 如果既沒有 `Deny` 也沒有 `Allow`，預設結果是拒絕。
    **Implicit Deny**: If there is neither a `Deny` nor an `Allow`, the default result is a rejection.

> **關鍵區別 (Key Distinction)**: Identity-based Policy（我是誰，我能做什麼） vs. Resource-based Policy（這是什麼資源，誰能存取它）。S3 Bucket Policy 是典型的 Resource-based Policy。
> **Key Distinction**: Identity-based Policy (Who am I, what can I do) vs. Resource-based Policy (What is this resource, who can access it). S3 Bucket Policy is a typical Resource-based Policy.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

## 3.1 多帳號架構與 Landing Zone
## 3.1 Multi-Account Architecture & Landing Zone

在 Production 環境中，將所有資源（Dev, Test, Prod）放在同一個 AWS Account 是極度危險的。資深架構師會設計 **AWS Organizations** 結構：

In a production environment, keeping all resources (Dev, Test, Prod) in a single AWS Account is extremely dangerous. A Senior Architect designs an **AWS Organizations** structure:

*   **Management Account (Root)**: 僅用於 Billing 與管理 Organizations，不跑任何 Workload。
    **Management Account (Root)**: Used only for Billing and managing Organizations; runs no workloads.
*   **Security OU**: 包含 Log Archive（集中存放 CloudTrail/Config logs）與 Security Tooling 帳號。
    **Security OU**: Contains Log Archive (centralized CloudTrail/Config logs) and Security Tooling accounts.
*   **Workload OU**: 依據環境（Prod/Non-Prod）或業務線（BU）隔離應用程式帳號。
    **Workload OU**: Isolates application accounts based on environment (Prod/Non-Prod) or Business Unit (BU).

**設計優勢 (Design Benefits):**
*   **Blast Radius Reduction**: 開發環境被駭不會影響生產環境的 IAM。
    **Blast Radius Reduction**: A compromise in the development environment does not affect the IAM of the production environment.
*   **Cost Allocation**: 帳單清晰分離，易於歸屬成本。
    **Cost Allocation**: Clear separation of bills, making cost attribution easier.

## 3.2 權限邊界 (Permissions Boundaries) 的應用
## 3.2 Application of Permissions Boundaries

假設你需要讓開發者能夠創建 IAM Role（例如為 Lambda 創建 Role），但你不希望他們創建一個擁有 `AdministratorAccess` 的 Role 來提升自己的權限（Privilege Escalation）。

Suppose you need to allow developers to create IAM Roles (e.g., for Lambda), but you don't want them to create a role with `AdministratorAccess` to escalate their own privileges.

*   **Solution**: 使用 Permissions Boundary。你允許開發者 `iam:CreateRole`，但條件是他們必須將一個特定的 Policy（例如 `PowerUserAccess`）附加為該 Role 的 Boundary。這樣，即使開發者給該 Role 寫了 `Allow: *`，該 Role 的實際權限也無法超過 Boundary 的範圍。
    **Solution**: Use Permissions Boundaries. You allow developers `iam:CreateRole`, but with the condition that they must attach a specific policy (e.g., `PowerUserAccess`) as a boundary for that role. This way, even if the developer writes `Allow: *` for that role, the role's actual permissions cannot exceed the scope of the Boundary.

---

# 4. 逐步示例 (Walkthrough / Example)

## 案例：防止開發者關閉 CloudTrail (Preventing Developers from Disabling CloudTrail)

**背景 (Context)**:
在大型組織中，為了合規性（Compliance），必須確保所有 AWS 帳號的 CloudTrail 永遠開啟。即使是該帳號的 Administrator 也不應該能關閉它。

In a large organization, for compliance reasons, CloudTrail must be enabled in all AWS accounts at all times. Even the Administrator of that account should not be able to disable it.

### 步驟 1: Naive Approach (IAM Policy)
單純在 IAM User 上移除 `cloudtrail:StopLogging` 權限。
Simply removing `cloudtrail:StopLogging` permission from IAM Users.

*   **問題 (Problem)**: 如果該 User 有 `iam:AttachUserPolicy`，他可以自己把權限加回來。如果是 Root User，IAM Policy 無法限制。
    **Problem**: If the user has `iam:AttachUserPolicy`, they can add the permission back themselves. If it's the Root User, IAM Policies cannot restrict them.

### 步驟 2: Better Approach (SCP - Service Control Policy)
使用 AWS Organizations 的 SCP。SCP 是作用於 Account 層級的「護欄（Guardrails）」。

Use SCPs within AWS Organizations. SCPs act as "Guardrails" at the Account level.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyCloudTrailModification",
      "Effect": "Deny",
      "Action": [
        "cloudtrail:StopLogging",
        "cloudtrail:DeleteTrail",
        "cloudtrail:UpdateTrail"
      ],
      "Resource": "*",
      "Condition": {
        "StringNotLike": {
          "aws:PrincipalARN": "arn:aws:iam::*:role/SecurityAdminRole"
        }
      }
    }
  ]
}
```

### 3. 分析 (Analysis)
*   **Effect: Deny**: 這是最強的限制。
    **Effect: Deny**: This is the strongest restriction.
*   **Scope**: 將此 SCP 綁定到 Production OU。該 OU 下的所有帳號（包括帳號內的 Root User）都會受到限制。
    **Scope**: Attach this SCP to the Production OU. All accounts under this OU (including the Root User within the account) will be restricted.
*   **Exception**: 使用 `Condition` 排除特定的 Security Role，確保只有安全團隊可以變更設定。
    **Exception**: Use `Condition` to exclude specific Security Roles, ensuring only the security team can modify settings.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 長期憑證 (Long-term Credentials / IAM Access Keys)
*   **Anti-pattern**: 在 CI/CD 或應用程式設定檔中硬編碼 IAM Access Key / Secret Key。
    **Anti-pattern**: Hardcoding IAM Access Key / Secret Key in CI/CD pipelines or application configuration files.
*   **Why it's bad**: Key 洩漏是 AWS 安全事故的主因。輪替（Rotation）管理困難。
    **Why it's bad**: Key leakage is the leading cause of AWS security incidents. Rotation management is difficult.
*   **Better Solution**:
    *   **EC2**: Use Instance Profiles.
    *   **EKS**: Use IRSA (IAM Roles for Service Accounts).
    *   **External/Local**: Use AWS IAM Identity Center (SSO) or `AssumeRole` with temporary credentials.

## 5.2 過度依賴 Inline Policies
## 5.2 Over-reliance on Inline Policies
*   **Anti-pattern**: 直接將 JSON 寫在 User 或 Role 裡面（Inline）。
    **Anti-pattern**: Writing JSON directly inside the User or Role (Inline).
*   **Why it's bad**: 難以維護、無法復用、版本控制困難，且容易達到 Policy Size 限制。
    **Why it's bad**: Hard to maintain, not reusable, difficult to version control, and easy to hit Policy Size limits.
*   **Better Solution**: 使用 **Customer Managed Policies**。這允許你在多個 Role 之間共享邏輯，並進行獨立的版本更新。
    **Better Solution**: Use **Customer Managed Policies**. This allows you to share logic across multiple roles and perform independent version updates.

## 5.3 忽略數據傳輸成本 (Ignoring Data Transfer Costs)
*   **Anti-pattern**: 架構設計時未考慮 Availability Zone (AZ) 之間的流量費用。
    **Anti-pattern**: Designing architecture without considering traffic costs between Availability Zones (AZs).
*   **Why it's bad**: 跨 AZ 的數據傳輸不是免費的。頻繁的跨 AZ 呼叫（例如 App 在 AZ-A，DB 在 AZ-B）會導致帳單暴增。
    **Why it's bad**: Cross-AZ data transfer is not free. Frequent cross-AZ calls (e.g., App in AZ-A, DB in AZ-B) will cause bill shock.
*   **Better Solution**: 盡量保持流量在同一 AZ 內（Data Locality），或評估是否真的需要 Multi-AZ 的即時同步。
    **Better Solution**: Keep traffic within the same AZ as much as possible (Data Locality), or evaluate if real-time Multi-AZ synchronization is truly necessary.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何在不影響現有業務的情況下，移除一個過於寬鬆的權限（如 AdministratorAccess）？
## Q1: How do you remove an overly permissive permission (like AdministratorAccess) without impacting existing business operations?

*   **Key Points**:
    *   **Access Analyzer**: 提及使用 IAM Access Analyzer 生成基於實際 CloudTrail 歷史記錄的 Policy。
        **Access Analyzer**: Mention using IAM Access Analyzer to generate policies based on actual CloudTrail history.
    *   **Process**: 不要直接刪除。先創建一個新 Policy，觀察 CloudTrail 確認沒有 Access Denied，再切換。
        **Process**: Do not delete directly. Create a new policy first, monitor CloudTrail to ensure no Access Denied errors, then switch.
    *   **Fallout Plan**: 準備好快速回滾（Rollback）機制。
        **Fallout Plan**: Have a quick rollback mechanism ready.

## Q2: 請比較 Security Group 與 Network ACL 的差異，並說明在架構中如何搭配使用？
## Q2: Compare Security Groups and Network ACLs, and explain how to use them together in architecture?

*   **Key Points**:
    *   **Stateful vs. Stateless**: SG 是有狀態的（回應流量自動允許），NACL 是無狀態的（需分別設定 Inbound/Outbound）。
        **Stateful vs. Stateless**: SGs are stateful (return traffic automatically allowed); NACLs are stateless (Inbound/Outbound set separately).
    *   **Level**: SG 作用於 ENI (Instance) 層級；NACL 作用於 Subnet 層級。
        **Level**: SGs act at the ENI (Instance) level; NACLs act at the Subnet level.
    *   **Strategy**: 資深回答應強調 **Defense in Depth**。SG 是主要防線，NACL 用於粗粒度的封鎖（例如封鎖特定惡意 IP 段），通常 NACL 保持寬鬆，由 SG 進行細粒度控制。
        **Strategy**: A senior answer should emphasize **Defense in Depth**. SGs are the primary defense; NACLs are for coarse-grained blocking (e.g., blocking specific malicious IP ranges). Usually, NACLs are kept permissive, with SGs handling fine-grained control.

## Q3: 在 System Design 中，如何權衡 Reliability 與 Cost？
## Q3: In System Design, how do you trade off Reliability vs. Cost?

*   **Key Points**:
    *   **Multi-AZ vs. Multi-Region**: Multi-AZ 是標準配置（高可用）；Multi-Region 是災難恢復（DR），成本極高且涉及數據複製延遲。除非有合規或極高 SLA 需求，否則不輕易上 Multi-Region。
        **Multi-AZ vs. Multi-Region**: Multi-AZ is standard (High Availability); Multi-Region is for Disaster Recovery (DR), which is very costly and involves data replication latency. Do not easily adopt Multi-Region unless there are compliance or extremely high SLA requirements.
    *   **Spot Instances**: 對於無狀態（Stateless）且可容錯的服務，使用 Spot Instances 犧牲一點可靠性換取大幅成本降低。
        **Spot Instances**: For stateless and fault-tolerant services, use Spot Instances to sacrifice a bit of reliability for significant cost reduction.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 記憶錨點 (Key Takeaways)
1.  **Well-Architected Framework** 是關於權衡（Trade-offs），而非完美。
    **Well-Architected Framework** is about trade-offs, not perfection.
2.  **IAM 邏輯**: Explicit Deny > Explicit Allow > Implicit Deny。
    **IAM Logic**: Explicit Deny > Explicit Allow > Implicit Deny.
3.  **SCP** 是組織層級的憲法，**Permissions Boundary** 是委派管理的邊界。
    **SCPs** are the constitution at the organization level; **Permissions Boundaries** are the borders for delegated administration.
4.  **多帳號策略 (Multi-Account)** 是隔離風險與成本的最佳實踐。
    **Multi-Account Strategy** is the best practice for isolating risk and cost.
5.  **最小權限 (Least Privilege)** 需配合 Access Analyzer 與持續監控來實現，而非一次性設定。
    **Least Privilege** is achieved through Access Analyzer and continuous monitoring, not a one-time setup.

## 後續延伸 (Next Steps)
*   **Next Chapter**: `AWS Networking & VPC Design`。既然我們已經建立了安全的帳號結構與權限模型，下一步是建立網路隔離（VPC, Subnets, Transit Gateway），這是雲端架構的骨架。
    **Next Chapter**: `AWS Networking & VPC Design`. Now that we have established a secure account structure and permission model, the next step is to build network isolation (VPC, Subnets, Transit Gateway), which is the skeleton of cloud architecture.
*   **Action Item**: 檢查你目前的 AWS 專案，是否有使用 IAM User 的 Access Key？嘗試將其遷移至 IAM Role。
    **Action Item**: Check your current AWS projects. Are you using IAM User Access Keys? Try migrating them to IAM Roles.