# GCP 核心心智模型：資源階層與全球網路 / Core Mental Models: Resource Hierarchy & Global Network

## Mental model｜心智模型

在開始操作 GCP 之前，必須先重塑兩個關鍵的心智模型，這通常是 AWS 或地端工程師轉移到 GCP 時最大的認知障礙。

### 1. 資源階層：檔案系統般的繼承結構 (The File System Analogy)
不同於 AWS 帳號 (Account) 之間相對隔離，GCP 的資源管理更像是一個**企業級的檔案系統**。

- **Organization (Root)**: 公司的根目錄。所有資源的擁有權最終歸屬於此，而非建立資源的個人。
- **Folders (Directories)**: 資料夾。用於反映公司的組織架構（如部門）或環境（如 Prod/Dev）。重點在於**IAM 權限與 Org Policies 的繼承**。
- **Projects (Files/Binders)**: 專案。這是 GCP 的**計費 (Billing)** 與 **權限邊界 (Trust Boundary)** 的最小原子單位，而不是單純的命名空間。所有的 API 啟用、Quota 限制、帳單都是掛在 Project 上。
- **Resources**: VM, Bucket, Database 等具體資源。

> **Mental Shift**: 不要把 GCP Project 當作一個簡單的 Tag，它更像是一個獨立的「虛擬資料中心」。如果你需要隔離帳單或隔離安全性，就開一個新的 Project。

### 2. 全球網路：軟體定義的全球 LAN (Global VPC)
這是 GCP 與 AWS/Azure 最本質的區別。
- **AWS/Azure**: VPC 是 **Regional (區域性)** 的。如果你需要在 `us-east-1` 和 `asia-northeast-1` 部署，你需要建立兩個 VPC 並設定 VPC Peering。
- **GCP**: VPC 是 **Global (全球性)** 的。一個 VPC 可以跨越所有 GCP 的 Region。
  - **Subnets (子網段)** 是 Regional 的。
  - 資源（如 VM）掛在 Subnet 上。

> **Mental Shift**: 想像 GCP 的 VPC 是一個已經拉好全球光纖的超大內網。你在東京開一台 VM，在紐約開一台 VM，只要它們在同一個 VPC 內（即使不同 Subnet），它們預設就能透過 Internal IP 互通，無需經過 Public Internet，也無需設定 VPN 或 Peering。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 資源階層設計模式 (Hierarchy Design Patterns)

在設計 Organization 和 Folder 結構時，推薦採用 **"Environment-First"** 或 **"Hybrid"** 模式，而非單純的部門結構。

- **推薦結構：Environment Isolation**
  ```text
  Organization
  ├── folders/Common (Shared Services, CI/CD, Auditing)
  ├── folders/Production
  │   ├── folders/Payment-Service
  │   └── folders/User-Service
  └── folders/Non-Production
      ├── folders/Development
      └── folders/Staging
  ```
  - **Why?** 這樣最容易在 Folder 層級套用 **Organization Policies**。例如：在 `folders/Production` 層級強制設定 `constraints/compute.vmExternalIpAccess` 為 Deny，確保生產環境沒有 VM 擁有 Public IP。

### 2. 網路架構模式：Shared VPC (XPN)

在企業級應用中，單一 Project 單一 VPC 的模式很難管理。標準做法是 **Shared VPC**。

- **Host Project**: 專門用來管理網路（VPC, Subnets, Firewall Rules, Cloud NAT, VPN）。由網路團隊 (NetOps) 管理。
- **Service Projects**: 各個應用團隊的 Project。它們沒有自己的 VPC，而是直接使用 Host Project 分享過來的 Subnets。
- **優勢**:
  - 應用開發者不需要懂 CIDR 規劃。
  - 安全性集中管理（防火牆規則統一由 NetOps 審核）。
  - 節省 Public IP 和 VPN Gateway 的成本。

### 3. 權限管理：Google Groups Mapping

不要直接將 IAM Role 綁定給個人的 Gmail 或 corporate email。
- **Pattern**: 建立 Google Group (e.g., `gcp-org-admins@company.com`, `gcp-billing-viewers@company.com`)。
- **Action**: 在 IAM Policy 中綁定 Role 給 Google Group。
- **Benefit**: 當有人員入職或離職，只需在 Google Workspace/Cloud Identity 修改 Group 成員，無需改動 GCP 架構設定。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Flat" Hierarchy (扁平化結構)
- **現象**: 所有 Project 直接掛在 Organization 下，沒有使用 Folders。
- **後果**: 當公司擴張，需要對 "Production" 環境做特殊限制（如禁止 Service Account Key Creation）時，你必須逐個 Project 設定，導致維運地獄與安全漏洞。

### 2. AWS Mental Drift: VPC Peering Mesh
- **現象**: 習慣 AWS 的工程師在 GCP 上為每個 Region 建立獨立的 VPC，然後瘋狂建立 VPC Peering。
- **後果**: 增加了網路複雜度、路由表限制，並失去了 GCP Global VPC 的原生優勢（跨 Region 高吞吐低延遲內網）。
- **修正**: 使用單一 Global VPC，在不同 Region 切分 Subnet 即可。

### 3. Default VPC Trap
- **現象**: 直接使用每個 Project 預設建立的 `default` VPC。
- **後果**: `default` VPC 預設包含大量寬鬆的防火牆規則，且 Subnet 遍布全球所有 Region，容易造成 IP 浪費與安全隱患。
- **建議**: 建立 Project 的第一件事就是**刪除 default VPC**，並建立 Custom VPC。

### 4. Overlapping CIDRs in Hybrid Cloud
- **現象**: 在規劃 GCP VPC CIDR 時，未考量地端 (On-premise) 或其他雲端的網段。
- **後果**: 未來建立 VPN 或 Interconnect 混合雲連線時發生 IP 衝突，導致必須重建整個網路或使用複雜的 NAT 方案。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Do I need a new Project?
- [ ] **Billing isolation?** (需要獨立出帳單給特定客戶或部門？) -> **Yes**
- [ ] **Security boundary?** (需要完全隔離 IAM，避免誤觸？) -> **Yes**
- [ ] **Environment separation?** (Prod vs Dev?) -> **Yes**
- [ ] **Just a new microservice?** -> **No** (Use the same project, separate by Service Account/K8s Namespace).

### Network Setup Checklist (Day 1)
- [ ] **Delete Default VPC**: 確認已刪除自動生成的 `default` 網路。
- [ ] **CIDR Planning**: 規劃 Global VPC 的 IP 範圍，確保與地端/AWS 不衝突 (e.g., `10.128.0.0/9` for GCP)。
- [ ] **Private Google Access**: 在所有 Subnet 啟用此選項，讓沒有 Public IP 的 VM 也能存取 GCS/BigQuery 等 Google API。
- [ ] **Cloud NAT**: 為需要連網更新套件的 Private VM 配置 Cloud NAT（避免給予 Public IP）。
- [ ] **Firewall Rules**: 建立 "Deny All" 的低優先級規則，並僅開放必要的 Tag/Service Account 流量。

---

## Real-world examples｜實戰案例

### Scenario: Global Gaming Backend (全球遊戲後端)

**需求**：
一家遊戲公司，後端伺服器需部署在 `us-central1` (美國), `europe-west1` (歐洲), `asia-east1` (台灣)，且資料庫需同步，服務間需低延遲通訊。

**AWS Style (Anti-pattern in GCP context)**:
1. 建立 3 個 VPC (US, EU, Asia)。
2. 設定 3 組 VPC Peering (Full Mesh)。
3. 路由表複雜，跨區通訊需經過 Peering Gateway。

**GCP Native Style**:
1. **Resource Hierarchy**:
   - `Folder: Production` -> `Project: game-backend-prod`
2. **Network**:
   - 建立 **1 個 Global VPC** (`vpc-game-global`).
   - 建立 **3 個 Subnets**:
     - `sb-us (10.1.0.0/20)`
     - `sb-eu (10.2.0.0/20)`
     - `sb-asia (10.3.0.0/20)`
3. **Connectivity**:
   - 位於台灣的 VM (`10.3.0.5`) 可以直接 ping 美國的 VM (`10.1.0.5`)。
   - 流量走 Google 骨幹網路 (Backbone)，不經過公網，延遲最低且穩定。
4. **Security**:
   - 防火牆規則設定：`Allow Internal` (Source: `10.0.0.0/8`)，一次設定，全球生效。

### Scenario: Enterprise Shared VPC (企業級共享網路)

**結構**:
- **Host Project (`net-hub-prod`)**:
  - 擁有 VPC `vpc-prod-shared`.
  - 定義 Subnets: `subnet-frontend`, `subnet-backend`, `subnet-data`.
  - 管理 VPN 連線至地端辦公室。
- **Service Project A (`app-payment-prod`)**:
  - 獲得 `subnet-backend` 的使用權。
  - 部署 GKE Cluster，Node IP 來自 `subnet-backend`。
- **Service Project B (`app-frontend-prod`)**:
  - 獲得 `subnet-frontend` 的使用權。
  - 部署 Compute Engine，IP 來自 `subnet-frontend`。

**結果**: Payment Service 與 Frontend Service 視為在同一個內網中，但由不同團隊管理資源與帳單，且網路管理權限收斂在核心網管團隊手中。