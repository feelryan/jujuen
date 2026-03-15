# 常見資安陷阱與反模式 / Common Security Pitfalls & Anti-Patterns

在軟體開發中，最大的資安風險往往不是來自於「不知道高深的駭客技術」，而是來自於「自作聰明」或「為了方便而妥協」。本章節將盤點那些在 Code Review 與架構設計中最常出現的致命錯誤。

In software development, the biggest security risks often stem not from a lack of advanced hacking knowledge, but from "trying to be clever" or "compromising for convenience." This chapter covers the most common fatal errors found in code reviews and architectural designs.

---

## Mental model｜心智模型

### 1. 柯克霍夫原則 (Kerckhoffs's Principle)
**"The system must not require secrecy and can be stolen by the enemy without causing trouble."**
永遠假設攻擊者擁有你的原始碼、資料庫結構與架構圖。系統的安全性應完全依賴於**密鑰 (Key)** 的保密，而不是依賴於**演算法或邏輯**的隱藏。
> **Rule:** 如果你的安全機制依賴於「沒人知道這個 API 存在」或「沒人看得懂這段混淆程式碼」，那你已經被攻破了。

### 2. 乏味即安全 (Boring is Safe)
在密碼學與資安實作領域，「創新」通常意味著「漏洞」。使用經過數十年驗證的標準庫 (Standard Libraries) 與演算法，遠比自己寫一個「輕量級加密」要安全得多。
> **Rule:** Don't roll your own crypto. Use boring, standard, proven tools.

### 3. 最小權限原則 (Principle of Least Privilege, PoLP)
權限給予應當是「剛好夠用 (Just Enough)」，而不是「為了方便全開」。這是一個經濟學問題：限制權限能將單點突破後的「爆炸半徑 (Blast Radius)」降到最低。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 使用標準加密原語 (Standard Cryptographic Primitives)
不要自己實作 XOR 運算或位移加密。
- **對稱加密 (Symmetric):** 使用 `AES-GCM` (Authenticated Encryption) 或 `ChaCha20-Poly1305`。
- **雜湊 (Hashing):** 使用 `SHA-256` (for signatures) 或 `Argon2id` / `bcrypt` (for passwords)。
- **隨機數 (Randomness):** 必須使用 `CSPRNG` (Cryptographically Secure Pseudo-Random Number Generator)，如 `/dev/urandom` 或語言內建的 `crypto.getRandomValues()`。

### 2. 縱深防禦 (Defense in Depth)
不要依賴單一層防護。
- 即使 API Gateway 有驗證，內部的 Microservices 之間仍需 mTLS 或 Token 驗證。
- 即使資料庫在內網，連線仍需加密且需強密碼。

### 3. 基礎設施即代碼 (IaC) 的權限限縮
在 Terraform 或 CloudFormation 中，明確定義 Resource 與 Action。
- **Pattern:** 為每個 Lambda/Service 建立獨立的 IAM Role，只給予其讀寫特定 S3 Bucket 或 DynamoDB Table 的權限。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 自製加密演算法 (The DIY Cryptographer)
這是最危險的反模式。開發者常誤以為將資料進行複雜的位元運算或 Base64 編碼就是加密。
- **Pitfall:** 使用 `Base64` 偽裝成加密。
- **Pitfall:** 使用簡單的 `XOR` 加上寫死在程式碼裡的 Key。
- **Risk:** 容易受到頻率分析攻擊 (Frequency Analysis) 或已知明文攻擊 (Known-plaintext attack)。且自製演算法通常無法防範側信道攻擊 (Side-channel attacks，如 Timing Attack)。

### 2. 隱匿式安全 (Security by Obscurity)
試圖透過「隱藏」來獲取安全感，而非透過數學或嚴格的驗證。
- **Pitfall:** 將 Admin 後台路徑改為 `/super-secret-admin-v2` 而不加強 MFA。
- **Pitfall:** 依賴前端 JavaScript 混淆 (Obfuscation) 來保護 API Key 或商業邏輯。
- **Pitfall:** 將 SSH Port 從 22 改為 2222，卻不禁用密碼登入。
- **Reality:** Port scanning 和 Directory brute-forcing 工具能在幾分鐘內找到這些「秘密」。

### 3. 過度寬鬆的雲端權限 (Permissive Cloud Permissions)
為了開發方便，給予過大的權限，最後忘記收回。
- **Pitfall:** 在 AWS IAM Policy 中使用 `Action: "*"` 或 `Resource: "*"`。
- **Pitfall:**賦予 Developer `AdministratorAccess` 權限以便除錯。
- **Pitfall:** 將 S3 Bucket 設為 Public Read，只因為「檔名是隨機雜湊的，沒人猜得到」。
- **Consequence:** 一旦 Access Key 洩漏，攻擊者可直接刪除整個基礎設施或植入挖礦程式。

### 4. 錯誤處理洩漏資訊 (Verbose Error Leaking)
- **Pitfall:** 在 Production API Response 中回傳完整的 Stack Trace。
- **Pitfall:** 登入失敗時回傳「該使用者不存在」vs「密碼錯誤」（應統一回傳「帳號或密碼錯誤」以防範 User Enumeration）。

---

## Checklists & workflows｜檢查清單與流程

在進行 Code Review 或部署前，請對照以下清單：

### Crypto & Data Protection
- [ ] **No DIY Crypto:** 確認沒有自創的加密邏輯，所有加密皆呼叫語言標準庫 (e.g., Python `cryptography`, Node `crypto`, Go `crypto/aes`)。
- [ ] **No Hardcoded Secrets:** 程式碼中沒有寫死 API Key、密碼或 Salt。應使用環境變數或 Secret Manager。
- [ ] **Hashing:** 密碼儲存是否使用了 `bcrypt`、`scrypt` 或 `Argon2`？（嚴禁使用 MD5, SHA1, 甚至單純的 SHA256）。
- [ ] **Randomness:** 隨機數生成是否使用了 CSPRNG？（避免使用 `Math.random()` 進行安全相關操作）。

### Access Control & Cloud
- [ ] **Least Privilege:** 檢查 IAM Role/Policy，是否移除了所有的 `*` (Wildcard)？每個服務是否只有其運作所需的最小權限？
- [ ] **Object Level Access:** 檢查 IDOR (Insecure Direct Object References)。使用者 A 透過 API 修改 ID=123 的資料時，後端是否驗證了 ID=123 確實屬於使用者 A？
- [ ] **Public Exposure:** 確認 S3 Buckets、Elasticsearch Clusters、Databases 未對 `0.0.0.0/0` 開放。

### Input & Output
- [ ] **Input Validation:** 所有輸入是否經過驗證（Allow-list 優先）？
- [ ] **Output Encoding:** 所有輸出到瀏覽器的資料是否經過適當的 Encoding 以防範 XSS？
- [ ] **Generic Errors:** API 錯誤訊息是否已過濾敏感資訊（無 Stack Trace、無 SQL 錯誤細節）？

---

## Real-world examples｜實戰案例

### Case 1: The "Base64 is Encryption" Fallacy
**❌ Bad (Anti-Pattern):**
開發者為了「保護」儲存在 LocalStorage 的使用者設定，做了一層編碼。
```javascript
// 這不是加密，這只是編碼，任何人都能解碼
const secretData = JSON.stringify({ key: '1234-5678' });
const protectedData = btoa(secretData); // Base64 encode
localStorage.setItem('config', protectedData);
```

**✅ Good (Best Practice):**
如果資料必須在 Client 端加密（極少見，通常由 Server 處理），需使用 Web Crypto API。
```javascript
// 使用 AES-GCM 進行真實加密 (簡化示意)
const key = await window.crypto.subtle.generateKey(...);
const iv = window.crypto.getRandomValues(new Uint8Array(12));
const encrypted = await window.crypto.subtle.encrypt(
    { name: "AES-GCM", iv: iv },
    key,
    new TextEncoder().encode(secretData)
);
```

### Case 2: AWS IAM Permission Bloat
**❌ Bad (Anti-Pattern):**
為了讓 Lambda 能寫入 Log 和讀取 S3，開發者直接給了 Admin 權限。
```json
{
    "Effect": "Allow",
    "Action": "*",
    "Resource": "*"
}
```
*後果：如果這個 Lambda 的程式碼有漏洞被注入 (RCE)，攻擊者現在擁有整個 AWS 帳號的控制權。*

**✅ Good (Best Practice):**
只給予特定 Bucket 的特定權限。
```json
{
    "Effect": "Allow",
    "Action": [
        "s3:GetObject",
        "s3:PutObject"
    ],
    "Resource": "arn:aws:s3:::my-specific-app-bucket/*"
}
```

### Case 3: Timing Attack due to String Comparison
**❌ Bad (Anti-Pattern):**
比較 HMAC 簽章時使用一般字串比較。
```python
# 當字串在第1個字元就不匹配時，回傳速度比在第10個字元不匹配時快
# 攻擊者可利用微小的時間差猜出正確的 signature
if user_signature == correct_signature:
    return True
```

**✅ Good (Best Practice):**
使用 Constant Time Comparison (常數時間比較)。
```python
import hmac
# 無論在哪個字元不匹配，花費時間皆相同
if hmac.compare_digest(user_signature, correct_signature):
    return True
```