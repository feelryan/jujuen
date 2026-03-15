# 測試策略與 Mock 技巧 / Testing Strategies & Mocking Techniques

## Mental model｜心智模型

在 Python 的測試生態系中，我們不應將測試視為單純的「驗證碼」，而應將其視為**「可執行的規格書」 (Executable Specifications)** 與**「受控的實驗室」 (Controlled Laboratory)**。

### 1. The Laboratory: Isolation & Determinism (實驗室：隔離與確定性)
測試代碼（SUT, System Under Test）就像是一個放在無塵室中的實驗樣本。
- **Fixtures (`pytest.fixture`)** 是實驗前的「準備工作」與實驗後的「清理工作」（Setup & Teardown）。它們負責將環境重置為已知狀態。
- **Mocks (`unittest.mock`)** 是「替身演員」。當真實的依賴（如 Database, API, File System）太慢、太貴或不可控時，我們用行為固定的替身來取代它們。

### 2. The Patching Rule: "Patch where it is used" (Patch 的黃金法則)
這是 Python Mocking 最常讓人困惑的概念。
- **不要 Patch 定義的地方 (Don't patch where it is defined)**。
- **要 Patch 被查找的地方 (Patch where it is looked up)**。
- *Mental Image*: 當你的模組 A `import` 了模組 B 的 `function_x`，模組 A 擁有的是 `function_x` 的一份參考（Reference）。你必須替換掉模組 A 手上的那份參考，而不是去修改模組 B 本身。

### 3. Testing Behavior vs. Implementation (行為 vs. 實作)
- **White-box testing (白箱)**：過度依賴 Mock 內部函式呼叫，導致重構時測試由紅轉綠極其困難（Brittle Tests）。
- **Black-box testing (黑箱)**：關注 Input 與 Output（包含 Side Effects）。這是我們追求的目標。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Pytest Fixtures over `setUp/tearDown`
使用 `pytest` 的 Fixture 機制取代傳統 `unittest` 類別的 `setUp`。Fixtures 支援依賴注入（Dependency Injection），更具模組化與可重用性。

- **Scope Management**: 善用 `scope="session"` 或 `scope="module"` 來共用昂貴的資源（如 DB 連線），並用 `scope="function"` 進行資料清理。
- **Yield Fixtures**: 使用 `yield` 語法來處理 Teardown，比 `addfinalizer` 更直觀。

```python
@pytest.fixture
def db_session():
    # Setup: Create connection
    conn = connect_db()
    yield conn
    # Teardown: Close connection
    conn.close()
```

### 2. Parametrization for Data-Driven Tests
不要在測試中使用 `for` 迴圈。使用 `@pytest.mark.parametrize` 可以讓每個案例獨立執行，失敗時報告更清晰。

```python
@pytest.mark.parametrize("input_str, expected", [
    ("hello", "HELLO"),
    ("World", "WORLD"),
    ("", ""),
])
def test_string_upper(input_str, expected):
    assert input_str.upper() == expected
```

### 3. Safe Mocking with `autospec=True`
使用 `unittest.mock.patch` 或 `mocker.patch` 時，務必加上 `autospec=True`。這會強制 Mock 物件遵循原始物件的 API 簽章（Signature）。
- **Benefit**: 防止測試通過但實際執行失敗（例如：你呼叫了 Mock 物件上一個根本不存在於真實物件的方法，預設 Mock 會默默接受，但 `autospec` 會報錯）。

### 4. Use `pytest-mock` wrapper
雖然 Python 內建 `unittest.mock`，但在 `pytest` 中建議安裝 `pytest-mock` 套件，使用 `mocker` fixture。它會自動處理 `stop()` (unpatch)，避免測試失敗後 Mock 殘留污染其他測試。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Mocking Everything" Trap (過度 Mock)
- **症狀**：測試程式碼比被測程式碼還長，充滿了 `mock_a.assert_called_once_with(...)`。
- **後果**：你只是在測試「程式碼是怎麼寫的」，而不是「程式碼做了什麼」。一旦重構內部邏輯（即使輸出不變），測試就會掛掉。
- **解法**：盡量只 Mock **跨越邊界** 的依賴（I/O, Network, 3rd Party Libs）。對於內部的 Helper function，直接測試或讓它們參與整合測試。

### 2. Patching the Wrong Location (Patch 錯位置)
- **錯誤**：在 `service.py` 中 `from external import api`，但在測試中 `patch('external.api')`。
- **後果**：`service.py` 已經拿到了 `api` 的參考，你的 Patch 沒生效。
- **解法**：必須 `patch('service.api')`。

### 3. Logic inside Tests (測試中有邏輯)
- **症狀**：測試程式碼中包含 `if`, `while`, 或複雜的資料轉換。
- **後果**：測試本身可能包含 Bug。
- **解法**：測試應該是線性的（Arrange -> Act -> Assert）。如果邏輯複雜，請拆分為多個參數化測試。

### 4. Leaking Global State (全域狀態洩漏)
- **症狀**：單獨跑測試 A 通過，單獨跑測試 B 通過，但一起跑就失敗。
- **原因**：修改了 `os.environ`、`sys.modules` 或 Class Attributes 卻沒復原。
- **解法**：使用 `pytest` 的 `monkeypatch` fixture，它會在測試結束後自動復原修改。

---

## Checklists & workflows｜檢查清單與流程

### Mocking Decision Tree (我需要 Mock 嗎？)
- [ ] **Is it I/O bound?** (Network, Disk, Database) -> **YES** (Mock or use Dockerized Fixture).
- [ ] **Is it Non-deterministic?** (Time, Random, Sensor data) -> **YES** (Mock/Freeze time).
- [ ] **Is it Slow?** (> 0.1s) -> **YES**.
- [ ] **Is it a pure logic internal function?** -> **NO** (Test directly or via integration).

### Code Review Checklist for Tests
- [ ] **AAA Pattern**: 結構是否清晰？(Arrange, Act, Assert)
- [ ] **Isolation**: 測試是否依賴外部真實服務？(不應依賴)
- [ ] **Determinism**: 多次執行結果是否一致？
- [ ] **Cleanup**: 是否使用了 `yield` fixture 或 `monkeypatch` 確保環境復原？
- [ ] **Coverage**: 是否測試了 Happy Path **以及** Edge Cases (Exceptions, Timeouts)？
- [ ] **Mock Specificity**: Mock 是否使用了 `autospec=True`？

---

## Real-world examples｜實戰案例

### Scenario 1: Handling External API & Side Effects
測試一個會呼叫外部 API 的 Service，並處理 Timeout 異常。

```python
# src/payment.py
import requests
from requests.exceptions import Timeout

def process_payment(url, data):
    try:
        response = requests.post(url, json=data, timeout=5)
        response.raise_for_status()
        return response.json()
    except Timeout:
        return {"error": "Payment gateway timed out"}

# tests/test_payment.py
import pytest
from src.payment import process_payment

def test_process_payment_timeout(mocker):
    # Arrange: Mock 'requests.post' inside 'src.payment' module
    # Note: We patch where it is used, not where it is defined
    mock_post = mocker.patch("src.payment.requests.post", autospec=True)
    
    # Simulate a Side Effect (Exception)
    mock_post.side_effect = requests.exceptions.Timeout
    
    # Act
    result = process_payment("http://fake-api.com", {"amount": 100})
    
    # Assert
    assert result == {"error": "Payment gateway timed out"}
    mock_post.assert_called_once()
```

### Scenario 2: Advanced Fixture with Scope & Cleanup
模擬一個資料庫連線，使用 `yield` 確保測試後關閉連線。

```python
# tests/conftest.py
import pytest

class MockDB:
    def __init__(self):
        self.connected = False
        self.data = {}
    
    def connect(self):
        self.connected = True
        
    def close(self):
        self.connected = False
        self.data = {}

@pytest.fixture(scope="function")
def db():
    # Setup
    _db = MockDB()
    _db.connect()
    
    # Provide the fixture value
    yield _db
    
    # Teardown (Guarantee execution even if test fails)
    _db.close()

# tests/test_db.py
def test_database_insert(db):
    assert db.connected is True
    db.data["key"] = "value"
    assert db.data["key"] == "value"
    # Teardown happens automatically after this function
```

### Scenario 3: Freezing Time
測試依賴當前時間的邏輯（如 Token 過期）。推薦使用 `freezegun` 或 `pytest-freezegun`。

```python
import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time

def is_token_expired(creation_time, ttl_seconds=3600):
    return datetime.now() > creation_time + timedelta(seconds=ttl_seconds)

@freeze_time("2023-10-01 12:00:00")
def test_token_expiration():
    creation_time = datetime(2023, 10, 1, 11, 0, 0) # 1 hour ago
    
    # Exactly 1 hour later (at frozen time)
    assert is_token_expired(creation_time) is False
    
    # Move time forward
    with freeze_time("2023-10-01 12:00:01"):
        assert is_token_expired(creation_time) is True
```