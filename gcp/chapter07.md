# 1. 前言與學習目標 (Introduction & Learning Objectives)

在雲端架構演進到 Senior 階段時，資安不再只是「防火牆規則」或「IAM 權限設定」，而是必須建立一套**縱深防禦（Defense in Depth）**體系。對於大型企業或受監管產業（FinTech, Healthcare），單點防護失效是不可接受的風險。本章將聚焦於 GCP 特有的高階資安組件，教你如何防止資料外洩、抵禦外部攻擊並管理敏感憑證。

As cloud architecture evolves to a Senior level, security is no longer just about "firewall rules" or "IAM permissions"; it requires establishing a **Defense in Depth** strategy. For large enterprises or regulated industries (FinTech, Healthcare), single-point failure in security is an unacceptable risk. This chapter focuses on GCP-specific high-level security components, teaching you how to prevent data exfiltration, mitigate external attacks, and manage sensitive credentials.

**完成本章後，你將能夠：**
**After completing this chapter, you will be able to:**

1.  **實作縱深防禦架構**：整合 Cloud Armor（邊緣防護）、VPC Service Controls（資料邊界）與 KMS（資料加密）。
    **Implement Defense in Depth:** Integrate Cloud Armor (Edge Security), VPC Service Controls (Data Perimeter), and KMS (Data Encryption).
2.  **區分並正確使用 KMS 與 Secret Manager**：理解何時該加密資料（Encryption），何時該儲存機密字串（Secrets），並實作自動化輪替（Rotation）。
    **Distinguish and correctly use KMS vs. Secret Manager:** Understand when to encrypt data versus when to store secret strings, and implement automated rotation.
3.  **設計防範資料外洩（Data Exfiltration）的機制**：利用 VPC Service Controls 建立受保護的服務邊界，即使 IAM 憑證洩漏也能阻擋未授權存取。
    **Design mechanisms to prevent Data Exfiltration:** Use VPC Service Controls to create protected service perimeters that block unauthorized access even if IAM credentials are compromised.
4.  **應對 DDoS 與應用層攻擊**：配置 Cloud Armor 安全策略以保護後端負載平衡器。
    **Mitigate DDoS and Application Layer attacks:** Configure Cloud Armor security policies to protect backend load balancers.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

### 2.1 縱深防禦 (Defense in Depth)

想像一座城堡：Cloud Armor 是護城河與城門（過濾外部流量）；VPC Service Controls 是城堡內部的隔離區（防止間諜把機密帶出去）；IAM 是身分識別證；KMS 與 Secret Manager 則是保險箱的鑰匙與密碼。

Imagine a castle: Cloud Armor is the moat and the gate (filtering external traffic); VPC Service Controls are the quarantine zones inside the castle (preventing spies from taking secrets out); IAM is the ID badge; KMS and Secret Manager are the keys and combinations to the safes.

### 2.2 VPC Service Controls (VPC SC)

這是 GCP 獨有且最強大的資安功能之一，也是 AWS 使用者最容易混淆的概念。
This is one of GCP's most unique and powerful security features, and often the most confusing for AWS users.

*   **定義 (Definition)**：VPC SC 在 Google 託管服務（如 BigQuery, Cloud Storage, SQL）周圍建立一個邏輯邊界（Perimeter）。
    VPC SC creates a logical perimeter around Google-managed services (like BigQuery, Cloud Storage, SQL).
*   **關鍵差異 (Key Differentiator)**：防火牆控制的是 IP 封包；VPC SC 控制的是 **API 請求的上下文 (Context)**。即使攻擊者偷到了擁有權限的 Service Account Key，如果他不在受信任的網路邊界內（例如公司 VPN 或特定 VPC），VPC SC 會直接拒絕請求。
    Firewalls control IP packets; VPC SC controls the **context of API requests**. Even if an attacker steals a privileged Service Account Key, if they are not within the trusted network perimeter (e.g., corporate VPN or specific VPC), VPC SC will deny the request outright.

### 2.3 KMS vs. Secret Manager

資深工程師必須清楚區分這兩者的用途，避免將 API Key 寫入 KMS，或試圖用 Secret Manager 加密大量資料。
Senior engineers must clearly distinguish between these two, avoiding putting API Keys into KMS or trying to encrypt large datasets with Secret Manager.

| Feature | Cloud KMS | Secret Manager |
| :--- | :--- | :--- |
| **主要用途 (Primary Use)** | 加密/解密資料加密金鑰 (DEK) 或少量資料 | 儲存與管理機密字串 (API Keys, DB Passwords) |
| **操作對象 (Operates On)** | Cryptographic Keys (Symmetric/Asymmetric) | Secret Versions (Strings/Binaries) |
| **典型場景 (Scenario)** | Database Encryption (CMEK), Signing JWTs | Injecting DB creds into Kubernetes Pods |
| **AWS 對應 (AWS Equivalent)** | AWS KMS | AWS Secrets Manager / Parameter Store |

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在系統設計面試或 Production 環境規劃中，我們通常會將這些組件置入一個高合規性的架構中。

In system design interviews or production planning, we typically place these components into a high-compliance architecture.

### 3.1 架構圖概念描述 (Architecture Concept)

一個處理 PII (Personally Identifiable Information) 的典型架構：

A typical architecture handling PII (Personally Identifiable Information):

1.  **Edge Layer**: Global External Load Balancer 綁定 **Cloud Armor**。
    *   *作用*：阻擋 SQL Injection, XSS, 以及來自惡意 IP 的流量。
2.  **Compute Layer**: GKE Cluster 位於 Private VPC。
    *   *作用*：應用程式邏輯運行處。
3.  **Data Layer**: Cloud SQL 與 Cloud Storage。
    *   *Security*: 資料使用 **CMEK (Customer-Managed Encryption Keys)** 透過 **Cloud KMS** 進行加密，而非預設的 Google-managed keys。這讓你有權隨時撤銷金鑰存取權（Crypto-shredding）。
4.  **Credential Management**: 應用程式啟動時，從 **Secret Manager** 讀取 DB 密碼，而非從環境變數（Environment Variables）讀取。
5.  **Perimeter**: 整個專案被包在 **VPC Service Controls** 邊界內。
    *   *作用*：防止內鬼或被駭的 VM 將資料 `gsutil cp` 到外部的 Bucket。

### 3.2 對系統屬性的影響 (Impact on System Attributes)

*   **可靠性 (Reliability)**: VPC SC 配置錯誤會導致「自我阻斷服務 (Self-DoS)」，這是常見的 outage 原因。Secret Manager 的存取失敗會導致服務無法啟動。
    Misconfiguration of VPC SC can lead to "Self-DoS," a common cause of outages. Failure to access Secret Manager will prevent services from starting.
*   **效能 (Performance)**: Cloud Armor 在邊緣處理，對延遲影響極小。KMS 加密通常有硬體加速，但大量小檔案加密可能會產生 API 延遲與成本。
    Cloud Armor processes at the edge with minimal latency impact. KMS encryption is usually hardware-accelerated, but encrypting massive amounts of small files can incur API latency and costs.

---

# 4. 逐步示例 (Walkthrough / Example)

我們將重點放在 **Secret Manager 的正確整合** 與 **VPC Service Controls 的除錯**，這是實作中最常遇到的挑戰。

We will focus on the **correct integration of Secret Manager** and **debugging VPC Service Controls**, as these are the most common challenges in implementation.

### 4.1 使用 Secret Manager 取代環境變數 (Replacing Env Vars with Secret Manager)

許多團隊習慣將密碼放在 Kubernetes ConfigMap 或 `.env` 檔，這在資安稽核中是不合格的。

Many teams are used to putting passwords in Kubernetes ConfigMaps or `.env` files, which fails security audits.

**Python 範例 (Python Example):**

```python
from google.cloud import secretmanager
import os

def get_db_password(project_id, secret_id, version_id="latest"):
    """
    從 Secret Manager 獲取機密，而非依賴 os.environ
    Fetches secret from Secret Manager instead of relying on os.environ
    """
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    try:
        response = client.access_secret_version(request={"name": name})
        payload = response.payload.data.decode("UTF-8")
        return payload
    except Exception as e:
        # 在 Production 中，這裡應該有嚴謹的 Error Handling 與 Alerting
        # In Production, rigorous Error Handling and Alerting should be here
        print(f"Failed to access secret: {e}")
        raise

# Usage
# DB_PASSWORD = get_db_password("my-gcp-project", "prod-db-pass")
```

**實務考量 (Practical Considerations):**
*   **Caching**: 為了效能與成本，不要在每個 Request 都呼叫 Secret Manager API。應該在應用程式啟動時讀取並快取，或實作定期重新讀取（以支援 Rotation）。
    **Caching:** For performance and cost, do not call the Secret Manager API on every request. Read and cache it at application startup, or implement periodic re-reading (to support Rotation).

### 4.2 設定 VPC Service Controls 與除錯 (Setting up VPC SC & Debugging)

設定 VPC SC 最怕的是「阻擋了合法流量」。

The biggest fear when setting up VPC SC is "blocking legitimate traffic."

**情境 (Scenario)**: 你設定了 Perimeter 保護 BigQuery，但你的 CI/CD Pipeline (跑在 Cloud Build 上) 突然無法部署資料了。

**除錯步驟 (Debugging Steps)**:

1.  **不要盲目猜測 (Don't Guess)**: VPC SC 的錯誤訊息通常很模糊（例如 `403 Forbidden`），不會直接告訴你是因為 Perimeter。
    VPC SC error messages are often vague (e.g., `403 Forbidden`) and won't explicitly tell you it's due to the Perimeter.
2.  **檢查 Audit Logs (Check Audit Logs)**:
    前往 Cloud Logging，使用以下過濾器：
    Go to Cloud Logging and use the following filter:
    ```text
    protoPayload.metadata.@type="type.googleapis.com/google.cloud.audit.VpcServiceControlAuditMetadata"
    severity=ERROR
    ```
3.  **分析違規類型 (Analyze Violation Type)**:
    *   `NO_MATCHING_ACCESS_LEVEL`: 來源 IP 或身分不在允許清單內。
    *   `RESOURCES_NOT_IN_SAME_SERVICE_PERIMETER`: 試圖跨越兩個不同的邊界存取資源。
4.  **解決方案 (Solution)**:
    *   為 Cloud Build 的 Service Account 建立 **Ingress Rule**。
    *   或者將 Cloud Build 的專案加入同一個 Perimeter。

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

### 5.1 濫用 Owner 權限繞過資安 (Abusing Owner Permissions to Bypass Security)
*   **錯誤 (Mistake)**: 因為 VPC SC 或 KMS 權限設定太複雜，開發者直接給予 Service Account `Editor` 或 `Owner` 權限。
    Because VPC SC or KMS permissions are too complex, developers directly grant `Editor` or `Owner` permissions to Service Accounts.
*   **後果 (Consequence)**: 違反最小權限原則（Least Privilege）。如果該 Key 洩漏，攻擊者擁有整個專案的控制權。
    Violates the Principle of Least Privilege. If that Key is compromised, the attacker has control over the entire project.
*   **修正 (Fix)**: 使用 Granular Roles（如 `roles/cloudkms.cryptoKeyEncrypterDecrypter`）。

### 5.2 忽略 Secret Rotation (Ignoring Secret Rotation)
*   **錯誤 (Mistake)**: 使用 Secret Manager 但從不輪替密碼。
    Using Secret Manager but never rotating passwords.
*   **後果 (Consequence)**: 靜態密碼一旦洩漏，威脅是永久的。
    Once a static password is leaked, the threat is permanent.
*   **修正 (Fix)**: 設定 Secret Manager 的 Rotation Schedule，並配合 Cloud Functions 自動更新資料庫密碼。

### 5.3 誤解 Cloud Armor 的範圍 (Misunderstanding Cloud Armor Scope)
*   **錯誤 (Mistake)**: 以為 Cloud Armor 可以保護 VM 的所有 Port。
    Thinking Cloud Armor protects all ports on a VM.
*   **事實 (Fact)**: Cloud Armor 主要掛載於 **Load Balancer** 上，針對 HTTP/HTTPS 流量。對於直接針對 VM IP 的 SSH 暴力破解，Cloud Armor 無法防護（需依賴 Firewall Rules 或 IAP）。
    Cloud Armor is primarily attached to **Load Balancers** for HTTP/HTTPS traffic. It cannot protect against SSH brute force attacks directly targeting VM IPs (rely on Firewall Rules or IAP for that).

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

### Q1: 如何設計一個系統，確保即使 Google 的 SRE 也無法讀取你的資料？
**How would you design a system to ensure that even Google SREs cannot read your data?**

*   **高分回答要點 (Key Points)**:
    *   提及 **CMEK (Customer-Managed Encryption Keys)**：金鑰由客戶控制。
    *   進階：提及 **Cloud EKM (External Key Manager)**，金鑰儲存在 GCP 之外（如地端 HSM 或 AWS KMS），GCP 僅在運算時暫時請求解密。
    *   提及 **Key Access Justifications**：每次 Google 人員試圖存取金鑰時，需提供理由並由政策決定是否放行。

### Q2: 我們需要在不更動程式碼的情況下，防止敏感資料（如信用卡號）被寫入 Logs。你會怎麼做？
**We need to prevent sensitive data (like credit card numbers) from being written to Logs without changing the application code. What would you do?**

*   **高分回答要點 (Key Points)**:
    *   使用 **Cloud DLP (Data Loss Prevention)** API。
    *   在 Logging 的 Sink 處整合 DLP 進行去識別化（De-identification）或遮罩（Masking）。
    *   雖然這不是本章重點（Cloud Armor/KMS），但這是 Cloud Security 的常見延伸題，展示你對 GCP 資安生態系的廣度認知。

### Q3: 什麼是 "Break Glass" 機制？在 VPC Service Controls 中如何規劃？
**What is a "Break Glass" mechanism? How do you plan for it in VPC Service Controls?**

*   **高分回答要點 (Key Points)**:
    *   當 VPC SC 設定錯誤導致所有自動化流程鎖死時，需要一個緊急通道。
    *   設計一個特殊的 Service Account 或 Group，被排除在限制之外（Excluded from access levels），但平時監控極其嚴格，僅在緊急事故（Incident）時啟用並觸發高層級警報。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

### 本章記憶錨點 (Key Takeaways)
1.  **縱深防禦 (Defense in Depth)** 是雲端資安的黃金標準，單靠防火牆是不夠的。
2.  **Cloud Armor** 負責邊緣防護（WAF/DDoS），保護 Load Balancer。
3.  **VPC Service Controls** 提供了「情境感知」的邊界防護，防止資料外洩（Data Exfiltration）。
4.  **Secret Manager** 用於憑證管理與輪替；**KMS** 用於資料加密（CMEK）。
5.  永遠透過 **Audit Logs** 來除錯 VPC SC 的 `403` 錯誤。

### 後續延伸 (Next Steps)
*   **實作 (Practice)**: 試著在一個 GKE 專案中啟用 VPC Service Controls，並觀察它如何阻擋你的 `kubectl` 或 `gcloud` 指令，然後修復它。
*   **下一章預告 (Next Chapter)**: 掌握了資安後，我們將進入 **Chapter 08: 可觀測性與除錯 (Observability & Debugging)**，學習如何使用 Cloud Operations Suite (Stackdriver) 監控這些複雜的系統。