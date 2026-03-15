# Schema 設計實戰 Checklist | Schema Design Checklist

## Mental model｜心智模型

在設計 MySQL Schema 時，不能只考慮「資料如何儲存」，更要考慮「資料如何被存取」。Schema 是資料庫效能的地基，一旦地基打歪了，後續的 Query 優化或索引調整都只是在補救。

**核心思維：**

1.  **Schema follows Access Patterns (Schema 追隨存取模式)**：
    不要在真空狀態下設計 Schema。你必須知道應用程式會如何 `SELECT`、`INSERT` 和 `UPDATE` 這些資料。讀多寫少？還是寫入密集？這決定了正規化程度。
2.  **Compactness is King (緊湊即王道)**：
    MySQL (InnoDB) 是基於 Page (通常 16KB) 儲存的。一列 (Row) 的資料越小，一個 Page 能塞下的 Row 就越多，Buffer Pool 的快取命中率就越高，磁碟 I/O 就越少。
3.  **Three-Valued Logic Awareness (三值邏輯意識)**：
    永遠記住 `NULL` 不是 `0` 也不是 `Empty String`，它是「未知」。在 SQL 中，`NULL` 會破壞比較運算（`= NULL` 永遠為 False）並讓索引失效或變複雜。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Primary Key 策略 (Identity Strategy)
-   **Default Choice**: 使用 `BIGINT UNSIGNED AUTO_INCREMENT`。這是最高效的，因為它是循序寫入 (Sequential Write)，能減少 B-Tree 的頁分裂 (Page Splits)。
-   **Distributed Systems**: 如果需要全域唯一 ID (如分散式系統)，避免使用標準 UUID (亂序字串)。
    -   *Better*: 使用 **ULID** 或 **UUID v7** (Time-ordered)，並以 `BINARY(16)` 儲存，而非 `CHAR(36)`。這能保持索引的局部性 (Locality)。

### 2. 資料型別精準化 (Data Type Precision)
-   **Integer**: 根據實際範圍選擇。
    -   `TINYINT` (1 byte): 狀態碼、Enum 代替品、Boolean (`TINYINT(1)`).
    -   `INT` (4 bytes): 足夠應付 +/- 20億。
    -   `BIGINT` (8 bytes): 用於 ID 或極大數值。
-   **Strings**:
    -   `VARCHAR(N)`: N 代表**字元數**而非 Byte 數。雖然 `VARCHAR` 是變長的，但記憶體引擎在處理排序或暫存表時，可能會依據 N 分配固定記憶體，所以不要無腦設 `VARCHAR(255)`，設 `VARCHAR(50)` 若夠用就好。
    -   `CHAR(N)`: 僅用於長度固定的資料（如 Hash 值、國碼 `TW`, `US`），避免碎片化。
-   **Currency**: **絕對不要**用 `FLOAT` 或 `DOUBLE` 存錢。
    -   *Option A*: `DECIMAL(M, D)` (e.g., `DECIMAL(19, 4)`).
    -   *Option B*: 存成 `BIGINT` (以「分」或「最小單位」為單位)。

### 3. 字元集與排序 (Charset & Collation)
-   **Standard**: 現代應用一律使用 `utf8mb4` (支援 Emoji)。
-   **Collation**: 推薦 `utf8mb4_0900_ai_ci` (MySQL 8.0+ default) 或 `utf8mb4_unicode_ci`。

### 4. 正規化與反正規化 (Normalization vs. Denormalization)
-   **Start with 3NF**: 預設先做正規化，避免資料冗餘導致的更新異常。
-   **Denormalize for Reads**: 當 Join 超過 3 個大表且影響效能時，才考慮反正規化。
    -   *Pattern*: **Cache Columns** (e.g., 在 `users` 表存 `post_count`，避免每次 `COUNT(*) FROM posts`)。
    -   *Trade-off*: 必須在應用層或透過 Trigger 維護一致性。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The `NULL` Trap (NULL 的陷阱)
-   **Pitfall**: 允許欄位為 `NULL` 卻沒有特殊理由。
-   **Why**:
    -   `COUNT(col)` 不會計算 `NULL` 值。
    -   `NOT IN (subquery)` 如果子查詢包含 `NULL`，結果會變成空。
    -   程式碼中充滿 `if (val != null)` 的防禦性檢查。
-   **Fix**: 盡量設為 `NOT NULL` 並給予 Default Value (例如字串給 `''`，數值給 `0`，狀態給 `DEFAULT` status)。

### 2. EAV (Entity-Attribute-Value) Abuse
-   **Pitfall**: 建立一個包含 `entity_id`, `key`, `value` 的通用表來存所有屬性。
-   **Why**: 導致 Query 極其複雜 (無數個 Self-Join)，無法有效利用型別檢查與索引。
-   **Fix**: 使用 JSON 欄位 (MySQL 5.7+) 儲存稀疏屬性，或正規化為具體欄位。

### 3. Using `TEXT`/`BLOB` on High-Traffic Tables
-   **Pitfall**: 在頻繁讀取的主表（如 `users`）中放入 `description` (TEXT)。
-   **Why**: 即使不 Select 該欄位，某些操作仍可能導致效能抖動。且 `TEXT` 欄位通常會導致磁碟上的臨時表 (On-disk temporary tables) 而非記憶體臨時表。
-   **Fix**: 垂直分割 (Vertical Partitioning)，將大欄位移到 `user_profiles` 表。

### 4. Over-indexing or No-indexing FKs
-   **Pitfall**: 加上了 Foreign Key constraint 卻忘了給該欄位加 Index。
-   **Why**: 在做 Join 或 Delete Parent 時會導致全表掃描或鎖定問題。

---

## Checklists & workflows｜檢查清單與流程

在送出 Pull Request 或執行 Migration 腳本前，請執行以下檢查：

### 基礎結構檢查 (Structural Health)
- [ ] **Engine**: 確認使用 `InnoDB`。
- [ ] **Charset**: 確認使用 `utf8mb4`。
- [ ] **Primary Key**: 每個表都有 PK，且優先使用 `BIGINT UNSIGNED AUTO_INCREMENT` (除非有分散式 ID 需求)。
- [ ] **Foreign Keys**: 關聯欄位（FK）是否有建立索引？
- [ ] **Naming**: 表名與欄位名是否符合團隊規範（如 `snake_case`，表名複數 `users` vs 單數 `user`）？

### 欄位與型別檢查 (Column & Type Hygiene)
- [ ] **Integer Size**: 是否使用了過大的型別？(例如 Boolean 狀態用了 `INT` 而非 `TINYINT`)。
- [ ] **String Length**: `VARCHAR` 長度是否合理？是否誤用了 `TEXT`？
- [ ] **Decimals**: 金錢相關欄位是否使用了 `DECIMAL` 或 `BIGINT`？
- [ ] **NULL Strategy**: 所有欄位預設是否為 `NOT NULL`？若允許 `NULL`，是否有明確的業務理由？
- [ ] **Defaults**: 是否設定了合理的 `DEFAULT` 值？

### 效能與擴展性 (Performance & Scalability)
- [ ] **Large Columns**: 是否將極少存取的大欄位 (TEXT/BLOB) 拆分到附屬表？
- [ ] **JSON Usage**: 如果使用了 JSON 欄位，是否評估過查詢需求？(若需頻繁 filter JSON 內的 key，應考慮 Generated Column + Index)。
- [ ] **Denormalization**: 如果有反正規化欄位 (如 `total_amount`)，是否有對應的更新機制 (Trigger/App Logic)？

---

## Real-world examples｜實戰案例

### Case 1: User Table Optimization (使用者資料表優化)

#### ❌ Bad Design (常見錯誤)
```sql
CREATE TABLE users (
    id VARCHAR(255),            -- UUID 存成字串，浪費空間且索引效率低
    username VARCHAR(255),      -- 長度過長
    email VARCHAR(255),
    age INT,                    -- INT 浪費，人不會活超過 255 歲
    balance DOUBLE,             -- 浮點數存錢，精度災難
    is_active INT,              -- Boolean 用 INT
    created_at DATETIME         -- 沒有預設值
);
```

#### ✅ Good Design (推薦做法)
```sql
CREATE TABLE users (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    -- 若需對外隱藏 ID，另開 public_id BINARY(16) 存 UUID
    username VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    age TINYINT UNSIGNED NULL,          -- 允許 NULL 代表未填寫
    balance DECIMAL(19, 4) NOT NULL DEFAULT 0.0000, -- 金錢精確度
    is_active TINYINT(1) NOT NULL DEFAULT 1,        -- Boolean
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 自動時間戳
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

### Case 2: Handling Status with Enums vs TinyInt

**情境**：訂單狀態 (Pending, Paid, Shipped, Cancelled)。

-   **Approach A: ENUM**
    -   `status ENUM('pending', 'paid', ...)`
    -   *Pros*: 儲存空間小，資料庫層級限制值。
    -   *Cons*: 修改 ENUM 列表（增加狀態）在舊版 MySQL 是昂貴的 Schema Change。
-   **Approach B: TINYINT (Recommended)**
    -   `status TINYINT UNSIGNED NOT NULL DEFAULT 0`
    -   配合應用程式層的 Constants (e.g., `const STATUS_PENDING = 0`).
    -   *Pros*: 擴充狀態不需鎖表修改 Schema，移植性高。
    -   *Cons*: 查詢時看到的是數字，需對照表。

### Case 3: JSON Column for Flexible Attributes

**情境**：產品表，不同產品有完全不同的規格參數（衣服有尺寸顏色，電腦有 CPU RAM）。

```sql
CREATE TABLE products (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category_id INT UNSIGNED NOT NULL,
    attributes JSON,  -- 存儲 {"size": "M", "color": "red"} 或 {"cpu": "M1", "ram": "16GB"}
    
    -- Virtual Column for Indexing (MySQL 5.7+)
    -- 如果經常需要搜尋 "color"，建立一個虛擬欄位並加索引
    v_color VARCHAR(20) GENERATED ALWAYS AS (attributes->>'$.color') VIRTUAL,
    INDEX idx_category_color (category_id, v_color)
);
```
*Mental Check*: 不要因為有了 JSON 就放棄關聯式設計。核心欄位（需頻繁 Join、Sort、Filter 的）仍應保留為獨立 Column。