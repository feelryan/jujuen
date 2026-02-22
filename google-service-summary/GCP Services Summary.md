# GCP Services Summary

## General

### Compliance (合規性)
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security, Privacy, and Compliance pillar)**. 合規性是安全性支柱中的核心基礎，確保架構符合法律與產業標準。
* **產品重要說明 (Product Description)**:
    * Compliance refers to the adherence to laws, regulations, guidelines, and specifications relevant to your business processes.
    * 合規性是指遵守與您的業務流程相關的法律、法規、指導方針和規範。
    * Google Cloud undergoes independent third-party audits to verify that its data protection practices match high standards.
    * Google Cloud 接受獨立的第三方審計，以驗證其資料保護實務符合高標準。
* **主要功能 (Main Functions)**:
    * **Resource Manager**: Sets organization-wide policies to enforce compliance.
    * **Resource Manager**: 設定全機構的政策以強制執行合規性。
    * **Cloud Audit Logs**: Maintains an audit trail of who did what and when.
    * **Cloud Audit Logs**: 維護「誰在何時做了什麼」的稽核追蹤。
    * **Compliance Reports Manager**: Provides access to compliance reports (e.g., SOC, ISO, PCI, HIPAA).
    * **Compliance Reports Manager**: 提供存取合規性報告（例如 SOC、ISO、PCI、HIPAA）的功能。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: When designing for a healthcare client, you must ensure HIPAA compliance.
    * **架構師觀點**: 在為醫療保健客戶進行設計時，您必須確保符合 HIPAA 合規性。
    * You would select products covered by the BAA (Business Associate Agreement) and configure strict IAM roles and audit logging.
    * 您會選擇 BAA (商業夥伴協議) 涵蓋的產品，並配置嚴格的 IAM 角色和稽核紀錄。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Shared Responsibility Model**: Google protects the infrastructure (security *of* the cloud), but the customer is responsible for their data and configuration (security *in* the cloud).
    * **共同責任模型**: Google 保護基礎設施（雲端*本身*的安全性），但客戶負責其資料和配置（雲端*內部*的安全性）。
    * **Data Residency**: Understanding where data is stored is crucial for GDPR compliance.
    * **資料駐留**: 了解資料儲存的位置對於 GDPR 合規性至關重要。

---

### REST APIs
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Operational Excellence pillar)**. 自動化與程式化互動是卓越營運的關鍵。
* **產品重要說明 (Product Description)**:
    * Google Cloud services expose their functionality through RESTful APIs, which use HTTP requests to manage resources.
    * Google Cloud 服務透過 RESTful API 揭露其功能，使用 HTTP 請求來管理資源。
    * JSON is the primary data format used for API requests and responses.
    * JSON 是用於 API 請求和回應的主要資料格式。
* **主要功能 (Main Functions)**:
    * **Programmatic Access**: Allows developers to control GCP resources using code instead of the Console.
    * **程式化存取**: 允許開發人員使用程式碼而非控制台來控制 GCP 資源。
    * **Google Cloud SDK**: The `gcloud` command-line tool wraps these REST APIs.
    * **Google Cloud SDK**: `gcloud` 命令列工具封裝了這些 REST API。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You are building a custom internal portal for provisioning VMs.
    * **架構師觀點**: 您正在建立一個用於配置 VM 的自定義內部入口網站。
    * Instead of giving users Console access, the portal backend calls the Compute Engine REST API to create instances.
    * 入口網站後端會呼叫 Compute Engine REST API 來建立執行個體，而不是給予使用者控制台存取權限。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Authentication**: Most APIs require OAuth 2.0 or Service Accounts for authentication.
    * **身分驗證**: 大多數 API 需要 OAuth 2.0 或服務帳戶進行身分驗證。
    * **Quotas and Limits**: API calls are subject to quotas to prevent abuse and manage load.
    * **配額與限制**: API 呼叫受配額限制，以防止濫用並管理負載。

---

### Capex vs Opex
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Cost Optimization pillar)**. 這是雲端成本優化的核心經濟概念。
* **產品重要說明 (Product Description)**:
    * Capex (Capital Expenditure) involves upfront costs for physical infrastructure, typical of on-premises data centers.
    * Capex (資本支出) 涉及實體基礎設施的預先成本，是地端資料中心的典型特徵。
    * Opex (Operational Expenditure) involves pay-as-you-go costs for services used, which is the primary model of Cloud Computing.
    * Opex (營運支出) 涉及按使用量付費的服務成本，這是雲端運算的主要模式。
* **主要功能 (Main Functions)**:
    * **Shift to Variable Expense**: Moving from fixed data center costs to variable cloud costs.
    * **轉向變動支出**: 從固定的資料中心成本轉向變動的雲端成本。
    * **Cost Agility**: Ability to scale costs up or down based on demand.
    * **成本敏捷性**: 能夠根據需求擴展或縮減成本。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: A startup wants to launch a new app but has limited capital.
    * **架構師觀點**: 一家新創公司想要推出一個新應用程式，但資本有限。
    * You advise using GCP to leverage the Opex model, avoiding the need to buy servers before knowing if the app will succeed.
    * 您建議使用 GCP 來利用 Opex 模式，避免在知道應用程式是否成功之前購買伺服器。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **TCO (Total Cost of Ownership)**: When comparing on-prem to cloud, you must factor in power, cooling, and labor (Capex + hidden Opex) vs. direct cloud billing (Opex).
    * **TCO (總體擁有成本)**: 在比較地端與雲端時，您必須將電力、冷卻和人力（Capex + 隱藏的 Opex）與直接的雲端帳單（Opex）進行因素比較。
    * **Predictability**: While Opex offers flexibility, it requires governance (budgets/alerts) to prevent unexpected bills.
    * **可預測性**: 雖然 Opex 提供靈活性，但它需要治理（預算/警報）以防止意外的帳單。

---

### Migrating GCP Projects
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Operational Excellence pillar)**. 專案結構與遷移管理屬於營運管理的範疇。
* **產品重要說明 (Product Description)**:
    * Migrating GCP projects usually refers to moving a project from one Organization resource to another.
    * 遷移 GCP 專案通常是指將專案從一個機構資源移動到另一個機構資源。
    * This is often required during company mergers or acquisitions.
    * 這通常在公司合併或收購期間需要。
* **主要功能 (Main Functions)**:
    * **Resource Hierarchy**: Projects sit under Folders and Organizations.
    * **資源階層**: 專案位於資料夾和機構之下。
    * **Organization Policy**: Moving a project changes which Organization Policies apply to it.
    * **機構政策**: 移動專案會改變適用於該專案的機構政策。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Company A acquires Company B, and Company B has its own GCP Organization.
    * **架構師觀點**: A 公司收購了 B 公司，而 B 公司有自己的 GCP 機構。
    * You plan the migration of B's projects into A's Organization to centralize billing and security management.
    * 您規劃將 B 的專案遷移到 A 的機構中，以集中帳單和安全管理。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Billing Accounts**: The billing account associated with the project might need to be changed or linked to the new organization.
    * **帳單帳戶**: 與專案關聯的帳單帳戶可能需要更改或連結到新機構。
    * **IAM Impacts**: IAM policies inherited from the old Organization will be lost; new ones will be inherited from the destination.
    * **IAM 影響**: 從舊機構繼承的 IAM 政策將會遺失；新的政策將從目標機構繼承。

---

### Google Front End (GFE)
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Performance Efficiency & Security pillars)**. GFE 是 Google 全球網路效能與第一層防禦的關鍵。
* **產品重要說明 (Product Description)**:
    * GFE is the software-defined infrastructure that sits at the edge of Google's network.
    * GFE 是位於 Google 網路邊緣的軟體定義基礎設施。
    * It handles incoming requests for Google services (like Search, Gmail, and GCP Load Balancers).
    * 它處理對 Google 服務（如搜尋、Gmail 和 GCP 負載平衡器）的傳入請求。
* **主要功能 (Main Functions)**:
    * **SSL/TLS Termination**: Decrypts traffic at the edge, close to the user.
    * **SSL/TLS 終止**: 在靠近使用者的邊緣解密流量。
    * **Global Load Balancing**: Distributes traffic to the nearest Google data center.
    * **全球負載平衡**: 將流量分配到最近的 Google 資料中心。
    * **DDoS Protection**: Provides the first line of defense against attacks (Google Cloud Armor integrates here).
    * **DDoS 防護**: 提供抵禦攻擊的第一道防線（Google Cloud Armor 在此整合）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You are configuring an HTTP(S) Load Balancer.
    * **架構師觀點**: 您正在配置 HTTP(S) 負載平衡器。
    * You understand that the GFE receives the client request first, terminates the SSL, and then forwards the request to your backend instances via Google's private backbone.
    * 您了解 GFE 首先接收客戶端請求，終止 SSL，然後透過 Google 的專用骨幹網路將請求轉發到您的後端執行個體。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Latency**: GFE minimizes latency by terminating connections close to the user.
    * **延遲**: GFE 透過在靠近使用者處終止連線來最小化延遲。
    * **Abstraction**: It abstracts the physical location of your services from the public internet.
    * **抽象化**: 它將您服務的實體位置從公共網際網路中抽象出來。

---

### SRE (Site Reliability Engineering)
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Reliability pillar)**. SRE 是 Google 定義可靠性工程的核心哲學。
* **產品重要說明 (Product Description)**:
    * SRE is a discipline that incorporates aspects of software engineering and applies them to infrastructure and operations problems.
    * SRE 是一門學科，結合了軟體工程的各個方面，並將其應用於基礎設施和維運問題。
    * The main goal is to create scalable and highly reliable software systems.
    * 主要目標是建立可擴展且高度可靠的軟體系統。
* **主要功能 (Main Functions)**:
    * **Eliminating Toil**: Automating repetitive, manual work.
    * **消除瑣事 (Toil)**: 自動化重複性的手動工作。
    * **Error Budgets**: Balancing reliability with the velocity of feature releases.
    * **錯誤預算**: 在可靠性與功能發布速度之間取得平衡。
    * **Blameless Postmortems**: Analyzing incidents to improve systems without punishing individuals.
    * **不指責的事後檢討**: 分析事件以改進系統，而不懲罰個人。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: An organization wants to improve their uptime but releases are constantly breaking things.
    * **架構師觀點**: 一個組織希望提高其正常運行時間，但發布卻不斷破壞事物。
    * You recommend adopting SRE practices, specifically implementing Error Budgets to freeze launches when reliability drops below targets.
    * 您建議採用 SRE 實務，特別是實施錯誤預算，以便在可靠性低於目標時凍結發布。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **DevOps vs SRE**: SRE implements DevOps. SRE is a specific set of practices for the abstract philosophy of DevOps.
    * **DevOps 與 SRE**: SRE 實作了 DevOps。SRE 是針對 DevOps 抽象哲學的一套具體實務。

---

### SLOs, SLIs, SLAs
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Reliability pillar)**. 這些是測量與定義可靠性的標準度量。
* **產品重要說明 (Product Description)**:
    * These are the three pillars of measuring reliability in SRE.
    * 這些是 SRE 中衡量可靠性的三大支柱。
    * They define metrics (SLI), targets (SLO), and consequences (SLA).
    * 它們定義了指標 (SLI)、目標 (SLO) 和後果 (SLA)。
* **主要功能 (Main Functions)**:
    * **SLI (Service Level Indicator)**: A quantitative measure of the level of service provided (e.g., latency, error rate).
    * **SLI (服務水準指標)**: 提供的服務水準之量化測量（例如延遲、錯誤率）。
    * **SLO (Service Level Objective)**: A target value or range of values for a service level (e.g., 99.9% availability).
    * **SLO (服務水準目標)**: 服務水準的目標值或數值範圍（例如 99.9% 的可用性）。
    * **SLA (Service Level Agreement)**: A contract with consequences (financial penalty) if the SLO is not met.
    * **SLA (服務水準協議)**: 如果未達到 SLO，則具有後果（財務處罰）的合約。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You are designing a service for an external customer.
    * **架構師觀點**: 您正在為外部客戶設計一項服務。
    * You define an internal SLO of 99.95% to ensure you comfortably meet the external SLA of 99.9%, leaving room for error.
    * 您定義 99.95% 的內部 SLO，以確保您能輕鬆達到 99.9% 的外部 SLA，並留有錯誤空間。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Internal vs External**: SLOs are typically for internal engineering teams; SLAs are for external customers.
    * **內部與外部**: SLO 通常針對內部工程團隊；SLA 針對外部客戶。
    * **Error Budget Calculation**: Error Budget = 100% - SLO. If your SLO is 99.9%, your error budget is 0.1%.
    * **錯誤預算計算**: 錯誤預算 = 100% - SLO。如果您的 SLO 是 99.9%，您的錯誤預算是 0.1%。

---

### Uptime checks
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Reliability pillar)**. 這是監控系統健康狀態的最基本方式。
* **產品重要說明 (Product Description)**:
    * Uptime checks allow you to verify the availability of your public services from locations around the world.
    * 正常運行時間檢查允許您從世界各地的位置驗證您的公共服務的可用性。
    * They are a feature of Google Cloud Monitoring.
    * 它們是 Google Cloud Monitoring 的一項功能。
* **主要功能 (Main Functions)**:
    * **Global Probing**: Pings your endpoints (HTTP, HTTPS, TCP) from various global regions.
    * **全球探測**: 從全球各個區域 Ping 您的端點（HTTP、HTTPS、TCP）。
    * **Alerting**: Triggers alerts if the service fails the check from multiple locations.
    * **警報**: 如果服務在多個位置檢查失敗，則觸發警報。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You deploy a web server on Compute Engine.
    * **架構師觀點**: 您在 Compute Engine 上部署了一個網頁伺服器。
    * You configure an Uptime Check to hit the homepage every 5 minutes from USA, Europe, and Asia to ensure global accessibility.
    * 您配置一個正常運行時間檢查，每 5 分鐘從美國、歐洲和亞洲訪問首頁，以確保全球可存取性。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Private IPs**: Standard Uptime Checks cannot reach private IP addresses; they are for public endpoints.
    * **私人 IP**: 標準正常運行時間檢查無法到達私人 IP 位址；它們適用於公共端點。
    * **Private Uptime Checks**: A separate feature exists to check internal resources via Private Service Connect (more advanced).
    * **私人正常運行時間檢查**: 存在一個單獨的功能，透過 Private Service Connect 檢查內部資源（更進階）。

---

## Compute Environment

### Compute Engine (GCE)
* **Knowledge Level**: 3: advanced
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Infrastructure pillar)**. IaaS 核心服務，是建構客製化、高彈性架構的基礎。
* **產品重要說明 (Product Description)**:
    * Compute Engine delivers configurable virtual machines running in Google's data centers.
    * Compute Engine 提供在 Google 資料中心運行的可配置虛擬機器。
    * It offers Infrastructure-as-a-Service (IaaS) capabilities with high performance and scalability.
    * 它提供具有高效能和可擴展性的基礎設施即服務 (IaaS) 能力。
* **主要功能 (Main Functions)**:
    * **Machine Types**: Predefined (e.g., e2-medium) or Custom Machine Types (CPU/RAM ratio customization).
    * **機器類型**: 預定義（例如 e2-medium）或自定義機器類型（CPU/RAM 比例客製化）。
    * **Live Migration**: Keeps instances running even when a host system event (maintenance) occurs.
    * **即時遷移**: 即使發生主機系統事件（維護），也能保持執行個體運行。
    * **Global Load Balancing Support**: Integrates directly with GCP Load Balancers.
    * **全球負載平衡支援**: 與 GCP 負載平衡器直接整合。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You are migrating a legacy enterprise application that requires a specific OS kernel and full control over the file system.
    * **架構師觀點**: 您正在遷移需要特定作業系統核心且需要完全控制檔案系統的舊版企業應用程式。
    * You choose Compute Engine because PaaS (App Engine) or Serverless (Cloud Run) cannot support the custom software dependencies.
    * 您選擇 Compute Engine，因為 PaaS (App Engine) 或無伺服器 (Cloud Run) 無法支援自定義軟體依賴關係。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Live Migration**: This is a key differentiator. Google can patch the host hardware without rebooting your VM.
    * **即時遷移**: 這是一個關鍵區別。Google 可以在不重新啟動您的 VM 的情況下修補主機硬體。
    * **Availability Policies**: You must understand `onHostMaintenance` (MIGRATE or TERMINATE) and `automaticRestart`.
    * **可用性政策**: 您必須了解 `onHostMaintenance` (遷移或終止) 和 `automaticRestart` (自動重啟)。
    * **Rightsizing**: Using Monitoring to analyze CPU/RAM usage and adjusting the machine type to save costs (Recommendation API).
    * **適當規模化 (Rightsizing)**: 使用 Monitoring 分析 CPU/RAM 使用情況並調整機器類型以節省成本（推薦 API）。
    * **Spot VMs**: Understanding the tradeoff of using ephemeral instances for batch processing to save up to 91%.
    * **Spot VMs**: 了解使用臨時執行個體進行批次處理以節省高達 91% 費用的權衡。

---

### Managing access to VMs (OS Login etc)
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security pillar)**. 管理 SSH 存取是 VM 安全的關鍵環節。
* **產品重要說明 (Product Description)**:
    * Traditionally, SSH keys were managed by adding public keys to VM metadata.
    * 傳統上，SSH 金鑰是透過將公鑰新增至 VM Metadata 來管理的。
    * **OS Login** links the Linux user account to the Google Identity (Cloud IAM), offering a more secure and centralized way to manage SSH access.
    * **OS Login** 將 Linux 使用者帳戶連結到 Google 身分 (Cloud IAM)，提供了一種更安全且集中的方式來管理 SSH 存取。
* **主要功能 (Main Functions)**:
    * **IAM Integration**: Grants SSH access based on IAM roles (e.g., `roles/compute.osLogin`).
    * **IAM 整合**: 根據 IAM 角色授予 SSH 存取權（例如 `roles/compute.osLogin`）。
    * **2FA Support**: Can enforce 2-Step Verification for SSH connections.
    * **雙重驗證支援**: 可以強制對 SSH 連線進行雙步驟驗證。
    * **Audit Logging**: Logs SSH connections tied to specific Google users.
    * **稽核記錄**: 記錄與特定 Google 使用者綁定的 SSH 連線。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: A corporate security policy requires that when an employee leaves the company, their access to all servers is immediately revoked.
    * **架構師觀點**: 公司安全政策要求，當員工離職時，必須立即撤銷其對所有伺服器的存取權限。
    * Instead of manually removing SSH keys from hundreds of VMs, you enable OS Login. Revoking the user's Google account automatically denies SSH access.
    * 您啟用 OS Login，而不是手動從數百個 VM 中移除 SSH 金鑰。撤銷使用者的 Google 帳戶會自動拒絕 SSH 存取。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Metadata vs OS Login**: If OS Login is enabled, metadata-based SSH keys are ignored (unless configured otherwise).
    * **Metadata 與 OS Login**: 如果啟用了 OS Login，則會忽略基於 Metadata 的 SSH 金鑰（除非另有配置）。
    * **Service Accounts**: You can also use OS Login to allow service accounts to SSH into instances for automation tasks.
    * **服務帳戶**: 您也可以使用 OS Login 允許服務帳戶透過 SSH 進入執行個體以執行自動化任務。

---

### Persistent Disks
* **Knowledge Level**: 3: advanced
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Reliability & Performance pillars)**. 資料持久層的選擇直接影響 RPO 和 IOPS。
* **產品重要說明 (Product Description)**:
    * Persistent Disks (PD) are durable, high-performance block storage devices that you attach to your instances.
    * 持久磁碟 (PD) 是耐用、高效能的區塊儲存裝置，您可以將其附加到您的執行個體。
    * Data is independent of the VM lifecycle, meaning data survives if the VM is deleted.
    * 資料獨立於 VM 生命週期，這意味著如果 VM 被刪除，資料仍然存在。
* **主要功能 (Main Functions)**:
    * **Types**: Standard (HDD), Balanced, SSD, and Extreme PD.
    * **類型**: 標準 (HDD)、平衡、SSD 和極限 PD。
    * **Resizing**: You can increase the size of a disk while it is running (no downtime).
    * **調整大小**: 您可以在磁碟運行時增加其大小（無停機時間）。
    * **Snapshots**: Incremental backups that can be stored regionally or multi-regionally.
    * **快照**: 可儲存在區域或多區域的增量備份。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You need a High Availability (HA) database setup on Compute Engine.
    * **架構師觀點**: 您需要在 Compute Engine 上設定高可用性 (HA) 資料庫。
    * You use **Regional Persistent Disks**. These replicate data synchronously between two zones in the same region.
    * 您使用 **區域性持久磁碟 (Regional Persistent Disks)**。這些磁碟會在同一區域的兩個可用區 (Zone) 之間同步複製資料。
    * If one zone fails, you can force-attach the disk to a VM in the other zone to recover quickly.
    * 如果一個可用區發生故障，您可以強制將磁碟附加到另一個可用區的 VM 以快速恢復。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Performance Scaling**: IOPS and throughput usually scale with the disk size (except for Extreme PD). To get higher IOPS, you often need a larger disk.
    * **效能擴展**: IOPS 和傳輸量通常隨磁碟大小擴展（極限 PD 除外）。為了獲得更高的 IOPS，您通常需要更大的磁碟。
    * **Zonal vs Regional**: Zonal PDs are cheaper but bound to a zone. Regional PDs offer HA but are more expensive and have slightly higher write latency (due to sync replication).
    * **區域性 vs 地區性**: 區域性 (Zonal) PD 較便宜但受限於單一可用區。地區性 (Regional) PD 提供 HA，但價格較高且寫入延遲稍高（由於同步複製）。
    * **Multi-writer mode**: Supported only on SSD persistent disks for specific use cases (like cluster filesystems), but with limitations.
    * **多寫入器模式**: 僅在 SSD 持久磁碟上支援特定使用案例（如叢集檔案系統），但有限制。

---

### GCE Instance Groups
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Reliability & Scalability pillars)**. 實現自動修復與彈性伸縮的標準元件。
* **產品重要說明 (Product Description)**:
    * Instance Groups organize VM instances as a single entity.
    * 執行個體群組將 VM 執行個體組織為一個單一實體。
    * There are two types: Managed Instance Groups (MIGs) and Unmanaged Instance Groups.
    * 有兩種類型：託管執行個體群組 (MIG) 和非託管執行個體群組。
* **主要功能 (Main Functions)**:
    * **Auto-healing**: Automatically recreates VMs if they fail a health check.
    * **自動修復**: 如果 VM 未通過健康檢查，則自動重新建立它們。
    * **Auto-scaling**: Adds or removes VMs based on CPU load or custom metrics (MIGs only).
    * **自動擴展**: 根據 CPU 負載或自定義指標新增或移除 VM（僅限 MIG）。
    * **Multi-zone deployment**: Distributes VMs across zones for high availability (Regional MIGs).
    * **多區域部署**: 跨可用區分發 VM 以實現高可用性（區域性 MIG）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You are deploying a stateless frontend web application.
    * **架構師觀點**: 您正在部署無狀態的前端 Web 應用程式。
    * You create a Regional Managed Instance Group with Autoscaling enabled and attach it to an HTTP Load Balancer.
    * 您建立一個啟用了自動擴展的區域性託管執行個體群組，並將其附加到 HTTP 負載平衡器。
    * This ensures the app survives a zonal outage and scales up during traffic spikes.
    * 這確保了應用程式能夠在區域性中斷中存活，並在流量激增期間進行擴展。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Stateful MIGs**: While MIGs are best for stateless apps, Stateful MIGs preserve disk state and IP addresses upon recreation, useful for databases like Cassandra.
    * **有狀態 MIG**: 雖然 MIG 最適合無狀態應用程式，但有狀態 MIG 在重新建立時會保留磁碟狀態和 IP 位址，這對 Cassandra 等資料庫很有用。
    * **Unmanaged Groups**: Generally avoided unless you need to group heterogeneous VMs or legacy setups that cannot use instance templates.
    * **非託管群組**: 通常避免使用，除非您需要對異質 VM 進行分組，或使用無法使用執行個體範本的舊版設定。

---

### Multi-NIC VMs
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Networking & Security pillars)**. 用於網路隔離與特定網路設備架構。
* **產品重要說明 (Product Description)**:
    * Multi-NIC VMs allow a single virtual machine to connect to multiple VPC networks simultaneously.
    * 多網卡 (Multi-NIC) VM 允許單一虛擬機器同時連線到多個 VPC 網路。
    * Each network interface connects to a different VPC network.
    * 每個網路介面連線到不同的 VPC 網路。
* **主要功能 (Main Functions)**:
    * **Network Isolation**: Separates management traffic from data traffic.
    * **網路隔離**: 將管理流量與資料流量分開。
    * **Virtual Appliances**: Essential for running firewalls, load balancers, or proxy VMs that sit between networks.
    * **虛擬設備**: 對於運行位於網路之間的防火牆、負載平衡器或代理 VM 至關重要。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You are deploying a third-party Next-Generation Firewall (NGFW) appliance on GCP.
    * **架構師觀點**: 您正在 GCP 上部署第三方次世代防火牆 (NGFW) 設備。
    * The appliance needs one interface in the "Untrusted" (Public) VPC and one interface in the "Trusted" (Private) VPC to filter traffic passing between them.
    * 該設備需要在「不受信任」(公共) VPC 中有一個介面，在「受信任」(私人) VPC 中有一個介面，以過濾它們之間傳遞的流量。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Creation Time**: You must configure network interfaces when you create the VM instance; you cannot add them later.
    * **建立時間**: 您必須在建立 VM 執行個體時配置網路介面；您無法在之後新增它們。
    * **Subnet Constraint**: Each interface must be attached to a subnet in a *different* VPC network. You cannot have two NICs in the same VPC.
    * **子網限制**: 每個介面必須附加到*不同* VPC 網路中的子網。您不能在同一個 VPC 中有兩個 NIC。

---

### App Engine flexible environment
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Modernization)**. 適用於需要容器化但又希望由平台管理的應用。
* **產品重要說明 (Product Description)**:
    * App Engine Flex allows you to run applications within Docker containers on Compute Engine VMs managed by Google.
    * App Engine Flex 允許您在由 Google 管理的 Compute Engine VM 上的 Docker 容器內運行應用程式。
    * Unlike Standard, it supports any runtime capable of running in a container.
    * 與 Standard 不同，它支援任何能夠在容器中運行的執行環境。
* **主要功能 (Main Functions)**:
    * **Custom Runtimes**: Supports any language via Dockerfile.
    * **自定義執行環境**: 透過 Dockerfile 支援任何語言。
    * **Background Processes**: Allows long-running background processes and writing to local disk (ephemeral).
    * **背景程序**: 允許長時間運行的背景程序並寫入本地磁碟（暫時性）。
    * **Network Access**: VMs appear in your VPC, allowing connection to Compute Engine or VPN resources.
    * **網路存取**: VM 出現在您的 VPC 中，允許連線到 Compute Engine 或 VPN 資源。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You have a Python application that uses C++ libraries requiring specific OS-level installation.
    * **架構師觀點**: 您有一個 Python 應用程式，它使用需要特定 OS 層級安裝的 C++ 函式庫。
    * App Engine Standard's sandbox prevents this. You use Flex with a custom Dockerfile to install these dependencies.
    * App Engine Standard 的沙箱阻止了這一點。您使用帶有自定義 Dockerfile 的 Flex 來安裝這些依賴項。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Deployment Speed**: Flex deployments are slower (minutes) compared to Standard (seconds) because VMs must be provisioned.
    * **部署速度**: 與 Standard（秒）相比，Flex 部署較慢（分鐘），因為必須配置 VM。
    * **Scaling**: Scaling is slower than Standard. It does not scale to zero (minimum 1 instance usually required to serve traffic without cold start).
    * **擴展**: 擴展速度比 Standard 慢。它不會擴展到零（通常至少需要 1 個執行個體來提供服務而無冷啟動）。

---

### App Engine standard environment
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Cost Optimization & Scalability)**. 適用於流量突發型應用。
* **產品重要說明 (Product Description)**:
    * App Engine Standard is a fully serverless platform that runs specific languages (Python, Java, Node.js, Go, PHP, Ruby) in a secure sandbox.
    * App Engine Standard 是一個完全無伺服器的平台，在安全的沙箱中運行特定語言（Python, Java, Node.js, Go, PHP, Ruby）。
    * It abstracts away the OS and infrastructure completely.
    * 它完全抽象化了作業系統和基礎設施。
* **主要功能 (Main Functions)**:
    * **Rapid Scaling**: Scales from 0 to 1000s of instances in seconds.
    * **快速擴展**: 在幾秒鐘內從 0 擴展到數千個執行個體。
    * **Scale to Zero**: Cost is zero when no traffic is hitting the service.
    * **擴展到零**: 當沒有流量訪問服務時，成本為零。
    * **Integrated Services**: Built-in Memcache, Task Queues, and Search APIs (Generation 1 mostly, Gen 2 relies more on cloud-native equivalents).
    * **整合服務**: 內建 Memcache、任務佇列和搜尋 API（主要是第 1 代，第 2 代更依賴於雲端原生對應項目）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You are building a marketing campaign site that expects widely fluctuating traffic (spikes) and periods of inactivity.
    * **架構師觀點**: 您正在建立一個行銷活動網站，預期會有劇烈波動的流量（峰值）和不活動期。
    * App Engine Standard is ideal because it handles the spikes instantly and costs nothing when the campaign is over (idle).
    * App Engine Standard 是理想的選擇，因為它可以立即處理峰值，並且在活動結束（閒置）時不花費任何費用。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Restrictions**: File system is read-only. No background threads (historically) unless using Cloud Tasks or specific configurations.
    * **限制**: 檔案系統是唯讀的。除非使用 Cloud Tasks 或特定配置，否則沒有背景執行緒（歷史上如此）。
    * **Generations**: Understand the difference between 1st Gen (proprietary APIs) and 2nd Gen (open source runtimes, fewer proprietary constraints).
    * **世代**: 了解第一代（專有 API）和第二代（開源執行環境，較少的專有限制）之間的區別。

---

### Cloud GPUs
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Performance Efficiency)**. 針對 ML 與 HPC 負載的加速器。
* **產品重要說明 (Product Description)**:
    * Cloud GPUs allows you to attach Graphics Processing Units (NVIDIA) to Compute Engine VMs.
    * Cloud GPU 允許您將圖形處理單元 (NVIDIA) 附加到 Compute Engine VM。
    * They are used to accelerate math-intensive workloads.
    * 它們用於加速數學密集型工作負載。
* **主要功能 (Main Functions)**:
    * **Workload Acceleration**: Significantly speeds up Machine Learning training and 3D visualization.
    * **工作負載加速**: 顯著加快機器學習訓練和 3D 視覺化速度。
    * **Passthrough Mode**: Provides direct access to the GPU hardware for maximum performance.
    * **直通模式**: 提供對 GPU 硬體的直接存取以獲得最大效能。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You are training a Deep Learning model using TensorFlow.
    * **架構師觀點**: 您正在使用 TensorFlow 訓練深度學習模型。
    * A standard CPU takes days to complete the training. You attach an NVIDIA Tesla T4 or V100 GPU to the VM to reduce training time to hours.
    * 標準 CPU 需要數天才能完成訓練。您將 NVIDIA Tesla T4 或 V100 GPU 附加到 VM，將訓練時間縮短至數小時。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Host Maintenance**: VMs with GPUs *cannot* use Live Migration. They must terminate or restart during maintenance events.
    * **主機維護**: 帶有 GPU 的 VM *不能*使用即時遷移。它們必須在維護事件期間終止或重新啟動。
    * **Driver Installation**: You are responsible for installing GPU drivers on the VM (unless using Deep Learning VM Images which have them pre-installed).
    * **驅動程式安裝**: 您負責在 VM 上安裝 GPU 驅動程式（除非使用預先安裝了驅動程式的深度學習 VM 映像檔）。

---

### Migrate for Compute Engine
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Operational Excellence - Migration)**. 用於大規模且無縫地將工作負載轉移到雲端。
* **產品重要說明 (Product Description)**:
    * Formerly known as Velostrata, this service enables you to migrate VMs from on-premises (VMware/Hyper-V) or other clouds (AWS/Azure) to Google Compute Engine.
    * 前身為 Velostrata，此服務讓您能夠將 VM 從地端 (VMware/Hyper-V) 或其他雲端 (AWS/Azure) 遷移至 Google Compute Engine。
    * It focuses on "lift and shift" scenarios with minimal downtime.
    * 它專注於具有最短停機時間的「直接轉移 (Lift and Shift)」情境。
* **主要功能 (Main Functions)**:
    * **Agentless Migration**: Often does not require installing agents on the source VMs.
    * **無代理程式遷移**: 通常不需要在來源 VM 上安裝代理程式。
    * **Streaming**: Begins running the VM in the cloud while data is still being copied in the background (within minutes).
    * **串流**: 在背景仍在複製資料的同時，即開始在雲端運行 VM（幾分鐘內）。
    * **Testing**: Allows validating the migration in an isolated cloud environment before committing.
    * **測試**: 允許在提交之前於隔離的雲端環境中驗證遷移。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: A customer needs to evacuate a data center in 2 months.
    * **架構師觀點**: 一位客戶需要在 2 個月內撤出資料中心。
    * You use Migrate for Compute Engine to quickly move hundreds of VMs to GCP without re-architecting them.
    * 您使用 Migrate for Compute Engine 快速將數百個 VM 移動到 GCP，而無需重新架構它們。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Waves**: Migrations are organized into "waves" (batches of VMs).
    * **波次**: 遷移被組織成「波次」（一批 VM）。
    * **Rollback**: Provides a quick rollback mechanism if issues are discovered during the testing phase.
    * **復原**: 如果在測試階段發現問題，提供快速復原機制。

---

### VMware Engine
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Infrastructure & Migration)**. 讓企業能直接利用既有 VMware 投資。
* **產品重要說明 (Product Description)**:
    * Google Cloud VMware Engine (GCVE) is a fully managed service that runs the VMware platform (vSphere, vCenter, vSAN, NSX-T) natively on Google Cloud bare metal.
    * Google Cloud VMware Engine (GCVE) 是一項完全託管的服務，可在 Google Cloud 裸機上原生運行 VMware 平台 (vSphere, vCenter, vSAN, NSX-T)。
    * It allows customers to migrate VMware workloads without refactoring or changing applications.
    * 它允許客戶在不重構或更改應用程式的情況下遷移 VMware 工作負載。
* **主要功能 (Main Functions)**:
    * **Native Integration**: High-bandwidth connection to other GCP services (BigQuery, Cloud Storage) via VPC peering.
    * **原生整合**: 透過 VPC 對等互連與其他 GCP 服務（BigQuery, Cloud Storage）進行高頻寬連線。
    * **Familiar Tools**: Administrators keep using vCenter and other VMware tools they already know.
    * **熟悉的工具**: 管理員繼續使用他們已經熟悉的 vCenter 和其他 VMware 工具。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: An enterprise relies heavily on VMware tools and scripts for operations and DR.
    * **架構師觀點**: 一家企業嚴重依賴 VMware 工具和腳本進行維運和災難復原。
    * Instead of converting VMs to Compute Engine format, you deploy a GCVE Private Cloud and use HCX to extend their on-prem network to GCP.
    * 您部署 GCVE 私有雲並使用 HCX 將其地端網路延伸到 GCP，而不是將 VM 轉換為 Compute Engine 格式。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **License Portability**: Helps avoid the cost of refactoring and retraining staff.
    * **授權可攜性**: 協助避免重構和重新培訓員工的成本。
    * **Dedicated Hardware**: Runs on dedicated nodes, ensuring isolation.
    * **專用硬體**: 在專用節點上運行，確保隔離。

---

### Cloud Run
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Modernization & Cost Optimization)**. 現代化應用開發的首選無伺服器容器平台。
* **產品重要說明 (Product Description)**:
    * Cloud Run is a managed compute platform that lets you run stateless containers that are invocable via HTTP requests.
    * Cloud Run 是一個託管運算平台，讓您可以運行可透過 HTTP 請求呼叫的無狀態容器。
    * It abstracts away all infrastructure management (Serverless).
    * 它抽象化了所有基礎設施管理（無伺服器）。
* **主要功能 (Main Functions)**:
    * **Knative based**: Built on the Knative open-source standard, ensuring portability (avoiding lock-in).
    * **基於 Knative**: 建立在 Knative 開源標準之上，確保可攜性（避免被鎖定）。
    * **Scale to Zero**: Automatically scales down to zero instances when idle.
    * **擴展到零**: 閒置時自動縮減為零個執行個體。
    * **Concurrency**: Handles multiple requests per container instance (unlike Cloud Functions).
    * **並發性**: 每個容器執行個體處理多個請求（與 Cloud Functions 不同）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You have a microservice packaged as a Docker container that handles REST API requests.
    * **架構師觀點**: 您有一個打包為 Docker 容器的微服務，用於處理 REST API 請求。
    * You deploy it to Cloud Run to get automatic SSL, global load balancing (via integration), and pay-per-use billing.
    * 您將其部署到 Cloud Run 以獲得自動 SSL、全球負載平衡（透過整合）和按使用付費的帳單。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Statelessness**: Containers are ephemeral. Any state must be stored in external services like Cloud SQL or Firestore.
    * **無狀態**: 容器是暫時的。任何狀態都必須儲存在外部服務中，如 Cloud SQL 或 Firestore。
    * **Services vs Jobs**: "Services" are for responding to web requests. "Jobs" are for tasks that run to completion (e.g., batch data processing).
    * **服務 vs 作業**: 「服務」用於回應 Web 請求。「作業」用於運行至完成的任務（例如批次資料處理）。

---

### Cloud Functions
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Event-Driven Architecture)**. 輕量級事件驅動架構的核心。
* **產品重要說明 (Product Description)**:
    * Cloud Functions is a lightweight, event-based, serverless compute solution.
    * Cloud Functions 是一個輕量級、基於事件的無伺服器運算解決方案。
    * It allows you to create single-purpose functions that respond to cloud events without managing servers.
    * 它允許您建立單一用途的函式，以回應雲端事件，而無需管理伺服器。
* **主要功能 (Main Functions)**:
    * **Event Triggers**: Can be triggered by HTTP, Cloud Storage (file upload), Pub/Sub (messages), or Firestore (data changes).
    * **事件觸發**: 可以由 HTTP、Cloud Storage（檔案上傳）、Pub/Sub（訊息）或 Firestore（資料變更）觸發。
    * **Language Support**: Supports Node.js, Python, Go, Java, .NET, Ruby, PHP.
    * **語言支援**: 支援 Node.js, Python, Go, Java, .NET, Ruby, PHP。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Every time a user uploads an image to a Cloud Storage bucket, you need to generate a thumbnail.
    * **架構師觀點**: 每當使用者將圖片上傳到 Cloud Storage bucket 時，您都需要產生縮圖。
    * You write a Cloud Function triggered by the `google.storage.object.finalize` event to process the image automatically.
    * 您編寫一個由 `google.storage.object.finalize` 事件觸發的 Cloud Function 來自動處理圖片。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Execution Time**: Has a maximum timeout (e.g., 9 minutes for Gen 1, 60 minutes for Gen 2). Not for long-running processes.
    * **執行時間**: 具有最大逾時限制（例如第一代為 9 分鐘，第二代為 60 分鐘）。不適用於長時間運行的程序。
    * **Gen 2**: Built on Cloud Run and Eventarc, offering higher concurrency and larger instance sizes compared to Gen 1.
    * **第二代**: 建立在 Cloud Run 和 Eventarc 之上，與第一代相比提供更高的並發性和更大的執行個體規模。

---

### Bare Metal Solution
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Specialized Workloads)**. 針對無法虛擬化的傳統重型工作負載。
* **產品重要說明 (Product Description)**:
    * Bare Metal Solution allows you to run specialized workloads (typically Oracle databases) on dedicated hardware located in regional extensions of Google Cloud data centers.
    * Bare Metal Solution 允許您在位於 Google Cloud 資料中心區域擴展的專用硬體上運行專門的工作負載（通常是 Oracle 資料庫）。
    * It provides low-latency access to other GCP services.
    * 它提供對其他 GCP 服務的低延遲存取。
* **主要功能 (Main Functions)**:
    * **Oracle Support**: Specifically designed to run Oracle workloads that have strict licensing or performance requirements not met by VMs.
    * **Oracle 支援**: 專為運行具有 VM 無法滿足的嚴格授權或效能要求的 Oracle 工作負載而設計。
    * **Managed Hardware**: Google manages power, cooling, and hardware; you manage the OS and software (root access).
    * **託管硬體**: Google 管理電源、冷卻和硬體；您管理 OS 和軟體（root 權限）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: A client has a massive Oracle database with licensing that prohibits running on virtual CPUs (cloud vCPUs).
    * **架構師觀點**: 客戶擁有一個龐大的 Oracle 資料庫，其授權禁止在虛擬 CPU (cloud vCPUs) 上運行。
    * You migrate this database to the Bare Metal Solution to comply with licensing while connecting the application layer running on GKE to the database.
    * 您將此資料庫遷移到 Bare Metal Solution 以符合授權要求，同時將運行在 GKE 上的應用程式層連線到該資料庫。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Not Compute Engine**: These are not GCE instances. They are physical servers.
    * **非 Compute Engine**: 這些不是 GCE 執行個體。它們是實體伺服器。
    * **Provisioning**: Takes weeks to provision (unlike VMs which take seconds), as it involves physical hardware setup.
    * **配置**: 配置需要數週時間（不像 VM 需要數秒），因為涉及實體硬體設定。

---

### GCVE (Google Cloud VMware Engine)
* **Knowledge Level**: 1: basics
* **附註**: 此項目與上方的 "VMware Engine" 為同一產品。
* **產品重要說明 (Product Description)**:
    * (See VMware Engine above. Repetitive entry in the list.)
    * (請參閱上方的 VMware Engine。清單中的重複項目。)
    * Focus: Providing a private cloud environment using the VMware stack.
    * 重點：使用 VMware 堆疊提供私有雲環境。
* **主要功能 (Main Functions)**:
    * **vMotion**: Move live VMs from on-prem to GCVE.
    * **vMotion**: 將即時 VM 從地端移動到 GCVE。
    * **Hybrid Cloud**: Unified management across on-prem and cloud.
    * **混合雲**: 跨地端和雲端的統一管理。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Disaster Recovery (DR). Using GCVE as a DR site for on-prem VMware workloads to avoid maintaining a second physical data center.
    * **架構師觀點**: 災難復原 (DR)。使用 GCVE 作為地端 VMware 工作負載的 DR 站點，以避免維護第二個實體資料中心。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Minimum Node Count**: Typically requires a minimum of 3 nodes to start a private cloud cluster.
    * **最低節點數**: 通常至少需要 3 個節點才能啟動私有雲叢集。

---

### Preemptible VMs
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Cost Optimization)**. 用於容錯批次處理的成本節省利器。
* **產品重要說明 (Product Description)**:
    * Preemptible VMs (PVMs) are highly affordable Compute Engine instances that last up to 24 hours.
    * 先佔式 VM (PVM) 是非常經濟實惠的 Compute Engine 執行個體，持續時間最長為 24 小時。
    * Google can stop (preempt) them at any time if it needs the resources back.
    * 如果 Google 需要收回資源，可以隨時停止（搶佔）它們。
    * *Note: Spot VMs are the newer version of Preemptible VMs with more flexible duration (no 24h limit), but the concept is similar.*
    * *註：Spot VM 是先佔式 VM 的較新版本，具有更靈活的持續時間（無 24 小時限制），但概念相似。*
* **主要功能 (Main Functions)**:
    * **Cost Savings**: Up to 80% cheaper than standard instances.
    * **節省成本**: 比標準執行個體便宜高達 80%。
    * **Batch Processing**: Ideal for fault-tolerant workloads like rendering or data analysis.
    * **批次處理**: 適用於容錯工作負載，如渲染或資料分析。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You are running a Hadoop cluster (Dataproc) to process logs.
    * **架構師觀點**: 您正在運行 Hadoop 叢集 (Dataproc) 來處理日誌。
    * You configure the "secondary workers" (which only process data) to be Preemptible VMs. If some die, the job slows down but doesn't fail. This drastically reduces cost.
    * 您將「次要工作節點」（僅處理資料）配置為先佔式 VM。如果有些節點死亡，作業會變慢但不會失敗。這大大降低了成本。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Termination Notice**: You get a 30-second warning (ACPI shutdown signal) before the VM stops. You should use a shutdown script to save state.
    * **終止通知**: 在 VM 停止之前，您會收到 30 秒的警告（ACPI 關機訊號）。您應該使用關機腳本來儲存狀態。
    * **No SLAs**: Preemptible VMs are excluded from the Compute Engine SLA.
    * **無 SLA**: 先佔式 VM 不包含在 Compute Engine SLA 中。

---

### Sole-tenant Nodes
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Compliance & Security)**. 針對嚴格隔離與合規需求的實體獨占方案。
* **產品重要說明 (Product Description)**:
    * Sole-tenant nodes provide a physical Compute Engine server that is dedicated to hosting only your project's VMs.
    * 獨占節點提供一個實體 Compute Engine 伺服器，專門用於託管您專案的 VM。
    * It ensures that your VMs do not share the host hardware with other customers.
    * 它確保您的 VM 不會與其他客戶共享主機硬體。
* **主要功能 (Main Functions)**:
    * **Isolation**: Hardware isolation for compliance (e.g., PCI DSS, HIPAA) or sensitive workloads.
    * **隔離**: 用於合規性（例如 PCI DSS, HIPAA）或敏感工作負載的硬體隔離。
    * **Licensing**: Supports "Bring Your Own License" (BYOL) for per-core or per-socket licensed software (e.g., Windows, SQL Server).
    * **授權**: 支援按核心或按插槽授權軟體（例如 Windows, SQL Server）的「自帶授權」(BYOL)。
    * **Placement Control**: Gives you control over which specific node a VM runs on.
    * **放置控制**: 讓您可以控制 VM 運行在哪個特定節點上。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You have existing Windows Server licenses that are charged per physical CPU socket.
    * **架構師觀點**: 您現有的 Windows Server 授權是按實體 CPU 插槽收費的。
    * Moving to standard shared cloud VMs would invalidate these licenses. Using Sole-tenant nodes allows you to count the physical sockets and reuse your licenses.
    * 移至標準共享雲端 VM 將使這些授權無效。使用獨占節點允許您計算實體插槽並重複使用您的授權。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Node Groups**: You manage node groups, and then provision VMs onto those groups using "Node Affinity" labels.
    * **節點群組**: 您管理節點群組，然後使用「節點親和性 (Node Affinity)」標籤將 VM 配置到這些群組上。
    * **Overcommit**: You can overcommit CPU on sole-tenant nodes to increase density (running more vCPUs than physical threads), trading performance for cost.
    * **超額使用**: 您可以在獨占節點上超額使用 CPU 以增加密度（運行的 vCPU 多於實體執行緒），以效能換取成本。

---

### Local SSD
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Performance Efficiency)**. 極致效能需求的暫存層。
* **產品重要說明 (Product Description)**:
    * Local SSDs are physically attached to the server that hosts your VM instance.
    * Local SSD 是實體連接到託管您 VM 執行個體的伺服器上。
    * They offer very high input/output operations per second (IOPS) and very low latency compared to Persistent Disks.
    * 與持久磁碟相比，它們提供非常高的每秒輸入/輸出操作 (IOPS) 和非常低的延遲。
* **主要功能 (Main Functions)**:
    * **High Performance**: Designed for scratch data, caching, or data processing that requires speed.
    * **高效能**: 專為需要速度的暫存資料、快取或資料處理而設計。
    * **Ephemeral**: Data persists only while the instance is running.
    * **暫時性**: 資料僅在執行個體運行時保留。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You are running a high-frequency trading application or a NoSQL database cache (like Redis).
    * **架構師觀點**: 您正在運行高頻交易應用程式或 NoSQL 資料庫快取（如 Redis）。
    * You use Local SSD for the cache layer to achieve sub-millisecond latency, while persisting the actual data to a standard Persistent Disk for safety.
    * 您使用 Local SSD 作為快取層以實現亞毫秒級延遲，同時將實際資料持久化到標準持久磁碟以確保安全。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Data Loss Risks**: If you stop (shutdown) the instance, the data on Local SSD is discarded. Data survives a reboot (guest OS reset), but not a host error or instance stop.
    * **資料遺失風險**: 如果您停止（關機）執行個體，Local SSD 上的資料將被丟棄。資料可以在重新啟動（Guest OS 重置）中存活，但不能在主機錯誤或執行個體停止中存活。
    * **Interface**: Supports both SCSI and NVMe interfaces (NVMe is faster).
    * **介面**: 支援 SCSI 和 NVMe 介面（NVMe 較快）。

---

### VM Manager
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security & Operational Excellence)**. 大規模機隊管理的自動化工具。
* **產品重要說明 (Product Description)**:
    * VM Manager is a suite of tools that can be used to manage operating systems for large fleets of VMs.
    * VM Manager 是一套工具，可用於管理大型 VM 機隊的作業系統。
    * It simplifies patch management, configuration management, and inventory collection.
    * 它簡化了修補程式管理、組態管理和清單收集。
* **主要功能 (Main Functions)**:
    * **OS Patch Management**: Automatically applies OS patches across VMs on a schedule.
    * **OS 修補程式管理**: 依排程自動在 VM 之間套用 OS 修補程式。
    * **OS Inventory Management**: Collects and lists OS details and installed packages.
    * **OS 清單管理**: 收集並列出 OS 詳細資訊和已安裝的套件。
    * **OS Configuration Management**: Enforces desired states (e.g., ensuring a specific software is installed).
    * **OS 組態管理**: 強制執行所需狀態（例如，確保安裝了特定軟體）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You manage 500 Linux VMs and need to ensure they all have the latest security patches every month.
    * **架構師觀點**: 您管理 500 個 Linux VM，並需要確保它們每個月都有最新的安全性修補程式。
    * Instead of SSH-ing into each one, you set up a VM Manager Patch Policy to apply updates during a maintenance window automatically.
    * 您無需透過 SSH 進入每一個 VM，而是設定 VM Manager 修補程式政策，以便在維護視窗期間自動套用更新。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Agent Required**: Requires the OS Config agent to be installed and running on the VMs.
    * **代理程式需求**: 需要在 VM 上安裝並運行 OS Config 代理程式。
    * **Scope**: Can target VMs based on labels, zones, or specific instances.
    * **範圍**: 可以根據標籤、可用區或特定執行個體來鎖定 VM。

---

### Sharing OS images across projects
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security & Operational Excellence)**. 建立黃金映像檔 (Golden Image) 策略的基礎。
* **產品重要說明 (Product Description)**:
    * In a multi-project environment, it is best practice to centralize the management of custom OS images (Golden Images).
    * 在多專案環境中，最佳實務是集中管理自定義 OS 映像檔（黃金映像檔）。
    * This allows one "Image Factory" project to share approved images with other "Consumer" projects.
    * 這允許一個「映像檔工廠」專案與其他「消費者」專案共享已核准的映像檔。
* **主要功能 (Main Functions)**:
    * **Centralized Governance**: Ensures all projects use secure, pre-configured OS images.
    * **集中治理**: 確保所有專案使用安全的、預先配置的 OS 映像檔。
    * **IAM Control**: Uses specific IAM roles to grant access to images without granting access to the project itself.
    * **IAM 控制**: 使用特定的 IAM 角色授予對映像檔的存取權，而不授予對專案本身的存取權。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: The security team builds a hardened Linux image with specific monitoring agents.
    * **架構師觀點**: 安全團隊建立了一個帶有特定監控代理程式的強化 Linux 映像檔。
    * They store it in a dedicated `images-project`. Development teams in `dev-project-a` and `dev-project-b` are granted the `Compute Image User` role on the `images-project` to use this image for their VMs.
    * 他們將其儲存在專用的 `images-project` 中。`dev-project-a` 和 `dev-project-b` 中的開發團隊被授予 `images-project` 上的 `Compute Image User` 角色，以便為其 VM 使用此映像檔。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Image Families**: You should point users to an "Image Family" (e.g., `production-v1`) rather than a specific version. This allows you to update the underlying image without breaking consumer scripts.
    * **映像檔系列**: 您應該將使用者指向「映像檔系列」（例如 `production-v1`）而不是特定版本。這允許您更新底層映像檔而不會破壞消費者的腳本。
    * **IAM Role**: The key role is `roles/compute.imageUser`.
    * **IAM 角色**: 關鍵角色是 `roles/compute.imageUser`。

---

### VM Serial Console
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Reliability - Troubleshooting)**. 排除 VM 啟動與網路故障的最後手段。
* **產品重要說明 (Product Description)**:
    * The interactive serial console allows you to connect to a VM's serial port.
    * 互動式序列主控台允許您連線到 VM 的序列埠。
    * It enables troubleshooting when you cannot connect via SSH or RDP (e.g., firewall issues, bad network config).
    * 當您無法透過 SSH 或 RDP 連線時（例如防火牆問題、錯誤的網路配置），它可以用於疑難排解。
* **主要功能 (Main Functions)**:
    * **Direct Access**: Interacts with the VM kernel and bootloader directly.
    * **直接存取**: 直接與 VM 核心和開機載入程式互動。
    * **Boot Logs**: Viewing the serial port output is often the only way to see why a VM failed to boot (Kernel Panic).
    * **開機日誌**: 檢視序列埠輸出通常是查看 VM 為何無法開機（核心恐慌）的唯一方法。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: A VM becomes unreachable after a junior admin modified the `iptables` firewall rules inside the OS.
    * **架構師觀點**: 在初級管理員修改了 OS 內部的 `iptables` 防火牆規則後，VM 變得無法連線。
    * Since SSH is blocked, you use the Serial Console to log in as root (if configured) and revert the firewall changes.
    * 由於 SSH 被封鎖，您使用序列主控台以 root 身分登入（如果已配置）並還原防火牆變更。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Not Enabled by Default**: For security, interactive access is disabled by default. It must be enabled via metadata (`serial-port-enable=1`).
    * **預設未啟用**: 為了安全起見，互動式存取預設為停用。必須透過 Metadata 啟用 (`serial-port-enable=1`)。
    * **Organization Policy**: Often disabled at the organization level (`constraints/compute.disableSerialPortAccess`) in high-security environments.
    * **機構政策**: 在高安全性環境中，通常在機構層級停用 (`constraints/compute.disableSerialPortAccess`)。

---

## Storage

### Cloud Storage
* **Knowledge Level**: 3: advanced
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Cost, Reliability, Security, Performance pillars)**. 這是 GCP 最核心的物件儲存服務，幾乎涉及所有架構支柱。
* **產品重要說明 (Product Description)**:
    * Cloud Storage is a globally unified, scalable, and highly durable object storage service for unstructured data.
    * Cloud Storage 是一個全球統一、可擴展且高度耐用的物件儲存服務，用於儲存非結構化資料。
    * It is designed for 99.999999999% (11 nines) annual durability.
    * 它的設計目標是提供 99.999999999% (11 個 9) 的年度耐用性。
* **主要功能 (Main Functions)**:
    * **Storage Classes**: Standard (hot data), Nearline (once a month), Coldline (once a quarter), Archive (once a year) for cost optimization.
    * **儲存類別**: 標準 (熱資料)、Nearline (每月一次)、Coldline (每季一次)、Archive (每年一次) 以進行成本優化。
    * **Lifecycle Management**: Automatically transitions objects to cheaper classes or deletes them based on rules (e.g., age).
    * **生命週期管理**: 根據規則（例如保存期限）自動將物件轉移到更便宜的類別或刪除它們。
    * **Object Versioning**: Protects against accidental overwrites or deletions by keeping history.
    * **物件版本控制**: 透過保留歷史記錄來防止意外覆寫或刪除。
    * **Hosting**: Can host static websites directly.
    * **託管**: 可以直接託管靜態網站。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You are designing a Data Lake for a global analytics platform.
    * **架構師觀點**: 您正在為全球分析平台設計資料湖。
    * You use a **Multi-Region** bucket to ingest data from IoT devices worldwide for low latency. You apply a Lifecycle Policy to move data to Coldline after 30 days for analysis archival, ensuring cost efficiency while maintaining global availability.
    * 您使用**多地區 (Multi-Region)** bucket 來接收來自全球 IoT 裝置的資料以實現低延遲。您套用生命週期政策，在 30 天後將資料移動到 Coldline 進行分析封存，在確保成本效益的同時維持全球可用性。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Consistency**: Cloud Storage offers strong global consistency for read-after-write, listing, and metadata updates. This is a key differentiator from eventual consistency models in some other clouds.
    * **一致性**: Cloud Storage 為寫後讀 (read-after-write)、列表和 Metadata 更新提供強大的全球一致性。這是與其他一些雲端中最終一致性模型的一個關鍵區別。
    * **Uniform Bucket-Level Access**: Google recommends enabling this to disable ACLs (Access Control Lists) and manage access solely via IAM.
    * **統一 bucket 層級存取權**: Google 建議啟用此功能以停用 ACL (存取控制清單)，並僅透過 IAM 管理存取權。
    * **Dual-region vs Multi-region**: Dual-region is optimized for specific High Availability (HA) and Disaster Recovery (DR) pairs (e.g., Tokyo and Osaka), whereas Multi-region is for broad geo-redundancy.
    * **雙地區與多地區**: 雙地區針對特定的高可用性 (HA) 和災難復原 (DR) 配對進行優化（例如東京和大阪），而多地區則用於廣泛的地理備援。

---

### GCS Bucket Locks
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security & Compliance pillar)**. 針對資料保留法規 (Data Retention) 的強制性控制。
* **產品重要說明 (Product Description)**:
    * Bucket Lock allows you to configure a data retention policy for a Cloud Storage bucket that governs how long objects must be retained.
    * Bucket Lock 允許您為 Cloud Storage bucket 配置資料保留政策，以管理物件必須保留多長時間。
    * It enables WORM (Write Once, Read Many) compliance.
    * 它實現了 WORM (一次寫入，多次讀取) 的合規性。
* **主要功能 (Main Functions)**:
    * **Retention Policy**: Specifies a minimum retention period for objects in the bucket.
    * **保留政策**: 指定 bucket 中物件的最短保留期限。
    * **Locking**: Once a policy is "locked," it cannot be removed or reduced (extended only).
    * **鎖定**: 一旦政策被「鎖定」，就無法移除或縮減（只能延長）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: A financial institution must keep all transaction logs for 7 years due to government regulations.
    * **架構師觀點**: 由於政府法規，一家金融機構必須將所有交易日誌保留 7 年。
    * You apply a Bucket Lock with a 7-year retention period. This prevents even administrators with full permissions from deleting these logs before the time is up.
    * 您套用一個保留期為 7 年的 Bucket Lock。這可以防止即使擁有完整權限的管理員在時間到期之前刪除這些日誌。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Holds**: Besides retention policies, you can place "Legal Holds" on specific objects to prevent deletion indefinitely until the hold is removed.
    * **保留 (Holds)**: 除了保留政策外，您還可以對特定物件設定「法律保留」，以無限期防止刪除，直到保留被移除。
    * **Permanence**: Be extremely careful when locking a policy. If you lock a bucket for 10 years, you cannot delete the bucket unless it is empty, and you cannot delete the objects until they age out.
    * **永久性**: 鎖定政策時要非常小心。如果您將 bucket 鎖定 10 年，除非 bucket 為空，否則您無法刪除該 bucket，並且在物件過期之前您也無法刪除這些物件。

---

### Cloud Filestore
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Infrastructure & Migration pillar)**. 解決傳統應用程式對共用檔案系統的依賴。
* **產品重要說明 (Product Description)**:
    * Cloud Filestore is a managed file storage service for applications that require a file system interface and a shared file system for data.
    * Cloud Filestore 是一個託管檔案儲存服務，適用於需要檔案系統介面和共用檔案系統來儲存資料的應用程式。
    * It supports the NFSv3 protocol.
    * 它支援 NFSv3 協定。
* **主要功能 (Main Functions)**:
    * **Managed NFS**: Fully managed Network File System (NFS) servers.
    * **託管 NFS**: 完全託管的網路檔案系統 (NFS) 伺服器。
    * **Compute Engine Integration**: Mounts easily to GCE VMs as a network drive.
    * **Compute Engine 整合**: 輕鬆掛載到 GCE VM 作為網路磁碟機。
    * **GKE Integration**: Provides persistent storage for containers (ReadWriteMany volumes).
    * **GKE 整合**: 為容器提供持久儲存 (ReadWriteMany 磁碟區)。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You are migrating a legacy CMS (Content Management System) like WordPress or Drupal to GKE.
    * **架構師觀點**: 您正在將舊版 CMS（內容管理系統，如 WordPress 或 Drupal）遷移到 GKE。
    * The application needs a shared directory where multiple web server pods can read and write media files simultaneously. You provision a Filestore instance and mount it as a Persistent Volume.
    * 應用程式需要一個共用目錄，讓多個 Web 伺服器 Pod 可以同時讀取和寫入媒體檔案。您配置一個 Filestore 執行個體並將其掛載為持久磁碟區。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Service Tiers**: Basic (HDD/SSD, Zonal availability) vs Enterprise (Regional HA).
    * **服務層級**: Basic (HDD/SSD，區域可用性) 與 Enterprise (地區性 HA)。
    * **Performance**: Performance (throughput/IOPS) usually scales with capacity. Larger instances are faster.
    * **效能**: 效能 (傳輸量/IOPS) 通常隨容量擴展。較大的執行個體速度較快。

---

## Databases

### Cloud Bigtable
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Performance & Reliability pillars)**. 針對極大規模、高吞吐量數據的 NoSQL 首選。
* **產品重要說明 (Product Description)**:
    * Cloud Bigtable is a fully managed, scalable NoSQL database service for large analytical and operational workloads.
    * Cloud Bigtable 是一個完全託管、可擴展的 NoSQL 資料庫服務，適用於大型分析和維運工作負載。
    * It is ideal for storing very large amounts of data (Petabytes) and accessing it with very low latency.
    * 它非常適合儲存極大量的資料 (Petabytes) 並以極低的延遲進行存取。
* **主要功能 (Main Functions)**:
    * **HBase Compatible**: Uses the Apache HBase API, making it easy to migrate existing Hadoop/HBase workloads.
    * **HBase 相容**: 使用 Apache HBase API，使得遷移現有的 Hadoop/HBase 工作負載變得容易。
    * **High Throughput**: Designed for millions of reads/writes per second.
    * **高吞吐量**: 專為每秒數百萬次的讀取/寫入而設計。
    * **Seamless Scaling**: Scale storage and throughput linearly by adding nodes without downtime.
    * **無縫擴展**: 透過新增節點來線性擴展儲存和吞吐量，無需停機時間。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You are designing an IoT platform ingesting sensor data from millions of devices or an AdTech platform tracking user clicks in real-time.
    * **架構師觀點**: 您正在設計一個從數百萬個裝置接收感測器資料的 IoT 平台，或一個即時追蹤使用者點擊的廣告科技平台。
    * Relational databases (SQL) cannot handle the write throughput. You choose Bigtable because it offers single-digit millisecond latency and handles the high velocity of incoming data.
    * 關聯式資料庫 (SQL) 無法處理這種寫入吞吐量。您選擇 Bigtable 是因為它提供個位數毫秒的延遲，並能處理高速傳入的資料。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Schema Design (Key Visualizer)**: Designing the "Row Key" is critical. Poor key design leads to "hotspotting" (overloading specific nodes). Sequential keys (e.g., timestamps) are bad; hashed or reversed keys are better.
    * **結構描述設計 (Key Visualizer)**: 設計「列鍵 (Row Key)」至關重要。糟糕的金鑰設計會導致「熱點 (Hotspotting)」（特定節點過載）。順序鍵（例如時間戳）是不好的；雜湊或反轉鍵比較好。
    * **Separation of Compute and Storage**: Compute (Nodes) is separated from Storage (Colossus). This allows you to resize the cluster instantly without moving data.
    * **運算與儲存分離**: 運算 (節點) 與儲存 (Colossus) 是分開的。這允許您立即調整叢集大小而無需移動資料。

---

### Cloud Firestore
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Modernization)**. 現代化 Web 與行動應用的後端資料庫。
* **產品重要說明 (Product Description)**:
    * Cloud Firestore is a flexible, scalable NoSQL cloud database to store and sync data for client- and server-side development.
    * Cloud Firestore 是一個靈活、可擴展的 NoSQL 雲端資料庫，用於為客戶端和伺服器端開發儲存和同步資料。
    * It is the successor to Datastore and the realtime database for Firebase.
    * 它是 Datastore 和 Firebase 即時資料庫的繼任者。
* **主要功能 (Main Functions)**:
    * **Real-time Synchronization**: Automatically syncs data across connected devices (Web, iOS, Android).
    * **即時同步**: 自動在連線的裝置（Web, iOS, Android）之間同步資料。
    * **Offline Support**: Caches data on the device, allowing apps to work offline and sync when connectivity returns.
    * **離線支援**: 在裝置上快取資料，允許應用程式離線工作並在連線恢復時同步。
    * **Strong Consistency**: Unlike many NoSQL databases, it offers strong consistency.
    * **強一致性**: 與許多 NoSQL 資料庫不同，它提供強一致性。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You are building a mobile chat application or a collaborative inventory management tool.
    * **架構師觀點**: 您正在建立一個行動聊天應用程式或協作庫存管理工具。
    * You use Firestore because users need to see updates instantly without refreshing (Real-time) and need to continue working when they enter a subway tunnel (Offline mode).
    * 您使用 Firestore 是因為使用者需要即時看到更新而無需重新整理（即時），並且需要在進入地鐵隧道時繼續工作（離線模式）。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Native Mode vs Datastore Mode**: You must choose one mode per project. "Native" is for mobile/web apps (features real-time + offline). "Datastore Mode" is for server-side apps requiring high write throughput (compatible with old Datastore APIs).
    * **原生模式 vs Datastore 模式**: 您必須為每個專案選擇一種模式。「原生」適用於行動/Web 應用程式（具有即時 + 離線功能）。「Datastore 模式」適用於需要高寫入吞吐量的伺服器端應用程式（與舊版 Datastore API 相容）。
    * **Query Limitations**: Queries are shallow (cannot join collections easily) and rely heavily on indexes. You cannot filter on multiple fields without a composite index.
    * **查詢限制**: 查詢是淺層的（無法輕易 Join 集合）且嚴重依賴索引。如果沒有複合索引，您無法針對多個欄位進行過濾。

---

### Memorystore for Memcached
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Performance Efficiency)**. 提升應用程式回應速度的快取層。
* **產品重要說明 (Product Description)**:
    * Memorystore for Memcached is a fully managed Memcached service.
    * Memorystore for Memcached 是一個完全託管的 Memcached 服務。
    * It is used for in-memory caching to speed up applications by serving frequently accessed data from RAM.
    * 它用於記憶體內快取，透過從 RAM 提供頻繁存取的資料來加速應用程式。
* **主要功能 (Main Functions)**:
    * **Open Source Compatibility**: Fully compatible with the Memcached protocol.
    * **開源相容性**: 與 Memcached 協定完全相容。
    * **Auto-discovery**: Simplify endpoint management.
    * **自動探索**: 簡化端點管理。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You are migrating a legacy PHP/Python application that already uses Memcached for session management.
    * **架構師觀點**: 您正在遷移已經使用 Memcached 進行工作階段 (Session) 管理的舊版 PHP/Python 應用程式。
    * To perform a "lift and shift" without code changes, you provision Memorystore for Memcached instead of managing your own Memcached servers on VMs.
    * 為了在不更改程式碼的情況下執行「直接轉移」，您配置 Memorystore for Memcached，而不是在 VM 上管理自己的 Memcached 伺服器。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **No Persistence**: Memcached is purely volatile. If the node restarts, data is lost. It is a cache, not a durable store.
    * **無持久性**: Memcached 純粹是揮發性的。如果節點重新啟動，資料就會遺失。它是快取，不是持久儲存。
    * **Simple Key-Value**: Unlike Redis, it supports only simple string key-values, no complex data structures.
    * **簡單鍵值**: 與 Redis 不同，它僅支援簡單的字串鍵值，不支援複雜的資料結構。

---

### Memorystore for Redis
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Performance Efficiency)**. 功能豐富的高階快取與記憶體資料庫。
* **產品重要說明 (Product Description)**:
    * Memorystore for Redis is a fully managed service powered by the Redis in-memory data store.
    * Memorystore for Redis 是一項由 Redis 記憶體內資料儲存支援的完全託管服務。
    * It offers rich data structures and persistence options, unlike Memcached.
    * 與 Memcached 不同，它提供豐富的資料結構和持久性選項。
* **主要功能 (Main Functions)**:
    * **High Availability**: Standard Tier provides a primary and replica instance across zones with automatic failover.
    * **高可用性**: 標準層提供跨可用區的主執行個體和複本執行個體，並具有自動容錯移轉功能。
    * **Advanced Structures**: Supports lists, sets, sorted sets, hashes, bitmaps, etc.
    * **進階結構**: 支援列表、集合、排序集合、雜湊、點陣圖等。
    * **Persistence**: Supports RDB snapshots to disk (optional).
    * **持久性**: 支援 RDB 快照到磁碟（選用）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You are building a gaming leaderboard or a shopping cart service.
    * **架構師觀點**: 您正在建立遊戲排行榜或購物車服務。
    * You choose Redis because its "Sorted Set" data structure is perfect for leaderboards, and its HA capabilities ensure the cart data isn't lost if a zone fails.
    * 您選擇 Redis 是因為它的「排序集合」資料結構非常適合排行榜，而且它的 HA 功能確保如果可用區發生故障，購物車資料不會遺失。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Single Threaded**: Redis is largely single-threaded. Scaling is usually done by scaling up (larger instance) or using Read Replicas (now supported in newer tiers/versions).
    * **單執行緒**: Redis 在很大程度上是單執行緒的。擴展通常是透過擴大（更大的執行個體）或使用讀取複本（現在較新的層級/版本支援）來完成的。
    * **Cluster Mode**: Memorystore for Redis Cluster (fully managed) allows sharding data across multiple nodes for horizontal scaling (Preview/GA status changes frequently, check current status).
    * **叢集模式**: Memorystore for Redis Cluster（完全託管）允許跨多個節點分片資料以進行水平擴展（預覽/GA 狀態經常變化，請檢查目前狀態）。

---

### Cloud Spanner
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Reliability & Scalability pillars)**. 結合 SQL 與 NoSQL 優點的獨特資料庫，是全球一致性架構的核心。
* **產品重要說明 (Product Description)**:
    * Cloud Spanner is a fully managed, mission-critical, relational database service that offers transactional consistency at a global scale.
    * Cloud Spanner 是一個完全託管、關鍵任務的關聯式資料庫服務，可在全球規模上提供交易一致性。
    * It combines the benefits of relational database structure (SQL, ACID transactions) with non-relational horizontal scale.
    * 它結合了關聯式資料庫結構（SQL、ACID 交易）與非關聯式水平擴展的優點。
* **主要功能 (Main Functions)**:
    * **Global Consistency**: Offers strong external consistency even across regions.
    * **全球一致性**: 即使跨區域也能提供強大的外部一致性。
    * **Horizontal Scaling**: Scales to unlimited size by sharding data automatically.
    * **水平擴展**: 透過自動分片資料來擴展到無限大小。
    * **High Availability**: Up to 99.999% availability SLA.
    * **高可用性**: 高達 99.999% 的可用性 SLA。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You are building a global banking ledger or inventory system for a multinational retailer.
    * **架構師觀點**: 您正在為一家跨國零售商建立全球銀行分類帳或庫存系統。
    * You cannot afford inconsistent data (selling the same item twice in different countries) and need SQL semantics. Cloud SQL cannot scale writes globally. Spanner is the only choice that provides Global ACID transactions.
    * 您無法承受資料不一致（在不同國家重複銷售同一件商品）並且需要 SQL 語意。Cloud SQL 無法在全球範圍內擴展寫入。Spanner 是唯一提供全球 ACID 交易的選擇。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **TrueTime**: Spanner relies on atomic clocks and GPS to synchronize time across data centers, enabling its consistency model.
    * **TrueTime**: Spanner 依賴原子鐘和 GPS 來同步資料中心之間的時間，從而實現其一致性模型。
    * **Cost**: It is expensive. It is generally not for small workloads.
    * **成本**: 它很昂貴。通常不適合小型工作負載。
    * **Primary Keys**: Like Bigtable, primary key choice dictates data distribution (sharding). Sequential keys cause hotspots.
    * **主鍵**: 像 Bigtable 一樣，主鍵的選擇決定了資料分佈（分片）。順序鍵會導致熱點。

---

### Cloud SQL
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Reliability & Migration)**. 傳統關聯式資料庫上雲的標準解決方案。
* **產品重要說明 (Product Description)**:
    * Cloud SQL is a fully managed relational database service for MySQL, PostgreSQL, and SQL Server.
    * Cloud SQL 是一個完全託管的關聯式資料庫服務，支援 MySQL, PostgreSQL 和 SQL Server。
    * It is the easiest way to run traditional relational workloads on GCP without managing the OS or database software updates.
    * 這是在 GCP 上運行傳統關聯式工作負載的最簡單方法，無需管理作業系統或資料庫軟體更新。
* **主要功能 (Main Functions)**:
    * **Automated Backups & Patching**: Google handles maintenance windows and daily backups.
    * **自動備份與修補**: Google 處理維護視窗和每日備份。
    * **High Availability (HA)**: Automatic failover to a standby instance in another zone.
    * **高可用性 (HA)**: 自動容錯移轉到另一個可用區的待命執行個體。
    * **Read Replicas**: Create copies to scale read traffic (not write traffic).
    * **讀取複本**: 建立複本以擴展讀取流量（而非寫入流量）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You are migrating a typical web application (e.g., WordPress, Magento, Django) from an on-premise server.
    * **架構師觀點**: 您正在將典型的 Web 應用程式（例如 WordPress, Magento, Django）從地端伺服器遷移。
    * You use Cloud SQL for MySQL or PostgreSQL to lift-and-shift the backend database with minimal configuration changes.
    * 您使用 Cloud SQL for MySQL 或 PostgreSQL 以最小的配置變更將後端資料庫進行直接轉移 (lift-and-shift)。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Scaling Limits**: Cloud SQL scales *vertically* (bigger machine). It does not scale *horizontally* for writes (use Spanner for that).
    * **擴展限制**: Cloud SQL 進行*垂直*擴展（更大的機器）。它不支援寫入的*水平*擴展（如需此功能請使用 Spanner）。
    * **Cloud SQL Proxy**: The recommended way to connect safely from GKE, Cloud Run, or App Engine without managing IP allowlists.
    * **Cloud SQL Auth Proxy**: 這是從 GKE, Cloud Run 或 App Engine 安全連線的推薦方式，無需管理 IP 允許清單。
    * **Storage Auto-increase**: You can configure storage to grow automatically, but you cannot shrink it back down.
    * **儲存空間自動增加**: 您可以設定儲存空間自動增長，但無法將其縮小。

---

### Datastore
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Modernization)**. 應用於特定舊版系統或需要簡易 NoSQL 儲存的場景。
* **產品重要說明 (Product Description)**:
    * Datastore is a highly scalable NoSQL database for your applications.
    * Datastore 是一個高度可擴展的 NoSQL 資料庫，適用於您的應用程式。
    * *Note: It is essentially the predecessor to Firestore in Datastore mode. New projects generally use Firestore.*
    * *註：它本質上是 Datastore 模式下 Firestore 的前身。新專案通常使用 Firestore。*
* **主要功能 (Main Functions)**:
    * **Schemaless**: No fixed structure for data entities.
    * **無結構描述**: 資料實體沒有固定的結構。
    * **ACID Transactions**: Supports transactions across multiple entities.
    * **ACID 交易**: 支援跨多個實體的交易。
    * **SQL-like Queries**: Supports GQL (Google Query Language) for retrieving objects.
    * **類 SQL 查詢**: 支援 GQL (Google 查詢語言) 來檢索物件。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You are maintaining a legacy App Engine (Python 2.7 or Java 8) application built 5 years ago.
    * **架構師觀點**: 您正在維護一個 5 年前建立的舊版 App Engine (Python 2.7 或 Java 8) 應用程式。
    * It relies heavily on Datastore (NDB library). You continue to use Datastore for continuity, knowing that under the hood, Google has upgraded the infrastructure to Firestore technology.
    * 它嚴重依賴 Datastore (NDB 函式庫)。您繼續使用 Datastore 以保持連續性，並知道 Google 在底層已將基礎設施升級為 Firestore 技術。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Index Explosion**: A common pitfall where defining too many indexes on a property with many values causes write costs and latency to skyrocket.
    * **索引爆炸**: 一個常見的陷阱，即在具有許多值的屬性上定義過多索引，會導致寫入成本和延遲急劇上升。
    * **Consistency**: Historically used eventual consistency for some queries; Firestore in Datastore mode now provides strong consistency.
    * **一致性**: 歷史上某些查詢使用最終一致性；Datastore 模式下的 Firestore 現在提供強一致性。

---

### Database Migration Service
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Migration)**. 簡化資料庫上雲流程的關鍵工具。
* **產品重要說明 (Product Description)**:
    * Database Migration Service (DMS) is a serverless, easy-to-use tool to migrate databases to Cloud SQL or AlloyDB.
    * Database Migration Service (DMS) 是一個無伺服器、易於使用的工具，可將資料庫遷移至 Cloud SQL 或 AlloyDB。
    * It supports migrations from on-premises, AWS RDS, or other cloud providers.
    * 它支援從地端、AWS RDS 或其他雲端供應商進行遷移。
* **主要功能 (Main Functions)**:
    * **Homogeneous Migration**: Focuses on MySQL to MySQL, PostgreSQL to PostgreSQL migrations.
    * **同質遷移**: 專注於 MySQL 到 MySQL、PostgreSQL 到 PostgreSQL 的遷移。
    * **Continuous Replication**: Keeps source and destination in sync for minimal downtime cutover.
    * **持續複製**: 保持來源和目標同步，以實現最短停機時間的切換。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You need to move a production MySQL database from AWS RDS to Cloud SQL.
    * **架構師觀點**: 您需要將正式環境的 MySQL 資料庫從 AWS RDS 移動到 Cloud SQL。
    * You use DMS to set up a replication stream. Once the data is synced and the lag is zero, you stop writes to the source and promote the Cloud SQL instance to primary.
    * 您使用 DMS 設定複製串流。一旦資料同步且延遲為零，您停止對來源的寫入並將 Cloud SQL 執行個體升級為主機。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Connectivity**: Requires setting up connectivity (VPC Peering, VPN, or public IP allowlists) so DMS can reach the source database.
    * **連線能力**: 需要設定連線（VPC 對等互連、VPN 或公共 IP 允許清單），以便 DMS 可以到達來源資料庫。
    * **CDC**: Uses native replication capabilities (like MySQL binlogs or PostgreSQL WAL files) for Change Data Capture.
    * **CDC**: 使用原生複製功能（如 MySQL binlogs 或 PostgreSQL WAL 檔案）進行變更資料擷取 (Change Data Capture)。

---

### Firebase
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Modernization)**. 行動與 Web 應用程式開發的一站式平台。
* **產品重要說明 (Product Description)**:
    * Firebase is a comprehensive platform for building mobile and web applications.
    * Firebase 是一個用於建立行動和 Web 應用程式的綜合平台。
    * It includes databases (Firestore, Realtime Database), authentication, hosting, storage, and analytics.
    * 它包含資料庫（Firestore, Realtime Database）、身分驗證、託管、儲存和分析。
* **主要功能 (Main Functions)**:
    * **Firebase Authentication**: Easy login integration (Google, Facebook, Email/Password).
    * **Firebase Authentication**: 簡單的登入整合（Google, Facebook, 電子郵件/密碼）。
    * **Cloud Messaging (FCM)**: Send notifications to devices.
    * **Cloud Messaging (FCM)**: 傳送通知到裝置。
    * **Crashlytics**: Real-time crash reporting.
    * **Crashlytics**: 即時當機報告。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: A startup wants to launch an MVP (Minimum Viable Product) mobile app quickly.
    * **架構師觀點**: 一家新創公司希望快速推出 MVP（最小可行產品）行動應用程式。
    * You choose Firebase to handle the entire backend (Auth, DB, Storage) so the team can focus solely on the frontend UI/UX logic.
    * 您選擇 Firebase 來處理整個後端（驗證、資料庫、儲存），以便團隊可以專注於前端 UI/UX 邏輯。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **GCP Integration**: Firebase projects are GCP projects. You can access Firebase resources (like Cloud Storage buckets or Firestore data) from GCP tools.
    * **GCP 整合**: Firebase 專案即 GCP 專案。您可以從 GCP 工具存取 Firebase 資源（如 Cloud Storage buckets 或 Firestore 資料）。
    * **Free Tier**: Offers a generous free tier for development, making it popular for prototyping.
    * **免費層級**: 為開發提供大方的免費層級，使其在原型設計中很受歡迎。

---

## Migration

### BigQuery Data Transfer Service
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Operational Excellence - Automation)**. 自動化資料擷取流程，減少手動 ETL 維護。
* **產品重要說明 (Product Description)**:
    * BigQuery Data Transfer Service automates the movement of data into BigQuery on a scheduled, managed basis.
    * BigQuery Data Transfer Service 會以排程、託管的方式自動將資料移動到 BigQuery 中。
    * It is primarily used for importing data from SaaS applications (like Google Ads, YouTube) and other data warehouses (like Teradata, Amazon Redshift).
    * 它主要用於從 SaaS 應用程式（如 Google Ads, YouTube）和其他資料倉儲（如 Teradata, Amazon Redshift）匯入資料。
* **主要功能 (Main Functions)**:
    * **SaaS Connectors**: Pre-built connectors for Google ecosystem (Ads, Play, YouTube) and external services (Amazon S3).
    * **SaaS 連接器**: 針對 Google 生態系統（Ads, Play, YouTube）和外部服務 (Amazon S3) 的預建連接器。
    * **Automated Scheduling**: Runs transfers automatically at set intervals (e.g., daily).
    * **自動排程**: 以設定的時間間隔（例如每天）自動執行傳輸。
    * **Backfills**: Easily recover or ingest historical data.
    * **回填 (Backfills)**: 輕鬆復原或擷取歷史資料。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: The marketing team wants to analyze ad spend performance across Google Ads and YouTube in BigQuery.
    * **架構師觀點**: 行銷團隊希望在 BigQuery 中分析 Google Ads 和 YouTube 的廣告支出成效。
    * Instead of writing custom Python scripts to hit the APIs, you configure the BigQuery Data Transfer Service to pull this data automatically every night.
    * 您無需編寫自定義 Python 腳本來呼叫 API，而是配置 BigQuery Data Transfer Service 每天晚上自動提取此資料。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Zero Coding**: It is a "no-code" solution for supported data sources.
    * **零程式碼**: 對於支援的資料來源，這是一個「無程式碼」解決方案。
    * **Permissions**: Requires the user setting up the transfer to have access to the source data (e.g., Google Ads account access).
    * **權限**: 要求設定傳輸的使用者必須擁有來源資料的存取權限（例如 Google Ads 帳戶存取權）。

---

### Transfer Service
* **Knowledge Level**: 2: medium
* **附註**: 通常指 **Storage Transfer Service**。
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Cost & Operational Excellence)**. 優化大規模資料傳輸的成本與可靠性。
* **產品重要說明 (Product Description)**:
    * Storage Transfer Service allows you to quickly and securely import online data into Cloud Storage.
    * Storage Transfer Service 允許您快速且安全地將線上資料匯入 Cloud Storage。
    * It supports transfers from other public clouds (AWS S3, Azure Blob Storage) and HTTP/HTTPS locations.
    * 它支援從其他公有雲 (AWS S3, Azure Blob Storage) 和 HTTP/HTTPS 位置進行傳輸。
* **主要功能 (Main Functions)**:
    * **Cloud-to-Cloud**: Moves data from AWS S3 or Azure to GCS without setting up servers.
    * **雲對雲**: 無需設定伺服器即可將資料從 AWS S3 或 Azure 移動到 GCS。
    * **On-premises**: Uses lightweight agents (Docker containers) to move data from on-prem file systems to GCS.
    * **地端**: 使用輕量級代理程式 (Docker 容器) 將資料從地端檔案系統移動到 GCS。
    * **Scheduling**: Supports one-time or recurring transfers.
    * **排程**: 支援一次性或週期性傳輸。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You are migrating a media library from Amazon S3 to Google Cloud Storage.
    * **架構師觀點**: 您正在將媒體庫從 Amazon S3 遷移到 Google Cloud Storage。
    * You create a Transfer Job in the Google Cloud Console, specifying the S3 bucket credentials. The service handles the bandwidth, retries, and checksum validation automatically.
    * 您在 Google Cloud Console 中建立一個傳輸作業，指定 S3 bucket 憑證。該服務會自動處理頻寬、重試和校驗和驗證。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Incremental**: Can be configured to copy only files that have changed or are new since the last run.
    * **增量**: 可以配置為僅複製自上次執行以來已更改或新增的檔案。
    * **Delete source**: Option to delete source objects after they are successfully transferred (use with caution).
    * **刪除來源**: 成功傳輸後刪除來源物件的選項（謹慎使用）。

---

### Migrate for Anthos
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Modernization)**. 應用程式現代化（從 VM 到容器）的關鍵工具。
* **產品重要說明 (Product Description)**:
    * Migrate for Anthos is a tool to modernize traditional VM-based applications by converting them into containers that run on Google Kubernetes Engine (GKE).
    * Migrate for Anthos 是一個工具，透過將傳統的基於 VM 的應用程式轉換為在 Google Kubernetes Engine (GKE) 上運行的容器，來對其進行現代化。
    * It works for VMs running on-premises (VMware), on Compute Engine, or other clouds.
    * 它適用於在地端 (VMware)、Compute Engine 或其他雲端上運行的 VM。
* **主要功能 (Main Functions)**:
    * **Assessment**: Analyzes VMs to determine if they are good candidates for containerization ("Fit Assessment").
    * **評估**: 分析 VM 以確定它們是否適合容器化（「適合度評估」）。
    * **Extraction**: Extracts the application and its dependencies from the VM image into a Docker container artifact.
    * **擷取**: 將應用程式及其依賴項從 VM 映像檔擷取到 Docker 容器成品中。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You have a legacy Tomcat Java application running on a Linux VM. You want to move it to GKE to leverage auto-scaling and simplified management.
    * **架構師觀點**: 您有一個在 Linux VM 上運行的舊版 Tomcat Java 應用程式。您希望將其移動到 GKE 以利用自動擴展和簡化管理。
    * Instead of rewriting the app or manually writing a Dockerfile, you use Migrate for Anthos to automatically generate the container image and Kubernetes deployment YAMLs.
    * 您無需重寫應用程式或手動編寫 Dockerfile，而是使用 Migrate for Anthos 自動產生容器映像檔和 Kubernetes 部署 YAML。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Not for everything**: Best for Linux-based web servers or application servers. Not suitable for databases (keep DBs on VMs or use managed services).
    * **非萬能**: 最適合基於 Linux 的 Web 伺服器或應用程式伺服器。不適合資料庫（將資料庫保留在 VM 上或使用託管服務）。
    * **Day 2 Operations**: The goal is to get into Kubernetes first, then refactor/optimize later ("Replatform then Refactor").
    * **Day 2 維運**: 目標是先進入 Kubernetes，然後再進行重構/優化（「先更換平台再重構」）。

---

### Migrate for Compute Engine
* **Knowledge Level**: 1: basics
* **附註**: 此項目已在 Compute Environment 類別中詳細說明，此處針對 Migration 類別做重點補充。
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Migration)**. 大規模 Lift-and-Shift 的標準工具。
* **產品重要說明 (Product Description)**:
    * (Recap) Allows lift-and-shift migration of VMs to GCP with minimal downtime using streaming technology.
    * (回顧) 允許使用串流技術以最短的停機時間將 VM 直接轉移 (lift-and-shift) 到 GCP。
    * Often referred to as the "Velostrata" technology.
    * 通常被稱為 "Velostrata" 技術。
* **主要功能 (Main Functions)**:
    * **Test-Clone**: Clone VMs in the cloud for testing without impacting the on-prem live production system.
    * **測試複製**: 在雲端複製 VM 進行測試，而不影響地端即時正式環境系統。
    * **Right-sizing**: Provides recommendations for instance sizing based on observed performance during the migration phase.
    * **適當規模化**: 根據遷移階段觀察到的效能，提供執行個體規模建議。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Migration deadline is tight.
    * **架構師觀點**: 遷移期限很緊迫。
    * You choose this tool over manual export/import because it allows the application to start running in GCP within minutes, while the storage synchronizes in the background.
    * 您選擇此工具而非手動匯出/匯入，因為它允許應用程式在幾分鐘內於 GCP 中開始運行，而儲存則在背景同步。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Pre-migration validation**: Running the "fit assessment" helps identify VMs that use unsupported OS versions or specific drivers that might fail.
    * **遷移前驗證**: 執行「適合度評估」有助於識別使用不支援的 OS 版本或可能導致失敗的特定驅動程式的 VM。

---

### Transfer Appliance
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Cost & Performance - Network limitations)**. 解決網路頻寬不足的實體解決方案。
* **產品重要說明 (Product Description)**:
    * Transfer Appliance is a high-capacity hardware storage device (server) that Google ships to your data center.
    * Transfer Appliance 是 Google 運送到您資料中心的容量硬體儲存裝置（伺服器）。
    * You fill it with data and ship it back to Google to upload to Cloud Storage.
    * 您將其裝滿資料並運回 Google 以傳上傳到 Cloud Storage。
    * It is used when transferring data over the network would take too long (e.g., > 1 week).
    * 當透過網路傳輸資料耗時過長（例如 > 1 週）時使用。
* **主要功能 (Main Functions)**:
    * **Offline Transfer**: Bypasses the internet completely for the main data move.
    * **離線傳輸**: 主要資料移動完全繞過網際網路。
    * **Encryption**: Data is encrypted on the device to ensure security during transit.
    * **加密**: 資料在裝置上加密，以確保運輸過程中的安全性。
    * **Ruggedized**: Designed to withstand shipping.
    * **堅固耐用**: 專為承受運輸而設計。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: A research lab has 1 PB of genomic data and a 100 Mbps internet connection.
    * **架構師觀點**: 一個研究實驗室擁有 1 PB 的基因組資料和 100 Mbps 的網際網路連線。
    * Uploading via network would take years. You order Transfer Appliances, copy the data locally in a few days, and ship them back. The data appears in your GCS bucket shortly after.
    * 透過網路傳上傳需要數年時間。您訂購 Transfer Appliances，在幾天內將資料複製到本地，然後運回。資料不久後就會出現在您的 GCS bucket 中。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Capacity**: Typically comes in sizes like 40TB or 300TB.
    * **容量**: 通常有 40TB 或 300TB 等容量規格。
    * **Data Wipe**: Google securely wipes the device after data is uploaded to your bucket.
    * **資料抹除**: 資料上傳到您的 bucket 後，Google 會安全地抹除裝置。

---

## Containers

### Google Kubernetes Engine (GKE)
* **Knowledge Level**: 3: advanced
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Operational Excellence, Reliability, Scalability, Security)**. 這是 Google Cloud 最核心的現代化運算平台，幾乎是所有容器化策略的基礎。
* **產品重要說明 (Product Description)**:
    * GKE is a managed environment for deploying, managing, and scaling your containerized applications using Kubernetes.
    * GKE 是一個託管環境，用於使用 Kubernetes 部署、管理和擴展您的容器化應用程式。
    * It abstracts the underlying infrastructure while giving you the power of Kubernetes orchestration.
    * 它抽象化了底層基礎設施，同時為您提供 Kubernetes 調度的強大功能。
* **主要功能 (Main Functions)**:
    * **Autopilot vs Standard**: Standard gives you node control; Autopilot manages nodes/infrastructure for you (fully managed).
    * **Autopilot 與 Standard**: Standard 讓您控制節點；Autopilot 為您管理節點/基礎設施（完全託管）。
    * **Auto-scaling**: Supports Cluster Autoscaler (nodes) and Horizontal Pod Autoscaler (pods).
    * **自動擴展**: 支援叢集自動擴展器 (節點) 和水平 Pod 自動擴展器 (Pod)。
    * **Auto-repair/Auto-upgrade**: Keeps nodes healthy and up-to-date automatically.
    * **自動修復/自動升級**: 自動保持節點健康和最新狀態。
    * **Regional Clusters**: Control plane replicated across multiple zones for high availability.
    * **區域性叢集**: 控制平面跨多個可用區複製以實現高可用性。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You are designing a microservices e-commerce platform that must handle Black Friday traffic spikes.
    * **架構師觀點**: 您正在設計一個必須處理黑色星期五流量高峰的微服務電子商務平台。
    * You use a **Regional GKE Cluster** for control plane HA. You configure **HPA** to scale pods based on CPU and custom metrics (requests per second), and **Cluster Autoscaler** to add nodes when pods are pending.
    * 您使用**區域性 GKE 叢集**來實現控制平面 HA。您配置 **HPA** 根據 CPU 和自定義指標（每秒請求數）擴展 Pod，並配置 **Cluster Autoscaler** 在 Pod 處於 Pending 狀態時新增節點。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **VPC-native Clusters**: The recommended mode where Pods get their own IP addresses from the VPC (Alias IPs). This avoids NAT performance penalties and simplifies firewalling.
    * **VPC 原生叢集**: 推薦模式，其中 Pod 從 VPC 獲取自己的 IP 位址（別名 IP）。這避免了 NAT 效能損失並簡化了防火牆設定。
    * **Private Clusters**: Nodes have only private IPs. Access to the master endpoint can be restricted to specific CIDR ranges or via a jump host. Critical for security.
    * **私人叢集**: 節點僅具有私人 IP。對主端點的存取可以限制在特定 CIDR 範圍內或透過跳板機。這對安全性至關重要。
    * **Ingress**: GKE creates a Google Cloud Load Balancer (L7) when you create an Ingress object.
    * **Ingress**: 當您建立 Ingress 物件時，GKE 會建立 Google Cloud 負載平衡器 (L7)。

---

### Container Registry
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security - Supply Chain)**. 安全軟體供應鏈的儲存庫。
* **產品重要說明 (Product Description)**:
    * Container Registry (GCR) is a private storage for Docker images on Google Cloud.
    * Container Registry (GCR) 是 Google Cloud 上 Docker 映像檔的私人儲存空間。
    * *Note: Artifact Registry is the successor and recommended for new projects, but GCR is still widely used.*
    * *註：Artifact Registry 是繼任者，建議用於新專案，但 GCR 仍被廣泛使用。*
* **主要功能 (Main Functions)**:
    * **Storage**: Stores images in Cloud Storage buckets under the hood.
    * **儲存**: 在底層將映像檔儲存在 Cloud Storage bucket 中。
    * **Vulnerability Scanning**: Automatically scans images for known security vulnerabilities (OS level).
    * **漏洞掃描**: 自動掃描映像檔中的已知安全漏洞（OS 層級）。
    * **IAM Integration**: Access is controlled via Cloud IAM.
    * **IAM 整合**: 存取透過 Cloud IAM 控制。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Your CI/CD pipeline builds a container image.
    * **架構師觀點**: 您的 CI/CD 流程建立一個容器映像檔。
    * The pipeline pushes the image to GCR (`gcr.io/my-project/my-image`). GKE pulls this image to deploy. Only authorized service accounts can pull the image.
    * 流程將映像檔推送至 GCR (`gcr.io/my-project/my-image`)。GKE 拉取此映像檔進行部署。只有經過授權的服務帳戶才能拉取映像檔。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Location**: You can store images in regional (e.g., `asia.gcr.io`) or multi-regional buckets for faster pull times in those locations.
    * **位置**: 您可以將映像檔儲存在區域性（例如 `asia.gcr.io`）或多區域 bucket 中，以便在這些位置獲得更快的拉取時間。

---

### Cloud Build
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Operational Excellence - CI/CD)**. 完全託管的無伺服器 CI/CD 平台。
* **產品重要說明 (Product Description)**:
    * Cloud Build is a service that executes your builds on Google Cloud infrastructure.
    * Cloud Build 是一項在 Google Cloud 基礎設施上執行您的建置的服務。
    * It can import source code, run build steps (Docker builds, unit tests), and produce artifacts (containers, jars).
    * 它可以匯入原始碼、執行建置步驟（Docker 建置、單元測試）並產生成品（容器、Jars）。
* **主要功能 (Main Functions)**:
    * **Serverless**: No build servers to manage. Scales up instantly.
    * **無伺服器**: 無需管理建置伺服器。立即擴展。
    * **Triggers**: Starts builds automatically on git push to Cloud Source Repositories, GitHub, or Bitbucket.
    * **觸發程序**: 在 git push 到 Cloud Source Repositories, GitHub 或 Bitbucket 時自動開始建置。
    * **Security**: Supports Binary Authorization to sign images.
    * **安全性**: 支援二進位授權以簽署映像檔。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You want to implement a GitOps workflow for GKE.
    * **架構師觀點**: 您希望為 GKE 實作 GitOps 工作流程。
    * You set up a Cloud Build trigger. When a developer pushes to the `main` branch, Cloud Build runs `docker build`, pushes the image to GCR, and then runs `kubectl apply` to update the GKE cluster.
    * 您設定一個 Cloud Build 觸發程序。當開發人員推送到 `main` 分支時，Cloud Build 執行 `docker build`，將映像檔推送至 GCR，然後執行 `kubectl apply` 來更新 GKE 叢集。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Cloud Build Workers**: You can use the default pool (public IP) or "Private Pools" to access resources inside a private VPC.
    * **Cloud Build Workers**: 您可以使用預設集區（公共 IP）或「私人集區 (Private Pools)」來存取私人 VPC 內的資源。

---

### Cloud Deploy
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Operational Excellence - CD)**. 專注於 Kubernetes 交付流程的託管服務。
* **產品重要說明 (Product Description)**:
    * Cloud Deploy is a fully managed continuous delivery (CD) service specifically for GKE and Anthos.
    * Cloud Deploy 是一個完全託管的持續交付 (CD) 服務，專門針對 GKE 和 Anthos。
    * It simplifies the "CD" part of CI/CD, managing the progression of releases across environments (e.g., Dev -> Staging -> Prod).
    * 它簡化了 CI/CD 的 "CD" 部分，管理跨環境（例如開發 -> 預備 -> 正式）的發布流程。
* **主要功能 (Main Functions)**:
    * **Pipeline Visualization**: Shows the state of your release in a UI.
    * **管線視覺化**: 在 UI 中顯示發布的狀態。
    * **Rollbacks**: One-click rollback to a previous good state.
    * **復原**: 一鍵復原到先前的良好狀態。
    * **Skaffold**: Uses Skaffold configuration under the hood to define rendering and deployment.
    * **Skaffold**: 底層使用 Skaffold 配置來定義渲染和部署。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You have three GKE clusters: Dev, QA, and Prod.
    * **架構師觀點**: 您有三個 GKE 叢集：Dev, QA 和 Prod。
    * Cloud Build builds the image. Cloud Deploy then takes that image and deploys it first to Dev. After manual approval in the console, it promotes the release to QA, and finally to Prod.
    * Cloud Build 建立映像檔。然後 Cloud Deploy 獲取該映像檔並將其首先部署到 Dev。在控制台中手動核准後，它將發布晉升到 QA，最後到 Prod。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Separation of concerns**: Cloud Build does the CI (build/test), Cloud Deploy does the CD (promote/deploy).
    * **關注點分離**: Cloud Build 執行 CI (建置/測試)，Cloud Deploy 執行 CD (晉升/部署)。

---

### Container Optimized OS
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security & Performance)**. 這是 GKE 節點的預設且推薦的作業系統。
* **產品重要說明 (Product Description)**:
    * Container-Optimized OS (COS) is a hardened operating system image maintained by Google.
    * Container-Optimized OS (COS) 是由 Google 維護的強化作業系統映像檔。
    * It is optimized for running Docker containers and is the default OS for GKE nodes.
    * 它針對運行 Docker 容器進行了優化，是 GKE 節點的預設 OS。
* **主要功能 (Main Functions)**:
    * **Minimal Footprint**: Contains only the necessary packages to run containers, reducing the attack surface.
    * **最小足跡**: 僅包含運行容器所需的套件，減少攻擊面。
    * **Locked Down**: Root filesystem is read-only.
    * **鎖定**: Root 檔案系統是唯讀的。
    * **Auto-update**: Designed to automatically update and patch itself (managed by GKE).
    * **自動更新**: 設計為自動更新和修補自身（由 GKE 管理）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You are configuring GKE node pools.
    * **架構師觀點**: 您正在配置 GKE 節點集區。
    * You choose COS over Ubuntu because COS provides better security (read-only root) and faster boot times, ensuring nodes scale up quickly during traffic spikes.
    * 您選擇 COS 而不是 Ubuntu，因為 COS 提供更好的安全性（唯讀 root）和更快的開機時間，確保節點在流量高峰期間快速擴展。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Tooling**: Since you can't install packages easily, debugging is done using the `toolbox` container which brings debugging tools temporarily.
    * **工具**: 由於您無法輕易安裝套件，因此偵錯是使用 `toolbox` 容器完成的，它會暫時帶來偵錯工具。

---

### Workload Identity
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security - Identity)**. 這是 GKE 最重要的安全最佳實務之一。
* **產品重要說明 (Product Description)**:
    * Workload Identity allows a Kubernetes Service Account (KSA) to act as a Google Cloud IAM Service Account (GSA).
    * Workload Identity 允許 Kubernetes 服務帳戶 (KSA) 充當 Google Cloud IAM 服務帳戶 (GSA)。
    * It removes the need to store JSON key files (secrets) inside containers.
    * 它消除了在容器內儲存 JSON 金鑰檔案 (Secrets) 的需求。
* **主要功能 (Main Functions)**:
    * **IAM Mapping**: Maps `KSA` -> `GSA` -> `IAM Roles`.
    * **IAM 對應**: 對應 `KSA` -> `GSA` -> `IAM 角色`。
    * **Security**: Pods automatically retrieve short-lived tokens from the metadata server.
    * **安全性**: Pod 自動從 Metadata 伺服器檢索短期權杖。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Your GKE application needs to read from a Cloud Storage bucket.
    * **架構師觀點**: 您的 GKE 應用程式需要從 Cloud Storage bucket 讀取。
    * Instead of mounting a GCP service account key as a Kubernetes Secret (risky), you enable Workload Identity. You bind the Pod's Service Account to a GCP Service Account that has `Storage Object Viewer`.
    * 您啟用 Workload Identity，而不是將 GCP 服務帳戶金鑰掛載為 Kubernetes Secret（有風險）。您將 Pod 的服務帳戶綁定到具有 `Storage Object Viewer` 權限的 GCP 服務帳戶。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Standard**: This is now the standard/recommended way for authentication in GKE. Node Service Account should have minimal permissions.
    * **標準**: 這是目前 GKE 中推薦的身分驗證標準方式。節點服務帳戶應具有最低權限。

---

### Network Policies
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security - Zero Trust)**. 叢集內部的防火牆規則。
* **產品重要說明 (Product Description)**:
    * Network Policies serve as a firewall for your GKE cluster's internal traffic.
    * Network Policies 充當 GKE 叢集內部流量的防火牆。
    * They control which pods can communicate with each other.
    * 它們控制哪些 Pod 可以互相通訊。
    * By default, in Kubernetes, all pods can talk to all other pods (flat network).
    * 預設情況下，在 Kubernetes 中，所有 Pod 都可以與所有其他 Pod 通訊（扁平網路）。
* **主要功能 (Main Functions)**:
    * **Traffic Control**: Allow or Deny ingress/egress traffic based on Pod labels and Namespaces.
    * **流量控制**: 根據 Pod 標籤和命名空間允許或拒絕傳入/傳出流量。
    * **Micro-segmentation**: Isolate sensitive services (e.g., "frontend" cannot talk directly to "database" pod, must go through "backend").
    * **微分割**: 隔離敏感服務（例如，「前端」不能直接與「資料庫」Pod 通訊，必須經過「後端」）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You are running a multi-tenant cluster hosting app A and app B.
    * **架構師觀點**: 您正在運行一個託管應用程式 A 和應用程式 B 的多租戶叢集。
    * You apply a Network Policy that denies all cross-namespace traffic, ensuring that if App A is compromised, the attacker cannot reach App B's pods.
    * 您套用一個拒絕所有跨命名空間流量的 Network Policy，確保如果應用程式 A 受到破壞，攻擊者無法到達應用程式 B 的 Pod。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **CNI**: Requires the GKE cluster to be created with Network Policy enabled (typically uses Calico or Dataplane V2).
    * **CNI**: 要求在建立 GKE 叢集時啟用 Network Policy（通常使用 Calico 或 Dataplane V2）。

---

## Networking

### Cloud Armor
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security pillar)**. 保護對外服務的關鍵邊緣防禦層。
* **產品重要說明 (Product Description)**:
    * Cloud Armor is Google's Web Application Firewall (WAF) and DDoS protection service.
    * Cloud Armor 是 Google 的 Web 應用程式防火牆 (WAF) 和 DDoS 防護服務。
    * It sits at the edge of Google's network (integrated with Global Load Balancing) to stop attacks before they reach your backend.
    * 它位於 Google 網路的邊緣（與全球負載平衡整合），在攻擊到達您的後端之前將其阻止。
* **主要功能 (Main Functions)**:
    * **DDoS Defense**: Protects against L3/L4 volumetric attacks automatically.
    * **DDoS 防禦**: 自動防禦 L3/L4 流量攻擊。
    * **WAF Rules**: Pre-configured rules to block OWASP Top 10 attacks (SQL injection, XSS).
    * **WAF 規則**: 預先配置的規則可阻止 OWASP Top 10 攻擊（SQL 注入、XSS）。
    * **Rate Limiting**: Throttles clients sending too many requests per minute.
    * **速率限制**: 限制每分鐘發送過多請求的客戶端。
    * **Geo-blocking**: Allow or deny traffic based on country/region.
    * **地理封鎖**: 根據國家/地區允許或拒絕流量。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Your e-commerce site is under a Layer 7 HTTP flood attack from a specific set of IPs.
    * **架構師觀點**: 您的電子商務網站正遭受來自一組特定 IP 的 Layer 7 HTTP 洪水攻擊。
    * You apply a Cloud Armor security policy to your HTTP(S) Load Balancer to rate-limit requests from those IPs and block common SQL injection patterns.
    * 您將 Cloud Armor 安全政策套用到您的 HTTP(S) 負載平衡器，以限制來自這些 IP 的請求速率，並阻止常見的 SQL 注入模式。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Integration**: Works only with HTTP(S) Load Balancing (Global external, Regional external, and some internal types). Does not work directly on a VM NIC.
    * **整合**: 僅適用於 HTTP(S) 負載平衡（全球外部、區域外部和某些內部類型）。不能直接在 VM 網卡上運作。
    * **Adaptive Protection**: Uses ML to detect anomalies and suggest rules automatically (Managed Protection Plus tier).
    * **自適應防護**: 使用機器學習來檢測異常並自動建議規則（Managed Protection Plus 層級）。

---

### Cloud Domains
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **No (Utility)**. 基礎網域名稱註冊服務。
* **產品重要說明 (Product Description)**:
    * Cloud Domains allows you to register and manage domain names directly within Google Cloud.
    * Cloud Domains 允許您直接在 Google Cloud 內註冊和管理網域名稱。
    * It simplifies the integration with Cloud DNS and Cloud Run/App Engine custom domains.
    * 它簡化了與 Cloud DNS 和 Cloud Run/App Engine 自定義網域的整合。
* **主要功能 (Main Functions)**:
    * **Registration**: Buy domains (e.g., .com, .net, .dev).
    * **註冊**: 購買網域（例如 .com, .net, .dev）。
    * **Management**: Manage DNS settings and auto-renewal.
    * **管理**: 管理 DNS 設定和自動續訂。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You are setting up a new startup infrastructure.
    * **架構師觀點**: 您正在建立一個新的新創公司基礎設施。
    * Instead of using GoDaddy or Namecheap, you register the domain via Cloud Domains so that billing is consolidated into your monthly GCP invoice and DNS is auto-configured.
    * 您無需使用 GoDaddy 或 Namecheap，而是透過 Cloud Domains 註冊網域，以便將帳單合併到您的每月 GCP 發票中，並且自動配置 DNS。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Privacy**: Offers privacy protection (Whois redaction) usually included for free.
    * **隱私**: 提供隱私保護（Whois 編輯），通常免費包含在內。

---

### Cloud CDN
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Performance & Cost pillars)**. 全球內容傳遞與頻寬成本優化的關鍵。
* **產品重要說明 (Product Description)**:
    * Cloud CDN (Content Delivery Network) uses Google's globally distributed edge points of presence to cache external HTTP(S) load balanced content close to your users.
    * Cloud CDN (內容傳遞網路) 使用 Google 全球分佈的邊緣節點，在靠近使用者的位置快取外部 HTTP(S) 負載平衡內容。
    * It reduces latency and offloads traffic from your backend servers.
    * 它減少了延遲並減輕了後端伺服器的流量負載。
* **主要功能 (Main Functions)**:
    * **Caching**: Caches static assets (images, CSS, JS) and video.
    * **快取**: 快取靜態資產（圖片、CSS、JS）和影片。
    * **Cache Modes**: Supports static content, but also dynamic content via cache keys.
    * **快取模式**: 支援靜態內容，也支援透過快取鍵的動態內容。
    * **Signed URLs/Cookies**: Restricts access to paid content (e.g., subscription video).
    * **簽署 URL/Cookies**: 限制對付費內容的存取（例如訂閱影片）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You have a media website serving heavy images stored in GCS.
    * **架構師觀點**: 您有一個媒體網站，提供儲存在 GCS 中的大量圖片。
    * You enable Cloud CDN on the Load Balancer backend bucket. Users in Europe fetch images from a European edge cache instead of going all the way to your US bucket, speeding up load times and saving egress costs.
    * 您在負載平衡器後端 bucket 上啟用 Cloud CDN。歐洲的使用者從歐洲邊緣快取獲取圖片，而不是一路連線到您的美國 bucket，從而加快載入時間並節省傳出流量成本。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Backend Support**: Works with Instance Groups, Cloud Storage buckets, and Cloud Run/Functions (Serverless NEGs).
    * **後端支援**: 適用於執行個體群組、Cloud Storage buckets 和 Cloud Run/Functions (Serverless NEG)。
    * **Invalidation**: You can invalidate the cache (clear it) via API/Console, but it is rate-limited and can take minutes.
    * **撤銷**: 您可以透過 API/控制台撤銷快取（清除它），但它有速率限制，並且可能需要幾分鐘。

---

### Cloud DNS
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Reliability pillar)**. 高可用性且可程式化的 DNS 服務。
* **產品重要說明 (Product Description)**:
    * Cloud DNS is a scalable, reliable, and managed authoritative Domain Name System (DNS) service.
    * Cloud DNS 是一個可擴展、可靠且託管的權威網域名稱系統 (DNS) 服務。
    * It translates domain names like `www.google.com` into IP addresses.
    * 它將網域名稱（如 `www.google.com`）轉換為 IP 位址。
* **主要功能 (Main Functions)**:
    * **Public Zones**: Managing DNS records for public domains visible to the internet.
    * **公共區域**: 管理網際網路可見的公共網域 DNS 記錄。
    * **Private Zones**: Managing internal DNS names for VM-to-VM communication within a VPC (split-horizon DNS).
    * **私人區域**: 管理 VPC 內 VM 到 VM 通訊的內部 DNS 名稱（水平分割 DNS）。
    * **Peering**: Allowing one VPC to query the DNS records of another VPC.
    * **對等互連**: 允許一個 VPC 查詢另一個 VPC 的 DNS 記錄。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You have a microservices architecture in a private VPC.
    * **架構師觀點**: 您在私人 VPC 中擁有微服務架構。
    * You use Cloud DNS Private Zones to map `service-a.internal` to an internal load balancer IP. This allows services to find each other using friendly names without exposing DNS to the public internet.
    * 您使用 Cloud DNS 私人區域將 `service-a.internal` 對應到內部負載平衡器 IP。這允許服務使用易記名稱相互尋找，而無需將 DNS 暴露給公共網際網路。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **100% SLA**: Google Cloud DNS is one of the few services offering a 100% availability SLA.
    * **100% SLA**: Google Cloud DNS 是少數提供 100% 可用性 SLA 的服務之一。

---

### DNSSEC
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security pillar)**. 防止 DNS 劫持與快取投毒。
* **產品重要說明 (Product Description)**:
    * DNS Security Extensions (DNSSEC) adds a layer of security to the DNS protocol.
    * DNS 安全擴充 (DNSSEC) 為 DNS 協定增加了一層安全性。
    * It enables authentication of DNS data to prevent spoofing and cache poisoning attacks.
    * 它啟用 DNS 資料的身分驗證，以防止詐騙和快取投毒攻擊。
* **主要功能 (Main Functions)**:
    * **Signing**: Cryptographically signs your DNS records.
    * **簽署**: 對您的 DNS 記錄進行加密簽署。
    * **Validation**: Resolvers verify the signature to ensure the IP address hasn't been tampered with.
    * **驗證**: 解析器驗證簽名以確保 IP 位址未被篡改。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: A financial client requires strict protection against "Man-in-the-Middle" attacks.
    * **架構師觀點**: 一個金融客戶要求嚴格防範「中間人」攻擊。
    * You enable DNSSEC on their Cloud DNS zone. This ensures that when customers visit `bank.com`, they are definitely connecting to the real IP and not a malicious redirect.
    * 您在他們的 Cloud DNS 區域上啟用 DNSSEC。這確保當客戶訪問 `bank.com` 時，他們絕對是連線到真實的 IP，而不是惡意的重新導向。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **One-click**: In Cloud DNS, enabling DNSSEC is often a simple checkbox ("DNSSEC state: On").
    * **一鍵啟用**: 在 Cloud DNS 中，啟用 DNSSEC 通常只是一個簡單的核取方塊（「DNSSEC 狀態：開啟」）。
    * **Registrar update**: You must update your domain registrar with the DS records generated by Cloud DNS to complete the chain of trust.
    * **註冊商更新**: 您必須使用 Cloud DNS 產生的 DS 記錄更新您的網域註冊商，以完成信任鏈。

---

### Cloud Load Balancing
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Reliability & Performance pillars)**. GCP 網路架構的核心，實現全球單一 IP 存取。
* **產品重要說明 (Product Description)**:
    * Cloud Load Balancing allows you to distribute your applications' traffic across multiple instances in a single region or multiple regions.
    * Cloud Load Balancing 允許您將應用程式的流量分配到單一區域或多個區域的多個執行個體中。
    * It is a fully distributed, software-defined managed service.
    * 它是一個完全分散式、軟體定義的託管服務。
* **主要功能 (Main Functions)**:
    * **Global HTTP(S) LB**: Layer 7 balancing across regions. Single Anycast IP.
    * **全球 HTTP(S) LB**: 跨區域的 Layer 7 平衡。單一 Anycast IP。
    * **Regional Network LB**: Layer 4 balancing (TCP/UDP) within a region.
    * **區域網路 LB**: 區域內的 Layer 4 平衡 (TCP/UDP)。
    * **Internal LB**: Private balancing for internal traffic (L4 or L7).
    * **內部 LB**: 內部流量的私人平衡（L4 或 L7）。
    * **Anycast IP**: Advertise the same IP from all global edge locations.
    * **Anycast IP**: 從所有全球邊緣位置廣播相同的 IP。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You are launching a global game backend.
    * **架構師觀點**: 您正在推出一個全球遊戲後端。
    * You use the **Global External HTTP(S) Load Balancer**. It gives you one IPv4 address. Users in Asia are routed to the Asia backend; users in US are routed to the US backend. If the US backend fails, traffic automatically overflows to Asia or Europe.
    * 您使用**全球外部 HTTP(S) 負載平衡器**。它給您一個 IPv4 位址。亞洲使用者被路由到亞洲後端；美國使用者被路由到美國後端。如果美國後端發生故障，流量會自動溢位到亞洲或歐洲。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Proxy vs Pass-through**:
        * HTTP(S) and SSL Proxy LBs are **Proxies** (terminate connection, open new one to backend).
        * Network LB is **Pass-through** (packets go directly to backend, preserving client IP).
    * **Proxy 與 Pass-through**:
        * HTTP(S) 和 SSL Proxy LB 是 **Proxy**（終止連線，開啟新連線到後端）。
        * Network LB 是 **Pass-through**（封包直接到達後端，保留客戶端 IP）。
    * **Session Affinity**: Can be configured (e.g., Client IP affinity) if your app is stateful.
    * **工作階段親和性**: 如果您的應用程式是有狀態的，則可以進行配置（例如客戶端 IP 親和性）。

---

### Cloud NAT
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security pillar)**. 允許私人執行個體存取外部網路而不暴露自己的標準方法。
* **產品重要說明 (Product Description)**:
    * Cloud NAT (Network Address Translation) allows Google Cloud VM instances without external IP addresses to access the internet.
    * Cloud NAT (網路位址轉譯) 允許沒有外部 IP 位址的 Google Cloud VM 執行個體存取網際網路。
    * It provides outbound connectivity while preventing inbound connections from the internet.
    * 它提供對外連線能力，同時阻止來自網際網路的對內連線。
* **主要功能 (Main Functions)**:
    * **Outbound Connectivity**: Allows downloading updates/patches from the public web.
    * **對外連線**: 允許從公共網路下載更新/修補程式。
    * **Security**: Hides internal VMs from public internet scans (no public IP on VM).
    * **安全性**: 對公共網路掃描隱藏內部 VM（VM 上無公共 IP）。
    * **Fully Managed**: No NAT proxy instances to manage; high availability is built-in.
    * **完全託管**: 無需管理 NAT 代理執行個體；內建高可用性。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You have a cluster of private database servers in a secure subnet.
    * **架構師觀點**: 您在一個安全子網中擁有一群私人資料庫伺服器。
    * They need to download OS updates from a public repository. You configure Cloud NAT on the Cloud Router associated with that region. The VMs can now reach the repo, but hackers cannot reach the VMs.
    * 它們需要從公共存放庫下載 OS 更新。您在與該區域關聯的 Cloud Router 上配置 Cloud NAT。VM 現在可以連線到存放庫，但駭客無法連線到 VM。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Regional Resource**: Cloud NAT is a regional resource. You need one per region where you need outbound access.
    * **區域性資源**: Cloud NAT 是區域性資源。您需要在每個需要對外存取的區域配置一個。
    * **Port Exhaustion**: A single NAT IP has 65,536 ports. If you have many VMs making many connections, you might run out of ports. You can add multiple public IPs to the NAT gateway to scale.
    * **連接埠耗盡**: 單個 NAT IP 有 65,536 個連接埠。如果您有許多 VM 建立許多連線，可能會耗盡連接埠。您可以將多個公共 IP 新增至 NAT 閘道以進行擴展。

---

### Hybrid Connectivity
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Infrastructure pillar)**. 企業混合雲架構的總稱。
* **產品重要說明 (Product Description)**:
    * Hybrid Connectivity refers to the suite of products connecting your on-premises infrastructure to Google Cloud.
    * 混合連線是指將您的地端基礎設施連線到 Google Cloud 的一系列產品。
    * It includes Cloud VPN, Cloud Interconnect, and Peering.
    * 它包含 Cloud VPN, Cloud Interconnect 和 Peering。
* **主要功能 (Main Functions)**:
    * **Cloud VPN**: Secure connection over the public internet (IPsec).
    * **Cloud VPN**: 透過公共網際網路的安全連線 (IPsec)。
    * **Cloud Interconnect**: Dedicated physical connection (Dedicated or Partner) avoiding the public internet.
    * **Cloud Interconnect**: 避開公共網際網路的專用實體連線（專用或合作夥伴）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You need to choose a connection method.
    * **架構師觀點**: 您需要選擇一種連線方式。
    * If bandwidth is low (< 3 Gbps) and cost is a concern, use **Cloud VPN**. If you need 10 Gbps+ or strict SLA on latency/throughput, use **Dedicated Interconnect**.
    * 如果頻寬較低 (< 3 Gbps) 且關注成本，請使用 **Cloud VPN**。如果您需要 10 Gbps+ 或對延遲/吞吐量有嚴格的 SLA，請使用 **Dedicated Interconnect**。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Redundancy**: A proper hybrid setup always requires redundancy (e.g., two VPN tunnels or two Interconnect circuits) to achieve high availability SLAs (99.99%).
    * **備援**: 適當的混合設定總是需要備援（例如，兩個 VPN 通道或兩條 Interconnect 電路）以達到高可用性 SLA (99.99%)。

---

### Network Intelligence Center
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Operational Excellence - Observability)**. 網路視覺化與診斷中心。
* **產品重要說明 (Product Description)**:
    * Network Intelligence Center provides a single console for managing and monitoring your network visibility.
    * Network Intelligence Center 提供單一控制台來管理和監控您的網路可視性。
    * It helps verify connectivity and troubleshoot network configurations.
    * 它有助於驗證連線能力並排除網路組態疑難。
* **主要功能 (Main Functions)**:
    * **Network Topology**: Visualizes your VPCs, subnets, and how traffic flows between them.
    * **網路拓撲**: 視覺化您的 VPC、子網以及它們之間的流量流向。
    * **Connectivity Tests**: Simulates a packet from Source A to Dest B to see if firewall rules allow it.
    * **連線測試**: 模擬從來源 A 到目的地 B 的封包，以查看防火牆規則是否允許。
    * **Performance Dashboard**: Monitors packet loss and latency between regions.
    * **效能儀表板**: 監控區域之間的封包遺失和延遲。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: A developer claims "the network is down" because App A cannot talk to DB B.
    * **架構師觀點**: 開發人員聲稱「網路中斷」，因為應用程式 A 無法與資料庫 B 通訊。
    * You run a **Connectivity Test** in Network Intelligence Center. It reveals that a firewall rule is blocking traffic on port 5432. You fix the rule.
    * 您在 Network Intelligence Center 中執行**連線測試**。它顯示防火牆規則阻止了連接埠 5432 上的流量。您修復了該規則。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Configuration Analysis**: It analyzes configuration (static analysis), not just live traffic packets. It can tell you *why* a connection would fail even if no traffic is currently flowing.
    * **組態分析**: 它分析組態（靜態分析），而不僅僅是即時流量封包。即使目前沒有流量流動，它也能告訴您連線*為什麼*會失敗。

---

### Network Service Tiers
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Performance & Cost)**. 決定網路流量走 Google 骨幹還是公共網路的選項。
* **產品重要說明 (Product Description)**:
    * GCP allows you to choose the network tier for your external traffic: Premium or Standard.
    * GCP 允許您為外部流量選擇網路層級：進階 (Premium) 或標準 (Standard)。
* **主要功能 (Main Functions)**:
    * **Premium Tier (Default)**: Traffic enters Google's network at the nearest edge PoP globally and rides Google's private backbone. Higher performance.
    * **進階層級 (預設)**: 流量在全球最近的邊緣 PoP 進入 Google 網路，並在 Google 的專用骨幹網路上傳輸。效能較高。
    * **Standard Tier**: Traffic enters Google's network at the PoP closest to the data center (region). It travels over the public internet for most of the journey. Lower cost.
    * **標準層級**: 流量在最接近資料中心（區域）的 PoP 進入 Google 網路。大部分旅程都在公共網際網路上傳輸。成本較低。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You have a budget-constrained project serving users only in one specific region (e.g., users in Germany accessing a server in Frankfurt).
    * **架構師觀點**: 您有一個預算受限的專案，僅為特定區域的使用者提供服務（例如，德國使用者存取法蘭克福的伺服器）。
    * You choose **Standard Tier** to save costs, as the global backbone benefits are minimal for local traffic.
    * 您選擇**標準層級**以節省成本，因為全球骨幹網路對本地流量的優勢微乎其微。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Global LB Requirement**: Global Load Balancing *requires* Premium Tier. Standard Tier only supports regional resources.
    * **全球 LB 需求**: 全球負載平衡*需要*進階層級。標準層級僅支援區域性資源。

---

### Virtual Private Cloud (VPC)
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (All pillars)**. 所有雲端資源的網路基礎。
* **產品重要說明 (Product Description)**:
    * A VPC is a virtual version of a physical network implemented inside Google's production network.
    * VPC 是在 Google 生產網路內部實作的實體網路的虛擬版本。
    * It provides connectivity for your VM instances, GKE clusters, etc.
    * 它為您的 VM 執行個體、GKE 叢集等提供連線能力。
* **主要功能 (Main Functions)**:
    * **Global**: Unlike AWS (regional), a Google VPC is a global resource. Subnets are regional.
    * **全球性**: 與 AWS（區域性）不同，Google VPC 是全球性資源。子網是區域性的。
    * **Subnets**: Defined by IP ranges (CIDR).
    * **子網**: 由 IP 範圍 (CIDR) 定義。
    * **Firewall Rules**: Control traffic to/from instances.
    * **防火牆規則**: 控制進出執行個體的流量。
    * **Routes**: Control traffic paths (e.g., to internet gateway, to VPN).
    * **路由**: 控制流量路徑（例如，到網際網路閘道，到 VPN）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You are designing a multi-region app.
    * **架構師觀點**: 您正在設計一個多區域應用程式。
    * You create one VPC. You create a subnet in `us-central1` and another in `asia-northeast1`. VMs in these subnets can talk to each other via internal IP addresses automatically over Google's backbone, with no extra VPN configuration needed.
    * 您建立一個 VPC。您在 `us-central1` 建立一個子網，在 `asia-northeast1` 建立另一個。這些子網中的 VM 可以透過 Google 骨幹網路自動使用內部 IP 位址相互通訊，無需額外的 VPN 配置。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Shared VPC**: Allows sharing a VPC from a "Host Project" to multiple "Service Projects". Critical for centralized network administration in large organizations.
    * **共用 VPC**: 允許將 VPC 從「主機專案」分享給多個「服務專案」。這對於大型組織中的集中式網路管理至關重要。
    * **VPC Peering**: Connects two independent VPCs so they can communicate using internal IPs. (Non-transitive).
    * **VPC 對等互連**: 連線兩個獨立的 VPC，以便它們可以使用內部 IP 進行通訊。（不可傳遞）。

---

### Cloud Router
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Infrastructure)**. 實現動態路由的核心元件。
* **產品重要說明 (Product Description)**:
    * Cloud Router is a fully distributed and managed service to program custom dynamic routes.
    * Cloud Router 是一個完全分散式且託管的服務，用於程式化自定義動態路由。
    * It enables dynamic route exchange between your VPC and your on-premises network using BGP (Border Gateway Protocol).
    * 它使用 BGP (邊界閘道協定) 啟用 VPC 與地端網路之間的動態路由交換。
* **主要功能 (Main Functions)**:
    * **Dynamic Routing**: Automatically learns new subnets from on-prem and advertises new VPC subnets to on-prem.
    * **動態路由**: 自動從地端學習新子網，並將新 VPC 子網廣播到地端。
    * **Cloud NAT Host**: Acts as the control plane for Cloud NAT.
    * **Cloud NAT 主機**: 充當 Cloud NAT 的控制平面。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You connect your VPC to your corporate datacenter via Cloud VPN.
    * **架構師觀點**: 您透過 Cloud VPN 將您的 VPC 連線到企業資料中心。
    * You use Cloud Router with BGP. When you add a new subnet in your VPC for a new project, Cloud Router automatically advertises this range to your on-prem router.
    * 您使用帶有 BGP 的 Cloud Router。當您在 VPC 中為新專案新增一個子網時，Cloud Router 會自動將此範圍廣播給您的地端路由器。
    * Without dynamic routing, you would have to manually update static routes on both ends every time network topology changes.
    * 如果沒有動態路由，每次網路拓撲變更時，您都必須手動更新兩端的靜態路由。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Global vs Regional Routing**:
        * **Regional Routing**: Cloud Router only advertises subnets in its own region.
        * **Global Routing**: Cloud Router advertises all subnets from the VPC (all regions) to on-prem.
    * **全球 vs 區域路由**:
        * **區域路由**: Cloud Router 僅廣播其自身區域內的子網。
        * **全球路由**: Cloud Router 將 VPC（所有區域）中的所有子網廣播到地端。

---

### Cloud VPN
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Infrastructure)**. 經濟實惠的混合雲連線方案。
* **產品重要說明 (Product Description)**:
    * Cloud VPN securely connects your peer network to your Virtual Private Cloud (VPC) network through an IPsec VPN connection.
    * Cloud VPN 透過 IPsec VPN 連線安全地將您的對等網路連線到您的虛擬私有雲 (VPC) 網路。
    * Traffic travels over the public internet but is encrypted.
    * 流量在公共網際網路上傳輸，但是經過加密的。
* **主要功能 (Main Functions)**:
    * **HA VPN (High Availability)**: Offers a 99.99% SLA by using two interfaces and two external IPs.
    * **HA VPN (高可用性)**: 透過使用兩個介面和兩個外部 IP 提供 99.99% 的 SLA。
    * **Classic VPN**: Older generation, retiring. (SLA 99.9%).
    * **傳統 VPN**: 舊世代，即將退役。(SLA 99.9%)。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Establishing a secure link for a branch office to access cloud apps.
    * **架構師觀點**: 建立一個安全連結，供分公司存取雲端應用程式。
    * You set up an HA VPN gateway. It creates two tunnels. If one tunnel fails (internet hiccup or router maintenance), traffic switches to the other automatically via BGP routing.
    * 您設定一個 HA VPN 閘道。它建立兩條通道。如果一條通道失敗（網路中斷或路由器維護），流量會透過 BGP 路由自動切換到另一條。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Bandwidth**: Each tunnel supports up to 3 Gbps. HA VPN allows ECMP (Equal Cost Multi-Path) to bond tunnels for higher bandwidth.
    * **頻寬**: 每條通道支援高達 3 Gbps。HA VPN 允許 ECMP（等價多路徑）來綁定通道以獲得更高的頻寬。

---

### VPC Flow Logs
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security & Observability)**. 網路流量稽核與取證工具。
* **產品重要說明 (Product Description)**:
    * VPC Flow Logs record a sample of network flows sent from and received by VM instances.
    * VPC Flow Logs 記錄 VM 執行個體發送和接收的網路流量樣本。
    * They are critical for security monitoring and network forensics.
    * 它們對於安全監控和網路鑑識至關重要。
* **主要功能 (Main Functions)**:
    * **Visibility**: Shows who talked to whom (Source IP:Port -> Dest IP:Port).
    * **可視性**: 顯示誰與誰通訊（來源 IP:連接埠 -> 目的地 IP:連接埠）。
    * **Troubleshooting**: Helps identify why traffic is blocked (though Firewall Rules Logging is more specific for blocks).
    * **疑難排解**: 協助識別流量為何被封鎖（雖然防火牆規則記錄對於封鎖更具體）。
    * **Metadata**: Includes latency data (RTT).
    * **Metadata**: 包含延遲資料 (RTT)。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Security audit.
    * **架構師觀點**: 安全稽核。
    * You need to verify if any internal servers are communicating with a known malicious external IP.
    * 您需要驗證是否有任何內部伺服器正在與已知的惡意外部 IP 通訊。
    * You enable Flow Logs on the subnet, export the logs to BigQuery, and run a SQL query to check for connections to that bad IP.
    * 您在子網上啟用 Flow Logs，將日誌匯出到 BigQuery，並執行 SQL 查詢以檢查與該惡意 IP 的連線。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Sampling**: You can adjust the sampling rate (e.g., 0.1 for 10%) to save on log storage costs.
    * **取樣**: 您可以調整取樣率（例如 0.1 代表 10%）以節省日誌儲存成本。
    * **No Performance Impact**: Logs are collected outside the VM path, so enabling them does not slow down the network.
    * **無效能影響**: 日誌是在 VM 路徑之外收集的，因此啟用它們不會減慢網路速度。

---

### Firewall Insights
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security pillar)**. 優化防火牆規則與減少攻擊面的工具。
* **產品重要說明 (Product Description)**:
    * Firewall Insights analyzes your VPC firewall rules to provide insights into how they are being used.
    * Firewall Insights 分析您的 VPC 防火牆規則，以提供有關其使用情況的深入分析。
    * It helps detect misconfigurations and optimize rule sets.
    * 它有助於檢測錯誤配置並優化規則集。
* **主要功能 (Main Functions)**:
    * **Shadowed Rules**: Identifies rules that are completely blocked by a higher-priority rule (redundant).
    * **被遮蔽的規則**: 識別被較高優先順序規則完全阻擋的規則（多餘的）。
    * **Overly Permissive Rules**: Highlights rules that allow too much traffic (e.g., allow `0.0.0.0/0` on port 22).
    * **過度寬鬆的規則**: 強調允許過多流量的規則（例如，允許 `0.0.0.0/0` 存取連接埠 22）。
    * **Usage Tracking**: Shows which rules have not been hit in the last X days.
    * **使用追蹤**: 顯示哪些規則在過去 X 天內未被觸發。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Cleanup of legacy infrastructure.
    * **架構師觀點**: 清理舊有基礎設施。
    * A project has 100 firewall rules accumulated over 3 years. You use Firewall Insights to identify "Unused rules" and safely delete them to reduce complexity and security risk.
    * 一個專案累積了 3 年共 100 條防火牆規則。您使用 Firewall Insights 識別「未使用的規則」並安全地刪除它們，以降低複雜性和安全風險。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Dependency**: Requires Firewall Rules Logging to be enabled for the rules you want to analyze for usage.
    * **依賴性**: 需要為您想要分析使用情況的規則啟用防火牆規則記錄。

---

### Network Connectivity Center
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Infrastructure)**. 統一管理多點連接的中樞。
* **產品重要說明 (Product Description)**:
    * Network Connectivity Center (NCC) acts as a hub for connecting different networks together (Spoke).
    * Network Connectivity Center (NCC) 充當將不同網路連線在一起的中樞 (Hub)。
    * It uses Google's global backbone to connect on-premise sites, VPNs, and SD-WAN appliances.
    * 它使用 Google 的全球骨幹網路來連線地端站點、VPN 和 SD-WAN 設備。
* **主要功能 (Main Functions)**:
    * **Site-to-Site**: Connects your office in Tokyo to your office in New York using Google's network as the transit (Router Appliance).
    * **站點對站點**: 使用 Google 網路作為傳輸（路由器設備），將您在東京的辦公室連線到紐約的辦公室。
    * **Centralized Management**: Manages Cloud VPNs, Interconnects, and Router Appliances in a single place.
    * **集中管理**: 在單一位置管理 Cloud VPN、Interconnect 和路由器設備。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You want to replace your expensive MPLS WAN with Google's network.
    * **架構師觀點**: 您希望用 Google 的網路取代昂貴的 MPLS WAN。
    * You connect your branch offices to GCP via VPN/Interconnect and link them to the NCC Hub. Now, branch-to-branch traffic travels over Google's backbone.
    * 您透過 VPN/Interconnect 將分公司連線到 GCP，並將其連結到 NCC Hub。現在，分公司對分公司的流量透過 Google 的骨幹網路傳輸。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Data Transfer Costs**: You pay for traffic moving between spokes (e.g., Site A -> GCP -> Site B).
    * **資料傳輸成本**: 您需要支付在 Spoke 之間移動流量的費用（例如，站點 A -> GCP -> 站點 B）。

---

### Cloud Interconnect
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Infrastructure)**. 企業級專線連接方案。
* **產品重要說明 (Product Description)**:
    * Cloud Interconnect provides low-latency, high-availability connections between your on-premises network and Google Cloud.
    * Cloud Interconnect 在您的地端網路與 Google Cloud 之間提供低延遲、高可用性的連線。
    * It bypasses the public internet.
    * 它避開公共網際網路。
* **主要功能 (Main Functions)**:
    * **Dedicated Interconnect**: Physical cable connection directly to Google (10 Gbps or 100 Gbps).
    * **專用 Interconnect**: 直接連線到 Google 的實體纜線（10 Gbps 或 100 Gbps）。
    * **Partner Interconnect**: Connection via a service provider (bandwidths from 50 Mbps to 10 Gbps).
    * **合作夥伴 Interconnect**: 透過服務供應商連線（頻寬從 50 Mbps 到 10 Gbps）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: High-throughput Data Warehouse migration.
    * **架構師觀點**: 高吞吐量資料倉儲遷移。
    * You need to move 500 TB of data to BigQuery regularly and securely. Public internet VPN is too slow and unstable. You provision a 10G Dedicated Interconnect for consistent throughput.
    * 您需要定期且安全地將 500 TB 的資料移動到 BigQuery。公共網際網路 VPN 太慢且不穩定。您配置一條 10G 專用 Interconnect 以獲得一致的吞吐量。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **SLA Requirements**: To get the 99.99% SLA, you strictly need 4 circuits (2 in one metro, 2 in another metro). 99.9% requires 2 circuits in one metro.
    * **SLA 需求**: 為了獲得 99.99% 的 SLA，您嚴格需要 4 條電路（一個都會區 2 條，另一個都會區 2 條）。99.9% 需要在一個都會區有 2 條電路。

---

### Direct / Carrier Peering
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **No (Specialized Networking)**. 用於特定流量交換需求的非 GCP 資源連接。
* **產品重要說明 (Product Description)**:
    * Peering allows you to exchange internet traffic with Google at edge locations.
    * Peering 允許您在邊緣位置與 Google 交換網際網路流量。
    * *Crucial Distinction*: Unlike Interconnect, Peering connects you to *Google Services* (YouTube, Gmail, Workspace, Public Cloud APIs), not directly to your private VPC IP addresses (RFC 1918).
    * *關鍵區別*: 與 Interconnect 不同，Peering 將您連線到 *Google 服務*（YouTube, Gmail, Workspace, 公有雲 API），而不是直接連線到您的私人 VPC IP 位址 (RFC 1918)。
* **主要功能 (Main Functions)**:
    * **Direct Peering**: Direct physical link with Google.
    * **直接 Peering**: 與 Google 的直接實體連結。
    * **Carrier Peering**: Peering via a partner.
    * **電信業者 Peering**: 透過合作夥伴進行 Peering。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: An ISP wants to improve YouTube performance for its customers.
    * **架構師觀點**: 一家 ISP 希望為其客戶改善 YouTube 效能。
    * The ISP sets up Direct Peering with Google so that YouTube traffic flows directly to their network, skipping intermediate transit providers.
    * 該 ISP 與 Google 建立直接 Peering，以便 YouTube 流量直接流向其網路，跳過中間傳輸供應商。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Not for VPC Access**: Do not use Peering to access your Compute Engine VMs securely. Use Interconnect or VPN for that.
    * **不適用於 VPC 存取**: 請勿使用 Peering 來安全地存取您的 Compute Engine VM。請使用 Interconnect 或 VPN。

---

### Network Service Tiers
* **Knowledge Level**: 1: basics
* **附註**: 此項目已在上一批次中詳細說明。
* **產品重要說明 (Product Description)**:
    * (Duplicate) Premium vs Standard Tier options for routing external traffic.
    * (重複) 用於路由外部流量的進階與標準層級選項。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Recap**: Premium uses Google backbone (global). Standard uses public internet (regional).
    * **回顧**: 進階層級使用 Google 骨幹網路（全球）。標準層級使用公共網際網路（區域）。

---

### Cloud Router
* **Knowledge Level**: 2: medium
* **附註**: 此項目已在上一批次中詳細說明。
* **產品重要說明 (Product Description)**:
    * (Duplicate) The BGP control plane for VPN and Interconnect.
    * (重複) 用於 VPN 和 Interconnect 的 BGP 控制平面。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Recap**: Enables dynamic routing (Global/Regional) to propagate routes between VPC and on-prem.
    * **回顧**: 啟用動態路由（全球/區域）以在 VPC 和地端之間傳播路由。

---

### Network Intelligence Center
* **Knowledge Level**: 1: basics
* **附註**: 此項目已在上一批次中詳細說明。
* **產品重要說明 (Product Description)**:
    * (Duplicate) Observability and troubleshooting suite.
    * (重複) 可觀測性和疑難排解套件。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Recap**: Includes Connectivity Tests and Network Topology visualization.
    * **回顧**: 包含連線測試和網路拓撲視覺化。

---

### Packet Mirroring
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security pillar)**. 用於深度封包檢測 (DPI) 與入侵偵測系統 (IDS) 的基礎。
* **產品重要說明 (Product Description)**:
    * Packet Mirroring clones the traffic of specified VM instances and forwards it to a collector system for inspection.
    * Packet Mirroring 會複製指定 VM 執行個體的流量，並將其轉發到收集器系統進行檢查。
    * It captures all traffic (payload and headers) without disrupting the flow.
    * 它會擷取所有流量（酬載和標頭），而不會中斷流量傳輸。
* **主要功能 (Main Functions)**:
    * **Full Visibility**: Mirrors both ingress and egress traffic.
    * **完全可視性**: 鏡像傳入和傳出流量。
    * **Tool Integration**: Forwards traffic to third-party security appliances (e.g., Palo Alto, Fortinet) or Intrusion Detection Systems (IDS).
    * **工具整合**: 將流量轉發到第三方安全設備（例如 Palo Alto, Fortinet）或入侵偵測系統 (IDS)。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Security Compliance requiring Intrusion Detection (IDS).
    * **架構師觀點**: 需要入侵偵測 (IDS) 的安全合規性。
    * You need to inspect traffic for malware signatures. You configure a Packet Mirroring policy on your web servers to send a copy of all packets to an Internal Load Balancer fronting a group of IDS appliances.
    * 您需要檢查流量中的惡意軟體簽名。您在網頁伺服器上配置 Packet Mirroring 政策，將所有封包的副本傳送到前端為一組 IDS 設備的內部負載平衡器。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Sampler vs Mirror**: Flow Logs only sample headers (metadata). Packet Mirroring captures the actual data content (payload).
    * **取樣器 vs 鏡像**: Flow Logs 僅對標頭 (Metadata) 進行取樣。Packet Mirroring 擷取實際資料內容 (酬載)。
    * **Bandwidth**: Mirrored traffic counts against the instance's bandwidth limit.
    * **頻寬**: 鏡像流量計入執行個體的頻寬限制。

---

### Private Service Connect
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security pillar)**. 現代化、私密的服務存取方式，取代 VPC Peering。
* **產品重要說明 (Product Description)**:
    * Private Service Connect (PSC) allows private consumption of services across VPC networks without VPC Peering.
    * Private Service Connect (PSC) 允許跨 VPC 網路私密使用服務，而無需 VPC 對等互連。
    * It exposes a service via a private IP address in the consumer's VPC.
    * 它透過消費者 VPC 中的私人 IP 位址揭露服務。
* **主要功能 (Main Functions)**:
    * **Consumer-Producer Model**: One VPC (Producer) hosts the service; another VPC (Consumer) accesses it via a local IP endpoint.
    * **消費者-生產者模型**: 一個 VPC (生產者) 託管服務；另一個 VPC (消費者) 透過本地 IP 端點存取它。
    * **No CIDR Conflict**: Unlike Peering, IP ranges do not need to be unique between networks.
    * **無 CIDR 衝突**: 與 Peering 不同，IP 範圍不需要在網路之間是唯一的。
    * **Google APIs**: Securely access Google APIs (like Storage, BigQuery) from private IPs.
    * **Google API**: 從私人 IP 安全地存取 Google API（如 Storage, BigQuery）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Multi-tenant SaaS on GCP.
    * **架構師觀點**: GCP 上的多租戶 SaaS。
    * You are a SaaS provider. You want 100 different customers to access your service privately.
    * 您是 SaaS 供應商。您希望 100 個不同的客戶私密地存取您的服務。
    * VPC Peering won't work well due to IP overlap and peering limits (25 max). You use PSC to publish your service, and customers create a PSC endpoint in their VPCs to connect.
    * 由於 IP 重疊和對等互連限制（最多 25 個），VPC 對等互連效果不佳。您使用 PSC 發布您的服務，客戶在他們的 VPC 中建立 PSC 端點進行連線。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Scalability**: Overcomes the scaling limits of VPC Peering.
    * **可擴展性**: 克服了 VPC 對等互連的擴展限制。
    * **Forwarding Rule**: The "endpoint" in the consumer VPC is technically a Forwarding Rule.
    * **轉發規則**: 消費者 VPC 中的「端點」在技術上是一個轉發規則。

---

### Private Google Access
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security pillar)**. 確保內部 VM 存取 Google API 不走公網。
* **產品重要說明 (Product Description)**:
    * Private Google Access allows VMs with *only* internal IP addresses to reach the public IP addresses of Google APIs and services (like Cloud Storage, BigQuery).
    * Private Google Access 允許*僅*具有內部 IP 位址的 VM 到達 Google API 和服務（如 Cloud Storage, BigQuery）的公共 IP 位址。
    * Traffic stays entirely within Google's network.
    * 流量完全停留在 Google 網路內。
* **主要功能 (Main Functions)**:
    * **Security**: No need to assign external IPs to VMs just to access GCS or Pub/Sub.
    * **安全性**: 無需為了存取 GCS 或 Pub/Sub 而將外部 IP 指派給 VM。
    * **Subnet Level**: Enabled on a per-subnet basis.
    * **子網層級**: 以子網為單位啟用。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Data processing pipeline.
    * **架構師觀點**: 資料處理流程。
    * Your private GKE nodes need to push logs to Cloud Logging and read data from Cloud Storage.
    * 您的私人 GKE 節點需要將日誌推送到 Cloud Logging 並從 Cloud Storage 讀取資料。
    * You enable Private Google Access on the subnet. Even though the nodes have no internet access, they can reach `storage.googleapis.com` internally.
    * 您在子網上啟用 Private Google Access。即使節點沒有網際網路存取權限，它們也可以在內部連線到 `storage.googleapis.com`。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **DNS**: It relies on the default DNS resolution of Google domains to public IPs, but the network path intercepts this traffic and routes it internally.
    * **DNS**: 它依賴 Google 網域到公共 IP 的預設 DNS 解析，但網路路徑會攔截此流量並在內部進行路由。
    * **On-prem**: "Private Google Access for on-premises hosts" is a related feature allowing on-prem servers to do the same via VPN/Interconnect.
    * **地端**: 「適用於地端主機的 Private Google Access」是一項相關功能，允許地端伺服器透過 VPN/Interconnect 執行相同操作。

---

### VPC Routes
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Infrastructure)**. 控制網路流量流向的基礎機制。
* **產品重要說明 (Product Description)**:
    * Routes define the paths that network traffic takes from a VM instance to other destinations.
    * 路由定義網路流量從 VM 執行個體到其他目的地所採取的路徑。
    * Every VPC has a system-generated default route to the internet and to local subnets.
    * 每個 VPC 都有系統產生的通往網際網路和本地子網的預設路由。
* **主要功能 (Main Functions)**:
    * **Static Routes**: Manually defined routes (e.g., route `10.0.0.0/8` to a specific VPN gateway).
    * **靜態路由**: 手動定義的路由（例如，將 `10.0.0.0/8` 路由到特定的 VPN 閘道）。
    * **Policy Based Routing (PBR)**: Route traffic based on source IP, not just destination IP (Advanced).
    * **策略路由 (PBR)**: 根據來源 IP 而不僅僅是目的地 IP 路由流量（進階）。
    * **Tags**: Routes can apply only to VMs with specific network tags.
    * **標籤**: 路由可以僅套用到具有特定網路標籤的 VM。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Routing traffic through a firewall appliance (NAT Gateway instance).
    * **架構師觀點**: 透過防火牆設備（NAT 閘道執行個體）路由流量。
    * You create a custom static route for destination `0.0.0.0/0` with the "next hop" set to your Firewall VM instance. You apply this route to specific App VMs using a tag `route-through-firewall`.
    * 您為目的地 `0.0.0.0/0` 建立自定義靜態路由，將「下一跳」設定為您的防火牆 VM 執行個體。您使用標籤 `route-through-firewall` 將此路由套用到特定的應用程式 VM。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Priority**: More specific routes (longer prefix) take precedence. If prefixes are equal, priority (lower number) wins.
    * **優先順序**: 更具體的路由（較長的前綴）優先。如果前綴相同，則優先順序（較小的數字）獲勝。

---

### VPC Peering
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Infrastructure)**. 連接兩個獨立 VPC 的簡單方式。
* **產品重要說明 (Product Description)**:
    * VPC Network Peering allows you to connect two VPC networks so that workloads in different networks can communicate internally.
    * VPC 網路對等互連允許您連線兩個 VPC 網路，以便不同網路中的工作負載可以在內部進行通訊。
    * Traffic stays within Google's network.
    * 流量停留在 Google 網路內。
* **主要功能 (Main Functions)**:
    * **Performance**: No gateway bottleneck; runs at full line speed.
    * **效能**: 無閘道瓶頸；以全線速運行。
    * **Cross-Project**: Can peer VPCs in different projects or organizations.
    * **跨專案**: 可以對等互連不同專案或機構中的 VPC。
    * **Route Exchange**: Automatically exchanges subnet routes.
    * **路由交換**: 自動交換子網路由。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Mergers and Acquisitions.
    * **架構師觀點**: 合併與收購。
    * Company A buys Company B. Both have their own GCP Organizations and VPCs. You peer the two VPCs to allow immediate connectivity between their applications.
    * A 公司收購了 B 公司。兩者都有自己的 GCP 機構和 VPC。您將兩個 VPC 對等互連，以允許其應用程式之間立即連線。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Non-Transitive**: If VPC A peers with B, and B peers with C, A cannot talk to C. This is a major architectural constraint. (Use Shared VPC or VPN Hub-and-Spoke to solve this).
    * **不可傳遞**: 如果 VPC A 與 B 對等互連，且 B 與 C 對等互連，則 A 無法與 C 通訊。這是一個主要的架構限制。（使用共用 VPC 或 VPN Hub-and-Spoke 來解決此問題）。
    * **CIDR Overlap**: You cannot peer VPCs if they have overlapping subnet IP ranges.
    * **CIDR 重疊**: 如果 VPC 具有重疊的子網 IP 範圍，則無法進行對等互連。

---

### Shared VPC
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security & Operational Excellence)**. 大型組織集中管理網路的標準架構。
* **產品重要說明 (Product Description)**:
    * Shared VPC allows an organization to connect resources from multiple projects to a common VPC network.
    * 共用 VPC 允許機構將來自多個專案的資源連線到一個共同的 VPC 網路。
    * It separates network administration (Host Project) from application deployment (Service Projects).
    * 它將網路管理（主機專案）與應用程式部署（服務專案）分開。
* **主要功能 (Main Functions)**:
    * **Host Project**: The central project owning the VPC, subnets, firewall rules, and VPNs.
    * **主機專案**: 擁有 VPC、子網、防火牆規則和 VPN 的中央專案。
    * **Service Project**: Projects attached to the Host Project. Admins here can use the subnets but cannot modify network settings.
    * **服務專案**: 附加到主機專案的專案。此處的管理員可以使用子網，但無法修改網路設定。
    * **Centralized Control**: Security team manages firewalls in one place.
    * **集中控制**: 安全團隊在一個地方管理防火牆。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Enterprise Foundation Setup.
    * **架構師觀點**: 企業基礎設定。
    * You set up a "Networking Project" (Host). You create "Dev", "Test", "Prod" subnets.
    * 您設定一個「網路專案」(主機)。您建立 "Dev", "Test", "Prod" 子網。
    * You attach the "Shopping Cart App" project as a Service Project. The app developers deploy VMs into the "Prod" subnet without having permissions to change firewall rules or delete the subnet.
    * 您將「購物車應用程式」專案附加為服務專案。應用程式開發人員將 VM 部署到 "Prod" 子網中，而無需擁有更改防火牆規則或刪除子網的權限。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **IAM Separation**: `Compute Network User` role is granted to Service Project users on specific subnets of the Host Project.
    * **IAM 分離**: `Compute Network User` 角色被授予服務專案使用者，針對主機專案的特定子網。
    * **Organization Level**: Requires an Organization resource to function.
    * **機構層級**: 需要機構資源才能運作。

---

## Security and Identity

### Binary Authorization
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security - Software Supply Chain)**. 確保只有受信任的容器映像檔能被部署。
* **產品重要說明 (Product Description)**:
    * Binary Authorization is a deploy-time security control that ensures only trusted container images are deployed on Google Kubernetes Engine (GKE) or Cloud Run.
    * Binary Authorization 是一種部署時的安全控制，確保只有受信任的容器映像檔被部署在 Google Kubernetes Engine (GKE) 或 Cloud Run 上。
    * It enforces signature validation (attestations) before allowing a deployment.
    * 它在允許部署之前強制執行簽章驗證（證明）。
* **主要功能 (Main Functions)**:
    * **Policy Enforcement**: Define rules like "Images must be signed by the QA team attester".
    * **政策強制執行**: 定義規則，例如「映像檔必須由 QA 團隊證明者簽署」。
    * **Break-glass**: Allows bypassing the policy in emergencies, but logs the event for audit.
    * **緊急破窗 (Break-glass)**: 允許在緊急情況下繞過政策，但會記錄該事件以供稽核。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You want to prevent developers from deploying local, untested Docker images to Production.
    * **架構師觀點**: 您希望防止開發人員將本地、未經測試的 Docker 映像檔部署到正式環境。
    * You configure your CI/CD pipeline (Cloud Build) to sign the image after it passes automated tests. You set a Binary Authorization policy on the Prod GKE cluster to reject any image without that signature.
    * 您配置 CI/CD 流程 (Cloud Build) 在通過自動化測試後簽署映像檔。您在正式環境 GKE 叢集上設定 Binary Authorization 政策，以拒絕任何沒有該簽章的映像檔。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Attestors**: Entities (using KMS keys) that verify and sign images.
    * **證明者 (Attestors)**: 驗證並簽署映像檔的實體（使用 KMS 金鑰）。
    * **Dry Run Mode**: You can run policies in "audit only" mode to see what *would* be blocked without breaking production.
    * **試執行模式 (Dry Run)**: 您可以在「僅稽核」模式下執行政策，以查看什麼*會*被封鎖，而不會破壞正式環境。

---

### Cloud Data Loss Prevention
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security & Compliance)**. 自動發現與去識別化敏感資料。
* **產品重要說明 (Product Description)**:
    * Cloud DLP is a fully managed service designed to discover, classify, and protect sensitive data (PII).
    * Cloud DLP 是一個完全託管的服務，旨在發現、分類和保護敏感資料 (PII)。
    * It helps you manage data risk and comply with regulations like GDPR and HIPAA.
    * 它協助您管理資料風險並遵守 GDPR 和 HIPAA 等法規。
* **主要功能 (Main Functions)**:
    * **Inspection**: Scans Storage buckets, BigQuery tables, and Datastore for sensitive info (Credit Cards, SSNs).
    * **檢查**: 掃描 Storage buckets, BigQuery tables 和 Datastore 以尋找敏感資訊（信用卡、SSN）。
    * **De-identification**: Redacts, masks, or tokenizes sensitive data before it is used for analysis.
    * **去識別化**: 在資料用於分析之前，對敏感資料進行編輯、遮蔽或權杖化。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: You want to let your data science team analyze customer support logs in BigQuery.
    * **架構師觀點**: 您希望讓資料科學團隊分析 BigQuery 中的客戶支援日誌。
    * The logs contain emails and phone numbers. You create a DLP job to scan the logs and replace all emails with a masked string (e.g., `s***@gmail.com`) before the team gets access.
    * 日誌包含電子郵件和電話號碼。您建立一個 DLP 作業來掃描日誌，並在團隊獲得存取權限之前，將所有電子郵件替換為遮蔽字串（例如 `s***@gmail.com`）。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **InfoTypes**: DLP has over 120 built-in detectors (InfoTypes) for global PII (Passport numbers, Drivers licenses). You can also define custom regex InfoTypes.
    * **InfoTypes**: DLP 擁有超過 120 個內建偵測器 (InfoTypes)，用於全球 PII（護照號碼、駕照）。您也可以定義自定義 Regex InfoTypes。

---

### Cloud Key Management Service
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security - Data Protection)**. 集中管理加密金鑰的服務。
* **產品重要說明 (Product Description)**:
    * Cloud KMS allows you to manage cryptographic keys for your cloud services the same way you do on-premises.
    * Cloud KMS 允許您像在地端一樣管理雲端服務的加密金鑰。
    * You can generate, use, rotate, and destroy AES256, RSA, and EC keys.
    * 您可以產生、使用、輪替和銷毀 AES256, RSA 和 EC 金鑰。
* **主要功能 (Main Functions)**:
    * **CMEK (Customer-Managed Encryption Keys)**: Use your own keys to encrypt data in GCS, BigQuery, Compute Engine, etc., instead of Google-managed keys.
    * **CMEK (客戶管理的加密金鑰)**: 使用您自己的金鑰來加密 GCS, BigQuery, Compute Engine 等中的資料，而不是 Google 管理的金鑰。
    * **Automatic Rotation**: Set a rotation schedule (e.g., every 90 days) for symmetric keys.
    * **自動輪替**: 為對稱金鑰設定輪替排程（例如，每 90 天）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Highly regulated banking data.
    * **架構師觀點**: 高度監管的銀行資料。
    * The regulation requires that *you* control the encryption keys, not the cloud provider.
    * 法規要求*您*控制加密金鑰，而不是雲端供應商。
    * You create a key ring in Cloud KMS and generate a key. You then configure your Cloud Storage bucket to use this key (CMEK). If you destroy the key, the data in the bucket becomes cryptographically shredded (unreadable forever).
    * 您在 Cloud KMS 中建立一個金鑰環並產生一把金鑰。然後，您配置 Cloud Storage bucket 使用此金鑰 (CMEK)。如果您銷毀該金鑰，bucket 中的資料將被加密粉碎（永遠無法讀取）。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Separation of Duties**: IAM roles for Key Admin (manage keys) should be separate from Key Encrypter/Decrypter (use keys).
    * **職責分離**: 金鑰管理員（管理金鑰）的 IAM 角色應與金鑰加密/解密者（使用金鑰）分開。
    * **Location**: Keys are regional. You cannot use a key in `us-central1` to encrypt a bucket in `asia-east1`.
    * **位置**: 金鑰是區域性的。您不能使用 `us-central1` 中的金鑰來加密 `asia-east1` 中的 bucket。

---

### Cloud Security Command Center
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security - Detection)**. GCP 的集中式安全與風險儀表板。
* **產品重要說明 (Product Description)**:
    * Security Command Center (SCC) is the centralized vulnerability and threat reporting service for GCP.
    * Security Command Center (SCC) 是 GCP 的集中式漏洞和威脅報告服務。
    * It gives you asset inventory, discovery of vulnerabilities, and detection of threats.
    * 它為您提供資產清單、漏洞發現和威脅偵測。
* **主要功能 (Main Functions)**:
    * **Asset Discovery**: Real-time view of all GCP assets.
    * **資產探索**: 所有 GCP 資產的即時檢視。
    * **Security Health Analytics**: Detects common misconfigurations (e.g., open firewall ports, public buckets).
    * **安全健康分析**: 檢測常見的錯誤配置（例如，開放的防火牆連接埠、公共 bucket）。
    * **Event Threat Detection**: Uses logs to detect suspicious behavior (e.g., crypto mining).
    * **事件威脅偵測**: 使用日誌檢測可疑行為（例如，加密貨幣挖礦）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Continuous Compliance Monitoring.
    * **架構師觀點**: 持續合規監控。
    * You enable SCC Standard (Free) or Premium. You check the dashboard weekly to see "Findings".
    * 您啟用 SCC 標準版（免費）或進階版。您每週檢查儀表板以查看「調查結果」。
    * You see a high-severity finding: "Storage bucket world readable". You click it to identify the bucket and fix the IAM policy immediately.
    * 您看到一個高嚴重性的調查結果：「Storage bucket 全球可讀」。您點擊它以識別該 bucket 並立即修復 IAM 政策。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Tiers**: Standard is free (Asset inventory + Health Analytics basics). Premium adds Event Threat Detection, Container Threat Detection, and regulatory compliance reports.
    * **層級**: 標準版是免費的（資產清單 + 健康分析基礎）。進階版增加了事件威脅偵測、容器威脅偵測和法規合規報告。

---

### VPC Service Controls
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security - Data Protection)**. 防止資料透過 Google API 外洩 (Exfiltration) 的邊界防護。
* **產品重要說明 (Product Description)**:
    * VPC Service Controls allow you to define a security perimeter around Google Cloud resources (like Cloud Storage buckets, BigQuery datasets).
    * VPC Service Controls 允許您在 Google Cloud 資源（如 Cloud Storage buckets, BigQuery 資料集）周圍定義安全邊界。
    * It prevents data from being copied out of the perimeter to unauthorized external resources.
    * 它防止資料從邊界複製到未經授權的外部資源。
* **主要功能 (Main Functions)**:
    * **Service Perimeters**: Virtual boundaries that block API access from outside unless explicitly allowed.
    * **服務邊界**: 虛擬邊界，除非明確允許，否則阻止來自外部的 API 存取。
    * **Context-aware Access**: Allow access based on IP, identity, or device trust level.
    * **情境感知存取**: 根據 IP、身分或裝置信任層級允許存取。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Preventing insider data theft.
    * **架構師觀點**: 防止內部人員竊取資料。
    * An employee has access to a corporate BigQuery dataset. Without VPC SC, they could run a query and save the results to their *personal* Gmail GCS bucket.
    * 一名員工有權存取公司 BigQuery 資料集。如果沒有 VPC SC，他們可以執行查詢並將結果儲存到他們的*個人* Gmail GCS bucket。
    * With VPC SC perimeter around BigQuery, this "copy to external" operation is blocked at the API level.
    * 透過在 BigQuery 周圍設定 VPC SC 邊界，這種「複製到外部」的操作會在 API 層級被封鎖。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Dry Run**: Extremely important to configure in Dry Run mode first. VPC SC is complex and can easily break legitimate automated pipelines if misconfigured.
    * **試執行**: 首先在試執行模式下配置非常重要。VPC SC 很複雜，如果配置錯誤，很容易破壞合法的自動化流程。

---

### Web Security Scanner
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security - AppSec)**. 自動化 Web 應用程式漏洞掃描。
* **產品重要說明 (Product Description)**:
    * Web Security Scanner scans your App Engine, GKE, and Compute Engine web applications for common vulnerabilities.
    * Web Security Scanner 掃描您的 App Engine, GKE 和 Compute Engine Web 應用程式以尋找常見漏洞。
    * It follows links and attempts to exercise user inputs.
    * 它會跟隨連結並嘗試執行使用者輸入。
* **主要功能 (Main Functions)**:
    * **Vulnerability Detection**: Finds XSS (Cross-site scripting), Flash injection, mixed content (HTTP/HTTPS), and outdated libraries.
    * **漏洞偵測**: 尋找 XSS (跨站腳本攻擊)、Flash 注入、混合內容 (HTTP/HTTPS) 和過時的函式庫。
    * **Dashboard**: Integrated into the Security Command Center.
    * **儀表板**: 整合到 Security Command Center 中。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Pre-launch check.
    * **架構師觀點**: 發布前檢查。
    * Before going live with a new App Engine app, you run a scan. It reports that you have a "Mixed Content" warning because one image is loaded over HTTP instead of HTTPS. You fix it before launch.
    * 在上線新的 App Engine 應用程式之前，您執行掃描。它報告您有一個「混合內容」警告，因為有一張圖片是透過 HTTP 而不是 HTTPS 載入的。您在發布前修復它。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Authentication**: Can scan behind login pages (supports Google Accounts and non-Google accounts).
    * **身分驗證**: 可以掃描登入頁面背後的內容（支援 Google 帳戶和非 Google 帳戶）。
    * **No Denial of Service**: It is designed *not* to flood the app, but caution is needed for production scans.
    * **無阻斷服務**: 它的設計*不是*為了淹沒應用程式，但對正式環境掃描需要謹慎。

---

### Cloud EKM
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security - Trust)**. 外部金鑰管理，讓您完全掌握金鑰所有權。
* **產品重要說明 (Product Description)**:
    * Cloud External Key Manager (EKM) allows you to use keys that you manage *outside* of Google Cloud to encrypt data *inside* Google Cloud.
    * Cloud External Key Manager (EKM) 允許您使用您在 Google Cloud *外部*管理的金鑰來加密 Google Cloud *內部*的資料。
    * The key material never leaves the external key manager.
    * 金鑰材料永遠不會離開外部金鑰管理器。
* **主要功能 (Main Functions)**:
    * **Third-party Integration**: Works with partners like Thales, Fortanix, Equinix.
    * **第三方整合**: 與 Thales, Fortanix, Equinix 等合作夥伴合作。
    * **Full Control**: If you deny access on your external HSM, Google immediately loses the ability to decrypt your data.
    * **完全控制**: 如果您拒絕外部 HSM 上的存取，Google 會立即失去解密您資料的能力。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Data Sovereignty.
    * **架構師觀點**: 資料主權。
    * A European government agency requires that encryption keys must never be stored in a US-owned cloud provider's infrastructure.
    * 歐洲政府機構要求加密金鑰絕不能儲存在美國擁有的雲端供應商的基礎設施中。
    * You use Cloud EKM to keep keys in a local European HSM (Hardware Security Module). Google Cloud services call out to this HSM for every decryption operation.
    * 您使用 Cloud EKM 將金鑰保存在本地歐洲 HSM (硬體安全模組) 中。Google Cloud 服務每次解密操作都會呼叫此 HSM。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Latency & Availability**: Introduces a dependency on the external key manager. If the connection to your external HSM goes down, your data on Google Cloud becomes inaccessible.
    * **延遲與可用性**: 引入了對外部金鑰管理器的依賴。如果與外部 HSM 的連線中斷，您在 Google Cloud 上的資料將無法存取。

---

### Cloud HSM
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security - Compliance)**. 滿足 FIPS 140-2 Level 3 合規性需求的雲端硬體安全模組。
* **產品重要說明 (Product Description)**:
    * Cloud HSM (Hardware Security Module) provides cloud-hosted hardware security modules to protect your cryptographic keys.
    * Cloud HSM (硬體安全模組) 提供雲端託管的硬體安全模組來保護您的加密金鑰。
    * It is fully integrated with Cloud KMS.
    * 它與 Cloud KMS 完全整合。
    * It enables you to meet compliance mandates like FIPS 140-2 Level 3.
    * 它使您能夠滿足 FIPS 140-2 Level 3 等合規性要求。
* **主要功能 (Main Functions)**:
    * **Hardware Protection**: Keys are stored in tamper-resistant hardware devices, not just software.
    * **硬體保護**: 金鑰儲存在防篡改硬體裝置中，而不僅僅是軟體中。
    * **Managed Service**: Google manages the clustering, scaling, and patching of the HSMs.
    * **託管服務**: Google 管理 HSM 的叢集、擴展和修補。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: PCI-DSS Compliance.
    * **架構師觀點**: PCI-DSS 合規性。
    * Your payment processing application requires that the master encryption key used to protect credit card data is stored in a FIPS 140-2 Level 3 validated device.
    * 您的支付處理應用程式要求用於保護信用卡資料的主加密金鑰必須儲存在經過 FIPS 140-2 Level 3 驗證的裝置中。
    * You select "HSM" as the protection level when creating the key ring in Cloud KMS. The API experience remains the same, but the backend storage is hardware-backed.
    * 在 Cloud KMS 中建立金鑰環時，您選擇「HSM」作為保護等級。API 體驗保持不變，但後端儲存是硬體支援的。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Cost**: Cloud HSM keys are significantly more expensive than software keys.
    * **成本**: Cloud HSM 金鑰比軟體金鑰昂貴得多。
    * **Availability**: Keys are available in specific regions where Google has HSM hardware deployed.
    * **可用性**: 金鑰僅在 Google 部署了 HSM 硬體的特定區域可用。

---

### Confidential Computing
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security - Data Protection)**. 填補「使用中資料 (Data in Use)」的加密缺口。
* **產品重要說明 (Product Description)**:
    * Confidential Computing encrypts data *while it is being processed* (in memory).
    * 機密運算 (Confidential Computing) 會在*資料處理過程中*（在記憶體中）對資料進行加密。
    * Standard cloud security encrypts data at rest (storage) and in transit (network). Confidential Computing adds the third pillar: data in use.
    * 標準雲端安全加密靜態資料（儲存）和傳輸中資料（網路）。機密運算增加了第三個支柱：使用中資料。
    * It uses AMD SEV (Secure Encrypted Virtualization) technology.
    * 它使用 AMD SEV (安全加密虛擬化) 技術。
* **主要功能 (Main Functions)**:
    * **Memory Encryption**: RAM is encrypted. Even if an attacker gains physical access to the server or hypervisor, they cannot read the memory dump.
    * **記憶體加密**: RAM 已加密。即使攻擊者獲得對伺服器或 Hypervisor 的實體存取權限，他們也無法讀取記憶體傾印。
    * **Confidential VMs**: Easy to enable (checkbox) when creating a VM instance.
    * **機密 VM**: 建立 VM 執行個體時易於啟用（核取方塊）。
    * **Confidential GKE**: Encrypts GKE nodes processing sensitive workloads.
    * **機密 GKE**: 加密處理敏感工作負載的 GKE 節點。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Multi-party computation in healthcare.
    * **架構師觀點**: 醫療保健中的多方計算。
    * Two hospitals want to collaborate on a model without seeing each other's raw patient data. They run the computation on a Confidential VM. The data is encrypted in memory, ensuring neither party (nor Google) can peek at the raw data during processing.
    * 兩家醫院希望合作建立一個模型，但不想看到對方的原始病患資料。他們在機密 VM 上執行運算。資料在記憶體中加密，確保任何一方（以及 Google）都無法在處理過程中窺視原始資料。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Performance Impact**: There is a slight performance overhead due to real-time memory encryption/decryption, but it is usually negligible for most apps.
    * **效能影響**: 由於即時記憶體加密/解密，會有輕微的效能開銷，但對於大多數應用程式來說通常可以忽略不計。

---

### Service Accounts
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security - Identity)**. 機器身分管理的基礎。
* **產品重要說明 (Product Description)**:
    * A Service Account (SA) is a special type of Google account intended to represent a non-human user (application, VM, or workload).
    * 服務帳戶 (SA) 是一種類殊類型的 Google 帳戶，旨在代表非人類使用者（應用程式、VM 或工作負載）。
    * It is authenticated via keys (JSON files) or natively via GCP infrastructure (Metadata server).
    * 它透過金鑰（JSON 檔案）或原生透過 GCP 基礎設施（Metadata 伺服器）進行身分驗證。
* **主要功能 (Main Functions)**:
    * **Identity**: Provides an email address (e.g., `app@project.iam.gserviceaccount.com`) to identify the app.
    * **身分**: 提供一個電子郵件地址（例如 `app@project.iam.gserviceaccount.com`）來識別應用程式。
    * **Authorization**: Granted IAM roles to access resources.
    * **授權**: 被授予 IAM 角色以存取資源。
    * **Impersonation**: Users can "act as" a service account to perform tasks.
    * **模擬**: 使用者可以「充當」服務帳戶來執行任務。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: VM accessing Cloud Storage.
    * **架構師觀點**: VM 存取 Cloud Storage。
    * Instead of embedding credentials in code, you assign a User-Managed Service Account to the VM. The code uses Application Default Credentials (ADC) to automatically discover the SA and authenticate.
    * 您無需在程式碼中嵌入憑證，而是將使用者管理的服務帳戶指派給 VM。程式碼使用應用程式預設憑證 (ADC) 自動發現 SA 並進行身分驗證。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Key Management**: Avoid downloading JSON keys whenever possible. Use Workload Identity (for GKE) or attached Service Accounts (for Compute). Keys are a major security risk (leakage).
    * **金鑰管理**: 盡可能避免下載 JSON 金鑰。使用 Workload Identity (適用於 GKE) 或附加服務帳戶 (適用於 Compute)。金鑰是一個主要的資安風險（洩露）。
    * **Default SA**: The default Compute Engine SA has the primitive `Editor` role, which is too broad. Always create custom SAs with least privilege.
    * **預設 SA**: 預設的 Compute Engine SA 具有原始的 `Editor` 角色，權限太過廣泛。始終建立具有最低權限的自定義 SA。

---

### Access Transparency
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security - Trust)**. 監控 Google 支援人員存取行為的日誌。
* **產品重要說明 (Product Description)**:
    * Access Transparency provides you with logs of actions taken by Google staff when accessing your content.
    * Access Transparency 為您提供 Google 員工在存取您的內容時所採取行動的日誌。
    * Normally, Google does not access your data. However, during a support case, they might need to.
    * 通常，Google 不會存取您的資料。但是，在支援案例期間，他們可能需要這樣做。
* **主要功能 (Main Functions)**:
    * **Audit Logs**: Captures the "why", "who", "when", and "what" of Google's access.
    * **稽核日誌**: 擷取 Google 存取的「原因」、「人員」、「時間」和「內容」。
    * **Justification**: Includes the Support Ticket number or reason for access.
    * **理由**: 包含支援票證編號或存取原因。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Compliance Audit.
    * **架構師觀點**: 合規性稽核。
    * An auditor asks: "Can you prove that the cloud provider isn't secretly reading your database?"
    * 稽核員問：「你能證明雲端供應商沒有秘密讀取你的資料庫嗎？」
    * You show them the Access Transparency logs which are empty, proving no Google engineer accessed the data. Or, if there are entries, they correlate perfectly with the support tickets you opened.
    * 您向他們展示空白的 Access Transparency 日誌，證明沒有 Google 工程師存取過資料。或者，如果有條目，它們與您開啟的支援票證完全相關。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Approval**: "Access Approval" is a related feature where you must explicitly *approve* the access request before Google can touch the data (Access Transparency just logs it).
    * **核准**: 「存取核准 (Access Approval)」是一項相關功能，您必須明確*核准*存取請求，Google 才能接觸資料（Access Transparency 只是記錄它）。

---

### BeyondCorp / BeyonProd model
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security - Zero Trust)**. Google 的零信任安全模型架構。
* **產品重要說明 (Product Description)**:
    * **BeyondCorp** is Google's implementation of the Zero Trust model for user access. It shifts access controls from the network perimeter (VPN) to individual users and devices.
    * **BeyondCorp** 是 Google 針對使用者存取的零信任模型的實作。它將存取控制從網路邊界 (VPN) 轉移到個別使用者和裝置。
    * **BeyondProd** applies the same Zero Trust principles to service-to-service communication (microservices).
    * **BeyondProd** 將相同的零信任原則應用於服務對服務通訊（微服務）。
* **主要功能 (Main Functions)**:
    * **Identity-Aware Proxy (IAP)**: The core tool for BeyondCorp. Access based on identity, not VPN.
    * **Identity-Aware Proxy (IAP)**: BeyondCorp 的核心工具。基於身分而非 VPN 的存取。
    * **Context**: Checks device health, location, and user identity before granting access.
    * **情境**: 在授予存取權限之前檢查裝置健康狀況、位置和使用者身分。
    * **Mutual TLS (mTLS)**: The core of BeyondProd. Services authenticate each other via certificates.
    * **相互 TLS (mTLS)**: BeyondProd 的核心。服務透過憑證相互驗證。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Remote workforce.
    * **架構師觀點**: 遠端工作力。
    * Instead of forcing all employees to use a VPN to access the internal corporate portal, you expose the portal via IAP.
    * 您無需強制所有員工使用 VPN 存取內部公司入口網站，而是透過 IAP 揭露該入口網站。
    * Employees can access it from any coffee shop, but only if they log in with their corporate account AND utilize a managed corporate laptop (Context).
    * 員工可以在任何咖啡店存取它，但前提是他們使用公司帳戶登入*並且*使用受管理的公司筆記型電腦（情境）。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **No VPN**: The slogan is "No more VPNs". Access is application-specific, not network-wide.
    * **無 VPN**: 口號是「不再有 VPN」。存取是針對特定應用程式的，而不是整個網路。

---

### Organization Policy Service
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security & Governance)**. 對雲端資源施加的強制性護欄。
* **產品重要說明 (Product Description)**:
    * Organization Policy Service gives you centralized and programmatic control over your organization's cloud resources.
    * Organization Policy Service 為您提供對機構雲端資源的集中式和程式化控制。
    * Unlike IAM (which says "who" can do what), Org Policy says "what" can be done (restrictions).
    * 與 IAM（說明「誰」可以做什麼）不同，Org Policy 說明可以做「什麼」（限制）。
* **主要功能 (Main Functions)**:
    * **Constraints**: Predefined rules you can enforce.
    * **限制**: 您可以強制執行的預定義規則。
    * **List Constraints**: Allow/Deny specific values (e.g., restrict VM creation to `asia-east1` only).
    * **清單限制**: 允許/拒絕特定值（例如，限制僅在 `asia-east1` 建立 VM）。
    * **Boolean Constraints**: Enforce a feature on/off (e.g., Disable External IP creation for VMs).
    * **布林限制**: 強制開啟/關閉某項功能（例如，停用 VM 的外部 IP 建立）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Preventing Shadow IT and Data Residency violations.
    * **架構師觀點**: 防止影子 IT 和資料駐留違規。
    * You set an Organization Policy `constraints/gcp.resourceLocations` to allow only `europe-west1`.
    * 您設定機構政策 `constraints/gcp.resourceLocations` 以僅允許 `europe-west1`。
    * Now, even if a user has "Owner" permissions, they simply cannot create a bucket or VM in `us-central1`. The API will reject the request.
    * 現在，即使使用者擁有 "Owner" 權限，他們也無法在 `us-central1` 建立 bucket 或 VM。API 將拒絕該請求。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Hierarchy**: Policies are inherited. Org level -> Folder -> Project. You can override policies at lower levels if allowed.
    * **階層**: 政策是繼承的。機構層級 -> 資料夾 -> 專案。如果允許，您可以在較低層級覆寫政策。
    * **IAM vs Org Policy**: IAM grants permission. Org Policy restricts the resource configuration. Both must pass for an action to succeed.
    * **IAM vs Org Policy**: IAM 授予權限。Org Policy 限制資源組態。兩者都必須通過，動作才能成功。

---

## Identity and access

### Cloud IAM
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security pillar)**. GCP 的存取控制核心。
* **產品重要說明 (Product Description)**:
    * Cloud Identity and Access Management (IAM) lets you authorize who can take action on specific resources.
    * Cloud IAM (身分與存取管理) 讓您授權誰可以對特定資源採取行動。
    * It unifies access control for Google Cloud services into a single system.
    * 它將 Google Cloud 服務的存取控制統一到單一系統中。
* **主要功能 (Main Functions)**:
    * **Who (Identity)**: Google Account, Service Account, Cloud Identity user/group.
    * **Who (身分)**: Google 帳戶、服務帳戶、Cloud Identity 使用者/群組。
    * **Can do what (Role)**: A collection of permissions (e.g., `compute.instances.start`).
    * **Can do what (角色)**: 權限的集合（例如 `compute.instances.start`）。
    * **On which resource**: Project, Folder, Bucket, etc.
    * **On which resource (資源)**: 專案、資料夾、Bucket 等。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Least Privilege Principle.
    * **架構師觀點**: 最小權限原則。
    * You have a developer who needs to debug an application on a VM but shouldn't be able to delete the VM or change the firewall.
    * 您有一位開發人員需要在 VM 上偵錯應用程式，但不應能夠刪除 VM 或更改防火牆。
    * Instead of giving `Editor` (too broad), you give them `Compute Instance Admin (v1)` role on that specific project.
    * 您不給予 `Editor`（太寬泛），而是給予他們在該特定專案上的 `Compute Instance Admin (v1)` 角色。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Basic vs Predefined vs Custom Roles**:
        * **Basic**: Owner, Editor, Viewer (Avoid using these in production).
        * **Predefined**: Granular roles managed by Google (e.g., `Storage Object Viewer`).
        * **Custom**: You pick specific permissions. User's responsibility to maintain.
    * **基本 vs 預定義 vs 自定義角色**:
        * **基本**: 擁有者、編輯者、檢視者（避免在正式環境中使用這些）。
        * **預定義**: 由 Google 管理的精細角色（例如 `Storage Object Viewer`）。
        * **自定義**: 您挑選特定的權限。使用者的維護責任。
    * **Inheritance**: Permissions flow down: Organization -> Folder -> Project -> Resource. A user with `Owner` at the Org level is `Owner` everywhere.
    * **繼承**: 權限向下流動：機構 -> 資料夾 -> 專案 -> 資源。在機構層級擁有 `Owner` 權限的使用者在任何地方都是 `Owner`。

---

### Cloud Identity
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security - Identity)**. 企業級身分即服務 (IDaaS) 解決方案。
* **產品重要說明 (Product Description)**:
    * Cloud Identity is an Identity as a Service (IDaaS) solution that manages users and groups.
    * Cloud Identity 是一個管理使用者和群組的身分即服務 (IDaaS) 解決方案。
    * It is essentially the "non-Gmail" version of Google Workspace (G Suite). It allows you to create corporate Google accounts (`alice@company.com`) without paying for Gmail/Drive if you don't need them.
    * 它本質上是 Google Workspace (G Suite) 的「非 Gmail」版本。它允許您建立公司 Google 帳戶 (`alice@company.com`)，如果您不需要 Gmail/Drive，則無需為其付費。
* **主要功能 (Main Functions)**:
    * **User Lifecycle**: Create, suspend, delete users.
    * **使用者生命週期**: 建立、暫停、刪除使用者。
    * **SSO (Single Sign-On)**: Integrate with on-prem Active Directory or Okta/Azure AD.
    * **SSO (單一登入)**: 與地端 Active Directory 或 Okta/Azure AD 整合。
    * **MFA (Multi-Factor Authentication)**: Enforce 2-step verification.
    * **MFA (多因素驗證)**: 強制執行雙步驟驗證。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Syncing Active Directory.
    * **架構師觀點**: 同步 Active Directory。
    * Your company uses Microsoft Active Directory (AD) on-prem. You use **Google Cloud Directory Sync (GCDS)** to sync users from AD to Cloud Identity.
    * 貴公司在地端使用 Microsoft Active Directory (AD)。您使用 **Google Cloud Directory Sync (GCDS)** 將使用者從 AD 同步到 Cloud Identity。
    * When a new employee is added to AD, their Google Cloud account is automatically created. When they leave, it's suspended.
    * 當新員工新增至 AD 時，他們的 Google Cloud 帳戶會自動建立。當他們離職時，帳戶會被暫停。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Free Edition**: Cloud Identity Free edition allows up to 50 users (and more upon request). Premium adds advanced mobile management.
    * **免費版**: Cloud Identity 免費版允許最多 50 個使用者（應請求可增加）。進階版增加了進階行動管理功能。
    * **Unmanaged Accounts**: If users previously created personal Google accounts with their corporate email (`bob@company.com`), Cloud Identity helps you "evict" or "transfer" these conflicting accounts.
    * **非受管帳戶**: 如果使用者先前使用其公司電子郵件 (`bob@company.com`) 建立了個人 Google 帳戶，Cloud Identity 可協助您「驅逐」或「轉移」這些衝突的帳戶。

---

### Cloud Identity-Aware Proxy
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security - Zero Trust)**. 零信任存取的關鍵閘道。
* **產品重要說明 (Product Description)**:
    * Identity-Aware Proxy (IAP) controls access to your cloud applications running on App Engine, Compute Engine, and GKE.
    * Identity-Aware Proxy (IAP) 控制對運行在 App Engine, Compute Engine 和 GKE 上的雲端應用程式的存取。
    * It verifies user identity and context ensuring that only authorized users can access the app.
    * 它驗證使用者身分和情境，確保只有經授權的使用者才能存取應用程式。
* **主要功能 (Main Functions)**:
    * **Centralized Access Control**: Manage access via IAM roles, not firewall rules.
    * **集中式存取控制**: 透過 IAM 角色而非防火牆規則來管理存取。
    * **TCP Forwarding**: Allows SSH/RDP access to VMs without public IPs (via IAP Tunnel).
    * **TCP 轉發**: 允許在沒有公共 IP 的情況下對 VM 進行 SSH/RDP 存取（透過 IAP 通道）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Internal Admin Tool.
    * **架構師觀點**: 內部管理工具。
    * You have an internal dashboard running on a VM. You don't want to expose it to the public internet or manage VPNs.
    * 您有一個在 VM 上運行的內部儀表板。您不想將其暴露給公共網際網路或管理 VPN。
    * You enable IAP. Now, when a user visits the URL, they are redirected to Google Sign-In. If they have the `IAP-Secured Web App User` role, traffic is passed through. If not, they get a 403. The VM remains private.
    * 您啟用 IAP。現在，當使用者訪問該 URL 時，他們會被重新導向到 Google 登入。如果他們擁有 `IAP-Secured Web App User` 角色，流量就會通過。如果沒有，他們會收到 403 錯誤。VM 保持私密。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Headers**: IAP passes the user identity to the backend app in the `X-Goog-Authenticated-User-Email` header.
    * **標頭**: IAP 透過 `X-Goog-Authenticated-User-Email` 標頭將使用者身分傳遞給後端應用程式。

---

### Identity Platform
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Modernization)**. 為您的應用程式提供客戶身分與存取管理 (CIAM)。
* **產品重要說明 (Product Description)**:
    * Identity Platform is a customer identity and access management (CIAM) platform.
    * Identity Platform 是一個客戶身分與存取管理 (CIAM) 平台。
    * It helps you add authentication to your applications (web/mobile) for *your* end users (not your employees).
    * 它協助您為*您的*終端使用者（而非您的員工）將身分驗證新增至您的應用程式（Web/行動）。
    * It is the enterprise evolution of Firebase Authentication.
    * 它是 Firebase Authentication 的企業進化版。
* **主要功能 (Main Functions)**:
    * **Multi-tenancy**: Host multiple distinct user bases in a single project.
    * **多租戶**: 在單一專案中託管多個不同的使用者群。
    * **Broad Provider Support**: Google, Facebook, Twitter, Microsoft, OIDC, SAML.
    * **廣泛的供應商支援**: Google, Facebook, Twitter, Microsoft, OIDC, SAML。
    * **SLA**: Enterprise-grade SLA (unlike Firebase Auth free tier).
    * **SLA**: 企業級 SLA（與 Firebase Auth 免費層級不同）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: B2B SaaS Application.
    * **架構師觀點**: B2B SaaS 應用程式。
    * You are building an app used by different companies.
    * 您正在建立一個供不同公司使用的應用程式。
    * You use Identity Platform's multi-tenancy feature to isolate the users of "Company A" from "Company B", allowing Company A to use their own Okta for login while Company B uses Google Sign-In.
    * 您使用 Identity Platform 的多租戶功能將「A 公司」的使用者與「B 公司」隔離開來，允許 A 公司使用他們自己的 Okta 登入，而 B 公司使用 Google 登入。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Relationship**: It shares the SDK with Firebase Auth but adds enterprise features like OIDC/SAML support and multi-tenancy.
    * **關係**: 它與 Firebase Auth 共用 SDK，但增加了 OIDC/SAML 支援和多租戶等企業功能。

---

### Managed Service for Microsoft Active Directory
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Migration)**. 託管的 AD 服務，簡化依賴 AD 的應用程式遷移。
* **產品重要說明 (Product Description)**:
    * This service provides a highly available, hardened Google-managed Microsoft Active Directory (AD).
    * 此服務提供高可用性、經過強化的 Google 託管 Microsoft Active Directory (AD)。
    * It allows you to run AD-dependent workloads on GCP without maintaining AD domain controllers yourself.
    * 它允許您在 GCP 上運行依賴 AD 的工作負載，而無需自己維護 AD 網域控制站。
* **主要功能 (Main Functions)**:
    * **Compatibility**: Supports standard AD features like Group Policy, Trusts, and LDAP/Kerberos.
    * **相容性**: 支援標準 AD 功能，如群組原則、信任和 LDAP/Kerberos。
    * **Trusts**: Can create a trust relationship with your on-prem AD.
    * **信任**: 可以與您的地端 AD 建立信任關係。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Windows App Migration.
    * **架構師觀點**: Windows 應用程式遷移。
    * You are lifting-and-shifting a legacy Windows application that requires domain joining and LDAP authentication.
    * 您正在直接轉移 (lift-and-shift) 一個需要網域加入和 LDAP 驗證的舊版 Windows 應用程式。
    * Instead of deploying Windows VMs and installing AD DS manually (managing patches, backups, HA), you launch Managed Service for Microsoft AD. The app VMs join this managed domain seamlessly.
    * 您啟動 Managed Service for Microsoft AD，而不是手動部署 Windows VM 並安裝 AD DS（管理修補程式、備份、HA）。應用程式 VM 無縫加入此託管網域。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Domain Controller Access**: You do *not* get Domain Admin or RDP access to the Domain Controllers. You get a delegated admin account.
    * **網域控制站存取**: 您*不*會獲得網域控制站的網域管理員或 RDP 存取權限。您會獲得一個委派的管理員帳戶。

---

### Resource Manager
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Governance)**. 定義 GCP 資源階層結構的服務。
* **產品重要說明 (Product Description)**:
    * Resource Manager enables you to centrally manage projects, folders, and organizations.
    * Resource Manager 使您能夠集中管理專案、資料夾和機構。
    * It defines the hierarchy: Organization -> Folders -> Projects -> Resources.
    * 它定義了階層結構：機構 -> 資料夾 -> 專案 -> 資源。
* **主要功能 (Main Functions)**:
    * **Organization Node**: Root node for the Google Cloud hierarchy.
    * **機構節點**: Google Cloud 階層的根節點。
    * **Folders**: Group projects for easier policy/IAM administration (e.g., Dept: Finance, Dept: HR).
    * **資料夾**: 將專案分組以便更輕鬆地進行政策/IAM 管理（例如，部門：財務，部門：人資）。
    * **Projects**: The entity that holds resources and enables billing/APIs.
    * **專案**: 持有資源並啟用帳單/API 的實體。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Structuring for a large enterprise.
    * **架構師觀點**: 為大型企業建構結構。
    * You design the hierarchy based on business units, not technical environments.
    * 您根據業務單位而非技術環境來設計階層。
    * `Organization` -> `Folder: Retail` -> `Folder: Online Store` -> `Project: Production`.
    * `機構` -> `資料夾：零售` -> `資料夾：線上商店` -> `專案：正式環境`。
    * You apply strict Organization Policies at the `Retail` folder level (e.g., restrict regions to US only) which are inherited by all projects underneath.
    * 您在 `零售` 資料夾層級套用嚴格的機構政策（例如，限制僅限美國區域），這些政策會被下面的所有專案繼承。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Immutability**: Projects can be moved between folders. Resources (like VMs) *cannot* be moved between projects (usually need migration/recreation).
    * **不可變性**: 專案可以在資料夾之間移動。資源（如 VM）*不能*在專案之間移動（通常需要遷移/重新建立）。

---

### IAM Conditions
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security - Least Privilege)**. 基於屬性的存取控制 (ABAC)。
* **產品重要說明 (Product Description)**:
    * IAM Conditions allow you to define conditional attribute-based access control for IAM policies.
    * IAM Conditions 允許您為 IAM 政策定義基於屬性的條件式存取控制。
    * You can grant a role only if specific conditions are met (e.g., time of day, resource name prefix).
    * 只有在滿足特定條件（例如一天中的時間、資源名稱前綴）時，您才能授予角色。
* **主要功能 (Main Functions)**:
    * **Time-based**: Grant access only during business hours (e.g., 9 AM - 5 PM) or for a limited duration (expires after 2 hours).
    * **基於時間**: 僅在營業時間內（例如上午 9 點至下午 5 點）或在有限的時間內（2 小時後過期）授予存取權限。
    * **Resource-based**: Grant access only to buckets starting with `dev-`.
    * **基於資源**: 僅授予對以 `dev-` 開頭的 bucket 的存取權限。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Temporary contractor access.
    * **架構師觀點**: 臨時承包商存取。
    * A contractor needs to fix a bug over the weekend.
    * 承包商需要在週末修復一個錯誤。
    * You grant them the `Editor` role with an IAM Condition: `request.time < timestamp("2023-12-31T00:00:00Z")`.
    * 您授予他們 `Editor` 角色，並帶有 IAM 條件：`request.time < timestamp("2023-12-31T00:00:00Z")`。
    * After that timestamp, the role is effectively revoked automatically.
    * 在該時間戳記之後，該角色實際上會被自動撤銷。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **CEL**: Conditions are written in Common Expression Language (CEL).
    * **CEL**: 條件是使用通用表達式語言 (CEL) 編寫的。
    * **Not supported everywhere**: Not all Google Cloud services support IAM conditions yet, though coverage is wide for core services.
    * **並非隨處支援**: 雖然核心服務的涵蓋範圍很廣，但並非所有 Google Cloud 服務都支援 IAM 條件。

---

## Operations

### Operations Suite
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Operational Excellence pillar)**. GCP 的全方位監控與維運平台（前身為 Stackdriver）。
* **產品重要說明 (Product Description)**:
    * Google Cloud Operations Suite (formerly Stackdriver) is a suite of integrated tools for monitoring, logging, and troubleshooting.
    * Google Cloud Operations Suite (前身為 Stackdriver) 是一套用於監控、記錄和疑難排解的整合工具。
    * It monitors infrastructure, applications, and services on GCP, AWS, and on-premises.
    * 它監控 GCP, AWS 和地端的基礎設施、應用程式和服務。
* **主要功能 (Main Functions)**:
    * **Integration**: Combines metrics, logs, traces, and profiling in one place.
    * **整合**: 將指標、日誌、追蹤和效能分析結合在一個地方。
    * **Multi-cloud**: Supports AWS (via agent) and hybrid environments.
    * **多雲**: 支援 AWS (透過代理程式) 和混合環境。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Incident Response.
    * **架構師觀點**: 事件回應。
    * When an alert fires (Monitoring), an engineer clicks the link to see the graph. From the graph, they jump directly to the logs (Logging) for that specific timeframe and resource.
    * 當警報觸發時 (Monitoring)，工程師點擊連結查看圖表。從圖表中，他們可以直接跳轉到該特定時間範圍和資源的日誌 (Logging)。
    * They see a latency spike and click to view the trace (Trace) to find the slow database query.
    * 他們看到延遲激增，點擊查看追蹤 (Trace) 以找到緩慢的資料庫查詢。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Agents**: For full visibility into VMs (RAM usage, disk space, app logs), you must install the Ops Agent.
    * **代理程式**: 為了獲得對 VM 的完全可視性（RAM 使用量、磁碟空間、應用程式日誌），您必須安裝 Ops Agent。

---

### Cloud Logging
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Operational Excellence & Security)**. 集中式日誌管理系統。
* **產品重要說明 (Product Description)**:
    * Cloud Logging allows you to store, search, analyze, and alert on log data and events from Google Cloud and Amazon Web Services.
    * Cloud Logging 允許您儲存、搜尋、分析來自 Google Cloud 和 Amazon Web Services 的日誌資料和事件，並對其發出警報。
    * It includes a fully managed backend and a Logs Explorer UI.
    * 它包含一個完全託管的後端和一個日誌探索器 (Logs Explorer) UI。
* **主要功能 (Main Functions)**:
    * **Ingestion**: Automatically captures Admin Activity logs and Data Access logs (if enabled).
    * **擷取**: 自動擷取管理活動日誌和資料存取日誌（如果啟用）。
    * **Log Router (Sinks)**: Export logs to Cloud Storage (archive), BigQuery (analytics), or Pub/Sub (streaming to external SIEM).
    * **日誌路由器 (Sinks)**: 將日誌匯出到 Cloud Storage (封存)、BigQuery (分析) 或 Pub/Sub (串流到外部 SIEM)。
    * **Exclusion**: Filter out noisy logs to save costs.
    * **排除**: 過濾掉嘈雜的日誌以節省成本。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Compliance Archiving.
    * **架構師觀點**: 合規封存。
    * Regulations require keeping all audit logs for 5 years. Cloud Logging retention is shorter (usually 30 days for data access).
    * 法規要求保留所有稽核日誌 5 年。Cloud Logging 的保留期較短（資料存取通常為 30 天）。
    * You set up a **Log Sink** with a filter `logName:"cloudaudit"` to export logs to a Cloud Storage bucket with a Bucket Lock retention policy.
    * 您設定一個帶有過濾器 `logName:"cloudaudit"` 的 **Log Sink**，將日誌匯出到具有 Bucket Lock 保留政策的 Cloud Storage bucket。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Log-based Metrics**: You can create custom metrics from logs (e.g., count occurrences of "Error 500") to alert on them in Cloud Monitoring.
    * **基於日誌的指標**: 您可以從日誌建立自定義指標（例如，計算「錯誤 500」的發生次數），以便在 Cloud Monitoring 中對其發出警報。

---

### Cloud Monitoring
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Reliability)**. 基礎設施與應用程式效能監控。
* **產品重要說明 (Product Description)**:
    * Cloud Monitoring collects metrics, events, and metadata from Google Cloud services, hosted uptime probes, application instrumentation, and a variety of common application components.
    * Cloud Monitoring 從 Google Cloud 服務、託管的正常運行時間探測、應用程式儀表化和各種常見應用程式元件收集指標、事件和 Metadata。
* **主要功能 (Main Functions)**:
    * **Dashboards**: Visualizes metrics (CPU, Memory, Latency).
    * **儀表板**: 視覺化指標（CPU、記憶體、延遲）。
    * **Alerting**: Sends notifications (Email, SMS, Slack, PagerDuty) when thresholds are breached.
    * **警報**: 當超過閾值時發送通知（電子郵件、簡訊、Slack, PagerDuty）。
    * **Uptime Checks**: Tests availability of public services from around the world.
    * **正常運行時間檢查**: 從世界各地測試公共服務的可用性。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Scaling a web app.
    * **架構師觀點**: 擴展 Web 應用程式。
    * You want to scale your Instance Group based on the number of active connections, but that's not a standard metric.
    * 您希望根據活動連線數來擴展您的執行個體群組，但這不是標準指標。
    * You install the Ops Agent to collect `tcp_connections` and create a custom metric. Then you configure the Autoscaler to use this custom metric from Cloud Monitoring.
    * 您安裝 Ops Agent 來收集 `tcp_connections` 並建立自定義指標。然後，您配置自動擴展器使用來自 Cloud Monitoring 的這個自定義指標。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **MQL**: Monitoring Query Language allows for complex queries and ratios (e.g., error rate = errors / total requests) that simple UI builders cannot handle.
    * **MQL**: 監控查詢語言 (Monitoring Query Language) 允許進行簡單 UI 建置器無法處理的複雜查詢和比率計算（例如，錯誤率 = 錯誤 / 總請求）。

---

### Error Reporting
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Operational Excellence)**. 應用程式崩潰與異常的聚合視圖。
* **產品重要說明 (Product Description)**:
    * Error Reporting counts, analyzes, and aggregates the crashes in your running cloud services.
    * Error Reporting 計算、分析並聚合您正在運行的雲端服務中的崩潰。
    * It deduplicates errors so you see "1 error happening 1000 times" instead of 1000 separate log lines.
    * 它對錯誤進行去重複，因此您會看到「1 個錯誤發生了 1000 次」，而不是 1000 個單獨的日誌行。
* **主要功能 (Main Functions)**:
    * **Aggregation**: Groups similar stack traces together.
    * **聚合**: 將相似的堆疊追蹤分組在一起。
    * **Notification**: Emails you instantly when a *new* type of error is seen.
    * **通知**: 當看到*新*類型的錯誤時立即透過電子郵件通知您。
    * **Language Support**: Java, Python, Node.js, Ruby, Go, PHP, .NET.
    * **語言支援**: Java, Python, Node.js, Ruby, Go, PHP, .NET。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Post-deployment monitoring.
    * **架構師觀點**: 部署後監控。
    * You just deployed a new version of your code. You keep the Error Reporting dashboard open.
    * 您剛剛部署了新版本的程式碼。您保持 Error Reporting 儀表板開啟。
    * Suddenly, a new error group appears: `NullPointerException` in `PaymentService`. You immediately know the new code caused a regression and can roll back before users complain.
    * 突然，出現一個新的錯誤群組：`PaymentService` 中的 `NullPointerException`。您立即知道新程式碼導致了回歸，並可以在使用者投訴之前進行復原。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Source**: It parses existing logs for stack traces *or* you can use the API to report errors explicitly.
    * **來源**: 它解析現有日誌以尋找堆疊追蹤，*或者*您可以使用 API 明確報告錯誤。

---

### Cloud Trace
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Performance Efficiency)**. 分散式追蹤系統，用於尋找延遲瓶頸。
* **產品重要說明 (Product Description)**:
    * Cloud Trace is a distributed tracing system that collects latency data from your applications and displays it in the Google Cloud Console.
    * Cloud Trace 是一個分散式追蹤系統，從您的應用程式收集延遲資料並將其顯示在 Google Cloud Console 中。
    * It helps you understand how long a request takes to propagate across your microservices.
    * 它協助您了解請求在您的微服務中傳播需要多長時間。
* **主要功能 (Main Functions)**:
    * **Waterfall View**: Visualizes the call stack and time spent in each service (spans).
    * **瀑布視圖**: 視覺化呼叫堆疊和在每個服務中花費的時間 (Spans)。
    * **Latency Reports**: Shows latency shift over time (e.g., "Latency increased by 50% after yesterday's release").
    * **延遲報告**: 顯示隨時間變化的延遲偏移（例如，「昨天的發布後延遲增加了 50%」）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Debugging slow requests.
    * **架構師觀點**: 偵錯緩慢的請求。
    * Users complain that the "Checkout" page is slow.
    * 使用者投訴「結帳」頁面很慢。
    * You look at a Trace for a checkout request. You see a waterfall: Frontend (10ms) -> Inventory Service (50ms) -> Shipping Service (2000ms).
    * 您查看結帳請求的 Trace。您看到一個瀑布圖：前端 (10ms) -> 庫存服務 (50ms) -> 運送服務 (2000ms)。
    * You instantly identify the "Shipping Service" as the bottleneck, specifically an API call to an external courier that is timing out.
    * 您立即識別出「運送服務」是瓶頸，特別是呼叫外部快遞公司的 API 逾時了。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Sampling**: Tracing every request is expensive. Usually, you sample a small percentage (e.g., 0.1%) which is statistically sufficient to find bottlenecks.
    * **取樣**: 追蹤每個請求都很昂貴。通常，您會取樣一小部分（例如 0.1%），這在統計上足以發現瓶頸。

---

### Cloud Profiler
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Performance & Cost)**. 低開銷的持續性程式碼效能分析。
* **產品重要說明 (Product Description)**:
    * Cloud Profiler changes how you consume resources by continuously analyzing the performance of your CPU and heap usage in production.
    * Cloud Profiler 透過持續分析正式環境中 CPU 和堆積使用量的效能，改變您消耗資源的方式。
    * It helps you identify code that consumes the most resources.
    * 它協助您識別消耗最多資源的程式碼。
* **主要功能 (Main Functions)**:
    * **Low Overhead**: Runs with very low impact (< 5% CPU overhead) suitable for production.
    * **低開銷**: 以極低的影響運行 (< 5% CPU 開銷)，適用於正式環境。
    * **Flame Graphs**: Visualizes resource consumption (width of bar = resource usage).
    * **火焰圖**: 視覺化資源消耗（條形的寬度 = 資源使用量）。
    * **History**: Compare performance between versions (e.g., "Version 2 uses 20% more RAM than Version 1").
    * **歷史記錄**: 比較版本之間的效能（例如，「版本 2 比版本 1 多使用 20% 的 RAM」）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Cost Optimization.
    * **架構師觀點**: 成本優化。
    * Your GKE cluster bill is high.
    * 您的 GKE 叢集帳單很高。
    * You use Cloud Profiler and see a flame graph showing that 40% of CPU time in your Java app is spent in a specific XML parsing library.
    * 您使用 Cloud Profiler 並看到火焰圖顯示，您的 Java 應用程式中 40% 的 CPU 時間花在特定的 XML 解析函式庫上。
    * You replace that library with a more efficient JSON parser, reducing CPU usage by 30%, allowing you to downsize your cluster nodes.
    * 您將該函式庫替換為更高效的 JSON 解析器，將 CPU 使用量減少 30%，從而允許您縮小叢集節點的規模。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Continuous**: Unlike traditional profilers used locally for minutes, this runs all the time (via statistical sampling) to catch issues that only happen after days of running.
    * **持續性**: 與本地使用數分鐘的傳統分析工具不同，它一直運行（透過統計取樣）以捕捉僅在運行數天後發生的問題。

---

### Cloud Debugger
* **Knowledge Level**: 1: basics
* **附註**: Google 已宣佈 **Cloud Debugger 停止服務 (Deprecated)**，並建議改用 **Source Breakpoints** (在 Cloud Workstations 或 IDE 中)。但為了考試準備，仍需了解其概念。
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Operational Excellence)**. 正式環境下的即時偵錯工具。
* **產品重要說明 (Product Description)**:
    * Cloud Debugger allows you to inspect the state of a running application in real-time without stopping it or slowing it down.
    * Cloud Debugger 允許您即時檢查正在運行的應用程式狀態，而無需停止或減慢它的速度。
    * *Note: As of 2023, this service is deprecated and replaced by Snapshot Debugger in other tools.*
    * *註：截至 2023 年，此服務已棄用，並由其他工具中的快照偵錯工具取代。*
* **主要功能 (Main Functions)**:
    * **Snapshots**: Capture local variables and call stack at a specific line of code when it is executed.
    * **快照**: 當執行到特定程式碼行時，擷取區域變數和呼叫堆疊。
    * **Non-blocking**: Does not pause the thread (unlike a traditional breakpoint).
    * **非阻塞**: 不會暫停執行緒（與傳統中斷點不同）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: "It works on my machine but fails in prod."
    * **架構師觀點**: 「在我的機器上可以運作，但在正式環境中失敗。」
    * You cannot reproduce a bug locally. You place a "Snapshot" on the line where the logic seems weird.
    * 您無法在本地重現錯誤。您在邏輯看起來很奇怪的那一行放置一個「快照」。
    * When a user triggers that code path, you get a dump of the variables. You see that variable `user_id` is unexpected `null`, helping you fix the bug without downtime.
    * 當使用者觸發該程式碼路徑時，您會獲得變數的傾印。您看到變數 `user_id` 意外地為 `null`，這有助於您在不停機的情況下修復錯誤。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Source Code Link**: Requires linking your source repository (GitHub, Cloud Source Repos) to the debugger so it knows which lines correspond to the running binary.
    * **原始碼連結**: 需要將您的原始碼存放庫 (GitHub, Cloud Source Repos) 連結到偵錯工具，以便它知道哪些行對應於正在運行的二進位檔案。

---

### Cloud Audit Logs
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security & Compliance)**. 雲端操作的數位足跡。
* **產品重要說明 (Product Description)**:
    * Cloud Audit Logs maintain audit trails for your Google Cloud projects.
    * Cloud Audit Logs 為您的 Google Cloud 專案維護稽核追蹤。
    * It answers "Who did what, where, and when?".
    * 它回答了「誰在何時、何地做了什麼？」。
* **主要功能 (Main Functions)**:
    * **Admin Activity**: Records administrative actions (e.g., "Create VM", "Delete Bucket"). Enabled by default and free.
    * **管理活動**: 記錄管理動作（例如，「建立 VM」、「刪除 Bucket」）。預設啟用且免費。
    * **Data Access**: Records reads/writes to user data (e.g., "Read file from bucket"). Disabled by default (except for BigQuery) because it generates huge volume.
    * **資料存取**: 記錄對使用者資料的讀取/寫入（例如，「從 bucket 讀取檔案」）。預設停用（BigQuery 除外），因為它會產生大量資料。
    * **System Event**: Records automated system actions (e.g., Live Migration).
    * **系統事件**: 記錄自動化系統動作（例如，即時遷移）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Forensics.
    * **架構師觀點**: 鑑識。
    * A VM was mysteriously deleted.
    * 一個 VM 神秘地被刪除了。
    * You go to Logs Explorer and filter for `protoPayload.methodName="v1.compute.instances.delete"`.
    * 您前往 Logs Explorer 並過濾 `protoPayload.methodName="v1.compute.instances.delete"`。
    * You see the email of the principal who performed the action.
    * 您會看到執行該動作的主體電子郵件。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Immutability**: Audit logs are immutable (cannot be changed), ensuring integrity for compliance.
    * **不可變性**: 稽核日誌是不可變的（無法更改），確保合規性的完整性。
    * **Exemptions**: You can configure exemptions to stop collecting specific audit logs to save money, but this creates security blind spots.
    * **豁免**: 您可以配置豁免以停止收集特定稽核日誌來省錢，但這會產生安全盲點。

---

### Centralized telemetry
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Operational Excellence)**. 跨專案與混合雲的統一監控策略。
* **產品重要說明 (Product Description)**:
    * Centralized telemetry refers to the architectural pattern of collecting logs and metrics from multiple projects (and even clouds) into a single "Operations" project.
    * 集中式遙測是指將來自多個專案（甚至雲端）的日誌和指標收集到單一「維運」專案中的架構模式。
* **主要功能 (Main Functions)**:
    * **Log Sinks**: Use Aggregated Sinks (Organization level) to route logs from all projects to a central BigQuery dataset or Storage bucket.
    * **日誌 Sinks**: 使用聚合 Sinks（機構層級）將來自所有專案的日誌路由到中央 BigQuery 資料集或 Storage bucket。
    * **Monitoring Scoping**: Configure a "Scoping Project" in Cloud Monitoring that views metrics from up to 375 other projects.
    * **監控範圍**: 在 Cloud Monitoring 中配置「範圍專案」，以查看來自多達 375 個其他專案的指標。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Managed Service Provider (MSP) or Central IT.
    * **架構師觀點**: 託管服務供應商 (MSP) 或中央 IT。
    * Your central SRE team needs to monitor 50 different application projects.
    * 您的中央 SRE 團隊需要監控 50 個不同的應用程式專案。
    * Instead of opening 50 different tabs, you set up a single Monitoring Workspace that aggregates metrics from all 50 projects. You create one dashboard that shows the health of the entire organization.
    * 您無需開啟 50 個不同的分頁，而是設定一個單一的監控工作區，聚合來自所有 50 個專案的指標。您建立一個儀表板來顯示整個機構的健康狀況。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Granularity**: Be careful with cost. Centralizing *everything* (especially Data Access logs) can lead to massive BigQuery or Storage bills. Filter wisely.
    * **粒度**: 注意成本。集中*所有內容*（尤其是資料存取日誌）可能會導致巨額的 BigQuery 或 Storage 帳單。明智地過濾。

---
## Hybrid and mutli-cloud

### Anthos
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Modernization & Hybrid)**. 統一混合雲與多雲管理的旗艦平台。
* **產品重要說明 (Product Description)**:
    * Anthos is a modern application management platform that provides a consistent development and operations experience for cloud and on-premises environments.
    * Anthos 是一個現代化的應用程式管理平台，為雲端和地端環境提供一致的開發和維運體驗。
    * It allows you to run Kubernetes clusters anywhere (GCP, AWS, Azure, On-prem) and manage them from a single pane of glass (GCP Console).
    * 它允許您在任何地方（GCP, AWS, Azure, 地端）運行 Kubernetes 叢集，並從單一介面（GCP 控制台）管理它們。
* **主要功能 (Main Functions)**:
    * **Unified Management**: View and manage GKE clusters across all environments.
    * **統一管理**: 檢視和管理所有環境中的 GKE 叢集。
    * **Policy Management**: Enforce consistent security policies across all clusters using Config Management.
    * **政策管理**: 使用 Config Management 在所有叢集上強制執行一致的安全政策。
    * **Service Mesh**: Manage traffic and security between services regardless of where they run.
    * **服務網格**: 管理服務之間的流量和安全性，無論它們在哪裡運行。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Regulated Banking.
    * **架構師觀點**: 受監管的銀行業務。
    * You must keep sensitive customer data on-prem due to regulations, but you want to use modern CI/CD and Kubernetes.
    * 由於法規，您必須將敏感的客戶資料保留在地端，但您希望使用現代化的 CI/CD 和 Kubernetes。
    * You deploy Anthos on bare metal in your data center. You manage it from the Google Cloud Console just like a standard GKE cluster. Developers push code to the cloud, and Anthos deploys it to your data center.
    * 您在資料中心的裸機上部署 Anthos。您像管理標準 GKE 叢集一樣從 Google Cloud Console 管理它。開發人員將程式碼推送到雲端，Anthos 將其部署到您的資料中心。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Components**: It's not one product but a suite: GKE (on-prem/cloud), Anthos Config Management, Anthos Service Mesh, and Migrate for Anthos.
    * **組件**: 它不是單一產品而是一套套件：GKE (地端/雲端)、Anthos Config Management, Anthos Service Mesh 和 Migrate for Anthos。

---

### Anthos GKE
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Hybrid)**. Anthos 的執行引擎，讓 GKE 跑在任何地方。
* **產品重要說明 (Product Description)**:
    * Anthos GKE (or GKE on-prem / GKE on AWS/Azure) is the Kubernetes runtime component of Anthos.
    * Anthos GKE (或 GKE on-prem / GKE on AWS/Azure) 是 Anthos 的 Kubernetes 執行環境組件。
    * It brings the GKE experience to your own hardware or other clouds.
    * 它將 GKE 體驗帶到您自己的硬體或其他雲端。
* **主要功能 (Main Functions)**:
    * **GKE on VMware**: Runs GKE clusters on top of vSphere.
    * **GKE on VMware**: 在 vSphere 之上運行 GKE 叢集。
    * **GKE on Bare Metal**: Runs directly on Linux servers without a hypervisor.
    * **GKE on Bare Metal**: 直接在 Linux 伺服器上運行，無需 Hypervisor。
    * **Multi-Cloud**: Runs GKE on AWS EC2 or Azure VMs.
    * **多雲**: 在 AWS EC2 或 Azure VM 上運行 GKE。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Low latency edge computing.
    * **架構師觀點**: 低延遲邊緣運算。
    * You operate a factory and need to run ML models on camera feeds with < 5ms latency. Cloud is too far.
    * 您經營一家工廠，需要在攝影機饋送上運行 ML 模型，延遲需小於 5 毫秒。雲端太遠了。
    * You install **GKE on Bare Metal** on a server rack inside the factory. You deploy the ML containers from the cloud console. The processing happens locally (Edge), but management is centralized.
    * 您在工廠內部的伺服器機架上安裝 **GKE on Bare Metal**。您從雲端控制台部署 ML 容器。處理在本地發生（邊緣），但管理是集中的。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Connect Agent**: A small agent runs in the remote cluster to establish a secure link back to Google Cloud for management.
    * **Connect Agent**: 在遠端叢集中運行的小型代理程式，用於建立回傳 Google Cloud 進行管理的安全連結。

---

### Anthos Config Management
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Governance)**. 實現 GitOps 策略的核心工具。
* **產品重要說明 (Product Description)**:
    * Anthos Config Management (ACM) allows you to define policies and configuration (YAML) in a Git repository and automatically apply them to all your Kubernetes clusters.
    * Anthos Config Management (ACM) 允許您在 Git 存放庫中定義政策和配置 (YAML)，並自動將其套用到您的所有 Kubernetes 叢集。
    * It enables "Configuration as Code".
    * 它實現了「配置即程式碼」。
* **主要功能 (Main Functions)**:
    * **Config Sync**: Continuously syncs the state of the cluster with the Git repo.
    * **Config Sync**: 持續將叢集狀態與 Git 存放庫同步。
    * **Policy Controller**: Enforces rules (e.g., "No external load balancers") using OPA (Open Policy Agent) Gatekeeper.
    * **Policy Controller**: 使用 OPA (Open Policy Agent) Gatekeeper 強制執行規則（例如，「沒有外部負載平衡器」）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Managing 50 clusters.
    * **架構師觀點**: 管理 50 個叢集。
    * You have 50 GKE clusters across Dev, Test, and Prod. You need to ensure a specific security namespace exists in all of them.
    * 您在開發、測試和正式環境中擁有 50 個 GKE 叢集。您需要確保所有叢集中都存在一個特定的安全命名空間。
    * Instead of running `kubectl apply` 50 times, you commit the namespace YAML to the central Git repo. ACM picks it up and applies it to all 50 clusters within seconds.
    * 您無需執行 `kubectl apply` 50 次，而是將命名空間 YAML 提交到中央 Git 存放庫。ACM 會擷取它並在幾秒鐘內將其套用到所有 50 個叢集。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Drift Prevention**: If someone manually changes a setting in the cluster (drift), ACM detects it and reverts it back to what is defined in Git.
    * **偏移預防**: 如果有人手動更改了叢集中的設定（偏移），ACM 會檢測到並將其還原為 Git 中定義的內容。

---

### Anthos Service Mesh
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security & Observability)**. 基於 Istio 的託管服務網格。
* **產品重要說明 (Product Description)**:
    * Anthos Service Mesh (ASM) is a fully managed service mesh based on Istio.
    * Anthos Service Mesh (ASM) 是一個基於 Istio 的完全託管服務網格。
    * It manages secure communication between services (mTLS), traffic shifting (Canary), and observability (tracing).
    * 它管理服務之間的安全通訊 (mTLS)、流量切換 (Canary) 和可觀測性 (Tracing)。
* **主要功能 (Main Functions)**:
    * **mTLS**: Automatically encrypts traffic between microservices without code changes.
    * **mTLS**: 自動加密微服務之間的流量，無需更改程式碼。
    * **Traffic Splitting**: Send 90% of traffic to v1 and 10% to v2 for safe rollouts.
    * **流量分割**: 將 90% 的流量發送到 v1，10% 發送到 v2，以進行安全發布。
    * **Service Dashboard**: Golden signals (latency, traffic, errors) for every service.
    * **服務儀表板**: 每個服務的黃金訊號（延遲、流量、錯誤）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Zero Trust Networking in K8s.
    * **架構師觀點**: K8s 中的零信任網路。
    * Your security team requires all service-to-service traffic to be encrypted.
    * 您的安全團隊要求所有服務對服務的流量都必須加密。
    * Implementing SSL in every Java/Node/Go app is painful. You install ASM. It injects a sidecar proxy (Envoy) that handles the encryption transparently.
    * 在每個 Java/Node/Go 應用程式中實作 SSL 很痛苦。您安裝 ASM。它會注入一個 Sidecar 代理 (Envoy)，透明地處理加密。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Managed Control Plane**: Google manages the Istio control plane (in the Managed version), saving you from complex upgrades and maintenance.
    * **託管控制平面**: Google 管理 Istio 控制平面（在託管版本中），讓您免於複雜的升級和維護。

---

### Google Cloud Platform Marketplace
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Operational Excellence)**. 快速部署經認證的第三方解決方案。
* **產品重要說明 (Product Description)**:
    * GCP Marketplace allows you to deploy functional software packages (like WordPress, Elasticsearch, Jenkins) that run on Google Cloud.
    * GCP Marketplace 允許您部署在 Google Cloud 上運行的功能性軟體套件（如 WordPress, Elasticsearch, Jenkins）。
    * Solutions are vetted by Google (for security vulnerabilities) and partners.
    * 解決方案由 Google（針對安全漏洞）和合作夥伴審核。
* **主要功能 (Main Functions)**:
    * **One-Click Deploy**: Deploys complex multi-VM or Kubernetes setups with a single click via Deployment Manager or Helm.
    * **一鍵部署**: 透過 Deployment Manager 或 Helm 一鍵部署複雜的多 VM 或 Kubernetes 設定。
    * **Integrated Billing**: Third-party license costs appear on your single GCP invoice.
    * **整合帳單**: 第三方授權費用會出現在您的單一 GCP 發票上。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Rapid Prototyping.
    * **架構師觀點**: 快速原型設計。
    * You need a LAMP stack to test a PHP app.
    * 您需要一個 LAMP 堆疊來測試 PHP 應用程式。
    * Instead of creating a VM and running `apt-get install apache2 mysql...`, you go to Marketplace, search "LAMP", and click "Launch". In 2 minutes, you have a working VM with everything installed and passwords generated.
    * 您無需建立 VM 並執行 `apt-get install apache2 mysql...`，而是前往 Marketplace，搜尋 "LAMP"，然後點擊「啟動」。2 分鐘內，您就擁有一個安裝了所有內容並產生了密碼的運作中 VM。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Private Marketplace**: Enterprises can curate a "Private Marketplace" containing only approved images, preventing users from deploying unapproved software.
    * **私人 Marketplace**: 企業可以策劃一個僅包含已核准映像檔的「私人 Marketplace」，防止使用者部署未經核准的軟體。

---

### Migrate for Anthos
* **Knowledge Level**: 1: basics
* **附註**: 此項目已在 Migration 類別中詳細說明。
* **產品重要說明 (Product Description)**:
    * (Duplicate) Tool to containerize VMs into GKE workloads.
    * (重複) 將 VM 容器化為 GKE 工作負載的工具。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Recap**: Ideal for "modernizing in place" or moving legacy Linux apps to Kubernetes without rewriting code.
    * **回顧**: 非常適合「就地現代化」或在不重寫程式碼的情況下將舊版 Linux 應用程式移動到 Kubernetes。

---
## API Management

### Apigee
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security & Operational Excellence)**. 企業級全生命週期 API 管理平台。
* **產品重要說明 (Product Description)**:
    * Apigee is a full-lifecycle API management platform that enables businesses to secure, deploy, monitor, and scale APIs.
    * Apigee 是一個全生命週期的 API 管理平台，使企業能夠保護、部署、監控和擴展 API。
    * It sits in front of your backend services (legacy or modern) and provides a unified interface to consumers.
    * 它位於您的後端服務（舊版或現代化）之前，並為消費者提供統一的介面。
* **主要功能 (Main Functions)**:
    * **Security**: OAuth 2.0, API key validation, threat protection (XML/JSON attacks).
    * **安全性**: OAuth 2.0, API 金鑰驗證, 威脅防護 (XML/JSON 攻擊)。
    * **Traffic Management**: Quotas, spike arrest (smoothing traffic spikes), caching.
    * **流量管理**: 配額, 峰值攔截 (平滑流量峰值), 快取。
    * **Analytics**: Deep insights into API usage, latency, and errors.
    * **分析**: 深入了解 API 使用情況、延遲和錯誤。
    * **Monetization**: Charge developers for using your APIs.
    * **貨幣化**: 向開發人員收取使用您 API 的費用。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Exposing legacy SOAP services as REST.
    * **架構師觀點**: 將舊版 SOAP 服務揭露為 REST。
    * A bank has a legacy mainframe backend that speaks XML/SOAP. They want to launch a mobile app that speaks JSON/REST.
    * 一家銀行擁有一個使用 XML/SOAP 的舊版大型主機後端。他們希望推出一個使用 JSON/REST 的行動應用程式。
    * Instead of rewriting the mainframe, you use Apigee to create an API proxy. Apigee accepts JSON from the app, transforms it to XML for the backend, and transforms the response back.
    * 您無需重寫大型主機，而是使用 Apigee 建立 API 代理。Apigee 接收來自應用程式的 JSON，將其轉換為後端的 XML，並將回應轉換回來。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Apigee X vs Edge**: Apigee X is the newer version integrated deeply with GCP networking (Cloud Armor, VPC). Apigee Edge is the older platform.
    * **Apigee X vs Edge**: Apigee X 是與 GCP 網路（Cloud Armor, VPC）深度整合的較新版本。Apigee Edge 是較舊的平台。
    * **Hub architecture**: Typically deployed in a centralized "API Project" that fronts services in other projects.
    * **Hub 架構**: 通常部署在集中式的「API 專案」中，該專案位於其他專案中的服務之前。

---

### Cloud Endpoints
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Performance)**. 輕量級、基於 NGINX 的 API 閘道。
* **產品重要說明 (Product Description)**:
    * Cloud Endpoints is an API management system that helps you secure, monitor, and scale your APIs.
    * Cloud Endpoints 是一個 API 管理系統，可協助您保護、監控和擴展您的 API。
    * It uses an NGINX-based proxy (Extensible Service Proxy - ESP) deployed alongside your application (sidecar).
    * 它使用部署在您的應用程式旁邊（sidecar）的基於 NGINX 的代理 (Extensible Service Proxy - ESP)。
* **主要功能 (Main Functions)**:
    * **Speed**: Since the proxy runs locally with the app (in the same GKE pod or VM), latency is minimal.
    * **速度**: 由於代理與應用程式在本地運行（在同一個 GKE Pod 或 VM 中），延遲極小。
    * **OpenAPI Spec**: You define your API using Swagger/OpenAPI specification.
    * **OpenAPI 規範**: 您使用 Swagger/OpenAPI 規範定義您的 API。
    * **GCP Integration**: Validates Google ID tokens and Firebase Auth tokens easily.
    * **GCP 整合**: 輕鬆驗證 Google ID 權杖和 Firebase Auth 權杖。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: High-performance gRPC microservices.
    * **架構師觀點**: 高效能 gRPC 微服務。
    * You are building a high-speed internal service using gRPC on GKE.
    * 您正在 GKE 上使用 gRPC 建立高速內部服務。
    * You deploy Cloud Endpoints (ESPv2) as a sidecar container. It handles authentication and logging for every call without adding a network hop to a centralized gateway.
    * 您將 Cloud Endpoints (ESPv2) 部署為 Sidecar 容器。它處理每個呼叫的身分驗證和記錄，而無需增加到集中式閘道的網路跳躍。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Distributed**: Unlike Apigee/API Gateway which are centralized, Endpoints is distributed. Updates to the API config require redeploying the ESP sidecars.
    * **分散式**: 與集中式的 Apigee/API Gateway 不同，Endpoints 是分散式的。更新 API 配置需要重新部署 ESP Sidecars。

---

### API Gateway
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Serverless)**. 專為 Serverless (Cloud Functions/Run) 設計的完全託管閘道。
* **產品重要說明 (Product Description)**:
    * API Gateway is a fully managed service that sits in front of your Cloud Functions, Cloud Run, and App Engine services.
    * API Gateway 是一個完全託管的服務，位於您的 Cloud Functions, Cloud Run 和 App Engine 服務之前。
    * It is similar to Cloud Endpoints but fully managed (no sidecars to deploy).
    * 它類似於 Cloud Endpoints，但完全託管（無需部署 Sidecar）。
* **主要功能 (Main Functions)**:
    * **Serverless**: Scales to zero and handles spikes automatically.
    * **無伺服器**: 擴展到零並自動處理峰值。
    * **Security**: API Keys, JWT validation (Firebase, Auth0, Google ID).
    * **安全性**: API 金鑰、JWT 驗證 (Firebase, Auth0, Google ID)。
    * **Rate Limiting**: Simple quota management.
    * **速率限制**: 簡單的配額管理。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Serverless Backend Facade.
    * **架構師觀點**: 無伺服器後端門面。
    * You have 5 different Cloud Functions acting as microservices. You want to expose them as a single cohesive API (`/api/v1/users`, `/api/v1/orders`).
    * 您有 5 個不同的 Cloud Functions 充當微服務。您希望將它們作為一個單一的凝聚 API 揭露 (`/api/v1/users`, `/api/v1/orders`)。
    * You create an API Gateway config that routes specific paths to specific functions. The client only knows the Gateway URL.
    * 您建立一個 API Gateway 配置，將特定路徑路由到特定函式。客戶端只知道 Gateway URL。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Under the hood**: It is built on top of the same Envoy-based infrastructure as Cloud Run, making it highly scalable.
    * **底層機制**: 它建立在與 Cloud Run 相同的基於 Envoy 的基礎設施之上，使其具有高度可擴展性。
    * **Limitations**: Not as feature-rich as Apigee (no monetization, complex transformation, or XML support).
    * **限制**: 功能不如 Apigee 豐富（沒有貨幣化、複雜轉換或 XML 支援）。

---

## Data Analytics

### BigQuery
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Performance & Cost Optimization)**. GCP 的無伺服器企業級資料倉儲。
* **產品重要說明 (Product Description)**:
    * BigQuery is a serverless, highly scalable, and cost-effective multi-cloud data warehouse designed for business agility.
    * BigQuery 是一個無伺服器、高度可擴展且具成本效益的多雲資料倉儲，專為業務敏捷性而設計。
    * It allows you to analyze petabytes of data using ANSI SQL at blazing-fast speeds.
    * 它允許您以極快的速度使用 ANSI SQL 分析 PB 級的資料。
* **主要功能 (Main Functions)**:
    * **Serverless**: No infrastructure to manage. Compute separates from storage.
    * **無伺服器**: 無需管理基礎設施。運算與儲存分離。
    * **In-memory BI Engine**: Extremely fast analysis for dashboards (like Looker Studio).
    * **記憶體內 BI 引擎**: 為儀表板（如 Looker Studio）提供極快的分析。
    * **BigQuery ML**: Build and run machine learning models directly in SQL.
    * **BigQuery ML**: 直接在 SQL 中建立和運行機器學習模型。
    * **Federated Queries**: Query data residing in GCS, Cloud SQL, or Spanner without moving it.
    * **聯邦查詢**: 查詢駐留在 GCS, Cloud SQL 或 Spanner 中的資料，而無需移動它。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Replacing an on-prem Teradata/Oracle warehouse.
    * **架構師觀點**: 取代地端 Teradata/Oracle 資料倉儲。
    * You migrate 500TB of historical sales data to BigQuery. Analysts who know SQL can immediately start running queries without learning a new tool.
    * 您將 500TB 的歷史銷售資料遷移到 BigQuery。懂 SQL 的分析師可以立即開始執行查詢，而無需學習新工具。
    * You set up **Partitioning** (by date) and **Clustering** (by customer ID) to ensure queries are cheap and fast.
    * 您設定**分區 (Partitioning)**（按日期）和**叢集 (Clustering)**（按客戶 ID），以確保查詢既便宜又快速。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Slots**: BigQuery uses "slots" (virtual CPUs) for processing. You can pay on-demand (per TB scanned) or buy flat-rate slots (predictable monthly cost).
    * **Slots**: BigQuery 使用 "slots"（虛擬 CPU）進行處理。您可以按需付費（按掃描的 TB）或購買固定費率 slots（可預測的月費）。
    * **Caching**: Query results are cached for 24 hours. Repeating the *exact* same query is free.
    * **快取**: 查詢結果會快取 24 小時。重複*完全*相同的查詢是免費的。

---

### Cloud Composer
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Operational Excellence)**. 基於 Apache Airflow 的工作流程編排服務。
* **產品重要說明 (Product Description)**:
    * Cloud Composer is a fully managed workflow orchestration service built on Apache Airflow.
    * Cloud Composer 是一個建立在 Apache Airflow 之上的完全託管工作流程編排服務。
    * It allows you to author, schedule, and monitor pipelines that span across clouds and on-premises data centers.
    * 它允許您編寫、排程和監控跨越雲端和地端資料中心的流程 (Pipelines)。
* **主要功能 (Main Functions)**:
    * **Python-based**: Workflows are defined as Directed Acyclic Graphs (DAGs) in Python.
    * **基於 Python**: 工作流程在 Python 中定義為有向無環圖 (DAG)。
    * **Integration**: Deeply integrated with BigQuery, Dataflow, Dataproc, and AI Platform.
    * **整合**: 與 BigQuery, Dataflow, Dataproc 和 AI Platform 深度整合。
    * **Hybrid**: Can trigger jobs on-prem via connectors.
    * **混合**: 可以透過連接器觸發地端作業。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Complex ETL dependency management.
    * **架構師觀點**: 複雜的 ETL 依賴關係管理。
    * You have a pipeline: 1. Ingest data from FTP (VM). 2. Process it in Dataflow. 3. Load into BigQuery. 4. Retrain an ML model.
    * 您有一個流程：1. 從 FTP (VM) 擷取資料。 2. 在 Dataflow 中處理它。 3. 載入到 BigQuery。 4. 重新訓練 ML 模型。
    * Cloud Composer manages this sequence. If step 2 fails, it retries or alerts. It ensures step 3 doesn't start until step 2 succeeds.
    * Cloud Composer 管理此順序。如果步驟 2 失敗，它會重試或發出警報。它確保步驟 2 成功後才開始步驟 3。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Environment**: It actually spins up a GKE cluster in your project to run the Airflow schedulers and workers.
    * **環境**: 它實際上是在您的專案中啟動一個 GKE 叢集來運行 Airflow 排程器和工作節點。
    * **Cost**: It can be expensive for very simple tasks due to the underlying GKE infrastructure. (Composer 2 optimizes this with GKE Autopilot).
    * **成本**: 由於底層 GKE 基礎設施，對於非常簡單的任務來說可能很昂貴。（Composer 2 使用 GKE Autopilot 優化了這一點）。

---

### Cloud Dataflow
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Performance & Scalability)**. 基於 Apache Beam 的統一串流與批次資料處理。
* **產品重要說明 (Product Description)**:
    * Cloud Dataflow is a fully managed service for executing Apache Beam pipelines within the Google Cloud Platform ecosystem.
    * Cloud Dataflow 是一個完全託管的服務，用於在 Google Cloud Platform 生態系統內執行 Apache Beam 流程。
    * It supports both stream (real-time) and batch processing in a single programming model.
    * 它在單一程式設計模型中同時支援串流（即時）和批次處理。
* **主要功能 (Main Functions)**:
    * **Auto-scaling**: Automatically scales the number of worker VMs based on data volume.
    * **自動擴展**: 根據資料量自動擴展工作節點 VM 的數量。
    * **Exactly-once**: Guarantees exactly-once processing for streaming data (crucial for financial data).
    * **精確一次**: 保證串流資料的精確一次處理（對金融資料至關重要）。
    * **Streaming Engine**: Offloads state storage and shuffling to a specialized service backend for lower latency.
    * **串流引擎**: 將狀態儲存和 Shuffling 卸載到專門的服務後端，以降低延遲。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Real-time fraud detection.
    * **架構師觀點**: 即時詐欺偵測。
    * Transaction events arrive via Pub/Sub. Dataflow reads the stream, joins it with user profile data from Bigtable, applies a fraud detection rule, and writes suspicious transactions to a "Fraud Alerts" Pub/Sub topic.
    * 交易事件透過 Pub/Sub 到達。Dataflow 讀取串流，將其與來自 Bigtable 的使用者設定檔資料結合，套用詐欺偵測規則，並將可疑交易寫入「詐欺警報」Pub/Sub 主題。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Windowing & Watermarks**: Key concepts for handling "late data" in streaming. Dataflow handles late-arriving events gracefully based on event time vs. processing time.
    * **視窗化與浮水印**: 處理串流中「遲到資料」的關鍵概念。Dataflow 根據事件時間與處理時間優雅地處理遲到的事件。
    * **Flex Templates**: Allows you to package your pipeline as a Docker image so non-developers can run it from the Console with custom parameters.
    * **Flex Templates**: 允許您將流程打包為 Docker 映像檔，以便非開發人員可以使用自定義參數從控制台運行它。

---

### Cloud Dataprep
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Operational Excellence)**. 視覺化資料清理與準備工具。
* **產品重要說明 (Product Description)**:
    * Cloud Dataprep by Trifacta is an intelligent data service for visually exploring, cleaning, and preparing data for analysis.
    * Cloud Dataprep by Trifacta 是一個智慧資料服務，用於視覺化地探索、清理和準備用於分析的資料。
    * It is designed for data analysts (non-coders) rather than data engineers.
    * 它是為資料分析師（非程式設計師）而非資料工程師設計的。
* **主要功能 (Main Functions)**:
    * **Visual Interface**: Click-and-drag UI to fix messy data (e.g., split columns, remove nulls).
    * **視覺化介面**: 點擊拖放 UI 來修復混亂的資料（例如，分割欄位、移除 Null 值）。
    * **Intelligent Suggestions**: Predicts the transformation you want based on your selection (Machine Learning driven).
    * **智慧建議**: 根據您的選擇預測您想要的轉換（機器學習驅動）。
    * **Execution**: Compiles the recipe into a Dataflow job to run on scale.
    * **執行**: 將配方 (Recipe) 編譯成 Dataflow 作業以進行大規模執行。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Ad-hoc analysis by business users.
    * **架構師觀點**: 業務使用者的臨時分析。
    * A marketing analyst receives a messy CSV export from a legacy CRM.
    * 行銷分析師收到一個來自舊版 CRM 的混亂 CSV 匯出檔。
    * Instead of asking IT to write a Python script, they upload it to Dataprep. They visually clean the phone number formats and fix date errors. The result is exported to BigQuery for analysis.
    * 他們無需請求 IT 編寫 Python 腳本，而是將其上傳到 Dataprep。他們視覺化地清理電話號碼格式並修復日期錯誤。結果匯出到 BigQuery 進行分析。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Underlying Engine**: It runs on Dataflow (or BigQuery in some cases), so you pay for the underlying processing resources.
    * **底層引擎**: 它在 Dataflow（或在某些情況下為 BigQuery）上運行，因此您需要支付底層處理資源的費用。

---

### Cloud Dataproc
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Modernization)**. 託管的 Hadoop/Spark 叢集服務。
* **產品重要說明 (Product Description)**:
    * Cloud Dataproc is a fully managed and highly scalable service for running Apache Spark, Apache Flink, Presto, and 30+ open source tools.
    * Cloud Dataproc 是一個完全託管且高度可擴展的服務，用於運行 Apache Spark, Apache Flink, Presto 和 30 多種開源工具。
    * It allows you to lift-and-shift existing Hadoop clusters to GCP.
    * 它允許您將現有的 Hadoop 叢集直接轉移 (lift-and-shift) 到 GCP。
* **主要功能 (Main Functions)**:
    * **Ephemeral Clusters**: Spin up a cluster in 90 seconds, process data, and shut it down (saving money).
    * **暫時性叢集**: 在 90 秒內啟動叢集，處理資料，然後將其關閉（省錢）。
    * **Integration**: Connects HDFS (Hadoop Distributed File System) directly to GCS via the GCS Connector.
    * **整合**: 透過 GCS Connector 將 HDFS (Hadoop 分散式檔案系統) 直接連線到 GCS。
    * **Autoscaling**: Automatically adds/removes nodes.
    * **自動擴展**: 自動新增/移除節點。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Migrating an on-prem Spark workload.
    * **架構師觀點**: 遷移地端 Spark 工作負載。
    * You have a nightly batch job running on a fixed-size physical Hadoop cluster that is idle 20 hours a day.
    * 您有一個每晚批次作業運行在固定大小的實體 Hadoop 叢集上，該叢集每天閒置 20 小時。
    * You migrate the job to Dataproc. You store the data in GCS (instead of HDFS). You create a workflow that spins up a Dataproc cluster at 2 AM, runs the job, and deletes the cluster at 4 AM. This reduces cost by 80%.
    * 您將作業遷移到 Dataproc。您將資料儲存在 GCS（而不是 HDFS）。您建立一個工作流程，在凌晨 2 點啟動 Dataproc 叢集，執行作業，並在凌晨 4 點刪除叢集。這將成本降低了 80%。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Preemptible VMs**: Using Preemptible VMs for secondary worker nodes is a best practice to drastically reduce costs for fault-tolerant Spark jobs.
    * **先佔式 VM**: 為次要工作節點使用先佔式 VM 是大幅降低容錯 Spark 作業成本的最佳實務。
    * **Workflow Templates**: Define a graph of jobs and the cluster configuration in YAML to automate the ephemeral lifecycle.
    * **工作流程範本**: 在 YAML 中定義作業圖和叢集配置，以自動化暫時性生命週期。

---

### Cloud Pub/Sub
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Reliability & Scalability)**. 全球性非同步訊息傳遞服務，用於解耦微服務。
* **產品重要說明 (Product Description)**:
    * Cloud Pub/Sub is an asynchronous messaging service designed to be highly reliable and scalable.
    * Cloud Pub/Sub 是一個專為高可靠性和可擴展性而設計的非同步訊息傳遞服務。
    * It decouples services that produce events from services that process events.
    * 它將產生事件的服務與處理事件的服務解耦。
* **主要功能 (Main Functions)**:
    * **Global Availability**: Topics are global resources. You can publish from anywhere and subscribe from anywhere.
    * **全球可用性**: 主題 (Topics) 是全球資源。您可以從任何地方發布並從任何地方訂閱。
    * **Push & Pull**: Supports Push (webhook style) and Pull (worker polling) delivery mechanisms.
    * **推播與拉取**: 支援推播 (Webhook 風格) 和拉取 (工作節點輪詢) 傳遞機制。
    * **Filtering**: Subscribers can filter messages based on attributes, reducing downstream processing.
    * **過濾**: 訂閱者可以根據屬性過濾訊息，減少下游處理。
    * **Dead Letter Queues**: Handles messages that cannot be processed successfully after several attempts.
    * **死信佇列 (DLQ)**: 處理在多次嘗試後無法成功處理的訊息。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Buffer for traffic spikes.
    * **架構師觀點**: 流量峰值的緩衝區。
    * During a flash sale, your order service receives 100k requests/sec, but your inventory database can only handle 10k writes/sec.
    * 在快閃拍賣期間，您的訂單服務接收 100k 請求/秒，但您的庫存資料庫只能處理 10k 寫入/秒。
    * Instead of writing directly to the DB (which would crash it), you publish orders to Pub/Sub. A backend worker pulls messages at a controlled rate (10k/sec) and updates the DB. Pub/Sub acts as a shock absorber.
    * 您不直接寫入 DB（這會導致其崩潰），而是將訂單發布到 Pub/Sub。後端工作節點以受控速率 (10k/秒) 拉取訊息並更新 DB。Pub/Sub 充當避震器。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Ordering**: By default, ordering is *not* guaranteed (for scale). You must enable "Message Ordering" and use an "Ordering Key" if strict order is required.
    * **順序**: 預設情況下，順序*不*保證（為了擴展）。如果需要嚴格順序，必須啟用「訊息排序」並使用「排序鍵」。
    * **At-least-once**: Pub/Sub guarantees at-least-once delivery. Your application must be idempotent (handle duplicate messages gracefully).
    * **至少一次**: Pub/Sub 保證至少一次傳遞。您的應用程式必須是冪等的（優雅地處理重複訊息）。

---

### Data Catalog
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security & Governance)**. 企業資料資產的搜尋與標籤管理系統。
* **產品重要說明 (Product Description)**:
    * Data Catalog is a fully managed and scalable metadata management service.
    * Data Catalog 是一個完全託管且可擴展的 Metadata 管理服務。
    * It allows you to quickly discover, manage, and understand your data in Google Cloud (BigQuery, Pub/Sub, GCS).
    * 它允許您快速探索、管理和了解 Google Cloud (BigQuery, Pub/Sub, GCS) 中的資料。
* **主要功能 (Main Functions)**:
    * **Search**: Find tables or files using keywords (e.g., "Find all tables with 'revenue' in the name").
    * **搜尋**: 使用關鍵字尋找資料表或檔案（例如，「尋找名稱中包含 'revenue' 的所有資料表」）。
    * **Tagging**: Apply technical and business metadata tags to data assets.
    * **標籤**: 將技術和業務 Metadata 標籤套用到資料資產。
    * **Cloud IAM Integration**: Searching respects IAM permissions (you only see what you have access to).
    * **Cloud IAM 整合**: 搜尋遵循 IAM 權限（您只能看到您有權存取的內容）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Data Governance.
    * **架構師觀點**: 資料治理。
    * You have 10,000 datasets across the organization. The compliance team needs to know which ones contain PII (Personally Identifiable Information).
    * 您的機構中有 10,000 個資料集。合規團隊需要知道哪些包含 PII（個人識別資訊）。
    * You use the DLP API to scan tables and automatically apply a Data Catalog Tag "PII: True" to sensitive tables. The compliance officer can then search `tag:PII=True` to get a full report.
    * 您使用 DLP API 掃描資料表，並自動將 Data Catalog 標籤 "PII: True" 套用到敏感資料表。合規官員隨後可以搜尋 `tag:PII=True` 以獲取完整報告。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Tag Templates**: You define a schema for your tags (e.g., Enum: High, Medium, Low) to ensure consistency across the organization.
    * **標籤範本**: 您為標籤定義結構描述（例如，列舉：高、中、低），以確保整個機構的一致性。

---

### Avro data format
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Performance)**. 大數據處理與儲存的高效能標準格式。
* **產品重要說明 (Product Description)**:
    * Avro is a row-oriented remote procedure call and data serialization framework developed within Apache's Hadoop project.
    * Avro 是一個在 Apache Hadoop 專案中開發的列導向 (Row-oriented) 遠端程序呼叫和資料序列化框架。
    * In GCP context, it is the preferred format for loading data into BigQuery and storing data in Cloud Storage for analytics.
    * 在 GCP 情境下，它是將資料載入 BigQuery 以及在 Cloud Storage 中儲存資料以進行分析的首選格式。
* **主要功能 (Main Functions)**:
    * **Schema Evolution**: Handles changes in data structure (adding/removing fields) gracefully.
    * **結構描述演進**: 優雅地處理資料結構的變更（新增/移除欄位）。
    * **Compression**: Highly efficient binary format, smaller than JSON or CSV.
    * **壓縮**: 高效的二進位格式，比 JSON 或 CSV 小。
    * **Splittable**: Can be processed in parallel by Hadoop/Dataflow (unlike standard GZIP JSON).
    * **可分割**: 可以由 Hadoop/Dataflow 平行處理（與標準 GZIP JSON 不同）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Optimizing BigQuery Load Jobs.
    * **架構師觀點**: 優化 BigQuery 載入作業。
    * You are exporting data from a database to GCS to load into BigQuery.
    * 您正在將資料從資料庫匯出到 GCS 以載入到 BigQuery。
    * Using JSON is slow and prone to type errors (string vs int). Using Avro preserves the schema information inside the file itself, making the load into BigQuery faster and error-free.
    * 使用 JSON 速度慢且容易出現類型錯誤（字串 vs 整數）。使用 Avro 會在檔案本身內部保留結構描述資訊，使載入 BigQuery 更快且無錯誤。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Avro vs Parquet**: Avro is row-based (better for write-heavy transaction records). Parquet is column-based (better for read-heavy analytics queries).
    * **Avro vs Parquet**: Avro 是基於列的（更適合寫入密集的交易記錄）。Parquet 是基於欄的（更適合讀取密集的分析查詢）。

---

### Hadoop ecosystem (HBase / Spark / Hive / Pig / MapReduce / HDFS)
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Migration)**. 了解傳統大數據生態系是為了將其遷移至現代化 GCP 服務。
* **產品重要說明 (Product Description)**:
    * This refers to the collection of open-source tools for big data processing.
    * 這指的是用於大數據處理的開源工具集合。
    * GCP offers managed versions of these via **Cloud Dataproc**.
    * GCP 透過 **Cloud Dataproc** 提供這些工具的託管版本。
* **主要功能 (Main Functions)**:
    * **HDFS**: Distributed file system. -> Replaced by **Cloud Storage (GCS)** in GCP architecture.
    * **HDFS**: 分散式檔案系統。 -> 在 GCP 架構中由 **Cloud Storage (GCS)** 取代。
    * **Spark**: In-memory processing. -> Run on **Dataproc** or migrated to **Dataflow**.
    * **Spark**: 記憶體內處理。 -> 在 **Dataproc** 上運行或遷移到 **Dataflow**。
    * **Hive**: SQL on Hadoop. -> Replaced by **BigQuery**.
    * **Hive**: Hadoop 上的 SQL。 -> 由 **BigQuery** 取代。
    * **HBase**: NoSQL database. -> Managed version is **Cloud Bigtable**.
    * **HBase**: NoSQL 資料庫。 -> 託管版本為 **Cloud Bigtable**。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Modernization Strategy.
    * **架構師觀點**: 現代化策略。
    * A client has a massive Hive warehouse on-prem.
    * 客戶在地端擁有龐大的 Hive 資料倉儲。
    * **Strategy 1 (Lift & Shift)**: Move to Dataproc with Hive installed, pointing to data in GCS.
    * **策略 1 (直接轉移)**: 遷移到安裝了 Hive 的 Dataproc，指向 GCS 中的資料。
    * **Strategy 2 (Modernize)**: Rewrite the HiveQL queries to BigQuery SQL and move the data to BigQuery native storage for better performance and zero maintenance.
    * **策略 2 (現代化)**: 將 HiveQL 查詢重寫為 BigQuery SQL，並將資料移動到 BigQuery 原生儲存，以獲得更好的效能和零維護。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Decoupling**: The #1 principle in GCP big data is decoupling storage (GCS) from compute (Dataproc). In traditional on-prem Hadoop, they are coupled on the same nodes.
    * **解耦**: GCP 大數據的第一原則是將儲存 (GCS) 與運算 (Dataproc) 解耦。在傳統的地端 Hadoop 中，它們耦合在相同的節點上。

---

## Developer Tools

### Application Deployment Models
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Operational Excellence)**. 部署策略直接影響服務的可靠性與發布速度。
* **產品重要說明 (Product Description)**:
    * This is a concept, not a specific product. It refers to the strategies used to release new software versions.
    * 這是一個概念，而非特定產品。它指的是用於發布新軟體版本的策略。
    * Common models include Blue/Green, Canary, and Rolling Updates.
    * 常見的模型包括藍/綠 (Blue/Green)、金絲雀 (Canary) 和滾動更新 (Rolling Updates)。
* **主要功能 (Main Functions)**:
    * **Blue/Green**: Two identical environments. Switch traffic from old (Blue) to new (Green) instantly. Fast rollback, high cost (double resources).
    * **藍/綠**: 兩個相同的環境。立即將流量從舊的 (藍) 切換到新的 (綠)。快速復原，高成本（雙倍資源）。
    * **Canary**: Roll out update to a small % of users first. Verify health, then expand. Low risk.
    * **金絲雀**: 先向一小部分使用者推出更新。驗證健康狀況，然後擴大範圍。低風險。
    * **Rolling**: Update instances one by one (or in batches). Zero downtime, lower resource cost, slower rollback.
    * **滾動**: 逐一（或分批）更新執行個體。零停機時間，較低的資源成本，復原較慢。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Choosing the right strategy for GKE.
    * **架構師觀點**: 為 GKE 選擇正確的策略。
    * For a mission-critical payment service, you choose **Canary Deployment**. You use Istio (Anthos Service Mesh) to route 1% of traffic to the new version. If error rates stay low for 1 hour, you automatically increase to 10%, then 100%.
    * 對於關鍵任務支付服務，您選擇**金絲雀部署**。您使用 Istio (Anthos Service Mesh) 將 1% 的流量路由到新版本。如果錯誤率在 1 小時內保持低位，您會自動增加到 10%，然後是 100%。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **A/B Testing vs Canary**: Canary is for risk mitigation (finding bugs). A/B testing is for business decisions (which UI converts better).
    * **A/B 測試 vs 金絲雀**: 金絲雀用於風險緩解（尋找錯誤）。A/B 測試用於業務決策（哪個 UI 轉換率更好）。

---

### Artifact Registry
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Security - Supply Chain)**. 下一代的軟體套件與容器映像檔儲存庫。
* **產品重要說明 (Product Description)**:
    * Artifact Registry is the evolution of Container Registry.
    * Artifact Registry 是 Container Registry 的演進。
    * It is a single place to manage container images and language packages (Maven, npm, Python, NuGet, etc.).
    * 它是管理容器映像檔和語言套件（Maven, npm, Python, NuGet 等）的單一位置。
* **主要功能 (Main Functions)**:
    * **Multi-format**: Supports Docker, Maven (Java), npm (Node), Python, Apt/Yum.
    * **多格式**: 支援 Docker, Maven (Java), npm (Node), Python, Apt/Yum。
    * **Regional**: Repositories are regional, offering better control over data residency and latency.
    * **區域性**: 存放庫是區域性的，提供對資料駐留和延遲的更好控制。
    * **Granular IAM**: Permissions can be set per repository (unlike GCR which is per bucket).
    * **精細 IAM**: 權限可以按存放庫設定（與 GCR 按 bucket 設定不同）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Secure Build Pipeline.
    * **架構師觀點**: 安全建置流程。
    * Your developers use private Java libraries. Instead of hosting a Jenkins server with Artifactory, you upload these jars to a private Maven repository in Artifact Registry.
    * 您的開發人員使用私人 Java 函式庫。您無需託管帶有 Artifactory 的 Jenkins 伺服器，而是將這些 Jar 上傳到 Artifact Registry 中的私人 Maven 存放庫。
    * Your Cloud Build pipeline authenticates securely to fetch these dependencies during the build process.
    * 您的 Cloud Build 流程安全地進行身分驗證，以便在建置過程中擷取這些依賴項。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Migration**: Google recommends migrating from GCR to Artifact Registry. GCR redirects can be enabled to support old URLs.
    * **遷移**: Google 建議從 GCR 遷移到 Artifact Registry。可以啟用 GCR 重新導向以支援舊 URL。

---

### Cloud SDK
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Operational Excellence)**. 命令列工具與自動化腳本的基礎。
* **產品重要說明 (Product Description)**:
    * The Cloud SDK is a set of command-line tools for managing resources and applications hosted on Google Cloud.
    * Cloud SDK 是一套命令列工具，用於管理 Google Cloud 上託管的資源和應用程式。
    * It includes `gcloud`, `gsutil`, and `bq`.
    * 它包含 `gcloud`, `gsutil` 和 `bq`。
* **主要功能 (Main Functions)**:
    * **gcloud**: The primary CLI for most services (Compute, GKE, IAM).
    * **gcloud**: 大多數服務 (Compute, GKE, IAM) 的主要 CLI。
    * **gsutil**: Python-based CLI specifically for Cloud Storage operations.
    * **gsutil**: 專門用於 Cloud Storage 操作的基於 Python 的 CLI。
    * **bq**: CLI for BigQuery.
    * **bq**: BigQuery 的 CLI。
    * **Scripting**: Allows automation via shell scripts.
    * **腳本**: 允許透過 Shell 腳本進行自動化。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Automating routine tasks.
    * **架構師觀點**: 自動化例行任務。
    * You need to create a project, enable APIs, and create a GKE cluster for every new client.
    * 您需要為每個新客戶建立一個專案、啟用 API 並建立一個 GKE 叢集。
    * You write a bash script using `gcloud projects create`, `gcloud services enable`, and `gcloud container clusters create`. This ensures consistency compared to clicking in the Console.
    * 您使用 `gcloud projects create`, `gcloud services enable` 和 `gcloud container clusters create` 編寫一個 Bash 腳本。與在控制台中點擊相比，這確保了一致性。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Configuration**: `gcloud config set project [PROJECT_ID]` helps switch contexts. `gcloud config configurations create` allows managing multiple profiles (e.g., separate auth for personal vs work).
    * **配置**: `gcloud config set project [PROJECT_ID]` 有助於切換情境。`gcloud config configurations create` 允許管理多個設定檔（例如，個人與工作的單獨驗證）。

---

### Container Registry
* **Knowledge Level**: 1: basics
* **附註**: 此項目已在 Containers 類別中詳細說明。
* **產品重要說明 (Product Description)**:
    * (Duplicate) Legacy container image storage.
    * (重複) 舊版容器映像檔儲存。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Recap**: Use Artifact Registry for new projects. GCR stores images in GCS buckets.
    * **回顧**: 新專案請使用 Artifact Registry。GCR 將映像檔儲存在 GCS bucket 中。

---

### Cloud Build
* **Knowledge Level**: 2: medium
* **附註**: 此項目已在 Containers 類別中出現，此處知識等級提升至 2: medium，表示需更深入了解。
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Operational Excellence)**. CI/CD 流程的引擎。
* **產品重要說明 (Product Description)**:
    * Cloud Build is a serverless platform for CI/CD.
    * Cloud Build 是一個用於 CI/CD 的無伺服器平台。
    * It executes builds as a series of container steps.
    * 它將建置作為一系列容器步驟執行。
* **主要功能 (Main Functions)**:
    * **Custom Builders**: You can use any Docker container as a build step. If `gcloud` or `mvn` isn't enough, build your own container with specific tools and use it in the pipeline.
    * **自定義建置器**: 您可以使用任何 Docker 容器作為建置步驟。如果 `gcloud` 或 `mvn` 不夠用，請使用特定工具建立您自己的容器，並在流程中使用它。
    * **Caching**: Can cache build artifacts (like Maven `.m2` directory) to GCS to speed up subsequent builds.
    * **快取**: 可以將建置成品（如 Maven `.m2` 目錄）快取到 GCS，以加快後續建置速度。
    * **Parallel Steps**: Steps can depend on each other (`waitFor: ['-']`) to run in parallel.
    * **平行步驟**: 步驟可以相互依賴 (`waitFor: ['-']`) 以平行運行。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Hybrid Deployment.
    * **架構師觀點**: 混合部署。
    * You need to deploy code to an on-premise GKE cluster.
    * 您需要將程式碼部署到地端 GKE 叢集。
    * You use Cloud Build with **Private Pools**. The build workers run inside a private VPC connected via VPN to your data center. This allows the build process to reach the private on-prem cluster API.
    * 您使用帶有 **Private Pools** 的 Cloud Build。建置工作節點在透過 VPN 連線到您資料中心的私人 VPC 內運行。這允許建置流程連線到私人地端叢集 API。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **cloudbuild.yaml**: The configuration file. Understanding the syntax (`steps`, `id`, `waitFor`, `substitutions`) is critical for the exam.
    * **cloudbuild.yaml**: 配置檔案。了解語法 (`steps`, `id`, `waitFor`, `substitutions`) 對於考試至關重要。
    * **Substitution Variables**: Use `${_MY_VAR}` to pass dynamic values (like commit SHA) into the build at runtime.
    * **替換變數**: 使用 `${_MY_VAR}` 在執行時將動態值（如 commit SHA）傳遞到建置中。

---

### Cloud Deploy
* **Knowledge Level**: 1: basics
* **附註**: 此項目已在 Containers 類別中詳細說明。
* **產品重要說明 (Product Description)**:
    * (Duplicate) Continuous Delivery for GKE.
    * (重複) GKE 的持續交付。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Recap**: Manages promotion sequences (Dev -> Stage -> Prod) and rollbacks. Integrates with Skaffold.
    * **回顧**: 管理晉升順序 (Dev -> Stage -> Prod) 和復原。與 Skaffold 整合。

---

### Cloud Source Repositories
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Operational Excellence)**. 與 GCP 整合的私有 Git 儲存庫。
* **產品重要說明 (Product Description)**:
    * Cloud Source Repositories (CSR) are fully featured, private Git repositories hosted on Google Cloud.
    * Cloud Source Repositories (CSR) 是託管在 Google Cloud 上的全功能、私人 Git 存放庫。
    * They are integrated with Cloud IAM for access control.
    * 它們與 Cloud IAM 整合以進行存取控制。
* **主要功能 (Main Functions)**:
    * **Mirroring**: Automatically mirror repositories from GitHub or Bitbucket.
    * **鏡像**: 自動從 GitHub 或 Bitbucket 鏡像存放庫。
    * **IAM Integration**: Use Google identities to control who can push/pull code.
    * **IAM 整合**: 使用 Google 身分來控制誰可以推送/拉取程式碼。
    * **Debugger Integration**: Source code is automatically available to Cloud Debugger (deprecated) and Cloud Profiler.
    * **偵錯工具整合**: 原始碼自動可用於 Cloud Debugger (已棄用) 和 Cloud Profiler。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Disaster Recovery for Code.
    * **架構師觀點**: 程式碼的災難復原。
    * Your primary code lives in GitHub. You worry about GitHub outages affecting your deployment pipeline.
    * 您的主要程式碼位於 GitHub。您擔心 GitHub 中斷會影響您的部署流程。
    * You set up CSR to mirror your GitHub repos. If GitHub goes down, your Cloud Build triggers can (with some config changes) pull from CSR instead, ensuring business continuity.
    * 您設定 CSR 來鏡像您的 GitHub 存放庫。如果 GitHub 當機，您的 Cloud Build 觸發程序可以（透過一些配置更改）從 CSR 拉取，從而確保業務連續性。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Search**: Provides semantic code search across all your projects, which is powerful for finding usage of specific libraries across a large organization.
    * **搜尋**: 提供跨所有專案的語意程式碼搜尋，這對於在大型組織中尋找特定函式庫的使用情況非常強大。

---

### Cloud Scheduler
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Operational Excellence)**. 完全託管的 cron 作業服務。
* **產品重要說明 (Product Description)**:
    * Cloud Scheduler is a fully managed enterprise-grade cron job scheduler.
    * Cloud Scheduler 是一個完全託管的企業級 cron 作業排程器。
    * It allows you to schedule virtually any job, including batch, big data, and cloud infrastructure operations.
    * 它允許您排程幾乎任何作業，包括批次、大數據和雲端基礎設施操作。
* **主要功能 (Main Functions)**:
    * **Triggers**: Can trigger HTTP/S endpoints, Pub/Sub topics, or App Engine apps.
    * **觸發程序**: 可以觸發 HTTP/S 端點、Pub/Sub 主題或 App Engine 應用程式。
    * **Reliability**: Guarantees at-least-once delivery.
    * **可靠性**: 保證至少一次傳遞。
    * **Retries**: Configurable retry policies if the job fails.
    * **重試**: 如果作業失敗，可配置重試政策。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Database Backup.
    * **架構師觀點**: 資料庫備份。
    * You have a MongoDB running on Compute Engine (no managed backup).
    * 您在 Compute Engine 上運行 MongoDB（沒有託管備份）。
    * You write a Cloud Function that SSHs into the VM and runs `mongodump`. You set up Cloud Scheduler to trigger this Cloud Function every night at 3 AM via Pub/Sub or HTTP.
    * 您編寫一個 Cloud Function，透過 SSH 進入 VM 並執行 `mongodump`。您設定 Cloud Scheduler 每天凌晨 3 點透過 Pub/Sub 或 HTTP 觸發此 Cloud Function。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Format**: Uses standard unix-cron format (e.g., `0 9 * * 1` for every Monday at 9 AM).
    * **格式**: 使用標準 unix-cron 格式（例如，`0 9 * * 1` 代表每週一上午 9 點）。

---

### Cloud Tasks
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Reliability)**. 處理大量分散式任務的非同步執行。
* **產品重要說明 (Product Description)**:
    * Cloud Tasks is a fully managed service that allows you to manage the execution, dispatch, and delivery of a large number of distributed tasks.
    * Cloud Tasks 是一個完全託管的服務，允許您管理大量分散式任務的執行、調度與傳遞。
    * It is the successor to App Engine Task Queues.
    * 它是 App Engine 任務佇列的繼任者。
* **主要功能 (Main Functions)**:
    * **Rate Limiting**: Control the rate at which tasks are dispatched to your worker (e.g., "Max 500 requests/second").
    * **速率限制**: 控制將任務調度到工作節點的速率（例如，「最大 500 請求/秒」）。
    * **Retries**: Advanced retry configuration (backoff, max attempts).
    * **重試**: 進階重試配置（退避、最大嘗試次數）。
    * **De-duplication**: Prevents adding the same task multiple times (within a time window).
    * **去重複**: 防止多次新增相同的任務（在時間視窗內）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Throttling calls to a legacy backend.
    * **架構師觀點**: 限制對舊版後端的呼叫。
    * A user uploads a CSV with 10,000 records to be processed by a legacy mainframe API that crashes if it gets > 10 req/sec.
    * 使用者上傳包含 10,000 筆記錄的 CSV，由舊版大型主機 API 處理，如果該 API 收到 > 10 請求/秒，就會崩潰。
    * Your ingestion service splits the CSV into 10,000 tasks and adds them to a Cloud Task queue configured with `max_dispatches_per_second = 10`. The queue ensures the mainframe is fed safely.
    * 您的擷取服務將 CSV 分割成 10,000 個任務，並將它們新增到配置了 `max_dispatches_per_second = 10` 的 Cloud Task 佇列中。佇列確保安全地向大型主機饋送資料。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Pub/Sub vs Cloud Tasks**: Pub/Sub is for "fire and forget" multicasting events. Cloud Tasks is for explicit task execution where you need rate limiting and specific retries for a specific worker.
    * **Pub/Sub vs Cloud Tasks**: Pub/Sub 用於「射後不理」的多播事件。Cloud Tasks 用於明確的任務執行，其中您需要針對特定工作節點進行速率限制和特定重試。

---

### Cloud Tools for PowerShell
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **No (Utility)**. 專為 Windows 管理員設計的工具。
* **產品重要說明 (Product Description)**:
    * Cloud Tools for PowerShell is a collection of cmdlets for Windows PowerShell that lets you manage Google Cloud resources.
    * Cloud Tools for PowerShell 是一組適用於 Windows PowerShell 的 cmdlet，讓您管理 Google Cloud 資源。
    * It targets Windows-centric organizations.
    * 它針對以 Windows 為中心的機構。
* **主要功能 (Main Functions)**:
    * **Native Management**: Create VMs, manage Cloud SQL, and bucket storage using standard PowerShell syntax.
    * **原生管理**: 使用標準 PowerShell 語法建立 VM、管理 Cloud SQL 和 bucket 儲存。
    * **Scripting**: Integrate GCP management into existing PowerShell automation scripts.
    * **腳本**: 將 GCP 管理整合到現有的 PowerShell 自動化腳本中。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Windows Admin Team.
    * **架構師觀點**: Windows 管理員團隊。
    * Your IT team is proficient in PowerShell but doesn't know Linux or `gcloud`.
    * 您的 IT 團隊精通 PowerShell，但不了解 Linux 或 `gcloud`。
    * You install Cloud Tools for PowerShell on their workstations so they can manage GCP resources using familiar commands like `Get-GceInstance`.
    * 您在他們的工作站上安裝 Cloud Tools for PowerShell，以便他們可以使用熟悉的指令（如 `Get-GceInstance`）管理 GCP 資源。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Wrapper**: It essentially wraps the .NET client libraries for Google Cloud.
    * **封裝**: 它本質上封裝了 Google Cloud 的 .NET 用戶端函式庫。

---

### Cloud Tools for Visual Studio
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **No (Utility)**. 專為 .NET 開發者設計的 IDE 擴充。
* **產品重要說明 (Product Description)**:
    * An extension for Visual Studio that helps .NET developers build and deploy applications to Google Cloud.
    * 一個 Visual Studio 擴充功能，協助 .NET 開發人員建置並將應用程式部署到 Google Cloud。
* **主要功能 (Main Functions)**:
    * **Right-click Deploy**: Deploy ASP.NET Core apps to App Engine, GKE, or Compute Engine directly from the IDE.
    * **右鍵部署**: 直接從 IDE 將 ASP.NET Core 應用程式部署到 App Engine, GKE 或 Compute Engine。
    * **Resource Explorer**: View and manage GCP resources inside Visual Studio.
    * **資源瀏覽器**: 在 Visual Studio 內部檢視和管理 GCP 資源。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Developer Productivity.
    * **架構師觀點**: 開發者生產力。
    * Facilitating the transition of .NET developers to GCP by allowing them to stay in their familiar IDE environment.
    * 透過允許 .NET 開發人員留在他們熟悉的 IDE 環境中，促進他們過渡到 GCP。

---

### Cloud Tools for Eclipse
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **No (Utility)**. 專為 Java 開發者設計的 IDE 擴充。
* **產品重要說明 (Product Description)**:
    * An extension for the Eclipse IDE that helps Java developers build and deploy applications to Google Cloud.
    * 一個 Eclipse IDE 擴充功能，協助 Java 開發人員建置並將應用程式部署到 Google Cloud。
* **主要功能 (Main Functions)**:
    * **App Engine Deployment**: Simplified deployment for App Engine Standard/Flex.
    * **App Engine 部署**: 簡化 App Engine Standard/Flex 的部署。
    * **Local Development**: Emulators for testing locally.
    * **本地開發**: 用於本地測試的模擬器。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Legacy Java Maintenance.
    * **架構師觀點**: 舊版 Java 維護。
    * Useful for teams maintaining legacy Java applications who are accustomed to Eclipse.
    * 對於習慣使用 Eclipse 維護舊版 Java 應用程式的團隊很有用。

---

### Helm
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **Yes (Operational Excellence)**. Kubernetes 的套件管理器。
* **產品重要說明 (Product Description)**:
    * Helm is an open-source package manager for Kubernetes.
    * Helm 是一個 Kubernetes 的開源套件管理器。
    * It helps you manage Kubernetes applications through "Charts" (packages of pre-configured K8s resources).
    * 它協助您透過 "Charts"（預先配置的 K8s 資源套件）管理 Kubernetes 應用程式。
* **主要功能 (Main Functions)**:
    * **Templating**: Replace hardcoded values in YAMLs with variables.
    * **樣板化**: 使用變數取代 YAML 中的硬編碼值。
    * **Versioning**: Track versions of your application deployments.
    * **版本控制**: 追蹤應用程式部署的版本。
    * **Reusability**: Share complex application setups (e.g., Prometheus + Grafana stack) easily.
    * **可重複使用性**: 輕鬆分享複雜的應用程式設定（例如 Prometheus + Grafana 堆疊）。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Standardizing Deployments.
    * **架構師觀點**: 標準化部署。
    * Instead of developers writing raw Kubernetes YAMLs (error-prone), you create a Helm Chart for your company's standard microservice (including Service, Deployment, HPA, Ingress).
    * 您為公司的標準微服務（包含 Service, Deployment, HPA, Ingress）建立 Helm Chart，而不是讓開發人員編寫原始的 Kubernetes YAML（容易出錯）。
    * Developers simply run `helm install my-app ./my-chart --set image=v1`.
    * 開發人員只需執行 `helm install my-app ./my-chart --set image=v1`。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Artifact Registry**: Can now host Helm charts (OCI format), treating them like container images.
    * **Artifact Registry**: 現在可以託管 Helm Charts (OCI 格式)，將它們像容器映像檔一樣對待。

---
## Internet of Things

### Cloud IoT Core
* **Knowledge Level**: 1: basics
* **重要通知 (Important Notice)**:
    * **Google Cloud has officially retired IoT Core (discontinued on August 16, 2023).**
    * **Google Cloud 已正式淘汰 IoT Core（於 2023 年 8 月 16 日停止服務）。**
    * *However, since it is in your list, I will provide the context for historical understanding or for migrating away from it.*
    * *然而，由於它在您的清單中，我將提供相關背景，以便了解歷史或進行遷移。*
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: **No (Retired)**.
* **產品重要說明 (Product Description)**:
    * Cloud IoT Core was a fully managed service for securely connecting, managing, and ingesting data from millions of globally dispersed devices.
    * Cloud IoT Core 曾是一個完全託管的服務，用於安全地連線、管理和擷取來自全球數百萬個分散裝置的資料。
    * It used MQTT and HTTP protocols to bridge devices with GCP services like Pub/Sub.
    * 它使用 MQTT 和 HTTP 協定將裝置與 GCP 服務（如 Pub/Sub）橋接起來。
* **主要功能 (Main Functions)**:
    * **Device Manager**: Registered devices and managed their identity (keys).
    * **裝置管理員**: 註冊裝置並管理其身分（金鑰）。
    * **Protocol Bridge**: Terminated MQTT/HTTP connections and forwarded telemetry to Pub/Sub.
    * **協定橋接器**: 終止 MQTT/HTTP 連線並將遙測資料轉發到 Pub/Sub。
* **詳盡應用情境 (Detailed Scenarios)**:
    * **Architect's View**: Migration Strategy (Current context).
    * **架構師觀點**: 遷移策略（目前情境）。
    * Since the service is retired, you would look for partner solutions (like ClearBlade, KORE Wireless) that offer a similar MQTT broker interface or build your own using generic MQTT brokers on GKE (complex).
    * 由於該服務已停止，您會尋找提供類似 MQTT 代理介面的合作夥伴解決方案（如 ClearBlade, KORE Wireless），或在 GKE 上使用通用 MQTT 代理自行建立（複雜）。
* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Retirement**: It is crucial for the exam to know that this service is no longer a valid option for new designs.
    * **退役**: 為了考試，務必知道此服務對於新設計不再是有效選項。

---

## Management Tools

### Cloud Shell
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: 是 (Operational Excellence - 用於快速管理與故障排除 / Used for rapid management and troubleshooting)

* **產品重要說明 (Product Description)**:
    * Cloud Shell 是一個互動式的 shell 環境，可直接透過瀏覽器隨時隨地存取 Google Cloud 資源。
    * Cloud Shell is an interactive shell environment for Google Cloud that allows you to access resources from anywhere directly through your browser.
    * 它提供了一個預先安裝並經過驗證的線上終端機，無需在本機安裝任何工具即可開始工作。
    * It provides a pre-installed and authenticated online terminal, allowing you to start working without installing any tools locally.

* **主要功能 (Main Functions)**:
    * **預裝工具 (Pre-installed Tools)**: 內建 `gcloud`、`kubectl`、`terraform`、Docker、Java、Go、Python 等常用工具。
    * **Pre-installed Tools**: Built-in common tools like `gcloud`, `kubectl`, `terraform`, Docker, Java, Go, Python, and more.
    * **持久性磁碟儲存 (Persistent Disk Storage)**: 每個使用者擁有 5GB 的持久性主目錄 (`$HOME`) 儲存空間。
    * **Persistent Disk Storage**: Each user gets 5GB of persistent home directory (`$HOME`) storage.
    * **網頁預覽 (Web Preview)**: 允許使用者預覽在 Cloud Shell 虛擬機上運行的 Web 應用程式 (連接埠 8080-8084)。
    * **Web Preview**: Allows users to preview web applications running on the Cloud Shell VM instance (ports 8080-8084).

* **詳盡應用情境 (Detailed Scenarios)**:
    * **臨時管理任務 (Ad-hoc Administration)**:
        * 當架構師需要快速執行 `gcloud` 指令來檢查資源狀態或重啟 VM，但手邊沒有配置好環境的筆電時。
        * When an architect needs to quickly execute `gcloud` commands to check resource status or restart a VM but doesn't have a configured laptop at hand.
    * **開發與測試腳本 (Development and Testing Scripts)**:
        * 在部署到正式環境前，開發者利用 Cloud Shell 快速測試 Terraform 設定檔或 Python SDK 腳本。
        * Developers use Cloud Shell to quickly test Terraform configuration files or Python SDK scripts before deploying to production.

* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **暫時性虛擬機 (Ephemeral VM)**: Cloud Shell 運行在一個暫時的 VM 上，該 VM 在閒置一段時間後會被重置，只有 `$HOME` 目錄下的資料會被保留。
    * **Ephemeral VM**: Cloud Shell runs on a temporary VM that resets after a period of inactivity; only data in the `$HOME` directory is persisted.
    * **Private IP 存取 (Private IP Access)**: Cloud Shell 本身位於 Google 管理的網路中，若要存取僅有 Private IP 的 VPC 資源，通常需要透過 IAP (Identity-Aware Proxy) 建立通道。
    * **Private IP Access**: Cloud Shell resides in a Google-managed network; to access VPC resources with only Private IPs, you typically need to establish a tunnel via IAP (Identity-Aware Proxy).

---

### Service Catalog
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: 是 (Security and Compliance - 用於治理與標準化 / Used for governance and standardization)

* **產品重要說明 (Product Description)**:
    * Service Catalog 允許企業策劃並管理一套經核准的 IT 解決方案目錄，供內部使用者部署。
    * Service Catalog allows enterprises to curate and manage a catalog of approved IT solutions for internal users to deploy.
    * 它確保了組織內部的雲端資源部署符合合規性與架構標準。
    * It ensures that cloud resource deployments within the organization comply with compliance and architectural standards.

* **主要功能 (Main Functions)**:
    * **集中式目錄管理 (Centralized Catalog Management)**: 管理員可上架 Cloud Deployment Manager 或 Terraform 的範本。
    * **Centralized Catalog Management**: Administrators can onboard Cloud Deployment Manager or Terraform templates.
    * **存取控制 (Access Control)**: 控制哪些使用者或群組可以看到並部署特定的解決方案。
    * **Access Control**: Control which users or groups can view and deploy specific solutions.

* **詳盡應用情境 (Detailed Scenarios)**:
    * **自助式服務門戶 (Self-service Portal)**:
        * 數據科學團隊需要部署 Jupyter Notebook 環境，他們可以從 Service Catalog 選擇經資安部門核准的範本，而無需了解底層網路設定。
        * A data science team needs to deploy a Jupyter Notebook environment; they can select a security-approved template from the Service Catalog without needing to understand the underlying network settings.

* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **與 Deployment Manager/Terraform 整合 (Integration)**: Service Catalog 的核心是透過基礎設施即程式碼 (IaC) 範本來驅動的。
    * **Integration**: Service Catalog is driven at its core by Infrastructure as Code (IaC) templates.
    * **治理 (Governance)**: 這是 PCA 考試中關於「如何強制執行標準化部署」或「限制開發者只能使用特定配置」的常見解答。
    * **Governance**: This is a common answer in the PCA exam regarding "how to enforce standardized deployments" or "restricting developers to specific configurations."

---

### Cloud Deployment Manager
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: 是 (Operational Excellence - 基礎設施即程式碼 / Infrastructure as Code)

* **產品重要說明 (Product Description)**:
    * Cloud Deployment Manager 是 Google Cloud 原生的基礎設施部署服務，使用宣告式語言來定義資源。
    * Cloud Deployment Manager is Google Cloud's native infrastructure deployment service that uses declarative language to define resources.
    * 它允許使用者透過 YAML 或 Python 範本來自動化建立與管理 GCP 資源。
    * It allows users to automate the creation and management of GCP resources via YAML or Python templates.

* **主要功能 (Main Functions)**:
    * **宣告式配置 (Declarative Configuration)**: 使用者定義「由於什麼狀態」(What)，而非「如何做」(How)，系統會自動處理依賴關係。
    * **Declarative Configuration**: Users define "what" the state should be rather than "how" to do it, and the system automatically handles dependencies.
    * **並行部署 (Parallel Deployment)**: 能夠同時並行部署多個資源以加快速度。
    * **Parallel Deployment**: Capable of deploying multiple resources in parallel to speed up the process.

* **詳盡應用情境 (Detailed Scenarios)**:
    * **環境複製 (Environment Replication)**:
        * 快速複製一套與生產環境完全相同的測試環境，包含 VPC、VM 和負載平衡器。
        * Quickly replicating a test environment that is identical to production, including VPCs, VMs, and Load Balancers.

* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **結構 (Structure)**: 設定檔 (Configuration .yaml) -> 匯入範本 (Templates .jinja/.py) -> 綱要 (Schema)。
    * **Structure**: Configuration (.yaml) -> Imports Templates (.jinja/.py) -> Schema.
    * **預覽模式 (Preview Mode)**: 在實際變更資源前，可以預覽部署將會產生的影響 (類似 Terraform plan)。
    * **Preview Mode**: You can preview the impact of a deployment before actually changing resources (similar to Terraform plan).
    * **目前狀態 (Current State)**: 雖然 Terraform 目前在業界更為流行，但 Deployment Manager 仍是 GCP 原生工具，考試中仍需了解其基本運作。
    * **Current State**: While Terraform is more popular in the industry, Deployment Manager is the native GCP tool, and understanding its basic operation is still required for the exam.

---

### Terraform
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: 是 (Operational Excellence - 行業標準 IaC 工具 / Industry Standard IaC Tool)

* **產品重要說明 (Product Description)**:
    * Terraform 是 HashiCorp 開發的開源基礎設施即程式碼 (IaC) 工具，廣泛用於跨雲平台的資源管理。
    * Terraform is an open-source Infrastructure as Code (IaC) tool developed by HashiCorp, widely used for resource management across cloud platforms.
    * 它透過狀態檔 (State file) 來追蹤資源狀態，確保雲端實際環境與程式碼定義一致。
    * It tracks resource status via a State file, ensuring the actual cloud environment matches the code definition.

* **主要功能 (Main Functions)**:
    * **Google Cloud Provider**: Google 提供官方維護的 Terraform Provider，支援幾乎所有 GCP 資源。
    * **Google Cloud Provider**: Google offers an officially maintained Terraform Provider supporting almost all GCP resources.
    * **狀態管理 (State Management)**: 使用 `tfstate` 檔案記錄資源屬性，建議將此檔案儲存在 GCS bucket 中以實現團隊協作與鎖定 (Locking)。
    * **State Management**: Uses `tfstate` files to record resource attributes; it is recommended to store this file in a GCS bucket for team collaboration and locking.

* **詳盡應用情境 (Detailed Scenarios)**:
    * **多雲架構管理 (Multi-cloud Management)**:
        * 企業使用 Terraform 同時管理 GCP 的 BigQuery 和 AWS 的 S3，使用統一的工作流程。
        * An enterprise uses Terraform to manage GCP BigQuery and AWS S3 simultaneously using a unified workflow.

* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **IaC 最佳實踐 (IaC Best Practices)**: 將 Terraform 狀態檔存在 GCS Bucket (Backend) 而非本地，以啟用版本控制和防止並發寫入衝突。
    * **IaC Best Practices**: Store the Terraform state file in a GCS Bucket (Backend) instead of locally to enable versioning and prevent concurrent write conflicts.
    * **不可變基礎設施 (Immutable Infrastructure)**: 鼓勵透過替換而非修補的方式來更新伺服器，Terraform 非常適合此模式。
    * **Immutable Infrastructure**: Encourages updating servers by replacing them rather than patching; Terraform fits this pattern perfectly.

---

### Cloud Billing
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: 是 (Cost Optimization - 核心組件 / Core Component)

* **產品重要說明 (Product Description)**:
    * Cloud Billing 是一套工具集，用於管理 Google Cloud 的費用支付、預算設定及成本分析。
    * Cloud Billing is a suite of tools used to manage payments, budget settings, and cost analysis for Google Cloud.
    * 它定義了誰負責支付資源費用，並透過帳單帳戶 (Billing Account) 與專案 (Project) 連結。
    * It defines who is responsible for paying for resources and links to Projects via a Billing Account.

* **主要功能 (Main Functions)**:
    * **預算與快訊 (Budgets & Alerts)**: 設定支出門檻，當成本達到預算百分比時發送 Email 或 Pub/Sub 通知。
    * **Budgets & Alerts**: Set spending thresholds to send Emails or Pub/Sub notifications when costs reach a percentage of the budget.
    * **Billing Export**: 將詳細的帳單數據匯出至 BigQuery 以進行深入的 SQL 分析或製作 Data Studio 報表。
    * **Billing Export**: Export detailed billing data to BigQuery for in-depth SQL analysis or Data Studio reporting.

* **詳盡應用情境 (Detailed Scenarios)**:
    * **自動化成本控制 (Automated Cost Control)**:
        * 設定預算快訊發送消息到 Pub/Sub，觸發 Cloud Function 自動關閉測試環境的 VM 以防止費用超支。
        * Configure budget alerts to send messages to Pub/Sub, triggering a Cloud Function to automatically shut down VMs in a test environment to prevent overspending.

* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **IAM 角色 (IAM Roles)**: 區分 `Billing Account Administrator` (管理付款方式、發票) 與 `Project Billing Manager` (將專案連結至帳單帳戶)。
    * **IAM Roles**: Distinguish between `Billing Account Administrator` (manages payment methods, invoices) and `Project Billing Manager` (links projects to billing accounts).
    * **帳單層級 (Billing Hierarchy)**: 組織 (Organization) -> 帳單帳戶 (Billing Account) -> 專案 (Project)。一個專案只能連結一個帳單帳戶。
    * **Billing Hierarchy**: Organization -> Billing Account -> Project. A project can only be linked to one billing account.
    * **Cap Cost**: 預設的預算通知 **不會** 自動停止資源，必須透過程式化方式 (Programmatic approach) 實作。
    * **Cap Cost**: Default budget notifications do **NOT** automatically stop resources; this must be implemented via a programmatic approach.

---

## ARTIFICIAL INTELLIGENCE / MACHINE LEARNING

### AutoML Natural Language
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: 否 (屬於特定領域應用服務 / Specific domain application service)

* **產品重要說明 (Product Description)**:
    * AutoML Natural Language 允許開發者使用自己的數據訓練自定義的機器學習模型，以進行文本分類、實體提取或情感分析，且無需撰寫 ML 程式碼。
    * AutoML Natural Language allows developers to train custom machine learning models for text classification, entity extraction, or sentiment analysis using their own data, without writing ML code.
    * 它填補了通用 API 與完全自定義 TensorFlow 模型之間的空白。
    * It bridges the gap between generic APIs and fully custom TensorFlow models.

* **主要功能 (Main Functions)**:
    * **自定義分類 (Custom Classification)**: 將文本分類為使用者定義的標籤（例如：將客服工單分類為「退款」、「技術支援」、「一般諮詢」）。
    * **Custom Classification**: Categorize text into user-defined labels (e.g., classifying support tickets as "Refund", "Tech Support", "General Inquiry").
    * **自定義實體提取 (Custom Entity Extraction)**: 識別特定領域的關鍵字（例如：從醫療報告中提取特定的藥品名稱）。
    * **Custom Entity Extraction**: Identify domain-specific keywords (e.g., extracting specific drug names from medical reports).

* **詳盡應用情境 (Detailed Scenarios)**:
    * **特定領域文件分析 (Domain-specific Document Analysis)**:
        * 一家律師事務所需要自動標記合約中的法律條款，標準的 NLP API 無法識別這些專有名詞，因此使用 AutoML 進行訓練。
        * A law firm needs to automatically tag legal clauses in contracts; standard NLP APIs cannot recognize these proper terms, so they use AutoML for training.

* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **AutoML vs. Cloud Natural Language API**: 這是考試關鍵。若需求是通用的（如「這句話是正面的嗎？」），使用 API；若需求是特定的（如「這句話是在抱怨我們的 X 型號產品嗎？」），使用 AutoML。
    * **AutoML vs. Cloud Natural Language API**: This is key for the exam. If the requirement is generic (e.g., "Is this sentence positive?"), use the API; if specific (e.g., "Is this sentence complaining about our Model X product?"), use AutoML.

---

### AutoML Translation
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: 否

* **產品重要說明 (Product Description)**:
    * AutoML Translation 讓使用者能上傳已翻譯的語言對 (Language pairs)，訓練出針對特定領域術語優化的自定義翻譯模型。
    * AutoML Translation allows users to upload translated language pairs to train custom translation models optimized for domain-specific terminology.
    * 它建立在 Google 強大的翻譯技術之上，但允許修正特定詞彙的翻譯方式。
    * It builds upon Google's powerful translation technology but allows for corrections in how specific vocabulary is translated.

* **主要功能 (Main Functions)**:
    * **自定義模型訓練 (Custom Model Training)**: 使用 TMX 檔案或 CSV 格式的平行句子數據集進行訓練。
    * **Custom Model Training**: Train using parallel sentence datasets in TMX or CSV formats.
    * **詞彙表 (Glossary)**: 雖然標準 API 也有詞彙表功能，但 AutoML 能更深入地學習句式結構的風格。
    * **Glossary**: While the standard API also has glossary features, AutoML can more deeply learn the style of sentence structures.

* **詳盡應用情境 (Detailed Scenarios)**:
    * **金融或醫療文件翻譯 (Financial or Medical Document Translation)**:
        * 翻譯含有高度專業術語的財報或病歷，通用翻譯可能會誤解上下文，AutoML 則可依據歷史文件提供精準翻譯。
        * Translating financial reports or medical records containing highly technical jargon; generic translation might misinterpret the context, whereas AutoML can provide precise translation based on historical documents.

* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **數據需求 (Data Requirements)**: 訓練高品質模型需要大量的平行語料庫 (Parallel Corpus)。
    * **Data Requirements**: Training high-quality models requires a significant amount of parallel corpus.
    * **適用時機 (Use Case)**: 當 Cloud Translation API 的準確度不足以應對特定行業的行話時。
    * **Use Case**: When the accuracy of the Cloud Translation API is insufficient for specific industry jargon.

---

### Video AI (Cloud Video Intelligence API)
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: 否

* **產品重要說明 (Product Description)**:
    * Video AI (Cloud Video Intelligence API) 是一個預先訓練好的機器學習服務，可分析影片內容以識別物體、地點、動作及文字。
    * Video AI (Cloud Video Intelligence API) is a pre-trained machine learning service that analyzes video content to identify objects, places, actions, and text.
    * 它使影片像文件一樣可被搜尋和檢索。
    * It makes videos as searchable and discoverable as documents.

* **主要功能 (Main Functions)**:
    * **標籤檢測 (Label Detection)**: 識別影片中的實體（如「狗」、「海灘」、「跑步」）。
    * **Label Detection**: Identify entities in the video (e.g., "Dog", "Beach", "Run").
    * **鏡頭轉換檢測 (Shot Change Detection)**: 自動識別影片中的場景切換點。
    * **Shot Change Detection**: Automatically identify scene changes within a video.
    * **明確內容檢測 (Explicit Content Detection)**: 過濾成人或暴力內容。
    * **Explicit Content Detection**: Filter adult or violent content.

* **詳盡應用情境 (Detailed Scenarios)**:
    * **媒體資產管理 (Media Asset Management)**:
        * 電視台將數萬小時的歷史存檔上傳至 GCS，使用 Video AI 自動生成標籤（MetaData），讓編輯能搜尋「包含艾菲爾鐵塔的片段」。
        * A TV station uploads tens of thousands of hours of archives to GCS and uses Video AI to generate metadata, allowing editors to search for "clips containing the Eiffel Tower."

* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **儲存整合 (Storage Integration)**: 影片通常儲存在 Cloud Storage (GCS) 中，API 直接讀取 GCS URI 進行處理。
    * **Storage Integration**: Videos are typically stored in Cloud Storage (GCS), and the API reads the GCS URI directly for processing.
    * **非同步處理 (Asynchronous Processing)**: 影片分析通常是長時間運行的操作 (Long-running operations)，結果會以 JSON 格式返回。
    * **Asynchronous Processing**: Video analysis is typically a long-running operation, and results are returned in JSON format.

---

### Cloud Natural Language
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: 否

* **產品重要說明 (Product Description)**:
    * Cloud Natural Language 提供預先訓練好的模型，透過 REST API 揭示文本的結構與意義。
    * Cloud Natural Language provides pre-trained models to reveal the structure and meaning of text via REST API.
    * 開發者無需具備 ML 知識即可立即使用。
    * Developers can use it immediately without ML knowledge.

* **主要功能 (Main Functions)**:
    * **情感分析 (Sentiment Analysis)**: 判斷文本是正面、負面還是中立 (Score & Magnitude)。
    * **Sentiment Analysis**: Determine if text is positive, negative, or neutral (Score & Magnitude).
    * **實體識別 (Entity Analysis)**: 識別人物、組織、地點、事件等。
    * **Entity Analysis**: Identify people, organizations, locations, events, etc.
    * **語法分析 (Syntax Analysis)**: 解析句子的語法結構。
    * **Syntax Analysis**: Parse the grammatical structure of sentences.

* **詳盡應用情境 (Detailed Scenarios)**:
    * **社群媒體監控 (Social Media Monitoring)**:
        * 行銷團隊透過 API 即時分析 Twitter 上關於新產品的推文情感，以評估市場反應。
        * A marketing team analyzes sentiment of tweets about a new product in real-time via the API to gauge market reaction.

* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **現成可用 (Out-of-the-box)**: 與 AutoML 的主要區別在於它不需要訓練數據，但只能識別通用概念。
    * **Out-of-the-box**: The main difference from AutoML is that it requires no training data but can only recognize generic concepts.
    * **資料隱私 (Data Privacy)**: Google 提供選項不記錄傳送至 API 的數據以用於模型改進（需透過加入計畫或特定設定）。
    * **Data Privacy**: Google offers options not to log data sent to the API for model improvement (via opt-in/opt-out settings).

---

### Cloud Translation
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: 否

* **產品重要說明 (Product Description)**:
    * Cloud Translation API 提供程式化的介面來翻譯任意字串，支援超過一百種語言。
    * Cloud Translation API provides a programmatic interface to translate arbitrary strings, supporting over a hundred languages.
    * 它與 Google 翻譯 (Consumer version) 使用相同的技術，但針對企業規模進行了優化。
    * It uses the same technology as Google Translate (Consumer version) but is optimized for enterprise scale.

* **主要功能 (Main Functions)**:
    * **語言檢測 (Language Detection)**: 自動識別輸入文本的來源語言。
    * **Language Detection**: Automatically identify the source language of the input text.
    * **文本翻譯 (Text Translation)**: 將文本從一種語言轉換為另一種語言。
    * **Text Translation**: Convert text from one language to another.

* **詳盡應用情境 (Detailed Scenarios)**:
    * **即時聊天翻譯 (Real-time Chat Translation)**:
        * 跨國遊戲平台使用此 API 讓講不同語言的玩家在聊天室中即時溝通。
        * A global gaming platform uses this API to allow players speaking different languages to communicate in real-time within chat rooms.
    * **網站本地化 (Website Localization)**:
        * 電商平台動態翻譯產品描述給全球買家。
        * An e-commerce platform dynamically translates product descriptions for global buyers.

* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **版本 (Editions)**: 區分為 Basic (標準翻譯) 與 Advanced (支援詞彙表、批次翻譯、AutoML 模型整合)。
    * **Editions**: Distinguished between Basic (standard translation) and Advanced (supports glossaries, batch translation, AutoML model integration).
    * **簡單整合 (Simple Integration)**: 架構師常將其作為資料處理管線 (Dataflow) 的一部分，進行資料清洗或標準化。
    * **Simple Integration**: Architects often include it as part of a data processing pipeline (Dataflow) for data cleansing or standardization.

---

### Text-to-Speech
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: 否

* **產品重要說明 (Product Description)**:
    * Text-to-Speech API 能將文字轉換為自然流暢的語音，並支援多種語言與聲音。
    * The Text-to-Speech API converts text into natural-sounding speech, supporting a wide variety of languages and voices.
    * 它利用 DeepMind 的 WaveNet 技術，產生極高保真度的合成語音。
    * It leverages DeepMind's WaveNet technology to synthesize high-fidelity speech.

* **主要功能 (Main Functions)**:
    * **WaveNet 語音 (WaveNet Voices)**: 提供比標準語音更接近真人的合成聲音。
    * **WaveNet Voices**: Provides synthesized voices that sound much more human than standard voices.
    * **SSML 支援 (SSML Support)**: 支援語音合成標記語言 (SSML)，可微調發音、語速、音調及停頓。
    * **SSML Support**: Supports Speech Synthesis Markup Language (SSML) to fine-tune pronunciation, rate, pitch, and pauses.

* **詳盡應用情境 (Detailed Scenarios)**:
    * **無障礙應用 (Accessibility Applications)**:
        * 新聞 App 使用此 API 將文章朗讀給視障使用者聽。
        * A news app uses this API to read articles aloud to visually impaired users.
    * **物聯網設備 (IoT Devices)**:
        * 智慧音箱或家電透過 API 發出語音通知（如「洗衣行程已完成」）。
        * Smart speakers or appliances use the API to provide voice notifications (e.g., "Laundry cycle complete").

* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **音訊編碼 (Audio Encoding)**: 支援 MP3, Linear16 (WAV), Ogg Opus 等格式輸出，架構師需根據頻寬需求選擇合適格式。
    * **Audio Encoding**: Supports output formats like MP3, Linear16 (WAV), and Ogg Opus; architects need to choose the appropriate format based on bandwidth requirements.

---

### Speech-to-Text
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: 否

* **產品重要說明 (Product Description)**:
    * Speech-to-Text API 使用機器學習技術將音訊轉換為文字，支援串流 (Streaming) 與批次 (Batch) 處理。
    * The Speech-to-Text API uses machine learning to convert audio to text, supporting both streaming and batch processing.
    * 它能適應各種音訊品質，包括電話通話或嘈雜環境中的錄音。
    * It adapts to various audio qualities, including phone calls or recordings in noisy environments.

* **主要功能 (Main Functions)**:
    * **即時語音識別 (Real-time Speech Recognition)**: 在使用者說話時同步回傳文字結果。
    * **Real-time Speech Recognition**: Returns text results synchronously as the user speaks.
    * **自動標點符號 (Automatic Punctuation)**: 自動在轉錄文本中加入逗號、問號與句號。
    * **Automatic Punctuation**: Automatically adds commas, question marks, and periods to the transcribed text.
    * **多聲道識別 (Multi-channel Recognition)**: 能區分不同的發言者 (Speaker Diarization)。
    * **Multi-channel Recognition**: Capable of distinguishing between different speakers (Speaker Diarization).

* **詳盡應用情境 (Detailed Scenarios)**:
    * **客戶服務分析 (Customer Service Analysis)**:
        * 客服中心將通話錄音轉錄為文字，隨後使用 Natural Language API 分析客戶滿意度。
        * A call center transcribes call recordings into text, then uses the Natural Language API to analyze customer satisfaction.

* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **模型適應 (Model Adaptation)**: 可透過提供「短語提示 (Phrase Hints)」來提高特定詞彙（如產品名稱或指令）的識別準確率。
    * **Model Adaptation**: Recognition accuracy for specific vocabulary (like product names or commands) can be improved by providing "Phrase Hints."
    * **雜訊處理 (Noise Handling)**: 專為處理現實世界中的嘈雜音訊而設計，無需大量預處理。
    * **Noise Handling**: Designed to handle real-world noisy audio without requiring extensive pre-processing.

---

### Dialogflow
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: 否

* **產品重要說明 (Product Description)**:
    * Dialogflow 是一個端到端的開發套件，用於構建對話式介面（聊天機器人與語音機器人）。
    * Dialogflow is an end-to-end development suite for building conversational interfaces (chatbots and voicebots).
    * 它使用自然語言理解 (NLU) 來處理使用者輸入並將其對應到相應的意圖 (Intents)。
    * It uses Natural Language Understanding (NLU) to process user input and map it to corresponding Intents.

* **主要功能 (Main Functions)**:
    * **意圖與實體 (Intents & Entities)**: 定義使用者的意圖（想做什麼）並從中提取參數（如日期、地點）。
    * **Intents & Entities**: Define user intents (what they want to do) and extract parameters (like dates, locations) from them.
    * **履行 (Fulfillment)**: 透過 Webhook (通常連接 Cloud Functions) 執行後端邏輯並動態產生回應。
    * **Fulfillment**: Execute backend logic and dynamically generate responses via Webhooks (typically connected to Cloud Functions).
    * **多平台整合 (Multi-platform Integration)**: 一鍵整合至 Google Assistant, Slack, Facebook Messenger 等。
    * **Multi-platform Integration**: One-click integration with Google Assistant, Slack, Facebook Messenger, and more.

* **詳盡應用情境 (Detailed Scenarios)**:
    * **自助服務機器人 (Self-service Bot)**:
        * 銀行 App 內建聊天機器人，讓使用者查詢餘額或轉帳。Dialogflow 解析「轉 500 給媽媽」，後端 Cloud Function 執行交易。
        * A banking app features a built-in chatbot for users to check balances or transfer money. Dialogflow parses "Transfer 500 to Mom," and a backend Cloud Function executes the transaction.

* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **版本差異 (Editions)**: 需區分 **Dialogflow ES** (標準版，適合簡單問答) 與 **Dialogflow CX** (進階版，適合複雜的多輪對話流程與企業級應用)。
    * **Editions**: Distinguish between **Dialogflow ES** (Standard, for simple Q&A) and **Dialogflow CX** (Advanced, for complex multi-turn conversation flows and enterprise applications).

---

### Recommendations AI
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: 否

* **產品重要說明 (Product Description)**:
    * Recommendations AI (現整合於 Discovery Solutions / Vertex AI Search for Retail) 提供基於 Google 機器學習技術的個人化推薦服務。
    * Recommendations AI (now integrated into Discovery Solutions / Vertex AI Search for Retail) delivers personalized recommendation services based on Google's machine learning technology.
    * 它能根據使用者的瀏覽行為與購買歷史，預測他們可能感興趣的商品。
    * It predicts products users might be interested in based on their browsing behavior and purchase history.

* **主要功能 (Main Functions)**:
    * **高度個人化 (Highly Personalized)**: 不僅僅是「熱門商品」，而是針對該使用者的即時推薦。
    * **Highly Personalized**: Not just "popular items," but real-time recommendations tailored to that user.
    * **目標優化 (Objective Optimization)**: 可選擇優化點擊率 (CTR) 或 轉換率 (CVR) 或 營收 (Revenue)。
    * **Objective Optimization**: Choose to optimize for Click-Through Rate (CTR), Conversion Rate (CVR), or Revenue.

* **詳盡應用情境 (Detailed Scenarios)**:
    * **電商首頁推薦 (E-commerce Homepage Recommendations)**:
        * 當使用者登入購物網站時，首頁顯示「為您推薦」區塊，展示他們可能購買的商品，從而提高平均訂單價值。
        * When a user logs into a shopping site, the homepage displays a "Recommended for You" section showing items they are likely to buy, thereby increasing average order value.

* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **數據導入 (Data Ingestion)**: 必須導入「產品目錄 (Catalog)」與「使用者事件 (User Events, 如點擊、加購物車)」才能訓練模型。
    * **Data Ingestion**: You must ingest "Product Catalog" and "User Events" (e.g., clicks, add-to-cart) to train the model.
    * **冷啟動 (Cold Start)**: Google 的模型能較好地處理新使用者或新產品的推薦問題。
    * **Cold Start**: Google's models handle the recommendation problem for new users or new products relatively well.

---

### AI Platform
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: 是 (Operational Excellence - MLOps 基礎 / MLOps Foundation)

* **產品重要說明 (Product Description)**:
    * AI Platform (舊稱，現正逐步遷移至 **Vertex AI**) 是一套用於機器學習開發生命週期的託管服務。
    * AI Platform (legacy name, transitioning to **Vertex AI**) is a suite of managed services for the machine learning development lifecycle.
    * 它允許資料科學家訓練、調整與部署自定義的機器學習模型。
    * It allows data scientists to train, tune, and deploy custom machine learning models.

* **主要功能 (Main Functions)**:
    * **AI Platform Training**: 無伺服器環境下執行 TensorFlow, Scikit-learn, XGBoost 的訓練作業。
    * **AI Platform Training**: Run training jobs for TensorFlow, Scikit-learn, and XGBoost in a serverless environment.
    * **AI Platform Prediction**: 託管模型以提供線上預測 (Online Prediction) 或批次預測 (Batch Prediction) 的 API 端點。
    * **AI Platform Prediction**: Host models to provide API endpoints for Online Prediction or Batch Prediction.
    * **Notebooks**: 託管的 JupyterLab 環境 (現為 Vertex AI Workbench)。
    * **Notebooks**: Managed JupyterLab environments (now Vertex AI Workbench).

* **詳盡應用情境 (Detailed Scenarios)**:
    * **自定義模型部署 (Custom Model Deployment)**:
        * 團隊開發了一個獨特的房價預測 TensorFlow 模型，使用 AI Platform Training 進行大規模訓練，並部署到 AI Platform Prediction 供 Web App 呼叫。
        * A team develops a unique housing price prediction TensorFlow model, trains it at scale using AI Platform Training, and deploys it to AI Platform Prediction for the Web App to call.

* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Vertex AI 關係 (Relation to Vertex AI)**: 考試中若同時出現 AI Platform 與 Vertex AI，Vertex AI 通常是現代化、整合性更強的正確答案，但需了解 AI Platform 是其前身，指代基礎的訓練與預測服務。
    * **Relation to Vertex AI**: If both AI Platform and Vertex AI appear in the exam, Vertex AI is usually the modern, more integrated correct answer, but understand that AI Platform is its predecessor, referring to basic training and prediction services.
    * **容器支援 (Container Support)**: 支援使用自定義 Docker 容器來運行任何 ML 框架的訓練代碼。
    * **Container Support**: Supports using custom Docker containers to run training code for any ML framework.

---

### Vertex AI
* **Knowledge Level**: 2: medium
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: 是 (Operational Excellence - 統一的 MLOps 平台 / Unified MLOps Platform)

* **產品重要說明 (Product Description)**:
    * Vertex AI 是 Google Cloud 的統一機器學習平台，整合了 AutoML 和 AI Platform 的功能。
    * Vertex AI is Google Cloud's unified machine learning platform, integrating the capabilities of AutoML and AI Platform.
    * 它提供了一套完整的 MLOps 工具，旨在加速機器學習模型從開發到部署與管理的整個生命週期。
    * It offers a comprehensive suite of MLOps tools designed to accelerate the entire lifecycle of machine learning models from development to deployment and management.

* **主要功能 (Main Functions)**:
    * **統一 UI 與 API (Unified UI & API)**: 單一介面管理 AutoML 訓練與自定義代碼訓練 (Custom Training)。
    * **Unified UI & API**: A single interface to manage both AutoML training and Custom Training.
    * **Vertex Pipelines**: 構建並自動化 ML 工作流程（基於 Kubeflow 或 TFX）。
    * **Vertex Pipelines**: Build and automate ML workflows (based on Kubeflow or TFX).
    * **Feature Store**: 集中管理與服務 ML 特徵，確保訓練與服務時的一致性。
    * **Feature Store**: Centrally manage and serve ML features to ensure consistency between training and serving.
    * **Model Monitoring**: 持續監控部署的模型是否存在偏差 (Skew) 或漂移 (Drift)。
    * **Model Monitoring**: Continuously monitor deployed models for Skew or Drift.

* **詳盡應用情境 (Detailed Scenarios)**:
    * **端到端 MLOps (End-to-End MLOps)**:
        * 資料科學團隊使用 Vertex AI Workbench 開發模型，透過 Vertex Pipelines 自動化訓練流程，將模型註冊到 Model Registry，最後部署到 Endpoint 並開啟 Model Monitoring 監控效能衰退。
        * A data science team uses Vertex AI Workbench to develop models, automates the training process via Vertex Pipelines, registers the model to the Model Registry, and finally deploys it to an Endpoint with Model Monitoring enabled to track performance degradation.

* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **整合性 (Consolidation)**: 在 PCA 考試中，Vertex AI 是「如何標準化 ML 工作流」與「解決模型訓練與預測環境不一致」的首選答案。
    * **Consolidation**: In the PCA exam, Vertex AI is the primary answer for "how to standardize ML workflows" and "solving discrepancies between model training and prediction environments."
    * **AutoML vs Custom**: Vertex AI 允許先嘗試 AutoML 快速驗證，若效果不足再轉為 Custom Training，且都在同一平台管理。
    * **AutoML vs Custom**: Vertex AI allows you to first try AutoML for rapid validation and switch to Custom Training if results are insufficient, all managed within the same platform.

---

### Cloud GPUs
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: 是 (Performance Efficiency - 硬體加速 / Hardware Acceleration)

* **產品重要說明 (Product Description)**:
    * Cloud GPUs 是可附加至 Compute Engine 虛擬機、GKE 節點等的 NVIDIA 硬體加速器。
    * Cloud GPUs are NVIDIA hardware accelerators that can be attached to Compute Engine instances, GKE nodes, and more.
    * 它們專為大規模數學運算設計，大幅加速深度學習訓練與推論、科學計算及圖形渲染。
    * They are designed for massive mathematical computations, significantly accelerating deep learning training and inference, scientific computing, and graphics rendering.

* **主要功能 (Main Functions)**:
    * **多種型號 (Variety of Models)**: 提供從經濟型 (T4) 到高效能型 (A100, V100) 的多種 NVIDIA GPU 選擇。
    * **Variety of Models**: Offers a range of NVIDIA GPU options from economical (T4) to high-performance (A100, V100).
    * **Passthrough 模式**: 讓虛擬機直接存取 GPU 硬體，減少虛擬化損耗。
    * **Passthrough Mode**: Allows VMs to directly access GPU hardware, minimizing virtualization overhead.

* **詳盡應用情境 (Detailed Scenarios)**:
    * **深度學習訓練 (Deep Learning Training)**:
        * 訓練複雜的 TensorFlow 圖像識別模型，使用搭載 NVIDIA V100 的 VM 可將時間從數天縮短至數小時。
        * Training a complex TensorFlow image recognition model; using a VM with NVIDIA V100s can reduce the time from days to hours.

* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **與 TPU 的選擇 (Choice vs TPU)**: GPU 通用性較高（支援所有 ML 框架及圖形處理）；TPU 則針對 TensorFlow/JAX 矩陣運算極致優化。若考試提到「需要渲染」或「自定義 CUDA 代碼」，必選 GPU。
    * **Choice vs TPU**: GPUs are more general-purpose (support all ML frameworks and graphics processing); TPUs are optimized for TensorFlow/JAX matrix operations. If the exam mentions "rendering" or "custom CUDA code," GPU is the required choice.
    * **驅動程式 (Drivers)**: 使用 GPU 需要在 VM 上安裝特定的 NVIDIA 驅動程式（或使用 Deep Learning Image）。
    * **Drivers**: Using GPUs requires installing specific NVIDIA drivers on the VM (or using a Deep Learning Image).

---

### Cloud TPU
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: 是 (Performance Efficiency - 專用 ASIC / Dedicated ASIC)

* **產品重要說明 (Product Description)**:
    * Cloud TPU (Tensor Processing Unit) 是 Google 專為機器學習工作負載設計的客製化 ASIC 晶片。
    * Cloud TPU (Tensor Processing Unit) is a custom ASIC chip designed by Google specifically for machine learning workloads.
    * 它們針對 TensorFlow (現也支援 PyTorch 和 JAX) 的矩陣運算進行了極致優化，提供極高的吞吐量。
    * They are highly optimized for matrix operations in TensorFlow (now also supporting PyTorch and JAX), offering extremely high throughput.

* **主要功能 (Main Functions)**:
    * **TPU Pods**: 可將數千個 TPU 晶片連接成超級電腦，平行處理超大規模模型訓練。
    * **TPU Pods**: Connect thousands of TPU chips into a supercomputer to process ultra-large-scale model training in parallel.
    * **低延遲推論 (Low Latency Inference)**: 適合需要極快回應速度的矩陣計算。
    * **Low Latency Inference**: Suitable for matrix calculations requiring extremely fast response times.

* **詳盡應用情境 (Detailed Scenarios)**:
    * **大規模模型訓練 (Large-scale Model Training)**:
        * 訓練類似 BERT 或 GPT 的大型語言模型，TPU Pod 能提供比傳統 GPU 叢集更高的性價比與速度。
        * Training large language models like BERT or GPT; TPU Pods can provide better cost-performance and speed compared to traditional GPU clusters.

* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **適用性 (Applicability)**: TPU 最適合高度平行化的大型矩陣運算。若工作負載含有大量非矩陣運算或自定義 C++ 操作，GPU 可能更適合。
    * **Applicability**: TPUs are best suited for highly parallel large matrix operations. If the workload contains many non-matrix operations or custom C++ ops, GPUs might be more suitable.
    * **區域性 (Zonal)**: TPU 是區域性資源。
    * **Zonal**: TPUs are zonal resources.

---

### TensorFlow Enterprise
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: 否

* **產品重要說明 (Product Description)**:
    * TensorFlow Enterprise 提供企業級的 TensorFlow 支援、優化與管理服務。
    * TensorFlow Enterprise provides enterprise-grade support, optimization, and management for TensorFlow.
    * 它確保了 TensorFlow 版本在 Google Cloud 上的穩定性與效能。
    * It ensures the stability and performance of TensorFlow versions on Google Cloud.

* **主要功能 (Main Functions)**:
    * **長期支援 (Long Term Support - LTS)**: 為特定 TensorFlow 版本提供長達 3 年的安全修補與錯誤修復（社群版通常僅 1 年）。
    * **Long Term Support (LTS)**: Provides up to 3 years of security patches and bug fixes for specific TensorFlow versions (Community edition is typically 1 year).
    * **雲端優化 (Cloud Optimization)**: 包含針對 GCP 硬體 (TPU/GPU) 與服務 (BigQuery/GCS) 優化的二進位檔。
    * **Cloud Optimization**: Includes binaries optimized for GCP hardware (TPU/GPU) and services (BigQuery/GCS).

* **詳盡應用情境 (Detailed Scenarios)**:
    * **關鍵任務系統 (Mission-critical Systems)**:
        * 銀行使用 TensorFlow 構建詐欺偵測系統，因合規需求不能頻繁升級軟體版本，因此選用 TensorFlow Enterprise 以獲得舊版本的長期安全維護。
        * A bank builds a fraud detection system using TensorFlow; due to compliance, they cannot frequently upgrade software versions, so they choose TensorFlow Enterprise to receive long-term security maintenance for older versions.

* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **無縫整合 (Seamless Integration)**: 它不是一個獨立的「產品」，而是 Deep Learning VM Images 和 Vertex AI 預建容器中的一個核心組件。
    * **Seamless Integration**: It is not a standalone "product" but a core component within Deep Learning VM Images and Vertex AI pre-built containers.

---

### BigQuery ML
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: 是 (Cost Optimization & Operational Excellence - 減少資料移動 / Reduce Data Movement)

* **產品重要說明 (Product Description)**:
    * BigQuery ML (BQML) 允許數據分析師使用標準 SQL 查詢在 BigQuery 中直接建立與執行機器學習模型。
    * BigQuery ML (BQML) allows data analysts to create and execute machine learning models directly within BigQuery using standard SQL queries.
    * 它消除了將數據匯出到外部 ML 訓練環境的繁瑣過程，實現了「數據原地分析」。
    * It eliminates the tedious process of exporting data to external ML training environments, enabling "in-place data analysis."

* **主要功能 (Main Functions)**:
    * **SQL 介面 (SQL Interface)**: 使用 `CREATE MODEL` 語句即可訓練模型，使用 `ML.PREDICT` 進行預測。
    * **SQL Interface**: Train models using `CREATE MODEL` statements and make predictions using `ML.PREDICT`.
    * **多種模型支援 (Diverse Model Support)**: 支援線性回歸 (Linear Regression)、邏輯回歸 (Logistic Regression)、K-means 分群、矩陣分解 (推薦系統)、時間序列預測 (ARIMA) 等。
    * **Diverse Model Support**: Supports Linear Regression, Logistic Regression, K-means Clustering, Matrix Factorization (Recommendation), Time Series (ARIMA), and more.

* **詳盡應用情境 (Detailed Scenarios)**:
    * **快速預測分析 (Rapid Predictive Analytics)**:
        * 行銷分析師想要預測下個月的客戶流失率，直接在現有的 BigQuery 用戶數據表上運行 SQL 建立邏輯回歸模型，無需請求資料科學家協助或搬移數據。
        * A marketing analyst wants to predict customer churn for the next month; they run SQL directly on existing BigQuery user tables to build a logistic regression model without needing data scientist assistance or moving data.

* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **適用對象 (Target Audience)**: 主要針對 SQL 分析師或需要快速基準測試 (Benchmarking) 的場景，而非需要高度客製化深度神經網絡的研究。
    * **Target Audience**: Primarily targets SQL analysts or scenarios requiring rapid benchmarking, rather than research requiring highly customized deep neural networks.
    * **模型匯出 (Model Export)**: 訓練好的模型可以匯出為 TensorFlow SavedModel 格式，以便在其他地方部署（如 Cloud Run）。
    * **Model Export**: Trained models can be exported as TensorFlow SavedModel format for deployment elsewhere (e.g., Cloud Run).

---

### Kubeflow Pipelines
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: 是 (Operational Excellence - 自動化與可重複性 / Automation and Reproducibility)

* **產品重要說明 (Product Description)**:
    * Kubeflow Pipelines 是一個基於 Docker 容器的平台，用於構建與部署可攜式、可擴展的機器學習工作流程 (Workflows)。
    * Kubeflow Pipelines is a platform based on Docker containers for building and deploying portable, scalable machine learning workflows.
    * 它源自開源 Kubeflow 專案，旨在解決 ML 實驗的可重複性與生產環境部署的複雜性。
    * Originating from the open-source Kubeflow project, it aims to solve the reproducibility of ML experiments and the complexity of production deployments.

* **主要功能 (Main Functions)**:
    * **工作流編排 (Workflow Orchestration)**: 將 ML 流程定義為有向無環圖 (DAG)，包含數據預處理、訓練、評估等步驟。
    * **Workflow Orchestration**: Define ML processes as Directed Acyclic Graphs (DAGs), including data preprocessing, training, evaluation, and more.
    * **組件重用 (Component Reusability)**: 每個步驟都是一個容器，可以被模組化並在不同管道中重複使用。
    * **Component Reusability**: Each step is a container that can be modularized and reused across different pipelines.

* **詳盡應用情境 (Detailed Scenarios)**:
    * **持續訓練 (Continuous Training - CT)**:
        * 當 GCS 中有新數據上傳時，自動觸發 Kubeflow Pipeline，執行數據清洗、模型再訓練、驗證準確率，若通過門檻則推送到生產環境。
        * When new data is uploaded to GCS, a Kubeflow Pipeline is automatically triggered to perform data cleaning, model retraining, and accuracy validation, pushing to production if thresholds are met.

* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Vertex AI Pipelines**: 在 GCP 上，通常建議使用託管版本的 Kubeflow Pipelines，即 **Vertex AI Pipelines**，以減少維運 Kubernetes 叢集的負擔。
    * **Vertex AI Pipelines**: On GCP, it is generally recommended to use the managed version of Kubeflow Pipelines, **Vertex AI Pipelines**, to reduce the operational overhead of managing Kubernetes clusters.
    * **可攜性 (Portability)**: 由於基於容器，Pipeline 可以輕鬆地從筆記本電腦遷移到地端叢集或雲端。
    * **Portability**: Being container-based, pipelines can be easily migrated from a laptop to an on-premise cluster or the cloud.

---

### Google Data Studio
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: 否 (視覺化工具 / Visualization Tool)

* **產品重要說明 (Product Description)**:
    * Google Data Studio (現已更名為 **Looker Studio**) 是一個免費的自助式商業智慧工具，用於將數據轉化為資訊豐富的儀表板與報告。
    * Google Data Studio (now rebranded as **Looker Studio**) is a free, self-service business intelligence tool used to turn data into informative dashboards and reports.
    * 它以易於使用、拖放式介面著稱，並能與 Google 生態系統（如 Google Analytics, BigQuery, Sheets）無縫整合。
    * It is known for its easy-to-use, drag-and-drop interface and seamless integration with the Google ecosystem (e.g., Google Analytics, BigQuery, Sheets).

* **主要功能 (Main Functions)**:
    * **即時連接器 (Live Connectors)**: 直接連接數據源（如 BigQuery），無需將數據複製到工具中，數據保持即時更新。
    * **Live Connectors**: Connect directly to data sources (like BigQuery) without copying data into the tool, keeping data up-to-date.
    * **協作 (Collaboration)**: 像編輯 Google Docs 一樣，允許多人同時查看與編輯報告。
    * **Collaboration**: Allows multiple people to view and edit reports simultaneously, just like editing Google Docs.

* **詳盡應用情境 (Detailed Scenarios)**:
    * **行銷成效報告 (Marketing Performance Report)**:
        * 行銷團隊將 Google Ads、Analytics 和 BigQuery 中的銷售數據整合到一個 Data Studio 頁面，供管理層隨時查看 ROI。
        * A marketing team integrates data from Google Ads, Analytics, and sales data in BigQuery into a single Data Studio page for management to view ROI at any time.

* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **快取 (Caching)**: 為了加速儀表板載入與減少 BigQuery 查詢費用，Data Studio 預設會使用 BI Engine 或內建快取層。
    * **Caching**: To speed up dashboard loading and reduce BigQuery query costs, Data Studio uses BI Engine or a built-in caching layer by default.
    * **定位 (Positioning)**: 適合快速、臨時性的分析或非技術人員的報表需求；與 Looker (企業級治理) 有所區隔。
    * **Positioning**: Suitable for quick, ad-hoc analysis or non-technical reporting needs; distinct from Looker (Enterprise-grade governance).

---

### Looker
* **Knowledge Level**: 1: basics
* **是否為 Google Cloud Well-Architected Framework 所採用的產品**: 是 (Operational Excellence - 數據驅動決策 / Data-driven Decision Making)

* **產品重要說明 (Product Description)**:
    * Looker 是一個現代化的企業級商業智慧與數據分析平台，透過其專有的建模語言 LookML 提供統一的數據定義。
    * Looker is a modern enterprise business intelligence and data analytics platform that provides unified data definitions through its proprietary modeling language, LookML.
    * 與傳統 BI 不同，Looker 直接在資料庫內 (In-database) 執行運算，利用底層資料庫（如 BigQuery）的效能。
    * Unlike traditional BI, Looker performs computations directly in-database, leveraging the performance of the underlying database (like BigQuery).

* **主要功能 (Main Functions)**:
    * **LookML (Looker Modeling Language)**: 一種語義層語言，用於定義業務邏輯（如「毛利」的計算公式），確保全公司指標一致。
    * **LookML (Looker Modeling Language)**: A semantic layer language used to define business logic (e.g., the formula for "Gross Margin"), ensuring consistent metrics across the company.
    * **嵌入式分析 (Embedded Analytics)**: 將報表或探索功能嵌入到外部應用程式或網站中。
    * **Embedded Analytics**: Embed reports or exploration capabilities into external applications or websites.

* **詳盡應用情境 (Detailed Scenarios)**:
    * **單一數據源 (Single Source of Truth)**:
        * 大型企業使用 Looker 定義所有 KPI，當財務部門與銷售部門查看「本季營收」時，因為底層都引用同一個 LookML 定義，所以數值絕對一致。
        * A large enterprise uses Looker to define all KPIs; when Finance and Sales departments view "Quarterly Revenue," the figures are identical because they both reference the same LookML definition.

* **詳盡關鍵知識 (Detailed Key Knowledge)**:
    * **Looker vs Data Studio**: 考試重點。Looker 強調 **治理 (Governance)** 與 **語義層 (Semantic Layer)**，適合企業級、需要嚴格數據定義的場景；Data Studio 強調 **靈活** 與 **免費**，適合個人或小團隊。
    * **Looker vs Data Studio**: Exam key point. Looker emphasizes **Governance** and **Semantic Layer**, suitable for enterprise-grade scenarios requiring strict data definitions; Data Studio emphasizes **Flexibility** and **Free** usage, suitable for individuals or small teams.
    * **不移動數據 (No Data Movement)**: Looker 不儲存數據，它將使用者操作轉換為 SQL 查詢傳送給 BigQuery 執行。
    * **No Data Movement**: Looker does not store data; it translates user actions into SQL queries sent to BigQuery for execution.

---