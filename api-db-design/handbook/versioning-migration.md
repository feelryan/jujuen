# 版本控制與無停機遷移指南 / Versioning & Zero-Downtime Migration Guide

## Mental model｜心智模型

在處理 API 版本與資料庫遷移時，最核心的心智模型是 **「並行宇宙與合約管理」（Parallel Universes & Contract Management）**。

### 1. API 是「合約」（The Contract）
API 版本控制不僅是改網址，而是對客戶端的一種承諾。
- **Breaking Change (違約)**：當你改變了回應格式、移除了欄位，導致舊的客戶端程式崩潰。這時必須建立新的合約（新版本）。
- **Non-breaking Change (補充條款)**：新增欄位或端點，舊客戶端忽略即可，不需要新版本。

### 2. 資料庫遷移是「行駛中換輪胎」（Changing Tires on a Moving Car）
在 Production 環境，你不能暫停服務來修改資料庫結構。
- **Expand and Contract (擴充與收縮)**：這是無停機遷移的黃金法則。永遠不要「修改」現有的東西，而是先「新增」新的結構，讓舊新並存，最後才「移除」舊的。
- **Decoupling Deployment from Release (部署與發布解耦)**：資料庫的變更（Schema Change）與程式碼的變更（Code Deployment）必須是解耦的，且通常資料庫變更要先行。

---

## Patterns & best practices｜常見模式與最佳實務

### API Versioning Strategies｜API 版本控制策略

在實戰中，主要有兩種主流派別，選擇哪種取決於你的客戶端類型：

#### 1. URI Versioning (The Pragmatist's Choice)
將版本號直接放在 URL 路徑中。
- **Format**: `GET /v1/users/123`
- **Pros**:
  - **極度直觀**：開發者一眼就知道在用哪個版本。
  - **易於快取**：CDN 和瀏覽器可以輕鬆根據 URL 進行快取。
  - **瀏覽器友善**：可以直接在瀏覽器網址列測試。
- **Cons**: 破壞了 REST 的資源恆定性原則（同一個 User 有兩個 URL）。
- **Best for**: **Public APIs**、對外開放的服務（如 Stripe, Twitter）。

#### 2. Header / Media Type Versioning (The Purist's Choice)
利用 HTTP Header 來指定版本。
- **Format**:
  - Custom Header: `Accept-Version: v1`
  - Content Negotiation: `Accept: application/vnd.mycompany.v1+json`
- **Pros**: URL 保持乾淨，符合 REST 精神（資源只有一個 URI）。
- **Cons**: 難以透過瀏覽器直接測試，Cache 設定較複雜（需設定 `Vary` header）。
- **Best for**: **Internal Microservices**、完全由你控制的 Mobile App。

### Zero-Downtime DB Migration (Parallel Change Pattern)

要在不鎖表、不中斷服務的情況下修改 Schema（例如：將 `name` 欄位拆分為 `first_name` 和 `last_name`），必須遵循 **四階段模式**：

1.  **Phase 1: Expand (新增)**
    - 在 DB 中新增 `first_name` 和 `last_name` 欄位（設為 Nullable）。
    - **此時程式碼行為**：完全不讀寫新欄位，服務正常運作。

2.  **Phase 2: Dual Write (雙寫)**
    - 更新程式碼：寫入時同時寫入舊欄位 (`name`) 與新欄位 (`first_name`, `last_name`)。讀取時仍讀舊欄位。
    - **Backfill (回填)**：執行背景腳本，將歷史資料從 `name` 解析並填入新欄位。

3.  **Phase 3: Switch Read (切換讀取)**
    - 確認資料一致後，更新程式碼：讀取時改讀新欄位。寫入時仍保持雙寫（為了安全回滾）。
    - 觀察一段時間，確認無誤後，停止寫入舊欄位。

4.  **Phase 4: Contract (收縮)**
    - 移除程式碼中對舊欄位的參照。
    - 在 DB 中移除舊欄位 `name`（或標記為 deprecated）。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### API Anti-patterns
- **The "Big Bang" Release**: 強制所有客戶端在同一時間升級。這在 Mobile App 世界是不可能的，因為使用者不一定會更新 App。
- **Versioning for Additive Changes**: 只是加了一個新欄位就升級到 `v2`。這會造成版本號通膨，增加維護成本。只有 Breaking Change 才需要升版。
- **Business Logic in Routing**: 在 Gateway 層寫死 `if v1 go to Service A, if v2 go to Service B`，導致版本邏輯洩漏到基礎設施層。

### Database Migration Pitfalls
- **Renaming Columns Directly**: `ALTER TABLE users RENAME COLUMN name TO full_name;`
  - **後果**：部署期間，舊程式碼還在找 `name`，新程式碼找 `full_name`。無論先部署 DB 還是先部署 Code，都會導致服務中斷 (Downtime)。
- **Adding Default Values to Large Tables**: 在舊版 MySQL/Postgres 中，對大表新增帶有 `DEFAULT` 值的欄位會鎖表（Lock Table）並重寫整張表。
  - **解法**：新增 Nullable 欄位 -> 程式碼層處理 Default -> 背景更新舊資料 -> 最後設為 Not Null。
- **Ignoring Lock Timeouts**: Migration script 沒有設定 `lock_timeout`。如果由 CI/CD 自動執行，可能會因為等待鎖定而卡住整個部署 Pipeline，甚至導致 Production 資料庫連線堆積。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Breaking Change Handling

1.  **是 Breaking Change 嗎？**
    - No (新增欄位) -> 直接修改 Serializer/DTO，不升版。
    - Yes (移除/改名/改變型別) -> 進入下一步。
2.  **能透過「寬容讀取 (Tolerant Reader)」解決嗎？**
    - Yes (例如舊客戶端送 string，新版能 parse 成 int) -> 在程式碼層相容，不升版。
    - No -> **必須建立新版本 (vNext)**。

### Zero-Downtime Migration Checklist

在執行 Schema 變更前，請勾選以下項目：

- [ ] **Backward Compatibility**: 新增的欄位是否允許 `NULL`？（除非表是空的，否則不能直接加 `NOT NULL`）。
- [ ] **Locking Strategy**: 針對 PostgreSQL，是否使用了 `CREATE INDEX CONCURRENTLY`？針對大表修改，是否評估了鎖表時間？
- [ ] **Dual Write Logic**: 程式碼是否已實作「雙寫」邏輯？
- [ ] **Backfill Plan**: 是否有腳本遷移歷史資料？腳本是否會造成 DB 負載過高（應分批次執行）？
- [ ] **Rollback Plan**: 如果新欄位有問題，能否僅透過 Revert Code 恢復（而不需回滾 DB）？
- [ ] **Deprecation Policy**: 舊版本的 API 是否已加上 `Deprecation` 或 `Sunset` header 通知客戶端？

---

## Real-world examples｜實戰案例

### Scenario: Migrating from `address` (string) to `address_json` (structured)

假設我們有一個 `users` 表，原本 `address` 存純文字，現在需求變更要存 JSON 結構。

#### Step 1: Migration (SQL) - Expand
```sql
-- 1. Add new column, nullable
ALTER TABLE users ADD COLUMN address_json JSONB;
```

#### Step 2: Application Code (Dual Write)
```python
# Pseudo-code in User Model
def save(self):
    # 寫入舊欄位 (Source of Truth for now)
    self.db_row.address = self.address_str
    
    # 同步寫入新欄位 (Shadow write)
    self.db_row.address_json = parse_address(self.address_str)
    
    self.db_row.save()

def get_address(self):
    # 讀取仍使用舊欄位
    return self.db_row.address
```

#### Step 3: Backfill (Background Job)
```sql
-- 分批次更新，避免鎖死
UPDATE users 
SET address_json = json_build_object('raw', address) 
WHERE address_json IS NULL 
LIMIT 1000;
-- Repeat until done
```

#### Step 4: Application Code (Switch Read)
```python
def get_address(self):
    # 切換讀取來源 (Source of Truth moved to new column)
    if self.db_row.address_json:
        return format_address(self.db_row.address_json)
    return self.db_row.address # Fallback just in case
```

#### Step 5: Cleanup (SQL) - Contract
```sql
-- 經過數週觀察確認無誤後
-- 1. 移除程式碼中的 address 寫入邏輯
-- 2. Drop column (Optional, often kept for a while as backup)
ALTER TABLE users DROP COLUMN address;
```