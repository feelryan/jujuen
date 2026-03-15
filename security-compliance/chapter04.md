# 1. 前言與學習目標 (Introduction & Learning Objectives)

在資深工程師的職涯中，密碼學（Cryptography）往往是最容易被誤用，卻也是風險最高的領域。我們不需要成為數學家來發明新的演算法，但必須成為合格的「密碼學工程師（Cryptography Engineer）」，懂得正確選擇原語（Primitives）並管理密鑰生命週期。本章目標不在於數學推導，而在於工程實踐與架構決策。

In the career of a Senior Software Engineer, Cryptography is often the most misused and highest-risk area. We don't need to be mathematicians inventing new algorithms, but we must become competent "Cryptography Engineers" who know how to select the right primitives and manage key lifecycles. The goal of this chapter is not mathematical derivation, but engineering practice and architectural decision-making.

完成本章後，你應該能夠：

After completing this chapter, you should be able to:

1.  **精準選擇加密原語**：在 Hashing、對稱加密（Symmetric）與非對稱加密（Asymmetric）之間，根據資料機密性、完整性與驗證需求做出正確選擇。
    **Select cryptographic primitives precisely**: Make the right choice between Hashing, Symmetric, and Asymmetric encryption based on data confidentiality, integrity, and authentication needs.
2.  **設計信封加密（Envelope Encryption）架構**：理解並實作大型系統中的密鑰階層管理（Key Hierarchy），解決海量資料加密的效能與密鑰輪替（Rotation）問題。
    **Design Envelope Encryption architecture**: Understand and implement key hierarchy management in large-scale systems to solve performance and key rotation challenges for massive data encryption.
3.  **實作安全的資料狀態保護**：針對 Data at Rest（靜態資料）與 Data in Transit（傳輸中資料）制定合規（如 GDPR/PCI-DSS）的保護策略，並避免常見的實作漏洞（如 ECB 模式、弱隨機數）。
    **Implement secure data state protection**: Formulate compliant protection strategies (e.g., GDPR/PCI-DSS) for Data at Rest and Data in Transit, avoiding common implementation vulnerabilities (e.g., ECB mode, weak RNGs).

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 密碼學原語的三大支柱 (The Three Pillars of Cryptographic Primitives)

對於工程師而言，將密碼學工具視為具有不同屬性的「黑盒子」是建立心智模型的第一步。

For engineers, treating cryptographic tools as "black boxes" with distinct properties is the first step in building a mental model.

1.  **雜湊 (Hashing)**：
    *   **模型**：指紋機（Fingerprint Machine）。
    *   **特性**：單向（不可逆）、定長輸出、雪崩效應（Avalanche Effect）。
    *   **用途**：資料完整性校驗（Checksums）、密碼儲存（需加 Salt）、數位簽章的摘要。
    *   **Model**: Fingerprint Machine.
    *   **Characteristics**: One-way (irreversible), fixed-length output, Avalanche Effect.
    *   **Usage**: Data integrity checks (Checksums), password storage (requires Salt), summaries for digital signatures.

2.  **對稱加密 (Symmetric Encryption)**：
    *   **模型**：保險箱（Safe Box）。只有一把鑰匙，鎖上和打開都用它。
    *   **特性**：速度快（適合大數據量）、密鑰分發困難（Shared Secret Problem）。
    *   **演算法**：AES-GCM (推薦), ChaCha20.
    *   **Model**: Safe Box. There is only one key used for both locking and unlocking.
    *   **Characteristics**: Fast (suitable for large data volumes), difficult key distribution (Shared Secret Problem).
    *   **Algorithms**: AES-GCM (Recommended), ChaCha20.

3.  **非對稱加密 (Asymmetric Encryption)**：
    *   **模型**：郵筒（Mailbox）。任何人都可以將信件投入郵筒（公鑰加密），但只有郵差有鑰匙能取出信件（私鑰解密）。
    *   **特性**：速度慢（比對稱加密慢 1000 倍以上）、解決了密鑰分發問題、支援數位簽章（身份驗證）。
    *   **演算法**：RSA, ECC (Elliptic Curve Cryptography).
    *   **Model**: Mailbox. Anyone can drop a letter in (Public Key encryption), but only the postman has the key to retrieve it (Private Key decryption).
    *   **Characteristics**: Slow (1000x+ slower than symmetric), solves key distribution, supports digital signatures (Identity Authentication).
    *   **Algorithms**: RSA, ECC (Elliptic Curve Cryptography).

## 2.2 信封加密 (Envelope Encryption)

這是雲端時代處理資料加密的核心心智模型。我們不直接用「主密鑰（Master Key）」加密 TB 級的資料，而是採用分層結構。

This is the core mental model for handling data encryption in the cloud era. We do not encrypt TB-scale data directly with a "Master Key"; instead, we use a layered structure.

*   **DEK (Data Encryption Key)**：用來加密實際資料的對稱金鑰。每個檔案或每筆 Record 可能都有獨立的 DEK。
*   **KEK (Key Encryption Key)**：用來加密 DEK 的金鑰（通常由 KMS 管理）。
*   **流程**：`Encrypt(Data, DEK)` -> `Encrypt(DEK, KEK)` -> 儲存 `Ciphertext + Encrypted_DEK`。

*   **DEK (Data Encryption Key)**: A symmetric key used to encrypt the actual data. Each file or record may have an independent DEK.
*   **KEK (Key Encryption Key)**: A key used to encrypt the DEK (usually managed by a KMS).
*   **Flow**: `Encrypt(Data, DEK)` -> `Encrypt(DEK, KEK)` -> Store `Ciphertext + Encrypted_DEK`.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在系統設計面試或架構規劃中，Security 不應是事後諸葛，而需內建於設計中（Security by Design）。

In system design interviews or architectural planning, Security should not be an afterthought but built into the design (Security by Design).

## 3.1 Key Management System (KMS) 的角色 (The Role of KMS)

在微服務架構中，KMS 是核心的「信任根（Root of Trust）」。

In a microservices architecture, the KMS acts as the core "Root of Trust".

*   **集中化管理 (Centralization)**：避免金鑰散落在 Config 檔或程式碼中。
*   **審計 (Auditability)**：誰（Service Account）、在什麼時候、解密了哪個 Key，KMS 都有 Log。這對 Compliance（如 SOC2, PCI-DSS）至關重要。
*   **自動輪替 (Automatic Rotation)**：KMS 可以設定 KEK 每年自動輪替，舊資料在解密時使用舊版 KEK，重新加密時使用新版 KEK（Lazy Re-encryption）。

*   **Centralization**: Prevents keys from being scattered in config files or code.
*   **Auditability**: Who (Service Account), when, and which Key was decrypted—KMS logs everything. This is crucial for Compliance (e.g., SOC2, PCI-DSS).
*   **Automatic Rotation**: KMS can be configured to rotate KEKs annually. Old data uses the old KEK version upon decryption and the new KEK version upon re-encryption (Lazy Re-encryption).

## 3.2 資料庫加密策略 (Database Encryption Strategies)

當設計一個儲存 PII（個人識別資訊）的系統時，你有三個層次的選擇：

When designing a system to store PII (Personally Identifiable Information), you have choices at three levels:

1.  **Volume/Disk Encryption (e.g., AWS EBS Encryption)**:
    *   **優點**：透明、對 App 無感、防範硬碟物理失竊。
    *   **缺點**：無法防範 DB Admin 或 SQL Injection 攻擊（資料在記憶體中是明文）。
    *   **Pros**: Transparent, agnostic to App, protects against physical drive theft.
    *   **Cons**: Does not protect against DB Admin or SQL Injection attacks (data is plaintext in memory).

2.  **Transparent Data Encryption (TDE)**:
    *   **優點**：DB 引擎層加密，備份檔是加密的。
    *   **缺點**：DB 運作時仍需解密，對擁有 DB 權限的攻擊者防禦有限。
    *   **Pros**: DB engine layer encryption; backups are encrypted.
    *   **Cons**: Still requires decryption during DB operation; limited defense against attackers with DB privileges.

3.  **Application-Level Encryption (Client-Side Encryption)**:
    *   **優點**：最高安全性。DB 只看到亂碼，即便 DB 洩漏，資料也是安全的。
    *   **缺點**：**喪失搜尋能力**（無法做 Range Query 或 Fuzzy Search），Schema 變更複雜。
    *   **Pros**: Highest security. DB only sees gibberish; even if the DB leaks, data remains secure.
    *   **Cons**: **Loss of searchability** (cannot perform Range Query or Fuzzy Search), complex Schema changes.

**資深觀點**：對於極度敏感欄位（如信用卡號、SSN），通常採用 **Application-Level Encryption** 配合 **Envelope Encryption**。

**Senior View**: For highly sensitive fields (e.g., Credit Card Numbers, SSN), **Application-Level Encryption** combined with **Envelope Encryption** is typically used.

---

# 4. 逐步示例 (Walkthrough / Example)

## 案例：實作基於 KMS 的信封加密 (Scenario: Implementing Envelope Encryption with KMS)

假設我們需要將使用者的信用卡號寫入資料庫。我們不希望應用程式伺服器長期持有主金鑰。

Suppose we need to write user credit card numbers into a database. We do not want the application server to hold the master key long-term.

### 步驟 1: 定義介面與依賴 (Step 1: Define Interface and Dependencies)

我們使用 AWS KMS 或 Google Cloud KMS 作為 KEK 的託管者。

We use AWS KMS or Google Cloud KMS as the custodian of the KEK.

```python
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# 模擬 KMS 客戶端 (Mock KMS Client)
class MockKMSClient:
    def __init__(self, master_key):
        self.master_key = master_key # KEK

    def encrypt(self, plaintext_data_key):
        # 在真實世界中，這是一個 API call (如 aws kms encrypt)
        # In real world, this is an API call (e.g., aws kms encrypt)
        aesgcm = AESGCM(self.master_key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, plaintext_data_key, None)
        return nonce + ciphertext

    def decrypt(self, encrypted_data_key):
        # 真實世界中，KMS 會驗證 IAM 權限後解密
        # In real world, KMS verifies IAM permissions before decrypting
        aesgcm = AESGCM(self.master_key)
        nonce = encrypted_data_key[:12]
        ciphertext = encrypted_data_key[12:]
        return aesgcm.decrypt(nonce, ciphertext, None)

# 初始化 KMS (Initialize KMS)
# KEK 通常由雲端供應商生成並保存在 HSM 中
# KEK is usually generated by cloud provider and stored in HSM
kek_master = AESGCM.generate_key(bit_length=256) 
kms = MockKMSClient(kek_master)
```

### 步驟 2: 加密流程 (Step 2: Encryption Flow)

每次寫入資料時，生成一個新的 DEK。

Generate a new DEK every time data is written.

```python
def protect_data(sensitive_data: bytes, kms_client):
    # 1. 生成一次性的 Data Encryption Key (DEK)
    # 1. Generate a one-time Data Encryption Key (DEK)
    dek = AESGCM.generate_key(bit_length=256)
    
    # 2. 使用 DEK 加密資料 (本地端操作，速度快)
    # 2. Encrypt data using DEK (Local operation, fast)
    aesgcm = AESGCM(dek)
    nonce = os.urandom(12)
    # Associated Data 設為 None，實務上可綁定 Context (如 user_id) 防篡改
    ciphertext_blob = aesgcm.encrypt(nonce, sensitive_data, None)
    
    # 3. 呼叫 KMS 加密 DEK
    # 3. Call KMS to encrypt the DEK
    encrypted_dek = kms_client.encrypt(dek)
    
    # 4. 清除記憶體中的明文 DEK (Python 較難完全控制 GC，但在 C++/Go 需顯式清除)
    # 4. Wipe plaintext DEK from memory (Harder in Python GC, but explicit in C++/Go)
    del dek
    
    # 返回結構：加密後的資料 + 加密後的鑰匙 + Nonce
    # Return structure: Encrypted Data + Encrypted Key + Nonce
    return {
        "ciphertext": ciphertext_blob,
        "nonce": nonce,
        "encrypted_dek": encrypted_dek
    }

# 使用範例 (Usage Example)
credit_card = b"4111-2222-3333-4444"
record = protect_data(credit_card, kms)

print(f"Stored in DB: {record}")
# DB 儲存的是全是亂碼，沒有明文 Key
# DB stores only gibberish, no plaintext Key
```

### 步驟 3: 解密流程 (Step 3: Decryption Flow)

讀取時，先解密 DEK，再解密資料。

When reading, decrypt the DEK first, then decrypt the data.

```python
def access_data(record, kms_client):
    # 1. 從 DB 讀取 encrypted_dek，呼叫 KMS 解密
    # 1. Read encrypted_dek from DB, call KMS to decrypt
    dek = kms_client.decrypt(record["encrypted_dek"])
    
    # 2. 使用解密後的 DEK 還原資料
    # 2. Restore data using the decrypted DEK
    aesgcm = AESGCM(dek)
    plaintext = aesgcm.decrypt(record["nonce"], record["ciphertext"], None)
    
    return plaintext

recovered_cc = access_data(record, kms)
assert recovered_cc == credit_card
print("Decryption successful.")
```

### 為何這個做法可行？ (Why does this work?)
*   **效能 (Performance)**：大量資料的加密在本地完成（AES-GCM 很快），只有小小的 Key 透過網路傳輸給 KMS 加密。
*   **安全性 (Security)**：DEK 從未以明文形式儲存在硬碟上。KEK 從未離開過 KMS (HSM)。
*   **範圍爆炸半徑 (Blast Radius)**：如果某個 DEK 洩漏，只有該筆資料受影響，而非全庫。

*   **Performance**: Encryption of large data is done locally (AES-GCM is fast), only the small Key is transmitted over the network to KMS for encryption.
*   **Security**: DEK is never stored in plaintext on disk. KEK never leaves the KMS (HSM).
*   **Blast Radius**: If a specific DEK is leaked, only that specific record is compromised, not the entire database.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 使用 ECB 模式 (Using ECB Mode)
*   **錯誤描述**：使用 AES 時選擇 ECB (Electronic Codebook) 模式。
*   **為何不好**：ECB 對相同的明文區塊會產生相同的密文。經典的「企鵝圖片」例子顯示，加密後仍能看見企鵝的輪廓。它無法隱藏資料的模式（Patterns）。
*   **正確做法**：始終使用 **AES-GCM** 或 **ChaCha20-Poly1305**。這些是 AEAD (Authenticated Encryption with Associated Data)，同時保證機密性與完整性。

*   **Description**: Choosing ECB (Electronic Codebook) mode when using AES.
*   **Why it's bad**: ECB produces identical ciphertext for identical plaintext blocks. The classic "Penguin image" example shows the penguin's outline is still visible after encryption. It fails to hide data patterns.
*   **Best Practice**: Always use **AES-GCM** or **ChaCha20-Poly1305**. These are AEAD (Authenticated Encryption with Associated Data), ensuring both confidentiality and integrity.

## 5.2 自創密碼學演算法 (Rolling Your Own Crypto)
*   **錯誤描述**：試圖自己寫 XOR 混淆或修改現有演算法來「增加安全性」。
*   **為何不好**：密碼學極度依賴數學證明與社群審查。自創演算法幾乎 100% 存在側信道攻擊（Side-channel attacks）或數學漏洞。
*   **正確做法**：使用經過驗證的標準庫（如 OpenSSL, BoringSSL, Python `cryptography`, Java `Bouncy Castle`）。

*   **Description**: Attempting to write your own XOR obfuscation or modifying existing algorithms to "add security".
*   **Why it's bad**: Cryptography relies heavily on mathematical proofs and community review. Home-brewed algorithms almost 100% contain side-channel attacks or mathematical flaws.
*   **Best Practice**: Use verified standard libraries (e.g., OpenSSL, BoringSSL, Python `cryptography`, Java `Bouncy Castle`).

## 5.3 混淆 Hashing 與 Encryption (Confusing Hashing with Encryption)
*   **錯誤描述**：對密碼進行「加密」儲存，或者對需要還原的資料進行「雜湊」。
*   **為何不好**：密碼若可逆（加密），一旦 Key 洩漏，所有用戶密碼皆失竊。雜湊不可逆，但若需還原業務資料則無法使用。
*   **正確做法**：
    *   密碼（Password） -> **Hashing** (Argon2, bcrypt, scrypt) + Salt。
    *   信用卡/PII -> **Encryption** (AES-GCM) + Key Management。

*   **Description**: "Encrypting" passwords for storage, or "Hashing" data that needs to be retrieved.
*   **Why it's bad**: If passwords are reversible (encrypted), a Key leak compromises all user passwords. Hashing is irreversible, making it unusable for business data that needs retrieval.
*   **Best Practice**:
    *   Passwords -> **Hashing** (Argon2, bcrypt, scrypt) + Salt.
    *   Credit Cards/PII -> **Encryption** (AES-GCM) + Key Management.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何安全地儲存使用者的密碼？
**How do you securely store user passwords?**

*   **高分回答要點**：
    *   **不可逆性**：明確指出不能用加密（Encryption），必須用雜湊（Hashing）。
    *   **演算法選擇**：拒絕 MD5/SHA1/SHA256（速度太快，易被 GPU 暴力破解）。推薦 **Argon2** (Winner of Password Hashing Competition), **bcrypt**, 或 **scrypt**。
    *   **Salt**：解釋 Salt 如何防禦 Rainbow Table 攻擊（每個用戶獨立 Salt）。
    *   **Work Factor**：提及調整迭代次數（Cost factor）以隨著硬體進步保持破解難度。

*   **Key Points**:
    *   **Irreversibility**: Explicitly state that Encryption cannot be used; Hashing must be used.
    *   **Algorithm Choice**: Reject MD5/SHA1/SHA256 (too fast, vulnerable to GPU brute-force). Recommend **Argon2**, **bcrypt**, or **scrypt**.
    *   **Salt**: Explain how Salt defends against Rainbow Table attacks (unique Salt per user).
    *   **Work Factor**: Mention adjusting iteration counts (Cost factor) to maintain cracking difficulty as hardware improves.

## Q2: 在微服務架構中，Service A 如何安全地傳輸敏感資料給 Service B？
**In a microservices architecture, how does Service A securely transmit sensitive data to Service B?**

*   **高分回答要點**：
    *   **Transport Layer**: 必須使用 TLS 1.2+ (推薦 TLS 1.3)。
    *   **Mutual TLS (mTLS)**：不僅 Server 驗證，Client (Service A) 也要提供憑證，實現 Zero Trust 內網通訊。
    *   **Application Layer (Optional)**：若資料極度敏感（如經過不可信的中間件），可疊加 Payload Encryption（JWE 或 PGP），確保只有 Service B 能解開 Payload。

*   **Key Points**:
    *   **Transport Layer**: Must use TLS 1.2+ (TLS 1.3 recommended).
    *   **Mutual TLS (mTLS)**: Not just Server validation; Client (Service A) must also provide certificates, implementing Zero Trust internal communication.
    *   **Application Layer (Optional)**: If data is highly sensitive (e.g., passing through untrusted middleware), overlay Payload Encryption (JWE or PGP) to ensure only Service B can decrypt the payload.

## Q3: 請解釋 Envelope Encryption 以及為什麼我們需要它？
**Please explain Envelope Encryption and why we need it.**

*   **高分回答要點**：
    *   **定義**：Data Key 加密資料，Master Key 加密 Data Key。
    *   **效能**：避免每次加解密都呼叫遠端 KMS（網路延遲），只在解密 Data Key 時呼叫。
    *   **管理**：Master Key (KEK) 數量少，易於在 HSM 中管理與輪替；Data Key (DEK) 數量多但隨資料儲存，無需獨立管理。
    *   **限制突破**：雲端 KMS 通常有每秒請求數限制（Quota），Envelope Encryption 可大幅降低對 KMS 的 API 呼叫量。

*   **Key Points**:
    *   **Definition**: Data Key encrypts data; Master Key encrypts Data Key.
    *   **Performance**: Avoids calling remote KMS for every encryption/decryption (network latency); calls only occur when decrypting the Data Key.
    *   **Management**: Master Keys (KEK) are few and easy to manage/rotate in HSM; Data Keys (DEK) are many but stored with data, requiring no independent management.
    *   **Limit Breakthrough**: Cloud KMS often has Requests Per Second limits (Quota); Envelope Encryption drastically reduces API calls to KMS.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 本章記憶錨點 (Key Takeaways)
1.  **原語區分**：Hashing 是單向指紋；Symmetric 是保險箱（快）；Asymmetric 是郵筒（慢，身分驗證）。
2.  **信封加密 (Envelope Encryption)**：大數據加密的標準解法（DEK 加密資料，KEK 加密 DEK）。
3.  **KMS 是信任根**：不要自行管理 Master Key，使用 Cloud KMS 或 HSM。
4.  **AEAD**：對稱加密請認明 **AES-GCM**，拒絕 ECB。
5.  **密碼儲存**：使用慢速雜湊（Argon2/bcrypt）加 Salt，絕對不要用一般加密。

1.  **Primitive Distinction**: Hashing is a one-way fingerprint; Symmetric is a safe box (fast); Asymmetric is a mailbox (slow, identity auth).
2.  **Envelope Encryption**: The standard solution for big data encryption (DEK encrypts data, KEK encrypts DEK).
3.  **KMS is Root of Trust**: Do not manage Master Keys yourself; use Cloud KMS or HSM.
4.  **AEAD**: For symmetric encryption, stick to **AES-GCM**; reject ECB.
5.  **Password Storage**: Use slow hashing (Argon2/bcrypt) with Salt; absolutely never use standard encryption.

## 後續延伸 (Next Steps)
*   **實作練習**：在 AWS/GCP 上建立一個 KMS Key，並寫一段 Python script 使用 boto3/google-cloud-kms 實作信封加密。
*   **延伸閱讀**：研究 **TLS 1.3 Handshake** 流程，理解 Diffie-Hellman Key Exchange 如何在公開網路上協商出對稱金鑰。
*   **下一章預告**：進入 `Identity & Access Management (IAM)`，探討 OAuth2, OIDC 與 RBAC/ABAC 模型。

*   **Practical Exercise**: Create a KMS Key on AWS/GCP and write a Python script using boto3/google-cloud-kms to implement envelope encryption.
*   **Further Reading**: Research the **TLS 1.3 Handshake** process to understand how Diffie-Hellman Key Exchange negotiates symmetric keys over public networks.
*   **Next Chapter Preview**: Moving into `Identity & Access Management (IAM)`, exploring OAuth2, OIDC, and RBAC/ABAC models.