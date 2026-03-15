# 資料隱私與密碼學工程實務 / Data Privacy & Cryptography Engineering Practices

## Mental model｜心智模型

在處理資料安全時，工程師應具備以下核心思維，而非僅僅將加密視為一個 API 呼叫：

### 1. 密碼學不是魔法粉末 (Cryptography is not Magic Dust)
你不能隨便在系統上灑一點「加密」就覺得安全了。密碼學是一個**鏈條 (Chain)**，其強度取決於最脆弱的一環。通常最脆弱的不是數學演算法（如 AES 本身），而是**金鑰管理 (Key Management)**、**實作模式 (Implementation Modes)** 或 **隨機數生成 (RNG)**。
> **Rule of Thumb**: If you are typing `import crypto` and writing raw math logic, you are likely doing it wrong. Use high-level abstractions.

### 2. 資料有毒 (Data is Toxic Waste)
從隱私角度來看，將 PII (Personally Identifiable Information) 視為「有毒廢棄物」。
- **最小化 (Minimization)**：只收集絕對必要的資料。
- **隔離 (Isolation)**：將敏感資料與一般業務資料分開存儲。
- **生命週期 (Lifecycle)**：一旦不再需要，立即銷毀。
資料越少，洩漏時的爆炸半徑 (Blast Radius) 就越小。

### 3. 防禦縱深 (Defense in Depth) for Data
資料有三種狀態，必須在每一層都進行保護：
- **At Rest (靜態)**：硬碟、資料庫、備份檔（加密防止物理竊取或硬碟報廢後的洩漏）。
- **In Transit (傳輸中)**：網路傳輸（TLS 防止中間人監聽）。
- **In Use (使用中)**：記憶體內（防止 Memory Dump 或日誌洩漏）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 演算法選擇指南 (Algorithm Selection Guide)
不要自己發明或選擇冷門演算法，請遵循當前的工業標準：

| 用途 (Use Case) | 推薦演算法 (Recommended) | 備註 |
| :--- | :--- | :--- |
| **對稱加密 (Symmetric)** <br> *資料儲存* | **AES-256-GCM** (或 ChaCha20-Poly1305) | **必須使用 AEAD** (Authenticated Encryption)。GCM 模式同時保證機密性與完整性。避免使用 CBC 或 ECB。 |
| **非對稱加密 (Asymmetric)** <br> *金鑰交換、數位簽章* | **ECC (Curve25519 / Ed25519)** 或 RSA-4096 | ECC 效能更好且金鑰更短。若必須用 RSA，請確保 Key Size $\ge$ 2048 (推薦 4096)。 |
| **密碼雜湊 (Password Hashing)** | **Argon2id** / bcrypt / scrypt | **絕對不要**用 SHA-256 存密碼。必須使用專門設計的「慢速雜湊」以抵抗 GPU 暴力破解。 |
| **資料完整性 (Integrity)** | **SHA-256** / SHA-3 / HMAC-SHA256 | 用於驗證檔案未被竄改，而非用於密碼存儲。 |

### 2. 信封加密 (Envelope Encryption)
在雲端環境或大型系統中，直接使用一把 Master Key 加密所有資料是危險且難以管理的。
- **Pattern**: 使用一個中心化的 Master Key (KEK - Key Encryption Key) 來加密 每個資料獨有的 Data Key (DEK)。
- **Flow**:
  1. 生成一個隨機的 DEK。
  2. 用 DEK 加密資料。
  3. 呼叫 KMS (如 AWS KMS) 用 KEK 加密這個 DEK。
  4. 將「加密後的資料」與「加密後的 DEK」一起存入資料庫。
- **Benefit**: 減少 Master Key 的使用頻率（降低被破解風險），且便於輪替 (Rotation) 和權限控管。

### 3. PII 去識別化模式 (De-identification Patterns)
在存入 Data Warehouse 或 Log 之前，必須處理敏感資料：
- **Tokenization (代碼化)**：將敏感資料（如信用卡號）替換為無意義的 UUID，真實對應關係存在另一個高安全性的 Vault 中。
- **Masking (遮罩)**：只顯示部分資訊，如 `****-****-****-1234`。
- **Hashing (雜湊)**：用於比對但不需還原的情境（如檢查 Email 是否註冊過），記得加 **Salt** 防止 Rainbow Table 攻擊。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 使用 ECB 模式 (Using AES-ECB)
- **Bad Practice**: `AES.new(key, AES.MODE_ECB)`
- **Why**: ECB 模式將相同的明文區塊加密成相同的密文區塊。這意味著資料的**結構模式**（Pattern）會被保留。著名的「企鵝圖」就是例子，加密後仍能看見企鵝輪廓。
- **Fix**: 總是使用 **GCM** 或至少 CBC + HMAC。

### 2. 硬編碼金鑰 (Hardcoded Keys)
- **Bad Practice**: `const SECRET_KEY = "my-super-secret-key";` 直接寫在程式碼裡並 commit 到 Git。
- **Why**: 原始碼洩漏等於資料全毀。且無法在不重新部署的情況下輪替金鑰。
- **Fix**: 使用環境變數 (ENV) 或專門的 Secret Manager (HashiCorp Vault, AWS Secrets Manager)。

### 3. 錯誤的隨機數來源 (Weak Randomness)
- **Bad Practice**: 使用 `Math.random()` 或 `rand()` 生成 IV (Initialization Vector) 或 Salt。
- **Why**: 這些是偽隨機 (PRNG)，可被預測。
- **Fix**: 使用 CSPRNG (Cryptographically Secure Pseudo-Random Number Generator)，如 Python 的 `secrets` 模組、Node.js 的 `crypto.randomBytes()`。

### 4. 加密但未驗證完整性 (Encryption without Integrity)
- **Bad Practice**: 使用 AES-CBC 加密資料，但沒有計算 HMAC。
- **Why**: 攻擊者可以修改密文（Bit-flipping attack），解密後的資料會變成垃圾或特定的惡意 payload，而系統不會報錯，甚至引發 Padding Oracle Attack。
- **Fix**: 使用 **AEAD (Authenticated Encryption with Associated Data)**，如 AES-GCM，它內建了完整性檢查。

### 5. 在日誌中記錄原始資料 (Logging Raw Data)
- **Bad Practice**: `logger.info("Request payload: " + JSON.stringify(userRequest))`
- **Why**: 如果 payload 包含密碼、信用卡號或 PII，這些資料會永久留在 Log 系統中（通常 Log 的安全性低於 DB）。
- **Fix**: 實作 Log Sanitizer / Redactor middleware。

---

## Checklists & workflows｜檢查清單與流程

### 實作前決策樹 (Decision Tree)

1. **我要保護的是密碼嗎？**
   - [Yes] -> 使用 **Argon2id** 或 **bcrypt**。 (絕對不要用 AES 或 SHA-256)
   - [No] -> 下一步。
2. **我要與他人交換加密訊息嗎？**
   - [Yes] -> 使用 **TLS** (傳輸層) 或 **RSA/ECC** + **AES** (混合加密)。
   - [No] -> 下一步。
3. **我要儲存資料在資料庫/硬碟嗎？**
   - [Yes] -> 使用 **AES-256-GCM**。
   - **Key 誰管？** -> 雲端 KMS (推薦) 或 環境變數。

### Code Review Checklist

- [ ] **Algorithm**: 是否使用了過時的演算法 (MD5, SHA1, DES, RC4)？應強制拒絕。
- [ ] **Mode**: 對稱加密是否使用了 GCM 或 Poly1305？(若用 CBC，是否有 HMAC？若用 ECB，直接 Reject)。
- [ ] **Randomness**: IV (Initialization Vector) 和 Salt 是否是隨機生成且**每次不同**？(IV 不可重用)。
- [ ] **Secrets**: 程式碼中是否有字串常數看起來像金鑰？
- [ ] **Logs**: 是否有針對 PII 欄位做 Masking 處理？
- [ ] **Error Handling**: 解密失敗時，錯誤訊息是否洩漏了細節？(應只回傳通用的 "Decryption Failed"，防止 Oracle Attack)。

---

## Real-world examples｜實戰案例

### 案例 1：正確的資料庫欄位加密 (Application-Level Encryption)

假設需要儲存使用者的身分證字號 (National ID)。

**❌ 錯誤做法 (Naive Approach):**
```javascript
// BAD: ECB mode, weak key, no IV
const cipher = crypto.createCipher('aes-256-ecb', 'password');
let encrypted = cipher.update(nationalId, 'utf8', 'hex');
encrypted += cipher.final('hex');
// Result: 相同的 ID 總是產生相同的密文，容易被頻率分析攻擊。
```

**✅ 正確做法 (Best Practice - AES-GCM):**
```javascript
// GOOD: AES-256-GCM, Random IV, Authentication Tag
const key = process.env.DATA_ENCRYPTION_KEY; // 32 bytes from KMS/Env
const iv = crypto.randomBytes(12); // GCM standard IV size is 12 bytes (96 bits)
const cipher = crypto.createCipheriv('aes-256-gcm', Buffer.from(key, 'hex'), iv);

let encrypted = cipher.update(nationalId, 'utf8', 'hex');
encrypted += cipher.final('hex');
const authTag = cipher.getAuthTag().toString('hex');

// Store in DB: { iv: iv.toString('hex'), content: encrypted, tag: authTag }
// 解密時需要同時提供 IV, Content, 和 AuthTag 才能成功。
```

### 案例 2：PII 資料的 Log 脫敏 (Logging Sanitization)

在處理 API 請求時，防止敏感資料進入 ELK/Datadog。

**Pseudo-code (Middleware Pattern):**

```python
SENSITIVE_KEYS = {'password', 'credit_card', 'token', 'ssn'}

def sanitize_payload(payload):
    if isinstance(payload, dict):
        new_payload = payload.copy()
        for key, value in new_payload.items():
            if key.lower() in SENSITIVE_KEYS:
                new_payload[key] = '***MASKED***'
            else:
                new_payload[key] = sanitize_payload(value) # Recursive
        return new_payload
    return payload

# In your logging middleware
def log_request(request):
    safe_body = sanitize_payload(request.json)
    logger.info(f"Received request: {safe_body}")
```

### 案例 3：密碼儲存 (Password Storage)

**Scenario**: 使用者註冊。

1. **User Input**: `P@ssw0rd123`
2. **Backend**:
   - Generate Salt: `random_bytes(16)`
   - Hash: `Argon2id(password, salt, time_cost=2, memory_cost=64MB)`
   - **Store**: `$argon2id$v=19$m=65536,t=2,p=1$gZiV...$eUj8...` (包含演算法參數、Salt 和 Hash 結果的標準字串)
3. **Verification**:
   - 直接使用驗證函式 `Argon2.verify(stored_hash, input_password)`，函式會自動解析 stored_hash 中的 salt 與參數進行計算比對。