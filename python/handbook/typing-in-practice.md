# 實戰型別系統與靜態分析 / Practical Type Hinting & Static Analysis

## Mental model｜心智模型

### 1. 漸進式型別 (Gradual Typing)
Python 的型別系統是「漸進式」的。這意味著你可以選擇性地為部分程式碼加上型別註解，而不需要像 Java 或 C++ 那樣全有或全無。
**Mental Model**: 將 Type Hints 視為 **「可被機器驗證的文件 (Machine-verified documentation)」**。它主要服務於開發階段（IDE 提示）與 CI 階段（靜態分析），而非執行階段（Runtime）。Python VM 在執行時基本上會忽略這些註解。

### 2. 靜態分析 vs. 執行期驗證 (Static Analysis vs. Runtime Validation)
這是最容易混淆的概念。
- **Static Analysis (MyPy, Pyright)**: 在程式執行**前**檢查邏輯錯誤。它假設你的標註是誠實的。
- **Runtime Validation (Pydantic, Marshmallow)**: 在程式執行**時**檢查資料邊界（I/O Boundary）。它負責將外部不可信的 JSON/Raw Data 轉換為內部可信的物件。

**Rule of Thumb**: 在系統邊界（API Request, DB Read）使用 Pydantic 進行**驗證**；在系統內部邏輯使用 Type Hints 進行**約束**。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 使用 Protocol 實作結構化型別 (Structural Subtyping)
不要為了型別檢查而強迫繼承。Python 的強項是 Duck Typing，`typing.Protocol` 讓我們能以型別安全的方式保留這個特性。

```python
from typing import Protocol

# Pattern: 定義行為，而非繼承關係
class Sender(Protocol):
    def send(self, message: str) -> None: ...

# 任何有 send 方法的 class 都會自動符合 Sender，無需顯式繼承
def alert_user(sender: Sender, msg: str) -> None:
    sender.send(msg)
```

### 2. 現代化語法 (Modern Syntax)
盡量使用 Python 3.10+ 的原生語法，可讀性更高。
- **Union**: 使用 `str | int` 代替 `Union[str, int]`。
- **Optional**: 使用 `str | None` 代替 `Optional[str]`。
- **Collections**: 使用 `list[str]` 代替 `List[str]` (Python 3.9+)。

### 3. 泛型與 TypeVar 的正確使用 (Generics)
當函式輸入與輸出型別連動時，必須使用 `TypeVar`，否則會丟失型別資訊。

```python
from typing import TypeVar, Sequence

T = TypeVar("T")

# Bad: 返回的是 list[Any] 或 list[object]
def first_bad(items: Sequence): 
    return items[0]

# Good: 如果輸入是 list[int]，IDE 知道返回的一定是 int
def first_good(items: Sequence[T]) -> T:
    return items[0]
```

### 4. 解決循環依賴 (Handling Circular Imports)
型別註解常導致兩個模組互相 import。使用 `TYPE_CHECKING` 區塊與字串化型別 (Stringified Types) 來解決。

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # 這些 import 只在型別檢查時執行，Runtime 不會跑，避免循環引用
    from .user import User 

class Post:
    # 使用字串 "User" 作為前向引用 (Forward Reference)
    def __init__(self, author: "User"):
        self.author = author
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 濫用 `Any` (The `Any` Virus)
`Any` 會關閉該變數及其後續傳遞鏈的所有型別檢查。
- **Pitfall**: 一旦使用了 `Any`，它會像病毒一樣擴散，讓 MyPy 對整條邏輯鏈「失明」。
- **Fix**: 如果真的無法確定型別，考慮使用 `object` (什麼都不能做) 或建立一個寬鬆的 `Protocol`。如果必須用 `Any`，請加上 `# type: ignore` 並註明原因，或者在專案設定中禁止隱式 `Any`。

### 2. 誤用 `Optional` (The Optional Trap)
常見錯誤是標記了 `Optional[str]` (即 `str | None`)，但在程式碼中直接當作 `str` 使用，沒有先檢查 `is None`。
- **Anti-pattern**: 直接對 `Optional` 變數呼叫方法。
- **Consequence**: 雖然通過了簡單的 lint，但在 Runtime 可能引發 `AttributeError: 'NoneType' object has no attribute...`。

### 3. 過度複雜的型別體操 (Type Gymnastics)
不要寫出只有你自己看得懂的複雜 `Overload` 或巢狀 `Generic`。
- **Principle**: 如果型別註解比程式碼邏輯還長且難懂，說明你的程式碼設計可能需要重構，或者你正在過度使用型別系統。

---

## Checklists & workflows｜檢查清單與流程

### Configuration & Setup
- [ ] **啟用 Strict Mode**: 在 `pyproject.toml` 中設定 `mypy` 的 `strict = true` 或至少啟用 `disallow_untyped_defs`。
- [ ] **整合 Pre-commit**: 確保 `mypy` (或 `basedpyright`) 與 `ruff` 在 commit 前自動執行。

### Code Review Checklist
- [ ] **邊界檢查**: 所有公共函式 (Public API) 的參數與回傳值是否有明確型別？
- [ ] **No Any**: 是否存在未經說明的 `Any`？(應盡量消除)。
- [ ] **None Handling**: 對於 `Optional` 型別，是否有 `if x is not None:` 的防禦性寫法？
- [ ] **Container Types**: `list` 或 `dict` 是否指定了內容型別？(例如 `dict[str, int]` 而非單純 `dict`)。

### Workflow: Adding Types to Legacy Code
1. **Baseline**: 先跑一次 mypy，將現有錯誤存入 baseline 檔案或是 ignore 清單。
2. **New Code Strict**: 設定 CI 規則，新提交的程式碼必須通過嚴格檢查。
3. **Gradual Fix**: 每次修改舊檔案時，順手補上該檔案的型別註解 (Boy Scout Rule)。

---

## Real-world examples｜實戰案例

### Scenario 1: Refactoring with Protocols (Dependency Injection)
在大型專案中，我們希望 Service 層不依賴具體的 Database 實作。

```python
# ❌ Bad: 強耦合，難以測試
# from infrastructure.db import PostgresDatabase
# def get_user_data(db: PostgresDatabase, user_id: int): ...

# ✅ Good: 使用 Protocol 定義所需介面
from typing import Protocol, Any

class DataReader(Protocol):
    def fetch(self, query: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        ...

# 實作時，不管是 PostgresDatabase 還是 MockDatabase，
# 只要有 fetch 方法且簽章符合，MyPy 就會通過。
def get_user_data(db: DataReader, user_id: int) -> dict[str, Any]:
    return db.fetch("SELECT * FROM users WHERE id = :id", {"id": user_id})[0]
```

### Scenario 2: Pydantic + Static Analysis
結合 Runtime 驗證與靜態分析的完美搭配。

```python
from pydantic import BaseModel, EmailStr

# 1. 定義 Schema (Runtime Validation)
class UserCreateRequest(BaseModel):
    username: str
    email: EmailStr
    age: int | None = None  # Optional field

# 2. 業務邏輯 (Static Analysis)
# MyPy 知道 user.email 是字串，user.age 可能是 int 或 None
def process_registration(user: UserCreateRequest) -> str:
    # MyPy 會在這裡報錯，因為 age 可能是 None，不能直接加 1
    # next_age = user.age + 1  <-- Error: Unsupported operand types for +: 'None' and 'int'
    
    # 正確寫法：型別限縮 (Type Narrowing)
    if user.age is not None:
        return f"User {user.username} will be {user.age + 1} next year."
    
    return f"User {user.username} registered."
```

### Scenario 3: TypedDict for JSON Payloads
當你不想建立完整的 Class，但又需要對 Dictionary 結構進行型別檢查時（常見於呼叫外部 API 的 payload）。

```python
from typing import TypedDict, NotRequired

class SlackMessage(TypedDict):
    text: str
    channel: str
    # Python 3.11+ 特性：標記某些 key 是可選的
    thread_ts: NotRequired[str] 

def send_slack(msg: SlackMessage) -> None:
    ...

# ✅ OK
send_slack({"text": "Hello", "channel": "#general"})

# ❌ MyPy Error: Missing key 'channel'
# send_slack({"text": "Hello"}) 

# ❌ MyPy Error: Extra key 'invalid_field'
# send_slack({"text": "Hi", "channel": "#dev", "invalid_field": 1})
```