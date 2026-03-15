# 資安事件應變與鑑識基礎 / Security Incident Response & Forensics Basics

在資安領域，我們常說：「不是『如果』被駭，而是『何時』被駭」（It's not *if*, but *when*）。

本章節不談如何防止攻擊，而是聚焦於當防線被突破時，工程團隊如何有條理地**止血（Containment）**、**保存證據（Forensics）**並**恢復服務（Recovery）**。這是一套結合了「消防員」與「鑑識警探」的技能。

---

## Mental model｜心智模型

### 1. The "Crime Scene" Mindset（刑案現場思維）
當資安事件發生時（例如伺服器被植入挖礦程式），工程師的第一直覺通常是 `ssh` 進去然後 `rm -rf` 惡意檔案或直接重啟機器。
**這是錯誤的。**
將受駭系統視為「刑案現場」。任何未經規劃的操作（登入、刪除檔案、重啟）都會破壞「指紋」（記憶體殘留、檔案時間戳記、連線紀錄）。
*   **原則**：先隔離與快照（Snapshot），再進行分析與清理。

### 2. OODA Loop in Incident Response
應變過程是一個快速迭代的循環：
*   **Observe（觀察）**：監控告警、異常流量、Log。
*   **Orient（判斷）**：這是誤報（False Positive）還是真實攻擊？影響範圍多大？
*   **Decide（決策）**：要切斷網路？要停機維護？還是先觀察攻擊者行為？
*   **Act（行動）**：執行阻斷、修補或復原。

### 3. Containment vs. Eradication（圍堵 vs. 根除）
*   **圍堵（Containment）**：像是急救中的止血帶。目的是限制損害擴大（例如：切斷受駭主機的對外網路），即便這可能導致部分服務中斷。
*   **根除（Eradication）**：像是手術切除腫瘤。目的是徹底移除威脅（例如：修補漏洞、移除後門帳號）。
*   **關鍵決策**：不要為了急著根除而忽略了圍堵，導致攻擊者在修復期間橫向移動到其他系統。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. The "Kill Switch" Architecture（緊急煞車機制）
在系統設計階段，就預留「一鍵隔離」的能力。
*   **Feature Flags**：能瞬間關閉特定高風險功能（如檔案上傳、第三方 API 呼叫）。
*   **Revocation API**：能批次作廢特定 User ID 或 Session Token 的機制。
*   **Network Isolation**：在 Cloud 環境（AWS/GCP）預先設定好一個 "Quarantine Security Group"（隔離安全群組），該群組 Deny All Inbound/Outbound，只允許鑑識人員 IP 連入。一旦出事，直接將受駭實例（Instance）切換至此群組。

### 2. Immutable Forensics（不可變鑑識）
不要在「活體」生產環境上做深度分析。
*   **Snapshot First**：發現異常時，第一件事是對 Disk 和 Memory 進行快照。
*   **Analyze Offline**：將快照掛載到一個與生產環境隔離的「鑑識沙箱環境」中進行分析。
*   **Chain of Custody**：確保證據（Logs, Snapshots）的完整性，證明這些數據未被篡改（使用 Checksum/Hash）。

### 3. Structured Incident Roles（結構化應變角色）
不要讓所有人同時跳進去修 code，這會造成混亂。參考 Google SRE 或消防隊編制：
*   **Incident Commander (IC)**：總指揮。不做技術操作，只負責決策、協調與溝通。
*   **Ops Lead / Tech Lead**：負責執行具體操作（改設定、重啟、撈 Log）。
*   **Comms Lead**：負責對內（管理層）與對外（客戶、公關）的溝通，避免工程師被追問進度而分心。

### 4. The "5 Whys" Root Cause Analysis（根因分析）
事後檢討（Post-Mortem）不是為了找戰犯（Blameless），而是為了找出系統性缺失。
*   **現象**：資料庫被勒索。
*   **Why 1**：攻擊者取得了 DB Admin 權限。
*   **Why 2**：Admin 密碼被硬寫在程式碼中並推送到 GitHub。
*   **Why 3**：CI/CD 流程中沒有 Secret Scanning 機制。
*   **Why 4**：開發團隊缺乏憑證管理的安全意識培訓。
*   **Why 5**：公司沒有制定 Secrets Management 的標準規範。
*   **Action Item**：導入 Vault 並在 CI 流程加入 Gitleaks 掃描（而不僅僅是「修改密碼」）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Reboot Reflex"（反射性重啟）
*   **行為**：看到 Server 變慢或有怪 Process，直接 `reboot`。
*   **後果**：揮發性記憶體（RAM）中的證據（如無檔案惡意程式 Fileless Malware、解密後的金鑰、網路連線狀態）全部消失。
*   **修正**：先做 Memory Dump 或暫停（Pause/Suspend）虛擬機，而非重啟。

### 2. Alert Fatigue & The "Boy Who Cried Wolf"（告警疲勞）
*   **行為**：資安監控系統每天發送 500 封 "High Severity" 郵件，沒人看。
*   **後果**：真正的攻擊混在垃圾告警中被忽略。
*   **修正**：調校規則，區分「資訊（Info）」與「行動（Actionable）」層級。只有需要人為介入的事項才發送 Pager/Slack 通知。

### 3. Public Denial without Investigation（未經調查的否認）
*   **行為**：公關或高層在 Twitter/公告上說：「我們非常重視資安，目前沒有證據顯示資料外洩。」（但其實工程師根本還沒查完 Log）。
*   **後果**：幾天後被打臉，信譽破產。
*   **修正**：使用保守且精確的語言：「我們正在調查潛在的異常活動（We are investigating a potential anomaly）」，不輕易承諾未驗證的事實。

### 4. Analyzing on the Compromised Host（在受駭主機上分析）
*   **行為**：SSH 進去受駭主機，安裝 `tcpdump` 或 `htop` 進行除錯。
*   **後果**：攻擊者可能替換了系統指令（如 `ls`, `ps`），讓你看到假資訊；或者你的操作覆蓋了攻擊者的 `bash_history`。

---

## Checklists & workflows｜檢查清單與流程

這是一份針對工程師的 **First Responder Checklist（第一線應變清單）**。

### Phase 1: Identification & Triage (識別與檢傷)
- [ ] **驗證來源**：確認告警是否為誤報（False Positive）？（例如：是否剛好有壓力測試正在進行？）
- [ ] **評估範圍**：受影響的是單一 Container、整個 Cluster 還是資料庫？
- [ ] **建立 War Room**：開設專屬 Slack Channel / 會議室，拉入必要人員（IC, Tech Lead）。
- [ ] **開啟紀錄**：開始記錄時間軸（Timeline），幾點幾分做了什麼操作、觀察到什麼現象（這對事後檢討至關重要）。

### Phase 2: Containment (圍堵與隔離)
- [ ] **隔離受駭實體**：
    - 若是 AWS EC2：修改 Security Group (Deny All Inbound/Outbound)。
    - 若是 K8s Pod：NetworkPolicy 隔離或直接 Pause Container。
    - 若是帳號被盜：立即 Rotate API Key / Password，並強制登出所有 Sessions。
- [ ] **保存現場（Forensics Prep）**：
    - [ ] 建立 Disk Snapshot（標記為 Evidence，設定防刪除）。
    - [ ] 若環境允許，建立 Memory Dump。
    - [ ] 備份相關 Logs（Application logs, Load Balancer logs, Audit logs）至唯讀儲存桶。

### Phase 3: Eradication & Recovery (根除與復原)
- [ ] **識別入侵點**：確認攻擊者是如何進來的（漏洞？釣魚？弱密碼？）。
- [ ] **修補漏洞**：Patch 軟體、修改防火牆規則或更新程式碼。
- [ ] **清理環境**：
    - **不要**試圖清理受駭的伺服器並重新上線。
    - **應該**銷毀受駭伺服器，從乾淨的 Image/IaC 重新部署全新環境。
- [ ] **重設憑證**：假設環境中所有憑證（DB 密碼、AWS Keys）都已洩漏，全部輪替（Rotate）。
- [ ] **驗證復原**：確認新環境運作正常，且攻擊者無法再次利用同一漏洞。

### Phase 4: Post-Incident Activity (事後活動)
- [ ] **撰寫 Post-Mortem 報告**：包含時間軸、根因分析、改進項目。
- [ ] **更新 IRP**：根據這次經驗，優化 Incident Response Plan。

---

## Real-world examples｜實戰案例

### Scenario 1: AWS Access Key Leaked on GitHub
**情境**：開發者不小心將 AWS `admin` 權限的 Access Key 推送到公開 Repo。15 分鐘後，Billing 告警顯示開了 50 台 `x1.32xlarge` 機器挖礦。

**應變流程**：
1.  **Containment**:
    *   **不要**只是刪除 GitHub 上的 code（歷史紀錄還在）。
    *   立即在 AWS IAM Console 將該 User 的 Policy 設為 `DenyAll` 或直接 Deactivate Key。
    *   撤銷該 User 的所有 Active Sessions。
2.  **Investigation**:
    *   查詢 CloudTrail Logs，搜尋該 Key ID 在洩漏期間的所有 API 呼叫。
    *   確認除了開機器外，是否建立了新的 IAM User？是否修改了 S3 Bucket Policy？是否建立了後門 Security Group？
3.  **Remediation**:
    *   Terminate 所有異常 EC2 實例。
    *   刪除攻擊者建立的任何資源。
    *   使用 `git filter-branch` 或 BFG Repo-Cleaner 清理 Git 歷史紀錄，或直接刪除 Repo 重建。

### Scenario 2: Ransomware in Database
**情境**：應用程式報錯，檢查 DB 發現資料表被清空，只留下一張 `READ_ME` 表格要求支付比特幣。

**應變流程**：
1.  **Containment**:
    *   立即切斷 DB 對外連線（除了維運 VPN）。
    *   檢查 Web Server 是否也被入侵（通常 DB 不會直接暴露，是透過 Web App SQL Injection 或 Web Shell 進來的）。
2.  **Forensics**:
    *   檢查 DB Access Logs，找出攻擊者 IP 與執行的 SQL 指令。
    *   檢查 Web Server Logs，找出對應時間點的 HTTP Request（尋找 SQL Injection 特徵）。
3.  **Recovery**:
    *   **不要支付贖金**（無法保證資料能拿回）。
    *   檢查備份檔（Backups）的完整性，確保備份檔沒有被加密或刪除。
    *   找出並修補 SQL Injection 漏洞。
    *   從乾淨的備份還原資料庫到新的實例。

### Scenario 3: Supply Chain Attack (e.g., Malicious npm package)
**情境**：CI/CD Pipeline 突然失敗，或者 Build 出來的 Image 包含異常連線行為。發現依賴的 npm 套件被惡意更新。

**應變流程**：
1.  **Identification**:
    *   比對 `package-lock.json` 或 `yarn.lock`，確認依賴版本變更。
    *   使用 `npm audit` 或 Snyk 等工具確認漏洞情報。
2.  **Containment**:
    *   鎖定依賴版本（Pin version）到已知的安全版本。
    *   檢查是否有任何由該惡意版本 Build 出來的 Artifacts 已經部署到 Production。
3.  **Remediation**:
    *   若已部署，立即 Rollback 到上一個安全版本。
    *   因為惡意套件可能在 Build 階段竊取 ENV 中的 Secrets，**必須視為所有 Build Time Secrets 已洩漏**，進行全面輪替。