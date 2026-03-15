# 合規標準與審計日誌設計 / Compliance Standards & Audit Log Design

## Mental model｜心智模型

### 1. 審計日誌是「數位黑盒子」 (The Digital Flight Recorder)
不要將審計日誌（Audit Logs）視為一般的應用程式日誌（Application Logs）。
- **Application Logs** 是給開發者看的，目的是 **Debugging**（除錯），關注的是「程式碼為何崩潰」。
- **Audit Logs** 是給稽核員與資安官看的，目的是 **Accountability**（問責）與 **Non-repudiation**（不可否認性），關注的是「誰在什麼時候對什麼資料做了什麼」。

### 2. 合規是「業務風險的可觀測性」 (Observability for Business Risk)
GDPR、SOC2 或 ISO 27001 並非單純的文書作業，而是要求系統具備「證明自身清白」的能力。
- **GDPR**: 重點在於 PII（個人識別資訊）的生命週期與存取權限（Right to be forgotten, Data minimization）。
- **SOC2 / ISO 27001**: 重點在於變更管理（Change Management）與安全性監控（Security Monitoring）。

### 3. 核心結構：The 5 Ws + 1 H
每一條有效的 Audit Log 必須回答以下問題：
- **Who**: 誰觸發了動作？（User ID, Service Account, IP Address）
- **What**: 做了什麼動作？（Action: Create, Update, Delete, Export）
- **Where**: 對哪個資源操作？（Resource ID, Endpoint）
- **When**: 確切時間點？（UTC Timestamp with high precision）
- **Why**: 授權依據是什麼？（Role, Scope, Reason text）
- **How**: 操作結果與狀態？（Success/Failure, Status Code, Diff）

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 結構化日誌與上下文傳遞 (Structured Logging & Context Propagation)
絕對不要使用字串拼接（String Concatenation）來記錄審計日誌。必須使用 JSON 格式，並確保欄位schema 統一。
- **Pattern**: 在 API Gateway 或 Middleware 層級生成唯一的 `TraceID` 或 `RequestID`，並將其貫穿整個 Request Lifecycle。
- **Best Practice**: 記錄「變更前後的差異（Diff）」，而不僅僅是「發生了變更」。
  - *Good*: `{"field": "role", "old_value": "viewer", "new_value": "admin"}`
  - *Bad*: `User updated role.`

### 2. 非同步寫入與獨立儲存 (Async Write & Segregated Storage)
審計日誌的寫入不應阻塞主業務邏輯（Main Thread），且不應與業務資料庫混用。
- **Pattern**: 使用 **Sidecar 模式** 或 **Message Queue** (如 Kafka, SQS) 將審計事件非同步送出。
- **Best Practice**: 審計日誌應寫入 **WORM (Write Once, Read Many)** 儲存介質（如 AWS S3 Object Lock, Append-only Database），確保即便是系統管理員也無法輕易竄改或刪除歷史紀錄。

### 3. 敏感資料脫敏 (Data Masking & Redaction)
合規的矛盾點在於：為了記錄操作，你可能會不小心記錄下敏感資料（PII/Secrets）。
- **Pattern**: 在日誌寫入前實施 **Filter/Sanitizer**。
- **Best Practice**:
  - 密碼、API Key：完全過濾或僅留 Hash/前幾碼。
  - PII（Email, Phone）：根據需求進行 Masking（如 `j***@example.com`）。
  - **由應用層處理脫敏**，不要依賴日誌收集端處理（避免原始數據洩漏在傳輸過程中）。

### 4. 讀取操作的選擇性記錄 (Selective Read Logging)
記錄所有的 `READ` 操作會造成巨大的雜訊與儲存成本。
- **Strategy**:
  - **一般資料**：僅記錄 `WRITE/UPDATE/DELETE`。
  - **敏感資料**（如病歷、信用卡號、薪資單）：必須記錄 `READ` 操作（誰看過這筆資料？）。
  - **批量導出**：必須記錄 `EXPORT` 操作。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 混合日誌流 (The "Mixed Stream" Trap)
- **Anti-pattern**: 將 Audit Logs 和 Debug Logs 輸出到同一個 `stdout` 或同一個 Log Group。
- **Consequence**: Log retention policy 衝突（Debug log 留 7 天，Audit log 需留 1-7 年），且稽核時難以檢索，增加合規成本。

### 2. 缺乏身分上下文 (The "System User" Fallacy)
- **Anti-pattern**: 在後端微服務調用時，Audit Log 只記錄了 `service-account` 而丟失了原始觸發的 `human-user-id`。
- **Consequence**: 無法追溯到具體操作人員，違反 SOC2 的 Non-repudiation 要求。
- **Fix**: 務必透過 JWT 或 Context 傳遞 `X-Original-User-ID`。

### 3. 記錄過多或過少 (The Goldilocks Dilemma)
- **Too Much**: 記錄完整的 HTTP Request Body。
  - *Risk*: 極高機率洩漏 PII 或 Secrets。
- **Too Little**: 只記錄 "Something happened"。
  - *Risk*: 發生資安事件時，無法知道攻擊者改了什麼參數。

### 4. 本地儲存 (Local Storage Reliance)
- **Anti-pattern**: 將 Audit Logs 寫在 Container 內部的檔案系統。
- **Consequence**: Container 重啟或被駭客入侵刪除後，證據永久消失。

---

## Checklists & workflows｜檢查清單與流程

### Design Phase: Audit Log Schema Definition
- [ ] **Identity**: 是否包含 `User ID`, `IP Address`, `User Agent`, `Session ID`?
- [ ] **Resource**: 是否明確標示受影響的 `Resource ID` 與 `Resource Type`?
- [ ] **Action**: 動作動詞是否標準化（e.g., 使用 `create`, `delete` 而非混用 `add`, `remove`）?
- [ ] **Outcome**: 是否包含 `Status` (Success/Failure) 與 `Error Code`?
- [ ] **Timestamp**: 是否使用 ISO 8601 UTC 格式?

### Implementation Phase: Security & Privacy
- [ ] **Immutability**: 儲存層是否開啟了 Object Lock 或 Append-only 模式?
- [ ] **Sanitization**: 是否已測試過濾器，確保 Password, Token, Credit Card Number 不會被寫入?
- [ ] **Retention**: 是否設定了自動生命週期管理（e.g., Hot storage 3 個月, Cold storage 1 年, Archive 7 年）?
- [ ] **Alerting**: 針對高風險操作（如「刪除審計日誌」、「授權變更」）是否設定了即時告警?

### Compliance Check (GDPR/SOC2 Mapping)
- [ ] **Right to Access**: 能否透過 User ID 快速檢索該用戶的所有操作紀錄?
- [ ] **Data Integrity**: 是否有機制檢測日誌是否被竄改（如 Checksum 或 Hash Chain）?

---

## Real-world examples｜實戰案例

### Scenario: Admin User Changing Permissions
情境：一名管理員將某個使用者的權限從 `Viewer` 提升為 `Editor`。

#### Bad Audit Log (Anti-pattern)
```json
// 缺乏細節，無法知道改了什麼，也不確定是誰改的（只顯示 admin）
{
  "level": "INFO",
  "msg": "Update user permission success",
  "time": "2023-10-12 10:00:00"
}
```

#### Good Audit Log (Best Practice)
```json
{
  "event_id": "evt_88392019",
  "trace_id": "trc_xyz789",
  "timestamp": "2023-10-12T10:00:00.123Z",
  "actor": {
    "id": "usr_admin_01",
    "ip": "203.0.113.1",
    "role": "super_admin",
    "user_agent": "Mozilla/5.0..."
  },
  "action": {
    "type": "iam.role.update",
    "category": "security_modification",
    "outcome": "success"
  },
  "target": {
    "resource_type": "user",
    "resource_id": "usr_target_99"
  },
  "changes": {
    "attribute": "access_level",
    "old_value": "viewer",
    "new_value": "editor"
  },
  "metadata": {
    "reason": "Ticket-1234 approval"
  }
}
```

### Architecture: Tamper-Evident Logging Pipeline

1.  **App Service**: 產生結構化 Log Event，發送至 **Kafka** (Topic: `audit-events`)。
2.  **Audit Consumer**: 訂閱 Kafka，進行格式驗證與 PII 再次檢查。
3.  **Storage (Hot)**: 寫入 **Elasticsearch/OpenSearch** (供 90 天內快速查詢、Dashboard 監控)。
4.  **Storage (Cold/Archive)**: 透過 Firehose 寫入 **AWS S3**。
    - 啟用 **S3 Object Lock (Compliance Mode)**：設定 365 天內不可刪除/覆寫。
    - 啟用 **S3 Server Access Logging**：監控誰存取了這些 Log 檔案。
5.  **Alerting**: 若偵測到 `action.type = "audit_log.delete"` 或 `actor.role = "admin"` 的異常頻率，觸發 PagerDuty。